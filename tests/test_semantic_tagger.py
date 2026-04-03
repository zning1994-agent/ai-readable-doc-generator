"""
Unit tests for the semantic tagger plugin.
"""

import pytest

from ai_readable_doc_generator.parser.plugins.semantic_tagger import (
    ContentType,
    ImportanceLevel,
    SectionRelationship,
    SemanticTag,
    SemanticTaggerPlugin,
    TaggedContent,
)


class TestSemanticTag:
    """Tests for SemanticTag dataclass."""

    def test_creation_with_required_fields(self) -> None:
        """Test creating a SemanticTag with required fields only."""
        tag = SemanticTag(name="type", value="heading")
        assert tag.name == "type"
        assert tag.value == "heading"
        assert tag.confidence == 1.0
        assert tag.metadata == {}

    def test_creation_with_all_fields(self) -> None:
        """Test creating a SemanticTag with all fields."""
        tag = SemanticTag(
            name="importance",
            value="high",
            confidence=0.85,
            metadata={"source": "keyword_detection"},
        )
        assert tag.name == "importance"
        assert tag.value == "high"
        assert tag.confidence == 0.85
        assert tag.metadata == {"source": "keyword_detection"}

    def test_to_dict(self) -> None:
        """Test converting SemanticTag to dictionary."""
        tag = SemanticTag(name="test", value="value", confidence=0.9, metadata={"key": "val"})
        result = tag.to_dict()
        assert result == {
            "name": "test",
            "value": "value",
            "confidence": 0.9,
            "metadata": {"key": "val"},
        }


class TestTaggedContent:
    """Tests for TaggedContent dataclass."""

    def test_creation_with_defaults(self) -> None:
        """Test creating TaggedContent with default values."""
        content = TaggedContent(content="Hello, world!")
        assert content.content == "Hello, world!"
        assert content.content_type == ContentType.TEXT
        assert content.importance == ImportanceLevel.MEDIUM
        assert content.tags == []
        assert content.relationships == []
        assert content.position == {}

    def test_add_tag(self) -> None:
        """Test adding a semantic tag to content."""
        content = TaggedContent(content="Test content")
        content.add_tag(name="category", value="documentation")
        
        assert len(content.tags) == 1
        assert content.tags[0].name == "category"
        assert content.tags[0].value == "documentation"

    def test_add_multiple_tags(self) -> None:
        """Test adding multiple semantic tags."""
        content = TaggedContent(content="Test content")
        content.add_tag(name="tag1", value="value1")
        content.add_tag(name="tag2", value="value2", confidence=0.8)
        
        assert len(content.tags) == 2
        assert content.tags[1].confidence == 0.8

    def test_add_relationship(self) -> None:
        """Test adding a section relationship."""
        content = TaggedContent(content="Test content")
        content.add_relationship("section_1", SectionRelationship.PRECEDES)
        
        assert len(content.relationships) == 1
        assert content.relationships[0] == ("section_1", SectionRelationship.PRECEDES)

    def test_to_dict(self) -> None:
        """Test converting TaggedContent to dictionary."""
        content = TaggedContent(content="Test")
        content.add_tag(name="type", value="heading")
        content.add_relationship("other", SectionRelationship.SIBLING)
        content.position = {"line_start": 1, "line_end": 2}
        
        result = content.to_dict()
        assert result["content"] == "Test"
        assert result["content_type"] == "text"
        assert result["importance"] == "medium"
        assert len(result["tags"]) == 1
        assert len(result["relationships"]) == 1


class TestContentType:
    """Tests for ContentType enumeration."""

    def test_all_content_types_exist(self) -> None:
        """Test that all expected content types are defined."""
        expected_types = [
            "text", "code", "heading", "list", "table",
            "image", "link", "blockquote", "callout", "math", "diagram", "unknown",
        ]
        actual_types = [ct.value for ct in ContentType]
        
        for expected in expected_types:
            assert expected in actual_types


class TestImportanceLevel:
    """Tests for ImportanceLevel enumeration."""

    def test_all_importance_levels_exist(self) -> None:
        """Test that all expected importance levels are defined."""
        expected_levels = ["critical", "high", "medium", "low"]
        actual_levels = [level.value for level in ImportanceLevel]
        
        for expected in expected_levels:
            assert expected in actual_levels


