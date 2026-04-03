# ai-readable-doc-generator

Transform your documentation into AI-agent-friendly formats with structured output, semantic tagging, and MCP compatibility.

## Overview

**ai-readable-doc-generator** is an automation tool that converts existing documentation into formats optimized for AI Agents and LLM-based systems. It addresses the structural ambiguity and context loss that plague traditional document formats when consumed by AI systems.

## Problem It Solves

AI Agents and LLM systems struggle with:

- **Structural ambiguity** - Natural language documents lack explicit hierarchical relationships
- **Context loss** - Important metadata is lost during format conversion
- **Integration complexity** - Different AI frameworks require different input formats
- **MCP incompatibility** - No native support for the Model Context Protocol

## Solution

ai-readable-doc-generator provides:

- **Structured output generation** - JSON/YAML with explicit schema definitions
- **Semantic tagging** - Machine-readable markers throughout documents
- **MCP compatibility** - Native support for Model Context Protocol
- **Multi-format support** - Extensible architecture for various input formats

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| Markdown Parsing | Full support for CommonMark and GitHub-flavored Markdown |
| Structured JSON Output | Configurable JSON schema with explicit relationships |
| Semantic Tagging | Automatic content classification and importance indicators |
| MCP Server | Run as a Model Context Protocol server for AI integration |
| CLI Interface | Command-line tool for batch and single-file processing |

### Output Formats

- **JSON** - Structured data with schema definitions
- **MCP-compatible** - Direct integration with MCP-capable AI agents
- **YAML** (planned) - Human-readable structured output

## Quick Start

### Installation

```bash
pip install ai-readable-doc-generator
```

### Basic Usage

Convert a Markdown file to structured JSON:

```bash
ai-docgen convert input.md -o output.json
```

Convert with semantic tagging enabled:

```bash
ai-docgen convert input.md -o output.json --semantic-tags
```

### MCP Server Mode

Start the MCP server for AI agent integration:

```bash
ai-docgen mcp-server --port 8080
```

## Documentation

- [Usage Guide](usage.md) - Detailed CLI commands, configuration options, and examples
- [MCP Integration](mcp_integration.md) - Model Context Protocol setup and integration

## Target Users

| User Segment | Primary Use Case |
|--------------|------------------|
| AI Agent Developers | Preparing documentation for AI agent knowledge bases |
| LLM Application Builders | Converting documentation for RAG pipelines |
| Technical Documentation Teams | Making existing docs AI-consumable |
| Enterprise AI Teams | Standardizing document formats |

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Markdown      │────▶│   Parser         │────▶│   Transformer   │
│   Input         │     │   (BaseParser)   │     │   (JSON/MCP)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                         │
                              ▼                         ▼
                      ┌──────────────────┐     ┌─────────────────┐
                      │   Semantic       │     │   Structured    │
                      │   Tagger Plugin  │     │   Output        │
                      └──────────────────┘     └─────────────────┘
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see our contributing guidelines for more information.
