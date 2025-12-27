"""
User Management Schemas

Pydantic models for user profile management and family linking.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserUpdateRequest(BaseModel):
    """User profile update request."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class DoctorProfileUpdate(BaseModel):
    """Doctor-specific profile update."""
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None


class FamilyMemberLink(BaseModel):
    """Link a family member to patient account."""
    family_member_phone: Optional[str] = None
    family_member_email: Optional[EmailStr] = None
    relationship: str = Field(..., pattern="^(spouse|child|parent|sibling|other)$")


class FamilyMemberResponse(BaseModel):
    """Family member information."""
    id: str
    full_name: str
    relationship: str
    phone: Optional[str] = None
    email: Optional[str] = None
    linked_at: datetime


class UserProfileResponse(BaseModel):
    """Complete user profile response."""
    id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    full_name: str
    role: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_verified: bool
    family_members: List[FamilyMemberResponse] = []
    created_at: datetime
    updated_at: datetime

