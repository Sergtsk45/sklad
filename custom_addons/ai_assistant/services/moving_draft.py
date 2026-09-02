from odoo.exceptions import ValidationError

from .action_tools.read_tools import uoms_are_compatible
from .moving_stock import MovingWarehouseResolver, ensure_moving_access


class MovingDraftService:
    """Workflow-only write boundary; deliberately absent from ToolRegistry."""

    def __init__(self, env):
        self.env = env

    def create(self, product_id, quantity, source_warehouse_id,
               destination_warehouse_id, scheduled_date=None):
        ensure_moving_access(self.env)
        product = self.env['product.product'].browse(product_id).exists()
        if not product or not product.active or not product.is_storable:
            raise ValidationError('Для перемещения нужен активный складской товар.')
        if quantity <= 0:
            raise ValidationError('Количество должно быть больше нуля.')
        resolver = MovingWarehouseResolver(self.env)
        source = resolver.validate(source_warehouse_id)
        destination = resolver.validate(destination_warehouse_id, source.id)
        if not uoms_are_compatible(product.uom_id, product.uom_id):
            raise ValidationError('Единица измерения несовместима.')
        origin = 'Перемещение (AI): %s → %s' % (source.code, destination.code)
        values = {
            'picking_type_id': destination.int_type_id.id,
            'location_id': source.lot_stock_id.id,
            'location_dest_id': destination.lot_stock_id.id,
            'origin': origin,
            'move_ids': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': quantity,
                'product_uom': product.uom_id.id,
                'description_picking': product.display_name,
                'location_id': source.lot_stock_id.id,
                'location_dest_id': destination.lot_stock_id.id,
            })],
        }
        if scheduled_date:
            values['scheduled_date'] = scheduled_date
        picking = self.env['stock.picking'].create(values)
        picking.message_post(
            body='Черновик перемещения создан AI-ассистентом.',
            message_type='notification', subtype_xmlid='mail.mt_note',
        )
        self.env['ai_assistant.audit'].sudo().create({
            'user_id': self.env.user.id,
            'tool_name': 'moving_execute_plan',
            'args_summary': (
                'product_id=%s, quantity=%s, source=%s, destination=%s'
                % (product.id, quantity, source.code, destination.code)
            ),
            'result_status': 'success',
            'record_ref': 'stock.picking,%s' % picking.id,
        })
        return picking
