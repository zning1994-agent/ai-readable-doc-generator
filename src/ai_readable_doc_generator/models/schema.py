"""Schema definitions for semantic document representation.

This module defines the data models used to represent documents with
semantic tagging for AI consumption.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of content that can be identified in documents."""

    TEXT = "text"
    HEADING = "heading"
    CODE = "code"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    LINK = "link"
    IMAGE = "image"
    HORIZONTAL_RULE = "horizontal_rule"
    EMPHASIS = "emphasis"
    STRONG = "strong"
    INLINE_CODE = "inline_code"
    HTML = "html"


class HeadingLevel(str, Enum):
    """Heading hierarchy levels."""

    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"


class RelationshipType(str, Enum):
    """Types of relationships between document elements."""

    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    REFERENCE = "reference"
    DEFINITION = "definition"
    SEQUENTIAL = "sequential"


class DocumentMetadata(BaseModel):
    """Metadata about the source document."""

    source_path: Optional[str] = Field(default=None, description="Path to source file")
    source_format: str = Field(default="markdown", description="Source document format")
    title: Optional[str] = Field(default=None, description="Document title (usually from H1)")
    description: Optional[str] = Field(default=None, description="Document description/summary")
    author: Optional[str] = Field(default=None, description="Document author")
    version: Optional[str] = Field(default=None, description="Document version")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    word_count: int = Field(default=0, description="Total word count")
    reading_time_minutes: Optional[float] = Field(default=None, description="Estimated reading time")
    tags: list[str] = Field(default_factory=list, description="Document-level tags")
    custom: dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")


class SemanticBlock(BaseModel):
    """A semantic block representing a piece of content."""

    id: str = Field(description="Unique identifier for this block")
    content_type: ContentType = Field(description="Type of content")
    content: str = Field(description="The actual text content")
    raw_content: Optional[str] = Field(default=None, description="Raw content before processing")
    language: Optional[str] = Field(default=None, description="Programming language for code blocks")
    url: Optional[str] = Field(default=None, description="URL for links/images")
    alt_text: Optional[str] = Field(default=None, description="Alternative text for images")
    level: Optional[HeadingLevel] = Field(default=None, description="Heading level")
    line_number: int = Field(default=0, description="Line number in source")
    semantic_tags: list[str] = Field(default_factory=list, description="Semantic classification tags")
    importance: str = Field(default="normal", description="Importance level: low, normal, high, critical")
    relationships: list[dict[str, Any]] = Field(default_factory=list, description="Relationships to other blocks")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional block metadata")

    class Config:
        use_enum_values = True


class SemanticSection(BaseModel):
    """A semantic section grouping related blocks."""

    id: str = Field(description="Unique identifier for this section")
    title: Optional[str] = Field(default=None, description="Section title (from heading)")
    level: HeadingLevel = Field(default=HeadingLevel.H2, description="Section depth level")
    content_type: ContentType = Field(default=ContentType.HEADING, description="Primary content type")
    blocks: list[SemanticBlock] = Field(default_factory=list, description="Content blocks in this section")
    section_type: Optional[str] = Field(default=None, description="Semantic section type (e.g., introduction, conclusion)")
    importance: str = Field(default="normal", description="Section importance level")
    child_sections: list["SemanticSection"] = Field(default_factory=list, description="Nested sections")
    line_number: int = Field(default=0, description="Starting line number in source")
    word_count: int = Field(default=0, description="Word count in this section")
    relationships: list[dict[str, Any]] = Field(default_factory=list, description="Relationships to other sections")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional section metadata")

    class Config:
        use_enum_values = True


class SemanticDocument(BaseModel):
    """Complete semantic representation of a document."""

    version: str = Field(default="1.0", description="Schema version")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="Document metadata")
    sections: list[SemanticSection] = Field(default_factory=list, description="Top-level sections")
    all_blocks: list[SemanticBlock] = Field(default_factory=list, description="Flat list of all content blocks")
    table_of_contents: list[dict[str, Any]] = Field(default_factory=list, description="Generated table of contents")
    statistics: dict[str, Any] = Field(default_factory=dict, description="Document statistics")
    semantic_summary: Optional[dict[str, Any]] = Field(default=None, description="AI-friendly summary of document")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(mode="json")

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(mode="json", **kwargs)
