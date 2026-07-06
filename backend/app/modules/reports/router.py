"""Reports Router.

Exposes endpoints for triggering and fetching reports.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import ReportCreate, ReportResponse
from app.modules.reports.service import ReportService
from app.shared.response import APIResponse, success_response

router = APIRouter()


def get_report_service(db: AsyncSession = Depends(get_db_session)) -> ReportService:
    repo = ReportRepository(db)
    return ReportService(repo)


@router.get("", response_model=APIResponse[list[ReportResponse]])
async def list_reports(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    report_service: ReportService = Depends(get_report_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """List all generated reports for the hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    reports = await report_service.get_hospital_reports(hospital_id, skip, limit)
    return success_response(data=list(reports))


@router.post("", response_model=APIResponse[ReportResponse])
async def generate_report(
    request: Request,
    data: ReportCreate,
    report_service: ReportService = Depends(get_report_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Trigger the generation of a new report."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    report = await report_service.generate_report(data, hospital_id, actor_id)
    return success_response(data=report, message="Report generated successfully")


@router.get("/{report_id}", response_model=APIResponse[ReportResponse])
async def get_report(
    report_id: uuid.UUID,
    report_service: ReportService = Depends(get_report_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Fetch details of a specific report."""
    report = await report_service.get_report(report_id)
    return success_response(data=report)
