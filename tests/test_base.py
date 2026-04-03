"""Tests for base converter class."""

import pytest

from ai_readable_doc_generator.base import BaseConverter


class ConcreteConverter(BaseConverter):
    """Concrete implementation of BaseConverter for testing."""

    def convert(self, source: str) -> "Document":
        from ai_readable_doc_generator import Document
        return Document(content=source)

    def validate(self, source: str) -> bool:
        return bool(source)


class TestBaseConverter:
    """Tests for BaseConverter."""

    def test_preprocess_default(self) -> None:
        """Test default preprocessing."""
        converter = ConcreteConverter()
        result = converter.preprocess("test")
        assert result == "test"

    def test_postprocess_default(self) -> None:
        """Test default postprocessing."""
        from ai_readable_doc_generator import Document
        converter = ConcreteConverter()
        doc = Document(content="test")
        result = converter.postprocess(doc)
        assert result == doc
