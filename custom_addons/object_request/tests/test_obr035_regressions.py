import base64
import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "obr035")
class TestObr035Regressions(TransactionCase):
    """Регрессии по workflow, распределению и импорту."""

    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR-035"}
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR035",
                "login": "foreman_test_obr035",
                "email": "foreman_obr035@test.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Товар OBR035",
                "default_code": "OBR035-ITEM",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id), ("active", "=", True)],
            limit=2,
        )
        self.warehouse1 = warehouses[:1]
        self.warehouse2 = (
            warehouses[1]
            if len(warehouses) > 1
            else self._create_warehouse("B")
        )

    def _create_warehouse(self, suffix):
        return self.env["stock.warehouse"].sudo().create(
            {
                "name": f"Склад OBR035-{suffix}",
                "code": f"35{suffix}",
                "company_id": self.env.company.id,
            }
        )

    def _create_request(self, state="draft"):
        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
                "issue_warehouse_ids": [
                    (6, 0, [self.warehouse1.id, self.warehouse2.id])
                ],
            }
        )
        if state != "draft":
            request.write({"state": state})
        return request

    def _add_line(self, request, qty=2.0, product=None):
        product = product or self.product
        return self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": product.name,
                "qty_requested": qty,
                "product_id": product.id,
                "uom_id": product.uom_id.id,
            }
        )

    def _add_stock(self, line, warehouse, qty_on_hand, qty_to_issue=0.0):
        return (
            self.env["object.request.line.stock"]
            .with_context(auto_stock_distribution=True)
            .create(
                {
                    "line_id": line.id,
                    "warehouse_id": warehouse.id,
                    "qty_on_hand": qty_on_hand,
                    "qty_to_issue": qty_to_issue,
                }
            )
        )

    def test_auto_issue_max_does_not_allocate_same_stock_twice(self):
        request = self._create_request()
        line1 = self._add_line(request, qty=2.0)
        line2 = self._add_line(request, qty=2.0)
        request.write({"state": "in_progress"})
        self._add_stock(line1, self.warehouse1, 2.0)
        self._add_stock(line2, self.warehouse1, 2.0)

        request.action_lines_issue_max()

        self.assertAlmostEqual(
            sum(request.line_ids.mapped("stock_ids").mapped("qty_to_issue")),
            2.0,
        )
        self.assertAlmostEqual(line1.qty_to_issue + line2.qty_to_issue, 2.0)
        self.assertAlmostEqual(line1.qty_to_buy + line2.qty_to_buy, 2.0)

    def test_manual_distribution_cannot_exceed_product_warehouse_stock(self):
        request = self._create_request()
        line1 = self._add_line(request, qty=2.0)
        line2 = self._add_line(request, qty=2.0)
        request.write({"state": "in_progress"})
        stock1 = self._add_stock(line1, self.warehouse1, 2.0)
        stock2 = self._add_stock(line2, self.warehouse1, 2.0)

        stock1.write({"qty_to_issue": 2.0})
        stock2.write({"qty_to_issue": 2.0})

        with self.assertRaises(ValidationError):
            request.action_open_issue_wizard()

    def test_stock_check_keeps_excluded_warehouse_rows(self):
        request = self._create_request()
        line = self._add_line(request, qty=5.0)
        self._add_stock(line, self.warehouse1, 5.0)
        request.write(
            {
                "issue_warehouse_ids": [
                    (6, 0, [self.warehouse1.id, self.warehouse2.id])
                ],
            }
        )
        request.action_check_stock()
        self.assertTrue(
            line.stock_ids.filtered(
                lambda stock: stock.warehouse_id == self.warehouse1
            )
        )

        request.write({"issue_warehouse_ids": [(6, 0, [self.warehouse2.id])]})
        request.action_check_stock()

        self.assertTrue(
            line.stock_ids.filtered(
                lambda stock: stock.warehouse_id == self.warehouse1
            )
        )

    def test_issue_cannot_be_created_twice_for_same_stock_lines(self):
        request = self._create_request()
        line = self._add_line(request, qty=2.0)
        request.write({"state": "in_progress"})
        self._add_stock(line, self.warehouse1, 2.0, qty_to_issue=2.0)

        wizard = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(default_request_id=request.id)
            .create({})
        )
        wizard.action_create_issues()

        second = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(default_request_id=request.id)
            .create({})
        )
        with self.assertRaises(UserError):
            second.action_create_issues()

    def test_purchase_cannot_be_created_twice_for_same_lines(self):
        vendor = self.env["res.partner"].create(
            {"name": "Поставщик OBR035", "supplier_rank": 1}
        )
        request = self._create_request()
        line = self._add_line(request, qty=2.0)
        request.write({"state": "in_progress"})
        line.write({"qty_to_buy": 2.0, "preferred_vendor_id": vendor.id})

        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=request.id)
            .create({"request_id": request.id})
        )
        wizard.action_create_purchase()

        second = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=request.id)
            .create({"request_id": request.id})
        )
        with self.assertRaises(UserError):
            second.action_create_purchase()

    def test_import_duplicate_file_checksum_is_blocked(self):
        file_data = base64.b64encode(b"same workbook bytes")
        vals = {
            "file": file_data,
            "file_name": "same.xlsx",
            "project_id": self.project.id,
            "foreman_user_id": self.foreman.id,
            "need_date": datetime.date.today(),
            "validation_state": "valid",
            "preview_line_ids": [
                (
                    0,
                    0,
                    {
                        "sequence": 1,
                        "source_row_no": 2,
                        "name_raw": "Товар из файла",
                        "qty": 1.0,
                        "match_status": "unmatched",
                        "matching_required": True,
                    },
                )
            ],
        }
        self.env["object.request.import.wizard"].create(vals).action_import()

        with self.assertRaises(UserError):
            self.env["object.request.import.wizard"].create(
                vals
            ).action_import()

    def test_action_open_lines_sets_column_layout_scope(self):
        """Smart-button «Строки» передаёт scope для раскладки колонок."""
        request = self._create_request()
        self._add_line(request)

        action = request.action_open_lines()

        self.assertEqual(action["res_model"], "object.request.line")
        self.assertEqual(
            action["context"].get("object_request_column_layout_scope"),
            "request_action_lines",
        )

    def test_only_assigned_approver_can_approve(self):
        approver_group = self.env.ref("object_request.group_approver")
        user_group = self.env.ref("base.group_user")
        approver = self.env["res.users"].create(
            {
                "name": "Approver OBR035",
                "login": "approver_test_obr035",
                "email": "approver_obr035@test.com",
                "group_ids": [(6, 0, [user_group.id, approver_group.id])],
            }
        )
        other = self.env["res.users"].create(
            {
                "name": "Other Approver OBR035",
                "login": "other_approver_test_obr035",
                "email": "other_approver_obr035@test.com",
                "group_ids": [(6, 0, [user_group.id, approver_group.id])],
            }
        )
        request = self._create_request()
        request.write(
            {
                "approver_user_id": approver.id,
                "approval_state": "pending",
            }
        )

        with self.assertRaises(UserError):
            request.with_user(other).action_approve()
        request.with_user(approver).action_approve()
        self.assertEqual(request.approval_state, "approved")
