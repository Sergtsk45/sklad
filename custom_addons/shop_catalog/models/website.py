"""Настройки витрины: товары строками, больше строк на странице."""

from odoo import api, models

LIST_LAYOUT = 'o_wsale_products_opt_layout_list'
GRID_LAYOUTS = (
    'o_wsale_products_opt_layout_catalog',
    'o_wsale_products_opt_layout_grid',
)
ROWS_PER_PAGE = 40


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _shop_apply_list_layout(self):
        """Вид «список» (как santech.ru) и русский язык на всех сайтах."""
        for website in self.search([]):
            classes = (website.shop_opt_products_design_classes or '').split()
            classes = [cls for cls in classes if cls not in GRID_LAYOUTS]
            if LIST_LAYOUT not in classes:
                classes.insert(0, LIST_LAYOUT)
            vals = {
                'shop_opt_products_design_classes': ' '.join(classes),
                'shop_ppg': ROWS_PER_PAGE,
            }
            russian = self.env['res.lang']._lang_get('ru_RU')
            if russian:
                vals['language_ids'] = [(4, russian.id)]
                vals['default_lang_id'] = russian.id
            website.write(vals)
