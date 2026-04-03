"""
Tests for the processor pipeline including format detection and error handling.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from ai_readable_doc_generator.base import BaseProcessor
from ai_readable_doc_generator.converter import DocumentConverter
from ai_readable_doc_generator.parser.base import BaseParser
from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer
from ai_readable_doc_generator.transformer.json_transformer import JsonTransformer
from ai_readable_doc_generator.transformer.mcp_transformer import MCPTransformer


# =============================================================================
# Format Detection Tests
# =============================================================================


class TestFormatDetection:
    """Test cases for format detection functionality."""

    def test_detect_markdown_by_extension(self, tmp_path: Path) -> None:
        """Test that markdown files are correctly identified by extension."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Document")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"

    def test_detect_markdown_with_uppercase_extension(self, tmp_path: Path) -> None:
        """Test that markdown files with uppercase extension are detected."""
        test_file = tmp_path / "test.MD"
        test_file.write_text("# Test Document")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"

    def test_detect_markdown_with_mixed_case_extension(self, tmp_path: Path) -> None:
        """Test that markdown files with mixed case extension are detected."""
        test_file = tmp_path / "test.MarkDown"
        test_file.write_text("# Test Document")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"

    def test_detect_markdown_with_content_header(self, tmp_path: Path) -> None:
        """Test markdown detection by content when extension is unknown."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("# Markdown Header\n\nSome content")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"

    def test_detect_unknown_format(self, tmp_path: Path) -> None:
        """Test that unknown file formats return None or raise appropriate error."""
        test_file = tmp_path / "test.unknown"
        test_file.write_text("Some content")

        with pytest.raises(ValueError) as exc_info:
            DocumentConverter.detect_format(str(test_file))
        assert "Unsupported format" in str(exc_info.value) or "Unknown format" in str(exc_info.value)

    def test_detect_format_from_content_type_header(self, tmp_path: Path) -> None:
        """Test format detection from content analysis when extension is ambiguous."""
        # Markdown content with typical markers
        markdown_content = """# Heading 1
## Heading 2
- List item 1
- List item 2
```code block```
"""
        test_file = tmp_path / "document.data"
        test_file.write_text(markdown_content)

        # The converter should try content-based detection
        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"

    def test_detect_json_format(self, tmp_path: Path) -> None:
        """Test JSON file format detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "json"

    def test_detect_yaml_format(self, tmp_path: Path) -> None:
        """Test YAML file format detection."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key: value")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "yaml"

    def test_detect_non_existent_file(self, tmp_path: Path) -> None:
        """Test error handling when file does not exist."""
        non_existent = tmp_path / "non_existent.md"

        with pytest.raises(FileNotFoundError):
            DocumentConverter.detect_format(str(non_existent))

    def test_detect_empty_file(self, tmp_path: Path) -> None:
        """Test format detection for empty files."""
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        detected_format = DocumentConverter.detect_format(str(test_file))
        assert detected_format == "markdown"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestConverterErrorHandling:
    """Test cases for converter error handling."""

    def test_converter_with_invalid_input_path(self) -> None:
        """Test converter handles invalid input path gracefully."""
        converter = DocumentConverter()

        with pytest.raises(FileNotFoundError):
            converter.convert("/nonexistent/path/file.md")

    def test_converter_with_unsupported_format(self, tmp_path: Path) -> None:
        """Test converter handles unsupported format gracefully."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")

        converter = DocumentConverter()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            converter.convert(str(test_file))
        assert "Unsupported" in str(exc_info.value) or "format" in str(exc_info.value).lower()

    def test_converter_with_corrupted_markdown(self, tmp_path: Path) -> None:
        """Test converter handles corrupted/invalid markdown gracefully."""
        # Invalid UTF-8 content or malformed markdown
        test_file = tmp_path / "test.md"
        test_file.write_bytes(b"\x00\x01\x02 Invalid Markdown Content")

        converter = DocumentConverter()

        # Should either raise a specific error or return partial results
        with pytest.raises((ValueError, UnicodeDecodeError, Exception)):
            converter.convert(str(test_file))

    def test_converter_with_empty_content(self, tmp_path: Path) -> None:
        """Test converter handles empty file content."""
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        # Should return valid result for empty content
        assert result is not None

    def test_converter_with_very_long_lines(self, tmp_path: Path) -> None:
        """Test converter handles files with very long lines."""
        test_file = tmp_path / "long.md"
        # Create content with very long lines (> 10000 chars)
        long_content = "# Header\n" + ("a" * 20000) + "\n"
        test_file.write_text(long_content)

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_converter_with_binary_content(self, tmp_path: Path) -> None:
        """Test converter handles binary content gracefully."""
        test_file = tmp_path / "binary.md"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00")

        converter = DocumentConverter()

        with pytest.raises((UnicodeDecodeError, ValueError)):
            converter.convert(str(test_file))

    def test_converter_with_nested_directories(self, tmp_path: Path) -> None:
        """Test converter handles nested directory paths."""
        nested_dir = tmp_path / "a" / "b" / "c"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test.md"
        test_file.write_text("# Nested Document")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_converter_permission_error(self, tmp_path: Path) -> None:
        """Test converter handles permission errors."""
        test_file = tmp_path / "noperm.md"
        test_file.write_text("# No Permission")

        # Make file read-only (if supported)
        if hasattr(test_file, "chmod"):
            test_file.chmod(0o000)

        converter = DocumentConverter()

        try:
            # On systems that enforce permissions
            with pytest.raises((PermissionError, OSError)):
                converter.convert(str(test_file))
        finally:
            # Restore permissions for cleanup
            if hasattr(test_file, "chmod"):
                test_file.chmod(0o644)


