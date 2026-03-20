from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.knowledge_provider import (
    KnowledgeProvider, MAX_SNIPPET_CHARS, MAX_TECH_CONTEXT_CHARS,
)


_SAMPLE_INDEX = {
    'modules': [
        {'module': 'stock', 'file': 'stock.json'},
        {'module': 'crm', 'file': 'crm.json'},
        {'module': 'settings', 'file': 'settings.json'},
    ],
    'fallback_module': 'settings',
}

_STOCK_SNIPPETS = {
    'snippets': [
        {
            'topic': 'Создание товара',
            'content': 'Нажмите Создать в меню Товары.',
            'keywords': ['товар', 'создать', 'продукт'],
        },
        {
            'topic': 'Инвентаризация',
            'content': 'Перейдите в Склад → Операции → Инвентаризация.',
            'keywords': ['инвентаризация', 'остатки', 'склад'],
        },
        {
            'topic': 'Приёмка товаров',
            'content': 'Создайте заявку на приёмку через меню Приёмки.',
            'keywords': ['приёмка', 'поступление', 'склад'],
        },
    ]
}

_SETTINGS_SNIPPETS = {
    'snippets': [
        {
            'topic': 'Общая навигация',
            'content': 'Используйте главное меню для перехода между модулями.',
            'keywords': ['навигация', 'меню', 'модуль'],
        }
    ]
}


def _mock_load(provider, filename):
    data = {
        'stock.json': _STOCK_SNIPPETS,
        'settings.json': _SETTINGS_SNIPPETS,
        'crm.json': {'snippets': []},
    }
    return data.get(filename, {'snippets': []}).get('snippets', [])


