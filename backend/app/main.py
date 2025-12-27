"""
Jeevan+ Telemedicine Backend - Main Application Entry Point

Production-ready FastAPI backend for rural healthcare application.
Designed for offline-first operation with cloud sync capabilities.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time

from app.core.config import settings
from app.core.dependencies import get_firestore_client
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.records.routes import router as records_router
from app.ai.routes import router as ai_router
from app.consultation.routes import router as consultation_router
from app.pharmacy.routes import router as pharmacy_router
from app.iot.routes import router as iot_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize Firestore connection
    logger.info("Starting Jeevan+ Backend...")
    try:
        # Test Firestore connection
        db = await get_firestore_client()
        logger.info("Firestore connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Firestore: {e}")
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("Shutting down Jeevan+ Backend...")


# Initialize FastAPI application
app = FastAPI(
    title="Jeevan+ Telemedicine API",
    description="Production-ready backend for rural healthcare telemedicine platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors without exposing sensitive details."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "jeevan-backend",
        "version": "1.0.0"
    }


# API Routes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(records_router, prefix="/api/records", tags=["Health Records"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Services"])
app.include_router(consultation_router, prefix="/api/consultations", tags=["Consultations"])
app.include_router(pharmacy_router, prefix="/api/pharmacy", tags=["Pharmacy"])
app.include_router(iot_router, prefix="/api/iot", tags=["IoT"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

