<<<<<<< HEAD
"""RBAC — Role-Based Access Control for HRIP.

Defines:
  1. Permission constants (module:action strings)
  2. Role → permission set mapping
  3. require_permission() — FastAPI dependency factory

Usage in a router:

    from app.core.security.rbac import require_permission, Permissions

    @router.get("/patients")
    async def list_patients(
        _: None = Depends(require_permission(Permissions.PATIENTS_READ)),
        current_user: TokenPayload = Depends(get_current_user),
    ):
        ...

The dependency raises PermissionDeniedError (403) if the current user's
token does not carry the required permission.
"""
from __future__ import annotations

from fastapi import Depends

from app.core.exceptions.base import PermissionDeniedError
from app.core.logging.logger import get_logger

log = get_logger(__name__)


# ── Permission constants ───────────────────────────────────────────────────────


class Permissions:
    """Namespace for all HRIP permission strings.

    Convention: "<module>:<action>"
    Actions: read | write | delete | approve | export
    """

    # Users
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"

    # Hospitals
    HOSPITALS_READ = "hospitals:read"
    HOSPITALS_WRITE = "hospitals:write"
    HOSPITALS_DELETE = "hospitals:delete"

    # Patients
    PATIENTS_READ = "patients:read"
    PATIENTS_WRITE = "patients:write"
    PATIENTS_DELETE = "patients:delete"

    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"
    INVENTORY_DELETE = "inventory:delete"

    # Beds
    BEDS_READ = "beds:read"
    BEDS_WRITE = "beds:write"
    BEDS_DELETE = "beds:delete"

    # Doctors
    DOCTORS_READ = "doctors:read"
    DOCTORS_WRITE = "doctors:write"
    DOCTORS_DELETE = "doctors:delete"

    # Laboratory
    LABORATORY_READ = "laboratory:read"
    LABORATORY_WRITE = "laboratory:write"
    LABORATORY_DELETE = "laboratory:delete"

    # Emergency
    EMERGENCY_READ = "emergency:read"
    EMERGENCY_WRITE = "emergency:write"
    EMERGENCY_DELETE = "emergency:delete"

    # Notifications
    NOTIFICATIONS_READ = "notifications:read"
    NOTIFICATIONS_WRITE = "notifications:write"

    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"

    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"

    # Audit
    AUDIT_READ = "audit:read"

    # AI Recommendations
    AI_RECOMMENDATIONS_READ = "ai_recommendations:read"
    AI_RECOMMENDATIONS_APPROVE = "ai_recommendations:approve"
    AI_RECOMMENDATIONS_REJECT = "ai_recommendations:reject"


# ── Role definitions ───────────────────────────────────────────────────────────


class Roles:
    """Role name constants. Match the values stored in the JWT 'role' claim."""

    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    DISTRICT_ADMIN = "DISTRICT_ADMIN"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    PHARMACIST = "PHARMACIST"
    EMERGENCY_OPERATOR = "EMERGENCY_OPERATOR"


