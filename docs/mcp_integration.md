# MCP Integration Guide

Integrate ai-readable-doc-generator with AI agents using the Model Context Protocol (MCP).

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Architecture](#architecture)
- [Setup](#setup)
- [Server Configuration](#server-configuration)
- [Client Integration](#client-integration)
- [Tools Reference](#tools-reference)
- [Examples](#examples)
- [Security](#security)

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol that enables AI agents to interact with external tools and data sources. It provides a consistent interface for:

- **Tool invocation** - AI agents can call tools exposed via MCP
- **Resource access** - Structured data retrieval from connected systems
- **Context management** - Maintaining conversation state across interactions

ai-readable-doc-generator exposes document processing as MCP tools, allowing AI agents to:

1. Convert documentation on-demand
2. Extract structured information from documents
3. Validate document quality and structure
4. Apply semantic tagging to content

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Agent                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Claude Desktop / LangChain / Custom Agent Framework     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐      │
│  │  /convert   │  │  /validate  │  │  /get_schema       │      │
│  └─────────────┘  └─────────────┘  └─────────────────────┘      │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │           ai-readable-doc-generator Core                 │     │
│  │  ┌─────────┐  ┌────────────┐  ┌───────────────────┐    │     │
│  │  │ Parser  │  │ Semantic   │  │ Transformer       │    │     │
│  │  │         │  │ Tagger     │  │ (JSON/MCP)        │    │     │
│  │  └─────────┘  └────────────┘  └───────────────────┘    │     │
│  └─────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Setup

### Prerequisites

- Python 3.11+
- ai-readable-doc-generator installed

### Quick Start

1. **Start the MCP server:**

```bash
ai-docgen mcp-server --port 8080
```

2. **Configure your AI client** (see Client Integration below)

3. **Test the connection:**

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "capabilities": ["convert", "validate", "get_schema"]
}
```

## Server Configuration

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server bind address | localhost |
| `--port` | Server port | 8080 |
| `--ssl` | Enable TLS/SSL | false |
| `--cert` | TLS certificate path | - |
| `--key` | TLS private key path | - |
| `--timeout` | Request timeout (seconds) | 30 |
| `--max-file-size` | Maximum file size (MB) | 10 |
| `--log-level` | Logging level | INFO |

### Configuration File

Create `mcp-config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8080
  timeout: 30
  
ssl:
  enabled: false
  cert: /path/to/cert.pem
  key: /path/to/key.pem

limits:
  max_file_size_mb: 10
  max_batch_size: 100
  rate_limit_per_minute: 60

semantic:
  enabled: true
  confidence_threshold: 0.7

logging:
  level: INFO
  format: json
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MCP_HOST` | Server host |
| `MCP_PORT` | Server port |
| `MCP_SSL_ENABLED` | Enable SSL |
| `MCP_TIMEOUT` | Request timeout |

## Client Integration

### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ai-docgen": {
      "command": "ai-docgen",
      "args": ["mcp-server", "--port", "8080"],
      "env": {
        "MCP_TIMEOUT": "30"
      }
    }
  }
}
```

### LangChain Integration

```python
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

# Connect to MCP server
client = MultiServerMCPClient(
    {
        "docgen": {
            "command": "ai-docgen",
            "args": ["mcp-server", "--port", "8080"]
        }
    }
)

# Get tools
tools = client.get_tools()

# Use in agent
@tool
def process_document(document_content: str) -> str:
    """Process a markdown document using ai-docgen."""
    # Call MCP tool
    result = next(t for t in tools if t.name == "convert")
    return result.invoke({"content": document_content})
```

### Custom HTTP Client

```python
import requests

class DocGeneratorClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    def convert(self, content: str, semantic_tags: bool = False) -> dict:
        """Convert markdown to structured JSON."""
        response = requests.post(
            f"{self.base_url}/convert",
            json={
                "content": content,
                "options": {
                    "semantic_tags": semantic_tags
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def validate(self, content: str, schema: str = None) -> dict:
        """Validate markdown content."""
        response = requests.post(
            f"{self.base_url}/validate",
            json={
                "content": content,
                "schema": schema
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_schema(self) -> dict:
        """Get the document schema definition."""
        response = requests.get(f"{self.base_url}/schema")
        response.raise_for_status()
        return response.json()
```

## Tools Reference

### /convert

Convert markdown content to structured format.

**Request:**

```json
{
  "content": "# Markdown content here...",
  "options": {
    "format": "json",
    "semantic_tags": true,
    "pretty": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "title": "Document Title",
    "sections": [...],
    "metadata": {...}
  }
}
```

### /validate

Validate markdown content against schema.

**Request:**

```json
{
  "content": "# Markdown content...",
  "schema": null,
  "strict": false
}
```

**Response:**

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

### /get_schema

Get the JSON schema for document structure.

**Response:**

```json
{
  "schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "title": {"type": "string"},
      "sections": {
        "type": "array",
        "items": {"$ref": "#/definitions/section"}
      }
    }
  }
}
```

## Examples

### Example 1: AI Agent Document Query

A Claude agent can query documentation:

```
User: Can you convert the API documentation at ./docs/api.md to JSON?

Claude: I'll convert that documentation for you.

[Calls /convert tool with content from ./docs/api.md]

Result:
{
  "title": "API Reference",
  "sections": [
    {"type": "heading", "level": 1, "content": "API Reference"},
    {"type": "code", "language": "python", "content": "import api\napi.connect()"},
    ...
  ]
}
```

### Example 2: Semantic Document Analysis

```
User: Extract all code examples from the documentation and tag them by purpose.

Claude: I'll analyze the documents and categorize the code examples.

[Calls /convert with semantic_tags enabled, then processes results]

Result: Code examples categorized as:
- setup (3 examples)
- usage (7 examples)
- configuration (2 examples)
- testing (1 example)
```

### Example 3: Batch Documentation Processing

```python
from docgen_client import DocGeneratorClient

client = DocGeneratorClient("http://localhost:8080")
schema = client.get_schema()

docs = [
    "docs/getting-started.md",
    "docs/api-reference.md",
    "docs/troubleshooting.md"
]

for doc_path in docs:
    with open(doc_path) as f:
        content = f.read()
    
    result = client.convert(content, semantic_tags=True)
    save_structured_doc(doc_path, result)
```

## Security

### Authentication

Enable API key authentication:

```bash
ai-docgen mcp-server \
  --port 8080 \
  --api-key "your-secret-key"
```

### Rate Limiting

Configure rate limiting in `mcp-config.yaml`:

```yaml
limits:
  rate_limit_per_minute: 60
  burst_size: 10
```

### Input Validation

The server validates all inputs:

- Content size limits
- Content type verification
- Schema validation
- Sanitization of special characters

### Best Practices

1. **Use HTTPS in production** - Enable SSL/TLS
2. **Restrict network access** - Bind to internal interfaces
3. **Monitor usage** - Enable detailed logging
4. **Validate inputs** - Use schema validation
5. **Rate limit clients** - Prevent abuse

## Troubleshooting

### Connection Issues

**Error: Connection refused**

```bash
# Check if server is running
ps aux | grep ai-docgen

# Check port availability
lsof -i :8080

# Check firewall
sudo ufw status
```

**Error: SSL certificate error**

- Verify certificate path is correct
- Check certificate expiration
- Ensure private key matches certificate

### Integration Issues

**Claude Desktop not recognizing tools**

1. Restart Claude Desktop
2. Check configuration syntax
3. Review Claude Desktop logs

**Tools not appearing in LangChain**

1. Verify MCP server is running
2. Check MultiServerMCPClient configuration
3. Enable debug logging

## Next Steps

- [Usage Guide](usage.md) - CLI commands and configuration
- See the main [README](../README.md) for project overview
