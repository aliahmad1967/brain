from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_package_version() -> str:
    try:
        return version("brain-backend")
    except PackageNotFoundError:
        return "0.1.0"


class BackendSettings(BaseSettings):
    """Backend configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BRAIN_BACKEND_",
        extra="ignore",
    )

    app_name: str = "Brain Backend"
    description: str = "Local-first AI backend for Brain."
    environment: str = "production"
    version: str = Field(default_factory=get_package_version)

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    log_level: str = "INFO"
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".brain" / "backend",
        description="Directory for backend runtime files, logs, and caches.",
    )
    log_file: Path = Field(
        default_factory=lambda: Path.home() / ".brain" / "backend" / "brain-backend.log",
        description="Path to the backend log file.",
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins for frontend clients.",
    )

    @property
    def is_debug(self) -> bool:
        return self.environment.lower() == "development" or self.debug

    @field_validator("cors_origins", mode="before")
    def normalize_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


settings = BackendSettings()
