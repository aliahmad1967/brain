"""SQLite-based metadata storage layer."""

import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from brain.shared.exceptions import StorageError
from brain.shared.models import ChatMessage, Conversation, Document, get_utc_now

LATEST_SCHEMA_VERSION = 2


@dataclass
class Collection:
    """Represents a document collection in metadata storage."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = field(default_factory=str)
    description: str | None = None
    created_at: datetime = field(default_factory=get_utc_now)
    updated_at: datetime = field(default_factory=get_utc_now)


@dataclass
class Tag:
    """Represents a tag assigned to a document."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = field(default_factory=str)
    created_at: datetime = field(default_factory=get_utc_now)


@dataclass
class ImportHistory:
    """Represents a recorded import operation."""

    id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str | None = None
    source_path: str = field(default_factory=str)
    file_type: str = field(default_factory=str)
    imported_at: datetime = field(default_factory=get_utc_now)
    status: str = field(default_factory=str)
    error_message: str | None = None


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
    def save_collection(self, collection: Collection) -> None:
        """Persist a document collection."""
        pass

    @abstractmethod
    def get_collection(self, collection_id: str) -> Collection | None:
        """Retrieve a collection by its ID."""
        pass

    @abstractmethod
    def list_collections(self) -> list[Collection]:
        """List all collections."""
        pass

    @abstractmethod
    def delete_collection(self, collection_id: str) -> None:
        """Delete a collection and its relationships."""
        pass

    @abstractmethod
    def save_tag(self, tag: Tag) -> None:
        """Persist a tag."""
        pass

    @abstractmethod
    def get_tag(self, tag_id: str) -> Tag | None:
        """Retrieve a tag by its ID."""
        pass

    @abstractmethod
    def list_tags(self) -> list[Tag]:
        """List all tags."""
        pass

    @abstractmethod
    def delete_tag(self, tag_id: str) -> None:
        """Delete a tag and its relationships."""
        pass

    @abstractmethod
    def add_document_to_collection(self, document_id: UUID, collection_id: str) -> None:
        """Associate a document with a collection."""
        pass

    @abstractmethod
    def remove_document_from_collection(self, document_id: UUID, collection_id: str) -> None:
        """Remove a document from a collection."""
        pass

    @abstractmethod
    def list_documents_in_collection(self, collection_id: str) -> list[Document]:
        """List documents that belong to a collection."""
        pass

    @abstractmethod
    def tag_document(self, document_id: UUID, tag_id: str) -> None:
        """Attach a tag to a document."""
        pass

    @abstractmethod
    def untag_document(self, document_id: UUID, tag_id: str) -> None:
        """Remove a tag from a document."""
        pass

    @abstractmethod
    def list_tags_for_document(self, document_id: UUID) -> list[Tag]:
        """List tags associated with a document."""
        pass

    @abstractmethod
    def list_documents_for_tag(self, tag_id: str) -> list[Document]:
        """List documents associated with a tag."""
        pass

    @abstractmethod
    def record_import_history(self, entry: ImportHistory) -> None:
        """Record an import history entry."""
        pass

    @abstractmethod
    def get_import_history(self, history_id: str) -> ImportHistory | None:
        """Retrieve an import history entry by ID."""
        pass

    @abstractmethod
    def list_import_history(self) -> list[ImportHistory]:
        """List import history entries."""
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
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to connect to SQLite database at {self.db_path}: {e}"
            ) from e

    def initialize(self) -> None:
        """Create or migrate the database schema."""
        conn = self._get_connection()
        try:
            current_version = self._get_schema_version(conn)
            if current_version == 0:
                self._apply_initial_schema(conn)
            elif current_version < LATEST_SCHEMA_VERSION:
                self._apply_migrations(conn, current_version)
        except sqlite3.Error as e:
            raise StorageError(f"Database initialization failed: {e}") from e
        finally:
            conn.close()

    def _schema_version_table_exists(self, conn: sqlite3.Connection) -> bool:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        return cursor.fetchone() is not None

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def _get_schema_version(self, conn: sqlite3.Connection) -> int:
        if not self._schema_version_table_exists(conn):
            if self._table_exists(conn, "documents"):
                return 1
            return 0

        cursor = conn.execute("SELECT version FROM schema_version WHERE id = 1")
        row = cursor.fetchone()
        return int(row["version"]) if row else 0

    def _set_schema_version(self, conn: sqlite3.Connection, version: int) -> None:
        conn.execute(
            "INSERT INTO schema_version (id, version) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET version = excluded.version;",
            (version,),
        )

    def _apply_initial_schema(self, conn: sqlite3.Connection) -> None:
        with conn:
            for statement in self._schema_statements():
                conn.execute(statement)
            self._set_schema_version(conn, LATEST_SCHEMA_VERSION)

    def _apply_migrations(self, conn: sqlite3.Connection, current_version: int) -> None:
        while current_version < LATEST_SCHEMA_VERSION:
            next_version = current_version + 1
            migration = getattr(self, f"_migrate_v{current_version}_to_v{next_version}")
            with conn:
                migration(conn)
                self._set_schema_version(conn, next_version)
            current_version = next_version

    def _migrate_v1_to_v2(self, conn: sqlite3.Connection) -> None:
        for statement in self._v2_statements():
            conn.execute(statement)

    def _schema_statements(self) -> list[str]:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL
            );
            """,
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
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS collection_documents (
                collection_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                PRIMARY KEY (collection_id, document_id),
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS import_history (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                source_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
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
        statements.extend(self._index_statements())
        return statements

    def _v2_statements(self) -> list[str]:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS collection_documents (
                collection_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                PRIMARY KEY (collection_id, document_id),
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS import_history (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                source_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
            );
            """,
        ]
        statements.extend(self._index_statements())
        return statements

    def _index_statements(self) -> list[str]:
        return [
            "CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);",
            "CREATE INDEX IF NOT EXISTS idx_collection_name ON collections(name);",
            "CREATE INDEX IF NOT EXISTS idx_tag_name ON tags(name);",
            "CREATE INDEX IF NOT EXISTS idx_collection_documents_collection_id ON collection_documents(collection_id);",
            "CREATE INDEX IF NOT EXISTS idx_collection_documents_document_id ON collection_documents(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_document_tags_document_id ON document_tags(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_document_tags_tag_id ON document_tags(tag_id);",
            "CREATE INDEX IF NOT EXISTS idx_import_history_document_id ON import_history(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_import_history_status ON import_history(status);",
        ]

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
            return self._to_document(row)
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
            return [self._to_document(row) for row in rows]
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

    def save_collection(self, collection: Collection) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO collections (id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        description=excluded.description,
                        updated_at=excluded.updated_at;
                    """,
                    (
                        collection.id,
                        collection.name,
                        collection.description,
                        collection.created_at.isoformat(),
                        collection.updated_at.isoformat(),
                    ),
                )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to save collection {collection.id}: {e}") from e
        finally:
            conn.close()

    def get_collection(self, collection_id: str) -> Collection | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at FROM collections WHERE id = ?",
                (collection_id,),
            )
            row = cursor.fetchone()
            return self._to_collection(row) if row else None
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve collection {collection_id}: {e}") from e
        finally:
            conn.close()

    def list_collections(self) -> list[Collection]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, created_at, updated_at FROM collections")
            rows = cursor.fetchall()
            return [self._to_collection(row) for row in rows]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list collections: {e}") from e
        finally:
            conn.close()

    def delete_collection(self, collection_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        except sqlite3.Error as e:
            raise StorageError(f"Failed to delete collection {collection_id}: {e}") from e
        finally:
            conn.close()

    def save_tag(self, tag: Tag) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO tags (id, name, created_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name;
                    """,
                    (tag.id, tag.name, tag.created_at.isoformat()),
                )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to save tag {tag.id}: {e}") from e
        finally:
            conn.close()

    def get_tag(self, tag_id: str) -> Tag | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, created_at FROM tags WHERE id = ?", (tag_id,))
            row = cursor.fetchone()
            return self._to_tag(row) if row else None
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve tag {tag_id}: {e}") from e
        finally:
            conn.close()

    def list_tags(self) -> list[Tag]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, created_at FROM tags")
            rows = cursor.fetchall()
            return [self._to_tag(row) for row in rows]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list tags: {e}") from e
        finally:
            conn.close()

    def delete_tag(self, tag_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        except sqlite3.Error as e:
            raise StorageError(f"Failed to delete tag {tag_id}: {e}") from e
        finally:
            conn.close()

    def add_document_to_collection(self, document_id: UUID, collection_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO collection_documents (collection_id, document_id) VALUES (?, ?)",
                    (collection_id, str(document_id)),
                )
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to add document {document_id} to collection {collection_id}: {e}"
            ) from e
        finally:
            conn.close()

    def remove_document_from_collection(self, document_id: UUID, collection_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "DELETE FROM collection_documents WHERE collection_id = ? AND document_id = ?",
                    (collection_id, str(document_id)),
                )
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to remove document {document_id} from collection {collection_id}: {e}"
            ) from e
        finally:
            conn.close()

    def list_documents_in_collection(self, collection_id: str) -> list[Document]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT d.id, d.name, d.file_path, d.file_type, d.content, d.created_at, d.updated_at, d.meta_info "
                "FROM documents d "
                "JOIN collection_documents cd ON d.id = cd.document_id "
                "WHERE cd.collection_id = ?",
                (collection_id,),
            )
            return [self._to_document(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to list documents in collection {collection_id}: {e}"
            ) from e
        finally:
            conn.close()

    def tag_document(self, document_id: UUID, tag_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)",
                    (str(document_id), tag_id),
                )
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to tag document {document_id} with tag {tag_id}: {e}"
            ) from e
        finally:
            conn.close()

    def untag_document(self, document_id: UUID, tag_id: str) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "DELETE FROM document_tags WHERE document_id = ? AND tag_id = ?",
                    (str(document_id), tag_id),
                )
        except sqlite3.Error as e:
            raise StorageError(
                f"Failed to untag document {document_id} for tag {tag_id}: {e}"
            ) from e
        finally:
            conn.close()

    def list_tags_for_document(self, document_id: UUID) -> list[Tag]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT t.id, t.name, t.created_at "
                "FROM tags t "
                "JOIN document_tags dt ON t.id = dt.tag_id "
                "WHERE dt.document_id = ?",
                (str(document_id),),
            )
            return [self._to_tag(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list tags for document {document_id}: {e}") from e
        finally:
            conn.close()

    def list_documents_for_tag(self, tag_id: str) -> list[Document]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT d.id, d.name, d.file_path, d.file_type, d.content, d.created_at, d.updated_at, d.meta_info "
                "FROM documents d "
                "JOIN document_tags dt ON d.id = dt.document_id "
                "WHERE dt.tag_id = ?",
                (tag_id,),
            )
            return [self._to_document(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list documents for tag {tag_id}: {e}") from e
        finally:
            conn.close()

    def record_import_history(self, entry: ImportHistory) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO import_history (id, document_id, source_path, file_type, imported_at, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        document_id=excluded.document_id,
                        source_path=excluded.source_path,
                        file_type=excluded.file_type,
                        imported_at=excluded.imported_at,
                        status=excluded.status,
                        error_message=excluded.error_message;
                    """,
                    (
                        entry.id,
                        entry.document_id,
                        entry.source_path,
                        entry.file_type,
                        entry.imported_at.isoformat(),
                        entry.status,
                        entry.error_message,
                    ),
                )
        except sqlite3.Error as e:
            raise StorageError(f"Failed to record import history {entry.id}: {e}") from e
        finally:
            conn.close()

    def get_import_history(self, history_id: str) -> ImportHistory | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, document_id, source_path, file_type, imported_at, status, error_message "
                "FROM import_history WHERE id = ?",
                (history_id,),
            )
            row = cursor.fetchone()
            return self._to_import_history(row) if row else None
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve import history {history_id}: {e}") from e
        finally:
            conn.close()

    def list_import_history(self) -> list[ImportHistory]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, document_id, source_path, file_type, imported_at, status, error_message "
                "FROM import_history ORDER BY imported_at DESC"
            )
            return [self._to_import_history(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise StorageError(f"Failed to list import history: {e}") from e
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

    def _to_document(self, row: sqlite3.Row) -> Document:
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

    def _to_collection(self, row: sqlite3.Row) -> Collection:
        return Collection(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _to_import_history(self, row: sqlite3.Row) -> ImportHistory:
        return ImportHistory(
            id=row["id"],
            document_id=row["document_id"],
            source_path=row["source_path"],
            file_type=row["file_type"],
            imported_at=datetime.fromisoformat(row["imported_at"]),
            status=row["status"],
            error_message=row["error_message"],
        )
