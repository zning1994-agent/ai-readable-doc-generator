"""Unit tests for Pydantic schemas in models/schema.py.

This test module provides comprehensive coverage for all schema models,
validating data structures, relationships, and serialization behavior.
"""

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from models.schema import (
    CodeLanguage,
    ContentBlock,
    ContentType,
    DocumentMetadata,
    DocumentSection,
    ImportanceLevel,
    ListItem,
    MCPSchema,
    MCPToolName,
    MCPToolResult,
    SemanticRelation,
    SemanticTag,
    SourceLocation,
    StructuredDocument,
    TableCell,
    TableRow,
    ValidationError as SchemaValidationError,
    ValidationResult,
)


# =============================================================================
# SourceLocation Tests
# =============================================================================


class TestSourceLocation:
    """Tests for SourceLocation model."""

    def test_valid_source_location(self):
        """Test creating a valid source location."""
        location = SourceLocation(
            line_start=1,
            line_end=10,
            column_start=1,
            column_end=50,
            file_path="/path/to/doc.md",
        )
        assert location.line_start == 1
        assert location.line_end == 10
        assert location.file_path == "/path/to/doc.md"

    def test_source_location_without_file_path(self):
        """Test source location without file path (optional)."""
        location = SourceLocation(
            line_start=5,
            line_end=15,
            column_start=1,
            column_end=100,
        )
        assert location.file_path is None

    def test_invalid_line_range(self):
        """Test that line_end < line_start raises error."""
        with pytest.raises(ValidationError) as exc_info:
            SourceLocation(
                line_start=10,
                line_end=5,
                column_start=1,
                column_end=50,
            )
        assert "line_end must be >= line_start" in str(exc_info.value)

    def test_invalid_column_range(self):
        """Test that column_end < column_start raises error."""
        with pytest.raises(ValidationError) as exc_info:
            SourceLocation(
                line_start=1,
                line_end=10,
                column_start=50,
                column_end=10,
            )
        assert "column_end must be >= column_start" in str(exc_info.value)

    def test_line_start_must_be_positive(self):
        """Test that line_start must be >= 1."""
        with pytest.raises(ValidationError):
            SourceLocation(
                line_start=0,
                line_end=10,
                column_start=1,
                column_end=50,
            )

    def test_serialization(self):
        """Test serialization to dict."""
        location = SourceLocation(
            line_start=1,
            line_end=5,
            column_start=1,
            column_end=20,
        )
        data = location.model_dump()
        assert data["line_start"] == 1
        assert data["line_end"] == 5


# =============================================================================
# SemanticTag Tests
# =============================================================================


class TestSemanticTag:
    """Tests for SemanticTag model."""

    def test_create_semantic_tag(self):
        """Test creating a semantic tag with all fields."""
        tag = SemanticTag(
            name="api_reference",
            value="GET",
            confidence=0.95,
            source="automatic",
            metadata={"endpoint": "/users"},
        )
        assert tag.name == "api_reference"
        assert tag.value == "GET"
        assert tag.confidence == 0.95

    def test_semantic_tag_defaults(self):
        """Test semantic tag default values."""
        tag = SemanticTag(name="test_tag")
        assert tag.value is None
        assert tag.confidence == 1.0
        assert tag.source == "heuristic"
        assert tag.metadata == {}

    def test_invalid_confidence_high(self):
        """Test that confidence > 1.0 raises error."""
        with pytest.raises(ValidationError):
            SemanticTag(name="test", confidence=1.5)

    def test_invalid_confidence_low(self):
        """Test that confidence < 0.0 raises error."""
        with pytest.raises(ValidationError):
            SemanticTag(name="test", confidence=-0.1)

    def test_name_length_validation(self):
        """Test name length constraints."""
        with pytest.raises(ValidationError):
            SemanticTag(name="")  # Too short
        with pytest.raises(ValidationError):
            SemanticTag(name="x" * 101)  # Too long


