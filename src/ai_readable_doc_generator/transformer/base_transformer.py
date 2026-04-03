"""Base transformer class for document output formatting."""

from abc import ABC, abstractmethod
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema


class BaseTransformer(ABC):
    """Abstract base class for document transformers.

    Transformers are responsible for converting parsed Document objects
    into various output formats (JSON, YAML, MCP, etc.).
    """

    def __init__(self, schema: OutputSchema | None = None) -> None:
        """Initialize transformer with optional schema.

        Args:
            schema: Optional output schema configuration.
        """
        self.schema = schema or OutputSchema.default_json()

    @abstractmethod
    def transform(self, document: Document) -> str:
        """Transform document to output format.

        Args:
            document: The document to transform.

        Returns:
            Transformed document as string.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform document to dictionary representation.

        Args:
            document: The document to transform.

        Returns:
            Transformed document as dictionary.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def _apply_schema_fields(
        self, data: dict[str, Any], document: Document
    ) -> dict[str, Any]:
        """Apply schema field mappings to document data.

        Args:
            data: Base data dictionary.
            document: Source document for field extraction.

        Returns:
            Data with schema fields applied.
        """
        if not self.schema.fields:
            return data

        result = {}
        for field in self.schema.fields:
            value = self._get_field_value(field.path, data)
            if value is not None or not field.required:
                result[field.name] = value if value is not None else field.default

        return result

    def _get_field_value(self, path: str, data: dict[str, Any]) -> Any:
        """Get value from dictionary using path notation.

        Args:
            path: Dot-notation path to value (e.g., 'title', 'sections[0].content').
            data: Source dictionary.

        Returns:
            Value at path or None if not found.
        """
        # Handle array notation
        if "[" in path:
            parts = path.split("[")
            current = data
            for i, part in enumerate(parts):
                if i == 0:
                    current = current.get(part, {})
                else:
                    # Extract index from '[x]' or '[*]'
                    bracket_match = part.find("]")
                    if bracket_match != -1:
                        key = part[:bracket_match]
                        part = part[bracket_match + 1:]
                        if key == "*":
                            # Return list for array expansion
                            if isinstance(current, dict):
                                current = current.get(part, [])
                            if isinstance(current, list):
                                return [item.get(part.split(".")[-1] if "." in part else "content", "") for item in current]
                        else:
                            index = int(key)
                            if isinstance(current, (list, dict)):
                                current = current[index] if isinstance(current, list) else current.get(key, {})
                            if part:
                                current = current.get(part.split(".")[0], {}) if isinstance(current, dict) else {}
            return current

        return data.get(path)
