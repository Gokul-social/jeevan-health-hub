"""
Consultation Service

Business logic for telemedicine consultation sessions and WebRTC signaling.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging
import secrets

from app.core.config import settings
from app.core.encryption import encryption_service
from app.consultation.schemas import ConsultationStatus, ConsultationType

logger = logging.getLogger(__name__)


class ConsultationService:
    """Service for consultation management."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.consultations_collection = db.collection("consultations")
        self.signaling_collection = db.collection("webrtc_signaling")
    
    async def create_consultation(
        self,
        doctor_id: str,
        patient_id: str,
        consultation_type: ConsultationType = ConsultationType.VIDEO,
        scheduled_time: Optional[datetime] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> dict:
        """
        Create a new consultation session.
        
        Args:
            doctor_id: Doctor user ID
            patient_id: Patient user ID
            consultation_type: Type of consultation
            scheduled_time: Scheduled start time
            reason: Reason for consultation
            notes: Additional notes
            
        Returns:
            Consultation document data
        """
        consultation_data = {
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "status": ConsultationStatus.SCHEDULED.value if scheduled_time else ConsultationStatus.ACTIVE.value,
            "consultation_type": consultation_type.value,
            "scheduled_time": scheduled_time,
            "started_at": None if scheduled_time else datetime.utcnow(),
            "ended_at": None,
            "reason": reason,
            "notes": notes,
            "session_token": None,  # Generated on join
            "webrtc_config": self._generate_webrtc_config(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        doc_ref = self.consultations_collection.document()
        await doc_ref.set(consultation_data)
        
        consultation_data["id"] = doc_ref.id
        logger.info(f"Consultation created: {doc_ref.id}")
        
        return consultation_data
    
    async def get_consultation(
        self,
        consultation_id: str,
        user_id: str
    ) -> Optional[dict]:
        """
        Get consultation by ID (with authorization check).
        
        Args:
            consultation_id: Consultation document ID
            user_id: User ID (must be doctor or patient)
            
        Returns:
            Consultation document or None
        """
        doc_ref = self.consultations_collection.document(consultation_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        consultation_data = doc.to_dict()
        
        # Verify user is participant
        if (consultation_data.get("doctor_id") != user_id and
            consultation_data.get("patient_id") != user_id):
            return None
        
        consultation_data["id"] = doc.id
        return consultation_data
    
    async def join_consultation(
        self,
        consultation_id: str,
        user_id: str
    ) -> dict:
        """
        Join an active consultation and get session token.
        
        Args:
            consultation_id: Consultation document ID
            user_id: User ID joining
            
        Returns:
            Join response with session token and WebRTC config
        """
        consultation = await self.get_consultation(consultation_id, user_id)
        
        if not consultation:
            raise ValueError("Consultation not found or access denied")
        
        if consultation["status"] not in [
            ConsultationStatus.SCHEDULED.value,
            ConsultationStatus.ACTIVE.value
        ]:
            raise ValueError("Consultation is not active")
        
        # Generate session token
        session_token = self._generate_session_token(consultation_id, user_id)
        
        # Update consultation status if needed
        if consultation["status"] == ConsultationStatus.SCHEDULED.value:
            await self.consultations_collection.document(consultation_id).update({
                "status": ConsultationStatus.ACTIVE.value,
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Determine other participant
        other_participant_id = (
            consultation["patient_id"] if user_id == consultation["doctor_id"]
            else consultation["doctor_id"]
        )
        
        return {
            "consultation_id": consultation_id,
            "session_token": session_token,
            "webrtc_config": consultation.get("webrtc_config", {}),
            "other_participant_id": other_participant_id,
            "status": consultation["status"]
        }
    
    async def end_consultation(
        self,
        consultation_id: str,
        user_id: str
    ) -> bool:
        """
        End a consultation session.
        
        Args:
            consultation_id: Consultation document ID
            user_id: User ID ending the consultation
            
        Returns:
            True if successful
        """
        consultation = await self.get_consultation(consultation_id, user_id)
        
        if not consultation:
            return False
        
        await self.consultations_collection.document(consultation_id).update({
            "status": ConsultationStatus.COMPLETED.value,
            "ended_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        logger.info(f"Consultation ended: {consultation_id}")
        return True
    
    async def send_webrtc_signal(
        self,
        consultation_id: str,
        from_user_id: str,
        to_user_id: str,
        signal_type: str,
        signal_data: Dict[str, Any]
    ) -> dict:
        """
        Send WebRTC signaling message.
        
        Args:
            consultation_id: Consultation ID
            from_user_id: Sender user ID
            to_user_id: Recipient user ID
            signal_type: Signal type (offer, answer, ice-candidate)
            signal_data: Signal payload
            
        Returns:
            Signaling message document
        """
        signal_message = {
            "consultation_id": consultation_id,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "signal_type": signal_type,
            "signal_data": signal_data,
            "timestamp": datetime.utcnow(),
            "delivered": False
        }
        
        doc_ref = self.signaling_collection.document()
        await doc_ref.set(signal_message)
        
        signal_message["id"] = doc_ref.id
        logger.debug(f"WebRTC signal sent: {signal_type} from {from_user_id} to {to_user_id}")
        
        return signal_message
    
    async def get_pending_signals(
        self,
        consultation_id: str,
        user_id: str
    ) -> list:
        """
        Get pending WebRTC signals for a user.
        
        Args:
            consultation_id: Consultation ID
            user_id: User ID to get signals for
            
        Returns:
            List of pending signals
        """
        query = (
            self.signaling_collection
            .where("consultation_id", "==", consultation_id)
            .where("to_user_id", "==", user_id)
            .where("delivered", "==", False)
            .order_by("timestamp")
        )
        
        signals = []
        async for doc in query.stream():
            signal_data = doc.to_dict()
            signal_data["id"] = doc.id
            signals.append(signal_data)
        
        # Mark as delivered
        for signal in signals:
            await self.signaling_collection.document(signal["id"]).update({
                "delivered": True
            })
        
        return signals
    
    def _generate_session_token(self, consultation_id: str, user_id: str) -> str:
        """Generate encrypted session token for consultation."""
        token_data = f"{consultation_id}:{user_id}:{secrets.token_urlsafe(32)}"
        return encryption_service.encrypt(token_data)
    
    def _generate_webrtc_config(self) -> Dict[str, Any]:
        """Generate WebRTC configuration."""
        return {
            "stun_servers": [
                {"urls": settings.WEBRTC_STUN_SERVER}
            ],
            "turn_servers": [
                {"urls": settings.WEBRTC_TURN_SERVER} if settings.WEBRTC_TURN_SERVER else None
            ],
            "ice_transport_policy": "all",
            "rtcp_mux_policy": "require"
        }

