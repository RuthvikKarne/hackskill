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
