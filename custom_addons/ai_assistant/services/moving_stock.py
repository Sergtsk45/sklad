import re

from odoo.exceptions import AccessError, ValidationError

from .action_tools.validators import LEGACY_OBJECT_WAREHOUSE_ALIASES


def _normalized(value):
    return re.sub(r'\s+', ' ', (value or '').replace('\xa0', ' ')).strip().casefold()


class MovingAvailabilityService:
    def __init__(self, env):
        self.env = env

    def totals(self, product_id, warehouse):
        warehouse = self._warehouse(warehouse)
        domain = [
            ('product_id', '=', product_id),
            ('location_id', 'child_of', warehouse.lot_stock_id.id),
            ('location_id.usage', '=', 'internal'),
            ('company_id', '=', self.env.company.id),
        ]
        rows = self.env['stock.quant']._read_group(
            domain, [], ['quantity:sum', 'reserved_quantity:sum'],
        )
        quantity, reserved = rows[0] if rows else (0.0, 0.0)
        quantity, reserved = quantity or 0.0, reserved or 0.0
        return {'on_hand': quantity, 'reserved': reserved,
                'available': quantity - reserved}

    def _warehouse(self, warehouse):
        record = warehouse if getattr(warehouse, '_name', None) else (
            self.env['stock.warehouse'].browse(warehouse)
        )
        record = record.exists()
        if not record or record.company_id != self.env.company:
            raise ValidationError('Склад не найден в текущей компании.')
        return record


class MovingWarehouseResolver:
    """Deterministic exact-first resolver; fuzzy results are never selected."""

    def __init__(self, env):
        self.env = env

    def resolve(self, query, exclude_id=None, limit=20):
        query = (query or '').strip()
        if not query:
            return []
        domain = self._base_domain(exclude_id)
        exact_code = self.env['stock.warehouse'].search(
            domain + [('code', '=ilike', query)], limit=limit,
        )
        if exact_code:
            return self._format(exact_code, 'exact_code', 'code')
        alias = LEGACY_OBJECT_WAREHOUSE_ALIASES.get(query.casefold())
        if alias:
            records = self.env['stock.warehouse'].search(
                domain + [('code', '=ilike', alias)], limit=limit,
            )
            if records:
                return self._format(records, 'exact_alias', 'alias')
        records = self.env['stock.warehouse'].search(domain, limit=200)
        exact_name = records.filtered(
            lambda wh: _normalized(wh.name) == _normalized(query)
        )[:limit]
        if exact_name:
            return self._format(exact_name, 'exact_name', 'name')
        fuzzy = self.env['stock.warehouse'].search(
            domain + ['|', ('code', 'ilike', query), ('name', 'ilike', query)],
            limit=limit,
        )
        return self._format(fuzzy, 'fuzzy', 'code_or_name')

    def list_candidates(self, exclude_id=None, product_id=None,
                        positive_available=False, limit=20):
        warehouses = self.env['stock.warehouse'].search(
            self._base_domain(exclude_id), order='code, name', limit=100,
        )
        availability = MovingAvailabilityService(self.env)
        result = []
        for warehouse in warehouses:
            item = self._item(warehouse, 'listed', 'list')
            if product_id:
                item.update(availability.totals(product_id, warehouse))
            if positive_available and item.get('available', 0) <= 0:
                continue
            result.append(item)
        if product_id:
            result.sort(key=lambda item: (-item.get('available', 0),
                                          item['code'], item['name']))
        return result[:limit]

    def validate(self, warehouse_id, exclude_id=None):
        warehouse = self.env['stock.warehouse'].browse(warehouse_id).exists()
        if not warehouse or warehouse.company_id != self.env.company:
            raise ValidationError('Склад не доступен.')
        if 'active' in warehouse._fields and not warehouse.active:
            raise ValidationError('Склад больше не активен.')
        if exclude_id and warehouse.id == exclude_id:
            raise ValidationError('Склады источника и назначения должны различаться.')
        if (not warehouse.lot_stock_id
                or warehouse.lot_stock_id.usage != 'internal'):
            raise ValidationError('У склада нет валидной внутренней локации.')
        if not self.env['stock.location'].search_count([
            ('id', '=', warehouse.lot_stock_id.id),
            ('id', 'child_of', warehouse.view_location_id.id),
        ]):
            raise ValidationError('Локация склада не относится к его иерархии.')
        if (not warehouse.int_type_id
                or warehouse.int_type_id.code != 'internal'):
            raise ValidationError('У склада нет операции internal.')
        if ('active' in warehouse.int_type_id._fields
                and not warehouse.int_type_id.active):
            raise ValidationError('Операция internal больше не активна.')
        return warehouse

    def _base_domain(self, exclude_id):
        domain = [
            ('company_id', '=', self.env.company.id),
            ('lot_stock_id.usage', '=', 'internal'),
            ('int_type_id.code', '=', 'internal'),
        ]
        if 'active' in self.env['stock.warehouse']._fields:
            domain.append(('active', '=', True))
        picking_type = self.env['stock.picking.type']
        if 'active' in picking_type._fields:
            domain.append(('int_type_id.active', '=', True))
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        return domain

    def _format(self, records, match_type, matched_by):
        return [self._item(record, match_type, matched_by) for record in records]

    def _item(self, warehouse, match_type, matched_by):
        return {
            'id': warehouse.id, 'name': warehouse.name, 'code': warehouse.code,
            'display_name': warehouse.display_name,
            'lot_stock_id': warehouse.lot_stock_id.id,
            'picking_type_id': warehouse.int_type_id.id,
            'match_type': match_type, 'matched_by': matched_by,
        }


def ensure_moving_access(env):
    if not (env.user.has_group('ai_assistant.group_ai_assistant_supply')
            and env.user.has_group('stock.group_stock_user')):
        raise AccessError(
            'Недостаточно прав для межскладского перемещения.'
        )
