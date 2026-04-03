"""Markdown converter using markdown-it-py for AST parsing and semantic transformation."""

import re
import uuid
from pathlib import Path
from typing import Any, Iterator

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode

from ai_readable_doc_generator.base import BaseConverter
from ai_readable_doc_generator.document import Document
from ai_readable_doc_generator.models.schema import (
    ContentType,
    DocumentMetadata,
    HeadingLevel,
    RelationshipType,
    SemanticBlock,
    SemanticDocument,
    SemanticSection,
)


class MarkdownConverter(BaseConverter):
    """Converter for Markdown documents to semantic format.

    Uses markdown-it-py to parse Markdown into an AST and transforms
    it into a SemanticDocument with structured, AI-readable output.
    """

    # Mapping from markdown-it token types to ContentType
    TOKEN_TYPE_MAP: dict[str, ContentType] = {
        "paragraph": ContentType.TEXT,
        "heading": ContentType.HEADING,
        "code_block": ContentType.CODE_BLOCK,
        "fence": ContentType.CODE_BLOCK,
        "blockquote": ContentType.BLOCKQUOTE,
        "hr": ContentType.HORIZONTAL_RULE,
        "bullet_list": ContentType.LIST,
        "ordered_list": ContentType.LIST,
        "list_item": ContentType.LIST_ITEM,
        "table": ContentType.TABLE,
        "tr": ContentType.TABLE_ROW,
        "td": ContentType.TABLE_CELL,
        "th": ContentType.TABLE_CELL,
        "link": ContentType.LINK,
        "image": ContentType.IMAGE,
        "inline_code": ContentType.INLINE_CODE,
        "em": ContentType.EMPHASIS,
        "strong": ContentType.STRONG,
        "html_inline": ContentType.HTML,
        "html_block": ContentType.HTML,
    }

    # Semantic section type keywords
    SECTION_TYPE_KEYWORDS: dict[str, list[str]] = {
        "introduction": ["introduction", "overview", "summary", "背景", "简介"],
        "installation": ["installation", "install", "setup", "安装", "部署"],
        "usage": ["usage", "usage example", "how to use", "quick start", "使用", "用法"],
        "configuration": ["configuration", "config", "settings", "配置", "设置"],
        "api_reference": ["api", "api reference", "reference", "接口", "api文档"],
        "examples": ["example", "examples", "demo", "示例", "案例"],
        "faq": ["faq", "q&a", "questions", "常见问题"],
        "troubleshooting": ["troubleshooting", "debug", "problems", "问题排查"],
        "contributing": ["contributing", "contribution", "开发", "贡献"],
        "license": ["license", "copyright", "许可证", "授权"],
        "changelog": ["changelog", "history", "更新日志", "变更记录"],
        "conclusion": ["conclusion", "summary", "结论", "总结"],
    }

    # Importance keywords
    IMPORTANCE_KEYWORDS: dict[str, list[str]] = {
        "critical": [
            "warning", "important", "danger", "critical", "security",
            "注意", "警告", "重要", "安全",
        ],
        "high": [
            "note", "info", "tip", "hint", "best practice",
            "提示", "技巧", "最佳实践",
        ],
        "low": [
            "optional", "advanced", "see also", "related",
            "可选", "高级", "相关",
        ],
    }

    def __init__(
        self,
        add_table_of_contents: bool = True,
        add_statistics: bool = True,
        extract_semantic_tags: bool = True,
        importance_detection: bool = True,
        enable_relationships: bool = True,
    ) -> None:
        """Initialize the Markdown converter.

        Args:
            add_table_of_contents: Whether to generate a table of contents.
            add_statistics: Whether to generate document statistics.
            extract_semantic_tags: Whether to extract semantic tags.
            importance_detection: Whether to detect content importance.
            enable_relationships: Whether to generate relationships between blocks.
        """
        super().__init__(
            add_table_of_contents=add_table_of_contents,
            add_statistics=add_statistics,
            extract_semantic_tags=extract_semantic_tags,
            importance_detection=importance_detection,
        )
        self.enable_relationships = enable_relationships
        self._md_parser = MarkdownIt()
        self._block_counter = 0
        self._section_counter = 0

    def convert(self, source: str | Path) -> SemanticDocument:
        """Convert a Markdown file to semantic format.

        Args:
            source: File path or raw Markdown content.

        Returns:
            SemanticDocument with structured content.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If the source cannot be processed.
        """
        is_file, value = self._validate_source(source)

        if is_file:
            path = Path(value)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            content = path.read_text(encoding="utf-8")
            source_path = str(path)
        else:
            content = value
            source_path = None

        # Create internal document
        doc = Document(content=content, source_path=source_path)
        doc.metadata["source_format"] = "markdown"

        # Parse and create semantic document
        semantic_doc = self.parse(content)
        semantic_doc.metadata.source_path = source_path

        # Extract title from first H1 if available
        if not semantic_doc.metadata.title:
            title = self._extract_title(content)
            semantic_doc.metadata.title = title

        # Calculate word count
        semantic_doc.metadata.word_count = len(content.split())
        semantic_doc.metadata.reading_time_minutes = self._calculate_reading_time(content)

        # Add table of contents
        if self.add_table_of_contents:
            semantic_doc.table_of_contents = self._build_toc(semantic_doc.sections)

        # Add statistics
        if self.add_statistics:
            semantic_doc.statistics = self._generate_statistics(semantic_doc)

        # Generate semantic summary
        semantic_doc.semantic_summary = self._generate_summary(semantic_doc)

        return semantic_doc

    def parse(self, content: str) -> SemanticDocument:
        """Parse Markdown content to semantic format.

        Args:
            content: Raw Markdown content string.

        Returns:
            SemanticDocument with structured content.
        """
        self._reset_counters()

        # Tokenize with markdown-it
        tokens = self._md_parser.parse(content)

        # Build syntax tree for hierarchical analysis
        tree = SyntaxTreeNode(tokens)

        # Create semantic document
        semantic_doc = SemanticDocument()

        # Process tokens to create blocks
        blocks = self._process_tokens(tokens)
        semantic_doc.all_blocks = blocks

        # Group blocks into sections based on headings
        semantic_doc.sections = self._build_sections(blocks)

        # Post-process sections
        self._post_process_sections(semantic_doc.sections)

        return semantic_doc

    def _reset_counters(self) -> None:
        """Reset internal counters for new document."""
        self._block_counter = 0
        self._section_counter = 0

    def _generate_block_id(self) -> str:
        """Generate a unique block ID."""
        self._block_counter += 1
        return f"block_{self._block_counter:04d}"

    def _generate_section_id(self) -> str:
        """Generate a unique section ID."""
        self._section_counter += 1
        return f"section_{self._section_counter:04d}"

    def _extract_title(self, content: str) -> str | None:
        """Extract title from the first H1 heading.

        Args:
            content: Markdown content.

        Returns:
            Title string or None if not found.
        """
        # Match # Title pattern
        match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _process_tokens(self, tokens: list[Token]) -> list[SemanticBlock]:
        """Process markdown-it tokens into semantic blocks.

        Args:
            tokens: List of markdown-it tokens.

        Returns:
            List of SemanticBlock objects.
        """
        blocks: list[SemanticBlock] = []
        current_line = 1

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Skip container tokens (don't create blocks for them)
            if token.type.endswith("_open") and token.nesting == 1:
                container_type = token.type.replace("_open", "")
                container_end = f"{container_type}_close"

                # Find matching close token
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j].type == container_end:
                        depth -= 1
                    elif tokens[j].type == token.type:
                        depth += 1
                    j += 1

                # Process container content
                container_tokens = tokens[i + 1:j]
                block = self._token_to_block(token, container_tokens, current_line)
                if block:
                    blocks.append(block)

                current_line = tokens[j - 1].map[1] if tokens[j - 1].map else current_line
                i = j
                continue

            # Process regular tokens
            block = self._token_to_block(token, [], current_line)
            if block:
                blocks.append(block)

            current_line = token.map[1] if token.map else current_line
            i += 1

        return blocks

    def _token_to_block(
        self, token: Token, children: list[Token], current_line: int
    ) -> SemanticBlock | None:
        """Convert a markdown-it token to a SemanticBlock.

        Args:
            token: The markdown-it token.
            children: Child tokens for container blocks.
            current_line: Current line number.

        Returns:
            SemanticBlock or None if token should be skipped.
        """
        token_type = token.type
        nesting = token.nesting

        # Skip close tokens
        if nesting == -1:
            return None

        # Skip embeds (not standard markdown)
        if token_type == "embed":
            return None

        # Map token type to ContentType
        content_type = self.TOKEN_TYPE_MAP.get(token_type, ContentType.TEXT)

        # Extract content
        if content_type == ContentType.CODE_BLOCK:
            content = token.content
            language = token.info.strip() or None
        elif content_type == ContentType.HEADING:
            # Get heading text from content or children
            content = self._get_heading_text(token, children)
        elif content_type == ContentType.LIST:
            content = self._get_list_text(token, children)
        elif content_type == ContentType.BLOCKQUOTE:
            content = self._get_blockquote_text(token, children)
        elif content_type == ContentType.TABLE:
            content = self._get_table_text(token, children)
        else:
            content = token.content or ""

        # Handle inline tokens for simple blocks
        if not content and token.map and children:
            content = self._render_inline(children)

        # Extract heading level
        level = None
        if content_type == ContentType.HEADING:
            match = re.match(r"^#+\s+", token.tag or "")
            if match:
                level = match.group(0).count("#")
                level_enum = {1: HeadingLevel.H1, 2: HeadingLevel.H2, 3: HeadingLevel.H3,
                              4: HeadingLevel.H4, 5: HeadingLevel.H5, 6: HeadingLevel.H6}
                level = level_enum.get(level, HeadingLevel.H2)

        # Extract link/image URL
        url = None
        alt_text = None
        if content_type == ContentType.LINK:
            url = token.get("href")
        elif content_type == ContentType.IMAGE:
            url = token.get("src")
            alt_text = token.get("alt")

        # Generate semantic tags
        semantic_tags = []
        if self.extract_semantic_tags:
            semantic_tags = self._extract_semantic_tags(content, content_type)

        # Determine importance
        importance = "normal"
        if self.importance_detection:
            importance = self._detect_importance(content)

        # Create relationships
        relationships = []
        if self.enable_relationships:
            relationships = self._generate_relationships(token, content_type)

        block = SemanticBlock(
            id=self._generate_block_id(),
            content_type=content_type,
            content=content.strip() if content else "",
            raw_content=token.content,
            language=language,
            url=url,
            alt_text=alt_text,
            level=level,
            line_number=token.map[0] if token.map else current_line,
            semantic_tags=semantic_tags,
            importance=importance,
            relationships=relationships,
            metadata={},
        )

        return block

    def _get_heading_text(self, token: Token, children: list[Token]) -> str:
        """Extract text from a heading token."""
        if token.content:
            return token.content
        return self._render_inline(children)

    def _get_list_text(self, token: Token, children: list[Token]) -> str:
        """Extract text from a list token."""
        lines = []
        for child in children:
            if child.type == "list_item_open":
                # Find the text content
                text = self._render_inline([c for c in children if c.nesting == 0][:3])
                lines.append(f"- {text}")
        return "\n".join(lines) if lines else token.content or ""

    def _get_blockquote_text(self, token: Token, children: list[Token]) -> str:
        """Extract text from a blockquote token."""
        return self._render_inline(children)

    def _get_table_text(self, token: Token, children: list[Token]) -> str:
        """Extract text from a table token."""
        return token.content or ""

    def _render_inline(self, tokens: list[Token]) -> str:
        """Render inline tokens as plain text.

        Args:
            tokens: List of inline tokens.

        Returns:
            Plain text content.
        """
        parts = []
        for token in tokens:
            if token.type == "inline" and token.children:
                parts.append(self._render_inline(token.children))
            elif token.type in ("text", "code_inline"):
                parts.append(token.content or "")
            elif token.type == "softbreak":
                parts.append(" ")
            elif token.type == "hardbreak":
                parts.append("\n")
            elif token.type == "html_inline":
                # Strip HTML tags but keep text
                text = re.sub(r"<[^>]+>", "", token.content or "")
                parts.append(text)
            elif token.content:
                parts.append(token.content)
        return "".join(parts).strip()

    def _extract_semantic_tags(self, content: str, content_type: ContentType) -> list[str]:
        """Extract semantic tags from content.

        Args:
            content: The text content.
            content_type: Type of content.

        Returns:
            List of semantic tags.
        """
        tags: list[str] = []

        # Add content type tag
        tags.append(content_type.value)

        # Check for section type keywords
        content_lower = content.lower()
        for section_type, keywords in self.SECTION_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    tags.append(f"section:{section_type}")
                    break

        # Check for code language
        if content_type == ContentType.CODE_BLOCK:
            # Try to extract language from content (first line usually)
            lines = content.split("\n")
            if lines:
                # Common language patterns
                for lang in ["python", "javascript", "typescript", "java", "go", "rust",
                             "bash", "shell", "json", "yaml", "xml", "sql", "html", "css"]:
                    if lines[0].lower().startswith(lang):
                        tags.append(f"language:{lang}")
                        break

        # Check for API patterns
        if "function" in content_lower or "def " in content_lower:
            tags.append("category:api")
        if "class " in content_lower:
            tags.append("category:class")

        return list(set(tags))  # Remove duplicates

    def _detect_importance(self, content: str) -> str:
        """Detect content importance based on keywords.

        Args:
            content: The text content.

        Returns:
            Importance level: low, normal, high, or critical.
        """
        content_lower = content.lower()

        # Check critical first
        for keyword in self.IMPORTANCE_KEYWORDS["critical"]:
            if keyword.lower() in content_lower:
                return "critical"

        # Check high
        for keyword in self.IMPORTANCE_KEYWORDS["high"]:
            if keyword.lower() in content_lower:
                return "high"

        # Check low
        for keyword in self.IMPORTANCE_KEYWORDS["low"]:
            if keyword.lower() in content_lower:
                return "low"

        return "normal"

    def _generate_relationships(self, token: Token, content_type: ContentType) -> list[dict[str, Any]]:
        """Generate relationships for a block.

        Args:
            token: The markdown-it token.
            content_type: Type of content.

        Returns:
            List of relationship dictionaries.
        """
        relationships: list[dict[str, Any]] = []

        # Add sequential relationship for ordered content
        if content_type in (ContentType.LIST, ContentType.CODE_BLOCK, ContentType.TABLE):
            relationships.append({
                "type": RelationshipType.SEQUENTIAL.value,
                "direction": "next",
            })

        # Add reference relationships for links
        if content_type == ContentType.LINK and token.get("href"):
            relationships.append({
                "type": RelationshipType.REFERENCE.value,
                "target_type": "external",
                "url": token.get("href"),
            })

        return relationships

    def _build_sections(self, blocks: list[SemanticBlock]) -> list[SemanticSection]:
        """Build sections from blocks based on headings.

        Args:
            blocks: List of all content blocks.

        Returns:
            List of SemanticSection objects organized hierarchically.
        """
        sections: list[SemanticSection] = []
        current_section: SemanticSection | None = None
        current_level = 0
        section_stack: list[SemanticSection] = []

        for block in blocks:
            if block.content_type == ContentType.HEADING and block.level:
                # Determine heading level
                level_num = int(block.level.value[1])  # Convert "h1" to 1
                level_enum = {1: HeadingLevel.H1, 2: HeadingLevel.H2, 3: HeadingLevel.H3,
                              4: HeadingLevel.H4, 5: HeadingLevel.H5, 6: HeadingLevel.H6}
                level = level_enum.get(level_num, HeadingLevel.H2)

                # Create new section
                new_section = SemanticSection(
                    id=self._generate_section_id(),
                    title=block.content,
                    level=level,
                    content_type=ContentType.HEADING,
                    blocks=[block],
                    section_type=self._detect_section_type(block.content),
                    importance=block.importance,
                    line_number=block.line_number,
                )

                # Find the right place to add this section
                while section_stack and section_stack[-1].level.value >= block.level.value:
                    section_stack.pop()

                if not section_stack:
                    # Top level section
                    sections.append(new_section)
                    section_stack.append(new_section)
                else:
                    # Nested section
                    parent = section_stack[-1]
                    parent.child_sections.append(new_section)
                    section_stack.append(new_section)

                current_section = new_section
                current_level = level_num
            else:
                # Add block to current section
                if current_section:
                    current_section.blocks.append(block)
                else:
                    # Create a default section for blocks before first heading
                    default_section = SemanticSection(
                        id=self._generate_section_id(),
                        title="Introduction",
                        level=HeadingLevel.H1,
                        content_type=ContentType.TEXT,
                        blocks=[block],
                        section_type="introduction",
                        line_number=block.line_number,
                    )
                    sections.insert(0, default_section)
                    current_section = default_section

        return sections if sections else self._create_default_section(blocks)

    def _detect_section_type(self, title: str) -> str | None:
        """Detect the semantic type of a section from its title.

        Args:
            title: Section title.

        Returns:
            Section type or None.
        """
        title_lower = title.lower()
        for section_type, keywords in self.SECTION_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return section_type
        return None

    def _post_process_sections(self, sections: list[SemanticSection]) -> None:
        """Post-process sections to add statistics and relationships.

        Args:
            sections: List of sections to process.
        """
        for section in sections:
            # Calculate word count for section
            section.word_count = sum(len(b.content.split()) for b in section.blocks)

            # Generate parent-child relationships
            if self.enable_relationships:
                for i, block in enumerate(section.blocks):
                    if i > 0:
                        block.relationships.append({
                            "type": RelationshipType.SEQUENTIAL.value,
                            "related_id": section.blocks[i - 1].id,
                            "direction": "previous",
                        })
                    if i < len(section.blocks) - 1:
                        block.relationships.append({
                            "type": RelationshipType.SEQUENTIAL.value,
                            "related_id": section.blocks[i + 1].id,
                            "direction": "next",
                        })

            # Recursively process child sections
            if section.child_sections:
                self._post_process_sections(section.child_sections)

    def _create_default_section(self, blocks: list[SemanticBlock]) -> list[SemanticSection]:
        """Create a default section when no headings are present.

        Args:
            blocks: List of blocks.

        Returns:
            List with a single default section.
        """
        default_section = SemanticSection(
            id=self._generate_section_id(),
            title="Document",
            level=HeadingLevel.H1,
            content_type=ContentType.TEXT,
            blocks=blocks,
            section_type="general",
            line_number=blocks[0].line_number if blocks else 1,
            word_count=sum(len(b.content.split()) for b in blocks),
        )
        return [default_section]

    def _build_toc(self, sections: list[SemanticSection]) -> list[dict[str, Any]]:
        """Build a table of contents from sections.

        Args:
            sections: List of sections.

        Returns:
            List of TOC entries.
        """
        toc: list[dict[str, Any]] = []

        def process_section(section: SemanticSection, depth: int = 0) -> None:
            entry = {
                "id": section.id,
                "title": section.title,
                "level": depth,
                "type": section.section_type,
                "line_number": section.line_number,
            }
            toc.append(entry)

            for child in section.child_sections:
                process_section(child, depth + 1)

        for section in sections:
            process_section(section)

        return toc

    def _generate_summary(self, document: SemanticDocument) -> dict[str, Any]:
        """Generate an AI-friendly summary of the document.

        Args:
            document: The semantic document.

        Returns:
            Summary dictionary.
        """
        # Count sections by type
        section_types: dict[str, int] = {}
        for section in document.sections:
            if section.section_type:
                section_types[section.section_type] = section_types.get(section.section_type, 0) + 1

        # Find important blocks
        important_blocks = [
            {
                "id": b.id,
                "content_type": b.content_type,
                "content_preview": b.content[:100] + "..." if len(b.content) > 100 else b.content,
                "importance": b.importance,
            }
            for b in document.all_blocks
            if b.importance in ("critical", "high") and b.content_type != ContentType.HEADING
        ]

        # Identify key topics from headings
        topics = [s.title for s in document.sections if s.level.value <= "h2" and s.title]

        return {
            "purpose": f"Document with {len(document.sections)} sections covering {len(topics)} main topics",
            "main_topics": topics[:5],  # Top 5 topics
            "section_breakdown": section_types,
            "key_content": important_blocks[:5],  # Top 5 important blocks
            "reading_level": "intermediate",  # Could be enhanced with readability analysis
        }
