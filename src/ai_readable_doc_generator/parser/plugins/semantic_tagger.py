"""
Semantic Tagger Plugin for AI-Readable Document Generator.

This plugin provides semantic tagging functionality to add machine-readable
semantic markers (content types, relationships, importance indicators) to document sections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContentType(Enum):
    """Enumeration of content types for semantic tagging."""
    
    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    LINK = "link"
    BLOCKQUOTE = "blockquote"
    CALLout = "callout"
    MATH = "math"
    DIAGRAM = "diagram"
    UNKNOWN = "unknown"


class ImportanceLevel(Enum):
    """Importance levels for content prioritization."""
    
    CRITICAL = "critical"  # Essential information, must not be lost
    HIGH = "high"          # Important content that should be preserved
    MEDIUM = "medium"      # Standard content
    LOW = "low"            # Supplementary or decorative content


class SectionRelationship(Enum):
    """Types of relationships between document sections."""
    
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    REFERENCES = "references"
    NONE = "none"


@dataclass
class SemanticTag:
    """
    Represents a semantic tag applied to a piece of content.
    
    Attributes:
        name: The name/type of the semantic tag.
        value: The value or content of the tag.
        confidence: Confidence score (0.0 to 1.0) for the tag assignment.
        metadata: Additional metadata associated with the tag.
    """
    
    name: str
    value: str
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the semantic tag to a dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class TaggedContent:
    """
    Represents a piece of content with semantic tags.
    
    Attributes:
        content: The actual content text.
        content_type: The type of content.
        importance: The importance level of the content.
        tags: List of semantic tags applied to this content.
        relationships: List of relationships to other content.
        position: Position information (line number, etc.).
    """
    
    content: str
    content_type: ContentType = ContentType.TEXT
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    tags: list[SemanticTag] = field(default_factory=list)
    relationships: list[tuple[str, SectionRelationship]] = field(default_factory=list)
    position: dict[str, int] = field(default_factory=dict)
    
    def add_tag(self, name: str, value: str, confidence: float = 1.0, **metadata: Any) -> None:
        """Add a semantic tag to this content."""
        tag = SemanticTag(name=name, value=value, confidence=confidence, metadata=metadata)
        self.tags.append(tag)
    
    def add_relationship(self, target_id: str, relationship: SectionRelationship) -> None:
        """Add a relationship to another piece of content."""
        self.relationships.append((target_id, relationship))
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the tagged content to a dictionary."""
        return {
            "content": self.content,
            "content_type": self.content_type.value,
            "importance": self.importance.value,
            "tags": [tag.to_dict() for tag in self.tags],
            "relationships": [
                {"target": target, "relationship": rel.value}
                for target, rel in self.relationships
            ],
            "position": self.position,
        }


