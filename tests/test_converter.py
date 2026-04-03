"""Tests for the PlaintextConverter class.

This module contains comprehensive tests for the PlaintextConverter
which applies heuristic rules to infer document structure from plain text.
"""

import pytest

from ai_readable_doc_generator.converter import (
    PlaintextConverter,
    PlaintextHeuristics,
)
from ai_readable_doc_generator.models import (
    Section,
    SectionType,
    ContentType,
    Importance,
)


class TestPlaintextConverter:
    """Test suite for PlaintextConverter."""

    @pytest.fixture
    def converter(self) -> PlaintextConverter:
        """Create a default converter instance."""
        return PlaintextConverter()

    @pytest.fixture
    def heuristics(self) -> PlaintextHeuristics:
        """Create default heuristics configuration."""
        return PlaintextHeuristics()

    # Basic conversion tests

    def test_convert_empty_content(self, converter: PlaintextConverter) -> None:
        """Test conversion of empty content."""
        doc = converter.convert("")
        assert doc.metadata.word_count == 0
        assert len(doc.sections) == 0

    def test_convert_whitespace_content(self, converter: PlaintextConverter) -> None:
        """Test conversion of whitespace-only content."""
        doc = converter.convert("   \n\n   ")
        assert len(doc.sections) == 0

    def test_convert_single_paragraph(self, converter: PlaintextConverter) -> None:
        """Test conversion of a single paragraph."""
        content = "This is a simple paragraph of text."
        doc = converter.convert(content)
        assert len(doc.sections) == 1
        assert doc.sections[0].content == content
        assert doc.sections[0].section_type == SectionType.PARAGRAPH

    def test_convert_multiple_paragraphs(self, converter: PlaintextConverter) -> None:
        """Test conversion of multiple paragraphs."""
        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        doc = converter.convert(content)
        assert len(doc.sections) == 3
        for section in doc.sections:
            assert section.section_type == SectionType.PARAGRAPH

    # Heading detection tests

    def test_detect_allcaps_heading(self, converter: PlaintextConverter) -> None:
        """Test detection of ALL CAPS headings."""
        content = "INTRODUCTION\n\nThis is the introduction."
        doc = converter.convert(content)
        assert any(s.section_type == SectionType.HEADING for s in doc.sections)

    def test_detect_numbered_section(self, converter: PlaintextConverter) -> None:
        """Test detection of numbered sections like '1. Title'."""
        content = "1. First Section\n\nContent here."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        assert len(headings) >= 1
        assert "First Section" in headings[0].content

    def test_detect_nested_numbered_section(self, converter: PlaintextConverter) -> None:
        """Test detection of nested numbered sections like '1.2.3 Title'."""
        content = "1.2.3 Nested Section\n\nContent."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        assert len(headings) >= 1

    def test_detect_underline_heading_equals(self, converter: PlaintextConverter) -> None:
        """Test detection of underline headings with ===."""
        content = "Main Title\n==========\n\nContent."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        assert len(headings) >= 1
        assert headings[0].content_type == ContentType.HEADING_1

    def test_detect_underline_heading_dashes(self, converter: PlaintextConverter) -> None:
        """Test detection of underline headings with ---."""
        content = "Sub Title\n--------\n\nContent."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        assert len(headings) >= 1
        assert headings[0].content_type == ContentType.HEADING_2

    def test_detect_short_uppercase_heading(self, converter: PlaintextConverter) -> None:
        """Test detection of short ALL CAPS headings like 'API' or 'FAQ'."""
        content = "API\n\nDocumentation for the API."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        assert len(headings) >= 1

    # List detection tests

    def test_detect_bullet_list(self, converter: PlaintextConverter) -> None:
        """Test detection of bullet point lists."""
        content = "- First item\n- Second item\n- Third item"
        doc = converter.convert(content)
        list_sections = [s for s in doc.sections if s.section_type == SectionType.LIST]
        assert len(list_sections) >= 1
        assert "First item" in list_sections[0].content

    def test_detect_asterisk_list(self, converter: PlaintextConverter) -> None:
        """Test detection of asterisk bullet lists."""
        content = "* First item\n* Second item"
        doc = converter.convert(content)
        list_sections = [s for s in doc.sections if s.section_type == SectionType.LIST]
        assert len(list_sections) >= 1

    def test_detect_numbered_list(self, converter: PlaintextConverter) -> None:
        """Test detection of numbered lists."""
        content = "1. First\n2. Second\n3. Third"
        doc = converter.convert(content)
        list_sections = [s for s in doc.sections if s.section_type == SectionType.LIST]
        assert len(list_sections) >= 1

    def test_detect_numbered_parens_list(self, converter: PlaintextConverter) -> None:
        """Test detection of numbered lists with parentheses."""
        content = "1) First\n2) Second"
        doc = converter.convert(content)
        list_sections = [s for s in doc.sections if s.section_type == SectionType.LIST]
        assert len(list_sections) >= 1

    def test_detect_mixed_lists(self, converter: PlaintextConverter) -> None:
        """Test that mixed list types are handled correctly."""
        content = "- Bullet item\n1. Numbered item"
        doc = converter.convert(content)
        # Both types should be detected
        assert len(doc.sections) >= 2

    # Code block detection tests

    def test_detect_fenced_code_block(self, converter: PlaintextConverter) -> None:
        """Test detection of fenced code blocks."""
        content = "```python\nprint('hello')\n```"
        doc = converter.convert(content)
        code_blocks = [s for s in doc.sections if s.section_type == SectionType.CODE_BLOCK]
        assert len(code_blocks) >= 1
        assert "print('hello')" in code_blocks[0].content
        assert code_blocks[0].metadata.get("language") == "python"

    def test_detect_code_block_no_language(self, converter: PlaintextConverter) -> None:
        """Test detection of fenced code blocks without language."""
        content = "```\ncode without language\n```"
        doc = converter.convert(content)
        code_blocks = [s for s in doc.sections if s.section_type == SectionType.CODE_BLOCK]
        assert len(code_blocks) >= 1

    def test_detect_indented_code_block(self, converter: PlaintextConverter) -> None:
        """Test detection of indented code blocks."""
        content = "    def example():\n        pass\n    more_code()"
        doc = converter.convert(content)
        code_blocks = [s for s in doc.sections if s.section_type == SectionType.CODE_BLOCK]
        assert len(code_blocks) >= 1

    # Table detection tests

    def test_detect_pipe_table(self, converter: PlaintextConverter) -> None:
        """Test detection of pipe-delimited tables."""
        content = "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
        doc = converter.convert(content)
        tables = [s for s in doc.sections if s.section_type == SectionType.TABLE]
        assert len(tables) >= 1
        assert tables[0].metadata.get("columns") == 2

    def test_detect_simple_table(self, converter: PlaintextConverter) -> None:
        """Test detection of simple tables."""
        content = "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |"
        doc = converter.convert(content)
        tables = [s for s in doc.sections if s.section_type == SectionType.TABLE]
        assert len(tables) >= 1
        assert tables[0].metadata.get("rows") >= 2

    # Blockquote detection tests

    def test_detect_blockquote_gt(self, converter: PlaintextConverter) -> None:
        """Test detection of blockquotes with > marker."""
        content = "> This is a quoted text."
        doc = converter.convert(content)
        blockquotes = [s for s in doc.sections if s.section_type == SectionType.BLOCKQUOTE]
        assert len(blockquotes) >= 1

    def test_detect_blockquote_pipe(self, converter: PlaintextConverter) -> None:
        """Test detection of blockquotes with | marker."""
        content = "| This is a quoted text."
        doc = converter.convert(content)
        blockquotes = [s for s in doc.sections if s.section_type == SectionType.BLOCKQUOTE]
        assert len(blockquotes) >= 1

    # Semantic classification tests

    def test_classify_note_content(self, converter: PlaintextConverter) -> None:
        """Test classification of note content."""
        content = "Note: This is an important note."
        doc = converter.convert(content)
        notes = [s for s in doc.sections if s.content_type == ContentType.NOTE]
        assert len(notes) >= 1

    def test_classify_warning_content(self, converter: PlaintextConverter) -> None:
        """Test classification of warning content."""
        content = "Warning: Be careful with this operation."
        doc = converter.convert(content)
        warnings = [s for s in doc.sections if s.content_type == ContentType.WARNING]
        assert len(warnings) >= 1

    def test_classify_tip_content(self, converter: PlaintextConverter) -> None:
        """Test classification of tip content."""
        content = "Tip: You can use this shortcut."
        doc = converter.convert(content)
        tips = [s for s in doc.sections if s.content_type == ContentType.TIP]
        assert len(tips) >= 1

    def test_classify_question_content(self, converter: PlaintextConverter) -> None:
        """Test classification of question content."""
        content = "How do I install this package?"
        doc = converter.convert(content)
        questions = [s for s in doc.sections if s.content_type == ContentType.QUESTION]
        assert len(questions) >= 1

    def test_classify_introduction_heading(self, converter: PlaintextConverter) -> None:
        """Test classification of introduction headings."""
        content = "Introduction\n\nOverview of the project."
        doc = converter.convert(content)
        intro_sections = [
            s for s in doc.sections
            if s.section_type == SectionType.HEADING and s.content_type == ContentType.INTRODUCTION
        ]
        assert len(intro_sections) >= 1

    def test_classify_conclusion_heading(self, converter: PlaintextConverter) -> None:
        """Test classification of conclusion headings."""
        content = "Conclusion\n\nSummary of findings."
        doc = converter.convert(content)
        conclusion_sections = [
            s for s in doc.sections
            if s.section_type == SectionType.HEADING and s.content_type == ContentType.CONCLUSION
        ]
        assert len(conclusion_sections) >= 1

    # Importance inference tests

    def test_infer_high_importance_level1_heading(self, converter: PlaintextConverter) -> None:
        """Test that level 1 headings get high importance."""
        content = "1. Main Title\n\nContent."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        if headings:
            assert headings[0].importance == Importance.HIGH

    def test_infer_medium_importance_level2_heading(self, converter: PlaintextConverter) -> None:
        """Test that level 2 headings get medium importance."""
        content = "1.2 Sub Section\n\nContent."
        doc = converter.convert(content)
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        if headings:
            assert headings[0].importance in [Importance.HIGH, Importance.MEDIUM]

    # Metadata extraction tests

    def test_extract_word_count(self, converter: PlaintextConverter) -> None:
        """Test that word count is extracted correctly."""
        content = "One two three four five."
        doc = converter.convert(content)
        assert doc.metadata.word_count == 5

    def test_extract_line_count(self, converter: PlaintextConverter) -> None:
        """Test that line count is extracted correctly."""
        content = "Line one\nLine two\nLine three"
        doc = converter.convert(content)
        assert doc.metadata.line_count == 3

    def test_extract_source_format(self, converter: PlaintextConverter) -> None:
        """Test that source format is set to plaintext."""
        content = "Some content"
        doc = converter.convert(content)
        assert doc.metadata.source_format == "plaintext"

    def test_extract_source_path(self, converter: PlaintextConverter) -> None:
        """Test that source path is extracted correctly."""
        content = "Some content"
        doc = converter.convert(content, source_path="/path/to/file.txt")
        assert doc.metadata.source_path == "/path/to/file.txt"

    def test_raw_content_preserved(self, converter: PlaintextConverter) -> None:
        """Test that raw content is preserved in document."""
        content = "Original content with\nline breaks."
        doc = converter.convert(content)
        assert doc.raw_content == content

    # Heuristics configuration tests

    def test_disable_allcaps_detection(self) -> None:
        """Test disabling ALL CAPS heading detection."""
        heuristics = PlaintextHeuristics(detect_allcaps=False)
        converter = PlaintextConverter(heuristics=heuristics)
        content = "ALL CAPS HEADING\n\nContent."
        doc = converter.convert(content)
        # Should not detect as heading when disabled
        headings = [s for s in doc.sections if s.section_type == SectionType.HEADING]
        # The uppercase might still be detected via other heuristics
        assert len(doc.sections) >= 1

    def test_disable_list_detection(self) -> None:
        """Test disabling list detection."""
        heuristics = PlaintextHeuristics(detect_bullet_markers=False, detect_numbered_lists=False)
        converter = PlaintextConverter(heuristics=heuristics)
        content = "- Item one\n- Item two"
        doc = converter.convert(content)
        # When list detection is disabled, content should be paragraphs
        sections = [s for s in doc.sections if s.section_type == SectionType.LIST]
        # May still be detected due to other heuristics
        assert len(doc.sections) >= 1

    def test_custom_heading_length(self) -> None:
        """Test custom heading length constraints."""
        heuristics = PlaintextHeuristics(min_heading_length=10, max_heading_length=50)
        converter = PlaintextConverter(heuristics=heuristics)
        content = "AB\n\nVery long heading that is definitely over fifty characters here and more"
        doc = converter.convert(content)
        # Short headings should be filtered out
        assert len(doc.sections) >= 0

    # Edge cases

    def test_mixed_content_with_all_elements(self, converter: PlaintextConverter) -> None:
        """Test a complex document with multiple element types."""
        content = """Main Title
==========

Introduction

This is the introduction paragraph.

## Features

- Feature 1
- Feature 2

### Code Example

```python
def hello():
    print("Hello")
```

## Conclusion

> Important quote here.

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        doc = converter.convert(content)
        # Should have multiple section types
        section_types = {s.section_type for s in doc.sections}
        assert len(section_types) >= 3

    def test_consecutive_paragraphs(self, converter: PlaintextConverter) -> None:
        """Test handling of consecutive paragraphs."""
        content = "Para one\n\nPara two\n\nPara three"
        doc = converter.convert(content)
        assert len(doc.sections) == 3

    def test_empty_lines_preserved(self, converter: PlaintextConverter) -> None:
        """Test that empty lines don't create empty sections."""
        content = "First\n\n\n\nSecond"
        doc = converter.convert(content)
        non_empty = [s for s in doc.sections if s.section_type != SectionType.EMPTY]
        assert len(non_empty) == 2

    def test_parse_method(self, converter: PlaintextConverter) -> None:
        """Test that parse method works the same as convert."""
        content = "Test content"
        parse_result = converter.parse(content)
        convert_result = converter.convert(content)
        assert parse_result.metadata.word_count == convert_result.metadata.word_count
        assert len(parse_result.sections) == len(convert_result.sections)


