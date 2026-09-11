# -*- coding: utf-8 -*-
"""
@file: test_product_purchase_create_guard.py
@description: Запрет создания товара из контекста закупки.
@dependencies: object_request.models.product_purchase_create_guard
@created: 2026-08-10
"""

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProductPurchaseCreateGuard(TransactionCase):
    """Нельзя name_create/create товар с block_product_create_from_purchase."""

    def test_name_create_blocked_with_purchase_context(self):
        Product = self.env["product.product"].with_context(
            block_product_create_from_purchase=True
        )
        with self.assertRaises(UserError) as err:
            Product.name_create("Случайное имя из счёта")
        self.assertIn("Нельзя создавать карточку", str(err.exception))

    def test_create_blocked_with_purchase_context(self):
        Product = self.env["product.product"].with_context(
            block_product_create_from_purchase=True
        )
        with self.assertRaises(UserError):
            Product.create({"name": "Ещё один товар из PO", "type": "consu"})

    def test_create_allowed_without_purchase_context(self):
        product = self.env["product.product"].create(
            {
                "name": "Труба гофрированная ПВХ Ду25, серая, бухта 100 м",
                "type": "consu",
                "is_storable": True,
                "purchase_ok": True,
            }
        )
        self.assertTrue(product.id)

    def test_purchase_form_product_id_has_no_create(self):
        view = self.env.ref(
            "object_request.view_purchase_order_inherit_object_request"
        )
        arch = view.arch_db or ""
        self.assertIn("no_create", arch)
        self.assertIn("block_product_create_from_purchase", arch)
