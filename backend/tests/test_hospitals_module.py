from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.security.jwt import TokenPayload, create_access_token
from app.config import get_settings


@pytest.mark.asyncio
async def test_hospitals_crud_and_listing(client: AsyncClient, hospital_admin_token: TokenPayload) -> None:
    settings = get_settings()
    token = create_access_token(
        hospital_admin_token,
        private_key=settings.JWT_PRIVATE_KEY,
        expire_minutes=60,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "name": "Aster General Hospital",
        "code": "AST-001",
        "type": "district_hospital",
        "level": "tertiary",
        "address": "34 River Road",
        "city": "Kigali",
        "state": "Gasabo",
        "country": "Rwanda",
        "phone": "+250788123456",
        "email": "info@astergeneral.example",
        "beds_capacity": 240,
        "icu_beds": 18,
        "status": "active",
        "latitude": -1.9441,
        "longitude": 30.0619,
    }

    create_response = await client.post("/api/v1/hospitals", json=create_payload, headers=headers)
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()["data"]
    assert created["name"] == create_payload["name"]

    list_response = await client.get("/api/v1/hospitals", headers=headers)
    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["data"]["items"]

    detail_response = await client.get(f"/api/v1/hospitals/{created['id']}", headers=headers)
    assert detail_response.status_code == 200, detail_response.text

    update_payload = {"name": "Aster General Hospital Updated", "status": "operational"}
    update_response = await client.patch(f"/api/v1/hospitals/{created['id']}", json=update_payload, headers=headers)
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["data"]["name"] == update_payload["name"]

    delete_response = await client.delete(f"/api/v1/hospitals/{created['id']}", headers=headers)
    assert delete_response.status_code == 200, delete_response.text