class TestSectionRelationship:
    """Tests for SectionRelationship enumeration."""

    def test_all_relationships_exist(self) -> None:
        """Test that all expected relationships are defined."""
        expected = ["parent", "child", "sibling", "precedes", "follows", "references", "none"]
        actual = [r.value for r in SectionRelationship]
        
        for exp in expected:
            assert exp in actual


class TestSemanticTaggerPlugin:
    """Tests for SemanticTaggerPlugin."""

    def test_initialization_default(self) -> None:
        """Test plugin initialization with defaults."""
        plugin = SemanticTaggerPlugin()
        assert plugin.custom_tags == {}
        assert plugin._content_id_counter == 0

    def test_initialization_with_custom_tags(self) -> None:
        """Test plugin initialization with custom tags."""
        custom = {"todo": ["TODO", "FIXME"]}
        plugin = SemanticTaggerPlugin(custom_tags=custom)
        assert plugin.custom_tags == custom

    def test_initialization_with_importance_keywords(self) -> None:
        """Test plugin initialization with custom importance keywords."""
        keywords = {ImportanceLevel.HIGH: ["priority"]}
        plugin = SemanticTaggerPlugin(importance_keywords=keywords)
        assert plugin.importance_keywords[ImportanceLevel.HIGH] == ["priority"]

    def test_classify_heading(self) -> None:
        """Test content type classification for headings."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("# Title") == ContentType.HEADING
        assert plugin._classify_content_type("## Subtitle") == ContentType.HEADING
        assert plugin._classify_content_type("### H3 Title") == ContentType.HEADING

    def test_classify_code(self) -> None:
        """Test content type classification for code blocks."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("```python\ncode\n```") == ContentType.CODE
        assert plugin._classify_content_type("    indented code") == ContentType.CODE
        assert plugin._classify_content_type("\t\ttabbed code") == ContentType.CODE

    def test_classify_list(self) -> None:
        """Test content type classification for lists."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("- list item") == ContentType.LIST
        assert plugin._classify_content_type("* bullet item") == ContentType.LIST
        assert plugin._classify_content_type("1. numbered item") == ContentType.LIST

    def test_classify_table(self) -> None:
        """Test content type classification for tables."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("| col1 | col2 |") == ContentType.TABLE
        assert plugin._classify_content_type("| A | B | C |") == ContentType.TABLE

    def test_classify_blockquote(self) -> None:
        """Test content type classification for blockquotes."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("> quote text") == ContentType.BLOCKQUOTE

    def test_classify_image(self) -> None:
        """Test content type classification for images."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("![alt](image.png)") == ContentType.IMAGE

    def test_classify_link(self) -> None:
        """Test content type classification for links."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("[link text](http://example.com)") == ContentType.LINK

    def test_classify_callout(self) -> None:
        """Test content type classification for callouts."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("NOTE: This is a note") == ContentType.CALLout
        assert plugin._classify_content_type("WARNING: Be careful!") == ContentType.CALLout
        assert plugin._classify_content_type("TIP: Use this approach") == ContentType.CALLout

    def test_classify_math(self) -> None:
        """Test content type classification for math expressions."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("$x^2 + y^2 = z^2$") == ContentType.MATH

    def test_classify_text_default(self) -> None:
        """Test content type classification defaults to text."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._classify_content_type("Just plain text content.") == ContentType.TEXT

    def test_determine_importance_critical(self) -> None:
        """Test importance detection for critical content."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._determine_importance("WARNING: This is critical") == ImportanceLevel.CRITICAL
        assert plugin._determine_importance("Security vulnerability detected") == ImportanceLevel.CRITICAL
        assert plugin._determine_importance("This must be done") == ImportanceLevel.CRITICAL

    def test_determine_importance_high(self) -> None:
        """Test importance detection for high importance content."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._determine_importance("Important note") == ImportanceLevel.HIGH
        assert plugin._determine_importance("Best practice tip") == ImportanceLevel.HIGH
        assert plugin._determine_importance("Key information here") == ImportanceLevel.HIGH

    def test_determine_importance_low(self) -> None:
        """Test importance detection for low importance content."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._determine_importance("Optional feature") == ImportanceLevel.LOW
        assert plugin._determine_importance("See also related docs") == ImportanceLevel.LOW

    def test_determine_importance_medium_default(self) -> None:
        """Test importance detection defaults to medium."""
        plugin = SemanticTaggerPlugin()
        
        assert plugin._determine_importance("Regular content paragraph") == ImportanceLevel.MEDIUM

    def test_apply_custom_tags(self) -> None:
        """Test applying custom tags to content."""
        plugin = SemanticTaggerPlugin(custom_tags={"todo": ["TODO", "FIXME"]})
        
        tagged = TaggedContent(content="TODO: Fix this bug")
        plugin._apply_custom_tags(tagged, "TODO: Fix this bug")
        
        assert len(tagged.tags) == 1
        assert tagged.tags[0].name == "todo"
        assert tagged.tags[0].value == "TODO"

    def test_tag_content(self) -> None:
        """Test tagging a single piece of content."""
        plugin = SemanticTaggerPlugin()
        
        result = plugin.tag_content("# Introduction", line_start=1)
        
        assert result.content == "# Introduction"
        assert result.content_type == ContentType.HEADING
        assert result.position["line_start"] == 1
        assert result.position["line_end"] == 1

    def test_tag_content_with_context(self) -> None:
        """Test tagging content with context information."""
        plugin = SemanticTaggerPlugin()
        
        context = {"section": "intro", "parent": "document"}
        result = plugin.tag_content("Some content", context=context)
        
        assert result.content == "Some content"

    def test_tag_document(self) -> None:
        """Test tagging multiple document sections."""
        plugin = SemanticTaggerPlugin()
        
        sections = [
            {"content": "# Title", "level": 1, "line_start": 0},
            {"content": "Some paragraph text", "level": 2, "line_start": 2},
            {"content": "- list item", "level": 2, "line_start": 4},
        ]
        
        results = plugin.tag_document(sections)
        
        assert len(results) == 3
        assert results[0].content_type == ContentType.HEADING
        assert results[1].content_type == ContentType.TEXT
        assert results[2].content_type == ContentType.LIST

    def test_tag_document_with_relationships(self) -> None:
        """Test that relationships are preserved when tagging documents."""
        plugin = SemanticTaggerPlugin()
        
        sections = [
            {"content": "# First", "level": 1},
            {"content": "# Second", "level": 1},
        ]
        
        results = plugin.tag_document(sections, preserve_relationships=True)
        
        # Second section should have relationship to first
        assert len(results[1].relationships) > 0

    def test_tag_document_without_relationships(self) -> None:
        """Test that relationships are not added when preserve_relationships is False."""
        plugin = SemanticTaggerPlugin()
        
        sections = [
            {"content": "# First", "level": 1},
            {"content": "# Second", "level": 1},
        ]
        
        results = plugin.tag_document(sections, preserve_relationships=False)
        
        for result in results:
            assert len(result.relationships) == 0

    def test_extract_semantic_metadata(self) -> None:
        """Test extracting semantic metadata from tagged content."""
        plugin = SemanticTaggerPlugin()
        
        tagged = TaggedContent(content="Test content")
        tagged.add_tag(name="category", value="documentation")
        tagged.position = {"line_start": 1}
        
        metadata = plugin.extract_semantic_metadata(tagged)
        
        assert metadata["content_type"] == "text"
        assert metadata["importance"] == "medium"
        assert len(metadata["tags"]) == 1
        assert metadata["content_length"] == 12
        assert metadata["word_count"] == 2

    def test_generate_content_id(self) -> None:
        """Test unique content ID generation."""
        plugin = SemanticTaggerPlugin()
        
        id1 = plugin._generate_content_id()
        id2 = plugin._generate_content_id()
        
        assert id1 == "content_1"
        assert id2 == "content_2"

    def test_multiline_content_position(self) -> None:
        """Test position tracking for multiline content."""
        plugin = SemanticTaggerPlugin()
        
        content = "Line 1\nLine 2\nLine 3"
        result = plugin.tag_content(content, line_start=5)
        
        assert result.position["line_start"] == 5
        assert result.position["line_end"] == 7  # 5 + 2 newlines
