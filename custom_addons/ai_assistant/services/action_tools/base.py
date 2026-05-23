from abc import ABC, abstractmethod


class AbstractTool(ABC):
    """Base class for AI action tools independent from HTTP and LLM clients."""

    name = ''
    description = ''
    parameters_schema = {
        'type': 'object',
        'properties': {},
        'required': [],
        'additionalProperties': False,
    }
    required_groups = []
    is_write = False

    def validate_args(self, args):
        """Validate tool arguments against the JSON Schema subset we use."""
        schema = self.parameters_schema or {}
        self._validate_with_jsonschema_if_available(args, schema)

    def _validate_with_jsonschema_if_available(self, args, schema):
        try:
            from jsonschema import Draft202012Validator
        except Exception:
            self._validate_args_manually(args, schema)
            return

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(args), key=lambda err: err.path)
        if errors:
            raise ValueError(errors[0].message)

    def _validate_args_manually(self, args, schema):
        if schema.get('type') == 'object' and not isinstance(args, dict):
            raise ValueError('Tool arguments must be an object')

        properties = schema.get('properties', {})
        required = schema.get('required', [])
        for field_name in required:
            if field_name not in args:
                raise ValueError("Missing required argument: %s" % field_name)

        if schema.get('additionalProperties') is False:
            extra = set(args) - set(properties)
            if extra:
                raise ValueError(
                    "Unexpected argument: %s" % sorted(extra)[0]
                )

        for field_name, value in args.items():
            field_schema = properties.get(field_name)
            if not field_schema:
                continue
            self._validate_value_type(field_name, value, field_schema)
            self._validate_value_enum(field_name, value, field_schema)

    def _validate_value_type(self, field_name, value, field_schema):
        expected_type = field_schema.get('type')
        if not expected_type:
            return

        if isinstance(expected_type, list):
            if any(self._matches_json_type(value, item) for item in expected_type):
                return
            raise ValueError("Invalid type for argument: %s" % field_name)

        if not self._matches_json_type(value, expected_type):
            raise ValueError("Invalid type for argument: %s" % field_name)

    def _matches_json_type(self, value, expected_type):
        if expected_type == 'null':
            return value is None
        if expected_type == 'string':
            return isinstance(value, str)
        if expected_type == 'integer':
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == 'number':
            return (
                isinstance(value, (int, float)) and not isinstance(value, bool)
            )
        if expected_type == 'boolean':
            return isinstance(value, bool)
        if expected_type == 'array':
            return isinstance(value, list)
        if expected_type == 'object':
            return isinstance(value, dict)
        return True

    def _validate_value_enum(self, field_name, value, field_schema):
        enum_values = field_schema.get('enum')
        if enum_values is not None and value not in enum_values:
            raise ValueError("Invalid enum value for argument: %s" % field_name)

    @abstractmethod
    def execute(self, env, args):
        """Execute tool logic in the supplied Odoo env and return a dict."""


class AbstractReadTool(AbstractTool):
    is_write = False


class AbstractWriteTool(AbstractTool):
    is_write = True

    @abstractmethod
    def idempotency_key(self, args):
        """Return a stable key for duplicate write protection."""
