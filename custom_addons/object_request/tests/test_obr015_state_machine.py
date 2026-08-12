from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestStateMachine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тест OBR-015",
            }
        )
        self.user = self.env.user
        self.product = self.env["product.product"].create(
            {
                "name": "Товар OBR-015",
                "type": "consu",
            }
        )

    def _make_request(self):
        return self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.user.id,
                "need_date": "2026-04-01",
            }
        )

    def _add_matched_line(self, request):
        return self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Тестовая позиция",
                "qty_requested": 10.0,
                "product_id": self.product.id,
                "matching_required": False,
            }
        )

    def _add_unmatched_line(self, request):
        return self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Несопоставленная позиция",
                "qty_requested": 5.0,
                "matching_required": True,
            }
        )

    # --- draft → in_progress ---

    def test_in_progress_no_lines_raises(self):
        req = self._make_request()
        with self.assertRaises(UserError):
            req.action_in_progress()

    def test_in_progress_matched_lines_succeeds(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        self.assertEqual(req.state, "in_progress")

    def test_in_progress_unmatched_returns_wizard(self):
        req = self._make_request()
        self._add_unmatched_line(req)
        result = req.action_in_progress()
        self.assertEqual(
            result.get("res_model"), "object.request.confirm.wizard"
        )
        self.assertEqual(req.state, "draft")  # state не изменился

    def test_in_progress_via_wizard(self):
        req = self._make_request()
        self._add_unmatched_line(req)
        result = req.action_in_progress()
        wizard = (
            self.env["object.request.confirm.wizard"]
            .with_context(result["context"])
            .create(
                {
                    "request_id": result["context"]["default_request_id"],
                    "action_type": result["context"]["default_action_type"],
                    "message": result["context"]["default_message"],
                }
            )
        )
        wizard.action_confirm()
        self.assertEqual(req.state, "in_progress")

    # --- in_progress → closed ---

    def test_close_all_supplied_succeeds(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"qty_to_issue": 10.0, "qty_issued": 10.0})
        req.action_close()
        self.assertEqual(req.state, "closed")

    def test_close_unprocessed_returns_wizard(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        # строка в state 'ready', не fully_supplied
        result = req.action_close()
        self.assertEqual(
            result.get("res_model"), "object.request.confirm.wizard"
        )
        self.assertEqual(req.state, "in_progress")

    def test_close_via_wizard(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        result = req.action_close()
        wizard = (
            self.env["object.request.confirm.wizard"]
            .with_context(result["context"])
            .create(
                {
                    "request_id": result["context"]["default_request_id"],
                    "action_type": result["context"]["default_action_type"],
                    "message": result["context"]["default_message"],
                }
            )
        )
        wizard.action_confirm()
        self.assertEqual(req.state, "closed")

    def test_close_cancelled_lines_allowed(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"is_cancelled": True})
        req.action_close()
        self.assertEqual(req.state, "closed")

    # --- draft/in_progress → cancelled ---

    def test_cancel_from_draft(self):
        req = self._make_request()
        req.action_cancel()
        self.assertEqual(req.state, "cancelled")

    def test_cancel_from_in_progress(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        req.action_cancel()
        self.assertEqual(req.state, "cancelled")

    # --- Финальные статусы ---

    def test_closed_is_final(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"is_cancelled": True})
        req.action_close()
        self.assertEqual(req.state, "closed")
        # Нет метода для выхода из closed

    def test_cancelled_is_final(self):
        req = self._make_request()
        req.action_cancel()
        self.assertEqual(req.state, "cancelled")

    # --- Редактируемость: project_id readonly в in_progress ---

    def test_header_fields_editable_in_draft(self):
        req = self._make_request()
        self.assertEqual(req.state, "draft")
        new_project = self.env["object.request.project"].create(
            {
                "name": "Новый объект OBR-015",
            }
        )
        req.write({"project_id": new_project.id})
        self.assertEqual(req.project_id, new_project)

    def test_comment_editable_in_progress(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        req.write({"comment": "Комментарий в работе"})
        self.assertEqual(req.comment, "Комментарий в работе")

    # --- Состав строк: только черновик ---

    def test_draft_allows_line_create_qty_and_unlink(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        line.write({"qty_requested": 12.0})
        self.assertAlmostEqual(line.qty_requested, 12.0)
        line.unlink()
        self.assertFalse(req.line_ids)

    def test_in_progress_forbids_line_create(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        with self.assertRaises(UserError):
            self._add_unmatched_line(req)

    def test_in_progress_forbids_line_unlink(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        with self.assertRaises(UserError):
            line.unlink()
        self.assertTrue(line.exists())

    def test_in_progress_forbids_line_unlink_via_rpc_context(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        with self.assertRaises(UserError):
            line.with_context(object_request_allow_line_unlink=True).unlink()
        self.assertTrue(line.exists())

    def test_in_progress_forbids_qty_requested_change(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        with self.assertRaises(UserError):
            line.write({"qty_requested": 20.0})
        self.assertAlmostEqual(line.qty_requested, 10.0)

    def test_in_progress_allows_same_qty_requested_write(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"qty_requested": 10.0, "qty_to_issue": 4.0})
        self.assertAlmostEqual(line.qty_to_issue, 4.0)

    def test_in_progress_allows_qty_to_issue_change(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"qty_to_issue": 3.0})
        self.assertAlmostEqual(line.qty_to_issue, 3.0)

    def test_closed_forbids_line_create(self):
        req = self._make_request()
        line = self._add_matched_line(req)
        req.action_in_progress()
        line.write({"qty_to_issue": 10.0, "qty_issued": 10.0})
        req.action_close()
        with self.assertRaises(UserError):
            self._add_unmatched_line(req)

    def test_in_progress_request_unlink_still_works(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        req.unlink()
        self.assertFalse(req.exists())

    def test_copy_in_progress_becomes_draft(self):
        req = self._make_request()
        self._add_matched_line(req)
        req.action_in_progress()
        copy = req.copy()
        self.assertEqual(copy.state, "draft")
        self.assertEqual(len(copy.line_ids), 1)

    def test_form_view_locks_line_composition_in_progress(self):
        view = self.env.ref("object_request.view_object_request_form")
        arch = view.arch_db
        self.assertIn("'create': [('state', '=', 'draft')]", arch)
        self.assertIn("'delete': [('state', '=', 'draft')]", arch)
        self.assertNotIn('create="parent.state', arch)
        self.assertNotIn('delete="parent.state', arch)
        self.assertIn('readonly="parent.state != \'draft\'"', arch)
