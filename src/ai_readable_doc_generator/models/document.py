"""Document model for AI-readable documentation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class DocumentMetadata:
    """Metadata for a document."""

    title: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    source_path: str = ""
    source_format: str = "markdown"
    word_count: int = 0
    line_count: int = 0
    tags: list[str] = field(default_factory=list)
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return {
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "modified_at": self.modified_at.isoformat() if isinstance(self.modified_at, datetime) else self.modified_at,
            "source_path": self.source_path,
            "source_format": self.source_format,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "tags": self.tags,
            **self.custom,
        }


@dataclass
class DocumentSummary:
    """Summary of document content."""

    total_sections: int = 0
    section_types: dict[str, int] = field(default_factory=dict)
    reading_time_minutes: float = 0.0
    keywords: list[str] = field(default_factory=list)
    main_topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to dictionary representation."""
        return {
            "total_sections": self.total_sections,
            "section_types": self.section_types,
            "reading_time_minutes": round(self.reading_time_minutes, 2),
            "keywords": self.keywords,
            "main_topics": self.main_topics,
        }


@dataclass
class DocumentRelationship:
    """Represents relationships between document sections."""

    source_id: str
    target_id: str
    relationship_type: str  # e.g., "parent", "child", "reference", "see_also"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
        }


@dataclass
class Document:
    """Represents a complete document with sections and metadata."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    sections: list = field(default_factory=list)  # List of Section objects
    semantic_tags: dict[str, Any] = field(default_factory=dict)
    relationships: list[DocumentRelationship] = field(default_factory=list)
    summary: DocumentSummary = field(default_factory=DocumentSummary)

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation."""
        result = {
            "document_id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
        }

        if self.sections:
            result["sections"] = [s.to_dict() if hasattr(s, "to_dict") else s for s in self.sections]
        if self.semantic_tags:
            result["semantic_tags"] = self.semantic_tags
        if self.relationships:
            result["relationships"] = [r.to_dict() for r in self.relationships]
        if self.summary:
            result["summary"] = self.summary.to_dict()

        return result

    def get_plain_text(self) -> str:
        """Get plain text content from all sections."""
        parts = []
        if self.title:
            parts.append(f"# {self.title}")
        if self.content:
            parts.append(self.content)
        for section in self.sections:
            if hasattr(section, "get_text_content"):
                parts.append(section.get_text_content())
        return "\n\n".join(parts)

    def calculate_summary(self) -> None:
        """Calculate document summary statistics."""
        self.summary.total_sections = len(self.sections)

        # Count section types
        section_types: dict[str, int] = {}
        for section in self.sections:
            section_type = section.type.value if hasattr(section, "type") else "unknown"
            section_types[section_type] = section_types.get(section_type, 0) + 1
        self.summary.section_types = section_types

        # Estimate reading time (average 200 words per minute)
        word_count = len(self.get_plain_text().split())
        self.metadata.word_count = word_count
        self.summary.reading_time_minutes = word_count / 200

    def add_section(self, section: Any) -> None:
        """Add a section to the document."""
        self.sections.append(section)
        self.calculate_summary()

    def add_relationship(
        self, source_id: str, target_id: str, relationship_type: str, description: str = ""
    ) -> None:
        """Add a relationship between sections."""
        relationship = DocumentRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            description=description,
        )
        self.relationships.append(relationship)
