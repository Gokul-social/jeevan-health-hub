"""
AI Symptom Checker Service

Local-first AI service with cloud fallback support.
Supports rule-based logic and ML model inference.
"""

from typing import List, Dict, Any, Optional
import logging
import json

from app.core.config import settings
from app.ai.schemas import (
    SymptomCheckRequest,
    ConditionPrediction,
    Recommendation,
    SymptomCheckResponse
)

logger = logging.getLogger(__name__)


class AISymptomCheckerService:
    """
    AI Symptom Checker Service with local and cloud fallback.
    
    Supports:
    - Local rule-based logic
    - HuggingFace model inference
    - Google Gemini API
    """
    
    def __init__(self):
        self.service_type = settings.AI_SERVICE_TYPE
        self.fallback_enabled = settings.AI_FALLBACK_ENABLED
    
    async def check_symptoms(self, request: SymptomCheckRequest) -> SymptomCheckResponse:
        """
        Analyze symptoms and return possible conditions.
        
        Args:
            request: Symptom check request
            
        Returns:
            Symptom check response with predictions and recommendations
        """
        try:
            # Try primary service
            if self.service_type == "local":
                result = await self._local_rule_based_check(request)
                service_used = "local"
            elif self.service_type == "huggingface":
                result = await self._huggingface_check(request)
                service_used = "huggingface"
            elif self.service_type == "gemini":
                result = await self._gemini_check(request)
                service_used = "gemini"
            else:
                # Default to local
                result = await self._local_rule_based_check(request)
                service_used = "local"
        
        except Exception as e:
            logger.error(f"Primary AI service error: {e}")
            
            # Fallback to local if enabled
            if self.fallback_enabled and self.service_type != "local":
                logger.info("Falling back to local rule-based checker")
                result = await self._local_rule_based_check(request)
                service_used = "local_fallback"
            else:
                raise
        
        return result
    
    async def _local_rule_based_check(
        self,
        request: SymptomCheckRequest
    ) -> SymptomCheckResponse:
        """
        Local rule-based symptom checker.
        
        Uses predefined rules and symptom-condition mappings.
        """
        # Extract symptom keywords
        symptom_texts = [s.symptom.lower() for s in request.symptoms]
        all_symptoms = " ".join(symptom_texts)
        
        # Rule-based condition matching
        conditions = []
        
        # Fever patterns
        if any("fever" in s or "temperature" in s for s in symptom_texts):
            if any("cough" in s for s in symptom_texts):
                conditions.append(ConditionPrediction(
                    condition="Upper Respiratory Infection",
                    confidence=0.75,
                    icd10_code="J06.9",
                    description="Possible viral or bacterial infection"
                ))
            else:
                conditions.append(ConditionPrediction(
                    condition="Fever of Unknown Origin",
                    confidence=0.60,
                    description="Fever without clear cause"
                ))
        
        # Headache patterns
        if any("headache" in s for s in symptom_texts):
            if any("nausea" in s or "vomit" in s for s in symptom_texts):
                conditions.append(ConditionPrediction(
                    condition="Migraine",
                    confidence=0.70,
                    icd10_code="G43.9",
                    description="Possible migraine headache"
                ))
            else:
                conditions.append(ConditionPrediction(
                    condition="Tension Headache",
                    confidence=0.65,
                    icd10_code="G44.2",
                    description="Possible tension-type headache"
                ))
        
        # Abdominal pain patterns
        if any("stomach" in s or "abdominal" in s or "belly" in s for s in symptom_texts):
            if any("nausea" in s or "vomit" in s for s in symptom_texts):
                conditions.append(ConditionPrediction(
                    condition="Gastroenteritis",
                    confidence=0.70,
                    icd10_code="A09",
                    description="Possible stomach infection or inflammation"
                ))
            else:
                conditions.append(ConditionPrediction(
                    condition="Abdominal Pain",
                    confidence=0.55,
                    description="Abdominal discomfort requiring evaluation"
                ))
        
        # Chest pain patterns
        if any("chest" in s or "heart" in s for s in symptom_texts):
            conditions.append(ConditionPrediction(
                condition="Chest Pain - Requires Immediate Evaluation",
                confidence=0.80,
                icd10_code="R06.02",
                description="Chest pain should be evaluated promptly"
            ))
        
        # Default if no specific pattern
        if not conditions:
            conditions.append(ConditionPrediction(
                condition="General Symptoms",
                confidence=0.40,
                description="Symptoms require medical evaluation"
            ))
        
        # Sort by confidence
        conditions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Generate recommendations
        primary_condition = conditions[0] if conditions else None
        recommendations = self._generate_recommendations(primary_condition, request)
        
        return SymptomCheckResponse(
            possible_conditions=conditions[:5],  # Top 5
            primary_recommendation=recommendations[0],
            additional_recommendations=recommendations[1:],
            confidence_score=primary_condition.confidence if primary_condition else 0.4,
            ai_service_used="local_rule_based"
        )
    
    async def _huggingface_check(
        self,
        request: SymptomCheckRequest
    ) -> SymptomCheckResponse:
        """
        HuggingFace model inference (placeholder implementation).
        
        In production, integrate with HuggingFace Inference API or local model.
        """
        # Placeholder - would call HuggingFace API or local model
        logger.info("HuggingFace check requested (not implemented)")
        
        # Fallback to local for now
        return await self._local_rule_based_check(request)
    
    async def _gemini_check(
        self,
        request: SymptomCheckRequest
    ) -> SymptomCheckResponse:
        """
        Google Gemini API integration (placeholder implementation).
        
        In production, integrate with Gemini API for symptom analysis.
        """
        # Placeholder - would call Gemini API
        logger.info("Gemini check requested (not implemented)")
        
        # Fallback to local for now
        return await self._local_rule_based_check(request)
    
    def _generate_recommendations(
        self,
        primary_condition: Optional[ConditionPrediction],
        request: SymptomCheckRequest
    ) -> List[Recommendation]:
        """Generate recommendations based on condition and symptoms."""
        recommendations = []
        
        if not primary_condition:
            recommendations.append(Recommendation(
                action="Consult a healthcare provider",
                urgency="medium",
                description="Your symptoms require professional evaluation",
                suggested_specialist="General Practitioner"
            ))
            return recommendations
        
        # High confidence or severe symptoms
        if primary_condition.confidence > 0.7 or any(
            s.severity.value in ["severe", "critical"] for s in request.symptoms
        ):
            recommendations.append(Recommendation(
                action="Seek immediate medical attention",
                urgency="high",
                description=f"Based on your symptoms, {primary_condition.condition} is a possibility. Please consult a healthcare provider.",
                suggested_specialist="Emergency Department" if any(
                    s.severity.value == "critical" for s in request.symptoms
                ) else "General Practitioner"
            ))
        else:
            recommendations.append(Recommendation(
                action="Schedule a consultation",
                urgency="medium",
                description=f"Your symptoms may indicate {primary_condition.condition}. Consider consulting a healthcare provider.",
                suggested_specialist="General Practitioner"
            ))
        
        # Additional recommendations
        if any("fever" in s.symptom.lower() for s in request.symptoms):
            recommendations.append(Recommendation(
                action="Monitor temperature and stay hydrated",
                urgency="low",
                description="Keep track of your temperature and ensure adequate fluid intake"
            ))
        
        if any("pain" in s.symptom.lower() for s in request.symptoms):
            recommendations.append(Recommendation(
                action="Consider over-the-counter pain relief (if appropriate)",
                urgency="low",
                description="Consult a pharmacist before taking any medication"
            ))
        
        return recommendations

