from __future__ import annotations

from fastapi import APIRouter, status

from app.config import get_settings
from app.core.security.jwt import TokenPayload, create_access_token
from app.shared.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/demo-login", status_code=status.HTTP_200_OK)
async def demo_login() -> dict:
    settings = get_settings()
    payload = TokenPayload(
        sub="d5aafaa4-c250-425b-a6e0-f4a9d535fe84",
        role="HOSPITAL_ADMIN",
        hospital_id="137e4bf4-10db-4c33-9dd1-7c6e79c7c4a2",
        permissions=[
            "hospitals:read",
            "hospitals:write",
            "patients:read",
            "patients:write",
            "beds:read",
            "beds:write",
            "analytics:read",
        ],
    )
    token = create_access_token(
        payload,
        private_key=settings.JWT_PRIVATE_KEY,
        expire_minutes=60,
        algorithm=settings.JWT_ALGORITHM,
    )
    return success_response(
        data={
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
        },
        message="Demo authentication successful.",
    )
