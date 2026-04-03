"""
Base parser class for document parsing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the parser with optional configuration.

        Args:
            config: Optional configuration dictionary for parser settings.
        """
        self.config = config or {}
        self._plugins: List[Any] = []

    def register_plugin(self, plugin: Any) -> None:
        """
        Register a plugin to be used during parsing.

        Args:
            plugin: A plugin instance that implements the parser plugin interface.
        """
        self._plugins.append(plugin)

    def unregister_plugin(self, plugin: Any) -> None:
        """
        Unregister a plugin from the parser.

        Args:
            plugin: The plugin instance to remove.
        """
        if plugin in self._plugins:
            self._plugins.remove(plugin)

    def clear_plugins(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()

    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse document content into a structured format.

        Args:
            content: The raw document content to parse.

        Returns:
            A dictionary representing the parsed document structure.

        Raises:
            ParseError: If parsing fails.
        """
        pass

    @abstractmethod
    def validate(self, content: str) -> bool:
        """
        Validate if the content can be parsed.

        Args:
            content: The document content to validate.

        Returns:
            True if the content is valid for this parser, False otherwise.
        """
        pass

    def _apply_plugins(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply registered plugins to parsed content.

        Args:
            parsed: The parsed document dictionary.

        Returns:
            The document with plugins applied.
        """
        result = parsed
        for plugin in self._plugins:
            result = plugin.process(result)
        return result


class ParseError(Exception):
    """Exception raised when parsing fails."""

    def __init__(self, message: str, line: Optional[int] = None):
        """
        Initialize a parse error.

        Args:
            message: The error message.
            line: Optional line number where the error occurred.
        """
        self.line = line
        if line is not None:
            super().__init__(f"Parse error at line {line}: {message}")
        else:
            super().__init__(f"Parse error: {message}")
