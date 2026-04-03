"""Document metadata model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    frontmatter: dict[str, Any] = field(default_factory=dict)
    character_count: Optional[int] = None
    word_count: Optional[int] = None
    section_count: Optional[int] = None
    source_path: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.
        
        Returns:
            Dictionary representation of the metadata.
        """
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tags": self.tags,
            "frontmatter": self.frontmatter,
            "character_count": self.character_count,
            "word_count": self.word_count,
            "section_count": self.section_count,
            "source_path": self.source_path,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """Create metadata from dictionary.
        
        Args:
            data: Dictionary containing metadata fields.
        
        Returns:
            DocumentMetadata instance.
        """
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            author=data.get("author"),
            version=data.get("version"),
            created_at=created_at,
            updated_at=updated_at,
            tags=data.get("tags", []),
            frontmatter=data.get("frontmatter", {}),
            character_count=data.get("character_count"),
            word_count=data.get("word_count"),
            section_count=data.get("section_count"),
            source_path=data.get("source_path"),
        )
