"""
Tests for format detection functionality in ai-readable-doc-generator.
"""

import json
from pathlib import Path
from typing import Optional

import pytest


# =============================================================================
# Format Detection Unit Tests
# =============================================================================


class TestFormatDetectionByExtension:
    """Test format detection based on file extensions."""

    def test_detect_markdown_md_extension(self, tmp_path: Path) -> None:
        """Test detection of .md files."""
        test_file = tmp_path / "document.md"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_markdown_mdown_extension(self, tmp_path: Path) -> None:
        """Test detection of .mdown files."""
        test_file = tmp_path / "document.mdown"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_markdown_markdown_extension(self, tmp_path: Path) -> None:
        """Test detection of .markdown files."""
        test_file = tmp_path / "document.markdown"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_json_extension(self, tmp_path: Path) -> None:
        """Test detection of .json files."""
        test_file = tmp_path / "data.json"
        test_file.write_text('{"key": "value"}')

        format_type = self._detect_format(str(test_file))
        assert format_type == "json"

    def test_detect_yaml_extension(self, tmp_path: Path) -> None:
        """Test detection of .yaml files."""
        test_file = tmp_path / "config.yaml"
        test_file.write_text("key: value")

        format_type = self._detect_format(str(test_file))
        assert format_type == "yaml"

    def test_detect_yml_extension(self, tmp_path: Path) -> None:
        """Test detection of .yml files."""
        test_file = tmp_path / "config.yml"
        test_file.write_text("key: value")

        format_type = self._detect_format(str(test_file))
        assert format_type == "yaml"

    def test_detect_txt_extension(self, tmp_path: Path) -> None:
        """Test detection of .txt files - should default to markdown-like."""
        test_file = tmp_path / "document.txt"
        test_file.write_text("# Plain text document")

        format_type = self._detect_format(str(test_file))
        # .txt files might be treated as markdown or have their own type
        assert format_type in ("markdown", "text", "plain")

    def _detect_format(self, file_path: str) -> str:
        """Helper to detect format from file path."""
        from ai_readable_doc_generator.converter import DocumentConverter

        return DocumentConverter.detect_format(file_path)


class TestFormatDetectionByContent:
    """Test format detection based on file content analysis."""

    def test_detect_markdown_by_content_headers(self, tmp_path: Path) -> None:
        """Test markdown detection by header patterns in content."""
        test_file = tmp_path / "noextension"
        test_file.write_text("# Header 1\n\n## Header 2\n\nContent")

        format_type = self._detect_format_by_content(str(test_file))
        assert format_type == "markdown"

    def test_detect_markdown_by_list_patterns(self, tmp_path: Path) -> None:
        """Test markdown detection by list patterns."""
        test_file = tmp_path / "noextension"
        test_file.write_text("- Item 1\n- Item 2\n- Item 3")

        format_type = self._detect_format_by_content(str(test_file))
        assert format_type == "markdown"

    def test_detect_markdown_by_code_blocks(self, tmp_path: Path) -> None:
        """Test markdown detection by code block patterns."""
        test_file = tmp_path / "noextension"
        test_file.write_text("```python\ndef foo():\n    pass\n```")

        format_type = self._detect_format_by_content(str(test_file))
        assert format_type == "markdown"

    def test_detect_json_by_braces(self, tmp_path: Path) -> None:
        """Test JSON detection by brace patterns."""
        test_file = tmp_path / "noextension"
        test_file.write_text('{"key": "value", "array": [1, 2, 3]}')

        format_type = self._detect_format_by_content(str(test_file))
        assert format_type == "json"

    def test_detect_yaml_by_colon_patterns(self, tmp_path: Path) -> None:
        """Test YAML detection by colon patterns."""
        test_file = tmp_path / "noextension"
        test_file.write_text("name: value\nlist:\n  - item1\n  - item2")

        format_type = self._detect_format_by_content(str(test_file))
        assert format_type == "yaml"

    def _detect_format_by_content(self, file_path: str) -> str:
        """Helper to detect format from file content."""
        from ai_readable_doc_generator.converter import DocumentConverter

        return DocumentConverter.detect_format(file_path)


