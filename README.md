# Brain

**A local-first AI knowledge platform.**

Import PDFs and Markdown documents, chat with them using local LLMs, and search across your knowledge base with hybrid (semantic + keyword) search — all without sending your data to the cloud.

---

## Vision

Brain is your second brain for local document intelligence. It combines the privacy of local-first architecture with the power of modern AI:

- **Import** PDF and Markdown documents into a structured knowledge base
- **Chat** with your documents using retrieval-augmented generation (RAG)
- **Search** using hybrid search (vector embeddings + full-text keyword)
- **Run locally** with Ollama for LLM inference and Qdrant for vector storage
- **Own your data** — everything stays on your machine by default

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Desktop (PySide6)                 │
│                     Web (React)                      │
├─────────────────────────────────────────────────────┤
│                   FastAPI Backend                     │
├──────────┬──────────┬──────────┬─────────────────────┤
│  Core    │    AI    │ Importer │   Search             │
│ (config, │ (RAG,    │ (PDF,    │  (hybrid, rerank)    │
│  events) │  Ollama) │  MD)     │                      │
├──────────┴──────────┴──────────┴─────────────────────┤
│  Storage (SQLite metadata, Qdrant embeddings)         │
│  Shared (models, schemas, exceptions)                 │
└─────────────────────────────────────────────────────┘
```

## Repository Structure

```
brain/
├── apps/
│   ├── desktop/          # PySide6 desktop application
│   └── web/              # React web application
├── packages/
│   ├── backend/          # FastAPI server, routes, middleware
│   ├── core/             # Configuration, event system, lifecycle
│   ├── ai/               # RAG pipeline, LLM client, prompt management
│   ├── importer/         # PDF and Markdown ingestion
│   ├── search/           # Hybrid search, indexing, reranking
│   ├── storage/          # SQLite metadata layer, Qdrant client
│   └── shared/           # Domain models, schemas, exceptions
├── docs/                 # Architecture, ADRs, user guides
├── tests/
│   ├── unit/             # Unit tests per package
│   └── integration/      # Integration tests (DB, Qdrant, Ollama)
├── scripts/              # Dev tooling, build, setup helpers
├── assets/               # Icons, fonts, static resources
├── examples/             # Sample documents, usage demos
├── .brain/               # Local runtime data (gitignored)
└── .github/              # CI workflows, issue templates
```

## Tech Stack

| Layer         | Technology                                      |
|---------------|-------------------------------------------------|
| Language      | Python 3.13, TypeScript (web)                   |
| Backend       | FastAPI                                         |
| Desktop       | PySide6                                         |
| Web           | React                                           |
| Vector Store  | Qdrant                                          |
| Metadata      | SQLite                                          |
| LLM Runtime   | Ollama                                          |
| Search        | Hybrid (dense + sparse)                         |
| Linting       | Ruff, Black, Mypy                               |
| Testing       | Pytest                                          |
| Packaging     | uv                                              |

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full development roadmap.

### v0.1 — Foundation
- [x] Project structure and configuration
- [ ] PDF and Markdown document import
- [ ] Chat with documents via Ollama
- [ ] Hybrid search (vector + keyword)
- [ ] SQLite metadata storage
- [ ] Qdrant vector storage
- [ ] FastAPI backend
- [ ] PySide6 desktop application
- [ ] React web application

## Getting Started

> **Note:** Brain is in early development. These instructions will be updated as the project matures.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/aliahmad1967/brain.git
cd brain

# Create a virtual environment and install dependencies
uv sync --dev

# Run tests
uv run pytest
```

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for our contribution guidelines and [ROADMAP.md](ROADMAP.md) for the development plan.

### Quick Start for Contributors

```bash
uv sync --dev
uv run ruff check .
uv run black --check .
uv run mypy packages/
uv run pytest
```

## License

Brain is open-source under the [MIT License](LICENSE).

---

Built with ❤️ for local-first AI.
