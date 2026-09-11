# -*- coding: utf-8 -*-
"""OBR-039: ручная отметка «Счёт запрошен» и статус ожидания счёта."""

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _make_user(env, name, login, group):
    return env["res.users"].create(
        {
            "name": name,
            "login": login,
            "group_ids": [(4, group.id)],
        }
    )


@tagged("post_install", "-at_install", "obr039")
class TestObr039LineWaitInvoice(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR-039"}
        )
        self.vendor = self.env["res.partner"].create(
            {"name": "Поставщик OBR-039", "supplier_rank": 1}
        )
        self.vendor_b = self.env["res.partner"].create(
            {"name": "Поставщик B OBR-039", "supplier_rank": 1}
        )
        self.product = self.env["product.product"].create(
            {"name": "Товар OBR-039", "type": "consu"}
        )
        self.product_b = self.env["product.product"].create(
            {"name": "Товар B OBR-039", "type": "consu"}
        )
        self.supply = _make_user(
            self.env,
            "Снабженец OBR-039",
            "supply_obr039@test.com",
            self.env.ref("object_request.group_supply_manager"),
        )
        self.foreman = _make_user(
            self.env,
            "Прораб OBR-039",
            "foreman_obr039@test.com",
            self.env.ref("object_request.group_foreman"),
        )
        self.storekeeper = _make_user(
            self.env,
            "Кладовщик OBR-039",
            "store_obr039@test.com",
            self.env.ref("object_request.group_storekeeper"),
        )
        self.approver = _make_user(
            self.env,
            "Согласующий OBR-039",
            "approver_obr039@test.com",
            self.env.ref("object_request.group_approver"),
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": "2026-08-20",
            }
        )

    def _line(self, **vals):
        defaults = {
            "request_id": self.request.id,
            "name_raw": "Позиция OBR-039",
            "qty_requested": 10.0,
        }
        defaults.update(vals)
        return self.env["object.request.line"].create(defaults)

    def _mark(self, line, **vals):
        payload = {"supplier_invoice_requested": True}
        payload.update(vals)
        line.with_user(self.supply).write(payload)
        return line

    def test_product_vendor_checkbox_sets_awaiting(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_no_product_checkbox_sets_awaiting(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            matching_required=True,
        )
        self._mark(line)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_matching_required_checkbox_sets_awaiting(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=True,
        )
        self._mark(line)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_uncheck_without_product_returns_requires_mapping(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.with_user(self.supply).write(
            {"supplier_invoice_requested": False}
        )
        self.assertEqual(line.line_state, "requires_mapping")

    def test_uncheck_with_product_returns_ready(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.with_user(self.supply).write(
            {"supplier_invoice_requested": False}
        )
        self.assertEqual(line.line_state, "ready")

    def test_uncheck_partial_returns_partially_issued(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
            qty_issued=3.0,
        )
        self._mark(line)
        line.with_user(self.supply).write(
            {"supplier_invoice_requested": False}
        )
        self.assertEqual(line.line_state, "partially_issued")

    def test_without_checkbox_requires_mapping_stays_red(self):
        line = self._line(matching_required=True)
        self.assertEqual(line.line_state, "requires_mapping")

    def test_fully_supplied_wins_over_awaiting(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.write({"qty_issued": 10.0})
        self.assertEqual(line.line_state, "fully_supplied")
        self.assertTrue(line.supplier_invoice_requested)

    def test_cancelled_wins_over_awaiting(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"is_cancelled": True})
        self.assertEqual(line.line_state, "cancelled")

    def test_partial_with_checkbox_stays_awaiting(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
            qty_issued=4.0,
            qty_to_issue=4.0,
            qty_to_buy=6.0,
        )
        self._mark(line)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_cannot_mark_without_vendor(self):
        line = self._line(product_id=self.product.id)
        with self.assertRaises(UserError):
            self._mark(line)

    def test_can_mark_without_product(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        self.assertTrue(line.supplier_invoice_requested)

    def test_cannot_mark_cancelled(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            is_cancelled=True,
        )
        with self.assertRaises(UserError):
            self._mark(line)

    def test_cannot_mark_fully_supplied(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
            qty_issued=10.0,
        )
        with self.assertRaises(UserError):
            self._mark(line)

    def test_cannot_mark_closed_document(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self.request.write({"state": "closed"})
        with self.assertRaises(UserError):
            self._mark(line)

    def test_can_mark_pending_approval(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self.request.write({"approval_state": "pending"})
        self._mark(line)
        self.assertTrue(line.supplier_invoice_requested)

    def test_can_mark_without_qty_to_buy(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            qty_to_buy=0.0,
        )
        self._mark(line)
        self.assertTrue(line.supplier_invoice_requested)

    def test_can_unmark_after_fully_supplied(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.write({"qty_issued": 10.0})
        line.with_user(self.supply).write(
            {"supplier_invoice_requested": False}
        )
        self.assertFalse(line.supplier_invoice_requested)

    def test_same_true_write_skips_validation(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"qty_issued": 10.0})
        line.with_user(self.supply).write(
            {"supplier_invoice_requested": True}
        )
        self.assertTrue(line.supplier_invoice_requested)

    def test_vendor_replace_resets(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"preferred_vendor_id": self.vendor_b.id})
        self.assertFalse(line.supplier_invoice_requested)

    def test_vendor_clear_resets(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"preferred_vendor_id": False})
        self.assertFalse(line.supplier_invoice_requested)

    def test_first_vendor_fill_does_not_set_flag(self):
        line = self._line()
        line.write({"preferred_vendor_id": self.vendor.id})
        self.assertFalse(line.supplier_invoice_requested)

    def test_product_replace_resets(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.write({"product_id": self.product_b.id})
        self.assertFalse(line.supplier_invoice_requested)

    def test_product_clear_resets(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.write({"product_id": False})
        self.assertFalse(line.supplier_invoice_requested)

    def test_first_product_fill_keeps_flag(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"product_id": self.product.id})
        self.assertTrue(line.supplier_invoice_requested)

    def test_same_product_id_keeps_flag(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.write({"product_id": self.product.id, "qty_to_buy": 2.0})
        self.assertTrue(line.supplier_invoice_requested)

    def test_qty_change_keeps_flag(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.write({"qty_to_issue": 3.0, "qty_to_buy": 7.0})
        self.assertTrue(line.supplier_invoice_requested)

    def test_multi_write_resets_only_replaced_product(self):
        marked = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
            name_raw="С товаром",
        )
        empty = self._line(
            preferred_vendor_id=self.vendor.id,
            name_raw="Без товара",
        )
        same = self._line(
            product_id=self.product_b.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
            name_raw="Уже B",
        )
        self._mark(marked)
        self._mark(empty)
        self._mark(same)
        (marked | empty | same).write({"product_id": self.product_b.id})
        self.assertFalse(marked.supplier_invoice_requested)
        self.assertTrue(empty.supplier_invoice_requested)
        self.assertTrue(same.supplier_invoice_requested)

    def test_explicit_true_with_new_vendor_keeps_flag(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        line.with_user(self.supply).write(
            {
                "preferred_vendor_id": self.vendor_b.id,
                "supplier_invoice_requested": True,
            }
        )
        self.assertTrue(line.supplier_invoice_requested)
        self.assertEqual(line.preferred_vendor_id, self.vendor_b)

    def test_onchange_product_replace_clears_flag(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        wizard = line.new(
            {
                "product_id": self.product_b.id,
                "supplier_invoice_requested": True,
            },
            origin=line,
        )
        wizard._onchange_product_id()
        self.assertFalse(wizard.supplier_invoice_requested)

    def test_onchange_first_product_keeps_flag(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        wizard = line.new(
            {
                "product_id": self.product.id,
                "supplier_invoice_requested": True,
            },
            origin=line,
        )
        wizard._onchange_product_id()
        self.assertTrue(wizard.supplier_invoice_requested)

    def test_onchange_clear_product_clears_flag(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        wizard = line.new(
            {
                "product_id": False,
                "supplier_invoice_requested": True,
            },
            origin=line,
        )
        wizard._onchange_product_id()
        self.assertFalse(wizard.supplier_invoice_requested)

    def test_onchange_vendor_replace_clears_flag(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        wizard = line.new(
            {
                "preferred_vendor_id": self.vendor_b.id,
                "supplier_invoice_requested": True,
            },
            origin=line,
        )
        wizard._onchange_preferred_vendor_id()
        self.assertFalse(wizard.supplier_invoice_requested)

    def test_foreman_cannot_mark(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        with self.assertRaises(UserError):
            line.with_user(self.foreman).write(
                {"supplier_invoice_requested": True}
            )

    def test_storekeeper_cannot_mark(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        with self.assertRaises(UserError):
            line.with_user(self.storekeeper).write(
                {"supplier_invoice_requested": True}
            )

    def test_approver_cannot_mark(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        with self.assertRaises(UserError):
            line.with_user(self.approver).write(
                {"supplier_invoice_requested": True}
            )

    def test_foreman_cannot_keep_flag_when_changing_vendor(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        with self.assertRaises(UserError):
            line.with_user(self.foreman).write(
                {
                    "preferred_vendor_id": self.vendor_b.id,
                    "supplier_invoice_requested": True,
                }
            )
        self.assertEqual(line.preferred_vendor_id, self.vendor)
        self.assertTrue(line.supplier_invoice_requested)

    def test_superuser_can_mark(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        line.write({"supplier_invoice_requested": True})
        self.assertTrue(line.supplier_invoice_requested)

    def test_foreman_product_replace_resets_without_rights_error(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            matching_required=False,
        )
        self._mark(line)
        line.with_user(self.foreman).write({"product_id": self.product_b.id})
        self.assertFalse(line.supplier_invoice_requested)

    def test_problem_count_excludes_awaiting(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            matching_required=True,
        )
        self.request.invalidate_recordset(["line_problem_count"])
        self.assertEqual(self.request.line_problem_count, 1)
        self._mark(line)
        self.request.invalidate_recordset(["line_problem_count"])
        self.assertEqual(self.request.line_problem_count, 0)

    def test_problem_action_excludes_awaiting(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            matching_required=True,
        )
        self._mark(line)
        action = self.request.action_open_problem_lines()
        self.assertIn(
            ("supplier_invoice_requested", "=", False),
            action["domain"],
        )
        found = self.env["object.request.line"].search(action["domain"])
        self.assertNotIn(line, found)

    def test_requires_nomenclature_review_unchanged(self):
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            matching_required=True,
        )
        self._mark(line)
        self.assertTrue(line._requires_nomenclature_review())

    def test_xml_views_have_awaiting_decorations_and_filter(self):
        form = self.env.ref("object_request.view_object_request_form").arch_db
        lines = self.env.ref(
            "object_request.view_object_request_line_list"
        ).arch_db
        search = self.env.ref(
            "object_request.view_object_request_line_search"
        ).arch_db
        self.assertIn("awaiting_supplier_invoice", form)
        self.assertIn("supplier_invoice_requested", form)
        self.assertIn("group_supply_manager", form)
        self.assertIn("awaiting_supplier_invoice", lines)
        self.assertIn('readonly="1"', lines)
        self.assertIn("filter_awaiting_supplier_invoice", search)
        self.assertIn("supplier_invoice_requested", search)
        danger = (
            "matching_required == True and "
            "line_state != 'awaiting_supplier_invoice'"
        )
        self.assertIn(danger, form)
        self.assertIn(danger, lines)

    def test_import_default_false(self):
        line = self._line()
        self.assertFalse(line.supplier_invoice_requested)

    def test_create_with_true_requires_vendor(self):
        with self.assertRaises(UserError):
            self._line(supplier_invoice_requested=True)
        line = self._line(
            preferred_vendor_id=self.vendor.id,
            supplier_invoice_requested=True,
        )
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_multi_write_resets_only_replaced_vendor(self):
        marked = self._line(preferred_vendor_id=self.vendor.id)
        empty = self._line()
        same = self._line(preferred_vendor_id=self.vendor_b.id)
        self._mark(marked)
        self._mark(same)
        (marked | empty | same).write(
            {"preferred_vendor_id": self.vendor_b.id}
        )
        self.assertFalse(marked.supplier_invoice_requested)
        self.assertFalse(empty.supplier_invoice_requested)
        self.assertTrue(same.supplier_invoice_requested)

    def test_purchase_wizard_includes_awaiting_line(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
            qty_to_buy=10.0,
        )
        self._mark(line)
        self.request.write({"state": "in_progress"})
        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=self.request.id)
            .create({"request_id": self.request.id})
        )
        self.assertIn(line, wizard.line_ids)
        result = wizard.action_create_purchase()
        self.assertEqual(result["res_model"], "purchase.order")
        self.assertTrue(line.supplier_invoice_requested)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_stock_check_and_auto_split_keep_flag(self):
        line = self._line(
            product_id=self.product.id,
            preferred_vendor_id=self.vendor.id,
        )
        self._mark(line)
        self.request.action_check_stock()
        self.assertTrue(line.supplier_invoice_requested)
        self.request.action_auto_split()
        self.assertTrue(line.supplier_invoice_requested)
        self.assertEqual(line.line_state, "awaiting_supplier_invoice")

    def test_close_confirms_unfinished_awaiting_line(self):
        line = self._line(preferred_vendor_id=self.vendor.id)
        self._mark(line)
        self.request.write({"state": "in_progress"})
        result = self.request.action_close()
        self.assertEqual(result["res_model"], "object.request.confirm.wizard")
        self.assertIn("1 строк", result["context"]["default_message"])
        self.assertNotEqual(self.request.state, "closed")
