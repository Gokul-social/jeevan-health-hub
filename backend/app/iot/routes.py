"""
IoT Vital Data Routes

API endpoints for IoT device data collection and vital sign monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from google.cloud.firestore import AsyncClient
from typing import Optional, List
from datetime import datetime
import logging

from app.iot.schemas import (
    VitalDataBatch,
    VitalDataResponse,
    TimeSeriesQuery
)
from app.iot.service import IoTService
from app.core.dependencies import get_firestore_db
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/data/batch", status_code=status.HTTP_201_CREATED)
async def batch_store_vital_data(
    batch: VitalDataBatch,
    db: AsyncClient = Depends(get_firestore_db)
):
    """
    Store batch of vital data from IoT device.
    
    Requires device authentication via device_token.
    """
    try:
        service = IoTService(db)
        
        # Authenticate device
        user_id = await service.authenticate_device(batch.device_id, batch.device_token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid device credentials"
            )
        
        # Convert Pydantic models to dicts
        data_points = [dp.model_dump() for dp in batch.data_points]
        
        # Store data
        stored = await service.batch_store_vital_data(user_id, batch.device_id, data_points)
        
        return {
            "message": f"Stored {len(stored)} data points",
            "stored_count": len(stored)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Store vital data error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store vital data"
        )


@router.get("/data/recent", response_model=List[VitalDataResponse])
async def get_recent_vitals(
    limit: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get most recent vital data points for current user."""
    try:
        service = IoTService(db)
        vitals = await service.get_recent_vitals(user_id, limit)
        
        return [VitalDataResponse(**v) for v in vitals]
    
    except Exception as e:
        logger.error(f"Get recent vitals error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vital data"
        )


@router.post("/data/timeseries", response_model=List[dict])
async def get_time_series(
    query: TimeSeriesQuery,
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get time-series vital data for a date range."""
    try:
        service = IoTService(db)
        data_points = await service.get_vital_data_time_series(
            user_id=user_id,
            start_time=query.start_time,
            end_time=query.end_time,
            metrics=query.metrics,
            aggregation=query.aggregation
        )
        
        return data_points
    
    except Exception as e:
        logger.error(f"Get time series error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve time series data"
        )


@router.get("/alerts", response_model=List[dict])
async def get_active_alerts(
    user_id: str = Depends(get_current_user_id),
    db: AsyncClient = Depends(get_firestore_db)
):
    """Get active vital sign alerts for current user."""
    try:
        service = IoTService(db)
        alerts = await service.get_active_alerts(user_id)
        
        return alerts
    
    except Exception as e:
        logger.error(f"Get alerts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )

