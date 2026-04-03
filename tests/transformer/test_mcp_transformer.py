"""Unit tests for MCP transformer module."""

import json
import pytest

from ai_readable_doc_generator.transformer.mcp_transformer import (
    ContentType,
    ImportanceLevel,
    MCPSection,
    MCPContext,
    MCPTransformer,
    OutputFormat,
)


class TestMCPSection:
    """Tests for MCPSection dataclass."""

    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a proper dictionary."""
        section = MCPSection(
            id="sec_1",
            title="Test Section",
            content_type=ContentType.GENERAL,
            content="Test content",
            importance=ImportanceLevel.MEDIUM,
        )
        result = section.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "sec_1"
        assert result["title"] == "Test Section"
        assert result["content_type"] == "general"
        assert result["content"] == "Test content"
        assert result["importance"] == "medium"
        assert result["parent_id"] is None
        assert result["children_ids"] == []
        assert result["metadata"] == {}
        assert result["tags"] == []

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields populated."""
        section = MCPSection(
            id="sec_2",
            title="API Reference",
            content_type=ContentType.API_REFERENCE,
            content="def foo(): pass",
            importance=ImportanceLevel.HIGH,
            parent_id="sec_1",
            children_ids=["sec_3", "sec_4"],
            metadata={"language": "python"},
            tags=["api", "reference"],
        )
        result = section.to_dict()

        assert result["parent_id"] == "sec_1"
        assert result["children_ids"] == ["sec_3", "sec_4"]
        assert result["metadata"] == {"language": "python"}
        assert result["tags"] == ["api", "reference"]


