"""Web client calls of product search v2 under a stock user."""

from odoo.tests import HttpCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestProductSearchHttp(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env, login='cps_stock_user', groups='stock.group_stock_user',
        )
        cls.bolt = cls.env['product.product'].create({
            'name': 'Болт М16×70 ГОСТ 7798-70 веб-тест',
            'type': 'consu',
        })

    def _call_kw(self, model, method, args, kwargs):
        return self.make_jsonrpc_request(
            f'/web/dataset/call_kw/{model}/{method}',
            {'model': model, 'method': method, 'args': args, 'kwargs': kwargs},
        )

    def test_autocomplete_and_list_filter(self):
        self.authenticate('cps_stock_user', 'cps_stock_user')
        rows = self._call_kw(
            'product.product', 'web_name_search', [],
            {
                'name': 'болт оцинк. М16х70 веб-тест',
                'specification': {'display_name': {}},
                'limit': 8,
            },
        )
        self.assertEqual(rows[0]['id'], self.bolt.id)

        result = self._call_kw(
            'product.product', 'web_search_read', [],
            {
                'domain': [('x_smart_search', 'ilike', 'болт м16 веб-тест')],
                'specification': {'display_name': {}},
            },
        )
        self.assertIn(
            self.bolt.id, [record['id'] for record in result['records']],
        )

    def test_stock_user_edits_synonyms(self):
        self.authenticate('cps_stock_user', 'cps_stock_user')
        self._call_kw(
            'product.search.synonym', 'create',
            [[{'term': 'болтик', 'canonical': 'болт'}]], {},
        )
        rows = self._call_kw(
            'product.product', 'web_name_search', [],
            {
                'name': 'болтик м16х70 веб-тест',
                'specification': {'display_name': {}},
                'limit': 8,
            },
        )
        self.assertEqual(rows[0]['id'], self.bolt.id)
