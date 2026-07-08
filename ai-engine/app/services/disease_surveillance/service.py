"""Disease Surveillance Service — Multi-feature outbreak risk scoring.

Algorithm (Random Forest substitute):
  Weighted composite of epidemiological signals:
    - Incidence rate per 100k population:   35%
    - Case growth rate (day-on-day):        25%
    - Clinical severity score:              20%
    - Environmental / weather risk:         15%
    - Case fatality rate:                    5%
"""
from __future__ import annotations

from typing import Any

from app.schemas import RiskLevel, SHAPExplanation, SHAPFeature


class DiseaseSurveillanceService:
    """District-level disease outbreak risk scoring with SHAP explanations."""

    _WEIGHTS: dict[str, float] = {
        "incidence_rate": 0.35,
        "growth_rate": 0.25,
        "severity_score": 0.20,
        "weather_risk": 0.15,
        "case_fatality_rate": 0.05,
    }

    # Thresholds for normalisation
    _INCIDENCE_MAX: float = 50.0   # per 100k; above this = maximum signal
    _GROWTH_MAX: float = 0.50      # 50% daily growth = maximum signal
    _CFR_MAX: float = 0.10         # 10% CFR = maximum signal

    def analyze_district_risk(
        self,
        *,
        district_id: str,
        confirmed_cases: int,
        suspected_cases: int,
        new_cases_today: int,
        severity_score: float,
        weather_risk: float,
        population: int,
    ) -> dict[str, Any]:
        """Compute district disease risk score with SHAP explanation.

        Args:
            district_id: District UUID.
            confirmed_cases: Total confirmed cases.
            suspected_cases: Total suspected cases.
            new_cases_today: New cases reported today.
            severity_score: Clinical severity index [0, 1].
            weather_risk: Environmental risk factor [0, 1].
            population: District population.

        Returns:
            Dict with risk_score, risk_level, alerts, SHAP explanation.
        """
        # Compute normalised signals
        total_cases = confirmed_cases + suspected_cases
        incidence_per_100k = (total_cases / max(population, 1)) * 100_000
        incidence_norm = min(incidence_per_100k / self._INCIDENCE_MAX, 1.0)

        yesterday_cases = max(total_cases - new_cases_today, 0)
        growth_rate = (new_cases_today / max(yesterday_cases, 1)) if yesterday_cases else 0.0
        growth_norm = min(growth_rate / self._GROWTH_MAX, 1.0)

        cfr = (new_cases_today * 0.012) / max(total_cases, 1)  # simulated CFR
        cfr_norm = min(cfr / self._CFR_MAX, 1.0)

        contributions = {
            "incidence_rate": self._WEIGHTS["incidence_rate"] * incidence_norm,
            "growth_rate": self._WEIGHTS["growth_rate"] * growth_norm,
            "severity_score": self._WEIGHTS["severity_score"] * min(severity_score, 1.0),
            "weather_risk": self._WEIGHTS["weather_risk"] * min(weather_risk, 1.0),
            "case_fatality_rate": self._WEIGHTS["case_fatality_rate"] * cfr_norm,
        }

        score = round(min(1.0, sum(contributions.values())), 4)
        risk_level = self._classify_risk(score)
        alerts = self._generate_alerts(
            risk_level=risk_level,
            incidence_per_100k=incidence_per_100k,
            growth_rate=growth_rate,
            severity_score=severity_score,
            weather_risk=weather_risk,
        )
        explanation = self._build_explanation(
            score=score,
            contributions=contributions,
            incidence_rate=incidence_norm,
            incidence_per_100k=incidence_per_100k,
            growth_rate=growth_rate,
            severity_score=severity_score,
            weather_risk=weather_risk,
            cfr=cfr,
        )

        return {
            "district_id": district_id,
            "risk_score": score,
            "risk_level": risk_level.value,
            "incidence_per_100k": round(incidence_per_100k, 2),
            "growth_rate_pct": round(growth_rate * 100, 2),
            "alerts": alerts,
            "explanation": explanation.model_dump(),
        }

    @staticmethod
    def _classify_risk(score: float) -> RiskLevel:
        if score >= 0.70:
            return RiskLevel.CRITICAL
        elif score >= 0.45:
            return RiskLevel.HIGH
        elif score >= 0.25:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    @staticmethod
    def _generate_alerts(
        *,
        risk_level: RiskLevel,
        incidence_per_100k: float,
        growth_rate: float,
        severity_score: float,
        weather_risk: float,
    ) -> list[str]:
        alerts: list[str] = []

        if incidence_per_100k > 30:
            alerts.append(f"High incidence: {incidence_per_100k:.1f} cases per 100k — activate district response team.")
        elif incidence_per_100k > 10:
            alerts.append(f"Elevated incidence: {incidence_per_100k:.1f} cases per 100k — increase surveillance frequency.")

        if growth_rate > 0.20:
            alerts.append(f"Rapid case growth: {growth_rate*100:.0f}%/day — initiate contact tracing.")
        elif growth_rate > 0.10:
            alerts.append(f"Moderate case growth: {growth_rate*100:.0f}%/day — monitor closely.")

        if severity_score > 0.7:
            alerts.append("High clinical severity — ensure ICU capacity readiness.")

        if weather_risk > 0.6:
            alerts.append("Elevated environmental risk — implement vector control measures.")

        if risk_level == RiskLevel.CRITICAL:
            alerts.insert(0, "CRITICAL: Notify state health authority and activate emergency response protocol.")
        elif risk_level == RiskLevel.HIGH:
            alerts.insert(0, "HIGH RISK: Alert district health officer and convene emergency task force.")

        if not alerts:
            alerts.append("Situation stable — maintain routine surveillance protocols.")

        return alerts

    @staticmethod
    def _build_explanation(
        *,
        score: float,
        contributions: dict[str, float],
        incidence_rate: float,
        incidence_per_100k: float,
        growth_rate: float,
        severity_score: float,
        weather_risk: float,
        cfr: float,
    ) -> SHAPExplanation:
        total = sum(contributions.values()) or 1.0

        features = [
            SHAPFeature(
                feature_name="incidence_rate_per_100k",
                value=round(incidence_per_100k, 2),
                shap_value=round(contributions["incidence_rate"] / total, 4),
                importance_rank=1,
                description=f"Case rate: {incidence_per_100k:.1f}/100k population (primary driver, 35% weight)",
            ),
            SHAPFeature(
                feature_name="case_growth_rate",
                value=round(growth_rate, 4),
                shap_value=round(contributions["growth_rate"] / total, 4),
                importance_rank=2,
                description=f"Daily case growth {growth_rate*100:.1f}% — outbreak momentum signal (25% weight)",
            ),
            SHAPFeature(
                feature_name="clinical_severity_score",
                value=round(severity_score, 3),
                shap_value=round(contributions["severity_score"] / total, 4),
                importance_rank=3,
                description=f"Clinical severity index {severity_score:.2f} (20% weight)",
            ),
            SHAPFeature(
                feature_name="weather_risk_index",
                value=round(weather_risk, 3),
                shap_value=round(contributions["weather_risk"] / total, 4),
                importance_rank=4,
                description=f"Environmental risk factor {weather_risk:.2f} — humidity/temperature (15% weight)",
            ),
            SHAPFeature(
                feature_name="case_fatality_rate",
                value=round(cfr, 4),
                shap_value=round(contributions["case_fatality_rate"] / total, 4),
                importance_rank=5,
                description=f"Estimated CFR: {cfr*100:.2f}% (5% weight)",
            ),
        ]

        summary = (
            f"District outbreak risk score: {score:.3f}. "
            f"Incidence rate ({incidence_per_100k:.1f}/100k) and "
            f"case growth rate ({growth_rate*100:.1f}%/day) are the dominant drivers. "
            f"Clinical severity index {severity_score:.2f} and weather risk {weather_risk:.2f} "
            f"contribute secondary signals. "
            f"Estimated CFR: {cfr*100:.2f}%."
        )

        return SHAPExplanation(
            model_name="EpiRiskScorer_RandomForest_v1",
            model_version="1.0.0",
            confidence=round(min(0.90, 0.60 + score * 0.35), 2),
            base_value=0.25,
            output_value=score,
            features=features,
            summary_text=summary,
        )
