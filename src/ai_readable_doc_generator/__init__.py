"""
ai-readable-doc-generator: Transform documentation into AI-agent-friendly formats.

This package provides tools for converting documentation (Markdown) into
structured formats with semantic tagging that AI agents can parse effectively.

Usage:
    from ai_readable_doc_generator import Converter, Document

    # Convert markdown to AI-readable format
    document = Document.from_markdown("# Hello\n\nContent here")
    converter = Converter()
    result = converter.convert(document, JSONTransformer())
"""

__version__ = "0.1.0"
__author__ = "AI Documentation Team"
__license__ = "MIT"

from .converter import Converter
from .document import Document

# Import transformers
from .transformer.json_transformer import JSONTransformer
from .transformer.mcp_transformer import MCPTransformer

__all__ = [
    "Converter",
    "Document",
    "JSONTransformer",
    "MCPTransformer",
    "__version__",
]
