"""Tests for schema models."""

import pytest
from pydantic import ValidationError

from ai_readable_doc_generator.models.schema import (
    ContentType,
    DocumentMetadata,
    HeadingLevel,
    RelationshipType,
    SemanticBlock,
    SemanticDocument,
    SemanticSection,
)


class TestContentType:
    """Tests for ContentType enum."""

    def test_content_type_values(self) -> None:
        """Test ContentType enum values."""
        assert ContentType.TEXT.value == "text"
        assert ContentType.HEADING.value == "heading"
        assert ContentType.CODE_BLOCK.value == "code_block"
        assert ContentType.LIST.value == "list"
        assert ContentType.LINK.value == "link"
        assert ContentType.IMAGE.value == "image"

    def test_content_type_from_string(self) -> None:
        """Test creating ContentType from string."""
        ct = ContentType("text")
        assert ct == ContentType.TEXT


class TestHeadingLevel:
    """Tests for HeadingLevel enum."""

    def test_heading_level_values(self) -> None:
        """Test HeadingLevel enum values."""
        assert HeadingLevel.H1.value == "h1"
        assert HeadingLevel.H2.value == "h2"
        assert HeadingLevel.H3.value == "h3"
        assert HeadingLevel.H4.value == "h4"
        assert HeadingLevel.H5.value == "h5"
        assert HeadingLevel.H6.value == "h6"


class TestRelationshipType:
    """Tests for RelationshipType enum."""

    def test_relationship_type_values(self) -> None:
        """Test RelationshipType enum values."""
        assert RelationshipType.PARENT.value == "parent"
        assert RelationshipType.CHILD.value == "child"
        assert RelationshipType.SIBLING.value == "sibling"
        assert RelationshipType.REFERENCE.value == "reference"


class TestDocumentMetadata:
    """Tests for DocumentMetadata model."""

    def test_default_metadata(self) -> None:
        """Test default metadata values."""
        metadata = DocumentMetadata()
        assert metadata.source_format == "markdown"
        assert metadata.title is None
        assert metadata.word_count == 0
        assert metadata.tags == []
        assert metadata.custom == {}

    def test_custom_metadata(self) -> None:
        """Test custom metadata values."""
        metadata = DocumentMetadata(
            source_path="/path/to/doc.md",
            title="Test Document",
            author="Test Author",
            version="1.0.0",
            word_count=100,
        )
        assert metadata.source_path == "/path/to/doc.md"
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.version == "1.0.0"
        assert metadata.word_count == 100


class TestSemanticBlock:
    """Tests for SemanticBlock model."""

    def test_create_block(self) -> None:
        """Test creating a semantic block."""
        block = SemanticBlock(
            id="block_001",
            content_type=ContentType.TEXT,
            content="Hello, World!",
            line_number=1,
        )
        assert block.id == "block_001"
        assert block.content_type == ContentType.TEXT
        assert block.content == "Hello, World!"
        assert block.line_number == 1

    def test_block_with_code_language(self) -> None:
        """Test block with code language."""
        block = SemanticBlock(
            id="block_002",
            content_type=ContentType.CODE_BLOCK,
            content="def hello(): pass",
            language="python",
        )
        assert block.language == "python"

    def test_block_with_url(self) -> None:
        """Test block with URL (link/image)."""
        block = SemanticBlock(
            id="block_003",
            content_type=ContentType.LINK,
            content="Click here",
            url="https://example.com",
        )
        assert block.url == "https://example.com"

    def test_block_with_semantic_tags(self) -> None:
        """Test block with semantic tags."""
        block = SemanticBlock(
            id="block_004",
            content_type=ContentType.HEADING,
            content="Installation",
            semantic_tags=["section:installation", "category:guide"],
        )
        assert "section:installation" in block.semantic_tags

    def test_block_with_importance(self) -> None:
        """Test block with importance level."""
        block = SemanticBlock(
            id="block_005",
            content_type=ContentType.TEXT,
            content="Warning: Important!",
            importance="high",
        )
        assert block.importance == "high"

    def test_block_with_relationships(self) -> None:
        """Test block with relationships."""
        block = SemanticBlock(
            id="block_006",
            content_type=ContentType.TEXT,
            content="Content",
            relationships=[
                {"type": "sequential", "related_id": "block_005", "direction": "previous"},
            ],
        )
        assert len(block.relationships) == 1
        assert block.relationships[0]["type"] == "sequential"


class TestSemanticSection:
    """Tests for SemanticSection model."""

    def test_create_section(self) -> None:
        """Test creating a semantic section."""
        section = SemanticSection(
            id="section_001",
            title="Introduction",
            level=HeadingLevel.H1,
        )
        assert section.id == "section_001"
        assert section.title == "Introduction"
        assert section.level == HeadingLevel.H1
        assert section.blocks == []
        assert section.child_sections == []

    def test_section_with_blocks(self) -> None:
        """Test section with content blocks."""
        block = SemanticBlock(
            id="block_001",
            content_type=ContentType.TEXT,
            content="Some text",
        )
        section = SemanticSection(
            id="section_002",
            title="Test Section",
            level=HeadingLevel.H2,
            blocks=[block],
        )
        assert len(section.blocks) == 1
        assert section.blocks[0].content == "Some text"

    def test_section_with_child_sections(self) -> None:
        """Test section with nested child sections."""
        child = SemanticSection(
            id="section_child",
            title="Child Section",
            level=HeadingLevel.H3,
        )
        parent = SemanticSection(
            id="section_parent",
            title="Parent Section",
            level=HeadingLevel.H2,
            child_sections=[child],
        )
        assert len(parent.child_sections) == 1
        assert parent.child_sections[0].title == "Child Section"

    def test_section_word_count(self) -> None:
        """Test section word count calculation."""
        section = SemanticSection(
            id="section_003",
            blocks=[
                SemanticBlock(id="b1", content_type=ContentType.TEXT, content="One two three"),
                SemanticBlock(id="b2", content_type=ContentType.TEXT, content="Four five six"),
            ],
        )
        section.word_count = sum(len(b.content.split()) for b in section.blocks)
        assert section.word_count == 6


class TestSemanticDocument:
    """Tests for SemanticDocument model."""

    def test_create_document(self) -> None:
        """Test creating a semantic document."""
        doc = SemanticDocument()
        assert doc.version == "1.0"
        assert doc.sections == []
        assert doc.all_blocks == []
        assert doc.table_of_contents == []
        assert doc.statistics == {}

    def test_document_with_sections(self) -> None:
        """Test document with sections."""
        section = SemanticSection(
            id="section_001",
            title="Test",
            level=HeadingLevel.H1,
        )
        doc = SemanticDocument(sections=[section])
        assert len(doc.sections) == 1

    def test_document_to_dict(self) -> None:
        """Test converting document to dictionary."""
        doc = SemanticDocument(
            metadata=DocumentMetadata(title="Test Doc"),
        )
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert d["metadata"]["title"] == "Test Doc"

    def test_document_to_json(self) -> None:
        """Test converting document to JSON string."""
        doc = SemanticDocument(
            metadata=DocumentMetadata(title="Test Doc"),
        )
        json_str = doc.to_json()
        assert isinstance(json_str, str)
        assert "Test Doc" in json_str

    def test_document_metadata_access(self) -> None:
        """Test accessing document metadata."""
        doc = SemanticDocument()
        assert doc.metadata.source_format == "markdown"
        doc.metadata.title = "New Title"
        assert doc.metadata.title == "New Title"
