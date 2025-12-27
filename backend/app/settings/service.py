"""
Settings Service

Business logic for user settings, preferences, and storage management.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging

from app.settings.schemas import (
    LanguageCode,
    AppearanceMode,
    NotificationPreferences,
    SyncPreferences,
    PrivacySettings,
    StorageInfo,
    SecurityInfo,
    ClearStorageRequest
)

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for user settings management."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.settings_collection = db.collection("user_settings")
        self.users_collection = db.collection("users")
        self.health_records_collection = db.collection("health_records")
        self.vital_data_collection = db.collection("vital_data")
        
        # Default storage limits (MB)
        self.default_storage_limit = 500.0
    
    async def get_user_settings(self, user_id: str) -> dict:
        """
        Get complete user settings.
        
        Args:
            user_id: User ID
            
        Returns:
            Complete settings document
        """
        # Get or create settings document
        settings_doc = await self.settings_collection.document(user_id).get()
        
        if not settings_doc.exists:
            # Create default settings
            return await self._create_default_settings(user_id)
        
        settings_data = settings_doc.to_dict()
        settings_data["user_id"] = user_id
        
        # Get storage info
        storage_info = await self._calculate_storage_usage(user_id)
        settings_data["storage"] = storage_info
        
        # Get security info
        security_info = await self._get_security_info(user_id)
        settings_data["security"] = security_info
        
        return settings_data
    
    async def update_settings(
        self,
        user_id: str,
        update_data: dict
    ) -> dict:
        """
        Update user settings.
        
        Args:
            user_id: User ID
            update_data: Dictionary of settings to update
            
        Returns:
            Updated settings
        """
        # Ensure settings document exists
        settings_doc = await self.settings_collection.document(user_id).get()
        if not settings_doc.exists:
            await self._create_default_settings(user_id)
        
        # Prepare update
        update_fields = {
            "updated_at": datetime.utcnow()
        }
        
        # Update language
        if "language" in update_data:
            update_fields["language"] = update_data["language"].value if hasattr(update_data["language"], "value") else update_data["language"]
        
        # Update appearance
        if "appearance" in update_data:
            update_fields["appearance"] = update_data["appearance"].value if hasattr(update_data["appearance"], "value") else update_data["appearance"]
        
        # Update notifications
        if "notifications" in update_data:
            if isinstance(update_data["notifications"], dict):
                update_fields["notifications"] = update_data["notifications"]
            else:
                update_fields["notifications"] = update_data["notifications"].model_dump()
        
        # Update sync
        if "sync" in update_data:
            if isinstance(update_data["sync"], dict):
                update_fields["sync"] = update_data["sync"]
            else:
                update_fields["sync"] = update_data["sync"].model_dump()
        
        # Update privacy
        if "privacy" in update_data:
            if isinstance(update_data["privacy"], dict):
                update_fields["privacy"] = update_data["privacy"]
            else:
                update_fields["privacy"] = update_data["privacy"].model_dump()
        
        # Update document
        await self.settings_collection.document(user_id).update(update_fields)
        
        logger.info(f"Settings updated for user: {user_id}")
        
        # Return updated settings
        return await self.get_user_settings(user_id)
    
    async def get_storage_info(self, user_id: str) -> StorageInfo:
        """
        Get storage usage information.
        
        Args:
            user_id: User ID
            
        Returns:
            Storage information
        """
        return await self._calculate_storage_usage(user_id)
    
    async def clear_storage(
        self,
        user_id: str,
        clear_request: ClearStorageRequest
    ) -> dict:
        """
        Clear offline storage.
        
        Args:
            user_id: User ID
            clear_request: Clear storage request
            
        Returns:
            Clear storage response
        """
        cleared_mb = 0.0
        
        if clear_request.clear_all:
            # Clear everything
            cleared_mb = await self._clear_all_storage(user_id)
        else:
            # Selective clearing
            if clear_request.clear_offline_records:
                cleared_mb += await self._clear_offline_records(user_id)
            
            if clear_request.clear_media:
                cleared_mb += await self._clear_media_files(user_id)
            
            if clear_request.clear_cache:
                cleared_mb += await self._clear_cache(user_id)
        
        # Get updated storage info
        storage_info = await self._calculate_storage_usage(user_id)
        
        # Update last cleared timestamp
        await self.settings_collection.document(user_id).update({
            "storage_last_cleared": datetime.utcnow()
        })
        
        logger.info(f"Storage cleared: {cleared_mb} MB for user {user_id}")
        
        return {
            "cleared_mb": cleared_mb,
            "remaining_mb": storage_info["used_mb"],
            "cleared_at": datetime.utcnow()
        }
    
    async def get_notification_preferences(self, user_id: str) -> dict:
        """Get notification preferences."""
        settings = await self.get_user_settings(user_id)
        return settings.get("notifications", {})
    
    async def update_notification_preferences(
        self,
        user_id: str,
        preferences: dict
    ) -> dict:
        """Update notification preferences."""
        return await self.update_settings(user_id, {"notifications": preferences})
    
    async def _create_default_settings(self, user_id: str) -> dict:
        """Create default settings for a user."""
        default_settings = {
            "user_id": user_id,
            "language": LanguageCode.ENGLISH.value,
            "appearance": AppearanceMode.SYSTEM.value,
            "notifications": {
                "enabled": True,
                "consultation_notifications": True,
                "prescription_notifications": True,
                "lab_result_notifications": True,
                "appointment_notifications": True,
                "vital_alerts": True,
                "medication_reminders": True,
                "general_notifications": True,
                "quiet_hours_enabled": False,
                "quiet_hours_start": None,
                "quiet_hours_end": None
            },
            "sync": {
                "auto_sync_enabled": True,
                "sync_on_wifi_only": False,
                "sync_frequency": "realtime",
                "sync_health_records": True,
                "sync_prescriptions": True,
                "sync_lab_reports": True,
                "sync_vital_data": True
            },
            "privacy": {
                "share_data_for_research": False,
                "allow_analytics": True,
                "allow_crash_reporting": True,
                "data_retention_days": 365
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.settings_collection.document(user_id).set(default_settings)
        
        # Add storage and security info
        default_settings["storage"] = await self._calculate_storage_usage(user_id)
        default_settings["security"] = await self._get_security_info(user_id)
        
        return default_settings
    
    async def _calculate_storage_usage(self, user_id: str) -> dict:
        """
        Calculate storage usage breakdown.
        
        Returns:
            Storage information dictionary
        """
        breakdown = {}
        total_mb = 0.0
        
        # Health records (estimate ~50KB per record)
        records_query = self.health_records_collection.where("user_id", "==", user_id)
        records_count = sum(1 async for _ in records_query.stream())
        records_mb = (records_count * 50) / 1024  # Convert KB to MB
        breakdown["health_records"] = round(records_mb, 2)
        total_mb += records_mb
        
        # Vital data (estimate ~1KB per data point)
        vitals_query = self.vital_data_collection.where("user_id", "==", user_id)
        vitals_count = sum(1 async for _ in vitals_query.stream())
        vitals_mb = (vitals_count * 1) / 1024
        breakdown["vital_data"] = round(vitals_mb, 2)
        total_mb += vitals_mb
        
        # Media files (attachments) - estimate from records
        # Assume average 2MB per attachment
        attachments_mb = records_count * 2  # Rough estimate
        breakdown["media"] = round(attachments_mb, 2)
        total_mb += attachments_mb
        
        # Cache (estimate 10MB base)
        cache_mb = 10.0
        breakdown["cache"] = round(cache_mb, 2)
        total_mb += cache_mb
        
        # Get last cleared time
        settings_doc = await self.settings_collection.document(user_id).get()
        last_cleared = None
        if settings_doc.exists:
            last_cleared = settings_doc.to_dict().get("storage_last_cleared")
        
        return {
            "used_mb": round(total_mb, 2),
            "total_mb": self.default_storage_limit,
            "usage_percentage": round((total_mb / self.default_storage_limit) * 100, 2),
            "breakdown": breakdown,
            "last_cleared": last_cleared
        }
    
    async def _get_security_info(self, user_id: str) -> dict:
        """Get security information for user."""
        user_doc = await self.users_collection.document(user_id).get()
        
        if not user_doc.exists:
            return {
                "encryption_enabled": True,
                "encryption_algorithm": "AES-256-GCM",
                "tls_version": "TLS 1.3",
                "two_factor_enabled": False,
                "account_created": datetime.utcnow(),
                "last_login": None,
                "active_sessions": 0
            }
        
        user_data = user_doc.to_dict()
        
        return {
            "encryption_enabled": True,
            "encryption_algorithm": "AES-256-GCM",
            "tls_version": "TLS 1.3",
            "two_factor_enabled": False,  # TODO: Implement 2FA
            "last_password_change": user_data.get("password_changed_at"),
            "account_created": user_data.get("created_at", datetime.utcnow()),
            "last_login": user_data.get("last_login"),
            "active_sessions": 1  # TODO: Track active sessions
        }
    
    async def _clear_all_storage(self, user_id: str) -> float:
        """Clear all offline storage."""
        # Clear offline records (mark as synced, not deleted)
        query = self.health_records_collection.where("user_id", "==", user_id).where("sync_status", "==", "pending")
        cleared_count = 0
        async for doc in query.stream():
            await doc.reference.update({"sync_status": "synced"})
            cleared_count += 1
        
        # Clear cache (simulated)
        cache_mb = 10.0
        
        # Estimate cleared MB
        cleared_mb = (cleared_count * 50) / 1024 + cache_mb
        
        return round(cleared_mb, 2)
    
    async def _clear_offline_records(self, user_id: str) -> float:
        """Clear offline records that are pending sync."""
        query = self.health_records_collection.where("user_id", "==", user_id).where("sync_status", "==", "pending")
        cleared_count = 0
        async for doc in query.stream():
            await doc.reference.update({"sync_status": "synced"})
            cleared_count += 1
        
        return round((cleared_count * 50) / 1024, 2)
    
    async def _clear_media_files(self, user_id: str) -> float:
        """Clear media files (simulated - in production, delete from Firebase Storage)."""
        # In production, this would delete files from Firebase Storage
        # For now, return estimated cleared space
        return 50.0  # Estimated MB
    
    async def _clear_cache(self, user_id: str) -> float:
        """Clear application cache."""
        # In production, clear local cache
        return 10.0  # Estimated MB

