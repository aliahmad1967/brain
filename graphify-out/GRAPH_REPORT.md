# Graph Report - .  (2026-07-03)

## Corpus Check
- Corpus is ~20,086 words - fits in a single context window. You may not need a graph.

## Summary
- 418 nodes · 581 edges · 73 communities (17 shown, 56 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 153 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]

## God Nodes (most connected - your core abstractions)
1. `SQLiteMetadataStore` - 55 edges
2. `StorageError` - 46 edges
3. `Document` - 22 edges
4. `SearchResult` - 16 edges
5. `AIError` - 14 edges
6. `DocumentChunk` - 14 edges
7. `ImportService` - 13 edges
8. `ChatMessage` - 13 edges
9. `MarkdownImporter` - 12 edges
10. `DocumentImportError` - 12 edges

## Surprising Connections (you probably didn't know these)
- `test_event_bus_pub_sub()` --calls--> `EventBus`  [INFERRED]
  tests/unit/test_core.py → packages/core/src/brain/core/events.py
- `test_document_chunk_creation()` --calls--> `DocumentChunk`  [INFERRED]
  tests/unit/test_shared.py → packages/shared/src/brain/shared/models.py
- `test_settings_default_values()` --calls--> `Settings`  [INFERRED]
  tests/unit/test_core.py → packages/core/src/brain/core/config.py
- `test_lifecycle_manager()` --calls--> `LifecycleManager`  [INFERRED]
  tests/unit/test_core.py → packages/core/src/brain/core/lifecycle.py
- `test_markdown_importer_supports()` --calls--> `MarkdownImporter`  [INFERRED]
  tests/unit/test_importer.py → packages/importer/src/brain/importer/markdown.py

## Communities (73 total, 56 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (30): BaseModel, Protocol, Backend router package for Brain., version_endpoint(), VersionResponse, HybridSearcher, Hybrid search combining vector similarity and keyword search., Protocol defining the structural type required for vector and keyword search. (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.0
Nodes (5): Raised when storage operations (SQLite or Qdrant) fail., StorageError, Production-ready SQLite implementation of the MetadataStore., Create or migrate the database schema., SQLiteMetadataStore

### Community 2 - "Community 2"
Cohesion: 0.0
Nodes (31): DocumentImporter, DocumentImporter, Abstract base class that all document importers must implement., MarkdownImporter, Markdown document importer implementation., Parses Markdown documents to extract text content and optional frontmatter metad, PDFImporter, PDF document importer implementation. (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.0
Nodes (23): ABC, create_ollama_client_from_settings(), EmbeddingsClient, EmbeddingService, OllamaEmbeddingsClient, Embedding provider abstractions and an embedding service.  This module defines a, Generate embeddings for `chunks` and upsert them to the provided         vector, Convenience factory to build an Ollama client from configuration. (+15 more)

### Community 5 - "Community 5"
Cohesion: 0.0
Nodes (15): Configuration management for the Brain platform., Application settings, loaded from environment variables or .env file., Ensure that the data directory and any subdirectories exist., Settings, LifecycleManager, Application lifecycle management for startup and shutdown hooks., Manages the startup and shutdown sequences of the Brain platform., Register a coroutine function to be executed during startup. (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.0
Nodes (8): create_app(), FastAPI application bootstrap and runtime configuration for Brain backend., Create and configure the FastAPI application instance., BackendSettings, Backend configuration loaded from environment variables or .env., register_exception_handlers(), configure_logging(), BaseSettings

### Community 7 - "Community 7"
Cohesion: 0.0
Nodes (11): ApplicationError, Base class for application-level errors., ResourceNotFoundError, Exception, BrainError, ConfigurationError, Custom exceptions for the Brain platform., Raised when application configuration is invalid or missing. (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.0
Nodes (6): EventBus, Event bus implementation for decoupled package communication., A thread-safe, async-capable Event Bus for publish-subscribe communication., Subscribe a callback to a specific event type., Unsubscribe a callback from a specific event type., Publish an event to all subscribed listeners asynchronously.

### Community 9 - "Community 9"
Cohesion: 0.0
Nodes (12): Conversation, Represents a conversation history session., Collection, ImportHistory, Represents a document collection in metadata storage., Represents a tag assigned to a document., Represents a recorded import operation., Tag (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.0
Nodes (7): LexicalDensityReranker, Reranking algorithms for search result optimization., Abstract base class for search result rerankers., Reranks search results based on lexical word overlap and frequency density., Initialize the reranker.          Args:             query_weight: Interpolation, Normalize and tokenize text into lowercase alphanumeric words., Reranker

### Community 11 - "Community 11"
Cohesion: 0.0
Nodes (6): main(), MainWindow, Desktop application entry point and main window shell., Main window shell for the Brain desktop application., Bootstrap and start the PySide6 desktop application., QMainWindow

### Community 12 - "Community 12"
Cohesion: 0.0
Nodes (3): PromptManager, Prompt templates and prompt management for local AI inference., Manages system and user prompt templates for local AI generation.

### Community 13 - "Community 13"
Cohesion: 0.0
Nodes (3): Simple text chunker for splitting documents into `DocumentChunk`s., Naive text chunker splitting on whitespace by approx token count.      This is i, TextChunker

### Community 14 - "Community 14"
Cohesion: 0.0
Nodes (3): ContextBuilder, Builds context for RAG by selecting and formatting search hits., Formats a list of `SearchResult` into a single context string for LLM prompts.

## Knowledge Gaps
- **145 isolated node(s):** `Desktop application entry point and main window shell.`, `Main window shell for the Brain desktop application.`, `Bootstrap and start the PySide6 desktop application.`, `PySide6 desktop application for Brain.`, `Simple text chunker for splitting documents into `DocumentChunk`s.` (+140 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.