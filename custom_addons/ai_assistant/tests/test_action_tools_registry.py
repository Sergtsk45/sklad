from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.action_tools.base import (
    AbstractReadTool,
    AbstractWriteTool,
)
from odoo.addons.ai_assistant.services.action_tools.registry import (
    ToolRegistry,
)


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


class NullableSchemaReadTool(AbstractReadTool):
    name = 'nullable_read'
    description = 'Read dummy data with nullable/enum fields'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': ['string', 'null']},
            'state': {
                'type': ['string', 'null'],
                'enum': ['draft', 'done', None],
            },
            'codes': {
                'type': ['array', 'null'],
                'items': {'type': 'string'},
            },
            'nested': {
                'type': 'object',
                'properties': {
                    'count': {'type': ['integer', 'null']},
                },
            },
        },
        'required': [],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        return {}


class AnyOfReadTool(AbstractReadTool):
    name = 'any_of_read'
    description = 'Read dummy data requiring one of two fields'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 1},
            'code_pattern': {'type': 'string', 'minLength': 1},
        },
        'anyOf': [
            {'required': ['query']},
            {'required': ['code_pattern']},
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        return {}


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

    def test_to_openrouter_tools_sanitizes_nullable_types(self):
        registry = ToolRegistry()
        registry.register(NullableSchemaReadTool())
        tools = registry.to_openrouter_tools(DummyEnv())
        props = tools[0]['function']['parameters']['properties']

        self.assertEqual(props['query']['type'], 'string')
        self.assertTrue(props['query']['nullable'])

        self.assertEqual(props['state']['type'], 'string')
        self.assertTrue(props['state']['nullable'])
        self.assertNotIn(None, props['state']['enum'])

        self.assertEqual(props['codes']['type'], 'array')
        self.assertTrue(props['codes']['nullable'])

        self.assertEqual(
            props['nested']['properties']['count']['type'], 'integer'
        )
        self.assertTrue(props['nested']['properties']['count']['nullable'])

    def test_to_openrouter_tools_does_not_mutate_class_schema(self):
        registry = ToolRegistry()
        registry.register(NullableSchemaReadTool())
        registry.to_openrouter_tools(DummyEnv())

        self.assertEqual(
            NullableSchemaReadTool.parameters_schema['properties']['query'],
            {'type': ['string', 'null']},
        )

    def test_to_openrouter_tools_makes_any_of_branches_self_contained(self):
        registry = ToolRegistry()
        registry.register(AnyOfReadTool())
        tools = registry.to_openrouter_tools(DummyEnv())
        any_of = tools[0]['function']['parameters']['anyOf']

        self.assertEqual(any_of[0]['type'], 'object')
        self.assertEqual(
            any_of[0]['properties'],
            {'query': {'type': 'string', 'minLength': 1}},
        )
        self.assertEqual(any_of[1]['type'], 'object')
        self.assertEqual(
            any_of[1]['properties'],
            {'code_pattern': {'type': 'string', 'minLength': 1}},
        )

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
