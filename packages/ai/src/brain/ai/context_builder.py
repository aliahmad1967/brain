"""Builds context for RAG by selecting and formatting search hits."""

from typing import List

from brain.shared.models import SearchResult


class ContextBuilder:
    """Formats a list of `SearchResult` into a single context string for LLM prompts."""

    def __init__(self, max_chars: int = 3000) -> None:
        self.max_chars = max_chars

    def build(self, results: List[SearchResult]) -> str:
        parts: List[str] = []
        total = 0
        for res in results:
            snippet = f"[Source: {res.chunk.document_id} | idx:{res.chunk.chunk_index}]\n{res.chunk.content}\n"
            if total + len(snippet) > self.max_chars:
                break
            parts.append(snippet)
            total += len(snippet)

        return "\n---\n".join(parts)
