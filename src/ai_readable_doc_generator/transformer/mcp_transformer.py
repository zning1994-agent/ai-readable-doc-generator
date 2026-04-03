"""MCP (Model Context Protocol) transformer for AI agent compatible output.

This transformer converts documents into MCP-compatible structured formats
that AI agents can reliably parse and understand.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class ContentType(str, Enum):
    """Semantic content type markers for document sections."""

    INTRODUCTION = "introduction"
    API_REFERENCE = "api_reference"
    TUTORIAL = "tutorial"
    EXAMPLE = "example"
    CODE = "code"
    CONFIGURATION = "configuration"
    TROUBLESHOOTING = "troubleshooting"
    CHANGELOG = "changelog"
    GLOSSARY = "glossary"
    FAQ = "faq"
    WARNING = "warning"
    NOTE = "note"
    DEPRECATION = "deprecation"
    GENERAL = "general"


class ImportanceLevel(str, Enum):
    """Importance level indicators for content sections."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OutputFormat(str, Enum):
    """Supported MCP output formats."""

    MCP_CONTEXT = "mcp_context"
    MCP_RESOURCE = "mcp_resource"
    MCP_TOOL_SCHEMA = "mcp_tool_schema"
    COMPLETE_CONTEXT = "complete_context"


@dataclass
class MCPSection:
    """Represents a semantically tagged section for MCP output."""

    id: str
    title: str
    content_type: ContentType
    content: str
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert section to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type.value,
            "content": self.content,
            "importance": self.importance.value,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "metadata": self.metadata,
            "tags": self.tags,
        }


