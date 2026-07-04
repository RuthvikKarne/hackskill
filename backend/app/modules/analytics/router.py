"""Analytics Router.

Exposes endpoints for hospital dashboards and reporting.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.analytics.schemas import DashboardStatsResponse
from app.modules.analytics.service import AnalyticsService
from app.shared.response import APIResponse, success_response

router = APIRouter()


def get_analytics_service(db: AsyncSession = Depends(get_db_session)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/dashboard", response_model=APIResponse[DashboardStatsResponse])
async def get_dashboard_stats(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    # Hospital admins and doctors usually need dashboard access
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR"]))
) -> Any:
    """Get aggregated metrics for the hospital dashboard."""
    hospital_id = uuid.UUID(user["hospital_id"])
    stats = await analytics_service.get_dashboard_stats(hospital_id)
    return success_response(data=stats)