class TestFormatDetectionEdgeCases:
    """Test edge cases in format detection."""

    def test_detect_file_with_no_extension(self, tmp_path: Path) -> None:
        """Test detection of files without extensions."""
        test_file = tmp_path / "README"
        test_file.write_text("# Readme Content")

        format_type = self._detect_format(str(test_file))
        # Should try content-based detection
        assert format_type is not None

    def test_detect_file_with_multiple_dots(self, tmp_path: Path) -> None:
        """Test detection of files with multiple dots in name."""
        test_file = tmp_path / "document.backup.md"
        test_file.write_text("# Backup Document")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_file_with_underscore(self, tmp_path: Path) -> None:
        """Test detection of files with underscores."""
        test_file = tmp_path / "test_file.md"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_file_with_hyphen(self, tmp_path: Path) -> None:
        """Test detection of files with hyphens."""
        test_file = tmp_path / "test-file.md"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_file_with_camel_case(self, tmp_path: Path) -> None:
        """Test detection of files with camelCase."""
        test_file = tmp_path / "testFile.MD"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def test_detect_file_with_snake_case(self, tmp_path: Path) -> None:
        """Test detection of files with snake_case."""
        test_file = tmp_path / "test_file.md"
        test_file.write_text("# Test")

        format_type = self._detect_format(str(test_file))
        assert format_type == "markdown"

    def _detect_format(self, file_path: str) -> str:
        """Helper to detect format from file path."""
        from ai_readable_doc_generator.converter import DocumentConverter

        return DocumentConverter.detect_format(file_path)


class TestFormatDetectionErrors:
    """Test error handling in format detection."""

    def test_error_on_nonexistent_file(self) -> None:
        """Test error when file does not exist."""
        with pytest.raises(FileNotFoundError):
            self._detect_format("/nonexistent/path/file.md")

    def test_error_on_unsupported_extension(self, tmp_path: Path) -> None:
        """Test error on unsupported file extension."""
        test_file = tmp_path / "file.xyz"
        test_file.write_text("content")

        with pytest.raises((ValueError, TypeError)) as exc_info:
            self._detect_format(str(test_file))
        assert "format" in str(exc_info.value).lower() or "unsupported" in str(exc_info.value).lower()

    def test_error_on_empty_extension(self, tmp_path: Path) -> None:
        """Test error when file has no extension and unreadable content."""
        test_file = tmp_path / "file"
        test_file.write_text("binary content \x00\x01\x02")

        with pytest.raises((ValueError, TypeError)):
            self._detect_format(str(test_file))

    def test_error_on_directory_path(self, tmp_path: Path) -> None:
        """Test error when path is a directory."""
        with pytest.raises((IsADirectoryError, ValueError, TypeError)):
            self._detect_format(str(tmp_path))

    def _detect_format(self, file_path: str) -> str:
        """Helper to detect format from file path."""
        from ai_readable_doc_generator.converter import DocumentConverter

        return DocumentConverter.detect_format(file_path)


# =============================================================================
# Supported Formats Tests
# =============================================================================


class TestSupportedFormats:
    """Test that all supported formats are correctly identified."""

    @pytest.mark.parametrize(
        "extension,expected_format",
        [
            (".md", "markdown"),
            (".markdown", "markdown"),
            (".mdown", "markdown"),
            (".json", "json"),
            (".yaml", "yaml"),
            (".yml", "yaml"),
        ],
    )
    def test_supported_extensions(
        self, tmp_path: Path, extension: str, expected_format: str
    ) -> None:
        """Test that supported extensions are correctly mapped."""
        test_file = tmp_path / f"file{extension}"
        test_file.write_text("# Test")

        from ai_readable_doc_generator.converter import DocumentConverter

        detected = DocumentConverter.detect_format(str(test_file))
        assert detected == expected_format

    def test_get_supported_formats(self) -> None:
        """Test that we can retrieve list of supported formats."""
        from ai_readable_doc_generator.converter import DocumentConverter

        formats = DocumentConverter.get_supported_formats()

        assert isinstance(formats, (list, set, tuple))
        assert "markdown" in formats
        assert "json" in formats
        assert "yaml" in formats

    def test_supported_format_check(self) -> None:
        """Test checking if a format is supported."""
        from ai_readable_doc_generator.converter import DocumentConverter

        assert DocumentConverter.is_format_supported("markdown") is True
        assert DocumentConverter.is_format_supported("json") is True
        assert DocumentConverter.is_format_supported("yaml") is True
        assert DocumentConverter.is_format_supported("pdf") is False
        assert DocumentConverter.is_format_supported("docx") is False
