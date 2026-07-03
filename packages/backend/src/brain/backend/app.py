"""FastAPI application bootstrap and runtime configuration for Brain backend."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from brain.backend.config import settings as backend_settings
from brain.backend.exceptions import register_exception_handlers
from brain.backend.logging import configure_logging
from brain.backend.routers.system import router as system_router
from brain.core import lifecycle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    backend_settings.ensure_dirs()
    logger = configure_logging(backend_settings)
    logger.info("Initializing Brain backend application")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.settings = backend_settings
        app.state.logger = logger

        logger.debug("Starting application lifecycle")
        await lifecycle.startup()
        yield
        logger.debug("Stopping application lifecycle")
        await lifecycle.shutdown()

    app = FastAPI(
        title=backend_settings.app_name,
        description=backend_settings.description,
        version=backend_settings.version,
        debug=backend_settings.is_debug,
        lifespan=lifespan,
    )

    app.state.settings = backend_settings
    app.state.logger = logger

    app.add_middleware(
        CORSMiddleware,
        allow_origins=backend_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(system_router)

    return app


app = create_app()
