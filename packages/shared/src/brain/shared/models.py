"""Domain models and schemas for the Brain platform."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    """Return the current time in UTC with timezone info."""
    return datetime.now(UTC)


class Document(BaseModel):
    """Represents a document imported into the system."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="The name of the document (usually the filename)")
    file_path: str = Field(..., description="The original local path of the imported document")
    file_type: str = Field(..., description="The file extension/format (e.g., pdf, md)")
    content: str = Field(..., description="The full raw text content of the document")
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
    meta_info: dict[str, str | int | float | bool] = Field(
        default_factory=dict, description="Arbitrary metadata from ingestion"
    )


class DocumentChunk(BaseModel):
    """Represents a segment of an imported document for vector indexing."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID = Field(..., description="The parent document's ID")
    chunk_index: int = Field(
        ..., description="Zero-based sequence order of the chunk in the document"
    )
    content: str = Field(..., description="The text content of this chunk")
    meta_info: dict[str, str | int | float | bool] = Field(
        default_factory=dict, description="Metadata specific to this chunk"
    )


class SearchResult(BaseModel):
    """Represents a hit in hybrid or semantic search."""

    chunk: DocumentChunk = Field(..., description="The matched document chunk")
    score: float = Field(..., description="The similarity/relevance score")


class ChatMessage(BaseModel):
    """Represents a message in a conversation session."""

    id: UUID = Field(default_factory=uuid4)
    role: str = Field(..., description="The role of the sender (system, user, assistant)")
    content: str = Field(..., description="The message text content")
    created_at: datetime = Field(default_factory=get_utc_now)


class Conversation(BaseModel):
    """Represents a conversation history session."""

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="The user-visible title of the conversation")
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