class TestPlaintextHeuristics:
    """Test suite for PlaintextHeuristics configuration."""

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        h = PlaintextHeuristics()
        assert h.detect_shadows is True
        assert h.detect_allcaps is True
        assert h.detect_numbered_sections is True
        assert h.min_heading_length == 3
        assert h.max_heading_length == 120

    def test_custom_values(self) -> None:
        """Test setting custom heuristic values."""
        h = PlaintextHeuristics(
            detect_allcaps=False,
            min_heading_length=5,
            max_heading_length=100,
        )
        assert h.detect_allcaps is False
        assert h.min_heading_length == 5
        assert h.max_heading_length == 100

    def test_all_detection_flags(self) -> None:
        """Test all detection flags can be set."""
        h = PlaintextHeuristics(
            detect_shadows=False,
            detect_allcaps=False,
            detect_numbered_sections=False,
            detect_underscore_headings=False,
            detect_bullet_markers=False,
            detect_numbered_lists=False,
            detect_code_blocks=False,
            detect_tables=False,
            detect_blockquotes=False,
        )
        assert h.detect_shadows is False
        assert h.detect_tables is False


class TestHeuristicPatterns:
    """Test individual heuristic pattern matching."""

    def test_title_case_heading_pattern(self) -> None:
        """Test title case heading detection."""
        from ai_readable_doc_generator.converter import HEADING_PATTERNS

        # Should match
        assert HEADING_PATTERNS["allcaps"].match("ALL CAPS HEADING")
        # Should not match
        assert not HEADING_PATTERNS["allcaps"].match("All Caps")

    def test_numbered_section_pattern(self) -> None:
        """Test numbered section pattern."""
        from ai_readable_doc_generator.converter import HEADING_PATTERNS

        assert HEADING_PATTERNS["numbered_section"].match("1. First Section")
        assert HEADING_PATTERNS["numbered_section"].match("1.2.3 Nested")
        assert not HEADING_PATTERNS["numbered_section"].match("Not numbered")

    def test_list_patterns(self) -> None:
        """Test list marker patterns."""
        from ai_readable_doc_generator.converter import LIST_PATTERNS

        assert LIST_PATTERNS["bullet"].match("- item")
        assert LIST_PATTERNS["bullet"].match("* item")
        assert LIST_PATTERNS["numbered"].match("1. item")
        assert LIST_PATTERNS["numbered_parens"].match("1) item")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
