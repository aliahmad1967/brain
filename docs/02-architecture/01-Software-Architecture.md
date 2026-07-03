# Software Architecture Document

## Overview

This document describes the architecture of Brain as a local-first AI platform. It defines the system context, containers, components, storage, AI, import, search, and application layers. The design is aligned to C4 architecture principles and includes Mermaid diagrams to illustrate system boundaries, runtime containers, and component interactions.

## Architectural Principles

- Local-first execution: prioritize on-device inference and offline capability.
- Clear separation of concerns: isolate data handling, AI processing, search, and application logic.
- Modular extensibility: support future integrations through well-defined interfaces.
- Privacy by design: keep user data local and minimize external dependencies.
- Resilience: ensure the system degrades gracefully when resources are constrained.

## System Context

Brain is a desktop-focused AI platform that operates primarily on the user’s local device. It interacts with external resources only when optional sync or updates are enabled.

### System Context Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  User["User\n(creator, knowledge worker, engineer)"]
  BrainApp["Brain Application\n(Local AI platform)"]
  LocalStorage["Local Storage\n(disk, cache, history)"]
  ModelStore["Local Model Store\n(models, weights, metadata)"]
  OptionalSync["Optional Cloud Sync\n(configurable, user opt-in)"]
  ExternalUpdates["External Model Updates\n(when connected)"]

  User -->|uses| BrainApp
  BrainApp -->|reads/writes| LocalStorage
  BrainApp -->|loads| ModelStore
  BrainApp -->|optional sync| OptionalSync
  BrainApp -->|optional updates| ExternalUpdates
```

### System Context Narrative

- The primary actor is the end user, who runs Brain on a local desktop machine.
- Brain interacts with local storage for persistent session data, content, and model metadata.
- It uses a local model store for AI inference with downloaded or preinstalled models.
- Optional integrations, such as cloud sync or external model updates, are available only when the user opts in.

## Containers

Brain is decomposed into logical containers representing major runtime subsystems.

### Container Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart TD
  App["Application Layer\n(Frontend / UI)"]
  Backend["Backend Layer\n(Core services, orchestration)"]
  AI["AI Layer\n(Model orchestration, inference engine)"]
  Storage["Storage Layer\n(Local persistence, cache)"]
  Import["Import Layer\n(Document ingestion, converters)"]
  Search["Search Layer\n(Indexing, retrieval, query service)"]

  App -->|API calls| Backend
  Backend -->|requests| AI
  Backend -->|reads/writes| Storage
  Backend -->|ingest data| Import
  Backend -->|query| Search
  Import -->|store documents| Storage
  Import -->|notify| Search
  Search -->|reads| Storage
  AI -->|reads models| Storage
```

### Container Responsibilities

- Application Layer: user interface and user experience handling.
- Backend Layer: orchestration of features, security, session management, and inter-container communication.
- AI Layer: model management and inference orchestration.
- Storage Layer: persistent storage of content, sessions, and metadata.
- Import Layer: document ingestion, transformation, and content extraction.
- Search Layer: indexing, retrieval, and search query processing.

## Components

Each container contains components with single responsibilities.

### Application Layer Components

- UI Shell: main application window, navigation, and workspace layout.
- Interaction Panel: prompt entry, response display, and refinement controls.
- Status & Settings: offline state, model selection, privacy settings, onboarding.
- History Viewer: session history, search, and restore capabilities.

### Backend Layer Components

- Session Manager: stores and retrieves active session state.
- Request Router: routes frontend requests to the appropriate subsystem.
- Privacy Controller: enforces local data handling rules and user consent.
- Configuration Service: loads and persists user preferences and settings.
- Notification Hub: broadcasts status and error updates to the UI.

### AI Layer Components

- Model Orchestrator: selects, loads, and switches between local models.
- Inference Engine: executes inference with local models and returns outputs.
- Model Metadata Store: tracks available models, resource requirements, and capabilities.
- Resource Monitor: observes CPU, memory, and device capacity for inference.

### Storage Layer Components

- Document Store: persistent storage for imported files and generated content.
- Session Store: local history and active session persistence.
- Cache Manager: temporary storage for inference artifacts, tokenized contexts, and intermediate results.
- Config Store: user settings, model selections, and privacy choices.

