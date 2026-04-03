"""
Tests for the Document domain model.

This module contains unit tests for the Document class as the root aggregate.
"""

import pytest

from ai_readable_doc_generator.models import (
    ContentType,
    Document,
    DocumentMetadata,
    OutputSchema,
    SchemaType,
    Section,
    SectionType,
)


class TestDocumentMetadata:
    """Tests for DocumentMetadata class."""

    def test_create_metadata_with_defaults(self):
        """Test creating metadata with default values."""
        metadata = DocumentMetadata()
        assert metadata.title == ""
        assert metadata.description == ""
        assert metadata.author == ""
        assert metadata.source_path == ""
        assert metadata.version == "1.0.0"
        assert metadata.tags == []
        assert metadata.language == "en"

    def test_create_metadata_with_values(self):
        """Test creating metadata with specific values."""
        metadata = DocumentMetadata(
            title="Test Document",
            description="A test document",
            author="Test Author",
            language="en",
        )
        assert metadata.title == "Test Document"
        assert metadata.description == "A test document"
        assert metadata.author == "Test Author"
        assert metadata.language == "en"

    def test_metadata_to_dict(self):
        """Test metadata serialization to dictionary."""
        metadata = DocumentMetadata(title="Test", author="Author")
        result = metadata.to_dict()
        assert result["title"] == "Test"
        assert result["author"] == "Author"
        assert "created_at" in result

    def test_metadata_from_dict(self):
        """Test metadata deserialization from dictionary."""
        data = {
            "title": "From Dict",
            "author": "Dict Author",
            "language": "zh",
        }
        metadata = DocumentMetadata.from_dict(data)
        assert metadata.title == "From Dict"
        assert metadata.author == "Dict Author"
        assert metadata.language == "zh"