# =============================================================================
# DocumentMetadata Tests
# =============================================================================


class TestDocumentMetadata:
    """Tests for DocumentMetadata model."""

    def test_create_metadata(self):
        """Test creating document metadata with all fields."""
        metadata = DocumentMetadata(
            title="Test Document",
            description="A test document",
            author="Test Author",
            version="2.0.0",
            language="en",
            tags=["python", "testing"],
            word_count=1000,
        )
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert "python" in metadata.tags

    def test_metadata_defaults(self):
        """Test metadata default values."""
        metadata = DocumentMetadata()
        assert metadata.version == "1.0.0"
        assert metadata.source_format == "markdown"
        assert metadata.language == "en"
        assert metadata.tags == []
        assert metadata.word_count == 0

    def test_custom_fields(self):
        """Test custom fields support."""
        metadata = DocumentMetadata(
            custom_fields={
                "custom_key": "custom_value",
                "nested": {"key": "value"},
            }
        )
        assert metadata.custom_fields["custom_key"] == "custom_value"
        assert metadata.custom_fields["nested"]["key"] == "value"


# =============================================================================
# ContentBlock Tests
# =============================================================================


class TestContentBlock:
    """Tests for ContentBlock model."""

    def test_create_content_block(self):
        """Test creating a content block."""
        block = ContentBlock(
            id="block-1",
            content_type=ContentType.PARAGRAPH,
            raw_text="This is a test paragraph.",
        )
        assert block.id == "block-1"
        assert block.content_type == ContentType.PARAGRAPH
        assert block.raw_text == "This is a test paragraph."
        assert block.processed_text == block.raw_text  # Auto-set

    def test_content_block_with_semantic_tags(self):
        """Test content block with semantic tags."""
        tags = [
            SemanticTag(name="topic", value="testing"),
            SemanticTag(name="difficulty", value="beginner"),
        ]
        block = ContentBlock(
            id="block-2",
            content_type=ContentType.HEADING_2,
            raw_text="Getting Started",
            semantic_tags=tags,
        )
        assert len(block.semantic_tags) == 2
        assert block.semantic_tags[0].name == "topic"

    def test_content_block_with_source_location(self):
        """Test content block with source location."""
        location = SourceLocation(
            line_start=10,
            line_end=10,
            column_start=1,
            column_end=50,
        )
        block = ContentBlock(
            id="block-3",
            content_type=ContentType.CODE_BLOCK,
            raw_text="print('hello')",
            source_location=location,
        )
        assert block.source_location.line_start == 10

    def test_importance_level_default(self):
        """Test default importance level is MEDIUM."""
        block = ContentBlock(
            id="block-4",
            content_type=ContentType.PARAGRAPH,
            raw_text="Test",
        )
        assert block.importance == ImportanceLevel.MEDIUM

    def test_content_type_enum_values(self):
        """Test ContentType enum values."""
        assert ContentType.PARAGRAPH.value == "paragraph"
        assert ContentType.CODE_BLOCK.value == "code_block"
        assert ContentType.HEADING_1.value == "heading_1"


# =============================================================================
# DocumentSection Tests
# =============================================================================