### Import Layer Components

- File Ingestor: accepts supported file formats and converts them into structured content.
- Parser Service: extracts text and metadata from documents.
- Content Normalizer: cleans, chunks, and prepares imported content for search and AI context.
- Import Audit Trail: records ingestion operations for review and reuse.

### Search Layer Components

- Indexer: builds and updates searchable indexes from imported content.
- Search Engine: processes queries and returns relevant results.
- Embedding Service: creates local embeddings for search and semantic retrieval.
- Search Cache: caches query results for faster repeat retrieval.

## Package Responsibilities

This section maps logical responsibilities to the repository’s package structure.

### `packages/core`

- Core orchestration services and runtime plumbing.
- Application bootstrapping and dependency injection.
- Common lifecycle management and event dispatching.

### `packages/backend`

- Backend services and API implementations for the desktop application.
- Request routing, privacy enforcement, and configuration management.
- Backend bridges to local storage, AI, import, and search subsystems.

### `packages/ai`

- AI interfaces, model loading, inference orchestration, and prompt utilities.
- Embeddings and local model configuration.
- AI prompts, template management, and model lifecycle utilities.

### `packages/storage`

- Local persistence abstractions and storage drivers.
- Session history, document store, cache manager, and config store implementations.
- Storage schemas, serialization, and data integrity checks.

### `packages/importer`

- Document ingestion services and file parsing logic.
- Format-specific converters, text extraction, and content normalization.
- Import audit and pipeline orchestration.

### `packages/search`

- Search indexing and retrieval services.
- Semantic search utilities and embedding orchestration.
- Search query processing and local search cache.

### `packages/shared`

- Shared utilities, types, and constants used across packages.
- Common error handling, logging, and model metadata definitions.

## Dependency Rules

The architecture enforces clear dependency directions to avoid coupling and improve maintainability.

- `packages/core` is the foundation and may be consumed by all other packages.
- `packages/backend` may depend on `packages/core`, `packages/storage`, `packages/ai`, `packages/importer`, `packages/search`, and `packages/shared`.
- `packages/ai` may depend on `packages/core`, `packages/storage`, and `packages/shared`.
- `packages/storage` may depend on `packages/core` and `packages/shared`, but not on `packages/backend`, `packages/ai`, `packages/importer`, or `packages/search`.
- `packages/importer` may depend on `packages/core`, `packages/storage`, and `packages/shared`, but not on `packages/backend`, `packages/ai`, or `packages/search`.
- `packages/search` may depend on `packages/core`, `packages/storage`, `packages/ai` (for embeddings), and `packages/shared`, but not on `packages/backend`.
- `packages/shared` must be dependency-free of application-specific packages and may be consumed by all packages.

### Dependency Rule Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart TD
  subgraph Core[Core Layer]
    CorePkg["packages/core"]
    SharedPkg["packages/shared"]
  end
  subgraph Backend[Backend Layer]
    BackendPkg["packages/backend"]
  end
  subgraph AI[AI Layer]
    AIPkg["packages/ai"]
  end
  subgraph Storage[Storage Layer]
    StoragePkg["packages/storage"]
  end
  subgraph Import[Import Layer]
    ImportPkg["packages/importer"]
  end
  subgraph Search[Search Layer]
    SearchPkg["packages/search"]
  end

  BackendPkg --> CorePkg
  BackendPkg --> StoragePkg
  BackendPkg --> AIPkg
  BackendPkg --> ImportPkg
  BackendPkg --> SearchPkg
  BackendPkg --> SharedPkg
  AIPkg --> CorePkg
  AIPkg --> StoragePkg
  AIPkg --> SharedPkg
  StoragePkg --> CorePkg
  StoragePkg --> SharedPkg
  ImportPkg --> CorePkg
  ImportPkg --> StoragePkg
  ImportPkg --> SharedPkg
  SearchPkg --> CorePkg
  SearchPkg --> StoragePkg
  SearchPkg --> AIPkg
  SearchPkg --> SharedPkg
