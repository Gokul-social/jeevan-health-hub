"""
Settings Schemas

Pydantic models for user settings and preferences.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"


class AppearanceMode(str, Enum):
    """Appearance/theme modes."""
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class NotificationType(str, Enum):
    """Notification types."""
    CONSULTATION = "consultation"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    APPOINTMENT = "appointment"
    VITAL_ALERT = "vital_alert"
    MEDICATION_REMINDER = "medication_reminder"
    GENERAL = "general"


class NotificationPreferences(BaseModel):
    """Notification preferences."""
    enabled: bool = True
    consultation_notifications: bool = True
    prescription_notifications: bool = True
    lab_result_notifications: bool = True
    appointment_notifications: bool = True
    vital_alerts: bool = True
    medication_reminders: bool = True
    general_notifications: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")  # HH:MM format
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class SyncPreferences(BaseModel):
    """Sync preferences."""
    auto_sync_enabled: bool = True
    sync_on_wifi_only: bool = False
    sync_frequency: str = Field("realtime", pattern="^(realtime|hourly|daily|manual)$")
    sync_health_records: bool = True
    sync_prescriptions: bool = True
    sync_lab_reports: bool = True
    sync_vital_data: bool = True


class PrivacySettings(BaseModel):
    """Privacy settings."""
    share_data_for_research: bool = False
    allow_analytics: bool = True
    allow_crash_reporting: bool = True
    data_retention_days: int = Field(365, ge=30, le=3650)  # 30 days to 10 years


class SecurityInfo(BaseModel):
    """Security information response."""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    tls_version: str = "TLS 1.3"
    two_factor_enabled: bool = False
    last_password_change: Optional[datetime] = None
    account_created: datetime
    last_login: Optional[datetime] = None
    active_sessions: int = 0


class StorageInfo(BaseModel):
    """Offline storage information."""
    used_mb: float = Field(..., ge=0)
    total_mb: float = Field(..., ge=0)
    usage_percentage: float = Field(..., ge=0, le=100)
    breakdown: Dict[str, float] = Field(default_factory=dict)  # Type -> MB
    last_cleared: Optional[datetime] = None


class SettingsUpdateRequest(BaseModel):
    """Update settings request."""
    language: Optional[LanguageCode] = None
    appearance: Optional[AppearanceMode] = None
    notifications: Optional[NotificationPreferences] = None
    sync: Optional[SyncPreferences] = None
    privacy: Optional[PrivacySettings] = None


class UserSettingsResponse(BaseModel):
    """Complete user settings response."""
    user_id: str
    language: LanguageCode = LanguageCode.ENGLISH
    appearance: AppearanceMode = AppearanceMode.SYSTEM
    notifications: NotificationPreferences
    sync: SyncPreferences
    privacy: PrivacySettings
    storage: StorageInfo
    security: SecurityInfo
    created_at: datetime
    updated_at: datetime


class ClearStorageRequest(BaseModel):
    """Clear storage request."""
    clear_cache: bool = True
    clear_offline_records: bool = False
    clear_media: bool = False
    clear_all: bool = False


class ClearStorageResponse(BaseModel):
    """Clear storage response."""
    cleared_mb: float
    remaining_mb: float
    cleared_at: datetime

