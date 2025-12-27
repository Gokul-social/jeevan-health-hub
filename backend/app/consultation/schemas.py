"""
Consultation Schemas

Pydantic models for telemedicine consultation sessions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConsultationStatus(str, Enum):
    """Consultation session status."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"


class ConsultationType(str, Enum):
    """Type of consultation."""
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class ConsultationCreate(BaseModel):
    """Create consultation session."""
    doctor_id: str = Field(..., description="Doctor user ID")
    patient_id: Optional[str] = None  # If not provided, uses current user
    scheduled_time: Optional[datetime] = None
    consultation_type: ConsultationType = ConsultationType.VIDEO
    reason: Optional[str] = None
    notes: Optional[str] = None


class WebRTCSignal(BaseModel):
    """WebRTC signaling message."""
    consultation_id: str
    signal_type: str = Field(..., description="offer, answer, ice-candidate")
    signal_data: Dict[str, Any]
    from_user_id: str
    to_user_id: str


class ConsultationResponse(BaseModel):
    """Consultation session response."""
    id: str
    doctor_id: str
    patient_id: str
    status: ConsultationStatus
    consultation_type: ConsultationType
    scheduled_time: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    reason: Optional[str]
    notes: Optional[str]
    session_token: Optional[str] = Field(None, description="Encrypted session token for WebRTC")
    webrtc_config: Optional[Dict[str, Any]] = Field(None, description="WebRTC configuration")
    created_at: datetime
    updated_at: datetime


class ConsultationJoinResponse(BaseModel):
    """Response when joining a consultation."""
    consultation_id: str
    session_token: str
    webrtc_config: Dict[str, Any]
    other_participant_id: str
    status: ConsultationStatus

