#!/usr/bin/env python3
"""
AI-Readable Doc Generator - Main Entry Point

This module provides the primary CLI interface for the ai-readable-doc-generator tool.
It orchestrates document parsing, transformation, and output generation.

Usage:
    python main.py convert <input_file> [options]
    python main.py validate <schema_file>
    python main.py --help

For module-level CLI access:
    python -m ai_readable_doc_generator --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

# Version info
__version__ = "0.1.0"
__author__ = "AI Documentation Team"
__description__ = "Transform documentation into AI-agent-friendly formats"


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="ai-readable-doc-generator",
        description="Transform existing documentation into AI-Agent-friendly formats "
        "with structured output, semantic tagging, and MCP compatibility.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s convert input.md -o output.json
  %(prog)s convert input.md --format mcp --pretty
  %(prog)s validate schema.json
  %(prog)s --version

For more information, visit: https://github.com/ai-readable-doc-generator
        """,
    )

    # Version argument
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        description="Available commands for document processing",
        required=True,
    )

    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert a document to AI-readable format",
        description="Parse an input document and convert it to structured AI-ready output",
    )
    _setup_convert_parser(convert_parser)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate document structure against schema",
        description="Validate that a document follows the expected schema format",
    )
    _setup_validate_parser(validate_parser)

    return parser


def _setup_convert_parser(parser: argparse.ArgumentParser) -> None:
    """Configure arguments for the convert subcommand."""
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input document (Markdown supported in MVP)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output file (default: stdout)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml", "mcp"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the output (add indentation and newlines)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to a custom output schema file (JSON or YAML)",
    )
    parser.add_argument(
        "--no-semantic-tags",
        action="store_true",
        help="Disable semantic tagging in the output",
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        default=True,
        help="Include document metadata in output (default: enabled)",
    )


def _setup_validate_parser(parser: argparse.ArgumentParser) -> None:
    """Configure arguments for the validate subcommand."""
    parser.add_argument(
        "schema_file",
        type=Path,
        help="Path to the schema file to validate",
    )
    parser.add_argument(
        "--document",
        type=Path,
        help="Optional document file to validate against the schema",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation (fail on warnings)",
    )


def handle_convert(args: argparse.Namespace) -> int:
    """
    Handle the convert command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        # Import here to avoid circular imports and lazy loading
        from ai_readable_doc_generator.converter import DocumentConverter
        from ai_readable_doc_generator.document import Document
        from ai_readable_doc_generator.parser import MarkdownParser
        from ai_readable_doc_generator.transformer import JSONTransformer, MCPTransformer

        # Check input file exists
        if not args.input_file.exists():
            print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
            return 1

        if not args.input_file.is_file():
            print(f"Error: Input path is not a file: {args.input_file}", file=sys.stderr)
            return 1

        # Parse the input document
        parser = MarkdownParser()
        document: Document = parser.parse(args.input_file)

        # Create appropriate transformer
        if args.format == "mcp":
            transformer: type = MCPTransformer
        else:
            transformer = JSONTransformer

        # Configure transformer options
        transformer_options = {
            "pretty": args.pretty,
            "include_semantic_tags": not args.no_semantic_tags,
            "include_metadata": args.include_metadata,
        }

        if args.schema:
            transformer_options["custom_schema"] = args.schema

        # Convert the document
        converter = DocumentConverter(transformer=transformer, **transformer_options)
        result = converter.convert(document)

        # Output the result
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding="utf-8")
            print(f"Successfully converted to: {args.output}")
        else:
            print(result)

        return 0

    except ImportError as e:
        print(f"Error: Required module not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        if args.pretty:  # Show full traceback in debug mode
            import traceback
            traceback.print_exc()
        return 1


def handle_validate(args: argparse.Namespace) -> int:
    """
    Handle the validate command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        from ai_readable_doc_generator.models.schema import SchemaValidator

        if not args.schema_file.exists():
            print(f"Error: Schema file not found: {args.schema_file}", file=sys.stderr)
            return 1

        # Initialize validator
        validator = SchemaValidator(
            schema_path=args.schema_file,
            strict=args.strict,
        )

        # Validate schema file itself
        schema_valid, schema_errors = validator.validate_schema()
        if not schema_valid:
            print("Schema validation failed:")
            for error in schema_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1

        print("Schema validation: PASSED")

        # If document provided, validate it against the schema
        if args.document:
            if not args.document.exists():
                print(f"Error: Document file not found: {args.document}", file=sys.stderr)
                return 1

            doc_valid, doc_errors = validator.validate_document(args.document)
            if not doc_valid:
                print("Document validation failed:")
                for error in doc_errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1

            print("Document validation: PASSED")

        return 0

    except ImportError as e:
        print(f"Error: Required module not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        if args.strict:
            import traceback
            traceback.print_exc()
        return 1


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for the CLI application.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Route to appropriate handler
    if args.command == "convert":
        return handle_convert(args)
    elif args.command == "validate":
        return handle_validate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
