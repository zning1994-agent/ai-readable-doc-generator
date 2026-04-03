"""
CLI commands for ai-readable-doc-generator.

This module implements the command-line interface using the click framework.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from ..converter import Converter
from ..document import Document
from ..parser.plugins.semantic_tagger import SemanticTagger
from ..transformer.json_transformer import JSONTransformer
from ..transformer.mcp_transformer import MCPTransformer


def validate_input_file(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Optional[str]:
    """Validate that the input file exists."""
    if value is None:
        return None
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"Input file does not exist: {value}")
    if not path.is_file():
        raise click.BadParameter(f"Input must be a file: {value}")
    return value


def validate_output_file(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Optional[str]:
    """Validate the output file path."""
    if value is None:
        return None
    path = Path(value)
    if path.exists() and not path.is_file():
        raise click.BadParameter(f"Output must be a file path: {value}")
    return value


@click.group()
@click.version_option(version="0.1.0", prog_name="ai-readable-doc-generator")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    ai-readable-doc-generator: Transform documentation into AI-agent-friendly formats.

    This tool converts documentation (initially Markdown) into structured formats
    with semantic tagging that AI agents can parse effectively.

    Supported features:
    \b
    - Markdown to JSON conversion
    - Semantic tagging (section types, content classifications)
    - MCP-compatible output mode
    - Configurable schema definitions
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "-i",
    "--input",
    "input_file",
    type=click.Path(exists=False),
    required=True,
    callback=validate_input_file,
    help="Input markdown file path",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(exists=False),
    callback=validate_output_file,
    help="Output file path (default: stdout)",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["json", "mcp"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format",
)
@click.option(
    "--schema",
    "schema_file",
    type=click.Path(exists=False),
    callback=validate_output_file,
    help="Custom JSON schema file for validation",
)
@click.option(
    "--pretty/--no-pretty",
    "pretty_print",
    default=True,
    show_default=True,
    help="Pretty print JSON output",
)
@click.option(
    "--include-metadata/--no-include-metadata",
    "include_metadata",
    default=True,
    show_default=True,
    help="Include document metadata in output",
)
@click.option(
    "--tag-semantics/--no-tag-semantics",
    "tag_semantics",
    default=True,
    show_default=True,
    help="Apply semantic tagging to sections",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase output verbosity (can be repeated)",
)
@click.pass_context
def convert(
    ctx: click.Context,
    input_file: str,
    output_file: Optional[str],
    output_format: str,
    schema_file: Optional[str],
    pretty_print: bool,
    include_metadata: bool,
    tag_semantics: bool,
    verbose: int,
) -> None:
    """
    Convert a markdown file to AI-readable format.

    This command transforms markdown documentation into structured JSON with
    semantic tagging that AI agents can parse effectively.

    Examples:

    \b
        # Convert markdown to JSON (stdout)
        $ ai-readable-doc convert -i docs/README.md

    \b
        # Convert to JSON file
        $ ai-readable-doc convert -i docs/README.md -o output.json

    \b
        # Convert to MCP-compatible format
        $ ai-readable-doc convert -i docs/README.md -f mcp -o mcp_output.json

    \b
        # Convert with custom schema
        $ ai-readable-doc convert -i docs/README.md --schema custom_schema.json
    """
    try:
        # Read input file
        input_path = Path(input_file)
        if verbose > 0:
            click.echo(f"Reading input file: {input_file}")

        markdown_content = input_path.read_text(encoding="utf-8")

        # Load custom schema if provided
        schema = None
        if schema_file:
            schema_path = Path(schema_file)
            if verbose > 0:
                click.echo(f"Loading custom schema: {schema_file}")
            schema = json.loads(schema_path.read_text(encoding="utf-8"))

        # Create document from markdown
        if verbose > 0:
            click.echo("Parsing markdown content...")

        document = Document.from_markdown(markdown_content)

        # Apply semantic tagging if enabled
        if tag_semantics:
            if verbose > 0:
                click.echo("Applying semantic tagging...")
            tagger = SemanticTagger()
            document = tagger.tag(document)

        # Create converter and transform
        if verbose > 0:
            click.echo(f"Converting to {output_format} format...")

        converter = Converter()

        if output_format == "mcp":
            transformer = MCPTransformer(schema=schema)
        else:
            transformer = JSONTransformer(
                schema=schema,
                include_metadata=include_metadata,
                pretty=pretty_print,
            )

        result = converter.convert(document, transformer)

        # Output result
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(result, encoding="utf-8")
            if verbose > 0:
                click.echo(f"Output written to: {output_file}")
        else:
            click.echo(result)

        if verbose > 0:
            click.echo("Conversion completed successfully.")

    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in schema file - {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: Invalid content - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Conversion failed - {e}", err=True)
        if verbose > 1:
            raise
        sys.exit(1)


@cli.command()
@click.option(
    "-i",
    "--input",
    "input_file",
    type=click.Path(exists=True),
    required=True,
    callback=validate_input_file,
    help="Input markdown file to validate",
)
@click.option(
    "--strict/--no-strict",
    "strict_mode",
    default=False,
    show_default=True,
    help="Enable strict validation mode",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase output verbosity (can be repeated)",
)
@click.pass_context
def validate(
    ctx: click.Context,
    input_file: str,
    strict_mode: bool,
    verbose: int,
) -> None:
    """
    Validate a markdown file for AI-readable conversion.

    This command checks if a markdown file is suitable for conversion,
    identifying potential issues with structure and content.

    Examples:

    \b
        # Validate a markdown file
        $ ai-readable-doc validate -i docs/README.md

    \b
        # Validate with verbose output
        $ ai-readable-doc validate -i docs/README.md -vv
    """
    try:
        input_path = Path(input_file)

        if verbose > 0:
            click.echo(f"Validating: {input_file}")

        # Read content
        markdown_content = input_path.read_text(encoding="utf-8")

        # Parse document
        if verbose > 0:
            click.echo("Parsing markdown content...")

        document = Document.from_markdown(markdown_content)

        # Run validations
        issues = []
        warnings = []

        # Check for empty content
        if not document.content.strip():
            issues.append("Document is empty")

        # Check for sections
        if not document.sections:
            warnings.append("No sections detected in document")

        # Check for headings hierarchy
        has_headings = any(s.level for s in document.sections)
        if not has_headings:
            warnings.append("No heading structure detected")

        # Check document length
        if len(markdown_content) < 50:
            warnings.append("Document is very short (< 50 characters)")

        # Report results
        if issues:
            click.echo("❌ Validation FAILED:", err=True)
            for issue in issues:
                click.echo(f"  • {issue}", err=True)

        if warnings and (verbose > 0 or strict_mode):
            click.echo("⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"  • {warning}")

        if not issues:
            if verbose > 0:
                click.echo("✅ Validation PASSED")
            else:
                click.echo("✅ Document is valid for conversion")

            if warnings:
                click.echo(f"\n{len(warnings)} warning(s) found. Use -v for details.")

    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Validation failed - {e}", err=True)
        if verbose > 1:
            raise
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(exists=False),
    help="Output file path (default: <input>.ai-readable.json)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "mcp"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format",
)
@click.pass_context
def inspect(
    ctx: click.Context,
    input_file: str,
    output_file: Optional[str],
    output_format: str,
) -> None:
    """
    Inspect a markdown file and display its structure.

    This command parses a markdown file and displays a summary of its
    structure, including sections, headings, and semantic tags.

    Example:

    \b
        $ ai-readable-doc inspect docs/README.md
    """
    try:
        input_path = Path(input_file)

        if output_file:
            output_path = Path(output_file)
        else:
            output_path = input_path.with_suffix(".ai-readable.json")

        # Read and parse
        markdown_content = input_path.read_text(encoding="utf-8")
        document = Document.from_markdown(markdown_content)

        # Apply semantic tagging for inspection
        tagger = SemanticTagger()
        tagged_document = tagger.tag(document)

        # Generate output
        if output_format == "mcp":
            transformer = MCPTransformer()
        else:
            transformer = JSONTransformer(include_metadata=True, pretty=True)

        converter = Converter()
        result = converter.convert(tagged_document, transformer)

        # Write to file
        output_path.write_text(result, encoding="utf-8")
        click.echo(f"✅ Structure inspection saved to: {output_path}")

        # Display summary
        click.echo(f"\n📄 Document Summary:")
        click.echo(f"  Title: {document.title or 'Untitled'}")
        click.echo(f"  Sections: {len(document.sections)}")

        # Count sections by type
        section_types = {}
        for section in document.sections:
            section_type = section.metadata.get("type", "unknown")
            section_types[section_type] = section_types.get(section_type, 0) + 1

        if section_types:
            click.echo(f"  Section Types:")
            for sec_type, count in section_types.items():
                click.echo(f"    - {sec_type}: {count}")

    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Inspection failed - {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--schema",
    "schema_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON schema file to display",
)
def schema_info(schema_file: str) -> None:
    """
    Display information about a JSON schema file.

    This command parses a JSON schema and displays its structure,
    properties, and validation rules in a human-readable format.

    Example:

    \b
        $ ai-readable-doc schema-info --schema custom_schema.json
    """
    try:
        import jsonschema

        schema_path = Path(schema_file)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        click.echo(f"📋 Schema: {schema_file}\n")

        # Title and description
        if "$defs" in schema or "definitions" in schema:
            click.echo(f"  Type: Compound Schema")
            definitions = schema.get("$defs", schema.get("definitions", {}))
            click.echo(f"  Definitions: {len(definitions)}")

        # Properties
        if "properties" in schema:
            props = schema["properties"]
            click.echo(f"\n  Properties ({len(props)}):")
            for name, prop in props.items():
                prop_type = prop.get("type", "any")
                description = prop.get("description", "")
                required = prop.get("description", "optional")
                req_marker = "🔴" if name in schema.get("required", []) else "⚪"
                click.echo(f"    {req_marker} {name}: {prop_type}")
                if description:
                    click.echo(f"        {description}")

        # Print full schema
        click.echo("\n📄 Full Schema:")
        click.echo("-" * 40)
        click.echo(json.dumps(schema, indent=2))

    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in schema file - {e}", err=True)
        sys.exit(1)
    except ImportError:
        click.echo("Note: Install jsonschema for detailed schema analysis", err=True)
        click.echo(json.dumps(json.loads(Path(schema_file).read_text()), indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
