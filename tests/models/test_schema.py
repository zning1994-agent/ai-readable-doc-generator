"""Unit tests for schema module."""

import pytest

from ai_readable_doc_generator.models.schema import (
    OutputFormat,
    SchemaDefinition,
    SchemaField,
    SchemaValidator,
)


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_exist(self):
        """Test all expected output formats exist."""
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.YAML.value == "yaml"
        assert OutputFormat.MCP.value == "mcp"
        assert OutputFormat.MARKDOWN.value == "markdown"

    def test_format_values(self):
        """Test format values are strings."""
        for fmt in OutputFormat:
            assert isinstance(fmt.value, str)


class TestSchemaField:
    """Tests for SchemaField class."""

    def test_create_field(self):
        """Test creating a basic field."""
        field = SchemaField(name="title", field_type="string")

        assert field.name == "title"
        assert field.field_type == "string"
        assert field.required is True
        assert field.default is None
        assert field.description == ""

    def test_create_optional_field(self):
        """Test creating an optional field."""
        field = SchemaField(name="author", field_type="string", required=False)

        assert field.required is False

    def test_create_field_with_defaults(self):
        """Test creating a field with default value."""
        field = SchemaField(
            name="status",
            field_type="string",
            default="draft",
        )

        assert field.default == "draft"

    def test_create_field_with_enum(self):
        """Test creating a field with enum values."""
        field = SchemaField(
            name="priority",
            field_type="string",
            enum_values=["low", "medium", "high"],
        )

        assert field.enum_values == ["low", "medium", "high"]

    def test_to_dict(self):
        """Test converting field to dictionary."""
        field = SchemaField(
            name="version",
            field_type="string",
            required=False,
            description="Version number",
        )

        result = field.to_dict()

        assert result["name"] == "version"
        assert result["type"] == "string"
        assert result["required"] is False
        assert result["description"] == "Version number"
        assert "default" not in result

    def test_to_dict_with_default(self):
        """Test converting field with default to dict."""
        field = SchemaField(name="count", field_type="integer", default=0)

        result = field.to_dict()

        assert result["default"] == 0

    def test_to_dict_with_enum(self):
        """Test converting field with enum to dict."""
        field = SchemaField(
            name="type",
            field_type="string",
            enum_values=["a", "b"],
        )

        result = field.to_dict()

        assert result["enum"] == ["a", "b"]


