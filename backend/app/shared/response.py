<<<<<<< HEAD
"""Standard response envelope for all HRIP API responses.

Every router returns either success_response() or error_response().
No router returns a raw dict — this ensures a consistent shape for all
API consumers regardless of which module or operation is called.

Success envelope:
    {
        "success": true,
        "message": "Patient registered successfully.",
        "data": { ... },
        "errors": null,
        "meta": {
            "request_id": "uuid",
            "timestamp": "2026-07-03T08:00:00Z",
            "version": "1.0"
        }
    }

Error envelope (built by exception handlers, not routers):
    {
        "success": false,
        "message": "Patient not found.",
        "data": null,
        "errors": { "field": "error detail" },
        "meta": {
            "request_id": "uuid",
            "timestamp": "...",
            "version": "1.0",
            "error_code": "patient.not_found"
        }
    }

Usage in a router:
    from app.shared.response import success_response

    return success_response(
        data=patient.model_dump(),
        message="Patient registered successfully.",
        request=request,
    )
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

API_VERSION = "1.0"


def _build_meta(request: Request | None = None, *, error_code: str | None = None) -> dict:
    """Build the standard 'meta' block.

    Args:
        request: FastAPI request object (used to extract request_id).
        error_code: Optional machine-readable error code for error responses.

    Returns:
        Dict containing request_id, timestamp, and version.
    """
    request_id = "unknown"
    if request is not None:
        request_id = getattr(request.state, "request_id", "unknown")

    meta: dict[str, Any] = {
        "request_id": request_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "version": API_VERSION,
    }
    if error_code:
        meta["error_code"] = error_code

    return meta


def success_response(
    *,
    data: Any = None,
    message: str = "Success.",
    request: Request | None = None,
    status_code: int = 200,
) -> JSONResponse:
    """Build and return a standard success envelope.

    Args:
        data: The response payload (dict, list, or primitive).
        message: Human-readable success message.
        request: FastAPI request (for request_id extraction).
        status_code: HTTP status code. Default 200.

    Returns:
        JSONResponse with the standard success envelope.

    Example:
        return success_response(
            data={"id": str(patient.id)},
            message="Patient registered successfully.",
            request=request,
            status_code=201,
        )
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
            "meta": _build_meta(request),
        },
    )


def created_response(
    *,
    data: Any = None,
    message: str = "Resource created successfully.",
    request: Request | None = None,
) -> JSONResponse:
    """Convenience wrapper for 201 Created responses.

    Args:
        data: The newly created resource.
        message: Human-readable success message.
        request: FastAPI request (for request_id).

    Returns:
        JSONResponse with status 201.
    """
    return success_response(data=data, message=message, request=request, status_code=201)


def no_content_response() -> JSONResponse:
    """Return a 204 No Content response for DELETE operations.

    Returns:
        JSONResponse with status 204 and empty body.
    """
    return JSONResponse(status_code=204, content=None)


def paginated_response(
    *,
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Records retrieved successfully.",
    request: Request | None = None,
) -> JSONResponse:
    """Build a standard paginated success envelope.

    Args:
        items: The page of results.
        total: Total number of records matching the query.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
        message: Human-readable success message.
        request: FastAPI request (for request_id).

    Returns:
        JSONResponse with pagination metadata embedded in 'meta'.
    """
    meta = _build_meta(request)
    meta["pagination"] = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, -(-total // page_size)),  # Ceiling division
        "has_next": (page * page_size) < total,
        "has_prev": page > 1,
    }

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": items,
            "errors": None,
            "meta": meta,
        },
=======
"""Standard API response wrappers.

All API endpoints must return a standardized response envelope.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.config import get_settings

settings = get_settings()

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata included in every API response."""
    request_id: str = Field(description="Unique request identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the response was generated"
    )
    version: str = Field(
        default_factory=lambda: settings.APP_VERSION,
        description="API version"
    )


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool
    message: str
    data: T | None = None
    meta: ResponseMeta


def success_response(
    data: T | None = None, 
    message: str = "Operation successful",
    request_id: str | None = None
) -> APIResponse[T]:
    """Helper to construct a successful API response."""
    return APIResponse(
        success=True,
        message=message,
        data=data,
        meta=ResponseMeta(request_id=request_id or str(uuid.uuid4()))
    )


def error_response(
    message: str,
    request_id: str | None = None
) -> APIResponse[None]:
    """Helper to construct an error API response."""
    return APIResponse(
        success=False,
        message=message,
        data=None,
        meta=ResponseMeta(request_id=request_id or str(uuid.uuid4()))
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
    )
