"""Base converter class for document conversion."""

from abc import ABC, abstractmethod
from typing import Optional

from ai_readable_doc_generator.models import Document, OutputSchema, SchemaType


class BaseConverter(ABC):
    """
    Abstract base class for document converters.

    Converters transform raw document content into structured Document objects
    with semantic tagging and metadata.

    Attributes:
        schema: Output schema to use for conversion.
        options: Additional conversion options.
    """

    def __init__(
        self,
        schema: Optional[OutputSchema] = None,
        options: Optional[dict] = None,
    ) -> None:
        """
        Initialize the converter.

        Args:
            schema: Output schema to use. Defaults to standard schema.
            options: Additional conversion options.
        """
        self.schema = schema or OutputSchema.standard()
        self.options = options or {}

    @abstractmethod
    def convert(self, content: str, source_path: str = "") -> Document:
        """
        Convert raw content to a structured Document.

        Args:
            content: Raw document content.
            source_path: Optional source file path.

        Returns:
            Structured Document object.
        """
        pass

    @abstractmethod
    def parse(self, content: str) -> Document:
        """
        Parse content into sections without full conversion.

        This method can be used for quick parsing without
        applying full semantic analysis.

        Args:
            content: Raw document content.

        Returns:
            Parsed Document with basic structure.
        """
        pass

    def validate_content(self, content: str) -> bool:
        """
        Validate that content can be processed.

        Args:
            content: Content to validate.

        Returns:
            True if content is valid for processing.
        """
        return bool(content and content.strip())

    def get_schema(self) -> OutputSchema:
        """
        Get the current output schema.

        Returns:
            Current OutputSchema instance.
        """
        return self.schema

    def set_schema(self, schema: OutputSchema) -> None:
        """
        Set a new output schema.

        Args:
            schema: New OutputSchema to use.
        """
        self.schema = schema
