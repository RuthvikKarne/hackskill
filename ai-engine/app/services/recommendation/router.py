"""Recommendation Service Router — Human approval workflow for AI recommendations."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.schemas import (
    AIRecommendation,
    ApproveRequest,
    RecommendationCategory,
    RecommendationStatus,
    RejectRequest,
)
from app.services.recommendation.service import get_recommendation_service

router = APIRouter()


def _svc() -> "RecommendationService":  # type: ignore[name-defined]
    return get_recommendation_service()


@router.get(
    "/pending",
    response_model=list[AIRecommendation],
    summary="List pending recommendations",
    description="List all AI recommendations awaiting human approval, optionally filtered by hospital.",
)
async def get_pending_recommendations(
    hospital_id: str | None = Query(None, description="Filter by hospital UUID"),
) -> list[AIRecommendation]:
    """List pending recommendations awaiting human approval."""
    return _svc().get_pending(hospital_id=hospital_id)


@router.get(
    "/",
    response_model=list[AIRecommendation],
    summary="List all recommendations",
    description="List all AI recommendations with optional filtering by hospital, category, or status.",
)
async def list_recommendations(
    hospital_id: str | None = Query(None, description="Filter by hospital UUID"),
    category: RecommendationCategory | None = Query(None, description="Filter by category"),
    status: RecommendationStatus | None = Query(None, description="Filter by status"),
) -> list[AIRecommendation]:
    """List all recommendations with optional filters."""
    return _svc().get_all(hospital_id=hospital_id, category=category, status=status)


@router.get(
    "/counts",
    summary="Recommendation counts by status",
    description="Return counts of recommendations grouped by status (PENDING/APPROVED/REJECTED).",
)
async def get_counts() -> dict[str, int]:
    """Return recommendation counts by status."""
    return _svc().count()


@router.get(
    "/{recommendation_id}",
    response_model=AIRecommendation,
    summary="Get recommendation by ID",
)
async def get_recommendation(
    recommendation_id: str = Path(..., description="Recommendation UUID"),
) -> AIRecommendation:
    """Get a single recommendation by ID."""
    rec = _svc().get_by_id(recommendation_id)
    if rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation '{recommendation_id}' not found.",
        )
    return rec


@router.post(
    "/{recommendation_id}/approve",
    response_model=AIRecommendation,
    summary="Approve a recommendation",
    description=(
        "Approve an AI recommendation. Status changes from PENDING → APPROVED. "
        "In production this triggers the backend to execute the recommended action."
    ),
)
async def approve_recommendation(
    recommendation_id: str = Path(..., description="Recommendation UUID"),
    request: ApproveRequest = ...,
) -> AIRecommendation:
    """Approve a pending recommendation."""
    try:
        return _svc().approve(recommendation_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/{recommendation_id}/reject",
    response_model=AIRecommendation,
    summary="Reject a recommendation",
    description=(
        "Reject an AI recommendation with a mandatory reason. "
        "Status changes from PENDING → REJECTED. Rejection reason is recorded in the audit log."
    ),
)
async def reject_recommendation(
    recommendation_id: str = Path(..., description="Recommendation UUID"),
    request: RejectRequest = ...,
) -> AIRecommendation:
    """Reject a pending recommendation."""
    try:
        return _svc().reject(recommendation_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/seed-demo",
    response_model=list[AIRecommendation],
    summary="Seed demo recommendations",
    description=(
        "Seed a set of demo recommendations for showcasing the approval workflow. "
        "Useful for testing and demonstrations."
    ),
)
async def seed_demo(
    hospital_id: str = Query(..., description="Hospital UUID to seed recommendations for"),
) -> list[AIRecommendation]:
    """Seed demo recommendations for the approval workflow."""
    return _svc().seed_demo_recommendations(hospital_id)
