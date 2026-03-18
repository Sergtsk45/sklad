import re

from odoo import api, models

_UOM_MAP = {
    'шт': 'шт.', 'шт.': 'шт.', 'штука': 'шт.',
    'штук': 'шт.', 'штуки': 'шт.',
    'кг': 'кг.', 'кг.': 'кг.', 'килограмм': 'кг.',
    'килограммов': 'кг.',
    'м': 'м.', 'м.': 'м.', 'метр': 'м.', 'метров': 'м.',
    'л': 'л.', 'л.': 'л.', 'литр': 'л.', 'литров': 'л.',
    'уп': 'уп.', 'уп.': 'уп.', 'упаковка': 'уп.',
    'упаковок': 'уп.',
    'м2': 'м²', 'кв.м': 'м²', 'кв.м.': 'м²', 'кв м': 'м²',
    'м3': 'м³', 'куб.м': 'м³', 'куб.м.': 'м³', 'куб м': 'м³',
}

_SKIP_ARTICLES = {'', 'none', 'н/а', '-', '—', 'нет', 'n/a'}


class ExcelParser(models.AbstractModel):
    _name = 'object.request.excel.parser'
    _description = 'Сервис парсинга и автосопоставления строк Excel'

    @api.model
    def normalize_uom(self, uom_str):
        if not uom_str:
            return ''
        key = re.sub(r'\s+', ' ', str(uom_str).strip().lower())
        return _UOM_MAP.get(key, str(uom_str).strip())

    @api.model
    def normalize_str(self, s):
        if not s:
            return ''
        return re.sub(r'\s+', ' ', str(s).strip())

    @api.model
    def match_product_by_article(self, supplier_article):
        """Поиск product по артикулу поставщика через product.supplierinfo."""
        article = self.normalize_str(supplier_article)
        if not article or article.lower() in _SKIP_ARTICLES:
            return self.env['product.product'].browse()
        info = self.env['product.supplierinfo'].search(
            [('product_code', '=ilike', article)], limit=1,
        )
        if info and info.product_id:
            return info.product_id
        if info and info.product_tmpl_id:
            return info.product_tmpl_id.product_variant_ids[:1]
        return self.env['product.product'].browse()

    @api.model
    def match_product_by_name(self, name_raw):
        """Поиск product по наименованию: exact, затем ilike."""
        name = self.normalize_str(name_raw)
        if not name:
            return self.env['product.product'].browse()
        Product = self.env['product.product']
        product = Product.search(
            [('name', '=', name), ('active', '=', True)], limit=1,
        )
        if not product:
            product = Product.search(
                [('name', 'ilike', name), ('active', '=', True)], limit=1,
            )
        return product

    @api.model
    def match_vendor_by_name(self, supplier_raw):
        """Поиск res.partner по имени поставщика (ilike, supplier_rank > 0)."""
        name = self.normalize_str(supplier_raw)
        if not name:
            return self.env['res.partner'].browse()
        Partner = self.env['res.partner']
        partner = Partner.search(
            [('name', '=ilike', name), ('supplier_rank', '>', 0)], limit=1,
        )
        if not partner:
            partner = Partner.search(
                [('name', 'ilike', name), ('supplier_rank', '>', 0)], limit=1,
            )
        return partner

    @api.model
    def match_row(self, supplier_article, name_raw, supplier_raw):
        """Комбинированное сопоставление строки Excel.

        Returns:
            dict: product, vendor, matching_required, manual_vendor_required
        """
        product = self.match_product_by_article(supplier_article)
        if not product:
            product = self.match_product_by_name(name_raw)
        vendor = self.match_vendor_by_name(supplier_raw)
        return {
            'product': product,
            'vendor': vendor,
            'matching_required': not bool(product),
            'manual_vendor_required': not bool(vendor),
        }
