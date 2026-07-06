"""Global exception handlers for FastAPI.

<<<<<<< HEAD
Registers handlers that convert HRIPException subclasses — and unexpected
Python exceptions — into the standard response envelope:

    {
        "success": false,
        "message": "...",
        "data": null,
        "meta": { "request_id": "...", "timestamp": "...", "version": "1.0" }
    }

Handlers are registered on the FastAPI app in main.py during startup.

Usage in main.py:
    from app.core.exceptions.handlers import register_exception_handlers
    register_exception_handlers(app)
"""
from __future__ import annotations

import traceback
from datetime import UTC, datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions.base import (
    AuthenticationError,
    BusinessRuleViolation,
    ConflictError,
    ExternalServiceError,
    HRIPException,
    NotFoundError,
    PermissionDeniedError,
    RateLimitExceededError,
    ValidationError,
)
from app.core.logging.logger import get_logger

log = get_logger(__name__)


# ── Response builder ──────────────────────────────────────────────────────────


def _error_response(
    request: Request,
    *,
    http_status: int,
    message: str,
    error_code: str,
    errors: dict | list | None = None,
) -> JSONResponse:
    """Build the standard error envelope.

    Args:
        request: Incoming FastAPI request (used to extract request_id).
        http_status: HTTP response status code.
        message: Human-readable error summary.
        error_code: Machine-readable error code.
        errors: Optional field-level or structured error detail.

    Returns:
        JSONResponse with the standard error envelope.
    """
    request_id: str = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=http_status,
        content={
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "1.0",
                "error_code": error_code,
            },
        },
    )


# ── HRIP application exception handler ───────────────────────────────────────


async def hrip_exception_handler(
    request: Request,
    exc: HRIPException,
) -> JSONResponse:
    """Handle all HRIPException subclasses.

    Logs at WARNING for client errors (4xx) and ERROR for server errors (5xx).
    """
    if exc.http_status >= 500:
        log.error(
            "server_error",
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
        )
    else:
        log.warning(
            "client_error",
            error_code=exc.error_code,
            message=exc.message,
            http_status=exc.http_status,
        )

    return _error_response(
        request,
        http_status=exc.http_status,
        message=exc.message,
        error_code=exc.error_code,
        errors=exc.detail if exc.detail else None,
    )


# ── Pydantic / FastAPI validation error handler ───────────────────────────────


async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle FastAPI/Pydantic request validation errors (422).

    Converts Pydantic's nested error list into a flat field → message map.
    """
    field_errors: dict[str, str] = {}
    for error in exc.errors():
        loc = " → ".join(str(part) for part in error["loc"] if part != "body")
        field_errors[loc or "request"] = error["msg"]

    log.warning("validation_error", field_errors=field_errors)

    return _error_response(
        request,
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed.",
        error_code="validation_error",
        errors=field_errors,
    )


# ── Catch-all unhandled exception handler ────────────────────────────────────


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch any unhandled exception and return 500 without leaking internals.

    The full traceback is logged but never returned to the caller.
    """
    log.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        traceback=traceback.format_exc(),
    )
    return _error_response(
        request,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
        error_code="internal_error",
    )


# ── Registration helper ───────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application.

    Call this once in main.py during app creation:
        register_exception_handlers(app)

    Args:
        app: The FastAPI application instance.
    """
    # Most-specific first — HRIPException subclasses
    app.add_exception_handler(
        HRIPException,
        hrip_exception_handler,  # type: ignore[arg-type]
    )
    # FastAPI/Pydantic validation errors
    app.add_exception_handler(
        RequestValidationError,
        request_validation_handler,  # type: ignore[arg-type]
    )
    # Catch-all safety net
    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,  # type: ignore[arg-type]
    )
=======
Catches unhandled exceptions and returns standardized APIResponse JSON.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

from app.shared.response import error_response

logger = structlog.get_logger(__name__)

def add_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers to the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handles Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", None)
        errors = exc.errors()
        error_msg = f"Validation Error: {errors}"
        logger.warning("request_validation_error", errors=errors)
        
        response = error_response(message=error_msg, request_id=request_id)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(mode='json'),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all for any unhandled exception."""
        request_id = getattr(request.state, "request_id", None)
        logger.exception("unhandled_exception", exc_info=exc)
        
        response = error_response(
            message="An unexpected internal server error occurred.", 
            request_id=request_id
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode='json'),
        )
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
