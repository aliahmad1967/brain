"""Markdown document importer implementation."""

import re
from pathlib import Path

from brain.importer.base import DocumentImporter
from brain.shared.exceptions import DocumentImportError
from brain.shared.models import Document


class MarkdownImporter(DocumentImporter):
    """Parses Markdown documents to extract text content and optional frontmatter metadata."""

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".md", ".markdown")

    def import_file(self, file_path: Path) -> Document:
        if not file_path.exists():
            raise DocumentImportError(f"Markdown file not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
            meta_info: dict[str, str | int | float | bool] = {}
            body = content

            # Regex to match YAML frontmatter (between opening and closing '---')
            frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)
                body = content[frontmatter_match.end() :]

                # Parse simple YAML frontmatter key-value pairs without external dependency
                for line in frontmatter_text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or ":" not in line:
                        continue

                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")

                    if val.lower() == "true":
                        meta_info[key] = True
                    elif val.lower() == "false":
                        meta_info[key] = False
                    else:
                        try:
                            if "." in val:
                                meta_info[key] = float(val)
                            else:
                                meta_info[key] = int(val)
                        except ValueError:
                            meta_info[key] = val

            return Document(
                name=file_path.name,
                file_path=str(file_path.resolve()),
                file_type="markdown",
                content=body,
                meta_info=meta_info,
            )
        except Exception as e:
            raise DocumentImportError(f"Error parsing Markdown file at {file_path}: {e}") from e