class SemanticTaggerPlugin:
    """
    Plugin for adding semantic tags to document content.
    
    This plugin analyzes document content and adds semantic markers including:
    - Content type classification
    - Importance level assignment
    - Semantic tags for machine-readable metadata
    - Section relationship mapping
    
    Example:
        >>> tagger = SemanticTaggerPlugin()
        >>> tagged = tagger.tag_content("# Introduction\\n\\nThis is a test.", line_start=1)
        >>> print(tagged.content_type)
        ContentType.HEADING
    """
    
    def __init__(
        self,
        custom_tags: dict[str, list[str]] | None = None,
        importance_keywords: dict[ImportanceLevel, list[str]] | None = None,
    ) -> None:
        """
        Initialize the semantic tagger plugin.
        
        Args:
            custom_tags: Custom tag mappings (e.g., {"todo": ["TODO", "FIXME"]}).
            importance_keywords: Keywords mapped to importance levels.
        """
        self.custom_tags = custom_tags or {}
        self.importance_keywords = importance_keywords or self._default_importance_keywords()
        self._content_id_counter = 0
    
    def _default_importance_keywords(self) -> dict[ImportanceLevel, list[str]]:
        """Get default keywords for importance level detection."""
        return {
            ImportanceLevel.CRITICAL: [
                "warning", "danger", "critical", "security", "vulnerability",
                "breaking", "must", "required", "essential",
            ],
            ImportanceLevel.HIGH: [
                "important", "note", "tip", "best practice", "recommend",
                "significant", "key", "main",
            ],
            ImportanceLevel.LOW: [
                "optional", "see also", "related", "footnote", "appendix",
            ],
        }
    
    def _generate_content_id(self) -> str:
        """Generate a unique content ID."""
        self._content_id_counter += 1
        return f"content_{self._content_id_counter}"
    
    def tag_content(
        self,
        content: str,
        line_start: int = 0,
        context: dict[str, Any] | None = None,
    ) -> TaggedContent:
        """
        Tag a piece of content with semantic markers.
        
        Args:
            content: The content text to tag.
            line_start: Starting line number for position tracking.
            context: Optional context information (parent section, previous content, etc.).
        
        Returns:
            TaggedContent with semantic tags applied.
        """
        tagged = TaggedContent(
            content=content,
            position={"line_start": line_start, "line_end": line_start + content.count("\\n")},
        )
        tagged.content_type = self._classify_content_type(content)
        tagged.importance = self._determine_importance(content)
        self._apply_custom_tags(tagged, content)
        return tagged
    
    def _classify_content_type(self, content: str) -> ContentType:
        """
        Classify the content type based on content analysis.
        
        Args:
            content: The content to classify.
        
        Returns:
            The classified ContentType.
        """
        stripped = content.strip()
        
        # Check for code blocks
        if stripped.startswith("```") or stripped.startswith("    ") or "\t" in stripped[:4]:
            return ContentType.CODE
        
        # Check for headings
        if stripped.startswith("#"):
            return ContentType.HEADING
        
        # Check for list items
        if stripped.startswith(("- ", "* ", "+ ")) or stripped.startswith((
            "1. ", "2. ", "3. ", "4. ", "5. ",
        )):
            return ContentType.LIST
        
        # Check for tables (simplified detection)
        if "|" in stripped and stripped.count("|") >= 2:
            return ContentType.TABLE
        
        # Check for blockquotes
        if stripped.startswith(">"):
            return ContentType.BLOCKQUOTE
        
        # Check for images
        if stripped.startswith("!["):
            return ContentType.IMAGE
        
        # Check for links
        if stripped.startswith("[") and "]" in stripped and "(" in stripped:
            return ContentType.LINK
        
        # Check for callouts/admonitions
        lower_content = stripped.lower()
        if any(keyword in lower_content for keyword in ["note:", "warning:", "tip:", "caution:", "info:"]):
            return ContentType.CALLout
        
        # Check for math expressions
        if stripped.startswith("$") and stripped.endswith("$"):
            return ContentType.MATH
        
        # Default to text
        return ContentType.TEXT
    
    def _determine_importance(self, content: str) -> ImportanceLevel:
        """
        Determine the importance level of content based on keywords.
        
        Args:
            content: The content to analyze.
        
        Returns:
            The determined ImportanceLevel.
        """
        lower_content = content.lower()
        
        # Check for critical keywords
        for keyword in self.importance_keywords[ImportanceLevel.CRITICAL]:
            if keyword in lower_content:
                return ImportanceLevel.CRITICAL
        
        # Check for high importance keywords
        for keyword in self.importance_keywords[ImportanceLevel.HIGH]:
            if keyword in lower_content:
                return ImportanceLevel.HIGH
        
        # Check for low importance keywords
        for keyword in self.importance_keywords[ImportanceLevel.LOW]:
            if keyword in lower_content:
                return ImportanceLevel.LOW
        
        return ImportanceLevel.MEDIUM
    
    def _apply_custom_tags(self, tagged: TaggedContent, content: str) -> None:
        """
        Apply custom tags based on configured tag mappings.
        
        Args:
            tagged: The TaggedContent to apply tags to.
            content: The content to analyze for custom tags.
        """
        for tag_name, keywords in self.custom_tags.items():
            for keyword in keywords:
                if keyword in content:
                    tagged.add_tag(
                        name=tag_name,
                        value=keyword,
                        confidence=0.9,
                        matched_keyword=keyword,
                    )
    
    def tag_document(
        self,
        sections: list[dict[str, Any]],
        preserve_relationships: bool = True,
    ) -> list[TaggedContent]:
        """
        Tag multiple document sections with semantic markers.
        
        Args:
            sections: List of document sections with 'content' and optional 'level'.
            preserve_relationships: Whether to detect and preserve section relationships.
        
        Returns:
            List of TaggedContent with semantic tags applied.
        """
        tagged_sections = []
        
        for idx, section in enumerate(sections):
            content = section.get("content", "")
            level = section.get("level", 0)
            line_start = section.get("line_start", idx * 10)
            
            tagged = self.tag_content(content, line_start)
            tagged.position["level"] = level
            tagged.position["section_index"] = idx
            
            # Preserve section relationships if requested
            if preserve_relationships and idx > 0:
                tagged.add_relationship(
                    target_id=f"content_{idx}",
                    relationship=SectionRelationship.PRECEDES,
                )
            
            tagged_sections.append(tagged)
        
        return tagged_sections
    
    def extract_semantic_metadata(self, tagged_content: TaggedContent) -> dict[str, Any]:
        """
        Extract structured semantic metadata from tagged content.
        
        Args:
            tagged_content: The TaggedContent to extract metadata from.
        
        Returns:
            Dictionary containing semantic metadata.
        """
        return {
            "content_type": tagged_content.content_type.value,
            "importance": tagged_content.importance.value,
            "tags": [tag.to_dict() for tag in tagged_content.tags],
            "relationship_count": len(tagged_content.relationships),
            "position": tagged_content.position,
            "content_length": len(tagged_content.content),
            "word_count": len(tagged_content.content.split()),
        }
