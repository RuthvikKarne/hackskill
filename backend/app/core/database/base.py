<<<<<<< HEAD
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
=======
"""Base database classes and repositories.

Provides the SQLAlchemy declarative base and the abstract BaseRepository.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import DateTime, Integer, Select, Uuid, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class BaseModel(Base):
    """Abstract base model with standard mandatory columns.
    
    All business entity models should inherit from this class.
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hospital_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    
    # Audit tracking
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    
    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Optimistic locking configuration
    __mapper_args__ = {
        "version_id_col": version,
    }


ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base generic repository for basic CRUD operations.
    
    Attributes:
        model: The SQLAlchemy model class this repository manages.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Initialize the repository with a model class and DB session.
        
        Args:
            model: The SQLAlchemy declarative model class.
            session: The SQLAlchemy async session.
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Retrieve a single active record by its ID.
        
        Ignores soft-deleted records.
        """
        stmt = select(self.model).where(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Retrieve multiple active records for a given hospital.
        
        Ignores soft-deleted records.
        """
        stmt = (
            select(self.model)
            .where(
                self.model.hospital_id == hospital_id,
                self.model.deleted_at.is_(None)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new record and flush it to the database."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: uuid.UUID, **kwargs: Any) -> ModelType | None:
        """Update an existing record."""
        obj = await self.get_by_id(id)
        if not obj:
            return None
        
        for key, value in kwargs.items():
            setattr(obj, key, value)
            
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def soft_delete(self, id: uuid.UUID) -> bool:
        """Soft delete a record by setting deleted_at."""
        stmt = (
            update(self.model)
            .where(self.model.id == id, self.model.deleted_at.is_(None))
            .values(deleted_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, id: uuid.UUID) -> bool:
        """Check if an active record exists by ID."""
        stmt = select(self.model.id).where(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
