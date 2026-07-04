"""Users Service logic.

Handles business logic for user management and registration.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.core.security.password import get_password_hash
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.events import UserCreatedEvent


class UserService:
    """Service layer for users."""
    
    def __init__(self, user_repo: UserRepository) -> None:
        self.repo = user_repo

    async def get_all_users(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Fetch all active users for a specific hospital."""
        return await self.repo.get_all(hospital_id=hospital_id, skip=skip, limit=limit)

    async def get_user(self, user_id: uuid.UUID) -> User:
        """Fetch a single user by ID."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def create_user(self, data: UserCreate, actor_id: uuid.UUID, actor_hospital_id: uuid.UUID | None) -> User:
        """Create a new user."""
        # Check if email is taken
        existing_user = await self.repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_pwd = get_password_hash(data.password)
        
        # Determine hospital_id (use provided if sysadmin, otherwise use actor's hospital)
        final_hospital_id = data.hospital_id if data.hospital_id else actor_hospital_id
        if not final_hospital_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hospital_id is required"
            )

        # Create user
        user = await self.repo.create(
            email=data.email,
            hashed_password=hashed_pwd,
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=data.role_id,
            hospital_id=final_hospital_id,
            created_by=actor_id
        )
        
        # Fire event
        event = UserCreatedEvent.create(
            user_id=user.id,
            hospital_id=user.hospital_id,
            actor_id=actor_id,
            role_id=user.role_id
        )
        await event_bus.publish(event)
        
        return user
