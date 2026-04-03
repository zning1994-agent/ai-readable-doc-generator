"""Section model for document structure representation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Enumeration of section content types."""

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
    FRONTMATTER = "frontmatter"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a section of a document with semantic tagging.

    Attributes:
        content: The raw text content of the section.
        section_type: The type of content (heading, paragraph, etc.).
        level: Hierarchical level for headings (1-6 for markdown headings).
        metadata: Additional semantic metadata for the section.
        children: Child sections (for nested content).
        line_number: Original line number in source document.
    """

    content: str
    section_type: SectionType = SectionType.PARAGRAPH
    level: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list["Section"] = field(default_factory=list)
    line_number: int = 0

    def add_child(self, child: "Section") -> None:
        """Add a child section to this section.

        Args:
            child: The section to add as a child.
        """
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation.

        Returns:
            Dictionary containing section data.
        """
        return {
            "content": self.content,
            "type": self.section_type.value,
            "level": self.level,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
            "line_number": self.line_number,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """Create section from dictionary representation.

        Args:
            data: Dictionary containing section data.

        Returns:
            Section instance.
        """
        section_type = SectionType(data.get("type", "paragraph"))
        return cls(
            content=data.get("content", ""),
            section_type=section_type,
            level=data.get("level", 0),
            metadata=data.get("metadata", {}),
            children=[
                cls.from_dict(child) for child in data.get("children", [])
            ],
            line_number=data.get("line_number", 0),
        )
