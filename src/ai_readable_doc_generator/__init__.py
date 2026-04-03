"""
AI-Readable Document Generator.

A tool that transforms documentation into AI-agent-friendly formats with
structured output, semantic tagging, and MCP compatibility.
"""

__version__ = "0.1.0"

from ai_readable_doc_generator.models import (
    Section,
    SectionMetadata,
    SectionType,
    ContentImportance,
)

__all__ = [
    "Section",
    "SectionMetadata",
    "SectionType",
    "ContentImportance",
]
