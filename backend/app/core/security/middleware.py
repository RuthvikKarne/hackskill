"""Security and Request tracking Middlewares."""
import uuid
import structlog
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security.jwt import decode_token

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injects a unique request ID into every request and response.
    Also binds it to the structlog context.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client sent an ID, otherwise generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Attach to request state
        request.state.request_id = request_id
        
        # Bind to structlog context
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        structlog.contextvars.clear_contextvars()
        return response


class JWTMiddleware(BaseHTTPMiddleware):
    """Extracts JWT token from HttpOnly cookie or Authorization header
    and attaches user context to the request.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Don't validate on auth endpoints or health checks
        path = request.url.path
        if path.startswith("/api/v1/auth") or path in ("/health", "/ready", "/api/docs", "/api/openapi.json"):
            return await call_next(request)

        token = None
        # Try finding token in header (Bearer)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        # Fallback to HttpOnly cookie
        if not token:
            token = request.cookies.get("access_token")
            
        if token:
            try:
                payload = decode_token(token)
                request.state.user = payload
                structlog.contextvars.bind_contextvars(
                    user_id=payload.get("sub"),
                    hospital_id=payload.get("hospital_id")
                )
            except ValueError:
                # Invalid token, proceed anonymously (RBAC will block if needed)
                request.state.user = None
        else:
            request.state.user = None
            
        return await call_next(request)
