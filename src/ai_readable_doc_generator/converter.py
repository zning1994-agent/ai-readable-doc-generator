"""
PlaintextConverter - Heuristic-based structure inference for plain text.

This converter applies various heuristic rules to infer document structure
from plain text without explicit markup. It detects patterns like:
- Headings (uppercase, numbered sections, etc.)
- Lists (bullet points, numbered lists, markers)
- Code blocks (fenced and unfenced)
- Tables (pipe-delimited and alignment-based)
- Blockquotes (indented text, quote markers)
- Paragraphs (line break patterns)
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from ai_readable_doc_generator.base import BaseConverter
from ai_readable_doc_generator.models import (
    Document,
    DocumentMetadata,
    Section,
    SectionType,
    ContentType,
    Importance,
)


@dataclass
class PlaintextHeuristics:
    """
    Configuration for heuristic rules used in PlaintextConverter.

    Attributes:
        detect_shadows: Detect title case headings (Title Case with shadow words).
        detect_allcaps: Detect ALL CAPS as potential headings.
        detect_numbered_sections: Detect patterns like "1. Title" or "1.1 Title".
        detect_underscore_headings: Detect underline headings (=== or ---).
        detect_bullet_markers: Detect bullet points (-, *, +, •, etc.).
        detect_numbered_lists: Detect numbered list patterns (1., 1), etc.).
        detect_code_blocks: Detect code block patterns (fenced and indent-based).
        detect_tables: Detect table structures (pipe-delimited, alignment).
        detect_blockquotes: Detect blockquote patterns (>, |, etc.).
        min_heading_length: Minimum length for inferred headings.
        max_heading_length: Maximum length for inferred headings.
        code_block_indent: Indentation level for code block detection.
    """

    detect_shadows: bool = True
    detect_allcaps: bool = True
    detect_numbered_sections: bool = True
    detect_underscore_headings: bool = True
    detect_bullet_markers: bool = True
    detect_numbered_lists: bool = True
    detect_code_blocks: bool = True
    detect_tables: bool = True
    detect_blockquotes: bool = True
    min_heading_length: int = 3
    max_heading_length: int = 120
    code_block_indent: int = 4


# Shadow words that indicate a heading when capitalized
SHADOW_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can",
    "her", "was", "one", "our", "out", "day", "get", "has", "him",
    "his", "how", "its", "may", "new", "now", "old", "see", "two",
    "way", "who", "boy", "did", "own", "say", "she", "too", "use",
}

# Common heading patterns
HEADING_PATTERNS = {
    "allcaps": re.compile(r"^[A-Z][A-Z\s]{5,}[A-Z]$"),
    "title_shadow": re.compile(r"^[A-Z][a-z]*(?:[A-Z][a-z]*)+\s+(?:{})".format(
        "|".join(SHADOW_WORDS)
    )),
    "numbered_section": re.compile(r"^\d+(?:\.\d+)*\.\s+.+"),
    "numbered_parens": re.compile(r"^\d+\)\s+.+"),
    "roman_numeral": re.compile(r"^[IVXLC]+\.\s+.+"),
    "underline_eq": re.compile(r"^=+$"),
    "underline_dash": re.compile(r"^-+$"),
    "markdown_heading": re.compile(r"^#{1,6}\s+.+"),
}

# List marker patterns
LIST_PATTERNS = {
    "bullet": re.compile(r"^[\-\*\+•·]\s+"),
    "numbered": re.compile(r"^\d+\.\s+"),
    "numbered_parens": re.compile(r"^\d+\)\s+"),
    "letter_bullet": re.compile(r"^[a-z]\)\s+"),
    "letter_dot": re.compile(r"^[a-z]\.\s+"),
    "check_box": re.compile(r"^\[[\s\-xX✓]\]\s*"),
}

# Code block patterns
CODE_PATTERNS = {
    "fenced_start": re.compile(r"^```(\w*)\s*$"),
    "fenced_end": re.compile(r"^```\s*$"),
    "indented": re.compile(r"^\s{4,}"),
    "leading_whitespace": re.compile(r"^\s+"),
}

# Table patterns
TABLE_PATTERNS = {
    "pipe_delimited": re.compile(r"^\|.+\|\s*$"),
    "alignment": re.compile(r"^\|?[\s\-:]+\|\s*$"),
    "simple_table": re.compile(r"^\S+\s+\S+(\s+\S+)+\s*$"),
}

# Blockquote patterns
BLOCKQUOTE_PATTERNS = {
    "gt_marker": re.compile(r"^>\s*"),
    "pipe_quote": re.compile(r"^\|\s*"),
}

# Semantic classification patterns
SEMANTIC_PATTERNS = {
    "note": re.compile(r"^(?:note:|NOTE:|Note:)\s*", re.IGNORECASE),
    "warning": re.compile(r"^(?:warning:|WARNING:|Caution:|CAUTION:|⚠️?)\s*", re.IGNORECASE),
    "tip": re.compile(r"^(?:tip:|TIP:|Tip:|💡)\s*", re.IGNORECASE),
    "important": re.compile(r"^(?:important:|IMPORTANT:|Important:)\s*", re.IGNORECASE),
    "question": re.compile(r"^(?:\?|Q:)\s*"),
    "answer": re.compile(r"^(?:A:|Answer:)\s*"),
    "definition": re.compile(r"^:\s+\w+"),
    "citation": re.compile(r"^\[.*\]\(.*\)|^https?://"),
    "code_ref": re.compile(r"`[^`]+`"),
}


class PlaintextConverter(BaseConverter):
    """
    Converter that applies heuristic rules to infer structure from plain text.

    This converter analyzes text patterns to detect document structure elements
    like headings, lists, code blocks, tables, and semantic content types.

    Example:
        >>> converter = PlaintextConverter()
        >>> content = "Introduction\\n\\nThis is a paragraph.\\n\\n1. First item\\n2. Second item"
        >>> doc = converter.convert(content)
        >>> print(len(doc.sections))
        3
    """

    def __init__(
        self,
        heuristics: Optional[PlaintextHeuristics] = None,
        schema: Optional["OutputSchema"] = None,
        options: Optional[dict] = None,
    ) -> None:
        """
        Initialize the PlaintextConverter.

        Args:
            heuristics: Heuristic configuration. Uses defaults if not provided.
            schema: Output schema to use.
            options: Additional conversion options.
        """
        super().__init__(schema, options)
        self.heuristics = heuristics or PlaintextHeuristics()

    def convert(self, content: str, source_path: str = "") -> Document:
        """
        Convert plain text content to a structured Document.

        Args:
            content: Raw plain text content.
            source_path: Optional source file path.

        Returns:
            Structured Document with inferred sections and metadata.
        """
        if not self.validate_content(content):
            return Document()

        lines = content.split("\n")
        sections = self._parse_lines(lines)

        metadata = self._extract_metadata(content, source_path)
        document = Document(metadata=metadata, sections=sections, raw_content=content)

        return document

    def parse(self, content: str) -> Document:
        """
        Parse content into sections with basic structure inference.

        Args:
            content: Raw plain text content.

        Returns:
            Parsed Document with sections.
        """
        return self.convert(content)

    def _parse_lines(self, lines: list[str]) -> list[Section]:
        """
        Parse lines into sections using heuristic rules.

        Args:
            lines: List of content lines.

        Returns:
            List of parsed Section objects.
        """
        sections = []
        current_paragraph_lines = []
        in_code_block = False
        code_block_lines = []
        code_block_lang = ""
        current_list_items: list[str] = []
        current_list_type: Optional[str] = None

        def _flush_paragraph() -> Optional[Section]:
            """Flush accumulated paragraph lines into a section."""
            nonlocal current_paragraph_lines
            if not current_paragraph_lines:
                return None
            content = " ".join(current_paragraph_lines).strip()
            current_paragraph_lines = []
            if not content:
                return None
            section = self._create_paragraph_section(content)
            return section

        def _flush_list() -> Optional[Section]:
            """Flush accumulated list items into a list section."""
            nonlocal current_list_items, current_list_type
            if not current_list_items:
                return None
            section = self._create_list_section(current_list_items, current_list_type or "bullet")
            current_list_items = []
            current_list_type = None
            return section

        for i, line in enumerate(lines):
            # Handle code blocks
            if self.heuristics.detect_code_blocks:
                fenced_match = CODE_PATTERNS["fenced_start"].match(line)
                if fenced_match:
                    if not in_code_block:
                        # Flush pending content
                        para = _flush_paragraph()
                        if para:
                            sections.append(para)
                        lst = _flush_list()
                        if lst:
                            sections.append(lst)
                        in_code_block = True
                        code_block_lang = fenced_match.group(1) or ""
                        code_block_lines = []
                        continue
                    else:
                        # End code block
                        in_code_block = False
                        sections.append(self._create_code_section(code_block_lines, code_block_lang))
                        code_block_lines = []
                        code_block_lang = ""
                        continue

                if in_code_block:
                    code_block_lines.append(line)
                    continue

            # Handle indented code blocks
            if self.heuristics.detect_code_blocks and CODE_PATTERNS["indented"].match(line):
                para = _flush_paragraph()
                if para:
                    sections.append(para)
                lst = _flush_list()
                if lst:
                    sections.append(lst)
                # Collect all indented lines
                j = i
                indented_lines = []
                while j < len(lines) and CODE_PATTERNS["indented"].match(lines[j]):
                    indented_lines.append(lines[j])
                    j += 1
                sections.append(self._create_code_section(indented_lines, ""))
                continue

            # Handle headings
            heading_result = self._detect_heading(line)
            if heading_result:
                para = _flush_paragraph()
                if para:
                    sections.append(para)
                lst = _flush_list()
                if lst:
                    sections.append(lst)
                sections.append(heading_result)
                continue

            # Handle underline headings
            if i > 0 and i < len(lines) - 1:
                underline_result = self._detect_underline_heading(lines[i - 1], line, lines[i + 1])
                if underline_result:
                    # Replace the previous paragraph-like section
                    if sections and sections[-1].section_type == SectionType.PARAGRAPH:
                        sections[-1] = underline_result
                        continue

            # Handle lists
            list_result = self._detect_list_item(line)
            if list_result:
                list_type = list_result[1]
                if current_list_type == list_type:
                    current_list_items.append(list_result[0])
                else:
                    lst = _flush_list()
                    if lst:
                        sections.append(lst)
                    current_list_type = list_type
                    current_list_items = [list_result[0]]
                continue
            else:
                lst = _flush_list()
                if lst:
                    sections.append(lst)

            # Handle tables
            if self.heuristics.detect_tables:
                table_lines = self._detect_table(lines, i)
                if table_lines:
                    para = _flush_paragraph()
                    if para:
                        sections.append(para)
                    sections.append(self._create_table_section(table_lines))
                    i += len(table_lines) - 1
                    continue

            # Handle blockquotes
            if self.heuristics.detect_blockquotes:
                bq_result = self._detect_blockquote(line)
                if bq_result:
                    para = _flush_paragraph()
                    if para:
                        sections.append(para)
                    sections.append(bq_result)
                    continue

            # Handle empty lines and paragraphs
            if not line.strip():
                para = _flush_paragraph()
                if para:
                    sections.append(para)
            else:
                current_paragraph_lines.append(line.strip())

        # Flush remaining content
        para = _flush_paragraph()
        if para:
            sections.append(para)
        lst = _flush_list()
        if lst:
            sections.append(lst)

        # Apply semantic classification to all sections
        sections = self._classify_semantics(sections)

        return sections

    def _detect_heading(self, line: str) -> Optional[Section]:
        """
        Detect if a line is a heading using heuristic patterns.

        Args:
            line: Line to analyze.

        Returns:
            Section if heading detected, None otherwise.
        """
        stripped = line.strip()
        if not stripped:
            return None

        # Check length constraints
        if len(stripped) < self.heuristics.min_heading_length:
            return None
        if len(stripped) > self.heuristics.max_heading_length:
            return None

        # Check numbered sections (1. Title, 1.1 Title, etc.)
        if self.heuristics.detect_numbered_sections:
            if HEADING_PATTERNS["numbered_section"].match(stripped):
                level = stripped.split(".").__len__() - 1
                level = min(level, 6)
                return Section(
                    content=re.sub(r"^\d+(?:\.\d+)*\.\s*", "", stripped),
                    section_type=SectionType.HEADING,
                    content_type=self._classify_heading_type(stripped),
                    level=level,
                    importance=self._infer_heading_importance(level),
                    raw_text=line,
                )
            if HEADING_PATTERNS["numbered_parens"].match(stripped):
                return Section(
                    content=re.sub(r"^\d+\)\s*", "", stripped),
                    section_type=SectionType.HEADING,
                    content_type=self._classify_heading_type(stripped),
                    level=1,
                    importance=Importance.HIGH,
                    raw_text=line,
                )

        # Check ALL CAPS headings
        if self.heuristics.detect_allcaps:
            if HEADING_PATTERNS["allcaps"].match(stripped):
                # Exclude lines that look like abbreviations or short caps
                if len(stripped) >= 10:
                    return Section(
                        content=stripped,
                        section_type=SectionType.HEADING,
                        content_type=ContentType.HEADING_1,
                        level=1,
                        importance=Importance.HIGH,
                        raw_text=line,
                    )

        # Check shadow title headings (Title Case with shadow words)
        if self.heuristics.detect_shadows:
            if HEADING_PATTERNS["title_shadow"].match(stripped):
                # Ensure at least one non-shadow word capitalized
                words = stripped.split()
                capitalized_non_shadow = any(
                    w.rstrip(",.:").istitle() and w.lower().rstrip(",.:") not in SHADOW_WORDS
                    for w in words
                )
                if capitalized_non_shadow:
                    return Section(
                        content=stripped,
                        section_type=SectionType.HEADING,
                        content_type=self._classify_heading_type(stripped),
                        level=self._infer_heading_level(stripped),
                        importance=Importance.MEDIUM,
                        raw_text=line,
                    )

        # Check short uppercase lines (SHORTCUT style)
        if self.heuristics.detect_allcaps:
            if re.match(r"^[A-Z]{2,}(?:\s+[A-Z]{2,})*$", stripped) and len(stripped) <= 30:
                return Section(
                    content=stripped,
                    section_type=SectionType.HEADING,
                    content_type=self._classify_heading_type(stripped),
                    level=self._infer_heading_level(stripped),
                    importance=Importance.MEDIUM,
                    raw_text=line,
                )

        return None

    def _detect_underline_heading(
        self, line_above: str, underline: str, line_below: str
    ) -> Optional[Section]:
        """
        Detect underline headings (=== or ---).

        Args:
            line_above: Line above the underline.
            underline: The underline line.
            line_below: Line below the underline.

        Returns:
            Section if underline heading detected, None otherwise.
        """
        if not self.heuristics.detect_underscore_headings:
            return None

        if not line_above.strip():
            return None

        if HEADING_PATTERNS["underline_eq"].match(underline.strip()):
            return Section(
                content=line_above.strip(),
                section_type=SectionType.HEADING,
                content_type=ContentType.HEADING_1,
                level=1,
                importance=Importance.HIGH,
                raw_text=f"{line_above}\n{underline}",
            )

        if HEADING_PATTERNS["underline_dash"].match(underline.strip()):
            return Section(
                content=line_above.strip(),
                section_type=SectionType.HEADING,
                content_type=ContentType.HEADING_2,
                level=2,
                importance=Importance.MEDIUM,
                raw_text=f"{line_above}\n{underline}",
            )

        return None

    def _detect_list_item(self, line: str) -> Optional[tuple[str, str]]:
        """
        Detect if a line is a list item.

        Args:
            line: Line to analyze.

        Returns:
            Tuple of (content, list_type) if detected, None otherwise.
        """
        stripped = line.strip()
        if not stripped:
            return None

        # Check bullet markers
        if self.heuristics.detect_bullet_markers:
            for name, pattern in LIST_PATTERNS.items():
                match = pattern.match(stripped)
                if match:
                    content = stripped[match.end():].strip()
                    return (content, name)

        return None

    def _detect_table(self, lines: list[str], start_idx: int) -> Optional[list[str]]:
        """
        Detect a table structure starting at given index.

        Args:
            lines: All lines.
            start_idx: Starting index.

        Returns:
            List of table lines if detected, None otherwise.
        """
        if not self.heuristics.detect_tables:
            return None

        if start_idx >= len(lines):
            return None

        line = lines[start_idx]
        stripped = line.strip()

        # Check for pipe-delimited first row
        if not TABLE_PATTERNS["pipe_delimited"].match(stripped):
            return None

        table_lines = [stripped]
        i = start_idx + 1

        # Look for header separator row
        if i < len(lines) and TABLE_PATTERNS["alignment"].match(lines[i].strip()):
            table_lines.append(lines[i].strip())
            i += 1

        # Look for data rows
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if TABLE_PATTERNS["pipe_delimited"].match(next_line):
                table_lines.append(next_line)
                i += 1
            elif TABLE_PATTERNS["alignment"].match(next_line):
                # Alignment row at end of table
                table_lines.append(next_line)
                break
            else:
                break

        # Valid table should have at least 2 rows
        if len(table_lines) >= 2:
            return table_lines

        return None

    def _detect_blockquote(self, line: str) -> Optional[Section]:
        """
        Detect if a line is a blockquote.

        Args:
            line: Line to analyze.

        Returns:
            Section if blockquote detected, None otherwise.
        """
        stripped = line.strip()
        if not stripped:
            return None

        for name, pattern in BLOCKQUOTE_PATTERNS.items():
            match = pattern.match(stripped)
            if match:
                content = stripped[match.end():].strip()
                return Section(
                    content=content,
                    section_type=SectionType.BLOCKQUOTE,
                    content_type=ContentType.CITATION,
                    importance=Importance.LOW,
                    raw_text=line,
                )

        return None

    def _create_paragraph_section(self, content: str) -> Section:
        """
        Create a paragraph section.

        Args:
            content: Paragraph content.

        Returns:
            Section for the paragraph.
        """
        semantic_type = self._classify_paragraph_semantics(content)
        return Section(
            content=content,
            section_type=SectionType.PARAGRAPH,
            content_type=semantic_type,
            importance=self._infer_paragraph_importance(semantic_type),
        )

    def _create_list_section(self, items: list[str], list_type: str) -> Section:
        """
        Create a list section from items.

        Args:
            items: List item contents.
            list_type: Type of list (bullet, numbered, etc.).

        Returns:
            Section for the list.
        """
        list_content = "\n".join(f"- {item}" for item in items)
        return Section(
            content=list_content,
            section_type=SectionType.LIST,
            content_type=ContentType.LIST_ITEM,
            metadata={"list_type": list_type, "item_count": len(items)},
        )

    def _create_code_section(self, lines: list[str], language: str) -> Section:
        """
        Create a code block section.

        Args:
            lines: Code block lines.
            language: Programming language (if detected).

        Returns:
            Section for the code block.
        """
        # Remove leading indentation if present
        content = "\n".join(lines)
        return Section(
            content=content,
            section_type=SectionType.CODE_BLOCK,
            content_type=ContentType.CODE_EXAMPLE,
            importance=Importance.MEDIUM,
            metadata={"language": language} if language else {},
            raw_text=content,
        )

    def _create_table_section(self, lines: list[str]) -> Section:
        """
        Create a table section.

        Args:
            lines: Table lines including header and separator.

        Returns:
            Section for the table.
        """
        content = "\n".join(lines)
        # Count columns from first row
        first_row_cols = len([c.strip() for c in lines[0].split("|") if c.strip()])
        return Section(
            content=content,
            section_type=SectionType.TABLE,
            content_type=ContentType.UNCLASSIFIED,
            importance=Importance.MEDIUM,
            metadata={"columns": first_row_cols, "rows": len(lines)},
            raw_text=content,
        )

    def _classify_heading_type(self, heading: str) -> ContentType:
        """
        Classify the type of heading based on content.

        Args:
            heading: Heading text.

        Returns:
            ContentType classification.
        """
        lower = heading.lower()

        # Check for common heading types
        if any(word in lower for word in ["introduction", "overview", "summary"]):
            return ContentType.INTRODUCTION
        if any(word in lower for word in ["conclusion", "summary", "wrap-up"]):
            return ContentType.CONCLUSION
        if any(word in lower for word in ["example", "examples"]):
            return ContentType.CODE_EXAMPLE
        if any(word in lower for word in ["note", "warning", "tip", "caution"]):
            return ContentType.NOTE
        if lower.endswith("?") or lower.startswith("how") or lower.startswith("what"):
            return ContentType.QUESTION
        if any(word in lower for word in ["definition", "term"]):
            return ContentType.DEFINITION

        return ContentType.BODY

    def _classify_paragraph_semantics(self, content: str) -> ContentType:
        """
        Classify semantic type of a paragraph.

        Args:
            content: Paragraph content.

        Returns:
            ContentType classification.
        """
        for semantic_name, pattern in SEMANTIC_PATTERNS.items():
            if pattern.search(content):
                mapping = {
                    "note": ContentType.NOTE,
                    "warning": ContentType.WARNING,
                    "tip": ContentType.TIP,
                    "important": ContentType.NOTE,
                    "question": ContentType.QUESTION,
                    "answer": ContentType.ANSWER,
                    "definition": ContentType.DEFINITION,
                    "citation": ContentType.CITATION,
                }
                return mapping.get(semantic_name, ContentType.UNCLASSIFIED)

        return ContentType.BODY

    def _infer_heading_level(self, heading: str) -> int:
        """
        Infer heading level from formatting.

        Args:
            heading: Heading text.

        Returns:
            Heading level (1-6).
        """
        if len(heading) < 20:
            return 1
        if len(heading) < 40:
            return 2
        return 3

    def _infer_heading_importance(self, level: int) -> Importance:
        """
        Infer importance from heading level.

        Args:
            level: Heading level.

        Returns:
            Importance level.
        """
        if level == 1:
            return Importance.CRITICAL
        if level == 2:
            return Importance.HIGH
        return Importance.MEDIUM

    def _infer_paragraph_importance(self, content_type: ContentType) -> Importance:
        """
        Infer importance from paragraph content type.

        Args:
            content_type: Content type classification.

        Returns:
            Importance level.
        """
        high_importance_types = {
            ContentType.WARNING,
            ContentType.IMPORTANT,
            ContentType.QUESTION,
        }
        medium_importance_types = {
            ContentType.NOTE,
            ContentType.TIP,
            ContentType.DEFINITION,
            ContentType.CODE_EXAMPLE,
        }

        if content_type in high_importance_types:
            return Importance.HIGH
        if content_type in medium_importance_types:
            return Importance.MEDIUM
        return Importance.LOW

    def _classify_semantics(self, sections: list[Section]) -> list[Section]:
        """
        Apply semantic classification to all sections.

        Args:
            sections: List of sections to classify.

        Returns:
            Classified sections.
        """
        # Track context for better classification
        context_stack = []

        for section in sections:
            if section.section_type == SectionType.HEADING:
                # Update context based on heading
                context_stack = context_stack[: section.level]
                context_stack.append(section.content)

            elif section.section_type == SectionType.PARAGRAPH:
                # Enhance classification based on context
                if context_stack:
                    context_text = " ".join(context_stack).lower()
                    if "example" in context_text:
                        section.content_type = ContentType.CODE_EXAMPLE
                    elif "note" in context_text or "warning" in context_text:
                        section.content_type = ContentType.NOTE

        return sections

    def _extract_metadata(self, content: str, source_path: str) -> DocumentMetadata:
        """
        Extract metadata from content.

        Args:
            content: Full document content.
            source_path: Source file path.

        Returns:
            DocumentMetadata instance.
        """
        lines = content.split("\n")
        word_count = len(content.split())
        line_count = len(lines)

        # Try to extract title from first heading
        title = ""
        for line in lines[:10]:  # Check first 10 lines
            heading = self._detect_heading(line)
            if heading and heading.content:
                title = heading.content
                break

        # Extract tags from common patterns
        tags = []
        tag_pattern = re.compile(r"^\s*tags?\s*:\s*(.+)$", re.IGNORECASE)
        for line in lines[:20]:
            match = tag_pattern.match(line)
            if match:
                tags = [t.strip() for t in match.group(1).split(",")]
                break

        return DocumentMetadata(
            title=title,
            source_path=source_path,
            source_format="plaintext",
            word_count=word_count,
            line_count=line_count,
            tags=tags,
            created_at=datetime.now(),
        )


# Export the converter class
__all__ = ["PlaintextConverter", "PlaintextHeuristics"]
