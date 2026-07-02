"""Qdrant-based vector storage layer."""

import logging
from abc import ABC, abstractmethod
from uuid import UUID

from brain.shared.exceptions import StorageError
from brain.shared.models import DocumentChunk, SearchResult
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract interface defining the contract for vector database interactions."""

    @abstractmethod
    def initialize(self) -> None:
        """Create collections or indices if they do not exist."""
        pass

    @abstractmethod
    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        """Store document chunks and their corresponding embedding vectors."""
        pass

    @abstractmethod
    def search(self, query_vector: list[float], limit: int = 5) -> list[SearchResult]:
        """Perform a vector similarity search."""
        pass

    @abstractmethod
    def search_keyword(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Perform a text-based keyword search on stored chunk contents."""
        pass

    @abstractmethod
    def delete_document_chunks(self, document_id: UUID) -> None:
        """Remove all chunks associated with a specific document ID."""
        pass


class QdrantVectorStore(VectorStore):
    """Production-ready Qdrant implementation of the VectorStore."""

    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        collection_name: str = "documents",
        vector_size: int = 768,
    ) -> None:
        self.collection_name = collection_name
        self.vector_size = vector_size
        try:
            self.client = QdrantClient(url=url, api_key=api_key)
        except Exception as e:
            raise StorageError(f"Failed to connect to Qdrant server at {url}: {e}") from e

    def initialize(self) -> None:
        """Create the Qdrant collection and payload text indices if they do not exist."""
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info("Creating Qdrant collection: %s", self.collection_name)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.vector_size,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                # Create text index on 'content' for payload full-text search
                logger.info("Creating full-text payload index on 'content'")
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="content",
                    field_schema=qmodels.TextIndexParams(
                        type="text",
                        tokenizer=qmodels.TokenizerType.WORD,
                        lowercase=True,
                    ),
                )
        except UnexpectedResponse as e:
            raise StorageError(f"Failed to query or create Qdrant collection: {e}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error during vector store initialization: {e}") from e

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("The number of chunks must match the number of embeddings.")

        if not chunks:
            return

        points = []
        for chunk, vector in zip(chunks, embeddings, strict=True):
            payload = {
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "meta_info": chunk.meta_info,
            }
            points.append(
                qmodels.PointStruct(
                    id=str(chunk.id),
                    vector=vector,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
        except Exception as e:
            raise StorageError(f"Failed to upsert chunks to Qdrant: {e}") from e

    def search(self, query_vector: list[float], limit: int = 5) -> list[SearchResult]:
        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Query vector size ({len(query_vector)}) must match vector size ({self.vector_size})"
            )

        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
            ).points

            search_results = []
            for hit in results:
                payload = hit.payload
                if not payload:
                    continue

                chunk = DocumentChunk(
                    id=UUID(hit.id) if isinstance(hit.id, str) else UUID(int=hit.id),
                    document_id=UUID(payload["document_id"]),
                    chunk_index=payload["chunk_index"],
                    content=payload["content"],
                    meta_info=payload.get("meta_info", {}),
                )
                search_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=hit.score,
                    )
                )
            return search_results
        except Exception as e:
            raise StorageError(f"Vector search failed: {e}") from e

    def search_keyword(self, query: str, limit: int = 5) -> list[SearchResult]:
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="content",
                            match=qmodels.MatchText(text=query),
                        )
                    ]
                ),
                limit=limit,
            ).points

            search_results = []
            for hit in results:
                payload = hit.payload
                if not payload:
                    continue

                chunk = DocumentChunk(
                    id=UUID(hit.id) if isinstance(hit.id, str) else UUID(int=hit.id),
                    document_id=UUID(payload["document_id"]),
                    chunk_index=payload["chunk_index"],
                    content=payload["content"],
                    meta_info=payload.get("meta_info", {}),
                )
                # Text matches do not have vector distance score, assign 1.0 default
                search_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=1.0,
                    )
                )
            return search_results
        except Exception as e:
            raise StorageError(f"Keyword search on Qdrant failed: {e}") from e

    def delete_document_chunks(self, document_id: UUID) -> None:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(document_id)),
                        )
                    ]
                ),
                wait=True,
            )
        except Exception as e:
            raise StorageError(
                f"Failed to delete document chunks for {document_id} from Qdrant: {e}"
            ) from e
