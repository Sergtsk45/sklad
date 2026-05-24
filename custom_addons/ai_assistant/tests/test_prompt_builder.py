from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.knowledge_provider_v2 import (
    KnowledgeProviderV2,
)
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
        shown_groups = [g for g in context['user_groups'][:5]]
        for g in shown_groups:
            self.assertIn(g, block)
        self.assertNotIn('group_5', block)

    # --- build_knowledge_block (v1 list format) ---

    def test_build_knowledge_block_with_snippets(self):
        snippets = [
            {
                'topic': 'Создание товара',
                'content': 'Нажмите Создать в меню Товары.',
            },
            {
                'topic': 'Инвентаризация',
                'content': 'Перейдите в раздел Инвентаризация.',
            },
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

    # --- build_knowledge_block (v2 dict format) ---

    def test_build_knowledge_block_v2_format_docs_snippets(self):
        knowledge = {
            'docs_snippets': '## Поступления\n1. Открой Склад → Трансферы.',
            'tech_context': None,
            'term_mapping': {},
        }
        block = self.builder.build_knowledge_block(knowledge)
        self.assertIn('ДОКУМЕНТАЦИЯ', block)
        self.assertIn('Поступления', block)

    def test_build_knowledge_block_v2_format_with_tech_context(self):
        knowledge = {
            'docs_snippets': 'Документация',
            'tech_context': '## stock.picking\n| field | type |',
            'term_mapping': {},
        }
        block = self.builder.build_knowledge_block(knowledge)
        self.assertIn('Структура данных', block)
        self.assertIn('stock.picking', block)

    def test_build_knowledge_block_v2_empty_dict_returns_empty(self):
        block = self.builder.build_knowledge_block({})
        self.assertEqual(block, '')

    # --- build_term_mapping_block ---

    def test_build_term_mapping_block_contains_buttons(self):
        terms = {
            'buttons': {'New': 'Новое', 'Validate': 'Подтвердить'},
            'menu_items': {'Inventory': 'Склад'},
            'removed_in_v19': {'Save': 'нет кнопки Сохранить в v19'},
        }
        block = self.builder.build_term_mapping_block(terms)
        self.assertIn('МАППИНГ ТЕРМИНОВ', block)
        self.assertIn('Новое', block)
        self.assertIn('Подтвердить', block)

    def test_build_term_mapping_block_contains_removed_in_v19(self):
        terms = {
            'buttons': {},
            'removed_in_v19': {'Save': 'Автосохранение, кнопки нет'},
        }
        block = self.builder.build_term_mapping_block(terms)
        self.assertIn('Save', block)
        self.assertIn('Автосохранение', block)

    def test_build_term_mapping_block_empty_returns_empty(self):
        block = self.builder.build_term_mapping_block({})
        self.assertEqual(block, '')

    def test_build_term_mapping_block_none_returns_empty(self):
        block = self.builder.build_term_mapping_block(None)
        self.assertEqual(block, '')

    # --- build_messages (new signature) ---

    def test_build_messages_order_system_history_user(self):
        history = [
            {'role': 'user', 'content': 'Первый вопрос'},
            {'role': 'assistant', 'content': 'Первый ответ'},
        ]
        messages = self.builder.build_messages(
            'Новый вопрос', history, context=None, override='SYSTEM'
        )
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[2]['role'], 'assistant')
        self.assertEqual(messages[-1]['role'], 'user')
        self.assertEqual(messages[-1]['content'], 'Новый вопрос')

    def test_build_messages_empty_history(self):
        messages = self.builder.build_messages(
            'Вопрос', [], context=None, override='SYS'
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')

    def test_build_messages_ignores_unknown_roles(self):
        history = [
            {'role': 'admin', 'content': 'Секрет'},
            {'role': 'user', 'content': 'Привет'},
        ]
        messages = self.builder.build_messages(
            'Вопрос', history, context=None, override='SYS'
        )
        roles = [m['role'] for m in messages]
        self.assertNotIn('admin', roles)

    def test_build_messages_ignores_empty_content(self):
        history = [
            {'role': 'user', 'content': ''},
            {'role': 'assistant', 'content': 'Ответ'},
        ]
        messages = self.builder.build_messages(
            'Вопрос', history, context=None, override='SYS'
        )
        contents = [m['content'] for m in messages]
        self.assertNotIn('', contents)

    def test_build_messages_system_prompt_is_first(self):
        messages = self.builder.build_messages(
            'Q', [], context=None, override='SYSTEM'
        )
        self.assertEqual(messages[0]['role'], 'system')
        self.assertIn('SYSTEM', messages[0]['content'])

    def test_build_messages_user_is_last(self):
        messages = self.builder.build_messages(
            'Мой вопрос', [], context=None, override='SYS'
        )
        self.assertEqual(messages[-1]['role'], 'user')
        self.assertEqual(messages[-1]['content'], 'Мой вопрос')

    # --- System prompt v2 rules ---

    def test_v19_rules_in_system_prompt(self):
        prompt = self.builder.build_system_prompt()
        self.assertIn('Сохранить', prompt)
        self.assertIn('Редактировать', prompt)
        self.assertIn('Новое', prompt)

    def test_system_prompt_contains_no_save_rule(self):
        """System prompt должен объяснять отсутствие кнопки Сохранить."""
        prompt = self.builder.build_system_prompt()
        self.assertIn('НЕТ', prompt.upper() + 'НЕТ')

    # --- term_mapping в промпте ---

    def test_term_mapping_included_in_build_messages(self):
        """term_mapping должен попадать в системный промпт."""
        knowledge = {
            'docs_snippets': '',
            'tech_context': None,
            'term_mapping': {
                'buttons': {'New': 'Новое'},
                'menu_items': {},
                'removed_in_v19': {'Save': 'Нет в v19'},
            },
        }
        messages = self.builder.build_messages(
            'Вопрос', [], context=None, knowledge=knowledge
        )
        system_content = messages[0]['content']
        self.assertIn('Новое', system_content)
        self.assertIn('МАППИНГ ТЕРМИНОВ', system_content)

    def test_knowledge_v2_format_in_build_messages(self):
        """Документация v2 (dict) должна попадать в системный промпт."""
        knowledge = {
            'docs_snippets': 'Инструкция: нажмите Новое.',
            'tech_context': None,
            'term_mapping': {},
        }
        messages = self.builder.build_messages(
            'Как создать товар?', [], context=None, knowledge=knowledge
        )
        system_content = messages[0]['content']
        self.assertIn('ДОКУМЕНТАЦИЯ', system_content)
        self.assertIn('Инструкция', system_content)

    def test_actions_mode_includes_rules(self):
        messages = self.builder.build_messages(
            'Создай PO', [], context=None, mode='actions'
        )
        system_content = messages[0]['content']
        self.assertIn('РЕЖИМ ДЕЙСТВИЙ', system_content)
        self.assertIn('Я создам', system_content)
        self.assertIn('post_chatter_note', system_content)

    def test_navigation_rules_in_consult_and_actions_modes(self):
        consult_messages = self.builder.build_messages(
            'Как посмотреть заказы поставщикам?', [], context=None,
            mode='consult'
        )
        actions_messages = self.builder.build_messages(
            'Открой заказы поставщикам', [], context=None, mode='actions'
        )
        for messages in (consult_messages, actions_messages):
            system_content = messages[0]['content']
            self.assertIn('ПРАВИЛО НАВИГАЦИОННЫХ ССЫЛОК', system_content)
            self.assertIn('get_navigation_link', system_content)
            self.assertIn('НИКОГДА не выдумывай URL', system_content)

    def test_navigation_map_included_in_knowledge_block(self):
        knowledge = KnowledgeProviderV2().get_knowledge(
            'purchase',
            'как посмотреть заказы поставщикам',
            include_technical=False,
        )
        block = self.builder.build_knowledge_block(knowledge)
        self.assertIn('Навигационные ссылки Odoo', block)
        self.assertIn('get_navigation_link', block)
        self.assertIn('Заказы поставщикам', block)

    def test_consult_mode_unchanged(self):
        default_messages = self.builder.build_messages(
            'Вопрос', [], context=None
        )
        consult_messages = self.builder.build_messages(
            'Вопрос', [], context=None, mode='consult'
        )
        self.assertEqual(default_messages, consult_messages)
        self.assertNotIn('РЕЖИМ ДЕЙСТВИЙ', consult_messages[0]['content'])
        self.assertIn(
            'Не обещай выполнить действия автоматически',
            consult_messages[0]['content']
        )

    def test_actions_mode_blocks_inventory_mention(self):
        messages = self.builder.build_messages(
            'Создай приход', [], context=None, mode='actions'
        )
        system_content = messages[0]['content']
        self.assertIn('button_confirm', system_content)
        self.assertIn('button_validate', system_content)
        self.assertIn('state', system_content)
        self.assertIn('инвентаризацию', system_content)
        self.assertNotIn(
            'Не обещай выполнить действия автоматически',
            self.builder.build_safety_rules(mode='actions')
        )

    # --- build_technical_context_block ---

    def test_build_technical_context_block_with_content(self):
        content = '## `purchase.order`\n| field | type |\n|-------|------|\n'
        block = self.builder.build_technical_context_block(content)
        self.assertIn('## Структура данных текущего модуля', block)
        self.assertIn('техническая карта', block)
        self.assertIn('## `purchase.order`', block)
        self.assertIn('| field | type |', block)

    def test_build_technical_context_block_none_returns_empty(self):
        block = self.builder.build_technical_context_block(None)
        self.assertEqual(block, '')

    def test_build_technical_context_block_empty_string_returns_empty(self):
        block = self.builder.build_technical_context_block('')
        self.assertEqual(block, '')
