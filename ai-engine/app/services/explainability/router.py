"""Explainability Service — SHAP-based model explanations.

Every AI recommendation includes a human-readable explanation of:
  - Which features drove the prediction
  - Feature importance values (SHAP)
  - Confidence score
  - Model version used

This service wraps SHAP (SHapley Additive exPlanations) around all models.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/recommendation/{recommendation_id}")
async def explain_recommendation(recommendation_id: str) -> dict:
    """Get a human-readable explanation for an AI recommendation.

    TODO Phase 6: Implement with SHAP.
    """
    return {
        "message": "Explainability service — implementation pending (Phase 6)",
        "recommendation_id": recommendation_id,
    }
