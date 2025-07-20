"""Shared dependencies"""
import os
import redis
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from fastapi import Request, HTTPException, status
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
        return json.loads(override_data)
    return None

def blacklist_token(token: str):
    """Blacklist a JWT token"""
    try:
        # Decode without verification to get expiry
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp:
            # Calculate remaining time until expiry
            remaining_time = exp - int(datetime.utcnow().timestamp())
            if remaining_time > 0:
                # Store in Redis with expiry
                redis_client.setex(f"blacklist:{token}", remaining_time, "1")
    except Exception:
        pass  # Invalid token, ignore

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted"""
    return redis_client.exists(f"blacklist:{token}") == 1

def hash_pii(value: str) -> str:
    """Hash PII for safe logging"""
    return hashlib.sha256(value.encode()).hexdigest()[:16]

def generate_csrf_token() -> str:
    """Generate a CSRF token"""
    return secrets.token_urlsafe(32)

def store_csrf_token(session_id: str, token: str):
    """Store CSRF token in Redis with 1 hour expiry"""
    redis_client.setex(f"csrf:{session_id}", 3600, token)

def verify_csrf_token(session_id: str, token: str) -> bool:
    """Verify CSRF token"""
    stored_token = redis_client.get(f"csrf:{session_id}")
    return stored_token == token

def require_csrf_token(request: Request):
    """CSRF protection dependency"""
    # Skip CSRF for safe methods
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return
    
    # Get session ID from cookie or header
    session_id = request.cookies.get("session_id") or request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing session ID for CSRF protection"
        )
    
    # Get CSRF token from header
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing CSRF token"
        )
    
    # Verify CSRF token
    if not verify_csrf_token(session_id, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )