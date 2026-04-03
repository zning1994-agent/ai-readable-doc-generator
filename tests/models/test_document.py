"""Unit tests for document module."""

import json

import pytest

from ai_readable_doc_generator.models.document import Document, DocumentMetadata
from ai_readable_doc_generator.models.section import ContentType, Section, SectionType, SemanticTag


class TestDocumentMetadata:
    """Tests for DocumentMetadata class."""

    def test_create_empty_metadata(self):
        """Test creating empty metadata."""
        metadata = DocumentMetadata()

        assert metadata.author is None
        assert metadata.version is None
        assert metadata.created_at is None
        assert metadata.updated_at is None
        assert metadata.language == "en"
        assert metadata.license is None
        assert metadata.tags == []
        assert metadata.custom == {}

    def test_create_metadata_with_values(self):
        """Test creating metadata with values."""
        metadata = DocumentMetadata(
            author="John Doe",
            version="1.0",
            created_at="2024-01-01",
            language="en",
            tags=["python", "documentation"],
        )

        assert metadata.author == "John Doe"
        assert metadata.version == "1.0"
        assert metadata.tags == ["python", "documentation"]

    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = DocumentMetadata(
            author="Jane Doe",
            version="2.0",
            language="en",
        )

        result = metadata.to_dict()

        assert result["author"] == "Jane Doe"
        assert result["version"] == "2.0"
        assert result["language"] == "en"
        assert "custom" not in result or result.get("custom") == {}

    def test_to_dict_with_custom(self):
        """Test converting metadata with custom fields to dict."""
        metadata = DocumentMetadata(custom={"custom_field": "value"})

        result = metadata.to_dict()

        assert result["custom_field"] == "value"

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "author": "Test Author",
            "version": "1.5",
            "language": "zh",
            "tags": ["test"],
        }

        metadata = DocumentMetadata.from_dict(data)

        assert metadata.author == "Test Author"
        assert metadata.version == "1.5"
        assert metadata.language == "zh"
        assert metadata.tags == ["test"]

    def test_from_dict_with_defaults(self):
        """Test creating metadata from dict with missing fields."""
        data = {"author": "Only Author"}

        metadata = DocumentMetadata.from_dict(data)

        assert metadata.author == "Only Author"
        assert metadata.language == "en"
        assert metadata.tags == []

    def test_from_dict_custom_fields(self):
        """Test that custom fields are preserved."""
        data = {
            "author": "Test",
            "custom_api_key": "secret",
            "custom_value": 123,
        }

        metadata = DocumentMetadata.from_dict(data)

        assert metadata.custom["custom_api_key"] == "secret"
        assert metadata.custom["custom_value"] == 123


class TestDocument:
    """Tests for Document class."""

    def test_create_document(self):
        """Test creating a basic document."""
        doc = Document(title="Test Document")

        assert doc.title == "Test Document"
        assert doc.content_type == ContentType.OTHER
        assert doc.sections == []
        assert doc.metadata is not None
        assert doc.semantic_tags == []
        assert doc.source_path is None

    def test_create_document_with_content_type(self):
        """Test creating document with content type."""
        doc = Document(
            title="API Reference",
            content_type=ContentType.API_REFERENCE,
        )

        assert doc.content_type == ContentType.API_REFERENCE

    def test_add_section(self):
        """Test adding sections to document."""
        doc = Document(title="Test")
        section = Section(section_type=SectionType.PARAGRAPH, content="Hello")

        doc.add_section(section)

        assert len(doc.sections) == 1
        assert doc.sections[0].content == "Hello"

    def test_add_semantic_tag(self):
        """Test adding semantic tags."""
        doc = Document(title="Test")
        tag = SemanticTag(name="documentation")

        doc.add_semantic_tag(tag)

        assert len(doc.semantic_tags) == 1
        assert doc.semantic_tags[0].name == "documentation"

    def test_get_all_tags(self):
        """Test getting all tags from document and sections."""
        doc = Document(title="Test")
        doc_tag = SemanticTag(name="doc_tag")
        section = Section(section_type=SectionType.PARAGRAPH, content="Test")
        section_tag = SemanticTag(name="section_tag")

        doc.add_semantic_tag(doc_tag)
        doc.add_section(section)
        doc.sections[0].add_semantic_tag(section_tag)

        all_tags = doc.get_all_tags()
        tag_names = [t.name for t in all_tags]

        assert "doc_tag" in tag_names
        assert "section_tag" in tag_names

    def test_get_text_content(self):
        """Test getting all text content."""
        doc = Document(title="Title")
        doc.add_section(Section(section_type=SectionType.PARAGRAPH, content="Content"))

        text = doc.get_text_content()

        assert "Title" in text
        assert "Content" in text

    def test_to_dict(self):
        """Test converting document to dictionary."""
        doc = Document(title="Test Document")
        doc.metadata = DocumentMetadata(author="Test Author")

        result = doc.to_dict()

        assert result["title"] == "Test Document"
        assert result["content_type"] == "other"
        assert result["sections"] == []
        assert result["metadata"]["author"] == "Test Author"
        assert result["source_path"] is None

    def test_to_dict_with_sections(self):
        """Test converting document with sections to dict."""
        doc = Document(title="Test")
        doc.add_section(Section(section_type=SectionType.HEADING, heading="Section 1"))
        doc.add_section(
            Section(
                section_type=SectionType.PARAGRAPH,
                content="Some content",
            )
        )

        result = doc.to_dict()

        assert len(result["sections"]) == 2
        assert result["sections"][0]["heading"] == "Section 1"
        assert result["sections"][1]["content"] == "Some content"

    def test_to_json(self):
        """Test converting document to JSON string."""
        doc = Document(title="Test")

        json_str = doc.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["title"] == "Test"

    def test_to_json_indent(self):
        """Test JSON indentation."""
        doc = Document(title="Test")

        json_str = doc.to_json(indent=4)

        assert "\n" in json_str  # Should have newlines due to indentation

    def test_from_dict(self):
        """Test creating document from dictionary."""
        data = {
            "title": "My Document",
            "content_type": "api_reference",
            "sections": [
                {"type": "paragraph", "content": "Test content", "level": 1}
            ],
            "metadata": {"author": "Test"},
            "semantic_tags": [],
        }

        doc = Document.from_dict(data)

        assert doc.title == "My Document"
        assert doc.content_type == ContentType.API_REFERENCE
        assert len(doc.sections) == 1
        assert doc.metadata.author == "Test"

    def test_from_dict_with_defaults(self):
        """Test creating document from dict with missing fields."""
        data = {"title": "Minimal"}

        doc = Document.from_dict(data)

        assert doc.title == "Minimal"
        assert doc.content_type == ContentType.OTHER
        assert doc.sections == []

    def test_from_json(self):
        """Test creating document from JSON string."""
        json_str = '{"title": "JSON Document", "content_type": "introduction"}'

        doc = Document.from_json(json_str)

        assert doc.title == "JSON Document"
        assert doc.content_type == ContentType.INTRODUCTION

    def test_validate_valid_document(self):
        """Test validating a valid document."""
        doc = Document(title="Valid")
        doc.add_section(Section(section_type=SectionType.PARAGRAPH, content="Content"))

        is_valid, errors = doc.validate()

        assert is_valid is True
        assert errors == []

    def test_validate_empty_title(self):
        """Test validation fails for empty title."""
        doc = Document(title="")
        doc.add_section(Section(section_type=SectionType.PARAGRAPH, content="Content"))

        is_valid, errors = doc.validate()

        assert is_valid is False
        assert "Document title is required" in errors

    def test_validate_no_sections(self):
        """Test validation fails for no sections."""
        doc = Document(title="No Sections")

        is_valid, errors = doc.validate()

        assert is_valid is False
        assert "Document must have at least one section" in errors

    def test_validate_section_no_content(self):
        """Test validation fails for section without content."""
        doc = Document(title="Test")
        doc.add_section(Section(section_type=SectionType.PARAGRAPH, content=""))

        is_valid, errors = doc.validate()

        assert is_valid is False
        assert any("no content or heading" in e for e in errors)

    def test_get_headings(self):
        """Test getting all headings."""
        doc = Document(title="Test")
        doc.add_section(Section(section_type=SectionType.HEADING, heading="H1", level=1))
        doc.add_section(
            Section(section_type=SectionType.HEADING, heading="H2", level=2)
        )

        headings = doc.get_headings()

        assert len(headings) == 2
        assert (1, "H1") in headings
        assert (2, "H2") in headings

    def test_get_headings_nested(self):
        """Test getting headings from nested sections."""
        doc = Document(title="Test")
        parent = Section(section_type=SectionType.HEADING, heading="Parent", level=1)
        child = Section(section_type=SectionType.HEADING, heading="Child", level=2)
        parent.add_child(child)
        doc.add_section(parent)

        headings = doc.get_headings()

        assert len(headings) == 2
        assert ("Child", "Child") in [(h[1], h[1]) for h in headings]

    def test_get_code_sections(self):
        """Test getting all code sections."""
        doc = Document(title="Test")
        doc.add_section(
            Section(section_type=SectionType.CODE_BLOCK, content="code1")
        )
        doc.add_section(
            Section(section_type=SectionType.PARAGRAPH, content="text")
        )
        doc.add_section(
            Section(section_type=SectionType.CODE_BLOCK, content="code2")
        )

        code_sections = doc.get_code_sections()

        assert len(code_sections) == 2
        assert all(s.is_code_section() for s in code_sections)

    def test_export_json(self):
        """Test exporting to JSON format."""
        from ai_readable_doc_generator.models.schema import OutputFormat

        doc = Document(title="Export Test")

        result = doc.export(OutputFormat.JSON)

        assert isinstance(result, str)
        assert "Export Test" in result

    def test_export_markdown(self):
        """Test exporting to Markdown format."""
        from ai_readable_doc_generator.models.schema import OutputFormat

        doc = Document(title="MD Export")
        doc.add_section(Section(section_type=SectionType.HEADING, heading="Section 1"))
        doc.add_section(Section(section_type=SectionType.PARAGRAPH, content="Content"))

        result = doc.export(OutputFormat.MARKDOWN)

        assert "# MD Export" in result
        assert "# Section 1" in result
        assert "Content" in result

    def test_export_yaml(self):
        """Test exporting to YAML format."""
        from ai_readable_doc_generator.models.schema import OutputFormat

        doc = Document(title="YAML Export")

        result = doc.export(OutputFormat.YAML)

        assert "title:" in result
        assert "YAML Export" in result

    def test_export_unsupported_format(self):
        """Test exporting unsupported format raises error."""
        from ai_readable_doc_generator.models.schema import OutputFormat

        doc = Document(title="Test")

        with pytest.raises(ValueError, match="Unsupported format"):
            doc.export(OutputFormat.MCP)


