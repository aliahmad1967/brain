"""Unit tests for the document importer package."""

from pathlib import Path

from brain.importer.markdown import MarkdownImporter
from brain.importer.pdf import PDFImporter
from brain.importer.service import ImportService
from brain.importer.txt import TXTImporter
from brain.shared.exceptions import DocumentImportError
from pypdf import PdfWriter


def test_markdown_importer_supports() -> None:
    importer = MarkdownImporter()
    assert importer.supports(Path("doc.md")) is True
    assert importer.supports(Path("doc.markdown")) is True
    assert importer.supports(Path("doc.pdf")) is False


def test_markdown_importer_parsing(tmp_path: Path) -> None:
    importer = MarkdownImporter()
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "---\n"
        "title: Test Markdown Doc\n"
        "version: 1\n"
        "is_draft: false\n"
        "---\n"
        "# Main Heading\n"
        "This is paragraph text.",
        encoding="utf-8",
    )

    doc = importer.import_file(test_file)
    assert doc.name == "test.md"
    assert doc.file_type == "markdown"
    assert doc.meta_info["title"] == "Test Markdown Doc"
    assert doc.meta_info["version"] == 1
    assert doc.meta_info["is_draft"] is False
    assert "# Main Heading" in doc.content
    assert "This is paragraph text." in doc.content


def test_txt_importer_supports_and_parses(tmp_path: Path) -> None:
    importer = TXTImporter()
    test_file = tmp_path / "notes.txt"
    test_file.write_text("Sample text content.\nLine two.", encoding="utf-8")

    assert importer.supports(test_file) is True
    assert importer.supports(Path("notes.md")) is False

    doc = importer.import_file(test_file)
    assert doc.name == "notes.txt"
    assert doc.file_type == "text"
    assert "Sample text content." in doc.content


def test_pdf_importer_supports_and_parses(tmp_path: Path) -> None:
    importer = PDFImporter()
    test_file = tmp_path / "report.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with test_file.open("wb") as handle:
        writer.write(handle)

    assert importer.supports(test_file) is True
    assert importer.supports(Path("report.md")) is False

    doc = importer.import_file(test_file)
    assert doc.name == "report.pdf"
    assert doc.file_type == "pdf"
    assert doc.meta_info["page_count"] == 1
    assert isinstance(doc.content, str)


def test_import_service_dispatches_to_correct_importer(tmp_path: Path) -> None:
    service = ImportService()

    md_file = tmp_path / "doc.md"
    md_file.write_text("# Title\nHello world", encoding="utf-8")
    md_doc = service.import_file(md_file)
    assert md_doc.file_type == "markdown"

    txt_file = tmp_path / "story.txt"
    txt_file.write_text("Offline notes.", encoding="utf-8")
    txt_doc = service.import_file(txt_file)
    assert txt_doc.file_type == "text"

    pdf_file = tmp_path / "report.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_file.open("wb") as handle:
        writer.write(handle)

    pdf_doc = service.import_file(pdf_file)
    assert pdf_doc.file_type == "pdf"


def test_import_service_rejects_unsupported_file_type(tmp_path: Path) -> None:
    service = ImportService()
    test_file = tmp_path / "data.bin"
    test_file.write_bytes(b"012345")

    try:
        service.import_file(test_file)
        assert False, "Expected DocumentImportError for unsupported file type"
    except DocumentImportError as exc:
        assert "Unsupported file type" in str(exc)
