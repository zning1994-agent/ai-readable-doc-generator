"""Document model for complete document representation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ai_readable_doc_generator.models.section import Section


@dataclass
class Document:
    """Represents a complete document with metadata and sections.

    Attributes:
        title: Document title.
        source_format: Original format of the document (e.g., 'markdown').
        content: Raw document content.
        sections: Parsed sections of the document.
        metadata: Document-level metadata.
        created_at: Timestamp when document was created.
        source_path: Optional path to source file.
    """

    title: str = ""
    source_format: str = "markdown"
    content: str = ""
    sections: list[Section] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    source_path: str | None = None

    def add_section(self, section: Section) -> None:
        """Add a section to the document.

        Args:
            section: The section to add.
        """
        self.sections.append(section)

    def get_headings(self) -> list[Section]:
        """Get all heading sections from the document.

        Returns:
            List of heading sections in document order.
        """
        return [
            s for s in self.sections
            if s.section_type.value in ("title", "heading")
        ]

    def get_table_of_contents(self) -> list[dict[str, Any]]:
        """Generate table of contents from headings.

        Returns:
            List of heading entries with level and content.
        """
        toc = []
        for section in self.get_headings():
            toc.append({
                "level": section.level,
                "content": section.content,
                "line_number": section.line_number,
            })
        return toc

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation.

        Returns:
            Dictionary containing document data.
        """
        return {
            "title": self.title,
            "source_format": self.source_format,
            "content": self.content,
            "sections": [section.to_dict() for section in self.sections],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create document from dictionary representation.

        Args:
            data: Dictionary containing document data.

        Returns:
            Document instance.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            title=data.get("title", ""),
            source_format=data.get("source_format", "markdown"),
            content=data.get("content", ""),
            sections=[
                Section.from_dict(s) for s in data.get("sections", [])
            ],
            metadata=data.get("metadata", {}),
            created_at=created_at or datetime.now(),
            source_path=data.get("source_path"),
        )
