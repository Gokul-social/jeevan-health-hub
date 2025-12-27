"""
IoT Vital Data Schemas

Pydantic models for IoT device vital sign data collection.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class VitalDataPoint(BaseModel):
    """Individual vital sign data point."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    heart_rate: Optional[int] = Field(None, ge=0, le=300, description="BPM")
    systolic_bp: Optional[int] = Field(None, ge=0, le=300, description="mmHg")
    diastolic_bp: Optional[int] = Field(None, ge=0, le=200, description="mmHg")
    spo2: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage")
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0, description="Celsius")
    glucose: Optional[float] = Field(None, ge=0.0, description="mg/dL")
    weight: Optional[float] = Field(None, ge=0.0, description="kg")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VitalDataBatch(BaseModel):
    """Batch of vital data points from IoT device."""
    device_id: str = Field(..., description="IoT device identifier")
    device_token: str = Field(..., description="Device authentication token")
    data_points: List[VitalDataPoint] = Field(..., min_length=1, max_length=100)


class VitalDataResponse(BaseModel):
    """Vital data response."""
    id: str
    user_id: str
    device_id: str
    timestamp: datetime
    heart_rate: Optional[int]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    spo2: Optional[float]
    temperature: Optional[float]
    glucose: Optional[float]
    weight: Optional[float]
    alerts: List[str] = Field(default_factory=list, description="Generated alerts")
    created_at: datetime


class AlertThreshold(BaseModel):
    """Alert threshold configuration."""
    metric: str = Field(..., pattern="^(heart_rate|bp|spo2|temperature|glucose)$")
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    alert_level: str = Field("warning", pattern="^(warning|critical)$")


class TimeSeriesQuery(BaseModel):
    """Query parameters for time-series vital data."""
    start_time: datetime
    end_time: datetime
    metrics: List[str] = Field(default_factory=lambda: ["heart_rate", "spo2", "bp"])
    aggregation: Optional[str] = Field("none", pattern="^(none|hourly|daily)$")

