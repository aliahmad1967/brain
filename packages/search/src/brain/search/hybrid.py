"""Hybrid search combining vector similarity and keyword search."""

import logging
from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from brain.shared.models import DocumentChunk, SearchResult

logger = logging.getLogger(__name__)


class VectorStoreProtocol(Protocol):
    """Protocol defining the structural type required for vector and keyword search.

    This avoids direct dependency on the storage package (Dependency Inversion).
    """

    def search(self, query_vector: list[float], limit: int = 5) -> list[SearchResult]:
        """Perform vector similarity search."""
        ...

    def search_keyword(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Perform text-based keyword search."""
        ...


class HybridSearcher(ABC):
    """Abstract interface defining the contract for hybrid document retrieval."""

    @abstractmethod
    async def search(
        self, query: str, query_vector: list[float], limit: int = 5
    ) -> list[SearchResult]:
        """Perform a hybrid search combining vector (dense) and keyword (sparse) retrieval.

        Args:
            query: The raw string query for keyword matching.
            query_vector: The dense vector representation of the query.
            limit: Maximum number of search results to return.
        """
        pass


class ReciprocalRankFusionSearcher(HybridSearcher):
    """Fuses dense vector results and sparse keyword results using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, vector_store: VectorStoreProtocol) -> None:
        self.vector_store = vector_store
        self.rrf_k = 60  # Standard RRF constant

    async def search(
        self, query: str, query_vector: list[float], limit: int = 5
    ) -> list[SearchResult]:
        """Combine dense vector search and sparse keyword search results via RRF."""
        try:
            # 1. Vector Search
            vector_results = self.vector_store.search(query_vector, limit=limit * 2)

            # 2. Keyword Search
            keyword_results = self.vector_store.search_keyword(query, limit=limit * 2)
        except Exception as e:
            logger.error("Failed to retrieve search results from vector store protocol: %s", e)
            return []

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF score = sum_{m in systems} 1 / (k + rank(d, m))
        rrf_scores: dict[UUID, float] = {}
        chunk_map: dict[UUID, DocumentChunk] = {}

        # Process vector results
        for rank, res in enumerate(vector_results, start=1):
            chunk_id = res.chunk.id
            chunk_map[chunk_id] = res.chunk
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Process keyword results
        for rank, res in enumerate(keyword_results, start=1):
            chunk_id = res.chunk.id
            chunk_map[chunk_id] = res.chunk
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort chunk IDs by fused RRF scores descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[
            :limit
        ]

        # Build fused SearchResult list
        fused_results = [
            SearchResult(
                chunk=chunk_map[cid],
                score=rrf_scores[cid],
            )
            for cid in sorted_ids
        ]

        return fused_results
