"""Pydantic schemas for document validation and structured output.

This module defines the core data models used throughout the ai-readable-doc-generator
for parsing, validating, and transforming documentation into AI-agent-friendly formats.

Schema Hierarchy:
    StructuredDocument
    ├── DocumentMetadata
    ├── DocumentSection[]
    │   ├── SourceLocation
    │   ├── ContentBlock[]
    │   │   ├── ContentType
    │   │   └── SemanticTag[]
    │   └── SemanticTag[]
    └── MCPSchema
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Enums
# =============================================================================


class ContentType(str, Enum):
    """Enumeration of content block types for semantic classification."""

    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    HEADING_4 = "heading_4"
    HEADING_5 = "heading_5"
    HEADING_6 = "heading_6"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    TASK_LIST = "task_list"
    BLOCKQUOTE = "blockquote"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    IMAGE = "image"
    LINK = "link"
    MATH_BLOCK = "math_block"
    MATH_INLINE = "math_inline"
    HTML_BLOCK = "html_block"
    COMMENT = "comment"
    FRONTMATTER = "frontmatter"
    DEFINITION_LIST = "definition_list"
    ADMONITION = "admonition"


class ImportanceLevel(str, Enum):
    """Importance level indicators for content prioritization.

    Used by AI systems to determine which content should be given
    more weight during retrieval and reasoning tasks.
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SemanticRelation(str, Enum):
    """Semantic relationships between document elements.

    Defines how different parts of the document relate to each other,
    enabling AI systems to understand document structure and context.
    """

    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    REFERENCES = "references"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    DEPENDS_ON = "depends_on"
    SEE_ALSO = "see_also"


class CodeLanguage(str, Enum):
    """Common programming languages for code block classification."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    SQL = "sql"
    BASH = "bash"
    SHELL = "shell"
    POWERSHELL = "powershell"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    CSS = "css"
    MARKDOWN = "markdown"
    DOCKERFILE = "dockerfile"
    MAKEFILE = "makefile"
    UNKNOWN = "unknown"


class MCPToolName(str, Enum):
    """Model Context Protocol tool names for MCP-compatible output."""

    DOCUMENT_PARSER = "document_parser"
    SEMANTIC_EXTRACTOR = "semantic_extractor"
    SCHEMA_VALIDATOR = "schema_validator"
    CONTENT_CLASSIFIER = "content_classifier"


# =============================================================================
# Core Data Models
# =============================================================================


class SourceLocation(BaseModel):
    """Represents the source location of a document element.

    Tracks where content originated in the source document for
    traceability and error reporting.

    Attributes:
        line_start: Starting line number (1-indexed).
        line_end: Ending line number (inclusive).
        column_start: Starting column number (1-indexed).
        column_end: Ending column number (inclusive).
        file_path: Path to the source file if applicable.
    """

    line_start: int = Field(ge=1, description="Starting line number (1-indexed)")
    line_end: int = Field(ge=1, description="Ending line number (inclusive)")
    column_start: int = Field(ge=1, description="Starting column number (1-indexed)")
    column_end: int = Field(ge=1, description="Ending column number (inclusive)")
    file_path: Optional[str] = Field(None, description="Path to the source file")

    @field_validator("line_end")
    @classmethod
    def validate_line_end(cls, v: int, info) -> int:
        """Ensure line_end is >= line_start."""
        if "line_start" in info.data and v < info.data["line_start"]:
            raise ValueError("line_end must be >= line_start")
        return v

    @field_validator("column_end")
    @classmethod
    def validate_column_end(cls, v: int, info) -> int:
        """Ensure column_end is >= column_start within the same line."""
        if "column_start" in info.data and v < info.data["column_start"]:
            raise ValueError("column_end must be >= column_start")
        return v


class SemanticTag(BaseModel):
    """Represents a semantic tag for content classification.

    Semantic tags provide machine-readable metadata about content,
    enabling AI systems to understand and categorize document elements.

    Attributes:
        name: The semantic tag identifier (e.g., 'api_reference', 'tutorial').
        value: Optional value for the tag (e.g., 'GET' for HTTP method).
        confidence: Confidence score (0.0-1.0) for the tag classification.
        source: Indicates how the tag was assigned ('automatic', 'manual', 'heuristic').
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Semantic tag identifier",
    )
    value: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional tag value for parameterized tags",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for tag assignment",
    )
    source: str = Field(
        default="heuristic",
        description="Tag assignment source: 'automatic', 'manual', or 'heuristic'",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the semantic tag",
    )


