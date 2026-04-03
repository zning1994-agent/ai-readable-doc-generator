"""Tests for Document model."""

import pytest

from ai_readable_doc_generator.document import Document


class TestDocument:
    """Tests for Document dataclass."""

    @pytest.fixture
    def sample_content(self) -> str:
        """Sample Markdown content."""
        return "# Hello World\n\nThis is a test document."

    def test_create_document(self, sample_content: str) -> None:
        """Test creating a document."""
        doc = Document(content=sample_content)
        assert doc.content == sample_content
        assert doc.source_path is None
        assert doc.raw_tokens == []
        assert doc.ast is None

    def test_create_document_with_path(self, sample_content: str) -> None:
        """Test creating a document with source path."""
        doc = Document(content=sample_content, source_path="/path/to/doc.md")
        assert doc.source_path == "/path/to/doc.md"

    def test_document_metadata(self, sample_content: str) -> None:
        """Test document metadata."""
        doc = Document(content=sample_content)
        assert doc.metadata["source_format"] == "markdown"
        assert doc.metadata["title"] is None
        assert doc.metadata["description"] is None

    def test_title_property(self, sample_content: str) -> None:
        """Test title property getter and setter."""
        doc = Document(content=sample_content)
        assert doc.title is None

        doc.title = "Test Title"
        assert doc.title == "Test Title"
        assert doc.metadata["title"] == "Test Title"

    def test_word_count_property(self, sample_content: str) -> None:
        """Test word count property."""
        doc = Document(content=sample_content)
        expected_count = len(sample_content.split())
        assert doc.word_count == expected_count

    def test_empty_content_word_count(self) -> None:
        """Test word count with empty content."""
        doc = Document(content="")
        assert doc.word_count == 0

    def test_add_token(self, sample_content: str) -> None:
        """Test adding tokens to document."""
        doc = Document(content=sample_content)
        doc.add_token({"type": "heading", "content": "test"})
        assert len(doc.raw_tokens) == 1
        assert doc.raw_tokens[0]["type"] == "heading"

    def test_set_ast(self, sample_content: str) -> None:
        """Test setting AST."""
        doc = Document(content=sample_content)
        mock_ast = {"type": "root", "children": []}
        doc.set_ast(mock_ast)
        assert doc.ast == mock_ast

    def test_metadata_custom_fields(self, sample_content: str) -> None:
        """Test custom metadata fields."""
        doc = Document(content=sample_content)
        doc.metadata["custom_key"] = "custom_value"
        assert doc.metadata["custom_key"] == "custom_value"