```

## Storage Layer

The storage layer provides persistent local storage for user content, session data, model metadata, and configuration.

### Responsibilities

- Persist user-generated content and imported documents.
- Maintain searchable indexes and cached AI artifacts.
- Store session history and application state.
- Store user preferences, model selections, and privacy settings.

### Storage Layer Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  DocumentStore["Document Store\n(imported + generated content)"]
  SessionStore["Session Store\n(prompt history, conversations)"]
  CacheManager["Cache Manager\n(inference artifacts, temp data)"]
  ConfigStore["Config Store\n(settings, model selections)"]
  ModelStore["Model Store\n(local model files and metadata)"]

  StorageCore["Storage Layer API"]
  StorageCore --> DocumentStore
  StorageCore --> SessionStore
  StorageCore --> CacheManager
  StorageCore --> ConfigStore
  StorageCore --> ModelStore
```

### Storage Layer Patterns

- Use an append-only history model for session data to preserve recoverability.
- Keep content and metadata separate from binary model artifacts.
- Provide transactional update semantics for user settings and model selection.
- Use a local storage abstraction that can map to native desktop storage APIs or file-based persistence.

### Storage Layer Data Flow

- Document imports are written to Document Store and indexed for search.
- User prompts and AI outputs are recorded in Session Store.
- Model metadata and selection state are persisted in Config Store.
- Temporary inference state and caches are handled by Cache Manager.

## AI Layer

The AI layer orchestrates local model execution and manages model lifecycle.

### Responsibilities

- Manage locally available AI models and model metadata.
- Load and unload models according to user selection and resource constraints.
- Execute inference requests and return responses to the backend.
- Monitor local compute resources to avoid overload.

### AI Layer Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  ModelOrchestrator["Model Orchestrator\n(selection, loading)"]
  InferenceEngine["Inference Engine\n(prompt execution"]
  ResourceMonitor["Resource Monitor\n(CPU, mem, GPU)"]
  ModelMetadata["Model Metadata Store\n(capabilities, sizes)"]
  ModelStore["Model Store\n(local weights + files)"]

  Backend["Backend Layer"]
  Backend --> ModelOrchestrator
  ModelOrchestrator --> ModelMetadata
  ModelOrchestrator --> ModelStore
  ModelOrchestrator --> ResourceMonitor
  ModelOrchestrator --> InferenceEngine
  InferenceEngine --> ModelStore
  InferenceEngine --> ResourceMonitor
```

### AI Layer Patterns

- Maintain a model registry that tracks available local models and their resource profiles.
- Separate model selection from inference execution to enable dynamic switching.
- Provide a retry and fallback mechanism when a model fails to load or execute.
- Expose monitoring data for the UI to display performance and status.

## Import Layer

The import layer handles file ingestion and content extraction.

### Responsibilities

- Accept documents from the user and convert them into structured internal representations.
- Extract text, metadata, and attachments from supported formats.
- Normalize imported content for search and AI context.
- Record import operations for audit and reuse.

### Import Layer Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  FileIngestor["File Ingestor\n(file selection, upload)"]
  ParserService["Parser Service\n(text extraction)"]
  ContentNormalizer["Content Normalizer\n(chunking, cleanup)"]
  AuditTrail["Import Audit Trail\n(operation history)"]
  DocumentStore["Document Store"]
  SearchIndexer["Search Indexer"]

  Backend --> FileIngestor
  FileIngestor --> ParserService
  ParserService --> ContentNormalizer
  ContentNormalizer --> DocumentStore
  ContentNormalizer --> SearchIndexer
  FileIngestor --> AuditTrail
```

### Import Layer Patterns

- Use pluggable parsers for new document types.
- Normalize text to preserve semantic context and reduce noise.
- Chunk content to support efficient search and AI retrieval.
- Keep import processing local and offline by default.

## Search Layer

The search layer provides retrieval and semantic search capabilities.

### Responsibilities

- Index imported content and generated output for fast retrieval.
- Perform search queries and return ranked results.
- Use local embeddings to support semantic search and relevance.
- Cache frequently used query results for performance.

### Search Layer Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  Indexer["Indexer\n(index maintenance)"]
  SearchEngine["Search Engine\n(query execution)"]
  EmbeddingService["Embedding Service\n(semantic vectors)"]
  SearchCache["Search Cache\n(cached queries)"]
  DocumentStore["Document Store"]
  AI["AI Layer"]

  Backend --> SearchEngine
  SearchEngine --> Indexer
  SearchEngine --> SearchCache
  SearchEngine --> EmbeddingService
  Indexer --> DocumentStore
  EmbeddingService --> AI
