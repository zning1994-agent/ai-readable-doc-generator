"""Base converter module providing common functionality for all converters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConversionOptions:
    """Options for document conversion."""

    include_metadata: bool = True
    include_toc: bool = True
    semantic_tagging: bool = True
    preserve_formatting: bool = True
    max_heading_depth: Optional[int] = None
    custom_schema: Optional[dict[str, Any]] = None


@dataclass
class ConversionResult:
    """Result of a document conversion."""

    success: bool
    content: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if the conversion has errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if the conversion has warnings."""
        return len(self.warnings) > 0


class BaseConverter(ABC):
    """Abstract base class for document converters."""

    def __init__(self, options: Optional[ConversionOptions] = None):
        """Initialize the converter with optional configuration.

        Args:
            options: Configuration options for the conversion process.
        """
        self.options = options or ConversionOptions()

    @abstractmethod
    def convert(self, content: str) -> ConversionResult:
        """Convert document content to AI-readable format.

        Args:
            content: The raw document content to convert.

        Returns:
            ConversionResult containing the converted content and metadata.
        """
        pass

    @abstractmethod
    def validate(self, content: str) -> bool:
        """Validate if the content can be converted.

        Args:
            content: The content to validate.

        Returns:
            True if the content is valid for conversion, False otherwise.
        """
        pass

    def get_supported_formats(self) -> list[str]:
        """Get list of supported input formats.

        Returns:
            List of format identifiers supported by this converter.
        """
        return []

    def get_output_format(self) -> str:
        """Get the output format identifier.

        Returns:
            The output format string (e.g., 'json', 'yaml').
        """
        return "json"
