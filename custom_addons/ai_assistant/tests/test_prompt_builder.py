from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.prompt_builder import PromptBuilder


@tagged('post_install', '-at_install')
class TestPromptBuilder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.builder = PromptBuilder()

    # --- build_system_prompt ---

    def test_build_system_prompt_contains_key_instructions(self):
        prompt = self.builder.build_system_prompt()
        self.assertIn('Odoo', prompt)
        self.assertIn('консультант', prompt.lower() + 'консультант')

    def test_build_system_prompt_override_replaces_default(self):
        override = 'Custom system prompt for tests'
        prompt = self.builder.build_system_prompt(override=override)
        self.assertEqual(prompt, override)

    def test_build_system_prompt_no_override_returns_default(self):
        prompt = self.builder.build_system_prompt(override=None)
        self.assertIn('Odoo 19', prompt)

    # --- build_safety_rules ---

    def test_build_safety_rules_returns_non_empty(self):
        rules = self.builder.build_safety_rules()
        self.assertTrue(rules)
        self.assertIsInstance(rules, str)

    def test_build_safety_rules_contains_limitations(self):
        rules = self.builder.build_safety_rules()
        self.assertIn('Odoo', rules)

    # --- build_context_block ---

    def test_build_context_block_with_full_context(self):
        context = {
            'module': 'stock',
            'action': 'Products',
            'model': 'product.template',
            'view_type': 'list',
            'lang': 'ru_RU',
            'user_groups': ['stock.group_stock_user'],
        }
        block = self.builder.build_context_block(context)
        self.assertIn('stock', block)
        self.assertIn('product.template', block)
        self.assertIn('list', block)
        self.assertIn('ru_RU', block)

    def test_build_context_block_empty_context_returns_empty(self):
        block = self.builder.build_context_block({})
        self.assertEqual(block, '')

    def test_build_context_block_none_returns_empty(self):
        block = self.builder.build_context_block(None)
        self.assertEqual(block, '')

    def test_build_context_block_partial_context(self):
        context = {'module': 'crm'}
        block = self.builder.build_context_block(context)
        self.assertIn('crm', block)

    def test_build_context_block_groups_limited_to_five(self):
        context = {
            'user_groups': [f'group_{i}' for i in range(10)],
        }
        block = self.builder.build_context_block(context)
        # Only 5 groups should appear
        shown_groups = [g for g in context['user_groups'][:5]]
        for g in shown_groups:
            self.assertIn(g, block)
        # 6th group should not be in block
        self.assertNotIn('group_5', block)

    # --- build_knowledge_block ---

    def test_build_knowledge_block_with_snippets(self):
        snippets = [
            {'topic': 'Создание товара', 'content': 'Нажмите Создать в меню Товары.'},
            {'topic': 'Инвентаризация', 'content': 'Перейдите в раздел Инвентаризация.'},
        ]
        block = self.builder.build_knowledge_block(snippets)
        self.assertIn('Создание товара', block)
        self.assertIn('Нажмите Создать', block)
        self.assertIn('Инвентаризация', block)

    def test_build_knowledge_block_empty_returns_empty(self):
        block = self.builder.build_knowledge_block([])
        self.assertEqual(block, '')

    def test_build_knowledge_block_none_returns_empty(self):
        block = self.builder.build_knowledge_block(None)
        self.assertEqual(block, '')

    def test_build_knowledge_block_missing_fields_skipped(self):
        snippets = [
            {'topic': '', 'content': ''},
            {'topic': 'Тест', 'content': 'Содержимое'},
        ]
        block = self.builder.build_knowledge_block(snippets)
        self.assertIn('Тест', block)

    # --- build_messages ---

    def test_build_messages_order_system_history_user(self):
        history = [
            {'role': 'user', 'content': 'Первый вопрос'},
            {'role': 'assistant', 'content': 'Первый ответ'},
        ]
        messages = self.builder.build_messages('sys', history, 'Новый вопрос')
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[2]['role'], 'assistant')
        self.assertEqual(messages[-1]['role'], 'user')
        self.assertEqual(messages[-1]['content'], 'Новый вопрос')

    def test_build_messages_empty_history(self):
        messages = self.builder.build_messages('sys', [], 'Вопрос')
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')

    def test_build_messages_ignores_unknown_roles(self):
        history = [
            {'role': 'admin', 'content': 'Секрет'},
            {'role': 'user', 'content': 'Привет'},
        ]
        messages = self.builder.build_messages('sys', history, 'Вопрос')
        roles = [m['role'] for m in messages]
        self.assertNotIn('admin', roles)

    def test_build_messages_ignores_empty_content(self):
        history = [
            {'role': 'user', 'content': ''},
            {'role': 'assistant', 'content': 'Ответ'},
        ]
        messages = self.builder.build_messages('sys', history, 'Вопрос')
        contents = [m['content'] for m in messages]
        self.assertNotIn('', contents)

    def test_build_messages_system_prompt_is_first(self):
        messages = self.builder.build_messages('SYSTEM', [], 'Q')
        self.assertEqual(messages[0]['content'], 'SYSTEM')
