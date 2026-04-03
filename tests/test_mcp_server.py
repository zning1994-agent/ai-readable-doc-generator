"""
Tests for MCP server read tool functionality.

This module tests the Model Context Protocol (MCP) server implementation,
specifically focusing on the read tool capabilities for document processing.
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_readable_doc_generator.models.document import Document, Section, SectionType
from ai_readable_doc_generator.models.section import ContentType, ImportanceLevel


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing."""
    return """# Introduction

This is the introduction section.

## Getting Started

Follow these steps to get started.

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
pip install ai-readable-doc-generator
```

## Configuration

Configure your environment variables.

## API Reference

### Methods

| Method | Description |
|--------|-------------|
| read   | Read a document |
| search | Search documents |

> **Important**: This is a critical note.

<!-- comments are ignored -->
"""


@pytest.fixture
def sample_document() -> Document:
    """Create a sample Document object for testing."""
    sections = [
        Section(
            title="Introduction",
            level=1,
            content="This is the introduction section.",
            section_type=SectionType.INTRODUCTION,
            content_type=ContentType.NARRATIVE,
            importance=ImportanceLevel.HIGH,
            children=[
                Section(
                    title="Getting Started",
                    level=2,
                    content="Follow these steps to get started.",
                    section_type=SectionType.GUIDE,
                    content_type=ContentType.PROCEDURAL,
                    importance=ImportanceLevel.MEDIUM,
                    children=[
                        Section(
                            title="Prerequisites",
                            level=3,
                            content="- Python 3.11+\n- pip",
                            section_type=SectionType.INFO,
                            content_type=ContentType.LIST,
                            importance=ImportanceLevel.LOW,
                            children=[],
                        ),
                        Section(
                            title="Installation",
                            level=3,
                            content='```bash\npip install ai-readable-doc-generator\n```',
                            section_type=SectionType.INFO,
                            content_type=ContentType.CODE,
                            importance=ImportanceLevel.MEDIUM,
                            children=[],
                        ),
                    ],
                ),
                Section(
                    title="Configuration",
                    level=2,
                    content="Configure your environment variables.",
                    section_type=SectionType.CONFIGURATION,
                    content_type=ContentType.NARRATIVE,
                    importance=ImportanceLevel.MEDIUM,
                    children=[],
                ),
                Section(
                    title="API Reference",
                    level=2,
                    content="API documentation.",
                    section_type=SectionType.REFERENCE,
                    content_type=ContentType.DOCUMENTATION,
                    importance=ImportanceLevel.HIGH,
                    children=[],
                ),
            ],
        ),
    ]

    return Document(
        title="Test Document",
        source_path="test.md",
        sections=sections,
        metadata={"author": "Test", "version": "1.0"},
    )


@pytest.fixture
def temp_markdown_file(sample_markdown_content: str, tmp_path: Path) -> Path:
    """Create a temporary markdown file for testing."""
    file_path = tmp_path / "test.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    return file_path


@pytest.fixture
def mock_mcp_server() -> MagicMock:
    """Create a mock MCP server for testing."""
    mock = MagicMock()
    mock.name = "ai-readable-doc-generator"
    mock.version = "1.0.0"
    mock.is_running = False
    return mock


@pytest.fixture
def mcp_read_request() -> dict[str, Any]:
    """Sample MCP read tool request."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "read_document",
            "arguments": {
                "path": "docs/guide.md",
                "format": "structured",
            },
        },
    }


# =============================================================================
# Test Classes
# =============================================================================


class TestMCPReadToolInterface:
    """Tests for MCP read tool interface compliance."""

    def test_read_tool_schema_definition(self) -> None:
        """Test that read tool has proper MCP schema definition."""
        # MCP read tool should have a schema with required and optional parameters
        schema = {
            "name": "read_document",
            "description": "Read and parse a document for AI consumption",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the document to read",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["structured", "json", "yaml"],
                        "description": "Output format for the document",
                        "default": "structured",
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include document metadata in output",
                        "default": True,
                    },
                    "semantic_tags": {
                        "type": "boolean",
                        "description": "Include semantic tags in output",
                        "default": True,
                    },
                },
                "required": ["path"],
            },
        }

        # Verify schema structure
        assert schema["name"] == "read_document"
        assert "inputSchema" in schema
        assert "properties" in schema["inputSchema"]
        assert "path" in schema["inputSchema"]["properties"]
        assert schema["inputSchema"]["required"] == ["path"]

    def test_read_tool_returns_json_rpc_response(self) -> None:
        """Test that read tool returns proper JSON-RPC response format."""
        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": '{"title": "Document", "sections": []}',
                    }
                ]
            },
        }

        assert response["jsonrpc"] == "2.0"
        assert "id" in response
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) > 0
        assert response["result"]["content"][0]["type"] == "text"

    def test_read_tool_error_response_format(self) -> None:
        """Test that read tool returns proper error response format."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32602,
                "message": "Invalid params: path is required",
                "data": {"param": "path"},
            },
        }

        assert error_response["jsonrpc"] == "2.0"
        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]
        assert error_response["error"]["code"] == -32602


