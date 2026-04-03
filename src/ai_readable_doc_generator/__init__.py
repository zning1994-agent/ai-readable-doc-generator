"""AI-Readable Document Generator.

A tool for converting documentation into AI-agent-friendly formats.
"""

__version__ = "0.1.0"
__author__ = "AI Documentation Tools"
__license__ = "MIT"

from ai_readable_doc_generator.models import (
    ContentImportance,
    Document,
    DocumentMetadata,
    DocumentRelationship,
    DocumentSummary,
    OutputSchema,
    SchemaField,
    SchemaVersion,
    Section,
    SectionType,
)
from ai_readable_doc_generator.transformer import BaseTransformer, JSONTransformer

__all__ = [
    # Version
    "__version__",
    # Models
    "ContentImportance",
    "Document",
    "DocumentMetadata",
    "DocumentRelationship",
    "DocumentSummary",
    "OutputSchema",
    "SchemaField",
    "SchemaVersion",
    "Section",
    "SectionType",
    # Transformers
    "BaseTransformer",
    "JSONTransformer",
]
