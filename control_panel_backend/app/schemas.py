"""Pydantic schemas for API validation"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import re

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(default="viewer", pattern="^(admin|operator|viewer)$")

class UserCreate(UserBase):
    password: str = Field(min_length=12, max_length=128, description="Password must be 12-128 characters with uppercase, lowercase, digit, and special character")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Enforce strong password policy"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        # Check for common patterns
        if any(pattern in v.lower() for pattern in ['password', '12345', 'qwerty', 'admin']):
            raise ValueError('Password contains common patterns')
        return v

class UserLogin(BaseModel):
    username: EmailStr  # Using username for compatibility with OAuth2
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|operator|viewer)$")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    user_id: str
    email: str
    role: str

# System override schemas
class SystemOverrideRequest(BaseModel):
    reason: str = Field(min_length=10)
    affected_services: Optional[List[str]] = None

class SystemOverrideResponse(BaseModel):
    id: UUID
    override_type: str
    initiated_by: UUID
    reason: str
    affected_services: Optional[Dict[str, Any]]
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Audit log schemas
class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    resource: Optional[str]
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Health check schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]