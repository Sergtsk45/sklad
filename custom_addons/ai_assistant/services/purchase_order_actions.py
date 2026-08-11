import logging

from odoo.exceptions import ValidationError

from .action_tools.validators import validate_state_in

_logger = logging.getLogger(__name__)


class PurchaseOrderActionsService:
    ALLOWED = {
        'send_rfq': ('draft', 'sent'),
        'confirm': ('draft', 'sent'),
        'cancel': ('draft', 'sent', 'purchase', 'to approve'),
    }

    def __init__(self, env):
        self.env = env

    def confirm_order(self, po_id):
        po = self._po(po_id)
        validate_state_in(po, self.ALLOWED['confirm'])
        po.button_confirm()
        po.message_post(body='Заказ подтверждён через AI-ассистент.')
        return po

    def cancel_order(self, po_id):
        po = self._po(po_id)
        validate_state_in(po, self.ALLOWED['cancel'])
        po.button_cancel()
        po.message_post(body='Заказ отменён через AI-ассистент.')
        return po

    def send_rfq_action(self, po_id):
        po = self._po(po_id)
        validate_state_in(po, self.ALLOWED['send_rfq'])
        return po.with_context(send_rfq=True).action_rfq_send()

    def print_action(self, po_id):
        po = self._po(po_id)
        return self.env.ref(
            'purchase.action_report_purchase_order'
        ).report_action(po)

    def dispatch(self, action, po_id):
        if action == 'confirm':
            return self.confirm_order(po_id), None
        if action == 'cancel':
            return self.cancel_order(po_id), None
        if action == 'send_rfq':
            return self._po(po_id), self.send_rfq_action(po_id)
        if action == 'print':
            return self._po(po_id), self.print_action(po_id)
        raise ValidationError('Неизвестное действие над заказом.')

    def dispatch_for_session(self, store, uid, token, action,
                             advisory_po_id=None):
        """Resolve the target exclusively from the authenticated session."""
        session = store.get_session(uid, token)
        if not session or not session.get('po_id'):
            raise ValidationError(
                'Действие недоступно: сессия истекла.'
            )
        po_id = session['po_id']
        if advisory_po_id and advisory_po_id != po_id:
            _logger.warning(
                'Replenishment PO mismatch: uid=%s token=%s session_po=%s ui_po=%s',
                uid, token, po_id, advisory_po_id,
            )
        po, action_to_run = self.dispatch(action, po_id)
        actions = self.action_items(po)
        return {
            'ok': True,
            'po': {'id': po.id, 'name': po.name, 'state': po.state,
                   'actions': actions},
            'card': self.card(po, token),
            'action_to_run': action_to_run,
        }

    def card(self, po, replenishment_token):
        actions = self.action_items(po)
        return {
            'type': 'result',
            'status': 'success',
            'record': {
                'model': 'purchase.order',
                'id': po.id,
                'name': po.name,
                'url': '/odoo/purchase/%s' % po.id,
            },
            'details': [{
                'label': 'Статус',
                'value': po.state,
            }],
            'next_hint': 'Проверьте заказ и выберите следующее действие.',
            'steps': [],
            'workflow': {
                'type': 'replenishment',
                'token': replenishment_token,
            },
            'replenishmentToken': replenishment_token,
            'replenishment_token': replenishment_token,
            'po': {'id': po.id, 'name': po.name, 'state': po.state},
            'actions': actions,
        }

    def action_items(self, po):
        return [
            self._item('Отправить запрос', 'send_rfq', po,
                       self.ALLOWED['send_rfq']),
            self._item('Подтвердить заказ', 'confirm', po,
                       self.ALLOWED['confirm']),
            self._item('Печать', 'print', po, None),
            self._item('Отменить', 'cancel', po, self.ALLOWED['cancel']),
        ]

    def _item(self, label, action, po, allowed):
        return {'label': label, 'action': action, 'po_id': po.id,
                'disabled': bool(allowed and po.state not in allowed)}

    def _po(self, po_id):
        po = self.env['purchase.order'].browse(po_id).exists()
        if not po:
            raise ValidationError('Заказ поставщику не найден.')
        return po
