"""Tests for base converter functionality."""

import pytest

from ai_readable_doc_generator.base import BaseConverter
from ai_readable_doc_generator.models.schema import SemanticDocument


class ConcreteConverter(BaseConverter):
    """Concrete implementation of BaseConverter for testing."""

    def convert(self, source: str) -> SemanticDocument:
        """Convert source to semantic document."""
        return self.parse(source)

    def parse(self, content: str) -> SemanticDocument:
        """Parse content to semantic document."""
        doc = SemanticDocument()
        doc.metadata.word_count = len(content.split())
        return doc


class TestBaseConverter:
    """Tests for BaseConverter functionality."""

    @pytest.fixture
    def converter(self) -> ConcreteConverter:
        """Create a converter instance for testing."""
        return ConcreteConverter(
            add_table_of_contents=True,
            add_statistics=True,
            extract_semantic_tags=True,
            importance_detection=True,
        )

    def test_initialization(self, converter: ConcreteConverter) -> None:
        """Test converter initializes with correct defaults."""
        assert converter.add_table_of_contents is True
        assert converter.add_statistics is True
        assert converter.extract_semantic_tags is True
        assert converter.importance_detection is True

    def test_validate_source_string(self, converter: ConcreteConverter) -> None:
        """Test validating string source (content)."""
        is_file, value = converter._validate_source("some content")
        assert is_file is False
        assert value == "some content"

    def test_validate_source_path_string(self, converter: ConcreteConverter) -> None:
        """Test validating string that looks like a path."""
        is_file, value = converter._validate_source("/path/to/file.txt")
        # Since file doesn't exist, it will be treated as content
        assert value == "/path/to/file.txt"

    def test_validate_source_pathlib_path(self, converter: ConcreteConverter) -> None:
        """Test validating pathlib.Path source."""
        from pathlib import Path
        path = Path("/path/to/file.txt")
        is_file, value = converter._validate_source(path)
        assert is_file is True
        assert value == "/path/to/file.txt"

    def test_calculate_reading_time(self, converter: ConcreteConverter) -> None:
        """Test reading time calculation."""
        # 200 words at 200 wpm = 1 minute
        text = "word " * 200
        reading_time = converter._calculate_reading_time(text)
        assert reading_time == 1.0

    def test_calculate_reading_time_custom_wpm(self, converter: ConcreteConverter) -> None:
        """Test reading time with custom words per minute."""
        # 100 words at 100 wpm = 1 minute
        text = "word " * 100
        reading_time = converter._calculate_reading_time(text, words_per_minute=100)
        assert reading_time == 1.0

    def test_generate_statistics(self, converter: ConcreteConverter) -> None:
        """Test statistics generation."""
        doc = SemanticDocument()
        doc.metadata.word_count = 100
        doc.metadata.reading_time_minutes = 0.5
        doc.all_blocks = []
        doc.sections = []

        stats = converter._generate_statistics(doc)
        assert "total_sections" in stats
        assert "total_blocks" in stats
        assert stats["word_count"] == 100
        assert stats["reading_time_minutes"] == 0.5

    def test_generate_statistics_with_content(self, converter: ConcreteConverter) -> None:
        """Test statistics generation with actual content."""
        from ai_readable_doc_generator.models.schema import SemanticBlock, ContentType

        doc = SemanticDocument()
        doc.metadata.word_count = 50
        doc.metadata.reading_time_minutes = 0.25
        doc.all_blocks = [
            SemanticBlock(id="b1", content_type=ContentType.TEXT, content="Text block"),
            SemanticBlock(id="b2", content_type=ContentType.CODE_BLOCK, content="Code block"),
            SemanticBlock(id="b3", content_type=ContentType.LINK, content="Link"),
        ]
        doc.sections = [
            SemanticBlock(id="s1", content_type=ContentType.HEADING, content="Section 1"),
        ]

        stats = converter._generate_statistics(doc)
        assert stats["total_sections"] == 1
        assert stats["total_blocks"] == 3
        assert "content_types" in stats

    def test_parse_method(self, converter: ConcreteConverter) -> None:
        """Test parse method returns SemanticDocument."""
        content = "Hello world this is a test"
        result = converter.parse(content)
        assert isinstance(result, SemanticDocument)
        assert result.metadata.word_count == 6

    def test_convert_method(self, converter: ConcreteConverter) -> None:
        """Test convert method returns SemanticDocument."""
        content = "Hello world this is a test"
        result = converter.convert(content)
        assert isinstance(result, SemanticDocument)
