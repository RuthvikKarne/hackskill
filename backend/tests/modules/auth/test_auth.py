"""Tests for the auth module."""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test that login with bad credentials returns 401."""
    response = await client.post(
        "/api/v1/auth/login", 
        json={"email": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False

@pytest.mark.asyncio
async def test_logout_endpoint(client: AsyncClient):
    """Test the logout endpoint."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
