"""AI-Readable Document Generator.

Transform Markdown documentation into AI-friendly formats with semantic tagging.
"""

__version__ = "0.1.0"
__author__ = "AI Documentation Team"
__description__ = "Transform documentation into AI-agent-friendly formats"

from ai_readable_doc_generator.converter import Converter
from ai_readable_doc_generator.document import Document
from ai_readable_doc_generator.models.document import DocumentMetadata
from ai_readable_doc_generator.models.section import Section, SectionType
from ai_readable_doc_generator.models.schema import OutputSchema

__all__ = [
    "Converter",
    "Document",
    "DocumentMetadata",
    "Section",
    "SectionType",
    "OutputSchema",
]