# Permission set for each role (mirrors the RBAC matrix in the architecture doc)
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    Roles.SYSTEM_ADMIN: frozenset(
        [
            Permissions.USERS_READ, Permissions.USERS_WRITE, Permissions.USERS_DELETE,
            Permissions.HOSPITALS_READ, Permissions.HOSPITALS_WRITE, Permissions.HOSPITALS_DELETE,
            Permissions.PATIENTS_READ, Permissions.PATIENTS_WRITE, Permissions.PATIENTS_DELETE,
            Permissions.INVENTORY_READ, Permissions.INVENTORY_WRITE, Permissions.INVENTORY_DELETE,
            Permissions.BEDS_READ, Permissions.BEDS_WRITE, Permissions.BEDS_DELETE,
            Permissions.DOCTORS_READ, Permissions.DOCTORS_WRITE, Permissions.DOCTORS_DELETE,
            Permissions.LABORATORY_READ, Permissions.LABORATORY_WRITE, Permissions.LABORATORY_DELETE,
            Permissions.EMERGENCY_READ, Permissions.EMERGENCY_WRITE, Permissions.EMERGENCY_DELETE,
            Permissions.ANALYTICS_READ, Permissions.ANALYTICS_EXPORT,
            Permissions.REPORTS_READ, Permissions.REPORTS_EXPORT,
            Permissions.AUDIT_READ,
            Permissions.AI_RECOMMENDATIONS_READ, Permissions.AI_RECOMMENDATIONS_APPROVE,
            Permissions.AI_RECOMMENDATIONS_REJECT,
        ]
    ),
    Roles.DISTRICT_ADMIN: frozenset(
        [
            Permissions.USERS_READ,
            Permissions.HOSPITALS_READ,
            Permissions.PATIENTS_READ,
            Permissions.INVENTORY_READ,
            Permissions.BEDS_READ,
            Permissions.DOCTORS_READ, Permissions.DOCTORS_WRITE,
            Permissions.LABORATORY_READ,
            Permissions.EMERGENCY_READ, Permissions.EMERGENCY_WRITE,
            Permissions.ANALYTICS_READ, Permissions.ANALYTICS_EXPORT,
            Permissions.REPORTS_READ, Permissions.REPORTS_EXPORT,
            Permissions.AUDIT_READ,
            Permissions.AI_RECOMMENDATIONS_READ, Permissions.AI_RECOMMENDATIONS_APPROVE,
        ]
    ),
    Roles.HOSPITAL_ADMIN: frozenset(
        [
            Permissions.USERS_READ,
            Permissions.HOSPITALS_READ, Permissions.HOSPITALS_WRITE,
            Permissions.PATIENTS_READ, Permissions.PATIENTS_WRITE, Permissions.PATIENTS_DELETE,
            Permissions.INVENTORY_READ, Permissions.INVENTORY_WRITE, Permissions.INVENTORY_DELETE,
            Permissions.BEDS_READ, Permissions.BEDS_WRITE, Permissions.BEDS_DELETE,
            Permissions.DOCTORS_READ, Permissions.DOCTORS_WRITE,
            Permissions.LABORATORY_READ, Permissions.LABORATORY_WRITE,
            Permissions.EMERGENCY_READ, Permissions.EMERGENCY_WRITE,
            Permissions.ANALYTICS_READ,
            Permissions.REPORTS_READ, Permissions.REPORTS_EXPORT,
            Permissions.AUDIT_READ,
            Permissions.AI_RECOMMENDATIONS_READ, Permissions.AI_RECOMMENDATIONS_APPROVE,
        ]
    ),
    Roles.DOCTOR: frozenset(
        [
            Permissions.PATIENTS_READ, Permissions.PATIENTS_WRITE,
            Permissions.INVENTORY_READ,
            Permissions.BEDS_READ,
            Permissions.DOCTORS_READ,
            Permissions.LABORATORY_READ,
            Permissions.EMERGENCY_READ,
            Permissions.ANALYTICS_READ,
        ]
    ),
    Roles.NURSE: frozenset(
        [
            Permissions.PATIENTS_READ, Permissions.PATIENTS_WRITE,
            Permissions.INVENTORY_READ,
            Permissions.BEDS_READ, Permissions.BEDS_WRITE,
            Permissions.DOCTORS_READ,
            Permissions.LABORATORY_READ,
            Permissions.EMERGENCY_READ,
        ]
    ),
    Roles.LAB_TECHNICIAN: frozenset(
        [
            Permissions.PATIENTS_READ,
            Permissions.LABORATORY_READ, Permissions.LABORATORY_WRITE,
        ]
    ),
    Roles.PHARMACIST: frozenset(
        [
            Permissions.PATIENTS_READ,
            Permissions.INVENTORY_READ, Permissions.INVENTORY_WRITE,
        ]
    ),
    Roles.EMERGENCY_OPERATOR: frozenset(
        [
            Permissions.PATIENTS_READ,
            Permissions.INVENTORY_READ,
            Permissions.BEDS_READ, Permissions.BEDS_WRITE,
            Permissions.EMERGENCY_READ, Permissions.EMERGENCY_WRITE, Permissions.EMERGENCY_DELETE,
            Permissions.ANALYTICS_READ,
        ]
    ),
}


def get_role_permissions(role: str) -> frozenset[str]:
    """Return the permission set for a given role.

    Args:
        role: Role name (e.g. "HOSPITAL_ADMIN").

    Returns:
        Frozenset of permission strings. Empty set if role is unknown.
    """
    return ROLE_PERMISSIONS.get(role, frozenset())


# ── FastAPI dependency factory ─────────────────────────────────────────────────


def require_permission(permission: str):
    """FastAPI dependency factory that enforces a single permission.

    Reads the current user from request.state.user (set by JWTAuthMiddleware).
    Raises PermissionDeniedError (403) if the permission is not in the
    user's token claims.

    Args:
        permission: A permission constant, e.g. Permissions.PATIENTS_READ.

    Returns:
        A FastAPI dependency (async function).

    Usage:
        @router.get("/patients")
        async def list_patients(
            _: None = Depends(require_permission(Permissions.PATIENTS_READ)),
        ):
            ...
    """
    from fastapi import Request

    async def _dependency(request: Request) -> None:
        user = getattr(request.state, "user", None)
        if user is None:
            raise PermissionDeniedError(permission)

        if not user.has_permission(permission):
            log.warning(
                "permission_denied",
                required=permission,
                user_id=user.sub,
                role=user.role,
                user_permissions=user.permissions,
            )
            raise PermissionDeniedError(permission)

    return _dependency
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
