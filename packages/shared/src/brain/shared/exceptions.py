"""Custom exceptions for the Brain platform."""


class BrainError(Exception):
    """Base exception for all Brain errors."""

    pass


class ConfigurationError(BrainError):
    """Raised when application configuration is invalid or missing."""

    pass


class DocumentImportError(BrainError):
    """Raised when document importing or parsing fails."""

    pass


class StorageError(BrainError):
    """Raised when storage operations (SQLite or Qdrant) fail."""

    pass


class AIError(BrainError):
    """Raised when AI operations (Ollama inference or embeddings) fail."""

    pass


class SearchError(BrainError):
    """Raised when search or retrieval operations fail."""

    pass
