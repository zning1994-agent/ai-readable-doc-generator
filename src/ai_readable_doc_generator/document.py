"""Document model for semantic representation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """Internal document representation for processing.

    This class provides an intermediate representation during
    document parsing before conversion to the final SemanticDocument.
    """

    content: str
    source_path: str | None = None
    raw_tokens: list[Any] = field(default_factory=list)
    ast: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize derived fields after dataclass creation."""
        if not self.metadata:
            self.metadata = {
                "source_format": "markdown",
                "title": None,
                "description": None,
            }

    @property
    def title(self) -> str | None:
        """Get document title from metadata."""
        return self.metadata.get("title")

    @title.setter
    def title(self, value: str | None) -> None:
        """Set document title in metadata."""
        self.metadata["title"] = value

    @property
    def word_count(self) -> int:
        """Calculate word count."""
        return len(self.content.split())

    def add_token(self, token: Any) -> None:
        """Add a token to the raw tokens list.

        Args:
            token: A token from the parser.
        """
        self.raw_tokens.append(token)

    def set_ast(self, ast: Any) -> None:
        """Set the abstract syntax tree.

        Args:
            ast: The parsed AST representation.
        """
        self.ast = ast
