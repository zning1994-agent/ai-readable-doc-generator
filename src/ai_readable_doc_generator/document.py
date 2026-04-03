"""
Pydantic models for structured document output.

This module defines the core data models for representing documents
in an AI-agent-friendly format with semantic tagging and metadata.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Semantic content type classification for AI parsing."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    QUOTE = "quote"
    IMAGE = "image"
    LINK = "link"
    HORIZONTAL_RULE = "horizontal_rule"
    MATH = "math"
    NOTE = "note"
    UNKNOWN = "unknown"


class ImportanceLevel(str, Enum):
    """Content importance level for AI attention weighting."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ListType(str, Enum):
    """List classification."""

    ORDERED = "ordered"
    UNORDERED = "unordered"
    TASK = "task"


class Paragraph(BaseModel):
    """
    Represents a paragraph content block.

    Attributes:
        content: The text content of the paragraph.
        content_type: Semantic classification (always 'paragraph').
        importance: Relative importance level for AI processing.
        is_note: Whether this paragraph is a note or aside.
        is_summary: Whether this is a summary/conclusion paragraph.
    """

    content: str = Field(description="The text content of the paragraph")
    content_type: ContentType = Field(
        default=ContentType.PARAGRAPH,
        description="Semantic content type classification"
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Relative importance level for AI processing"
    )
    is_note: bool = Field(
        default=False,
        description="Whether this paragraph is a note or aside"
    )
    is_summary: bool = Field(
        default=False,
        description="Whether this is a summary or conclusion paragraph"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility"
    )


class ListItem(BaseModel):
    """
    Represents a single item within a list.

    Attributes:
        content: The text content of the list item.
        is_checked: For task lists, whether the item is completed.
        children: Nested list items for hierarchical lists.
    """

    content: str = Field(description="The text content of the list item")
    is_checked: Optional[bool] = Field(
        default=None,
        description="For task lists, whether the item is completed"
    )
    children: list["ListItem"] = Field(
        default_factory=list,
        description="Nested child list items"
    )


class List(BaseModel):
    """
    Represents a list content block.

    Attributes:
        list_type: Classification of the list type.
        items: The list items in order.
        content_type: Semantic classification (always 'list').
        importance: Relative importance level for AI processing.
    """

    list_type: ListType = Field(
        default=ListType.UNORDERED,
        description="Type of list (ordered, unordered, or task)"
    )
    items: list[ListItem] = Field(
        default_factory=list,
        description="The list items in order"
    )
    content_type: ContentType = Field(
        default=ContentType.LIST,
        description="Semantic content type classification"
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Relative importance level for AI processing"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility"
    )


class CodeBlock(BaseModel):
    """
    Represents a code block content.

    Attributes:
        code: The code content.
        language: Programming/language identifier (e.g., 'python', 'javascript').
        content_type: Semantic classification (always 'code_block').
        importance: Relative importance level for AI processing.
        is_executable: Whether the code is meant to be run.
        file_name: Suggested file name for the code (if applicable).
    """

    code: str = Field(description="The code content")
    language: str = Field(
        default="text",
        description="Programming/language identifier"
    )
    content_type: ContentType = Field(
        default=ContentType.CODE_BLOCK,
        description="Semantic content type classification"
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Relative importance level for AI processing"
    )
    is_executable: bool = Field(
        default=False,
        description="Whether the code is meant to be executed"
    )
    file_name: Optional[str] = Field(
        default=None,
        description="Suggested file name for the code"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility"
    )


class TableRow(BaseModel):
    """Represents a single row in a table."""

    cells: list[str] = Field(
        description="Cell values in order"
    )
    is_header: bool = Field(
        default=False,
        description="Whether this row is a header row"
    )


class Table(BaseModel):
    """
    Represents a table content block.

    Attributes:
        headers: Column header values.
        rows: Data rows (excluding header row).
        content_type: Semantic classification (always 'table').
        importance: Relative importance level for AI processing.
        caption: Optional table caption.
    """

    headers: list[str] = Field(
        default_factory=list,
        description="Column header values"
    )
    rows: list[TableRow] = Field(
        default_factory=list,
        description="Data rows (excluding header)"
    )
    content_type: ContentType = Field(
        default=ContentType.TABLE,
        description="Semantic content type classification"
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Relative importance level for AI processing"
    )
    caption: Optional[str] = Field(
        default=None,
        description="Optional table caption"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility"
    )


