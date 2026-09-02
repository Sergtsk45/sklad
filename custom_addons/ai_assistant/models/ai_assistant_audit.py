from odoo import fields, models


class AiAssistantAudit(models.Model):
    _name = 'ai_assistant.audit'
    _description = 'AI Assistant Tool Audit'
    _order = 'created_at desc, id desc'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
        ondelete='restrict',
    )
    tool_name = fields.Char(
        string='Tool',
        required=True,
        readonly=True,
    )
    args_summary = fields.Text(
        string='Arguments Summary',
        readonly=True,
    )
    result_status = fields.Selection(
        [
            ('success', 'Success'),
            ('error', 'Error'),
        ],
        string='Status',
        required=True,
        readonly=True,
    )
    record_ref = fields.Char(
        string='Record Reference',
        readonly=True,
    )
    created_at = fields.Datetime(
        string='Created At',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
    )
