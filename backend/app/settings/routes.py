"""
Settings Routes

API endpoints for user settings, preferences, and storage management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import AsyncClient
import logging

from pydantic import BaseModel
from app.settings.schemas import (
    UserSettingsResponse,
    SettingsUpdateRequest,
    StorageInfo,
    SecurityInfo,
    NotificationPreferences,
    ClearStorageRequest,
    ClearStorageResponse,
    LanguageCode,
    AppearanceMode
)
from app.settings.service import SettingsService
from app.core.dependencies import get_firestore_db
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=UserSettingsResponse)
async def get_settings(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Get complete user settings including preferences, storage, and security info.
    """
    try:
        service = SettingsService(db)
        settings = await service.get_user_settings(user_id)
        
        return UserSettingsResponse(**settings)
    
    except Exception as e:
        logger.error(f"Get settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings"
        )


@router.put("/", response_model=UserSettingsResponse)
async def update_settings(
    update_request: SettingsUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Update user settings (language, appearance, notifications, sync, privacy).
    """
    try:
        service = SettingsService(db)
        
        # Convert Pydantic models to dicts
        update_data = {}
        
        if update_request.language:
            update_data["language"] = update_request.language
        
        if update_request.appearance:
            update_data["appearance"] = update_request.appearance
        
        if update_request.notifications:
            update_data["notifications"] = update_request.notifications.model_dump()
        
        if update_request.sync:
            update_data["sync"] = update_request.sync.model_dump()
        
        if update_request.privacy:
            update_data["privacy"] = update_request.privacy.model_dump()
        
        updated = await service.update_settings(user_id, update_data)
        
        return UserSettingsResponse(**updated)
    
    except Exception as e:
        logger.error(f"Update settings error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )


@router.get("/storage", response_model=StorageInfo)
async def get_storage_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Get offline storage usage information.
    """
    try:
        service = SettingsService(db)
        storage_info = await service.get_storage_info(user_id)
        
        return StorageInfo(**storage_info)
    
    except Exception as e:
        logger.error(f"Get storage info error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage information"
        )


@router.post("/storage/clear", response_model=ClearStorageResponse)
async def clear_storage(
    clear_request: ClearStorageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Clear offline storage (cache, records, media).
    """
    try:
        service = SettingsService(db)
        result = await service.clear_storage(user_id, clear_request)
        
        return ClearStorageResponse(**result)
    
    except Exception as e:
        logger.error(f"Clear storage error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear storage"
        )


@router.get("/notifications", response_model=NotificationPreferences)
async def get_notification_preferences(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Get notification preferences.
    """
    try:
        service = SettingsService(db)
        preferences = await service.get_notification_preferences(user_id)
        
        return NotificationPreferences(**preferences)
    
    except Exception as e:
        logger.error(f"Get notification preferences error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification preferences"
        )


@router.put("/notifications", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Update notification preferences.
    """
    try:
        service = SettingsService(db)
        updated = await service.update_notification_preferences(
            user_id,
            preferences.model_dump()
        )
        
        # Return just the notifications part
        settings = await service.get_user_settings(user_id)
        return NotificationPreferences(**settings.get("notifications", {}))
    
    except Exception as e:
        logger.error(f"Update notification preferences error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.get("/security", response_model=SecurityInfo)
async def get_security_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Get security information (encryption, TLS, 2FA, etc.).
    """
    try:
        service = SettingsService(db)
        security_info = await service._get_security_info(user_id)
        
        return SecurityInfo(**security_info)
    
    except Exception as e:
        logger.error(f"Get security info error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security information"
        )


class LanguageUpdateRequest(BaseModel):
    """Language update request."""
    language: LanguageCode


class AppearanceUpdateRequest(BaseModel):
    """Appearance update request."""
    appearance: AppearanceMode


@router.put("/language", status_code=status.HTTP_200_OK)
async def update_language(
    request: LanguageUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Update user language preference.
    """
    try:
        service = SettingsService(db)
        await service.update_settings(user_id, {"language": request.language})
        
        return {"message": "Language updated successfully", "language": request.language.value}
    
    except Exception as e:
        logger.error(f"Update language error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update language"
        )


@router.put("/appearance", status_code=status.HTTP_200_OK)
async def update_appearance(
    request: AppearanceUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Update appearance/theme preference.
    """
    try:
        service = SettingsService(db)
        await service.update_settings(user_id, {"appearance": request.appearance})
        
        return {"message": "Appearance updated successfully", "appearance": request.appearance.value}
    
    except Exception as e:
        logger.error(f"Update appearance error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appearance"
        )

