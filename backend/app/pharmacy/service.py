"""
Pharmacy Service

Business logic for pharmacy management and medicine availability.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging
import math

logger = logging.getLogger(__name__)


class PharmacyService:
    """Service for pharmacy and medicine management."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.pharmacies_collection = db.collection("pharmacies")
        self.medicine_stock_collection = db.collection("medicine_stock")
        self.low_stock_threshold = 10  # Default threshold
    
    async def create_pharmacy(self, pharmacy_data: dict) -> dict:
        """
        Create a new pharmacy.
        
        Args:
            pharmacy_data: Pharmacy information
            
        Returns:
            Created pharmacy document
        """
        pharmacy_doc = {
            **pharmacy_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        doc_ref = self.pharmacies_collection.document()
        await doc_ref.set(pharmacy_doc)
        
        pharmacy_doc["id"] = doc_ref.id
        logger.info(f"Pharmacy created: {doc_ref.id}")
        
        return pharmacy_doc
    
    async def get_pharmacy(self, pharmacy_id: str) -> Optional[dict]:
        """Get pharmacy by ID."""
        doc_ref = self.pharmacies_collection.document(pharmacy_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    
    async def update_medicine_stock(
        self,
        pharmacy_id: str,
        medicine_name: str,
        quantity: int,
        unit: str = "units",
        expiry_date: Optional[str] = None,
        price: Optional[float] = None,
        manufacturer: Optional[str] = None
    ) -> dict:
        """
        Update medicine stock for a pharmacy.
        
        Args:
            pharmacy_id: Pharmacy ID
            medicine_name: Medicine name
            quantity: Stock quantity
            unit: Unit of measurement
            expiry_date: Expiry date
            price: Price per unit
            manufacturer: Manufacturer name
            
        Returns:
            Updated stock document
        """
        # Check if stock entry exists
        stock_query = (
            self.medicine_stock_collection
            .where("pharmacy_id", "==", pharmacy_id)
            .where("medicine_name", "==", medicine_name.lower())
            .limit(1)
        )
        
        stock_docs = [doc async for doc in stock_query.stream()]
        
        stock_data = {
            "pharmacy_id": pharmacy_id,
            "medicine_name": medicine_name.lower(),
            "quantity": quantity,
            "unit": unit,
            "expiry_date": expiry_date,
            "price": price,
            "manufacturer": manufacturer,
            "updated_at": datetime.utcnow(),
            "last_restocked": datetime.utcnow()
        }
        
        if stock_docs:
            # Update existing
            doc_ref = stock_docs[0].reference
            await doc_ref.update(stock_data)
            stock_data["id"] = doc_ref.id
        else:
            # Create new
            stock_data["created_at"] = datetime.utcnow()
            doc_ref = self.medicine_stock_collection.document()
            await doc_ref.set(stock_data)
            stock_data["id"] = doc_ref.id
        
        # Check for low stock alert
        if quantity <= self.low_stock_threshold:
            await self._create_low_stock_alert(pharmacy_id, medicine_name, quantity)
        
        logger.info(f"Stock updated: {medicine_name} at pharmacy {pharmacy_id}")
        
        return stock_data
    
    async def search_medicine_availability(
        self,
        medicine_name: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 10.0,
        min_quantity: int = 1
    ) -> List[dict]:
        """
        Search for medicine availability in nearby pharmacies.
        
        Args:
            medicine_name: Medicine to search for
            city: Filter by city
            state: Filter by state
            pincode: Filter by pincode
            latitude: User latitude for distance calculation
            longitude: User longitude for distance calculation
            radius_km: Search radius in kilometers
            min_quantity: Minimum required quantity
            
        Returns:
            List of available medicines with pharmacy info
        """
        # Search stock
        stock_query = (
            self.medicine_stock_collection
            .where("medicine_name", "==", medicine_name.lower())
            .where("quantity", ">=", min_quantity)
        )
        
        results = []
        
        async for stock_doc in stock_query.stream():
            stock_data = stock_doc.to_dict()
            pharmacy_id = stock_data.get("pharmacy_id")
            
            # Get pharmacy info
            pharmacy = await self.get_pharmacy(pharmacy_id)
            if not pharmacy:
                continue
            
            # Apply location filters
            if city and pharmacy.get("city", "").lower() != city.lower():
                continue
            if state and pharmacy.get("state", "").lower() != state.lower():
                continue
            if pincode and pharmacy.get("pincode") != pincode:
                continue
            
            # Calculate distance if coordinates provided
            distance_km = None
            if latitude and longitude and pharmacy.get("latitude") and pharmacy.get("longitude"):
                distance_km = self._calculate_distance(
                    latitude, longitude,
                    pharmacy["latitude"], pharmacy["longitude"]
                )
                
                # Filter by radius
                if distance_km > radius_km:
                    continue
            
            results.append({
                "medicine_name": medicine_name,
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": pharmacy.get("name", ""),
                "quantity": stock_data.get("quantity", 0),
                "unit": stock_data.get("unit", "units"),
                "price": stock_data.get("price"),
                "distance_km": distance_km,
                "in_stock": True,
                "pharmacy_address": pharmacy.get("address", ""),
                "pharmacy_phone": pharmacy.get("phone", "")
            })
        
        # Sort by distance if available
        if latitude and longitude:
            results.sort(key=lambda x: x.get("distance_km", float('inf')))
        
        return results
    
    async def get_low_stock_alerts(self, pharmacy_id: Optional[str] = None) -> List[dict]:
        """
        Get low stock alerts.
        
        Args:
            pharmacy_id: Optional pharmacy ID filter
            
        Returns:
            List of low stock alerts
        """
        alerts_collection = self.db.collection("low_stock_alerts")
        query = alerts_collection.where("resolved", "==", False)
        
        if pharmacy_id:
            query = query.where("pharmacy_id", "==", pharmacy_id)
        
        alerts = []
        async for doc in query.stream():
            alert_data = doc.to_dict()
            alert_data["id"] = doc.id
            alerts.append(alert_data)
        
        return alerts
    
    async def _create_low_stock_alert(
        self,
        pharmacy_id: str,
        medicine_name: str,
        current_quantity: int
    ):
        """Create a low stock alert."""
        alert_level = "critical" if current_quantity <= 5 else "warning"
        
        alert_data = {
            "pharmacy_id": pharmacy_id,
            "medicine_name": medicine_name,
            "current_quantity": current_quantity,
            "threshold": self.low_stock_threshold,
            "alert_level": alert_level,
            "created_at": datetime.utcnow(),
            "resolved": False
        }
        
        await self.db.collection("low_stock_alerts").add(alert_data)
        logger.warning(f"Low stock alert: {medicine_name} at pharmacy {pharmacy_id}")
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        return R * c

