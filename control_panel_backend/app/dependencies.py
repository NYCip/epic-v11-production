"""Shared dependencies"""
import os
import redis
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuditLog

# Redis client
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

async def log_audit(
    db: Session,
    user_id: Optional[str],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    request: Optional[Request] = None
):
    """Log an audit entry"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        success=success,
        error_message=error_message,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("User-Agent") if request else None
    )
    db.add(audit_log)
    db.commit()
    
    # Also send to Redis for real-time monitoring
    redis_client.xadd(
        "audit_stream",
        {
            "user_id": str(user_id) if user_id else "",
            "action": action,
            "resource": resource or "",
            "success": str(success),
            "timestamp": audit_log.timestamp.isoformat()
        }
    )

def check_system_override() -> Optional[dict]:
    """Check if system is in override mode"""
    override_data = redis_client.get("system_override")
    if override_data:
        import json
        return json.loads(override_data)
    return None