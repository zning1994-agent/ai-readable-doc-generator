"""Schema definitions for structured output."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutputSchema(Enum):
    """Supported output schema formats."""

    JSON = "json"
    YAML = "yaml"
    MCP = "mcp"


class MCPSchemaType(Enum):
    """MCP (Model Context Protocol) schema types."""

    TEXT = "text"
    CODE = "code"
    RESOURCE = "resource"
    PROMPT = "prompt"


@dataclass
class MCPSchema:
    """Schema for MCP-compatible output."""

    schema_type: MCPSchemaType
    content: str
    uri: str | None = None
    mime_type: str | None = None
    annotations: dict[str, Any] | None = None


@dataclass
class SchemaConfig:
    """Configuration for output schema."""

    schema: OutputSchema = OutputSchema.JSON
    include_raw: bool = False
    include_metadata: bool = True
    include_structure: bool = True
    pretty_print: bool = True
    indent: int = 2

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "schema": self.schema.value,
            "include_raw": self.include_raw,
            "include_metadata": self.include_metadata,
            "include_structure": self.include_structure,
            "pretty_print": self.pretty_print,
            "indent": self.indent,
        }
