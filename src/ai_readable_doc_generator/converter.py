"""Document converter for transforming documents to AI-readable formats."""

import json
from typing import Any, Optional

from .models.document import Document, MarkdownParser, DocumentSection
from .models.schema import (
    OutputFormat,
    SectionType,
    ContentClassification,
    SemanticTag,
    Relationship
)
from .parser.plugins.semantic_tagger import SemanticTagger


class DocumentConverter:
    """
    Converts documents to AI-readable formats with semantic tagging.

    This is the main entry point for document conversion, supporting:
    - Markdown input parsing
    - Semantic tagging
    - Multiple output formats (JSON, YAML, MCP)
    """

    def __init__(self):
        self.parser = MarkdownParser()
        self.tagger = SemanticTagger()

    def convert(
        self,
        content: str,
        source_name: str = "",
        output_format: OutputFormat = OutputFormat.JSON,
        include_metadata: bool = True,
        tag_sections: bool = True,
        tag_content_types: bool = True,
        extract_relationships: bool = True,
        add_importance: bool = False
    ) -> dict[str, Any]:
        """
        Convert document content to AI-readable format.

        Args:
            content: The document content (Markdown)
            source_name: Name or path identifier for the source
            output_format: Desired output format
            include_metadata: Include document metadata in output
            tag_sections: Add semantic tags to sections
            tag_content_types: Classify content types
            extract_relationships: Extract section relationships
            add_importance: Add importance indicators

        Returns:
            Dictionary representation of the converted document
        """
        # Parse document
        document = self.parser.parse(content, source_name)

        # Apply semantic tagging
        if tag_sections or tag_content_types:
            self._apply_semantic_tags(document, tag_sections, tag_content_types)

        # Extract relationships
        if extract_relationships:
            self._extract_relationships(document)

        # Add importance indicators
        if add_importance:
            self._add_importance(document)

        # Build output
        output = self._build_output(
            document,
            include_metadata,
            extract_relationships
        )

        return output

    def _apply_semantic_tags(
        self,
        document: Document,
        tag_sections: bool,
        tag_content_types: bool
    ) -> None:
        """Apply semantic tags to document sections."""
        for section in document.sections:
            if tag_sections:
                # Add section type tag
                section.semantic_tags.append(
                    SemanticTag(
                        name="section_type",
                        value=section.type.value,
                        confidence=1.0
                    )
                )

                # Add heading level tag for headings
                if section.type.value.startswith("heading_"):
                    section.semantic_tags.append(
                        SemanticTag(
                            name="heading_level",
                            value=str(section.level),
                            confidence=1.0
                        )
                    )

            if tag_content_types:
                # Classify content type
                classification = self.tagger.classify_content(
                    section.content,
                    section.type
                )
                section.classification = classification

                if classification:
                    section.semantic_tags.append(
                        SemanticTag(
                            name="content_class",
                            value=classification.value,
                            confidence=0.85
                        )
                    )

                # Detect special content patterns
                special_tags = self.tagger.detect_patterns(section.content)
                section.semantic_tags.extend(special_tags)

    def _extract_relationships(self, document: Document) -> None:
        """Extract relationships between document sections."""
        sections = document.sections
        heading_sections = [
            (i, s) for i, s in enumerate(sections)
            if s.type.value.startswith("heading_")
        ]

        for i, section in heading_sections:
            # Relationship to previous heading (parent/sibling)
            if i > 0:
                prev_idx, prev_section = heading_sections[i - 1]
                if prev_section.level < section.level:
                    # Parent relationship
                    document.relationships.append(
                        Relationship(
                            source_id=section.id,
                            target_id=prev_section.id,
                            relationship_type="parent",
                            metadata={"parent_level": prev_section.level}
                        )
                    )
                elif prev_section.level == section.level:
                    # Sibling relationship
                    document.relationships.append(
                        Relationship(
                            source_id=section.id,
                            target_id=prev_section.id,
                            relationship_type="sibling"
                        )
                    )

            # Code examples relationship
            if section.type == SectionType.HEADING_1 and "example" in section.content.lower():
                # Look for code blocks after this heading
                for j in range(i + 1, min(i + 5, len(sections))):
                    if sections[j].type == SectionType.CODE_BLOCK:
                        document.relationships.append(
                            Relationship(
                                source_id=section.id,
                                target_id=sections[j].id,
                                relationship_type="contains_example"
                            )
                        )

    def _add_importance(self, document: Document) -> None:
        """Add importance indicators to sections."""
        for section in document.sections:
            importance = 1  # Default

            # Check for important indicators
            content_lower = section.content.lower()

            if any(word in content_lower for word in ["warning", "danger", "critical"]):
                importance = 3
            elif any(word in content_lower for word in ["important", "note", "caution"]):
                importance = 2
            elif section.type.value.startswith("heading_") and section.level == 1:
                importance = 2

            section.metadata["importance"] = importance

    def _build_output(
        self,
        document: Document,
        include_metadata: bool,
        include_relationships: bool
    ) -> dict[str, Any]:
        """Build the final output dictionary."""
        output = {}

        if include_metadata:
            output["metadata"] = document.metadata.to_dict()

        output["content"] = [section.to_dict() for section in document.sections]
        output["structure"] = document.structure.to_dict()

        # Aggregate semantic tags by type
        all_tags: dict[str, list[dict[str, Any]]] = {}
        for section in document.sections:
            for tag in section.semantic_tags:
                if tag.name not in all_tags:
                    all_tags[tag.name] = []
                all_tags[tag.name].append({
                    "section_id": section.id,
                    "value": tag.value,
                    "confidence": tag.confidence
                })

        output["semantic_tags"] = all_tags

        if include_relationships:
            output["relationships"] = [
                rel.to_dict() for rel in document.relationships
            ]

        return output

    def to_json(self, document: Document, pretty: bool = True) -> str:
        """Convert document to JSON string."""
        output = document.to_dict()
        if pretty:
            return json.dumps(output, indent=2, ensure_ascii=False)
        return json.dumps(output, ensure_ascii=False)

    def to_mcp_format(self, document: Document) -> dict[str, Any]:
        """
        Convert document to MCP-specific format.

        MCP format includes additional metadata and structure
        optimized for AI agent consumption.
        """
        base_output = document.to_dict()

        # Add MCP-specific enhancements
        mcp_output = {
            "document": {
                "metadata": base_output.get("metadata", {}),
                "sections": base_output.get("content", []),
                "structure": base_output.get("structure", {}),
                "semantic_analysis": base_output.get("semantic_tags", {})
            },
            "relationships": base_output.get("relationships", []),
            "summary": {
                "total_sections": len(base_output.get("content", [])),
                "section_types": self._count_section_types(document),
                "has_code_examples": any(
                    s.type == SectionType.CODE_BLOCK for s in document.sections
                ),
                "complexity_score": self._calculate_complexity(document)
            },
            "context": {
                "depth": document.structure.max_heading_level,
                "word_count": document.metadata.word_count,
                "has_front_matter": bool(document.metadata.front_matter)
            }
        }

        return mcp_output

    def _count_section_types(self, document: Document) -> dict[str, int]:
        """Count sections by type."""
        counts: dict[str, int] = {}
        for section in document.sections:
            type_name = section.type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def _calculate_complexity(self, document: Document) -> float:
        """Calculate document complexity score."""
        score = 0.0

        # Factor 1: Structure depth
        score += document.structure.max_heading_level * 0.5

        # Factor 2: Code blocks
        code_count = sum(
            1 for s in document.sections
            if s.type == SectionType.CODE_BLOCK
        )
        score += min(code_count * 0.3, 2.0)

        # Factor 3: Word count (normalized)
        word_count = document.metadata.word_count
        score += min(word_count / 1000, 3.0)

        return round(score, 2)
