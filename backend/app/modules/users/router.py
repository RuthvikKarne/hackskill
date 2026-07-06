"""Users Router.

Exposes endpoints for user CRUD.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.auth.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserResponse
from app.modules.users.service import UserService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)


@router.get("", response_model=APIResponse[PaginatedResponse[UserResponse]])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    # Admins and Hospital Admins can view users in their hospital
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """List all users within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    users = await user_service.get_all_users(hospital_id, skip, limit)
    paginated = paginate(items=users, total=len(users), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[UserResponse])
async def create_user(
    request: Request,
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Register a new user."""
    actor_id = uuid.UUID(user["sub"])
    actor_hospital_id = uuid.UUID(user["hospital_id"]) if user.get("hospital_id") else None
    
    new_user = await user_service.create_user(data, actor_id, actor_hospital_id)
    return success_response(data=new_user, message="User created successfully")


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Get user details."""
    fetched_user = await user_service.get_user(user_id)
    return success_response(data=fetched_user)
