"""SQLite-based metadata storage layer."""

import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from brain.shared.exceptions import StorageError
from brain.shared.models import ChatMessage, Conversation, Document


class MetadataStore(ABC):
    """Abstract interface defining the contract for metadata persistence."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the database schemas."""
        pass

    @abstractmethod
    def save_document(self, document: Document) -> None:
        """Persist a document's metadata."""
        pass

    @abstractmethod
    def get_document(self, document_id: UUID) -> Document | None:
        """Retrieve a document by its ID."""
        pass

    @abstractmethod
    def list_documents(self) -> list[Document]:
        """List all stored documents."""
        pass

    @abstractmethod
    def delete_document(self, document_id: UUID) -> None:
        """Delete a document and its associated data."""
        pass

    @abstractmethod
    def create_conversation(self, conversation: Conversation) -> None:
        """Create a new conversation session."""
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        """Retrieve a conversation by its ID."""
        pass

    @abstractmethod
    def list_conversations(self) -> list[Conversation]:
        """List all conversations ordered by updated_at desc."""
        pass

    @abstractmethod
    def delete_conversation(self, conversation_id: UUID) -> None:
        """Delete a conversation and all its messages."""
        pass

    @abstractmethod
    def save_message(self, conversation_id: UUID, message: ChatMessage) -> None:
        """Save a chat message associated with a conversation."""
        pass

    @abstractmethod
    def get_messages(self, conversation_id: UUID) -> list[ChatMessage]:
        """Retrieve all messages for a conversation ordered by created_at."""
        pass


class SQLiteMetadataStore(MetadataStore):
    """Production-ready SQLite implementation of the MetadataStore."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        try:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to connect to SQLite database at {self.db_path}: {e}"
            ) from e

    def initialize(self) -> None:
        """Create database tables if they do not exist."""
        sql_statements = [
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                meta_info TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            """,
        ]
        conn = self._get_connection()
        try:
            with conn:
                for stmt in sql_statements:
                    conn.execute(stmt)
        except sqlite3.Error as e:
            raise StorageError(f"Database initialization failed: {e}") from e
        finally:
            conn.close()

    def save_document(self, document: Document) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO documents (id, name, file_path, file_type, content, created_at, updated_at, meta_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        file_path=excluded.file_path,
                        file_type=excluded.file_type,
                        content=excluded.content,
                        updated_at=excluded.updated_at,
                        meta_info=excluded.meta_info;
                    """,
                    (
                        str(document.id),
                        document.name,
                        document.file_path,
                        document.file_type,
                        document.content,
                        document.created_at.isoformat(),
                        document.updated_at.isoformat(),
                        json.dumps(document.meta_info),
                    ),
                )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to save document {document.id}: {e}") from e
        finally:
            conn.close()

    def get_document(self, document_id: UUID) -> Document | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, file_path, file_type, content, created_at, updated_at, meta_info FROM documents WHERE id = ?",
                (str(document_id),),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Document(
                id=UUID(row["id"]),
                name=row["name"],
                file_path=row["file_path"],
                file_type=row["file_type"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                meta_info=json.loads(row["meta_info"]),
            )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve document {document_id}: {e}") from e
        finally:
            conn.close()

    def list_documents(self) -> list[Document]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, file_path, file_type, content, created_at, updated_at, meta_info FROM documents"
            )
            rows = cursor.fetchall()
            return [
                Document(
                    id=UUID(row["id"]),
                    name=row["name"],
                    file_path=row["file_path"],
                    file_type=row["file_type"],
                    content=row["content"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    meta_info=json.loads(row["meta_info"]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list documents: {e}") from e
        finally:
            conn.close()

    def delete_document(self, document_id: UUID) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM documents WHERE id = ?", (str(document_id),))
        except sqlite3.Error as e:
            raise StorageError(f"Failed to delete document {document_id}: {e}") from e
        finally:
            conn.close()

    def create_conversation(self, conversation: Conversation) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO conversations (id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title=excluded.title,
                        updated_at=excluded.updated_at;
                    """,
                    (
                        str(conversation.id),
                        conversation.title,
                        conversation.created_at.isoformat(),
                        conversation.updated_at.isoformat(),
                    ),
                )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to create conversation {conversation.id}: {e}") from e
        finally:
            conn.close()

    def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (str(conversation_id),),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Conversation(
                id=UUID(row["id"]),
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve conversation {conversation_id}: {e}") from e
        finally:
            conn.close()

    def list_conversations(self) -> list[Conversation]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()
            return [
                Conversation(
                    id=UUID(row["id"]),
                    title=row["title"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list conversations: {e}") from e
        finally:
            conn.close()

    def delete_conversation(self, conversation_id: UUID) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM conversations WHERE id = ?", (str(conversation_id),))
        except sqlite3.Error as e:
            raise StorageError(f"Failed to delete conversation {conversation_id}: {e}") from e
        finally:
            conn.close()

    def save_message(self, conversation_id: UUID, message: ChatMessage) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO messages (id, conversation_id, role, content, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        content=excluded.content;
                    """,
                    (
                        str(message.id),
                        str(conversation_id),
                        message.role,
                        message.content,
                        message.created_at.isoformat(),
                    ),
                )
                # Update conversation updated_at
                conn.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (datetime.now(UTC).isoformat(), str(conversation_id)),
                )
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to save message {message.id} for conversation {conversation_id}: {e}"
            ) from e
        finally:
            conn.close()

    def get_messages(self, conversation_id: UUID) -> list[ChatMessage]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (str(conversation_id),),
            )
            rows = cursor.fetchall()
            return [
                ChatMessage(
                    id=UUID(row["id"]),
                    role=row["role"],
                    content=row["content"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to list messages for conversation {conversation_id}: {e}"
            ) from e
        finally:
            conn.close()
