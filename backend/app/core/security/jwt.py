"""JWT Authentication utilities.

Handles generation and validation of RS256 JWT tokens.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError

from app.config import get_settings

settings = get_settings()

def create_access_token(subject: str | uuid.UUID, role: str, hospital_id: str | uuid.UUID, permissions: list[str]) -> str:
    """Create a new short-lived access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "role": role,
        "hospital_id": str(hospital_id),
        "permissions": permissions,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_PRIVATE_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(subject: str | uuid.UUID) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_PRIVATE_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a token using the public key."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