```

### Search Layer Patterns

- Organize indexes by document and session content for efficient retrieval.
- Use embeddings to improve recall and relevance for semantically related queries.
- Cache rich query results to reduce repeated computation.
- Keep search results local and private.

## Application Layer

The application layer is responsible for user interaction, orchestration of workflows, and state management.

### Responsibilities

- Provide the user-facing UI and manage navigation.
- Route user actions to backend services and update the view.
- Maintain the active session and collaboration context.
- Present status, errors, and guidance to the user.

### Application Layer Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart LR
  UIShell["UI Shell\n(main screens, navigation)"]
  InteractionPanel["Interaction Panel\n(prompt entry, response display)"]
  StatusSettings["Status & Settings\n(offline, privacy, models)"]
  HistoryViewer["History Viewer\n(session browsing)"]
  Backend["Backend API\n(service orchestration)"]

  UIShell --> InteractionPanel
  UIShell --> StatusSettings
  UIShell --> HistoryViewer
  InteractionPanel --> Backend
  StatusSettings --> Backend
  HistoryViewer --> Backend
```

## Component Interactions

### C4 Component Diagram

```mermaid
%%{init: { "theme": "base", "themeVariables": { "fontFamily": "Arial" }}}%%
flowchart TD
  subgraph Frontend[Application Layer]
    UI["UI Shell"]
    Interaction["Interaction Panel"]
    Settings["Status & Settings"]
    History["History Viewer"]
  end

  subgraph Runtime[Backend Layer]
    Router["Request Router"]
    Session["Session Manager"]
    Privacy["Privacy Controller"]
    Config["Configuration Service"]
  end

  subgraph LocalAI[AI Layer]
    Orchestrator["Model Orchestrator"]
    Inference["Inference Engine"]
  end

  subgraph LocalData[Storage Layer]
    Docs["Document Store"]
    Sessions["Session Store"]
    ConfigStore["Config Store"]
    Cache["Cache Manager"]
  end

  subgraph DataIngest[Import Layer]
    Ingestor["File Ingestor"]
    Parser["Parser Service"]
    Normalizer["Content Normalizer"]
  end

  subgraph Retrieval[Search Layer]
    Indexer["Indexer"]
    SearchEngine["Search Engine"]
    Embeddings["Embedding Service"]
  end

  UI --> Router
  Interaction --> Router
  Settings --> Config
  Settings --> Privacy
  History --> Session
  Router --> Session
  Router --> Privacy
  Router --> Config
  Router --> Ingestor
  Router --> SearchEngine
  Router --> Orchestrator
  Session --> Sessions
  Config --> ConfigStore
  Privacy --> ConfigStore
  Ingestor --> Parser
  Parser --> Normalizer
  Normalizer --> Docs
  Normalizer --> Indexer
  Indexer --> Docs
  SearchEngine --> Docs
  SearchEngine --> Indexer
  SearchEngine --> Embeddings
  Orchestrator --> Inference
  Inference --> ModelStore
  Inference --> Cache
  Inference --> Sessions
```

## Deployment Considerations

- Brain is built as a desktop application with a bundled frontend and backend runtime.
- Model artifacts are installed locally, and the architecture should support safe storage of model files outside the main application runtime.
- The architecture should support optional external updates for models and the application.
- Local storage paths and permissions should be explicitly managed to ensure private data remains on the device.

## Security and Privacy Considerations

- Keep all user-generated content and imported documents in local storage by default.
- Avoid implicit cloud communication; require explicit user opt-in for any external sync or update.
- Enforce least privilege for file access and data persistence.
- Implement transparent user notifications for data operations and model activity.

## Evolution Strategy

- Start with a stable local architecture that can be extended with optional hybrid features later.
- Keep the core storage, AI, and import boundaries stable to allow future additions without major refactoring.
- Add new model capabilities, search enhancements, and integration points through clearly defined interfaces.
- Preserve the local-first promise while enabling optional cloud-assisted workflows when those features are introduced.
