# Brain development environment setup
# Run from repository root: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "Setting up Brain development environment..." -ForegroundColor Cyan

# Check uv
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not installed. Install it from https://docs.astral.sh/uv/"
    exit 1
}

# Sync dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
uv sync --dev

# Verify tooling
Write-Host "Verifying tooling..." -ForegroundColor Yellow
uv run ruff --version
uv run black --version
uv run mypy --version
uv run pytest --version

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  uv run ruff check .        - Lint all code"
Write-Host "  uv run black --check .     - Check formatting"
Write-Host "  uv run black .             - Format code"
Write-Host "  uv run mypy packages/      - Type check"
Write-Host "  uv run pytest              - Run tests"
