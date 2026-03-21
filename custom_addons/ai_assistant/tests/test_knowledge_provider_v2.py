"""
AIA-027: Unit-тесты для KnowledgeProviderV2.
Покрывают трёхслойную архитектуру: RST-docs, akaidoo context, term_mapping.
"""
import os
import json
import tempfile

from unittest.mock import patch, mock_open

from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.knowledge_provider_v2 import (
    KnowledgeProviderV2,
    MAX_DOCS_CHARS,
    MAX_TECH_CONTEXT_CHARS,
)

# --- Фиктивный term_mapping ---
_TERM_MAPPING = {
    'odoo_version': '19.0',
    'lang': 'ru_RU',
    'buttons': {'New': 'Новое', 'Validate': 'Подтвердить'},
    'menu_items': {'Inventory': 'Склад'},
    'fields': {'Quantity': 'Количество'},
    'statuses': {'Done': 'Готово'},
    'removed_in_v19': {'Save': 'Нет в v19'},
}

# --- Фиктивные MD-файлы ---
_STOCK_MD = """\
---
module: stock
---

# Управление складом

**Ключевые слова**: склад, поступление, отгрузка, товар

## Поступления

1. Перейдите в **Склад** → **Трансферы**.
2. Нажмите **Новое** для создания поступления.
3. Нажмите **Подтвердить** для завершения.

## Настройка склада

1. Откройте **Конфигурация** → **Склады**.
"""

_CRM_MD = """\
---
module: crm
---

# CRM: работа с лидами

**Ключевые слова**: лид, воронка, клиент, crm

## Создание лида

1. Перейдите в **CRM** → **Лиды**.
2. Нажмите **Новое**.
"""


