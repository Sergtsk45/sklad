"""
OBR-024: Склад больше не задаётся в шапке требования.
"""
import datetime

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObr024Warehouse(TransactionCase):
    """Проверка новой складской схемы: склад объекта + line.stock."""

    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR-024",
            }
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR024",
                "login": "foreman_test_obr024",
                "email": "foreman_obr024@test.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Кирпич OBR024",
                "default_code": "BRICK-024",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.warehouse = (
            self.env["stock.warehouse"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("id", "!=", self.project.warehouse_id.id),
                ],
                limit=1,
            )
            or self.project.warehouse_id
        )
        self.vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик OBR024",
                "supplier_rank": 1,
            }
        )

    def _create_request(self):
        return self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )

    def _add_line(self, request, qty_requested=10.0, vendor=None):
        vals = {
            "request_id": request.id,
            "name_raw": "Кирпич",
            "qty_requested": qty_requested,
            "product_id": self.product.id,
            "uom_id": self.product.uom_id.id,
        }
        if vendor:
            vals["preferred_vendor_id"] = vendor.id
        return self.env["object.request.line"].create(vals)

    def test_request_has_no_header_warehouse_field(self):
        self.assertNotIn("warehouse_id", self.env["object.request"]._fields)
        request = self._create_request()
        self.assertTrue(request.project_id.warehouse_id)

    def test_import_wizard_has_no_warehouse_field(self):
        self.assertNotIn(
            "warehouse_id", self.env["object.request.import.wizard"]._fields
        )
        wizard = self.env["object.request.import.wizard"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": fields.Date.today(),
                "file": b"",
                "file_name": "test.xlsx",
            }
        )
        self.assertTrue(wizard.id)

    def test_check_stock_creates_line_stock_distribution(self):
        request = self._create_request()
        line = self._add_line(request)
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.warehouse.lot_stock_id,
            42.0,
        )

        request.action_check_stock()

        self.assertTrue(line.stock_ids)
        self.assertAlmostEqual(line.stock_qty_on_hand, 42.0)
        stock = line.stock_ids.filtered(
            lambda item: item.warehouse_id == self.warehouse
        )
        self.assertAlmostEqual(stock.qty_on_hand, 42.0)

    def test_issue_preview_groups_by_distribution_warehouse(self):
        request = self._create_request()
        line = self._add_line(request)
        self.env["object.request.line.stock"].with_context(
            auto_stock_distribution=True,
        ).create(
            {
                "line_id": line.id,
                "warehouse_id": self.warehouse.id,
                "qty_on_hand": 5.0,
                "qty_to_issue": 5.0,
            }
        )

        wizard = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(
                default_request_id=request.id,
            )
            .create({})
        )

        self.assertEqual(len(wizard.group_ids), 1)
        self.assertEqual(wizard.group_ids.warehouse_id, self.warehouse)

    def test_purchase_wizard_po_receives_to_project_warehouse(self):
        request = self._create_request()
        line = self._add_line(request, qty_requested=3.0, vendor=self.vendor)
        line.write({"qty_to_buy": 3.0})

        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(
                default_request_id=request.id,
            )
            .create({"request_id": request.id})
        )
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        self.assertEqual(
            po.picking_type_id, self.project.warehouse_id.in_type_id
        )
