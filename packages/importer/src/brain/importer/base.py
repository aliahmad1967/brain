"""Base interface for document importers."""

from abc import ABC, abstractmethod
from pathlib import Path

from brain.shared.models import Document


class DocumentImporter(ABC):
    """Abstract base class that all document importers must implement."""

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Check if the given file type is supported by this importer.

        Args:
            file_path: Path to the target file.

        Returns:
            True if the file can be processed, False otherwise.
        """
        pass

    @abstractmethod
    def import_file(self, file_path: Path) -> Document:
        """Import and parse a file into a Document domain object.

        Args:
            file_path: Path to the target file on the local filesystem.

        Returns:
            A populated Document object containing metadata and text content.

        Raises:
            DocumentImportError: If reading or parsing the file fails.
        """
        pass
