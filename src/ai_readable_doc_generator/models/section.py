"""Section models for document structure representation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(Enum):
    """Types of sections in a document."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"
    IMAGE = "image"
    LINK = "link"
    CUSTOM = "custom"


class ContentType(Enum):
    """Semantic content types for classification."""

    TITLE = "title"
    INTRODUCTION = "introduction"
    BODY = "body"
    CONCLUSION = "conclusion"
    SUMMARY = "summary"
    CODE_EXAMPLE = "code_example"
    API_REFERENCE = "api_reference"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"
    CHANGELOG = "changelog"
    GLOSSARY = "glossary"
    APPENDIX = "appendix"
    OTHER = "other"


@dataclass
class SemanticTag:
    """A semantic tag for content classification."""

    name: str
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticTag":
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Section:
    """A section of a document with semantic tagging."""

    section_type: SectionType
    content: str
    level: int = 1
    heading: str | None = None
    content_type: ContentType = ContentType.OTHER
    semantic_tags: list[SemanticTag] = field(default_factory=list)
    children: list["Section"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_semantic_tag(self, tag: SemanticTag) -> None:
        """Add a semantic tag to this section."""
        self.semantic_tags.append(tag)

    def add_child(self, child: "Section") -> None:
        """Add a child section."""
        self.children.append(child)

    def get_all_tags(self) -> list[SemanticTag]:
        """Get all semantic tags including from children."""
        tags = list(self.semantic_tags)
        for child in self.children:
            tags.extend(child.get_all_tags())
        return tags

    def get_text_content(self) -> str:
        """Get all text content from this section and children."""
        parts = []
        if self.heading:
            parts.append(self.heading)
        if self.content:
            parts.append(self.content)
        for child in self.children:
            parts.append(child.get_text_content())
        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.section_type.value,
            "content": self.content,
            "level": self.level,
            "heading": self.heading,
            "content_type": self.content_type.value,
            "semantic_tags": [tag.to_dict() for tag in self.semantic_tags],
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Section":
        """Create from dictionary representation."""
        section_type = SectionType(data.get("type", "paragraph"))
        content_type = ContentType(data.get("content_type", "other"))

        semantic_tags = [
            SemanticTag.from_dict(t) for t in data.get("semantic_tags", [])
        ]
        children = [cls.from_dict(c) for c in data.get("children", [])]

        return cls(
            section_type=section_type,
            content=data.get("content", ""),
            level=data.get("level", 1),
            heading=data.get("heading"),
            content_type=content_type,
            semantic_tags=semantic_tags,
            children=children,
            metadata=data.get("metadata", {}),
        )

    def is_heading_section(self) -> bool:
        """Check if this is a heading section."""
        return self.section_type == SectionType.HEADING

    def is_code_section(self) -> bool:
        """Check if this is a code block section."""
        return self.section_type == SectionType.CODE_BLOCK

    def get_depth(self) -> int:
        """Get the depth of this section in the document tree."""
        max_child_depth = 0
        for child in self.children:
            child_depth = child.get_depth()
            if child_depth > max_child_depth:
                max_child_depth = child_depth
        return max_child_depth + 1
