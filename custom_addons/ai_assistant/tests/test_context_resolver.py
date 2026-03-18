from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.context_resolver import ContextResolver


@tagged('post_install', '-at_install')
class TestContextResolver(TransactionCase):

    def setUp(self):
        super().setUp()
        self.resolver = ContextResolver()

    def test_whitelist_filters_unknown_fields(self):
        raw = {
            'module': 'crm',
            'secret': 'should_be_removed',
            'injected': 'DROP TABLE',
        }
        result = self.resolver.resolve(raw, self.env)
        self.assertIn('module', result)
        self.assertNotIn('secret', result)
        self.assertNotIn('injected', result)

    def test_full_context_passes(self):
        raw = {
            'module': 'stock',
            'action': 'Inventory',
            'model': 'stock.picking',
            'view_type': 'list',
            'url': '#action=stock.action_picking_tree_all',
        }
        result = self.resolver.resolve(raw, self.env)
        self.assertEqual(result['module'], 'stock')
        self.assertEqual(result['model'], 'stock.picking')
        self.assertEqual(result['view_type'], 'list')

    def test_invalid_view_type_cleared(self):
        raw = {'view_type': 'unknown_malicious_type'}
        result = self.resolver.resolve(raw, self.env)
        self.assertEqual(result.get('view_type'), '')

    def test_valid_view_types_accepted(self):
        for vt in ('list', 'form', 'kanban', 'dashboard'):
            raw = {'view_type': vt}
            result = self.resolver.resolve(raw, self.env)
            self.assertEqual(result.get('view_type'), vt)

    def test_lang_injected_from_env(self):
        raw = {}
        result = self.resolver.resolve(raw, self.env)
        self.assertIn('lang', result)
        self.assertTrue(result['lang'])

    def test_lang_from_raw_is_overridden_by_server(self):
        raw = {'lang': 'en_FAKE'}
        result = self.resolver.resolve(raw, self.env)
        self.assertNotEqual(result.get('lang'), 'en_FAKE')

    def test_user_groups_is_list(self):
        raw = {}
        result = self.resolver.resolve(raw, self.env)
        self.assertIn('user_groups', result)
        self.assertIsInstance(result['user_groups'], list)

    def test_empty_context_returns_lang_and_groups(self):
        result = self.resolver.resolve({}, self.env)
        self.assertIn('lang', result)
        self.assertIn('user_groups', result)

    def test_none_context_handled(self):
        result = self.resolver.resolve(None, self.env)
        self.assertIn('lang', result)

    def test_field_length_truncated(self):
        raw = {'module': 'x' * 200, 'action': 'y' * 300, 'url': 'z' * 500}
        result = self.resolver.resolve(raw, self.env)
        self.assertLessEqual(len(result.get('module', '')), 64)
        self.assertLessEqual(len(result.get('action', '')), 128)
        self.assertLessEqual(len(result.get('url', '')), 256)
