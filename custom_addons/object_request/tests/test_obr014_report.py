"""
OBR-014: Тесты печатной формы расходной накладной.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestObjectRequestIssuePickingReport(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR014',
            'code': 'TEST-OBR014',
        })
        self.product = self.env['product.product'].create({
            'name': 'Кирпич рядовой OBR014',
            'default_code': 'BRICK-014',
            'type': 'consu',
        })
        self.uom = self.product.uom_id
        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        self.request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.env.user.id,
            'need_date': datetime.date.today(),
        })
        self.line = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Кирпич рядовой',
            'qty_requested': 500.0,
            'qty_to_issue': 300.0,
            'product_id': self.product.id,
            'uom_id': self.uom.id,
            'zone': 'Б',
            'floor': '2',
            'section': 'С2',
            'comment': 'Первая партия',
        })
        self.request.action_in_progress()
        customer_loc = self.env.ref('stock.stock_location_customers')
        wizard = self.env['object.request.issue.wizard'].create({
            'request_id': self.request.id,
            'line_ids': [(6, 0, [self.line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        result = wizard.action_create_issue()
        self.picking = self.env['stock.picking'].browse(result['res_id'])

    def _render_html(self):
        report_name = 'object_request.report_issue_picking'
        html, _ = self.env['ir.actions.report']._render_qweb_html(
            report_name, [self.picking.id]
        )
        return html.decode('utf-8') if isinstance(html, bytes) else html

    def test_report_action_exists(self):
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'object_request.report_issue_picking'),
        ])
        self.assertTrue(report, 'Отчёт должен быть зарегистрирован')
        self.assertEqual(report.model, 'stock.picking')

    def test_report_binding(self):
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'object_request.report_issue_picking'),
        ])
        self.assertTrue(report.binding_model_id)
        self.assertEqual(report.binding_model_id.model, 'stock.picking')

    def test_picking_is_object_request_issue(self):
        self.assertTrue(self.picking.is_object_request_issue)
        self.assertEqual(self.picking.object_request_project_id, self.project)

    def test_report_html_render(self):
        html_str = self._render_html()
        self.assertTrue(html_str)
        self.assertIn(self.picking.name, html_str)
        self.assertIn('Кирпич рядовой OBR014', html_str)

    def test_report_contains_project(self):
        html_str = self._render_html()
        self.assertIn('Тестовый объект OBR014', html_str)

    def test_report_contains_request_link(self):
        html_str = self._render_html()
        self.assertIn(self.request.name, html_str)

    def test_report_contains_signatures(self):
        html_str = self._render_html()
        self.assertIn('Кладовщик', html_str)
        self.assertIn('Получатель', html_str)

    def test_report_contains_zone_floor_section(self):
        html_str = self._render_html()
        self.assertIn('Б', html_str)
        self.assertIn('С2', html_str)
