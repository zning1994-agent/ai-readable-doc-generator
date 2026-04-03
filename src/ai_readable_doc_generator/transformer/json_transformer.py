"""JSON Transformer for structured JSON output."""

import json
from datetime import datetime
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema, SchemaVersion
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class JSONTransformer(BaseTransformer):
    """Transforms documents into structured JSON format.

    This transformer converts Document objects into JSON with configurable
    schema support, including semantic tagging and MCP-compatible output.

    Attributes:
        schema: Output schema configuration.
        indent: JSON indentation level.
        sort_keys: Whether to sort dictionary keys in output.
    """

    def __init__(
        self,
        schema: OutputSchema | None = None,
        indent: int | None = None,
        sort_keys: bool | None = None,
        include_metadata: bool | None = None,
        include_semantic_tags: bool | None = None,
        include_summary: bool | None = None,
    ) -> None:
        """Initialize the JSON transformer.

        Args:
            schema: Output schema configuration. Uses default if not provided.
            indent: JSON indentation level. Overrides schema setting if provided.
            sort_keys: Whether to sort dictionary keys. Overrides schema if provided.
            include_metadata: Include metadata in output. Overrides schema if provided.
            include_semantic_tags: Include semantic tags. Overrides schema if provided.
            include_summary: Include summary in output. Overrides schema if provided.
        """
        super().__init__(schema)

        # Allow runtime overrides of schema settings
        self.indent = indent if indent is not None else self.schema.indent
        self.sort_keys = sort_keys if sort_keys is not None else self.schema.sort_keys
        self.include_metadata = (
            include_metadata if include_metadata is not None else self.schema.include_metadata
        )
        self.include_semantic_tags = (
            include_semantic_tags if include_semantic_tags is not None else self.schema.include_semantic_tags
        )
        self.include_summary = (
            include_summary if include_summary is not None else self.schema.include_summary
        )

    def validate(self, document: Document) -> bool:
        """Validate a document before transformation.

        Args:
            document: The document to validate.

        Returns:
            True if the document is valid, False otherwise.
        """
        if not document:
            return False
        if not isinstance(document, Document):
            return False
        # Document must have at least a title or content
        if not document.title and not document.content and not document.sections:
            return False
        return True

    def transform(self, document: Document) -> str:
        """Transform a document to JSON string.

        Args:
            document: The document to transform.

        Returns:
            JSON string representation of the document.

        Raises:
            ValueError: If the document is invalid.
        """
        if not self.validate(document):
            raise ValueError("Invalid document: must have title, content, or sections")

        document = self.pre_transform(document)
        result = self._build_output(document)
        result = self.post_transform(result)

        return json.dumps(result, indent=self.indent, sort_keys=self.sort_keys, ensure_ascii=False)

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform a document to dictionary.

        Args:
            document: The document to transform.

        Returns:
            Dictionary representation of the document.

        Raises:
            ValueError: If the document is invalid.
        """
        if not self.validate(document):
            raise ValueError("Invalid document: must have title, content, or sections")

        document = self.pre_transform(document)
        result = self._build_output(document)
        return self.post_transform(result)

    def _build_output(self, document: Document) -> dict[str, Any]:
        """Build the output dictionary from a document.

        Args:
            document: The document to convert.

        Returns:
            Dictionary representation suitable for JSON output.
        """
        output: dict[str, Any] = {
            "_format": "ai-readable-document",
            "_version": self.schema.version.value,
            "_generated_at": datetime.now().isoformat(),
        }

        # Add document ID for MCP compatibility
        if self.schema.version == SchemaVersion.V2:
            output["document_id"] = document.id

        # Add title and content
        if document.title:
            output["title"] = document.title
        if document.content:
            output["content"] = document.content

        # Add sections
        if document.sections:
            output["sections"] = self._transform_sections(document.sections)

        # Add metadata
        if self.include_metadata and document.metadata:
            output["metadata"] = self._transform_metadata(document.metadata)

        # Add semantic tags
        if self.include_semantic_tags:
            if document.semantic_tags:
                output["semantic_tags"] = document.semantic_tags
            # Also include semantic tags from sections
            section_tags = self._extract_section_tags(document.sections)
            if section_tags:
                if "semantic_tags" not in output:
                    output["semantic_tags"] = {}
                output["semantic_tags"]["section_tags"] = section_tags

        # Add relationships
        if document.relationships:
            output["relationships"] = [
                rel.to_dict() for rel in document.relationships
            ]

        # Add summary
        if self.include_summary and document.summary:
            # Ensure summary is calculated
            if document.summary.total_sections == 0:
                document.calculate_summary()
            output["summary"] = document.summary.to_dict()

        # Add schema information
        output["_schema"] = {
            "version": self.schema.version.value,
            "fields_included": list(output.keys()),
        }

        return output

    def _transform_sections(self, sections: list) -> list[dict[str, Any]]:
        """Transform sections to output format.

        Args:
            sections: List of sections to transform.

        Returns:
            List of section dictionaries.
        """
        result = []
        for section in sections:
            if hasattr(section, "to_dict"):
                section_dict = section.to_dict()
                # Filter semantic tags based on configuration
                if not self.include_semantic_tags and "semantic_tags" in section_dict:
                    del section_dict["semantic_tags"]
                result.append(section_dict)
            else:
                result.append({"content": str(section)})
        return result

    def _transform_metadata(self, metadata) -> dict[str, Any]:
        """Transform metadata to output format.

        Args:
            metadata: The metadata object to transform.

        Returns:
            Metadata dictionary.
        """
        if hasattr(metadata, "to_dict"):
            return metadata.to_dict()
        return {}

    def _extract_section_tags(self, sections: list) -> dict[str, list[str]]:
        """Extract semantic tags from all sections.

        Args:
            sections: List of sections to extract tags from.

        Returns:
            Dictionary mapping tag keys to lists of values.
        """
        tags: dict[str, list[str]] = {}

        def process_section(section):
            if hasattr(section, "semantic_tags") and section.semantic_tags:
                for key, value in section.semantic_tags.items():
                    if key not in tags:
                        tags[key] = []
                    if isinstance(value, list):
                        tags[key].extend(value)
                    else:
                        tags[key].append(str(value))

            if hasattr(section, "children") and section.children:
                for child in section.children:
                    process_section(child)

        for section in sections:
            process_section(section)

        return tags

    def transform_to_file(self, document: Document, file_path: str) -> None:
        """Transform a document and write to a file.

        Args:
            document: The document to transform.
            file_path: Path to write the JSON output.

        Raises:
            ValueError: If the document is invalid.
            IOError: If the file cannot be written.
        """
        json_str = self.transform(document)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    def transform_batch(self, documents: list[Document]) -> list[str]:
        """Transform multiple documents to JSON strings.

        Args:
            documents: List of documents to transform.

        Returns:
            List of JSON string representations.

        Raises:
            ValueError: If any document is invalid.
        """
        results = []
        for doc in documents:
            results.append(self.transform(doc))
        return results

    def transform_batch_to_dict(self, documents: list[Document]) -> list[dict[str, Any]]:
        """Transform multiple documents to dictionaries.

        Args:
            documents: List of documents to transform.

        Returns:
            List of dictionary representations.

        Raises:
            ValueError: If any document is invalid.
        """
        results = []
        for doc in documents:
            results.append(self.transform_to_dict(doc))
        return results

    @classmethod
    def for_mcp(cls) -> "JSONTransformer":
        """Create a transformer configured for MCP compatibility.

        Returns:
            JSONTransformer configured for MCP output.
        """
        schema = OutputSchema.mcp_schema()
        return cls(schema=schema)

    @classmethod
    def for_rag(cls) -> "JSONTransformer":
        """Create a transformer configured for RAG pipelines.

        Returns:
            JSONTransformer configured for RAG output.
        """
        schema = OutputSchema.default_schema()
        return cls(
            schema=schema,
            include_metadata=True,
            include_semantic_tags=True,
            include_summary=True,
            sort_keys=True,
        )
