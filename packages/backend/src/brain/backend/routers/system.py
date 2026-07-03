from __future__ import annotations

from brain.backend.config import BackendSettings
from brain.backend.di import get_settings
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/system", tags=["System"])


class VersionResponse(BaseModel):
    name: str
    version: str
    environment: str


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "brain-backend"}


@router.get("/version", response_model=VersionResponse, summary="Service version information")
async def version_endpoint(settings: BackendSettings = Depends(get_settings)) -> VersionResponse:
    return VersionResponse(
        name=settings.app_name,
        version=settings.version,
        environment=settings.environment,
    )
