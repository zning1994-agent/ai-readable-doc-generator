"""
Pytest configuration and shared fixtures for ai-readable-doc-generator tests.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_markdown_content() -> str:
    """Provide sample markdown content for testing."""
    return """# Sample Document

## Introduction

This is an introduction to the document.

## Main Content

Here is the main content with:
- List item 1
- List item 2
- List item 3

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This is the conclusion.
"""


@pytest.fixture
def complex_markdown_content() -> str:
    """Provide complex markdown with various elements."""
    return """---
title: Complex Document
author: Test Author
date: 2024-01-01
---

# API Documentation

## Overview

This is the API overview.

## Endpoints

### GET /users

Returns list of users.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | int | No | User ID |

### POST /users

Creates a new user.

## Examples

### cURL

```bash
curl -X GET https://api.example.com/users
```

### Python

```python
import requests

response = requests.get("https://api.example.com/users")
print(response.json())
```

> **Note:** This is an important note.

## Changelog

- Version 1.0: Initial release
- Version 1.1: Added POST endpoint
"""


@pytest.fixture
def minimal_markdown() -> str:
    """Provide minimal markdown content."""
    return "# Title\n\nContent."


@pytest.fixture
def markdown_with_code_blocks() -> str:
    """Markdown with multiple code blocks."""
    return """# Code Blocks

## Python
```python
def foo():
    return 42
```

## JavaScript
```javascript
function foo() {
    return 42;
}
```

## Inline Code

Use `print()` to output.
"""


@pytest.fixture
def markdown_with_tables() -> str:
    """Markdown with tables."""
    return """# Tables

| Name | Value |
|------|-------|
| A    | 1     |
| B    | 2     |

| Col1 | Col2 | Col3 |
|:-----|:----:|-----:|
| L    | C    | R    |
"""


@pytest.fixture
def markdown_with_lists() -> str:
    """Markdown with various list types."""
    return """# Lists

## Unordered
- Item 1
- Item 2
  - Nested 1
  - Nested 2
- Item 3

## Ordered
1. First
2. Second
3. Third

## Task List
- [x] Done
- [ ] Not done
"""


@pytest.fixture
def markdown_with_blockquotes() -> str:
    """Markdown with blockquotes."""
    return """# Blockquotes

> Simple quote

> Multi-line quote
> with continuation

> **Note:** Important information here.

> List inside quote:
> - Item 1
> - Item 2
"""


@pytest.fixture
def unicode_markdown() -> str:
    """Markdown with Unicode characters."""
    return """# 多语言支持

## 日本語

これはテストです。

## 中文

这是一个测试。

## 한국어

이것은 테스트입니다.

## Emoji

🚀 🚢 📦
"""


# =============================================================================
# File Fixtures
# =============================================================================


@pytest.fixture
def sample_document_file(tmp_path: Path, sample_markdown_content: str) -> Path:
    """Create a temporary markdown file with sample content."""
    file_path = tmp_path / "sample.md"
    file_path.write_text(sample_markdown_content)
    return file_path


@pytest.fixture
def complex_document_file(tmp_path: Path, complex_markdown_content: str) -> Path:
    """Create a temporary markdown file with complex content."""
    file_path = tmp_path / "complex.md"
    file_path.write_text(complex_markdown_content)
    return file_path


@pytest.fixture
def invalid_format_file(tmp_path: Path) -> Path:
    """Create a file with unsupported format."""
    file_path = tmp_path / "test.invalid"
    file_path.write_text("invalid content")
    return file_path


@pytest.fixture
def empty_markdown_file(tmp_path: Path) -> Path:
    """Create an empty markdown file."""
    file_path = tmp_path / "empty.md"
    file_path.write_text("")
    return file_path


@pytest.fixture
def markdown_file_uppercase(tmp_path: Path, sample_markdown_content: str) -> Path:
    """Create a markdown file with uppercase extension."""
    file_path = tmp_path / "test.MD"
    file_path.write_text(sample_markdown_content)
    return file_path


@pytest.fixture
def json_sample_file(tmp_path: Path) -> Path:
    """Create a sample JSON file."""
    data = {"key": "value", "nested": {"foo": "bar"}}
    file_path = tmp_path / "sample.json"
    file_path.write_text(json.dumps(data))
    return file_path


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def default_config() -> Dict[str, Any]:
    """Default configuration for testing."""
    return {
        "include_metadata": True,
        "include_semantic_tags": False,
        "output_format": "json",
    }


@pytest.fixture
def mcp_config() -> Dict[str, Any]:
    """Configuration for MCP output."""
    return {
        "include_metadata": True,
        "include_semantic_tags": True,
        "output_format": "mcp",
        "schema_version": "1.0",
    }


@pytest.fixture
def custom_config() -> Dict[str, Any]:
    """Custom configuration for testing."""
    return {
        "include_metadata": True,
        "include_semantic_tags": True,
        "output_format": "json",
        "custom_option": "custom_value",
    }


# =============================================================================
# Document Structure Fixtures
# =============================================================================


@pytest.fixture
def expected_json_structure() -> Dict[str, Any]:
    """Expected JSON structure for valid output."""
    return {
        "title": str,
        "content": str,
        "sections": list,
        "metadata": dict,
    }


@pytest.fixture
def expected_mcp_structure() -> Dict[str, Any]:
    """Expected MCP structure for valid output."""
    return {
        "format": "mcp",
        "version": str,
        "document": dict,
        "semantic_tags": list,
    }


# =============================================================================
# Temporary Path Fixtures
# =============================================================================


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def nested_input_dir(tmp_path: Path) -> Path:
    """Create a nested directory structure for input files."""
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    return nested


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_parser_result() -> Dict[str, Any]:
    """Mock parser result for unit testing transformers."""
    return {
        "title": "Test Document",
        "sections": [
            {
                "level": 1,
                "heading": "Introduction",
                "content": "This is the introduction.",
                "children": [],
            },
            {
                "level": 1,
                "heading": "Main Content",
                "content": "Main content here.",
                "children": [
                    {
                        "level": 2,
                        "heading": "Subsection",
                        "content": "Subsection content.",
                        "children": [],
                    },
                ],
            },
        ],
        "metadata": {
            "author": "Test Author",
            "date": "2024-01-01",
        },
    }


# =============================================================================
# Parametrized Test Data
# =============================================================================


@pytest.fixture(params=["markdown", "json", "yaml"])
def supported_format(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture for supported formats."""
    return request.param


@pytest.fixture(params=[".md", ".MD", ".Markdown"])
def markdown_extensions(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture for markdown extensions."""
    return request.param


@pytest.fixture(params=["json", "mcp"])
def output_format(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture for output formats."""
    return request.param
