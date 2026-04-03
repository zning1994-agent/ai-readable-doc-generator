"""Document converters for different input formats."""

import json
import re
from typing import Any, Optional

from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.renderer import RendererHTML

from .base import BaseConverter, ConversionOptions, ConversionResult


class MarkdownConverter(BaseConverter):
    """Converter for Markdown documents to AI-readable JSON format."""

    def __init__(self, options: Optional[ConversionOptions] = None):
        """Initialize Markdown converter.

        Args:
            options: Configuration options for conversion.
        """
        super().__init__(options)
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": True})

    def validate(self, content: str) -> bool:
        """Validate Markdown content.

        Args:
            content: The Markdown content to validate.

        Returns:
            True if valid Markdown, False otherwise.
        """
        if not content or not content.strip():
            return False
        try:
            self.md.parse(content)
            return True
        except Exception:
            return False

    def convert(self, content: str) -> ConversionResult:
        """Convert Markdown content to AI-readable JSON format.

        Args:
            content: The Markdown content to convert.

        Returns:
            ConversionResult with structured JSON output.
        """
        errors = []
        warnings = []

        if not content:
            errors.append("Empty content provided")
            return ConversionResult(success=False, content="", errors=errors)

        try:
            tokens = self.md.parse(content)
            structure = self._parse_markdown_structure(tokens, content)
            result = self._build_json_output(structure, content)
            return ConversionResult(success=True, content=result, metadata={"format": "markdown"})
        except Exception as e:
            errors.append(f"Conversion failed: {str(e)}")
            return ConversionResult(success=False, content="", errors=errors)

    def _parse_markdown_structure(self, tokens: list[Token], content: str) -> dict[str, Any]:
        """Parse Markdown tokens into structured data.

        Args:
            tokens: Parsed Markdown tokens.
            content: Original Markdown content.

        Returns:
            Structured dictionary representation.
        """
        sections = []
        current_section = None
        section_stack = []

        for token in tokens:
            if token.type == "heading_open":
                level = int(token.tag[1]) if token.tag.startswith("h") else 1
                heading_text = ""
                section_type = self._classify_heading(level)
            elif token.type == "inline" and current_section is not None:
                heading_text = token.content
            elif token.type == "heading_close":
                if current_section:
                    if self.options.max_heading_depth and level > self.options.max_heading_depth:
                        warnings.append(f"Skipping heading at depth {level}")
                        continue
                    sections.append(current_section)
                current_section = {
                    "type": "heading",
                    "level": level,
                    "content": heading_text,
                    "section_type": section_type,
                    "children": [],
                }
            elif token.type == "paragraph_open":
                if current_section is None:
                    current_section = {"type": "paragraph", "content": "", "children": []}
            elif token.type == "inline" and current_section and current_section["type"] == "paragraph":
                current_section["content"] = token.content
                sections.append(current_section)
                current_section = None
            elif token.type == "code_block" or token.type == "fence":
                code_content = token.content
                lang = token.info or "text"
                sections.append({
                    "type": "code",
                    "language": lang,
                    "content": code_content,
                })
            elif token.type == "blockquote_open":
                if current_section is None:
                    current_section = {"type": "blockquote", "content": "", "children": []}
            elif token.type == "blockquote_close":
                if current_section and current_section["type"] == "blockquote":
                    sections.append(current_section)
                    current_section = None
            elif token.type == "list_open":
                list_type = "ordered" if token.tag == "ol" else "unordered"
                if current_section:
                    current_section["children"].append({"type": "list_start", "list_type": list_type})
            elif token.type == "list_item_open":
                if current_section:
                    current_section["children"].append({"type": "list_item"})
            elif token.type == "list_close":
                pass
            elif token.type == "hr":
                sections.append({"type": "horizontal_rule"})

        if current_section:
            sections.append(current_section)

        return {"sections": sections}

    def _classify_heading(self, level: int) -> str:
        """Classify heading level to semantic type.

        Args:
            level: Heading level (1-6).

        Returns:
            Semantic type string.
        """
        classification = {
            1: "title",
            2: "section",
            3: "subsection",
            4: "paragraph",
            5: "detail",
            6: "note",
        }
        return classification.get(level, "unknown")

    def _build_json_output(self, structure: dict[str, Any], original: str) -> str:
        """Build JSON output from parsed structure.

        Args:
            structure: Parsed document structure.
            original: Original content.

        Returns:
            JSON string representation.
        """
        output = {
            "document": {
                "original_length": len(original),
                "section_count": len(structure.get("sections", [])),
            },
            "sections": structure.get("sections", []),
        }

        if self.options.include_metadata:
            output["metadata"] = {
                "source_format": "markdown",
                "semantic_tagging_enabled": self.options.semantic_tagging,
                "preserve_formatting": self.options.preserve_formatting,
            }

        if self.options.include_toc:
            output["table_of_contents"] = self._build_toc(structure)

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _build_toc(self, structure: dict[str, Any]) -> list[dict[str, Any]]:
        """Build table of contents from structure.

        Args:
            structure: Parsed document structure.

        Returns:
            List of TOC entries.
        """
        toc = []
        for section in structure.get("sections", []):
            if section.get("type") == "heading":
                toc.append({
                    "level": section.get("level", 1),
                    "title": section.get("content", ""),
                    "section_type": section.get("section_type", "unknown"),
                })
        return toc

    def get_supported_formats(self) -> list[str]:
        """Get supported input formats."""
        return ["md", "markdown", "mdown"]

    def get_output_format(self) -> str:
        """Get output format."""
        return "json"


