"""Tests for Document model."""

import pytest

from ai_readable_doc_generator.models import Document, DocumentMetadata


class TestDocumentMetadata:
    """Tests for DocumentMetadata class."""

    def test_create_metadata(self) -> None:
        """Test metadata creation."""
        metadata = DocumentMetadata(title="Test", author="Author")
        assert metadata.title == "Test"
        assert metadata.author == "Author"

    def test_to_dict(self) -> None:
        """Test metadata serialization."""
        metadata = DocumentMetadata(title="Test", tags=["tag1", "tag2"])
        result = metadata.to_dict()
        assert result["title"] == "Test"
        assert result["tags"] == ["tag1", "tag2"]

    def test_from_dict(self) -> None:
        """Test metadata deserialization."""
        data = {"title": "Test", "author": "Author"}
        metadata = DocumentMetadata.from_dict(data)
        assert metadata.title == "Test"
        assert metadata.author == "Author"
