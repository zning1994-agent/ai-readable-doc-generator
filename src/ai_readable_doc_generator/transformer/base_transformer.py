"""Base transformer class for document transformation."""

from abc import ABC, abstractmethod
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.schema import OutputSchema


class BaseTransformer(ABC):
    """Abstract base class for document transformers."""

    def __init__(self, schema: OutputSchema | None = None) -> None:
        """Initialize the transformer with an optional schema.

        Args:
            schema: Output schema configuration. Uses default if not provided.
        """
        self.schema = schema or OutputSchema.default_schema()

    @abstractmethod
    def transform(self, document: Document) -> Any:
        """Transform a document to the target format.

        Args:
            document: The document to transform.

        Returns:
            The transformed document in the target format.

        Raises:
            ValueError: If the document is invalid.
        """
        pass

    @abstractmethod
    def validate(self, document: Document) -> bool:
        """Validate a document before transformation.

        Args:
            document: The document to validate.

        Returns:
            True if the document is valid, False otherwise.
        """
        pass

    def pre_transform(self, document: Document) -> Document:
        """Hook for pre-transformation processing.

        Args:
            document: The document to process.

        Returns:
            The processed document.
        """
        return document

    def post_transform(self, result: Any) -> Any:
        """Hook for post-transformation processing.

        Args:
            result: The transformation result.

        Returns:
            The processed result.
        """
        return result
