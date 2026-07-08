"""Explainability Service Router — SHAP-based model explanations."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Path, Query

from app.schemas import SHAPExplanation
from app.services.explainability.service import ExplainabilityService

router = APIRouter()
_service = ExplainabilityService()


@router.get(
    "/recommendation/{recommendation_id}",
    response_model=SHAPExplanation,
    summary="Explain a recommendation",
    description=(
        "Get a human-readable SHAP-style explanation for an AI recommendation. "
        "Returns feature importances, confidence, and a plain-language summary."
    ),
)
async def explain_recommendation(
    recommendation_id: str = Path(..., description="Recommendation UUID"),
    output_value: float = Query(0.5, ge=0.0, le=1.0, description="Model output score"),
) -> SHAPExplanation:
    """Get a generic explanation for a recommendation by ID."""
    return _service.explain_generic(
        recommendation_id=recommendation_id,
        model_name="GenericRecommender_v1",
        output_value=output_value,
        feature_map={"composite_score": output_value, "confidence": output_value},
    )


@router.post(
    "/compute",
    response_model=SHAPExplanation,
    summary="Compute custom SHAP explanation",
    description=(
        "Compute a SHAP-style explanation from a custom feature map. "
        "Useful for explaining any model output with named features and values."
    ),
)
async def compute_explanation(
    model_name: str = Query(..., description="Name of the model to explain"),
    output_value: float = Query(..., ge=0.0, le=1.0, description="Model output score"),
    feature_map: dict[str, float] = Body(..., description="Feature name → value mapping"),
    weight_map: dict[str, float] | None = Body(None, description="Optional feature → weight mapping"),
) -> SHAPExplanation:
    """Compute a custom SHAP explanation from a feature map."""
    return _service.explain_generic(
        recommendation_id="custom",
        model_name=model_name,
        output_value=output_value,
        feature_map=feature_map,
        weight_map=weight_map,
    )


@router.get(
    "/risk-score",
    response_model=SHAPExplanation,
    summary="Explain hospital risk score",
    description="Get SHAP explanation for a hospital risk score with the same features used in scoring.",
)
async def explain_risk_score(
    risk_score: float = Query(..., ge=0.0, le=1.0),
    occupancy_rate: float = Query(0.0, ge=0.0, le=1.0),
    stock_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0),
    average_wait_time: float = Query(0.0, ge=0.0),
    staff_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0),
    severity_score: float = Query(0.0, ge=0.0, le=1.0),
) -> SHAPExplanation:
    """Get a SHAP explanation for a hospital risk score."""
    return _service.explain_risk_score(
        risk_score=risk_score,
        occupancy_rate=occupancy_rate,
        stock_shortage_ratio=stock_shortage_ratio,
        average_wait_time=average_wait_time,
        staff_shortage_ratio=staff_shortage_ratio,
        severity_score=severity_score,
    )
