from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAiAssistantInstall(TransactionCase):
    """Verify the ai_assistant module installs without errors."""

    def test_manifest_has_actions_dependencies(self):
        module = self.env['ir.module.module'].search(
            [('name', '=', 'ai_assistant')]
        )
        dependencies = set(module.dependencies_id.mapped('name'))
        expected = {
            'mail',
            'stock',
            'purchase',
            'object_request',
            'custom_product_search',
        }
        self.assertTrue(
            expected.issubset(dependencies),
            "AI actions dependencies should be declared in manifest"
        )

    def test_module_is_installed(self):
        module = self.env['ir.module.module'].search(
            [('name', '=', 'ai_assistant')]
        )
        self.assertTrue(module, "Module ai_assistant should exist")
        self.assertEqual(
            module.state, 'installed',
            "Module ai_assistant should be in installed state"
        )

    def test_supply_group_is_not_admin(self):
        supply_group = self.env.ref('ai_assistant.group_ai_assistant_supply')
        implied_groups = supply_group.implied_ids
        self.assertIn(
            self.env.ref('ai_assistant.group_ai_assistant_user'),
            implied_groups,
            "Supply group should imply regular AI Assistant user access"
        )
        self.assertIn(
            self.env.ref('purchase.group_purchase_user'),
            implied_groups,
            "Supply group should imply Purchase user access"
        )
        self.assertIn(
            self.env.ref('stock.group_stock_user'),
            implied_groups,
            "Supply group should imply Stock user access"
        )
        self.assertNotIn(
            self.env.ref('base.group_system'),
            implied_groups,
            "Supply group must not imply Odoo administrator rights"
        )

    def test_actions_feature_flag_default_off(self):
        params = self.env['ir.config_parameter']
        self.assertFalse(params.get_param('ai_assistant.actions_enabled'))
        self.assertFalse(params.get_param('ai_assistant.moving_enabled'))
        settings = self.env['res.config.settings'].create({})
        self.assertFalse(settings.ai_assistant_actions_enabled)
        self.assertFalse(settings.ai_assistant_moving_enabled)
        self.assertTrue(settings.ai_assistant_replenishment_enabled)
