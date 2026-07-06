<<<<<<< HEAD
"""Unit tests for JWT utilities.

Tests cover:
    - Access token creation and decode round-trip (RS256)
    - TokenExpiredError raised on expired tokens
    - InvalidTokenError raised on tampered/wrong-key tokens
    - extract_token_from_request — Bearer header extraction
    - extract_token_from_request — Cookie extraction fallback
    - extract_token_from_request — returns None when no token present
    - Bearer takes precedence over cookie when both present
"""
from __future__ import annotations

import time
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.exceptions.base import InvalidTokenError, TokenExpiredError
from app.core.security.jwt import (
    ACCESS_TOKEN_COOKIE,
    TokenPayload,
    create_access_token,
    decode_token,
    extract_token_from_request,
)


# ── RSA key pair fixture (generated once per session) ────────────────────────


@pytest.fixture(scope="session")
def rsa_key_pair():
    """Generate a 2048-bit RSA key pair for test token signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return private_pem, public_pem


@pytest.fixture(scope="session")
def sample_payload():
    """A realistic TokenPayload for test token creation."""
    return TokenPayload(
        sub=str(uuid4()),
        role="HOSPITAL_ADMIN",
        hospital_id=str(uuid4()),
        district_id=str(uuid4()),
        permissions=["patients:read", "beds:write"],
        jti=str(uuid4()),
    )


# ── Token creation + decode ───────────────────────────────────────────────────


class TestJWTRoundTrip:
    def test_create_and_decode_access_token(self, rsa_key_pair, sample_payload):
        private_key, public_key = rsa_key_pair
        token = create_access_token(
            sample_payload,
            private_key=private_key,
            expire_minutes=15,
        )
        decoded = decode_token(token, public_key=public_key)

        assert decoded.sub == sample_payload.sub
        assert decoded.role == sample_payload.role
        assert decoded.hospital_id == sample_payload.hospital_id
        assert set(decoded.permissions) == set(sample_payload.permissions)

    def test_decoded_token_has_expiry(self, rsa_key_pair, sample_payload):
        private_key, public_key = rsa_key_pair
        token = create_access_token(sample_payload, private_key=private_key, expire_minutes=15)
        decoded = decode_token(token, public_key=public_key)
        assert decoded.exp > int(time.time())

    def test_token_payload_user_id_property(self, rsa_key_pair, sample_payload):
        private_key, public_key = rsa_key_pair
        token = create_access_token(sample_payload, private_key=private_key)
        decoded = decode_token(token, public_key=public_key)
        assert str(decoded.user_id) == sample_payload.sub

    def test_token_payload_has_permission(self, rsa_key_pair, sample_payload):
        private_key, public_key = rsa_key_pair
        token = create_access_token(sample_payload, private_key=private_key)
        decoded = decode_token(token, public_key=public_key)
        assert decoded.has_permission("patients:read") is True
        assert decoded.has_permission("inventory:write") is False


class TestJWTExpiry:
    def test_expired_token_raises_token_expired_error(self, rsa_key_pair, sample_payload):
        private_key, public_key = rsa_key_pair
        # expire_minutes=0 → token expires immediately
        token = create_access_token(
            sample_payload,
            private_key=private_key,
            expire_minutes=-1,  # Already expired
        )
        with pytest.raises(TokenExpiredError):
            decode_token(token, public_key=public_key)


class TestJWTInvalidToken:
    def test_wrong_key_raises_invalid_token_error(self, rsa_key_pair, sample_payload):
        private_key, _ = rsa_key_pair
        token = create_access_token(sample_payload, private_key=private_key)

        # Generate a different key pair — decoding with wrong public key must fail
        wrong_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        wrong_public = wrong_private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        with pytest.raises(InvalidTokenError):
            decode_token(token, public_key=wrong_public)

    def test_malformed_token_raises_invalid_token_error(self, rsa_key_pair):
        _, public_key = rsa_key_pair
        with pytest.raises(InvalidTokenError):
            decode_token("not.a.valid.jwt", public_key=public_key)

    def test_empty_token_raises_invalid_token_error(self, rsa_key_pair):
        _, public_key = rsa_key_pair
        with pytest.raises(InvalidTokenError):
            decode_token("", public_key=public_key)


# ── Token extraction (Change 1 — dual Bearer + Cookie) ───────────────────────


def _mock_request(*, auth_header: str | None = None, cookie: str | None = None):
    """Build a minimal mock Request for extraction tests."""
    request = MagicMock()
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    request.headers.get = lambda key, default=None: headers.get(key, default)
    request.cookies.get = lambda key, default=None: cookie if key == ACCESS_TOKEN_COOKIE else default
    return request


class TestTokenExtraction:
    def test_bearer_header_extracted(self):
        request = _mock_request(auth_header="Bearer my.jwt.token")
        assert extract_token_from_request(request) == "my.jwt.token"

    def test_cookie_extracted_when_no_header(self):
        request = _mock_request(cookie="my.cookie.token")
        assert extract_token_from_request(request) == "my.cookie.token"

    def test_bearer_takes_precedence_over_cookie(self):
        """Bearer header must win when both are present."""
        request = _mock_request(
            auth_header="Bearer header.token",
            cookie="cookie.token",
        )
        assert extract_token_from_request(request) == "header.token"

    def test_returns_none_when_no_token(self):
        request = _mock_request()
        assert extract_token_from_request(request) is None

    def test_bearer_prefix_without_token_falls_back_to_cookie(self):
        """'Bearer ' with no token should fall back to cookie."""
        request = _mock_request(auth_header="Bearer ", cookie="cookie.token")
        assert extract_token_from_request(request) == "cookie.token"

    def test_non_bearer_header_not_extracted(self):
        request = _mock_request(auth_header="Basic dXNlcjpwYXNz")
        assert extract_token_from_request(request) is None
=======
import uuid
import pytest
from jose import jwt, JWTError
from app.core.security.jwt import create_access_token, create_refresh_token, decode_token
from app.config import get_settings

settings = get_settings()

def test_create_access_token():
    user_id = str(uuid.uuid4())
    hospital_id = str(uuid.uuid4())
    token = create_access_token(
        subject=user_id,
        role="HOSPITAL_ADMIN",
        hospital_id=hospital_id,
        permissions=["patients:read"]
    )
    assert isinstance(token, str)
    
    # decode and verify
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "HOSPITAL_ADMIN"
    assert payload["hospital_id"] == hospital_id
    assert "patients:read" in payload["permissions"]
    assert "exp" in payload
    assert "iat" in payload

def test_create_refresh_token():
    user_id = str(uuid.uuid4())
    token = create_refresh_token(subject=user_id)
    assert isinstance(token, str)
    
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_decode_invalid_token():
    with pytest.raises(ValueError):
        decode_token("invalid.token.string")
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