class HTMLConverter(BaseConverter):
    """Converter for HTML documents to AI-readable JSON format."""

    def __init__(self, options: Optional[ConversionOptions] = None):
        """Initialize HTML converter.

        Args:
            options: Configuration options for conversion.
        """
        super().__init__(options)
        try:
            from bs4 import BeautifulSoup
            self.bs4 = BeautifulSoup
        except ImportError:
            self.bs4 = None

    def validate(self, content: str) -> bool:
        """Validate HTML content.

        Args:
            content: The HTML content to validate.

        Returns:
            True if valid HTML, False otherwise.
        """
        if not content or not content.strip():
            return False
        if self.bs4 is None:
            return False
        try:
            self.bs4(content, "html.parser")
            return True
        except Exception:
            return False

    def convert(self, content: str) -> ConversionResult:
        """Convert HTML content to AI-readable JSON format.

        Args:
            content: The HTML content to convert.

        Returns:
            ConversionResult with structured JSON output.
        """
        errors = []
        warnings = []

        if not content:
            errors.append("Empty content provided")
            return ConversionResult(success=False, content="", errors=errors)

        if self.bs4 is None:
            errors.append("BeautifulSoup4 is required for HTML conversion")
            return ConversionResult(success=False, content="", errors=errors)

        try:
            soup = self.bs4(content, "html.parser")
            structure = self._parse_html_structure(soup)
            result = self._build_json_output(structure, content)
            return ConversionResult(success=True, content=result, metadata={"format": "html"})
        except Exception as e:
            errors.append(f"Conversion failed: {str(e)}")
            return ConversionResult(success=False, content="", errors=errors)

    def _parse_html_structure(self, soup) -> dict[str, Any]:
        """Parse HTML soup into structured data.

        Args:
            soup: BeautifulSoup parsed document.

        Returns:
            Structured dictionary representation.
        """
        sections = []

        # Parse headings
        for i in range(1, 7):
            for heading in soup.find_all(f"h{i}"):
                text = self._clean_text(heading.get_text())
                if text:
                    sections.append({
                        "type": "heading",
                        "level": i,
                        "content": text,
                        "section_type": self._classify_heading(i),
                    })

        # Parse paragraphs
        for p in soup.find_all("p"):
            text = self._clean_text(p.get_text())
            if text:
                sections.append({
                    "type": "paragraph",
                    "content": text,
                })

        # Parse code blocks
        for pre in soup.find_all("pre"):
            code = pre.find("code")
            lang = ""
            if code and code.get("class"):
                classes = code.get("class", [])
                for cls in classes:
                    if cls.startswith("language-"):
                        lang = cls[9:]
                        break
            text = self._clean_text(code.get_text() if code else pre.get_text())
            sections.append({
                "type": "code",
                "language": lang,
                "content": text,
            })

        # Parse lists
        for ul in soup.find_all("ul"):
            items = []
            for li in ul.find_all("li"):
                text = self._clean_text(li.get_text())
                if text:
                    items.append(text)
            if items:
                sections.append({
                    "type": "list",
                    "list_type": "unordered",
                    "items": items,
                })

        for ol in soup.find_all("ol"):
            items = []
            for li in ol.find_all("li"):
                text = self._clean_text(li.get_text())
                if text:
                    items.append(text)
            if items:
                sections.append({
                    "type": "list",
                    "list_type": "ordered",
                    "items": items,
                })

        # Parse blockquotes
        for blockquote in soup.find_all("blockquote"):
            text = self._clean_text(blockquote.get_text())
            if text:
                sections.append({
                    "type": "blockquote",
                    "content": text,
                })

        # Parse tables
        for table in soup.find_all("table"):
            table_data = self._parse_table(table)
            if table_data:
                sections.append({
                    "type": "table",
                    "headers": table_data["headers"],
                    "rows": table_data["rows"],
                })

        return {"sections": sections}

    def _parse_table(self, table) -> dict[str, Any]:
        """Parse HTML table into structured data.

        Args:
            table: BeautifulSoup table element.

        Returns:
            Dictionary with headers and rows.
        """
        headers = []
        rows = []

        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
            if header_row:
                for th in header_row.find_all(["th", "td"]):
                    headers.append(self._clean_text(th.get_text()))

        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            if thead and tr == thead.find_parent("tr"):
                continue
            row = []
            for td in tr.find_all(["td", "th"]):
                row.append(self._clean_text(td.get_text()))
            if row:
                rows.append(row)

        return {"headers": headers, "rows": rows}

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace.

        Args:
            text: Raw text.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def _classify_heading(self, level: int) -> str:
        """Classify heading level to semantic type.

        Args:
            level: Heading level (1-6).

        Returns:
            Semantic type string.
        """
        classification = {
            1: "title",
            2: "section",
            3: "subsection",
            4: "paragraph",
            5: "detail",
            6: "note",
        }
        return classification.get(level, "unknown")

    def _build_json_output(self, structure: dict[str, Any], original: str) -> str:
        """Build JSON output from parsed structure.

        Args:
            structure: Parsed document structure.
            original: Original content.

        Returns:
            JSON string representation.
        """
        output = {
            "document": {
                "original_length": len(original),
                "section_count": len(structure.get("sections", [])),
            },
            "sections": structure.get("sections", []),
        }

        if self.options.include_metadata:
            output["metadata"] = {
                "source_format": "html",
                "semantic_tagging_enabled": self.options.semantic_tagging,
                "preserve_formatting": self.options.preserve_formatting,
            }

        if self.options.include_toc:
            output["table_of_contents"] = self._build_toc(structure)

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _build_toc(self, structure: dict[str, Any]) -> list[dict[str, Any]]:
        """Build table of contents from structure.

        Args:
            structure: Parsed document structure.

        Returns:
            List of TOC entries.
        """
        toc = []
        for section in structure.get("sections", []):
            if section.get("type") == "heading":
                toc.append({
                    "level": section.get("level", 1),
                    "title": section.get("content", ""),
                    "section_type": section.get("section_type", "unknown"),
                })
        return toc

    def get_supported_formats(self) -> list[str]:
        """Get supported input formats."""
        return ["html", "htm"]

    def get_output_format(self) -> str:
        """Get output format."""
        return "json"


