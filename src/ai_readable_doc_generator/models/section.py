"""Section model definitions."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class SectionType(Enum):
    """Types of sections that can be identified in documents."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    HORIZONTAL_RULE = "horizontal_rule"
    EMPTY = "empty"
    UNKNOWN = "unknown"


class ContentType(Enum):
    """Semantic content types for sections."""

    TITLE = "title"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    INTRODUCTION = "introduction"
    BODY = "body"
    CONCLUSION = "conclusion"
    SUMMARY = "summary"
    CODE_EXAMPLE = "code_example"
    NOTE = "note"
    WARNING = "warning"
    TIP = "tip"
    QUESTION = "question"
    ANSWER = "answer"
    DEFINITION = "definition"
    LIST_ITEM = "list_item"
    CITATION = "citation"
    REFERENCE = "reference"
    UNCLASSIFIED = "unclassified"


class Importance(Enum):
    """Importance level of content."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Section:
    """
    Represents a section of a document with semantic metadata.

    Attributes:
        content: The raw text content of the section.
        section_type: The type of section (heading, paragraph, etc.).
        content_type: Semantic classification of the content.
        level: Hierarchy level (e.g., heading level 1-6).
        importance: Importance level of the content.
        parent: Optional reference to parent section.
        children: List of child sections.
        metadata: Additional metadata dictionary.
        raw_text: Original unprocessed text.
        line_number: Line number in source document.
    """

    content: str
    section_type: SectionType = SectionType.PARAGRAPH
    content_type: ContentType = ContentType.UNCLASSIFIED
    level: int = 0
    importance: Importance = Importance.MEDIUM
    parent: Optional["Section"] = None
    children: list["Section"] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    raw_text: str = ""
    line_number: int = 0

    def __post_init__(self):
        """Initialize raw_text if not provided."""
        if not self.raw_text:
            self.raw_text = self.content

    def add_child(self, child: "Section") -> None:
        """Add a child section and set parent reference."""
        child.parent = self
        self.children.append(child)

    def to_dict(self) -> dict:
        """
        Convert section to dictionary representation.

        Returns:
            Dictionary representation of the section.
        """
        return {
            "content": self.content,
            "section_type": self.section_type.value,
            "content_type": self.content_type.value,
            "level": self.level,
            "importance": self.importance.value,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
            "raw_text": self.raw_text,
            "line_number": self.line_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Section":
        """
        Create a Section from a dictionary.

        Args:
            data: Dictionary containing section data.

        Returns:
            New Section instance.
        """
        return cls(
            content=data.get("content", ""),
            section_type=SectionType(data.get("section_type", "paragraph")),
            content_type=ContentType(data.get("content_type", "unclassified")),
            level=data.get("level", 0),
            importance=Importance(data.get("importance", "medium")),
            metadata=data.get("metadata", {}),
            raw_text=data.get("raw_text", ""),
            line_number=data.get("line_number", 0),
        )
