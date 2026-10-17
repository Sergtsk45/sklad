# -*- coding: utf-8 -*-
"""
@file: product_default_vendor.py
@description: Поставщик по умолчанию для строки требования: основной
    поставщик категории, затем последний поставщик по закупке, затем первая
    строка прайса карточки.
@dependencies: product.category, product.product, purchase.order.line
@created: 2026-10-17
"""

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    or_main_vendor_id = fields.Many2one(
        "res.partner",
        string="Основной поставщик",
        domain="[('supplier_rank', '>', 0)]",
        help=(
            "Подставляется в строки требований для товаров этой категории и "
            "подкатегорий, если поставщик есть в прайсе карточки. Помогает "
            "закупать, например, всю электрику щита у одного поставщика."
        ),
    )

    def _or_effective_main_vendor(self):
        """Основной поставщик категории или ближайшей родительской."""
        category = self[:1]
        while category:
            if category.or_main_vendor_id:
                return category.or_main_vendor_id
            category = category.parent_id
        return self.env["res.partner"]


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _or_default_vendor(self, company):
        """Поставщик по умолчанию для строки требования.

        1. Основной поставщик категории, если он есть в прайсе карточки.
        2. Последний поставщик подтверждённой закупки этого товара.
        3. Первая строка прайса (прежнее поведение).
        """
        self.ensure_one()
        sellers = self.with_company(company)._prepare_sellers()
        main = self.categ_id._or_effective_main_vendor()
        seller_partners = sellers.partner_id.commercial_partner_id
        if main and main.commercial_partner_id in seller_partners:
            return main
        last_line = self.env["purchase.order.line"].sudo().search(
            [
                ("product_id", "=", self.id),
                ("company_id", "=", company.id),
                ("order_id.state", "in", ("purchase", "done")),
            ],
            order="date_order desc, id desc",
            limit=1,
        )
        if last_line:
            return last_line.partner_id
        return sellers[:1].partner_id
