"""Audit Router.

Exposes endpoints for admins to view audit logs.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.audit.repository import AuditLogRepository
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.service import AuditService
from app.shared.response import APIResponse, success_response

router = APIRouter()


def get_audit_service(db: AsyncSession = Depends(get_db_session)) -> AuditService:
    repo = AuditLogRepository(db)
    return AuditService(repo)


@router.get("", response_model=APIResponse[list[AuditLogResponse]])
async def list_audit_logs(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    audit_service: AuditService = Depends(get_audit_service),
    # Only Admins can view audit logs
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """List audit logs for the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    logs = await audit_service.get_hospital_logs(hospital_id, skip, limit)
    return success_response(data=list(logs))
