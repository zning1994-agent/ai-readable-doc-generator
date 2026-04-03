"""
Section domain model for AI-readable documentation.

This module provides the Section class which represents a document section with:
- Content: The actual text/content of the section
- Metadata: Semantic tags, content types, importance levels
- Hierarchy: Parent/child relationships for nested sections
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Types of content that a section can contain."""
    
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    BLOCKQUOTE = "blockquote"
    ADMONITION = "admonition"
    DIVIDER = "divider"
    UNKNOWN = "unknown"


class ContentImportance(Enum):
    """Importance level of section content for AI processing."""
    
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFORMATIONAL = 5


@dataclass
class SectionMetadata:
    """
    Metadata for a section containing semantic information.
    
    Attributes:
        section_type: The type of content in this section
        importance: How important this section is for AI understanding
        tags: List of semantic tags for categorization
        language: Language code of the content (e.g., 'en', 'zh')
        word_count: Number of words in the section
        character_count: Number of characters in the section
        custom: Additional custom metadata as key-value pairs
    """
    
    section_type: SectionType = SectionType.UNKNOWN
    importance: ContentImportance = ContentImportance.MEDIUM
    tags: list[str] = field(default_factory=list)
    language: str = "en"
    word_count: int = 0
    character_count: int = 0
    custom: dict[str, Any] = field(default_factory=dict)
    
    def add_tag(self, tag: str) -> None:
        """Add a semantic tag to the section."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a semantic tag from the section."""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if the section has a specific tag."""
        return tag in self.tags
    
    def set_custom(self, key: str, value: Any) -> None:
        """Set a custom metadata value."""
        self.custom[key] = value
    
    def get_custom(self, key: str, default: Any = None) -> Any:
        """Get a custom metadata value."""
        return self.custom.get(key, default)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return {
            "section_type": self.section_type.value,
            "importance": self.importance.name,
            "tags": self.tags.copy(),
            "language": self.language,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "custom": self.custom.copy(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SectionMetadata:
        """Create metadata from dictionary representation."""
        section_type = SectionType(data.get("section_type", "unknown"))
        importance = ContentImportance[data.get("importance", "MEDIUM")]
        
        return cls(
            section_type=section_type,
            importance=importance,
            tags=data.get("tags", []),
            language=data.get("language", "en"),
            word_count=data.get("word_count", 0),
            character_count=data.get("character_count", 0),
            custom=data.get("custom", {}),
        )


@dataclass
class Section:
    """
    A document section with content, metadata, and hierarchy support.
    
    Sections can be nested to form a tree structure representing the
    document hierarchy. Each section contains:
    - Unique identifier
    - Title/heading text
    - Content body
    - Metadata for AI semantic understanding
    - Parent/child relationships
    - Timestamps for tracking
    
    Attributes:
        id: Unique identifier for this section
        title: Section title or heading
        content: The actual content/body of the section
        metadata: Semantic metadata for AI processing
        parent: Parent section (None for root sections)
        children: Child sections nested within this section
        level: Hierarchy level (0 for root, 1 for top-level, etc.)
        created_at: Timestamp when section was created
        updated_at: Timestamp when section was last modified
    """
    
    title: str = ""
    content: str = ""
    metadata: SectionMetadata = field(default_factory=SectionMetadata)
    parent: Section | None = None
    children: list[Section] = field(default_factory=list)
    level: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.metadata is None:
            self.metadata = SectionMetadata()
        self._update_counts()
    
    def _update_counts(self) -> None:
        """Update word and character counts from content."""
        if self.content:
            self.metadata.word_count = len(self.content.split())
            self.metadata.character_count = len(self.content)
        else:
            self.metadata.word_count = 0
            self.metadata.character_count = 0
    
    @property
    def is_root(self) -> bool:
        """Check if this section is a root section (no parent)."""
        return self.parent is None
    
    @property
    def is_leaf(self) -> bool:
        """Check if this section is a leaf (has no children)."""
        return len(self.children) == 0
    
    @property
    def depth(self) -> int:
        """Get the depth of this section in the hierarchy."""
        return self.level
    
    @property
    def path(self) -> list[str]:
        """Get the path of titles from root to this section."""
        path_parts = []
        current: Section | None = self
        while current is not None:
            if current.title:
                path_parts.insert(0, current.title)
            current = current.parent
        return path_parts
    
    @property
    def full_content(self) -> str:
        """Get the full content including all children's content."""
        parts = [self.content] if self.content else []
        for child in self.children:
            parts.append(child.full_content)
        return "\n\n".join(filter(None, parts))
    
    @property
    def total_word_count(self) -> int:
        """Get total word count including all children."""
        count = self.metadata.word_count
        for child in self.children:
            count += child.total_word_count
        return count
    
    @property
    def total_character_count(self) -> int:
        """Get total character count including all children."""
        count = self.metadata.character_count
        for child in self.children:
            count += child.total_character_count
        return count
    
    def add_child(self, section: Section) -> None:
        """
        Add a child section to this section.
        
        Args:
            section: The child section to add
        """
        if section.parent is not None:
            section.parent.remove_child(section)
        
        section.parent = self
        section.level = self.level + 1
        self.children.append(section)
        self.updated_at = datetime.now()
    
    def remove_child(self, section: Section) -> bool:
        """
        Remove a child section from this section.
        
        Args:
            section: The child section to remove
            
        Returns:
            True if the section was found and removed, False otherwise
        """
        if section in self.children:
            section.parent = None
            section.level = 0
            self.children.remove(section)
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_child(self, index: int) -> Section | None:
        """
        Get a child section by index.
        
        Args:
            index: The index of the child section
            
        Returns:
            The child section if found, None otherwise
        """
        if 0 <= index < len(self.children):
            return self.children[index]
        return None
    
    def find_child_by_id(self, section_id: str) -> Section | None:
        """
        Find a section by its ID within this section and its children.
        
        Args:
            section_id: The ID to search for
            
        Returns:
            The section if found, None otherwise
        """
        if self.id == section_id:
            return self
        
        for child in self.children:
            found = child.find_child_by_id(section_id)
            if found is not None:
                return found
        
        return None
    
    def find_children_by_tag(self, tag: str) -> list[Section]:
        """
        Find all sections with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List of sections containing the tag
        """
        results = []
        if self.metadata.has_tag(tag):
            results.append(self)
        
        for child in self.children:
            results.extend(child.find_children_by_tag(tag))
        
        return results
    
    def find_children_by_type(self, section_type: SectionType) -> list[Section]:
        """
        Find all sections of a specific type.
        
        Args:
            section_type: The section type to search for
            
        Returns:
            List of sections of the specified type
        """
        results = []
        if self.metadata.section_type == section_type:
            results.append(self)
        
        for child in self.children:
            results.extend(child.find_children_by_type(section_type))
        
        return results
    
    def get_ancestors(self) -> list[Section]:
        """
        Get all ancestor sections from parent to root.
        
        Returns:
            List of ancestor sections (nearest first)
        """
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_root(self) -> Section:
        """
        Get the root section of this section's hierarchy.
        
        Returns:
            The root section
        """
        current = self
        while current.parent is not None:
            current = current.parent
        return current
    
    def get_siblings(self) -> list[Section]:
        """
        Get all sibling sections (same parent).
        
        Returns:
            List of sibling sections (excluding this section)
        """
        if self.parent is None:
            return []
        return [s for s in self.parent.children if s is not self]
    
    def walk(self) -> list[Section]:
        """
        Walk through all sections in this subtree (depth-first).
        
        Returns:
            List of all sections including this one
        """
        result = [self]
        for child in self.children:
            result.extend(child.walk())
        return result
    
    def update_content(self, content: str) -> None:
        """
        Update the content of this section.
        
        Args:
            content: New content for the section
        """
        self.content = content
        self._update_counts()
        self.updated_at = datetime.now()
    
    def update_title(self, title: str) -> None:
        """
        Update the title of this section.
        
        Args:
            title: New title for the section
        """
        self.title = title
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert section to dictionary representation.
        
        Returns:
            Dictionary containing all section data
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "metadata": self.metadata.to_dict(),
            "children": [child.to_dict() for child in self.children],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Section:
        """
        Create a section from dictionary representation.
        
        Args:
            data: Dictionary containing section data
            
        Returns:
            New Section instance
        """
        metadata = SectionMetadata.from_dict(data.get("metadata", {}))
        
        section = cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            metadata=metadata,
            level=data.get("level", 0),
        )
        
        if "created_at" in data:
            section.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            section.updated_at = datetime.fromisoformat(data["updated_at"])
        
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            section.add_child(child)
        
        return section
    
    def __repr__(self) -> str:
        """String representation of the section."""
        title_preview = (
            self.title[:30] + "..." 
            if len(self.title) > 30 
            else self.title
        )
        return (
            f"Section(id={self.id[:8]}..., title='{title_preview}', "
            f"type={self.metadata.section_type.value}, "
            f"children={len(self.children)})"
        )
