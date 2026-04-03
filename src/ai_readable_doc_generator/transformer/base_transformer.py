"""Base transformer class for document transformation."""

from abc import ABC, abstractmethod
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema, SchemaType


class BaseTransformer(ABC):
    """Abstract base class for document transformers.

    Transformers convert Document objects into different output formats
    with configurable schemas and options.

    Attributes:
        schema: The output schema configuration.
        validate_output: Whether to validate the transformed output.
    """

    def __init__(
        self,
        schema: OutputSchema | None = None,
        validate_output: bool = True,
    ) -> None:
        """Initialize the transformer.

        Args:
            schema: Output schema configuration. Defaults to BASIC schema.
            validate_output: Whether to validate transformed output.
        """
        self.schema = schema or OutputSchema(schema_type=SchemaType.BASIC)
        self.validate_output = validate_output

    @abstractmethod
    def transform(self, document: Document) -> Any:
        """Transform a document into the target format.

        Args:
            document: The document to transform.

        Returns:
            The transformed document in the target format.

        Raises:
            ValueError: If document is invalid or transformation fails.
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement transform()")

    def validate(self, document: Document) -> bool:
        """Validate a document before transformation.

        Args:
            document: The document to validate.

        Returns:
            True if document is valid, False otherwise.
        """
        if not isinstance(document, Document):
            return False
        if not document.title and not document.sections:
            return False
        return True

    def _apply_schema_options(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply schema options to transformed data.

        Args:
            data: The transformed data dictionary.

        Returns:
            Data with schema options applied.
        """
        if not self.schema.include_metadata and "metadata" in data:
            del data["metadata"]

        if not self.schema.include_tags and "tags" in data:
            del data["tags"]

        if not self.schema.include_importance:
            data = self._remove_importance(data)

        if self.schema.flatten:
            data = self._flatten_sections(data)

        # Add custom fields
        if self.schema.custom_fields:
            data["custom"] = self.schema.custom_fields

        return data

    def _remove_importance(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively remove importance fields from data.

        Args:
            data: The data dictionary.

        Returns:
            Data with importance fields removed.
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key != "importance":
                    result[key] = self._remove_importance(value)
            return result
        elif isinstance(data, list):
            return [self._remove_importance(item) for item in data]
        return data

    def _flatten_sections(self, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested sections in data.

        Args:
            data: The data dictionary.

        Returns:
            Data with flattened sections.
        """
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            if key == "sections" and isinstance(value, list):
                result["sections"] = self._flatten_section_list(value)
            elif isinstance(value, dict):
                result[key] = self._flatten_sections(value)
            else:
                result[key] = value

        return result

    def _flatten_section_list(self, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Flatten a list of sections, extracting nested content.

        Args:
            sections: List of section dictionaries.

        Returns:
            Flattened list of sections.
        """
        result: list[dict[str, Any]] = []
        for section in sections:
            # Add section without nested children
            flat_section = {k: v for k, v in section.items() if k != "children"}
            result.append(flat_section)

            # Recursively flatten children
            if "children" in section and section["children"]:
                result.extend(self._flatten_section_list(section["children"]))

        return result

    def __repr__(self) -> str:
        """Return string representation of transformer."""
        return f"{self.__class__.__name__}(schema={self.schema.schema_type.value})"
