"""
User Management Service

Business logic for user profile management, family linking, and doctor verification.
"""

from typing import Optional, List
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging

from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.users_collection = db.collection("users")
        self.family_links_collection = db.collection("family_links")
    
    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """
        Get complete user profile with family members.
        
        Args:
            user_id: User document ID
            
        Returns:
            User profile data with family members
        """
        # Get user document
        user_doc = await self.users_collection.document(user_id).get()
        
        if not user_doc.exists:
            return None
        
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        
        # Decrypt sensitive fields
        if user_data.get("phone"):
            try:
                user_data["phone"] = encryption_service.decrypt(user_data["phone"])
            except:
                pass
        
        if user_data.get("email"):
            try:
                user_data["email"] = encryption_service.decrypt(user_data["email"])
            except:
                pass
        
        if user_data.get("emergency_contact_phone"):
            try:
                user_data["emergency_contact_phone"] = encryption_service.decrypt(
                    user_data["emergency_contact_phone"]
                )
            except:
                pass
        
        # Get family members
        family_query = self.family_links_collection.where("patient_id", "==", user_id)
        family_members = []
        
        async for doc in family_query.stream():
            link_data = doc.to_dict()
            member_id = link_data.get("family_member_id")
            
            if member_id:
                member_doc = await self.users_collection.document(member_id).get()
                if member_doc.exists:
                    member_data = member_doc.to_dict()
                    family_members.append({
                        "id": member_id,
                        "full_name": member_data.get("full_name", ""),
                        "relationship": link_data.get("relationship", ""),
                        "phone": encryption_service.decrypt(member_data.get("phone", "")) if member_data.get("phone") else None,
                        "email": encryption_service.decrypt(member_data.get("email", "")) if member_data.get("email") else None,
                        "linked_at": link_data.get("created_at")
                    })
        
        user_data["family_members"] = family_members
        return user_data
    
    async def update_user_profile(
        self,
        user_id: str,
        update_data: dict
    ) -> dict:
        """
        Update user profile.
        
        Args:
            user_id: User document ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated user data
        """
        # Encrypt sensitive fields
        if "phone" in update_data and update_data["phone"]:
            update_data["phone"] = encryption_service.encrypt(update_data["phone"])
        
        if "email" in update_data and update_data["email"]:
            update_data["email"] = encryption_service.encrypt(update_data["email"])
        
        if "emergency_contact_phone" in update_data and update_data["emergency_contact_phone"]:
            update_data["emergency_contact_phone"] = encryption_service.encrypt(
                update_data["emergency_contact_phone"]
            )
        
        # Add update timestamp and increment version
        update_data["updated_at"] = datetime.utcnow()
        
        # Get current version
        user_doc = await self.users_collection.document(user_id).get()
        if user_doc.exists:
            current_data = user_doc.to_dict()
            update_data["version"] = current_data.get("version", 1) + 1
        
        # Update document
        await self.users_collection.document(user_id).update(update_data)
        
        logger.info(f"User profile updated: {user_id}")
        
        # Return updated profile
        return await self.get_user_profile(user_id)
    
    async def link_family_member(
        self,
        patient_id: str,
        family_member_phone: Optional[str] = None,
        family_member_email: Optional[str] = None,
        relationship: str = "other"
    ) -> dict:
        """
        Link a family member to a patient account.
        
        Args:
            patient_id: Patient user ID
            family_member_phone: Family member's phone number
            family_member_email: Family member's email
            relationship: Relationship type
            
        Returns:
            Family link data
            
        Raises:
            ValueError: If family member not found or already linked
        """
        # Find family member
        family_member_id = None
        
        if family_member_phone:
            # Search for user by phone (encrypted search - simplified)
            query = self.users_collection.where("is_active", "==", True)
            async for doc in query.stream():
                user_data = doc.to_dict()
                if user_data.get("phone"):
                    try:
                        decrypted_phone = encryption_service.decrypt(user_data["phone"])
                        if decrypted_phone == family_member_phone:
                            family_member_id = doc.id
                            break
                    except:
                        pass
        
        if not family_member_id and family_member_email:
            # Search by email
            query = self.users_collection.where("is_active", "==", True)
            async for doc in query.stream():
                user_data = doc.to_dict()
                if user_data.get("email"):
                    try:
                        decrypted_email = encryption_service.decrypt(user_data["email"])
                        if decrypted_email == family_member_email:
                            family_member_id = doc.id
                            break
                    except:
                        pass
        
        if not family_member_id:
            raise ValueError("Family member not found")
        
        # Check if already linked
        existing_query = self.family_links_collection.where(
            "patient_id", "==", patient_id
        ).where("family_member_id", "==", family_member_id)
        
        existing_docs = [doc async for doc in existing_query.stream()]
        if existing_docs:
            raise ValueError("Family member already linked")
        
        # Create family link
        link_data = {
            "patient_id": patient_id,
            "family_member_id": family_member_id,
            "relationship": relationship,
            "created_at": datetime.utcnow()
        }
        
        doc_ref = self.family_links_collection.document()
        await doc_ref.set(link_data)
        
        logger.info(f"Family member linked: {family_member_id} to patient {patient_id}")
        
        return link_data
    
    async def update_doctor_profile(
        self,
        doctor_id: str,
        doctor_data: dict
    ) -> dict:
        """
        Update doctor-specific profile information.
        
        Args:
            doctor_id: Doctor user ID
            doctor_data: Doctor profile data
            
        Returns:
            Updated doctor profile
        """
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if "specialization" in doctor_data:
            update_data["specialization"] = doctor_data["specialization"]
        
        if "license_number" in doctor_data:
            # Encrypt license number
            update_data["license_number"] = encryption_service.encrypt(
                doctor_data["license_number"]
            )
        
        if "years_of_experience" in doctor_data:
            update_data["years_of_experience"] = doctor_data["years_of_experience"]
        
        if "bio" in doctor_data:
            update_data["bio"] = doctor_data["bio"]
        
        if "consultation_fee" in doctor_data:
            update_data["consultation_fee"] = doctor_data["consultation_fee"]
        
        # Increment version
        user_doc = await self.users_collection.document(doctor_id).get()
        if user_doc.exists:
            current_data = user_doc.to_dict()
            update_data["version"] = current_data.get("version", 1) + 1
        
        await self.users_collection.document(doctor_id).update(update_data)
        
        logger.info(f"Doctor profile updated: {doctor_id}")
        
        return await self.get_user_profile(doctor_id)
    
    async def verify_doctor(self, doctor_id: str, admin_id: str) -> bool:
        """
        Verify a doctor (admin only).
        
        Args:
            doctor_id: Doctor user ID
            admin_id: Admin user ID performing verification
            
        Returns:
            True if successful
        """
        update_data = {
            "is_verified": True,
            "verified_at": datetime.utcnow(),
            "verified_by": admin_id,
            "updated_at": datetime.utcnow()
        }
        
        await self.users_collection.document(doctor_id).update(update_data)
        
        logger.info(f"Doctor verified: {doctor_id} by admin {admin_id}")
        return True

