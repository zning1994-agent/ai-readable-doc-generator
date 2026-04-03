"""Tests for document module."""

import pytest

from ai_readable_doc_generator import Document, DocumentMetadata, Section, SectionType


class TestDocument:
    """Tests for Document class."""

    def test_create_document(self) -> None:
        """Test document creation."""
        doc = Document(content="Test content")
        assert doc.content == "Test content"

    def test_add_section(self) -> None:
        """Test adding section to document."""
        doc = Document(content="Test")
        section = Section(section_type=SectionType.PARAGRAPH, content="Section content")
        doc.add_section(section)
        assert len(doc.sections) == 1

    def test_to_dict(self) -> None:
        """Test document serialization."""
        doc = Document(content="Test", metadata=DocumentMetadata(title="Test Title"))
        result = doc.to_dict()
        assert result["content"] == "Test"
        assert result["metadata"]["title"] == "Test Title"
