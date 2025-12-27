"""
Authentication Schemas

Pydantic v2 models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema."""
    phone: Optional[str] = Field(None, description="Phone number for login")
    email: Optional[EmailStr] = Field(None, description="Email for login")
    password: str = Field(..., min_length=6, description="User password")
    
    @field_validator('phone', 'email')
    @classmethod
    def validate_contact(cls, v, info):
        """Ensure at least one contact method is provided."""
        data = info.data
        if not data.get('phone') and not data.get('email'):
            raise ValueError("Either phone or email must be provided")
        return v


class TokenResponse(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class RegisterRequest(BaseModel):
    """User registration request schema."""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2)
    role: str = Field("patient", pattern="^(patient|doctor|admin)$")
    
    @field_validator('phone', 'email')
    @classmethod
    def validate_contact(cls, v, info):
        """Ensure at least one contact method is provided."""
        data = info.data
        if not data.get('phone') and not data.get('email'):
            raise ValueError("Either phone or email must be provided")
        return v


class UserProfile(BaseModel):
    """User profile response schema."""
    id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    full_name: str
    role: str
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

