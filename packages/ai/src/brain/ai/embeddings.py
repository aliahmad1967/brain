"""Ollama embeddings client implementation."""

import logging
from abc import ABC, abstractmethod

import httpx
from brain.shared.exceptions import AIError

logger = logging.getLogger(__name__)


class EmbeddingsClient(ABC):
    """Abstract base class for vector embedding generation."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate a vector embedding for a query string."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate vector embeddings for a list of document strings in batch."""
        pass


class OllamaEmbeddingsClient(EmbeddingsClient):
    """Local embeddings client using Ollama's HTTP API."""

    def __init__(self, base_url: str, model_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    async def embed_query(self, text: str) -> list[float]:
        url = f"{self.base_url}/api/embed"
        payload = {
            "model": self.model_name,
            "input": text,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                # Ollama's /api/embed returns {"embeddings": [[...]]} for input as a string or list
                embeddings = data["embeddings"]
                return list(embeddings[0])
        except Exception as e:
            logger.error("Ollama embed query request failed: %s", e)
            raise AIError(f"Ollama embedding failure: {e}") from e

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        url = f"{self.base_url}/api/embed"
        payload = {
            "model": self.model_name,
            "input": texts,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings = data["embeddings"]
                return [list(vec) for vec in embeddings]
        except Exception as e:
            logger.error("Ollama embed documents request failed: %s", e)
            raise AIError(f"Ollama batch embedding failure: {e}") from e
