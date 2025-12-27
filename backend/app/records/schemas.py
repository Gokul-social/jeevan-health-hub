"""
Health Records Schemas

Pydantic models for medical history, prescriptions, and lab reports.
Designed for offline-first sync with versioning and conflict resolution.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RecordType(str, Enum):
    """Types of health records."""
    MEDICAL_HISTORY = "medical_history"
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    VITAL_SIGN = "vital_sign"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"


class MedicalHistoryCreate(BaseModel):
    """Create medical history record."""
    title: str = Field(..., min_length=1)
    description: str
    condition: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    attachments: List[str] = []  # Firebase Storage URLs
    metadata: Dict[str, Any] = {}
    client_version: int = Field(..., description="Client-side version for conflict resolution")


class PrescriptionCreate(BaseModel):
    """Create prescription record."""
    doctor_id: Optional[str] = None
    doctor_name: str
    medications: List[Dict[str, Any]] = Field(..., description="List of medications with dosage, frequency, etc.")
    instructions: Optional[str] = None
    prescribed_date: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    attachments: List[str] = []
    metadata: Dict[str, Any] = {}
    client_version: int


class LabReportCreate(BaseModel):
    """Create lab report record."""
    test_name: str
    test_type: str
    lab_name: Optional[str] = None
    test_date: datetime = Field(default_factory=datetime.utcnow)
    results: Dict[str, Any] = Field(..., description="Test results as key-value pairs")
    normal_ranges: Optional[Dict[str, Any]] = None
    doctor_notes: Optional[str] = None
    attachments: List[str] = []  # Report PDF/image URLs
    metadata: Dict[str, Any] = {}
    client_version: int


class HealthRecordResponse(BaseModel):
    """Health record response with versioning info."""
    id: str
    user_id: str
    record_type: RecordType
    data: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    is_deleted: bool = False
    sync_status: str = "synced"  # synced, pending, conflict


class ConflictResolutionRequest(BaseModel):
    """Request to resolve a sync conflict."""
    record_id: str
    chosen_version: int = Field(..., description="Version to keep (server or client)")
    resolved_data: Dict[str, Any] = Field(..., description="Merged or chosen data")


class RecordListResponse(BaseModel):
    """Paginated list of health records."""
    records: List[HealthRecordResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

