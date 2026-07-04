"""Users Schemas.

Pydantic models for user CRUD operations.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    role_id: uuid.UUID
    # hospital_id is usually inferred from the creator's token, but we allow it for SYS_ADMIN
    hospital_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[uuid.UUID] = None


class UserResponse(BaseModel):
    """Schema for returning user details."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    role_id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
