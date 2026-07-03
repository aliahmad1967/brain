"""Plain text file importer for the Brain platform."""

from pathlib import Path

from brain.importer.base import DocumentImporter
from brain.shared.exceptions import DocumentImportError
from brain.shared.models import Document


class TXTImporter(DocumentImporter):
    """Importer for plain text files that returns normalized document objects."""

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".txt"

    def import_file(self, file_path: Path) -> Document:
        if not file_path.exists():
            raise DocumentImportError(f"Text file not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
            return Document(
                name=file_path.name,
                file_path=str(file_path.resolve()),
                file_type="text",
                content=content,
            )
        except Exception as exc:
            raise DocumentImportError(f"Error parsing text file at {file_path}: {exc}") from exc
