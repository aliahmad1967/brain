"""Desktop application entry point and main window shell."""

import asyncio
import logging
import subprocess
import sys
import traceback
from pathlib import Path
from typing import override

from brain.ai import (
    EmbeddingService,
    OllamaLLMClient,
    create_ollama_client_from_settings,
)
from brain.ai.chunker import TextChunker
from brain.ai.prompts import PromptManager
from brain.core import settings
from brain.importer import ImportService
from brain.search.hybrid import ReciprocalRankFusionSearcher
from brain.shared.models import ChatMessage, Document
from brain.storage.metadata import SQLiteMetadataStore
from brain.storage.vector import QdrantVectorStore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window shell for the Brain desktop application."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(settings.app_name)
        self.resize(1200, 820)

        self.backend_process: subprocess.Popen | None = None
        self.import_service = ImportService()
        self.metadata_store = SQLiteMetadataStore(settings.db_path)
        self.vector_store: QdrantVectorStore | None = None
        self.embedding_client = create_ollama_client_from_settings(
            settings.ollama_url, settings.embedding_model
        )
        self.embedding_service: EmbeddingService | None = None
        self.llm_client = OllamaLLMClient(settings.ollama_url, settings.llm_model)
        self.chunker = TextChunker()
        self.searcher: ReciprocalRankFusionSearcher | None = None
        self.vector_store_available = False
        self.documents: list[Document] = []

        self._build_ui()
        self._initialize_services()
        self.statusBar().showMessage("Ready")

    def _initialize_services(self) -> None:
        try:
            self.metadata_store.initialize()
            self._append_status("Metadata store initialized.")
        except Exception as error:
            self._show_error("Initialization failed", error)
            return

        try:
            self.vector_store = QdrantVectorStore(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                collection_name=settings.vector_collection_name,
                vector_size=settings.vector_dimension,
            )
            self.vector_store.initialize()
            self.embedding_service = EmbeddingService(self.embedding_client, self.vector_store)
            self.searcher = ReciprocalRankFusionSearcher(self.vector_store)
            self.vector_store_available = True
            self.storage_status_label.setText("Storage and AI services are initialized.")
            self._append_status("Vector store initialized.")
        except Exception:
            self.vector_store = None
            self.embedding_service = None
            self.searcher = None
            self.vector_store_available = False
            self.storage_status_label.setText("Qdrant unavailable — search and chat are disabled.")
            self._show_warning(
                "Vector store unavailable",
                (
                    f"Could not connect to Qdrant at {settings.qdrant_url}. "
                    "Import and metadata will still work, but search and chat "
                    "require Qdrant to be running."
                ),
            )

        self._load_documents()

    def _build_ui(self) -> None:
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        title = QLabel(settings.app_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")

        subtitle = QLabel(
            "A local-first AI knowledge desktop application for importing, "
            "searching, and chatting with documents."
        )
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #555555;")

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_home_tab(), "Home")
        self.tabs.addTab(self._build_documents_tab(), "Documents")
        self.tabs.addTab(self._build_search_tab(), "Search")
        self.tabs.addTab(self._build_chat_tab(), "Chat")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(main_widget)

    def _build_home_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        intro = QLabel(
            "Use the tabs to import documents, browse your knowledge base, "
            "run search, and ask questions using local Ollama and Qdrant services."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("font-size: 13px; color: #333333;")

        status_box = QGroupBox("Runtime status")
        status_layout = QVBoxLayout(status_box)
        self.backend_status_label = QLabel("Backend is not started.")
        self.storage_status_label = QLabel("Storage and AI services are initialized.")
        status_layout.addWidget(self.backend_status_label)
        status_layout.addWidget(self.storage_status_label)

        import_button = QPushButton("Import Documents")
        import_button.setMinimumHeight(42)
        import_button.clicked.connect(self._import_documents)

        backend_button = QPushButton("Start Backend Server")
        backend_button.setMinimumHeight(42)
        backend_button.clicked.connect(self._start_backend)

        layout.addWidget(intro)
        layout.addWidget(status_box)
        layout.addSpacing(8)
        layout.addWidget(import_button)
        layout.addWidget(backend_button)
        layout.addStretch(1)

        return widget

    def _build_documents_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        left_panel = QVBoxLayout()
        self.documents_list = QListWidget()
        self.documents_list.itemSelectionChanged.connect(self._show_selected_document)

        refresh_button = QPushButton("Refresh Documents")
        refresh_button.clicked.connect(self._load_documents)

        left_panel.addWidget(refresh_button)
        left_panel.addWidget(self.documents_list)

        right_panel = QVBoxLayout()
        self.document_preview = QPlainTextEdit()
        self.document_preview.setReadOnly(True)
        self.document_preview.setPlaceholderText(
            "Select a document to preview its imported content."
        )

        right_panel.addWidget(QLabel("Document preview"))
        right_panel.addWidget(self.document_preview)

        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 2)

        return widget

    def _build_search_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter a search query...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._search_documents)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_button)

        self.search_results = QListWidget()
        self.search_results.itemSelectionChanged.connect(self._show_selected_search_result)

        self.search_preview = QPlainTextEdit()
        self.search_preview.setReadOnly(True)
        self.search_preview.setPlaceholderText(
            "Select a search result to preview the matching content."
        )

        layout.addLayout(search_row)
        layout.addWidget(self.search_results)
        layout.addWidget(QLabel("Result preview"))
        layout.addWidget(self.search_preview)

        return widget

    def _build_chat_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a question about your imported documents...")
        self.chat_button = QPushButton("Ask Brain")
        self.chat_button.clicked.connect(self._chat_with_documents)

        prompt_row = QHBoxLayout()
        prompt_row.addWidget(self.chat_input)
        prompt_row.addWidget(self.chat_button)

        self.chat_response = QPlainTextEdit()
        self.chat_response.setReadOnly(True)
        self.chat_response.setPlaceholderText("AI responses will appear here.")

        layout.addLayout(prompt_row)
        layout.addWidget(QLabel("Response"))
        layout.addWidget(self.chat_response)

        return widget

    def _run_async(self, coro):
        return asyncio.run(coro)

    def _append_status(self, message: str) -> None:
        self.statusBar().showMessage(message)
        logger.info(message)

    def _show_error(self, title: str, error: Exception) -> None:
        logger.exception(error)
        detail = traceback.format_exc(limit=2)
        QMessageBox.critical(self, title, f"{error}\n\n{detail}")
        self.statusBar().showMessage(f"Error: {error}")

    def _show_warning(self, title: str, message: str) -> None:
        logger.warning("%s: %s", title, message)
        QMessageBox.warning(self, title, message)
        self.statusBar().showMessage(message)

    def _load_documents(self) -> None:
        try:
            self.documents = self.metadata_store.list_documents()
            self.documents_list.clear()
            for document in self.documents:
                item = QListWidgetItem(f"{document.name} ({document.file_type})")
                item.setData(Qt.ItemDataRole.UserRole, document)
                self.documents_list.addItem(item)
            self._append_status(f"Loaded {len(self.documents)} imported document(s).")
        except Exception as exc:
            self._show_error("Failed to load documents", exc)

    def _show_selected_document(self) -> None:
        item = self.documents_list.currentItem()
        if not item:
            return
        document = item.data(Qt.ItemDataRole.UserRole)
        self.document_preview.setPlainText(document.content)

    def _show_selected_search_result(self) -> None:
        item = self.search_results.currentItem()
        if not item:
            return
        snippet = item.data(Qt.ItemDataRole.UserRole)
        self.search_preview.setPlainText(snippet)

    def _import_documents(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Documents",
            str(settings.data_dir),
            "Documents (*.pdf *.md *.txt)",
        )
        if not file_paths:
            return

        for path_text in file_paths:
            path = Path(path_text)
            try:
                document = self.import_service.import_file(path)
                self.metadata_store.save_document(document)
                chunks = self.chunker.chunk_document(document)
                if self.embedding_service is not None:
                    self._run_async(
                        self.embedding_service.embed_and_upsert(
                            chunks, vector_size=settings.vector_dimension
                        )
                    )
                    self._append_status(
                        f"Imported '{document.name}' ({len(chunks)} chunks) and indexed embeddings."
                    )
                else:
                    self._append_status(
                        f"Imported '{document.name}' ({len(chunks)} chunks). "
                        "Qdrant unavailable, so embeddings were not indexed."
                    )
            except Exception as exc:
                self._show_error(f"Failed to import {path.name}", exc)

        self._load_documents()

    def _search_documents(self) -> None:
        query = self.search_input.text().strip()
        if not query:
            self._append_status("Enter a search query first.")
            return

        if (
            not self.vector_store_available
            or self.searcher is None
            or self.embedding_service is None
        ):
            self._show_warning(
                "Search unavailable",
                "Qdrant is unavailable. Start Qdrant and restart the app to enable search.",
            )
            return

        try:
            query_vector = self._run_async(self.embedding_service.embed_query(query))
            results = self._run_async(self.searcher.search(query, query_vector, limit=8))
            self.search_results.clear()
            for result in results:
                title = (
                    f"Doc {result.chunk.document_id} · chunk {result.chunk.chunk_index} "
                    f"· score {result.score:.3f}"
                )
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, result.chunk.content)
                self.search_results.addItem(item)
            self._append_status(f"Search returned {len(results)} result(s).")
        except Exception as exc:
            self._show_error("Search failed", exc)

    def _chat_with_documents(self) -> None:
        question = self.chat_input.text().strip()
        if not question:
            self._append_status("Enter a question first.")
            return

        if (
            not self.vector_store_available
            or self.searcher is None
            or self.embedding_service is None
        ):
            self._show_warning(
                "Chat unavailable",
                "Qdrant is unavailable. Start Qdrant and restart the app to enable chat.",
            )
            return

        try:
            query_vector = self._run_async(self.embedding_service.embed_query(question))
            search_results = self._run_async(self.searcher.search(question, query_vector, limit=5))
            context_items = [res.chunk.content for res in search_results]
            if context_items:
                context = "\n\n".join(context_items)
            else:
                context = "No relevant document context could be found."

            system_prompt = PromptManager.format_rag_system(context)
            user_prompt = PromptManager.format_rag_user(question)
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ]
            assistant = self._run_async(self.llm_client.chat(messages))
            self.chat_response.setPlainText(assistant.content)
            self._append_status("Chat response generated.")
        except Exception as exc:
            self._show_error("Chat failed", exc)

    def _start_backend(self) -> None:
        if self.backend_process is not None and self.backend_process.poll() is None:
            self._append_status("Backend is already running.")
            return

        try:
            repo_root = Path(__file__).resolve().parents[6]
            self.backend_process = subprocess.Popen(
                [
                    "uv",
                    "run",
                    "uvicorn",
                    "brain.backend.app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.backend_status_label.setText("Backend process started on http://127.0.0.1:8000")
            self._append_status("Backend startup initiated.")
        except FileNotFoundError:
            self._show_error(
                "Backend launch failed",
                Exception("Could not start uv. Ensure uv is installed and on PATH."),
            )
        except Exception as exc:
            self._show_error("Backend launch failed", exc)

    @override
    def closeEvent(self, event) -> None:
        if self.backend_process is not None and self.backend_process.poll() is None:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=5)
        super().closeEvent(event)


def main() -> None:
    """Bootstrap and start the PySide6 desktop application."""
    settings.ensure_dirs()

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting %s desktop application shell...", settings.app_name)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
