"""MCP (Model Context Protocol) Server for tool capability verification"""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import uuid

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://epic_admin:password@localhost:5432/epic_v11")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class MCPTool(Base):
    __tablename__ = "mcp_tools"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(String)
    capabilities = Column(JSON, nullable=False)
    verified = Column(Boolean, default=False)
    verified_by = Column(String(255))
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class MCPToolLog(Base):
    __tablename__ = "mcp_tool_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(PGUUID(as_uuid=True), ForeignKey("mcp_tools.id"))
    action = Column(String(255), nullable=False)
    agent_name = Column(String(255))
    parameters = Column(JSON)
    result = Column(JSON)
    success = Column(Boolean, nullable=False)
    error_message = Column(String)
    duration_ms = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="EPIC V11 MCP Server",
    description="Model Context Protocol server for tool capability verification",
    version="11.0.0",
    docs_url="/mcp/docs",
    redoc_url="/mcp/redoc",
    openapi_url="/mcp/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://epic.pos.com", "http://agno_service:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ToolRegistration(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str
    capabilities: Dict[str, List[str]]

class VerificationRequest(BaseModel):
    tool_name: str
    capability: str
    agent_name: str

class VerificationResponse(BaseModel):
    tool_name: str
    capability: str
    verified: bool
    verified_at: datetime
    message: Optional[str] = None

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize core tools on startup
@app.on_event("startup")
async def startup_event():
    """Register core MCP tools"""
    db = SessionLocal()
    try:
        # Register Donna Protection Tools
        donna_tool = db.query(MCPTool).filter(MCPTool.name == "donna_protection").first()
        if not donna_tool:
            donna_tool = MCPTool(
                name="donna_protection",
                version="1.0.0",
                description="Family protection tools named after Edward's late mother",
                capabilities={
                    "actions": [
                        "check_family_impact",
                        "enforce_data_sovereignty",
                        "emergency_alert",
                        "privacy_shield"
                    ],
                    "risk_levels": ["LOW", "MEDIUM", "HIGH", "CRITICAL", "EXTREME"],
                    "protection_areas": ["personal_data", "financial", "location", "communication"]
                },
                verified=True,
                verified_by="EPIC_SYSTEM",
                verified_at=datetime.utcnow()
            )
            db.add(donna_tool)
            db.commit()
            print("✅ Registered Donna Protection Tools")
        
        # Register standard AI tools
        standard_tools = [
            {
                "name": "web_search",
                "version": "1.0.0",
                "description": "DuckDuckGo web search capability",
                "capabilities": {
                    "actions": ["search", "news_search"],
                    "limits": ["rate_limited", "no_personal_data"]
                }
            },
            {
                "name": "file_operations",
                "version": "1.0.0",
                "description": "Local file system operations",
                "capabilities": {
                    "actions": ["read", "write", "list"],
                    "restrictions": ["sandbox_only", "no_system_files"]
                }
            },
            {
                "name": "calculations",
                "version": "1.0.0",
                "description": "Mathematical and financial calculations",
                "capabilities": {
                    "actions": ["basic_math", "statistics", "financial_analysis"],
                    "precision": ["float64", "decimal128"]
                }
            }
        ]
        
        for tool_data in standard_tools:
            tool = db.query(MCPTool).filter(MCPTool.name == tool_data["name"]).first()
            if not tool:
                tool = MCPTool(
                    name=tool_data["name"],
                    version=tool_data["version"],
                    description=tool_data["description"],
                    capabilities=tool_data["capabilities"],
                    verified=True,
                    verified_by="EPIC_SYSTEM",
                    verified_at=datetime.utcnow()
                )
                db.add(tool)
        
        db.commit()
        print("✅ Initialized MCP tool registry")
        
    finally:
        db.close()

# Health check
@app.get("/health")
@app.get("/mcp/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
        
        # Count tools
        tool_count = db.query(MCPTool).count()
        verified_count = db.query(MCPTool).filter(MCPTool.verified == True).count()
        
    except Exception as e:
        db_status = "unhealthy"
        tool_count = 0
        verified_count = 0
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": db_status
        },
        "tools": {
            "total": tool_count,
            "verified": verified_count
        }
    }

# Register new tool
@app.post("/mcp/tools/register")
async def register_tool(
    tool: ToolRegistration,
    db: Session = Depends(get_db)
):
    """Register a new tool in the MCP registry"""
    # Check if tool exists
    existing = db.query(MCPTool).filter(MCPTool.name == tool.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool {tool.name} already registered"
        )
    
    # Create new tool
    db_tool = MCPTool(
        name=tool.name,
        version=tool.version,
        description=tool.description,
        capabilities=tool.capabilities
    )
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    
    return {
        "message": f"Tool {tool.name} registered successfully",
        "tool_id": str(db_tool.id),
        "verified": db_tool.verified
    }

