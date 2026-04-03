"""
Output schema models for structured document generation.

This module defines the schema types and configurations used to generate
AI-compatible structured output from documents.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SchemaType(Enum):
    """Enumeration of supported output schema types."""

    STANDARD = "standard"
    MCP = "mcp"
    MINIMAL = "minimal"
    EXTENDED = "extended"


@dataclass
class OutputSchema:
    """
    Configuration for document output schema.

    Defines how the document should be structured when serialized
    for AI consumption, including metadata inclusion and format options.

    Attributes:
        schema_type: The type of schema to use for output generation.
        include_metadata: Whether to include document-level metadata.
        include_semantic_tags: Whether to include semantic tagging information.
        include_relationships: Whether to include section relationship data.
        include_importance_scores: Whether to include importance indicators.
        custom_fields: Additional custom fields to include in output.
    """

    schema_type: SchemaType = SchemaType.STANDARD
    include_metadata: bool = True
    include_semantic_tags: bool = True
    include_relationships: bool = True
    include_importance_scores: bool = False
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert schema configuration to dictionary representation.

        Returns:
            Dictionary containing all schema configuration values.
        """
        return {
            "schema_type": self.schema_type.value,
            "include_metadata": self.include_metadata,
            "include_semantic_tags": self.include_semantic_tags,
            "include_relationships": self.include_relationships,
            "include_importance_scores": self.include_importance_scores,
            "custom_fields": self.custom_fields,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OutputSchema":
        """
        Create schema configuration from dictionary.

        Args:
            data: Dictionary containing schema configuration.

        Returns:
            OutputSchema instance populated from the dictionary.
        """
        schema_type = SchemaType(data.get("schema_type", "standard"))
        return cls(
            schema_type=schema_type,
            include_metadata=data.get("include_metadata", True),
            include_semantic_tags=data.get("include_semantic_tags", True),
            include_relationships=data.get("include_relationships", True),
            include_importance_scores=data.get("include_importance_scores", False),
            custom_fields=data.get("custom_fields", {}),
        )

    def with_type(self, schema_type: SchemaType) -> "OutputSchema":
        """
        Create a copy of this schema with a different type.

        Args:
            schema_type: The new schema type for the copy.

        Returns:
            New OutputSchema instance with updated type.
        """
        return OutputSchema(
            schema_type=schema_type,
            include_metadata=self.include_metadata,
            include_semantic_tags=self.include_semantic_tags,
            include_relationships=self.include_relationships,
            include_importance_scores=self.include_importance_scores,
            custom_fields=self.custom_fields.copy(),
        )
