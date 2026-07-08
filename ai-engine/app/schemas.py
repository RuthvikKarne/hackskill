"""Shared Pydantic schemas for the HRIP AI Engine.

These schemas define the standard contracts for AI recommendations,
SHAP explanations, and approval workflow responses.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────


class RecommendationStatus(str, Enum):
    """Lifecycle states for an AI recommendation."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RecommendationCategory(str, Enum):
    """Category / origin service of the recommendation."""

    FORECASTING = "FORECASTING"
    RISK = "RISK"
    OPTIMIZATION = "OPTIMIZATION"
    SURVEILLANCE = "SURVEILLANCE"
    GENERAL = "GENERAL"


class RiskLevel(str, Enum):
    """Risk severity levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# ── SHAP Explainability ───────────────────────────────────────────────────────


class SHAPFeature(BaseModel):
    """Single SHAP feature contribution."""

    feature_name: str = Field(..., description="Human-readable feature name")
    value: float = Field(..., description="Actual feature value")
    shap_value: float = Field(..., description="SHAP contribution (positive = pushes score up)")
    importance_rank: int = Field(..., description="Rank among all features (1 = most important)")
    description: str = Field("", description="Human-readable explanation of this feature")


class SHAPExplanation(BaseModel):
    """SHAP-style explanation attached to every AI output."""

    model_name: str = Field(..., description="Name of the model/algorithm used")
    model_version: str = Field(default="1.0.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence [0, 1]")
    base_value: float = Field(..., description="Expected output without any features")
    output_value: float = Field(..., description="Final model output score")
    features: list[SHAPFeature] = Field(default_factory=list)
    summary_text: str = Field("", description="One-paragraph human-readable explanation")


# ── AI Recommendation ────────────────────────────────────────────────────────


class AIRecommendation(BaseModel):
    """A single AI-generated recommendation requiring human approval."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hospital_id: str
    category: RecommendationCategory
    title: str = Field(..., description="Short title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommended action")
    action_items: list[str] = Field(default_factory=list, description="Concrete steps to take")
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    status: RecommendationStatus = RecommendationStatus.PENDING
    explanation: SHAPExplanation | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    rejection_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Approval Workflow Schemas ────────────────────────────────────────────────


class ApproveRequest(BaseModel):
    """Request body to approve a recommendation."""

    approved_by: str = Field(..., description="User ID or name of the approver")
    notes: str = Field("", description="Optional approval notes")


class RejectRequest(BaseModel):
    """Request body to reject a recommendation."""

    rejected_by: str = Field(..., description="User ID or name of the rejector")
    reason: str = Field(..., description="Mandatory reason for rejection")


# ── Forecast Schemas ─────────────────────────────────────────────────────────


class ForecastPoint(BaseModel):
    """Single point in a forecast series."""

    date: str = Field(..., description="ISO date string YYYY-MM-DD")
    value: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    """Response for patient load or medicine demand forecast."""

    hospital_id: str
    forecast_type: str
    horizon_days: int
    points: list[ForecastPoint]
    explanation: SHAPExplanation
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Optimization Schemas ─────────────────────────────────────────────────────


class ResourceAction(BaseModel):
    """A single resource redistribution action."""

    action_type: str = Field(..., description="e.g. TRANSFER, RESTOCK, DEPLOY")
    resource_type: str = Field(..., description="e.g. medicine, staff, equipment")
    from_hospital_id: str | None = None
    to_hospital_id: str
    quantity: float
    unit: str = ""
    priority: str = Field("MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    estimated_impact: str = ""


class OptimizationResponse(BaseModel):
    """Response from the resource optimization service."""

    district_id: str
    total_hospitals: int
    actions: list[ResourceAction]
    expected_shortage_reduction_pct: float
    confidence: float
    explanation: SHAPExplanation
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
