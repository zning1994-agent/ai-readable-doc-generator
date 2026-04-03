"""Document model for AI-readable documentation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Types of sections in a document."""

    TITLE = "title"
    HEADING_1 = "h1"
    HEADING_2 = "h2"
    HEADING_3 = "h3"
    HEADING_4 = "h4"
    HEADING_5 = "h5"
    HEADING_6 = "h6"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    IMAGE = "image"
    LINK = "link"
    UNKNOWN = "unknown"


class ContentClassification(Enum):
    """Classification of content for AI understanding."""

    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    API_DOCUMENTATION = "api_documentation"
    CONFIGURATION = "configuration"
    CHANGELOG = "changelog"
    METADATA = "metadata"


class ImportanceLevel(Enum):
    """Importance level for AI processing priority."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class SemanticTag:
    """Semantic tag for content classification."""

    name: str
    value: str | None = None
    confidence: float = 1.0


@dataclass
class DocumentSection:
    """A section within the document."""

    id: str
    content: str
    section_type: SectionType = SectionType.PARAGRAPH
    level: int = 0
    parent_id: str | None = None
    children: list["DocumentSection"] = field(default_factory=list)
    semantic_tags: list[SemanticTag] = field(default_factory=list)
    classification: ContentClassification = ContentClassification.NARRATIVE
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_semantic_tag(self, name: str, value: str | None = None, confidence: float = 1.0) -> None:
        """Add a semantic tag to this section."""
        self.semantic_tags.append(SemanticTag(name=name, value=value, confidence=confidence))

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "section_type": self.section_type.value,
            "level": self.level,
            "parent_id": self.parent_id,
            "children": [child.to_dict() for child in self.children],
            "semantic_tags": [
                {"name": tag.name, "value": tag.value, "confidence": tag.confidence}
                for tag in self.semantic_tags
            ],
            "classification": self.classification.value,
            "importance": self.importance.name,
            "metadata": self.metadata,
        }


@dataclass
class Document:
    """Represents a structured, AI-readable document."""

    title: str = ""
    description: str = ""
    sections: list[DocumentSection] = field(default_factory=list)
    source_format: str = "markdown"
    source_path: str | None = None
    semantic_tags: list[SemanticTag] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_section(self, section: DocumentSection) -> None:
        """Add a section to the document."""
        self.sections.append(section)

    def get_all_sections(self) -> list[DocumentSection]:
        """Get all sections including nested ones."""
        all_sections = []
        for section in self.sections:
            all_sections.append(section)
            all_sections.extend(self._flatten_children(section.children))
        return all_sections

    def _flatten_children(self, children: list[DocumentSection]) -> list[DocumentSection]:
        """Flatten nested sections recursively."""
        result = []
        for child in children:
            result.append(child)
            result.extend(self._flatten_children(child.children))
        return result

    def add_semantic_tag(self, name: str, value: str | None = None, confidence: float = 1.0) -> None:
        """Add a document-level semantic tag."""
        self.semantic_tags.append(SemanticTag(name=name, value=value, confidence=confidence))

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "title": self.title,
            "description": self.description,
            "sections": [section.to_dict() for section in self.sections],
            "source_format": self.source_format,
            "source_path": self.source_path,
            "semantic_tags": [
                {"name": tag.name, "value": tag.value, "confidence": tag.confidence}
                for tag in self.semantic_tags
            ],
            "metadata": self.metadata,
        }
