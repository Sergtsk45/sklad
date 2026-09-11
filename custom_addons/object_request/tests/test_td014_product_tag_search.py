# -*- coding: utf-8 -*-
"""TD-014: ручной поиск товара в OR по ``product.tag``."""

from lxml import etree

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.object_request.models.product_vendor_search import (
    CTX_PREFERRED_VENDOR,
    CTX_PRODUCT_TAG_SEARCH,
)


@tagged("post_install", "-at_install", "td014")
class TestTd014ProductTagSearch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tag_waterproof = self.env["product.tag"].create(
            {"name": "Гидроизоляция TD014"}
        )
        self.tag_roll = self.env["product.tag"].create(
            {"name": "Рулонный TD014"}
        )
        self.tag_variant = self.env["product.tag"].create(
            {"name": "Вариантный TD014"}
        )
        self.product_tag_only = self._product(
            "Материал Альфа TD014",
            [self.tag_waterproof, self.tag_roll],
        )
        self.product_one_tag = self._product(
            "Материал Бета TD014",
            [self.tag_waterproof],
        )
        self.product_name_and_tag = self._product(
            "Гидроизоляция именованная TD014",
            [self.tag_waterproof],
        )
        self.product_variant_tag = self._product(
            "Материал Гамма TD014",
        )
        self.product_variant_tag.write(
            {
                "additional_product_tag_ids": [
                    Command.set(self.tag_variant.ids)
                ]
            }
        )

    def _product(self, name, tags=None):
        template = self.env["product.template"].create(
            {
                "name": name,
                "type": "consu",
                "product_tag_ids": [
                    Command.set([tag.id for tag in tags])
                ]
                if tags
                else [],
            }
        )
        return template.product_variant_id

    def _tag_product(self, **extra_context):
        return self.env["product.product"].with_context(
            **{CTX_PRODUCT_TAG_SEARCH: True, **extra_context}
        )

    def _ids(self, query, **kwargs):
        return [
            product_id
            for product_id, _label in self._tag_product().name_search(
                query,
                **kwargs,
            )
        ]

    def test_template_tag_is_found_only_in_or_context(self):
        global_ids = [
            product_id
            for product_id, _label in self.env[
                "product.product"
            ].name_search("гидроизоляция", limit=100)
        ]
        or_ids = self._ids("гидроизоляция", limit=100)

        self.assertNotIn(self.product_tag_only.id, global_ids)
        self.assertIn(self.product_tag_only.id, or_ids)

    def test_variant_tag_is_found(self):
        ids = self._ids("вариантный", limit=100)
        self.assertIn(self.product_variant_tag.id, ids)

    def test_multi_token_query_requires_every_tag_token(self):
        ids = self._ids("гидроизоляция рулонный", limit=100)
        self.assertIn(self.product_tag_only.id, ids)
        self.assertNotIn(self.product_one_tag.id, ids)

    def test_name_results_keep_priority_and_tag_hits_are_not_duplicated(self):
        ids = self._ids("гидроизоляция", limit=100)
        self.assertEqual(ids.count(self.product_name_and_tag.id), 1)
        self.assertLess(
            ids.index(self.product_name_and_tag.id),
            ids.index(self.product_tag_only.id),
        )

    def test_tag_search_respects_domain_and_limit(self):
        domain_ids = self._ids(
            "гидроизоляция",
            domain=[("id", "=", self.product_tag_only.id)],
            limit=100,
        )
        limited_ids = self._ids("гидроизоляция", limit=1)
        unlimited_ids = self._ids("гидроизоляция", limit=0)

        self.assertEqual(domain_ids, [self.product_tag_only.id])
        self.assertEqual(len(limited_ids), 1)
        self.assertIn(self.product_tag_only.id, unlimited_ids)
        self.assertIn(self.product_one_tag.id, unlimited_ids)

    def test_vendor_filter_applies_to_tag_hits_and_keeps_label(self):
        vendor_a = self.env["res.partner"].create(
            {"name": "Vendor A TD014", "supplier_rank": 1}
        )
        vendor_b = self.env["res.partner"].create(
            {"name": "Vendor B TD014", "supplier_rank": 1}
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product_tag_only.product_tmpl_id.id,
                "partner_id": vendor_a.id,
                "price": 10.0,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.product_one_tag.product_tmpl_id.id,
                "partner_id": vendor_b.id,
                "price": 10.0,
            }
        )
        Product = self._tag_product(
            **{CTX_PREFERRED_VENDOR: vendor_a.id}
        )
        rows = Product.name_search("гидроизоляция", limit=100)
        labels = dict(rows)

        self.assertIn(self.product_tag_only.id, labels)
        self.assertNotIn(self.product_one_tag.id, labels)
        self.assertTrue(
            labels[self.product_tag_only.id].endswith(" — Vendor A TD014")
        )

    def test_web_name_search_returns_tag_hit(self):
        rows = self._tag_product().web_name_search(
            "вариантный",
            {"display_name": {}},
            limit=100,
        )
        self.assertIn(self.product_variant_tag.id, [row["id"] for row in rows])

    def test_interactive_or_views_enable_tag_search(self):
        checks = [
            ("object_request.view_object_request_form", "product_id"),
            ("object_request.view_object_request_line_list", "product_id"),
            ("object_request.view_assign_lines_wizard_form", "product_id"),
            (
                "object_request.view_object_request_import_wizard_form",
                "selected_product_id",
            ),
        ]
        for xml_id, field_name in checks:
            root = etree.fromstring(self.env.ref(xml_id).arch_db)
            contexts = [
                field.get("context") or ""
                for field in root.xpath(f"//field[@name='{field_name}']")
            ]
            self.assertTrue(
                any(CTX_PRODUCT_TAG_SEARCH in context for context in contexts),
                f"{xml_id}.{field_name} не включает поиск по тегам",
            )
