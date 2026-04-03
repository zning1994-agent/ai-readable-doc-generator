"""Semantic tagger plugin for enhanced content classification."""

import re
from typing import Optional

from ai_readable_doc_generator.models import Section, SectionType, ContentType


class SemanticTagger:
    """
    Plugin for enhanced semantic tagging of document sections.

    This tagger applies advanced heuristics to classify content types
    and add semantic annotations to sections.
    """

    # Pattern-based semantic classifiers
    SEMANTIC_PATTERNS = {
        ContentType.NOTE: [
            re.compile(r"^(?:note:|NOTE:|Note:)\s*", re.IGNORECASE),
            re.compile(r"ℹ️?\s*"),
        ],
        ContentType.WARNING: [
            re.compile(r"^(?:warning:|WARNING:|Caution:|CAUTION:|⚠️?)\s*", re.IGNORECASE),
        ],
        ContentType.TIP: [
            re.compile(r"^(?:tip:|TIP:|Tip:|💡)\s*", re.IGNORECASE),
            re.compile(r"^(?:pro tip:|PRO TIP:)\s*", re.IGNORECASE),
        ],
        ContentType.QUESTION: [
            re.compile(r"^\?"),
            re.compile(r"^(?:Q:|Qustion:|question:)\s*", re.IGNORECASE),
            re.compile(r"^(?:how|what|why|when|where|who)\s+(?:do|does|is|are|can|should)", re.IGNORECASE),
        ],
        ContentType.ANSWER: [
            re.compile(r"^(?:A:|Answer:|answer:)\s*", re.IGNORECASE),
        ],
        ContentType.CODE_EXAMPLE: [
            re.compile(r"^(?:example:|Example:|EXAMPLE:)\s*", re.IGNORECASE),
            re.compile(r"```"),
            re.compile(r"^\s{4,}"),
        ],
    }

    # Keywords that indicate specific content types
    CONTENT_KEYWORDS = {
        ContentType.INTRODUCTION: {"introduction", "overview", "background", "purpose"},
        ContentType.CONCLUSION: {"conclusion", "summary", "wrap-up", "final", "takeaway"},
        ContentType.DEFINITION: {"definition", "defined as", "means", "refers to"},
        ContentType.CITATION: {"according to", "as stated in", "see", "reference"},
        ContentType.REFERENCE: {"see also", "related", "further reading", "documentation"},
    }

    def tag(self, section: Section) -> Section:
        """
        Apply semantic tagging to a section.

        Args:
            section: Section to tag.

        Returns:
            Tagged section with enhanced metadata.
        """
        if section.section_type == SectionType.PARAGRAPH:
            self._tag_paragraph(section)
        elif section.section_type == SectionType.HEADING:
            self._tag_heading(section)
        elif section.section_type == SectionType.CODE_BLOCK:
            self._tag_code_block(section)
        elif section.section_type == SectionType.LIST:
            self._tag_list(section)

        return section

    def _tag_paragraph(self, section: Section) -> None:
        """Tag a paragraph section."""
        content = section.content

        # Apply pattern-based classification
        for content_type, patterns in self.SEMANTIC_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(content):
                    section.content_type = content_type
                    section.metadata["tagger_match"] = pattern.pattern
                    break

        # Check for keywords in context
        if section.content_type == ContentType.UNCLASSIFIED:
            for keyword_type, keywords in self.CONTENT_KEYWORDS.items():
                if any(kw in content.lower() for kw in keywords):
                    section.content_type = keyword_type
                    break

        # Add semantic annotations
        section.metadata["annotations"] = self._extract_annotations(content)

    def _tag_heading(self, section: Section) -> None:
        """Tag a heading section."""
        content = section.content.lower()

        # Infer heading semantic type from keywords
        for keyword_type, keywords in self.CONTENT_KEYWORDS.items():
            if any(kw in content for kw in keywords):
                section.content_type = keyword_type
                break

        # Add heading context metadata
        section.metadata["is_title"] = section.level == 1 and len(content) < 50

    def _tag_code_block(self, section: Section) -> None:
        """Tag a code block section."""
        # Detect language from fenced blocks
        if "```" in section.raw_text:
            match = re.search(r"```(\w*)", section.raw_text)
            if match and match.group(1):
                section.metadata["language"] = match.group(1)

        # Infer language from content patterns
        content = section.content
        if not section.metadata.get("language"):
            inferred = self._infer_language(content)
            if inferred:
                section.metadata["language"] = inferred

    def _tag_list(self, section: Section) -> None:
        """Tag a list section."""
        # Classify list based on content
        items = section.content.split("\n")
        if len(items) > 3:
            section.metadata["is_long_list"] = True

        # Check for checklist patterns
        if any("[" in item and "]" in item for item in items):
            section.metadata["is_checklist"] = True

    def _infer_language(self, code: str) -> Optional[str]:
        """
        Infer programming language from code content.

        Args:
            code: Code block content.

        Returns:
            Inferred language name or None.
        """
        code_lower = code.lower()

        # Simple language inference from common patterns
        if "def " in code or "import " in code or "from " in code:
            if ":" in code and ("self." in code or "cls." in code):
                return "python"
            return "python"
        if "function" in code_lower or "const " in code or "let " in code:
            if "=>" in code or "console." in code:
                return "javascript"
            if "interface" in code_lower or "type " in code:
                return "typescript"
            return "javascript"
        if "#include" in code or "int main" in code:
            return "c"
        if "package main" in code or "func " in code:
            return "go"
        if "class " in code and "{" in code:
            if "public static void main" in code:
                return "java"
            if "def" in code_lower:
                return "kotlin"
        if "fn main" in code or "let mut" in code:
            return "rust"
        if "<?php" in code or "$" in code:
            return "php"
        if "<html" in code_lower or "<!doctype" in code_lower:
            return "html"
        if "{" in code and ":" in code and (";" not in code or ";" in code.replace(" ", "")):
            return "css"

        return None

    def _extract_annotations(self, content: str) -> list[dict]:
        """
        Extract semantic annotations from content.

        Args:
            content: Content to analyze.

        Returns:
            List of annotation dictionaries.
        """
        annotations = []

        # Extract inline code references
        code_refs = re.findall(r"`([^`]+)`", content)
        for ref in code_refs:
            annotations.append({"type": "code_reference", "value": ref})

        # Extract URLs
        urls = re.findall(r"https?://[^\s]+", content)
        for url in urls:
            annotations.append({"type": "url", "value": url})

        # Extract citations
        citations = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for cite in citations:
            annotations.append({"type": "citation", "text": cite[0], "url": cite[1]})

        return annotations
