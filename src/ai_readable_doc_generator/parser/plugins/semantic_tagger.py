"""Semantic tagging plugin for adding machine-readable metadata to documents."""

import re
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.section import Section, SectionType


class SemanticTagger:
    """Adds semantic metadata tags to document sections.

    This plugin analyzes document content and adds machine-readable
    semantic markers to help AI systems better understand the structure
    and content of documents.
    """

    # Keywords that indicate importance or special content types
    IMPORTANT_PATTERNS = [
        r"\b(important|critical|warning|caution|danger|notice)\b",
        r"\b(essential|must|required|required|necessary)\b",
        r"\bNOTE|TIP|WARNING|CAUTION|DANGER\b",
    ]

    # Keywords that indicate code or technical content
    CODE_INDICATORS = [
        r"```[\w]*",
        r"`[^`]+`",
        r"\b(function|class|def|const|let|var|import|export)\b",
        r"\b\w+\(\)\s*\{",
    ]

    # Keywords that indicate lists
    LIST_PATTERNS = [
        r"^\s*[-*+]\s+",
        r"^\s*\d+\.\s+",
        r"^\s*\(?[a-zA-Z]\)\s+",
    ]

    def __init__(self) -> None:
        """Initialize the semantic tagger with compiled patterns."""
        self.important_re = [
            re.compile(p, re.IGNORECASE) for p in self.IMPORTANT_PATTERNS
        ]
        self.code_re = [
            re.compile(p) for p in self.CODE_INDICATORS
        ]
        self.list_re = [re.compile(p) for p in self.LIST_PATTERNS]

    def tag_document(self, document: Document) -> Document:
        """Add semantic tags to all sections in a document.

        Args:
            document: The document to tag.

        Returns:
            The same document with updated semantic metadata.
        """
        for section in document.sections:
            self._tag_section(section)

        # Update document-level metadata
        document.metadata["total_sections"] = len(document.sections)
        document.metadata["has_important_content"] = self._has_important_content(
            document
        )

        return document

    def _tag_section(self, section: Section) -> None:
        """Add semantic tags to a single section.

        Args:
            section: The section to tag.
        """
        content = section.content

        # Initialize semantic metadata
        semantic: dict[str, Any] = {
            "importance": "normal",
            "content_class": "text",
            "relationships": [],
        }

        # Detect importance level
        for pattern in self.important_re:
            if pattern.search(content):
                semantic["importance"] = "high"
                semantic["importance_indicator"] = pattern.pattern
                break

        # Detect content class
        for pattern in self.code_re:
            if pattern.search(content):
                semantic["content_class"] = "code"
                break

        # Detect if it's a list
        for pattern in self.list_re:
            if pattern.match(content):
                semantic["content_class"] = "list"
                break

        # Add heading context
        if section.section_type in (SectionType.HEADING, SectionType.TITLE):
            semantic["heading_level"] = section.level
            semantic["content_class"] = "heading"

        # Detect links
        if "http://" in content or "https://" in content:
            semantic["contains_links"] = True

        # Detect images
        if "image" in section.metadata or "![" in content:
            semantic["contains_images"] = True

        # Merge with existing metadata
        section.metadata["semantic"] = semantic

    def _has_important_content(self, document: Document) -> bool:
        """Check if document contains any important sections.

        Args:
            document: The document to check.

        Returns:
            True if document has important content.
        """
        for section in document.sections:
            if "semantic" in section.metadata:
                if section.metadata["semantic"].get("importance") == "high":
                    return True
        return False
