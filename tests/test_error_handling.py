"""
Tests for error handling in ai-readable-doc-generator.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


# =============================================================================
# Converter Error Handling Tests
# =============================================================================


class TestConverterErrors:
    """Test converter error handling."""

    def test_nonexistent_input_file(self) -> None:
        """Test converter raises error for non-existent input file."""
        from ai_readable_doc_generator.converter import DocumentConverter

        converter = DocumentConverter()

        with pytest.raises(FileNotFoundError):
            converter.convert("/nonexistent/path/to/file.md")

    def test_unsupported_format_raises_error(self, tmp_path: Path) -> None:
        """Test converter raises error for unsupported format."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "test.xyz"
        test_file.write_text("unsupported content")

        converter = DocumentConverter()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            converter.convert(str(test_file))
        assert "unsupported" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()

    def test_invalid_output_format_raises_error(self, tmp_path: Path) -> None:
        """Test converter raises error for invalid output format."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content")

        converter = DocumentConverter()

        with pytest.raises(ValueError) as exc_info:
            converter.convert(str(test_file), output_format="invalid_format")
        assert "format" in str(exc_info.value).lower() or "unsupported" in str(exc_info.value).lower()


class TestFileAccessErrors:
    """Test file access error handling."""

    def test_permission_denied(self, tmp_path: Path) -> None:
        """Test handling of permission denied errors."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "noperm.md"
        test_file.write_text("# No Permission")

        # Try to make file unreadable (may not work on all systems)
        try:
            test_file.chmod(0o000)
        except OSError:
            pytest.skip("Cannot modify file permissions on this system")

        converter = DocumentConverter()

        try:
            with pytest.raises((PermissionError, OSError)):
                converter.convert(str(test_file))
        finally:
            # Restore permissions for cleanup
            test_file.chmod(0o644)

    def test_file_is_directory(self, tmp_path: Path) -> None:
        """Test handling when input is a directory."""
        from ai_readable_doc_generator.converter import DocumentConverter

        converter = DocumentConverter()

        with pytest.raises((IsADirectoryError, ValueError, TypeError)):
            converter.convert(str(tmp_path))

    def test_broken_symlink(self, tmp_path: Path) -> None:
        """Test handling of broken symbolic links."""
        from ai_readable_doc_generator.converter import DocumentConverter

        # Create a broken symlink
        link_path = tmp_path / "broken_link.md"
        try:
            link_path.symlink_to("/nonexistent/target.md")
        except OSError:
            pytest.skip("Cannot create symlinks on this system")

        converter = DocumentConverter()

        with pytest.raises((FileNotFoundError, OSError)):
            converter.convert(str(link_path))


class TestContentErrors:
    """Test content-related error handling."""

    def test_empty_file_handling(self, tmp_path: Path) -> None:
        """Test converter handles empty files."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        converter = DocumentConverter()

        # Should either succeed with empty result or raise specific error
        try:
            result = converter.convert(str(test_file))
            assert result is not None
        except ValueError as e:
            # Empty file might raise ValueError
            assert "empty" in str(e).lower()

    def test_whitespace_only_file(self, tmp_path: Path) -> None:
        """Test converter handles files with only whitespace."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "whitespace.md"
        test_file.write_text("   \n\n   \n   ")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_binary_content_raises_error(self, tmp_path: Path) -> None:
        """Test converter raises error for binary content."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "binary.md"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        converter = DocumentConverter()

        with pytest.raises((UnicodeDecodeError, ValueError)):
            converter.convert(str(test_file))

    def test_invalid_utf8_content(self, tmp_path: Path) -> None:
        """Test converter handles invalid UTF-8 content."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "invalid_utf8.md"
        # Invalid UTF-8 sequence
        test_file.write_bytes(b"\xff\xfe\x00\x01")

        converter = DocumentConverter()

        with pytest.raises(UnicodeDecodeError):
            converter.convert(str(test_file))


class TestParserErrors:
    """Test parser error handling."""

    def test_none_input_raises_error(self) -> None:
        """Test parser raises error for None input."""
        from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser

        parser = MarkdownParser()

        with pytest.raises(TypeError):
            parser.parse(None)  # type: ignore

    def test_empty_string_input(self) -> None:
        """Test parser handles empty string input."""
        from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        result = parser.parse("")

        assert result is not None

    def test_invalid_markdown_structure(self) -> None:
        """Test parser handles malformed markdown."""
        from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser

        parser = MarkdownParser()

        malformed = """# Unclosed header with **bold text
## Another unclosed header
### ```unclosed code fence
Content without proper structure
- List without proper
    - Nested without parent
        - Deeply nested
- Normal item
"""
        # Should not crash, should parse what's possible
        result = parser.parse(malformed)
        assert result is not None


class TestTransformerErrors:
    """Test transformer error handling."""

    def test_json_transformer_none_input(self) -> None:
        """Test JSON transformer raises error for None input."""
        from ai_readable_doc_generator.transformer.json_transformer import JsonTransformer

        transformer = JsonTransformer()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            transformer.transform(None)  # type: ignore
        assert "none" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_json_transformer_invalid_document_type(self) -> None:
        """Test JSON transformer raises error for invalid document type."""
        from ai_readable_doc_generator.transformer.json_transformer import JsonTransformer

        transformer = JsonTransformer()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            transformer.transform("not a document")
        assert "invalid" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()

    def test_mcp_transformer_none_input(self) -> None:
        """Test MCP transformer raises error for None input."""
        from ai_readable_doc_generator.transformer.mcp_transformer import MCPTransformer

        transformer = MCPTransformer()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            transformer.transform(None)  # type: ignore
        assert "none" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_unsupported_output_format(self) -> None:
        """Test transformer raises error for unsupported output format."""
        from ai_readable_doc_generator.transformer.json_transformer import JsonTransformer

        transformer = JsonTransformer()

        with pytest.raises(ValueError) as exc_info:
            transformer.transform({}, output_format="xml")
        assert "unsupported" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()


class TestValidationErrors:
    """Test input validation error handling."""

    def test_invalid_config_type(self) -> None:
        """Test converter handles invalid config type."""
        from ai_readable_doc_generator.converter import DocumentConverter

        converter = DocumentConverter()

        with pytest.raises((ValueError, TypeError)):
            converter.convert("test.md", config="invalid_config")  # type: ignore

    def test_invalid_schema_type(self) -> None:
        """Test converter handles invalid schema type."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = Path("test.md")
        if test_file.exists():
            converter = DocumentConverter()
            with pytest.raises((ValueError, TypeError)):
                converter.convert(str(test_file), schema=123)  # type: ignore

    def test_missing_required_option(self) -> None:
        """Test converter handles missing required options gracefully."""
        from ai_readable_doc_generator.converter import DocumentConverter

        # Create converter without required initialization
        converter = DocumentConverter()

        # Should have default values or raise clear error
        assert converter is not None


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_very_long_filename(self, tmp_path: Path) -> None:
        """Test handling of files with very long names."""
        from ai_readable_doc_generator.converter import DocumentConverter

        # Create file with long name (but within filesystem limits)
        long_name = "a" * 200 + ".md"
        test_file = tmp_path / long_name
        test_file.write_text("# Test")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_filename_with_special_characters(self, tmp_path: Path) -> None:
        """Test handling of filenames with special characters."""
        from ai_readable_doc_generator.converter import DocumentConverter

        # Filenames with special chars might not work on all filesystems
        try:
            test_file = tmp_path / "test file [1].md"
            test_file.write_text("# Test")
        except OSError:
            pytest.skip("Filesystem does not support special characters in filenames")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_path_with_spaces(self, tmp_path: Path) -> None:
        """Test handling of paths with spaces."""
        from ai_readable_doc_generator.converter import DocumentConverter

        spaced_dir = tmp_path / "path with spaces"
        spaced_dir.mkdir()
        test_file = spaced_dir / "test.md"
        test_file.write_text("# Test")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None

    def test_path_with_unicode_characters(self, tmp_path: Path) -> None:
        """Test handling of paths with unicode characters."""
        from ai_readable_doc_generator.converter import DocumentConverter

        # Unicode paths might not work on all filesystems
        try:
            unicode_dir = tmp_path / "文档"
            unicode_dir.mkdir()
            test_file = unicode_dir / "测试.md"
            test_file.write_text("# Test")
        except OSError:
            pytest.skip("Filesystem does not support unicode in filenames")

        converter = DocumentConverter()
        result = converter.convert(str(test_file))

        assert result is not None


class TestRecoveryAndResilience:
    """Test error recovery and resilience features."""

    def test_partial_parse_on_incomplete_content(self) -> None:
        """Test that parser can handle incomplete/malformed content."""
        from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser

        parser = MarkdownParser()

        incomplete = """# Header without proper ending
## Section

Incomplete list:
- Item 1
- Item 2
"""
        # Should parse what's possible without crashing
        result = parser.parse(incomplete)
        assert result is not None

    def test_graceful_degradation_on_errors(self, tmp_path: Path) -> None:
        """Test graceful degradation when encountering errors."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "partial.md"
        test_file.write_text("# Partial\n\n## Section 1\n\nValid content.\n\n## Section 2\n\n```unclosed")

        converter = DocumentConverter()

        # Should either succeed with partial result or raise controlled error
        try:
            result = converter.convert(str(test_file))
            assert result is not None
        except (ValueError, SyntaxError):
            # Controlled error is acceptable
            pass

    def test_error_message_clarity(self, tmp_path: Path) -> None:
        """Test that error messages are clear and helpful."""
        from ai_readable_doc_generator.converter import DocumentConverter

        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")

        converter = DocumentConverter()

        with pytest.raises((ValueError, TypeError)) as exc_info:
            converter.convert(str(test_file))

        error_message = str(exc_info.value).lower()
        # Error message should be informative
        assert any(
            keyword in error_message
            for keyword in ["format", "unsupported", "file", "extension"]
        )
