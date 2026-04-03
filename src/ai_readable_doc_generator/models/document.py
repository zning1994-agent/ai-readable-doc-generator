"""
Document domain model as the root aggregate.

This module defines the Document class which serves as the root aggregate
for all document-related data, including metadata, sections, and schema
configuration for AI-readable output generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator

from ai_readable_doc_generator.models.schema import OutputSchema, SchemaType
from ai_readable_doc_generator.models.section import Section, SectionType


@dataclass
class DocumentMetadata:
    """
    Metadata associated with a document.

    Attributes:
        title: The document title.
        description: A brief description of the document.
        author: The document author(s).
        source_path: Original file path or source location.
        created_at: Document creation timestamp.
        modified_at: Document last modification timestamp.
        version: Document version identifier.
        tags: List of document-level tags.
        language: Document language code (e.g., 'en', 'zh').
        custom: Additional custom metadata fields.
    """

    title: str = ""
    description: str = ""
    author: str = ""
    source_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    language: str = "en"
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metadata to dictionary representation.

        Returns:
            Dictionary containing all metadata fields.
        """
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "source_path": self.source_path,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "language": self.language,
            "custom": self.custom,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """
        Create metadata from dictionary representation.

        Args:
            data: Dictionary containing metadata fields.

        Returns:
            DocumentMetadata instance populated from the dictionary.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        modified_at = data.get("modified_at")
        if isinstance(modified_at, str):
            modified_at = datetime.fromisoformat(modified_at)
        elif modified_at is None:
            modified_at = datetime.now()

        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            source_path=data.get("source_path", ""),
            created_at=created_at,
            modified_at=modified_at,
            version=data.get("version", "1.0.0"),
            tags=data.get("tags", []),
            language=data.get("language", "en"),
            custom=data.get("custom", {}),
        )


@dataclass
class Document:
    """
    Root aggregate for document representation.

    The Document class is the central domain model that aggregates all
    document content, metadata, and structural information. It provides
    a unified interface for document manipulation and serialization.

    Attributes:
        metadata: Document-level metadata information.
        sections: List of top-level sections in the document.
        schema: Output schema configuration for serialization.
        id: Unique identifier for this document.
    """

    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    sections: list[Section] = field(default_factory=list)
    schema: OutputSchema = field(default_factory=OutputSchema)
    id: str = ""

    _section_counter: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        """Validate document attributes after initialization."""
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """
        Generate a unique document identifier.

        Returns:
            A unique identifier string.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"doc_{timestamp}"

    def generate_section_id(self, prefix: str = "section") -> str:
        """
        Generate a unique section identifier.

        Args:
            prefix: Prefix for the section ID.

        Returns:
            A unique section identifier string.
        """
        self._section_counter += 1
        return f"{prefix}_{self._section_counter}"

    def add_section(self, section: Section, parent_id: str | None = None) -> None:
        """
        Add a section to the document.

        Args:
            section: The section to add.
            parent_id: Optional ID of a parent section for nesting.
        """
        if parent_id is None:
            self.sections.append(section)
        else:
            parent = self.find_section_by_id(parent_id)
            if parent:
                parent.add_child(section)
            else:
                self.sections.append(section)

    def remove_section(self, section_id: str) -> bool:
        """
        Remove a section from the document by ID.

        Args:
            section_id: The ID of the section to remove.

        Returns:
            True if the section was found and removed, False otherwise.
        """
        for i, section in enumerate(self.sections):
            if section.id == section_id:
                self.sections.pop(i)
                return True
            if section.remove_child(section_id):
                return True
        return False

    def find_section_by_id(self, section_id: str) -> Section | None:
        """
        Find a section by its ID.

        Args:
            section_id: The ID of the section to find.

        Returns:
            The section if found, None otherwise.
        """
        for section in self.sections:
            found = section.find_by_id(section_id)
            if found:
                return found
        return None

    def get_all_sections(self) -> list[Section]:
        """
        Get all sections in the document, including nested ones.

        Returns:
            List of all sections in document order.
        """
        all_sections: list[Section] = []

        def collect_sections(sections: list[Section]) -> None:
            for section in sections:
                all_sections.append(section)
                collect_sections(section.children)

        collect_sections(self.sections)
        return all_sections

    def get_sections_by_type(self, section_type: SectionType) -> list[Section]:
        """
        Get all sections of a specific type.

        Args:
            section_type: The type of sections to find.

        Returns:
            List of matching sections.
        """
        return [s for s in self.get_all_sections() if s.section_type == section_type]

    def get_headings(self) -> list[Section]:
        """
        Get all heading sections in the document.

        Returns:
            List of heading sections in document order.
        """
        return self.get_sections_by_type(SectionType.HEADING)

    def get_code_blocks(self) -> list[Section]:
        """
        Get all code block sections in the document.

        Returns:
            List of code block sections in document order.
        """
        return self.get_sections_by_type(SectionType.CODE_BLOCK)

    def sections_iter(self) -> Iterator[Section]:
        """
        Iterate over all sections in the document.

        Yields:
            Each section in the document, including nested ones.
        """
        for section in self.sections:
            yield section
            yield from section.children

    def update_metadata(self, **kwargs: Any) -> None:
        """
        Update document metadata fields.

        Args:
            **kwargs: Metadata fields to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        self.metadata.modified_at = datetime.now()

    def set_schema_type(self, schema_type: SchemaType) -> None:
        """
        Set the document's output schema type.

        Args:
            schema_type: The new schema type to use.
        """
        self.schema = self.schema.with_type(schema_type)

    def to_dict(self, include_schema: bool = True) -> dict[str, Any]:
        """
        Convert document to dictionary representation.

        Args:
            include_schema: Whether to include schema configuration.

        Returns:
            Dictionary containing all document data.
        """
        result: dict[str, Any] = {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
        }

        if include_schema:
            result["schema"] = self.schema.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """
        Create a document from dictionary representation.

        Args:
            data: Dictionary containing document data.

        Returns:
            Document instance populated from the dictionary.
        """
        metadata = DocumentMetadata.from_dict(data.get("metadata", {}))
        schema_data = data.get("schema", {})
        schema = OutputSchema.from_dict(schema_data) if schema_data else OutputSchema()

        document = cls(
            id=data.get("id", ""),
            metadata=metadata,
            schema=schema,
        )

        for section_data in data.get("sections", []):
            document.sections.append(Section.from_dict(section_data))

        return document

    def to_json_serializable(self) -> dict[str, Any]:
        """
        Convert document to JSON-serializable dictionary.

        This method ensures all values are JSON-serializable primitives.

        Returns:
            JSON-serializable dictionary representation.
        """
        return self.to_dict()

    def get_word_count(self) -> int:
        """
        Calculate the total word count across all sections.

        Returns:
            Total number of words in the document.
        """
        count = 0
        for section in self.get_all_sections():
            count += len(section.content.split())
        return count

    def get_section_count(self) -> int:
        """
        Get the total number of sections including nested ones.

        Returns:
            Total section count.
        """
        return len(self.get_all_sections())

    def __len__(self) -> int:
        """
        Get the number of top-level sections.

        Returns:
            Number of top-level sections.
        """
        return len(self.sections)

    def __iter__(self) -> Iterator[Section]:
        """
        Iterate over top-level sections.

        Yields:
            Each top-level section.
        """
        return iter(self.sections)

    def __repr__(self) -> str:
        """
        Return a string representation of the document.

        Returns:
            String representation of the document.
        """
        title = self.metadata.title or "Untitled Document"
        section_count = self.get_section_count()
        return f"Document(id={self.id!r}, title={title!r}, sections={section_count})"
