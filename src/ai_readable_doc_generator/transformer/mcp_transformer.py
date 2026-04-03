"""MCP (Model Context Protocol) transformer for AI agent compatibility."""

import json
from typing import Any

from ai_readable_doc_generator.models.document import Document
from ai_readable_doc_generator.models.section import ContentType
from ai_readable_doc_generator.transformer.base_transformer import BaseTransformer


class MCPTransformer(BaseTransformer):
    """Transformer that converts documents to MCP-compatible format.

    The Model Context Protocol requires structured, standardized input
    with explicit semantic markers. This transformer produces output
    that is optimized for consumption by MCP-capable AI agents.

    MCP Format Structure:
        - resources: List of document resources
        - resource_uri: Unique identifier for the resource
        - content: Structured content with semantic annotations
        - annotations: Metadata for AI processing

    Example:
        >>> from ai_readable_doc_generator import Document, Section, ContentType
        >>> from ai_readable_doc_generator.transformer import MCPTransformer
        >>> doc = Document(title="Test Doc")
        >>> transformer = MCPTransformer()
        >>> mcp_output = transformer.transform(doc)
    """

    def __init__(
        self,
        validate_output: bool = True,
        include_annotations: bool = True,
        semantic_hints: bool = True,
    ) -> None:
        """Initialize the MCP transformer.

        Args:
            validate_output: Whether to validate transformed output.
            include_annotations: Whether to include AI annotations.
            semantic_hints: Whether to include semantic hints for AI.
        """
        super().__init__(validate_output=validate_output)
        self.include_annotations = include_annotations
        self.semantic_hints = semantic_hints

    def transform(self, document: Document) -> str:
        """Transform a document to MCP-compatible format.

        Args:
            document: The document to transform.

        Returns:
            JSON string in MCP format.

        Raises:
            ValueError: If document validation fails.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        mcp_data = self._create_mcp_resource(document)
        return json.dumps(mcp_data, indent=2, ensure_ascii=False)

    def transform_to_dict(self, document: Document) -> dict[str, Any]:
        """Transform a document to MCP dictionary format.

        Args:
            document: The document to transform.

        Returns:
            Dictionary in MCP format.

        Raises:
            ValueError: If document validation fails.
        """
        if self.validate_output and not self.validate(document):
            raise ValueError("Invalid document: must have title or sections")

        return self._create_mcp_resource(document)

    def _create_mcp_resource(self, document: Document) -> dict[str, Any]:
        """Create an MCP resource from a document.

        Args:
            document: The document to convert.

        Returns:
            MCP-formatted resource dictionary.
        """
        resource_uri = self._generate_resource_uri(document)

        mcp_resource: dict[str, Any] = {
            "resource_uri": resource_uri,
            "resource_type": "documentation",
            "content": {
                "title": document.title,
                "sections": [self._transform_section_for_mcp(s) for s in document.sections],
                "metadata": self._create_metadata(document),
            },
        }

        if self.include_annotations:
            mcp_resource["annotations"] = self._create_annotations(document)

        if self.semantic_hints:
            mcp_resource["semantic_hints"] = self._create_semantic_hints(document)

        return mcp_resource

    def _generate_resource_uri(self, document: Document) -> str:
        """Generate a unique resource URI for the document.

        Args:
            document: The document to generate URI for.

        Returns:
            A unique resource URI.
        """
        import hashlib

        # Create a deterministic URI based on document content
        content_hash = hashlib.sha256()
        content_hash.update(document.title.encode())
        for section in document.sections:
            content_hash.update(section.content.encode())

        hash_suffix = content_hash.hexdigest()[:12]
        title_slug = document.title.lower().replace(" ", "-")[:20]
        return f"doc://ai-doc-gen/{title_slug}/{hash_suffix}"

    def _transform_section_for_mcp(self, section: Any) -> dict[str, Any]:
        """Transform a section for MCP format.

        Args:
            section: The section to transform.

        Returns:
            MCP-formatted section dictionary.
        """
        mcp_section: dict[str, Any] = {
            "id": section.id,
            "content": section.content,
            "type": self._map_content_type(section.content_type),
            "level": section.level,
            "purpose": self._infer_section_purpose(section),
        }

        if section.children:
            mcp_section["subsections"] = [
                self._transform_section_for_mcp(child) for child in section.children
            ]

        if section.tags:
            mcp_section["classifications"] = section.tags

        if section.importance >= 4:  # High importance
            mcp_section["is_critical"] = True

        return mcp_section

    def _map_content_type(self, content_type: ContentType) -> str:
        """Map internal content type to MCP content type.

        Args:
            content_type: Internal content type.

        Returns:
            MCP-compatible content type string.
        """
        type_mapping = {
            ContentType.TITLE: "title",
            ContentType.HEADING: "heading",
            ContentType.PARAGRAPH: "prose",
            ContentType.CODE_BLOCK: "code",
            ContentType.LIST: "list",
            ContentType.LIST_ITEM: "list_item",
            ContentType.BLOCKQUOTE: "quote",
            ContentType.TABLE: "table",
            ContentType.IMAGE: "image",
            ContentType.LINK: "link",
            ContentType.HORIZONTAL_RULE: "divider",
            ContentType.HTML: "html",
            ContentType.FRONTMATTER: "metadata",
            ContentType.UNKNOWN: "unknown",
        }
        return type_mapping.get(content_type, "unknown")

    def _infer_section_purpose(self, section: Any) -> str:
        """Infer the purpose of a section based on its content and type.

        Args:
            section: The section to analyze.

        Returns:
            Purpose string describing the section's role.
        """
        content_lower = section.content.lower()

        # Check for common purpose indicators
        if any(
            word in content_lower
            for word in ["example", "sample", "demo", "usage"]
        ):
            return "example"
        if any(
            word in content_lower
            for word in ["note", "warning", "caution", "tip"]
        ):
            return "advisory"
        if any(
            word in content_lower
            for word in ["install", "setup", "configure", "setup"]
        ):
            return "instruction"
        if any(
            word in content_lower
            for word in ["api", "reference", "specification"]
        ):
            return "reference"
        if any(
            word in content_lower
            for word in ["troubleshoot", "faq", "question"]
        ):
            return "support"
        if section.content_type in (ContentType.CODE_BLOCK,):
            return "example"

        # Default based on content type
        if section.content_type == ContentType.HEADING:
            return "topic"
        return "content"

    def _create_metadata(self, document: Document) -> dict[str, Any]:
        """Create metadata for MCP format.

        Args:
            document: The document to create metadata for.

        Returns:
            Metadata dictionary.
        """
        metadata: dict[str, Any] = {
            "source_format": document.source_format,
            "language": document.language,
            "section_count": len(document.sections),
            "total_content_length": sum(
                len(s.content) for s in document.get_all_sections()
            ),
        }

        if document.source_path:
            metadata["source_path"] = document.source_path

        if document.tags:
            metadata["document_tags"] = document.tags

        return metadata

    def _create_annotations(self, document: Document) -> dict[str, Any]:
        """Create AI annotations for MCP format.

        Args:
            document: The document to create annotations for.

        Returns:
            Annotations dictionary for AI processing.
        """
        sections = document.get_all_sections()
        content_types = [s.content_type for s in sections]
        purposes = [self._infer_section_purpose(s) for s in sections]

        return {
            "structure_type": self._classify_document_structure(document),
            "content_type_distribution": self._count_content_types(content_types),
            "purpose_distribution": self._count_purposes(purposes),
            "has_code_examples": ContentType.CODE_BLOCK in content_types,
            "is_api_reference": "reference" in purposes,
            "has_installation_guide": any(
                "install" in s.content.lower() for s in sections
            ),
        }

    def _create_semantic_hints(self, document: Document) -> dict[str, Any]:
        """Create semantic hints for AI consumption.

        Args:
            document: The document to create hints for.

        Returns:
            Semantic hints dictionary.
        """
        sections = document.get_all_sections()

        # Analyze headings for structure
        headings = [s for s in sections if s.content_type == ContentType.HEADING]

        hints: dict[str, Any] = {
            "primary_topic": document.title,
            "key_concepts": self._extract_key_concepts(sections),
            "reading_order": ["sequential"],
        }

        if len(headings) > 5:
            hints["reading_order"] = ["hierarchical", "sequential"]

        return hints

    def _classify_document_structure(self, document: Document) -> str:
        """Classify the overall structure of the document.

        Args:
            document: The document to classify.

        Returns:
            Structure type string.
        """
        sections = document.get_all_sections()
        content_types = [s.content_type for s in sections]

        if ContentType.CODE_BLOCK in content_types:
            code_ratio = content_types.count(ContentType.CODE_BLOCK) / len(content_types)
            if code_ratio > 0.3:
                return "tutorial"

        if len([s for s in sections if s.content_type == ContentType.TABLE]) > 2:
            return "reference"

        headings = [s for s in sections if s.content_type == ContentType.HEADING]
        if len(headings) > len(sections) * 0.5:
            return "outline"

        return "narrative"

    def _count_content_types(self, content_types: list[ContentType]) -> dict[str, int]:
        """Count occurrences of each content type.

        Args:
            content_types: List of content types.

        Returns:
            Dictionary of content type counts.
        """
        counts: dict[str, int] = {}
        for ct in content_types:
            key = ct.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_purposes(self, purposes: list[str]) -> dict[str, int]:
        """Count occurrences of each purpose.

        Args:
            purposes: List of purposes.

        Returns:
            Dictionary of purpose counts.
        """
        counts: dict[str, int] = {}
        for purpose in purposes:
            counts[purpose] = counts.get(purpose, 0) + 1
        return counts

    def _extract_key_concepts(self, sections: list[Any]) -> list[str]:
        """Extract key concepts from sections.

        Args:
            sections: List of sections.

        Returns:
            List of key concept strings.
        """
        # Simple extraction based on heading content
        concepts: list[str] = []
        for section in sections:
            if section.content_type == ContentType.HEADING:
                # Take first 50 chars of heading as concept
                concept = section.content[:50].strip()
                if concept:
                    concepts.append(concept)

        return concepts[:10]  # Limit to top 10

    def __repr__(self) -> str:
        """Return string representation of MCP transformer."""
        return (
            f"MCPTransformer(annotations={self.include_annotations}, "
            f"hints={self.semantic_hints})"
        )
