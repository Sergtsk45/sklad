from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.action_tools.base import (
    AbstractReadTool,
    AbstractWriteTool,
)
from odoo.addons.ai_assistant.services.action_tools.executor import (
    ToolExecutor,
    ToolRateLimiter,
)
from odoo.addons.ai_assistant.services.action_tools.registry import (
    ToolRegistry,
)
from odoo.addons.ai_assistant.services.action_tools.write_tools import (
    PostChatterNoteTool,
)


class EchoTool(AbstractReadTool):
    name = 'echo_tool'
    description = 'Echo args'
    parameters_schema = {
        'type': 'object',
        'properties': {'value': {'type': 'string'}},
        'required': ['value'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        return {'value': args['value']}


class GroupedWriteTool(AbstractWriteTool):
    name = 'grouped_write_tool'
    description = 'Grouped write'
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {'value': {'type': 'string'}},
        'required': ['value'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        return {'ok': True}

    def idempotency_key(self, args):
        return args['value']


class FailingTool(EchoTool):
    name = 'failing_tool'

    def execute(self, env, args):
        raise ValidationError('Проверочная ошибка')


class ForbiddenConfirmTool(GroupedWriteTool):
    name = 'purchase_order_button_confirm'


@tagged('post_install', '-at_install')
class TestToolExecutorSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supply_user = cls._create_user(
            'executor_supply',
            [
                'ai_assistant.group_ai_assistant_supply',
                'object_request.group_supply_manager',
            ],
        )
        cls.no_ai_user = cls._create_user(
            'executor_no_ai',
            ['object_request.group_supply_manager'],
        )
        cls.project = cls.env['object.request.project'].create({
            'name': 'Executor Object',
        })
        cls.request = cls.env['object.request'].create({
            'project_id': cls.project.id,
            'foreman_user_id': cls.env.user.id,
            'need_date': '2026-06-15',
        })

    @classmethod
    def _create_user(cls, login, group_xmlids):
        groups = [cls.env.ref('base.group_user').id]
        groups += [cls.env.ref(xmlid).id for xmlid in group_xmlids]
        return cls.env['res.users'].create({
            'name': login,
            'login': login,
            'email': '%s@example.invalid' % login,
            'group_ids': [(6, 0, groups)],
        })

    def test_executor_rejects_unknown_tool(self):
        result = ToolExecutor(self.env, registry=ToolRegistry()).execute(
            'missing_tool',
            {},
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'unknown_tool')

    def test_executor_rejects_user_without_group(self):
        registry = ToolRegistry()
        registry.register(GroupedWriteTool())

        result = ToolExecutor(
            self.env(user=self.no_ai_user),
            registry=registry,
        ).execute('grouped_write_tool', {'value': 'x'})

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'access_denied')

    def test_executor_validates_schema(self):
        registry = ToolRegistry()
        registry.register(EchoTool())

        result = ToolExecutor(self.env, registry=registry).execute(
            'echo_tool',
            {'extra': 'x'},
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'invalid_arguments')

    def test_executor_returns_error_envelope_on_exception(self):
        registry = ToolRegistry()
        registry.register(FailingTool())

        result = ToolExecutor(self.env, registry=registry).execute(
            'failing_tool',
            {'value': 'x'},
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'validation_error')

    def test_executor_post_chatter_only_allowed_models(self):
        registry = ToolRegistry()
        registry.register(PostChatterNoteTool())

        result = ToolExecutor(
            self.env(user=self.supply_user),
            registry=registry,
        ).execute('post_chatter_note', {
            'model': 'res.partner',
            'record_id': self.env.user.partner_id.id,
            'body': 'Тест',
        })

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'invalid_arguments')

    def test_executor_blocks_button_confirm_tool_even_if_registered(self):
        registry = ToolRegistry()
        registry.register(ForbiddenConfirmTool())

        result = ToolExecutor(
            self.env(user=self.supply_user),
            registry=registry,
        ).execute('purchase_order_button_confirm', {'value': 'x'})

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'access_denied')

    def test_rate_limit_blocks_after_5_writes(self):
        registry = ToolRegistry()
        registry.register(GroupedWriteTool())
        executor = ToolExecutor(
            self.env(user=self.supply_user),
            registry=registry,
            rate_limiter=ToolRateLimiter(),
        )

        for index in range(5):
            result = executor.execute(
                'grouped_write_tool',
                {'value': 'write-%s' % index},
            )
            self.assertTrue(result['success'])

        result = executor.execute('grouped_write_tool', {'value': 'blocked'})

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'rate_limited')
        self.assertGreater(result['error']['retry_after'], 0)

    def test_audit_records_write_tool_call(self):
        registry = ToolRegistry()
        registry.register(GroupedWriteTool())
        executor = ToolExecutor(
            self.env(user=self.supply_user),
            registry=registry,
            rate_limiter=ToolRateLimiter(),
        )

        result = executor.execute(
            'grouped_write_tool',
            {'value': 'secret-material-name'},
        )

        self.assertTrue(result['success'])
        audit = self.env['ai_assistant.audit'].sudo().search(
            [('tool_name', '=', 'grouped_write_tool')],
            order='id desc',
            limit=1,
        )
        self.assertTrue(audit)
        self.assertEqual(audit.user_id, self.supply_user)
        self.assertEqual(audit.result_status, 'success')
        self.assertIn('value: string', audit.args_summary)
        self.assertNotIn('secret-material-name', audit.args_summary)

    def test_rate_limit_blocks_after_30_reads(self):
        registry = ToolRegistry()
        registry.register(EchoTool())
        executor = ToolExecutor(
            self.env,
            registry=registry,
            rate_limiter=ToolRateLimiter(),
        )

        for index in range(30):
            result = executor.execute(
                'echo_tool',
                {'value': 'read-%s' % index},
            )
            self.assertTrue(result['success'])

        result = executor.execute('echo_tool', {'value': 'blocked'})

        self.assertFalse(result['success'])
        self.assertEqual(result['error']['code'], 'rate_limited')
        self.assertGreater(result['error']['retry_after'], 0)
