from .base import AbstractTool


def _sanitize_nullable_type(schema):
    """Rewrite JSON-Schema constructs that protobuf-based tool backends reject.

    Some LLM backends reached via OpenAI-compatible proxies (e.g. Gemini via
    Vertex AI) translate function parameters into a protobuf Schema message,
    which is stricter than plain JSON Schema in two ways relevant to our
    tool definitions:

    1. `type` is a single (non-repeating) enum value, so a nullable union
       like `{'type': ['string', 'null']}` fails with "Proto field is not
       repeating, cannot start list". We convert it to
       `{'type': 'string', 'nullable': True}`, which keeps the same meaning
       and is accepted by OpenAI-, Gemini- and Vertex-style backends alike.
    2. Each `anyOf` branch must be a self-contained object schema
       (`type: object` + its own `properties`) — Vertex rejects a branch
       that only has `required` and relies on the parent's `properties`,
       even though that is valid plain JSON Schema. We backfill `type` and
       `properties` into such branches from the parent schema.
    """
    if isinstance(schema, list):
        return [_sanitize_nullable_type(item) for item in schema]
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if key == 'type' and isinstance(value, list):
            non_null_types = [t for t in value if t != 'null']
            result['type'] = non_null_types[0] if non_null_types else value[0]
            if 'null' in value:
                result['nullable'] = True
        elif key == 'enum' and isinstance(value, list) and None in value:
            result['enum'] = [item for item in value if item is not None]
        elif key == 'properties' and isinstance(value, dict):
            result[key] = {
                prop_name: _sanitize_nullable_type(prop_schema)
                for prop_name, prop_schema in value.items()
            }
        elif key in ('items', 'anyOf', 'oneOf', 'allOf'):
            result[key] = _sanitize_nullable_type(value)
        else:
            result[key] = value

    if 'anyOf' in result:
        result['anyOf'] = [
            _self_contain_any_of_branch(branch, result.get('properties'))
            for branch in result['anyOf']
        ]
    return result


def _self_contain_any_of_branch(branch, parent_properties):
    """Backfill `type`/`properties` into a bare `{'required': [...]}`
    branch."""
    if not isinstance(branch, dict):
        return branch
    if 'type' in branch or 'properties' in branch or 'required' not in branch:
        return branch
    if not parent_properties:
        return branch

    branch = dict(branch)
    branch['type'] = 'object'
    branch['properties'] = {
        name: parent_properties[name]
        for name in branch['required']
        if name in parent_properties
    }
    return branch


class ToolRegistry:
    """Registry of action tools exposed to LLM tool-calling."""

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        if not isinstance(tool, AbstractTool):
            raise TypeError('tool must be an AbstractTool instance')
        if not tool.name:
            raise ValueError('tool.name is required')
        if tool.name in self._tools:
            raise ValueError('tool already registered: %s' % tool.name)
        self._tools[tool.name] = tool
        return tool

    def get(self, name):
        return self._tools[name]

    def list_for_user(self, env):
        return [
            tool for tool in self._tools.values()
            if self._user_has_required_groups(env, tool)
        ]

    def to_openrouter_tools(self, env, read_only=False):
        tools = self.list_for_user(env)
        if read_only:
            tools = [tool for tool in tools if not tool.is_write]
        return [
            {
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': _sanitize_nullable_type(
                        tool.parameters_schema
                    ),
                },
            }
            for tool in tools
        ]

    def _user_has_required_groups(self, env, tool):
        groups = tool.required_groups or []
        if not groups:
            return True
        return all(env.user.has_group(xmlid) for xmlid in groups)


default_registry = ToolRegistry()
