"""
Consultation Routes

API endpoints for telemedicine consultations and WebRTC signaling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import AsyncClient
import logging

from app.consultation.schemas import (
    ConsultationCreate,
    ConsultationResponse,
    ConsultationJoinResponse,
    WebRTCSignal
)
from app.consultation.service import ConsultationService
from app.core.dependencies import get_firestore_db
from app.core.security import get_current_user_id, require_role

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    consultation: ConsultationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Create a new consultation session."""
    try:
        service = ConsultationService(db)
        
        # Use current user as patient if not specified
        patient_id = consultation.patient_id or user_id
        
        # Verify user is patient or doctor
        if user_id != patient_id and user_id != consultation.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create consultations for yourself or as a doctor"
            )
        
        created = await service.create_consultation(
            doctor_id=consultation.doctor_id,
            patient_id=patient_id,
            consultation_type=consultation.consultation_type,
            scheduled_time=consultation.scheduled_time,
            reason=consultation.reason,
            notes=consultation.notes
        )
        
        return ConsultationResponse(**created)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create consultation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create consultation"
        )


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get consultation details."""
    try:
        service = ConsultationService(db)
        consultation = await service.get_consultation(consultation_id, user_id)
        
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        return ConsultationResponse(**consultation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get consultation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consultation"
        )


@router.post("/{consultation_id}/join", response_model=ConsultationJoinResponse)
async def join_consultation(
    consultation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Join an active consultation."""
    try:
        service = ConsultationService(db)
        join_data = await service.join_consultation(consultation_id, user_id)
        
        return ConsultationJoinResponse(**join_data)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Join consultation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join consultation"
        )


@router.post("/{consultation_id}/end", status_code=status.HTTP_200_OK)
async def end_consultation(
    consultation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """End a consultation session."""
    try:
        service = ConsultationService(db)
        success = await service.end_consultation(consultation_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        return {"message": "Consultation ended successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End consultation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end consultation"
        )


@router.post("/{consultation_id}/signal", status_code=status.HTTP_200_OK)
async def send_webrtc_signal(
    consultation_id: str,
    signal: WebRTCSignal,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Send WebRTC signaling message."""
    try:
        service = ConsultationService(db)
        
        # Verify consultation access
        consultation = await service.get_consultation(consultation_id, user_id)
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        # Verify sender
        if signal.from_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot send signal on behalf of another user"
            )
        
        await service.send_webrtc_signal(
            consultation_id=consultation_id,
            from_user_id=signal.from_user_id,
            to_user_id=signal.to_user_id,
            signal_type=signal.signal_type,
            signal_data=signal.signal_data
        )
        
        return {"message": "Signal sent successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send signal error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send signal"
        )


@router.get("/{consultation_id}/signals", status_code=status.HTTP_200_OK)
async def get_pending_signals(
    consultation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get pending WebRTC signals for current user."""
    try:
        service = ConsultationService(db)
        
        # Verify consultation access
        consultation = await service.get_consultation(consultation_id, user_id)
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        signals = await service.get_pending_signals(consultation_id, user_id)
        
        return {"signals": signals}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get signals error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve signals"
        )

