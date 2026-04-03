"""Main CLI module for ai-readable-doc-generator.

This module provides the command-line interface using Click framework.
"""

from ai_readable_doc_generator.cli.commands import (
    batch,
    cli,
    convert,
    info,
    mcp,
    validate,
)

__all__ = ["cli", "convert", "batch", "mcp", "validate", "info"]
