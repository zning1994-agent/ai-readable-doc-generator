"""Section model for document structure."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Types of sections in a document."""

    DOCUMENT = "document"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    CODE = "code"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    BLOCKQUOTE = "blockquote"
    IMAGE = "image"
    LINK = "link"
    DIVISION = "division"
    SPAN = "span"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    ASIDE = "aside"
    ARTICLE = "article"
    MAIN = "main"
    SECTION = "section"
    UNKNOWN = "unknown"


class ContentClassification(Enum):
    """Classification of content within a section."""

    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    EXAMPLE = "example"
    WARNING = "warning"
    NOTE = "note"
    CODE_LITERAL = "code_literal"
    METADATA = "metadata"
    NAVIGATION = "navigation"
    UNKNOWN = "unknown"


class ImportanceLevel(Enum):
    """Importance level of content."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Section:
    """Represents a section of a document with semantic metadata."""

    section_type: SectionType
    content: str
    level: int = 1
    children: list["Section"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    classification: ContentClassification = ContentClassification.UNKNOWN
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    id: str | None = None
    classes: list[str] = field(default_factory=list)
    raw_attributes: dict[str, str] = field(default_factory=dict)

    def add_child(self, child: "Section") -> None:
        """Add a child section."""
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation."""
        return {
            "section_type": self.section_type.value,
            "content": self.content,
            "level": self.level,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
            "classification": self.classification.value,
            "importance": self.importance.value,
            "id": self.id,
            "classes": self.classes,
            "raw_attributes": self.raw_attributes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """Create section from dictionary."""
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(
            section_type=SectionType(data.get("section_type", "unknown")),
            content=data.get("content", ""),
            level=data.get("level", 1),
            children=children,
            metadata=data.get("metadata", {}),
            classification=ContentClassification(
                data.get("classification", "unknown")
            ),
            importance=ImportanceLevel(data.get("importance", "medium")),
            id=data.get("id"),
            classes=data.get("classes", []),
            raw_attributes=data.get("raw_attributes", {}),
        )
