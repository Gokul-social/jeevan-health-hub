"""
Authentication Routes

API endpoints for user authentication, registration, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from google.cloud.firestore import AsyncClient
import logging

from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserProfile
)
from app.auth.service import AuthService
from app.core.dependencies import get_firestore_db, rate_limit_dependency
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncClient = Depends(get_firestore_db),
    _: None = Depends(rate_limit_dependency)
):
    """
    Register a new user.
    
    Supports patient, doctor, and admin registration.
    Phone or email required.
    """
    try:
        auth_service = AuthService(db)
        user_data = await auth_service.register_user(
            phone=request.phone,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        return UserProfile(**user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncClient = Depends(get_firestore_db),
    http_request: Request = None,
    _: None = Depends(rate_limit_dependency)
):
    """
    Authenticate user and return JWT tokens.
    
    Returns short-lived access token and longer-lived refresh token.
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(
            phone=request.phone,
            email=request.email,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone/email or password"
            )
        
        # Create tokens
        tokens = auth_service.create_tokens(user["id"], user["role"])
        
        logger.info(f"User logged in: {user['id']}")
        return TokenResponse(**tokens)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Refresh access token using refresh token.
    
    Returns new access token if refresh token is valid.
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.refresh_access_token(request.refresh_token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        return TokenResponse(**token_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Get current authenticated user's profile.
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(**user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