class PlaintextConverter(BaseConverter):
    """Converter for plain text documents to AI-readable JSON format."""

    def __init__(self, options: Optional[ConversionOptions] = None):
        """Initialize Plaintext converter.

        Args:
            options: Configuration options for conversion.
        """
        super().__init__(options)

    def validate(self, content: str) -> bool:
        """Validate plain text content.

        Args:
            content: The text content to validate.

        Returns:
            Always True for plain text, as any string is valid.
        """
        return content is not None

    def convert(self, content: str) -> ConversionResult:
        """Convert plain text content to AI-readable JSON format.

        Args:
            content: The plain text content to convert.

        Returns:
            ConversionResult with structured JSON output.
        """
        errors = []

        if content is None:
            errors.append("Content cannot be None")
            return ConversionResult(success=False, content="", errors=errors)

        try:
            structure = self._parse_text_structure(content)
            result = self._build_json_output(structure, content)
            return ConversionResult(success=True, content=result, metadata={"format": "plaintext"})
        except Exception as e:
            errors.append(f"Conversion failed: {str(e)}")
            return ConversionResult(success=False, content="", errors=errors)

    def _parse_text_structure(self, content: str) -> dict[str, Any]:
        """Parse plain text into structured data.

        Args:
            content: Plain text content.

        Returns:
            Structured dictionary representation.
        """
        lines = content.split("\n")
        sections = []
        current_paragraph: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Check if line is a heading (all caps or starts with #)
            if stripped.startswith("#"):
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

                heading_text = stripped.lstrip("#").strip()
                level = len(stripped) - len(stripped.lstrip("#"))
                sections.append({
                    "type": "heading",
                    "level": min(level, 6),
                    "content": heading_text,
                    "section_type": self._classify_heading(min(level, 6)),
                })

            # Check for markdown-style heading (underlined with === or ---)
            elif stripped == "=" * len(stripped) if stripped else False:
                if current_paragraph and len(sections) > 0:
                    prev = sections[-1]
                    if prev["type"] == "paragraph":
                        sections[-1] = {
                            "type": "heading",
                            "level": 1,
                            "content": prev["content"],
                            "section_type": "title",
                        }
                        current_paragraph = []
                continue

            elif stripped == "-" * len(stripped) if stripped else False:
                if current_paragraph and len(sections) > 0:
                    prev = sections[-1]
                    if prev["type"] == "paragraph":
                        sections[-1] = {
                            "type": "heading",
                            "level": 2,
                            "content": prev["content"],
                            "section_type": "section",
                        }
                        current_paragraph = []
                continue

            # Check for list items
            elif stripped.startswith(("- ", "* ", "+ ")):
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

                item_text = stripped[2:].strip()
                sections.append({
                    "type": "list_item",
                    "list_type": "unordered",
                    "content": item_text,
                })

            # Check for numbered list items
            elif re.match(r"^\d+[\.\)]\s", stripped):
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

                item_text = re.sub(r"^\d+[\.\)]\s", "", stripped)
                sections.append({
                    "type": "list_item",
                    "list_type": "ordered",
                    "content": item_text,
                })

            # Check for blockquote
            elif stripped.startswith(">"):
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

                quote_text = stripped.lstrip(">").strip()
                sections.append({
                    "type": "blockquote",
                    "content": quote_text,
                })

            # Check for horizontal rule
            elif re.match(r"^[-*_]{3,}$", stripped):
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

                sections.append({
                    "type": "horizontal_rule",
                })

            # Empty line - end current paragraph
            elif not stripped:
                if current_paragraph:
                    sections.append({
                        "type": "paragraph",
                        "content": " ".join(current_paragraph),
                    })
                    current_paragraph = []

            # Regular text - add to current paragraph
            else:
                current_paragraph.append(stripped)

        # Handle remaining paragraph
        if current_paragraph:
            sections.append({
                "type": "paragraph",
                "content": " ".join(current_paragraph),
            })

        return {"sections": sections}

    def _classify_heading(self, level: int) -> str:
        """Classify heading level to semantic type.

        Args:
            level: Heading level (1-6).

        Returns:
            Semantic type string.
        """
        classification = {
            1: "title",
            2: "section",
            3: "subsection",
            4: "paragraph",
            5: "detail",
            6: "note",
        }
        return classification.get(level, "unknown")

    def _build_json_output(self, structure: dict[str, Any], original: str) -> str:
        """Build JSON output from parsed structure.

        Args:
            structure: Parsed document structure.
            original: Original content.

        Returns:
            JSON string representation.
        """
        output = {
            "document": {
                "original_length": len(original),
                "line_count": len(original.split("\n")),
                "section_count": len(structure.get("sections", [])),
            },
            "sections": structure.get("sections", []),
        }

        if self.options.include_metadata:
            output["metadata"] = {
                "source_format": "plaintext",
                "semantic_tagging_enabled": self.options.semantic_tagging,
                "preserve_formatting": self.options.preserve_formatting,
            }

        if self.options.include_toc:
            output["table_of_contents"] = self._build_toc(structure)

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _build_toc(self, structure: dict[str, Any]) -> list[dict[str, Any]]:
        """Build table of contents from structure.

        Args:
            structure: Parsed document structure.

        Returns:
            List of TOC entries.
        """
        toc = []
        for section in structure.get("sections", []):
            if section.get("type") == "heading":
                toc.append({
                    "level": section.get("level", 1),
                    "title": section.get("content", ""),
                    "section_type": section.get("section_type", "unknown"),
                })
        return toc

    def get_supported_formats(self) -> list[str]:
        """Get supported input formats."""
        return ["txt", "text", "plain"]

    def get_output_format(self) -> str:
        """Get output format."""
        return "json"
