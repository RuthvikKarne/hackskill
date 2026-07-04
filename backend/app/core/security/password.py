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
