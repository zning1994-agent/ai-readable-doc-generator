"""Section model for document structure representation."""

from enum import Enum
from typing import Any


class ContentType(str, Enum):
    """Enumeration of content types for semantic tagging."""

    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    IMAGE = "image"
    LINK = "link"
    HORIZONTAL_RULE = "horizontal_rule"
    HTML = "html"
    FRONTMATTER = "frontmatter"
    UNKNOWN = "unknown"


class Section:
    """Represents a section of a document with semantic metadata.

    Attributes:
        id: Unique identifier for the section.
        content: The text content of the section.
        content_type: The type of content (e.g., paragraph, heading, code).
        level: Nesting level for headings (1-6).
        children: Child sections for nested content.
        metadata: Additional semantic metadata.
        importance: Importance level (1-5, where 5 is highest).
        tags: List of semantic tags for classification.
    """

    def __init__(
        self,
        content: str,
        content_type: ContentType = ContentType.PARAGRAPH,
        level: int = 1,
        importance: int = 3,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        id: str | None = None,
        children: list["Section"] | None = None,
    ) -> None:
        """Initialize a Section.

        Args:
            content: The text content of the section.
            content_type: The type of content.
            level: Nesting level for headings.
            importance: Importance level (1-5).
            tags: Semantic tags for classification.
            metadata: Additional metadata dictionary.
            id: Unique identifier for the section.
            children: Child sections for nested content.
        """
        self.id = id or self._generate_id(content)
        self.content = content
        self.content_type = content_type
        self.level = level
        self.children = children or []
        self.metadata = metadata or {}
        self.importance = self._validate_importance(importance)
        self.tags = tags or []

    @staticmethod
    def _generate_id(content: str) -> str:
        """Generate a unique ID from content.

        Args:
            content: The content to generate ID from.

        Returns:
            A URL-safe ID string.
        """
        import hashlib

        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"section_{content_hash}"

    @staticmethod
    def _validate_importance(value: int) -> int:
        """Validate importance value is within range.

        Args:
            value: The importance value to validate.

        Returns:
            Validated importance value (clamped to 1-5).
        """
        return max(1, min(5, value))

    def add_child(self, section: "Section") -> None:
        """Add a child section.

        Args:
            section: The section to add as a child.
        """
        self.children.append(section)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation.

        Returns:
            Dictionary containing section data.
        """
        return {
            "id": self.id,
            "content": self.content,
            "content_type": self.content_type.value,
            "level": self.level,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """Create a Section from dictionary data.

        Args:
            data: Dictionary containing section data.

        Returns:
            A new Section instance.
        """
        content_type = ContentType(data.get("content_type", "paragraph"))
        children = [cls.from_dict(child) for child in data.get("children", [])]

        return cls(
            content=data.get("content", ""),
            content_type=content_type,
            level=data.get("level", 1),
            importance=data.get("importance", 3),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            id=data.get("id"),
            children=children,
        )

    def __repr__(self) -> str:
        """Return string representation of Section."""
        return (
            f"Section(id={self.id!r}, type={self.content_type.value}, "
            f"level={self.level}, importance={self.importance})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Section."""
        if not isinstance(other, Section):
            return False
        return (
            self.id == other.id
            and self.content == other.content
            and self.content_type == other.content_type
            and self.level == other.level
        )
