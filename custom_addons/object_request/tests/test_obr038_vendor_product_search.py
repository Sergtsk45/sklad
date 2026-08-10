# -*- coding: utf-8 -*-
"""
OBR-038: поиск товара в OR с учётом preferred_vendor_id.
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.object_request.models.product_vendor_search import (
    CTX_PREFERRED_VENDOR,
)


@tagged("post_install", "-at_install")
class TestObr038VendorProductSearch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.vendor_a = self.env["res.partner"].create(
            {
                "name": "Vendor A OR038",
                "supplier_rank": 1,
            }
        )
        self.vendor_b = self.env["res.partner"].create(
            {
                "name": "Vendor B OR038",
                "supplier_rank": 1,
            }
        )
        self.product_a = self.env["product.product"].create(
            {
                "name": "Пена монтажная огнестойкая B1, 750 мл OR038",
                "type": "consu",
            }
        )
        self.product_b = self.env["product.product"].create(
            {
                "name": "Пена монтажная KUDO огнестойкая OR038",
                "type": "consu",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "partner_id": self.vendor_a.id,
                "product_name": (
                    "Пена монтажная проф. ПРОТИВОПОЖАРНАЯ B1 65 "
                    "1000/750гр, арт. 337/900"
                ),
                "product_code": "ЦБ-00075997-OR038",
                "price": 614.75,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product_b.product_tmpl_id.id,
                "partner_id": self.vendor_b.id,
                "product_name": "Пена KUDO Proff 45+ огнестойкая",
                "product_code": "KUDO-OR038",
                "price": 1000.0,
            }
        )

    def test_without_vendor_searches_normalized_name(self):
        ids = [
            pid
            for pid, _label in self.env["product.product"].name_search(
                "пена монтажная",
                limit=50,
            )
        ]
        self.assertIn(self.product_a.id, ids)
        self.assertIn(self.product_b.id, ids)

    def test_with_vendor_filters_to_seller_catalog(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        ids = [pid for pid, _label in Product.name_search("пена", limit=50)]
        self.assertIn(self.product_a.id, ids)
        self.assertNotIn(self.product_b.id, ids)

    def test_with_vendor_finds_trade_name(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        results = Product.name_search("ПРОТИВОПОЖАРНАЯ", limit=20)
        ids = [pid for pid, _label in results]
        self.assertIn(self.product_a.id, ids)
        labels = {pid: label for pid, label in results}
        self.assertIn("ПРОТИВОПОЖАРНАЯ", labels[self.product_a.id])

    def test_with_vendor_finds_supplier_code(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        ids = [
            pid
            for pid, _label in Product.name_search(
                "ЦБ-00075997-OR038",
                limit=20,
            )
        ]
        self.assertIn(self.product_a.id, ids)
