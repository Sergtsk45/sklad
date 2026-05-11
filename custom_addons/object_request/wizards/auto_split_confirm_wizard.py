from odoo import fields, models


class ObjectRequestAutoSplitConfirmWizard(models.TransientModel):
    _name = 'object.request.auto.split.confirm.wizard'
    _description = 'Подтверждение перезаписи распределения по складам'

    request_id = fields.Many2one(
        'object.request', string='Требование', required=True,
        readonly=True, ondelete='cascade',
    )
    manual_line_count = fields.Integer(
        string='Строк с ручными правками', readonly=True,
    )
    message = fields.Text(
        string='Сообщение', compute='_compute_message', readonly=True,
    )

    def _compute_message(self):
        for wizard in self:
            wizard.message = (
                'План распределения был отредактирован вручную '
                f'для {wizard.manual_line_count} строк. Перезаписать?'
            )

    def action_confirm(self):
        self.ensure_one()
        self.request_id.with_context(force_auto_split=True).action_auto_split()
        return {'type': 'ir.actions.act_window_close'}
