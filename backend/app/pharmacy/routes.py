"""
Pharmacy Routes

API endpoints for pharmacy and medicine availability management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from google.cloud.firestore import AsyncClient
from typing import Optional, List
import logging

from app.pharmacy.schemas import (
    PharmacyCreate,
    PharmacyResponse,
    MedicineStockUpdate,
    MedicineAvailability,
    MedicineSearchRequest,
    LowStockAlert
)
from app.pharmacy.service import PharmacyService
from app.core.dependencies import get_firestore_db
from app.core.security import require_role

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=PharmacyResponse, status_code=status.HTTP_201_CREATED)
async def create_pharmacy(
    pharmacy: PharmacyCreate,
    user_id: str = Depends(require_role(["admin"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Create a new pharmacy (admin only)."""
    try:
        service = PharmacyService(db)
        pharmacy_data = pharmacy.model_dump()
        created = await service.create_pharmacy(pharmacy_data)
        
        return PharmacyResponse(**created)
    
    except Exception as e:
        logger.error(f"Create pharmacy error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pharmacy"
        )


@router.get("/{pharmacy_id}", response_model=PharmacyResponse)
async def get_pharmacy(
    pharmacy_id: str,
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get pharmacy details."""
    try:
        service = PharmacyService(db)
        pharmacy = await service.get_pharmacy(pharmacy_id)
        
        if not pharmacy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pharmacy not found"
            )
        
        return PharmacyResponse(**pharmacy)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get pharmacy error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pharmacy"
        )


@router.put("/{pharmacy_id}/stock", status_code=status.HTTP_200_OK)
async def update_stock(
    pharmacy_id: str,
    stock_update: MedicineStockUpdate,
    user_id: str = Depends(require_role(["admin", "doctor"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Update medicine stock for a pharmacy."""
    try:
        service = PharmacyService(db)
        updated = await service.update_medicine_stock(
            pharmacy_id=pharmacy_id,
            medicine_name=stock_update.medicine_name,
            quantity=stock_update.quantity,
            unit=stock_update.unit,
            expiry_date=stock_update.expiry_date,
            price=stock_update.price,
            manufacturer=stock_update.manufacturer
        )
        
        return {"message": "Stock updated successfully", "stock": updated}
    
    except Exception as e:
        logger.error(f"Update stock error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update stock"
        )


@router.post("/search", response_model=List[MedicineAvailability])
async def search_medicine(
    search_request: MedicineSearchRequest,
    db: AsyncClient = Depends(get_firestore_db)
):
    """Search for medicine availability in nearby pharmacies."""
    try:
        service = PharmacyService(db)
        results = await service.search_medicine_availability(
            medicine_name=search_request.medicine_name,
            city=search_request.city,
            state=search_request.state,
            pincode=search_request.pincode,
            latitude=search_request.latitude,
            longitude=search_request.longitude,
            radius_km=search_request.radius_km,
            min_quantity=search_request.min_quantity
        )
        
        return [MedicineAvailability(**r) for r in results]
    
    except Exception as e:
        logger.error(f"Search medicine error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search medicine"
        )


@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
async def get_low_stock_alerts(
    pharmacy_id: Optional[str] = Query(None),
    user_id: str = Depends(require_role(["admin", "doctor"])),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get low stock alerts."""
    try:
        service = PharmacyService(db)
        alerts = await service.get_low_stock_alerts(pharmacy_id)
        
        return [LowStockAlert(**a) for a in alerts]
    
    except Exception as e:
        logger.error(f"Get alerts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )

