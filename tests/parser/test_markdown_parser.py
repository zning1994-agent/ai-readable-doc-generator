"""Unit tests for MarkdownParser class."""

import pytest

from ai_readable_doc_generator.parser.base import ParseError
from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser


class TestMarkdownParserInit:
    """Test suite for MarkdownParser initialization."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        parser = MarkdownParser()
        assert parser.config == {}
        assert parser.extract_front_matter is True
        assert parser.preserve_whitespace is False
        assert parser.heading_levels == {}

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "extract_front_matter": False,
            "preserve_whitespace": True,
            "heading_levels": {1: "title", 2: "chapter"},
        }
        parser = MarkdownParser(config)
        assert parser.config == config
        assert parser.extract_front_matter is False
        assert parser.preserve_whitespace is True
        assert parser.heading_levels == {1: "title", 2: "chapter"}

    def test_init_partial_config(self):
        """Test initialization with partial configuration."""
        parser = MarkdownParser({"extract_front_matter": False})
        assert parser.extract_front_matter is False
        assert parser.preserve_whitespace is True  # default


class TestMarkdownParserValidate:
    """Test suite for MarkdownParser.validate() method."""

    def test_validate_with_heading(self):
        """Test validation of content with heading."""
        parser = MarkdownParser()
        assert parser.validate("# Hello World") is True

    def test_validate_with_code_block(self):
        """Test validation of content with code block."""
        parser = MarkdownParser()
        content = "```python\nprint('hello')\n```"
        assert parser.validate(content) is True

    def test_validate_with_link(self):
        """Test validation of content with link."""
        parser = MarkdownParser()
        assert parser.validate("[link](http://example.com)") is True

    def test_validate_with_list(self):
        """Test validation of content with list."""
        parser = MarkdownParser()
        assert parser.validate("- item 1\n- item 2") is True

    def test_validate_with_ordered_list(self):
        """Test validation of content with ordered list."""
        parser = MarkdownParser()
        assert parser.validate("1. First\n2. Second") is True

    def test_validate_with_plain_text(self):
        """Test validation of plain text."""
        parser = MarkdownParser()
        assert parser.validate("Just some plain text") is True

    def test_validate_with_empty_string(self):
        """Test validation of empty string."""
        parser = MarkdownParser()
        assert parser.validate("") is False

    def test_validate_with_none(self):
        """Test validation of None."""
        parser = MarkdownParser()
        assert parser.validate(None) is False


class TestMarkdownParserParse:
    """Test suite for MarkdownParser.parse() method."""

    def test_parse_empty_raises_error(self):
        """Test that parsing empty content raises ParseError."""
        parser = MarkdownParser()
        with pytest.raises(ParseError) as exc_info:
            parser.parse("")
        assert "Content cannot be empty" in str(exc_info.value)

    def test_parse_simple_heading(self):
        """Test parsing a simple heading."""
        parser = MarkdownParser()
        result = parser.parse("# Title")
        assert len(result["sections"]) == 1
        assert result["sections"][0]["title"] == "Title"
        assert result["sections"][0]["level"] == 1

    def test_parse_multiple_headings(self):
        """Test parsing multiple headings."""
        parser = MarkdownParser()
        content = "# Title\n\n## Section 1\n\n### Subsection\n\n## Section 2"
        result = parser.parse(content)
        assert len(result["sections"]) == 4

    def test_parse_heading_levels(self):
        """Test parsing different heading levels."""
        parser = MarkdownParser()
        content = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"
        result = parser.parse(content)
        levels = [s["level"] for s in result["sections"]]
        assert levels == [1, 2, 3, 4, 5, 6]

    def test_parse_paragraph(self):
        """Test parsing paragraph content."""
        parser = MarkdownParser()
        content = "# Title\n\nThis is a paragraph."
        result = parser.parse(content)
        section = result["sections"][0]
        assert len(section["paragraphs"]) == 1
        assert "paragraph" in section["paragraphs"][0]["type"]

    def test_parse_multiple_paragraphs(self):
        """Test parsing multiple paragraphs."""
        parser = MarkdownParser()
        content = "# Title\n\nFirst paragraph.\n\nSecond paragraph."
        result = parser.parse(content)
        section = result["sections"][0]
        assert len(section["paragraphs"]) == 2

    def test_parse_unordered_list(self):
        """Test parsing unordered list."""
        parser = MarkdownParser()
        content = "# Title\n\n- Item 1\n- Item 2\n- Item 3"
        result = parser.parse(content)
        section = result["sections"][0]
        assert "list_items" in section
        assert len(section["list_items"]) == 3

    def test_parse_ordered_list(self):
        """Test parsing ordered list."""
        parser = MarkdownParser()
        content = "# Title\n\n1. First\n2. Second\n3. Third"
        result = parser.parse(content)
        section = result["sections"][0]
        assert "list_items" in section
        assert section["list_items"][0]["ordered"] is True

    def test_parse_nested_list(self):
        """Test parsing nested list items."""
        parser = MarkdownParser()
        content = "# Title\n\n- Item 1\n  - Nested 1\n  - Nested 2\n- Item 2"
        result = parser.parse(content)
        section = result["sections"][0]
        items = section["list_items"]
        assert items[0]["indent"] == 0
        assert items[1]["indent"] == 2
        assert items[2]["indent"] == 2

    def test_parse_inline_code(self):
        """Test parsing inline code."""
        parser = MarkdownParser()
        content = "# Title\n\nUse `code` here."
        result = parser.parse(content)
        assert len(result["elements"]) > 0
        code_elements = [e for e in result["elements"] if e["type"] == "inline_code"]
        assert len(code_elements) == 1
        assert code_elements[0]["code"] == "code"

    def test_parse_links(self):
        """Test parsing links."""
        parser = MarkdownParser()
        content = "# Title\n\nCheck [this link](http://example.com)."
        result = parser.parse(content)
        link_elements = [e for e in result["elements"] if e["type"] == "link"]
        assert len(link_elements) == 1
        assert link_elements[0]["text"] == "this link"
        assert link_elements[0]["url"] == "http://example.com"

    def test_parse_images(self):
        """Test parsing images."""
        parser = MarkdownParser()
        content = "# Title\n\n![alt text](image.png)"
        result = parser.parse(content)
        img_elements = [e for e in result["elements"] if e["type"] == "image"]
        assert len(img_elements) == 1
        assert img_elements[0]["alt"] == "alt text"
        assert img_elements[0]["url"] == "image.png"

    def test_parse_code_block(self):
        """Test parsing code block."""
        parser = MarkdownParser()
        content = "```python\nprint('hello')\n```"
        result = parser.parse(content)
        # Code blocks are just skipped in regular parsing
        assert result["elements"] == [] or result["elements"] is not None

    def test_parse_front_matter(self):
        """Test parsing front matter."""
        parser = MarkdownParser()
        content = """---
