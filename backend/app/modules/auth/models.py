"""Authentication database models.

Includes User, Role, and Permission models for RBAC.
"""
import uuid
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import BaseModel, Base

# Association table for Many-to-Many relationship between Role and Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)

class Permission(BaseModel):
    """System permissions for fine-grained access control."""
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )


class Role(BaseModel):
    """User roles that group multiple permissions together."""
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permissions, back_populates="roles", lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(BaseModel):
    """System users (Admin, Doctors, Nurses, etc.)."""
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Foreign Keys
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users", lazy="selectin")
