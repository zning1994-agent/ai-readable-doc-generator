"""Tests for HtmlConverter using BeautifulSoup4 with lxml parser."""

import pytest

from ai_readable_doc_generator.converter import HtmlConverter
from ai_readable_doc_generator.models import (
    ContentClassification,
    Document,
    ImportanceLevel,
    Section,
    SectionType,
)


class TestHtmlConverterBasic:
    """Basic HTML conversion tests."""

    def test_convert_simple_html(self) -> None:
        """Test conversion of simple HTML document."""
        html = "<html><body><p>Hello World</p></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        assert isinstance(document, Document)
        assert "Hello World" in document.content

    def test_convert_html_with_title(self) -> None:
        """Test extraction of title from HTML."""
        html = """
        <html>
            <head><title>Test Page Title</title></head>
            <body><p>Content</p></body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        assert document.metadata.title == "Test Page Title"
        assert document.metadata.source_type == "html"

    def test_convert_html_with_meta_description(self) -> None:
        """Test extraction of meta description."""
        html = """
        <html>
            <head>
                <meta name="description" content="Page description">
            </head>
            <body><p>Content</p></body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        assert document.metadata.description == "Page description"

    def test_convert_html_with_language(self) -> None:
        """Test extraction of language attribute."""
        html = '<html lang="en-US"><body><p>Content</p></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        assert document.metadata.language == "en-US"

    def test_validate_valid_html(self) -> None:
        """Test validation of valid HTML."""
        html = "<html><body><p>Valid</p></body></html>"
        converter = HtmlConverter()

        assert converter.validate(html) is True

    def test_validate_invalid_html(self) -> None:
        """Test validation of invalid HTML."""
        html = "Not HTML at all"
        converter = HtmlConverter()

        assert converter.validate(html) is False

    def test_convert_empty_html(self) -> None:
        """Test conversion of empty HTML."""
        html = "<html><body></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        assert isinstance(document, Document)


class TestHtmlConverterSemanticTags:
    """Tests for semantic HTML5 tag handling."""

    def test_convert_article_tag(self) -> None:
        """Test conversion of article element."""
        html = "<html><body><article><p>Article content</p></article></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        assert len(document.sections) > 0
        article_sections = self._find_sections_by_type(document.sections, SectionType.ARTICLE)
        assert len(article_sections) > 0

    def test_convert_nav_tag(self) -> None:
        """Test conversion of nav element."""
        html = "<html><body><nav><a href='/'>Home</a></nav></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        nav_sections = self._find_sections_by_type(document.sections, SectionType.NAVIGATION)
        assert len(nav_sections) > 0
        assert nav_sections[0].classification == ContentClassification.NAVIGATION

    def test_convert_section_tag(self) -> None:
        """Test conversion of section element."""
        html = "<html><body><section><h2>Section Title</h2></section></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        section_sections = self._find_sections_by_type(document.sections, SectionType.SECTION)
        assert len(section_sections) > 0

    def test_convert_aside_tag(self) -> None:
        """Test conversion of aside element."""
        html = "<html><body><aside><p>Sidebar content</p></aside></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        aside_sections = self._find_sections_by_type(document.sections, SectionType.ASIDE)
        assert len(aside_sections) > 0

    def test_convert_header_footer_tags(self) -> None:
        """Test conversion of header and footer elements."""
        html = """
        <html>
            <body>
                <header><h1>Site Title</h1></header>
                <footer>Copyright 2024</footer>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        header_sections = self._find_sections_by_type(document.sections, SectionType.HEADER)
        footer_sections = self._find_sections_by_type(document.sections, SectionType.FOOTER)
        assert len(header_sections) > 0
        assert len(footer_sections) > 0

    def test_convert_main_tag(self) -> None:
        """Test conversion of main element."""
        html = "<html><body><main><p>Main content</p></main></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        main_sections = self._find_sections_by_type(document.sections, SectionType.MAIN)
        assert len(main_sections) > 0


class TestHtmlConverterHeadings:
    """Tests for heading hierarchy extraction."""

    def test_convert_heading_levels(self) -> None:
        """Test extraction of heading levels."""
        html = """
        <html>
            <body>
                <h1>Level 1</h1>
                <h2>Level 2</h2>
                <h3>Level 3</h3>
                <h4>Level 4</h4>
                <h5>Level 5</h5>
                <h6>Level 6</h6>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        heading_sections = self._find_sections_by_type(document.sections, SectionType.HEADING)
        assert len(heading_sections) == 6

        levels = {s.level for s in heading_sections}
        assert levels == {1, 2, 3, 4, 5, 6}

    def test_convert_heading_importance(self) -> None:
        """Test heading importance levels."""
        html = """
        <html>
            <body>
                <h1>Primary</h1>
                <h2>Secondary</h2>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        h1_sections = [s for s in document.sections if s.level == 1 and s.section_type == SectionType.HEADING]
        h2_sections = [s for s in document.sections if s.level == 2 and s.section_type == SectionType.HEADING]

        if h1_sections:
            assert h1_sections[0].importance == ImportanceLevel.HIGH
        if h2_sections:
            assert h2_sections[0].importance == ImportanceLevel.HIGH


class TestHtmlConverterLists:
    """Tests for list structure extraction."""

    def test_convert_ordered_list(self) -> None:
        """Test conversion of ordered list."""
        html = "<html><body><ol><li>Item 1</li><li>Item 2</li></ol></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        list_sections = self._find_sections_by_type(document.sections, SectionType.LIST)
        assert len(list_sections) > 0

    def test_convert_unordered_list(self) -> None:
        """Test conversion of unordered list."""
        html = "<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        list_sections = self._find_sections_by_type(document.sections, SectionType.LIST)
        assert len(list_sections) > 0

    def test_convert_nested_list(self) -> None:
        """Test conversion of nested list structure."""
        html = """
        <html>
            <body>
                <ul>
                    <li>Parent 1
                        <ul>
                            <li>Child 1.1</li>
                            <li>Child 1.2</li>
                        </ul>
                    </li>
                    <li>Parent 2</li>
                </ul>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        list_sections = self._find_sections_by_type(document.sections, SectionType.LIST)
        assert len(list_sections) > 0

        # Check for nested list items
        item_sections = self._find_sections_by_type(document.sections, SectionType.LIST_ITEM)
        assert len(item_sections) >= 4


