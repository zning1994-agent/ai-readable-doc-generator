"""Base converter class for document transformation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from ai_readable_doc_generator.models.schema import SemanticDocument


class BaseConverter(ABC):
    """Abstract base class for document converters.

    All document format converters should inherit from this class
    and implement the required conversion methods.
    """

    def __init__(
        self,
        add_table_of_contents: bool = True,
        add_statistics: bool = True,
        extract_semantic_tags: bool = True,
        importance_detection: bool = True,
    ) -> None:
        """Initialize the converter.

        Args:
            add_table_of_contents: Whether to generate a table of contents.
            add_statistics: Whether to generate document statistics.
            extract_semantic_tags: Whether to extract semantic tags.
            importance_detection: Whether to detect content importance.
        """
        self.add_table_of_contents = add_table_of_contents
        self.add_statistics = add_statistics
        self.extract_semantic_tags = extract_semantic_tags
        self.importance_detection = importance_detection

    @abstractmethod
    def convert(self, source: str | Path) -> SemanticDocument:
        """Convert a document to semantic format.

        Args:
            source: Either a file path or raw content string.
                   Subclasses should detect the type and handle accordingly.

        Returns:
            SemanticDocument with structured, AI-readable content.

        Raises:
            ValueError: If the source cannot be processed.
            FileNotFoundError: If a file path does not exist.
        """
        pass

    @abstractmethod
    def parse(self, content: str) -> SemanticDocument:
        """Parse content directly to semantic format.

        Args:
            content: Raw document content string.

        Returns:
            SemanticDocument with structured content.
        """
        pass

    def _validate_source(self, source: str | Path) -> tuple[bool, Optional[str]]:
        """Validate the source input.

        Args:
            source: The source to validate.

        Returns:
            Tuple of (is_file, content_or_path).
        """
        if isinstance(source, Path):
            return True, str(source)
        elif isinstance(source, str):
            # Check if it looks like a file path
            path = Path(source)
            if path.exists() and path.is_file():
                return True, str(path)
            # Otherwise treat as content
            return False, source
        else:
            return False, str(source)

    def _calculate_reading_time(self, text: str, words_per_minute: int = 200) -> float:
        """Calculate estimated reading time.

        Args:
            text: The text to analyze.
            words_per_minute: Average reading speed.

        Returns:
            Estimated reading time in minutes.
        """
        word_count = len(text.split())
        return round(word_count / words_per_minute, 2)

    def _generate_statistics(self, document: SemanticDocument) -> dict[str, Any]:
        """Generate document statistics.

        Args:
            document: The semantic document.

        Returns:
            Dictionary containing various statistics.
        """
        stats: dict[str, Any] = {
            "total_sections": len(document.sections),
            "total_blocks": len(document.all_blocks),
            "word_count": document.metadata.word_count,
            "reading_time_minutes": document.metadata.reading_time_minutes,
        }

        # Count content by type
        content_types: dict[str, int] = {}
        for block in document.all_blocks:
            ct = block.content_type
            content_types[ct] = content_types.get(ct, 0) + 1

        stats["content_types"] = content_types

        # Count headings by level
        heading_levels: dict[str, int] = {}
        for section in document.sections:
            level = section.level
            heading_levels[level] = heading_levels.get(level, 0) + 1

        stats["heading_levels"] = heading_levels
        stats["code_blocks"] = content_types.get("code_block", 0)
        stats["links"] = content_types.get("link", 0)
        stats["images"] = content_types.get("image", 0)

        return stats
