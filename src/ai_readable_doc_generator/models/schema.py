"""Schema definitions for document output formats."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SchemaType(Enum):
    """Schema type enumeration for different output configurations."""

    BASIC = "basic"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    COMPREHENSIVE = "comprehensive"


class OutputFormat(Enum):
    """Supported output formats."""

    JSON = "json"
    YAML = "yaml"
    MCP = "mcp"
    MARKDOWN = "markdown"


@dataclass
class OutputSchema:
    """Schema configuration for document output.

    Attributes:
        schema_type: The type of schema to use.
        include_metadata: Whether to include metadata in output.
        include_tags: Whether to include tags in output.
        include_importance: Whether to include importance levels.
        flatten: Whether to flatten nested sections.
        custom_fields: Custom fields to add to output.
    """

    schema_type: SchemaType = SchemaType.BASIC
    include_metadata: bool = True
    include_tags: bool = True
    include_importance: bool = True
    flatten: bool = False
    custom_fields: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate schema after initialization."""
        if self.custom_fields is None:
            self.custom_fields = {}


@dataclass
class SchemaField:
    """A field definition in a schema."""

    name: str
    field_type: str
    required: bool = True
    default: Any = None
    description: str = ""
    enum_values: list[Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.field_type,
            "required": self.required,
            "description": self.description,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.enum_values:
            result["enum"] = self.enum_values
        return result


@dataclass
class SchemaDefinition:
    """Schema definition for document output."""

    name: str
    version: str = "1.0"
    description: str = ""
    fields: list[SchemaField] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_field(self, field: SchemaField) -> None:
        """Add a field to the schema."""
        self.fields.append(field)

    def get_field(self, name: str) -> SchemaField | None:
        """Get a field by name."""
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def get_required_fields(self) -> list[SchemaField]:
        """Get all required fields."""
        return [f for f in self.fields if f.required]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchemaDefinition":
        """Create from dictionary representation."""
        fields = [SchemaField(**f) for f in data.get("fields", [])]
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            fields=fields,
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def document_schema(cls) -> "SchemaDefinition":
        """Get the default document schema."""
        schema = cls(
            name="AIReadableDocument",
            version="1.0",
            description="Schema for AI-readable document output",
        )
        schema.add_field(SchemaField("title", "string", description="Document title"))
        schema.add_field(SchemaField("version", "string", description="Document version"))
        schema.add_field(SchemaField("author", "string", required=False))
        schema.add_field(
            SchemaField("created_at", "string", description="Creation timestamp")
        )
        schema.add_field(
            SchemaField("updated_at", "string", required=False, description="Update timestamp")
        )
        schema.add_field(
            SchemaField("content_type", "string", description="Document content type")
        )
        schema.add_field(
            SchemaField("sections", "array", description="Document sections")
        )
        schema.add_field(
            SchemaField("metadata", "object", required=False, description="Additional metadata")
        )
        schema.add_field(
            SchemaField("semantic_tags", "array", required=False, description="Global semantic tags")
        )
        return schema

    @classmethod
    def mcp_schema(cls) -> "SchemaDefinition":
        """Get the MCP-compatible schema."""
        schema = cls(
            name="MCPDocument",
            version="1.0",
            description="Schema for Model Context Protocol compatible output",
        )
        schema.add_field(SchemaField("context_type", "string"))
        schema.add_field(SchemaField("content", "object"))
        schema.add_field(SchemaField("annotations", "array", required=False))
        schema.add_field(SchemaField("relationships", "object", required=False))
        schema.add_field(SchemaField("metadata", "object", required=False))
        return schema


class SchemaValidator:
    """Validator for document schemas."""

    def __init__(self, schema: SchemaDefinition):
        """Initialize with a schema."""
        self.schema = schema

    def validate(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate data against schema.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required fields
        for field in self.schema.get_required_fields():
            if field.name not in data:
                errors.append(f"Missing required field: {field.name}")
            elif data[field.name] is None:
                errors.append(f"Field cannot be null: {field.name}")

        # Check field types
        for field in self.schema.fields:
            if field.name in data and data[field.name] is not None:
                if not self._check_type(data[field.name], field.field_type):
                    errors.append(
                        f"Invalid type for field '{field.name}': "
                        f"expected {field.field_type}, got {type(data[field.name]).__name__}"
                    )

        # Check enum values
        for field in self.schema.fields:
            if field.enum_values and field.name in data:
                if data[field.name] not in field.enum_values:
                    errors.append(
                        f"Invalid value for field '{field.name}': "
                        f"must be one of {field.enum_values}"
                    )

        return len(errors) == 0, errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown types are considered valid

        return isinstance(value, expected)

    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str | None]:
        """Validate a single field.

        Returns:
            Tuple of (is_valid, error_message)
        """
        field = self.schema.get_field(field_name)
        if field is None:
            return False, f"Unknown field: {field_name}"

        if field.required and value is None:
            return False, f"Required field cannot be null: {field_name}"

        if not self._check_type(value, field.field_type):
            return (
                False,
                f"Invalid type for field '{field_name}': "
                f"expected {field.field_type}, got {type(value).__name__}",
            )

        if field.enum_values and value not in field.enum_values:
            return (
                False,
                f"Invalid value for field '{field_name}': must be one of {field.enum_values}",
            )

        return True, None
