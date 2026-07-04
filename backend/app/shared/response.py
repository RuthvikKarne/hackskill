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
    )
