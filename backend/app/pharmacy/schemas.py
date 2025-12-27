"""
Pharmacy Schemas

Pydantic models for pharmacy and medicine availability management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PharmacyCreate(BaseModel):
    """Create pharmacy entry."""
    name: str = Field(..., min_length=1)
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    operating_hours: Dict[str, Any] = Field(default_factory=dict)
    is_24x7: bool = False


class MedicineStockUpdate(BaseModel):
    """Update medicine stock."""
    medicine_name: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)
    unit: str = Field("units", description="units, strips, bottles, etc.")
    expiry_date: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    manufacturer: Optional[str] = None


class PharmacyResponse(BaseModel):
    """Pharmacy response."""
    id: str
    name: str
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    operating_hours: Dict[str, Any]
    is_24x7: bool
    created_at: datetime
    updated_at: datetime


class MedicineAvailability(BaseModel):
    """Medicine availability information."""
    medicine_name: str
    pharmacy_id: str
    pharmacy_name: str
    quantity: int
    unit: str
    price: Optional[float]
    distance_km: Optional[float] = None
    in_stock: bool = True


class MedicineSearchRequest(BaseModel):
    """Search for medicine availability."""
    medicine_name: str = Field(..., min_length=1)
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = Field(10.0, ge=0, description="Search radius in kilometers")
    min_quantity: Optional[int] = Field(1, ge=0)


class LowStockAlert(BaseModel):
    """Low stock alert."""
    pharmacy_id: str
    medicine_name: str
    current_quantity: int
    threshold: int
    alert_level: str = Field(..., pattern="^(warning|critical)$")

