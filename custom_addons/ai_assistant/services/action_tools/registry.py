from .base import AbstractTool


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

    def to_openrouter_tools(self, env):
        return [
            {
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.parameters_schema,
                },
            }
            for tool in self.list_for_user(env)
        ]

    def _user_has_required_groups(self, env, tool):
        groups = tool.required_groups or []
        if not groups:
            return True
        return all(env.user.has_group(xmlid) for xmlid in groups)


default_registry = ToolRegistry()
