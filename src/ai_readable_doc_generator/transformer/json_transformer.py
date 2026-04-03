"""JSON transformer for structured output."""

import json
from typing import Any

from ai_readable_doc_generator.document import Document
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class JSONTransformer(BaseTransformer):
    """Transforms documents into structured JSON format."""
    
    def __init__(self, pretty: bool = True, indent: int = 2):
        """Initialize the JSON transformer.
        
        Args:
            pretty: Whether to pretty-print the JSON output.
            indent: Number of spaces for indentation when pretty printing.
        """
        self.pretty = pretty
        self.indent = indent if pretty else None
    
    def transform(self, document: Document) -> str:
        """Transform a document to JSON format.
        
        Args:
            document: The document to transform.
        
        Returns:
            JSON string representation of the document.
        """
        output = self._document_to_dict(document)
        
        if self.pretty:
            return json.dumps(output, indent=self.indent, ensure_ascii=False)
        else:
            return json.dumps(output, ensure_ascii=False)
    
    def _document_to_dict(self, document: Document) -> dict[str, Any]:
        """Convert a document to a dictionary representation.
        
        Args:
            document: The document to convert.
        
        Returns:
            Dictionary representation of the document.
        """
        result = {
            "metadata": self._metadata_to_dict(document.metadata),
            "sections": [self._section_to_dict(section) for section in document.sections],
            "structure": document.get_hierarchy(),
        }
        
        return result
    
    def _metadata_to_dict(self, metadata) -> dict[str, Any]:
        """Convert metadata to a dictionary.
        
        Args:
            metadata: The metadata to convert.
        
        Returns:
            Dictionary representation of the metadata.
        """
        return {
            "title": metadata.title,
            "description": metadata.description,
            "author": metadata.author,
            "version": metadata.version,
            "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
            "updated_at": metadata.updated_at.isoformat() if metadata.updated_at else None,
            "tags": metadata.tags or [],
            "frontmatter": metadata.frontmatter or {},
            "character_count": metadata.character_count,
            "word_count": metadata.word_count,
            "section_count": metadata.section_count,
        }
    
    def _section_to_dict(self, section) -> dict[str, Any]:
        """Convert a section to a dictionary.
        
        Args:
            section: The section to convert.
        
        Returns:
            Dictionary representation of the section.
        """
        result = {
            "id": section.id,
            "title": section.title,
            "type": section.type.value if hasattr(section.type, 'value') else str(section.type),
            "level": section.level,
            "content": section.content,
            "semantic_tags": section.semantic_tags or [],
            "content_type": section.content_type or "text",
            "importance": section.importance or "normal",
        }
        
        if section.children:
            result["children"] = [self._section_to_dict(child) for child in section.children]
        
        return result
    
    def get_content_type(self) -> str:
        """Get the content type of the output.
        
        Returns:
            MIME content type string.
        """
        return "application/json"
