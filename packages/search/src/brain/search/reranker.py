"""Reranking algorithms for search result optimization."""

import re
from abc import ABC, abstractmethod

from brain.shared.models import SearchResult


class Reranker(ABC):
    """Abstract base class for search result rerankers."""

    @abstractmethod
    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Re-score and re-order the initial search results.

        Args:
            query: The original search query string.
            results: The list of initial SearchResult objects.

        Returns:
            A re-ordered list of SearchResult objects with updated scores.
        """
        pass


class LexicalDensityReranker(Reranker):
    """Reranks search results based on lexical word overlap and frequency density."""

    def __init__(self, query_weight: float = 0.3) -> None:
        """Initialize the reranker.

        Args:
            query_weight: Interpolation factor between the original score (1 - weight)
                           and the lexical overlap score (weight).
        """
        self.query_weight = query_weight

    def _tokenize(self, text: str) -> set[str]:
        """Normalize and tokenize text into lowercase alphanumeric words."""
        return set(re.findall(r"\w+", text.lower()))

    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        if not results or not query:
            return results

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return results

        scored_results = []
        for res in results:
            chunk_tokens = self._tokenize(res.chunk.content)

            # Calculate Jaccard similarity (word overlap)
            intersection = query_tokens.intersection(chunk_tokens)
            union = query_tokens.union(chunk_tokens)
            overlap_score = len(intersection) / len(union) if union else 0.0

            # Linear interpolation: final_score = (1 - w) * original_score + w * overlap_score
            fused_score = (1.0 - self.query_weight) * res.score + self.query_weight * overlap_score

            scored_results.append(
                SearchResult(
                    chunk=res.chunk,
                    score=fused_score,
                )
            )

        # Sort descending by updated score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results