class Section(BaseModel):
    """
    Represents a document section with hierarchical content.

    Attributes:
        id: Unique identifier for the section.
        title: Section title/heading.
        level: Heading level (1-6 for markdown headings).
        content_type: Semantic classification (always 'heading').
        content: Paragraph content within this section.
        lists: List content within this section.
        code_blocks: Code blocks within this section.
        tables: Tables within this section.
        children: Nested subsections.
        importance: Relative importance level for AI processing.
        order: Display order among siblings.
    """

    id: str = Field(
        description="Unique identifier for the section"
    )
    title: Optional[str] = Field(
        default=None,
        description="Section title or heading"
    )
    level: int = Field(
        default=1,
        ge=1,
        le=6,
        description="Heading level (1-6)"
    )
    content_type: ContentType = Field(
        default=ContentType.HEADING,
        description="Semantic content type classification"
    )
    paragraphs: list[Paragraph] = Field(
        default_factory=list,
        description="Paragraph content within this section"
    )
    lists: list[List] = Field(
        default_factory=list,
        description="List content within this section"
    )
    code_blocks: list[CodeBlock] = Field(
        default_factory=list,
        description="Code blocks within this section"
    )
    tables: list[Table] = Field(
        default_factory=list,
        description="Tables within this section"
    )
    children: list["Section"] = Field(
        default_factory=list,
        description="Nested child sections"
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Relative importance level for AI processing"
    )
    order: int = Field(
        default=0,
        description="Display order among sibling sections"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility"
    )


class DocumentMetadata(BaseModel):
    """Metadata for the document."""

    title: Optional[str] = Field(
        default=None,
        description="Document title"
    )
    source_path: Optional[str] = Field(
        default=None,
        description="Original file path or URL"
    )
    author: Optional[str] = Field(
        default=None,
        description="Document author"
    )
    version: Optional[str] = Field(
        default=None,
        description="Document version"
    )
    created_at: Optional[str] = Field(
        default=None,
        description="Creation timestamp (ISO 8601)"
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Last update timestamp (ISO 8601)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Document description or summary"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Document tags for categorization"
    )
    language: str = Field(
        default="en",
        description="Primary document language (ISO 639-1)"
    )


class Document(BaseModel):
    """
    Root model representing a structured document for AI consumption.

    This model provides a comprehensive representation of a document
    with semantic tagging, hierarchical structure, and metadata
    that AI agents can reliably parse and understand.

    Attributes:
        version: Schema version for compatibility.
        metadata: Document-level metadata.
        sections: Top-level sections in document order.
        total_paragraphs: Total count of paragraphs.
        total_lists: Total count of lists.
        total_code_blocks: Total count of code blocks.
        total_tables: Total count of tables.
    """

    version: str = Field(
        default="1.0.0",
        description="Schema version for compatibility tracking"
    )
    metadata: DocumentMetadata = Field(
        default_factory=DocumentMetadata,
        description="Document-level metadata"
    )
    sections: list[Section] = Field(
        default_factory=list,
        description="Top-level sections in document order"
    )
    total_paragraphs: int = Field(
        default=0,
        description="Total count of paragraphs"
    )
    total_lists: int = Field(
        default=0,
        description="Total count of lists"
    )
    total_code_blocks: int = Field(
        default=0,
        description="Total count of code blocks"
    )
    total_tables: int = Field(
        default=0,
        description="Total count of tables"
    )

    def model_post_init(self, __context: Any) -> None:
        """Calculate totals after initialization."""
        self.total_paragraphs = self._count_paragraphs()
        self.total_lists = self._count_lists()
        self.total_code_blocks = self._count_code_blocks()
        self.total_tables = self._count_tables()

    def _count_paragraphs(self) -> int:
        """Recursively count all paragraphs."""
        count = 0
        for section in self.sections:
            count += len(section.paragraphs)
            count += self._count_paragraphs_in_children(section)
        return count

    def _count_lists(self) -> int:
        """Recursively count all lists."""
        count = 0
        for section in self.sections:
            count += len(section.lists)
            count += self._count_lists_in_children(section)
        return count

    def _count_code_blocks(self) -> int:
        """Recursively count all code blocks."""
        count = 0
        for section in self.sections:
            count += len(section.code_blocks)
            count += self._count_code_blocks_in_children(section)
        return count

    def _count_tables(self) -> int:
        """Recursively count all tables."""
        count = 0
        for section in self.sections:
            count += len(section.tables)
            count += self._count_tables_in_children(section)
        return count

    def _count_paragraphs_in_children(self, section: Section) -> int:
        """Recursively count paragraphs in child sections."""
        count = 0
        for child in section.children:
            count += len(child.paragraphs)
            count += self._count_paragraphs_in_children(child)
        return count

    def _count_lists_in_children(self, section: Section) -> int:
        """Recursively count lists in child sections."""
        count = 0
        for child in section.children:
            count += len(child.lists)
            count += self._count_lists_in_children(child)
        return count

    def _count_code_blocks_in_children(self, section: Section) -> int:
        """Recursively count code blocks in child sections."""
        count = 0
        for child in section.children:
            count += len(child.code_blocks)
            count += self._count_code_blocks_in_children(child)
        return count

    def _count_tables_in_children(self, section: Section) -> int:
        """Recursively count tables in child sections."""
        count = 0
        for child in section.children:
            count += len(child.tables)
            count += self._count_tables_in_children(child)
        return count
