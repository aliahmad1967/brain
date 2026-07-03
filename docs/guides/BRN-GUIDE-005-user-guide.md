---
id: BRN-GUIDE-005
title: User Guide
version: 0.1.0
status: Draft
last_updated: 2026-07-03
depends_on: [BRN-SPEC-006]
referenced_by: []
---

# User Guide

> A practical guide for installing, running, and using Brain locally.

## Overview

Brain is a local-first AI knowledge platform that lets you:

- Import PDF and Markdown documents
- Search with hybrid search (vector + keyword)
- Chat with documents through a local LLM runtime
- Run a desktop app, web app, and backend server on your machine

The current implementation is early-stage, so some functionality is scaffolded and may still be in development.

## Prerequisites

Before running Brain, install the following:

- Python 3.13 or later
- `uv` package manager / environment tool
- Node.js 20+ (for the web app)
- Local services if you want full AI/search support:
  - Ollama for LLM inference
  - Qdrant for vector storage

## Install and prepare the repository

From the repository root:

```powershell
cd D:\brain
uv sync --dev
```

That command will set up a local Python environment with the workspace packages.

## Runtime configuration

Brain loads settings from environment variables and `.env` files.

### Defaults

The default runtime settings are:

- `BRAIN_QDRANT_URL=http://localhost:6333`
- `BRAIN_OLLAMA_URL=http://localhost:11434`
- `BRAIN_BACKEND_ENVIRONMENT=production`

If you need to override defaults, create a `.env` file in the repo root.

### Example `.env`

```env
BRAIN_QDRANT_URL=http://localhost:6333
BRAIN_OLLAMA_URL=http://localhost:11434
BRAIN_BACKEND_ENVIRONMENT=development
```

## Run the desktop application

The desktop application entrypoint is `apps/desktop/src/brain/desktop/main.py`.

From the repo root:

```powershell
uv run python -m brain.desktop.main
```

### What to expect

- The desktop app currently launches a PySide6 main window shell.
- It sets up local runtime directories and uses the shared Brain settings.
- This window is the base for future document import, chat, and search UI.

## Run the backend server

The backend service is implemented in `packages/backend`.

From the repo root, start the server with Uvicorn:

```powershell
uv run uvicorn brain.backend.app:app --reload --host 127.0.0.1 --port 8000
```

### Backend endpoints

The backend exposes at least these system routes:

- `GET /system/health` — health check
- `GET /system/version` — service name and version

## Run the web application

The web app lives in `apps/web` and uses Vite + React.

From `apps/web`:

```powershell
cd apps/web
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal.

## Importing documents

Brain’s import layer supports PDF and Markdown documents.

### Supported importer packages

- `packages/importer` — document importer service
- `packages/importer/src/brain/importer/pdf.py` — PDF importer
- `packages/importer/src/brain/importer/markdown.py` — Markdown importer

The actual import UI and workflow are expected to be provided by the desktop or backend layers.

## Search and AI

Brain is built for hybrid search and local AI inference.

### Local services used

- Qdrant: vector storage for document embeddings
- Ollama: local LLM runtime for embeddings and chat

### Default models

- Embedding model: `bge-m3`
- LLM model: `llama3.2`

If these services are not running, search or chat features may fail until they are available.

## Typical usage flow

1. Start the backend server
2. Start the desktop or web application
3. Import documents into Brain
4. Run search queries against your imported knowledge base
5. Chat with your documents using the local LLM runtime

## Troubleshooting

### Common issues

- `uv run` fails: ensure `uv` is installed and you are in the repo root.
- Desktop app does not open: confirm `PySide6` is installed and the environment is active.
- Backend fails to start: check `uvicorn` is installed and that the `brain.backend.app:app` module is importable.
- Search/chat errors: verify Ollama and Qdrant are available at the configured URLs.

### Helpful commands

```powershell
uv run pytest
uv run ruff check .
uv run black --check .
uv run mypy packages/
```

## Notes

- Brain is early development: the desktop UI currently provides a shell, and the backend provides initial service wiring.
- The repo is designed to keep user data local by default.
- Future versions will expand on importer workflows, search UI, and chat interactions.
