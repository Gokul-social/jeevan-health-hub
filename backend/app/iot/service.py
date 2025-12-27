"""
IoT Vital Data Service

Business logic for IoT device data collection, time-series storage, and alert generation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from google.cloud.firestore import AsyncClient
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class IoTService:
    """Service for IoT vital data management."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.vital_data_collection = db.collection("vital_data")
        self.devices_collection = db.collection("iot_devices")
        self.alerts_collection = db.collection("vital_alerts")
        
        # Load thresholds from config
        self.thresholds = settings.IOT_ALERT_THRESHOLDS
    
    async def authenticate_device(self, device_id: str, device_token: str) -> Optional[str]:
        """
        Authenticate IoT device and return associated user ID.
        
        Args:
            device_id: Device identifier
            device_token: Device authentication token
            
        Returns:
            User ID if authenticated, None otherwise
        """
        doc_ref = self.devices_collection.document(device_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        device_data = doc.to_dict()
        
        # Verify token (in production, use secure token hashing)
        if device_data.get("token") != device_token:
            return None
        
        if not device_data.get("is_active", False):
            return None
        
        return device_data.get("user_id")
    
    async def store_vital_data(
        self,
        user_id: str,
        device_id: str,
        data_point: dict
    ) -> dict:
        """
        Store a single vital data point with alert checking.
        
        Args:
            user_id: User ID
            device_id: Device ID
            data_point: Vital data point
            
        Returns:
            Stored data document with alerts
        """
        # Check thresholds and generate alerts
        alerts = self._check_thresholds(data_point)
        
        vital_doc = {
            "user_id": user_id,
            "device_id": device_id,
            "timestamp": data_point.get("timestamp", datetime.utcnow()),
            "heart_rate": data_point.get("heart_rate"),
            "systolic_bp": data_point.get("systolic_bp"),
            "diastolic_bp": data_point.get("diastolic_bp"),
            "spo2": data_point.get("spo2"),
            "temperature": data_point.get("temperature"),
            "glucose": data_point.get("glucose"),
            "weight": data_point.get("weight"),
            "alerts": alerts,
            "metadata": data_point.get("metadata", {}),
            "created_at": datetime.utcnow()
        }
        
        doc_ref = self.vital_data_collection.document()
        await doc_ref.set(vital_doc)
        
        vital_doc["id"] = doc_ref.id
        
        # Create alert documents if any
        if alerts:
            await self._create_alert_documents(user_id, device_id, alerts, vital_doc)
        
        logger.info(f"Vital data stored: {doc_ref.id} for user {user_id}")
        
        return vital_doc
    
    async def batch_store_vital_data(
        self,
        user_id: str,
        device_id: str,
        data_points: List[dict]
    ) -> List[dict]:
        """
        Store multiple vital data points in batch.
        
        Args:
            user_id: User ID
            device_id: Device ID
            data_points: List of vital data points
            
        Returns:
            List of stored data documents
        """
        stored = []
        
        for data_point in data_points:
            stored_doc = await self.store_vital_data(user_id, device_id, data_point)
            stored.append(stored_doc)
        
        return stored
    
    async def get_vital_data_time_series(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        metrics: List[str] = None,
        aggregation: str = "none"
    ) -> List[dict]:
        """
        Get time-series vital data for a user.
        
        Args:
            user_id: User ID
            start_time: Start timestamp
            end_time: End timestamp
            metrics: List of metrics to retrieve
            aggregation: Aggregation level (none, hourly, daily)
            
        Returns:
            List of vital data points
        """
        query = (
            self.vital_data_collection
            .where("user_id", "==", user_id)
            .where("timestamp", ">=", start_time)
            .where("timestamp", "<=", end_time)
            .order_by("timestamp")
        )
        
        data_points = []
        async for doc in query.stream():
            data = doc.to_dict()
            
            # Filter by metrics if specified
            if metrics:
                filtered_data = {"id": doc.id, "timestamp": data.get("timestamp")}
                for metric in metrics:
                    if metric in data:
                        filtered_data[metric] = data[metric]
                data_points.append(filtered_data)
            else:
                data["id"] = doc.id
                data_points.append(data)
        
        # Apply aggregation if requested
        if aggregation != "none":
            data_points = self._aggregate_data(data_points, aggregation, metrics or [])
        
        return data_points
    
    async def get_recent_vitals(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[dict]:
        """
        Get most recent vital data points.
        
        Args:
            user_id: User ID
            limit: Number of recent points to retrieve
            
        Returns:
            List of recent vital data points
        """
        query = (
            self.vital_data_collection
            .where("user_id", "==", user_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
        )
        
        data_points = []
        async for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            data_points.append(data)
        
        return data_points
    
    async def get_active_alerts(
        self,
        user_id: str
    ) -> List[dict]:
        """
        Get active vital sign alerts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active alerts
        """
        query = (
            self.alerts_collection
            .where("user_id", "==", user_id)
            .where("resolved", "==", False)
            .order_by("created_at", direction="DESCENDING")
        )
        
        alerts = []
        async for doc in query.stream():
            alert_data = doc.to_dict()
            alert_data["id"] = doc.id
            alerts.append(alert_data)
        
        return alerts
    
    def _check_thresholds(self, data_point: dict) -> List[str]:
        """
        Check vital data against thresholds and generate alerts.
        
        Args:
            data_point: Vital data point
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Heart rate
        heart_rate = data_point.get("heart_rate")
        if heart_rate:
            if heart_rate < self.thresholds.get("heart_rate_min", 60):
                alerts.append(f"Low heart rate: {heart_rate} BPM (normal: {self.thresholds.get('heart_rate_min')}-{self.thresholds.get('heart_rate_max')})")
            elif heart_rate > self.thresholds.get("heart_rate_max", 100):
                alerts.append(f"High heart rate: {heart_rate} BPM (normal: {self.thresholds.get('heart_rate_min')}-{self.thresholds.get('heart_rate_max')})")
        
        # Blood pressure
        systolic = data_point.get("systolic_bp")
        diastolic = data_point.get("diastolic_bp")
        if systolic and systolic > self.thresholds.get("bp_systolic_max", 140):
            alerts.append(f"High systolic BP: {systolic} mmHg (normal: <{self.thresholds.get('bp_systolic_max')})")
        if diastolic and diastolic > self.thresholds.get("bp_diastolic_max", 90):
            alerts.append(f"High diastolic BP: {diastolic} mmHg (normal: <{self.thresholds.get('bp_diastolic_max')})")
        
        # SpO2
        spo2 = data_point.get("spo2")
        if spo2 and spo2 < self.thresholds.get("spo2_min", 95):
            alerts.append(f"Low SpO2: {spo2}% (normal: >{self.thresholds.get('spo2_min')}%)")
        
        return alerts
    
    async def _create_alert_documents(
        self,
        user_id: str,
        device_id: str,
        alerts: List[str],
        vital_data: dict
    ):
        """Create alert documents for critical vital signs."""
        for alert_message in alerts:
            alert_level = "critical" if any(keyword in alert_message.lower() for keyword in ["high", "low", "critical"]) else "warning"
            
            alert_doc = {
                "user_id": user_id,
                "device_id": device_id,
                "vital_data_id": vital_data.get("id"),
                "alert_message": alert_message,
                "alert_level": alert_level,
                "timestamp": vital_data.get("timestamp"),
                "created_at": datetime.utcnow(),
                "resolved": False,
                "resolved_at": None
            }
            
            await self.alerts_collection.add(alert_doc)
    
    def _aggregate_data(
        self,
        data_points: List[dict],
        aggregation: str,
        metrics: List[str]
    ) -> List[dict]:
        """
        Aggregate time-series data.
        
        Args:
            data_points: Raw data points
            aggregation: Aggregation level (hourly, daily)
            metrics: Metrics to aggregate
            
        Returns:
            Aggregated data points
        """
        # Simplified aggregation - in production, use proper time-series aggregation
        if not data_points:
            return []
        
        # Group by time window
        grouped = {}
        
        for point in data_points:
            timestamp = point.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if aggregation == "hourly":
                key = timestamp.replace(minute=0, second=0, microsecond=0)
            elif aggregation == "daily":
                key = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                key = timestamp
            
            if key not in grouped:
                grouped[key] = {"timestamp": key, "count": 0, "values": {metric: [] for metric in metrics}}
            
            grouped[key]["count"] += 1
            for metric in metrics:
                if metric in point and point[metric] is not None:
                    grouped[key]["values"][metric].append(point[metric])
        
        # Calculate averages
        aggregated = []
        for key, group in sorted(grouped.items()):
            agg_point = {"timestamp": group["timestamp"]}
            for metric in metrics:
                values = group["values"][metric]
                if values:
                    agg_point[metric] = sum(values) / len(values)
                else:
                    agg_point[metric] = None
            aggregated.append(agg_point)
        
        return aggregated

