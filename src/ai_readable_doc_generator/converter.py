"""Document converter implementations."""

import re
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag

from .base import BaseConverter
from .models import (
    ContentClassification,
    Document,
    DocumentMetadata,
    ImportanceLevel,
    Section,
    SectionType,
)


# Mapping of HTML tags to section types
TAG_TO_SECTION_TYPE: dict[str, SectionType] = {
    "html": SectionType.DOCUMENT,
    "body": SectionType.DOCUMENT,
    "article": SectionType.ARTICLE,
    "main": SectionType.MAIN,
    "section": SectionType.SECTION,
    "nav": SectionType.NAVIGATION,
    "aside": SectionType.ASIDE,
    "header": SectionType.HEADER,
    "footer": SectionType.FOOTER,
    "h1": SectionType.HEADING,
    "h2": SectionType.HEADING,
    "h3": SectionType.HEADING,
    "h4": SectionType.HEADING,
    "h5": SectionType.HEADING,
    "h6": SectionType.HEADING,
    "p": SectionType.PARAGRAPH,
    "ul": SectionType.LIST,
    "ol": SectionType.LIST,
    "li": SectionType.LIST_ITEM,
    "pre": SectionType.CODE,
    "code": SectionType.CODE,
    "table": SectionType.TABLE,
    "tr": SectionType.TABLE_ROW,
    "th": SectionType.TABLE_CELL,
    "td": SectionType.TABLE_CELL,
    "blockquote": SectionType.BLOCKQUOTE,
    "img": SectionType.IMAGE,
    "a": SectionType.LINK,
    "div": SectionType.DIVISION,
    "span": SectionType.SPAN,
}

# Classification patterns for semantic tagging
CLASSIFICATION_PATTERNS: dict[ContentClassification, list[str]] = {
    ContentClassification.WARNING: [
        "warning",
        "alert",
        "error",
        "danger",
        "caution",
    ],
    ContentClassification.NOTE: [
        "note",
        "info",
        "tip",
        "hint",
        "info-box",
    ],
    ContentClassification.TUTORIAL: [
        "tutorial",
        "how-to",
        "guide",
        "walkthrough",
    ],
    ContentClassification.REFERENCE: [
        "reference",
        "api",
        "docs",
        "documentation",
    ],
    ContentClassification.CODE_LITERAL: [
        "code",
        "syntax",
        "example",
        "snippet",
    ],
}

# Importance level patterns
IMPORTANCE_PATTERNS: dict[ImportanceLevel, list[str]] = {
    ImportanceLevel.CRITICAL: ["critical", "important", "required"],
    ImportanceLevel.HIGH: ["high", "primary", "main"],
    ImportanceLevel.LOW: ["secondary", "optional", "extra"],
}


