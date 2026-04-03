"""Base transformer class for document conversion."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):
    """Abstract base class for document transformers.
    
    Transformers convert parsed document structures into various output formats
    for AI agent consumption.
    """

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        """Initialize the transformer with optional configuration.
        
        Args:
            options: Optional configuration dictionary for transformer behavior.
        """
        self.options = options or {}

    @abstractmethod
    def transform(self, document: Any) -> str:
        """Transform a document into the target format.
        
        Args:
            document: The parsed document object to transform.
            
        Returns:
            String representation of the transformed document in target format.
        """
        pass

    @abstractmethod
    def validate(self, document: Any) -> bool:
        """Validate that a document can be transformed.
        
        Args:
            document: The document to validate.
            
        Returns:
            True if the document is valid for transformation, False otherwise.
        """
        pass
