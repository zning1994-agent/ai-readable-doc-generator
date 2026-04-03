"""
Tests for the Section domain model.
"""

import pytest
from datetime import datetime

from ai_readable_doc_generator.models.section import (
    Section,
    SectionMetadata,
    SectionType,
    ContentImportance,
)


class TestSectionMetadata:
    """Tests for SectionMetadata class."""
    
    def test_default_metadata(self):
        """Test default metadata values."""
        metadata = SectionMetadata()
        assert metadata.section_type == SectionType.UNKNOWN
        assert metadata.importance == ContentImportance.MEDIUM
        assert metadata.tags == []
        assert metadata.language == "en"
        assert metadata.word_count == 0
        assert metadata.character_count == 0
        assert metadata.custom == {}
    
    def test_add_tag(self):
        """Test adding tags to metadata."""
        metadata = SectionMetadata()
        metadata.add_tag("important")
        assert metadata.has_tag("important")
        assert "important" in metadata.tags
    
    def test_add_duplicate_tag(self):
        """Test that duplicate tags are not added."""
        metadata = SectionMetadata()
        metadata.add_tag("test")
        metadata.add_tag("test")
        assert metadata.tags.count("test") == 1
    
    def test_remove_tag(self):
        """Test removing tags from metadata."""
        metadata = SectionMetadata()
        metadata.add_tag("test")
        metadata.remove_tag("test")
        assert not metadata.has_tag("test")
    
    def test_set_custom(self):
        """Test setting custom metadata."""
        metadata = SectionMetadata()
        metadata.set_custom("author", "John")
        metadata.set_custom("version", 1)
        assert metadata.get_custom("author") == "John"
        assert metadata.get_custom("version") == 1
    
    def test_get_custom_default(self):
        """Test getting custom metadata with default."""
        metadata = SectionMetadata()
        assert metadata.get_custom("nonexistent", "default") == "default"
    
    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = SectionMetadata(
            section_type=SectionType.PARAGRAPH,
            importance=ContentImportance.HIGH,
            tags=["intro", "overview"],
            language="en",
            word_count=100,
            character_count=500,
        )
        data = metadata.to_dict()
        assert data["section_type"] == "paragraph"
        assert data["importance"] == "HIGH"
        assert data["tags"] == ["intro", "overview"]
        assert data["word_count"] == 100
    
    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "section_type": "heading",
            "importance": "CRITICAL",
            "tags": ["api", "reference"],
            "language": "en",
            "word_count": 50,
            "character_count": 250,
        }
        metadata = SectionMetadata.from_dict(data)
        assert metadata.section_type == SectionType.HEADING
        assert metadata.importance == ContentImportance.CRITICAL
        assert metadata.tags == ["api", "reference"]


