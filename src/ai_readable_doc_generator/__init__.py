"""ai-readable-doc-generator: Transform documentation into AI-agent-friendly formats.

This package provides tools for converting documentation (Markdown, HTML, etc.)
into structured formats with semantic tagging for AI agent consumption.
"""

__version__ = "0.1.0"

from .converter import HtmlConverter
from .document import Document
from .models import (
    ContentClassification,
    DocumentMetadata,
    ImportanceLevel,
    OutputSchema,
    SchemaConfig,
    Section,
    SectionType,
)

__all__ = [
    "ContentClassification",
    "Document",
    "DocumentMetadata",
    "HtmlConverter",
    "ImportanceLevel",
    "OutputSchema",
    "SchemaConfig",
    "Section",
    "SectionType",
]
