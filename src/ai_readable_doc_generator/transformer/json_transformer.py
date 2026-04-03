"""JSON transformer for structured JSON output."""

import json
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class JsonTransformer(BaseTransformer):
    """Transforms documents to JSON format with configurable schema.

    Supports both compact and pretty-printed JSON output with
    semantic tagging integration.
    """

    def __init__(
        self,
        schema: OutputSchema | None = None,
        pretty: bool = True,
        indent: int = 2,
    ) -> None:
        """Initialize JSON transformer.

        Args:
            schema: Optional output schema configuration.
            pretty: Whether to pretty-print JSON output.
            indent: Indentation level for pretty printing.
        """
        super().__init__(schema)
        self.pretty = pretty
        self.indent = indent

    def transform(self, document: Document) -> str:
        """Transform document to JSON string.

        Args:
            document: The document to transform.

        Returns:
            JSON string representation of the document.
        """
        data = self.transform_to_dict(document)

        if self.pretty:
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform document to dictionary for JSON conversion.

        Args:
            document: The document to transform.

        Returns:
            Dictionary representation of the document.
        """
        result: dict[str, Any] = {
            "title": document.title,
            "source_format": document.source_format,
        }

        # Include metadata if configured
        if self.schema.include_metadata:
            result["metadata"] = document.metadata

        # Include table of contents if configured
        if self.schema.include_toc:
            result["table_of_contents"] = document.get_table_of_contents()

        # Include semantic tags if configured
        if self.schema.semantic_tags:
            result["sections"] = [
                self._section_to_dict(section) for section in document.sections
            ]
        else:
            # Simple section list without semantic tags
            result["sections"] = [
                {"content": section.content, "type": section.section_type.value}
                for section in document.sections
            ]

        # Apply custom schema fields
        if self.schema.fields:
            result = self._apply_schema_fields(result, document)

        return result

    def _section_to_dict(self, section) -> dict[str, Any]:
        """Convert section to dictionary with semantic tags.

        Args:
            section: Section to convert.

        Returns:
            Dictionary representation of section.
        """
        result: dict[str, Any] = {
            "content": section.content,
            "type": section.section_type.value,
            "level": section.level,
        }

        # Include semantic metadata if available
        if "semantic" in section.metadata:
            result["semantic"] = section.metadata["semantic"]

        # Include children if any
        if section.children:
            result["children"] = [
                self._section_to_dict(child) for child in section.children
            ]

        return result
