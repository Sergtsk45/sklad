from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestOBR023Reports(TransactionCase):
    """OBR-023: Отчёты и аналитика."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.project1 = cls.env['object.request.project'].create({
            'name': 'Объект Аналитика 1',
        })
        cls.project2 = cls.env['object.request.project'].create({
            'name': 'Объект Аналитика 2',
        })
        cls.user = cls.env.ref('base.user_admin')
        cls.product = cls.env['product.product'].create({
            'name': 'Товар аналитика',
            'type': 'consu',
        })

        today = date.today()
        cls.past_date = (today - timedelta(days=5)).isoformat()
        cls.future_date = (today + timedelta(days=10)).isoformat()

    def _create_request(self, project, need_date, state='draft'):
        req = self.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': self.user.id,
            'need_date': need_date,
        })
        self.env['object.request.line'].create({
            'request_id': req.id,
            'name_raw': 'Тест',
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
            'qty_requested': 3.0,
        })
        if state == 'in_progress':
            req.write({'state': 'in_progress'})
        elif state == 'closed':
            req.write({'state': 'in_progress'})
            req.write({'state': 'closed'})
        return req

    # --- Тесты аналитических views ---

    def test_pivot_view_exists(self):
        """Pivot view для object.request зарегистрирован."""
        view = self.env.ref(
            'object_request.view_object_request_pivot',
            raise_if_not_found=False,
        )
        self.assertTrue(view, 'Pivot view не найден')
        self.assertEqual(view.type, 'pivot')

    def test_graph_view_exists(self):
        """Graph view для object.request зарегистрирован."""
        view = self.env.ref(
            'object_request.view_object_request_graph',
            raise_if_not_found=False,
        )
        self.assertTrue(view, 'Graph view не найден')
        self.assertEqual(view.type, 'graph')

    def test_line_pivot_view_exists(self):
        """Pivot view для object.request.line зарегистрирован."""
        view = self.env.ref(
            'object_request.view_object_request_line_pivot',
            raise_if_not_found=False,
        )
        self.assertTrue(view, 'Pivot view строк не найден')
        self.assertEqual(view.type, 'pivot')

    def test_analytics_action_exists(self):
        """Action «Аналитика требований» существует."""
        action = self.env.ref(
            'object_request.action_object_request_analytics',
            raise_if_not_found=False,
        )
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'object.request')

    def test_overdue_action_exists(self):
        """Action «Просроченные требования» существует."""
        action = self.env.ref(
            'object_request.action_object_request_overdue',
            raise_if_not_found=False,
        )
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'object.request')

    def test_matching_action_exists(self):
        """Action «Статистика сопоставления» существует."""
        action = self.env.ref(
            'object_request.action_object_request_line_matching',
            raise_if_not_found=False,
        )
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'object.request.line')

    # --- Тесты данных для overdue ---

    def test_overdue_domain_finds_past_requests(self):
        """Требования с прошедшей need_date и in_progress — просроченные."""
        req = self._create_request(
            self.project1, self.past_date, 'in_progress'
        )
        overdue = self.env['object.request'].search([
            ('need_date', '<', date.today().isoformat()),
            ('state', 'in', ['draft', 'in_progress']),
        ])
        self.assertIn(req, overdue)

    def test_overdue_domain_excludes_future(self):
        """Требования с будущей датой — не просроченные."""
        req = self._create_request(
            self.project1, self.future_date, 'in_progress'
        )
        overdue = self.env['object.request'].search([
            ('need_date', '<', date.today().isoformat()),
            ('state', 'in', ['draft', 'in_progress']),
        ])
        self.assertNotIn(req, overdue)

    def test_overdue_domain_excludes_closed(self):
        """Закрытые требования не попадают в просроченные."""
        req = self._create_request(self.project1, self.past_date, 'closed')
        overdue = self.env['object.request'].search([
            ('need_date', '<', date.today().isoformat()),
            ('state', 'in', ['draft', 'in_progress']),
        ])
        self.assertNotIn(req, overdue)

    # --- Тесты данных для сводки по объекту ---

    def test_aggregates_by_project(self):
        """Агрегаты qty_total_requested корректны по проектам."""
        self._create_request(self.project1, self.future_date)
        self._create_request(self.project2, self.future_date)

        reqs_p1 = self.env['object.request'].search([
            ('project_id', '=', self.project1.id),
        ])
        self.assertTrue(reqs_p1)
        total_requested = sum(r.qty_total_requested for r in reqs_p1)
        self.assertGreater(total_requested, 0)

    def test_line_matching_state_distribution(self):
        """Строки с разным matching_state корректно считаются."""
        req = self._create_request(self.project1, self.future_date)
        # Добавим строку с matching_required
        line2 = self.env['object.request.line'].create({
            'request_id': req.id,
            'name_raw': 'Несопоставленная позиция',
            'qty_requested': 2.0,
            'matching_state': 'requires_mapping',
            'matching_required': True,
        })
        matched = self.env['object.request.line'].search([
            ('request_id', '=', req.id),
            ('matching_state', '=', 'matched'),
        ])
        unmatched = self.env['object.request.line'].search([
            ('request_id', '=', req.id),
            ('matching_state', '=', 'requires_mapping'),
        ])
        self.assertGreater(len(matched), 0)
        self.assertIn(line2, unmatched)

    def test_stored_aggregate_fields_updated(self):
        """line_problem_count и qty_total_requested хранятся и обновляются."""
        req = self._create_request(self.project1, self.future_date)
        self.assertEqual(req.qty_total_requested, 3.0)
        self.assertEqual(req.line_count, 1)

        self.env['object.request.line'].create({
            'request_id': req.id,
            'name_raw': 'Вторая строка',
            'qty_requested': 7.0,
            'matching_required': True,
        })
        req.invalidate_recordset()
        self.assertAlmostEqual(req.qty_total_requested, 10.0)
        self.assertEqual(req.line_problem_count, 1)
