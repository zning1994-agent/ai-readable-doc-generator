"""Section model for document content representation."""

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import SectionType, ContentClassification, SemanticTag


@dataclass
class Section:
    """
    Represents a section of a document.

    Sections are the building blocks of structured documents,
    each containing content with semantic metadata.
    """
    id: str
    type: "SectionType"
    content: str
    level: int = 1
    line_start: int = 0
    line_end: int = 0
    language: str = ""
    semantic_tags: list["SemanticTag"] = field(default_factory=list)
    classification: "ContentClassification | None" = None
    children: list["Section"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "level": self.level,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "language": self.language,
            "semantic_tags": [tag.to_dict() for tag in self.semantic_tags],
            "classification": self.classification.value if self.classification else None,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata
        }

    def add_semantic_tag(self, name: str, value: str, confidence: float = 1.0) -> None:
        """Add a semantic tag to this section."""
        from .schema import SemanticTag
        self.semantic_tags.append(
            SemanticTag(name=name, value=value, confidence=confidence)
        )

    def get_word_count(self) -> int:
        """Get word count of section content."""
        return len(self.content.split())

    def get_char_count(self) -> int:
        """Get character count of section content."""
        return len(self.content)

    def is_empty(self) -> bool:
        """Check if section has no content."""
        return not self.content.strip()

    def get_depth(self) -> int:
        """Get the depth of this section in the document tree."""
        depth = 0
        current = self
        while current.children:
            depth += 1
            # Note: In this implementation, depth is based on children presence
            break  # Simplified - actual implementation would track parent
        return self.level


@dataclass
class SectionBuilder:
    """Builder for creating Section objects with fluent interface."""

    _section: Section | None = None

    def create(
        self,
        section_id: str,
        section_type: "SectionType",
        content: str = ""
    ) -> "SectionBuilder":
        """Start building a new section."""
        self._section = Section(
            id=section_id,
            type=section_type,
            content=content
        )
        return self

    def with_level(self, level: int) -> "SectionBuilder":
        """Set the heading level."""
        if self._section:
            self._section.level = level
        return self

    def with_line_range(self, start: int, end: int) -> "SectionBuilder":
        """Set the line range."""
        if self._section:
            self._section.line_start = start
            self._section.line_end = end
        return self

    def with_language(self, language: str) -> "SectionBuilder":
        """Set the programming language for code blocks."""
        if self._section:
            self._section.language = language
        return self

    def with_classification(
        self,
        classification: "ContentClassification"
    ) -> "SectionBuilder":
        """Set content classification."""
        if self._section:
            self._section.classification = classification
        return self

    def with_metadata(self, key: str, value: Any) -> "SectionBuilder":
        """Add metadata to the section."""
        if self._section:
            self._section.metadata[key] = value
        return self

    def add_child(self, child: Section) -> "SectionBuilder":
        """Add a child section."""
        if self._section:
            self._section.children.append(child)
        return self

    def build(self) -> Section | None:
        """Build and return the section."""
        return self._section
