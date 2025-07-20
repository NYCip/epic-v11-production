"""SQLAlchemy models"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    mfa_secret = Column(String(255))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    resource_id = Column(String(255))
    details = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class SystemOverride(Base):
    __tablename__ = "system_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    override_type = Column(String(50), nullable=False)
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    affected_services = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

class BoardDecision(Base):
    __tablename__ = "board_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    decision = Column(String(50), nullable=False)
    risk_level = Column(String(50), nullable=False)
    board_votes = Column(JSON, nullable=False)
    risk_assessments = Column(JSON, nullable=False)
    veto_by = Column(String(255))
    veto_reason = Column(Text)
    final_response = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class MCPTools(Base):
    __tablename__ = "mcp_tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_name = Column(String(255), nullable=False)
    tool_type = Column(String(100), nullable=False)
    verification_status = Column(String(50), nullable=False)
    donna_protected = Column(Boolean, default=True)
    risk_level = Column(String(50), nullable=False)
    last_verified = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

class ToolVerification(Base):
    __tablename__ = "tool_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp_tools.id"), nullable=False)
    verification_result = Column(String(50), nullable=False)
    safety_score = Column(Integer, nullable=False)
    protection_level = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))