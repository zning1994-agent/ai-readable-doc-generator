"""Tests for the base DocumentConverter abstract class."""

import pytest

from ai_readable_doc_generator.base import DocumentConverter
from ai_readable_doc_generator.document import Document


class ConcreteConverter(DocumentConverter):
    """Concrete implementation for testing."""

    def __init__(self, raise_error: bool = False):
        self.raise_error = raise_error

    def convert(self, content: str) -> Document:
        if self.raise_error:
            raise ValueError("Test error")
        doc = Document()
        doc.title = content[:50] if content else "Untitled"
        return doc


class TestDocumentConverter:
    """Test cases for DocumentConverter abstract base class."""

    def test_converter_is_abstract(self):
        """DocumentConverter should not be instantiable directly."""

        class NonImplementing:
            pass

        with pytest.raises(TypeError, match="abstract"):
            converter = NonImplementing()  # type: ignore
            converter.convert("test")

    def test_concrete_converter_implements_interface(self):
        """Concrete converter should implement the convert method."""

        class MyConverter(DocumentConverter):
            def convert(self, content: str) -> Document:
                return Document(title=content)

        converter = MyConverter()
        assert isinstance(converter, DocumentConverter)

    def test_convert_returns_document(self):
        """convert() should return a Document instance."""
        converter = ConcreteConverter()
        result = converter.convert("# Hello World")

        assert isinstance(result, Document)
        assert result.title == "# Hello World"[:50]

    def test_convert_with_empty_content(self):
        """convert() should handle empty content gracefully."""
        converter = ConcreteConverter()
        result = converter.convert("")

        assert isinstance(result, Document)
        assert result.title == "Untitled"

    def test_convert_preserves_error_behavior(self):
        """convert() should propagate errors from implementation."""
        converter = ConcreteConverter(raise_error=True)

        with pytest.raises(ValueError, match="Test error"):
            converter.convert("test content")

    def test_converter_subclass_can_add_custom_state(self):
        """Converter subclasses can have custom initialization."""

        class ConfigurableConverter(DocumentConverter):
            def __init__(self, prefix: str = ""):
                self.prefix = prefix

            def convert(self, content: str) -> Document:
                doc = Document()
                doc.title = f"{self.prefix}{content[:40]}"
                return doc

        converter = ConfigurableConverter(prefix="PREFIX: ")
        result = converter.convert("test")

        assert result.title == "PREFIX: test"

    def test_convert_signature(self):
        """Convert method should have the correct signature."""
        import inspect

        sig = inspect.signature(DocumentConverter.convert)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "content" in params
        assert len(params) == 2

    def test_convert_return_type_annotation(self):
        """Convert method should have Document return type annotation."""
        import inspect

        hints = DocumentConverter.convert.__annotations__
        assert "return" in hints
        assert hints["return"] is Document
