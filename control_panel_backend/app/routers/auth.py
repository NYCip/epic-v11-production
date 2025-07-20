"""Authentication endpoints"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..models import User
from ..schemas import Token, UserCreate, UserResponse, UserLogin
from ..auth import verify_password, get_password_hash, create_access_token, get_current_user, require_admin
from ..dependencies import log_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Register a new user (admin only)"""
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log audit
    await log_audit(
        db=db,
        user_id=str(user.id),
        action="user_register",
        resource="user",
        resource_id=str(user.id),
        details={"email": user.email, "role": user.role},
        success=True,
        request=request
    )
    
    return user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with form data (rate limited: 5 attempts per minute)"""
    return await _perform_login(request, form_data.username, form_data.password, db)

@router.post("/login-json", response_model=Token)
@limiter.limit("5/minute")
async def login_json(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with JSON data (rate limited: 5 attempts per minute)"""
    return await _perform_login(request, login_data.username, login_data.password, db)

async def _perform_login(request: Request, username: str, password: str, db: Session):
    """Login and receive access token"""
    # Find user
    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        # Log failed attempt
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                user.is_active = False
            db.commit()
        
        await log_audit(
            db=db,
            user_id=str(user.id) if user else None,
            action="login_failed",
            resource="auth",
            details={"email": username},
            success=False,
            error_message="Invalid credentials",
            request=request
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until}"
        )
    
    # Reset failed attempts and update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.is_active = True
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )
    
    # Log successful login
    await log_audit(
        db=db,
        user_id=str(user.id),
        action="login_success",
        resource="auth",
        details={"email": user.email},
        success=True,
        request=request
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout (audit logging)"""
    await log_audit(
        db=db,
        user_id=str(current_user.id),
        action="logout",
        resource="auth",
        success=True,
        request=request
    )
    
    return {"message": "Logged out successfully"}