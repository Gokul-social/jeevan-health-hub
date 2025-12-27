"""
AI Symptom Checker Routes

API endpoints for AI-powered symptom analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from google.cloud.firestore import AsyncClient
import logging

from app.ai.schemas import SymptomCheckRequest, SymptomCheckResponse
from app.ai.service import AISymptomCheckerService
from app.core.dependencies import get_firestore_db, rate_limit_dependency
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/symptom-check", response_model=SymptomCheckResponse)
async def check_symptoms(
    request: SymptomCheckRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db),
    http_request: Request = None,
    _: None = Depends(rate_limit_dependency)
):
    """
    Analyze symptoms and return possible conditions with recommendations.
    
    Supports local rule-based logic with cloud AI fallback.
    """
    try:
        service = AISymptomCheckerService()
        result = await service.check_symptoms(request)
        
        # Optional: Store symptom check history in Firestore
        # await _store_symptom_check_history(user_id, request, result, db)
        
        return result
    
    except Exception as e:
        logger.error(f"Symptom check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze symptoms"
        )

