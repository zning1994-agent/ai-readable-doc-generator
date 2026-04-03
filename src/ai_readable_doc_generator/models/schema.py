"""Schema models for structured document output."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SchemaVersion(str, Enum):
    """Supported schema versions."""

    V1 = "1.0"
    V2 = "2.0"


@dataclass
class SchemaField:
    """Represents a field in the output schema."""

    name: str
    field_type: str
    required: bool = True
    description: str = ""
    default: Any = None


@dataclass
class OutputSchema:
    """Schema configuration for structured output."""

    version: SchemaVersion = SchemaVersion.V1
    include_metadata: bool = True
    include_semantic_tags: bool = True
    include_summary: bool = True
    indent: int = 2
    sort_keys: bool = False

    # Schema field definitions
    fields: list[SchemaField] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "version": self.version.value,
            "include_metadata": self.include_metadata,
            "include_semantic_tags": self.include_semantic_tags,
            "include_summary": self.include_summary,
            "indent": self.indent,
            "sort_keys": self.sort_keys,
            "fields": [
                {"name": f.name, "type": f.field_type, "required": f.required}
                for f in self.fields
            ],
        }

    @classmethod
    def default_schema(cls) -> "OutputSchema":
        """Create a default output schema."""
        return cls(
            version=SchemaVersion.V1,
            fields=[
                SchemaField("title", "string", required=True, description="Document title"),
                SchemaField("content", "string", required=True, description="Main content"),
                SchemaField("sections", "array", required=False, description="Document sections"),
                SchemaField("metadata", "object", required=False, description="Document metadata"),
                SchemaField("semantic_tags", "object", required=False, description="Semantic tags"),
            ],
        )

    @classmethod
    def mcp_schema(cls) -> "OutputSchema":
        """Create MCP-compatible schema."""
        return cls(
            version=SchemaVersion.V2,
            include_metadata=True,
            include_semantic_tags=True,
            include_summary=True,
            fields=[
                SchemaField("document_id", "string", required=True, description="Unique document ID"),
                SchemaField("title", "string", required=True, description="Document title"),
                SchemaField("content", "string", required=True, description="Main content"),
                SchemaField("sections", "array", required=False, description="Document sections"),
                SchemaField("metadata", "object", required=True, description="Document metadata"),
                SchemaField("semantic_tags", "object", required=True, description="Semantic tags"),
                SchemaField("summary", "object", required=False, description="Document summary"),
                SchemaField("relationships", "array", required=False, description="Section relationships"),
            ],
        )
