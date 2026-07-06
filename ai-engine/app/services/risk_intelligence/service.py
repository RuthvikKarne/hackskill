from __future__ import annotations

from typing import Any


class RiskIntelligenceService:
    """Provide deterministic hospital risk scoring for MVP demos."""

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
        score = min(
            1.0,
            0.35 * min(occupancy_rate, 1.0)
            + 0.25 * min(stock_shortage_ratio, 1.0)
            + 0.2 * min(average_wait_time / 90.0, 1.0)
            + 0.15 * min(staff_shortage_ratio, 1.0)
            + 0.05 * min(severity_score, 1.0),
        )

        if score >= 0.75:
            risk_level = "critical"
        elif score >= 0.5:
            risk_level = "high"
        elif score >= 0.3:
            risk_level = "moderate"
        else:
            risk_level = "low"

        recommendations = []
        if risk_level in {"high", "critical"}:
            recommendations.extend(
                [
                    "Open additional temporary beds and reassign staff.",
                    "Escalate stock replenishment and oxygen availability immediately.",
                ]
            )
        else:
            recommendations.append("Maintain current monitoring cadence.")

        return {
            "hospital_id": hospital_id,
            "risk_score": round(score, 3),
            "risk_level": risk_level,
            "recommendations": recommendations,
            "explanation": {
                "occupancy_rate": occupancy_rate,
                "stock_shortage_ratio": stock_shortage_ratio,
                "average_wait_time": average_wait_time,
                "staff_shortage_ratio": staff_shortage_ratio,
                "severity_score": severity_score,
            },
        }