class TestDocumentIntegration:
    """Integration tests for document with sections."""

    def test_complete_document_structure(self):
        """Test a complete document with all features."""
        doc = Document(
            title="Complete Documentation",
            content_type=ContentType.API_REFERENCE,
            source_path="/path/to/doc.md",
        )
        doc.metadata.author = "Dev Team"
        doc.metadata.tags = ["api", "reference"]
        doc.add_semantic_tag(SemanticTag(name="official"))

        # Add heading section
        intro = Section(
            section_type=SectionType.HEADING,
            heading="Introduction",
            level=1,
            content_type=ContentType.INTRODUCTION,
        )
        intro.add_semantic_tag(SemanticTag(name="overview"))
        doc.add_section(intro)

        # Add content section
        content = Section(
            section_type=SectionType.PARAGRAPH,
            content="This is the introduction content.",
        )
        intro.add_child(content)

        # Add code section
        code = Section(
            section_type=SectionType.CODE_BLOCK,
            content="print('hello')",
            content_type=ContentType.CODE_EXAMPLE,
        )
        code.add_semantic_tag(SemanticTag(name="example", confidence=0.95))
        doc.add_section(code)

        # Verify structure
        assert doc.title == "Complete Documentation"
        assert doc.content_type == ContentType.API_REFERENCE
        assert len(doc.sections) == 2
        assert len(doc.get_all_tags()) == 3

        # Export and verify
        json_str = doc.to_json()
        restored = Document.from_json(json_str)
        assert restored.title == doc.title
        assert len(restored.sections) == len(doc.sections)

    def test_document_roundtrip(self):
        """Test document serialization roundtrip."""
        doc = Document(title="Roundtrip Test")
        doc.add_section(
            Section(
                section_type=SectionType.PARAGRAPH,
                content="Test content",
            )
        )

        # Serialize
        json_str = doc.to_json()
        data = json.loads(json_str)

        # Deserialize
        restored = Document.from_dict(data)

        assert restored.title == doc.title
        assert len(restored.sections) == 1
        assert restored.sections[0].content == "Test content"