@tagged('post_install', '-at_install')
class TestKnowledgeProviderV2(TransactionCase):

    def setUp(self):
        super().setUp()
        self.provider = KnowledgeProviderV2()
        # Сбросить кеши
        self.provider._docs_index = None
        self.provider._term_mapping = None
        self.provider._tech_cache = {}

    # ------------------------------------------------------------------
    # Вспомогательный контекст-менеджер — подменяем файловую систему
    # ------------------------------------------------------------------

    def _patch_docs(self, files_dict):
        """
        Подменяем os.path.isdir, os.listdir и open для docs-директории.
        files_dict: {filename: content_str}
        """
        import builtins
        real_open = builtins.open

        def fake_isdir(path):
            # docs/ и generated/ существуют
            return True

        def fake_listdir(path):
            return list(files_dict.keys())

        def fake_open(path, *args, **kwargs):
            fname = os.path.basename(path)
            if fname in files_dict:
                import io
                return io.StringIO(files_dict[fname])
            return real_open(path, *args, **kwargs)

        return (
            patch('odoo.addons.ai_assistant.services.knowledge_provider_v2'
                  '.os.path.isdir', side_effect=fake_isdir),
            patch('odoo.addons.ai_assistant.services.knowledge_provider_v2'
                  '.os.listdir', side_effect=fake_listdir),
            patch('builtins.open', side_effect=fake_open),
        )

    # ------------------------------------------------------------------
    # Тесты term_mapping
    # ------------------------------------------------------------------

    def test_load_term_mapping_returns_dict(self):
        tm_json = json.dumps(_TERM_MAPPING)
        with patch('builtins.open', mock_open(read_data=tm_json)):
            with patch('os.path.isfile', return_value=True):
                tm = self.provider._load_term_mapping()
        self.assertIsInstance(tm, dict)
        self.assertEqual(tm['lang'], 'ru_RU')

    def test_load_term_mapping_missing_file_returns_empty(self):
        with patch('builtins.open', side_effect=FileNotFoundError):
            tm = self.provider._load_term_mapping()
        self.assertEqual(tm, {})

    def test_get_relevant_terms_returns_buttons_and_menu(self):
        self.provider._term_mapping = _TERM_MAPPING
        terms = self.provider._get_relevant_terms('stock')
        self.assertIn('buttons', terms)
        self.assertIn('menu_items', terms)
        self.assertIn('removed_in_v19', terms)
        self.assertEqual(terms['buttons']['New'], 'Новое')

    def test_get_relevant_terms_empty_mapping_returns_empty(self):
        self.provider._term_mapping = {}
        terms = self.provider._get_relevant_terms('stock')
        self.assertEqual(terms, {})

    # ------------------------------------------------------------------
    # Тесты поиска по docs/
    # ------------------------------------------------------------------

    def test_build_docs_index_returns_sections(self):
        """Индекс должен содержать секции из MD-файлов."""
        files = {
            'stock_operations.md': _STOCK_MD,
            'crm_leads.md': _CRM_MD,
        }
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=True
        ), patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.listdir',
            return_value=list(files.keys())
        ):
            import io
            import builtins
            real_open = builtins.open

            def fake_open(path, *a, **kw):
                fname = os.path.basename(path)
                if fname in files:
                    return io.StringIO(files[fname])
                return real_open(path, *a, **kw)

            with patch('builtins.open', side_effect=fake_open):
                index = self.provider._build_docs_index()

        self.assertGreater(len(index), 0)
        modules = {s['module'] for s in index}
        self.assertIn('stock', modules)
        self.assertIn('crm', modules)

    def test_search_docs_returns_relevant_section(self):
        """_search_docs должен вернуть текст о поступлениях при запросе про склад."""
        files = {'stock_operations.md': _STOCK_MD}
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=True
        ), patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.listdir',
            return_value=list(files.keys())
        ):
            import io, builtins
            real_open = builtins.open

            def fake_open(path, *a, **kw):
                fname = os.path.basename(path)
                if fname in files:
                    return io.StringIO(files[fname])
                return real_open(path, *a, **kw)

            with patch('builtins.open', side_effect=fake_open):
                result = self.provider._search_docs('stock', 'поступление товаров')

        self.assertIn('Поступления', result)

    def test_search_docs_respects_max_chars(self):
        """Результат не должен превышать MAX_DOCS_CHARS."""
        long_md = '## Раздел\n' + ('x' * MAX_DOCS_CHARS * 2)
        files = {'stock_large.md': long_md}
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=True
        ), patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.listdir',
            return_value=['stock_large.md']
        ):
            import io, builtins
            real_open = builtins.open

            def fake_open(path, *a, **kw):
                if os.path.basename(path) == 'stock_large.md':
                    return io.StringIO(long_md)
                return real_open(path, *a, **kw)

            with patch('builtins.open', side_effect=fake_open):
                result = self.provider._search_docs('stock', 'запрос')

        self.assertLessEqual(len(result), MAX_DOCS_CHARS + 20)

    def test_search_docs_missing_dir_returns_empty(self):
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=False
        ):
            result = self.provider._search_docs('stock', 'запрос')
        self.assertEqual(result, '')

    def test_module_boost_applied(self):
        """Секции из stock*.md должны получить boost при запросе stock."""
        files = {
            'stock_operations.md': _STOCK_MD,
            'crm_leads.md': _CRM_MD,
        }
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=True
        ), patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.listdir',
            return_value=list(files.keys())
        ):
            import io, builtins
            real_open = builtins.open

            def fake_open(path, *a, **kw):
                fname = os.path.basename(path)
                if fname in files:
                    return io.StringIO(files[fname])
                return real_open(path, *a, **kw)

            with patch('builtins.open', side_effect=fake_open):
                # Нейтральный запрос — boost должен поднять stock
                result = self.provider._search_docs('stock', 'настройка')

        # stock контент должен присутствовать (boost по модулю)
        self.assertIn('Склад', result)

    # ------------------------------------------------------------------
    # Тесты get_technical_context
    # ------------------------------------------------------------------

    def test_get_technical_context_returns_content(self):
        fake_content = '## stock.picking\n| field | type |'
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=fake_content)):
            result = self.provider.get_technical_context('stock')
        self.assertEqual(result, fake_content)

    def test_get_technical_context_missing_returns_none(self):
        with patch('os.path.isfile', return_value=False):
            result = self.provider.get_technical_context('nonexistent_module')
        self.assertIsNone(result)

    def test_get_technical_context_truncated_at_max(self):
        long_content = 'x' * (MAX_TECH_CONTEXT_CHARS + 1000)
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=long_content)):
            result = self.provider.get_technical_context('stock')
        self.assertLessEqual(len(result), MAX_TECH_CONTEXT_CHARS + 20)
        self.assertIn('обрезано', result)

    def test_get_technical_context_cached(self):
        """Повторный вызов должен вернуть из кеша, без обращения к диску."""
        self.provider._tech_cache['stock'] = 'cached content'
        result = self.provider.get_technical_context('stock')
        self.assertEqual(result, 'cached content')

    # ------------------------------------------------------------------
    # Тесты get_knowledge (интеграция)
    # ------------------------------------------------------------------

    def test_get_knowledge_returns_all_layers(self):
        self.provider._term_mapping = _TERM_MAPPING
        with patch('os.path.isfile', return_value=False), \
             patch(
                 'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
                 return_value=False
             ):
            result = self.provider.get_knowledge('stock', 'поступление')
        self.assertIn('docs_snippets', result)
        self.assertIn('tech_context', result)
        self.assertIn('term_mapping', result)

    def test_get_knowledge_no_technical_when_not_requested(self):
        self.provider._term_mapping = _TERM_MAPPING
        self.provider._tech_cache['stock'] = 'some tech'
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=False
        ):
            result = self.provider.get_knowledge(
                'stock', 'запрос', include_technical=False
            )
        self.assertIsNone(result['tech_context'])

    def test_get_knowledge_includes_technical_when_requested(self):
        self.provider._term_mapping = _TERM_MAPPING
        self.provider._tech_cache['stock'] = 'tech context data'
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=False
        ):
            result = self.provider.get_knowledge(
                'stock', 'запрос', include_technical=True
            )
        self.assertEqual(result['tech_context'], 'tech context data')

    # ------------------------------------------------------------------
    # Тесты get_snippets (обратная совместимость)
    # ------------------------------------------------------------------

    def test_get_snippets_returns_list(self):
        files = {'stock_operations.md': _STOCK_MD}
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=True
        ), patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.listdir',
            return_value=['stock_operations.md']
        ):
            import io, builtins
            real_open = builtins.open

            def fake_open(path, *a, **kw):
                if os.path.basename(path) == 'stock_operations.md':
                    return io.StringIO(_STOCK_MD)
                return real_open(path, *a, **kw)

            with patch('builtins.open', side_effect=fake_open):
                result = self.provider.get_snippets('stock', 'поступление')

        self.assertIsInstance(result, list)
        # Каждый элемент — dict с 'content'
        for item in result:
            self.assertIn('content', item)

    def test_get_snippets_empty_when_no_docs(self):
        with patch(
            'odoo.addons.ai_assistant.services.knowledge_provider_v2.os.path.isdir',
            return_value=False
        ):
            result = self.provider.get_snippets('stock', 'запрос')
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # Тесты extract_keywords
    # ------------------------------------------------------------------

    def test_extract_keywords_from_keyword_line(self):
        text = '**Ключевые слова**: склад, поступление, отгрузка'
        kws = self.provider._extract_keywords(text)
        self.assertIn('склад', kws)
        self.assertIn('поступление', kws)

    def test_extract_keywords_from_headers(self):
        text = '## Поступления\n### Детали поступления'
        kws = self.provider._extract_keywords(text)
        self.assertTrue(len(kws) > 0)

    def test_score_section_module_boost(self):
        """Секция из нужного модуля получает boost +2."""
        section_stock = {'text': 'контент', 'filename': 'stock_ops.md',
                         'module': 'stock', 'keywords': []}
        section_crm = {'text': 'контент', 'filename': 'crm_leads.md',
                       'module': 'crm', 'keywords': []}
        score_stock = self.provider._score_section(
            section_stock, 'контент', {'контент'}, 'stock'
        )
        score_crm = self.provider._score_section(
            section_crm, 'контент', {'контент'}, 'stock'
        )
        self.assertGreater(score_stock, score_crm)
