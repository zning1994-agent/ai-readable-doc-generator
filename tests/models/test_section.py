"""Unit tests for section module."""

import pytest

from ai_readable_doc_generator.models.section import (
    ContentType,
    Section,
    SectionType,
    SemanticTag,
)


class TestSemanticTag:
    """Tests for SemanticTag class."""

    def test_create_semantic_tag(self):
        """Test creating a semantic tag."""
        tag = SemanticTag(name="important", confidence=0.9)
        assert tag.name == "important"
        assert tag.confidence == 0.9
        assert tag.metadata == {}

    def test_create_with_metadata(self):
        """Test creating a semantic tag with metadata."""
        metadata = {"category": "security", "severity": "high"}
        tag = SemanticTag(name="vulnerability", confidence=1.0, metadata=metadata)
        assert tag.metadata == metadata

    def test_to_dict(self):
        """Test converting to dictionary."""
        tag = SemanticTag(name="api", confidence=0.95, metadata={"type": "reference"})
        result = tag.to_dict()

        assert result["name"] == "api"
        assert result["confidence"] == 0.95
        assert result["metadata"] == {"type": "reference"}

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "name": "code_example",
            "confidence": 0.8,
            "metadata": {"language": "python"},
        }
        tag = SemanticTag.from_dict(data)

        assert tag.name == "code_example"
        assert tag.confidence == 0.8
        assert tag.metadata == {"language": "python"}

    def test_from_dict_with_defaults(self):
        """Test creating from dictionary with missing fields uses defaults."""
        data = {"name": "test"}
        tag = SemanticTag.from_dict(data)

        assert tag.name == "test"
        assert tag.confidence == 1.0
        assert tag.metadata == {}


class TestSectionType:
    """Tests for SectionType enum."""

    def test_all_section_types_exist(self):
        """Test all expected section types exist."""
        expected_types = [
            "heading",
            "paragraph",
            "code_block",
            "list",
            "table",
            "blockquote",
            "horizontal_rule",
            "image",
            "link",
            "custom",
        ]

        for type_name in expected_types:
            section_type = SectionType(type_name)
            assert section_type.value == type_name

    def test_section_type_values(self):
        """Test section type values."""
        assert SectionType.HEADING.value == "heading"
        assert SectionType.CODE_BLOCK.value == "code_block"
        assert SectionType.PARAGRAPH.value == "paragraph"


class TestContentType:
    """Tests for ContentType enum."""

    def test_all_content_types_exist(self):
        """Test all expected content types exist."""
        expected_types = [
            "title",
            "introduction",
            "body",
            "conclusion",
            "summary",
            "code_example",
            "api_reference",
            "troubleshooting",
            "faq",
            "changelog",
            "glossary",
            "appendix",
            "other",
        ]

        for type_name in expected_types:
            content_type = ContentType(type_name)
            assert content_type.value == type_name


