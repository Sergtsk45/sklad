import logging

from odoo.exceptions import ValidationError

from .moving_stock import ensure_moving_access

_logger = logging.getLogger(__name__)


class MovingPickingActionsService:
    ALLOWED = {
        'reserve': ('draft', 'waiting', 'confirmed'),
        'cancel': ('draft', 'waiting', 'confirmed', 'assigned'),
    }

    def __init__(self, env):
        self.env = env

    def dispatch_for_session(self, store, uid, token, action,
                             advisory_picking_id=None):
        ensure_moving_access(self.env)
        session = store.get_session(uid, token)
        if not session or not session.get('picking_id'):
            raise ValidationError('Действие недоступно: сессия истекла.')
        picking = self._picking(session['picking_id'])
        if advisory_picking_id and advisory_picking_id != picking.id:
            _logger.warning('Moving picking mismatch: uid=%s token=%s', uid, token)
        action_to_run = None
        if action == 'reserve':
            if not self._can_reserve(picking):
                raise ValidationError('Действие недоступно в текущем статусе.')
            picking.action_assign()
            picking.message_post(body='Резерв запущен через AI-ассистента.')
        elif action == 'cancel':
            self._validate_state(picking, 'cancel')
            picking.action_cancel()
            picking.message_post(body='Перемещение отменено через AI-ассистента.')
        elif action == 'open':
            action_to_run = {
                'type': 'ir.actions.act_window', 'res_model': 'stock.picking',
                'res_id': picking.id, 'views': [[False, 'form']],
                'target': 'current',
            }
        elif action == 'print':
            action_to_run = picking.do_print_picking()
        else:
            raise ValidationError('Неизвестное действие над перемещением.')
        self.env['ai_assistant.audit'].sudo().create({
            'user_id': self.env.user.id,
            'tool_name': 'moving_%s' % action,
            'args_summary': 'state=%s' % picking.state,
            'result_status': 'success',
            'record_ref': 'stock.picking,%s' % picking.id,
        })
        return {'ok': True, 'card': self.card(picking, token),
                'action_to_run': action_to_run}

    def card(self, picking, token):
        move = picking.move_ids[:1]
        return {
            'type': 'result', 'status': 'success',
            'workflow': {'type': 'moving', 'token': token},
            'record': {'model': 'stock.picking', 'id': picking.id,
                       'name': picking.name,
                       'url': '/odoo/stock.picking/%s' % picking.id},
            'details': [
                {'label': 'Статус', 'value': picking.state},
                {'label': 'Откуда', 'value': picking.location_id.display_name},
                {'label': 'Куда', 'value': picking.location_dest_id.display_name},
                {'label': 'Количество', 'value': (
                    '%s %s' % (move.product_uom_qty, move.product_uom.name)
                    if move else '—'
                )},
            ],
            'next_hint': 'Проверьте перемещение и проведите его в Odoo.',
            'actions': self.action_items(picking),
        }

    def action_items(self, picking):
        return [
            self._item('Зарезервировать', 'reserve', picking,
                       enabled=self._can_reserve(picking)),
            self._item('Открыть', 'open', picking),
            self._item('Печать', 'print', picking),
            self._item('Отменить', 'cancel', picking,
                       self.ALLOWED['cancel'], confirm=True),
        ]

    def _item(self, label, action, picking, allowed=None, confirm=False,
              enabled=None):
        disabled = (not enabled if enabled is not None else bool(
            allowed and picking.state not in allowed
        ))
        return {'label': label, 'action': action, 'disabled': disabled,
                'confirm': confirm}

    def _can_reserve(self, picking):
        return (
            picking.state in self.ALLOWED['reserve']
            or bool(getattr(picking, 'show_check_availability', False))
        )

    def _validate_state(self, picking, action):
        if picking.state not in self.ALLOWED[action]:
            raise ValidationError('Действие недоступно в текущем статусе.')

    def _picking(self, picking_id):
        picking = self.env['stock.picking'].browse(picking_id).exists()
        if not picking or picking.company_id != self.env.company:
            raise ValidationError('Перемещение не найдено.')
        return picking
