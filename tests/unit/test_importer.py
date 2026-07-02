"""Unit tests for the document importer package."""

from pathlib import Path

from brain.importer.markdown import MarkdownImporter


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
