"""
Application Dependencies

Shared dependencies for database connections, rate limiting, and utilities.
"""

from functools import lru_cache
from typing import AsyncGenerator, Optional
from google.cloud import firestore
from google.cloud.firestore import AsyncClient
from fastapi import Request
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Firestore client (will be initialized on first use)
_firestore_client: Optional[AsyncClient] = None


async def get_firestore_client() -> AsyncClient:
    """
    Get or create Firestore async client.
    
    Returns:
        Async Firestore client instance
        
    Note:
        In production, use Firebase Admin SDK with service account credentials.
        For local development, use application default credentials or emulator.
    """
    global _firestore_client
    
    if _firestore_client is None:
        try:
            # Initialize Firestore client
            if settings.FIREBASE_CREDENTIALS_PATH:
                # Use service account credentials if provided
                _firestore_client = firestore.AsyncClient.from_service_account_json(
                    settings.FIREBASE_CREDENTIALS_PATH,
                    project=settings.FIREBASE_PROJECT_ID
                )
            else:
                # Use default credentials (for Cloud Run, GCE, or local with gcloud auth)
                _firestore_client = firestore.AsyncClient(
                    project=settings.FIREBASE_PROJECT_ID
                )
            
            logger.info("Firestore client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            # Fallback: create client without explicit project (uses default)
            _firestore_client = firestore.AsyncClient()
    
    return _firestore_client


async def get_firestore_db() -> AsyncGenerator[AsyncClient, None]:
    """
    Dependency function for FastAPI route injection.
    Provides Firestore database client to route handlers.
    """
    db = await get_firestore_client()
    yield db


# Rate limiting (simple in-memory implementation)
# In production, use Redis-based rate limiting
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, status

_rate_limit_store = defaultdict(list)


def check_rate_limit(identifier: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """
    Simple in-memory rate limiting.
    
    Args:
        identifier: Unique identifier (e.g., user_id, IP address)
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Returns:
        True if request is allowed, False if rate limit exceeded
        
    Note:
        For production, replace with Redis-based rate limiting.
    """
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)
    
    # Clean old entries
    _rate_limit_store[identifier] = [
        req_time for req_time in _rate_limit_store[identifier]
        if req_time > window_start
    ]
    
    # Check limit
    if len(_rate_limit_store[identifier]) >= max_requests:
        return False
    
    # Add current request
    _rate_limit_store[identifier].append(now)
    return True


async def rate_limit_dependency(
    request: Request
):
    """
    FastAPI dependency for rate limiting.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # Try to get user_id from request state (set by auth middleware if authenticated)
    user_id = getattr(request.state, "user_id", None)
    
    # Use user_id if available, otherwise use IP address
    identifier = user_id or (request.client.host if request.client else "unknown")
    
    if not check_rate_limit(identifier, settings.RATE_LIMIT_PER_MINUTE, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

