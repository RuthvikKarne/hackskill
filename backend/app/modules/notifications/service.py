"""Notifications Service logic.

Handles business logic for retrieving and creating notifications.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository


class NotificationService:
    """Service layer for notifications."""
    
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    async def get_user_notifications(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Fetch notifications specific to a user."""
        return await self.repo.get_user_notifications(user_id=user_id, skip=skip, limit=limit)

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        """Mark a notification as read."""
        notif = await self.repo.get_by_id(notification_id)
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        if notif.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this notification")
            
        return await self.repo.update(notification_id, is_read=True)

    async def create_notification(
        self, 
        user_id: uuid.UUID, 
        hospital_id: uuid.UUID, 
        message: str, 
        related_entity_type: str = None, 
        related_entity_id: str = None
    ) -> Notification:
        """Internal method to create a notification (usually called by event listeners)."""
        return await self.repo.create(
            user_id=user_id,
            hospital_id=hospital_id,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