# Verify capability
@app.post("/mcp/tools/verify", response_model=VerificationResponse)
async def verify_capability(
    request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify if a tool has a specific capability"""
    start_time = datetime.utcnow()
    
    # Find tool
    tool = db.query(MCPTool).filter(MCPTool.name == request.tool_name).first()
    
    if not tool:
        # Log failed verification
        log_entry = MCPToolLog(
            tool_id=None,
            action="verify_capability",
            agent_name=request.agent_name,
            parameters={
                "tool_name": request.tool_name,
                "capability": request.capability
            },
            result={"verified": False, "reason": "tool_not_found"},
            success=False,
            error_message="Tool not found in registry",
            duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
        )
        db.add(log_entry)
        db.commit()
        
        return VerificationResponse(
            tool_name=request.tool_name,
            capability=request.capability,
            verified=False,
            verified_at=datetime.utcnow(),
            message="Tool not found in MCP registry"
        )
    
    # Check if tool is verified
    if not tool.verified:
        # Log unverified tool
        log_entry = MCPToolLog(
            tool_id=tool.id,
            action="verify_capability",
            agent_name=request.agent_name,
            parameters={
                "tool_name": request.tool_name,
                "capability": request.capability
            },
            result={"verified": False, "reason": "tool_not_verified"},
            success=False,
            error_message="Tool exists but is not verified",
            duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
        )
        db.add(log_entry)
        db.commit()
        
        return VerificationResponse(
            tool_name=request.tool_name,
            capability=request.capability,
            verified=False,
            verified_at=datetime.utcnow(),
            message="Tool is not verified by EPIC system"
        )
    
    # Check capability
    has_capability = False
    capabilities = tool.capabilities or {}
    
    # Check in actions list
    if "actions" in capabilities:
        has_capability = request.capability in capabilities["actions"]
    
    # Check in other capability categories
    if not has_capability:
        for category, items in capabilities.items():
            if isinstance(items, list) and request.capability in items:
                has_capability = True
                break
    
    # Log verification
    log_entry = MCPToolLog(
        tool_id=tool.id,
        action="verify_capability",
        agent_name=request.agent_name,
        parameters={
            "tool_name": request.tool_name,
            "capability": request.capability
        },
        result={"verified": has_capability},
        success=True,
        duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
    )
    db.add(log_entry)
    db.commit()
    
    return VerificationResponse(
        tool_name=request.tool_name,
        capability=request.capability,
        verified=has_capability,
        verified_at=datetime.utcnow(),
        message="Capability verified" if has_capability else "Capability not found"
    )

# List tools
@app.get("/mcp/tools/list")
async def list_tools(
    verified_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all registered tools"""
    query = db.query(MCPTool)
    
    if verified_only:
        query = query.filter(MCPTool.verified == True)
    
    tools = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(tool.id),
            "name": tool.name,
            "version": tool.version,
            "description": tool.description,
            "verified": tool.verified,
            "capabilities": tool.capabilities,
            "created_at": tool.created_at
        }
        for tool in tools
    ]

# Get tool details
@app.get("/mcp/tools/{tool_name}")
async def get_tool_details(
    tool_name: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific tool"""
    tool = db.query(MCPTool).filter(MCPTool.name == tool_name).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool {tool_name} not found"
        )
    
    # Get recent logs
    recent_logs = db.query(MCPToolLog)\
        .filter(MCPToolLog.tool_id == tool.id)\
        .order_by(MCPToolLog.timestamp.desc())\
        .limit(10)\
        .all()
    
    return {
        "tool": {
            "id": str(tool.id),
            "name": tool.name,
            "version": tool.version,
            "description": tool.description,
            "verified": tool.verified,
            "verified_by": tool.verified_by,
            "verified_at": tool.verified_at,
            "capabilities": tool.capabilities,
            "created_at": tool.created_at
        },
        "recent_activity": [
            {
                "action": log.action,
                "agent_name": log.agent_name,
                "success": log.success,
                "timestamp": log.timestamp
            }
            for log in recent_logs
        ]
    }

# Verify tool (admin function)
@app.post("/mcp/tools/{tool_name}/verify")
async def verify_tool(
    tool_name: str,
    verified_by: str = "EPIC_ADMIN",
    db: Session = Depends(get_db)
):
    """Mark a tool as verified (requires admin auth in production)"""
    tool = db.query(MCPTool).filter(MCPTool.name == tool_name).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool {tool_name} not found"
        )
    
    if tool.verified:
        return {"message": f"Tool {tool_name} is already verified"}
    
    # Update verification status
    tool.verified = True
    tool.verified_by = verified_by
    tool.verified_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Tool {tool_name} has been verified",
        "verified_by": verified_by,
        "verified_at": tool.verified_at
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)