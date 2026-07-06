"""JWT utilities — RS256 token creation and validation.

Change 1 (approved): Supports BOTH Bearer JWT and HttpOnly cookies.
The token extraction logic lives here in one place. The middleware and
the get_current_user() dependency both call extract_token_from_request()
and get the same TokenPayload regardless of how the token arrived.

Token strategy:
    Access token:  JWT signed with RS256 private key, 15-minute lifetime.
    Refresh token: Opaque UUID4, stored in Redis, 7-day lifetime.
                   Refresh token logic is in the auth module (Phase 2).

JWT payload (claims):
    sub:          User UUID (string)
    role:         Role name (e.g. "HOSPITAL_ADMIN")
    hospital_id:  Hospital UUID (string)
    district_id:  District UUID (string, may be None)
    permissions:  List of permission strings (e.g. ["patients:read"])
    exp:          Expiry timestamp (Unix)
    iat:          Issued-at timestamp (Unix)
    jti:          JWT ID (UUID4, for blocklist checks)

Usage:
    from app.core.security.jwt import create_access_token, decode_token

    token = create_access_token(payload=TokenPayload(...))
    claims = decode_token(token)
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from pydantic import BaseModel

from app.core.exceptions.base import InvalidTokenError, TokenExpiredError
from app.core.logging.logger import get_logger

log = get_logger(__name__)

# Cookie name for the access token (HttpOnly, Secure, SameSite=Strict)
ACCESS_TOKEN_COOKIE = "hrip_access_token"
# Cookie name for the refresh token
REFRESH_TOKEN_COOKIE = "hrip_refresh_token"


# ── Token payload schema ──────────────────────────────────────────────────────


class TokenPayload(BaseModel):
    """Typed representation of the JWT claims carried in every request.

    This is injected into request.state.user by JWTAuthMiddleware.

    Attributes:
        sub:          User UUID as string.
        role:         Role name.
        hospital_id:  Hospital UUID as string.
        district_id:  District UUID (or None for system admin).
        permissions:  List of permission strings.
        jti:          JWT ID for blocklist checks.
        exp:          Expiry as Unix timestamp.
        iat:          Issued-at as Unix timestamp.
    """

    sub: str
    role: str
    hospital_id: str
    district_id: str | None = None
    permissions: list[str] = []
    jti: str = ""
    exp: int = 0
    iat: int = 0

    @property
    def user_id(self) -> UUID:
        """Convenience accessor — sub as UUID."""
        return UUID(self.sub)

    @property
    def hospital_uuid(self) -> UUID:
        """Convenience accessor — hospital_id as UUID."""
        return UUID(self.hospital_id)

    def has_permission(self, permission: str) -> bool:
        """Check if the token carries a specific permission.

        Args:
            permission: Permission string, e.g. "patients:write".

        Returns:
            True if the permission is present in the token claims.
        """
        return permission in self.permissions


# ── Token creation ────────────────────────────────────────────────────────────


def create_access_token(
    payload: TokenPayload,
    *,
    private_key: str,
    expire_minutes: int = 15,
    algorithm: str = "RS256",
) -> str:
    """Sign and return a new JWT access token.

    Args:
        payload: The claims to encode in the token.
        private_key: PEM-encoded RSA private key from Settings.
        expire_minutes: Token lifetime in minutes. Defaults to 15.
        algorithm: JWT signing algorithm. Must be RS256 in production.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(UTC)
    jti = str(uuid4())

    claims: dict[str, Any] = {
        "sub": payload.sub,
        "role": payload.role,
        "hospital_id": payload.hospital_id,
        "district_id": payload.district_id,
        "permissions": payload.permissions,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expire_minutes)).timestamp()),
    }

    token = jwt.encode(claims, private_key, algorithm=algorithm)
    log.debug("access_token_created", sub=payload.sub, jti=jti, exp=claims["exp"])
    return token


def create_refresh_token() -> str:
    """Generate an opaque refresh token (UUID4).

    The refresh token is stored in Redis (Phase 2), NOT embedded in the JWT.
    The JWT is only used for access tokens.

    Returns:
        A random UUID4 string suitable for use as a refresh token.
    """
    return str(uuid4())


# ── Token decoding ────────────────────────────────────────────────────────────


def decode_token(
    token: str,
    *,
    public_key: str,
    algorithm: str = "RS256",
) -> TokenPayload:
    """Validate and decode a JWT access token.

    Args:
        token: The raw JWT string.
        public_key: PEM-encoded RSA public key from Settings.
        algorithm: JWT algorithm. Must match the signing algorithm.

    Returns:
        A TokenPayload with all decoded claims.

    Raises:
        TokenExpiredError: If the token has passed its expiry time.
        InvalidTokenError: If the signature is wrong, the token is malformed,
            or the algorithm does not match.
    """
    try:
        claims = jwt.decode(token, public_key, algorithms=[algorithm])
        return TokenPayload(**claims)
    except ExpiredSignatureError:
        log.warning("token_expired")
        raise TokenExpiredError()
    except JWTError as exc:
        log.warning("token_invalid", error=str(exc))
        raise InvalidTokenError() from exc


# ── Token extraction (Change 1 — dual Bearer + Cookie support) ───────────────


def extract_token_from_request(request: Any) -> str | None:
    """Extract the JWT string from the request — Bearer header OR cookie.

    This is the SINGLE extraction point used by both the middleware and
    the get_current_user() dependency. The logic is:

        1. Try Authorization: Bearer <token>  ← API clients, mobile apps, CI
        2. Fall back to hrip_access_token cookie ← Browser frontend

    Neither path is preferred — both are equally valid. The authentication
    logic (decode_token) is identical regardless of the source.

    Args:
        request: The Starlette/FastAPI Request object.

    Returns:
        The raw JWT string if found via either mechanism, or None if the
        request is unauthenticated (public route).
    """
    # 1. Bearer token from Authorization header
    auth_header: str | None = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            log.debug("token_source", source="bearer_header")
            return token

    # 2. HttpOnly cookie (browser frontend)
    cookie_token: str | None = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if cookie_token:
        log.debug("token_source", source="httponly_cookie")
        return cookie_token

    return None
