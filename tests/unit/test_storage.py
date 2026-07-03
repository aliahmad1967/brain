"""Unit tests for the storage metadata layer."""

from pathlib import Path
from uuid import UUID

from brain.shared.models import ChatMessage, Conversation, Document
from brain.storage.metadata import Collection, ImportHistory, SQLiteMetadataStore, Tag


def test_sqlite_metadata_store_documents_and_conversations(tmp_path: Path) -> None:
    db_file = tmp_path / "test_brain.db"
    store = SQLiteMetadataStore(db_file)
    store.initialize()

    doc = Document(
        name="test_doc.md",
        file_path="/path/to/doc.md",
        file_type="markdown",
        content="Hello world",
        meta_info={"importance": "high"},
    )
    store.save_document(doc)

    retrieved_doc = store.get_document(doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.name == "test_doc.md"
    assert retrieved_doc.content == "Hello world"
    assert retrieved_doc.meta_info["importance"] == "high"

    assert store.list_documents() == [retrieved_doc]

    conv = Conversation(title="Chat Session 1")
    store.create_conversation(conv)

    retrieved_conv = store.get_conversation(conv.id)
    assert retrieved_conv is not None
    assert retrieved_conv.title == "Chat Session 1"

    assert store.list_conversations()[0].id == conv.id

    msg = ChatMessage(role="user", content="What is Brain?")
    store.save_message(conv.id, msg)

    messages = store.get_messages(conv.id)
    assert len(messages) == 1
    assert messages[0].role == "user"
    assert messages[0].content == "What is Brain?"

    store.delete_document(doc.id)
    assert store.get_document(doc.id) is None

    store.delete_conversation(conv.id)
    assert store.get_conversation(conv.id) is None
    assert store.get_messages(conv.id) == []


def test_sqlite_metadata_store_collections_and_tags(tmp_path: Path) -> None:
    db_file = tmp_path / "test_brain.db"
    store = SQLiteMetadataStore(db_file)
    store.initialize()

    collection = Collection(name="Research Papers", description="Academic imports")
    store.save_collection(collection)
    assert store.get_collection(collection.id) == collection
    assert store.list_collections() == [collection]

    tag = Tag(name="urgent")
    store.save_tag(tag)
    assert store.get_tag(tag.id) == tag
    assert store.list_tags() == [tag]

    doc = Document(
        name="tagged_doc.txt",
        file_path="/path/to/tagged_doc.txt",
        file_type="txt",
        content="Tagged content",
    )
    store.save_document(doc)

    store.add_document_to_collection(doc.id, collection.id)
    docs_in_collection = store.list_documents_in_collection(collection.id)
    assert len(docs_in_collection) == 1
    assert docs_in_collection[0].id == doc.id

    store.tag_document(doc.id, tag.id)
    tags_for_doc = store.list_tags_for_document(doc.id)
    assert len(tags_for_doc) == 1
    assert tags_for_doc[0].id == tag.id

    docs_for_tag = store.list_documents_for_tag(tag.id)
    assert len(docs_for_tag) == 1
    assert docs_for_tag[0].id == doc.id

    store.untag_document(doc.id, tag.id)
    assert store.list_tags_for_document(doc.id) == []

    store.remove_document_from_collection(doc.id, collection.id)
    assert store.list_documents_in_collection(collection.id) == []

    store.delete_tag(tag.id)
    assert store.get_tag(tag.id) is None

    store.delete_collection(collection.id)
    assert store.get_collection(collection.id) is None


def test_sqlite_metadata_store_import_history(tmp_path: Path) -> None:
    db_file = tmp_path / "test_brain.db"
    store = SQLiteMetadataStore(db_file)
    store.initialize()

    doc = Document(
        name="imported_doc.txt",
        file_path="/path/to/imported_doc.txt",
        file_type="txt",
        content="Imported content",
    )
    store.save_document(doc)

    history = ImportHistory(
        document_id=str(doc.id),
        source_path="/path/to/imported_doc.txt",
        file_type="txt",
        status="success",
    )
    store.record_import_history(history)

    assert store.get_import_history(history.id) == history
    assert store.list_import_history()[0] == history

    history.status = "failed"
    history.error_message = "Parsing error"
    store.record_import_history(history)

    retrieved = store.get_import_history(history.id)
    assert retrieved is not None
    assert retrieved.status == "failed"
    assert retrieved.error_message == "Parsing error"
