"""Simple text chunker for splitting documents into `DocumentChunk`s."""

from typing import List
from uuid import UUID

from brain.shared.models import Document, DocumentChunk


class TextChunker:
    """Naive text chunker splitting on whitespace by approx token count.

    This is intentionally simple and modular so it can be swapped out for a
    tokenizer-aware chunker later.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        words = document.content.split()
        chunks: List[DocumentChunk] = []
        idx = 0
        chunk_index = 0
        while idx < len(words):
            end = min(idx + self.chunk_size, len(words))
            chunk_words = words[idx:end]
            content = " ".join(chunk_words)
            chunks.append(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    content=content,
                )
            )
            chunk_index += 1
            idx = end - self.overlap if end < len(words) else end

        return chunks
