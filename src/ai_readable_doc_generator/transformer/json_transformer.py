"""JSON transformer for structured document output."""

import json
from typing import Any

from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class JSONTransformer(BaseTransformer):
    """Transformer that converts documents to structured JSON format."""

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        """Initialize JSON transformer.
        
        Args:
            options: Optional configuration with keys:
                - pretty: Enable pretty printing (default: True)
                - indent: Indentation level for pretty printing (default: 2)
                - ensure_ascii: Escape non-ASCII characters (default: False)
        """
        super().__init__(options)
        self.pretty = self.options.get("pretty", True)
        self.indent = self.options.get("indent", 2)
        self.ensure_ascii = self.options.get("ensure_ascii", False)

    def transform(self, document: Any) -> str:
        """Transform a document to JSON format.
        
        Args:
            document: Document object with to_dict() method or dict.
            
        Returns:
            JSON string representation of the document.
        """
        if hasattr(document, "to_dict"):
            data = document.to_dict()
        elif isinstance(document, dict):
            data = document
        else:
            data = {"content": str(document)}

        if self.pretty:
            return json.dumps(
                data,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                default=str,
            )
        return json.dumps(data, ensure_ascii=self.ensure_ascii, default=str)

    def validate(self, document: Any) -> bool:
        """Validate that a document can be transformed to JSON.
        
        Args:
            document: Document to validate.
            
        Returns:
            True if document is valid, False otherwise.
        """
        if document is None:
            return False
        if hasattr(document, "to_dict") or isinstance(document, dict):
            return True
        return True  # Accept any convertible object