class TestSection:
    """Tests for Section class."""
    
    def test_default_section(self):
        """Test default section values."""
        section = Section()
        assert section.title == ""
        assert section.content == ""
        assert section.id is not None
        assert section.level == 0
        assert section.parent is None
        assert section.children == []
        assert section.metadata is not None
    
    def test_section_with_content(self):
        """Test section with content."""
        section = Section(
            title="Introduction",
            content="This is the introduction.",
        )
        assert section.title == "Introduction"
        assert section.content == "This is the introduction."
        assert section.metadata.word_count == 4
        assert section.metadata.character_count == 24
    
    def test_is_root(self):
        """Test root section detection."""
        root = Section(title="Root")
        assert root.is_root is True
        child = Section(title="Child")
        root.add_child(child)
        assert child.is_root is False
    
    def test_is_leaf(self):
        """Test leaf section detection."""
        parent = Section(title="Parent")
        child = Section(title="Child")
        assert parent.is_leaf is True
        parent.add_child(child)
        assert parent.is_leaf is False
        assert child.is_leaf is True
    
    def test_add_child(self):
        """Test adding child section."""
        parent = Section(title="Parent")
        child = Section(title="Child")
        parent.add_child(child)
        
        assert child in parent.children
        assert child.parent is parent
        assert child.level == 1
    
    def test_remove_child(self):
        """Test removing child section."""
        parent = Section(title="Parent")
        child = Section(title="Child")
        parent.add_child(child)
        
        result = parent.remove_child(child)
        assert result is True
        assert child not in parent.children
        assert child.parent is None
        assert child.level == 0
    
    def test_remove_nonexistent_child(self):
        """Test removing a child that doesn't exist."""
        parent = Section(title="Parent")
        child = Section(title="Child")
        
        result = parent.remove_child(child)
        assert result is False
    
    def test_get_child(self):
        """Test getting child by index."""
        parent = Section(title="Parent")
        child1 = Section(title="Child 1")
        child2 = Section(title="Child 2")
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert parent.get_child(0) is child1
        assert parent.get_child(1) is child2
        assert parent.get_child(5) is None
    
    def test_find_child_by_id(self):
        """Test finding child by ID."""
        root = Section(title="Root")
        child = Section(title="Child")
        root.add_child(child)
        
        found = root.find_child_by_id(child.id)
        assert found is child
        
        not_found = root.find_child_by_id("nonexistent")
        assert not_found is None
    
    def test_find_children_by_tag(self):
        """Test finding children by tag."""
        root = Section(title="Root")
        root.metadata.add_tag("root-tag")
        
        child1 = Section(title="Child 1")
        child1.metadata.add_tag("test-tag")
        root.add_child(child1)
        
        child2 = Section(title="Child 2")
        child2.metadata.add_tag("test-tag")
        root.add_child(child2)
        
        grandchild = Section(title="Grandchild")
        grandchild.metadata.add_tag("test-tag")
        child1.add_child(grandchild)
        
        results = root.find_children_by_tag("test-tag")
        assert len(results) == 3
    
    def test_find_children_by_type(self):
        """Test finding children by type."""
        root = Section(title="Root")
        root.metadata.section_type = SectionType.PARAGRAPH
        
        code_child = Section(title="Code")
        code_child.metadata.section_type = SectionType.CODE_BLOCK
        root.add_child(code_child)
        
        results = root.find_children_by_type(SectionType.CODE_BLOCK)
        assert len(results) == 1
        assert results[0].title == "Code"
    
    def test_get_ancestors(self):
        """Test getting ancestor sections."""
        root = Section(title="Root")
        parent = Section(title="Parent")
        child = Section(title="Child")
        
        root.add_child(parent)
        parent.add_child(child)
        
        ancestors = child.get_ancestors()
        assert len(ancestors) == 2
        assert ancestors[0] is parent
        assert ancestors[1] is root
    
    def test_get_root(self):
        """Test getting root section."""
        root = Section(title="Root")
        parent = Section(title="Parent")
        child = Section(title="Child")
        
        root.add_child(parent)
        parent.add_child(child)
        
        assert child.get_root() is root
        assert parent.get_root() is root
    
    def test_get_siblings(self):
        """Test getting sibling sections."""
        parent = Section(title="Parent")
        child1 = Section(title="Child 1")
        child2 = Section(title="Child 2")
        child3 = Section(title="Child 3")
        
        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)
        
        siblings = child2.get_siblings()
        assert len(siblings) == 2
        assert child1 in siblings
        assert child3 in siblings
        assert child2 not in siblings
    
    def test_path(self):
        """Test getting section path."""
        root = Section(title="Root")
        parent = Section(title="Parent")
        child = Section(title="Child")
        
        root.add_child(parent)
        parent.add_child(child)
        
        assert child.path == ["Root", "Parent", "Child"]
    
    def test_full_content(self):
        """Test getting full content including children."""
        root = Section(title="Root")
        root.content = "Root content"
        
        child = Section(title="Child")
        child.content = "Child content"
        root.add_child(child)
        
        assert root.full_content == "Root content\n\nChild content"
    
    def test_total_word_count(self):
        """Test total word count including children."""
        root = Section(title="Root")
        root.content = "one two three"
        
        child = Section(title="Child")
        child.content = "four five six seven"
        root.add_child(child)
        
        assert root.total_word_count == 7
    
    def test_update_content(self):
        """Test updating section content."""
        section = Section()
        section.update_content("New content")
        
        assert section.content == "New content"
        assert section.metadata.word_count == 2
        assert section.updated_at > section.created_at
    
    def test_update_title(self):
        """Test updating section title."""
        section = Section()
        section.update_title("New Title")
        
        assert section.title == "New Title"
        assert section.updated_at > section.created_at
    
    def test_walk(self):
        """Test walking through all sections."""
        root = Section(title="Root")
        child1 = Section(title="Child 1")
        child2 = Section(title="Child 2")
        grandchild = Section(title="Grandchild")
        
        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild)
        
        sections = root.walk()
        assert len(sections) == 4
        assert sections[0] is root
        assert sections[1] is child1
        assert sections[2] is grandchild
        assert sections[3] is child2
    
    def test_to_dict(self):
        """Test converting section to dictionary."""
        section = Section(
            title="Test Section",
            content="Test content",
        )
        section.metadata.section_type = SectionType.HEADING
        
        child = Section(title="Child")
        section.add_child(child)
        
        data = section.to_dict()
        assert data["title"] == "Test Section"
        assert data["content"] == "Test content"
        assert data["metadata"]["section_type"] == "heading"
        assert len(data["children"]) == 1
        assert data["children"][0]["title"] == "Child"
    
    def test_from_dict(self):
        """Test creating section from dictionary."""
        data = {
            "id": "test-id",
            "title": "Test",
            "content": "Content",
            "level": 0,
            "metadata": {
                "section_type": "paragraph",
                "importance": "HIGH",
                "tags": ["test"],
                "language": "en",
                "word_count": 1,
                "character_count": 7,
                "custom": {},
            },
            "children": [
                {
                    "title": "Child",
                    "content": "Child content",
                    "metadata": {
                        "section_type": "paragraph",
                        "importance": "MEDIUM",
                        "tags": [],
                        "language": "en",
                        "word_count": 2,
                        "character_count": 13,
                        "custom": {},
                    },
                    "children": [],
                }
            ],
        }
        
        section = Section.from_dict(data)
        assert section.id == "test-id"
        assert section.title == "Test"
        assert section.metadata.section_type == SectionType.PARAGRAPH
        assert len(section.children) == 1
        assert section.children[0].title == "Child"
    
    def test_repr(self):
        """Test string representation."""
        section = Section(title="Introduction")
        repr_str = repr(section)
        assert "Introduction" in repr_str
        assert "id=" in repr_str
        assert "type=" in repr_str


class TestSectionType:
    """Tests for SectionType enum."""
    
    def test_all_types_exist(self):
        """Test that all section types exist."""
        expected_types = [
            "title", "heading", "paragraph", "code_block",
            "list", "table", "image", "blockquote",
            "admonition", "divider", "unknown"
        ]
        actual_types = [t.value for t in SectionType]
        for expected in expected_types:
            assert expected in actual_types


class TestContentImportance:
    """Tests for ContentImportance enum."""
    
    def test_all_levels_exist(self):
        """Test that all importance levels exist."""
        expected_levels = [
            "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"
        ]
        actual_levels = [level.name for level in ContentImportance]
        for expected in expected_levels:
            assert expected in actual_levels
    
    def test_ordering(self):
        """Test that importance levels are ordered correctly."""
        assert ContentImportance.CRITICAL.value < ContentImportance.HIGH.value
        assert ContentImportance.HIGH.value < ContentImportance.MEDIUM.value
        assert ContentImportance.MEDIUM.value < ContentImportance.LOW.value
        assert ContentImportance.LOW.value < ContentImportance.INFORMATIONAL.value
