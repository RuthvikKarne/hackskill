"""Unit tests for the HRIP exception hierarchy and HTTP response mapping.

Tests cover:
    - Exception class attributes (http_status, error_code, message)
    - Exception specialisation (subclass relationships)
    - Error response builder correctness
    - Pydantic validation error handler
    - Unhandled exception handler (no traceback leak)
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions.base import (
    AuthenticationError,
    BusinessRuleViolation,
    ConflictError,
    ExternalServiceError,
    HRIPException,
    HospitalAccessDeniedError,
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitExceededError,
    TokenExpiredError,
    ValidationError,
)
from app.core.exceptions.handlers import register_exception_handlers


# ── Exception hierarchy tests ─────────────────────────────────────────────────


class TestExceptionHierarchy:
    def test_hrip_exception_is_base_exception(self):
        exc = HRIPException("test")
        assert isinstance(exc, Exception)

    def test_not_found_is_hrip_exception(self):
        assert issubclass(NotFoundError, HRIPException)

    def test_permission_denied_is_hrip_exception(self):
        assert issubclass(PermissionDeniedError, HRIPException)

    def test_token_expired_is_authentication_error(self):
        assert issubclass(TokenExpiredError, AuthenticationError)

    def test_invalid_token_is_authentication_error(self):
        assert issubclass(InvalidTokenError, AuthenticationError)

    def test_hospital_access_denied_is_permission_denied(self):
        assert issubclass(HospitalAccessDeniedError, PermissionDeniedError)


class TestExceptionAttributes:
    def test_not_found_default_status(self):
        exc = NotFoundError("Patient")
        assert exc.http_status == 404

    def test_not_found_with_id(self):
        from uuid import uuid4
        uid = uuid4()
        exc = NotFoundError("Patient", uid)
        assert "Patient" in exc.message
        assert str(uid) in exc.message

    def test_validation_error_carries_fields(self):
        exc = ValidationError("Bad input", fields={"email": "invalid"})
        assert exc.http_status == 400
        assert exc.fields["email"] == "invalid"

    def test_conflict_error_status(self):
        exc = ConflictError("User", field="email", value="test@example.com")
        assert exc.http_status == 409
        assert "email" in exc.message

    def test_permission_denied_carries_permission(self):
        exc = PermissionDeniedError("patients:read")
        assert exc.required_permission == "patients:read"
        assert exc.http_status == 403

    def test_external_service_error(self):
        exc = ExternalServiceError("Redis", reason="connection refused")
        assert exc.http_status == 503
        assert "Redis" in exc.message

    def test_rate_limit_error(self):
        exc = RateLimitExceededError()
        assert exc.http_status == 429

    def test_business_rule_violation(self):
        exc = BusinessRuleViolation("Bed already occupied", rule_code="bed.occupied")
        assert exc.http_status == 422
        assert exc.rule_code == "bed.occupied"

    def test_token_expired_status(self):
        exc = TokenExpiredError()
        assert exc.http_status == 401
        assert exc.error_code == "token_expired"

    def test_custom_error_code_override(self):
        exc = HRIPException("custom", error_code="my.custom_code")
        assert exc.error_code == "my.custom_code"


# ── HTTP response integration tests ───────────────────────────────────────────


def _make_test_app() -> FastAPI:
    """Build a minimal FastAPI app that raises HRIP exceptions for testing."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    async def raise_not_found():
        raise NotFoundError("Patient", "abc-123")

    @app.get("/permission-denied")
    async def raise_permission():
        raise PermissionDeniedError("patients:write")

    @app.get("/conflict")
    async def raise_conflict():
        raise ConflictError("User", field="email", value="dup@test.com")

    @app.get("/unhandled")
    async def raise_unhandled():
        raise RuntimeError("unexpected boom")

    @app.get("/validation")
    async def raise_validation():
        raise ValidationError("Bad data", fields={"name": "required"})

    return app


@pytest.fixture(scope="module")
def test_client():
    app = _make_test_app()
    return TestClient(app, raise_server_exceptions=False)


class TestExceptionHandlerResponses:
    def test_not_found_returns_404(self, test_client):
        resp = test_client.get("/not-found")
        assert resp.status_code == 404
        body = resp.json()
        assert body["success"] is False
        assert "Patient" in body["message"]
        assert body["meta"]["error_code"] == "patient.not_found"

    def test_permission_denied_returns_403(self, test_client):
        resp = test_client.get("/permission-denied")
        assert resp.status_code == 403
        body = resp.json()
        assert body["success"] is False
        assert body["meta"]["error_code"] == "permission_denied"

    def test_conflict_returns_409(self, test_client):
        resp = test_client.get("/conflict")
        assert resp.status_code == 409

    def test_unhandled_returns_500_without_traceback(self, test_client):
        resp = test_client.get("/unhandled")
        assert resp.status_code == 500
        body = resp.json()
        assert body["success"] is False
        # Traceback must not appear in the response body
        assert "RuntimeError" not in str(body)
        assert "Traceback" not in str(body)
        assert "unexpected boom" not in str(body)

    def test_validation_error_returns_400(self, test_client):
        resp = test_client.get("/validation")
        assert resp.status_code == 400

    def test_response_has_standard_meta(self, test_client):
        resp = test_client.get("/not-found")
        body = resp.json()
        assert "request_id" in body["meta"]
        assert "timestamp" in body["meta"]
        assert "version" in body["meta"]

    def test_success_false_on_error(self, test_client):
        for path in ("/not-found", "/permission-denied", "/conflict", "/unhandled"):
            resp = test_client.get(path)
            assert resp.json()["success"] is False, f"Failed for {path}"
