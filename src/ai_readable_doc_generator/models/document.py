"""Document model for AI-readable document representation."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ai_readable_doc_generator.models.section import ContentType, Section, SemanticTag
from ai_readable_doc_generator.models.schema import OutputFormat, SchemaDefinition, SchemaValidator


@dataclass
class DocumentMetadata:
    """Metadata for a document."""

    author: str | None = None
    version: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    language: str = "en"
    license: str | None = None
    tags: list[str] = field(default_factory=list)
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "language": self.language,
            "license": self.license,
            "tags": self.tags,
            **self.custom,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """Create from dictionary representation."""
        known_fields = {"author", "version", "created_at", "updated_at", "language", "license", "tags"}
        custom = {k: v for k, v in data.items() if k not in known_fields}
        return cls(
            author=data.get("author"),
            version=data.get("version"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            language=data.get("language", "en"),
            license=data.get("license"),
            tags=data.get("tags", []),
            custom=custom,
        )


@dataclass
class Document:
    """A document with semantic tagging for AI readability."""

    title: str
    content_type: ContentType = ContentType.OTHER
    sections: list[Section] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    semantic_tags: list[SemanticTag] = field(default_factory=list)
    source_path: str | None = None

    def add_section(self, section: Section) -> None:
        """Add a section to the document."""
        self.sections.append(section)

    def add_semantic_tag(self, tag: SemanticTag) -> None:
        """Add a global semantic tag to the document."""
        self.semantic_tags.append(tag)

    def get_all_tags(self) -> list[SemanticTag]:
        """Get all semantic tags from document and sections."""
        tags = list(self.semantic_tags)
        for section in self.sections:
            tags.extend(section.get_all_tags())
        return tags

    def get_text_content(self) -> str:
        """Get all text content from the document."""
        parts = [self.title]
        for section in self.sections:
            parts.append(section.get_text_content())
        return "\n\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "content_type": self.content_type.value,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata.to_dict(),
            "semantic_tags": [t.to_dict() for t in self.semantic_tags],
            "source_path": self.source_path,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create from dictionary representation."""
        content_type = ContentType(data.get("content_type", "other"))
        sections = [Section.from_dict(s) for s in data.get("sections", [])]
        metadata = DocumentMetadata.from_dict(data.get("metadata", {}))
        semantic_tags = [SemanticTag.from_dict(t) for t in data.get("semantic_tags", [])]

        return cls(
            title=data.get("title", ""),
            content_type=content_type,
            sections=sections,
            metadata=metadata,
            semantic_tags=semantic_tags,
            source_path=data.get("source_path"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Document":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the document structure.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if not self.title:
            errors.append("Document title is required")

        if not self.sections:
            errors.append("Document must have at least one section")

        # Validate sections
        for i, section in enumerate(self.sections):
            if not section.content and not section.heading:
                errors.append(f"Section {i} has no content or heading")

        return len(errors) == 0, errors

    def get_headings(self) -> list[tuple[int, str]]:
        """Get all headings with their levels.

        Returns:
            List of (level, heading_text) tuples
        """
        headings = []
        for section in self.sections:
            if section.is_heading_section() and section.heading:
                headings.append((section.level, section.heading))
            for child in section.children:
                if child.is_heading_section() and child.heading:
                    headings.append((child.level, child.heading))
        return headings

    def get_code_sections(self) -> list[Section]:
        """Get all code sections."""
        code_sections = []
        for section in self.sections:
            if section.is_code_section():
                code_sections.append(section)
            code_sections.extend(section.children)
        return code_sections

    def export(self, format: OutputFormat) -> str:
        """Export document in specified format.

        Args:
            format: The output format

        Returns:
            Formatted string representation
        """
        if format == OutputFormat.JSON:
            return self.to_json()
        elif format == OutputFormat.YAML:
            import yaml

            return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        elif format == OutputFormat.MARKDOWN:
            return self._to_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = [f"# {self.title}\n"]

        for section in self.sections:
            lines.append(self._section_to_markdown(section))

        return "\n".join(lines)

    def _section_to_markdown(self, section: Section) -> str:
        """Convert a section to Markdown."""
        lines = []

        if section.heading:
            heading_prefix = "#" * section.level
            lines.append(f"{heading_prefix} {section.heading}\n")

        if section.content:
            lines.append(f"{section.content}\n")

        for child in section.children:
            lines.append(self._section_to_markdown(child))

        return "\n".join(lines)
