<<<<<<< HEAD
"""Pagination utilities for HRIP API endpoints.

Provides:
    PaginationParams — FastAPI dependency for extracting page/sort query params.
    PaginatedResult  — Typed container returned by repository.get_all().

Usage in a router:

    from app.shared.pagination import PaginationParams

    @router.get("/patients")
    async def list_patients(
        pagination: PaginationParams = Depends(),
        ...
    ):
        patients, total = await patient_repo.get_all(
            hospital_id=current_user.hospital_uuid,
            page=pagination.page,
            page_size=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )
        return paginated_response(
            items=[p.model_dump() for p in patients],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            request=request,
        )
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import Query

T = TypeVar("T")

# Hard cap on page size — prevents accidental full-table fetches
MAX_PAGE_SIZE = 100


class PaginationParams:
    """FastAPI dependency that extracts pagination and sort parameters from query string.

    Query parameters:
        page:       Page number (1-indexed). Default: 1.
        page_size:  Records per page. Default: 20, max: 100.
        sort_by:    Column to sort on. Default: "created_at".
        sort_order: "asc" or "desc". Default: "desc".

    Usage:
        async def list_patients(pagination: PaginationParams = Depends()):
            ...
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(
            default=20,
            ge=1,
            le=MAX_PAGE_SIZE,
            description=f"Records per page (max {MAX_PAGE_SIZE})",
        ),
        sort_by: str = Query(
            default="created_at",
            description="Column to sort by",
            max_length=64,
        ),
        sort_order: str = Query(
            default="desc",
            pattern="^(asc|desc)$",
            description="Sort direction: 'asc' or 'desc'",
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order

    @property
    def offset(self) -> int:
        """Calculate the SQL OFFSET value from page and page_size.

        Returns:
            Integer offset for use in repository queries.
        """
        return (self.page - 1) * self.page_size


@dataclass
class PaginatedResult(Generic[T]):
    """Typed container for a page of results from a repository.

    Type parameter:
        T: The model type (e.g. Patient, Medicine).

    Attributes:
        items:      The page of model instances.
        total:      Total record count matching the query (before pagination).
        page:       Current page number.
        page_size:  Number of items per page.
    """

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Total number of pages (ceiling division)."""
        return max(1, -(-self.total // self.page_size))

    @property
    def has_next(self) -> bool:
        """True if there are more pages after the current one."""
        return (self.page * self.page_size) < self.total

    @property
    def has_prev(self) -> bool:
        """True if the current page is not the first page."""
        return self.page > 1
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