class TestDocument:
    """Tests for Document class as root aggregate."""

    def test_create_document_with_defaults(self):
        """Test creating document with default values."""
        doc = Document()
        assert doc.id != ""
        assert doc.id.startswith("doc_")
        assert isinstance(doc.metadata, DocumentMetadata)
        assert isinstance(doc.schema, OutputSchema)
        assert doc.sections == []

    def test_create_document_with_metadata(self):
        """Test creating document with specific metadata."""
        metadata = DocumentMetadata(title="My Document")
        doc = Document(metadata=metadata)
        assert doc.metadata.title == "My Document"

    def test_create_document_with_sections(self):
        """Test creating document with initial sections."""
        section = Section(id="sec_1", content="Test content")
        doc = Document(sections=[section])
        assert len(doc.sections) == 1
        assert doc.sections[0].content == "Test content"

    def test_add_section(self):
        """Test adding a section to document."""
        doc = Document()
        section = Section(id="sec_1", content="First section")
        doc.add_section(section)
        assert len(doc.sections) == 1
        assert doc.sections[0].id == "sec_1"

    def test_add_nested_section(self):
        """Test adding a nested section with parent."""
        doc = Document()
        parent = Section(id="parent", content="Parent")
        child = Section(id="child", content="Child")
        doc.add_section(parent)
        doc.add_section(child, parent_id="parent")
        assert len(doc.sections) == 1
        assert len(doc.sections[0].children) == 1

    def test_remove_section(self):
        """Test removing a section by ID."""
        doc = Document()
        section = Section(id="sec_1", content="To remove")
        doc.add_section(section)
        result = doc.remove_section("sec_1")
        assert result is True
        assert len(doc.sections) == 0

    def test_remove_nonexistent_section(self):
        """Test removing a section that doesn't exist."""
        doc = Document()
        result = doc.remove_section("nonexistent")
        assert result is False

    def test_find_section_by_id(self):
        """Test finding a section by ID."""
        doc = Document()
        section = Section(id="find_me", content="Found")
        doc.add_section(section)
        found = doc.find_section_by_id("find_me")
        assert found is not None
        assert found.content == "Found"

    def test_find_nested_section(self):
        """Test finding a nested section."""
        doc = Document()
        parent = Section(id="parent")
        child = Section(id="nested_child")
        doc.add_section(parent)
        doc.add_section(child, parent_id="parent")
        found = doc.find_section_by_id("nested_child")
        assert found is not None
        assert found.id == "nested_child"

    def test_get_all_sections(self):
        """Test getting all sections including nested."""
        doc = Document()
        parent = Section(id="parent")
        child1 = Section(id="child1")
        child2 = Section(id="child2")
        doc.add_section(parent)
        doc.add_section(child1, parent_id="parent")
        doc.add_section(child2)
        all_sections = doc.get_all_sections()
        assert len(all_sections) == 3

    def test_get_sections_by_type(self):
        """Test filtering sections by type."""
        doc = Document()
        doc.add_section(Section(id="sec_1", section_type=SectionType.HEADING))
        doc.add_section(Section(id="sec_2", section_type=SectionType.PARAGRAPH))
        doc.add_section(Section(id="sec_3", section_type=SectionType.HEADING))
        headings = doc.get_sections_by_type(SectionType.HEADING)
        assert len(headings) == 2

    def test_get_headings(self):
        """Test getting all heading sections."""
        doc = Document()
        doc.add_section(Section(id="h1", section_type=SectionType.HEADING))
        doc.add_section(Section(id="p1", section_type=SectionType.PARAGRAPH))
        headings = doc.get_headings()
        assert len(headings) == 1

    def test_get_code_blocks(self):
        """Test getting all code block sections."""
        doc = Document()
        doc.add_section(Section(id="code1", section_type=SectionType.CODE_BLOCK))
        doc.add_section(Section(id="code2", section_type=SectionType.CODE_BLOCK))
        code_blocks = doc.get_code_blocks()
        assert len(code_blocks) == 2

    def test_generate_section_id(self):
        """Test section ID generation."""
        doc = Document()
        id1 = doc.generate_section_id("test")
        id2 = doc.generate_section_id("test")
        assert id1 == "test_1"
        assert id2 == "test_2"

    def test_update_metadata(self):
        """Test updating document metadata."""
        doc = Document()
        doc.update_metadata(title="Updated", author="New Author")
        assert doc.metadata.title == "Updated"
        assert doc.metadata.author == "New Author"

    def test_set_schema_type(self):
        """Test changing document schema type."""
        doc = Document()
        doc.set_schema_type(SchemaType.MCP)
        assert doc.schema.schema_type == SchemaType.MCP

    def test_to_dict(self):
        """Test document serialization to dictionary."""
        doc = Document()
        doc.metadata.title = "Test Doc"
        section = Section(id="sec_1", content="Content")
        doc.add_section(section)
        result = doc.to_dict()
        assert result["metadata"]["title"] == "Test Doc"
        assert len(result["sections"]) == 1

    def test_to_dict_without_schema(self):
        """Test document serialization without schema."""
        doc = Document()
        result = doc.to_dict(include_schema=False)
        assert "schema" not in result

    def test_from_dict(self):
        """Test document deserialization from dictionary."""
        data = {
            "id": "test_doc",
            "metadata": {"title": "From Dict"},
            "sections": [
                {"id": "sec_1", "content": "Content", "section_type": "paragraph"}
            ],
        }
        doc = Document.from_dict(data)
        assert doc.id == "test_doc"
        assert doc.metadata.title == "From Dict"
        assert len(doc.sections) == 1
        assert doc.sections[0].content == "Content"

    def test_from_dict_without_sections(self):
        """Test document deserialization with no sections."""
        data = {"id": "no_sections", "metadata": {}}
        doc = Document.from_dict(data)
        assert doc.sections == []

    def test_get_word_count(self):
        """Test word count calculation."""
        doc = Document()
        doc.add_section(Section(id="sec_1", content="Hello world"))
        doc.add_section(Section(id="sec_2", content="This is a test"))
        assert doc.get_word_count() == 5

    def test_get_section_count(self):
        """Test total section count."""
        doc = Document()
        parent = Section(id="parent")
        child = Section(id="child")
        doc.add_section(parent)
        doc.add_section(child, parent_id="parent")
        assert doc.get_section_count() == 2

    def test_len(self):
        """Test document length (top-level sections only)."""
        doc = Document()
        doc.add_section(Section(id="sec_1"))
        doc.add_section(Section(id="sec_2"))
        doc.add_section(Section(id="sec_3"))
        assert len(doc) == 3

    def test_iter(self):
        """Test document iteration."""
        doc = Document()
        doc.add_section(Section(id="sec_1"))
        doc.add_section(Section(id="sec_2"))
        ids = [s.id for s in doc]
        assert ids == ["sec_1", "sec_2"]

    def test_repr(self):
        """Test document string representation."""
        doc = Document()
        doc.metadata.title = "Test"
        r = repr(doc)
        assert "Test" in r
        assert "Document" in r

    def test_section_iter(self):
        """Test sections_iter method."""
        doc = Document()
        parent = Section(id="parent")
        child = Section(id="child")
        doc.add_section(parent)
        doc.add_section(child, parent_id="parent")
        ids = [s.id for s in doc.sections_iter()]
        assert "parent" in ids
        assert "child" in ids
