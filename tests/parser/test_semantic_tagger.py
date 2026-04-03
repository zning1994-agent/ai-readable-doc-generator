"""Unit tests for SemanticTagger plugin."""

import pytest

from ai_readable_doc_generator.parser.plugins.semantic_tagger import SemanticTagger


class TestSemanticTaggerInit:
    """Test suite for SemanticTagger initialization."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        tagger = SemanticTagger()
        assert tagger.config == {}
        assert tagger.include_importance is True
        assert tagger.include_relationships is True
        assert tagger.min_word_count == 10

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "include_importance": False,
            "include_relationships": False,
            "min_word_count": 5,
            "custom_keywords": {"important_keywords": {"urgent"}},
        }
        tagger = SemanticTagger(config)
        assert tagger.config == config
        assert tagger.include_importance is False
        assert tagger.include_relationships is False
        assert tagger.min_word_count == 5

    def test_custom_keywords_merged(self):
        """Test that custom keywords are merged with defaults."""
        tagger = SemanticTagger({
            "custom_keywords": {"important_keywords": {"urgent", "critical"}}
        })
        assert "urgent" in tagger._keywords["important_keywords"]
        assert "critical" in tagger._keywords["important_keywords"]
        # Default keywords should still be present
        assert "important" in tagger._keywords["important_keywords"]
        assert "warning" in tagger._keywords["important_keywords"]


class TestSemanticTaggerProcess:
    """Test suite for SemanticTagger.process() method."""

    def test_process_empty_document(self):
        """Test processing an empty document."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert "semantic_tags" in result
        assert "sections" in result
        assert "elements" in result

    def test_process_with_sections(self):
        """Test processing document with sections."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "Introduction",
                    "paragraphs": [
                        {"type": "paragraph", "content": "This is an introduction."}
                    ]
                }
            ],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert len(result["sections"]) == 1
        assert "semantic_tags" in result["sections"][0]

    def test_process_with_elements(self):
        """Test processing document with elements."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [],
            "elements": [
                {"type": "link", "text": "example", "url": "http://example.com"},
            ],
        }
        result = tagger.process(parsed)
        assert len(result["elements"]) == 1
        assert "semantic_tags" in result["elements"][0]

    def test_process_adds_importance_markers(self):
        """Test that importance markers are added."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "Important Section",
                    "paragraphs": [
                        {"type": "paragraph", "content": "This is critical information."}
                    ]
                }
            ],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert "importance" in result["semantic_tags"]
        assert result["semantic_tags"]["importance"]["has_critical"] is True

    def test_process_adds_relationships(self):
        """Test that relationships are added."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {"type": "section", "level": 1, "title": "Intro", "paragraphs": []},
                {"type": "section", "level": 2, "title": "Details", "paragraphs": []},
            ],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert "relationships" in result["semantic_tags"]


