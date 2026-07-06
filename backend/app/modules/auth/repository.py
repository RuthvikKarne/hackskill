"""Authentication repository.

Handles DB access for Auth-related models (mainly querying User by email).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.auth.models import User


class UserRepository(BaseRepository[User]):
    """Repository for User model interactions."""
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)
        
    async def get_by_email(self, email: str) -> User | None:
        """Fetch an active user by email."""
        stmt = select(self.model).where(
            self.model.email == email,
            self.model.is_active.is_(True),
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