class HtmlConverter(BaseConverter):
    """Converter for HTML documents using BeautifulSoup4 with lxml parser.

    Extracts semantic structure from HTML documents including:
    - Semantic HTML5 elements (article, section, nav, aside, etc.)
    - Headings with proper hierarchy levels
    - Lists and nested list structures
    - Code blocks and inline code
    - Tables with header and data cells
    - Links and images
    - Semantic classes and IDs for classification
    """

    def __init__(
        self,
        extract_scripts: bool = False,
        extract_styles: bool = False,
        ignore_hidden: bool = True,
    ) -> None:
        """Initialize HTML converter.

        Args:
            extract_scripts: Whether to extract script content.
            extract_styles: Whether to extract style content.
            ignore_hidden: Whether to ignore hidden elements.
        """
        self.extract_scripts = extract_scripts
        self.extract_styles = extract_styles
        self.ignore_hidden = ignore_hidden

    def validate(self, source: str) -> bool:
        """Validate if source contains valid HTML.

        Args:
            source: The HTML source to validate.

        Returns:
            bool: True if valid HTML, False otherwise.
        """
        try:
            soup = BeautifulSoup(source, "lxml")
            return soup.find() is not None
        except Exception:
            return False

    def convert(self, source: str) -> Document:
        """Convert HTML source to Document.

        Args:
            source: The HTML source content.

        Returns:
            Document: The converted document with semantic structure.
        """
        soup = BeautifulSoup(source, "lxml")

        # Extract metadata
        metadata = self._extract_metadata(soup)

        # Build document structure
        sections = self._extract_sections(soup.body if soup.body else soup)

        # Create document
        document = Document(
            content=self._extract_text_content(soup),
            metadata=metadata,
            sections=sections,
            raw_content=source,
        )

        return self.postprocess(document)

    def preprocess(self, source: str) -> str:
        """Preprocess HTML source.

        Args:
            source: The raw HTML source.

        Returns:
            str: Preprocessed HTML.
        """
        # Normalize whitespace
        source = re.sub(r"\s+", " ", source)
        return source

    def postprocess(self, document: Document) -> Document:
        """Postprocess converted document.

        Args:
            document: The converted document.

        Returns:
            Document: Postprocessed document.
        """
        # Flatten empty sections
        document.sections = self._flatten_empty_sections(document.sections)
        return document

    def _extract_metadata(self, soup: BeautifulSoup) -> DocumentMetadata:
        """Extract metadata from HTML document.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            DocumentMetadata: Extracted metadata.
        """
        metadata = DocumentMetadata()
        metadata.source_type = "html"

        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            metadata.title = self._get_text(title_tag)

        # Extract meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", "")
            property_attr = meta.get("property", "")
            content = meta.get("content", "")

            if name == "description" or property_attr == "og:description":
                metadata.description = content
            elif name == "author":
                metadata.author = content
            elif name == "keywords":
                metadata.tags = [k.strip() for k in content.split(",")]
            elif property_attr == "og:title":
                metadata.title = metadata.title or content

        # Extract language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            metadata.language = html_tag.get("lang")

        return metadata

    def _extract_sections(self, element: Tag | NavigableString) -> list[Section]:
        """Extract sections from HTML element recursively.

        Args:
            element: BeautifulSoup element to process.

        Returns:
            list[Section]: List of extracted sections.
        """
        sections = []

        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                return [
                    Section(
                        section_type=SectionType.PARAGRAPH,
                        content=text,
                        classification=self._classify_content(text),
                    )
                ]
            return []

        if not isinstance(element, Tag):
            return []

        # Skip hidden elements if configured
        if self.ignore_hidden and self._is_hidden(element):
            return []

        # Skip script and style elements unless configured
        tag_name = element.name.lower()
        if tag_name == "script" and not self.extract_scripts:
            return []
        if tag_name == "style" and not self.extract_styles:
            return []

        # Determine section type
        section_type = self._get_section_type(element)

        # Handle heading elements
        level = self._get_heading_level(element)

        # Get element content
        content = self._get_element_content(element)

        # Skip empty structural elements that have children
        if not content.strip() and self._has_meaningful_children(element):
            # Process children instead
            for child in element.children:
                child_sections = self._extract_sections(child)
                sections.extend(child_sections)
            return sections

        # Create section
        section = Section(
            section_type=section_type,
            content=content,
            level=level,
            metadata=self._extract_element_metadata(element),
            classification=self._classify_element(element),
            importance=self._determine_importance(element),
            id=element.get("id"),
            classes=self._get_classes(element),
            raw_attributes=self._get_raw_attributes(element),
        )

        # Process children recursively
        for child in element.children:
            if isinstance(child, Tag):
                # Skip if this is a self-closing element we're already handling
                if child.name in ("img", "br", "hr", "input", "meta", "link"):
                    continue
                child_sections = self._extract_sections(child)
                for child_section in child_sections:
                    section.add_child(child_section)

        sections.append(section)
        return sections

    def _get_section_type(self, element: Tag) -> SectionType:
        """Get section type for HTML element.

        Args:
            element: HTML element.

        Returns:
            SectionType: Corresponding section type.
        """
        tag_name = element.name.lower()

        if tag_name in TAG_TO_SECTION_TYPE:
            return TAG_TO_SECTION_TYPE[tag_name]

        # Check class for semantic hints
        classes = self._get_classes(element)
        for cls in classes:
            cls_lower = cls.lower()
            for sec_type, patterns in TAG_TO_SECTION_TYPE.items():
                if cls_lower in patterns if isinstance(patterns, list) else False:
                    return sec_type

        return SectionType.UNKNOWN

    def _get_heading_level(self, element: Tag) -> int:
        """Get heading level for heading elements.

        Args:
            element: HTML element.

        Returns:
            int: Heading level (1-6) or 1 for non-headings.
        """
        tag_name = element.name.lower()
        if tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return int(tag_name[1])
        return 1

    def _get_element_content(self, element: Tag) -> str:
        """Get text content of element.

        Args:
            element: HTML element.

        Returns:
            str: Text content.
        """
        # Special handling for code blocks
        if element.name in ("pre", "code"):
            return element.get_text()

        # For other elements, get text without extra whitespace
        return " ".join(element.get_text().split())

    def _get_text(self, element: Tag | NavigableString) -> str:
        """Get text content of element.

        Args:
            element: BeautifulSoup element.

        Returns:
            str: Text content.
        """
        if isinstance(element, NavigableString):
            return str(element).strip()
        return element.get_text().strip()

    def _has_meaningful_children(self, element: Tag) -> bool:
        """Check if element has meaningful children.

        Args:
            element: HTML element.

        Returns:
            bool: True if has meaningful children.
        """
        for child in element.children:
            if isinstance(child, Tag):
                if child.name not in ("script", "style", "meta", "link"):
                    return True
            elif isinstance(child, NavigableString):
                if str(child).strip():
                    return True
        return False

    def _is_hidden(self, element: Tag) -> bool:
        """Check if element is hidden.

        Args:
            element: HTML element.

        Returns:
            bool: True if hidden.
        """
        style = element.get("style", "")
        if "display:none" in style or "visibility:hidden" in style:
            return True

        classes = self._get_classes(element)
        if "hidden" in classes or "sr-only" in classes:
            return True

        return False

    def _extract_element_metadata(self, element: Tag) -> dict[str, Any]:
        """Extract metadata from element.

        Args:
            element: HTML element.

        Returns:
            dict: Element metadata.
        """
        metadata: dict[str, Any] = {}

        # Extract common attributes
        if element.get("id"):
            metadata["html_id"] = element.get("id")
        if element.get("class"):
            metadata["html_classes"] = element.get("class")
        if element.get("title"):
            metadata["title"] = element.get("title")
        if element.get("alt"):
            metadata["alt"] = element.get("alt")

        # Extract data attributes
        for attr, value in element.attrs.items():
            if attr.startswith("data-"):
                metadata[attr] = value

        return metadata

    def _classify_element(self, element: Tag) -> ContentClassification:
        """Classify element content.

        Args:
            element: HTML element.

        Returns:
            ContentClassification: Content classification.
        """
        classes = self._get_classes(element)
        element_id = element.get("id", "").lower()

        # Check class patterns
        for classification, patterns in CLASSIFICATION_PATTERNS.items():
            for pattern in patterns:
                if pattern in classes or pattern in element_id:
                    return classification

        # Infer from element type
        if element.name in ("pre", "code"):
            return ContentClassification.CODE_LITERAL
        if element.name in ("script", "style", "meta"):
            return ContentClassification.METADATA
        if element.name == "nav":
            return ContentClassification.NAVIGATION

        # Check for semantic class names
        class_str = " ".join(classes).lower()
        if any(word in class_str for word in ["warning", "alert", "error"]):
            return ContentClassification.WARNING
        if any(word in class_str for word in ["note", "info", "tip"]):
            return ContentClassification.NOTE

        return ContentClassification.UNKNOWN

    def _classify_content(self, content: str) -> ContentClassification:
        """Classify text content.

        Args:
            content: Text content.

        Returns:
            ContentClassification: Content classification.
        """
        content_lower = content.lower()

        if any(word in content_lower for word in ["warning:", "caution:", "danger:"]):
            return ContentClassification.WARNING
        if any(word in content_lower for word in ["note:", "tip:", "info:"]):
            return ContentClassification.NOTE

        return ContentClassification.UNKNOWN

    def _determine_importance(self, element: Tag) -> ImportanceLevel:
        """Determine importance level of element.

        Args:
            element: HTML element.

        Returns:
            ImportanceLevel: Importance level.
        """
        classes = self._get_classes(element)
        element_id = element.get("id", "").lower()
        class_str = " ".join(classes + [element_id]).lower()

        # Check for importance indicators
        for level, patterns in IMPORTANCE_PATTERNS.items():
            for pattern in patterns:
                if pattern in class_str:
                    return level

        # Heading levels indicate importance
        if element.name in ("h1", "h2"):
            return ImportanceLevel.HIGH
        if element.name in ("h3", "h4"):
            return ImportanceLevel.MEDIUM

        return ImportanceLevel.MEDIUM

    def _get_classes(self, element: Tag) -> list[str]:
        """Get CSS classes from element.

        Args:
            element: HTML element.

        Returns:
            list[str]: List of class names.
        """
        class_attr = element.get("class", [])
        if isinstance(class_attr, str):
            return class_attr.split()
        return list(class_attr)

    def _get_raw_attributes(self, element: Tag) -> dict[str, str]:
        """Get raw attributes from element.

        Args:
            element: HTML element.

        Returns:
            dict: Raw attributes.
        """
        return {k: str(v) for k, v in element.attrs.items()}

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract plain text content from document.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            str: Plain text content.
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        return soup.get_text(separator=" ", strip=True)

    def _flatten_empty_sections(self, sections: list[Section]) -> list[Section]:
        """Remove or flatten empty sections.

        Args:
            sections: List of sections.

        Returns:
            list[Section]: Flattened sections.
        """
        result = []

        for section in sections:
            # Recursively flatten children
            section.children = self._flatten_empty_sections(section.children)

            # Keep section if it has content or children
            if section.content.strip() or section.children:
                # If section has children and no content, transfer children to result
                if not section.content.strip() and section.children:
                    result.extend(section.children)
                else:
                    result.append(section)

        return result
