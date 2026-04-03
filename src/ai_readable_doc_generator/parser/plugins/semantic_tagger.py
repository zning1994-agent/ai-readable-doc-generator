"""Semantic tagger plugin for content analysis and classification."""

import re
from typing import Optional

from ..models.schema import (
    SectionType,
    ContentClassification,
    SemanticTag,
    DEFAULT_SEMANTIC_MAPPINGS
)


class SemanticTagger:
    """
    Analyzes document content and applies semantic tags.

    This plugin detects patterns, classifies content types,
    and generates semantic metadata for AI-readable output.
    """

    # Patterns for detecting specific content types
    PATTERNS = {
        "api_endpoint": re.compile(
            r'\b(GET|POST|PUT|PATCH|DELETE)\s+[/@]?\w+',
            re.IGNORECASE
        ),
        "function_def": re.compile(
            r'\b(def|function|fn|func)\s+\w+\s*\(',
            re.IGNORECASE
        ),
        "class_def": re.compile(
            r'\b(class|struct|interface|type)\s+\w+',
            re.IGNORECASE
        ),
        "configuration": re.compile(
            r'\b[A-Z_]+(?:=|:)\s*["\']?.+["\']?',
            re.IGNORECASE
        ),
        "url": re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        ),
        "email": re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ),
        "version": re.compile(
            r'\bv?\d+\.\d+(?:\.\d+)*(?:[-.]?\w+)?\b'
        ),
        "file_path": re.compile(
            r'(?:[a-zA-Z]:\\|/)?(?:[^\\/:*?"<>|\r\n]+\/)*[^\\/:*?"<>|\r\n]+'
        ),
        "installation_command": re.compile(
            r'(?:pip|npm|yarn|apt|brew|cargo)\s+(?:install|add|get)\s+',
            re.IGNORECASE
        ),
        "code_inline": re.compile(r'`[^`]+`'),
        "bold_text": re.compile(r'\*\*[^*]+\*\*|__[^_]+__'),
        "link": re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
    }

    # Warning/note indicators
    CALLOUT_PATTERNS = {
        "warning": re.compile(
            r'\b(?:warning|caution|danger|attention)\b:?',
            re.IGNORECASE
        ),
        "note": re.compile(
            r'\b(?:note|tip|info|hint)\b:?',
            re.IGNORECASE
        ),
        "important": re.compile(
            r'\b(?:important|remember|do not|avoid)\b:?',
            re.IGNORECASE
        ),
    }

    def classify_content(
        self,
        content: str,
        section_type: SectionType
    ) -> Optional[ContentClassification]:
        """
        Classify the content type of a section.

        Args:
            content: The text content to classify
            section_type: The type of section

        Returns:
            ContentClassification or None if classification not possible
        """
        content_lower = content.lower()

        # Check for callouts first
        if self.CALLOUT_PATTERNS["warning"].search(content):
            return ContentClassification.WARNING
        if self.CALLOUT_PATTERNS["note"].search(content):
            return ContentClassification.NOTE

        # Check for API documentation
        if section_type == SectionType.CODE_BLOCK:
            if self.PATTERNS["api_endpoint"].search(content):
                return ContentClassification.API_DOC
            if self.PATTERNS["function_def"].search(content):
                return ContentClassification.API_DOC
            return ContentClassification.TECHNICAL

        # Check for configuration
        if self.PATTERNS["configuration"].search(content):
            return ContentClassification.CONFIGURATION

        # Check for troubleshooting
        if any(word in content_lower for word in ["error", "issue", "problem", "fix", "solution"]):
            return ContentClassification.TROUBLESHOOTING

        # Check for examples
        if any(word in content_lower for word in ["example", "example:", "e.g.", "for example"]):
            return ContentClassification.EXAMPLE

        # Default based on section type
        if section_type.value.startswith("heading_"):
            if any(word in content_lower for word in ["api", "reference", "docs"]):
                return ContentClassification.API_DOC
            return ContentClassification.NARRATIVE

        return ContentClassification.TECHNICAL

    def detect_patterns(self, content: str) -> list[SemanticTag]:
        """
        Detect patterns in content and return semantic tags.

        Args:
            content: The text content to analyze

        Returns:
            List of SemanticTag objects for detected patterns
        """
        tags = []

        # Check each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                tag = SemanticTag(
                    name="pattern",
                    value=pattern_name,
                    confidence=min(len(matches) * 0.2, 1.0),
                    source="pattern_match"
                )
                tags.append(tag)

        # Detect semantic mappings
        content_lower = content.lower()
        for keyword, classification in DEFAULT_SEMANTIC_MAPPINGS.items():
            if keyword in content_lower:
                tags.append(
                    SemanticTag(
                        name="semantic_marker",
                        value=classification.value,
                        confidence=0.9,
                        source="keyword_match"
                    )
                )

        # Detect numbered lists (often for steps)
        list_items = re.findall(r'^\d+\.\s+', content, re.MULTILINE)
        if len(list_items) >= 3:
            tags.append(
                SemanticTag(
                    name="list_type",
                    value="ordered_steps",
                    confidence=0.85,
                    source="structural_analysis"
                )
            )

        # Detect bullet lists
        bullet_items = re.findall(r'^[-*+]\s+', content, re.MULTILINE)
        if len(bullet_items) >= 3:
            tags.append(
                SemanticTag(
                    name="list_type",
                    value="unordered_items",
                    confidence=0.85,
                    source="structural_analysis"
                )
            )

        return tags

    def extract_entities(self, content: str) -> dict[str, list[str]]:
        """
        Extract named entities from content.

        Args:
            content: The text content to analyze

        Returns:
            Dictionary of entity types to lists of extracted values
        """
        entities: dict[str, list[str]] = {
            "urls": [],
            "emails": [],
            "file_paths": [],
            "versions": [],
            "commands": []
        }

        # Extract URLs
        entities["urls"] = self.PATTERNS["url"].findall(content)

        # Extract emails
        entities["emails"] = self.PATTERNS["email"].findall(content)

        # Extract file paths
        entities["file_paths"] = self.PATTERNS["file_path"].findall(content)

        # Extract versions
        entities["versions"] = self.PATTERNS["version"].findall(content)

        # Extract commands
        if self.PATTERNS["installation_command"].search(content):
            # Find the command
            match = re.search(
                r'(?:pip|npm|yarn|apt|brew|cargo)\s+\w+\s+[^\n]+',
                content
            )
            if match:
                entities["commands"].append(match.group(0))

        return entities

    def analyze_reading_level(self, content: str) -> dict[str, any]:
        """
        Analyze the reading level of content.

        Args:
            content: The text content to analyze

        Returns:
            Dictionary with reading level metrics
        """
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not words or not sentences:
            return {
                "average_word_length": 0,
                "average_sentence_length": 0,
                "word_count": 0,
                "sentence_count": 0
            }

        # Calculate average word length
        total_word_length = sum(len(w) for w in words)
        avg_word_length = total_word_length / len(words)

        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences)

        return {
            "average_word_length": round(avg_word_length, 2),
            "average_sentence_length": round(avg_sentence_length, 2),
            "word_count": len(words),
            "sentence_count": len(sentences)
        }
