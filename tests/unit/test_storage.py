"""Unit tests for the storage metadata layer."""

from brain.shared.models import ChatMessage, Conversation, Document
from brain.storage.metadata import SQLiteMetadataStore


def test_sqlite_metadata_store_operations(tmp_path: str) -> None:
    # Use tmp_path fixture from pytest for a temporary sqlite file
    from pathlib import Path

    db_file = Path(tmp_path) / "test_brain.db"
    store = SQLiteMetadataStore(db_file)
    store.initialize()

    # Test document operations
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

    all_docs = store.list_documents()
    assert len(all_docs) == 1
    assert all_docs[0].id == doc.id

    # Test conversation operations
    conv = Conversation(title="Chat Session 1")
    store.create_conversation(conv)

    retrieved_conv = store.get_conversation(conv.id)
    assert retrieved_conv is not None
    assert retrieved_conv.title == "Chat Session 1"

    all_convs = store.list_conversations()
    assert len(all_convs) == 1
    assert all_convs[0].id == conv.id

    # Test message operations
    msg = ChatMessage(role="user", content="What is Brain?")
    store.save_message(conv.id, msg)

    messages = store.get_messages(conv.id)
    assert len(messages) == 1
    assert messages[0].role == "user"
    assert messages[0].content == "What is Brain?"

    # Test deletion
    store.delete_document(doc.id)
    assert store.get_document(doc.id) is None

    store.delete_conversation(conv.id)
    assert store.get_conversation(conv.id) is None
    assert len(store.get_messages(conv.id)) == 0