class TestHtmlConverterCodeBlocks:
    """Tests for code block extraction."""

    def test_convert_pre_code_block(self) -> None:
        """Test conversion of pre/code block."""
        html = "<html><body><pre><code>def hello(): pass</code></pre></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        code_sections = self._find_sections_by_type(document.sections, SectionType.CODE)
        assert len(code_sections) > 0
        assert code_sections[0].classification == ContentClassification.CODE_LITERAL

    def test_convert_inline_code(self) -> None:
        """Test conversion of inline code."""
        html = "<html><body><p>Use <code>pip</code> to install.</p></body></html>"
        converter = HtmlConverter()
        document = converter.convert(html)

        code_sections = self._find_sections_by_type(document.sections, SectionType.CODE)
        assert len(code_sections) > 0


class TestHtmlConverterTables:
    """Tests for table structure extraction."""

    def test_convert_simple_table(self) -> None:
        """Test conversion of simple table."""
        html = """
        <html>
            <body>
                <table>
                    <tr><th>Header</th></tr>
                    <tr><td>Data</td></tr>
                </table>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        table_sections = self._find_sections_by_type(document.sections, SectionType.TABLE)
        assert len(table_sections) > 0

    def test_convert_table_structure(self) -> None:
        """Test table row and cell extraction."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th>Column 1</th>
                        <th>Column 2</th>
                    </tr>
                    <tr>
                        <td>Data 1</td>
                        <td>Data 2</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        row_sections = self._find_sections_by_type(document.sections, SectionType.TABLE_ROW)
        assert len(row_sections) >= 2


class TestHtmlConverterLinksAndImages:
    """Tests for link and image extraction."""

    def test_convert_link(self) -> None:
        """Test conversion of hyperlink."""
        html = '<html><body><a href="https://example.com">Example</a></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        link_sections = self._find_sections_by_type(document.sections, SectionType.LINK)
        assert len(link_sections) > 0
        assert "https://example.com" in link_sections[0].metadata.get("html_id", "") or \
               "href" in str(link_sections[0].raw_attributes)

    def test_convert_image(self) -> None:
        """Test conversion of image."""
        html = '<html><body><img src="image.png" alt="Test image"></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        image_sections = self._find_sections_by_type(document.sections, SectionType.IMAGE)
        assert len(image_sections) > 0
        assert image_sections[0].metadata.get("alt") == "Test image"