class TestSection:
    """Tests for Section class."""

    def test_create_section(self):
        """Test creating a basic section."""
        section = Section(
            section_type=SectionType.PARAGRAPH,
            content="This is a paragraph.",
        )

        assert section.section_type == SectionType.PARAGRAPH
        assert section.content == "This is a paragraph."
        assert section.level == 1
        assert section.heading is None
        assert section.content_type == ContentType.OTHER
        assert section.semantic_tags == []
        assert section.children == []

    def test_create_heading_section(self):
        """Test creating a heading section."""
        section = Section(
            section_type=SectionType.HEADING,
            heading="Introduction",
            level=2,
            content_type=ContentType.INTRODUCTION,
        )

        assert section.section_type == SectionType.HEADING
        assert section.heading == "Introduction"
        assert section.level == 2
        assert section.content_type == ContentType.INTRODUCTION

    def test_add_semantic_tag(self):
        """Test adding semantic tags."""
        section = Section(section_type=SectionType.PARAGRAPH, content="Test")
        tag = SemanticTag(name="important")

        section.add_semantic_tag(tag)

        assert len(section.semantic_tags) == 1
        assert section.semantic_tags[0].name == "important"

    def test_add_child(self):
        """Test adding child sections."""
        parent = Section(section_type=SectionType.PARAGRAPH, content="Parent")
        child = Section(section_type=SectionType.PARAGRAPH, content="Child")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0].content == "Child"

    def test_get_all_tags(self):
        """Test getting all tags including from children."""
        parent = Section(section_type=SectionType.PARAGRAPH, content="Parent")
        child = Section(section_type=SectionType.PARAGRAPH, content="Child")

        parent.add_semantic_tag(SemanticTag(name="parent_tag"))
        child.add_semantic_tag(SemanticTag(name="child_tag"))
        parent.add_child(child)

        tags = parent.get_all_tags()
        tag_names = [t.name for t in tags]

        assert "parent_tag" in tag_names
        assert "child_tag" in tag_names

    def test_get_text_content(self):
        """Test getting text content."""
        section = Section(
            section_type=SectionType.PARAGRAPH,
            content="Main content",
        )

        assert section.get_text_content() == "Main content"

    def test_get_text_content_with_heading(self):
        """Test getting text content including heading."""
        section = Section(
            section_type=SectionType.HEADING,
            heading="Title",
            content="Some content",
        )

        text = section.get_text_content()
        assert "Title" in text
        assert "Some content" in text

    def test_get_text_content_nested(self):
        """Test getting text content from nested sections."""
        parent = Section(section_type=SectionType.PARAGRAPH, content="Parent")
        child = Section(section_type=SectionType.PARAGRAPH, content="Child")
        parent.add_child(child)

        text = parent.get_text_content()
        assert "Parent" in text
        assert "Child" in text

    def test_to_dict(self):
        """Test converting section to dictionary."""
        section = Section(
            section_type=SectionType.CODE_BLOCK,
            content="print('hello')",
            level=1,
            content_type=ContentType.CODE_EXAMPLE,
        )

        result = section.to_dict()

        assert result["type"] == "code_block"
        assert result["content"] == "print('hello')"
        assert result["level"] == 1
        assert result["content_type"] == "code_example"
        assert result["semantic_tags"] == []
        assert result["children"] == []

    def test_to_dict_with_tags(self):
        """Test converting section with tags to dictionary."""
        section = Section(
            section_type=SectionType.PARAGRAPH,
            content="Test",
        )
        section.add_semantic_tag(SemanticTag(name="api"))

        result = section.to_dict()

        assert len(result["semantic_tags"]) == 1
        assert result["semantic_tags"][0]["name"] == "api"

    def test_from_dict(self):
        """Test creating section from dictionary."""
        data = {
            "type": "heading",
            "content": "Heading content",
            "level": 2,
            "heading": "My Heading",
            "content_type": "introduction",
            "semantic_tags": [],
            "children": [],
        }

        section = Section.from_dict(data)

        assert section.section_type == SectionType.HEADING
        assert section.content == "Heading content"
        assert section.level == 2
        assert section.heading == "My Heading"
        assert section.content_type == ContentType.INTRODUCTION

    def test_from_dict_with_children(self):
        """Test creating section with children from dictionary."""
        data = {
            "type": "paragraph",
            "content": "Parent",
            "children": [
                {
                    "type": "paragraph",
                    "content": "Child",
                    "level": 1,
                    "heading": None,
                    "content_type": "other",
                    "semantic_tags": [],
                    "children": [],
                }
            ],
        }

        section = Section.from_dict(data)

        assert len(section.children) == 1
        assert section.children[0].content == "Child"

    def test_from_dict_defaults(self):
        """Test creating section from dict with missing fields uses defaults."""
        data = {"content": "Test"}

        section = Section.from_dict(data)

        assert section.section_type == SectionType.PARAGRAPH
        assert section.level == 1
        assert section.content_type == ContentType.OTHER

    def test_is_heading_section(self):
        """Test heading section detection."""
        heading = Section(section_type=SectionType.HEADING, content="Title")
        paragraph = Section(section_type=SectionType.PARAGRAPH, content="Text")

        assert heading.is_heading_section() is True
        assert paragraph.is_heading_section() is False

    def test_is_code_section(self):
        """Test code section detection."""
        code = Section(section_type=SectionType.CODE_BLOCK, content="code")
        paragraph = Section(section_type=SectionType.PARAGRAPH, content="text")

        assert code.is_code_section() is True
        assert paragraph.is_code_section() is False

    def test_get_depth_single_level(self):
        """Test getting depth of single level section."""
        section = Section(section_type=SectionType.PARAGRAPH, content="Test")
        assert section.get_depth() == 1

    def test_get_depth_nested(self):
        """Test getting depth of nested sections."""
        parent = Section(section_type=SectionType.PARAGRAPH, content="Parent")
        child = Section(section_type=SectionType.PARAGRAPH, content="Child")
        grandchild = Section(section_type=SectionType.PARAGRAPH, content="Grandchild")

        parent.add_child(child)
        child.add_child(grandchild)

        assert parent.get_depth() == 3
        assert child.get_depth() == 2
        assert grandchild.get_depth() == 1
