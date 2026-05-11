from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestOBR022Approval(TransactionCase):
    """OBR-022: Workflow согласования документа."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.project = cls.env['object.request.project'].create({
            'name': 'Тест согласования',
        })
        cls.user = cls.env.ref('base.user_admin')

        approver_group = cls.env.ref('object_request.group_approver')
        cls.approver = cls.env['res.users'].create({
            'name': 'Согласующий Тестов',
            'login': 'approver_test_obr022',
            'group_ids': [(4, approver_group.id)],
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Товар для теста согласования',
            'type': 'consu',
        })

    def _create_request(self, approver=None):
        vals = {
            'project_id': self.project.id,
            'foreman_user_id': self.user.id,
            'need_date': '2026-06-01',
        }
        if approver:
            vals['approver_user_id'] = approver.id
        req = self.env['object.request'].create(vals)
        self.env['object.request.line'].create({
            'request_id': req.id,
            'name_raw': 'Тестовая позиция',
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
            'qty_requested': 5.0,
        })
        return req

    # --- Тесты ---

    def test_submit_for_approval_sets_pending(self):
        """Отправка на согласование → approval_state = pending."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        self.assertEqual(req.approval_state, 'pending')

    def test_approve_sets_approved(self):
        """Согласование → approval_state = approved."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        req.action_approve()
        self.assertEqual(req.approval_state, 'approved')

    def test_reject_sets_rejected(self):
        """Отклонение → approval_state = rejected."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        req.action_reject()
        self.assertEqual(req.approval_state, 'rejected')

    def test_in_progress_blocked_when_pending(self):
        """action_in_progress заблокирован при approval_state=pending."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        self.assertEqual(req.approval_state, 'pending')
        with self.assertRaises(UserError):
            req.action_in_progress()

    def test_in_progress_blocked_when_rejected(self):
        """action_in_progress заблокирован при approval_state=rejected."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        req.action_reject()
        with self.assertRaises(UserError):
            req.action_in_progress()

    def test_in_progress_allowed_when_approved(self):
        """action_in_progress разрешён при approval_state=approved."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        req.action_approve()
        req.action_in_progress()
        self.assertEqual(req.state, 'in_progress')

    def test_in_progress_allowed_when_not_required(self):
        """action_in_progress разрешён при approval_state=not_required."""
        req = self._create_request()
        req.action_in_progress()
        self.assertEqual(req.state, 'in_progress')

    def test_resubmit_after_rejection(self):
        """После отклонения можно повторно отправить на согласование."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        req.action_reject()
        self.assertEqual(req.approval_state, 'rejected')

        req.action_submit_for_approval()
        self.assertEqual(req.approval_state, 'pending')

    def test_submit_without_approver_raises_error(self):
        """Отправка без согласующего → UserError."""
        req = self._create_request()  # approver не задан
        with self.assertRaises(UserError):
            req.action_submit_for_approval()

    def test_submit_when_already_pending_raises_error(self):
        """Повторная отправка при статусе pending → UserError."""
        req = self._create_request(approver=self.approver)
        req.action_submit_for_approval()
        with self.assertRaises(UserError):
            req.action_submit_for_approval()

    def test_default_approval_state_is_not_required(self):
        """По умолчанию approval_state = not_required."""
        req = self._create_request()
        self.assertEqual(req.approval_state, 'not_required')

    def test_full_workflow_with_approval(self):
        """Полный цикл: submit → approve → in_progress."""
        req = self._create_request(approver=self.approver)
        self.assertEqual(req.state, 'draft')
        self.assertEqual(req.approval_state, 'not_required')

        req.action_submit_for_approval()
        self.assertEqual(req.approval_state, 'pending')
        self.assertEqual(req.state, 'draft')

        req.action_approve()
        self.assertEqual(req.approval_state, 'approved')

        req.action_in_progress()
        self.assertEqual(req.state, 'in_progress')

    def test_full_workflow_without_approval(self):
        """Цикл без согласования: draft → in_progress напрямую."""
        req = self._create_request()
        req.action_in_progress()
        self.assertEqual(req.state, 'in_progress')
        self.assertEqual(req.approval_state, 'not_required')
