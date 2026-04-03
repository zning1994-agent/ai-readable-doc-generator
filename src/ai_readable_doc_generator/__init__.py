"""AI-Readable Document Generator.

A tool for transforming documentation into AI-Agent-friendly formats
with semantic tagging and structured output.
"""

__version__ = "0.1.0"

from .document import MarkdownParser
from .converter import DocumentConverter
from .models import Document, OutputFormat

__all__ = [
    "MarkdownParser",
    "DocumentConverter",
    "Document",
    "OutputFormat"
]
