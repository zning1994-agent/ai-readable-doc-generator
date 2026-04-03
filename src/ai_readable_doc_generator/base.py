"""Abstract base class for document converters."""

from abc import ABC, abstractmethod

from .document import Document


class DocumentConverter(ABC):
    """
    Abstract base class for converting documents to AI-readable format.

    Subclasses must implement the `convert` method to transform
    raw content into structured Document objects with semantic tagging.

    Example:
        ```python
        class MarkdownConverter(DocumentConverter):
            def convert(self, content: str) -> Document:
                # Implementation here
                ...
        ```
    """

    @abstractmethod
    def convert(self, content: str) -> Document:
        """
        Convert raw content to a structured Document.

        Args:
            content: Raw document content (e.g., Markdown string).

        Returns:
            A structured Document with semantic tagging and hierarchy.

        Raises:
            ValueError: If the content cannot be parsed.
        """
        ...
