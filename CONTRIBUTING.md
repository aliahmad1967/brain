# Contributing to Brain

Thank you for considering contributing to Brain! This document outlines the guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

1. **Fork the repository** and create a branch from `main`.
2. **Set up your development environment:**
   ```bash
   uv sync --dev
   ```
3. **Run the quality checks** before submitting:
   ```bash
   uv run ruff check .
   uv run black --check .
   uv run mypy packages/
   uv run pytest
   ```

## Development Workflow

### Branch Naming

- `feature/<short-description>` — New features
- `fix/<short-description>` — Bug fixes
- `refactor/<short-description>` — Code improvements
- `docs/<short-description>` — Documentation changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`

### Before Submitting

- Ensure all existing tests pass: `uv run pytest`
- Ensure type correctness: `uv run mypy packages/`
- Ensure lint compliance: `uv run ruff check .`
- Ensure formatting compliance: `uv run black --check .`
- Write tests for new functionality
- Update documentation if necessary

## Code Standards

- **Python 3.13+** — Use modern Python features (pattern matching, type unions with `|`)
- **Type hints** — Required for all function signatures and module-level variables
- **SOLID principles** — Especially single responsibility and dependency inversion
- **Modular design** — Follow the existing package structure; avoid circular imports
- **No TODOs in committed code** — Address or track them properly
- **No placeholder code** — Every function must have a real implementation

## Architecture Guidelines

- Each package in `packages/` should have a clear, single responsibility
- Cross-package dependencies should flow through the `shared` package or the `core` event system
- The `shared` package must not import from any other Brain package
- Write integration tests that verify cross-package behavior
- Keep the `backend` package thin — it should only wire together core, ai, importer, search, and storage

## Review Process

1. Maintainers will review your PR within a few business days
2. All CI checks must pass
3. At least one maintainer approval is required for merge
4. Address review feedback promptly; use fixup commits during review

## Questions?

Open a [Discussion](https://github.com/your-org/brain/discussions) or join our community chat.
