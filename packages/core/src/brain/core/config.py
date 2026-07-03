"""Configuration management for the Brain platform."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BRAIN_",
        extra="ignore",
    )

    # General
    app_name: str = "Brain"
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".brain",
        description="Directory for local runtime files (DB, search indices, logs)",
    )

    # SQLite
    db_name: str = "brain.db"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    vector_collection_name: str = "documents"
    # Use 4096 to match `bge-m3` embedding size by default. Can be overridden.
    vector_dimension: int = 4096

    # AI / Ollama
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2"
    # Default embedding model: `bge-m3` (provider-specific model name)
    embedding_model: str = "bge-m3"

    @property
    def db_path(self) -> Path:
        """Get the full path to the SQLite database file."""
        return self.data_dir / self.db_name

    def ensure_dirs(self) -> None:
        """Ensure that the data directory and any subdirectories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Global settings singleton
settings = Settings()
