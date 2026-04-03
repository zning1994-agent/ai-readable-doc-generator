"""
Tests for document models.

These tests verify the Pydantic models for structured document output.
"""

import pytest
from pydantic import ValidationError

from ai_readable_doc_generator.document import (
    CodeBlock,
    ContentType,
    Document,
    DocumentMetadata,
    ImportanceLevel,
    List,
    ListItem,
    ListType,
    Paragraph,
    Section,
    Table,
    TableRow,
)


class TestParagraph:
    """Tests for Paragraph model."""

    def test_create_paragraph(self):
        """Test creating a basic paragraph."""
        paragraph = Paragraph(content="This is a test paragraph.")
        assert paragraph.content == "This is a test paragraph."
        assert paragraph.content_type == ContentType.PARAGRAPH
        assert paragraph.importance == ImportanceLevel.MEDIUM
        assert paragraph.is_note is False
        assert paragraph.is_summary is False

    def test_paragraph_with_all_fields(self):
        """Test creating paragraph with all optional fields."""
        paragraph = Paragraph(
            content="Important note content",
            importance=ImportanceLevel.HIGH,
            is_note=True,
            is_summary=False,
            metadata={"source": "author_note"},
        )
        assert paragraph.is_note is True
        assert paragraph.importance == ImportanceLevel.HIGH
        assert paragraph.metadata["source"] == "author_note"

    def test_paragraph_custom_metadata(self):
        """Test custom metadata storage."""
        paragraph = Paragraph(
            content="Test",
            metadata={"key1": "value1", "key2": 42},
        )
        assert paragraph.metadata["key1"] == "value1"
        assert paragraph.metadata["key2"] == 42


class TestListItem:
    """Tests for ListItem model."""

    def test_create_list_item(self):
        """Test creating a basic list item."""
        item = ListItem(content="First item")
        assert item.content == "First item"
        assert item.is_checked is None
        assert item.children == []

    def test_task_list_item(self):
        """Test creating a task list item with checked state."""
        item = ListItem(content="Completed task", is_checked=True)
        assert item.is_checked is True

    def test_nested_list_item(self):
        """Test list item with nested children."""
        child = ListItem(content="Child item")
        parent = ListItem(content="Parent item", children=[child])
        assert len(parent.children) == 1
        assert parent.children[0].content == "Child item"


class TestList:
    """Tests for List model."""

    def test_create_unordered_list(self):
        """Test creating an unordered list."""
        items = [
            ListItem(content="Item 1"),
            ListItem(content="Item 2"),
        ]
        list_obj = List(items=items, list_type=ListType.UNORDERED)
        assert len(list_obj.items) == 2
        assert list_obj.content_type == ContentType.LIST
        assert list_obj.list_type == ListType.UNORDERED

    def test_create_ordered_list(self):
        """Test creating an ordered list."""
        items = [ListItem(content=f"Step {i}") for i in range(1, 4)]
        list_obj = List(items=items, list_type=ListType.ORDERED)
        assert list_obj.list_type == ListType.ORDERED
        assert len(list_obj.items) == 3

    def test_create_task_list(self):
        """Test creating a task list."""
        items = [
            ListItem(content="Task 1", is_checked=True),
            ListItem(content="Task 2", is_checked=False),
        ]
        list_obj = List(items=items, list_type=ListType.TASK)
        assert list_obj.list_type == ListType.TASK
        assert list_obj.items[0].is_checked is True


class TestCodeBlock:
    """Tests for CodeBlock model."""

    def test_create_code_block(self):
        """Test creating a basic code block."""
        code = CodeBlock(code='print("Hello, World!")', language="python")
        assert code.code == 'print("Hello, World!")'
        assert code.language == "python"
        assert code.content_type == ContentType.CODE_BLOCK

    def test_code_block_with_file_name(self):
        """Test code block with suggested file name."""
        code = CodeBlock(
            code="def main(): pass",
            language="python",
            file_name="main.py",
            is_executable=True,
        )
        assert code.file_name == "main.py"
        assert code.is_executable is True

    def test_code_block_default_language(self):
        """Test code block default language."""
        code = CodeBlock(code="some text")
        assert code.language == "text"


class TestTableRow:
    """Tests for TableRow model."""

    def test_create_table_row(self):
        """Test creating a table row."""
        row = TableRow(cells=["Cell 1", "Cell 2", "Cell 3"])
        assert len(row.cells) == 3
        assert row.is_header is False

    def test_header_row(self):
        """Test creating a header row."""
        row = TableRow(cells=["Header 1", "Header 2"], is_header=True)
        assert row.is_header is True


class TestTable:
    """Tests for Table model."""

    def test_create_table(self):
        """Test creating a basic table."""
        headers = ["Name", "Age", "City"]
        rows = [
            TableRow(cells=["Alice", "30", "NYC"]),
            TableRow(cells=["Bob", "25", "LA"]),
        ]
        table = Table(headers=headers, rows=rows)
        assert len(table.headers) == 3
        assert len(table.rows) == 2
        assert table.content_type == ContentType.TABLE

    def test_table_with_caption(self):
        """Test table with caption."""
        table = Table(
            headers=["Col1"],
            rows=[TableRow(cells=["Data"])],
            caption="User Statistics",
        )
        assert table.caption == "User Statistics"


