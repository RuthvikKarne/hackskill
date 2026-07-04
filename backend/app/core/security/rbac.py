"""Role-Based Access Control.

Defines dependencies to protect routes based on JWT permissions.
"""
from typing import Callable

from fastapi import Depends, HTTPException, Request, status


class RequiresPermission:
    """Dependency to check if the current user has the required permission."""
    
    def __init__(self, required_permission: str) -> None:
        self.required_permission = required_permission

    def __call__(self, request: Request) -> dict:
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        user_permissions = user.get("permissions", [])
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}"
            )
            
        return user


class RequiresRole:
    """Dependency to check if the current user has a specific role."""
    
    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles

    def __call__(self, request: Request) -> dict:
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        user_role = user.get("role")
        if user_role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges"
            )
            
        return user