class TestDocumentSection:
    """Tests for DocumentSection model."""

    def test_create_section(self):
        """Test creating a document section."""
        section = DocumentSection(
            id="section-1",
            heading="Introduction",
            heading_level=1,
        )
        assert section.id == "section-1"
        assert section.heading == "Introduction"
        assert section.heading_level == 1

    def test_section_with_content_blocks(self):
        """Test section with content blocks."""
        blocks = [
            ContentBlock(
                id="block-1",
                content_type=ContentType.PARAGRAPH,
                raw_text="First paragraph",
            ),
            ContentBlock(
                id="block-2",
                content_type=ContentType.PARAGRAPH,
                raw_text="Second paragraph",
            ),
        ]
        section = DocumentSection(
            id="section-2",
            heading="Main Content",
            heading_level=2,
            content_blocks=blocks,
        )
        assert len(section.content_blocks) == 2

    def test_nested_sections(self):
        """Test nested subsections."""
        child_section = DocumentSection(
            id="child-section",
            heading="Child Section",
            heading_level=2,
        )
        parent_section = DocumentSection(
            id="parent-section",
            heading="Parent Section",
            heading_level=1,
            subsections=[child_section],
        )
        assert len(parent_section.subsections) == 1
        assert parent_section.subsections[0].id == "child-section"

    def test_section_relations(self):
        """Test section relations."""
        relations = [
            {"type": SemanticRelation.SEE_ALSO.value, "target_id": "section-2"},
            {"type": SemanticRelation.DEPENDS_ON.value, "target_id": "section-3"},
        ]
        section = DocumentSection(
            id="section-4",
            heading="Advanced Topic",
            relations=relations,
        )
        assert len(section.relations) == 2
        assert section.relations[0]["type"] == "see_also"

    def test_invalid_relation_missing_type(self):
        """Test that relation without type raises error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentSection(
                id="section-5",
                relations=[{"target_id": "section-1"}],
            )
        assert "type" in str(exc_info.value)

    def test_invalid_relation_missing_target(self):
        """Test that relation without target_id raises error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentSection(
                id="section-6",
                relations=[{"type": "parent"}],
            )
        assert "target_id" in str(exc_info.value)

    def test_heading_level_constraints(self):
        """Test heading level must be 1-6."""
        with pytest.raises(ValidationError):
            DocumentSection(id="test", heading_level=0)
        with pytest.raises(ValidationError):
            DocumentSection(id="test", heading_level=7)


# =============================================================================
# StructuredDocument Tests
# =============================================================================


class TestStructuredDocument:
    """Tests for StructuredDocument model."""

    def test_create_document(self):
        """Test creating a structured document."""
        metadata = DocumentMetadata(title="Test Doc")
        section = DocumentSection(id="sec-1", heading="Test")
        doc = StructuredDocument(
            metadata=metadata,
            sections=[section],
        )
        assert doc.metadata.title == "Test Doc"
        assert len(doc.sections) == 1

    def test_document_must_have_at_least_one_section(self):
        """Test that document requires at least one section."""
        with pytest.raises(ValidationError):
            StructuredDocument(
                metadata=DocumentMetadata(),
                sections=[],
            )

    def test_get_all_sections_flat(self):
        """Test flattening nested sections."""
        child = DocumentSection(id="child", heading="Child")
        parent = DocumentSection(
            id="parent",
            heading="Parent",
            subsections=[child],
        )
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[parent],
        )
        all_sections = doc.get_all_sections()
        assert len(all_sections) == 2

    def test_get_section_by_id(self):
        """Test finding section by ID."""
        section = DocumentSection(id="unique-id", heading="Test")
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[section],
        )
        found = doc.get_section_by_id("unique-id")
        assert found is not None
        assert found.id == "unique-id"

    def test_get_section_by_id_not_found(self):
        """Test searching for non-existent section."""
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[DocumentSection(id="sec-1", heading="Test")],
        )
        found = doc.get_section_by_id("non-existent")
        assert found is None

    def test_get_all_content_blocks(self):
        """Test extracting all content blocks."""
        blocks = [
            ContentBlock(id="b1", content_type=ContentType.PARAGRAPH, raw_text="A"),
            ContentBlock(id="b2", content_type=ContentType.PARAGRAPH, raw_text="B"),
        ]
        section = DocumentSection(id="sec-1", content_blocks=blocks)
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[section],
        )
        all_blocks = doc.get_all_content_blocks()
        assert len(all_blocks) == 2

    def test_search_by_semantic_tag(self):
        """Test searching content by semantic tag."""
        tag = SemanticTag(name="category", value="tutorial")
        block = ContentBlock(
            id="b1",
            content_type=ContentType.PARAGRAPH,
            raw_text="Tutorial content",
            semantic_tags=[tag],
        )
        section = DocumentSection(id="sec-1", content_blocks=[block])
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[section],
        )
        results = doc.search_by_semantic_tag("category")
        assert len(results) == 1
        assert results[0][1].id == "b1"

    def test_to_dict_serialization(self):
        """Test dictionary serialization."""
        doc = StructuredDocument(
            metadata=DocumentMetadata(title="Test"),
            sections=[DocumentSection(id="sec-1", heading="Test")],
        )
        data = doc.to_dict()
        assert isinstance(data, dict)
        assert data["metadata"]["title"] == "Test"

    def test_to_json_serialization(self):
        """Test JSON serialization."""
        doc = StructuredDocument(
            metadata=DocumentMetadata(title="Test"),
            sections=[DocumentSection(id="sec-1", heading="Test")],
        )
        json_str = doc.to_json()
        assert isinstance(json_str, str)
        assert '"title": "Test"' in json_str


