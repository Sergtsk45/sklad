import re
from urllib.parse import urlencode

from odoo.exceptions import AccessError

from .base import AbstractReadTool
from .navigation_catalog import NAVIGATION_CATALOG
from .registry import default_registry
from .validators import LEGACY_OBJECT_WAREHOUSE_ALIASES


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
    description = 'Поиск контрагента по имени или ИНН.'
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 2},
            'role': {
                'type': 'string',
                'enum': ['any', 'supplier', 'customer'],
                'default': 'any',
            },
            'is_supplier': {'type': 'boolean', 'default': True},
        },
        'required': ['query'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        query = args['query']
        role = args.get('role')
        if not role:
            role = 'supplier' if args.get('is_supplier', True) else 'any'
        domain = ['|', ('name', 'ilike', query), ('vat', '=', query)]
        if role == 'supplier':
            domain = ['&', ('supplier_rank', '>', 0)] + domain
        elif role == 'customer':
            domain = ['&', ('customer_rank', '>', 0)] + domain
        partners = env['res.partner'].search_read(
            domain,
            [
                'id',
                'display_name',
                'name',
                'vat',
                'supplier_rank',
                'customer_rank',
                'category_id',
                'city',
            ],
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
            domain.append(
                (
                    'warehouse_id.code',
                    'in',
                    self._normalize_warehouse_codes(warehouse_codes),
                )
            )
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

    def _normalize_warehouse_codes(self, warehouse_codes):
        normalized = []
        for code in warehouse_codes:
            target = LEGACY_OBJECT_WAREHOUSE_ALIASES.get(
                (code or '').strip().lower(),
                code,
            )
            if target not in normalized:
                normalized.append(target)
        return normalized


class FindWarehouseTool(AbstractReadTool):
    name = 'find_warehouse'
    description = (
        'Найти склад по коду (O002, ОбМ-4, O, ОбМ-) или по части '
        'названия/адреса (Хмельницкого, Ломоносова). Legacy aliases: '
        'ОбМ-2 -> O001, ОбМ-4 -> O002.'
    )
    parameters_schema = {
        'type': 'object',
        'properties': {
            'query': {'type': 'string', 'minLength': 1},
            'code_pattern': {'type': 'string', 'minLength': 1},
        },
        'anyOf': [
            {'required': ['query']},
            {'required': ['code_pattern']},
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        query = self._get_query(args)
        alias_code = self._legacy_alias_code(query)
        if alias_code:
            domain = [('code', '=ilike', alias_code)]
        elif self._is_object_warehouse_prefix_query(query):
            domain = [('code', 'in', self._legacy_object_alias_targets())]
        elif self._is_warehouse_code_query(query):
            operator = (
                'ilike'
                if query.endswith('-') or query.upper() == 'O'
                else '=ilike'
            )
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
        if len(query) < 2 and query.upper() != 'O':
            raise ValueError('query must contain at least 2 characters')
        return query

    def _is_object_warehouse_code_query(self, query):
        return bool(re.match(r'^ОбМ-\d*$', query))

    def _is_object_warehouse_prefix_query(self, query):
        return query == 'ОбМ-'

    def _is_warehouse_code_query(self, query):
        return bool(
            re.match(r'^(?:ОбМ-\d*|O\d*|O)$', query, re.IGNORECASE)
        )

    def _legacy_alias_code(self, query):
        return LEGACY_OBJECT_WAREHOUSE_ALIASES.get(query.lower())

    def _legacy_object_alias_targets(self):
        return list(LEGACY_OBJECT_WAREHOUSE_ALIASES.values())

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


class GetWarehouseStockLinkTool(AbstractReadTool):
    name = 'get_warehouse_stock_link'
    description = (
        'Вернуть ссылку на отчёт Odoo с товарами/остатками по конкретному '
        'складу (ai-warehouse-stock → stock-report). Не возвращает список '
        'позиций — только URL.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_user']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'warehouse_id': {'type': 'integer'},
            'query': {'type': 'string', 'minLength': 2},
            'only_available': {'type': 'boolean', 'default': True},
        },
        'anyOf': [
            {'required': ['warehouse_id']},
            {'required': ['query']},
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        if not env.user.has_group('stock.group_stock_user'):
            return {
                'url': None,
                'reason': 'forbidden',
            }

        warehouse = self._resolve_warehouse(env, args)
        if not warehouse:
            return {
                'url': None,
                'reason': 'warehouse_not_found',
            }

        action = env.ref(
            'stock.action_product_stock_view',
            raise_if_not_found=False,
        )
        if not action:
            return {
                'url': None,
                'reason': 'not_found',
            }

        if not self._can_read_products(env):
            return {
                'url': None,
                'reason': 'forbidden',
            }

        query_params = {'active_id': warehouse['id']}
        if not args.get('only_available', True):
            query_params['active_ids'] = '%s,0' % warehouse['id']

        url = '/odoo/ai-warehouse-stock?' + urlencode(query_params)
        return {
            'url': url,
            'label': 'Остатки: %s (%s)' % (
                warehouse['name'],
                warehouse['code'],
            ),
            'warehouse_id': warehouse['id'],
            'warehouse_code': warehouse['code'],
            'warehouse_name': warehouse['name'],
            'menu_breadcrumb': 'Склад -> Отчетность -> Наличие',
        }

    def _resolve_warehouse(self, env, args):
        warehouse_id = args.get('warehouse_id')
        if warehouse_id:
            warehouse = env['stock.warehouse'].browse(warehouse_id).exists()
            if warehouse:
                return warehouse.read(['id', 'name', 'code'])[0]
            return None

        query = (args.get('query') or '').strip()
        if len(query) < 2:
            return None

        warehouses = FindWarehouseTool().execute(
            env,
            {'query': query},
        ).get('warehouses') or []
        if not warehouses:
            return None
        if len(warehouses) == 1:
            return warehouses[0]

        normalized = query.lower()
        for warehouse in warehouses:
            if warehouse.get('code', '').lower() == normalized:
                return warehouse
        return warehouses[0]

    def _can_read_products(self, env):
        try:
            env['product.product'].check_access('read')
        except AccessError:
            return False
        return True


class GetNavigationLinkTool(AbstractReadTool):
    name = 'get_navigation_link'
    description = (
        'Вернуть проверенную ссылку на экран Odoo по теме навигации. '
        'Не угадывает URL для неизвестных тем.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_user']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'topic': {'type': 'string', 'minLength': 2},
            'extra_filters': {'type': ['object', 'null']},
        },
        'required': ['topic'],
        'additionalProperties': False,
    }
    catalog = NAVIGATION_CATALOG

    def execute(self, env, args):
        topic = self._normalize_topic(args['topic'])
        record = self._find_record(topic)
        if not record:
            return {
                'url': None,
                'reason': 'unknown_topic',
                'topic': topic,
            }

        if not self._user_has_groups(env, record.get('required_groups') or ()):
            return {
                'url': None,
                'reason': 'forbidden',
                'topic': topic,
            }

        action = self._resolve_action(env, record)
        if record.get('action_xml_id') and not action:
            return {
                'url': None,
                'reason': 'not_found',
                'topic': topic,
            }

        if action and not self._can_read_action_model(env, action):
            return {
                'url': None,
                'reason': 'forbidden',
                'topic': topic,
            }

        url = self._build_url(record, action, args.get('extra_filters'))
        return {
            'topic': topic,
            'label': record['label'],
            'url': url,
            'menu_breadcrumb': record['menu_breadcrumb'],
        }

    def _normalize_topic(self, topic):
        return (topic or '').strip().lower()

    def _find_record(self, topic):
        exact_match = None
        substring_match = None
        for record in self.catalog:
            keys = [self._normalize_topic(key) for key in record['topic_keys']]
            if topic in keys:
                exact_match = record
                break
            if any(key in topic or topic in key for key in keys):
                substring_match = substring_match or record
        return exact_match or substring_match

    def _user_has_groups(self, env, groups):
        return all(env.user.has_group(xmlid) for xmlid in groups)

    def _resolve_action(self, env, record):
        xml_id = record.get('action_xml_id')
        if xml_id:
            action = env.ref(xml_id, raise_if_not_found=False)
            if action:
                return action

        path = record.get('path')
        if path:
            return env['ir.actions.act_window'].search(
                [('path', '=', path)],
                limit=1,
            )
        return env['ir.actions.act_window']

    def _can_read_action_model(self, env, action):
        model_name = action.res_model
        if not model_name:
            return True
        if model_name not in env:
            return False
        try:
            env[model_name].check_access('read')
        except AccessError:
            return False
        return True

    def _build_url(self, record, action, extra_filters):
        path = self._get_url_path(record, action)
        query = dict(record.get('context_defaults') or {})
        if isinstance(extra_filters, dict):
            query.update(extra_filters)

        url = '/odoo/%s' % path
        if query:
            url += '?' + urlencode(query, doseq=True)
        return url

    def _get_url_path(self, record, action):
        if record.get('path'):
            return record['path']
        if action and action.path:
            return action.path
        return 'action-%s' % record['action_xml_id']


default_registry.register(SearchProductsTool())
default_registry.register(FindProductByIdTool())
default_registry.register(FindPartnerTool())
default_registry.register(SearchStockQuantsTool())
default_registry.register(FindWarehouseTool())
default_registry.register(FindPickingTypeTool())
default_registry.register(FindObjectRequestTool())
default_registry.register(ReadObjectRequestTool())
default_registry.register(GetWarehouseStockLinkTool())
default_registry.register(GetNavigationLinkTool())
