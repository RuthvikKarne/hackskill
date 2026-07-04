"""Notifications Router.

Exposes endpoints for users to view and manage their notifications.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import NotificationResponse
from app.modules.notifications.service import NotificationService
from app.shared.response import APIResponse, success_response

router = APIRouter()


def get_notification_service(db: AsyncSession = Depends(get_db_session)) -> NotificationService:
    repo = NotificationRepository(db)
    return NotificationService(repo)


@router.get("", response_model=APIResponse[list[NotificationResponse]])
async def list_notifications(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    notif_service: NotificationService = Depends(get_notification_service),
    # Any authenticated hospital user
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "LAB_TECH"]))
) -> Any:
    """List all notifications for the currently authenticated user."""
    actor_id = uuid.UUID(user["sub"])
    notifs = await notif_service.get_user_notifications(actor_id, skip, limit)
    return success_response(data=list(notifs))


@router.patch("/{notification_id}/read", response_model=APIResponse[NotificationResponse])
async def mark_notification_read(
    notification_id: uuid.UUID,
    notif_service: NotificationService = Depends(get_notification_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "LAB_TECH"]))
) -> Any:
    """Mark a specific notification as read."""
    actor_id = uuid.UUID(user["sub"])
    updated_notif = await notif_service.mark_as_read(notification_id, actor_id)
    return success_response(data=updated_notif, message="Notification marked as read")
