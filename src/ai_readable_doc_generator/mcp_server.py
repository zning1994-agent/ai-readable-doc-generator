"""
MCP Server Implementation for ai-readable-doc-generator

This module provides a Model Context Protocol (MCP) server that enables
AI Agents to consume documents through a standardized interface.

The server exposes a "read" tool that processes documents and returns
AI-readable structured output.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from .converter import DocumentConverter
    from .models.document import Document
    from .models.schema import OutputFormat
except ImportError:
    # Handle module import when running directly
    from converter import DocumentConverter
    from models.document import Document
    from models.schema import OutputFormat


class MCPErrorCode(Enum):
    """MCP error codes following JSON-RPC 2.0 spec."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class MCPJsonRPCRequest:
    """JSON-RPC 2.0 request object."""
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    method: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MCPJsonRPCRequest":
        """Create request from dictionary."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method", ""),
            params=data.get("params", {})
        )


@dataclass
class MCPJsonRPCResponse:
    """JSON-RPC 2.0 response object."""
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response


@dataclass
class MCPToolDefinition:
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP tool definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPToolResult:
    """Result from a tool execution."""
    content: list[dict[str, Any]]
    is_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP tool result format."""
        return {
            "content": self.content,
            "isError": self.is_error
        }


class MCPProtocolHandler:
    """Handles MCP protocol message processing."""

    TOOLS: list[MCPToolDefinition] = [
        MCPToolDefinition(
            name="read_document",
            description="Read and convert a document to AI-readable format with semantic tagging. "
                       "Supports Markdown input and outputs structured JSON with metadata, "
                       "section types, and relationships.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the document file to read"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "yaml", "mcp"],
                        "default": "json",
                        "description": "Output format: 'json', 'yaml', or 'mcp' (MCP-specific structured format)"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include document metadata in output"
                    },
                    "semantic_level": {
                        "type": "string",
                        "enum": ["basic", "detailed", "full"],
                        "default": "detailed",
                        "description": "Level of semantic tagging: 'basic' (section types), "
                                    "'detailed' (adds content classifications), "
                                    "'full' (includes all metadata and relationships)"
                    }
                },
                "required": ["path"]
            }
        ),
        MCPToolDefinition(
            name="read_document_content",
            description="Read document content directly from a string instead of a file path. "
                       "Useful for inline document processing.",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Raw document content (Markdown)"
                    },
                    "source_name": {
                        "type": "string",
                        "default": "inline",
                        "description": "Source identifier for the document"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "yaml", "mcp"],
                        "default": "json",
                        "description": "Output format"
                    },
                    "semantic_level": {
                        "type": "string",
                        "enum": ["basic", "detailed", "full"],
                        "default": "detailed",
                        "description": "Level of semantic tagging"
                    }
                },
                "required": ["content"]
            }
        ),
        MCPToolDefinition(
            name="list_tools",
            description="List all available tools in this MCP server",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
    ]

    def __init__(self):
        self.converter = DocumentConverter()

    async def handle_request(self, request: MCPJsonRPCRequest) -> MCPJsonRPCResponse:
        """Handle an incoming MCP request."""
        try:
            if request.method == "initialize":
                result = self._handle_initialize(request.params)
            elif request.method == "tools/list":
                result = self._handle_tools_list()
            elif request.method == "tools/call":
                result = await self._handle_tools_call(request.params)
            elif request.method == "resources/list":
                result = self._handle_resources_list()
            elif request.method == "ping":
                result = {"status": "pong"}
            else:
                return MCPJsonRPCResponse(
                    id=request.id,
                    error={
                        "code": MCPErrorCode.METHOD_NOT_FOUND.value,
                        "message": f"Method not found: {request.method}"
                    }
                )
            return MCPJsonRPCResponse(id=request.id, result=result)
        except Exception as e:
            return MCPJsonRPCResponse(
                id=request.id,
                error={
                    "code": MCPErrorCode.INTERNAL_ERROR.value,
                    "message": str(e)
                }
            )

    def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False}
            },
            "serverInfo": {
                "name": "ai-readable-doc-generator",
                "version": "0.1.0"
            }
        }

    def _handle_tools_list(self) -> dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [tool.to_dict() for tool in self.TOOLS]
        }

    async def _handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "read_document":
            return await self._tool_read_document(tool_args)
        elif tool_name == "read_document_content":
            return await self._tool_read_document_content(tool_args)
        elif tool_name == "list_tools":
            return await self._tool_list_tools()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _tool_read_document(self, args: dict[str, Any]) -> dict[str, Any]:
        """Tool implementation for reading documents from file path."""
        path = args.get("path")
        output_format = args.get("format", "json")
        include_metadata = args.get("include_metadata", True)
        semantic_level = args.get("semantic_level", "detailed")

        if not path:
            return MCPToolResult(
                content=[{"type": "text", "text": "Error: path is required"}],
                is_error=True
            ).to_dict()

        file_path = Path(path)
        if not file_path.exists():
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error: File not found: {path}"}],
                is_error=True
            ).to_dict()

        try:
            # Read the file content
            content = file_path.read_text(encoding="utf-8")

            # Convert to output format
            format_enum = OutputFormat(output_format) if output_format != "mcp" else OutputFormat.JSON

            # Determine semantic options based on level
            semantic_options = self._get_semantic_options(semantic_level)

            result = self.converter.convert(
                content=content,
                source_name=file_path.name,
                output_format=format_enum,
                include_metadata=include_metadata,
                **semantic_options
            )

            # Format output based on requested format
            if output_format == "yaml":
                output = self._to_yaml(result)
            elif output_format == "mcp":
                output = self._to_mcp_format(result)
            else:
                output = json.dumps(result, indent=2, ensure_ascii=False)

            return MCPToolResult(
                content=[{"type": "text", "text": output}]
            ).to_dict()

        except Exception as e:
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error processing document: {str(e)}"}],
                is_error=True
            ).to_dict()

    async def _tool_read_document_content(self, args: dict[str, Any]) -> dict[str, Any]:
        """Tool implementation for reading documents from content string."""
        content = args.get("content")
        source_name = args.get("source_name", "inline")
        output_format = args.get("format", "json")
        semantic_level = args.get("semantic_level", "detailed")

        if not content:
            return MCPToolResult(
                content=[{"type": "text", "text": "Error: content is required"}],
                is_error=True
            ).to_dict()

        try:
            format_enum = OutputFormat(output_format) if output_format != "mcp" else OutputFormat.JSON
            semantic_options = self._get_semantic_options(semantic_level)

            result = self.converter.convert(
                content=content,
                source_name=source_name,
                output_format=format_enum,
                include_metadata=True,
                **semantic_options
            )

            if output_format == "yaml":
                output = self._to_yaml(result)
            elif output_format == "mcp":
                output = self._to_mcp_format(result)
            else:
                output = json.dumps(result, indent=2, ensure_ascii=False)

            return MCPToolResult(
                content=[{"type": "text", "text": output}]
            ).to_dict()

        except Exception as e:
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error processing content: {str(e)}"}],
                is_error=True
            ).to_dict()

    async def _tool_list_tools(self) -> dict[str, Any]:
        """Tool implementation for listing available tools."""
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": json.dumps({
                    "tools": [tool.to_dict() for tool in self.TOOLS]
                }, indent=2)
            }]
        ).to_dict()

    def _handle_resources_list(self) -> dict[str, Any]:
        """Handle resources/list request."""
        return {"resources": []}

    def _get_semantic_options(self, level: str) -> dict[str, Any]:
        """Get semantic options based on requested level."""
        options = {
            "basic": {
                "tag_sections": True,
                "tag_content_types": False,
                "extract_relationships": False,
                "add_importance": False
            },
            "detailed": {
                "tag_sections": True,
                "tag_content_types": True,
                "extract_relationships": True,
                "add_importance": False
            },
            "full": {
                "tag_sections": True,
                "tag_content_types": True,
                "extract_relationships": True,
                "add_importance": True
            }
        }
        return options.get(level, options["detailed"])

    def _to_yaml(self, data: dict[str, Any]) -> str:
        """Convert data to YAML format (simplified implementation)."""
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # Fallback to JSON if PyYAML is not available
            return json.dumps(data, indent=2, ensure_ascii=False)

    def _to_mcp_format(self, data: dict[str, Any]) -> str:
        """Convert data to MCP-specific structured format."""
        mcp_output = {
            "document": {
                "metadata": data.get("metadata", {}),
                "content": data.get("content", []),
                "structure": data.get("structure", {}),
                "semantic_tags": data.get("semantic_tags", {})
            },
            "relationships": data.get("relationships", []),
            "summary": self._generate_summary(data)
        }
        return json.dumps(mcp_output, indent=2, ensure_ascii=False)

    def _generate_summary(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate document summary for quick AI comprehension."""
        sections = data.get("content", [])
        total_sections = len(sections)
        section_types = {}

        for section in sections:
            section_type = section.get("type", "unknown")
            section_types[section_type] = section_types.get(section_type, 0) + 1

        return {
            "total_sections": total_sections,
            "section_types": section_types,
            "has_metadata": "metadata" in data,
            "has_relationships": len(data.get("relationships", [])) > 0
        }


class MCPServer:
    """
    MCP Server implementation using stdio transport.

    This server communicates with AI agents via stdin/stdout using
    JSON-RPC 2.0 protocol.
    """

    def __init__(self):
        self.protocol_handler = MCPProtocolHandler()
        self._running = False

    async def run(self):
        """Run the MCP server, processing requests from stdin."""
        self._running = True

        while self._running:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Parse request
                try:
                    request_data = json.loads(line)
                    request = MCPJsonRPCRequest.from_dict(request_data)
                except json.JSONDecodeError as e:
                    error_response = MCPJsonRPCResponse(
                        error={
                            "code": MCPErrorCode.PARSE_ERROR.value,
                            "message": f"Invalid JSON: {str(e)}"
                        }
                    )
                    self._write_response(error_response)
                    continue

                # Handle request
                response = await self.protocol_handler.handle_request(request)
                self._write_response(response)

            except Exception as e:
                error_response = MCPJsonRPCResponse(
                    error={
                        "code": MCPErrorCode.INTERNAL_ERROR.value,
                        "message": f"Server error: {str(e)}"
                    }
                )
                self._write_response(error_response)

    def _write_response(self, response: MCPJsonRPCResponse):
        """Write response to stdout."""
        output = json.dumps(response.to_dict(), ensure_ascii=False)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    def stop(self):
        """Stop the server."""
        self._running = False


async def main():
    """Main entry point for MCP server."""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
