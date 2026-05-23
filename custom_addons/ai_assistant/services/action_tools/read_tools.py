import re

from .base import AbstractReadTool
from .registry import default_registry


class SearchProductsTool(AbstractReadTool):
    name = 'search_products'
    description = 'Поиск номенклатуры по нормализованному названию.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 2},
            'limit': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 30,
                'default': 10,
            },
        },
        'required': ['query'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        query = args['query']
        limit = min(int(args.get('limit') or 10), 30)
        raw_products = env['product.product'].ai_search_products(
            query, limit=limit
        )
        product_ids = [item['id'] for item in raw_products]
        products = env['product.product'].browse(product_ids)
        product_data = {
            product.id: product
            for product in products
        }
        return {
            'products': [
                self._format_product(product_data[item['id']], item)
                for item in raw_products
                if item['id'] in product_data
            ]
        }

    def _format_product(self, product, raw_data):
        return {
            'id': product.id,
            'display_name': raw_data.get('display_name'),
            'default_code': raw_data.get('default_code'),
            'uom_id': raw_data.get('uom_id'),
            'is_storable': product.is_storable,
            'list_price': product.list_price,
        }


class FindProductByIdTool(AbstractReadTool):
    name = 'find_product_by_id'
    description = 'Получить детали товара по ID.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'product_id': {'type': 'integer'},
        },
        'required': ['product_id'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        product = env['product.product'].browse(args['product_id']).exists()
        if not product:
            return {'product': None}
        data = product.read([
            'display_name',
            'uom_id',
            'categ_id',
            'is_storable',
            'seller_ids',
        ])[0]
        return {'product': data}


class FindPartnerTool(AbstractReadTool):
    name = 'find_partner'
    description = 'Поиск поставщика по имени или ИНН.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 2},
            'is_supplier': {'type': 'boolean', 'default': True},
        },
        'required': ['query'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        query = args['query']
        is_supplier = args.get('is_supplier', True)
        domain = ['|', ('name', 'ilike', query), ('vat', '=', query)]
        if is_supplier:
            domain = ['&', ('supplier_rank', '>', 0)] + domain
        partners = env['res.partner'].search_read(
            domain,
            ['id', 'display_name', 'name', 'vat', 'supplier_rank'],
            limit=10,
        )
        return {'partners': partners}


class SearchStockQuantsTool(AbstractReadTool):
    name = 'search_stock_quants'
    description = 'Поиск положительных остатков товара по складам.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'product_id': {'type': 'integer'},
            'warehouse_codes': {
                'type': ['array', 'null'],
                'items': {'type': 'string'},
            },
            'only_positive': {'type': 'boolean', 'default': True},
        },
        'required': ['product_id'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        domain = [('product_id', '=', args['product_id'])]
        if args.get('only_positive', True):
            domain.append(('quantity', '>', 0))
        warehouse_codes = args.get('warehouse_codes')
        if warehouse_codes:
            domain.append(('warehouse_id.code', 'in', warehouse_codes))
        quants = env['stock.quant'].search_read(
            domain,
            [
                'id',
                'product_id',
                'warehouse_id',
                'location_id',
                'quantity',
                'reserved_quantity',
                'available_quantity',
            ],
            limit=50,
        )
        return {'quants': quants}


class FindWarehouseTool(AbstractReadTool):
    name = 'find_warehouse'
    description = (
        'Найти склад по коду (ОбМ-4, ОбМ-) или по части '
        'названия/адреса (Хмельницкого, Ломоносова).'
    )
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 2},
            'code_pattern': {'type': 'string', 'minLength': 2},
        },
        'anyOf': [
            {'required': ['query']},
            {'required': ['code_pattern']},
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        query = self._get_query(args)
        if self._is_object_warehouse_code_query(query):
            operator = 'ilike' if query.endswith('-') else '=ilike'
            domain = [('code', operator, query)]
        else:
            domain = ['|', ('code', 'ilike', query), ('name', 'ilike', query)]
        warehouses = env['stock.warehouse'].search_read(
            domain,
            [
                'id',
                'name',
                'code',
                'in_type_id',
                'int_type_id',
                'lot_stock_id',
            ],
            limit=20,
        )
        return {'warehouses': self._deduplicate_by_id(warehouses)}

    def _get_query(self, args):
        # code_pattern is kept for compatibility with existing read tool calls.
        query = (args.get('query') or args.get('code_pattern') or '').strip()
        if len(query) < 2:
            raise ValueError('query must contain at least 2 characters')
        return query

    def _is_object_warehouse_code_query(self, query):
        return bool(re.match(r'^ОбМ-\d*$', query))

    def _deduplicate_by_id(self, warehouses):
        warehouse_by_id = {}
        for warehouse in warehouses:
            warehouse_by_id.setdefault(warehouse['id'], warehouse)
        return list(warehouse_by_id.values())


class FindPickingTypeTool(AbstractReadTool):
    name = 'find_picking_type'
    description = 'Найти тип операции incoming/internal для склада.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'warehouse_id': {'type': 'integer'},
            'code': {'type': 'string', 'enum': ['incoming', 'internal']},
        },
        'required': ['warehouse_id', 'code'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        picking_types = env['stock.picking.type'].search_read(
            [
                ('warehouse_id', '=', args['warehouse_id']),
                ('code', '=', args['code']),
            ],
            [
                'id',
                'name',
                'display_name',
                'code',
                'warehouse_id',
                'default_location_src_id',
                'default_location_dest_id',
            ],
            limit=10,
        )
        return {'picking_types': picking_types}


class FindObjectRequestTool(AbstractReadTool):
    name = 'find_object_request'
    description = 'Поиск требований OR по номеру, объекту или статусу.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': ['string', 'null']},
            'state': {
                'type': ['string', 'null'],
                'enum': [
                    'draft',
                    'in_progress',
                    'closed',
                    'cancelled',
                    None,
                ],
            },
            'project_id': {'type': ['integer', 'null']},
        },
        'required': [],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        domain = []
        query = args.get('query')
        if query:
            domain += ['|', ('name', 'ilike', query),
                       ('project_id.name', 'ilike', query)]
        if args.get('state'):
            domain.append(('state', '=', args['state']))
        if args.get('project_id'):
            domain.append(('project_id', '=', args['project_id']))
        requests = env['object.request'].search_read(
            domain,
            [
                'id',
                'name',
                'project_id',
                'state',
                'need_date',
                'qty_total_requested',
                'qty_total_to_issue',
                'qty_total_to_buy',
            ],
            limit=20,
            order='create_date desc, id desc',
        )
        return {'requests': requests}


