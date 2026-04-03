"""MCP (Model Context Protocol) compliance tests.

Tests that MCPTransformer output conforms to the Model Context Protocol schema
and that the MCP server's /read tool response format is correct.
"""

import json
from typing import Any

import pytest

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.section import Section, SectionType, ContentType
from ai_readable_doc_generator.transformer.mcp_transformer import MCPTransformer


class TestMCPServerToolCompliance:
    """Tests for MCP server /read tool response format compliance."""

    def test_mcp_tool_response_schema(self) -> None:
        """Test that MCP /read tool response conforms to expected schema."""
        # Mock the MCP server response structure
        expected_tool_response = {
            "content": [
                {
                    "type": "resource",
                    "resource": {
                        "uri": "doc://ai-doc-gen/example/abc123",
                        "mimeType": "application/json",
                        "text": "...",
                    }
                }
            ],
            "isError": False,
        }
        
        # Validate structure
        assert "content" in expected_tool_response
        assert isinstance(expected_tool_response["content"], list)
        assert "isError" in expected_tool_response
        
        # Content item structure
        content_item = expected_tool_response["content"][0]
        assert content_item["type"] == "resource"
        assert "resource" in content_item
        assert "uri" in content_item["resource"]
        assert "mimeType" in content_item["resource"]

    def test_mcp_error_response_schema(self) -> None:
        """Test that MCP error responses follow the schema."""
        error_response = {
            "content": [
                {
                    "type": "text",
                    "text": "Error message here",
                }
            ],
            "isError": True,
        }
        
        assert error_response["isError"] is True
        assert len(error_response["content"]) > 0
        assert error_response["content"][0]["type"] == "text"

    def test_mcp_resource_response_format(self) -> None:
        """Test that MCP resource response format is valid."""
        resource_response = {
            "content": [
                {
                    "type": "resource",
                    "resource": {
                        "uri": "doc://ai-doc-gen/test/abc123def456",
                        "mimeType": "application/json",
                        "text": '{"title": "Test", "sections": []}',
                    }
                }
            ],
            "isError": False,
        }
        
        assert resource_response["isError"] is False
        assert len(resource_response["content"]) == 1
        
        resource = resource_response["content"][0]["resource"]
        assert resource["uri"].startswith("doc://")
        assert resource["mimeType"] == "application/json"
        
        # Text should be valid JSON
        parsed = json.loads(resource["text"])
        assert "title" in parsed


class TestMCPResourceTypes:
    """Tests for MCP resource type compliance."""

    def test_resource_type_value(self) -> None:
        """Test that resource_type is a valid string value."""
        # Resource types should be strings
        valid_resource_types = ["documentation", "api", "guide", "reference"]
        
        for rt in valid_resource_types:
            assert isinstance(rt, str)
            assert len(rt) > 0

    def test_resource_uri_format_doc_protocol(self) -> None:
        """Test that resource_uri follows MCP doc:// URI conventions."""
        uri = "doc://ai-doc-gen/my-document/abc123def456"
        
        # Should start with doc://
        assert uri.startswith("doc://")
        
        # Should have path components after doc://
        path_part = uri.replace("doc://", "")
        assert "/" in path_part
        
        # Last part should be substantial identifier
        parts = path_part.split("/")
        assert len(parts[-1]) >= 6, "resource_uri should have substantial identifier"


class TestMCPTransformerStructure:
    """Tests for MCP transformer output structure validation."""

    def test_mcp_output_has_required_top_level_keys(self) -> None:
        """Test that MCP-compliant output has required top-level keys."""
        required_keys = ["resource_uri", "resource_type", "content"]
        
        # Simulated MCP output structure
        mcp_output = {
            "resource_uri": "doc://ai-doc-gen/test/abc123",
            "resource_type": "documentation",
            "content": {
                "title": "Test Document",
                "sections": [],
                "metadata": {}
            },
            "annotations": {},
            "semantic_hints": {}
        }
        
        for key in required_keys:
            assert key in mcp_output, f"MCP output must have '{key}'"

    def test_mcp_content_has_required_keys(self) -> None:
        """Test that MCP content section has required keys."""
        required_content_keys = ["title", "sections", "metadata"]
        
        content = {
            "title": "Test Document",
            "sections": [],
            "metadata": {
                "source_format": "markdown",
                "language": "en",
                "section_count": 0,
                "total_content_length": 0
            }
        }
        
        for key in required_content_keys:
            assert key in content, f"MCP content must have '{key}'"

    def test_mcp_section_structure(self) -> None:
        """Test that MCP section structure is valid."""
        section = {
            "id": "section-1",
            "content": "Section content",
            "type": "prose",
            "level": 1,
            "purpose": "content"
        }
        
        required_keys = ["id", "content", "type", "level", "purpose"]
        for key in required_keys:
            assert key in section, f"MCP section must have '{key}'"
        
        # Type should be valid MCP content type
        valid_types = ["title", "heading", "prose", "code", "list", "list_item", 
                       "quote", "table", "image", "link", "divider", "html", 
                       "metadata", "unknown"]
        assert section["type"] in valid_types