class TestParserErrorHandling:
    """Test cases for parser error handling."""

    def test_parser_with_invalid_content(self) -> None:
        """Test parser handles invalid content gracefully."""
        parser = MarkdownParser()

        with pytest.raises((ValueError, TypeError)):
            parser.parse("")

    def test_parser_with_none_content(self) -> None:
        """Test parser handles None content."""
        parser = MarkdownParser()

        with pytest.raises(TypeError):
            parser.parse(None)  # type: ignore

    def test_parser_with_malformed_markdown(self) -> None:
        """Test parser handles malformed markdown."""
        parser = MarkdownParser()

        malformed_content = """
# Header with unclosed **bold
## Incomplete [link](
### ```unclosed code block
- List without proper indentation
        - Nested item
- Normal item
"""
        # Should not crash, should parse what's possible
        result = parser.parse(malformed_content)
        assert result is not None


class TestTransformerErrorHandling:
    """Test cases for transformer error handling."""

    def test_json_transformer_with_none_input(self) -> None:
        """Test JSON transformer handles None input."""
        transformer = JsonTransformer()

        with pytest.raises((ValueError, TypeError)):
            transformer.transform(None)  # type: ignore

    def test_json_transformer_with_invalid_document(self) -> None:
        """Test JSON transformer handles invalid document object."""
        transformer = JsonTransformer()

        with pytest.raises((ValueError, AttributeError)):
            transformer.transform("not a document")

    def test_mcp_transformer_with_none_input(self) -> None:
        """Test MCP transformer handles None input."""
        transformer = MCPTransformer()

        with pytest.raises((ValueError, TypeError)):
            transformer.transform(None)  # type: ignore

    def test_transformer_with_unsupported_output_format(self) -> None:
        """Test transformer handles unsupported output format."""
        transformer = JsonTransformer()

        with pytest.raises(ValueError) as exc_info:
            transformer.transform({}, output_format="unsupported_format")
        assert "Unsupported" in str(exc_info.value) or "format" in str(exc_info.value).lower()


# =============================================================================
# Processor Pipeline Integration Tests
# =============================================================================


class TestProcessorPipeline:
    """Test cases for the complete processor pipeline."""

    def test_full_pipeline_markdown_to_json(self, tmp_path: Path) -> None:
        """Test complete pipeline from markdown to JSON."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""# Test Document

## Section 1

This is section 1 content.

## Section 2

This is section 2 content.
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None
        # Result should be valid JSON string
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_full_pipeline_markdown_to_mcp(self, tmp_path: Path) -> None:
        """Test complete pipeline from markdown to MCP format."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""# Test Document

## Introduction

This is the introduction.

## Features

