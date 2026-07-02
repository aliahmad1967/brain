# Roadmap

## v0.1 — Foundation (Current)

> Goal: A working local-first knowledge platform with core features.

**Packages**
- [ ] `packages/shared` — Domain models, Pydantic schemas, custom exceptions
- [ ] `packages/core` — Configuration management, event bus, application lifecycle
- [ ] `packages/storage` — SQLite metadata layer and Qdrant vector store client
- [ ] `packages/importer` — PDF and Markdown ingestion pipeline
- [ ] `packages/ai` — Ollama LLM client, RAG pipeline, prompt templates
- [ ] `packages/search` — Hybrid search (dense + sparse), document indexing, reranking
- [ ] `packages/backend` — FastAPI application wiring all packages together

**Applications**
- [ ] `apps/desktop` — PySide6 GUI with document import, chat, and search views
- [ ] `apps/web` — React SPA with equivalent functionality

**Quality**
- [ ] Unit test suite for all packages
- [ ] Integration tests for storage, search, and AI pipelines
- [ ] CI pipeline (lint, typecheck, test)
- [ ] Documentation: architecture, setup, API reference

---

## v0.2 — Polish & Performance

- [ ] Streaming responses in chat UI
- [ ] Document chunking strategies (sliding window, semantic)
- [ ] Batch import and progress tracking
- [ ] Full-text search boost tuning
- [ ] Desktop app: tray icon, auto-update
- [ ] Web app: dark mode, responsive layout
- [ ] Performance benchmarks and optimization

## v0.3 — Collaboration (Stretch)

- [ ] Multi-user support via shared Qdrant collections
- [ ] Document annotations and highlights
- [ ] Export conversations and search results
- [ ] Plugin system for custom importers and retrievers
- [ ] REST API stability and OpenAPI documentation

## Future

- [ ] Support for additional file formats (EPUB, HTML, plain text)
- [ ] OCR for scanned PDFs
- [ ] Federated search across multiple Brain instances
- [ ] Mobile companion app
- [ ] Local RAG evaluation framework
