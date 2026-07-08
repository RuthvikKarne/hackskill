"""Recommendation Service — Human approval workflow for AI recommendations.

Every AI-generated recommendation goes through this service:
  1. Service creates recommendation with status=PENDING
  2. Notification sent to admin (via Event Bus in production)
  3. Admin reviews in dashboard
  4. Admin APPROVES → status=APPROVED → backend executes action
  5. Admin REJECTS  → reason recorded → status=REJECTED

Storage: in-memory dict (keyed by UUID).
In production: backed by ai.recommendations PostgreSQL table.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.schemas import (
    AIRecommendation,
    ApproveRequest,
    RecommendationCategory,
    RecommendationStatus,
    RejectRequest,
    RiskLevel,
    SHAPExplanation,
    SHAPFeature,
)


class RecommendationService:
    """Manages AI recommendation lifecycle with human approval workflow."""

    def __init__(self) -> None:
        # In-memory store: recommendation_id → AIRecommendation
        self._store: dict[str, AIRecommendation] = {}

    # ── Create ────────────────────────────────────────────────────────────────

    def create_recommendation(
        self,
        *,
        hospital_id: str,
        category: RecommendationCategory,
        title: str,
        description: str,
        action_items: list[str],
        confidence: float,
        risk_level: RiskLevel = RiskLevel.MODERATE,
        explanation: SHAPExplanation | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AIRecommendation:
        """Create a new AI recommendation in PENDING state.

        Args:
            hospital_id: Target hospital UUID.
            category: Recommendation category.
            title: Short recommendation title.
            description: Detailed description.
            action_items: Concrete action steps.
            confidence: Model confidence [0, 1].
            risk_level: Associated risk level.
            explanation: SHAP explanation object.
            metadata: Additional service-specific metadata.

        Returns:
            Created AIRecommendation with PENDING status.
        """
        rec = AIRecommendation(
            id=str(uuid.uuid4()),
            hospital_id=hospital_id,
            category=category,
            title=title,
            description=description,
            action_items=action_items,
            confidence=confidence,
            risk_level=risk_level,
            status=RecommendationStatus.PENDING,
            explanation=explanation,
            metadata=metadata or {},
        )
        self._store[rec.id] = rec
        return rec

    # ── Approve / Reject ──────────────────────────────────────────────────────

    def approve(self, recommendation_id: str, request: ApproveRequest) -> AIRecommendation:
        """Approve a pending recommendation.

        Args:
            recommendation_id: UUID of the recommendation to approve.
            request: ApproveRequest with reviewer info.

        Returns:
            Updated AIRecommendation with APPROVED status.

        Raises:
            KeyError: If recommendation not found.
            ValueError: If recommendation is not in PENDING state.
        """
        rec = self._get_or_raise(recommendation_id)
        if rec.status != RecommendationStatus.PENDING:
            raise ValueError(
                f"Recommendation {recommendation_id} is in status '{rec.status}' — cannot approve."
            )
        rec.status = RecommendationStatus.APPROVED
        rec.reviewed_at = datetime.now(timezone.utc)
        rec.reviewed_by = request.approved_by
        if request.notes:
            rec.metadata["approval_notes"] = request.notes
        return rec

    def reject(self, recommendation_id: str, request: RejectRequest) -> AIRecommendation:
        """Reject a pending recommendation with mandatory reason.

        Args:
            recommendation_id: UUID of the recommendation to reject.
            request: RejectRequest with rejector info and reason.

        Returns:
            Updated AIRecommendation with REJECTED status.

        Raises:
            KeyError: If recommendation not found.
            ValueError: If recommendation is not in PENDING state.
        """
        rec = self._get_or_raise(recommendation_id)
        if rec.status != RecommendationStatus.PENDING:
            raise ValueError(
                f"Recommendation {recommendation_id} is in status '{rec.status}' — cannot reject."
            )
        rec.status = RecommendationStatus.REJECTED
        rec.reviewed_at = datetime.now(timezone.utc)
        rec.reviewed_by = request.rejected_by
        rec.rejection_reason = request.reason
        return rec

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_pending(self, hospital_id: str | None = None) -> list[AIRecommendation]:
        """Return all pending recommendations, optionally filtered by hospital."""
        return [
            r for r in self._store.values()
            if r.status == RecommendationStatus.PENDING
            and (hospital_id is None or r.hospital_id == hospital_id)
        ]

    def get_all(
        self,
        hospital_id: str | None = None,
        category: RecommendationCategory | None = None,
        status: RecommendationStatus | None = None,
    ) -> list[AIRecommendation]:
        """Return all recommendations with optional filters."""
        results = list(self._store.values())
        if hospital_id:
            results = [r for r in results if r.hospital_id == hospital_id]
        if category:
            results = [r for r in results if r.category == category]
        if status:
            results = [r for r in results if r.status == status]
        # Sort newest first
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def get_by_id(self, recommendation_id: str) -> AIRecommendation | None:
        """Return a recommendation by ID, or None if not found."""
        return self._store.get(recommendation_id)

    def count(self) -> dict[str, int]:
        """Return counts by status."""
        counts: dict[str, int] = {s.value: 0 for s in RecommendationStatus}
        for r in self._store.values():
            counts[r.status.value] += 1
        return counts

    # ── Seed demo data ────────────────────────────────────────────────────────

    def seed_demo_recommendations(self, hospital_id: str) -> list[AIRecommendation]:
        """Seed a set of demo recommendations for showcasing the approval workflow."""
        demo_recs = [
            dict(
                hospital_id=hospital_id,
                category=RecommendationCategory.RISK,
                title="Critical bed occupancy alert",
                description=(
                    "Bed occupancy has reached 92%. Immediate action required to prevent capacity breach. "
                    "Historical patterns indicate patient intake will continue at current pace for 48 hours."
                ),
                action_items=[
                    "Open emergency overflow ward (capacity: 20 additional beds)",
                    "Initiate patient transfer protocol for stable patients",
                    "Contact district coordinator for bed availability at nearby facilities",
                ],
                confidence=0.91,
                risk_level=RiskLevel.CRITICAL,
                explanation=SHAPExplanation(
                    model_name="WeightedRiskScorer_XGBoost_v1",
                    model_version="1.0.0",
                    confidence=0.91,
                    base_value=0.30,
                    output_value=0.87,
                    features=[
                        SHAPFeature(feature_name="bed_occupancy_rate", value=0.92, shap_value=0.3220, importance_rank=1, description="Primary risk driver"),
                        SHAPFeature(feature_name="stock_shortage_ratio", value=0.15, shap_value=0.0375, importance_rank=2, description="Secondary signal"),
                    ],
                    summary_text="Bed occupancy at 92% is the dominant risk factor. Immediate capacity expansion required.",
                ),
            ),
            dict(
                hospital_id=hospital_id,
                category=RecommendationCategory.OPTIMIZATION,
                title="Medicine redistribution recommended",
                description=(
                    "Paracetamol and Amoxicillin stocks are below 15% of minimum threshold. "
                    "Hospital H2 (12km away) has surplus inventory available for transfer."
                ),
                action_items=[
                    "Request 500 units Paracetamol from Hospital H2",
                    "Request 200 units Amoxicillin from district central pharmacy",
                    "Update procurement schedule to prevent future shortages",
                ],
                confidence=0.84,
                risk_level=RiskLevel.HIGH,
                explanation=None,
            ),
            dict(
                hospital_id=hospital_id,
                category=RecommendationCategory.FORECASTING,
                title="Patient surge expected in 72 hours",
                description=(
                    "Forecast model predicts a 35% increase in patient intake over the next 72 hours "
                    "based on seasonal patterns and current disease surveillance signals."
                ),
                action_items=[
                    "Pre-position additional nursing staff for next 3 days",
                    "Ensure triage area is fully staffed by Monday morning",
                    "Activate on-call protocol for emergency medicine department",
                ],
                confidence=0.76,
                risk_level=RiskLevel.MODERATE,
                explanation=None,
            ),
        ]

        created: list[AIRecommendation] = []
        for rec_data in demo_recs:
            created.append(self.create_recommendation(**rec_data))  # type: ignore[arg-type]
        return created

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_or_raise(self, recommendation_id: str) -> AIRecommendation:
        rec = self._store.get(recommendation_id)
        if rec is None:
            raise KeyError(f"Recommendation '{recommendation_id}' not found.")
        return rec


# ── Module-level singleton ────────────────────────────────────────────────────

_recommendation_service: RecommendationService | None = None


def get_recommendation_service() -> RecommendationService:
    """Return the singleton recommendation service."""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service


def init_recommendation_service() -> RecommendationService:
    """Initialize (or reset) the singleton. Called at startup."""
    global _recommendation_service
    _recommendation_service = RecommendationService()
    return _recommendation_service
