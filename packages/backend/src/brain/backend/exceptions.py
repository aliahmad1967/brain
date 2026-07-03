from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger("brain.backend.exceptions")


class ApplicationError(Exception):
    """Base class for application-level errors."""

    status_code: int = HTTP_400_BAD_REQUEST
    detail: str = "An application error occurred."

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail


class ResourceNotFoundError(ApplicationError):
    status_code = HTTP_404_NOT_FOUND
    detail = "The requested resource was not found."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.warning("Application error: %s", exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "application_error", "detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.debug("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "validation_error", "detail": exc.errors()},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.debug("Pydantic validation error: %s", exc.errors())
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "validation_error", "detail": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning("HTTP exception: %s", exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "http_exception", "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception during request processing")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_server_error", "detail": "An unexpected error occurred."},
        )
