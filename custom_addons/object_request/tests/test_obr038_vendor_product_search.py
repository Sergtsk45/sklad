# -*- coding: utf-8 -*-
"""
OBR-038: поиск товара в OR с учётом preferred_vendor_id.
"""

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.object_request.models.product_vendor_search import (
    CTX_PREFERRED_VENDOR,
    CTX_REQUEST_COMPANY,
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

    def _create_variant_template(self, suffix):
        attribute = self.env["product.attribute"].create(
            {"name": f"Цвет OR038 {suffix}"}
        )
        values = self.env["product.attribute.value"].create(
            [
                {
                    "name": f"Красный {suffix}",
                    "attribute_id": attribute.id,
                },
                {
                    "name": f"Синий {suffix}",
                    "attribute_id": attribute.id,
                },
            ]
        )
        template = self.env["product.template"].create(
            {
                "name": f"Краска огнестойкая OR038 {suffix}",
                "type": "consu",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(values.ids)],
                        }
                    )
                ],
            }
        )
        self.assertEqual(len(template.product_variant_ids), 2)
        return template, template.product_variant_ids.sorted("id")

    def _create_request_line(self, product, vendor):
        project = self.env["object.request.project"].create(
            {"name": f"Проект onchange OR038 {product.id}"}
        )
        request = self.env["object.request"].create(
            {
                "project_id": project.id,
                "foreman_user_id": self.env.user.id,
                "need_date": fields.Date.today(),
            }
        )
        vals = {
            "request_id": request.id,
            "name_raw": "Материал onchange OR038",
            "qty_requested": 1.0,
            "product_id": product.id,
        }
        if vendor:
            vals["preferred_vendor_id"] = vendor.id
        return self.env["object.request.line"].create(vals)

    def test_without_vendor_searches_normalized_name(self):
        results = self.env["product.product"].name_search(
            "пена монтажная",
            limit=50,
        )
        ids = [pid for pid, _label in results]
        self.assertIn(self.product_a.id, ids)
        self.assertIn(self.product_b.id, ids)
        labels = {pid: label for pid, label in results}
        self.assertFalse(
            labels[self.product_a.id].startswith("[Vendor A OR038] ")
        )

    def test_with_vendor_filters_to_seller_catalog(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        results = Product.name_search("пена", limit=50)
        ids = [pid for pid, _label in results]
        self.assertIn(self.product_a.id, ids)
        self.assertNotIn(self.product_b.id, ids)
        labels = {pid: label for pid, label in results}
        self.assertTrue(
            labels[self.product_a.id].startswith("[Vendor A OR038] ")
        )

    def test_with_vendor_finds_trade_name(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        results = Product.name_search("ПРОТИВОПОЖАРНАЯ", limit=20)
        ids = [pid for pid, _label in results]
        self.assertIn(self.product_a.id, ids)
        labels = {pid: label for pid, label in results}
        self.assertTrue(
            labels[self.product_a.id].startswith("[Vendor A OR038] ")
        )
        self.assertIn(
            " — Пена монтажная проф. ПРОТИВОПОЖАРНАЯ B1 65 ",
            labels[self.product_a.id],
        )

    def test_web_name_search_keeps_vendor_prefix_and_trade_name(self):
        self.product_a.default_code = "DEFAULT-CODE-OR038"
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        rows = Product.web_name_search(
            "ПРОТИВОПОЖАРНАЯ",
            {"display_name": {}},
            limit=20,
        )

        row = next(item for item in rows if item["id"] == self.product_a.id)
        self.assertEqual(
            row["display_name"],
            "[DEFAULT-CODE-OR038] "
            "Пена монтажная огнестойкая B1, 750 мл OR038",
        )
        self.assertTrue(
            row["__formatted_display_name"].startswith("[Vendor A OR038] ")
        )
        self.assertIn(
            "\t--DEFAULT-CODE-OR038--",
            row["__formatted_display_name"],
        )
        self.assertIn(
            " — Пена монтажная проф. ПРОТИВОПОЖАРНАЯ B1 65 ",
            row["__formatted_display_name"],
        )
        self.assertFalse(row["display_name"].startswith("[Vendor A OR038] "))

    def test_web_name_search_extended_specification_is_decorated(self):
        self.product_a.default_code = "EXTENDED-CODE-OR038"
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        rows = Product.web_name_search(
            "ПРОТИВОПОЖАРНАЯ",
            {"display_name": {}, "default_code": {}},
            limit=20,
        )

        row = next(item for item in rows if item["id"] == self.product_a.id)
        self.assertEqual(row["default_code"], "EXTENDED-CODE-OR038")
        self.assertFalse(row["display_name"].startswith("[Vendor A OR038] "))
        self.assertTrue(
            row["__formatted_display_name"].startswith("[Vendor A OR038] ")
        )
        self.assertIn(
            "\t--EXTENDED-CODE-OR038--",
            row["__formatted_display_name"],
        )
        self.assertIn(
            " — Пена монтажная проф. ПРОТИВОПОЖАРНАЯ B1 65 ",
            row["__formatted_display_name"],
        )

    def test_web_name_search_without_display_name_does_not_decorate(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        rows = Product.web_name_search(
            "ПРОТИВОПОЖАРНАЯ",
            {"default_code": {}},
            limit=20,
        )

        row = next(item for item in rows if item["id"] == self.product_a.id)
        self.assertNotIn("display_name", row)
        self.assertNotIn("__formatted_display_name", row)

    def test_with_vendor_empty_search_prefixes_all_results(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        results = Product.name_search("", limit=50)

        labels = {pid: label for pid, label in results}
        self.assertIn(self.product_a.id, labels)
        self.assertTrue(
            labels[self.product_a.id].startswith("[Vendor A OR038] ")
        )

    def test_with_vendor_limit_early_return_prefixes_results_once(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        results = Product.name_search("пена", limit=1)

        self.assertEqual(len(results), 1)
        _product_id, label = results[0]
        self.assertTrue(label.startswith("[Vendor A OR038] "))
        self.assertFalse(
            label.startswith("[Vendor A OR038] [Vendor A OR038] ")
        )

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

    def test_supplier_code_from_another_vendor_does_not_leak(self):
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "partner_id": self.vendor_b.id,
                "product_code": "ONLY-VENDOR-B-OR038",
                "price": 900.0,
            }
        )
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        ids = [
            product_id
            for product_id, _label in Product.name_search(
                "ONLY-VENDOR-B-OR038", limit=20
            )
        ]
        self.assertNotIn(self.product_a.id, ids)

    def test_zero_limit_keeps_odoo_unlimited_semantics(self):
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: self.vendor_a.id}
        )
        ids = [
            product_id
            for product_id, _label in Product.name_search("пена", limit=0)
        ]
        self.assertIn(self.product_a.id, ids)
        self.assertNotIn(self.product_b.id, ids)

    def test_variant_price_returns_only_its_variant(self):
        template, variants = self._create_variant_template("specific")
        vendor = self.env["res.partner"].create(
            {"name": "Variant Vendor OR038", "supplier_rank": 1}
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": template.id,
                "product_id": variants[0].id,
                "partner_id": vendor.id,
                "product_name": "Торговая краска VARIANT-OR038",
                "price": 10.0,
            }
        )
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: vendor.id}
        )

        trade_ids = [
            product_id
            for product_id, _label in Product.name_search(
                "VARIANT-OR038", limit=20
            )
        ]
        normal_ids = [
            product_id
            for product_id, _label in Product.name_search(
                "Краска огнестойкая", limit=20
            )
        ]

        self.assertEqual(trade_ids, variants[0].ids)
        self.assertEqual(normal_ids, variants[0].ids)

    def test_template_price_returns_all_variants(self):
        template, variants = self._create_variant_template("global")
        vendor = self.env["res.partner"].create(
            {"name": "Global Vendor OR038", "supplier_rank": 1}
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": template.id,
                "partner_id": vendor.id,
                "product_name": "Торговая краска GLOBAL-OR038",
                "price": 10.0,
            }
        )
        Product = self.env["product.product"].with_context(
            **{CTX_PREFERRED_VENDOR: vendor.id}
        )
        ids = {
            product_id
            for product_id, _label in Product.name_search(
                "GLOBAL-OR038", limit=20
            )
        }
        self.assertEqual(ids, set(variants.ids))

    def test_supplierinfo_from_other_company_is_ignored(self):
        other_company = self.env["res.company"].create(
            {"name": "Other Company OR038"}
        )
        product = self.env["product.product"].create(
            {"name": "Изоляция межфирменная OR038", "type": "consu"}
        )
        self.env["product.supplierinfo"].sudo().create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "partner_id": self.vendor_a.id,
                "company_id": other_company.id,
                "product_name": "Чужая компания COMPANY-OR038",
                "price": 10.0,
            }
        )
        Product = self.env["product.product"].with_context(
            allowed_company_ids=[self.env.company.id, other_company.id],
            **{
                CTX_PREFERRED_VENDOR: self.vendor_a.id,
                CTX_REQUEST_COMPANY: self.env.company.id,
            },
        )
        ids = [
            product_id
            for product_id, _label in Product.name_search(
                "COMPANY-OR038", limit=20
            )
        ]
        self.assertNotIn(product.id, ids)

    def test_vendor_onchange_clears_incompatible_product(self):
        line = self._create_request_line(self.product_a, self.vendor_b)
        line.uom_id = self.product_a.uom_id
        line.matching_required = False
        line.matching_state = "matched"
        line.matching_source = "manual"
        result = line._onchange_preferred_vendor_id()
        self.assertFalse(line.product_id)
        self.assertFalse(line.uom_id)
        self.assertTrue(line.matching_required)
        self.assertEqual(line.matching_state, "requires_mapping")
        self.assertEqual(line.matching_source, "unknown")
        self.assertEqual(result["warning"]["title"], "Товар очищен")
        self.assertIn("отсутствует в прайсе", result["warning"]["message"])

    def test_vendor_onchange_keeps_compatible_product(self):
        line = self._create_request_line(self.product_a, self.vendor_a)
        line._onchange_preferred_vendor_id()
        self.assertEqual(line.product_id, self.product_a)

    def test_vendor_onchange_respects_variant_specific_price(self):
        template, variants = self._create_variant_template("onchange")
        vendor = self.env["res.partner"].create(
            {"name": "Onchange Vendor OR038", "supplier_rank": 1}
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": template.id,
                "product_id": variants[0].id,
                "partner_id": vendor.id,
                "price": 10.0,
            }
        )
        matching_line = self._create_request_line(variants[0], vendor)
        other_line = self._create_request_line(variants[1], vendor)

        matching_line._onchange_preferred_vendor_id()
        other_line._onchange_preferred_vendor_id()

        self.assertEqual(matching_line.product_id, variants[0])
        self.assertFalse(other_line.product_id)

    def test_product_onchange_does_not_suggest_other_variant_vendor(self):
        template, variants = self._create_variant_template("suggest")
        vendor = self.env["res.partner"].create(
            {"name": "Suggest Vendor OR038", "supplier_rank": 1}
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": template.id,
                "product_id": variants[0].id,
                "partner_id": vendor.id,
                "price": 10.0,
            }
        )
        line = self._create_request_line(variants[1], False)

        line._onchange_product_id()

        self.assertFalse(line.preferred_vendor_id)
