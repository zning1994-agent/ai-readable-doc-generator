"""JSON transformer for structured document output."""

import json
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema, SchemaType
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class JSONTransformer(BaseTransformer):
    """Transformer that converts documents to JSON format.

    Supports configurable output schemas with various levels of detail,
    including semantic tagging, metadata, and importance levels.

    Example:
        >>> from ai_readable_doc_generator import Document, Section, ContentType
        >>> from ai_readable_doc_generator.transformer import JSONTransformer
        >>> doc = Document(title="Test", sections=[
        ...     Section("Hello World", content_type=ContentType.PARAGRAPH)
        ... ])
        >>> transformer = JSONTransformer()
        >>> json_output = transformer.transform(doc)
        >>> print(json_output)
    """

    def __init__(
        self,
        schema: OutputSchema | None = None,
        validate_output: bool = True,
        pretty: bool = True,
        indent: int = 2,
    ) -> None:
        """Initialize the JSON transformer.

        Args:
            schema: Output schema configuration.
            validate_output: Whether to validate transformed output.
            pretty: Whether to pretty-print the JSON output.
            indent: Number of spaces for indentation.
        """
        super().__init__(schema=schema, validate_output=validate_output)
        self.pretty = pretty
        self.indent = indent

    def transform(self, document: Document) -> str:
        """Transform a document to JSON format.

        Args:
            document: The document to transform.

        Returns:
            JSON string representation of the document.

        Raises:
            ValueError: If document validation fails.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        data = self._transform_document(document)
        data = self._apply_schema_options(data)

        if self.pretty:
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def _transform_document(self, document: Document) -> dict[str, Any]:
        """Transform a document into a dictionary.

        Args:
            document: The document to transform.

        Returns:
            Dictionary representation of the document.
        """
        result: dict[str, Any] = {
            "title": document.title,
            "sections": [self._transform_section(s) for s in document.sections],
            "source_format": document.source_format,
            "language": document.language,
        }

        if document.metadata:
            result["metadata"] = document.metadata

        if document.source_path:
            result["source_path"] = document.source_path

        if document.tags:
            result["tags"] = document.tags

        # Include timestamps
        result["created_at"] = document.created_at.isoformat()
        result["updated_at"] = document.updated_at.isoformat()

        return result

    def _transform_section(self, section: Any) -> dict[str, Any]:
        """Transform a section into a dictionary.

        Args:
            section: The section to transform.

        Returns:
            Dictionary representation of the section.
        """
        result: dict[str, Any] = {
            "id": section.id,
            "content": section.content,
            "content_type": section.content_type.value,
            "level": section.level,
        }

        if section.children:
            result["children"] = [self._transform_section(child) for child in section.children]

        if section.metadata:
            result["metadata"] = section.metadata

        if section.importance != 3:  # Only include if non-default
            result["importance"] = section.importance

        if section.tags:
            result["tags"] = section.tags

        return result

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform a document to a dictionary (without JSON serialization).

        Args:
            document: The document to transform.

        Returns:
            Dictionary representation of the document.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        data = self._transform_document(document)
        return self._apply_schema_options(data)

    def parse(self, json_str: str) -> Document:
        """Parse a JSON string back into a Document.

        Args:
            json_str: JSON string to parse.

        Returns:
            Document reconstructed from JSON.

        Raises:
            ValueError: If JSON parsing fails.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        return self._parse_document(data)

    def _parse_document(self, data: dict[str, Any]) -> Document:
        """Parse a dictionary into a Document.

        Args:
            data: Dictionary to parse.

        Returns:
            Reconstructed Document.
        """
        from datetime import datetime

        sections = [self._parse_section(s) for s in data.get("sections", [])]

        doc = Document(
            title=data.get("title", ""),
            sections=sections,
            metadata=data.get("metadata", {}),
            source_path=data.get("source_path"),
            source_format=data.get("source_format", "markdown"),
            tags=data.get("tags", []),
            language=data.get("language", "en"),
        )

        if created_at := data.get("created_at"):
            doc.created_at = datetime.fromisoformat(created_at)
        if updated_at := data.get("updated_at"):
            doc.updated_at = datetime.fromisoformat(updated_at)

        return doc

    def _parse_section(self, data: dict[str, Any]) -> Any:
        """Parse a dictionary into a Section.

        Args:
            data: Dictionary to parse.

        Returns:
            Reconstructed Section.
        """
        from ai_readable_doc_generator.models.section import ContentType, Section

        children = [self._parse_section(c) for c in data.get("children", [])]

        return Section(
            id=data.get("id"),
            content=data.get("content", ""),
            content_type=ContentType(data.get("content_type", "paragraph")),
            level=data.get("level", 1),
            importance=data.get("importance", 3),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            children=children,
        )

    def __repr__(self) -> str:
        """Return string representation of JSON transformer."""
        return f"JSONTransformer(pretty={self.pretty}, schema={self.schema.schema_type.value})"
