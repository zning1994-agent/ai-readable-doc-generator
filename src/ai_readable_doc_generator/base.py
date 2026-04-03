"""Base parser interface for document conversion."""

from abc import ABC, abstractmethod

from ai_readable_doc_generator.models.document import Document


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, content: str) -> Document:
        """Parse content into a structured Document.

        Args:
            content: Raw document content to parse.

        Returns:
            A structured Document object with semantic sections.
        """
        ...

    @abstractmethod
    def parse_file(self, file_path: str) -> Document:
        """Parse a file into a structured Document.

        Args:
            file_path: Path to the file to parse.

        Returns:
            A structured Document object with semantic sections.
        """
        ...

    def validate(self, content: str) -> bool:
        """Validate if the content can be parsed.

        Args:
            content: Raw document content to validate.

        Returns:
            True if the content is valid for this parser.
        """
        return True
