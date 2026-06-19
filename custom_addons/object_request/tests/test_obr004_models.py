from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestObjectRequestProject(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект",
            }
        )

    def test_create_project(self):
        self.assertEqual(self.project.name, "Тестовый объект")
        self.assertTrue(self.project.code)
        self.assertTrue(self.project.code.startswith("O"))
        self.assertTrue(self.project.active)

    def test_request_count(self):
        self.assertEqual(self.project.request_count, 0)

    def test_unique_code_constraint(self):
        manual_project = self.env["object.request.project"].create(
            {
                "name": "Ручной код",
                "code": "O777",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["object.request.project"].create(
                {
                    "name": "Другой объект",
                    "code": manual_project.code,
                }
            )


@tagged("post_install", "-at_install")
class TestObjectRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект",
            }
        )
        self.user = self.env.user
        self.product = self.env["product.product"].create(
            {
                "name": "Тестовый товар",
                "type": "consu",
            }
        )

    def _make_request(self, with_line=False):
        vals = {
            "project_id": self.project.id,
            "foreman_user_id": self.user.id,
            "need_date": "2026-04-01",
        }
        request = self.env["object.request"].create(vals)
        if with_line:
            self.env["object.request.line"].create(
                {
                    "request_id": request.id,
                    "name_raw": "Тестовый материал",
                    "qty_requested": 10.0,
                    "product_id": self.product.id,
                    "matching_required": False,
                }
            )
        return request

    def test_sequence_generated(self):
        request = self._make_request()
        self.assertNotEqual(request.name, "New")
        self.assertTrue(request.name.startswith("OR/"))

    def test_default_state(self):
        request = self._make_request()
        self.assertEqual(request.state, "draft")

    def test_action_in_progress_no_lines(self):
        request = self._make_request(with_line=False)
        with self.assertRaises(UserError):
            request.action_in_progress()

    def test_action_in_progress_with_lines(self):
        request = self._make_request(with_line=True)
        request.action_in_progress()
        self.assertEqual(request.state, "in_progress")

    def test_action_cancel(self):
        request = self._make_request()
        request.action_cancel()
        self.assertEqual(request.state, "cancelled")

    def test_line_count(self):
        request = self._make_request(with_line=True)
        self.assertEqual(request.line_count, 1)

    def test_qty_total_requested(self):
        request = self._make_request(with_line=True)
        self.assertAlmostEqual(request.qty_total_requested, 10.0)

    def test_matching_state_no_lines(self):
        request = self._make_request()
        self.assertEqual(request.matching_state, "all_matched")

    def test_matching_state_requires_mapping(self):
        request = self._make_request()
        self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Несопоставленный материал",
                "qty_requested": 5.0,
                "matching_required": True,
            }
        )
        self.assertEqual(request.matching_state, "requires_mapping")

    def test_matching_state_all_matched(self):
        request = self._make_request()
        self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Материал",
                "qty_requested": 5.0,
                "product_id": self.product.id,
                "matching_required": False,
            }
        )
        self.assertEqual(request.matching_state, "all_matched")

    def test_company_default(self):
        request = self._make_request()
        self.assertEqual(request.company_id, self.env.company)


@tagged("post_install", "-at_install")
class TestObjectRequestLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Объект для строк",
            }
        )
        self.user = self.env.user
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.user.id,
                "need_date": "2026-04-01",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Товар для теста",
                "type": "consu",
            }
        )

    def _make_line(self, **kwargs):
        vals = {
            "request_id": self.request.id,
            "name_raw": "Материал",
            "qty_requested": 10.0,
        }
        vals.update(kwargs)
        return self.env["object.request.line"].create(vals)

    def test_display_name_uses_sequence_and_name_raw(self):
        """display_name читаемый: номер и наименование из файла."""
        line = self._make_line(
            sequence=20,
            name_raw="Кран муфтовый DN20",
            supplier_article="KR-20",
        )
        self.assertEqual(
            line.display_name,
            "#20 [KR-20] Кран муфтовый DN20",
        )

    def test_display_name_falls_back_to_product(self):
        """Без name_raw display_name берёт название товара."""
        line = self._make_line(
            sequence=30,
            name_raw=" ",
            product_id=self.product.id,
        )
        self.assertEqual(line.display_name, "#30 Товар для теста")

    def test_line_state_requires_mapping_no_product(self):
        line = self._make_line()
        self.assertEqual(line.line_state, "requires_mapping")

    def test_line_state_ready_with_product(self):
        line = self._make_line(
            product_id=self.product.id, matching_required=False
        )
        self.assertEqual(line.line_state, "ready")

    def test_line_state_partially_issued(self):
        line = self._make_line(
            product_id=self.product.id,
            matching_required=False,
            qty_to_issue=10.0,
            qty_issued=5.0,
        )
        self.assertEqual(line.line_state, "partially_issued")

    def test_line_state_fully_supplied(self):
        line = self._make_line(
            product_id=self.product.id,
            matching_required=False,
            qty_to_issue=10.0,
            qty_issued=10.0,
        )
        self.assertEqual(line.line_state, "fully_supplied")

    def test_line_state_cancelled(self):
        line = self._make_line(is_cancelled=True)
        self.assertEqual(line.line_state, "cancelled")

    def test_qty_constraint_sum_exceeds(self):
        with self.assertRaises(ValidationError):
            self._make_line(qty_to_issue=6.0, qty_to_buy=5.0)

    def test_qty_constraint_exact_sum_ok(self):
        ln = self._make_line(qty_to_issue=4.0, qty_to_buy=6.0)
        self.assertAlmostEqual(ln.qty_to_issue + ln.qty_to_buy, 10.0)

    def test_has_substitutes_false(self):
        line = self._make_line()
        self.assertFalse(line.has_substitutes)

    def test_has_substitutes_true(self):
        sub = self.env["product.product"].create(
            {
                "name": "Замена",
                "type": "consu",
            }
        )
        line = self._make_line(allowed_substitute_ids=[(6, 0, [sub.id])])
        self.assertTrue(line.has_substitutes)

    def test_is_fully_matched(self):
        line = self._make_line(
            product_id=self.product.id, matching_required=False
        )
        self.assertTrue(line.is_fully_matched)

    def test_is_fully_matched_false_no_product(self):
        line = self._make_line()
        self.assertFalse(line.is_fully_matched)

    def test_cascade_delete(self):
        self._make_line()
        request_id = self.request.id
        self.request.unlink()
        lines = self.env["object.request.line"].search(
            [("request_id", "=", request_id)]
        )
        self.assertEqual(len(lines), 0)
