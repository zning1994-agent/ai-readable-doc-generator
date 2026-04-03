"""Document model for complete document representation."""

from datetime import datetime
from typing import Any

from ai_readable_doc_generator.models.section import Section


class Document:
    """Represents a complete document with metadata and sections.

    Attributes:
        title: The document title.
        sections: List of top-level sections in the document.
        metadata: Document-level metadata.
        source_path: Path to the source file (if applicable).
        source_format: Format of the source document (e.g., 'markdown').
        created_at: Timestamp when the document was created.
        updated_at: Timestamp when the document was last modified.
        tags: Document-level semantic tags.
        language: Document language code (e.g., 'en', 'zh').
    """

    def __init__(
        self,
        title: str = "",
        sections: list[Section] | None = None,
        metadata: dict[str, Any] | None = None,
        source_path: str | None = None,
        source_format: str = "markdown",
        tags: list[str] | None = None,
        language: str = "en",
    ) -> None:
        """Initialize a Document.

        Args:
            title: The document title.
            sections: List of sections in the document.
            metadata: Document-level metadata.
            source_path: Path to the source file.
            source_format: Format of the source document.
            tags: Document-level semantic tags.
            language: Document language code.
        """
        self.title = title
        self.sections = sections or []
        self.metadata = metadata or {}
        self.source_path = source_path
        self.source_format = source_format
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.tags = tags or []
        self.language = language

    def add_section(self, section: Section) -> None:
        """Add a section to the document.

        Args:
            section: The section to add.
        """
        self.sections.append(section)
        self.updated_at = datetime.now()

    def get_all_sections(self, flatten: bool = True) -> list[Section]:
        """Get all sections, optionally flattened.

        Args:
            flatten: Whether to flatten nested sections.

        Returns:
            List of sections.
        """
        if not flatten:
            return self.sections.copy()

        result: list[Section] = []
        for section in self.sections:
            result.append(section)
            if section.children:
                result.extend(self._flatten_sections(section.children))
        return result

    @staticmethod
    def _flatten_sections(sections: list[Section]) -> list[Section]:
        """Recursively flatten sections list.

        Args:
            sections: List of sections to flatten.

        Returns:
            Flattened list of sections.
        """
        result: list[Section] = []
        for section in sections:
            result.append(section)
            if section.children:
                result.extend(Document._flatten_sections(section.children))
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation.

        Returns:
            Dictionary containing document data.
        """
        return {
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
            "metadata": self.metadata,
            "source_path": self.source_path,
            "source_format": self.source_format,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create a Document from dictionary data.

        Args:
            data: Dictionary containing document data.

        Returns:
            A new Document instance.
        """
        sections = [Section.from_dict(s) for s in data.get("sections", [])]
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        doc = cls(
            title=data.get("title", ""),
            sections=sections,
            metadata=data.get("metadata", {}),
            source_path=data.get("source_path"),
            source_format=data.get("source_format", "markdown"),
            tags=data.get("tags", []),
            language=data.get("language", "en"),
        )

        if created_at:
            doc.created_at = datetime.fromisoformat(created_at)
        if updated_at:
            doc.updated_at = datetime.fromisoformat(updated_at)

        return doc

    def __repr__(self) -> str:
        """Return string representation of Document."""
        return f"Document(title={self.title!r}, sections={len(self.sections)})"
