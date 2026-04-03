"""Document processing and conversion utilities."""

from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema, SchemaType
from ai_readable_doc_generator.models.section import Section, SectionType


class DocumentProcessor:
    """Process and convert Document objects to various output formats."""

    def __init__(self, schema: OutputSchema | None = None) -> None:
        """Initialize the document processor.

        Args:
            schema: Output schema configuration.
        """
        self.schema = schema or OutputSchema()

    def to_dict(self, document: Document) -> dict[str, Any]:
        """Convert a Document to a dictionary representation.

        Args:
            document: The document to convert.

        Returns:
            Dictionary representation of the document.
        """
        result: dict[str, Any] = {}

        if self.schema.include_metadata:
            result["metadata"] = {
                "title": document.metadata.title,
                "source_path": document.metadata.source_path,
                "created_at": document.metadata.created_at.isoformat(),
                "language": document.metadata.language,
                "version": document.metadata.version,
                "generator": document.metadata.generator,
            }

        result["title"] = document.title

        if self.schema.semantic_tags:
            result["sections"] = [self._section_to_dict(s) for s in document.sections]
        else:
            result["content"] = self._flatten_content(document.sections)

        if self.schema.include_raw_content and document.raw_content:
            result["raw_content"] = document.raw_content

        if self.schema.schema_type == SchemaType.MCP:
            result["mcp_compatible"] = True
            result["schema_version"] = "1.0"

        return result

    def _section_to_dict(self, section: Section) -> dict[str, Any]:
        """Convert a Section to a dictionary representation.

        Args:
            section: The section to convert.

        Returns:
            Dictionary representation of the section.
        """
        result: dict[str, Any] = {
            "type": section.section_type.value,
            "content": section.content,
        }

        if section.heading_level is not None:
            result["heading_level"] = section.heading_level

        if section.language:
            result["language"] = section.language

        if section.url:
            result["url"] = section.url

        if section.alt_text:
            result["alt_text"] = section.alt_text

        if section.checked is not None:
            result["checked"] = section.checked

        if section.list_start is not None:
            result["list_start"] = section.list_start

        if self.schema.include_importance:
            result["importance"] = section.importance

        if section.metadata:
            result["metadata"] = section.metadata

        if self.schema.include_relationships and section.children:
            result["children"] = [self._section_to_dict(c) for c in section.children]

        return result

    def _flatten_content(self, sections: list[Section]) -> str:
        """Flatten sections into plain text content.

        Args:
            sections: List of sections to flatten.

        Returns:
            Plain text content.
        """
        parts: list[str] = []
        for section in sections:
            if section.content:
                parts.append(section.content)
            if section.children:
                parts.append(self._flatten_content(section.children))
        return "\n\n".join(parts)

    def to_json(self, document: Document, indent: int | None = None) -> str:
        """Convert a Document to JSON string.

        Args:
            document: The document to convert.
            indent: JSON indentation level.

        Returns:
            JSON string representation.
        """
        import json

        indent_value = indent if indent is not None else self.schema.indent
        return json.dumps(self.to_dict(document), indent=indent_value)

    def to_yaml(self, document: Document) -> str:
        """Convert a Document to YAML string.

        Args:
            document: The document to convert.

        Returns:
            YAML string representation.
        """
        try:
            import yaml
        except ImportError:
            try:
                import ruamel.yaml as yaml  # type: ignore
            except ImportError:
                raise ImportError("PyYAML or ruamel.yaml is required for YAML output")

        return yaml.dump(self.to_dict(document), default_flow_style=False)
