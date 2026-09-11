from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def _parse_action_context(self, action):
        ctx = action.get('context') or {}
        if isinstance(ctx, str):
            ctx = safe_eval(ctx, {'uid': self.env.uid})
        return dict(ctx)

    @api.model
    def action_ai_open_warehouse_stock(self):
        """Open stock-report with warehouse context from URL active_id/active_ids."""
        warehouse_id = self.env.context.get('active_id')
        active_ids = self.env.context.get('active_ids') or []
        only_available = True

        if len(active_ids) >= 2:
            warehouse_id = active_ids[0]
            only_available = bool(active_ids[1])
        elif active_ids:
            warehouse_id = active_ids[0]

        if not warehouse_id:
            raise UserError(_('Не указан склад (active_id).'))

        warehouse = self.browse(warehouse_id).exists()
        if not warehouse:
            raise UserError(_('Склад id=%s не найден.', warehouse_id))

        action = self.env['ir.actions.actions']._for_xml_id(
            'stock.action_product_stock_view',
        )
        ctx = self._parse_action_context(action)
        ctx['search_warehouse'] = warehouse.id
        if only_available:
            ctx['search_default_real_stock_available'] = 1
        action['context'] = ctx
        return action