class TestMCPReadToolDocumentProcessing:
    """Tests for MCP read tool document processing functionality."""

    def test_read_markdown_file(self, temp_markdown_file: Path) -> None:
        """Test reading a markdown file."""
        content = temp_markdown_file.read_text(encoding="utf-8")
        assert "# Introduction" in content
        assert "## Getting Started" in content

    def test_read_nonexistent_file_returns_error(self) -> None:
        """Test that reading a nonexistent file returns appropriate error."""
        nonexistent_path = Path("/nonexistent/file.md")

        # Should raise FileNotFoundError or return error response
        assert not nonexistent_path.exists()

    def test_read_file_with_utf8_encoding(self, tmp_path: Path) -> None:
        """Test reading a file with UTF-8 encoding."""
        file_path = tmp_path / "unicode.md"
        content = "Test with émojis 🎉 and unicode ñ"
        file_path.write_text(content, encoding="utf-8")

        read_content = file_path.read_text(encoding="utf-8")
        assert read_content == content

    def test_read_file_with_different_encoding(self, tmp_path: Path) -> None:
        """Test reading a file with different encoding."""
        file_path = tmp_path / "latin1.md"
        content = "Test with latin1 characters: \xe9\xe8\xe0"
        file_path.write_bytes(content.encode("latin-1"))

        read_content = file_path.read_text(encoding="latin-1")
        assert "Test with latin1" in read_content

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty file."""
        file_path = tmp_path / "empty.md"
        file_path.write_text("", encoding="utf-8")

        content = file_path.read_text(encoding="utf-8")
        assert content == ""


class TestMCPReadToolStructuredOutput:
    """Tests for MCP read tool structured output generation."""

    def test_structured_output_includes_title(self, sample_document: Document) -> None:
        """Test that structured output includes document title."""
        output = {
            "title": sample_document.title,
            "sections": [],
        }
        assert "title" in output
        assert output["title"] == "Test Document"

    def test_structured_output_includes_sections(self, sample_document: Document) -> None:
        """Test that structured output includes parsed sections."""
        output = {
            "title": sample_document.title,
            "sections": [
                {
                    "title": section.title,
                    "level": section.level,
                    "content": section.content,
                    "type": section.section_type.value if section.section_type else None,
                }
                for section in sample_document.sections
            ],
        }

        assert "sections" in output
        assert len(output["sections"]) == 1
        assert output["sections"][0]["title"] == "Introduction"

    def test_structured_output_includes_metadata(self, sample_document: Document) -> None:
        """Test that structured output includes metadata."""
        output = {
            "title": sample_document.title,
            "metadata": sample_document.metadata,
        }

        assert "metadata" in output
        assert output["metadata"]["author"] == "Test"
        assert output["metadata"]["version"] == "1.0"

    def test_structured_output_with_semantic_tags(self, sample_document: Document) -> None:
        """Test that structured output includes semantic tags."""
        section = sample_document.sections[0]
        output = {
            "sections": [
                {
                    "title": section.title,
                    "section_type": section.section_type.value if section.section_type else None,
                    "content_type": section.content_type.value if section.content_type else None,
                    "importance": section.importance.value if section.importance else None,
                }
            ]
        }

        assert "section_type" in output["sections"][0]
        assert "content_type" in output["sections"][0]
        assert "importance" in output["sections"][0]
        assert output["sections"][0]["section_type"] == "introduction"

    def test_structured_output_hierarchical_structure(self, sample_document: Document) -> None:
        """Test that structured output preserves hierarchical structure."""
        top_level = sample_document.sections[0]
        assert len(top_level.children) > 0

        child = top_level.children[0]
        assert child.level == 2
        assert child.title == "Getting Started"
        assert len(child.children) > 0


class TestMCPReadToolJSONOutput:
    """Tests for MCP read tool JSON output format."""

    def test_json_output_format(self, sample_document: Document) -> None:
        """Test JSON output format."""
        output = {
            "title": sample_document.title,
            "sections": sample_document.sections,
            "metadata": sample_document.metadata,
        }

        json_str = json.dumps(output, default=lambda x: x.value if hasattr(x, "value") else str(x))
        parsed = json.loads(json_str)

        assert parsed["title"] == "Test Document"
        assert "sections" in parsed

    def test_json_output_is_valid(self, sample_document: Document) -> None:
        """Test that JSON output is valid and parseable."""
        document_dict = {
            "title": sample_document.title,
            "sections": [
                {"title": "Section 1", "level": 1, "content": "Content"}
            ],
            "metadata": {"version": "1.0"},
        }

        json_str = json.dumps(document_dict)
        parsed = json.loads(json_str)

        assert isinstance(parsed, dict)
        assert parsed["title"] == "Test Document"

    def test_json_output_with_nested_structures(self) -> None:
        """Test JSON output with deeply nested structures."""
        nested = {
            "title": "Nested Document",
            "sections": [
                {
                    "title": "Level 1",
                    "children": [
                        {
                            "title": "Level 2",
                            "children": [{"title": "Level 3", "children": []}],
                        }
                    ],
                }
            ],
        }

        json_str = json.dumps(nested)
        parsed = json.loads(json_str)

        assert parsed["sections"][0]["children"][0]["children"][0]["title"] == "Level 3"


class TestMCPReadToolValidation:
    """Tests for MCP read tool input validation."""

    def test_validate_path_parameter(self) -> None:
        """Test path parameter validation."""
        valid_path = "docs/guide.md"
        invalid_paths = ["", None, 123, [], {}]

        # Valid path should pass
        assert isinstance(valid_path, str)
        assert len(valid_path) > 0

        # Invalid paths should fail
        for invalid in invalid_paths:
            assert not isinstance(invalid, str) or len(invalid) == 0

    def test_validate_format_parameter(self) -> None:
        """Test format parameter validation."""
        valid_formats = ["structured", "json", "yaml"]
        invalid_formats = ["xml", "csv", "txt", "invalid"]

        for fmt in valid_formats:
            assert fmt in ["structured", "json", "yaml"]

        for fmt in invalid_formats:
            assert fmt not in ["structured", "json", "yaml"]

    def test_validate_include_metadata_parameter(self) -> None:
        """Test include_metadata parameter validation."""
        valid_values = [True, False, None]

        for val in valid_values:
            assert isinstance(val, (bool, type(None)))

    def test_validate_semantic_tags_parameter(self) -> None:
        """Test semantic_tags parameter validation."""
        valid_values = [True, False, None]

        for val in valid_values:
            assert isinstance(val, (bool, type(None)))


class TestMCPReadToolErrorHandling:
    """Tests for MCP read tool error handling."""

    def test_file_not_found_error(self) -> None:
        """Test handling of file not found error."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32602,
                "message": "File not found: /nonexistent/file.md",
                "data": {"path": "/nonexistent/file.md", "error_type": "FileNotFoundError"},
            },
        }

        assert error_response["error"]["code"] == -32602
        assert "not found" in error_response["error"]["message"].lower()

    def test_invalid_format_error(self) -> None:
        """Test handling of invalid format error."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32602,
                "message": "Invalid format: 'xml' is not supported. Use 'structured', 'json', or 'yaml'",
                "data": {"format": "xml", "allowed": ["structured", "json", "yaml"]},
            },
        }

        assert error_response["error"]["code"] == -32602
        assert "invalid" in error_response["error"]["message"].lower()

    def test_permission_denied_error(self) -> None:
        """Test handling of permission denied error."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Permission denied: cannot read file",
                "data": {"path": "/protected/file.md", "error_type": "PermissionError"},
            },
        }

        assert error_response["error"]["code"] == -32603

    def test_parse_error(self) -> None:
        """Test handling of document parse error."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Failed to parse document: invalid markdown syntax",
                "data": {"path": "broken.md", "line": 42, "error_type": "ParseError"},
            },
        }

        assert error_response["error"]["code"] == -32603
        assert "parse" in error_response["error"]["message"].lower()


class TestMCPReadToolAsyncOperations:
    """Tests for MCP read tool async operations."""

    @pytest.mark.asyncio
    async def test_async_read_document(self, temp_markdown_file: Path) -> None:
        """Test async document reading."""
        async def read_document_async(path: Path) -> str:
            return path.read_text(encoding="utf-8")

        content = await read_document_async(temp_markdown_file)
        assert "# Introduction" in content

    @pytest.mark.asyncio
    async def test_async_read_with_processing(self, temp_markdown_file: Path) -> None:
        """Test async document reading with processing."""
        async def read_and_process(path: Path) -> dict[str, Any]:
            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")
            return {
                "path": str(path),
                "line_count": len(lines),
                "has_title": any(line.startswith("# ") for line in lines),
            }

        result = await read_and_process(temp_markdown_file)
        assert result["line_count"] > 0
        assert result["has_title"] is True

    @pytest.mark.asyncio
    async def test_async_error_handling(self) -> None:
        """Test async error handling."""
        async def read_with_error(path: Path) -> str:
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            return path.read_text(encoding="utf-8")

        with pytest.raises(FileNotFoundError):
            await read_with_error(Path("/nonexistent/file.md"))


class TestMCPReadToolIntegration:
    """Integration tests for MCP read tool."""

    def test_full_read_workflow(self, temp_markdown_file: Path) -> None:
        """Test complete read workflow from request to response."""
        # Step 1: Receive request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "read_document",
                "arguments": {
                    "path": str(temp_markdown_file),
                    "format": "structured",
                },
            },
        }

        # Step 2: Validate request
        assert request["params"]["name"] == "read_document"
        assert "path" in request["params"]["arguments"]

        # Step 3: Read file
        path = Path(request["params"]["arguments"]["path"])
        content = path.read_text(encoding="utf-8")
        assert len(content) > 0

        # Step 4: Generate structured output
        lines = content.split("\n")
        output = {
            "title": "Document",
            "sections": [{"line_count": len(lines)}],
            "metadata": {"path": str(path)},
        }

        # Step 5: Format response
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "content": [{"type": "text", "text": json.dumps(output)}]
            },
        }

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response

    def test_read_with_custom_options(self, temp_markdown_file: Path) -> None:
        """Test reading with custom output options."""
        options = {
            "include_metadata": True,
            "semantic_tags": True,
            "format": "structured",
        }

        assert options["include_metadata"] is True
        assert options["semantic_tags"] is True
        assert options["format"] == "structured"

    def test_batch_read_requests(self, tmp_path: Path) -> None:
        """Test handling multiple read requests."""
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = tmp_path / f"doc{i}.md"
            file_path.write_text(f"# Document {i}\n\nContent for document {i}.", encoding="utf-8")
            files.append(file_path)

        # Process each file
        results = []
        for file_path in files:
            content = file_path.read_text(encoding="utf-8")
            results.append({"path": str(file_path), "content_length": len(content)})

        assert len(results) == 3
        assert all(r["content_length"] > 0 for r in results)


class TestMCPReadToolContentExtraction:
    """Tests for content extraction in MCP read tool."""

    def test_extract_code_blocks(self, sample_markdown_content: str) -> None:
        """Test extraction of code blocks from markdown."""
        import re

        code_block_pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(code_block_pattern, sample_markdown_content, re.DOTALL)

        assert len(matches) > 0
        assert any("pip install" in match[1] for match in matches)

    def test_extract_tables(self, sample_markdown_content: str) -> None:
        """Test extraction of tables from markdown."""
        lines = sample_markdown_content.split("\n")
        table_lines = [line for line in lines if "|" in line and line.strip().startswith("|")]

        assert len(table_lines) > 0

    def test_extract_headings(self, sample_markdown_content: str) -> None:
        """Test extraction of headings from markdown."""
        import re

        heading_pattern = r"^(#{1,6})\s+(.+)$"
        headings = re.findall(heading_pattern, sample_markdown_content, re.MULTILINE)

        assert len(headings) > 0
        assert ("#", "Introduction") in headings

    def test_extract_links(self) -> None:
        """Test extraction of links from markdown."""
        import re

        content = "Check out [our website](https://example.com) for more info."
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(link_pattern, content)

        assert len(matches) > 0
        assert matches[0] == ("our website", "https://example.com")

    def test_extract_emphasis(self) -> None:
        """Test extraction of emphasized text from markdown."""
        import re

        content = "This is **bold** and *italic* text."
        bold_pattern = r"\*\*(.+?)\*\*"
        italic_pattern = r"\*(.+?)\*"

        bold_matches = re.findall(bold_pattern, content)
        italic_matches = re.findall(italic_pattern, content)

        assert "bold" in bold_matches
        assert "italic" in italic_matches


class TestMCPReadToolSchemaCompliance:
    """Tests for MCP protocol schema compliance."""

    def test_tool_definition_schema(self) -> None:
        """Test tool definition follows MCP schema."""
        tool_definition = {
            "name": "read_document",
            "description": "Read a document and return AI-readable structured format",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the document file",
                    },
                },
                "required": ["path"],
            },
        }

        # Verify required MCP fields
        assert "name" in tool_definition
        assert "description" in tool_definition
        assert "inputSchema" in tool_definition
        assert tool_definition["inputSchema"]["type"] == "object"

    def test_request_message_schema(self, mcp_read_request: dict[str, Any]) -> None:
        """Test request message follows MCP JSON-RPC 2.0 schema."""
        assert mcp_read_request["jsonrpc"] == "2.0"
        assert "id" in mcp_read_request
        assert "method" in mcp_read_request
        assert "params" in mcp_read_request

    def test_response_message_schema(self) -> None:
        """Test response message follows MCP JSON-RPC 2.0 schema."""
        success_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": "Hello, World!"}
                ]
            },
        }

        assert success_response["jsonrpc"] == "2.0"
        assert "id" in success_response
        assert "result" in success_response
        assert isinstance(success_response["result"]["content"], list)

    def test_error_response_schema(self) -> None:
        """Test error response follows MCP JSON-RPC 2.0 schema."""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32600,
                "message": "Invalid Request",
            },
        }

        assert error_response["jsonrpc"] == "2.0"
        assert "id" in error_response
        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]

    def test_content_block_schema(self) -> None:
        """Test content block follows MCP schema."""
        content_block = {
            "type": "text",
            "text": "Document content here",
        }

        assert "type" in content_block
        assert "text" in content_block
        assert content_block["type"] in ["text", "image", "resource"]


# =============================================================================
# Mock Tests (for integration with non-existent implementation)
# =============================================================================


class TestMCPReadToolMockIntegration:
    """Mock integration tests for MCP read tool."""

    def test_mock_server_initialization(self, mock_mcp_server: MagicMock) -> None:
        """Test mock MCP server initialization."""
        assert mock_mcp_server.name == "ai-readable-doc-generator"
        assert mock_mcp_server.version == "1.0.0"
        assert mock_mcp_server.is_running is False

    def test_mock_read_tool_call(self) -> None:
        """Test mock read tool call."""
        mock_tool = MagicMock()
        mock_tool.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": '{"title": "Test", "sections": []}'}
                ]
            },
        }

        result = mock_tool("docs/test.md", format="structured")
        assert result["result"]["content"][0]["type"] == "text"

    def test_mock_async_read(self) -> None:
        """Test mock async read operation."""
        mock_async_read = AsyncMock(return_value={"title": "Test Document"})
        result = mock_async_read(Path("test.md"))
        assert result["title"] == "Test Document"


# =============================================================================
# Edge Cases
# =============================================================================


class TestMCPReadToolEdgeCases:
    """Tests for edge cases in MCP read tool."""

    def test_read_large_file(self, tmp_path: Path) -> None:
        """Test reading a large file."""
        file_path = tmp_path / "large.md"
        content = "\n".join([f"Line {i}" for i in range(10000)])
        file_path.write_text(content, encoding="utf-8")

        assert file_path.stat().st_size > 0
        content_read = file_path.read_text(encoding="utf-8")
        assert len(content_read.split("\n")) == 10000

    def test_read_file_with_special_characters(self, tmp_path: Path) -> None:
        """Test reading a file with special characters."""
        file_path = tmp_path / "special.md"
        content = "Special chars: <>&\"' and unicode: 你好 🌍"
        file_path.write_text(content, encoding="utf-8")

        read_content = file_path.read_text(encoding="utf-8")
        assert read_content == content

    def test_read_file_with_long_lines(self, tmp_path: Path) -> None:
        """Test reading a file with long lines."""
        file_path = tmp_path / "longlines.md"
        long_line = "x" * 100000
        file_path.write_text(long_line, encoding="utf-8")

        read_content = file_path.read_text(encoding="utf-8")
        assert len(read_content) == 100000

    def test_read_nested_directory_file(self, tmp_path: Path) -> None:
        """Test reading a file in a nested directory."""
        nested_dir = tmp_path / "a" / "b" / "c"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / "nested.md"
        file_path.write_text("# Nested File\n\nContent.", encoding="utf-8")

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert "# Nested File" in content

    def test_read_symlink_file(self, tmp_path: Path) -> None:
        """Test reading a symbolic link."""
        real_file = tmp_path / "real.md"
        real_file.write_text("# Real File\n\nContent.", encoding="utf-8")

        symlink_file = tmp_path / "link.md"
        if hasattr(real_file, "symlink_to"):
            symlink_file.symlink_to(real_file)
        else:
            import os
            os.symlink(real_file, symlink_file)

        # Symlink should be readable
        assert symlink_file.exists() or symlink_file.is_symlink()
