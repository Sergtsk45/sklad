from odoo.tests.common import TransactionCase, tagged

from odoo.addons.ai_assistant.services.navigation_helper import (
    NavigationHelper,
)


@tagged('post_install', '-at_install')
class TestNavigationHelper(TransactionCase):

    def setUp(self):
        super().setUp()
        self.helper = NavigationHelper(self.env)

    def test_detects_navigation_question(self):
        self.assertTrue(
            self.helper.is_navigation_question(
                'как посмотреть заказы поставщикам?'
            )
        )
        self.assertTrue(
            self.helper.is_navigation_question(
                'где открыть поступления на складе?'
            )
        )

    def test_skips_entity_search(self):
        self.assertFalse(
            self.helper.is_navigation_question(
                'найди склад Хмельницкого'
            )
        )

    def test_resolve_topic_from_message(self):
        topic = self.helper.resolve_topic(
            'как посмотреть заказы поставщикам?'
        )
        self.assertIn('заказы', topic)

    def test_resolve_topic_zakupku_alias(self):
        topic = self.helper.resolve_topic(
            'как посмотреть заказы на закупку?'
        )
        self.assertEqual(topic, 'заказы на закупку')

    def test_fetch_link_returns_url(self):
        result = self.helper.fetch_link(
            'как посмотреть заказы поставщикам?'
        )
        self.assertTrue(result['url'].startswith('/odoo/'))
        self.assertEqual(result['label'], 'Заказы поставщикам')

    def test_enrich_answer_replaces_none_link(self):
        nav = self.helper.fetch_link(
            'как посмотреть заказы поставщикам?'
        )
        answer = (
            'Перейдите в [Открыть «Заказы на закупку»](None). '
            'Путь: Покупка → Заказы.'
        )
        enriched = self.helper.enrich_answer(answer, nav)
        self.assertNotIn('(None)', enriched)
        self.assertIn(nav['url'], enriched)

    def test_enrich_answer_appends_link_when_missing(self):
        nav = self.helper.fetch_link(
            'как посмотреть заказы поставщикам?'
        )
        enriched = self.helper.enrich_answer('Путь: Покупка → Заказы.', nav)
        self.assertIn(nav['url'], enriched)
