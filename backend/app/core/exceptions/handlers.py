"""Global exception handlers for FastAPI.

Catches unhandled exceptions and returns standardized APIResponse JSON.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

from app.shared.response import error_response

logger = structlog.get_logger(__name__)

def add_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers to the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handles Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", None)
        errors = exc.errors()
        error_msg = f"Validation Error: {errors}"
        logger.warning("request_validation_error", errors=errors)
        
        response = error_response(message=error_msg, request_id=request_id)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(mode='json'),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all for any unhandled exception."""
        request_id = getattr(request.state, "request_id", None)
        logger.exception("unhandled_exception", exc_info=exc)
        
        response = error_response(
            message="An unexpected internal server error occurred.", 
            request_id=request_id
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode='json'),
        )
