"""CLI commands for ai-readable-doc-generator."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ai_readable_doc_generator.converter import Converter
from ai_readable_doc_generator.models.document import DocumentMetadata
from ai_readable_doc_generator.transformer.json_transformer import JSONTransformer
from ai_readable_doc_generator.transformer.mcp_transformer import MCPTransformer
from ai_readable_doc_generator.transformer.yaml_transformer import YAMLTransformer


console = Console()


def resolve_output_path(input_path: Path, output_dir: Optional[Path], suffix: str) -> Path:
    """Resolve output path for a given input file.
    
    Args:
        input_path: The input file path.
        output_dir: Optional output directory. If None, uses input file's directory.
        suffix: Suffix to append to the output filename.
    
    Returns:
        Resolved output path.
    """
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{input_path.stem}{suffix}"
    else:
        return input_path.with_suffix(suffix)


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """AI-Readable Document Generator - Transform documentation into AI-friendly formats.
    
    Convert Markdown documents into structured JSON with semantic tagging
    for optimal AI agent and LLM consumption.
    """
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to input filename with .json extension.",
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    help="Pretty print JSON output. Default is True.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "mcp"], case_sensitive=False),
    default="json",
    help="Output format: json, yaml, or mcp. Default is json.",
)
def convert(input_file: Path, output_file: Optional[Path], pretty: bool, output_format: str) -> None:
    """Convert a single Markdown file to AI-readable format.
    
    INPUT_FILE: Path to the Markdown file to convert.
    
    Examples:
    
        ai-readable-doc-gen convert README.md
    
        ai-readable-doc-gen convert README.md -o output.json --pretty
    
        ai-readable-doc-gen convert README.md --format yaml -o output.yaml
    
        ai-readable-doc-gen convert README.md --format mcp -o mcp_output.json
    """
    try:
        converter = Converter()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Converting document...", total=None)
            
            result = converter.convert_file(input_file)
            
            if output_format == "mcp":
                transformer = MCPTransformer()
                output_content = transformer.transform(result)
            elif output_format == "yaml":
                transformer = YAMLTransformer(pretty=pretty)
                output_content = transformer.transform(result)
            else:
                transformer = JSONTransformer(pretty=pretty)
                output_content = transformer.transform(result)
            
            progress.update(task, completed=True)
        
        # Determine output path
        if output_file:
            output_path = output_file
        else:
            suffix_map = {"mcp": ".mcp.json", "yaml": ".yaml", "json": ".json"}
            suffix = suffix_map.get(output_format, ".json")
            output_path = resolve_output_path(input_file, None, suffix)
        
        # Write output
        output_path.write_text(output_content, encoding="utf-8")
        
        console.print(f"[green]✓[/green] Successfully converted: {input_file.name}")
        console.print(f"[dim]Output saved to: {output_path}[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument("input_paths", type=click.Path(exists=True, path_type=Path), nargs=-1)
@click.option(
    "-o",
    "--output-dir",
    "output_dir",
    type=click.Path(path_type=Path),
    help="Output directory for converted files. Defaults to each file's directory.",
)
@click.option(
    "--pattern",
    "-p",
    default="*.md",
    help="File pattern for batch processing. Default is '*.md'.",
)
@click.option(
    "--recursive/--no-recursive",
    "-r/-R",
    default=False,
    help="Recursively search for matching files in subdirectories.",
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    help="Pretty print JSON output. Default is True.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "mcp"], case_sensitive=False),
    default="json",
    help="Output format: json, yaml, or mcp. Default is json.",
)
def batch(
    input_paths: tuple[Path, ...],
    output_dir: Optional[Path],
    pattern: str,
    recursive: bool,
    pretty: bool,
    output_format: str,
) -> None:
    """Convert multiple Markdown files in batch mode.
    
    INPUT_PATHS: One or more files or directories to process.
    
    When a directory is provided, all Markdown files matching the pattern
    are processed. Use --recursive to search subdirectories.
    
    Examples:
    
        ai-readable-doc-gen batch docs/
    
        ai-readable-doc-gen batch README.md CHANGELOG.md -o output/
    
        ai-readable-doc-gen batch docs/ --pattern "*.md" --recursive -o output/
    
        ai-readable-doc-gen batch . --format yaml --pattern "*.md"
    """
    # Collect all input files
    input_files: list[Path] = []
    
    for input_path in input_paths:
        if input_path.is_file():
            if input_path.suffix.lower() == ".md":
                input_files.append(input_path)
        elif input_path.is_dir():
            if recursive:
                input_files.extend(input_path.rglob(pattern))
            else:
                input_files.extend(input_path.glob(pattern))
    
    if not input_files:
        console.print("[yellow]No Markdown files found to convert.[/yellow]")
        return
    
    # Setup transformer based on format
    suffix_map = {"mcp": ".mcp.json", "yaml": ".yaml", "json": ".json"}
    suffix = suffix_map.get(output_format, ".json")
    
    def get_transformer():
        if output_format == "mcp":
            return MCPTransformer()
        elif output_format == "yaml":
            return YAMLTransformer(pretty=pretty)
        else:
            return JSONTransformer(pretty=pretty)
    
    # Process files
    results: list[tuple[Path, bool, str]] = []  # (path, success, message)
    converter = Converter()
    
    console.print(f"\n[bold]Batch Conversion[/bold] - Processing {len(input_files)} file(s)\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Converting...", total=len(input_files))
        
        for input_file in input_files:
            try:
                result = converter.convert_file(input_file)
                transformer = get_transformer()
                output_content = transformer.transform(result)
                
                # Determine output path
                if output_dir:
                    output_path = resolve_output_path(input_file, output_dir, suffix)
                else:
                    output_path = resolve_output_path(input_file, None, suffix)
                
                output_path.write_text(output_content, encoding="utf-8")
                results.append((input_file, True, str(output_path)))
                
            except Exception as e:
                results.append((input_file, False, str(e)))
            
            progress.update(task, advance=1)
    
    # Display results table
    table = Table(title="Conversion Results")
    table.add_column("Status", style="green" if all(r[1] for r in results) else "red")
    table.add_column("File", style="cyan")
    table.add_column("Output", style="dim")
    
    success_count = 0
    for path, success, message in results:
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        output_info = message if success else f"[red]{message}[/red]"
        table.add_row(status, path.name, output_info)
        if success:
            success_count += 1
    
    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} files converted successfully")
    
    if success_count < len(results):
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to input filename with .mcp.json extension.",
)
def mcp(input_file: Path, output_file: Optional[Path]) -> None:
    """Convert a Markdown file to MCP-compatible JSON format.
    
    This is a convenience command equivalent to:
        convert INPUT_FILE --mcp --output OUTPUT
    
    INPUT_FILE: Path to the Markdown file to convert.
    
    Examples:
    
        ai-readable-doc-gen mcp README.md
    
        ai-readable-doc-gen mcp README.md -o mcp_output.json
    """
    # Delegate to convert command with MCP mode
    ctx = click.get_current_context()
    ctx.invoke(convert, input_file=input_file, output_file=output_file, pretty=True, output_format="mcp")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate a Markdown file for AI-readable conversion.
    
    Checks if the file can be parsed and identifies any potential issues.
    
    INPUT_FILE: Path to the Markdown file to validate.
    
    Examples:
    
        ai-readable-doc-gen validate README.md
    """
    from ai_readable_doc_generator.parser import MarkdownParser
    
    try:
        parser = MarkdownParser()
        content = input_file.read_text(encoding="utf-8")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Parsing document...", total=None)
            document = parser.parse(content, file_path=input_file)
            progress.update(task, completed=True)
        
        # Display validation info
        table = Table(title=f"Validation Results: {input_file.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        metadata = document.metadata
        table.add_row("Title", metadata.title or "(untitled)")
        table.add_row("Sections", str(len(document.sections)))
        table.add_row("Total Characters", str(metadata.character_count or 0))
        table.add_row("Total Words", str(metadata.word_count or 0))
        table.add_row("Has Frontmatter", "Yes" if metadata.frontmatter else "No")
        
        console.print(table)
        console.print("\n[green]✓[/green] Document is valid for conversion")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Validation failed: {e}")
        sys.exit(1)


@cli.command()
def info() -> None:
    """Display information about the AI-Readable Document Generator."""
    info_text = """
[bold cyan]AI-Readable Document Generator[/bold cyan] v0.1.0

[bold]Purpose:[/bold] Transform Markdown documentation into AI-friendly formats
with semantic tagging for optimal LLM and AI Agent consumption.

[bold]Supported Input Formats:[/bold]
  • Markdown (.md)

[bold]Supported Output Formats:[/bold]
  • JSON (structured)
  • YAML (structured)
  • MCP-compatible JSON

[bold]Features:[/bold]
  • Semantic tagging of sections
  • Hierarchical structure preservation
  • Frontmatter extraction
  • Content classification
  • MCP protocol compatibility

[bold]Commands:[/bold]
  convert   - Convert a single file
  batch     - Convert multiple files
  mcp       - Convert to MCP format
  validate  - Validate a document
  info      - Show this information

[bold]Getting Started:[/bold]
  ai-readable-doc-gen convert README.md -o output.json
  ai-readable-doc-gen batch docs/ --recursive -o output/
    """
    console.print(info_text)


if __name__ == "__main__":
    cli()
