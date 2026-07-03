"""Document import service that normalizes imported content into domain document objects."""

from pathlib import Path

from brain.importer.base import DocumentImporter
from brain.importer.markdown import MarkdownImporter
from brain.importer.pdf import PDFImporter
from brain.importer.txt import TXTImporter
from brain.shared.exceptions import DocumentImportError
from brain.shared.models import Document


class ImportService:
    """Service responsible for selecting the correct importer and returning normalized documents."""

    def __init__(self) -> None:
        self._importers: list[DocumentImporter] = [PDFImporter(), MarkdownImporter(), TXTImporter()]

    def import_file(self, file_path: Path) -> Document:
        """Import the file and return a normalized Document object.

        Args:
            file_path: Path to the target file.

        Returns:
            A normalized Document object containing raw text and metadata.

        Raises:
            DocumentImportError: If the file type is unsupported or the imported file fails.
        """
        selected_importer = self._get_importer_for_path(file_path)
        if selected_importer is None:
            raise DocumentImportError(f"Unsupported file type: {file_path.suffix}")

        return selected_importer.import_file(file_path)

    def _get_importer_for_path(self, file_path: Path) -> DocumentImporter | None:
        for importer in self._importers:
            if importer.supports(file_path):
                return importer
        return None
