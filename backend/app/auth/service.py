"""
Authentication Service

Business logic for user authentication, registration, and token management.
"""

from typing import Optional
from datetime import datetime
from google.cloud.firestore import AsyncClient
import logging

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncClient):
        self.db = db
        self.users_collection = db.collection("users")
    
    async def register_user(
        self,
        phone: Optional[str],
        email: Optional[str],
        password: str,
        full_name: str,
        role: str = "patient"
    ) -> dict:
        """
        Register a new user.
        
        Args:
            phone: User phone number (optional)
            email: User email (optional)
            password: Plain text password
            full_name: User's full name
            role: User role (patient, doctor, admin)
            
        Returns:
            User document data
            
        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        if phone:
            phone_query = self.users_collection.where("phone", "==", phone).limit(1)
            phone_docs = [doc async for doc in phone_query.stream()]
            if phone_docs:
                raise ValueError("User with this phone number already exists")
        
        if email:
            email_query = self.users_collection.where("email", "==", email).limit(1)
            email_docs = [doc async for doc in email_query.stream()]
            if email_docs:
                raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Encrypt sensitive fields
        encrypted_phone = encryption_service.encrypt(phone) if phone else None
        encrypted_email = encryption_service.encrypt(email) if email else None
        
        # Create user document
        user_data = {
            "phone": encrypted_phone,
            "email": encrypted_email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "role": role,
            "is_verified": False,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": 1  # For offline sync
        }
        
        # Add to Firestore
        doc_ref = self.users_collection.document()
        await doc_ref.set(user_data)
        
        # Return user data (without sensitive fields)
        user_data["id"] = doc_ref.id
        user_data["phone"] = phone  # Return decrypted for response
        user_data["email"] = email
        del user_data["password_hash"]
        
        logger.info(f"User registered: {doc_ref.id} with role {role}")
        return user_data
    
    async def authenticate_user(
        self,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        password: str = None
    ) -> Optional[dict]:
        """
        Authenticate a user and return user data.
        
        Args:
            phone: User phone number
            email: User email
            password: Plain text password
            
        Returns:
            User document data if authentication succeeds, None otherwise
        """
        if not phone and not email:
            return None
        
        # Search for user by phone or email
        query = None
        if phone:
            # Note: Since phone is encrypted, we need to search differently
            # In production, maintain a separate index or use phone hash
            # For now, we'll iterate (not ideal for scale, but works)
            query = self.users_collection.where("is_active", "==", True)
        elif email:
            query = self.users_collection.where("is_active", "==", True)
        
        if not query:
            return None
        
        # Find user (in production, use indexed queries)
        async for doc in query.stream():
            user_data = doc.to_dict()
            
            # Decrypt and check phone/email
            decrypted_phone = None
            decrypted_email = None
            
            if user_data.get("phone"):
                try:
                    decrypted_phone = encryption_service.decrypt(user_data["phone"])
                except:
                    pass
            
            if user_data.get("email"):
                try:
                    decrypted_email = encryption_service.decrypt(user_data["email"])
                except:
                    pass
            
            # Check if this is the user we're looking for
            if (phone and decrypted_phone == phone) or (email and decrypted_email == email):
                # Verify password
                if verify_password(password, user_data.get("password_hash", "")):
                    # Return user data
                    user_data["id"] = doc.id
                    user_data["phone"] = decrypted_phone
                    user_data["email"] = decrypted_email
                    del user_data["password_hash"]
                    return user_data
        
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User document ID
            
        Returns:
            User document data or None
        """
        doc_ref = self.users_collection.document(user_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        user_data = doc.to_dict()
        user_data["id"] = doc.id
        
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
        
        # Remove password hash
        if "password_hash" in user_data:
            del user_data["password_hash"]
        
        return user_data
    
    def create_tokens(self, user_id: str, role: str) -> dict:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: User ID
            role: User role
            
        Returns:
            Dictionary with access_token, refresh_token, and expires_in
        """
        token_data = {
            "sub": user_id,
            "role": role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes in seconds
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token data or None if refresh token is invalid
        """
        payload = decode_token(refresh_token)
        
        if payload is None or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id:
            return None
        
        # Verify user still exists and is active
        user = await self.get_user_by_id(user_id)
        if not user or not user.get("is_active"):
            return None
        
        # Create new access token
        token_data = {
            "sub": user_id,
            "role": role
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60
        }

