# -*- coding: utf-8 -*-
"""
@file: test_obr040_recent_vendors.py
@description: TD-008 / OBR-040: недавние поставщики в autocomplete.
@dependencies: partner_recent_search, object.request.line
@created: 2026-08-19
"""

from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.object_request.models.partner_recent_search import (
    CTX_RECENT_VENDORS,
    RECENT_VENDOR_LIMIT,
)
from odoo.addons.object_request.models.product_vendor_search import (
    CTX_REQUEST_COMPANY,
)


@tagged("post_install", "-at_install", "obr040")
class TestObr040RecentVendors(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR-040"}
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR-040",
                "login": "foreman_obr040@test.com",
            }
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": "2026-08-20",
            }
        )
        self.unused = self._vendor("AAA Unused OBR-040")
        self.vendor_a = self._vendor("AAA Vendor OBR-040")
        self.vendor_b = self._vendor("MMM Vendor OBR-040")
        self.vendor_c = self._vendor("ZZZ Vendor OBR-040")

    def _vendor(self, name, supplier_rank=1):
        return self.env["res.partner"].create(
            {"name": name, "supplier_rank": supplier_rank}
        )

    def _line(self, vendor):
        return self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": f"Позиция {vendor.name}",
                "qty_requested": 1.0,
                "preferred_vendor_id": vendor.id,
            }
        )

    def _partner(self):
        return self.env["res.partner"].with_context(
            **{
                CTX_RECENT_VENDORS: True,
                CTX_REQUEST_COMPANY: self.request.company_id.id,
            }
        )

    def _ids(self, name="", domain=None, limit=100, **ctx):
        partner = self._partner()
        if ctx:
            partner = partner.with_context(**ctx)
        domain = domain or [
            (
                "id",
                "in",
                [
                    self.unused.id,
                    self.vendor_a.id,
                    self.vendor_b.id,
                    self.vendor_c.id,
                ],
            )
        ]
        return [
            row[0]
            for row in partner.name_search(
                name, domain=domain, operator="ilike", limit=limit
            )
        ]

    def test_empty_search_puts_recent_vendors_first(self):
        self._line(self.vendor_a)
        self._line(self.vendor_b)
        self._line(self.vendor_c)
        ids = self._ids()
        self.assertEqual(
            ids[:3],
            [self.vendor_c.id, self.vendor_b.id, self.vendor_a.id],
        )
        self.assertIn(self.unused.id, ids)
        self.assertGreater(ids.index(self.unused.id), 2)

    def test_later_write_moves_vendor_to_front(self):
        self._line(self.vendor_a)
        self._line(self.vendor_b)
        line_c = self._line(self.vendor_c)
        line_c.write({"preferred_vendor_id": self.vendor_a.id})
        ids = self._ids()
        self.assertEqual(ids[0], self.vendor_a.id)

    def test_typed_search_does_not_boost_recents(self):
        self._line(self.vendor_c)
        ids = self._ids(name="AAA Vendor OBR-040")
        self.assertEqual(ids[0], self.vendor_a.id)
        self.assertNotIn(self.vendor_c.id, ids)

    def test_without_context_keeps_default_order(self):
        self._line(self.vendor_c)
        ids = [
            row[0]
            for row in self.env["res.partner"].name_search(
                "",
                domain=[
                    (
                        "id",
                        "in",
                        [self.unused.id, self.vendor_c.id],
                    )
                ],
                limit=10,
            )
        ]
        self.assertEqual(ids[0], self.unused.id)

    def test_archived_and_non_supplier_are_skipped(self):
        self._line(self.vendor_c)
        customer = self._vendor("Customer OBR-040", supplier_rank=0)
        self._line(customer)
        self.vendor_c.active = False
        ids = self._ids(
            domain=[
                ("supplier_rank", ">", 0),
                (
                    "id",
                    "in",
                    [
                        self.unused.id,
                        self.vendor_a.id,
                        self.vendor_c.id,
                        customer.id,
                    ],
                ),
            ]
        )
        self.assertNotIn(self.vendor_c.id, ids)
        self.assertNotIn(customer.id, ids)

    def test_recent_limit_is_eight(self):
        vendors = [
            self._vendor(f"Recent {index:02d} OBR-040")
            for index in range(10)
        ]
        for vendor in vendors:
            self._line(vendor)
        ids = self._ids(
            domain=[("id", "in", [vendor.id for vendor in vendors])],
            limit=20,
        )
        expected = [vendor.id for vendor in reversed(vendors[-8:])]
        self.assertEqual(ids[:RECENT_VENDOR_LIMIT], expected)
        self.assertEqual(len(ids), 10)

    def test_views_pass_recent_vendors_context(self):
        request_view = self.env.ref(
            "object_request.view_object_request_form"
        )
        root = etree.fromstring(request_view.arch_db)
        fields = root.xpath("//field[@name='preferred_vendor_id']")
        self.assertTrue(fields)
        context = fields[0].get("context") or ""
        self.assertIn(CTX_RECENT_VENDORS, context)

        line_view = self.env.ref(
            "object_request.view_object_request_line_list"
        )
        line_root = etree.fromstring(line_view.arch_db)
        line_fields = line_root.xpath(
            "//field[@name='preferred_vendor_id']"
        )
        line_context = line_fields[0].get("context") or ""
        self.assertIn(CTX_RECENT_VENDORS, line_context)

        wizard_view = self.env.ref(
            "object_request.view_assign_lines_wizard_form"
        )
        wizard_root = etree.fromstring(wizard_view.arch_db)
        vendor_fields = wizard_root.xpath("//field[@name='vendor_id']")
        wizard_context = vendor_fields[0].get("context") or ""
        self.assertIn(CTX_RECENT_VENDORS, wizard_context)