class TestSchemaDefinition:
    """Tests for SchemaDefinition class."""

    def test_create_schema(self):
        """Test creating a basic schema."""
        schema = SchemaDefinition(name="TestSchema", version="1.0")

        assert schema.name == "TestSchema"
        assert schema.version == "1.0"
        assert schema.description == ""
        assert schema.fields == []
        assert schema.metadata == {}

    def test_add_field(self):
        """Test adding fields to schema."""
        schema = SchemaDefinition(name="Test")
        field = SchemaField(name="title", field_type="string")

        schema.add_field(field)

        assert len(schema.fields) == 1
        assert schema.fields[0].name == "title"

    def test_get_field(self):
        """Test getting field by name."""
        schema = SchemaDefinition(name="Test")
        field1 = SchemaField(name="title", field_type="string")
        field2 = SchemaField(name="author", field_type="string")
        schema.add_field(field1)
        schema.add_field(field2)

        result = schema.get_field("author")

        assert result is not None
        assert result.name == "author"

    def test_get_field_not_found(self):
        """Test getting non-existent field."""
        schema = SchemaDefinition(name="Test")

        result = schema.get_field("nonexistent")

        assert result is None

    def test_get_required_fields(self):
        """Test getting required fields."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="required1", field_type="string", required=True))
        schema.add_field(SchemaField(name="optional", field_type="string", required=False))
        schema.add_field(SchemaField(name="required2", field_type="string", required=True))

        required = schema.get_required_fields()

        assert len(required) == 2
        assert {f.name for f in required} == {"required1", "required2"}

    def test_to_dict(self):
        """Test converting schema to dictionary."""
        schema = SchemaDefinition(
            name="TestSchema",
            version="2.0",
            description="A test schema",
        )
        schema.add_field(SchemaField(name="title", field_type="string"))

        result = schema.to_dict()

        assert result["name"] == "TestSchema"
        assert result["version"] == "2.0"
        assert result["description"] == "A test schema"
        assert len(result["fields"]) == 1
        assert result["metadata"] == {}

    def test_from_dict(self):
        """Test creating schema from dictionary."""
        data = {
            "name": "MySchema",
            "version": "1.5",
            "description": "Test description",
            "fields": [
                {"name": "title", "type": "string", "required": True},
                {"name": "count", "type": "integer", "required": False},
            ],
            "metadata": {"author": "test"},
        }

        schema = SchemaDefinition.from_dict(data)

        assert schema.name == "MySchema"
        assert schema.version == "1.5"
        assert schema.description == "Test description"
        assert len(schema.fields) == 2
        assert schema.fields[0].name == "title"
        assert schema.metadata == {"author": "test"}

    def test_from_dict_with_defaults(self):
        """Test creating schema from dict with missing fields."""
        data = {"name": "Minimal"}

        schema = SchemaDefinition.from_dict(data)

        assert schema.name == "Minimal"
        assert schema.version == "1.0"
        assert schema.description == ""
        assert schema.fields == []

    def test_document_schema(self):
        """Test creating default document schema."""
        schema = SchemaDefinition.document_schema()

        assert schema.name == "AIReadableDocument"
        assert schema.version == "1.0"
        assert len(schema.fields) > 0

        field_names = {f.name for f in schema.fields}
        assert "title" in field_names
        assert "sections" in field_names
        assert "metadata" in field_names

    def test_mcp_schema(self):
        """Test creating MCP schema."""
        schema = SchemaDefinition.mcp_schema()

        assert schema.name == "MCPDocument"
        assert len(schema.fields) > 0

        field_names = {f.name for f in schema.fields}
        assert "context_type" in field_names
        assert "content" in field_names
        assert "annotations" in field_names


class TestSchemaValidator:
    """Tests for SchemaValidator class."""

    def test_create_validator(self):
        """Test creating a validator."""
        schema = SchemaDefinition(name="Test")
        validator = SchemaValidator(schema)

        assert validator.schema.name == "Test"

    def test_validate_valid_data(self):
        """Test validating valid data."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="title", field_type="string", required=True))
        schema.add_field(SchemaField(name="count", field_type="integer", required=False))

        validator = SchemaValidator(schema)
        data = {"title": "Hello", "count": 42}

        is_valid, errors = validator.validate(data)

        assert is_valid is True
        assert errors == []

    def test_validate_missing_required_field(self):
        """Test validation fails for missing required field."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="title", field_type="string", required=True))

        validator = SchemaValidator(schema)
        data = {}

        is_valid, errors = validator.validate(data)

        assert is_valid is False
        assert "Missing required field: title" in errors

    def test_validate_null_required_field(self):
        """Test validation fails for null required field."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="title", field_type="string", required=True))

        validator = SchemaValidator(schema)
        data = {"title": None}

        is_valid, errors = validator.validate(data)

        assert is_valid is False
        assert "Field cannot be null: title" in errors

    def test_validate_invalid_type(self):
        """Test validation fails for wrong type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="count", field_type="integer"))

        validator = SchemaValidator(schema)
        data = {"count": "not an integer"}

        is_valid, errors = validator.validate(data)

        assert is_valid is False
        assert any("Invalid type" in e for e in errors)

    def test_validate_invalid_enum(self):
        """Test validation fails for invalid enum value."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(
            SchemaField(
                name="status",
                field_type="string",
                enum_values=["active", "inactive"],
            )
        )

        validator = SchemaValidator(schema)
        data = {"status": "unknown"}

        is_valid, errors = validator.validate(data)

        assert is_valid is False
        assert any("Invalid value" in e for e in errors)

    def test_validate_multiple_errors(self):
        """Test validation collects multiple errors."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="title", field_type="string", required=True))
        schema.add_field(SchemaField(name="author", field_type="string", required=True))

        validator = SchemaValidator(schema)
        data = {}

        is_valid, errors = validator.validate(data)

        assert is_valid is False
        assert len(errors) == 2

    def test_validate_field_valid(self):
        """Test validating a single field."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="count", field_type="integer"))

        validator = SchemaValidator(schema)
        is_valid, error = validator.validate_field("count", 42)

        assert is_valid is True
        assert error is None

    def test_validate_field_invalid_type(self):
        """Test validating field with wrong type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="count", field_type="integer"))

        validator = SchemaValidator(schema)
        is_valid, error = validator.validate_field("count", "not int")

        assert is_valid is False
        assert "Invalid type" in error

    def test_validate_field_unknown(self):
        """Test validating unknown field."""
        schema = SchemaDefinition(name="Test")

        validator = SchemaValidator(schema)
        is_valid, error = validator.validate_field("unknown", "value")

        assert is_valid is False
        assert "Unknown field" in error

    def test_validate_field_null_optional(self):
        """Test validating null optional field."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="optional", field_type="string", required=False))

        validator = SchemaValidator(schema)
        is_valid, error = validator.validate_field("optional", None)

        assert is_valid is True

    def test_validate_field_null_required(self):
        """Test validating null required field."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="required", field_type="string", required=True))

        validator = SchemaValidator(schema)
        is_valid, error = validator.validate_field("required", None)

        assert is_valid is False
        assert "Required field" in error

    def test_validate_string_type(self):
        """Test validating string type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="title", field_type="string"))

        validator = SchemaValidator(schema)
        is_valid, _ = validator.validate_field("title", "Hello")
        assert is_valid is True

    def test_validate_boolean_type(self):
        """Test validating boolean type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="active", field_type="boolean"))

        validator = SchemaValidator(schema)
        is_valid, _ = validator.validate_field("active", True)
        assert is_valid is True

    def test_validate_array_type(self):
        """Test validating array type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="items", field_type="array"))

        validator = SchemaValidator(schema)
        is_valid, _ = validator.validate_field("items", [1, 2, 3])
        assert is_valid is True

    def test_validate_object_type(self):
        """Test validating object type."""
        schema = SchemaDefinition(name="Test")
        schema.add_field(SchemaField(name="data", field_type="object"))

        validator = SchemaValidator(schema)
        is_valid, _ = validator.validate_field("data", {"key": "value"})
        assert is_valid is True