class TestMCPContext:
    """Tests for MCPContext dataclass."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        context = MCPContext(
            document_id="doc_1",
            title="Test Document",
            description="A test document",
        )
        result = context.to_dict()

        assert result["version"] == "1.0"
        assert result["document_id"] == "doc_1"
        assert result["title"] == "Test Document"
        assert result["description"] == "A test document"
        assert result["sections"] == []
        assert result["relationships"] == {}
        assert result["metadata"] == {}

    def test_to_dict_with_sections(self):
        """Test to_dict with sections included."""
        section = MCPSection(
            id="sec_1",
            title="Test",
            content_type=ContentType.GENERAL,
            content="Content",
        )
        context = MCPContext(
            document_id="doc_1",
            title="Test",
            sections=[section],
        )
        result = context.to_dict()

        assert len(result["sections"]) == 1
        assert result["sections"][0]["id"] == "sec_1"


class TestMCPTransformer:
    """Tests for MCPTransformer class."""

    def test_init_default_options(self):
        """Test initialization with default options."""
        transformer = MCPTransformer()

        assert transformer.output_format == OutputFormat.MCP_CONTEXT
        assert transformer.pretty is True
        assert transformer.indent == 2
        assert transformer.include_relationships is True
        assert transformer.include_metadata is True
        assert transformer.semantic_tagging is True
        assert transformer.importance_detection is True

    def test_init_custom_options(self):
        """Test initialization with custom options."""
        options = {
            "output_format": "mcp_resource",
            "pretty": False,
            "indent": 4,
            "include_relationships": False,
            "semantic_tagging": False,
        }
        transformer = MCPTransformer(options)

        assert transformer.output_format == OutputFormat.MCP_RESOURCE
        assert transformer.pretty is False
        assert transformer.indent == 4
        assert transformer.include_relationships is False
        assert transformer.semantic_tagging is False

    def test_validate_with_none(self):
        """Test validate returns False for None."""
        transformer = MCPTransformer()
        assert transformer.validate(None) is False

    def test_validate_with_empty_dict(self):
        """Test validate returns False for empty dict."""
        transformer = MCPTransformer()
        assert transformer.validate({}) is False

    def test_validate_with_valid_dict(self):
        """Test validate returns True for dict with required fields."""
        transformer = MCPTransformer()
        assert transformer.validate({"title": "Test"}) is True
        assert transformer.validate({"sections": []}) is True
        assert transformer.validate({"content": "Test"}) is True

    def test_validate_with_object(self):
        """Test validate with object having to_dict method."""
        transformer = MCPTransformer()

        class MockDocument:
            def to_dict(self):
                return {"title": "Test"}

        assert transformer.validate(MockDocument()) is True


class TestMCPTransformerTransform:
    """Tests for MCPTransformer.transform method."""

    def test_transform_basic_dict(self):
        """Test basic transformation of a dictionary."""
        transformer = MCPTransformer()
        document = {
            "id": "doc_1",
            "title": "Test Document",
            "description": "A test document",
            "sections": [
                {
                    "id": "sec_1",
                    "title": "Introduction",
                    "content": "Welcome to the document",
                }
            ],
        }

        result = transformer.transform(document)
        data = json.loads(result)

        assert data["document_id"] == "doc_1"
        assert data["title"] == "Test Document"
        assert len(data["sections"]) == 1
        assert data["sections"][0]["title"] == "Introduction"

    def test_transform_with_object(self):
        """Test transformation with object having to_dict method."""
        transformer = MCPTransformer()

        class MockDocument:
            def to_dict(self):
                return {
                    "title": "Object Document",
                    "sections": [
                        {"id": "s1", "title": "Section 1", "content": "Content 1"}
                    ],
                }

        result = transformer.transform(MockDocument())
        data = json.loads(result)

        assert data["title"] == "Object Document"
        assert len(data["sections"]) == 1

    def test_transform_pretty_print(self):
        """Test that pretty printing works."""
        transformer = MCPTransformer({"pretty": True})
        document = {"title": "Test", "sections": []}

        result = transformer.transform(document)

        assert "\n" in result
        assert "  " in result

    def test_transform_no_pretty_print(self):
        """Test that non-pretty output is compact."""
        transformer = MCPTransformer({"pretty": False})
        document = {"title": "Test", "sections": []}

        result = transformer.transform(document)

        assert "\n" not in result


class TestMCPTransformerSemanticTagging:
    """Tests for semantic tagging functionality."""

    def test_detect_api_reference(self):
        """Test detection of API reference content type."""
        transformer = MCPTransformer()
        content_type = transformer._detect_content_type(
            "API Reference", "def get_user(user_id): pass"
        )
        assert content_type == ContentType.API_REFERENCE

    def test_detect_tutorial(self):
        """Test detection of tutorial content type."""
        transformer = MCPTransformer()
        content_type = transformer._detect_content_type(
            "Getting Started Guide", "Follow these steps..."
        )
        assert content_type == ContentType.TUTORIAL

    def test_detect_code(self):
        """Test detection of code content type."""
        transformer = MCPTransformer()
        content_type = transformer._detect_content_type(
            "Examples", "```python\ndef foo(): pass\n```"
        )
        assert content_type == ContentType.CODE

    def test_detect_warning(self):
        """Test detection of warning content type."""
        transformer = MCPTransformer()
        content_type = transformer._detect_content_type(
            "Warning", "This may cause data loss"
        )
        assert content_type == ContentType.WARNING

    def test_detect_general(self):
        """Test default to general content type."""
        transformer = MCPTransformer()
        content_type = transformer._detect_content_type(
            "Some Random Title", "Random content"
        )
        assert content_type == ContentType.GENERAL


class TestMCPTransformerImportance:
    """Tests for importance detection functionality."""

    def test_detect_critical(self):
        """Test detection of critical importance."""
        transformer = MCPTransformer()
        importance = transformer._detect_importance(
            "Security Vulnerability", "Fix this now", ContentType.GENERAL
        )
        assert importance == ImportanceLevel.CRITICAL

    def test_detect_high(self):
        """Test detection of high importance."""
        transformer = MCPTransformer()
        importance = transformer._detect_importance(
            "Important Update", "Read this", ContentType.WARNING
        )
        assert importance == ImportanceLevel.HIGH

    def test_detect_low(self):
        """Test detection of low importance."""
        transformer = MCPTransformer()
        importance = transformer._detect_importance(
            "See Also", "Related topics", ContentType.GENERAL
        )
        assert importance == ImportanceLevel.LOW

    def test_detect_medium_default(self):
        """Test default medium importance."""
        transformer = MCPTransformer()
        importance = transformer._detect_importance(
            "Regular Section", "Normal content", ContentType.GENERAL
        )
        assert importance == ImportanceLevel.MEDIUM


class TestMCPTransformerTags:
    """Tests for tag extraction functionality."""

    def test_extract_language_tags(self):
        """Test extraction of language tags."""
        transformer = MCPTransformer()
        tags = transformer._extract_tags(
            "Python Example", "def hello(): print('world')"
        )

        assert "python" in tags

    def test_extract_feature_tags(self):
        """Test extraction of feature tags."""
        transformer = MCPTransformer()
        tags = transformer._extract_tags(
            "Installation Guide", "pip install package"
        )

        assert "setup" in tags


class TestMCPTransformerRelationships:
    """Tests for relationship building functionality."""

    def test_build_parent_child_relationships(self):
        """Test building parent-child relationships."""
        transformer = MCPTransformer()
        sections = [
            MCPSection(
                id="sec_1",
                title="Parent",
                content_type=ContentType.GENERAL,
                content="",
                children_ids=["sec_2"],
            ),
            MCPSection(
                id="sec_2",
                title="Child",
                content_type=ContentType.GENERAL,
                content="",
                parent_id="sec_1",
            ),
        ]

        relationships = transformer._build_relationships(sections)

        assert "sec_1" in relationships
        assert "sec_2" in relationships
        assert "by_content_type" in relationships

    def test_build_content_type_relationships(self):
        """Test building content type relationships."""
        transformer = MCPTransformer()
        sections = [
            MCPSection(
                id="sec_1",
                title="API 1",
                content_type=ContentType.API_REFERENCE,
                content="",
            ),
            MCPSection(
                id="sec_2",
                title="API 2",
                content_type=ContentType.API_REFERENCE,
                content="",
            ),
        ]

        relationships = transformer._build_relationships(sections)
        by_type = relationships["by_content_type"]

        assert "api_reference" in by_type
        assert len(by_type["api_reference"]) == 2


class TestMCPTransformerMetadata:
    """Tests for metadata extraction functionality."""

    def test_extract_standard_metadata(self):
        """Test extraction of standard metadata fields."""
        transformer = MCPTransformer()
        doc_data = {
            "title": "Test",
            "author": "John Doe",
            "version": "1.0.0",
            "license": "MIT",
        }

        metadata = transformer._extract_metadata(doc_data)

        assert metadata["author"] == "John Doe"
        assert metadata["version"] == "1.0.0"
        assert metadata["license"] == "MIT"

    def test_extract_section_count(self):
        """Test extraction of section count."""
        transformer = MCPTransformer()
        doc_data = {
            "title": "Test",
            "sections": [
                {"id": "1", "title": "S1"},
                {"id": "2", "title": "S2"},
            ],
        }

        metadata = transformer._extract_metadata(doc_data)

        assert metadata["section_count"] == 2


class TestMCPTransformerOutputFormats:
    """Tests for different output format options."""

    def test_output_format_mcp_context(self):
        """Test MCP_CONTEXT output format."""
        transformer = MCPTransformer({"output_format": "mcp_context"})
        document = {"title": "Test", "sections": []}

        result = transformer.transform(document)
        data = json.loads(result)

        assert "document_id" in data
        assert "sections" in data

    def test_output_format_mcp_resource(self):
        """Test MCP_RESOURCE output format."""
        transformer = MCPTransformer({"output_format": "mcp_resource"})
        document = {"id": "doc_1", "title": "Test", "sections": []}

        result = transformer.transform(document)
        data = json.loads(result)

        assert "resource" in data
        assert "contents" in data
        assert data["resource"]["uri"] == "doc://doc_1"

    def test_output_format_mcp_tool_schema(self):
        """Test MCP_TOOL_SCHEMA output format."""
        transformer = MCPTransformer({"output_format": "mcp_tool_schema"})
        document = {
            "id": "doc_1",
            "title": "Test Document",
            "description": "A test",
            "sections": [
                {"id": "sec_1", "title": "Section 1", "content": "Content 1"}
            ],
        }

        result = transformer.transform(document)
        data = json.loads(result)

        assert "name" in data
        assert "description" in data
        assert "inputSchema" in data
        assert "available_sections" in data
        assert len(data["available_sections"]) == 1


class TestMCPTransformerHelpers:
    """Tests for helper methods."""

    def test_get_available_content_types(self):
        """Test getting available content types."""
        transformer = MCPTransformer()
        types = transformer.get_available_content_types()

        assert "introduction" in types
        assert "api_reference" in types
        assert "tutorial" in types
        assert "general" in types

    def test_get_available_importance_levels(self):
        """Test getting available importance levels."""
        transformer = MCPTransformer()
        levels = transformer.get_available_importance_levels()

        assert "critical" in levels
        assert "high" in levels
        assert "medium" in levels
        assert "low" in levels
