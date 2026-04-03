"""Document model for complete document representation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .section import Section
from .schema import OutputSchema


@dataclass
class DocumentMetadata:
    """Metadata associated with a document."""

    title: str | None = None
    description: str | None = None
    author: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    version: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    language: str | None = None
    tags: list[str] = field(default_factory=list)
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "version": self.version,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "language": self.language,
            "tags": self.tags,
        }
        result.update(self.custom)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """Create metadata from dictionary."""
        known_fields = {
            "title",
            "description",
            "author",
            "created_at",
            "modified_at",
            "version",
            "source_url",
            "source_type",
            "language",
            "tags",
        }
        known_data = {k: v for k, v in data.items() if k in known_fields}
        custom_data = {k: v for k, v in data.items() if k not in known_fields}

        created_at = known_data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        modified_at = known_data.get("modified_at")
        if isinstance(modified_at, str):
            modified_at = datetime.fromisoformat(modified_at)

        return cls(
            title=known_data.get("title"),
            description=known_data.get("description"),
            author=known_data.get("author"),
            created_at=created_at,
            modified_at=modified_at,
            version=known_data.get("version"),
            source_url=known_data.get("source_url"),
            source_type=known_data.get("source_type"),
            language=known_data.get("language"),
            tags=known_data.get("tags", []),
            custom=custom_data,
        )


@dataclass
class Document:
    """Represents a complete document with semantic structure."""

    content: str
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    sections: list[Section] = field(default_factory=list)
    schema: OutputSchema = field(default_factory=OutputSchema.JSON)
    raw_content: str | None = None

    def add_section(self, section: Section) -> None:
        """Add a top-level section to the document."""
        self.sections.append(section)

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "metadata": self.metadata.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "schema": self.schema.value,
            "content": self.content,
            "raw_content": self.raw_content,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        metadata = DocumentMetadata.from_dict(data.get("metadata", {}))
        sections = [Section.from_dict(s) for s in data.get("sections", [])]
        return cls(
            content=data.get("content", ""),
            metadata=metadata,
            sections=sections,
            schema=OutputSchema(data.get("schema", "json")),
            raw_content=data.get("raw_content"),
        )
