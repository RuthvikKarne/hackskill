"""Security middlewares for HRIP Backend.

Includes:
1. JWTAuthMiddleware - Extracts and validates JWTs.
2. SecurityHeadersMiddleware - Adds standard HTTP security headers (XSS, HSTS, etc).
3. RequestSizeLimitMiddleware - Prevents excessively large payloads.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from app.core.exceptions.base import AuthenticationError, InvalidTokenError, TokenExpiredError
from app.core.logging.logger import get_logger
from app.core.security.jwt import TokenPayload, decode_token, extract_token_from_request

log = get_logger(__name__)

# Routes that do NOT require a JWT.
UNAUTHENTICATED_PATHS: frozenset[str] = frozenset(
    [
        "/health",
        "/ready",
        "/api/docs",
        "/api/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/demo-login",
        "/api/v1/auth/refresh",
    ]
)


def _is_public_path(path: str) -> bool:
    """Return True if the request path does not require authentication."""
    return any(path.startswith(public) for public in UNAUTHENTICATED_PATHS)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that validates JWTs and populates request.state.user."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        public_key: str,
        algorithm: str = "RS256",
    ) -> None:
        super().__init__(app)
        self._public_key = public_key
        self._algorithm = algorithm

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request through the JWT validation pipeline."""
        request.state.user = None

        if _is_public_path(request.url.path):
            return await call_next(request)

        raw_token = extract_token_from_request(request)
        if not raw_token:
            return self._unauthorized_response(
                request,
                message="Authentication required. Provide a Bearer token or session cookie.",
                error_code="authentication_required",
            )

        try:
            token_payload: TokenPayload = decode_token(
                raw_token,
                public_key=self._public_key,
                algorithm=self._algorithm,
            )
        except TokenExpiredError:
            return self._unauthorized_response(
                request,
                message="Your session has expired. Please log in again.",
                error_code="token_expired",
                http_status=401,
            )
        except (InvalidTokenError, AuthenticationError):
            return self._unauthorized_response(
                request,
                message="Invalid credentials.",
                error_code="invalid_token",
            )

        request.state.user = token_payload
        log.debug(
            "request_authenticated",
            user_id=token_payload.sub,
            role=token_payload.role,
            hospital_id=token_payload.hospital_id,
        )

        return await call_next(request)

    @staticmethod
    def _unauthorized_response(
        request: Request,
        *,
        message: str,
        error_code: str,
        http_status: int = 401,
    ) -> JSONResponse:
        from datetime import UTC, datetime

        request_id: str = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=http_status,
            content={
                "success": False,
                "message": message,
                "data": None,
                "errors": None,
                "meta": {
                    "request_id": request_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "version": "1.0",
                    "error_code": error_code,
                },
            },
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to every response to protect against XSS, clickjacking, etc."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limits incoming request bodies to a maximum size (default 2MB) to prevent DoS."""
    
    def __init__(self, app: ASGIApp, max_bytes: int = 2 * 1024 * 1024) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.max_bytes:
            log.warning("request_too_large", content_length=content_length, limit=self.max_bytes)
            return JSONResponse(
                status_code=413,
                content={"success": False, "message": "Payload too large. Maximum size is 2MB."}
            )
            
        return await call_next(request)
