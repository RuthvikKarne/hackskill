"""Notifications Repository.

Handles DB access for Notification models.
"""
import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.notifications.models import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Notification, session=session)

    async def get_user_notifications(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        """Fetch notifications specific to a user, ordered by newest first."""
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