class DocumentMetadata(BaseModel):
    """Metadata about the source document.

    Captures essential information about the document being processed,
    including authorship, versioning, and processing history.

    Attributes:
        title: Document title extracted from frontmatter or first heading.
        description: Document description or abstract.
        author: Document author(s).
        version: Document version string.
        created_at: Document creation timestamp.
        modified_at: Document last modification timestamp.
        source_format: Original document format (e.g., 'markdown', 'html').
        source_path: Path to the source file.
        language: Primary language of the document (ISO 639-1).
        license: Document license identifier.
        tags: List of document-level tags.
        custom_fields: Additional custom metadata fields.
    """

    title: Optional[str] = Field(None, max_length=500, description="Document title")
    description: Optional[str] = Field(None, max_length=2000, description="Document description")
    author: Optional[str] = Field(None, max_length=200, description="Document author")
    version: str = Field(default="1.0.0", max_length=50, description="Document version")
    created_at: Optional[datetime] = Field(None, description="Document creation timestamp")
    modified_at: Optional[datetime] = Field(None, description="Document modification timestamp")
    source_format: str = Field(default="markdown", max_length=50, description="Original format")
    source_path: Optional[str] = Field(None, max_length=1000, description="Source file path")
    language: str = Field(default="en", max_length=10, description="ISO 639-1 language code")
    license: Optional[str] = Field(None, max_length=100, description="License identifier")
    tags: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Document-level classification tags",
    )
    word_count: int = Field(default=0, ge=0, description="Total word count")
    reading_time_minutes: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated reading time in minutes",
    )
    custom_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata fields",
    )


class ContentBlock(BaseModel):
    """Represents a block of content within a document section.

    Content blocks are the fundamental units of content in the structured
    document format, each with its own semantic classification.

    Attributes:
        id: Unique identifier for this content block.
        content_type: Type classification of the content block.
        raw_text: Original raw text content.
        processed_text: Processed/cleaned text content.
        source_location: Source location in the original document.
        semantic_tags: Semantic tags assigned to this content block.
        importance: Importance level for AI prioritization.
        metadata: Additional metadata for the content block.
    """

    id: str = Field(
        ...,
        description="Unique identifier for this content block",
    )
    content_type: ContentType = Field(
        ...,
        description="Type classification of the content block",
    )
    raw_text: str = Field(
        ...,
        description="Original raw text content",
    )
    processed_text: Optional[str] = Field(
        None,
        description="Processed/cleaned text content",
    )
    source_location: Optional[SourceLocation] = Field(
        None,
        description="Source location in original document",
    )
    semantic_tags: list[SemanticTag] = Field(
        default_factory=list,
        max_length=50,
        description="Semantic tags assigned to this content block",
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Importance level for AI prioritization",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (language, URL, etc.)",
    )

    def model_post_init(self, __context: Any) -> None:
        """Set processed_text to raw_text if not provided."""
        if self.processed_text is None:
            self.processed_text = self.raw_text


class ListItem(BaseModel):
    """Represents an item within a list."""

    content: str = Field(..., description="List item text content")
    checked: Optional[bool] = Field(None, description="For task lists: checked state")
    nested_items: list["ListItem"] = Field(
        default_factory=list,
        description="Nested list items",
    )
    semantic_tags: list[SemanticTag] = Field(
        default_factory=list,
        description="Semantic tags for this list item",
    )


class TableCell(BaseModel):
    """Represents a cell in a table."""

    content: str = Field(..., description="Cell text content")
    is_header: bool = Field(default=False, description="Whether this is a header cell")
    column_span: int = Field(default=1, ge=1, description="Column span")
    row_span: int = Field(default=1, ge=1, description="Row span")


class TableRow(BaseModel):
    """Represents a row in a table."""

    cells: list[TableCell] = Field(..., description="Cells in this row")


class DocumentSection(BaseModel):
    """Represents a section of the document.

    Sections form the hierarchical structure of the document,
    containing related content blocks and nested subsections.

    Attributes:
        id: Unique identifier for this section.
        heading: Section heading text.
        heading_level: Heading level (1-6).
        content_blocks: List of content blocks in this section.
        subsections: Nested subsections.
        semantic_tags: Semantic tags for the entire section.
        importance: Section importance level.
        relations: Semantic relationships to other sections.
        metadata: Additional section metadata.
    """

    id: str = Field(..., description="Unique section identifier")
    heading: Optional[str] = Field(None, description="Section heading text")
    heading_level: int = Field(default=1, ge=1, le=6, description="Heading level (1-6)")
    content_blocks: list[ContentBlock] = Field(
        default_factory=list,
        description="Content blocks in this section",
    )
    subsections: list["DocumentSection"] = Field(
        default_factory=list,
        description="Nested subsections",
    )
    semantic_tags: list[SemanticTag] = Field(
        default_factory=list,
        max_length=30,
        description="Semantic tags for this section",
    )
    importance: ImportanceLevel = Field(
        default=ImportanceLevel.MEDIUM,
        description="Section importance level",
    )
    relations: list[dict[str, str]] = Field(
        default_factory=list,
        description="Semantic relationships to other sections",
    )
    source_location: Optional[SourceLocation] = Field(
        None,
        description="Source location of this section",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional section metadata",
    )

    @field_validator("relations")
    @classmethod
    def validate_relations(cls, v: list[dict[str, str]]) -> list[dict[str, str]]:
        """Ensure relations have required keys."""
        for relation in v:
            if "type" not in relation:
                raise ValueError("Each relation must have a 'type' field")
            if "target_id" not in relation:
                raise ValueError("Each relation must have a 'target_id' field")
        return v


