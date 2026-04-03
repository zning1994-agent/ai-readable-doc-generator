"""Unit tests for BaseParser class."""

import pytest

from ai_readable_doc_generator.parser.base import BaseParser, ParseError


class ConcreteParser(BaseParser):
    """Concrete implementation of BaseParser for testing."""

    def parse(self, content: str) -> dict:
        """Parse content by wrapping it in a dictionary."""
        if not content:
            raise ParseError("Content cannot be empty")
        return {"content": content, "type": "concrete"}

    def validate(self, content: str) -> bool:
        """Validate content is non-empty."""
        return bool(content and len(content.strip()) > 0)


class TestBaseParser:
    """Test suite for BaseParser class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        parser = ConcreteParser()
        assert parser.config == {}
        assert parser._plugins == []

    def test_init_with_config(self):
        """Test initialization with custom configuration."""
        config = {"key1": "value1", "key2": 42}
        parser = ConcreteParser(config)
        assert parser.config == config

    def test_register_plugin(self):
        """Test plugin registration."""
        parser = ConcreteParser()
        plugin = {"process": lambda x: x}
        parser.register_plugin(plugin)
        assert plugin in parser._plugins

    def test_register_multiple_plugins(self):
        """Test registering multiple plugins."""
        parser = ConcreteParser()
        plugin1 = {"process": lambda x: x}
        plugin2 = {"process": lambda x: x}
        parser.register_plugin(plugin1)
        parser.register_plugin(plugin2)
        assert len(parser._plugins) == 2
        assert plugin1 in parser._plugins
        assert plugin2 in parser._plugins

    def test_unregister_plugin(self):
        """Test plugin unregistration."""
        parser = ConcreteParser()
        plugin = {"process": lambda x: x}
        parser.register_plugin(plugin)
        parser.unregister_plugin(plugin)
        assert plugin not in parser._plugins

    def test_unregister_nonexistent_plugin(self):
        """Test unregistering a plugin that was never registered."""
        parser = ConcreteParser()
        plugin = {"process": lambda x: x}
        # Should not raise an error
        parser.unregister_plugin(plugin)
        assert len(parser._plugins) == 0

    def test_clear_plugins(self):
        """Test clearing all plugins."""
        parser = ConcreteParser()
        plugin1 = {"process": lambda x: x}
        plugin2 = {"process": lambda x: x}
        parser.register_plugin(plugin1)
        parser.register_plugin(plugin2)
        parser.clear_plugins()
        assert len(parser._plugins) == 0

    def test_apply_plugins_empty(self):
        """Test applying plugins when none are registered."""
        parser = ConcreteParser()
        result = parser._apply_plugins({"key": "value"})
        assert result == {"key": "value"}

    def test_apply_plugins_single(self):
        """Test applying a single plugin."""
        parser = ConcreteParser()
        called = {"value": False}

        def plugin_process(doc):
            called["value"] = True
            doc["plugin_applied"] = True
            return doc

        plugin = type("Plugin", (), {"process": plugin_process})()
        parser.register_plugin(plugin)

        result = parser._apply_plugins({"key": "value"})
        assert called["value"] is True
        assert result["plugin_applied"] is True

    def test_apply_plugins_multiple(self):
        """Test applying multiple plugins in order."""
        parser = ConcreteParser()
        call_order = []

        def make_plugin(name):
            def process(doc):
                call_order.append(name)
                doc[f"from_{name}"] = True
                return doc
            return type("Plugin", (), {"process": process})()

        plugin1 = make_plugin("p1")
        plugin2 = make_plugin("p2")
        plugin3 = make_plugin("p3")

        parser.register_plugin(plugin1)
        parser.register_plugin(plugin2)
        parser.register_plugin(plugin3)

        result = parser._apply_plugins({})
        assert call_order == ["p1", "p2", "p3"]
        assert result["from_p1"] is True
        assert result["from_p2"] is True
        assert result["from_p3"] is True


class TestParseError:
    """Test suite for ParseError exception."""

    def test_init_with_message_only(self):
        """Test initialization with just a message."""
        error = ParseError("Something went wrong")
        assert str(error) == "Parse error: Something went wrong"
        assert error.line is None

    def test_init_with_message_and_line(self):
        """Test initialization with message and line number."""
        error = ParseError("Invalid syntax", line=42)
        assert "line 42" in str(error)
        assert "Invalid syntax" in str(error)
        assert error.line == 42

    def test_init_with_zero_line(self):
        """Test initialization with line 0."""
        error = ParseError("Start error", line=0)
        assert "line 0" in str(error)
        assert error.line == 0

    def test_inheritance(self):
        """Test that ParseError inherits from Exception."""
        error = ParseError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching ParseError."""
        parser = ConcreteParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse("")

        assert "Content cannot be empty" in str(exc_info.value)


class TestConcreteParserInterface:
    """Test suite for concrete parser interface implementation."""

    def test_parse_returns_dict(self):
        """Test that parse returns a dictionary."""
        parser = ConcreteParser()
        result = parser.parse("test content")
        assert isinstance(result, dict)

    def test_parse_content_preserved(self):
        """Test that parse preserves content."""
        parser = ConcreteParser()
        content = "test content"
        result = parser.parse(content)
        assert result["content"] == content

    def test_parse_empty_raises_error(self):
        """Test that parsing empty content raises ParseError."""
        parser = ConcreteParser()
        with pytest.raises(ParseError):
            parser.parse("")

    def test_parse_whitespace_only_raises_error(self):
        """Test that parsing whitespace-only content raises ParseError."""
        parser = ConcreteParser()
        with pytest.raises(ParseError):
            parser.parse("   ")

    def test_validate_with_valid_content(self):
        """Test validate with valid content."""
        parser = ConcreteParser()
        assert parser.validate("valid content") is True

    def test_validate_with_empty_content(self):
        """Test validate with empty content."""
        parser = ConcreteParser()
        assert parser.validate("") is False

    def test_validate_with_whitespace_content(self):
        """Test validate with whitespace-only content."""
        parser = ConcreteParser()
        assert parser.validate("   ") is False

    def test_validate_with_none(self):
        """Test validate with None."""
        parser = ConcreteParser()
        assert parser.validate(None) is False
