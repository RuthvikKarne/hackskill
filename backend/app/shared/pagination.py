"""Pagination utilities.

Provides standard generic schemas for paginated API responses.
"""
from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number (1-indexed)")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic envelope for paginated list endpoints."""
    items: Sequence[T]
    meta: PaginationMeta


def paginate(items: Sequence[T], total: int, page: int, size: int) -> PaginatedResponse[T]:
    """Helper to construct a PaginatedResponse.
    
    Args:
        items: The items for the current page.
        total: The total count of items.
        page: The current page (1-indexed).
        size: The requested page size.
        
    Returns:
        A PaginatedResponse object.
    """
    pages = (total + size - 1) // size if size > 0 else 0
    return PaginatedResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
    )
