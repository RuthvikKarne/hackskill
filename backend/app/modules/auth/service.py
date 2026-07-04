"""Authentication Service logic.

Handles business logic for login, logout, and token management.
"""
import uuid
import structlog
import redis.asyncio as redis
from fastapi import HTTPException, status

from app.core.security.password import verify_password
from app.core.security.jwt import create_access_token, create_refresh_token
from app.core.events.bus import event_bus
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.repository import UserRepository
from app.modules.auth.events import UserLoggedInEvent
from app.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class AuthService:
    """Service layer for authentication."""
    
    def __init__(self, user_repo: UserRepository, redis_client: redis.Redis) -> None:
        self.user_repo = user_repo
        self.redis = redis_client

    async def authenticate_user(self, login_data: LoginRequest, ip_address: str | None) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            logger.warning("auth_failed", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract permissions from role
        permissions = [p.name for p in user.role.permissions] if user.role else []
        role_name = user.role.name if user.role else "USER"
        
        access_token = create_access_token(
            subject=user.id, 
            role=role_name, 
            hospital_id=user.hospital_id, 
            permissions=permissions
        )
        refresh_token = create_refresh_token(subject=user.id)
        
        # Store refresh token in redis for blocklist validation (7 days)
        await self.redis.setex(
            f"refresh:{user.id}:{refresh_token}", 
            timedelta_seconds=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400, 
            value="valid"
        )
        
        # Publish Domain Event
        event = UserLoggedInEvent.create(
            user_id=user.id, 
            hospital_id=user.hospital_id, 
            ip_address=ip_address
        )
        await event_bus.publish(event)
        
        logger.info("auth_success", user_id=str(user.id))
        
        # Return access_token, we will set refresh_token as HttpOnly cookie in the router
        return TokenResponse(access_token=access_token), refresh_token

    async def logout(self, user_id: str | uuid.UUID, refresh_token: str | None) -> None:
        """Log out user by invalidating the refresh token."""
        if refresh_token:
            await self.redis.delete(f"refresh:{user_id}:{refresh_token}")
        logger.info("auth_logout", user_id=str(user_id))
