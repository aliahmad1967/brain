"""Unit tests for the search package algorithms."""

from uuid import uuid4

from brain.search.reranker import LexicalDensityReranker
from brain.shared.models import DocumentChunk, SearchResult


def test_lexical_density_reranker() -> None:
    reranker = LexicalDensityReranker(query_weight=0.5)

    doc_id = uuid4()
    # Chunk 1 has a high keyword match (contains "python", "monorepo")
    chunk1 = DocumentChunk(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        content="This is a python project structure in a monorepo setup.",
    )
    # Chunk 2 has low overlap (contains general text)
    chunk2 = DocumentChunk(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=1,
        content="We are building local first software with desktop and web apps.",
    )

    results = [
        SearchResult(chunk=chunk1, score=0.4),
        SearchResult(chunk=chunk2, score=0.6),  # initial vector score is higher for chunk2
    ]

    # Query has words that overlap heavily with chunk1 ("python monorepo")
    reranked = reranker.rerank(query="python monorepo", results=results)

    assert len(reranked) == 2
    # Chunk 1 should be promoted to first position because of lexical density overlap
    assert reranked[0].chunk.id == chunk1.id
    assert reranked[0].score > reranked[1].score
