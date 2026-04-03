"""AI-readable document generator.

Transform documentation into AI-Agent-friendly formats with
structured output and semantic tagging.
"""

from .base import DocumentConverter
from .document import (
    ContentClassification,
    Document,
    DocumentSection,
    ImportanceLevel,
    SectionType,
    SemanticTag,
)

__all__ = [
    "DocumentConverter",
    "Document",
    "DocumentSection",
    "SectionType",
    "ContentClassification",
    "ImportanceLevel",
    "SemanticTag",
]
__version__ = "0.1.0"
