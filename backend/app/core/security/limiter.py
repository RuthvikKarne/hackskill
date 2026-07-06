"""Rate Limiting configuration.

Uses slowapi with a Redis storage backend for distributed rate limiting.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

from app.config import get_settings
from app.shared.response import error_response

logger = structlog.get_logger(__name__)
settings = get_settings()

# We will attach the storage dynamically during lifespan startup if needed,
# but slowapi's Limiter takes a generic key_func.
# For now, default memory storage, but we can set up Redis storage here.

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle RateLimitExceeded exceptions."""
    request_id = getattr(request.state, "request_id", None)
    logger.warning("rate_limit_exceeded", client=request.client.host if request.client else None)
    
    response = error_response(
        message=f"Rate limit exceeded: {exc.detail}",
        request_id=request_id
    )
    return JSONResponse(
        status_code=429,
        content=response.model_dump(mode='json')
    )

def setup_rate_limiter(app: FastAPI) -> None:
    """Attach the rate limiter and its exception handler to the app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
