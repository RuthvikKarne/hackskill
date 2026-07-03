"""Recommendation Service — Central recommendation aggregation.

This service aggregates recommendations from all other AI services
and writes them to the analytics.ai_recommendations table.

Every recommendation:
  - Has a confidence score (0.0 — 1.0)
  - Has a SHAP-based explanation
  - Has a model version tag
  - Requires human approval before any action is taken
  - Is linked to a specific hospital
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/pending")
async def get_pending_recommendations(hospital_id: str) -> dict:
    """List pending recommendations awaiting human approval.

    TODO Phase 6: Implement with full recommendation engine.
    """
    return {
        "message": "Recommendation service — implementation pending (Phase 6)",
        "hospital_id": hospital_id,
        "recommendations": [],
    }
