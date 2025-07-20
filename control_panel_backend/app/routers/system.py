"""System control endpoints"""
import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..models import SystemOverride, AuditLog
from ..schemas import SystemOverrideRequest, SystemOverrideResponse, AuditLogResponse
from ..auth import require_admin, require_operator, get_current_user
from ..dependencies import log_audit, redis_client, check_system_override
from ..models import User

router = APIRouter(prefix="/system", tags=["System"])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/override/halt", response_model=SystemOverrideResponse)
@limiter.limit("3/minute")
async def halt_system(
    override_request: SystemOverrideRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """EDWARD OVERRIDE: Halt all agent operations (admin only, rate limited: 3 per minute)"""
    # Check if already halted
    if check_system_override():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is already in override mode"
        )
    
    # Create override record
    override = SystemOverride(
        override_type="HALT",
        initiated_by=current_user.id,
        reason=override_request.reason,
        affected_services=override_request.affected_services or ["all"]
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    
    # Set Redis flag for immediate effect
    redis_client.set(
        "system_override",
        json.dumps({
            "type": "HALT",
            "id": str(override.id),
            "initiated_by": str(current_user.id),
            "timestamp": override.timestamp.isoformat(),
            "affected_services": override.affected_services
        })
    )
    
    # Broadcast halt command
    redis_client.publish("system_control", json.dumps({
        "command": "HALT",
        "override_id": str(override.id),
        "services": override.affected_services
    }))
    
    # Log audit
    await log_audit(
        db=db,
        user_id=str(current_user.id),
        action="system_halt",
        resource="system",
        resource_id=str(override.id),
        details={
            "reason": override_request.reason,
            "affected_services": override.affected_services
        },
        success=True,
        request=request
    )
    
    return override

@router.post("/override/resume", response_model=SystemOverrideResponse)
async def resume_system(
    override_request: SystemOverrideRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """EDWARD OVERRIDE: Resume agent operations (admin only)"""
    # Check current override
    current_override = check_system_override()
    if not current_override:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is not in override mode"
        )
    
    # Update override record
    override = db.query(SystemOverride).filter(
        SystemOverride.id == current_override["id"]
    ).first()
    
    if override:
        override.resolved_at = datetime.utcnow()
        override.resolved_by = current_user.id
        db.commit()
    
    # Clear Redis flag
    redis_client.delete("system_override")
    
    # Broadcast resume command
    redis_client.publish("system_control", json.dumps({
        "command": "RESUME",
        "override_id": current_override["id"]
    }))
    
    # Log audit
    await log_audit(
        db=db,
        user_id=str(current_user.id),
        action="system_resume",
        resource="system",
        resource_id=current_override["id"],
        details={"reason": override_request.reason},
        success=True,
        request=request
    )
    
    return override

@router.get("/override/status")
async def get_override_status(
    current_user: User = Depends(require_operator)
):
    """Get current system override status"""
    override = check_system_override()
    
    if override:
        return {
            "status": "HALTED",
            "override": override
        }
    else:
        return {
            "status": "NORMAL",
            "override": None
        }

@router.get("/override/history", response_model=List[SystemOverrideResponse])
async def get_override_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db)
):
    """Get system override history"""
    overrides = db.query(SystemOverride)\
        .order_by(SystemOverride.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return overrides

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    success: Optional[bool] = None,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db)
):
    """Get audit logs (operator+ only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    if success is not None:
        query = query.filter(AuditLog.success == success)
    
    logs = query.order_by(AuditLog.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return logs