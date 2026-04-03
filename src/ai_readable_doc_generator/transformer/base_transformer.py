"""Base transformer abstract class."""

from abc import ABC, abstractmethod

from ai_readable_doc_generator.document import Document


class BaseTransformer(ABC):
    """Abstract base class for document transformers."""
    
    @abstractmethod
    def transform(self, document: Document) -> str:
        """Transform a document to the target format.
        
        Args:
            document: The document to transform.
        
        Returns:
            Transformed document as a string.
        """
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get the content type of the output.
        
        Returns:
            MIME content type string.
        """
        pass
