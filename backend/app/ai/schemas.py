"""
AI Symptom Checker Schemas

Pydantic models for symptom analysis requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class SymptomSeverity(str, Enum):
    """Symptom severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class SymptomInput(BaseModel):
    """Individual symptom input."""
    symptom: str = Field(..., description="Symptom description")
    severity: SymptomSeverity = Field(SymptomSeverity.MODERATE)
    duration_days: Optional[int] = Field(None, ge=0, description="Duration in days")
    frequency: Optional[str] = Field(None, description="How often it occurs")


class SymptomCheckRequest(BaseModel):
    """Symptom checker request."""
    symptoms: List[SymptomInput] = Field(..., min_length=1)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    medical_history: Optional[List[str]] = Field(None, description="Previous conditions")
    current_medications: Optional[List[str]] = None
    additional_info: Optional[str] = None


class ConditionPrediction(BaseModel):
    """Predicted condition with confidence."""
    condition: str = Field(..., description="Possible condition name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    icd10_code: Optional[str] = Field(None, description="ICD-10 code if available")
    description: Optional[str] = None


class Recommendation(BaseModel):
    """Recommendation based on symptoms."""
    action: str = Field(..., description="Recommended action")
    urgency: str = Field(..., pattern="^(low|medium|high|emergency)$")
    description: str
    suggested_specialist: Optional[str] = None


class SymptomCheckResponse(BaseModel):
    """Symptom checker response."""
    possible_conditions: List[ConditionPrediction]
    primary_recommendation: Recommendation
    additional_recommendations: List[Recommendation] = []
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    ai_service_used: str = Field(..., description="Which AI service processed the request")
    disclaimer: str = "This is not a substitute for professional medical advice. Please consult a healthcare provider."

