"""Document model for structured representation."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .schema import SectionType, ContentClassification, SemanticTag, Relationship


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    source_name: str = ""
    source_path: str = ""
    title: str = ""
    description: str = ""
    author: str = ""
    version: str = ""
    created_at: str = ""
    modified_at: str = ""
    word_count: int = 0
    line_count: int = 0
    front_matter: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_name": self.source_name,
            "source_path": self.source_path,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "front_matter": self.front_matter
        }

    @classmethod
    def from_source(cls, content: str, source_name: str = "") -> "DocumentMetadata":
        """Create metadata from source content."""
        metadata = cls(source_name=source_name)
        metadata.line_count = len(content.splitlines())
        metadata.word_count = len(content.split())

        # Parse YAML front matter if present
        front_matter = cls._parse_front_matter(content)
        if front_matter:
            metadata.front_matter = front_matter
            metadata.title = front_matter.get("title", "")
            metadata.description = front_matter.get("description", "")
            metadata.author = front_matter.get("author", "")
            metadata.version = front_matter.get("version", "")

        return metadata

    @staticmethod
    def _parse_front_matter(content: str) -> dict[str, Any]:
        """Parse YAML front matter from markdown content."""
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        if not match:
            return {}

        try:
            import yaml
            return yaml.safe_load(match.group(1)) or {}
        except Exception:
            return {}


@dataclass
class DocumentSection:
    """A section of a document."""
    id: str
    type: SectionType
    content: str
    level: int = 1
    line_number: int = 0
    semantic_tags: list[SemanticTag] = field(default_factory=list)
    classification: ContentClassification | None = None
    children: list["DocumentSection"] = field(default_factory=list)
    parent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "level": self.level,
            "line_number": self.line_number,
            "semantic_tags": [tag.to_dict() for tag in self.semantic_tags],
            "classification": self.classification.value if self.classification else None,
            "children": [child.to_dict() for child in self.children]
        }


@dataclass
class DocumentStructure:
    """Document structure information."""
    heading_tree: list[dict[str, Any]] = field(default_factory=list)
    table_of_contents: list[dict[str, Any]] = field(default_factory=list)
    max_heading_level: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "heading_tree": self.heading_tree,
            "table_of_contents": self.table_of_contents,
            "max_heading_level": self.max_heading_level
        }


@dataclass
class Document:
    """Complete document representation."""
    content: str
    metadata: DocumentMetadata
    sections: list[DocumentSection] = field(default_factory=list)
    structure: DocumentStructure = field(default_factory=DocumentStructure)
    relationships: list[Relationship] = field(default_factory=list)
    semantic_tags: dict[str, list[SemanticTag]] = field(default_factory=dict)

    def to_dict(self, include_relationships: bool = True) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "metadata": self.metadata.to_dict(),
            "content": [section.to_dict() for section in self.sections],
            "structure": self.structure.to_dict(),
            "semantic_tags": {
                k: [tag.to_dict() for tag in v]
                for k, v in self.semantic_tags.items()
            }
        }

        if include_relationships:
            result["relationships"] = [rel.to_dict() for rel in self.relationships]

        return result


class MarkdownParser:
    """
    Parser for Markdown documents.

    Extracts structured content with semantic information.
    """

    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w*)\s*$')
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s*(.*)$')
    LIST_ITEM_PATTERN = re.compile(r'^(\s*)[-*+]\s+(.+)$')
    NUMBERED_LIST_PATTERN = re.compile(r'^(\s*)\d+\.\s+(.+)$')
    TABLE_ROW_PATTERN = re.compile(r'^\|.+\|$')
    HORIZONTAL_RULE_PATTERN = re.compile(r'^[-*_]{3,}\s*$')

    def __init__(self):
        self._section_counter = 0

    def parse(self, content: str, source_name: str = "") -> Document:
        """Parse markdown content into structured Document."""
        self._section_counter = 0

        metadata = DocumentMetadata.from_source(content, source_name)
        lines = content.splitlines()

        sections = []
        current_section: DocumentSection | None = None
        pending_content: list[str] = []

        for line_num, line in enumerate(lines, 1):
            # Check for front matter
            if line_num == 1 and line.strip() == "---":
                continue

            # Check for headings
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous section
                if current_section:
                    current_section.content = "\n".join(pending_content).strip()
                    sections.append(current_section)

                # Create new section
                hashes, heading_text = heading_match.groups()
                level = len(hashes)
                self._section_counter += 1
                current_section = DocumentSection(
                    id=f"section_{self._section_counter}",
                    type=SectionType(f"heading_{level}"),
                    content=heading_text.strip(),
                    level=level,
                    line_number=line_num
                )
                pending_content = []

                # Update metadata title if this is the first H1
                if level == 1 and not metadata.title:
                    metadata.title = heading_text.strip()

            # Check for code blocks
            elif self.CODE_BLOCK_PATTERN.match(line):
                if current_section:
                    current_section.content = "\n".join(pending_content).strip()
                    sections.append(current_section)

                self._section_counter += 1
                current_section = DocumentSection(
                    id=f"section_{self._section_counter}",
                    type=SectionType.CODE_BLOCK,
                    content=line,
                    level=0,
                    line_number=line_num
                )
                pending_content = []
                sections.append(current_section)
                current_section = None

            # Check for blockquotes
            elif self.BLOCKQUOTE_PATTERN.match(line):
                if current_section:
                    pending_content.append(line)

            # Check for list items
            elif self.LIST_ITEM_PATTERN.match(line) or self.NUMBERED_LIST_PATTERN.match(line):
                pending_content.append(line)

            # Check for horizontal rules
            elif self.HORIZONTAL_RULE_PATTERN.match(line):
                if current_section:
                    current_section.content = "\n".join(pending_content).strip()
                    sections.append(current_section)

                self._section_counter += 1
                current_section = DocumentSection(
                    id=f"section_{self._section_counter}",
                    type=SectionType.HORIZONTAL_RULE,
                    content="",
                    level=0,
                    line_number=line_num
                )
                pending_content = []

            # Regular content
            elif line.strip():
                pending_content.append(line)

        # Save last section
        if current_section:
            current_section.content = "\n".join(pending_content).strip()
            sections.append(current_section)

        # Build structure
        structure = self._build_structure(sections)

        return Document(
            content=content,
            metadata=metadata,
            sections=sections,
            structure=structure
        )

    def _build_structure(self, sections: list[DocumentSection]) -> DocumentStructure:
        """Build document structure from sections."""
        structure = DocumentStructure()

        # Build table of contents
        for section in sections:
            if section.type.value.startswith("heading_"):
                structure.table_of_contents.append({
                    "id": section.id,
                    "title": section.content,
                    "level": section.level,
                    "line_number": section.line_number
                })
                structure.max_heading_level = max(
                    structure.max_heading_level,
                    section.level
                )

        # Build heading tree
        structure.heading_tree = self._build_heading_tree(sections)

        return structure

    def _build_heading_tree(
        self,
        sections: list[DocumentSection]
    ) -> list[dict[str, Any]]:
        """Build hierarchical tree of headings."""
        tree = []
        stack: list[tuple[int, dict[str, Any]]] = []

        for section in sections:
            if not section.type.value.startswith("heading_"):
                continue

            node = {
                "id": section.id,
                "title": section.content,
                "level": section.level,
                "children": []
            }

            # Pop items from stack that are at same or higher level
            while stack and stack[-1][0] >= section.level:
                stack.pop()

            if stack:
                stack[-1][1]["children"].append(node)
            else:
                tree.append(node)

            stack.append((section.level, node))

        return tree
