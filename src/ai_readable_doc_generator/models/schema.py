"""Schema definitions for output formats."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SchemaType(Enum):
    """Supported output schema types."""

    STANDARD = "standard"
    MCP = "mcp"
    MINIMAL = "minimal"
    DETAILED = "detailed"


@dataclass
class SchemaField:
    """
    Definition of a schema field.

    Attributes:
        name: Field name.
        field_type: Expected field type.
        required: Whether the field is required.
        description: Field description.
        default: Default value if not present.
    """

    name: str
    field_type: str
    required: bool = False
    description: str = ""
    default: Optional[object] = None


@dataclass
class OutputSchema:
    """
    Schema definition for document output.

    Attributes:
        schema_type: Type of schema.
        fields: List of schema fields.
        version: Schema version.
        description: Schema description.
        metadata: Additional schema metadata.
    """

    schema_type: SchemaType = SchemaType.STANDARD
    fields: list[SchemaField] = field(default_factory=list)
    version: str = "1.0"
    description: str = ""
    metadata: dict = field(default_factory=dict)

    @classmethod
    def standard(cls) -> "OutputSchema":
        """
        Create a standard schema.

        Returns:
            Standard schema instance.
        """
        return cls(
            schema_type=SchemaType.STANDARD,
            description="Standard output schema for general use",
            fields=[
                SchemaField("content", "string", True, "Main content text"),
                SchemaField("type", "string", True, "Content type classification"),
                SchemaField("level", "integer", False, "Hierarchy level"),
                SchemaField("metadata", "object", False, "Additional metadata"),
            ],
        )

    @classmethod
    def mcp(cls) -> "OutputSchema":
        """
        Create an MCP-compatible schema.

        Returns:
            MCP schema instance.
        """
        return cls(
            schema_type=SchemaType.MCP,
            version="1.0",
            description="Model Context Protocol compatible schema",
            fields=[
                SchemaField("id", "string", True, "Unique section identifier"),
                SchemaField("content", "string", True, "Content text"),
                SchemaField("role", "string", True, "Semantic role"),
                SchemaField("priority", "integer", True, "Priority level (1-10)"),
                SchemaField("context", "object", False, "Context metadata"),
                SchemaField("annotations", "array", False, "Semantic annotations"),
            ],
        )

    @classmethod
    def minimal(cls) -> "OutputSchema":
        """
        Create a minimal schema.

        Returns:
            Minimal schema instance.
        """
        return cls(
            schema_type=SchemaType.MINIMAL,
            description="Minimal schema with essential fields only",
            fields=[
                SchemaField("content", "string", True, "Content text"),
                SchemaField("type", "string", True, "Content type"),
            ],
        )

    @classmethod
    def detailed(cls) -> "OutputSchema":
        """
        Create a detailed schema.

        Returns:
            Detailed schema instance.
        """
        return cls(
            schema_type=SchemaType.DETAILED,
            description="Detailed schema with full metadata",
            fields=[
                SchemaField("content", "string", True, "Main content text"),
                SchemaField("type", "string", True, "Content type classification"),
                SchemaField("level", "integer", False, "Hierarchy level"),
                SchemaField("importance", "string", False, "Importance level"),
                SchemaField("semantic_type", "string", False, "Semantic type"),
                SchemaField("confidence", "float", False, "Confidence score"),
                SchemaField("relationships", "array", False, "Related sections"),
                SchemaField("metadata", "object", False, "Additional metadata"),
                SchemaField("line_number", "integer", False, "Source line number"),
            ],
        )
