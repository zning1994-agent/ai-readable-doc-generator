# Usage Guide

Complete guide to using ai-readable-doc-generator CLI and API.

## Table of Contents

- [Installation](#installation)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Usage](#api-usage)

## Installation

### From PyPI

```bash
pip install ai-readable-doc-generator
```

### From Source

```bash
git clone https://github.com/your-org/ai-readable-doc-generator.git
cd ai-readable-doc-generator
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## CLI Commands

### convert

Convert a Markdown file to structured format.

```bash
ai-docgen convert <input_file> [options]
```

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | stdout |
| `--format` | `-f` | Output format (json, mcp) | json |
| `--semantic-tags` | `-s` | Enable semantic tagging | false |
| `--schema` | | Custom JSON schema path | built-in |
| `--pretty` | `-p` | Pretty-print JSON output | true |
| `--verbose` | `-v` | Verbose output | false |

**Examples:**

```bash
# Basic conversion
ai-docgen convert README.md -o output.json

# With semantic tagging
ai-docgen convert README.md -o output.json --semantic-tags

# MCP-compatible output
ai-docgen convert README.md -o output.json --format mcp

# With custom schema
ai-docgen convert README.md -o output.json --schema custom_schema.json
```

### batch

Convert multiple files at once.

```bash
ai-docgen batch <input_directory> [options]
```

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Output directory | ./output |
| `--pattern` | | File pattern (glob) | *.md |
| `--recursive` | `-r` | Recursive directory scan | false |
| `--semantic-tags` | `-s` | Enable semantic tagging | false |

**Examples:**

```bash
# Convert all markdown files in a directory
ai-docgen batch ./docs -o ./output

# Recursive conversion
ai-docgen batch ./docs -o ./output --recursive

# Custom file pattern
ai-docgen batch ./docs -o ./output --pattern "**/*.md"
```

### validate

Validate a Markdown file without converting.

```bash
ai-docgen validate <input_file> [options]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--schema` | | JSON schema to validate against |
| `--strict` | | Enable strict validation mode |

### mcp-server

Start the MCP-compatible server for AI agent integration.

```bash
ai-docgen mcp-server [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server host | localhost |
| `--port` | Server port | 8080 |
| `--ssl` | Enable SSL/TLS | false |
| `--cert` | SSL certificate path | - |
| `--key` | SSL key path | - |

**Examples:**

```bash
# Start server with default settings
ai-docgen mcp-server

# Custom host and port
ai-docgen mcp-server --host 0.0.0.0 --port 9000

# With SSL
ai-docgen mcp-server --ssl --cert server.crt --key server.key
```

## Configuration

### Configuration File

Create `ai-docgen.yaml` or `ai-docgen.json` in your project root:

```yaml
# ai-docgen.yaml
output:
  format: json
  pretty: true
  indent: 2

semantic:
  enabled: true
  confidence_threshold: 0.7
  tag_levels:
    - section
    - paragraph
    - code
    - list

parser:
  extensions:
    - tables
    - footnotes
    - tasklists
  strip_html: true

mcp:
  host: localhost
  port: 8080
  timeout: 30
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_DOCGEN_CONFIG` | Config file path | ./ai-docgen.yaml |
| `AI_DOCGEN_OUTPUT_DIR` | Default output directory | ./output |
| `AI_DOCGEN_LOG_LEVEL` | Logging level | INFO |

## Examples

### Example 1: Simple Conversion

Input (`example.md`):

```markdown
# Getting Started

This guide will help you get started with our API.

## Prerequisites

- Python 3.10+
- API key from dashboard

## Installation

```bash
pip install our-api
```
```

Command:

```bash
ai-docgen convert example.md -o example.json
```

Output (`example.json`):

```json
{
  "title": "Getting Started",
  "sections": [
    {
      "type": "heading",
      "level": 1,
      "content": "Getting Started"
    },
    {
      "type": "paragraph",
      "content": "This guide will help you get started with our API."
    },
    {
      "type": "heading",
      "level": 2,
      "content": "Prerequisites"
    },
    {
      "type": "list",
      "ordered": false,
      "items": [
        "Python 3.10+",
        "API key from dashboard"
      ]
    },
    {
      "type": "heading",
      "level": 2,
      "content": "Installation"
    },
    {
      "type": "code",
      "language": "bash",
      "content": "pip install our-api"
    }
  ],
  "metadata": {
    "word_count": 24,
    "section_count": 6,
    "parsing_version": "1.0.0"
  }
}
```

### Example 2: With Semantic Tags

Command:

```bash
ai-docgen convert example.md -o example_semantic.json --semantic-tags
```

Output includes additional semantic information:

```json
{
  "title": "Getting Started",
  "sections": [
    {
      "type": "heading",
      "level": 1,
      "content": "Getting Started",
      "semantic_tags": {
        "content_type": "title",
        "importance": "high",
        "category": "documentation"
      }
    },
    {
      "type": "paragraph",
      "content": "This guide will help you get started with our API.",
      "semantic_tags": {
        "content_type": "introduction",
        "purpose": "overview",
        "audience": "beginner"
      }
    }
  ]
}
```

### Example 3: Batch Processing

Convert all documentation files:

```bash
ai-docgen batch ./docs \
  --output-dir ./output \
  --recursive \
  --semantic-tags
```

### Example 4: MCP Server Integration

Start the server:

```bash
ai-docgen mcp-server --port 8080
```

The server provides these endpoints:

```
POST /convert     - Convert document
POST /validate    - Validate document
GET  /health      - Health check
GET  /schema      - Get schema definition
```

## API Usage

### Python API

```python
from ai_readable_doc_generator import Document, Converter

# Parse markdown
document = Document.from_markdown("""
# Hello World

This is a test document.
""")

# Convert to structured JSON
converter = Converter(format="json", semantic_tags=True)
output = converter.convert(document)

print(output)
```

### Programmatic MCP Server

```python
from ai_readable_doc_generator.mcp_server import MCPServer

server = MCPServer(host="localhost", port=8080)

@server.handler("convert")
def handle_convert(request):
    return converter.convert(request["content"])

server.start()
```

## Troubleshooting

### Common Issues

**Issue: Output is empty**

- Check if input file exists and contains valid markdown
- Verify file encoding (UTF-8 recommended)
- Enable verbose mode: `-v`

**Issue: Semantic tags not appearing**

- Ensure `--semantic-tags` flag is set
- Check confidence threshold in config

**Issue: MCP server connection refused**

- Verify server is running: `ps aux | grep ai-docgen`
- Check port availability: `lsof -i :8080`
- Firewall settings may block connections

## Next Steps

- [MCP Integration Guide](mcp_integration.md) - Learn how to integrate with AI agents
- See the main [README](../README.md) for project overview
