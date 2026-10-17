"""Раскладка товаров по категориям магазина и выборочная публикация."""

from odoo import _, api, models

from .shop_catalog_rules import RULES, SECTION_ORDER, match_category_path


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def action_shop_sync_catalog(self):
        """Разложить товары по категориям магазина по правилам.

        Создаёт недостающие категории дерева. Товару, у которого уже есть
        категория магазина, ничего не меняет — ручная раскладка сохраняется.
        Возвращает уведомление со статистикой.
        """
        products = self.with_context(lang='ru_RU').search([
            ('active', '=', True),
            ('type', '!=', 'service'),
        ])
        cache = {}
        assigned = kept = unmatched = 0
        for product in products:
            if product.public_categ_ids:
                kept += 1
                continue
            path = match_category_path(product.name)
            if not path:
                unmatched += 1
                continue
            product.public_categ_ids = self._shop_category(path, cache)
            assigned += 1
        self._shop_resequence()
        message = _(
            'Разложено: %(assigned)s, уже были в категориях: %(kept)s, '
            'не подошло ни одно правило: %(unmatched)s.',
            assigned=assigned, kept=kept, unmatched=unmatched,
        )
        return self._shop_notification(_('Каталог магазина'), message)

    @api.model
    def _shop_category(self, path, cache):
        """Категория магазина по пути, с созданием недостающих уровней."""
        Category = self.env['product.public.category'].with_context(
            lang='ru_RU'
        )
        parent = Category
        for depth in range(1, len(path) + 1):
            key = path[:depth]
            if key not in cache:
                name = key[-1]
                category = Category.search([
                    ('name', '=', name),
                    ('parent_id', '=', parent.id or False),
                ], limit=1)
                sequence = self._shop_sequence(key)
                if not category:
                    category = Category.create({
                        'name': name,
                        'parent_id': parent.id or False,
                        'sequence': sequence,
                    })
                elif category.sequence != sequence:
                    category.sequence = sequence
                cache[key] = category
            parent = cache[key]
        return parent

    @api.model
    def _shop_resequence(self):
        """Обновить порядок уже созданных категорий дерева."""
        Category = self.env['product.public.category'].with_context(
            lang='ru_RU'
        )
        parents = {(): Category}
        for path, _pattern in RULES:
            for depth in range(1, len(path) + 1):
                key = path[:depth]
                parent = parents.get(key[:-1])
                if key in parents or parent is None:
                    continue
                category = Category.search([
                    ('name', '=', key[-1]),
                    ('parent_id', '=', parent.id or False),
                ], limit=1)
                parents[key] = category or None
                sequence = self._shop_sequence(key)
                if category and category.sequence != sequence:
                    category.sequence = sequence

    @api.model
    def _shop_sequence(self, key):
        """Порядок: разделы — по SECTION_ORDER, ниже — как в правилах."""
        if len(key) == 1 and key[0] in SECTION_ORDER:
            return (SECTION_ORDER.index(key[0]) + 1) * 10
        order = []
        for path, _pattern in RULES:
            prefix = path[:len(key)]
            if len(prefix) == len(key) and prefix[:-1] == key[:-1]:
                if prefix not in order:
                    order.append(prefix)
        return (order.index(key) + 1) * 10 if key in order else 100

    def action_shop_publish(self):
        """Опубликовать выбранные товары на сайте."""
        self.write({'is_published': True, 'sale_ok': True})
        return self._shop_notification(
            _('Магазин'), _('Опубликовано: %s.', len(self)),
        )

    def action_shop_unpublish(self):
        """Снять выбранные товары с сайта."""
        self.write({'is_published': False})
        return self._shop_notification(
            _('Магазин'), _('Снято с сайта: %s.', len(self)),
        )

    @api.model
    def _shop_notification(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