class TestSection:
    """Tests for Section model."""

    def test_create_section(self):
        """Test creating a basic section."""
        section = Section(id="intro", title="Introduction", level=1)
        assert section.id == "intro"
        assert section.title == "Introduction"
        assert section.level == 1
        assert section.content_type == ContentType.HEADING

    def test_section_with_content(self):
        """Test section with various content types."""
        section = Section(
            id="example",
            title="Example",
            level=2,
            paragraphs=[Paragraph(content="Example paragraph.")],
            lists=[List(items=[ListItem(content="List item")])],
            code_blocks=[CodeBlock(code="x = 1", language="python")],
            tables=[Table(headers=["Col"], rows=[TableRow(cells=["Data"])])],
        )
        assert len(section.paragraphs) == 1
        assert len(section.lists) == 1
        assert len(section.code_blocks) == 1
        assert len(section.tables) == 1

    def test_nested_sections(self):
        """Test section with nested child sections."""
        child = Section(id="child", title="Child Section", level=2)
        parent = Section(id="parent", title="Parent Section", level=1, children=[child])
        assert len(parent.children) == 1
        assert parent.children[0].id == "child"

    def test_section_order(self):
        """Test section ordering."""
        section = Section(id="section", title="Section", order=5)
        assert section.order == 5

    def test_section_importance(self):
        """Test section importance level."""
        section = Section(
            id="important",
            title="Important Section",
            importance=ImportanceLevel.CRITICAL,
        )
        assert section.importance == ImportanceLevel.CRITICAL


class TestDocumentMetadata:
    """Tests for DocumentMetadata model."""

    def test_create_metadata(self):
        """Test creating document metadata."""
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            language="en",
        )
        assert metadata.title == "Test Document"
        assert metadata.author == "Test Author"
        assert metadata.language == "en"

    def test_metadata_with_tags(self):
        """Test metadata with tags."""
        metadata = DocumentMetadata(
            title="Tagged Document",
            tags=["python", "tutorial", "beginner"],
        )
        assert len(metadata.tags) == 3
        assert "python" in metadata.tags

    def test_metadata_defaults(self):
        """Test metadata default values."""
        metadata = DocumentMetadata()
        assert metadata.language == "en"
        assert metadata.tags == []


class TestDocument:
    """Tests for Document model."""

    def test_create_empty_document(self):
        """Test creating an empty document."""
        doc = Document()
        assert doc.version == "1.0.0"
        assert doc.sections == []
        assert doc.metadata is not None

    def test_document_with_sections(self):
        """Test document with sections."""
        sections = [
            Section(id="s1", title="Section 1", level=1),
            Section(id="s2", title="Section 2", level=1),
        ]
        doc = Document(sections=sections)
        assert len(doc.sections) == 2

    def test_document_counts_paragraphs(self):
        """Test document paragraph counting."""
        sections = [
            Section(
                id="s1",
                paragraphs=[
                    Paragraph(content="Para 1"),
                    Paragraph(content="Para 2"),
                ],
            ),
        ]
        doc = Document(sections=sections)
        assert doc.total_paragraphs == 2

    def test_document_counts_nested_content(self):
        """Test document counts include nested content."""
        nested_para = Paragraph(content="Nested")
        child_section = Section(id="child", paragraphs=[nested_para])
        parent_section = Section(
            id="parent",
            paragraphs=[Paragraph(content="Parent")],
            children=[child_section],
        )
        doc = Document(sections=[parent_section])
        assert doc.total_paragraphs == 2

    def test_document_counts_all_content_types(self):
        """Test document counts all content types."""
        sections = [
            Section(
                id="s1",
                paragraphs=[Paragraph(content="Text")],
                lists=[List(items=[ListItem(content="Item")])],
                code_blocks=[CodeBlock(code="x=1")],
                tables=[Table(headers=["H"], rows=[TableRow(cells=["D"])])],
            ),
        ]
        doc = Document(sections=sections)
        assert doc.total_paragraphs == 1
        assert doc.total_lists == 1
        assert doc.total_code_blocks == 1
        assert doc.total_tables == 1

    def test_document_with_metadata(self):
        """Test document with full metadata."""
        metadata = DocumentMetadata(
            title="Complete Document",
            author="Developer",
            source_path="/path/to/doc.md",
            tags=["test", "example"],
        )
        doc = Document(metadata=metadata)
        assert doc.metadata.title == "Complete Document"
        assert doc.metadata.author == "Developer"

    def test_document_serialization(self):
        """Test document can be serialized to JSON."""
        doc = Document(
            metadata=DocumentMetadata(title="Test"),
            sections=[Section(id="sec1", title="Section 1")],
        )
        json_str = doc.model_dump_json()
        assert '"title": "Test"' in json_str
        assert '"id": "sec1"' in json_str

    def test_document_deserialization(self):
        """Test document can be deserialized from JSON."""
        json_data = {
            "version": "1.0.0",
            "metadata": {"title": "From JSON"},
            "sections": [
                {
                    "id": "sec1",
                    "title": "Loaded Section",
                    "level": 1,
                    "content_type": "heading",
                }
            ],
        }
        doc = Document.model_validate(json_data)
        assert doc.metadata.title == "From JSON"
        assert len(doc.sections) == 1
        assert doc.sections[0].title == "Loaded Section"
