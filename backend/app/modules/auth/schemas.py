"""Authentication Schemas.

Pydantic models for authentication requests and responses.
"""
import uuid
from typing import List
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User plaintext password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    # refresh_token will be stored in an HttpOnly cookie


class UserBase(BaseModel):
    """Base user schema."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    hospital_id: uuid.UUID


class UserMeResponse(UserBase):
    """Schema for current user details including permissions."""
    role: str
    permissions: List[str]
    
    class Config:
        from_attributes = True
