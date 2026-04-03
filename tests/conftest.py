"""
Pytest configuration and shared fixtures for MCP server tests.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest


# =============================================================================
# Session-scoped fixtures
# =============================================================================


@pytest.fixture(scope="session")
def sample_markdown_content() -> str:
    """Session-scoped sample markdown content for testing."""
    return """# Introduction

This is the introduction section.

## Getting Started

Follow these steps to get started.

### Prerequisites

- Python 3.11+
- pip
- git

### Installation

```bash
pip install ai-readable-doc-generator
git clone https://github.com/example/repo.git
```

## Configuration

Configure your environment variables in `.env`.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | false |
| LOG_LEVEL | Logging level | info |

> **Note**: Make sure to restart the server after configuration changes.

## API Reference

### Endpoints

#### GET /api/documents

Retrieve all documents.

#### POST /api/documents

Create a new document.

```json
{
  "title": "My Document",
  "content": "Document content here"
}
```

## Troubleshooting

### Common Issues

1. **Installation fails**: Check Python version
2. **Import errors**: Verify dependencies installed
3. **Path errors**: Use absolute paths

<!-- This is a comment that should be ignored -->
"""


@pytest.fixture(scope="session")
def sample_json_output() -> dict[str, Any]:
    """Session-scoped sample JSON output for testing."""
    return {
        "title": "Sample Document",
        "format_version": "1.0",
        "metadata": {
            "source_path": "docs/sample.md",
            "created_at": "2026-04-03T00:00:00Z",
            "author": "Test Author",
            "version": "1.0.0",
        },
        "sections": [
            {
                "title": "Introduction",
                "level": 1,
                "content_type": "narrative",
                "importance": "high",
                "semantic_tags": ["introduction", "overview"],
            },
            {
                "title": "Getting Started",
                "level": 2,
                "content_type": "procedural",
                "importance": "medium",
                "semantic_tags": ["guide", "tutorial"],
            },
        ],
        "statistics": {
            "total_sections": 5,
            "total_lines": 100,
            "code_blocks": 2,
            "tables": 1,
            "links": 3,
        },
    }


# =============================================================================
# Function-scoped fixtures
# =============================================================================


@pytest.fixture
def temp_markdown_file(sample_markdown_content: str, tmp_path: Path) -> Path:
    """Create a temporary markdown file for testing."""
    file_path = tmp_path / "test.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    return file_path


@pytest.fixture
def temp_json_file(sample_json_output: dict[str, Any], tmp_path: Path) -> Path:
    """Create a temporary JSON file for testing."""
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample_json_output, f, indent=2)
    return file_path


@pytest.fixture
def temp_directory_with_files(tmp_path: Path) -> Path:
    """Create a temporary directory with multiple files for testing."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create various markdown files
    (docs_dir / "index.md").write_text("# Index\n\nWelcome to the docs.", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n\nFollow this guide.", encoding="utf-8")
    (docs_dir / "api.md").write_text("# API\n\nAPI reference.", encoding="utf-8")

    # Create subdirectory with files
    api_dir = docs_dir / "api"
    api_dir.mkdir()
    (api_dir / "endpoints.md").write_text("# Endpoints\n\nAPI endpoints.", encoding="utf-8")

    return docs_dir


@pytest.fixture
def mock_mcp_request() -> dict[str, Any]:
    """Create a mock MCP request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "read_document",
            "arguments": {
                "path": "docs/test.md",
                "format": "structured",
            },
        },
    }


@pytest.fixture
def mock_mcp_response() -> dict[str, Any]:
    """Create a mock MCP response for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "title": "Test Document",
                            "sections": [],
                        }
                    ),
                }
            ]
        },
    }


@pytest.fixture
def temp_file_factory(tmp_path: Path) -> Generator[callable, None, None]:
    """Factory fixture for creating temporary files."""
    created_files: list[Path] = []

    def _create_file(name: str, content: str) -> Path:
        file_path = tmp_path / name
        file_path.write_text(content, encoding="utf-8")
        created_files.append(file_path)
        return file_path

    yield _create_file

    # Cleanup is handled by tmp_path fixture


@pytest.fixture
def invalid_file_paths() -> list[str]:
    """List of invalid file paths for negative testing."""
    return [
        "",
        "/nonexistent/path/file.md",
        "relative/../path/file.md",
        "file with spaces.md",
        "file\twith\ttabs.md",
        "file\x00with\x00nulls.md",
    ]


@pytest.fixture
def valid_output_formats() -> list[str]:
    """List of valid output formats."""
    return ["structured", "json", "yaml"]


# =============================================================================
# Parametrized fixtures
# =============================================================================


@pytest.fixture(
    params=[
        "simple.md",
        "nested/deep/path.md",
        "file with spaces.md",
        "unicode_文件.md",
    ]
)
def various_path_formats(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture for various path formats."""
    return str(request.param)


# =============================================================================
# Async fixtures
# =============================================================================


@pytest.fixture
def async_temp_file(sample_markdown_content: str, tmp_path: Path) -> Path:
    """Create a temporary file for async tests."""
    file_path = tmp_path / "async_test.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    return file_path


# =============================================================================
# Markers
# =============================================================================


def pytest_configure(config: Any) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "mcp: mark test as MCP protocol test")
    config.addinivalue_line("markers", "async: mark test as async test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add MCP marker to all tests in test_mcp_server.py
        if "test_mcp_server" in str(item.fspath):
            item.add_marker("mcp")

        # Add async marker to async tests
        if "async" in item.name.lower():
            item.add_marker("async")
