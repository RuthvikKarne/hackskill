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