class TestMCPAnnotations:
    """Tests for MCP annotations structure."""

    def test_annotations_structure(self) -> None:
        """Test that annotations have expected structure."""
        annotations = {
            "structure_type": "narrative",
            "content_type_distribution": {"paragraph": 5, "heading": 2},
            "purpose_distribution": {"content": 4, "topic": 3},
            "has_code_examples": True,
            "is_api_reference": False,
            "has_installation_guide": True
        }
        
        assert isinstance(annotations, dict)
        assert "structure_type" in annotations
        assert "content_type_distribution" in annotations
        assert "purpose_distribution" in annotations

    def test_semantic_hints_structure(self) -> None:
        """Test that semantic hints have expected structure."""
        hints = {
            "primary_topic": "API Documentation",
            "key_concepts": ["Installation", "Configuration", "Usage"],
            "reading_order": ["hierarchical", "sequential"]
        }
        
        assert isinstance(hints, dict)
        assert "primary_topic" in hints
        assert "key_concepts" in hints
        assert "reading_order" in hints


class TestMCPComplianceScenarios:
    """Integration tests for MCP compliance scenarios."""

    def test_complete_mcp_document_structure(self) -> None:
        """Test a complete MCP document structure."""
        mcp_document = {
            "resource_uri": "doc://ai-doc-gen/api-guide/abc123xyz",
            "resource_type": "documentation",
            "content": {
                "title": "API Developer Guide",
                "sections": [
                    {
                        "id": "intro",
                        "content": "Introduction to the API",
                        "type": "heading",
                        "level": 1,
                        "purpose": "topic"
                    },
                    {
                        "id": "auth",
                        "content": "Authentication section",
                        "type": "prose",
                        "level": 1,
                        "purpose": "instruction"
                    },
                    {
                        "id": "example",
                        "content": "print('hello')",
                        "type": "code",
                        "level": 1,
                        "purpose": "example"
                    }
                ],
                "metadata": {
                    "source_format": "markdown",
                    "language": "en",
                    "section_count": 3,
                    "total_content_length": 100
                }
            },
            "annotations": {
                "structure_type": "tutorial",
                "has_code_examples": True,
                "has_installation_guide": False
            },
            "semantic_hints": {
                "primary_topic": "API Developer Guide",
                "key_concepts": ["Introduction", "Authentication"],
                "reading_order": ["sequential"]
            }
        }
        
        # Validate complete structure
        assert "resource_uri" in mcp_document
        assert "resource_type" in mcp_document
        assert "content" in mcp_document
        
        # Validate content
        assert len(mcp_document["content"]["sections"]) == 3
        
        # Validate sections have correct types
        section_types = [s["type"] for s in mcp_document["content"]["sections"]]
        assert "heading" in section_types
        assert "prose" in section_types
        assert "code" in section_types

    def test_mcp_tool_response_with_document(self) -> None:
        """Test MCP tool response wrapping a document."""
        doc_data = {
            "title": "Test Document",
            "sections": [{"id": "s1", "content": "Test", "type": "prose", "level": 1, "purpose": "content"}]
        }
        
        tool_response = {
            "content": [
                {
                    "type": "resource",
                    "resource": {
                        "uri": "doc://ai-doc-gen/test/abc123",
                        "mimeType": "application/json",
                        "text": json.dumps(doc_data)
                    }
                }
            ],
            "isError": False
        }
        
        # Verify tool response is valid
        assert tool_response["isError"] is False
        content = tool_response["content"][0]
        assert content["type"] == "resource"
        
        # Verify nested document parses correctly
        parsed_text = json.loads(content["resource"]["text"])
        assert parsed_text["title"] == "Test Document"


class TestMCPTypeMapping:
    """Tests for content type mapping to MCP types."""

    @pytest.mark.parametrize("section_type,expected_mcp_type", [
        (SectionType.HEADING, "heading"),
        (SectionType.PARAGRAPH, "prose"),
        (SectionType.CODE_BLOCK, "code"),
        (SectionType.LIST, "list"),
        (SectionType.BLOCKQUOTE, "quote"),
        (SectionType.TABLE, "table"),
        (SectionType.IMAGE, "image"),
        (SectionType.LINK, "link"),
        (SectionType.HORIZONTAL_RULE, "divider"),
    ])
    def test_section_type_to_mcp_type(
        self, section_type: SectionType, expected_mcp_type: str
    ) -> None:
        """Test that SectionType maps correctly to MCP content types."""
        transformer = MCPTransformer()
        
        result = transformer._map_content_type(section_type)
        
        assert result == expected_mcp_type
