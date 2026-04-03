"""
Section models for document structure representation.

This module defines the Section model which represents individual
sections within a document, including content type classification
and semantic tagging.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Enumeration of document section types."""

    TITLE = "title"
    HEADING = "heading"
    SUBHEADING = "subheading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    IMAGE = "image"
    LINK = "link"
    HORIZONTAL_RULE = "horizontal_rule"
    FOOTNOTE = "footnote"
    OTHER = "other"


class ContentType(Enum):
    """Enumeration of content type classifications."""

    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    REFERENCE = "reference"
    EXAMPLE = "example"
    WARNING = "warning"
    NOTE = "note"
    QUESTION = "question"
    DEFINITION = "definition"
    PROCEDURAL = "procedural"
    METADATA = "metadata"


@dataclass
class Section:
    """
    Represents a section within a document.

    A section is a structural unit of a document that contains content
    and semantic metadata. Sections can be nested to form hierarchies.

    Attributes:
        id: Unique identifier for this section within the document.
        section_type: The type of section (heading, paragraph, etc.).
        content: The raw content of this section.
        content_type: Classification of the content type.
        level: Nesting level in the document hierarchy (1 = top level).
        parent_id: ID of the parent section, if any.
        children: List of child sections within this section.
        semantic_tags: Dictionary of semantic metadata tags.
        importance: Importance score (0.0 to 1.0).
        metadata: Additional section-specific metadata.
    """

    id: str
    section_type: SectionType = SectionType.PARAGRAPH
    content: str = ""
    content_type: ContentType = ContentType.NARRATIVE
    level: int = 1
    parent_id: str | None = None
    children: list["Section"] = field(default_factory=list)
    semantic_tags: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate section attributes after initialization."""
        if not self.id:
            raise ValueError("Section id cannot be empty")
        if self.level < 1:
            raise ValueError("Section level must be >= 1")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("Importance must be between 0.0 and 1.0")

    def add_child(self, section: "Section") -> None:
        """
        Add a child section to this section.

        Args:
            section: The child section to add.
        """
        section.parent_id = self.id
        section.level = self.level + 1
        self.children.append(section)

    def remove_child(self, section_id: str) -> bool:
        """
        Remove a child section by ID.

        Args:
            section_id: The ID of the child section to remove.

        Returns:
            True if the child was found and removed, False otherwise.
        """
        for i, child in enumerate(self.children):
            if child.id == section_id:
                self.children.pop(i)
                return True
        return False

    def find_by_id(self, section_id: str) -> "Section | None":
        """
        Find a section by ID, searching this section and its children.

        Args:
            section_id: The ID of the section to find.

        Returns:
            The section if found, None otherwise.
        """
        if self.id == section_id:
            return self
        for child in self.children:
            found = child.find_by_id(section_id)
            if found:
                return found
        return None

    def add_tag(self, key: str, value: Any) -> None:
        """
        Add a semantic tag to this section.

        Args:
            key: The tag key.
            value: The tag value.
        """
        self.semantic_tags[key] = value

    def get_ancestors(self) -> list["Section"]:
        """
        Get all ancestor sections from root to parent.

        Returns:
            List of ancestor sections, ordered from root to parent.
        """
        ancestors: list[Section] = []
        return ancestors

    def to_dict(self) -> dict[str, Any]:
        """
        Convert section to dictionary representation.

        Returns:
            Dictionary containing all section data.
        """
        return {
            "id": self.id,
            "section_type": self.section_type.value,
            "content": self.content,
            "content_type": self.content_type.value,
            "level": self.level,
            "parent_id": self.parent_id,
            "children": [child.to_dict() for child in self.children],
            "semantic_tags": self.semantic_tags,
            "importance": self.importance,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """
        Create a section from dictionary representation.

        Args:
            data: Dictionary containing section data.

        Returns:
            Section instance populated from the dictionary.
        """
        section_type = SectionType(data.get("section_type", "paragraph"))
        content_type = ContentType(data.get("content_type", "narrative"))

        section = cls(
            id=data["id"],
            section_type=section_type,
            content=data.get("content", ""),
            content_type=content_type,
            level=data.get("level", 1),
            parent_id=data.get("parent_id"),
            semantic_tags=data.get("semantic_tags", {}),
            importance=data.get("importance", 0.5),
            metadata=data.get("metadata", {}),
        )

        for child_data in data.get("children", []):
            section.add_child(cls.from_dict(child_data))

        return section
