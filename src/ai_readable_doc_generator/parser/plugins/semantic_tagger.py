"""
Semantic tagger plugin for adding semantic markers to parsed content.
"""

import re
from typing import Any, Dict, List, Optional, Set


class SemanticTagger:
    """
    Plugin for adding semantic tags to document content.

    This plugin analyzes document structure and content to add:
    - Section type classification (introduction, body, conclusion, etc.)
    - Content type markers (explanation, instruction, reference, etc.)
    - Importance indicators (critical, important, supplementary)
    - Relationship markers between sections
    """

    # Patterns for content classification
    QUESTION_PATTERN = re.compile(r'\?$')
    EXCLAMATION_PATTERN = re.compile(r'!$')
    CODE_BLOCK_PATTERN = re.compile(r'^```', re.MULTILINE)
    IMPORTANT_KEYWORDS = {
        'important', 'critical', 'warning', 'caution', 'danger',
        'note', 'attention', 'notice', 'essential', 'required',
        'must', 'should', 'required', 'mandatory'
    }
    REFERENCE_KEYWORDS = {
        'see also', 'reference', 'related', 'further reading',
        'documentation', 'manual', 'guide', 'tutorial'
    }
    INSTRUCTION_KEYWORDS = {
        'step', 'steps', 'how to', 'how-to', 'instructions',
        'procedure', 'process', 'install', 'configure', 'setup',
        'run', 'execute', 'build', 'deploy'
    }
    CONFIGURATION_KEYWORDS = {
        'setting', 'config', 'configuration', 'option', 'parameter',
        'variable', 'environment', 'flag', 'feature'
    }
    API_KEYWORDS = {
        'api', 'endpoint', 'request', 'response', 'method',
        'header', 'status', 'authentication', 'authorization'
    }
    ERROR_KEYWORDS = {
        'error', 'exception', 'warning', 'fail', 'failed',
        'issue', 'problem', 'bug', 'crash', 'broken'
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the semantic tagger.

        Args:
            config: Optional configuration dictionary.
                - include_importance: Include importance markers (default: True)
                - include_relationships: Include section relationships (default: True)
                - min_word_count: Minimum word count for paragraphs (default: 10)
                - custom_keywords: Custom keyword mappings (default: {})
        """
        self.config = config or {}
        self.include_importance = self.config.get("include_importance", True)
        self.include_relationships = self.config.get("include_relationships", True)
        self.min_word_count = self.config.get("min_word_count", 10)
        self.custom_keywords = self.config.get("custom_keywords", {})

        # Merge custom keywords with defaults
        self._keywords = self._merge_keywords()

    def _merge_keywords(self) -> Dict[str, Set[str]]:
        """Merge custom keywords with default keyword sets."""
        return {
            "important_keywords": self.IMPORTANT_KEYWORDS | self.custom_keywords.get("important_keywords", set()),
            "reference_keywords": self.REFERENCE_KEYWORDS | self.custom_keywords.get("reference_keywords", set()),
            "instruction_keywords": self.INSTRUCTION_KEYWORDS | self.custom_keywords.get("instruction_keywords", set()),
            "configuration_keywords": self.CONFIGURATION_KEYWORDS | self.custom_keywords.get("configuration_keywords", set()),
            "api_keywords": self.API_KEYWORDS | self.custom_keywords.get("api_keywords", set()),
            "error_keywords": self.ERROR_KEYWORDS | self.custom_keywords.get("error_keywords", set()),
        }

    def process(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process parsed document and add semantic tags.

        Args:
            parsed: The parsed document dictionary.

        Returns:
            The document with semantic tags added.
        """
        result = parsed.copy()
        result["semantic_tags"] = {}

        # Tag sections
        if "sections" in result:
            result["sections"] = self._tag_sections(result["sections"])

        # Tag elements
        if "elements" in result:
            result["elements"] = self._tag_elements(result["elements"])

        # Add importance markers
        if self.include_importance:
            result["semantic_tags"]["importance"] = self._calculate_importance_markers(result)

        # Add relationships
        if self.include_relationships:
            result["semantic_tags"]["relationships"] = self._calculate_relationships(result)

        return result

    def _tag_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add semantic tags to sections.

        Args:
            sections: List of section dictionaries.

        Returns:
            Sections with semantic tags added.
        """
        tagged_sections = []

        for i, section in enumerate(sections):
            tagged = section.copy()
            tagged["semantic_tags"] = {}

            # Classify section type based on level and content
            tagged["semantic_tags"]["type"] = self._classify_section_type(section, i, len(sections))

            # Add content type
            tagged["semantic_tags"]["content_type"] = self._classify_content_type(section)

            # Add importance
            if self.include_importance:
                tagged["semantic_tags"]["importance"] = self._calculate_section_importance(section)

            # Add keywords found
            tagged["semantic_tags"]["keywords"] = self._extract_keywords(section)

            # Add reading order for AI
            tagged["semantic_tags"]["reading_order"] = i + 1

            tagged_sections.append(tagged)

        return tagged_sections

    def _tag_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add semantic tags to elements.

        Args:
            elements: List of element dictionaries.

        Returns:
            Elements with semantic tags added.
        """
        tagged_elements = []

        for element in elements:
            tagged = element.copy()
            tagged["semantic_tags"] = {}

            # Tag element type
            tagged["semantic_tags"]["content_type"] = self._classify_element_type(element)

            # Add importance
            if self.include_importance:
                tagged["semantic_tags"]["importance"] = self._calculate_element_importance(element)

            tagged_elements.append(tagged)

        return tagged_elements

    def _classify_section_type(
        self,
        section: Dict[str, Any],
        index: int,
        total: int
    ) -> str:
        """
        Classify the type of section based on its position and content.

        Args:
            section: The section dictionary.
            index: The section index.
            total: Total number of sections.

        Returns:
            The section type string.
        """
        title = section.get("title", "").lower()
        level = section.get("level", 1)

        # Check for specific section types by title
        for pattern, section_type in [
            (r'^introduction|^overview|^about', 'introduction'),
            (r'^conclusion|^summary|^final', 'conclusion'),
            (r'^table of contents|^toc', 'toc'),
            (r'^faq|^troubleshooting|^faq$', 'troubleshooting'),
            (r'^license|^copyright', 'legal'),
            (r'^appendix|^reference', 'reference'),
        ]:
            if re.search(pattern, title):
                return section_type

        # Classify by position and level
        if level == 1:
            if index == 0:
                return "introduction"
            elif index >= total - 1:
                return "conclusion"
            else:
                return "chapter"
        elif level == 2:
            return "subsection"
        else:
            return "subsubsection"

    def _classify_content_type(self, section: Dict[str, Any]) -> str:
        """
        Classify the content type of a section.

        Args:
            section: The section dictionary.

        Returns:
            The content type string.
        """
        title = section.get("title", "").lower()
        paragraphs = section.get("paragraphs", [])
        content = " ".join([
            section.get("title", ""),
            " ".join(p.get("content", "") for p in paragraphs)
        ]).lower()

        # Check for instruction content
        if self._contains_keywords(content, self._keywords["instruction_keywords"]):
            return "instruction"
        if self._contains_keywords(title, self._keywords["instruction_keywords"]):
            return "instruction"

        # Check for configuration content
        if self._contains_keywords(content, self._keywords["configuration_keywords"]):
            return "configuration"
        if self._contains_keywords(title, self._keywords["configuration_keywords"]):
            return "configuration"

        # Check for API documentation
        if self._contains_keywords(content, self._keywords["api_keywords"]):
            return "api_reference"
        if self._contains_keywords(title, self._keywords["api_keywords"]):
            return "api_reference"

        # Check for error/issue documentation
        if self._contains_keywords(content, self._keywords["error_keywords"]):
            return "error_reference"

        # Check for reference content
        if self._contains_keywords(content, self._keywords["reference_keywords"]):
            return "reference"

        return "explanation"

    def _classify_element_type(self, element: Dict[str, Any]) -> str:
        """
        Classify the type of an element.

        Args:
            element: The element dictionary.

        Returns:
            The element type string.
        """
        element_type = element.get("type", "unknown")
        content = element.get("content", "").lower()

        if element_type == "link":
            return "hyperlink"
        elif element_type == "image":
            return "media"
        elif element_type == "inline_code":
            return "code_reference"
        elif element_type == "list_item":
            if self._contains_keywords(content, self._keywords["instruction_keywords"]):
                return "instruction_step"
            return "list_item"
        elif element_type == "paragraph":
            if len(content.split()) < self.min_word_count:
                return "short_text"
            return "prose"

        return element_type

    def _calculate_section_importance(self, section: Dict[str, Any]) -> str:
        """
        Calculate the importance level of a section.

        Args:
            section: The section dictionary.

        Returns:
            The importance level string.
        """
        title = section.get("title", "").lower()
        content = " ".join([
            section.get("title", ""),
            " ".join(p.get("content", "") for p in section.get("paragraphs", []))
        ]).lower()

        # Check for critical keywords
        if any(kw in content for kw in self._keywords["important_keywords"]):
            return "critical"
        if any(kw in title for kw in self._keywords["important_keywords"]):
            return "important"

        # Code sections are typically important
        if "code" in title or "example" in title:
            return "important"

        # Configuration sections are important
        if self._contains_keywords(content, self._keywords["configuration_keywords"]):
            return "important"

        return "normal"

    def _calculate_element_importance(self, element: Dict[str, Any]) -> str:
        """
        Calculate the importance level of an element.

        Args:
            element: The element dictionary.

        Returns:
            The importance level string.
        """
        content = element.get("content", "").lower()
        element_type = element.get("type", "")

        # Code elements are important
        if element_type in ("code_reference", "inline_code"):
            return "important"

        # Links to external resources
        if element_type == "link":
            url = element.get("url", "").lower()
            if any(domain in url for domain in ["api.", "docs.", "reference."]):
                return "important"
            return "supplementary"

        # Short text is less important
        if len(content.split()) < self.min_word_count:
            return "supplementary"

        return "normal"

    def _extract_keywords(self, section: Dict[str, Any]) -> List[str]:
        """
        Extract relevant keywords from a section.

        Args:
            section: The section dictionary.

        Returns:
            List of extracted keywords.
        """
        title = section.get("title", "").lower()
        content = " ".join([
            section.get("title", ""),
            " ".join(p.get("content", "") for p in section.get("paragraphs", []))
        ]).lower()

        keywords: List[str] = []

        # Categorize by keyword types
        if self._contains_keywords(content, self._keywords["important_keywords"]):
            keywords.append("important")
        if self._contains_keywords(content, self._keywords["reference_keywords"]):
            keywords.append("reference")
        if self._contains_keywords(content, self._keywords["instruction_keywords"]):
            keywords.append("instruction")
        if self._contains_keywords(content, self._keywords["configuration_keywords"]):
            keywords.append("configuration")
        if self._contains_keywords(content, self._keywords["api_keywords"]):
            keywords.append("api")
        if self._contains_keywords(content, self._keywords["error_keywords"]):
            keywords.append("error")

        return list(set(keywords))

    def _calculate_importance_markers(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall importance markers for the document.

        Args:
            parsed: The parsed document dictionary.

        Returns:
            Dictionary of importance markers.
        """
        markers: Dict[str, Any] = {
            "has_critical": False,
            "has_important": False,
            "has_instructions": False,
            "has_configuration": False,
            "has_api_reference": False,
            "has_errors": False,
        }

        # Check sections
        for section in parsed.get("sections", []):
            tags = section.get("semantic_tags", {})
            importance = tags.get("importance", "normal")
            content_type = tags.get("content_type", "")

            if importance == "critical":
                markers["has_critical"] = True
            if importance == "important":
                markers["has_important"] = True
            if content_type == "instruction":
                markers["has_instructions"] = True
            if content_type == "configuration":
                markers["has_configuration"] = True
            if content_type == "api_reference":
                markers["has_api_reference"] = True
            if content_type == "error_reference":
                markers["has_errors"] = True

        return markers

    def _calculate_relationships(self, parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate relationships between sections.

        Args:
            parsed: The parsed document dictionary.

        Returns:
            List of relationship dictionaries.
        """
        relationships: List[Dict[str, Any]] = []
        sections = parsed.get("sections", [])

        for i, section in enumerate(sections):
            section_title = section.get("title", "")
            tags = section.get("semantic_tags", {})
            content_type = tags.get("content_type", "")

            # Find related sections based on content type
            if content_type == "reference":
                # Reference sections relate to introduction and body
                relationships.append({
                    "source": section_title,
                    "target": "introduction",
                    "type": "references",
                })

            # Parent-child relationships
            if i > 0:
                prev_section = sections[i - 1]
                if section.get("level", 1) > prev_section.get("level", 1):
                    relationships.append({
                        "source": prev_section.get("title", ""),
                        "target": section_title,
                        "type": "contains",
                    })

        return relationships

    def _contains_keywords(self, text: str, keywords: Set[str]) -> bool:
        """
        Check if text contains any of the keywords.

        Args:
            text: The text to check.
            keywords: Set of keywords to look for.

        Returns:
            True if any keyword is found, False otherwise.
        """
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return bool(words & keywords)