@tagged('post_install', '-at_install')
class TestKnowledgeProvider(TransactionCase):

    def setUp(self):
        super().setUp()
        self.provider = KnowledgeProvider()
        self.provider._index = _SAMPLE_INDEX
        self.provider._load_snippets = _mock_load.__get__(
            self.provider, KnowledgeProvider
        )

    # --- get_snippets: relevant results ---

    def test_get_snippets_returns_list(self):
        result = self.provider.get_snippets('stock', 'как создать товар')
        self.assertIsInstance(result, list)

    def test_get_snippets_keyword_match(self):
        result = self.provider.get_snippets('stock', 'создать товар')
        topics = [s['topic'] for s in result]
        self.assertIn('Создание товара', topics)

    def test_get_snippets_ranking_by_keyword(self):
        # 'инвентаризация остатки' should rank inventory higher than creation
        result = self.provider.get_snippets('stock', 'инвентаризация остатки')
        self.assertTrue(result)
        self.assertEqual(result[0]['topic'], 'Инвентаризация')

    def test_get_snippets_limit_respected(self):
        result = self.provider.get_snippets('stock', 'склад', limit=2)
        self.assertLessEqual(len(result), 2)

    def test_get_snippets_unknown_module_falls_back(self):
        result = self.provider.get_snippets('unknown_module', 'навигация')
        self.assertIsInstance(result, list)
        # fallback to settings — should return settings snippets
        topics = [s['topic'] for s in result]
        self.assertIn('Общая навигация', topics)

    def test_get_snippets_no_query_match_returns_fallback_snippets(self):
        # No keyword match → returns up to 3 first snippets
        result = self.provider.get_snippets('stock', 'xyz_no_match_xyz')
        self.assertLessEqual(len(result), 3)

    # --- keyword matching ---

    def test_rank_snippets_exact_keyword_scores_higher(self):
        snippets = [
            {'topic': 'A', 'content': 'text', 'keywords': ['товар']},
            {'topic': 'B', 'content': 'text', 'keywords': ['совсем другое']},
        ]
        ranked = self.provider._rank_snippets(snippets, 'товар')
        self.assertEqual(ranked[0]['topic'], 'A')

    def test_rank_snippets_partial_match_scores(self):
        snippets = [
            {'topic': 'A', 'content': 'text', 'keywords': ['товарооборот']},
            {'topic': 'B', 'content': 'text', 'keywords': ['другое']},
        ]
        ranked = self.provider._rank_snippets(snippets, 'товар')
        self.assertEqual(ranked[0]['topic'], 'A')

    def test_rank_snippets_no_match_returns_all(self):
        snippets = [
            {'topic': str(i), 'content': 'c', 'keywords': []} for i in range(5)
        ]
        ranked = self.provider._rank_snippets(snippets, 'нет совпадений')
        self.assertEqual(len(ranked), 3)  # fallback: first 3

    # --- size limit ---

    def test_apply_size_limit_truncates_large_snippets(self):
        large_content = 'x' * (MAX_SNIPPET_CHARS + 100)
        snippets = [
            {'topic': 'A', 'content': 'short content'},
            {'topic': 'B', 'content': large_content},
            {'topic': 'C', 'content': 'another short'},
        ]
        result = self.provider._apply_size_limit(snippets)
        topics = [s['topic'] for s in result]
        self.assertIn('A', topics)
        self.assertNotIn('B', topics)

    def test_apply_size_limit_empty_list(self):
        result = self.provider._apply_size_limit([])
        self.assertEqual(result, [])

    def test_apply_size_limit_single_snippet_within_budget(self):
        snippets = [{'topic': 'X', 'content': 'small'}]
        result = self.provider._apply_size_limit(snippets)
        self.assertEqual(len(result), 1)

    # --- load_knowledge_index caching ---

    def test_load_knowledge_index_uses_cache(self):
        provider = KnowledgeProvider()
        provider._index = {'modules': [], 'fallback_module': 'settings'}
        index1 = provider.load_knowledge_index()
        index2 = provider.load_knowledge_index()
        self.assertIs(index1, index2)

    # --- module entry search ---

    def test_find_module_entry_found(self):
        entry = self.provider._find_module_entry(_SAMPLE_INDEX, 'stock')
        self.assertIsNotNone(entry)
        self.assertEqual(entry['file'], 'stock.json')

    def test_find_module_entry_not_found_returns_none(self):
        entry = self.provider._find_module_entry(_SAMPLE_INDEX, 'nonexistent')
        self.assertIsNone(entry)

    # --- get_technical_context ---

    def test_get_technical_context_returns_content(self):
        provider = KnowledgeProvider()
        sample = '# Odoo Schema\n## `purchase.order`\n| field | type |\n'
        with patch('builtins.open', MagicMock(
            return_value=MagicMock(
                __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=sample))),
                __exit__=MagicMock(return_value=False),
            )
        )), patch('os.path.isfile', return_value=True):
            result = provider.get_technical_context('purchase')
        self.assertEqual(result, sample)

    def test_get_technical_context_unknown_module_returns_none(self):
        provider = KnowledgeProvider()
        with patch('os.path.isfile', return_value=False):
            result = provider.get_technical_context('nonexistent_module_xyz')
        self.assertIsNone(result)

    def test_get_technical_context_caches_result(self):
        provider = KnowledgeProvider()
        sample = '# Schema\n## `stock.move`\n'
        open_mock = MagicMock(
            return_value=MagicMock(
                __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=sample))),
                __exit__=MagicMock(return_value=False),
            )
        )
        with patch('builtins.open', open_mock), patch('os.path.isfile', return_value=True):
            first = provider.get_technical_context('stock')
            second = provider.get_technical_context('stock')
        self.assertIs(first, second)
        # open() called only once — second call hits cache
        self.assertEqual(open_mock.call_count, 1)

    def test_get_technical_context_truncates_large_content(self):
        provider = KnowledgeProvider()
        large_content = 'x' * (MAX_TECH_CONTEXT_CHARS + 500)
        with patch('builtins.open', MagicMock(
            return_value=MagicMock(
                __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=large_content))),
                __exit__=MagicMock(return_value=False),
            )
        )), patch('os.path.isfile', return_value=True):
            result = provider.get_technical_context('stock')
        self.assertEqual(len(result), MAX_TECH_CONTEXT_CHARS + len('\n...(обрезано)'))
        self.assertTrue(result.endswith('...(обрезано)'))

    def test_get_technical_context_file_not_found_returns_none(self):
        provider = KnowledgeProvider()
        with patch('os.path.isfile', return_value=False):
            result = provider.get_technical_context('sale')
        self.assertIsNone(result)
        # Повторный вызов тоже None — закэшировано
        result2 = provider.get_technical_context('sale')
        self.assertIsNone(result2)
