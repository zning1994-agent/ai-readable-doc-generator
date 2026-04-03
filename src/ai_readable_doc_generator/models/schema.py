"""Output schema models for structured document transformation."""

from enum import Enum
from typing import Any


class SchemaType(str, Enum):
    """Enumeration of supported output schema types."""

    BASIC = "basic"
    DETAILED = "detailed"
    SEMANTIC = "semantic"
    MCP = "mcp"
    CUSTOM = "custom"


class OutputSchema:
    """Schema definition for structured output.

    Attributes:
        schema_type: The type of schema to use.
        include_metadata: Whether to include metadata in output.
        include_tags: Whether to include semantic tags.
        include_importance: Whether to include importance levels.
        flatten: Whether to flatten nested sections.
        custom_fields: Additional custom fields to include.
    """

    # Default field configurations for each schema type
    SCHEMA_CONFIGS: dict[SchemaType, dict[str, bool]] = {
        SchemaType.BASIC: {
            "include_metadata": False,
            "include_tags": False,
            "include_importance": False,
            "flatten": True,
        },
        SchemaType.DETAILED: {
            "include_metadata": True,
            "include_tags": False,
            "include_importance": False,
            "flatten": False,
        },
        SchemaType.SEMANTIC: {
            "include_metadata": True,
            "include_tags": True,
            "include_importance": True,
            "flatten": False,
        },
        SchemaType.MCP: {
            "include_metadata": True,
            "include_tags": True,
            "include_importance": True,
            "flatten": False,
        },
        SchemaType.CUSTOM: {},
    }

    def __init__(
        self,
        schema_type: SchemaType = SchemaType.BASIC,
        include_metadata: bool | None = None,
        include_tags: bool | None = None,
        include_importance: bool | None = None,
        flatten: bool | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> None:
        """Initialize OutputSchema.

        Args:
            schema_type: The type of schema.
            include_metadata: Override for metadata inclusion.
            include_tags: Override for tags inclusion.
            include_importance: Override for importance inclusion.
            flatten: Override for flattening behavior.
            custom_fields: Custom fields to include in output.
        """
        self.schema_type = schema_type
        self.custom_fields = custom_fields or {}

        # Start with default config for schema type
        config = self.SCHEMA_CONFIGS.get(schema_type, self.SCHEMA_CONFIGS[SchemaType.BASIC]).copy()

        # Apply overrides if provided
        if include_metadata is not None:
            config["include_metadata"] = include_metadata
        if include_tags is not None:
            config["include_tags"] = include_tags
        if include_importance is not None:
            config["include_importance"] = include_importance
        if flatten is not None:
            config["flatten"] = flatten

        self.include_metadata = config["include_metadata"]
        self.include_tags = config["include_tags"]
        self.include_importance = config["include_importance"]
        self.flatten = config["flatten"]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OutputSchema":
        """Create OutputSchema from dictionary.

        Args:
            data: Dictionary containing schema configuration.

        Returns:
            A new OutputSchema instance.
        """
        schema_type = SchemaType(data.get("schema_type", "basic"))
        return cls(
            schema_type=schema_type,
            include_metadata=data.get("include_metadata"),
            include_tags=data.get("include_tags"),
            include_importance=data.get("include_importance"),
            flatten=data.get("flatten"),
            custom_fields=data.get("custom_fields"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation.

        Returns:
            Dictionary containing schema configuration.
        """
        result: dict[str, Any] = {
            "schema_type": self.schema_type.value,
            "include_metadata": self.include_metadata,
            "include_tags": self.include_tags,
            "include_importance": self.include_importance,
            "flatten": self.flatten,
        }
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        return result

    def merge(self, other: "OutputSchema") -> "OutputSchema":
        """Merge with another schema, taking non-default values from other.

        Args:
            other: Another OutputSchema to merge with.

        Returns:
            A new merged OutputSchema.
        """
        return OutputSchema(
            schema_type=other.schema_type,
            include_metadata=other.include_metadata
            if other.schema_type != SchemaType.BASIC
            else self.include_metadata,
            include_tags=other.include_tags
            if other.schema_type != SchemaType.BASIC
            else self.include_tags,
            include_importance=other.include_importance
            if other.schema_type != SchemaType.BASIC
            else self.include_importance,
            flatten=other.flatten if other.schema_type != SchemaType.BASIC else self.flatten,
            custom_fields={**self.custom_fields, **other.custom_fields},
        )

    def __repr__(self) -> str:
        """Return string representation of OutputSchema."""
        return f"OutputSchema(type={self.schema_type.value})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another OutputSchema."""
        if not isinstance(other, OutputSchema):
            return False
        return (
            self.schema_type == other.schema_type
            and self.include_metadata == other.include_metadata
            and self.include_tags == other.include_tags
            and self.include_importance == other.include_importance
            and self.flatten == other.flatten
            and self.custom_fields == other.custom_fields
        )
