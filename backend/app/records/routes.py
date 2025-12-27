"""
Health Records Routes

API endpoints for health records CRUD operations with offline-first support.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from google.cloud.firestore import AsyncClient
from typing import Optional, List
import logging

from app.records.schemas import (
    RecordType,
    MedicalHistoryCreate,
    PrescriptionCreate,
    LabReportCreate,
    HealthRecordResponse,
    ConflictResolutionRequest,
    RecordListResponse
)
from app.records.service import HealthRecordsService
from app.core.dependencies import get_firestore_db
from app.core.security import get_current_user_id, require_role

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/medical-history", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_history(
    record: MedicalHistoryCreate,
    user_id: str = Depends(require_role(["patient", "admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Create a medical history record."""
    try:
        service = HealthRecordsService(db)
        
        record_data = {
            "title": record.title,
            "description": record.description,
            "condition": record.condition,
            "diagnosis_date": record.diagnosis_date.isoformat() if record.diagnosis_date else None,
            "doctor_name": record.doctor_name,
            "hospital_name": record.hospital_name,
            "attachments": record.attachments,
            "metadata": record.metadata
        }
        
        created = await service.create_record(
            user_id=user_id,
            record_type=RecordType.MEDICAL_HISTORY,
            data=record_data,
            client_version=record.client_version,
            created_by=user_id
        )
        
        if created.get("conflict"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Version conflict detected",
                    "server_version": created.get("server_version"),
                    "client_version": created.get("client_version")
                }
            )
        
        return HealthRecordResponse(**created)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create medical history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medical history"
        )


@router.post("/prescription", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    record: PrescriptionCreate,
    user_id: str = Depends(require_role(["patient", "admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Create a prescription record."""
    try:
        service = HealthRecordsService(db)
        
        record_data = {
            "doctor_id": record.doctor_id,
            "doctor_name": record.doctor_name,
            "medications": record.medications,
            "instructions": record.instructions,
            "prescribed_date": record.prescribed_date.isoformat(),
            "valid_until": record.valid_until.isoformat() if record.valid_until else None,
            "attachments": record.attachments,
            "metadata": record.metadata
        }
        
        created = await service.create_record(
            user_id=user_id,
            record_type=RecordType.PRESCRIPTION,
            data=record_data,
            client_version=record.client_version,
            created_by=record.doctor_id or user_id
        )
        
        if created.get("conflict"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Version conflict detected",
                    "server_version": created.get("server_version"),
                    "client_version": created.get("client_version")
                }
            )
        
        return HealthRecordResponse(**created)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create prescription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prescription"
        )


@router.post("/lab-report", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_report(
    record: LabReportCreate,
    user_id: str = Depends(require_role(["patient", "admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Create a lab report record."""
    try:
        service = HealthRecordsService(db)
        
        record_data = {
            "test_name": record.test_name,
            "test_type": record.test_type,
            "lab_name": record.lab_name,
            "test_date": record.test_date.isoformat(),
            "results": record.results,
            "normal_ranges": record.normal_ranges,
            "doctor_notes": record.doctor_notes,
            "attachments": record.attachments,
            "metadata": record.metadata
        }
        
        created = await service.create_record(
            user_id=user_id,
            record_type=RecordType.LAB_REPORT,
            data=record_data,
            client_version=record.client_version,
            created_by=user_id
        )
        
        if created.get("conflict"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Version conflict detected",
                    "server_version": created.get("server_version"),
                    "client_version": created.get("client_version")
                }
            )
        
        return HealthRecordResponse(**created)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create lab report error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lab report"
        )


@router.get("/", response_model=RecordListResponse)
async def list_records(
    record_type: Optional[RecordType] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """List health records with pagination."""
    try:
        service = HealthRecordsService(db)
        result = await service.list_records(
            user_id=user_id,
            record_type=record_type,
            page=page,
            page_size=page_size
        )
        
        return RecordListResponse(**result)
    
    except Exception as e:
        logger.error(f"List records error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list records"
        )


@router.get("/{record_id}", response_model=HealthRecordResponse)
async def get_record(
    record_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get a specific health record."""
    try:
        service = HealthRecordsService(db)
        record = await service.get_record(record_id, user_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        return HealthRecordResponse(**record)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get record error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve record"
        )


@router.put("/{record_id}", response_model=HealthRecordResponse)
async def update_record(
    record_id: str,
    update_data: dict,
    client_version: int = Query(..., ge=1),
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Update a health record with conflict detection."""
    try:
        service = HealthRecordsService(db)
        updated = await service.update_record(
            record_id=record_id,
            user_id=user_id,
            update_data=update_data,
            client_version=client_version
        )
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        if updated.get("conflict"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Version conflict detected",
                    "server_version": updated.get("server_version"),
                    "client_version": updated.get("client_version"),
                    "server_data": updated.get("server_data")
                }
            )
        
        return HealthRecordResponse(**updated)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update record error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update record"
        )


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
async def delete_record(
    record_id: str,
    soft_delete: bool = Query(True),
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Delete a health record."""
    try:
        service = HealthRecordsService(db)
        success = await service.delete_record(record_id, user_id, soft_delete)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        return {"message": "Record deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete record error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete record"
        )


@router.post("/resolve-conflict", response_model=HealthRecordResponse)
async def resolve_conflict(
    conflict_request: ConflictResolutionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Resolve a sync conflict."""
    try:
        service = HealthRecordsService(db)
        resolved = await service.resolve_conflict(conflict_request, user_id)
        
        if not resolved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        return HealthRecordResponse(**resolved)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolve conflict error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve conflict"
        )


@router.get("/sync/pending", response_model=List[HealthRecordResponse])
async def get_pending_sync(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get records pending sync (for offline-first support)."""
    try:
        service = HealthRecordsService(db)
        records = await service.get_pending_sync_records(user_id)
        
        return [HealthRecordResponse(**r) for r in records]
    
    except Exception as e:
        logger.error(f"Get pending sync error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending sync records"
        )

