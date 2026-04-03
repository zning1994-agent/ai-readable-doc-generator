"""Entry point for running the CLI as a module.

Usage:
    python -m ai_readable_doc_generator.cli README.md
"""

from ai_readable_doc_generator.cli.commands import cli

if __name__ == "__main__":
    cli()
