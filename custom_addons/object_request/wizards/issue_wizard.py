from odoo import models, fields, api
from odoo.exceptions import UserError


class ObjectRequestIssueWizard(models.TransientModel):
    _name = 'object.request.issue.wizard'
    _description = 'Wizard создания выдачи со склада'

    request_id = fields.Many2one(
        'object.request',
        string='Требование',
        required=True,
        ondelete='cascade',
        readonly=True,
    )
    line_ids = fields.Many2many(
        'object.request.line',
        'object_request_issue_wizard_line_rel', 'wizard_id', 'line_id',
        string='Строки к выдаче',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Склад',
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Тип операции',
    )
    source_location_id = fields.Many2one(
        'stock.location', string='Откуда (источник)',
    )
    destination_location_id = fields.Many2one(
        'stock.location', string='Куда (назначение)',
    )
    scheduled_date = fields.Datetime(
        string='Дата выдачи', required=True, default=fields.Datetime.now,
    )
    comment = fields.Text(string='Комментарий')
    line_count = fields.Integer(
        compute='_compute_line_count',
        string='Строк к выдаче',
    )

    @api.depends('line_ids')
    def _compute_line_count(self):
        for wiz in self:
            wiz.line_count = len(wiz.line_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        request_id = self.env.context.get('default_request_id')
        if not request_id:
            return res
        request = self.env['object.request'].browse(request_id)
        lines = request.line_ids.filtered(
            lambda ln: ln.qty_to_issue > 0 and ln.product_id
        )
        res['line_ids'] = [(6, 0, lines.ids)]
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', request.company_id.id)], limit=1,
        )
        if warehouse:
            res['warehouse_id'] = warehouse.id
            res['picking_type_id'] = warehouse.int_type_id.id
            res['source_location_id'] = warehouse.lot_stock_id.id
            customer_loc = self.env.ref(
                'stock.stock_location_customers', raise_if_not_found=False,
            )
            if customer_loc:
                res['destination_location_id'] = customer_loc.id
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.picking_type_id = self.warehouse_id.int_type_id
            self.source_location_id = self.warehouse_id.lot_stock_id

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        pt = self.picking_type_id
        if pt:
            if pt.default_location_src_id:
                self.source_location_id = pt.default_location_src_id
            if pt.default_location_dest_id:
                self.destination_location_id = pt.default_location_dest_id

    def action_create_issue(self):
        self.ensure_one()
        wizard = self.env['object.request.issue.preview.wizard'].with_context(
            default_request_id=self.request_id.id,
        ).create({})
        return wizard.action_create_issues()

    def _legacy_action_create_issue(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda ln: ln.qty_to_issue > 0 and ln.product_id
        )
        if not lines:
            raise UserError(
                'Нет строк с заполненным количеством к выдаче '
                'и сопоставленным товаром.'
            )

        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.destination_location_id.id,
            'origin': self.request_id.name,
            'scheduled_date': self.scheduled_date,
            'is_object_request_issue': True,
            'object_request_project_id': self.request_id.project_id.id,
        })

        move_vals_list = []
        for line in lines:
            uom = line.uom_id or line.product_id.uom_id
            move_vals_list.append({
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty_to_issue,
                'product_uom': uom.id,
                'location_id': self.source_location_id.id,
                'location_dest_id': self.destination_location_id.id,
            })
        moves = self.env['stock.move'].create(move_vals_list)

        self.request_id.write({'issue_picking_ids': [(4, picking.id)]})

        for line, move in zip(lines, moves):
            line.write({
                'issue_picking_id': picking.id,
                'issue_move_id': move.id,
            })

        picking.action_assign()

        for line, move in zip(lines, moves):
            qty_res = sum(ml.quantity for ml in move.move_line_ids)
            line.write({
                'qty_reserved': qty_res,
                'issue_reserved': qty_res > 0,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Выдача',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
