"""PDF document importer implementation."""

from pathlib import Path

from brain.importer.base import DocumentImporter
from brain.shared.exceptions import DocumentImportError
from brain.shared.models import Document
from pypdf import PdfReader


class PDFImporter(DocumentImporter):
    """Parses PDF documents to extract text content and metadata."""

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def import_file(self, file_path: Path) -> Document:
        if not file_path.exists():
            raise DocumentImportError(f"PDF file not found: {file_path}")

        try:
            reader = PdfReader(str(file_path))
            text_segments = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_segments.append(text)

            content = "\n\n".join(text_segments)

            # Extract basic PDF metadata
            meta_info: dict[str, str | int | float | bool] = {
                "page_count": len(reader.pages),
            }

            info = reader.metadata
            if info:
                for key, value in info.items():
                    clean_key = key.lstrip("/").lower()
                    # Only map standard primitive values
                    if isinstance(value, str | int | float | bool):
                        meta_info[clean_key] = value

            return Document(
                name=file_path.name,
                file_path=str(file_path.resolve()),
                file_type="pdf",
                content=content,
                meta_info=meta_info,
            )
        except Exception as e:
            raise DocumentImportError(f"Error parsing PDF file at {file_path}: {e}") from e
