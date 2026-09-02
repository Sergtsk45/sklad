# -*- coding: utf-8 -*-
"""
@file: test_purchase_order_list_columns.py
@description: Колонки Объект и Склад в списках закупок.
@dependencies: object_request.models.purchase_order_ext
@created: 2026-08-17
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "or_po_list_cols")
class TestPurchaseOrderListColumns(TransactionCase):
    """Объект и склад видны в списке PO и в истории закупок товара."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["object.request.project"].create(
            {"name": "Объект колонок PO"}
        )
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Поставщик колонок PO", "supplier_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Товар колонок PO",
                "type": "consu",
                "is_storable": True,
                "purchase_ok": True,
            }
        )

    def _create_po(self):
        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.ref("base.user_admin").id,
                "need_date": "2026-08-17",
            }
        )
        self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": self.product.name,
                "product_id": self.product.id,
                "uom_id": self.product.uom_id.id,
                "qty_requested": 2.0,
                "qty_to_buy": 2.0,
                "preferred_vendor_id": self.vendor.id,
            }
        )
        request.write({"state": "in_progress"})
        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=request.id)
            .create({"request_id": request.id})
        )
        result = wizard.action_create_purchase()
        return self.env["purchase.order"].browse(result["res_id"])

    def test_po_dest_warehouse_and_project_related(self):
        po = self._create_po()
        self.assertEqual(po.object_request_project_id, self.project)
        self.assertEqual(po.dest_warehouse_id, self.project.warehouse_id)
        line = po.order_line[:1]
        self.assertEqual(line.object_request_project_id, self.project)
        self.assertEqual(line.dest_warehouse_id, self.project.warehouse_id)

    def _assert_list_has_object_warehouse(self, model, xmlid):
        view = self.env.ref(xmlid)
        arch = model.get_view(view.id, "list")["arch"]
        self.assertIn('name="object_request_project_id"', arch)
        self.assertIn('name="dest_warehouse_id"', arch)
        self.assertIn('string="Объект"', arch)
        self.assertIn('string="Склад"', arch)

    def test_purchase_order_lists_contain_columns(self):
        Order = self.env["purchase.order"]
        self._assert_list_has_object_warehouse(
            Order, "purchase.purchase_order_tree"
        )
        self._assert_list_has_object_warehouse(
            Order, "purchase.purchase_order_kpis_tree"
        )
        self._assert_list_has_object_warehouse(
            Order, "purchase.purchase_order_view_tree"
        )

    def test_product_purchase_history_contains_columns(self):
        self._assert_list_has_object_warehouse(
            self.env["purchase.order.line"],
            "purchase.purchase_history_tree",
        )