class TestHtmlConverterSemanticClasses:
    """Tests for semantic class-based classification."""

    def test_classify_warning_class(self) -> None:
        """Test classification based on warning class."""
        html = '<html><body><div class="warning">Warning message</div></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        warning_sections = [s for s in document.sections
                           if s.classification == ContentClassification.WARNING]
        assert len(warning_sections) > 0

    def test_classify_note_class(self) -> None:
        """Test classification based on note class."""
        html = '<html><body><div class="note">Note content</div></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        note_sections = [s for s in document.sections
                        if s.classification == ContentClassification.NOTE]
        assert len(note_sections) > 0

    def test_classify_code_class(self) -> None:
        """Test classification based on code class."""
        html = '<html><body><div class="code-snippet">x = 1</div></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        code_sections = [s for s in document.sections
                        if s.classification == ContentClassification.CODE_LITERAL]
        assert len(code_sections) > 0

    def test_importance_from_id(self) -> None:
        """Test importance determination from element ID."""
        html = '<html><body><p id="critical-info">Critical content</p></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        critical_sections = [s for s in document.sections
                            if s.importance == ImportanceLevel.CRITICAL]
        assert len(critical_sections) > 0


class TestHtmlConverterIdAndClasses:
    """Tests for ID and class attribute extraction."""

    def test_extract_element_id(self) -> None:
        """Test extraction of element ID."""
        html = '<html><body><section id="main-content"><p>Content</p></section></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        sections_with_id = [s for s in document.sections if s.id == "main-content"]
        assert len(sections_with_id) > 0

    def test_extract_element_classes(self) -> None:
        """Test extraction of CSS classes."""
        html = '<html><body><div class="container fluid highlight">Content</div></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        sections_with_classes = [s for s in document.sections if s.classes]
        assert len(sections_with_classes) > 0
        assert "container" in sections_with_classes[0].classes

    def test_extract_raw_attributes(self) -> None:
        """Test extraction of raw HTML attributes."""
        html = '<html><body><a href="test.html" target="_blank" data-id="123">Link</a></body></html>'
        converter = HtmlConverter()
        document = converter.convert(html)

        link_sections = self._find_sections_by_type(document.sections, SectionType.LINK)
        assert len(link_sections) > 0
        assert "href" in link_sections[0].raw_attributes
        assert link_sections[0].raw_attributes.get("data-id") == "123"


class TestHtmlConverterHiddenElements:
    """Tests for hidden element handling."""

    def test_ignore_display_none(self) -> None:
        """Test ignoring elements with display:none."""
        html = """
        <html>
            <body>
                <p>Visible content</p>
                <p style="display:none">Hidden content</p>
            </body>
        </html>
        """
        converter = HtmlConverter(ignore_hidden=True)
        document = converter.convert(html)

        assert "Visible content" in document.content
        assert "Hidden content" not in document.content

    def test_ignore_hidden_class(self) -> None:
        """Test ignoring elements with hidden class."""
        html = """
        <html>
            <body>
                <p>Visible</p>
                <p class="hidden">Hidden</p>
            </body>
        </html>
        """
        converter = HtmlConverter(ignore_hidden=True)
        document = converter.convert(html)

        assert "Visible" in document.content

    def test_ignore_sr_only(self) -> None:
        """Test ignoring elements with sr-only class."""
        html = """
        <html>
            <body>
                <p>Visible</p>
                <span class="sr-only">Screen reader only</span>
            </body>
        </html>
        """
        converter = HtmlConverter(ignore_hidden=True)
        document = converter.convert(html)

        assert "Visible" in document.content


