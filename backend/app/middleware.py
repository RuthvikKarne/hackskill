"""RequestIDMiddleware — injects a unique X-Request-ID per request.

Generates a UUID4 for every incoming request and:
1. Stores it in request.state.request_id (used by loggers + response envelope).
2. Binds it to structlog's async context (every subsequent log call carries it).
3. Adds X-Request-ID to the response header (for debugging and correlation).

Must be registered BEFORE JWTAuthMiddleware in the middleware stack so that
the request_id is available when auth errors are logged.

Usage in main.py:
    from app.middleware import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)
"""
from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.logging.logger import bind_request_context, get_logger

log = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a UUID4 request ID into every request and response.

    Args:
        app: The ASGI application.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Generate and bind the request ID, then pass the request through.

        Args:
            request: Incoming HTTP request.
            call_next: Next ASGI handler.

        Returns:
            The response with X-Request-ID header attached.
        """
        # Allow callers to pass their own request ID (e.g. from an upstream gateway)
        request_id: str = request.headers.get("X-Request-ID") or str(uuid4())

        # Make it available to all downstream handlers + exception handlers
        request.state.request_id = request_id

        # Bind to structlog async context — all log calls in this request carry it
        bind_request_context(request_id=request_id)

        response = await call_next(request)

        # Echo back in the response so clients can correlate logs
        response.headers["X-Request-ID"] = request_id
        return response
