"""Section models for document structure."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(str, Enum):
    """Types of document sections."""

    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    IMAGE = "image"
    LINK = "link"
    HORIZONTAL_RULE = "horizontal_rule"
    UNKNOWN = "unknown"


class ContentImportance(str, Enum):
    """Importance level of content."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Section:
    """Represents a section of a document."""

    id: str
    type: SectionType
    content: str
    level: int = 1
    children: list["Section"] = field(default_factory=list)
    semantic_tags: dict[str, Any] = field(default_factory=dict)
    importance: ContentImportance = ContentImportance.MEDIUM
    line_number: int = 0

    # Metadata
    heading: str | None = None
    code_language: str | None = None
    list_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation."""
        result = {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "level": self.level,
            "importance": self.importance.value,
            "line_number": self.line_number,
        }

        if self.heading:
            result["heading"] = self.heading
        if self.code_language:
            result["code_language"] = self.code_language
        if self.list_items:
            result["list_items"] = self.list_items
        if self.semantic_tags:
            result["semantic_tags"] = self.semantic_tags
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]

        return result

    @classmethod
    def from_markdown(cls, content: str, line_number: int = 0) -> "Section":
        """Create a section from markdown content."""
        return cls(
            id="",
            type=SectionType.UNKNOWN,
            content=content,
            line_number=line_number,
        )

    def add_tag(self, key: str, value: Any) -> None:
        """Add a semantic tag to the section."""
        self.semantic_tags[key] = value

    def get_text_content(self) -> str:
        """Get all text content including children."""
        parts = [self.content]
        for child in self.children:
            parts.append(child.get_text_content())
        return "\n".join(parts)
