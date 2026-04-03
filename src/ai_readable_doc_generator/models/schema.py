"""Output schema definitions for structured document output."""

from enum import Enum

from pydantic import BaseModel, Field


class SchemaType(str, Enum):
    """Supported output schema types."""

    STANDARD = "standard"
    MCP = "mcp"
    MINIMAL = "minimal"
    DETAILED = "detailed"


class OutputSchema(BaseModel):
    """Configuration for output schema formatting."""

    schema_type: SchemaType = Field(default=SchemaType.STANDARD)
    include_metadata: bool = True
    include_raw_content: bool = False
    indent: int = 2
    semantic_tags: bool = True
    include_importance: bool = True
    include_relationships: bool = True

    def model_dump(self, **kwargs) -> dict:
        """Dump schema as dictionary."""
        return {
            "schema_type": self.schema_type.value,
            "include_metadata": self.include_metadata,
            "include_raw_content": self.include_raw_content,
            "indent": self.indent,
            "semantic_tags": self.semantic_tags,
            "include_importance": self.include_importance,
            "include_relationships": self.include_relationships,
        }
