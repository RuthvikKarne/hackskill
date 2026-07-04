"""Authentication Router.

Exposes endpoints for login, logout, and token refresh.
"""
from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.database.redis import get_redis
from app.modules.auth.schemas import LoginRequest, TokenResponse, UserMeResponse
from app.modules.auth.repository import UserRepository
from app.modules.auth.service import AuthService
from app.shared.response import APIResponse, success_response
from app.core.security.rbac import RequiresRole

router = APIRouter()

def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    redis_client: redis.Redis = Depends(get_redis)
) -> AuthService:
    """Dependency injector for AuthService."""
    repo = UserRepository(db)
    return AuthService(repo, redis_client)


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """Authenticate user and return access token, sets refresh token in HttpOnly cookie."""
    client_ip = request.client.host if request.client else None
    token_response, refresh_token = await auth_service.authenticate_user(login_data, client_ip)
    
    # Set HttpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True, 
        samesite="strict",
        max_age=7 * 86400  # 7 days
    )
    
    return success_response(data=token_response, message="Logged in successfully")


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """Log out current user by clearing cookies and invalidating refresh token."""
    user = getattr(request.state, "user", None)
    refresh_token = request.cookies.get("refresh_token")
    
    if user and refresh_token:
        await auth_service.logout(user_id=user["sub"], refresh_token=refresh_token)
        
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    return success_response(message="Logged out successfully")


@router.get("/me", response_model=APIResponse[UserMeResponse])
async def get_me(
    request: Request,
    # Example usage of RBAC dependency: Only logged-in users get past this
    user_context: dict = Depends(RequiresRole(required_roles=["HOSPITAL_ADMIN", "SYS_ADMIN", "DOCTOR", "NURSE", "USER"]))
) -> Any:
    """Get details of the currently authenticated user."""
    # Fetch from DB if full profile is needed, but for /me usually JWT context is enough initially
    # For now, just map from the token context
    user_me = UserMeResponse(
        id=user_context["sub"],
        email="user@example.com",  # Placeholder, should fetch from DB in real implementation
        first_name="User",
        last_name="Name",
        hospital_id=user_context["hospital_id"],
        role=user_context["role"],
        permissions=user_context["permissions"]
    )
    return success_response(data=user_me)
