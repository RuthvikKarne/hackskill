<<<<<<< HEAD
"""JWT authentication middleware.

Intercepts every request, extracts the JWT via Bearer header OR cookie
(Change 1 — single extraction point in jwt.extract_token_from_request),
validates it, and injects the parsed TokenPayload into request.state.user.

Public routes (defined in UNAUTHENTICATED_PATHS) are passed through
without requiring a token.

The middleware does NOT enforce RBAC — that is the responsibility of the
require_permission() dependency in each router. This separation ensures:
- Health/readiness endpoints remain accessible without credentials.
- Auth endpoints (login) can receive unauthenticated requests.
- Every protected route explicitly declares its required permission.

Architecture:
    Browser/API Client
        ↓  Authorization: Bearer <token>   OR   Cookie: hrip_access_token=<token>
    JWTAuthMiddleware
        ↓  request.state.user = TokenPayload(...)
    Router
        ↓  require_permission("patients:read")  [Depends]
    Service
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
# Prefix-matched — any path starting with these strings is public.
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
    """Return True if the request path does not require authentication.

    Args:
        path: The raw request path string.

    Returns:
        True if any public path prefix matches.
    """
    return any(path.startswith(public) for public in UNAUTHENTICATED_PATHS)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that validates JWTs and populates request.state.user.

    Args:
        app: The ASGI application.
        public_key: PEM-encoded RSA public key (from Settings).
        algorithm: JWT algorithm (must match signing algorithm, default RS256).
    """

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
        """Process the request through the JWT validation pipeline.

        Args:
            request: Incoming HTTP request.
            call_next: Next ASGI handler in the middleware stack.

        Returns:
            The response from the next handler, or a 401 JSON response if
            authentication fails on a protected route.
        """
        # 1. Always inject empty user state (safe default for public routes)
        request.state.user = None

        # 2. Skip authentication for public paths
        if _is_public_path(request.url.path):
            return await call_next(request)

        # 3. Extract token (Bearer header OR HttpOnly cookie — same code path)
        raw_token = extract_token_from_request(request)
        if not raw_token:
            return self._unauthorized_response(
                request,
                message="Authentication required. Provide a Bearer token or session cookie.",
                error_code="authentication_required",
            )

        # 4. Validate and decode the token
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

        # 5. Inject parsed claims into request state
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
        """Build a standard 401 error envelope response.

        Args:
            request: Incoming request (for request_id extraction).
            message: Human-readable error message.
            error_code: Machine-readable error code.
            http_status: HTTP status code (usually 401).

        Returns:
            JSONResponse with the standard error envelope.
        """
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
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
