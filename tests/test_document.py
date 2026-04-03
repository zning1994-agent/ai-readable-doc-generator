"""Tests for the Document model classes."""

import pytest

from ai_readable_doc_generator.document import (
    ContentClassification,
    Document,
    DocumentSection,
    ImportanceLevel,
    SectionType,
    SemanticTag,
)


class TestSemanticTag:
    """Test cases for SemanticTag dataclass."""

    def test_create_tag(self):
        """SemanticTag should be created with name."""
        tag = SemanticTag(name="category")
        assert tag.name == "category"
        assert tag.value is None
        assert tag.confidence == 1.0

    def test_create_tag_with_value(self):
        """SemanticTag should accept value and confidence."""
        tag = SemanticTag(name="status", value="deprecated", confidence=0.8)
        assert tag.name == "status"
        assert tag.value == "deprecated"
        assert tag.confidence == 0.8


class TestDocumentSection:
    """Test cases for DocumentSection class."""

    def test_create_section(self):
        """DocumentSection should be created with required fields."""
        section = DocumentSection(id="sec1", content="Hello world")
        assert section.id == "sec1"
        assert section.content == "Hello world"
        assert section.section_type == SectionType.PARAGRAPH
        assert section.level == 0

    def test_create_section_with_options(self):
        """DocumentSection should accept optional parameters."""
        section = DocumentSection(
            id="sec2",
            content="Code snippet",
            section_type=SectionType.CODE_BLOCK,
            level=1,
            parent_id="sec1",
            classification=ContentClassification.TECHNICAL,
            importance=ImportanceLevel.HIGH,
        )
        assert section.id == "sec2"
        assert section.section_type == SectionType.CODE_BLOCK
        assert section.parent_id == "sec1"
        assert section.classification == ContentClassification.TECHNICAL
        assert section.importance == ImportanceLevel.HIGH

    def test_add_semantic_tag(self):
        """Section should allow adding semantic tags."""
        section = DocumentSection(id="sec1", content="Test")
        section.add_semantic_tag("type", "example", 0.9)

        assert len(section.semantic_tags) == 1
        assert section.semantic_tags[0].name == "type"
        assert section.semantic_tags[0].value == "example"
        assert section.semantic_tags[0].confidence == 0.9

    def test_to_dict(self):
        """Section should convert to dictionary."""
        section = DocumentSection(id="sec1", content="Test")
        section.add_semantic_tag("tag1", "value1")

        result = section.to_dict()

        assert result["id"] == "sec1"
        assert result["content"] == "Test"
        assert result["section_type"] == "paragraph"
        assert len(result["semantic_tags"]) == 1
        assert result["semantic_tags"][0]["name"] == "tag1"


class TestDocument:
    """Test cases for Document class."""

    def test_create_document(self):
        """Document should be created with defaults."""
        doc = Document()
        assert doc.title == ""
        assert doc.description == ""
        assert doc.sections == []
        assert doc.source_format == "markdown"

    def test_create_document_with_fields(self):
        """Document should accept field values."""
        doc = Document(
            title="Test Doc",
            description="A test document",
            source_format="markdown",
            source_path="/path/to/doc.md",
        )
        assert doc.title == "Test Doc"
        assert doc.description == "A test document"
        assert doc.source_format == "markdown"
        assert doc.source_path == "/path/to/doc.md"

    def test_add_section(self):
        """Document should allow adding sections."""
        doc = Document()
        section = DocumentSection(id="sec1", content="Test")
        doc.add_section(section)

        assert len(doc.sections) == 1
        assert doc.sections[0].id == "sec1"

    def test_add_semantic_tag(self):
        """Document should allow adding semantic tags."""
        doc = Document()
        doc.add_semantic_tag("author", "John Doe")

        assert len(doc.semantic_tags) == 1
        assert doc.semantic_tags[0].name == "author"
        assert doc.semantic_tags[0].value == "John Doe"

    def test_get_all_sections_flat(self):
        """get_all_sections should return all top-level sections."""
        doc = Document()
        doc.add_section(DocumentSection(id="sec1", content="Test 1"))
        doc.add_section(DocumentSection(id="sec2", content="Test 2"))

        sections = doc.get_all_sections()
        assert len(sections) == 2

    def test_get_all_sections_with_children(self):
        """get_all_sections should include nested children."""
        doc = Document()
        parent = DocumentSection(id="parent", content="Parent")
        child = DocumentSection(id="child", content="Child", parent_id="parent")
        parent.children.append(child)
        doc.add_section(parent)

        sections = doc.get_all_sections()
        assert len(sections) == 2
        assert sections[0].id == "parent"
        assert sections[1].id == "child"

    def test_to_dict(self):
        """Document should convert to dictionary."""
        doc = Document(title="Test")
        doc.add_section(DocumentSection(id="sec1", content="Content"))

        result = doc.to_dict()

        assert result["title"] == "Test"
        assert len(result["sections"]) == 1
        assert result["sections"][0]["id"] == "sec1"
        assert result["source_format"] == "markdown"


class TestEnums:
    """Test cases for enum classes."""

    def test_section_type_values(self):
        """SectionType should have expected values."""
        assert SectionType.TITLE.value == "title"
        assert SectionType.PARAGRAPH.value == "paragraph"
        assert SectionType.CODE_BLOCK.value == "code_block"
        assert SectionType.LIST.value == "list"

    def test_content_classification_values(self):
        """ContentClassification should have expected values."""
        assert ContentClassification.NARRATIVE.value == "narrative"
        assert ContentClassification.TECHNICAL.value == "technical"
        assert ContentClassification.REFERENCE.value == "reference"
        assert ContentClassification.API_DOCUMENTATION.value == "api_documentation"

    def test_importance_level_order(self):
        """ImportanceLevel should have correct numeric ordering."""
        assert ImportanceLevel.CRITICAL.value == 1
        assert ImportanceLevel.HIGH.value == 2
        assert ImportanceLevel.MEDIUM.value == 3
        assert ImportanceLevel.LOW.value == 4
