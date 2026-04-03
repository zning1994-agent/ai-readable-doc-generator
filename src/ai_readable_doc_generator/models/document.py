"""Document model definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ai_readable_doc_generator.models.section import Section


@dataclass
class DocumentMetadata:
    """
    Metadata for a document.

    Attributes:
        title: Document title.
        author: Document author.
        created_at: Creation timestamp.
        modified_at: Last modification timestamp.
        source_path: Original file path.
        source_format: Original format (markdown, plaintext, etc.).
        word_count: Total word count.
        line_count: Total line count.
        tags: List of document tags.
        custom: Custom metadata dictionary.
    """

    title: str = ""
    author: str = ""
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    source_path: str = ""
    source_format: str = "plaintext"
    word_count: int = 0
    line_count: int = 0
    tags: list[str] = field(default_factory=list)
    custom: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata.
        """
        return {
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "source_path": self.source_path,
            "source_format": self.source_format,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "tags": self.tags,
            "custom": self.custom,
        }


@dataclass
class Document:
    """
    Represents a complete document with sections and metadata.

    Attributes:
        metadata: Document metadata.
        sections: List of top-level sections.
        raw_content: Original unprocessed content.
        relationships: Document-level relationships.
    """

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    sections: list[Section] = field(default_factory=list)
    raw_content: str = ""
    relationships: dict = field(default_factory=dict)

    def add_section(self, section: Section) -> None:
        """
        Add a top-level section to the document.

        Args:
            section: Section to add.
        """
        self.sections.append(section)

    def get_all_sections(self) -> list[Section]:
        """
        Get all sections recursively including nested ones.

        Returns:
            Flat list of all sections in the document.
        """
        all_sections = []
        for section in self.sections:
            all_sections.append(section)
            all_sections.extend(section.children)
        return all_sections

    def to_dict(self) -> dict:
        """
        Convert document to dictionary representation.

        Returns:
            Dictionary representation of the document.
        """
        return {
            "metadata": self.metadata.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "raw_content": self.raw_content,
            "relationships": self.relationships,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """
        Create a Document from a dictionary.

        Args:
            data: Dictionary containing document data.

        Returns:
            New Document instance.
        """
        metadata = DocumentMetadata(**data.get("metadata", {}))
        return cls(
            metadata=metadata,
            sections=[Section.from_dict(s) for s in data.get("sections", [])],
            raw_content=data.get("raw_content", ""),
            relationships=data.get("relationships", {}),
        )
