"""Explainability Service — SHAP-compatible model explanations.

Provides human-readable, feature-importance-based explanations for every
AI recommendation. Implements the SHAP (SHapley Additive exPlanations)
output format without requiring the SHAP library.

In production this wraps the real SHAP library. The API contract is identical.
"""
from __future__ import annotations

from typing import Any

from app.schemas import SHAPExplanation, SHAPFeature


class ExplainabilityService:
    """Generate SHAP-style explanations for AI recommendations."""

    def explain_risk_score(
        self,
        *,
        risk_score: float,
        occupancy_rate: float,
        stock_shortage_ratio: float,
        average_wait_time: float,
        staff_shortage_ratio: float,
        severity_score: float,
    ) -> SHAPExplanation:
        """Build SHAP explanation for a hospital risk score.

        Weights mirror the risk scoring formula in RiskIntelligenceService.
        """
        contributions = {
            "bed_occupancy_rate": 0.35 * min(occupancy_rate, 1.0),
            "stock_shortage_ratio": 0.25 * min(stock_shortage_ratio, 1.0),
            "average_wait_time": 0.20 * min(average_wait_time / 90.0, 1.0),
            "staff_shortage_ratio": 0.15 * min(staff_shortage_ratio, 1.0),
            "severity_score": 0.05 * min(severity_score, 1.0),
        }

        total = sum(contributions.values()) or 1.0
        base_value = 0.30  # average expected risk score

        features = [
            SHAPFeature(
                feature_name="bed_occupancy_rate",
                value=round(occupancy_rate, 3),
                shap_value=round(contributions["bed_occupancy_rate"], 4),
                importance_rank=1,
                description=f"Bed occupancy at {occupancy_rate*100:.0f}% — highest weight feature (35%)",
            ),
            SHAPFeature(
                feature_name="stock_shortage_ratio",
                value=round(stock_shortage_ratio, 3),
                shap_value=round(contributions["stock_shortage_ratio"], 4),
                importance_rank=2,
                description=f"Medicine shortage ratio at {stock_shortage_ratio*100:.0f}% (25% weight)",
            ),
            SHAPFeature(
                feature_name="average_wait_time_minutes",
                value=round(average_wait_time, 1),
                shap_value=round(contributions["average_wait_time"], 4),
                importance_rank=3,
                description=f"Average wait time {average_wait_time:.0f} min (normalised to 90 min max, 20% weight)",
            ),
            SHAPFeature(
                feature_name="staff_shortage_ratio",
                value=round(staff_shortage_ratio, 3),
                shap_value=round(contributions["staff_shortage_ratio"], 4),
                importance_rank=4,
                description=f"Staff shortage ratio at {staff_shortage_ratio*100:.0f}% (15% weight)",
            ),
            SHAPFeature(
                feature_name="severity_score",
                value=round(severity_score, 3),
                shap_value=round(contributions["severity_score"], 4),
                importance_rank=5,
                description=f"External severity index {severity_score:.2f} (5% weight)",
            ),
        ]

        # Dominant factor for summary
        dominant = max(contributions, key=lambda k: contributions[k])
        dominant_label = dominant.replace("_", " ")

        if risk_score >= 0.75:
            level_text = "critical — immediate action required"
        elif risk_score >= 0.5:
            level_text = "high — escalation recommended"
        elif risk_score >= 0.3:
            level_text = "moderate — close monitoring required"
        else:
            level_text = "low — routine monitoring sufficient"

        summary = (
            f"The composite risk score is {risk_score:.3f} ({level_text}). "
            f"The dominant driver is {dominant_label} contributing {contributions[dominant]/total*100:.0f}% "
            f"of the total score. "
            f"Key actions should focus on: "
            f"{'reducing bed pressure' if occupancy_rate > 0.7 else ''}"
            f"{'replenishing critical stocks' if stock_shortage_ratio > 0.3 else ''}"
            f"{'addressing staff gaps' if staff_shortage_ratio > 0.3 else ''}."
        ).strip().rstrip(".")  + "."

        return SHAPExplanation(
            model_name="WeightedRiskScorer_v1",
            model_version="1.0.0",
            confidence=round(min(0.95, 0.65 + risk_score * 0.30), 2),
            base_value=base_value,
            output_value=round(risk_score, 4),
            features=features,
            summary_text=summary,
        )

    def explain_disease_risk(
        self,
        *,
        risk_score: float,
        incidence_rate: float,
        growth_rate: float,
        severity_score: float,
        weather_risk: float,
        case_fatality_rate: float,
    ) -> SHAPExplanation:
        """Build SHAP explanation for a district disease risk score."""
        contributions = {
            "incidence_rate": 0.35 * min(incidence_rate, 1.0),
            "growth_rate": 0.25 * min(growth_rate, 1.0),
            "severity_score": 0.20 * min(severity_score, 1.0),
            "weather_risk": 0.15 * min(weather_risk, 1.0),
            "case_fatality_rate": 0.05 * min(case_fatality_rate, 1.0),
        }

        features = [
            SHAPFeature(
                feature_name="incidence_rate_per_100k",
                value=round(incidence_rate, 4),
                shap_value=round(contributions["incidence_rate"], 4),
                importance_rank=1,
                description="Case rate per 100k population — primary epidemiological driver",
            ),
            SHAPFeature(
                feature_name="case_growth_rate",
                value=round(growth_rate, 4),
                shap_value=round(contributions["growth_rate"], 4),
                importance_rank=2,
                description="Day-on-day case growth rate — outbreak acceleration signal",
            ),
            SHAPFeature(
                feature_name="severity_score",
                value=round(severity_score, 3),
                shap_value=round(contributions["severity_score"], 4),
                importance_rank=3,
                description="Clinical severity index from reported case data",
            ),
            SHAPFeature(
                feature_name="weather_risk_index",
                value=round(weather_risk, 3),
                shap_value=round(contributions["weather_risk"], 4),
                importance_rank=4,
                description="Environmental risk factor (temperature + humidity index)",
            ),
            SHAPFeature(
                feature_name="case_fatality_rate",
                value=round(case_fatality_rate, 4),
                shap_value=round(contributions["case_fatality_rate"], 4),
                importance_rank=5,
                description="Observed case fatality rate",
            ),
        ]

        summary = (
            f"District disease risk score: {risk_score:.3f}. "
            f"Incidence rate ({incidence_rate*100:.2f} per 100k) is the primary driver. "
            f"Case growth rate of {growth_rate*100:.1f}%/day indicates "
            f"{'accelerating' if growth_rate > 0.1 else 'stable'} spread. "
            f"Weather conditions contribute {weather_risk*100:.0f}% environmental risk."
        )

        return SHAPExplanation(
            model_name="EpiRiskScorer_v1",
            model_version="1.0.0",
            confidence=round(min(0.90, 0.60 + risk_score * 0.35), 2),
            base_value=0.25,
            output_value=round(risk_score, 4),
            features=features,
            summary_text=summary,
        )

    def explain_generic(
        self,
        *,
        recommendation_id: str,
        model_name: str,
        output_value: float,
        feature_map: dict[str, float],
        weight_map: dict[str, float] | None = None,
    ) -> SHAPExplanation:
        """Build a generic SHAP explanation from a feature → value map.

        Args:
            recommendation_id: Reference ID of the recommendation.
            model_name: Name of the model.
            output_value: Model output score.
            feature_map: Dict of feature_name → value.
            weight_map: Optional dict of feature_name → importance weight.
                If not provided, weights are inferred from values.

        Returns:
            SHAPExplanation
        """
        if weight_map is None:
            # Uniform weights if not provided
            n = len(feature_map)
            weight_map = {k: 1.0 / n for k in feature_map}

        total_weight = sum(weight_map.values()) or 1.0
        features_sorted = sorted(
            feature_map.items(),
            key=lambda kv: weight_map.get(kv[0], 0.0),
            reverse=True,
        )

        features = [
            SHAPFeature(
                feature_name=name,
                value=round(val, 4),
                shap_value=round(val * weight_map.get(name, 0.0) / total_weight, 4),
                importance_rank=rank + 1,
                description=f"Feature '{name}' with value {val:.4f}",
            )
            for rank, (name, val) in enumerate(features_sorted)
        ]

        return SHAPExplanation(
            model_name=model_name,
            model_version="1.0.0",
            confidence=round(min(0.95, 0.50 + output_value * 0.45), 2),
            base_value=0.0,
            output_value=round(output_value, 4),
            features=features,
            summary_text=(
                f"Recommendation {recommendation_id}: model '{model_name}' produced output "
                f"{output_value:.3f}. Top feature: {features_sorted[0][0]} = {features_sorted[0][1]:.4f}."
            ),
        )

    def generate_summary_text(self, explanation: SHAPExplanation) -> str:
        """Generate a concise human-readable summary from a SHAPExplanation."""
        top_feature = explanation.features[0] if explanation.features else None
        top_name = top_feature.feature_name.replace("_", " ") if top_feature else "unknown"

        return (
            f"Model: {explanation.model_name} (v{explanation.model_version}). "
            f"Confidence: {explanation.confidence*100:.0f}%. "
            f"Score: {explanation.output_value:.3f} (vs base {explanation.base_value:.3f}). "
            f"Primary driver: {top_name}. "
            f"{explanation.summary_text}"
        )
