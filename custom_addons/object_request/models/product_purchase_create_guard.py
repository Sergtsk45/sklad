# -*- coding: utf-8 -*-
"""
@file: product_purchase_create_guard.py
@description: Запрет создания номенклатуры из закупки (нормализация имён).
@dependencies: product, purchase
@created: 2026-08-10
"""

from odoo import api, models
from odoo.exceptions import UserError

_BLOCK_CTX = "block_product_create_from_purchase"

_BLOCK_MSG = (
    "Нельзя создавать карточку товара из закупки: название не проходит "
    "нормализацию. Создайте или найдите товар в «Склад → Товары» "
    "(или через требование на комплектацию), затем выберите его в строке "
    "заказа. Поиск: типоразмер (например «гофрированная Ду20») или "
    "артикул поставщика."
)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def name_create(self, name):
        self._check_block_product_create_from_purchase()
        return super().name_create(name)

    @api.model_create_multi
    def create(self, vals_list):
        self._check_block_product_create_from_purchase()
        return super().create(vals_list)

    @api.model
    def _check_block_product_create_from_purchase(self):
        if self.env.context.get(_BLOCK_CTX):
            raise UserError(_BLOCK_MSG)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_create(self, name):
        self._check_block_product_create_from_purchase()
        return super().name_create(name)

    @api.model_create_multi
    def create(self, vals_list):
        self._check_block_product_create_from_purchase()
        return super().create(vals_list)

    @api.model
    def _check_block_product_create_from_purchase(self):
        if self.env.context.get(_BLOCK_CTX):
            raise UserError(_BLOCK_MSG)