class ReadObjectRequestTool(AbstractReadTool):
    name = 'read_object_request'
    description = 'Прочитать шапку OR и до 50 строк требования.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'request_id': {'type': 'integer'},
        },
        'required': ['request_id'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        request_record = env['object.request'].browse(
            args['request_id']
        ).exists()
        if not request_record:
            return {'request': None}

        request_data = request_record.read([
            'id',
            'name',
            'project_id',
            'state',
            'need_date',
            'qty_total_requested',
            'qty_total_to_issue',
            'qty_total_to_buy',
        ])[0]
        lines = env['object.request.line'].search_read(
            [('request_id', '=', request_record.id)],
            [
                'id',
                'name_raw',
                'product_id',
                'uom_id',
                'qty_requested',
                'qty_to_issue',
                'qty_to_buy',
                'matching_state',
                'line_state',
            ],
            limit=50,
            order='sequence, id',
        )
        request_data['lines'] = lines
        request_data['summary'] = {
            'qty_total_requested': request_record.qty_total_requested,
            'qty_total_to_issue': request_record.qty_total_to_issue,
            'qty_total_to_buy': request_record.qty_total_to_buy,
        }
        return {'request': request_data}


default_registry.register(SearchProductsTool())
default_registry.register(FindProductByIdTool())
default_registry.register(FindPartnerTool())
default_registry.register(SearchStockQuantsTool())
default_registry.register(FindWarehouseTool())
default_registry.register(FindPickingTypeTool())
default_registry.register(FindObjectRequestTool())
default_registry.register(ReadObjectRequestTool())
