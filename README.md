# AI-Readable Doc Generator

Transform documentation into AI-Agent-friendly formats with structured output and semantic tagging.

## Features

- **Structured Output**: Convert Markdown to JSON/YAML with explicit schema definitions
- **Semantic Tagging**: Automatic content classification with semantic markers
- **MCP Compatible**: Native support for Model Context Protocol integration
- **Rich Metadata**: Extract titles, descriptions, reading time, and statistics
- **Table of Contents**: Auto-generated navigation structure
- **Importance Detection**: Identify critical, high, and normal priority content

## Installation

```bash
pip install ai-readable-doc-generator
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Convert a Markdown file
ai-doc-gen convert document.md

# Output to JSON
ai-doc-gen convert document.md --format json

# Output to YAML
ai-doc-gen convert document.md --format yaml

# Output to MCP format
ai-doc-gen convert document.md --format mcp
```

### Python API

```python
from ai_readable_doc_generator import MarkdownConverter

# Initialize converter
converter = MarkdownConverter(
    add_table_of_contents=True,
    add_statistics=True,
    extract_semantic_tags=True,
)

# Convert Markdown file
doc = converter.convert("document.md")

# Or parse content directly
doc = converter.parse("# Title\n\nContent here...")

# Access semantic document
print(f"Title: {doc.metadata.title}")
print(f"Sections: {len(doc.sections)}")
print(f"Word Count: {doc.metadata.word_count}")

# Export to JSON
json_output = doc.to_json()
```

## Output Format

The converter produces a `SemanticDocument` with the following structure:

```json
{
  "version": "1.0",
  "metadata": {
    "source_format": "markdown",
    "title": "Document Title",
    "word_count": 1000,
    "reading_time_minutes": 5.0
  },
  "sections": [
    {
      "id": "section_001",
      "title": "Introduction",
      "level": "h1",
      "blocks": [...],
      "section_type": "introduction"
    }
  ],
  "table_of_contents": [...],
  "statistics": {
    "total_sections": 5,
    "total_blocks": 50,
    "content_types": {...}
  },
  "semantic_summary": {
    "purpose": "...",
    "main_topics": [...],
    "key_content": [...]
  }
}
```

## Supported Content Types

| Type | Description |
|------|-------------|
| `text` | Plain text paragraphs |
| `heading` | H1-H6 headings |
| `code_block` | Fenced code blocks with language |
| `list` | Bullet and numbered lists |
| `blockquote` | Quoted text |
| `link` | Hyperlinks |
| `image` | Images with alt text |
| `table` | Tables |
| `emphasis` | *Italic* text |
| `strong` | **Bold** text |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Markdown Parser | markdown-it-py |
| Data Models | Pydantic |
| CLI | Click |
| Terminal Output | Rich |

## Project Structure

```
src/ai_readable_doc_generator/
├── __init__.py
├── base.py              # Base converter class
├── converter.py        # MarkdownConverter implementation
├── document.py          # Internal document model
└── models/
    ├── __init__.py
    └── schema.py        # Semantic document schemas
tests/
├── __init__.py
├── test_base.py
├── test_converter.py
├── test_document.py
└── models/
    ├── __init__.py
    └── test_schema.py
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_readable_doc_generator

# Run specific test file
pytest tests/test_converter.py
```

## License

MIT License
