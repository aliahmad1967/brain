"""Embedding provider abstractions and an embedding service.

This module defines a provider-agnostic `EmbeddingsClient` interface and a
concrete `OllamaEmbeddingsClient`. It also provides `EmbeddingService`, which
orchestrates embedding generation and storing vectors via a VectorStore. The
implementation keeps the storage and provider decoupled so other providers
can be added without changing storage code.
"""

import logging
from abc import ABC, abstractmethod
from typing import List

import httpx
from brain.shared.exceptions import AIError

logger = logging.getLogger(__name__)


class EmbeddingsClient(ABC):
    """Abstract base class for vector embedding generation."""

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate a vector embedding for a query string."""

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of document strings in batch."""


class OllamaEmbeddingsClient(EmbeddingsClient):
    """Local embeddings client using Ollama's HTTP API.

    This class only knows how to call Ollama's HTTP endpoint. Callers should
    depend on the `EmbeddingsClient` interface so other providers can be used
    interchangeably.
    """

    def __init__(self, base_url: str, model_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    async def embed_query(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embed"
        payload = {"model": self.model_name, "input": text}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings = data.get("embeddings")
                if not embeddings:
                    raise AIError("Ollama returned empty embeddings")
                return list(embeddings[0])
        except Exception as e:
            logger.exception("Ollama embed query request failed")
            raise AIError(f"Ollama embedding failure: {e}") from e

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        url = f"{self.base_url}/api/embed"
        payload = {"model": self.model_name, "input": texts}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings = data.get("embeddings")
                if embeddings is None:
                    raise AIError("Ollama returned no embeddings for batch request")
                return [list(vec) for vec in embeddings]
        except Exception as e:
            logger.exception("Ollama embed documents request failed")
            raise AIError(f"Ollama batch embedding failure: {e}") from e


class EmbeddingService:
    """Service coordinating embedding generation and vector storage.

    The service is provider-agnostic: it accepts any implementation of
    `EmbeddingsClient` and a vector store with an `upsert_chunks` method.
    """

    def __init__(self, client: EmbeddingsClient, vector_store) -> None:
        self.client = client
        self.vector_store = vector_store

    async def embed_query(self, text: str) -> List[float]:
        return await self.client.embed_query(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.client.embed_documents(texts)

    async def embed_and_upsert(self, chunks: list, *, vector_size: int | None = None) -> None:
        """Generate embeddings for `chunks` and upsert them to the provided
        vector store. Each chunk is expected to have `content` and the
        data required by the store's `upsert_chunks` contract (e.g., id,
        document_id, chunk_index, meta_info).
        """

        if not chunks:
            return

        texts = [c.content for c in chunks]
        embeddings = await self.client.embed_documents(texts)

        if vector_size is not None:
            for v in embeddings:
                if len(v) != vector_size:
                    raise AIError(
                        f"Embedding vector size mismatch: expected {vector_size}, got {len(v)}"
                    )

        # Delegate storage to the vector store implementation
        self.vector_store.upsert_chunks(chunks, embeddings)


def create_ollama_client_from_settings(base_url: str, model_name: str) -> EmbeddingsClient:
    """Convenience factory to build an Ollama client from configuration."""

    return OllamaEmbeddingsClient(base_url=base_url, model_name=model_name)
