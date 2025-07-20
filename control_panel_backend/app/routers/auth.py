"""Authentication endpoints"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..models import User
from ..schemas import Token, UserCreate, UserResponse, UserLogin
from ..auth import verify_password, get_password_hash, create_access_token, create_refresh_token, get_current_user, require_admin, oauth2_scheme
from ..dependencies import log_audit, hash_pii, generate_csrf_token, store_csrf_token

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
    
    # Log audit with hashed PII
    await log_audit(
        db=db,
        user_id=str(user.id),
        action="user_register",
        resource="user",
        resource_id=str(user.id),
        details={"email_hash": hash_pii(user.email), "role": user.role},
        success=True,
        request=request
    )
    
    return user

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with form data (rate limited: 5 attempts per minute)"""
    return await _perform_login(request, response, form_data.username, form_data.password, db)

@router.post("/login-json")
@limiter.limit("5/minute")
async def login_json(
    request: Request,
    response: Response,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with JSON data (rate limited: 5 attempts per minute)"""
    return await _perform_login(request, response, login_data.username, login_data.password, db)

async def _perform_login(request: Request, response: Response, username: str, password: str, db: Session):
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
            details={"email_hash": hash_pii(username)},
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
    
    # Create access and refresh tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    # Log successful login
    await log_audit(
        db=db,
        user_id=str(user.id),
        action="login_success",
        resource="auth",
        details={"email_hash": hash_pii(user.email)},
        success=True,
        request=request
    )
    
    # Set httpOnly cookies for tokens
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=15 * 60,  # 15 minutes
        httponly=True,
        secure=not request.url.hostname in ["localhost", "127.0.0.1"],  # Secure in production
        samesite="strict"
    )
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=not request.url.hostname in ["localhost", "127.0.0.1"],  # Secure in production
        samesite="strict"
    )
    
    # Generate session ID for CSRF protection
    session_id = generate_csrf_token()
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=24 * 60 * 60,  # 24 hours
        httponly=False,  # Accessible to JavaScript for CSRF
        secure=not request.url.hostname in ["localhost", "127.0.0.1"],
        samesite="strict"
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout and blacklist token"""
    from ..dependencies import blacklist_token
    from ..auth import get_token_from_request
    
    # Get the token for blacklisting
    token = get_token_from_request(request)
    
    # Blacklist the current token
    blacklist_token(token)
    
    # Clear httpOnly cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="session_id")
    
    # Log audit
    await log_audit(
        db=db,
        user_id=str(current_user.id),
        action="logout",
        resource="auth",
        success=True,
        request=request
    )
    
    return {"message": "Logged out successfully"}

@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Get CSRF token for session"""
    # Generate session ID if not present
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = generate_csrf_token()
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    # Store CSRF token
    store_csrf_token(session_id, csrf_token)
    
    response_data = {
        "csrf_token": csrf_token,
        "session_id": session_id
    }
    
    return response_data