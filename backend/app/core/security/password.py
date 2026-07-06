<<<<<<< HEAD
"""Password hashing utilities using bcrypt.

All credential operations are centralised here so the hashing algorithm
can be swapped without touching any module code.

Never store plain-text passwords. Never log passwords or their hashes.

Usage:
    from app.core.security.password import hash_password, verify_password

    hashed = hash_password("user_plain_password")
    is_valid = verify_password("user_plain_password", hashed)
"""
from __future__ import annotations

from passlib.context import CryptContext

# bcrypt is the only allowed scheme. Deprecated schemes can be listed
# in 'deprecated' to auto-upgrade on next login (e.g. ["md5_crypt"]).
_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password with bcrypt.

    Args:
        plain_password: The user's raw password string.

    Returns:
        A bcrypt hash string safe to store in the database.

    Raises:
        ValueError: If plain_password is empty.
    """
    if not plain_password:
        raise ValueError("Password must not be empty.")
    return _crypt_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Uses a constant-time comparison internally to prevent timing attacks.

    Args:
        plain_password: The password submitted by the user.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return _crypt_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """Check if a stored hash should be upgraded (e.g. work factor increased).

    Call this after a successful verify_password(); if True, rehash and
    persist the new hash before returning the response.

    Args:
        hashed_password: The currently stored hash.

    Returns:
        True if the hash should be re-hashed with current settings.
    """
    return _crypt_context.needs_update(hashed_password)
=======
"""Password hashing utilities.

Uses passlib with bcrypt to securely hash and verify passwords.
"""
from passlib.context import CryptContext

# Set up the crypt context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hashed version.
    
    Args:
        plain_password: The plaintext password from the user.
        hashed_password: The hashed password from the database.
        
    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for a plaintext password.
    
    Args:
        password: The plaintext password to hash.
        
    Returns:
        The bcrypt hash string.
    """
    return pwd_context.hash(password)
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