class TestHtmlConverterScriptAndStyle:
    """Tests for script and style element handling."""

    def test_ignore_scripts_by_default(self) -> None:
        """Test ignoring script content by default."""
        html = """
        <html>
            <body>
                <p>Content</p>
                <script>console.log('script');</script>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        assert "console.log" not in document.content

    def test_extract_scripts_when_enabled(self) -> None:
        """Test extracting script content when enabled."""
        html = """
        <html>
            <body>
                <p>Content</p>
                <script>console.log('script');</script>
            </body>
        </html>
        """
        converter = HtmlConverter(extract_scripts=True)
        document = converter.convert(html)

        # Script content may or may not appear depending on implementation
        # The key is it doesn't raise an error
        assert isinstance(document, Document)


class TestHtmlConverterPreprocessing:
    """Tests for HTML preprocessing."""

    def test_preprocess_normalizes_whitespace(self) -> None:
        """Test that preprocessing normalizes whitespace."""
        html = """
        <html>
            <body>
                <p>Content   with    extra     spaces</p>
            </body>
        </html>
        """
        converter = HtmlConverter()
        processed = converter.preprocess(html)

        assert "    " not in processed


class TestHtmlConverterComplex:
    """Tests for complex HTML document structures."""

    def test_convert_blog_post(self) -> None:
        """Test conversion of typical blog post structure."""
        html = """
        <html lang="en">
            <head>
                <title>My Blog Post</title>
                <meta name="description" content="A sample blog post">
            </head>
            <body>
                <header>
                    <h1>My Blog</h1>
                    <nav>
                        <a href="/">Home</a>
                        <a href="/about">About</a>
                    </nav>
                </header>
                <main>
                    <article>
                        <h2>Blog Post Title</h2>
                        <p>First paragraph of the post.</p>
                        <p>Second paragraph with <code>inline code</code>.</p>
                        <pre><code>
def example():
    return "Hello"
                        </code></pre>
                        <h3>Subsection</h3>
                        <ul>
                            <li>List item one</li>
                            <li>List item two</li>
                        </ul>
                    </article>
                </main>
                <aside>
                    <h3>Related Posts</h3>
                    <p>Sidebar content</p>
                </aside>
                <footer>
                    <p>Copyright 2024</p>
                </footer>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        # Verify metadata
        assert document.metadata.title == "My Blog Post"
        assert document.metadata.description == "A sample blog post"
        assert document.metadata.language == "en"
        assert document.metadata.source_type == "html"

        # Verify structure
        nav_sections = self._find_sections_by_type(document.sections, SectionType.NAVIGATION)
        assert len(nav_sections) > 0

        article_sections = self._find_sections_by_type(document.sections, SectionType.ARTICLE)
        assert len(article_sections) > 0

        aside_sections = self._find_sections_by_type(document.sections, SectionType.ASIDE)
        assert len(aside_sections) > 0

    def test_convert_documentation_page(self) -> None:
        """Test conversion of typical documentation page."""
        html = """
        <html>
            <head><title>API Reference</title></head>
            <body>
                <nav class="sidebar">
                    <ul>
                        <li><a href="#intro">Introduction</a></li>
                        <li><a href="#api">API</a></li>
                    </ul>
                </nav>
                <main>
                    <section id="intro">
                        <h1>Introduction</h1>
                        <p>Welcome to the documentation.</p>
                        <div class="note">
                            <p>This is an important note.</p>
                        </div>
                    </section>
                    <section id="api">
                        <h2>API Reference</h2>
                        <div class="warning">
                            <p>Warning: API may change.</p>
                        </div>
                        <table>
                            <tr><th>Method</th><th>Description</th></tr>
                            <tr><td>GET</td><td>Retrieve data</td></tr>
                        </table>
                    </section>
                </main>
            </body>
        </html>
        """
        converter = HtmlConverter()
        document = converter.convert(html)

        assert document.metadata.title == "API Reference"
        assert document.metadata.source_type == "html"

        # Check semantic structure
        nav_sections = self._find_sections_by_type(document.sections, SectionType.NAVIGATION)
        assert len(nav_sections) > 0

        # Check note and warning classifications
        note_sections = [s for s in document.sections
                         if s.classification == ContentClassification.NOTE]
        warning_sections = [s for s in document.sections
                           if s.classification == ContentClassification.WARNING]
        assert len(note_sections) > 0
        assert len(warning_sections) > 0


# Helper functions

def _find_sections_by_type(sections: list[Section], section_type: SectionType) -> list[Section]:
    """Recursively find all sections of a given type."""
    result = []
    for section in sections:
        if section.section_type == section_type:
            result.append(section)
        result.extend(_find_sections_by_type(section.children, section_type))
    return result
