"""
User Management Routes

API endpoints for user profile management, family linking, and doctor operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import AsyncClient
import logging

from app.users.schemas import (
    UserUpdateRequest,
    DoctorProfileUpdate,
    FamilyMemberLink,
    UserProfileResponse
)
from app.users.service import UserService
from app.core.dependencies import get_firestore_db
from app.core.security import get_current_user_id, require_role, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get current user's complete profile."""
    try:
        user_service = UserService(db)
        profile = await user_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileResponse(**profile)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Update current user's profile."""
    try:
        user_service = UserService(db)
        
        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_unset=True)
        
        updated_profile = await user_service.update_user_profile(user_id, update_dict)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileResponse(**updated_profile)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/family/link", status_code=status.HTTP_201_CREATED)
async def link_family_member(
    link_request: FamilyMemberLink,
    user_id: str = Depends(require_role(["patient", "admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Link a family member to patient account."""
    try:
        user_service = UserService(db)
        link_data = await user_service.link_family_member(
            patient_id=user_id,
            family_member_phone=link_request.family_member_phone,
            family_member_email=link_request.family_member_email,
            relationship=link_request.relationship
        )
        
        return {
            "message": "Family member linked successfully",
            "link_id": link_data.get("id") if "id" in link_data else None
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Link family member error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link family member"
        )


@router.put("/doctor/profile", response_model=UserProfileResponse)
async def update_doctor_profile(
    doctor_data: DoctorProfileUpdate,
    doctor_id: str = Depends(require_role(["doctor", "admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Update doctor-specific profile information."""
    try:
        user_service = UserService(db)
        update_dict = doctor_data.model_dump(exclude_unset=True)
        updated_profile = await user_service.update_doctor_profile(doctor_id, update_dict)
        
        return UserProfileResponse(**updated_profile)
    
    except Exception as e:
        logger.error(f"Update doctor profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update doctor profile"
        )


@router.post("/doctor/{doctor_id}/verify", status_code=status.HTTP_200_OK)
async def verify_doctor(
    doctor_id: str,
    admin_id: str = Depends(require_admin()),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Verify a doctor (admin only)."""
    try:
        user_service = UserService(db)
        await user_service.verify_doctor(doctor_id, admin_id)
        
        return {"message": "Doctor verified successfully"}
    
    except Exception as e:
        logger.error(f"Verify doctor error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify doctor"
        )

