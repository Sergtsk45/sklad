from odoo.tests.common import TransactionCase, tagged

from odoo.addons.ai_assistant.services.warehouse_stock_link_helper import (
    WarehouseStockLinkHelper,
)


@tagged('post_install', '-at_install')
class TestWarehouseStockLinkHelper(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('code', '=', 'O002')],
            limit=1,
        )
        if not cls.warehouse:
            cls.warehouse = cls.env['stock.warehouse'].create({
                'name': 'Б. Хмельницкого, 112',
                'code': 'O002',
            })

    def setUp(self):
        super().setUp()
        self.helper = WarehouseStockLinkHelper(self.env)

    def test_detects_stock_link_request(self):
        self.assertTrue(
            self.helper.is_stock_link_request(
                'дай ссылку на фильтр товаров по складу'
            )
        )
        self.assertTrue(
            self.helper.is_stock_link_request(
                'что есть на этом складе'
            )
        )

    def test_fetch_link_from_history(self):
        history = [{
            'role': 'assistant',
            'content': (
                'Найдено: Склад Б. Хмельницкого, 112 (O002).'
            ),
        }]
        result = self.helper.fetch_link(
            'дай ссылку на фильтр товаров по складу',
            history,
        )
        self.assertTrue(result['url'].startswith('/odoo/ai-warehouse-stock?'))
        self.assertIn('O002', result['label'])

    def test_enrich_answer_replaces_none(self):
        result = self.helper.fetch_link(
            'что есть на складе ОбМ-4',
        )
        answer = 'Откройте [Отчёт](None).'
        enriched = self.helper.enrich_answer(answer, result)
        self.assertNotIn('(None)', enriched)
        self.assertIn('ai-warehouse-stock', enriched)
