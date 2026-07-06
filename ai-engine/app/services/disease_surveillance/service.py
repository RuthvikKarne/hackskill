from __future__ import annotations

from typing import Any


class DiseaseSurveillanceService:
    """Provide deterministic, explainable disease-risk scoring for MVP demos."""

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
        cases = confirmed_cases + suspected_cases
        incidence_rate = cases / max(population, 1) * 100000
        growth_factor = 1 + min(new_cases_today / max(confirmed_cases, 1), 2.0)
        score = min(
            1.0,
            0.5 * severity_score
            + 0.25 * min(weather_risk, 1.0)
            + 0.1 * min(incidence_rate / 200.0, 1.0)
            + 0.1 * min(growth_factor / 2.0, 1.0)
            + 0.05 * min((confirmed_cases + new_cases_today) / 250.0, 1.0),
        )

        if score >= 0.7:
            risk_level = "critical"
        elif score >= 0.45:
            risk_level = "high"
        elif score >= 0.25:
            risk_level = "moderate"
        else:
            risk_level = "low"

        recommendations = []
        if risk_level in {"high", "critical"}:
            recommendations.extend(
                [
                    "Activate surge staffing for the district response team.",
                    "Prioritize medicine and oxygen redistribution to high-risk facilities.",
                ]
            )
        else:
            recommendations.append("Continue routine district monitoring and reporting.")

        return {
            "district_id": district_id,
            "risk_score": round(score, 3),
            "risk_level": risk_level,
            "incidence_rate_per_100k": round(incidence_rate, 2),
            "recommendations": recommendations,
            "explanation": {
                "severity_score": severity_score,
                "weather_risk": weather_risk,
                "confirmed_cases": confirmed_cases,
                "suspected_cases": suspected_cases,
                "new_cases_today": new_cases_today,
            },
        }
