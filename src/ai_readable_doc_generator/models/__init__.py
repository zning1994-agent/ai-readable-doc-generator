"""
Domain models for AI-readable documentation generation.

This package contains the core domain models:
- Section: Document sections with content, metadata, and hierarchy support
- SectionMetadata: Semantic metadata for AI processing
- SectionType: Types of content a section can contain
- ContentImportance: Importance levels for AI understanding
"""

from ai_readable_doc_generator.models.section import (
    ContentImportance,
    Section,
    SectionMetadata,
    SectionType,
)

__all__ = [
    "Section",
    "SectionMetadata",
    "SectionType",
    "ContentImportance",
]
