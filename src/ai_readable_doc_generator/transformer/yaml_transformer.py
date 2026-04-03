"""YAML transformer for structured document output."""

from typing import Any

import yaml

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class YAMLTransformer(BaseTransformer):
    """Transformer that converts documents to YAML format.

    Supports configurable output schemas with various levels of detail,
    including semantic tagging, metadata, and importance levels.

    Example:
        >>> from ai_readable_doc_generator import Document, Section, ContentType
        >>> from ai_readable_doc_generator.transformer import YAMLTransformer
        >>> doc = Document(title="Test", sections=[
        ...     Section("Hello World", content_type=ContentType.PARAGRAPH)
        ... ])
        >>> transformer = YAMLTransformer()
        >>> yaml_output = transformer.transform(doc)
        >>> print(yaml_output)
    """

    def __init__(
        self,
        schema: Any | None = None,
        validate_output: bool = True,
        pretty: bool = True,
        default_flow_style: bool = False,
    ) -> None:
        """Initialize the YAML transformer.

        Args:
            schema: Output schema configuration.
            validate_output: Whether to validate transformed output.
            pretty: Whether to produce pretty-printed YAML output.
            default_flow_style: Whether to use flow style for sequences.
        """
        super().__init__(schema=schema, validate_output=validate_output)
        self.pretty = pretty
        self.default_flow_style = default_flow_style

    def transform(self, document: Document) -> str:
        """Transform a document to YAML format.

        Args:
            document: The document to transform.

        Returns:
            YAML string representation of the document.

        Raises:
            ValueError: If document validation fails.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        data = self._transform_document(document)
        data = self._apply_schema_options(data)

        return yaml.dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=self.default_flow_style if not self.pretty else False,
        )

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
            "source_format": "markdown",
            "language": document.metadata.language if document.metadata else "en",
        }

        if document.metadata:
            result["metadata"] = document.metadata.to_dict()

        if document.source_path:
            result["source_path"] = document.source_path

        if document.semantic_tags:
            result["tags"] = [t.name for t in document.semantic_tags]

        # Include timestamps if available
        if document.metadata and document.metadata.created_at:
            result["created_at"] = document.metadata.created_at
        if document.metadata and document.metadata.updated_at:
            result["updated_at"] = document.metadata.updated_at

        return result

    def _transform_section(self, section: Any) -> dict[str, Any]:
        """Transform a section into a dictionary.

        Args:
            section: The section to transform.

        Returns:
            Dictionary representation of the section.
        """
        # Generate id from heading or content
        section_id = section.heading or (section.content[:30] if section.content else "section")
        section_id = section_id.lower().replace(" ", "-")[:50]
        
        result: dict[str, Any] = {
            "id": section_id,
            "content": section.content or section.heading or "",
            "section_type": section.section_type.value,
            "level": section.level,
        }
        
        if section.heading:
            result["heading"] = section.heading

        if section.children:
            result["children"] = [self._transform_section(child) for child in section.children]

        if section.metadata:
            result["metadata"] = section.metadata
            
        if section.semantic_tags:
            result["semantic_tags"] = [t.name for t in section.semantic_tags]

        return result

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform a document to a dictionary (without YAML serialization).

        Args:
            document: The document to transform.

        Returns:
            Dictionary representation of the document.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        data = self._transform_document(document)
        return self._apply_schema_options(data)

    def parse(self, yaml_str: str) -> Document:
        """Parse a YAML string back into a Document.

        Args:
            yaml_str: YAML string to parse.

        Returns:
            Document reconstructed from YAML.

        Raises:
            ValueError: If YAML parsing fails.
        """
        try:
            data = yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}") from e

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
        """Return string representation of YAML transformer."""
        return f"YAMLTransformer(pretty={self.pretty}, schema={self.schema.schema_type.value})"
