from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_demo_login_returns_access_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/demo-login",
        json={"email": "admin@triarch.health", "password": "demo-password"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["data"]["access_token"]
    assert payload["data"]["token_type"] == "bearer"