# =============================================================================
# ValidationResult Tests
# =============================================================================


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_valid_document(self):
        """Test validation result for valid document."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 0

    def test_validation_with_errors(self):
        """Test validation result with errors."""
        errors = [
            SchemaValidationError(
                field="metadata.title",
                message="Title is required",
                error_type="missing_field",
            ),
        ]
        result = ValidationResult(is_valid=False, errors=errors)
        assert result.error_count == 1
        assert result.warnings == []

    def test_validation_with_warnings(self):
        """Test validation result with warnings."""
        result = ValidationResult(
            is_valid=True,
            warnings=["Consider adding a description field"],
        )
        assert result.warning_count == 1


# =============================================================================
# MCPSchema Tests
# =============================================================================


class TestMCPSchema:
    """Tests for MCPSchema model."""

    def test_create_mcp_schema(self):
        """Test creating MCP-compatible schema."""
        metadata = DocumentMetadata(title="MCP Test")
        section = DocumentSection(id="sec-1", heading="Test")
        doc = StructuredDocument(
            metadata=metadata,
            sections=[section],
        )
        mcp = MCPSchema(
            document=doc,
            extraction_metadata={"parser": "markdown-it"},
        )
        assert mcp.document.metadata.title == "MCP Test"
        assert mcp.version == "1.0.0"

    def test_mcp_with_tool_results(self):
        """Test MCP schema with tool results."""
        metadata = DocumentMetadata()
        doc = StructuredDocument(
            metadata=metadata,
            sections=[DocumentSection(id="sec-1")],
        )
        tool_result = MCPToolResult(
            tool_name=MCPToolName.DOCUMENT_PARSER,
            success=True,
            result={"blocks_processed": 10},
        )
        mcp = MCPSchema(
            document=doc,
            tool_results=[tool_result],
        )
        assert len(mcp.tool_results) == 1
        assert mcp.tool_results[0].success is True

    def test_mcp_generated_timestamp(self):
        """Test that generated_at is automatically set."""
        before = datetime.utcnow()
        metadata = DocumentMetadata()
        doc = StructuredDocument(
            metadata=metadata,
            sections=[DocumentSection(id="sec-1")],
        )
        mcp = MCPSchema(document=doc)
        after = datetime.utcnow()
        assert before <= mcp.generated_at <= after


# =============================================================================
# ListItem Tests
# =============================================================================


class TestListItem:
    """Tests for ListItem model."""

    def test_create_list_item(self):
        """Test creating a list item."""
        item = ListItem(content="List item text")
        assert item.content == "List item text"
        assert item.checked is None
        assert item.nested_items == []

    def test_task_list_item(self):
        """Test task list item with checked state."""
        item = ListItem(content="Completed task", checked=True)
        assert item.checked is True

    def test_nested_list_items(self):
        """Test nested list items."""
        child = ListItem(content="Child item")
        parent = ListItem(content="Parent item", nested_items=[child])
        assert len(parent.nested_items) == 1


# =============================================================================
# TableCell and TableRow Tests
# =============================================================================


class TestTableCell:
    """Tests for TableCell model."""

    def test_create_table_cell(self):
        """Test creating a table cell."""
        cell = TableCell(content="Cell content")
        assert cell.content == "Cell content"
        assert cell.is_header is False
        assert cell.column_span == 1

    def test_header_cell(self):
        """Test creating a header cell."""
        cell = TableCell(content="Header", is_header=True)
        assert cell.is_header is True

    def test_cell_with_spans(self):
        """Test cell with column and row spans."""
        cell = TableCell(content="Merged cell", column_span=2, row_span=3)
        assert cell.column_span == 2
        assert cell.row_span == 3


class TestTableRow:
    """Tests for TableRow model."""

    def test_create_table_row(self):
        """Test creating a table row."""
        cells = [
            TableCell(content="A"),
            TableCell(content="B"),
            TableCell(content="C"),
        ]
        row = TableRow(cells=cells)
        assert len(row.cells) == 3


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    """Tests for all enum types."""

    def test_content_type_values(self):
        """Test ContentType enum values."""
        assert ContentType.PARAGRAPH.value == "paragraph"
        assert ContentType.CODE_BLOCK.value == "code_block"
        assert ContentType.HEADING_1.value == "heading_1"

    def test_importance_level_order(self):
        """Test ImportanceLevel enum has correct order."""
        levels = list(ImportanceLevel)
        assert ImportanceLevel.CRITICAL in levels
        assert ImportanceLevel.LOW in levels

    def test_semantic_relation_values(self):
        """Test SemanticRelation enum values."""
        assert SemanticRelation.PARENT.value == "parent"
        assert SemanticRelation.DEPENDS_ON.value == "depends_on"

    def test_code_language_values(self):
        """Test CodeLanguage enum values."""
        assert CodeLanguage.PYTHON.value == "python"
        assert CodeLanguage.JAVASCRIPT.value == "javascript"

    def test_mcp_tool_name_values(self):
        """Test MCPToolName enum values."""
        assert MCPToolName.DOCUMENT_PARSER.value == "document_parser"
        assert MCPToolName.SEMANTIC_EXTRACTOR.value == "semantic_extractor"


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_deeply_nested_sections(self):
        """Test deeply nested section hierarchy."""
        section = DocumentSection(id="level-1", heading="Level 1")
        for i in range(2, 6):
            section = DocumentSection(
                id=f"level-{i}",
                heading=f"Level {i}",
                subsections=[section],
            )
        doc = StructuredDocument(
            metadata=DocumentMetadata(),
            sections=[section],
        )
        all_sections = doc.get_all_sections()
        assert len(all_sections) == 5

    def test_empty_semantic_tags_list(self):
        """Test section with empty semantic tags list."""
        section = DocumentSection(
            id="sec-1",
            semantic_tags=[],
        )
        assert section.semantic_tags == []

    def test_large_custom_fields(self):
        """Test document with large custom fields."""
        large_data = {"key": "x" * 10000}
        metadata = DocumentMetadata(custom_fields=large_data)
        assert len(metadata.custom_fields["key"]) == 10000

    def test_mixed_content_blocks(self):
        """Test section with mixed content types."""
        blocks = [
            ContentBlock(id="p1", content_type=ContentType.PARAGRAPH, raw_text="Text"),
            ContentBlock(id="c1", content_type=ContentType.CODE_BLOCK, raw_text="code"),
            ContentBlock(id="b1", content_type=ContentType.BULLET_LIST, raw_text="• item"),
        ]
        section = DocumentSection(id="sec-1", content_blocks=blocks)
        assert len(section.content_blocks) == 3
        assert section.content_blocks[0].content_type == ContentType.PARAGRAPH