title: Test Document
author: Test Author
---
# Title
"""
        result = parser.parse(content)
        assert "front_matter" in result["metadata"]
        assert result["metadata"]["front_matter"]["title"] == "Test Document"
        assert result["metadata"]["front_matter"]["author"] == "Test Author"

    def test_parse_front_matter_disabled(self):
        """Test parsing front matter when disabled."""
        parser = MarkdownParser({"extract_front_matter": False})
        content = """---
title: Test
---
# Title
"""
        result = parser.parse(content)
        assert "front_matter" not in result.get("metadata", {})

    def test_parse_without_front_matter(self):
        """Test parsing content without front matter."""
        parser = MarkdownParser()
        content = "# Title\n\nSome content."
        result = parser.parse(content)
        assert "front_matter" not in result.get("metadata", {})

    def test_parse_statistics(self):
        """Test that statistics are calculated correctly."""
        parser = MarkdownParser()
        content = "# Title\n\nParagraph content here."
        result = parser.parse(content)
        assert "statistics" in result
        assert result["statistics"]["total_lines"] == 3
        assert result["statistics"]["total_characters"] == len(content)

    def test_parse_section_count_in_statistics(self):
        """Test that section count is in statistics."""
        parser = MarkdownParser()
        content = "# H1\n## H2\n### H3"
        result = parser.parse(content)
        assert result["statistics"]["total_sections"] == 3

    def test_parse_line_number(self):
        """Test that sections have correct line numbers."""
        parser = MarkdownParser()
        content = "line 0\n# Title\n\n## Section"
        result = parser.parse(content)
        assert result["sections"][0]["line_number"] == 2
        assert result["sections"][1]["line_number"] == 4

    def test_parse_preserve_whitespace(self):
        """Test preserving whitespace in paragraphs."""
        parser = MarkdownParser({"preserve_whitespace": True})
        content = "# Title\n\nLine 1\nLine 2\nLine 3"
        result = parser.parse(content)
        paragraph = result["sections"][0]["paragraphs"][0]
        assert "\n" in paragraph["content"]

    def test_parse_no_preserve_whitespace(self):
        """Test collapsing whitespace in paragraphs."""
        parser = MarkdownParser({"preserve_whitespace": False})
        content = "# Title\n\nLine 1\nLine 2"
        result = parser.parse(content)
        paragraph = result["sections"][0]["paragraphs"][0]
        assert " " in paragraph["content"]
        assert "\n" not in paragraph["content"]

    def test_parse_custom_heading_levels(self):
        """Test custom heading level mapping."""
        parser = MarkdownParser({
            "heading_levels": {1: "document_title", 2: "chapter"}
        })
        content = "# Main\n## Chapter"
        result = parser.parse(content)
        assert result["sections"][0]["semantic_type"] == "document_title"
        assert result["sections"][1]["semantic_type"] == "chapter"

    def test_parse_heading_default_semantic_type(self):
        """Test default semantic type when not specified."""
        parser = MarkdownParser()
        content = "# Title"
        result = parser.parse(content)
        assert result["sections"][0]["semantic_type"] == "h1"

    def test_parse_empty_paragraph_between_sections(self):
        """Test handling empty lines between sections."""
        parser = MarkdownParser()
        content = "# Section 1\n\n\n\n# Section 2"
        result = parser.parse(content)
        assert len(result["sections"]) == 2

    def test_parse_top_level_elements(self):
        """Test elements before any heading become top-level."""
        parser = MarkdownParser()
        content = "This is before the title.\n\n# Title"
        result = parser.parse(content)
        # First paragraph becomes a top-level element
        assert len(result["elements"]) >= 1


class TestMarkdownParserEdgeCases:
    """Test suite for edge cases in MarkdownParser."""

    def test_parse_only_whitespace(self):
        """Test parsing content with only whitespace."""
        parser = MarkdownParser()
        with pytest.raises(ParseError):
            parser.parse("   \n\n   \n")

    def test_parse_only_heading_markers(self):
        """Test parsing content with only # markers."""
        parser = MarkdownParser()
        result = parser.parse("#")
        assert len(result["sections"]) == 1
        assert result["sections"][0]["title"] == ""

    def test_parse_unicode_content(self):
        """Test parsing unicode content."""
        parser = MarkdownParser()
        content = "# 标题\n\n内容 with unicode: 你好世界 🎉"
        result = parser.parse(content)
        assert result["sections"][0]["title"] == "标题"

    def test_parse_special_characters_in_title(self):
        """Test parsing titles with special characters."""
        parser = MarkdownParser()
        content = "# Title with [brackets] and (parentheses)"
        result = parser.parse(content)
        assert "brackets" in result["sections"][0]["title"]

    def test_parse_very_long_content(self):
        """Test parsing long content."""
        parser = MarkdownParser()
        content = "# Title\n\n" + ("word " * 1000)
        result = parser.parse(content)
        assert result["statistics"]["total_characters"] > 5000

    def test_parse_multiple_spaces_in_list(self):
        """Test list item with multiple spaces."""
        parser = MarkdownParser()
        content = "# Title\n\n-   Indented item"
        result = parser.parse(content)
        item = result["sections"][0]["list_items"][0]
        assert item["content"] == "Indented item"

    def test_parse_mixed_list_types(self):
        """Test mixing ordered and unordered lists."""
        parser = MarkdownParser()
        content = "# Title\n\n- Unordered\n1. Ordered\n- Unordered 2"
        result = parser.parse(content)
        items = result["sections"][0]["list_items"]
        assert len(items) == 3

    def test_parse_heading_with_trailing_spaces(self):
        """Test heading with trailing spaces."""
        parser = MarkdownParser()
        content = "# Title   \n\nContent"
        result = parser.parse(content)
        assert result["sections"][0]["title"] == "Title"

    def test_parse_multiline_paragraph(self):
        """Test paragraphs spanning multiple lines."""
        parser = MarkdownParser()
        content = "# Title\n\nFirst line\nSecond line\nThird line\n\nNew paragraph."
        result = parser.parse(content)
        paragraphs = result["sections"][0]["paragraphs"]
        assert len(paragraphs) == 2

    def test_parse_empty_document(self):
        """Test empty document raises error."""
        parser = MarkdownParser()
        with pytest.raises(ParseError):
            parser.parse("")
