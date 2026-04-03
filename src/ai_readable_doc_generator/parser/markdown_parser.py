"""
Markdown parser implementation.
"""

import re
from typing import Any, Dict, List, Optional

from ai_readable_doc_generator.parser.base import BaseParser, ParseError


class MarkdownParser(BaseParser):
    """Parser for Markdown documents."""

    # Patterns for Markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w*)\n([\s\S]*?)```', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s+(.+)$', re.MULTILINE)
    LIST_PATTERN = re.compile(r'^(\s*)[-*+]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^(\s*)\d+\.\s+(.+)$', re.MULTILINE)
    HORIZONTAL_RULE_PATTERN = re.compile(r'^[-*_]{3,}\s*$', re.MULTILINE)
    TABLE_PATTERN = re.compile(r'^\|.+\|\s*$')
    FRONT_MATTER_PATTERN = re.compile(r'^---\n([\s\S]*?)\n---', re.MULTILINE)

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Markdown parser.

        Args:
            config: Optional configuration dictionary.
                - extract_front_matter: Extract YAML front matter (default: True)
                - preserve_whitespace: Preserve whitespace in paragraphs (default: False)
                - heading_levels: Map heading levels to semantic types (default: {})
        """
        super().__init__(config)
        self.extract_front_matter = self.config.get("extract_front_matter", True)
        self.preserve_whitespace = self.config.get("preserve_whitespace", False)
        self.heading_levels = self.config.get("heading_levels", {})

    def validate(self, content: str) -> bool:
        """
        Validate if the content is valid Markdown.

        Args:
            content: The content to validate.

        Returns:
            True if content appears to be valid Markdown.
        """
        if not content or not isinstance(content, str):
            return False

        # Check for at least one Markdown element
        has_heading = bool(self.HEADING_PATTERN.search(content))
        has_code_block = '```' in content
        has_link = bool(self.LINK_PATTERN.search(content))
        has_list = bool(self.LIST_PATTERN.search(content) or self.ORDERED_LIST_PATTERN.search(content))

        return has_heading or has_code_block or has_link or has_list or len(content.strip()) > 0

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse Markdown content into a structured dictionary.

        Args:
            content: The Markdown content to parse.

        Returns:
            A dictionary containing the parsed document structure.

        Raises:
            ParseError: If parsing fails.
        """
        if not content:
            raise ParseError("Content cannot be empty")

        result: Dict[str, Any] = {
            "metadata": {},
            "sections": [],
            "elements": [],
            "statistics": {
                "total_lines": len(content.splitlines()),
                "total_characters": len(content),
            },
        }

        # Extract front matter if present
        if self.extract_front_matter:
            front_matter = self._extract_front_matter(content)
            if front_matter:
                result["metadata"]["front_matter"] = front_matter
                content = self.FRONT_MATTER_PATTERN.sub('', content)

        # Parse document structure
        lines = content.split('\n')
        current_section: Optional[Dict[str, Any]] = None
        current_paragraph: List[str] = []

        for i, line in enumerate(lines):
            processed_line = self._process_line(line, result["elements"])

            # Check if line is a heading
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                # Save current paragraph to current section
                if current_paragraph and current_section:
                    current_section.setdefault("paragraphs", []).append(
                        self._create_paragraph(current_paragraph)
                    )
                    current_paragraph = []

                # Save current section
                if current_section:
                    result["sections"].append(current_section)

                # Start new section
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                current_section = self._create_section(
                    level=level,
                    title=heading_text,
                    line_number=i + 1
                )
                continue

            # Check if line is empty
            if not line.strip():
                if current_paragraph:
                    if current_section:
                        current_section.setdefault("paragraphs", []).append(
                            self._create_paragraph(current_paragraph)
                        )
                    current_paragraph = []
                continue

            # Check if line is a list item
            list_match = self.LIST_PATTERN.match(line) or self.ORDERED_LIST_PATTERN.match(line)
            if list_match:
                if current_paragraph:
                    if current_section:
                        current_section.setdefault("paragraphs", []).append(
                            self._create_paragraph(current_paragraph)
                        )
                    current_paragraph = []

                list_item = self._create_list_item(line, list_match)
                if current_section:
                    current_section.setdefault("list_items", []).append(list_item)
                else:
                    result["elements"].append(list_item)
                continue

            # Check if line is a code block marker
            if line.strip().startswith('```'):
                continue

            # Regular content line
            if self.preserve_whitespace:
                current_paragraph.append(line)
            else:
                current_paragraph.append(line.strip())

        # Save final paragraph
        if current_paragraph:
            if current_section:
                current_section.setdefault("paragraphs", []).append(
                    self._create_paragraph(current_paragraph)
                )
            else:
                result["elements"].append(self._create_paragraph(current_paragraph))

        # Save final section
        if current_section:
            result["sections"].append(current_section)

        # Update statistics
        result["statistics"]["total_sections"] = len(result["sections"])
        result["statistics"]["total_elements"] = len(result["elements"])

        # Apply plugins
        result = self._apply_plugins(result)

        return result

    def _extract_front_matter(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract YAML front matter from content.

        Args:
            content: The content to extract from.

        Returns:
            A dictionary of front matter key-value pairs, or None if not found.
        """
        match = self.FRONT_MATTER_PATTERN.search(content)
        if not match:
            return None

        front_matter: Dict[str, Any] = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                front_matter[key.strip()] = value.strip()

        return front_matter

    def _process_line(self, line: str, elements: List[Dict[str, Any]]) -> str:
        """
        Process a line and extract inline elements.

        Args:
            line: The line to process.
            elements: List to append extracted elements to.

        Returns:
            The processed line content.
        """
        # Extract links
        for match in self.LINK_PATTERN.finditer(line):
            elements.append({
                "type": "link",
                "text": match.group(1),
                "url": match.group(2),
            })

        # Extract images
        for match in self.IMAGE_PATTERN.finditer(line):
            elements.append({
                "type": "image",
                "alt": match.group(1),
                "url": match.group(2),
            })

        # Extract inline code
        for match in self.INLINE_CODE_PATTERN.finditer(line):
            elements.append({
                "type": "inline_code",
                "code": match.group(1),
            })

        return line

    def _create_section(
        self,
        level: int,
        title: str,
        line_number: int
    ) -> Dict[str, Any]:
        """
        Create a section dictionary.

        Args:
            level: The heading level (1-6).
            title: The section title.
            line_number: The line number where the section starts.

        Returns:
            A dictionary representing the section.
        """
        semantic_type = self.heading_levels.get(level, f"h{level}")
        return {
            "type": "section",
            "semantic_type": semantic_type,
            "level": level,
            "title": title,
            "line_number": line_number,
        }

    def _create_paragraph(self, lines: List[str]) -> Dict[str, Any]:
        """
        Create a paragraph dictionary.

        Args:
            lines: The lines that make up the paragraph.

        Returns:
            A dictionary representing the paragraph.
        """
        content = ' '.join(lines) if not self.preserve_whitespace else '\n'.join(lines)
        return {
            "type": "paragraph",
            "content": content,
        }

    def _create_list_item(self, line: str, match: Any) -> Dict[str, Any]:
        """
        Create a list item dictionary.

        Args:
            line: The full line content.
            match: The regex match object.

        Returns:
            A dictionary representing the list item.
        """
        indent = len(match.group(1))
        text = match.group(2)
        return {
            "type": "list_item",
            "content": text,
            "indent": indent,
            "ordered": bool(self.ORDERED_LIST_PATTERN.match(line)),
        }
