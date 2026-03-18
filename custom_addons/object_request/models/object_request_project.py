from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ObjectRequestProject(models.Model):
    _name = 'object.request.project'
    _description = 'Project Object for Supply Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='Наименование', required=True, tracking=True)
    code = fields.Char(string='Код объекта', index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик')
    address = fields.Char(string='Адрес')
    comment = fields.Text(string='Комментарий')
    active = fields.Boolean(default=True)

    request_ids = fields.One2many(
        'object.request', 'project_id', string='Требования',
    )
    request_count = fields.Integer(
        compute='_compute_request_count', string='Количество требований',
    )

    @api.depends('request_ids')
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)

    def action_open_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Требования',
            'res_model': 'object.request',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    @api.constrains('code')
    def _check_unique_code(self):
        for rec in self:
            if not rec.code:
                continue
            duplicate = self.search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if duplicate:
                raise ValidationError(
                    f'Код объекта "{rec.code}" уже используется другим объектом.'
                )
