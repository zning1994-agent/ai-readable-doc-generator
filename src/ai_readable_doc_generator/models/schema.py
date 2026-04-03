"""Output schema model for configurable output formats."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutputFormat(Enum):
    """Enumeration of supported output formats."""

    JSON = "json"
    YAML = "yaml"
    MCP = "mcp"


@dataclass
class SchemaField:
    """Represents a field in the output schema.

    Attributes:
        name: Field name in output.
        path: JSONPath to source data.
        transform: Optional transformation function name.
        required: Whether field is required.
        default: Default value if source is missing.
    """

    name: str
    path: str
    transform: str | None = None
    required: bool = True
    default: Any = None


@dataclass
class OutputSchema:
    """Configuration for output schema.

    Attributes:
        format: Output format type.
        include_metadata: Whether to include document metadata.
        include_toc: Whether to include table of contents.
        semantic_tags: Whether to include semantic tag information.
        fields: Custom fields configuration.
    """

    format: OutputFormat = OutputFormat.JSON
    include_metadata: bool = True
    include_toc: bool = True
    semantic_tags: bool = True
    fields: list[SchemaField] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary representation.

        Returns:
            Dictionary containing schema configuration.
        """
        return {
            "format": self.format.value,
            "include_metadata": self.include_metadata,
            "include_toc": self.include_toc,
            "semantic_tags": self.semantic_tags,
            "fields": [
                {
                    "name": f.name,
                    "path": f.path,
                    "transform": f.transform,
                    "required": f.required,
                    "default": f.default,
                }
                for f in self.fields
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OutputSchema":
        """Create schema from dictionary representation.

        Args:
            data: Dictionary containing schema configuration.

        Returns:
            OutputSchema instance.
        """
        format_value = data.get("format", "json")
        output_format = OutputFormat(format_value)

        fields = [
            SchemaField(
                name=f["name"],
                path=f["path"],
                transform=f.get("transform"),
                required=f.get("required", True),
                default=f.get("default"),
            )
            for f in data.get("fields", [])
        ]

        return cls(
            format=output_format,
            include_metadata=data.get("include_metadata", True),
            include_toc=data.get("include_toc", True),
            semantic_tags=data.get("semantic_tags", True),
            fields=fields,
        )

    @classmethod
    def default_json(cls) -> "OutputSchema":
        """Create default JSON output schema.

        Returns:
            OutputSchema with default JSON configuration.
        """
        return cls(
            format=OutputFormat.JSON,
            include_metadata=True,
            include_toc=True,
            semantic_tags=True,
            fields=[
                SchemaField("title", "title", required=False),
                SchemaField("content", "sections[*].content"),
                SchemaField("type", "sections[*].type"),
                SchemaField("level", "sections[*].level"),
            ],
        )

    @classmethod
    def default_mcp(cls) -> "OutputSchema":
        """Create default MCP-compatible output schema.

        Returns:
            OutputSchema with MCP configuration.
        """
        return cls(
            format=OutputFormat.MCP,
            include_metadata=True,
            include_toc=True,
            semantic_tags=True,
            fields=[
                SchemaField("context", "title"),
                SchemaField("sections", "sections"),
                SchemaField("relationships", "metadata.relationships"),
            ],
        )
