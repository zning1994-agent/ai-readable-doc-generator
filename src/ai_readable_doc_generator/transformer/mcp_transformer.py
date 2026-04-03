"""MCP (Model Context Protocol) transformer for AI agent integration."""

import json
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class McpTransformer(BaseTransformer):
    """Transforms documents to MCP-compatible format for AI agent integration.

    The Model Context Protocol requires structured, standardized input
    with explicit relationships and semantic context.
    """

    def __init__(
        self,
        schema: OutputSchema | None = None,
        pretty: bool = True,
        indent: int = 2,
    ) -> None:
        """Initialize MCP transformer.

        Args:
            schema: Optional output schema configuration.
            pretty: Whether to pretty-print output.
            indent: Indentation level for pretty printing.
        """
        super().__init__(schema)
        self.pretty = pretty
        self.indent = indent

    def transform(self, document: Document) -> str:
        """Transform document to MCP-compatible format.

        Args:
            document: The document to transform.

        Returns:
            MCP-formatted string representation.
        """
        data = self.transform_to_dict(document)

        if self.pretty:
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform document to MCP-compatible dictionary.

        Args:
            document: The document to transform.

        Returns:
            MCP-structured dictionary representation.
        """
        # Build context structure for AI agents
        result: dict[str, Any] = {
            "mcp_version": "1.0",
            "context": {
                "title": document.title,
                "description": self._generate_description(document),
            },
        }

        # Add relationships for AI understanding
        if self.schema.semantic_tags:
            result["relationships"] = self._build_relationships(document)

        # Add structured sections
        result["sections"] = self._build_structured_sections(document)

        # Add document metadata
        if self.schema.include_metadata:
            result["metadata"] = self._build_metadata(document)

        # Add table of contents
        if self.schema.include_toc:
            result["navigation"] = {
                "table_of_contents": document.get_table_of_contents(),
                "total_sections": len(document.sections),
            }

        return result

    def _generate_description(self, document: Document) -> str:
        """Generate a brief description of the document.

        Args:
            document: Document to describe.

        Returns:
            Brief description string.
        """
        # Extract first paragraph as description
        for section in document.sections:
            if section.section_type.value == "paragraph":
                return section.content[:200] + "..." if len(section.content) > 200 else section.content
        return document.title or "Untitled document"

    def _build_relationships(self, document: Document) -> dict[str, Any]:
        """Build relationship graph for document structure.

        Args:
            document: Document to analyze.

        Returns:
            Relationship structure.
        """
        relationships: dict[str, Any] = {
            "hierarchical": self._build_hierarchy(document),
            "by_type": {},
            "important_sections": [],
        }

        # Group sections by type
        for section in document.sections:
            section_type = section.section_type.value
            if section_type not in relationships["by_type"]:
                relationships["by_type"][section_type] = []
            relationships["by_type"][section_type].append(section.content[:50])

            # Track important sections
            if section.metadata.get("semantic", {}).get("importance") == "high":
                relationships["important_sections"].append({
                    "content": section.content[:100],
                    "reason": section.metadata["semantic"].get("importance_indicator"),
                })

        return relationships

    def _build_hierarchy(self, document: Document) -> list[dict[str, Any]]:
        """Build hierarchical structure of headings.

        Args:
            document: Document to analyze.

        Returns:
            Hierarchical structure as nested list.
        """
        hierarchy: list[dict[str, Any]] = []
        current_level = 0

        for section in document.sections:
            if section.section_type.value in ("title", "heading"):
                hierarchy.append({
                    "level": section.level,
                    "content": section.content,
                    "line_number": section.line_number,
                })
                current_level = section.level

        return hierarchy

    def _build_structured_sections(self, document: Document) -> list[dict[str, Any]]:
        """Build structured sections with full semantic context.

        Args:
            document: Document to structure.

        Returns:
            List of structured section dictionaries.
        """
        structured = []

        for section in document.sections:
            section_data: dict[str, Any] = {
                "id": f"section_{section.line_number}",
                "content": section.content,
                "type": section.section_type.value,
                "context": {
                    "level": section.level,
                    "line_number": section.line_number,
                },
            }

            # Add semantic context if available
            if "semantic" in section.metadata:
                section_data["semantic"] = section.metadata["semantic"]

            structured.append(section_data)

        return structured

    def _build_metadata(self, document: Document) -> dict[str, Any]:
        """Build document metadata.

        Args:
            document: Document to extract metadata from.

        Returns:
            Metadata dictionary.
        """
        return {
            **document.metadata,
            "source_format": document.source_format,
            "source_path": document.source_path,
        }
