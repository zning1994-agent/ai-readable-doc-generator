"""Tests for Schema model."""

import pytest

from ai_readable_doc_generator.models import MCPSchemaType, OutputSchema, SchemaConfig


class TestSchema:
    """Tests for schema-related classes."""

    def test_output_schema_values(self) -> None:
        """Test OutputSchema enum values."""
        assert OutputSchema.JSON.value == "json"
        assert OutputSchema.YAML.value == "yaml"
        assert OutputSchema.MCP.value == "mcp"

    def test_mcp_schema_type_values(self) -> None:
        """Test MCPSchemaType enum values."""
        assert MCPSchemaType.TEXT.value == "text"
        assert MCPSchemaType.CODE.value == "code"
        assert MCPSchemaType.RESOURCE.value == "resource"

    def test_schema_config_defaults(self) -> None:
        """Test SchemaConfig default values."""
        config = SchemaConfig()
        assert config.schema == OutputSchema.JSON
        assert config.include_metadata is True
        assert config.include_structure is True
        assert config.pretty_print is True
        assert config.indent == 2
