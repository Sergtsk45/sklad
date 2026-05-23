from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.action_tools.base import (
    AbstractReadTool,
    AbstractWriteTool,
)
from odoo.addons.ai_assistant.services.action_tools.registry import ToolRegistry


class DummyEnv:
    def __init__(self, groups=None):
        self.user = DummyUser(groups or set())


class DummyUser:
    def __init__(self, groups):
        self._groups = groups

    def has_group(self, xmlid):
        return xmlid in self._groups


class DummyReadTool(AbstractReadTool):
    name = 'dummy_read'
    description = 'Read dummy data'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string'},
        },
        'required': ['query'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        return {'query': args['query']}


class GroupedReadTool(DummyReadTool):
    name = 'grouped_read'
    required_groups = ['ai_assistant.group_ai_assistant_supply']


class DummyWriteTool(AbstractWriteTool):
    name = 'dummy_write'
    description = 'Write dummy data'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'count': {'type': 'integer'},
        },
        'required': ['name'],
        'additionalProperties': False,
    }
    required_groups = ['ai_assistant.group_ai_assistant_supply']

    def execute(self, env, args):
        return {'id': 1}

    def idempotency_key(self, args):
        return args['name']


@tagged('post_install', '-at_install')
class TestActionToolsRegistry(TransactionCase):

    def test_register_and_get(self):
        registry = ToolRegistry()
        tool = DummyReadTool()
        registry.register(tool)
        self.assertIs(registry.get('dummy_read'), tool)

    def test_list_for_user_filters_by_group(self):
        registry = ToolRegistry()
        registry.register(DummyReadTool())
        registry.register(GroupedReadTool())

        env_without_group = DummyEnv()
        visible = registry.list_for_user(env_without_group)
        self.assertEqual([tool.name for tool in visible], ['dummy_read'])

        env_with_group = DummyEnv({'ai_assistant.group_ai_assistant_supply'})
        visible = registry.list_for_user(env_with_group)
        self.assertEqual(
            [tool.name for tool in visible],
            ['dummy_read', 'grouped_read']
        )

    def test_to_openrouter_tools_schema_shape(self):
        registry = ToolRegistry()
        registry.register(DummyReadTool())
        tools = registry.to_openrouter_tools(DummyEnv())

        self.assertEqual(tools[0]['type'], 'function')
        function = tools[0]['function']
        self.assertEqual(function['name'], 'dummy_read')
        self.assertEqual(function['description'], 'Read dummy data')
        self.assertEqual(function['parameters']['type'], 'object')
        self.assertFalse(function['parameters']['additionalProperties'])

    def test_validate_args_rejects_extra_properties(self):
        tool = DummyReadTool()
        with self.assertRaises(ValueError):
            tool.validate_args({'query': 'abc', 'state': 'done'})

    def test_validate_args_rejects_missing_required(self):
        tool = DummyReadTool()
        with self.assertRaises(ValueError):
            tool.validate_args({})

    def test_write_tool_requires_idempotency_key(self):
        tool = DummyWriteTool()
        self.assertTrue(tool.is_write)
        self.assertEqual(tool.idempotency_key({'name': 'abc'}), 'abc')
