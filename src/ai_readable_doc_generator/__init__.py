"""AI-Readable Document Generator.

A tool for transforming documentation into AI-Agent-friendly formats
with structured output and semantic tagging.
"""

__version__ = "0.1.0"

from ai_readable_doc_generator.base import BaseConverter
from ai_readable_doc_generator.converter import MarkdownConverter
from ai_readable_doc_generator.document import Document
from ai_readable_doc_generator.models.schema import (
    ContentType,
    DocumentMetadata,
    HeadingLevel,
    RelationshipType,
    SemanticBlock,
    SemanticDocument,
    SemanticSection,
)

__all__ = [
    "__version__",
    "BaseConverter",
    "MarkdownConverter",
    "Document",
    "SemanticDocument",
    "SemanticSection",
    "SemanticBlock",
    "DocumentMetadata",
    "ContentType",
    "HeadingLevel",
    "RelationshipType",
]