class MCPToolResult(BaseModel):
    """Result from an MCP tool execution."""

    tool_name: MCPToolName = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether the tool execution succeeded")
    result: Optional[dict[str, Any]] = Field(None, description="Tool result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata",
    )


class MCPSchema(BaseModel):
    """Model Context Protocol compatible output schema.

    Provides a standardized interface for MCP-capable AI agents to
    interact with parsed document data.

    Attributes:
        version: MCP schema version.
        schema_version: Document schema version.
        generated_at: Timestamp of schema generation.
        parser_version: Version of the parser that generated this schema.
        document: The structured document data.
        extraction_metadata: Metadata about the extraction process.
        tool_results: Results from MCP tool executions.
        validation: Validation results for the schema.
    """

    version: str = Field(
        default="1.0.0",
        description="MCP schema version",
    )
    schema_version: str = Field(
        default="1.0.0",
        description="Document schema version",
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Schema generation timestamp",
    )
    parser_version: str = Field(
        default="0.1.0",
        description="Parser version that generated this schema",
    )
    document: "StructuredDocument" = Field(
        ...,
        description="The structured document data",
    )
    extraction_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the extraction process",
    )
    tool_results: list[MCPToolResult] = Field(
        default_factory=list,
        description="Results from MCP tool executions",
    )
    validation: Optional["ValidationResult"] = Field(
        None,
        description="Schema validation results",
    )


class ValidationError(BaseModel):
    """Represents a single validation error."""

    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of validation error")
    severity: str = Field(default="error", description="Error severity")


class ValidationResult(BaseModel):
    """Result of schema validation."""

    is_valid: bool = Field(..., description="Whether the document is valid")
    errors: list[ValidationError] = Field(
        default_factory=list,
        description="List of validation errors",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings",
    )
    validated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Validation timestamp",
    )

    @property
    def error_count(self) -> int:
        """Return the number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Return the number of warnings."""
        return len(self.warnings)


class StructuredDocument(BaseModel):
    """The main structured document model.

    This is the root model that contains all parsed and enriched
    document data, ready for consumption by AI systems.

    Attributes:
        metadata: Document-level metadata.
        sections: Hierarchical document sections.
        semantic_tags: Document-level semantic tags.
        relations: Cross-references between sections.
        validation: Optional validation results.
        export_format: Target export format.
        custom_data: Additional custom data fields.
    """

    metadata: DocumentMetadata = Field(
        ...,
        description="Document-level metadata",
    )
    sections: list[DocumentSection] = Field(
        ...,
        min_length=1,
        description="Hierarchical document sections",
    )
    semantic_tags: list[SemanticTag] = Field(
        default_factory=list,
        max_length=100,
        description="Document-level semantic tags",
    )
    relations: list[dict[str, str]] = Field(
        default_factory=list,
        description="Cross-references between sections",
    )
    validation: Optional[ValidationResult] = Field(
        None,
        description="Validation results for this document",
    )
    export_format: str = Field(
        default="json",
        description="Target export format",
    )
    custom_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom data fields",
    )

    def get_all_sections(self) -> list[DocumentSection]:
        """Recursively get all sections including nested subsections."""

        def _flatten(sections: list[DocumentSection]) -> list[DocumentSection]:
            result = []
            for section in sections:
                result.append(section)
                if section.subsections:
                    result.extend(_flatten(section.subsections))
            return result

        return _flatten(self.sections)

    def get_section_by_id(self, section_id: str) -> Optional[DocumentSection]:
        """Find a section by its ID."""

        def _search(sections: list[DocumentSection]) -> Optional[DocumentSection]:
            for section in sections:
                if section.id == section_id:
                    return section
                if section.subsections:
                    found = _search(section.subsections)
                    if found:
                        return found
            return None

        return _search(self.sections)

    def get_all_content_blocks(self) -> list[ContentBlock]:
        """Get all content blocks from all sections."""
        blocks = []
        for section in self.get_all_sections():
            blocks.extend(section.content_blocks)
        return blocks

    def search_by_semantic_tag(
        self,
        tag_name: str,
        tag_value: Optional[str] = None,
    ) -> list[tuple[DocumentSection, ContentBlock]]:
        """Search for content blocks with a specific semantic tag."""
        results = []
        for section in self.get_all_sections():
            for block in section.content_blocks:
                for tag in block.semantic_tags:
                    if tag.name == tag_name:
                        if tag_value is None or tag.value == tag_value:
                            results.append((section, block))
        return results

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(**kwargs)

    def to_json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


# =============================================================================
# Forward References Update
# =============================================================================


# Update forward references for self-referential models
ListItem.model_rebuild()
DocumentSection.model_rebuild()
MCPSchema.model_rebuild()
