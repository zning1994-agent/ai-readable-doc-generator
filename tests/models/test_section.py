"""Tests for Section model."""

import pytest

from ai_readable_doc_generator.models import (
    ContentClassification,
    ImportanceLevel,
    Section,
    SectionType,
)


class TestSection:
    """Tests for Section class."""

    def test_create_section(self) -> None:
        """Test section creation."""
        section = Section(section_type=SectionType.PARAGRAPH, content="Test content")
        assert section.section_type == SectionType.PARAGRAPH
        assert section.content == "Test content"

    def test_add_child(self) -> None:
        """Test adding child section."""
        parent = Section(section_type=SectionType.DOCUMENT, content="Parent")
        child = Section(section_type=SectionType.PARAGRAPH, content="Child")
        parent.add_child(child)
        assert len(parent.children) == 1

    def test_to_dict(self) -> None:
        """Test section serialization."""
        section = Section(
            section_type=SectionType.HEADING,
            content="Title",
            level=1,
            classification=ContentClassification.NARRATIVE,
            importance=ImportanceLevel.HIGH,
        )
        result = section.to_dict()
        assert result["section_type"] == "heading"
        assert result["content"] == "Title"
        assert result["level"] == 1
