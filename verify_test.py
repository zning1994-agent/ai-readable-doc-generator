#!/usr/bin/env python3
"""Quick verification script for Document model."""

import sys
sys.path.insert(0, "src")

from ai_readable_doc_generator.models import (
    Document,
    DocumentMetadata,
    OutputSchema,
    SchemaType,
    Section,
    SectionType,
    ContentType,
)

def main():
    print("Testing Document Model...")

    # Create a document with metadata
    metadata = DocumentMetadata(
        title="Test Document",
        description="A test document for verification",
        author="Test Author",
        language="en",
    )

    doc = Document(metadata=metadata)

    # Add sections
    section1 = Section(
        id="intro",
        section_type=SectionType.HEADING,
        content="Introduction",
        content_type=ContentType.NARRATIVE,
    )

    section2 = Section(
        id="code-example",
        section_type=SectionType.CODE_BLOCK,
        content="print('Hello, World!')",
        content_type=ContentType.EXAMPLE,
    )

    doc.add_section(section1)
    doc.add_section(section2)

    # Test nested section
    child = Section(id="nested", content="Nested content")
    doc.add_section(child, parent_id="intro")

    # Verify structure
    print(f"Document ID: {doc.id}")
    print(f"Title: {doc.metadata.title}")
    print(f"Total sections: {doc.get_section_count()}")
    print(f"Headings: {len(doc.get_headings())}")
    print(f"Code blocks: {len(doc.get_code_blocks())}")
    print(f"Word count: {doc.get_word_count()}")

    # Test serialization
    data = doc.to_dict()
    print(f"\nSerialized to dict with {len(data['sections'])} sections")

    # Test deserialization
    doc2 = Document.from_dict(data)
    print(f"Deserialized document: {doc2.metadata.title}")

    # Test schema
    doc.set_schema_type(SchemaType.MCP)
    print(f"Schema type set to: {doc.schema.schema_type.value}")

    print("\n✅ All verifications passed!")

if __name__ == "__main__":
    main()
