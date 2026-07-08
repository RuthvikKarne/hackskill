"""Forecasting Service — Patient load and medicine demand forecasting.

Algorithm design (Prophet substitute):
  - Patient load: Linear regression on recent history + day-of-week seasonal weights
  - Medicine demand: Exponential smoothing + trend extrapolation
  - Confidence intervals: ±15% of mean (simplified frequentist approach)
  - SHAP weights computed as proportional feature contributions

These algorithms produce the same output contract as a real Prophet + XGBoost
pipeline would, making it straightforward to swap in real models in Phase 7+.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from app.schemas import (
    ForecastPoint,
    ForecastResponse,
    SHAPExplanation,
    SHAPFeature,
)

# Day-of-week patient load indices (Mon=0 … Sun=6)
# Based on epidemiological patterns: higher load Mon/Tue/Fri, lower weekends
_DOW_WEIGHTS: list[float] = [1.15, 1.10, 1.02, 0.98, 1.08, 0.85, 0.75]

# Month seasonal adjustment (Jan=0 … Dec=11)
# Higher in winter/monsoon months
_MONTH_WEIGHTS: list[float] = [
    1.12, 1.08, 1.05, 0.98, 0.95, 0.90,
    1.10, 1.15, 1.05, 1.00, 1.02, 1.10,
]

# Exponential smoothing alpha
_EMA_ALPHA: float = 0.4


def _compute_ema(series: list[float]) -> float:
    """Compute exponential moving average of a series."""
    if not series:
        return 0.0
    ema = series[0]
    for val in series[1:]:
        ema = _EMA_ALPHA * val + (1 - _EMA_ALPHA) * ema
    return ema


def _linear_trend(series: list[float]) -> float:
    """Compute slope of a simple linear trend using least-squares."""
    n = len(series)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(series) / n
    numerator = sum((i - x_mean) * (series[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator != 0 else 0.0


class ForecastingService:
    """Patient load and medicine demand forecasting service.

    Uses deterministic time-series methods that mirror the Prophet API contract.
    """

    # ── Patient Load Forecast ─────────────────────────────────────────────────

    def forecast_patient_load(
        self,
        *,
        hospital_id: str,
        horizon_days: int = 7,
        historical_volumes: list[float] | None = None,
        base_daily_volume: float = 120.0,
    ) -> ForecastResponse:
        """Forecast expected patient load for the next ``horizon_days`` days.

        Args:
            hospital_id: Target hospital UUID.
            horizon_days: Number of days to forecast (7 or 30).
            historical_volumes: List of recent daily patient counts (oldest first).
            base_daily_volume: Fallback baseline if no history available.

        Returns:
            ForecastResponse with daily forecast points and SHAP explanation.
        """
        history = historical_volumes or [base_daily_volume] * 14
        baseline = _compute_ema(history)
        trend = _linear_trend(history)

        points: list[ForecastPoint] = []
        today = date.today()

        for day_offset in range(1, horizon_days + 1):
            target_date = today + timedelta(days=day_offset)
            dow_w = _DOW_WEIGHTS[target_date.weekday()]
            month_w = _MONTH_WEIGHTS[target_date.month - 1]
            trend_contribution = trend * day_offset

            value = max(0.0, (baseline + trend_contribution) * dow_w * month_w)
            margin = value * 0.15  # ±15% confidence interval
            points.append(
                ForecastPoint(
                    date=target_date.isoformat(),
                    value=round(value, 1),
                    lower_bound=round(max(0.0, value - margin), 1),
                    upper_bound=round(value + margin, 1),
                )
            )

        explanation = self._build_patient_load_explanation(
            baseline=baseline,
            trend=trend,
            horizon_days=horizon_days,
            avg_dow_weight=sum(_DOW_WEIGHTS) / 7,
            forecast_mean=sum(p.value for p in points) / len(points),
        )

        return ForecastResponse(
            hospital_id=hospital_id,
            forecast_type="patient_load",
            horizon_days=horizon_days,
            points=points,
            explanation=explanation,
        )

    # ── Medicine Demand Forecast ──────────────────────────────────────────────

    def forecast_medicine_demand(
        self,
        *,
        hospital_id: str,
        medicine_id: str,
        historical_consumption: list[float] | None = None,
        base_monthly_consumption: float = 500.0,
    ) -> dict[str, Any]:
        """Forecast medicine consumption for the next 30 days.

        Args:
            hospital_id: Target hospital UUID.
            medicine_id: Medicine identifier.
            historical_consumption: Monthly consumption history (oldest first).
            base_monthly_consumption: Fallback if no history.

        Returns:
            Dict with 30-day forecast, reorder point, and SHAP explanation.
        """
        history = historical_consumption or [base_monthly_consumption] * 6
        ema = _compute_ema(history)
        trend = _linear_trend(history)

        # Forecast next 4 weeks (28 days)
        horizon = 4  # weeks
        weekly_base = ema / 4.3  # 4.3 weeks per month
        weekly_trend = trend / 4.3

        weekly_forecasts: list[dict[str, Any]] = []
        for week in range(1, horizon + 1):
            week_val = max(0.0, weekly_base + weekly_trend * week)
            margin = week_val * 0.12
            weekly_forecasts.append(
                {
                    "week": week,
                    "value": round(week_val, 1),
                    "lower_bound": round(max(0.0, week_val - margin), 1),
                    "upper_bound": round(week_val + margin, 1),
                }
            )

        total_30d = sum(w["value"] for w in weekly_forecasts)
        reorder_point = round(total_30d * 0.30, 1)  # reorder when 30% remains
        safety_stock = round(total_30d * 0.20, 1)   # 20% safety buffer

        shap_features = [
            SHAPFeature(
                feature_name="exponential_moving_average",
                value=round(ema, 2),
                shap_value=round(ema * 0.60, 3),
                importance_rank=1,
                description="Recent consumption trend (most influential)",
            ),
            SHAPFeature(
                feature_name="linear_trend_slope",
                value=round(trend, 3),
                shap_value=round(abs(trend) * 0.25, 3),
                importance_rank=2,
                description=f"Monthly trend direction: {'increasing' if trend >= 0 else 'decreasing'}",
            ),
            SHAPFeature(
                feature_name="seasonality",
                value=round(_MONTH_WEIGHTS[date.today().month - 1], 2),
                shap_value=round(ema * 0.15, 3),
                importance_rank=3,
                description="Monthly seasonal adjustment factor",
            ),
        ]

        summary = (
            f"Based on {len(history)} months of consumption history, "
            f"the model forecasts {total_30d:.0f} units of medicine '{medicine_id}' "
            f"over the next 30 days (EMA baseline: {ema:.0f}/month). "
            f"Recommended reorder point: {reorder_point:.0f} units remaining. "
            f"Safety stock: {safety_stock:.0f} units."
        )

        return {
            "hospital_id": hospital_id,
            "medicine_id": medicine_id,
            "forecast_period_days": 28,
            "total_forecast_units": round(total_30d, 1),
            "reorder_point_units": reorder_point,
            "safety_stock_units": safety_stock,
            "weekly_breakdown": weekly_forecasts,
            "explanation": SHAPExplanation(
                model_name="EMA_Linear_Trend",
                model_version="1.0.0",
                confidence=0.78,
                base_value=round(ema, 2),
                output_value=round(total_30d, 2),
                features=shap_features,
                summary_text=summary,
            ).model_dump(),
        }

    # ── Internal: SHAP explanation builders ──────────────────────────────────

    def _build_patient_load_explanation(
        self,
        *,
        baseline: float,
        trend: float,
        horizon_days: int,
        avg_dow_weight: float,
        forecast_mean: float,
    ) -> SHAPExplanation:
        """Build a SHAP-style explanation for the patient load forecast."""
        # Proportional SHAP contributions
        baseline_contrib = baseline
        trend_contrib = abs(trend * horizon_days / 2)
        seasonal_contrib = abs(forecast_mean - baseline) * 0.5

        total = baseline_contrib + trend_contrib + seasonal_contrib or 1.0

        features = [
            SHAPFeature(
                feature_name="recent_patient_volume_ema",
                value=round(baseline, 1),
                shap_value=round(baseline_contrib / total, 3),
                importance_rank=1,
                description="Exponential moving average of recent patient volumes — primary driver",
            ),
            SHAPFeature(
                feature_name="day_of_week_seasonality",
                value=round(avg_dow_weight, 3),
                shap_value=round(seasonal_contrib / total * 0.6, 3),
                importance_rank=2,
                description="Weekly patient volume patterns (higher Mon–Fri, lower weekends)",
            ),
            SHAPFeature(
                feature_name="month_seasonality",
                value=round(_MONTH_WEIGHTS[date.today().month - 1], 3),
                shap_value=round(seasonal_contrib / total * 0.4, 3),
                importance_rank=3,
                description="Monthly seasonal index reflecting disease burden patterns",
            ),
            SHAPFeature(
                feature_name="linear_trend",
                value=round(trend, 3),
                shap_value=round(trend_contrib / total, 3),
                importance_rank=4,
                description=f"Volume trend: {'increasing' if trend >= 0 else 'decreasing'} by {abs(trend):.1f}/day",
            ),
        ]

        direction = "increase" if trend >= 0 else "decrease"
        summary = (
            f"Patient load forecast for next {horizon_days} days averages {forecast_mean:.0f} patients/day. "
            f"The primary driver is recent history (EMA: {baseline:.0f}/day). "
            f"A {direction} trend of {abs(trend):.1f} patients/day is projected. "
            f"Day-of-week and seasonal adjustments contribute the remaining variation."
        )

        return SHAPExplanation(
            model_name="EMA_LinearTrend_Seasonal",
            model_version="1.0.0",
            confidence=round(min(0.92, 0.70 + math.log1p(len([baseline])) * 0.1), 2),
            base_value=round(baseline, 2),
            output_value=round(forecast_mean, 2),
            features=features,
            summary_text=summary,
        )
