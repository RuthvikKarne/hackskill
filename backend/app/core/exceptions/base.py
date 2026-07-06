"""HRIP exception hierarchy.

All application exceptions inherit from HRIPException. This gives us:
1. A single catch-all in the global exception handler.
2. Typed exceptions that carry HTTP status codes and error codes.
3. Consistent error structure across every module.

Module code raises typed exceptions; the handler in handlers.py converts
them to the standard response envelope.

Usage:
    from app.core.exceptions.base import NotFoundError

    raise NotFoundError(
        resource="Patient",
        resource_id=str(patient_id),
    )
"""
from __future__ import annotations

from typing import Any
from uuid import UUID


class HRIPException(Exception):
    """Root exception for all HRIP application errors.

    Args:
        message: Human-readable description (shown to callers).
        error_code: Machine-readable code (e.g. "patient.not_found").
        http_status: HTTP response status code.
        detail: Optional extra structured context (not shown in production).
    """

    http_status: int = 500
    default_message: str = "An unexpected error occurred."
    default_error_code: str = "internal_error"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        http_status: int | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.error_code = error_code or self.default_error_code
        self.http_status = http_status or self.__class__.http_status
        self.detail = detail or {}
        super().__init__(self.message)


# ── 400 Bad Request ───────────────────────────────────────────────────────────


class ValidationError(HRIPException):
    """Input validation failed — missing or invalid fields.

    Args:
        message: Summary of what failed.
        fields: Field-level error map, e.g. {"email": "invalid format"}.
    """

    http_status = 400
    default_error_code = "validation_error"
    default_message = "Input validation failed."

    def __init__(
        self,
        message: str | None = None,
        *,
        fields: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, detail={"fields": fields or {}})
        self.fields = fields or {}


class BusinessRuleViolation(HRIPException):
    """A business rule was violated (e.g. bed already occupied).

    Args:
        message: Description of the rule that was violated.
        rule_code: Machine-readable rule identifier.
    """

    http_status = 422
    default_error_code = "business_rule_violation"
    default_message = "A business rule was violated."

    def __init__(self, message: str, *, rule_code: str | None = None) -> None:
        super().__init__(message, detail={"rule_code": rule_code})
        self.rule_code = rule_code


# ── 401 Unauthorized ──────────────────────────────────────────────────────────


class AuthenticationError(HRIPException):
    """Request lacks valid credentials or the token is invalid/expired.

    Args:
        message: Human-readable reason.
    """

    http_status = 401
    default_error_code = "authentication_error"
    default_message = "Authentication required."


class TokenExpiredError(AuthenticationError):
    """JWT access token has expired — client should refresh."""

    default_error_code = "token_expired"
    default_message = "Access token has expired."


class InvalidTokenError(AuthenticationError):
    """JWT signature is invalid, malformed, or the algorithm is wrong."""

    default_error_code = "invalid_token"
    default_message = "The provided token is invalid."


# ── 403 Forbidden ─────────────────────────────────────────────────────────────


class PermissionDeniedError(HRIPException):
    """Authenticated user lacks the required permission.

    Args:
        required_permission: The permission string that was missing
            (e.g. "patients:write").
    """

    http_status = 403
    default_error_code = "permission_denied"
    default_message = "You do not have permission to perform this action."

    def __init__(self, required_permission: str | None = None) -> None:
        detail = {"required_permission": required_permission} if required_permission else {}
        super().__init__(detail=detail)
        self.required_permission = required_permission


class HospitalAccessDeniedError(PermissionDeniedError):
    """User is trying to access a resource from a different hospital."""

    default_error_code = "hospital_access_denied"
    default_message = "You cannot access resources from another hospital."


# ── 404 Not Found ─────────────────────────────────────────────────────────────


class NotFoundError(HRIPException):
    """Requested resource does not exist (or has been soft-deleted).

    Args:
        resource: Resource type name (e.g. "Patient", "Medicine").
        resource_id: ID that was looked up.
    """

    http_status = 404
    default_error_code = "not_found"
    default_message = "The requested resource was not found."

    def __init__(
        self,
        resource: str | None = None,
        resource_id: str | UUID | None = None,
    ) -> None:
        if resource and resource_id:
            message = f"{resource} with id '{resource_id}' was not found."
        elif resource:
            message = f"{resource} was not found."
        else:
            message = self.default_message

        super().__init__(
            message,
            error_code=f"{resource.lower()}.not_found" if resource else self.default_error_code,
            detail={"resource": resource, "resource_id": str(resource_id) if resource_id else None},
        )


# ── 409 Conflict ─────────────────────────────────────────────────────────────


class ConflictError(HRIPException):
    """Resource already exists or a unique constraint would be violated.

    Args:
        resource: Resource type name.
        field: The field that caused the conflict (e.g. "email").
        value: The conflicting value.
    """

    http_status = 409
    default_error_code = "conflict"
    default_message = "A resource with those details already exists."

    def __init__(
        self,
        resource: str | None = None,
        *,
        field: str | None = None,
        value: str | None = None,
    ) -> None:
        if resource and field:
            message = f"{resource} with {field}='{value}' already exists."
        else:
            message = self.default_message

        super().__init__(
            message,
            error_code=f"{resource.lower()}.conflict" if resource else self.default_error_code,
            detail={"resource": resource, "field": field, "value": value},
        )


# ── 429 Too Many Requests ─────────────────────────────────────────────────────


class RateLimitExceededError(HRIPException):
    """Request rate limit exceeded."""

    http_status = 429
    default_error_code = "rate_limit_exceeded"
    default_message = "Too many requests. Please try again later."


# ── 503 Service Unavailable ───────────────────────────────────────────────────


class ExternalServiceError(HRIPException):
    """A required external service (DB, Redis, AI Engine) is unavailable.

    Args:
        service: Name of the failing service.
        reason: Technical reason (logged, not returned to caller).
    """

    http_status = 503
    default_error_code = "external_service_error"
    default_message = "A required service is temporarily unavailable."

    def __init__(self, service: str, *, reason: str | None = None) -> None:
        super().__init__(
            f"Service '{service}' is unavailable.",
            detail={"service": service, "reason": reason},
        )
        self.service = service
