from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAiAssistantInstall(TransactionCase):
    """Verify the ai_assistant module installs without errors."""

    def test_module_is_installed(self):
        module = self.env['ir.module.module'].search(
            [('name', '=', 'ai_assistant')]
        )
        self.assertTrue(module, "Module ai_assistant should exist")
        self.assertEqual(
            module.state, 'installed',
            "Module ai_assistant should be in installed state"
        )
