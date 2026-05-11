from odoo import models, fields, api


class ObjectRequestStockCheckWizard(models.TransientModel):
    _name = 'object.request.stock.check.wizard'
    _description = 'Подтверждение результатов проверки наличия'

    request_id = fields.Many2one(
        'object.request', string='Требование', required=True,
        readonly=True, ondelete='cascade',
    )
    line_ids = fields.One2many(
        'object.request.stock.check.wizard.line',
        'wizard_id', string='Позиции с наличием',
        readonly=True,
    )
    lines_with_stock_count = fields.Integer(
        string='Позиций с наличием', compute='_compute_counts',
    )
    lines_total_count = fields.Integer(
        string='Всего позиций', compute='_compute_counts',
    )
    warehouse_names = fields.Char(
        string='Проверено по складам', compute='_compute_warehouse_names',
    )

    @api.depends('line_ids')
    def _compute_counts(self):
        for wiz in self:
            wiz.lines_with_stock_count = len(wiz.line_ids)
            wiz.lines_total_count = len(wiz.request_id.line_ids.filtered(
                lambda ln: ln.product_id and not ln.is_cancelled
            ))

    @api.depends('request_id')
    def _compute_warehouse_names(self):
        for wiz in self:
            warehouses = self.env['stock.warehouse'].search([
                ('company_id', '=', wiz.request_id.company_id.id),
                ('active', '=', True),
            ])
            wiz.warehouse_names = ', '.join(warehouses.mapped('name'))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        request_id = self.env.context.get('default_request_id')
        if not request_id:
            return res
        request = self.env['object.request'].browse(request_id)
        lines_with_stock = request.line_ids.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled and ln.stock_qty_on_hand > 0
        )
        res['line_ids'] = [(0, 0, {
            'product_id': ln.product_id.id,
            'name_raw': ln.name_raw,
            'qty_requested': ln.qty_requested,
            'stock_qty_on_hand': ln.stock_qty_on_hand,
            'stock_breakdown': ln._get_stock_breakdown_label(),
            'uom_id': ln.uom_id.id if ln.uom_id else False,
        }) for ln in lines_with_stock]
        return res

    def action_confirm(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_recheck(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}


class ObjectRequestStockCheckWizardLine(models.TransientModel):
    _name = 'object.request.stock.check.wizard.line'
    _description = 'Строка wizard проверки наличия'
    _order = 'stock_qty_on_hand desc'

    wizard_id = fields.Many2one(
        'object.request.stock.check.wizard', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one('product.product', string='Товар', readonly=True)
    name_raw = fields.Char(string='Наименование (из файла)', readonly=True)
    qty_requested = fields.Float(string='Запрошено', readonly=True)
    stock_qty_on_hand = fields.Float(string='Остаток на складе', readonly=True)
    stock_breakdown = fields.Char(string='Раскладка по складам', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Ед. изм.', readonly=True)
