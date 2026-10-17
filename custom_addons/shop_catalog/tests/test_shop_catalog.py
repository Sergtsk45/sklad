"""Правила раскладки и дерево категорий магазина."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.shop_catalog_rules import match_category_path


@tagged('post_install', '-at_install')
class TestShopCatalog(TransactionCase):

    def test_rules_examples(self):
        cases = {
            'Болт М16×70 ГОСТ 7798-70 оцинкованный': ('Крепёж', 'Болты'),
            'Кран латунный Ду15 В-В рычаг  (1/18)':
                ('Краны шаровые', 'Краны шаровые латунные'),
            'Кран шаровый для манометра Ду15':
                ('Приборы учёта и КИПиА', 'Принадлежности для КИП'),
            'Труба PPR, армированная алюминием, Ду25, PN25':
                ('Трубы PP-R армированные алюминием',),
            'Муфта соединительная PPR Ду25': ('Фитинги PP-R',),
            'Клапан обратный поворотный Ду50 Ру16': ('Клапаны обратные',),
            'Шина N нулевая 8×12 мм, 6 групп':
                ('Шины, клеммы и наконечники',),
            'Пена монтажная огнестойкая B1, 750 мл':
                ('Монтажная пена, клеи, герметики',),
        }
        for name, tail in cases.items():
            with self.subTest(name=name):
                path = match_category_path(name)
                self.assertEqual(path[-len(tail):], tail)

    def test_off_profile_goods_are_not_matched(self):
        self.assertIsNone(match_category_path('Мышь проводная A4Tech'))

    def test_sync_creates_tree_and_keeps_manual_category(self):
        Product = self.env['product.template']
        bolt = Product.create({'name': 'Болт М20×80 ТЕСТ', 'type': 'consu'})
        manual = self.env['product.public.category'].create(
            {'name': 'Ручная категория'}
        )
        valve = Product.create({
            'name': 'Задвижка ТЕСТ Ду80',
            'type': 'consu',
            'public_categ_ids': [(6, 0, manual.ids)],
        })
        Product.action_shop_sync_catalog()
        self.assertEqual(bolt.public_categ_ids.name, 'Болты')
        self.assertEqual(
            bolt.public_categ_ids.parent_id.parent_id.name,
            'Детали трубопроводов, хомуты и крепёж',
        )
        self.assertEqual(valve.public_categ_ids, manual)

    def test_publish_actions(self):
        product = self.env['product.template'].create(
            {'name': 'Отвод ТЕСТ 57×3,5', 'type': 'consu', 'sale_ok': False}
        )
        product.action_shop_publish()
        self.assertTrue(product.is_published and product.sale_ok)
        product.action_shop_unpublish()
        self.assertFalse(product.is_published)
