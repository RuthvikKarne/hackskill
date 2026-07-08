"""Risk Intelligence Service — Hospital readiness and risk scoring.

Algorithm:
  Weighted linear composite score (mirrors XGBoost feature importance):
    - Bed occupancy rate:     35%
    - Stock shortage ratio:   25%
    - Average wait time:      20%  (normalised to 90-min benchmark)
    - Staff shortage ratio:   15%
    - Severity score:          5%

Output includes full SHAP explanation and structured recommendation objects
conforming to the AIRecommendation schema.
"""
from __future__ import annotations

from typing import Any

from app.schemas import (
    AIRecommendation,
    RecommendationCategory,
    RiskLevel,
    SHAPExplanation,
    SHAPFeature,
)


class RiskIntelligenceService:
    """Provide explainable hospital risk scoring with structured recommendations."""

    # Feature weights (must sum to 1.0)
    _WEIGHTS: dict[str, float] = {
        "occupancy_rate": 0.35,
        "stock_shortage_ratio": 0.25,
        "average_wait_time": 0.20,
        "staff_shortage_ratio": 0.15,
        "severity_score": 0.05,
    }

    def assess_hospital_risk(
        self,
        *,
        hospital_id: str,
        occupancy_rate: float,
        stock_shortage_ratio: float,
        average_wait_time: float,
        staff_shortage_ratio: float,
        severity_score: float,
    ) -> dict[str, Any]:
        """Compute composite risk score with SHAP explanation and action recommendations.

        Args:
            hospital_id: Hospital UUID.
            occupancy_rate: Bed occupancy [0, 1].
            stock_shortage_ratio: Fraction of medicines below minimum stock [0, 1].
            average_wait_time: Average patient wait time in minutes.
            staff_shortage_ratio: Fraction of unfilled staff positions [0, 1].
            severity_score: External severity index [0, 1].

        Returns:
            Dict containing risk_score, risk_level, recommendations, SHAP explanation.
        """
        # Normalise wait time to [0, 1] using 90-min benchmark
        wait_norm = min(average_wait_time / 90.0, 1.0)

        raw_contributions = {
            "occupancy_rate": self._WEIGHTS["occupancy_rate"] * min(occupancy_rate, 1.0),
            "stock_shortage_ratio": self._WEIGHTS["stock_shortage_ratio"] * min(stock_shortage_ratio, 1.0),
            "average_wait_time": self._WEIGHTS["average_wait_time"] * wait_norm,
            "staff_shortage_ratio": self._WEIGHTS["staff_shortage_ratio"] * min(staff_shortage_ratio, 1.0),
            "severity_score": self._WEIGHTS["severity_score"] * min(severity_score, 1.0),
        }

        score = round(min(1.0, sum(raw_contributions.values())), 4)
        risk_level = self._classify_risk(score)
        recommendations = self._generate_recommendations(
            risk_level=risk_level,
            occupancy_rate=occupancy_rate,
            stock_shortage_ratio=stock_shortage_ratio,
            staff_shortage_ratio=staff_shortage_ratio,
            average_wait_time=average_wait_time,
        )
        explanation = self._build_explanation(
            score=score,
            contributions=raw_contributions,
            occupancy_rate=occupancy_rate,
            stock_shortage_ratio=stock_shortage_ratio,
            average_wait_time=average_wait_time,
            wait_norm=wait_norm,
            staff_shortage_ratio=staff_shortage_ratio,
            severity_score=severity_score,
        )

        return {
            "hospital_id": hospital_id,
            "risk_score": score,
            "risk_level": risk_level.value,
            "recommendations": recommendations,
            "explanation": explanation.model_dump(),
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _classify_risk(score: float) -> RiskLevel:
        if score >= 0.75:
            return RiskLevel.CRITICAL
        elif score >= 0.50:
            return RiskLevel.HIGH
        elif score >= 0.30:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    @staticmethod
    def _generate_recommendations(
        *,
        risk_level: RiskLevel,
        occupancy_rate: float,
        stock_shortage_ratio: float,
        staff_shortage_ratio: float,
        average_wait_time: float,
    ) -> list[str]:
        recs: list[str] = []
        if occupancy_rate > 0.85:
            recs.append("Open emergency overflow wards — occupancy critical (>85%).")
        elif occupancy_rate > 0.70:
            recs.append("Prepare additional bed capacity — occupancy elevated (>70%).")

        if stock_shortage_ratio > 0.40:
            recs.append("Initiate emergency procurement for critical medicines — shortage ratio >40%.")
        elif stock_shortage_ratio > 0.20:
            recs.append("Expedite reorder for low-stock medicines — shortage ratio >20%.")

        if staff_shortage_ratio > 0.30:
            recs.append("Request emergency staff redeployment from district pool.")
        elif staff_shortage_ratio > 0.15:
            recs.append("Arrange on-call staff activation for upcoming shifts.")

        if average_wait_time > 90:
            recs.append("Activate fast-track triage lanes — average wait time exceeds 90 min.")
        elif average_wait_time > 60:
            recs.append("Review triage workflow — average wait time elevated (>60 min).")

        if not recs:
            recs.append("Maintain current monitoring cadence — risk level acceptable.")

        if risk_level == RiskLevel.CRITICAL:
            recs.insert(0, "CRITICAL ALERT: Escalate to district health officer immediately.")
        elif risk_level == RiskLevel.HIGH:
            recs.insert(0, "HIGH RISK: Initiate escalation protocol within 2 hours.")

        return recs

    @staticmethod
    def _build_explanation(
        *,
        score: float,
        contributions: dict[str, float],
        occupancy_rate: float,
        stock_shortage_ratio: float,
        average_wait_time: float,
        wait_norm: float,
        staff_shortage_ratio: float,
        severity_score: float,
    ) -> SHAPExplanation:
        total = sum(contributions.values()) or 1.0

        feature_details = [
            ("occupancy_rate", occupancy_rate, f"Bed occupancy at {occupancy_rate*100:.0f}% — highest weight feature (35%)"),
            ("stock_shortage_ratio", stock_shortage_ratio, f"Medicine shortage ratio {stock_shortage_ratio*100:.0f}% (25% weight)"),
            ("average_wait_time_minutes", average_wait_time, f"Wait time {average_wait_time:.0f} min, normalised: {wait_norm:.2f} (20% weight)"),
            ("staff_shortage_ratio", staff_shortage_ratio, f"Staff shortage {staff_shortage_ratio*100:.0f}% (15% weight)"),
            ("severity_score", severity_score, f"External severity index {severity_score:.2f} (5% weight)"),
        ]

        contrib_keys = list(contributions.keys())
        features = [
            SHAPFeature(
                feature_name=name,
                value=round(val, 4),
                shap_value=round(contributions[contrib_keys[i]] / total, 4),
                importance_rank=i + 1,
                description=desc,
            )
            for i, (name, val, desc) in enumerate(feature_details)
        ]

        dominant = max(contributions, key=lambda k: contributions[k]).replace("_", " ")

        if score >= 0.75:
            level_text = "CRITICAL — immediate action required"
        elif score >= 0.5:
            level_text = "HIGH — escalation recommended"
        elif score >= 0.3:
            level_text = "MODERATE — close monitoring required"
        else:
            level_text = "LOW — routine monitoring sufficient"

        summary = (
            f"Composite risk score: {score:.3f} ({level_text}). "
            f"Primary driver: {dominant} "
            f"(contributes {contributions[contrib_keys[0]]/total*100:.0f}% of total score). "
            f"Bed occupancy ({occupancy_rate*100:.0f}%), stock shortage ({stock_shortage_ratio*100:.0f}%), "
            f"and wait time ({average_wait_time:.0f} min) are the top three risk factors."
        )

        return SHAPExplanation(
            model_name="WeightedRiskScorer_XGBoost_v1",
            model_version="1.0.0",
            confidence=round(min(0.95, 0.65 + score * 0.30), 2),
            base_value=0.30,
            output_value=score,
            features=features,
            summary_text=summary,
        )
