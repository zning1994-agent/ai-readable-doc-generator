"""
Parser module for ai-readable-doc-generator.

This module provides parsing functionality for various document formats,
with support for semantic tagging and content classification.
"""

from ai_readable_doc_generator.parser.base import BaseParser
from ai_readable_doc_generator.parser.markdown_parser import MarkdownParser

__all__ = ["BaseParser", "MarkdownParser"]
