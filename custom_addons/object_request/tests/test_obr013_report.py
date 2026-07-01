from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestObjectRequestReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR013",
            }
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.user.id,
                "need_date": "2026-04-01",
                "priority": "1",
            }
        )
        self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Кирпич строительный М150",
                "uom_raw": "шт",
                "qty_requested": 1000.0,
                "sequence": 10,
            }
        )
        self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "uom_raw": "кг",
                "qty_requested": 500.0,
                "zone": "А",
                "floor": "1",
                "section": "С1",
                "comment": "Срочно",
                "sequence": 20,
            }
        )

    def test_report_action_exists(self):
        report = self.env["ir.actions.report"].search(
            [
                ("report_name", "=", "object_request.report_object_request"),
            ]
        )
        self.assertTrue(report, "Отчёт должен быть зарегистрирован")
        self.assertEqual(report.model, "object.request")
        self.assertIn("Передаточная ведомость", report.print_report_name)
        self.assertIn("object.name", report.print_report_name)
        self.assertIn(
            "object.project_id.warehouse_id",
            report.print_report_name,
        )

    def test_report_binding(self):
        report = self.env["ir.actions.report"].search(
            [
                ("report_name", "=", "object_request.report_object_request"),
            ]
        )
        self.assertTrue(report.binding_model_id)
        self.assertEqual(report.binding_model_id.model, "object.request")

    def _render_report_html(self):
        report_name = "object_request.report_object_request"
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            report_name, [self.request.id]
        )
        return html.decode("utf-8") if isinstance(html, bytes) else html

    def test_report_html_render(self):
        html_str = self._render_report_html()
        self.assertTrue(html_str)
        self.assertIn(self.request.name, html_str)
        self.assertIn("Тестовый объект OBR013", html_str)
        self.assertIn("Кирпич строительный М150", html_str)
        self.assertIn("Цемент М500", html_str)

    def test_report_contains_signatures_block(self):
        html_str = self._render_report_html()
        self.assertIn("Прораб", html_str)
        self.assertIn("Снабженец", html_str)
        self.assertIn("Согласующий", html_str)

    def test_report_line_zone_floor_section(self):
        html_str = self._render_report_html()
        self.assertIn("А", html_str)
        self.assertIn("С1", html_str)
