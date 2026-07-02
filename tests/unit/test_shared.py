"""Unit tests for the shared domain models and exceptions."""

from uuid import uuid4

from brain.shared.exceptions import BrainError, DocumentImportError
from brain.shared.models import Document, DocumentChunk


def test_document_creation() -> None:
    doc_id = uuid4()
    doc = Document(
        id=doc_id,
        name="test.md",
        file_path="/path/to/test.md",
        file_type="markdown",
        content="# Test Content",
        meta_info={"author": "Test Author"},
    )
    assert doc.id == doc_id
    assert doc.name == "test.md"
    assert doc.file_path == "/path/to/test.md"
    assert doc.content == "# Test Content"
    assert doc.meta_info["author"] == "Test Author"


def test_document_chunk_creation() -> None:
    doc_id = uuid4()
    chunk_id = uuid4()
    chunk = DocumentChunk(
        id=chunk_id,
        document_id=doc_id,
        chunk_index=0,
        content="This is a test chunk.",
        meta_info={"char_count": 21},
    )
    assert chunk.id == chunk_id
    assert chunk.document_id == doc_id
    assert chunk.chunk_index == 0
    assert chunk.content == "This is a test chunk."
    assert chunk.meta_info["char_count"] == 21


def test_exceptions_inheritance() -> None:
    err = DocumentImportError("Ingestion failed")
    assert isinstance(err, BrainError)
    assert isinstance(err, Exception)
