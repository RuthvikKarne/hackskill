"""Abstract BaseRepository — the contract every module repository must satisfy.

Design decision (approved):
    BaseRepository is a PURE ABSTRACT BASE — it defines the interface but
    contains NO concrete SQL logic. Each module owns its own repository:

        BaseRepository  (this file — contract only)
              ↑
        PatientRepository   (backend/app/modules/patients/repository.py)
        HospitalRepository  (backend/app/modules/hospitals/repository.py)
        InventoryRepository (backend/app/modules/inventory/repository.py)
        ...

This ensures:
    - No single file becomes a "god repository" stuffed with all modules.
    - Each repository can override only the methods it needs.
    - Cross-module queries are impossible by design (modules don't import
      each other's repositories — they communicate via the Event Bus).
    - Concrete repositories can add module-specific query methods freely
      (e.g. PatientRepository.get_admitted_patients()).

Mandatory columns (enforced via HospitalScopedMixin):
    id, hospital_id, created_at, updated_at, deleted_at, created_by, version

Usage — implementing a concrete repository:

    from uuid import UUID
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database.base import BaseRepository
    from app.modules.patients.models import Patient

    class PatientRepository(BaseRepository[Patient]):
        def __init__(self, session: AsyncSession) -> None:
            super().__init__(session, Patient)

        async def get_admitted(self, hospital_id: UUID) -> list[Patient]:
            # Module-specific query — not possible in a generic base
            result = await self._session.execute(
                select(Patient).where(
                    Patient.hospital_id == hospital_id,
                    Patient.status == "admitted",
                    Patient.deleted_at.is_(None),
                )
            )
            return list(result.scalars().all())
"""
from __future__ import annotations

import abc
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

# T is bound to the concrete SQLAlchemy model for each repository
ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT], abc.ABC):
    """Abstract repository interface that all module repositories must implement.

    Provides a consistent async CRUD contract. Concrete repositories are
    injected with an AsyncSession per request via FastAPI's Depends() system.

    Type parameter:
        ModelT: The SQLAlchemy ORM model class this repository manages.

    Args:
        session: The request-scoped async session from get_db_session().
        model: The SQLAlchemy model class (passed by concrete __init__).
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    # ── Read operations ───────────────────────────────────────────────────────

    @abc.abstractmethod
    async def get_by_id(
        self,
        resource_id: UUID,
        *,
        hospital_id: UUID,
    ) -> ModelT | None:
        """Fetch a single record by primary key, scoped to the hospital.

        Args:
            resource_id: UUID primary key of the record.
            hospital_id: Must match the record's hospital_id (multi-tenancy).

        Returns:
            The model instance, or None if not found / belongs to a different
            hospital / has been soft-deleted.
        """

    @abc.abstractmethod
    async def get_all(
        self,
        *,
        hospital_id: UUID,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[ModelT], int]:
        """Fetch a paginated, filtered list of records for a hospital.

        Args:
            hospital_id: Scope all results to this hospital.
            filters: Key → value filter map (equality checks by default).
            page: 1-indexed page number.
            page_size: Number of records per page (max enforced by concrete).
            sort_by: Column name to sort by.
            sort_order: "asc" or "desc".

        Returns:
            A tuple of (list of model instances, total record count).
        """

    @abc.abstractmethod
    async def exists(self, resource_id: UUID, *, hospital_id: UUID) -> bool:
        """Check whether a record exists (and belongs to the hospital).

        Args:
            resource_id: UUID primary key.
            hospital_id: Hospital scope.

        Returns:
            True if the record exists, is active, and belongs to this hospital.
        """

    # ── Write operations ──────────────────────────────────────────────────────

    @abc.abstractmethod
    async def create(
        self,
        data: dict[str, Any],
        *,
        hospital_id: UUID,
        actor_id: UUID,
    ) -> ModelT:
        """Persist a new record.

        Args:
            data: Field values (excluding id, hospital_id, created_by,
                created_at, updated_at — these are set here).
            hospital_id: Multi-tenancy scope injected from JWT claims.
            actor_id: UUID of the user performing the action (audit trail).

        Returns:
            The newly created model instance.
        """

    @abc.abstractmethod
    async def update(
        self,
        resource_id: UUID,
        data: dict[str, Any],
        *,
        hospital_id: UUID,
        actor_id: UUID,
    ) -> ModelT:
        """Update an existing record.

        Args:
            resource_id: Primary key of the record to update.
            data: Fields to change. Unspecified fields are left unchanged.
            hospital_id: Multi-tenancy scope — raises if record belongs to
                a different hospital.
            actor_id: UUID of the actor (for audit trail + updated_by).

        Returns:
            The updated model instance.

        Raises:
            NotFoundError: If the record does not exist in this hospital.
        """

    @abc.abstractmethod
    async def soft_delete(
        self,
        resource_id: UUID,
        *,
        hospital_id: UUID,
        actor_id: UUID,
    ) -> bool:
        """Soft-delete a record by setting deleted_at = now().

        Clinical and audit records are NEVER hard-deleted.

        Args:
            resource_id: Primary key of the record.
            hospital_id: Multi-tenancy scope.
            actor_id: UUID of the actor performing the deletion.

        Returns:
            True if the record was found and soft-deleted, False otherwise.
        """

    # ── Convenience helper ────────────────────────────────────────────────────

    def _require_hospital_scope(
        self, record: ModelT, hospital_id: UUID
    ) -> None:
        """Raise HospitalAccessDeniedError if the record belongs to a different hospital.

        Concrete repositories call this after fetching a record by ID to
        ensure cross-hospital data leakage is impossible.

        Args:
            record: The fetched model instance.
            hospital_id: The hospital_id from the JWT claims.

        Raises:
            HospitalAccessDeniedError: If hospital IDs do not match.
        """
        from app.core.exceptions.base import HospitalAccessDeniedError

        record_hospital: UUID | None = getattr(record, "hospital_id", None)
        if record_hospital != hospital_id:
            raise HospitalAccessDeniedError()