- Feature 1
- Feature 2
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="mcp")

        assert result is not None
        # MCP format should be parseable
        parsed = json.loads(result)
        assert isinstance(parsed, (dict, list))

    def test_pipeline_with_semantic_tags(self, tmp_path: Path) -> None:
        """Test pipeline includes semantic tagging."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""# API Documentation

## Endpoints

### GET /users

Returns list of users.

### POST /users

Creates a new user.
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json", include_semantic_tags=True)

        assert result is not None
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_pipeline_with_custom_schema(self, tmp_path: Path) -> None:
        """Test pipeline respects custom schema configuration."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Custom Schema Test\n\nContent here.")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json", schema="custom")

        assert result is not None

    def test_pipeline_preserves_metadata(self, tmp_path: Path) -> None:
        """Test pipeline preserves document metadata."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: Test Document
author: Test Author
date: 2024-01-01
---

# Main Content
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None
        parsed = json.loads(result)
        # Metadata should be preserved
        assert "metadata" in parsed or "frontmatter" in parsed or "title" in str(parsed)


class TestProcessorEdgeCases:
    """Test edge cases in processor pipeline."""

    def test_processor_with_special_characters(self, tmp_path: Path) -> None:
        """Test processor handles special characters in markdown."""
        test_file = tmp_path / "special.md"
        test_file.write_text("""# Special Characters Test

## Code Block
```python
def hello():
    print("Hello, 世界! 🌍")
```

## Special Symbols
- & (ampersand)
- < (less than)
- > (greater than)
- " (quotes)
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_processor_with_unicode_content(self, tmp_path: Path) -> None:
        """Test processor handles Unicode content."""
        test_file = tmp_path / "unicode.md"
        test_file.write_text("""# 日本語テスト
# 简体中文测试
# 한국어 테스트

This document contains multiple Unicode scripts.
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None

    def test_processor_with_deeply_nested_structure(self, tmp_path: Path) -> None:
        """Test processor handles deeply nested markdown structures."""
        test_file = tmp_path / "nested.md"
        test_file.write_text("""# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None

    def test_processor_with_multiple_code_blocks(self, tmp_path: Path) -> None:
        """Test processor handles multiple code blocks."""
        test_file = tmp_path / "code_blocks.md"
        test_file.write_text("""# Code Blocks Test

## Python Example
```python
def foo():
    pass
```

## JavaScript Example
```javascript
function foo() {}
```

## Inline Code: `print("hello")`
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None

    def test_processor_with_tables(self, tmp_path: Path) -> None:
        """Test processor handles markdown tables."""
        test_file = tmp_path / "tables.md"
        test_file.write_text("""# Table Test

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None

    def test_processor_with_blockquotes(self, tmp_path: Path) -> None:
        """Test processor handles blockquotes."""
        test_file = tmp_path / "quotes.md"
        test_file.write_text("""# Quote Test

> This is a blockquote
> spanning multiple lines.

> Another quote:
> - With a list inside
""")

        converter = DocumentConverter()
        result = converter.convert(str(test_file), output_format="json")

        assert result is not None


# =============================================================================
# Base Processor Tests
# =============================================================================


class TestBaseProcessor:
    """Test cases for BaseProcessor class."""

    def test_base_processor_initialization(self) -> None:
        """Test base processor can be initialized."""
        processor = BaseProcessor()

        assert processor is not None

    def test_base_processor_with_config(self) -> None:
        """Test base processor accepts configuration."""
        config = {"option1": "value1", "option2": 42}
        processor = BaseProcessor(config=config)

        assert processor is not None

    def test_base_processor_process_method_exists(self) -> None:
        """Test base processor has process method."""
        processor = BaseProcessor()

        assert hasattr(processor, "process")
        assert callable(getattr(processor, "process"))


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_markdown_content() -> str:
    """Provide sample markdown content for testing."""
    return """# Sample Document

## Introduction

This is an introduction to the document.

## Main Content

Here is the main content with:
- List item 1
- List item 2
- List item 3

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This is the conclusion.
"""


@pytest.fixture
def sample_document_file(tmp_path: Path, sample_markdown_content: str) -> Path:
    """Create a temporary markdown file with sample content."""
    file_path = tmp_path / "sample.md"
    file_path.write_text(sample_markdown_content)
    return file_path


@pytest.fixture
def invalid_format_file(tmp_path: Path) -> Path:
    """Create a file with unsupported format."""
    file_path = tmp_path / "test.invalid"
    file_path.write_text("invalid content")
    return file_path


@pytest.fixture
def empty_markdown_file(tmp_path: Path) -> Path:
    """Create an empty markdown file."""
    file_path = tmp_path / "empty.md"
    file_path.write_text("")
    return file_path
