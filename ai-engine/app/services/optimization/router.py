"""Optimization Service Router — Resource redistribution optimization."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Query

from app.schemas import OptimizationResponse
from app.services.optimization.service import OptimizationService

router = APIRouter()
_service = OptimizationService()


@router.post(
    "/resource-redistribution",
    response_model=OptimizationResponse,
    summary="Optimize resource redistribution",
    description=(
        "Generate an optimal resource redistribution plan for all hospitals in a district. "
        "Uses greedy surplus→deficit matching (OR-Tools compatible output). "
        "Produces prioritised bed, medicine, and staff transfer actions with SHAP explanation."
    ),
)
async def optimize_resource_redistribution(
    district_id: str = Query(..., description="District UUID"),
    hospital_snapshots: list[dict[str, Any]] | None = Body(
        None,
        description=(
            "Optional list of hospital snapshots. Each must contain: "
            "hospital_id, bed_capacity, bed_occupancy, stock_level, staff_count, staff_required. "
            "If omitted, synthetic demo data is used."
        ),
    ),
) -> OptimizationResponse:
    """Generate optimal resource redistribution plan for a district."""
    return _service.optimize_resource_redistribution(
        district_id=district_id,
        hospital_snapshots=hospital_snapshots,
    )