@dataclass
class MCPContext:
    """MCP context structure for AI agent consumption."""

    version: str = "1.0"
    document_id: str = ""
    title: str = ""
    description: str = ""
    created_at: str = ""
    sections: list[MCPSection] = field(default_factory=list)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert MCP context to dictionary format."""
        return {
            "version": self.version,
            "document_id": self.document_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "sections": [s.to_dict() for s in self.sections],
            "relationships": self.relationships,
            "metadata": self.metadata,
        }


class MCPTransformer(BaseTransformer):
    """Transformer that converts documents to MCP (Model Context Protocol) format.

    MCP is a protocol designed for AI agent context management. This transformer
    produces structured, semantically tagged output that AI agents can reliably
    parse and understand.

    Features:
    - Structured context generation with explicit hierarchy
    - Semantic content type tagging
    - Relationship mapping between sections
    - Configurable output formats (context, resource, tool schema)
    - Importance level indicators
    - Custom metadata support
    """

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        """Initialize MCP transformer.

        Args:
            options: Optional configuration with keys:
                - output_format: Output format type (default: MCP_CONTEXT)
                - pretty: Enable pretty printing (default: True)
                - indent: Indentation level (default: 2)
                - include_relationships: Include section relationships (default: True)
                - include_metadata: Include document metadata (default: True)
                - semantic_tagging: Enable automatic semantic tagging (default: True)
                - importance_detection: Enable importance detection (default: True)
        """
        super().__init__(options)
        self.output_format = OutputFormat(
            self.options.get("output_format", "mcp_context")
        )
        self.pretty = self.options.get("pretty", True)
        self.indent = self.options.get("indent", 2)
        self.include_relationships = self.options.get("include_relationships", True)
        self.include_metadata = self.options.get("include_metadata", True)
        self.semantic_tagging = self.options.get("semantic_tagging", True)
        self.importance_detection = self.options.get("importance_detection", True)

    def transform(self, document: Any) -> str:
        """Transform a document to MCP-compatible format.

        Args:
            document: Document object with to_dict() method or dict structure.
                     Expected structure includes: title, description, sections.

        Returns:
            JSON string in MCP-compatible format.
        """
        if hasattr(document, "to_dict"):
            doc_data = document.to_dict()
        elif isinstance(document, dict):
            doc_data = document
        else:
            doc_data = self._document_to_dict(document)

        mcp_context = self._build_mcp_context(doc_data)

        if self.output_format == OutputFormat.MCP_RESOURCE:
            return self._format_as_resource(mcp_context)
        elif self.output_format == OutputFormat.MCP_TOOL_SCHEMA:
            return self._format_as_tool_schema(mcp_context)
        else:
            return self._format_as_context(mcp_context)

    def _document_to_dict(self, document: Any) -> dict[str, Any]:
        """Convert arbitrary document to dictionary format."""
        if hasattr(document, "__dict__"):
            return vars(document)
        return {"content": str(document)}

    def _build_mcp_context(self, doc_data: dict[str, Any]) -> MCPContext:
        """Build MCP context from document data."""
        context = MCPContext(
            version="1.0",
            document_id=doc_data.get("id", doc_data.get("document_id", "")),
            title=doc_data.get("title", ""),
            description=doc_data.get("description", ""),
            created_at=datetime.now().isoformat(),
        )

        sections = self._extract_sections(doc_data)
        context.sections = sections

        if self.include_relationships:
            context.relationships = self._build_relationships(sections)

        if self.include_metadata:
            context.metadata = self._extract_metadata(doc_data)

        return context

    def _extract_sections(self, doc_data: dict[str, Any]) -> list[MCPSection]:
        """Extract and tag sections from document data."""
        sections = []
        raw_sections = doc_data.get("sections", [])

        if isinstance(raw_sections, list):
            for i, raw_section in enumerate(raw_sections):
                section = self._process_section(raw_section, i)
                sections.append(section)

        return sections

    def _process_section(
        self, raw_section: dict[str, Any], index: int
    ) -> MCPSection:
        """Process a raw section into an MCP section with semantic tagging."""
        section_id = raw_section.get("id", f"section_{index}")
        title = raw_section.get("title", raw_section.get("name", f"Section {index}"))
        content = raw_section.get("content", raw_section.get("text", ""))

        if self.semantic_tagging:
            content_type = self._detect_content_type(title, content)
            tags = self._extract_tags(title, content)
        else:
            content_type = ContentType(raw_section.get("type", "general"))
            tags = raw_section.get("tags", [])

        if self.importance_detection:
            importance = self._detect_importance(title, content, content_type)
        else:
            importance = ImportanceLevel(raw_section.get("importance", "medium"))

        return MCPSection(
            id=section_id,
            title=title,
            content_type=content_type,
            content=content,
            importance=importance,
            parent_id=raw_section.get("parent_id"),
            children_ids=raw_section.get("children_ids", []),
            metadata=raw_section.get("metadata", {}),
            tags=tags,
        )

    def _detect_content_type(self, title: str, content: str) -> ContentType:
        """Detect semantic content type from title and content."""
        title_lower = title.lower()
        content_lower = content.lower()

        # Check title keywords first
        if any(k in title_lower for k in ["introduction", "overview", "about"]):
            return ContentType.INTRODUCTION
        if any(k in title_lower for k in ["api", "reference", "endpoint", "method"]):
            return ContentType.API_REFERENCE
        if any(k in title_lower for k in ["tutorial", "guide", "how to", "getting started"]):
            return ContentType.TUTORIAL
        if any(k in title_lower for k in ["example", "sample", "demo"]):
            return ContentType.EXAMPLE
        if any(k in title_lower for k in ["config", "configuration", "settings"]):
            return ContentType.CONFIGURATION
        if any(k in title_lower for k in ["troubleshoot", "debug", "error", "issue", "problem"]):
            return ContentType.TROUBLESHOOTING
        if any(k in title_lower for k in ["changelog", "changes", "history", "version"]):
            return ContentType.CHANGELOG
        if any(k in title_lower for k in ["glossary", "terms", "definitions"]):
            return ContentType.GLOSSARY
        if any(k in title_lower for k in ["faq", "question", "q&a"]):
            return ContentType.FAQ
        if any(k in title_lower for k in ["warning", "caution", "alert"]):
            return ContentType.WARNING
        if any(k in title_lower for k in ["note", "tip", "hint"]):
            return ContentType.NOTE
        if any(k in title_lower for k in ["deprecat", "deprecated"]):
            return ContentType.DEPRECATION

        # Check content patterns
        if "```" in content or "def " in content or "class " in content:
            return ContentType.CODE
        if any(k in content_lower for k in ["warning:", "caution:", "important:"]):
            return ContentType.WARNING

        return ContentType.GENERAL

    def _detect_importance(
        self, title: str, content: str, content_type: ContentType
    ) -> ImportanceLevel:
        """Detect importance level of content."""
        title_lower = title.lower()
        content_lower = content.lower()

        # High importance markers
        high_markers = ["critical", "important", "warning", "security", "breaking"]
        if any(m in title_lower for m in high_markers):
            return ImportanceLevel.HIGH

        # Critical markers
        critical_markers = ["security", "vulnerability", "breaking change", "urgent"]
        if any(m in title_lower for m in critical_markers):
            return ImportanceLevel.CRITICAL

        # Content type based importance
        critical_types = [
            ContentType.WARNING,
            ContentType.DEPRECATION,
        ]
        if content_type in critical_types:
            return ImportanceLevel.HIGH

        # Low importance markers
        low_markers = ["example", "sample", "see also", "related", "appendix"]
        if any(m in title_lower for m in low_markers):
            return ImportanceLevel.LOW

        return ImportanceLevel.MEDIUM

    def _extract_tags(self, title: str, content: str) -> list[str]:
        """Extract semantic tags from title and content."""
        tags = set()
        title_lower = title.lower()
        content_lower = content.lower()

        # Extract language/code indicators
        if "python" in content_lower:
            tags.add("python")
        if "javascript" in content_lower or "js" in content_lower:
            tags.add("javascript")
        if "typescript" in content_lower or "ts" in content_lower:
            tags.add("typescript")
        if "json" in content_lower:
            tags.add("json")
        if "yaml" in content_lower or "yml" in content_lower:
            tags.add("yaml")
        if "markdown" in content_lower or "md" in title_lower:
            tags.add("markdown")

        # Extract feature indicators
        feature_keywords = {
            "authentication": "auth",
            "authorization": "authz",
            "configuration": "config",
            "installation": "setup",
            "deployment": "deploy",
            "troubleshooting": "debug",
        }
        for keyword, tag in feature_keywords.items():
            if keyword in content_lower:
                tags.add(tag)

        return list(tags)

    def _build_relationships(
        self, sections: list[MCPSection]
    ) -> dict[str, list[str]]:
        """Build relationship map between sections."""
        relationships: dict[str, list[str]] = {}

        # Build parent-child relationships
        for section in sections:
            relationships[section.id] = {
                "parent": [section.parent_id] if section.parent_id else [],
                "children": section.children_ids,
            }

        # Build content-type-based relationships
        sections_by_type: dict[ContentType, list[str]] = {}
        for section in sections:
            if section.content_type not in sections_by_type:
                sections_by_type[section.content_type] = []
            sections_by_type[section.content_type].append(section.id)

        relationships["by_content_type"] = {
            ct.value: ids for ct, ids in sections_by_type.items()
        }

        return relationships

    def _extract_metadata(self, doc_data: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from document."""
        metadata: dict[str, Any] = {}

        # Copy standard metadata fields
        standard_fields = [
            "author",
            "version",
            "license",
            "tags",
            "category",
            "language",
        ]
        for field in standard_fields:
            if field in doc_data:
                metadata[field] = doc_data[field]

        # Add computed metadata
        if "sections" in doc_data and isinstance(doc_data["sections"], list):
            metadata["section_count"] = len(doc_data["sections"])
            metadata["content_types"] = list(
                set(
                    s.get("type", "general")
                    for s in doc_data["sections"]
                    if isinstance(s, dict)
                )
            )

        return metadata

    def _format_as_context(self, context: MCPContext) -> str:
        """Format MCP context as standard context output."""
        data = context.to_dict()

        if self.pretty:
            return json.dumps(data, indent=self.indent, default=str)
        return json.dumps(data, default=str)

    def _format_as_resource(self, context: MCPContext) -> str:
        """Format MCP context as MCP resource format."""
        resource = {
            "resource": {
                "uri": f"doc://{context.document_id}",
                "name": context.title,
                "description": context.description,
                "mimeType": "application/json",
                "createdAt": context.created_at,
            },
            "contents": [
                {
                    "uri": f"doc://{context.document_id}/sections/{section.id}",
                    "mimeType": "application/json",
                    "blob": json.dumps(section.to_dict(), default=str),
                }
                for section in context.sections
            ],
        }

        if self.pretty:
            return json.dumps(resource, indent=self.indent, default=str)
        return json.dumps(resource, default=str)

    def _format_as_tool_schema(self, context: MCPContext) -> str:
        """Format MCP context as tool schema for AI agent tools."""
        tool_schema = {
            "name": f"read_document_{context.document_id}",
            "description": context.description or f"Read document: {context.title}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "section_id": {
                        "type": "string",
                        "description": "Optional section ID to read specific section",
                        "enum": [s.id for s in context.sections],
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Filter sections by content type",
                        "enum": [ct.value for ct in ContentType],
                    },
                    "importance": {
                        "type": "string",
                        "description": "Filter sections by importance level",
                        "enum": [il.value for il in ImportanceLevel],
                    },
                },
            },
            "available_sections": [s.to_dict() for s in context.sections],
            "document_metadata": context.metadata,
        }

        if self.pretty:
            return json.dumps(tool_schema, indent=self.indent, default=str)
        return json.dumps(tool_schema, default=str)

    def validate(self, document: Any) -> bool:
        """Validate that a document can be transformed to MCP format.

        Args:
            document: Document to validate.

        Returns:
            True if document is valid, False otherwise.
        """
        if document is None:
            return False

        if hasattr(document, "to_dict"):
            doc_data = document.to_dict()
        elif isinstance(document, dict):
            doc_data = document
        else:
            return False

        # Check for required fields
        return "title" in doc_data or "sections" in doc_data or "content" in doc_data

    def get_available_content_types(self) -> list[str]:
        """Get list of available content type values.

        Returns:
            List of content type enum values.
        """
        return [ct.value for ct in ContentType]

    def get_available_importance_levels(self) -> list[str]:
        """Get list of available importance level values.

        Returns:
            List of importance level enum values.
        """
        return [il.value for il in ImportanceLevel]
