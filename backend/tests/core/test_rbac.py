"""Unit tests for RBAC — permission constants, role mapping, dependency factory.

Tests cover:
    - All roles have non-empty permission sets
    - System Admin has all permissions
    - Role-specific permission boundaries (e.g. nurse can't approve AI recs)
    - require_permission() dependency raises 403 on missing permission
    - require_permission() passes when permission is present
    - require_permission() raises when user is not authenticated
"""
from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions.base import PermissionDeniedError
from app.core.security.jwt import TokenPayload
from app.core.security.rbac import (
    ROLE_PERMISSIONS,
    Permissions,
    Roles,
    get_role_permissions,
    require_permission,
)


# ── Permission constant tests ─────────────────────────────────────────────────


class TestPermissionConstants:
    def test_all_permission_strings_are_non_empty(self):
        for attr in dir(Permissions):
            if not attr.startswith("_"):
                value = getattr(Permissions, attr)
                if isinstance(value, str):
                    assert ":" in value, f"{attr} should be 'module:action' format"

    def test_permission_format_is_module_colon_action(self):
        assert Permissions.PATIENTS_READ == "patients:read"
        assert Permissions.BEDS_WRITE == "beds:write"
        assert Permissions.AI_RECOMMENDATIONS_APPROVE == "ai_recommendations:approve"


# ── Role permission mapping tests ─────────────────────────────────────────────


class TestRolePermissions:
    def test_all_roles_have_permissions(self):
        for role in [
            Roles.SYSTEM_ADMIN, Roles.DISTRICT_ADMIN, Roles.HOSPITAL_ADMIN,
            Roles.DOCTOR, Roles.NURSE, Roles.LAB_TECHNICIAN,
            Roles.PHARMACIST, Roles.EMERGENCY_OPERATOR,
        ]:
            assert len(get_role_permissions(role)) > 0, f"{role} has no permissions"

    def test_system_admin_has_all_permissions(self):
        sys_admin_perms = get_role_permissions(Roles.SYSTEM_ADMIN)
        for attr in dir(Permissions):
            if not attr.startswith("_"):
                value = getattr(Permissions, attr)
                if isinstance(value, str):
                    assert value in sys_admin_perms, f"System admin missing {value}"

    def test_unknown_role_returns_empty_set(self):
        assert get_role_permissions("NONEXISTENT_ROLE") == frozenset()

    def test_nurse_cannot_approve_ai_recommendations(self):
        perms = get_role_permissions(Roles.NURSE)
        assert Permissions.AI_RECOMMENDATIONS_APPROVE not in perms

    def test_lab_tech_has_laboratory_write(self):
        perms = get_role_permissions(Roles.LAB_TECHNICIAN)
        assert Permissions.LABORATORY_WRITE in perms

    def test_pharmacist_has_inventory_write(self):
        perms = get_role_permissions(Roles.PHARMACIST)
        assert Permissions.INVENTORY_WRITE in perms

    def test_emergency_operator_has_emergency_write(self):
        perms = get_role_permissions(Roles.EMERGENCY_OPERATOR)
        assert Permissions.EMERGENCY_WRITE in perms

    def test_doctor_cannot_delete_patients(self):
        perms = get_role_permissions(Roles.DOCTOR)
        assert Permissions.PATIENTS_DELETE not in perms

    def test_role_permissions_are_frozenset(self):
        perms = get_role_permissions(Roles.DOCTOR)
        assert isinstance(perms, frozenset)


# ── require_permission() dependency tests ────────────────────────────────────


def _make_request_with_user(payload: TokenPayload | None) -> MagicMock:
    """Build a mock Request with the given user in state."""
    request = MagicMock()
    request.state.user = payload
    return request


class TestRequirePermission:
    @pytest.mark.asyncio
    async def test_passes_when_user_has_permission(self):
        payload = TokenPayload(
            sub=str(uuid4()),
            role=Roles.DOCTOR,
            hospital_id=str(uuid4()),
            permissions=["patients:read"],
        )
        request = _make_request_with_user(payload)
        dep = require_permission(Permissions.PATIENTS_READ)
        # Should not raise
        await dep(request)

    @pytest.mark.asyncio
    async def test_raises_when_user_lacks_permission(self):
        payload = TokenPayload(
            sub=str(uuid4()),
            role=Roles.LAB_TECHNICIAN,
            hospital_id=str(uuid4()),
            permissions=["laboratory:read"],
        )
        request = _make_request_with_user(payload)
        dep = require_permission(Permissions.PATIENTS_WRITE)

        with pytest.raises(PermissionDeniedError) as exc_info:
            await dep(request)

        assert exc_info.value.required_permission == Permissions.PATIENTS_WRITE

    @pytest.mark.asyncio
    async def test_raises_when_user_is_none(self):
        request = _make_request_with_user(None)
        dep = require_permission(Permissions.PATIENTS_READ)

        with pytest.raises(PermissionDeniedError):
            await dep(request)

    @pytest.mark.asyncio
    async def test_system_admin_passes_any_permission(self):
        payload = TokenPayload(
            sub=str(uuid4()),
            role=Roles.SYSTEM_ADMIN,
            hospital_id=str(uuid4()),
            permissions=list(get_role_permissions(Roles.SYSTEM_ADMIN)),
        )
        request = _make_request_with_user(payload)

        for attr in dir(Permissions):
            if not attr.startswith("_"):
                perm = getattr(Permissions, attr)
                if isinstance(perm, str):
                    dep = require_permission(perm)
                    await dep(request)  # Should not raise for any permission
