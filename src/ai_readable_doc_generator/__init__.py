"""
ai-readable-doc-generator

Transform documentation into AI-agent-friendly formats with structured output
and semantic tagging.

Example:
    >>> from ai_readable_doc_generator import PlaintextConverter
    >>> converter = PlaintextConverter()
    >>> doc = converter.convert("# Hello World\\n\\nThis is a test.")
    >>> print(doc.metadata.title)
    Hello World
"""

from ai_readable_doc_generator.base import BaseConverter
from ai_readable_doc_generator.converter import PlaintextConverter, PlaintextHeuristics
from ai_readable_doc_generator.models import (
    Document,
    DocumentMetadata,
    Section,
    SectionType,
    ContentType,
    Importance,
    OutputSchema,
    SchemaType,
)

__version__ = "0.1.0"

__all__ = [
    # Core
    "BaseConverter",
    "PlaintextConverter",
    "PlaintextHeuristics",
    # Models
    "Document",
    "DocumentMetadata",
    "Section",
    "SectionType",
    "ContentType",
    "Importance",
    "OutputSchema",
    "SchemaType",
    # Utilities
    "__version__",
]
