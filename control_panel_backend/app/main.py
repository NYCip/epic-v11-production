"""Main FastAPI application"""
import os
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langfuse import Langfuse
from .database import engine, get_db
from .models import Base
from .routers import auth, users, system
from .dependencies import redis_client, check_system_override

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize Langfuse if configured
langfuse = None
if os.getenv("LANGFUSE_HOST"):
    langfuse = Langfuse(
        host=os.getenv("LANGFUSE_HOST"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY")
    )

# Create FastAPI app
app = FastAPI(
    title="EPIC V11 Control Panel",
    description="Central control panel for EPIC V11 multi-agent system",
    version="11.0.0",
    docs_url="/control/docs",
    redoc_url="/control/redoc",
    openapi_url="/control/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://epic.pos.com",
        "https://langfuse.epic.pos.com",
        "https://n8n.epic.pos.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System override middleware
@app.middleware("http")
async def check_system_halt(request: Request, call_next):
    """Check if system is halted before processing requests"""
    # Skip check for auth and system endpoints
    if request.url.path.startswith("/control/auth") or \
       request.url.path.startswith("/control/system") or \
       request.url.path == "/control/health":
        return await call_next(request)
    
    # Check override status
    override = check_system_override()
    if override and override["type"] == "HALT":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "System is in HALT mode",
                "override_id": override["id"],
                "initiated_at": override["timestamp"]
            }
        )
    
    return await call_next(request)

# Langfuse middleware
if langfuse:
    @app.middleware("http")
    async def langfuse_trace(request: Request, call_next):
        """Trace requests with Langfuse"""
        trace = langfuse.trace(
            name=f"{request.method} {request.url.path}",
            metadata={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None
            }
        )
        
        response = await call_next(request)
        
        trace.update(
            output={
                "status_code": response.status_code
            }
        )
        
        return response

# Include routers
app.include_router(auth.router, prefix="/control")
app.include_router(users.router, prefix="/control")
app.include_router(system.router, prefix="/control")

# Health check endpoint
@app.get("/health")
@app.get("/control/health")
async def health_check():
    """Health check endpoint"""
    # Check database
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Check Redis
    try:
        redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    # Check system override
    override = check_system_override()
    system_status = "halted" if override else "normal"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "system": system_status
        }
    }

# Root redirect
@app.get("/control")
async def root():
    """Redirect to docs"""
    return {"message": "EPIC V11 Control Panel API", "docs": "/control/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)