class TestSemanticTaggerSectionClassification:
    """Test suite for section type classification."""

    def test_classify_introduction_section(self):
        """Test classification of introduction sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Introduction",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 0, 5)
        assert section_type == "introduction"

    def test_classify_overview_section(self):
        """Test classification of overview sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Project Overview",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 0, 5)
        assert section_type == "introduction"

    def test_classify_conclusion_section(self):
        """Test classification of conclusion sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Conclusion",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 4, 5)
        assert section_type == "conclusion"

    def test_classify_summary_section(self):
        """Test classification of summary sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Summary",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 4, 5)
        assert section_type == "conclusion"

    def test_classify_reference_section(self):
        """Test classification of reference sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Reference",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 2, 5)
        assert section_type == "reference"

    def test_classify_toc_section(self):
        """Test classification of table of contents."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Table of Contents",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 0, 5)
        assert section_type == "toc"

    def test_classify_first_h1_as_intro(self):
        """Test that first h1 is classified as introduction."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Main Title",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 0, 5)
        assert section_type == "introduction"

    def test_classify_last_h1_as_conclusion(self):
        """Test that last h1 is classified as conclusion."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "The End",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 4, 5)
        assert section_type == "conclusion"

    def test_classify_h2_as_subsection(self):
        """Test that h2 is classified as subsection."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 2,
            "title": "Subsection",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 1, 5)
        assert section_type == "subsection"


class TestSemanticTaggerContentType:
    """Test suite for content type classification."""

    def test_classify_instruction_content(self):
        """Test classification of instruction content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "How to Install",
            "paragraphs": [
                {"type": "paragraph", "content": "Follow these steps to install."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "instruction"

    def test_classify_instruction_by_keywords(self):
        """Test classification by instruction keywords."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Installation Guide",
            "paragraphs": [
                {"type": "paragraph", "content": "Step 1: Run the install command."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "instruction"

    def test_classify_configuration_content(self):
        """Test classification of configuration content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Configuration",
            "paragraphs": [
                {"type": "paragraph", "content": "Set the config parameter."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "configuration"

    def test_classify_api_reference_content(self):
        """Test classification of API reference content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "API Documentation",
            "paragraphs": [
                {"type": "paragraph", "content": "The endpoint accepts requests."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "api_reference"

    def test_classify_reference_content(self):
        """Test classification of reference content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "See Also",
            "paragraphs": [
                {"type": "paragraph", "content": "Related documentation."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "reference"

    def test_classify_error_content(self):
        """Test classification of error content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Troubleshooting",
            "paragraphs": [
                {"type": "paragraph", "content": "Common error messages and solutions."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "error_reference"

    def test_classify_explanation_content(self):
        """Test classification of explanation content."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Background",
            "paragraphs": [
                {"type": "paragraph", "content": "This section explains how it works."}
            ]
        }
        content_type = tagger._classify_content_type(section)
        assert content_type == "explanation"


class TestSemanticTaggerImportance:
    """Test suite for importance calculation."""

    def test_critical_importance(self):
        """Test critical importance detection."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Warning",
            "paragraphs": [
                {"type": "paragraph", "content": "This is critical and important."}
            ]
        }
        importance = tagger._calculate_section_importance(section)
        assert importance == "critical"

    def test_important_importance(self):
        """Test important importance detection."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Code Examples",
            "paragraphs": []
        }
        importance = tagger._calculate_section_importance(section)
        assert importance == "important"

    def test_normal_importance(self):
        """Test normal importance for regular sections."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Background",
            "paragraphs": [
                {"type": "paragraph", "content": "Some background information."}
            ]
        }
        importance = tagger._calculate_section_importance(section)
        assert importance == "normal"

    def test_element_code_importance(self):
        """Test code element importance."""
        tagger = SemanticTagger()
        element = {"type": "inline_code", "content": "code"}
        importance = tagger._calculate_element_importance(element)
        assert importance == "important"


class TestSemanticTaggerKeywords:
    """Test suite for keyword extraction."""

    def test_extract_keywords(self):
        """Test keyword extraction from section."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Setup",
            "paragraphs": [
                {"type": "paragraph", "content": "Configure the settings here."}
            ]
        }
        keywords = tagger._extract_keywords(section)
        assert "configuration" in keywords

    def test_extract_multiple_keywords(self):
        """Test extracting multiple keyword categories."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "API Setup",
            "paragraphs": [
                {"type": "paragraph", "content": "Important: configure the API endpoint."}
            ]
        }
        keywords = tagger._extract_keywords(section)
        assert "api" in keywords
        assert "important" in keywords
        assert "configuration" in keywords

    def test_extract_empty_keywords(self):
        """Test keyword extraction with no matching keywords."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "Background",
            "paragraphs": [
                {"type": "paragraph", "content": "Just some text."}
            ]
        }
        keywords = tagger._extract_keywords(section)
        assert len(keywords) == 0


class TestSemanticTaggerRelationships:
    """Test suite for relationship calculation."""

    def test_calculate_relationships(self):
        """Test basic relationship calculation."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {"type": "section", "level": 1, "title": "Intro", "paragraphs": []},
                {"type": "section", "level": 2, "title": "Details", "paragraphs": []},
                {"type": "section", "level": 1, "title": "Reference", "paragraphs": []},
            ],
            "elements": [],
        }
        relationships = tagger._calculate_relationships(parsed)
        # Should have parent-child relationships
        assert isinstance(relationships, list)

    def test_relationships_disabled(self):
        """Test relationships are not added when disabled."""
        tagger = SemanticTagger({"include_relationships": False})
        parsed = {
            "sections": [
                {"type": "section", "level": 1, "title": "Intro", "paragraphs": []}
            ],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert "relationships" not in result["semantic_tags"]


class TestSemanticTaggerImportanceMarkers:
    """Test suite for importance markers calculation."""

    def test_calculate_importance_markers(self):
        """Test importance markers calculation."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "Important",
                    "paragraphs": [],
                    "semantic_tags": {
                        "importance": "important",
                        "content_type": "explanation"
                    }
                }
            ],
            "elements": [],
        }
        markers = tagger._calculate_importance_markers(parsed)
        assert markers["has_important"] is True

    def test_markers_with_instructions(self):
        """Test markers detect instructions."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "How to",
                    "paragraphs": [],
                    "semantic_tags": {
                        "importance": "normal",
                        "content_type": "instruction"
                    }
                }
            ],
            "elements": [],
        }
        markers = tagger._calculate_importance_markers(parsed)
        assert markers["has_instructions"] is True

    def test_markers_with_api_reference(self):
        """Test markers detect API references."""
        tagger = SemanticTagger()
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "API",
                    "paragraphs": [],
                    "semantic_tags": {
                        "importance": "normal",
                        "content_type": "api_reference"
                    }
                }
            ],
            "elements": [],
        }
        markers = tagger._calculate_importance_markers(parsed)
        assert markers["has_api_reference"] is True


class TestSemanticTaggerElementTypes:
    """Test suite for element type classification."""

    def test_classify_link_element(self):
        """Test link element classification."""
        tagger = SemanticTagger()
        element = {"type": "link", "text": "click here", "url": "http://example.com"}
        element_type = tagger._classify_element_type(element)
        assert element_type == "hyperlink"

    def test_classify_image_element(self):
        """Test image element classification."""
        tagger = SemanticTagger()
        element = {"type": "image", "alt": "photo", "url": "image.png"}
        element_type = tagger._classify_element_type(element)
        assert element_type == "media"

    def test_classify_inline_code_element(self):
        """Test inline code element classification."""
        tagger = SemanticTagger()
        element = {"type": "inline_code", "code": "print('hi')"}
        element_type = tagger._classify_element_type(element)
        assert element_type == "code_reference"

    def test_classify_short_paragraph(self):
        """Test short paragraph classification."""
        tagger = SemanticTagger()
        element = {"type": "paragraph", "content": "Short text"}
        element_type = tagger._classify_element_type(element)
        assert element_type == "short_text"

    def test_classify_long_paragraph(self):
        """Test long paragraph classification."""
        tagger = SemanticTagger()
        element = {
            "type": "paragraph",
            "content": "This is a longer paragraph with more than ten words in it."
        }
        element_type = tagger._classify_element_type(element)
        assert element_type == "prose"


class TestSemanticTaggerReadingOrder:
    """Test suite for reading order assignment."""

    def test_reading_order_assigned(self):
        """Test that reading order is assigned to sections."""
        tagger = SemanticTagger()
        sections = [
            {"type": "section", "level": 1, "title": "First", "paragraphs": []},
            {"type": "section", "level": 1, "title": "Second", "paragraphs": []},
            {"type": "section", "level": 1, "title": "Third", "paragraphs": []},
        ]
        tagged = tagger._tag_sections(sections)
        assert tagged[0]["semantic_tags"]["reading_order"] == 1
        assert tagged[1]["semantic_tags"]["reading_order"] == 2
        assert tagged[2]["semantic_tags"]["reading_order"] == 3


class TestSemanticTaggerEdgeCases:
    """Test suite for edge cases in SemanticTagger."""

    def test_process_with_missing_keys(self):
        """Test processing document with missing optional keys."""
        tagger = SemanticTagger()
        parsed = {}
        result = tagger.process(parsed)
        assert "semantic_tags" in result

    def test_empty_sections_list(self):
        """Test processing with empty sections list."""
        tagger = SemanticTagger()
        parsed = {"sections": [], "elements": []}
        result = tagger.process(parsed)
        assert result["sections"] == []

    def test_empty_elements_list(self):
        """Test processing with empty elements list."""
        tagger = SemanticTagger()
        parsed = {"sections": [], "elements": []}
        result = tagger.process(parsed)
        assert result["elements"] == []

    def test_section_without_title(self):
        """Test processing section without title."""
        tagger = SemanticTagger()
        section = {"type": "section", "level": 1, "paragraphs": []}
        section_type = tagger._classify_section_type(section, 0, 1)
        # Should still classify based on level
        assert section_type == "introduction"

    def test_element_without_type(self):
        """Test processing element without type."""
        tagger = SemanticTagger()
        element = {"content": "some content"}
        element_type = tagger._classify_element_type(element)
        assert element_type == "unknown"

    def test_importance_markers_disabled(self):
        """Test importance markers not added when disabled."""
        tagger = SemanticTagger({"include_importance": False})
        parsed = {
            "sections": [
                {
                    "type": "section",
                    "level": 1,
                    "title": "Critical",
                    "paragraphs": [],
                    "semantic_tags": {
                        "importance": "critical",
                        "content_type": "explanation"
                    }
                }
            ],
            "elements": [],
        }
        result = tagger.process(parsed)
        assert "importance" not in result["semantic_tags"]

    def test_unicode_title(self):
        """Test processing unicode title."""
        tagger = SemanticTagger()
        section = {
            "type": "section",
            "level": 1,
            "title": "日本語タイトル",
            "paragraphs": []
        }
        section_type = tagger._classify_section_type(section, 0, 1)
        # Unicode title not matching patterns, defaults to position-based
        assert section_type == "introduction"
