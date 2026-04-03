"""Schema definitions for AI-readable document output."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    YAML = "yaml"
    MCP = "mcp"


class SectionType(Enum):
    """Types of document sections with semantic meaning."""
    TITLE = "title"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    HEADING_4 = "heading_4"
    HEADING_5 = "heading_5"
    HEADING_6 = "heading_6"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    LIST_ITEM = "list_item"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    FRONT_MATTER = "front_matter"


class ContentClassification(Enum):
    """Classification of content within sections."""
    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    REFERENCE = "reference"
    EXAMPLE = "example"
    WARNING = "warning"
    NOTE = "note"
    IMPORTANT = "important"
    API_DOC = "api_documentation"
    CONFIGURATION = "configuration"
    TROUBLESHOOTING = "troubleshooting"


class Importance(Enum):
    """Importance level of content for AI processing."""
    CRITICAL = 3
    HIGH = 2
    NORMAL = 1
    LOW = 0


@dataclass
class SemanticTag:
    """Semantic tag applied to document content."""
    name: str
    value: str
    confidence: float = 1.0
    source: str = "auto"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source
        }


@dataclass
class Relationship:
    """Relationship between document elements."""
    source_id: str
    target_id: str
    relationship_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.relationship_type,
            "metadata": self.metadata
        }


@dataclass
class SchemaDefinition:
    """
    Schema definition for structured document output.

    This defines the expected structure of AI-readable documents
    with explicit semantic annotations.
    """
    version: str = "1.0"
    format_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "version": self.version,
            "format_version": self.format_version,
            "sections": {
                "required": ["id", "type", "content"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": [t.value for t in SectionType]},
                    "content": {"type": "string"},
                    "level": {"type": "integer", "minimum": 1, "maximum": 6},
                    "semantic_tags": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/semantic_tag"}
                    },
                    "metadata": {"type": "object"}
                }
            },
            "definitions": {
                "semantic_tag": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "relationship": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        }


# Default semantic tag mappings for common Markdown patterns
DEFAULT_SEMANTIC_MAPPINGS = {
    "note": ContentClassification.NOTE,
    "info": ContentClassification.NOTE,
    "warning": ContentClassification.WARNING,
    "caution": ContentClassification.WARNING,
    "danger": ContentClassification.WARNING,
    "tip": ContentClassification.EXAMPLE,
    "example": ContentClassification.EXAMPLE,
    "important": ContentClassification.IMPORTANT,
    "see also": ContentClassification.REFERENCE,
    "related": ContentClassification.REFERENCE,
}
