from odoo import models, fields


class ObjectRequestConfirmWizard(models.TransientModel):
    _name = 'object.request.confirm.wizard'
    _description = 'Подтверждение смены статуса требования'

    request_id = fields.Many2one(
        'object.request', required=True, readonly=True, ondelete='cascade',
    )
    message = fields.Text(string='Сообщение', readonly=True)
    action_type = fields.Selection(
        [
            ('in_progress', 'В работу'),
            ('close', 'Закрыть'),
        ],
        required=True, readonly=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if self.action_type == 'in_progress':
            self.request_id.write({'state': 'in_progress'})
        elif self.action_type == 'close':
            self.request_id.write({'state': 'closed'})
        return {'type': 'ir.actions.act_window_close'}
