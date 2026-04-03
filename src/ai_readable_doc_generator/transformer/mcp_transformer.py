"""MCP (Model Context Protocol) transformer for AI agent compatibility."""

import json
from datetime import datetime
from typing import Any

from ai_readable_doc_generator.document import Document
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class MCPTransformer(BaseTransformer):
    """Transforms documents into MCP-compatible JSON format for AI agents."""
    
    def __init__(self, version: str = "1.0"):
        """Initialize the MCP transformer.
        
        Args:
            version: MCP protocol version to use.
        """
        self.version = version
        self._resource_id = 0
    
    def transform(self, document: Document) -> str:
        """Transform a document to MCP-compatible format.
        
        Args:
            document: The document to transform.
        
        Returns:
            MCP-compatible JSON string representation of the document.
        """
        output = self._create_mcp_response(document)
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _create_mcp_response(self, document: Document) -> dict[str, Any]:
        """Create an MCP-compliant response structure.
        
        Args:
            document: The document to transform.
        
        Returns:
            MCP-compliant dictionary structure.
        """
        return {
            "mcp_version": self.version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "resource": {
                "uri": f"file:///{document.metadata.source_path or 'unknown'}",
                "name": document.metadata.title or "Untitled Document",
                "mime_type": "text/markdown",
                "description": document.metadata.description,
            },
            "contents": [
                self._section_to_mcp_content(section, document)
                for section in document.sections
            ],
            "metadata": {
                "title": document.metadata.title,
                "author": document.metadata.author,
                "version": document.metadata.version,
                "tags": document.metadata.tags or [],
                "word_count": document.metadata.word_count,
                "section_count": document.metadata.section_count,
            },
            "context": {
                "hierarchy": document.get_hierarchy(),
                "relationships": self._extract_relationships(document),
            },
        }
    
    def _section_to_mcp_content(self, section, document: Document) -> dict[str, Any]:
        """Convert a section to MCP content format.
        
        Args:
            section: The section to convert.
            document: The parent document for context.
        
        Returns:
            MCP content representation of the section.
        """
        self._resource_id += 1
        
        content = {
            "type": "text",
            "resource_id": f"section_{self._resource_id}",
            "section_id": section.id,
            "title": section.title,
            "level": section.level,
            "section_type": section.type.value if hasattr(section.type, 'value') else str(section.type),
            "content": section.content,
            "semantic_tags": section.semantic_tags or [],
            "content_classification": {
                "type": section.content_type or "text",
                "importance": section.importance or "normal",
            },
            "annotations": {
                "has_code": self._contains_code(section.content),
                "has_lists": self._contains_lists(section.content),
                "has_links": self._contains_links(section.content),
                "has_tables": self._contains_tables(section.content),
            },
        }
        
        if section.children:
            content["children"] = [
                self._section_to_mcp_content(child, document)
                for child in section.children
            ]
        
        return content
    
    def _extract_relationships(self, document: Document) -> list[dict[str, Any]]:
        """Extract relationships between sections.
        
        Args:
            document: The document to analyze.
        
        Returns:
            List of relationship dictionaries.
        """
        relationships = []
        
        for section in document.sections:
            if section.children:
                for child in section.children:
                    relationships.append({
                        "type": "parent_child",
                        "parent_id": section.id,
                        "child_id": child.id,
                        "parent_title": section.title,
                        "child_title": child.title,
                    })
        
        return relationships
    
    def _contains_code(self, content: str) -> bool:
        """Check if content contains code blocks.
        
        Args:
            content: The content to check.
        
        Returns:
            True if content contains code blocks.
        """
        return "```" in content or "`" in content
    
    def _contains_lists(self, content: str) -> bool:
        """Check if content contains lists.
        
        Args:
            content: The content to check.
        
        Returns:
            True if content contains lists.
        """
        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
                return True
            if stripped and stripped[0].isdigit() and ". " in stripped[:5]:
                return True
        return False
    
    def _contains_links(self, content: str) -> bool:
        """Check if content contains links.
        
        Args:
            content: The content to check.
        
        Returns:
            True if content contains links.
        """
        return "[" in content and "](" in content
    
    def _contains_tables(self, content: str) -> bool:
        """Check if content contains tables.
        
        Args:
            content: The content to check.
        
        Returns:
            True if content contains tables.
        """
        lines = content.split("\n")
        table_markers = 0
        for line in lines:
            if "|" in line:
                table_markers += 1
            elif "---" in line and "|" in line:
                table_markers += 1
        return table_markers >= 2
    
    def get_content_type(self) -> str:
        """Get the content type of the output.
        
        Returns:
            MIME content type string.
        """
        return "application/json"
