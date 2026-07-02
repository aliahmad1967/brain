"""FastAPI application bootstrap and lifecycle configuration."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from brain.core import lifecycle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manages FastAPI application startup and shutdown events."""
    # Execute core package startup hooks
    await lifecycle.startup()
    yield
    # Execute core package shutdown hooks
    await lifecycle.shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="Brain API",
        description="Local-first AI Knowledge Platform API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Enable CORS for desktop/web frontend clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """Verify the server is running and accessible."""
        return {"status": "healthy", "service": "brain-backend"}

    return app


app = create_app()
