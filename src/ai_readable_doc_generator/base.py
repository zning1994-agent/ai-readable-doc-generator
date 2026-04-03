"""Base converter class for document conversion."""

from abc import ABC, abstractmethod

from .models import Document


class BaseConverter(ABC):
    """Abstract base class for document converters."""

    @abstractmethod
    def convert(self, source: str) -> Document:
        """Convert source content to Document.

        Args:
            source: The source content to convert (file path or raw content).

        Returns:
            Document: The converted document with semantic structure.
        """
        pass

    @abstractmethod
    def validate(self, source: str) -> bool:
        """Validate if the source can be converted.

        Args:
            source: The source content to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        pass

    def preprocess(self, source: str) -> str:
        """Preprocess source content before conversion.

        Args:
            source: The raw source content.

        Returns:
            str: Preprocessed content.
        """
        return source

    def postprocess(self, document: Document) -> Document:
        """Postprocess converted document.

        Args:
            document: The converted document.

        Returns:
            Document: Postprocessed document.
        """
        return document
