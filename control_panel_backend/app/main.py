"""Main FastAPI application"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langfuse import Langfuse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="EPIC V11 Control Panel",
    description="Central control panel for EPIC V11 multi-agent system",
    version="11.0.0",
    docs_url="/control/docs",
    redoc_url="/control/redoc",
    openapi_url="/control/openapi.json"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development frontend
        "https://epic.pos.com",
        "https://langfuse.epic.pos.com",
        "https://n8n.epic.pos.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp
    
    # Additional security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    # HTTPS enforcement (in production)
    if not request.url.hostname in ["localhost", "127.0.0.1"]:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    return response

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

# Health check endpoint (no rate limit - monitoring)
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
@limiter.limit("1000/hour")
async def root(request: Request):
    """Redirect to docs"""
    return {"message": "EPIC V11 Control Panel API", "docs": "/control/docs"}

# Request size limiting middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request size to prevent DoS"""
    if request.headers.get("content-length"):
        content_length = int(request.headers["content-length"])
        if content_length > 10_000_000:  # 10MB limit
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large"}
            )
    return await call_next(request)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to prevent information leakage"""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)