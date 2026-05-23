import hashlib
import json

from odoo.exceptions import AccessError, ValidationError

from .base import AbstractWriteTool
from .registry import default_registry
from .validators import (
    validate_partner_is_supplier,
    validate_picking_type_is_object,
    validate_product_is_storable,
    validate_uom_is_meter,
)


def _ensure_tool_required_groups(tool, env):
    for xmlid in tool.required_groups:
        if not env.user.has_group(xmlid):
            raise AccessError(
                'Недостаточно прав для выполнения действия через '
                'AI-ассистента.'
            )


class CreateObjectRequestDraftTool(AbstractWriteTool):
    name = 'create_object_request_draft'
    description = 'Создать черновик требования прораба object.request.'
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'project_id': {'type': 'integer'},
            'need_date': {'type': 'string'},
            'lines': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 100,
                'items': {
                    'type': 'object',
                    'properties': {
                        'name_raw': {'type': 'string', 'minLength': 1},
                        'qty_requested': {
                            'type': 'number',
                            'exclusiveMinimum': 0,
                        },
                        'preferred_vendor_id': {
                            'type': ['integer', 'null'],
                        },
                    },
                    'required': ['name_raw', 'qty_requested'],
                    'additionalProperties': False,
                },
            },
        },
        'required': ['project_id', 'need_date', 'lines'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        lines = self._validate_lines(args.get('lines') or [])

        request_record = env['object.request'].create({
            'project_id': args['project_id'],
            'need_date': args['need_date'],
            'foreman_user_id': env.user.id,
        })
        for line in lines:
            vals = {
                'request_id': request_record.id,
                'name_raw': line['name_raw'],
                'qty_requested': line['qty_requested'],
            }
            if line.get('preferred_vendor_id'):
                vals['preferred_vendor_id'] = line['preferred_vendor_id']
            env['object.request.line'].create(vals)

        request_record.message_post(
            body=(
                'Требование создано AI-ассистентом по запросу %s. '
                'Строк: %s.'
            ) % (env.user.name, len(lines)),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'request_id': request_record.id,
            'name': request_record.name,
            'url': '/odoo/object_request/%s' % request_record.id,
        }

    def idempotency_key(self, args):
        payload = {
            'project_id': args.get('project_id'),
            'need_date': args.get('need_date'),
            'lines': sorted(
                args.get('lines') or [],
                key=lambda item: (
                    item.get('name_raw') or '',
                    item.get('qty_requested') or 0,
                    item.get('preferred_vendor_id') or 0,
                ),
            ),
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _validate_lines(self, lines):
        if not lines:
            raise ValidationError('Добавьте хотя бы одну строку требования.')
        if len(lines) > 100:
            raise ValidationError(
                'В одном требовании допускается до 100 строк.'
            )

        for line in lines:
            if not (line.get('name_raw') or '').strip():
                raise ValidationError(
                    'В каждой строке должно быть наименование материала.'
                )
            if line.get('qty_requested', 0) <= 0:
                raise ValidationError(
                    'Количество в каждой строке должно быть больше нуля.'
                )
        return lines


default_registry.register(
    CreateObjectRequestDraftTool()
)


class CreatePurchaseOrderDraftTool(AbstractWriteTool):
    name = 'create_purchase_order_draft'
    description = 'Создать черновик заказа поставщику на склад объекта.'
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'partner_id': {'type': 'integer'},
            'picking_type_id': {'type': 'integer'},
            'origin': {'type': 'string', 'minLength': 1},
            'partner_ref': {'type': 'string', 'minLength': 1},
            'date_planned': {'type': ['string', 'null']},
            'lines': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'object',
                    'properties': {
                        'product_id': {'type': 'integer'},
                        'product_qty': {
                            'type': 'number',
                            'exclusiveMinimum': 0,
                        },
                        'product_uom': {'type': 'integer'},
                        'price_unit': {'type': 'number'},
                        'name': {'type': ['string', 'null']},
                    },
                    'required': [
                        'product_id',
                        'product_qty',
                        'product_uom',
                        'price_unit',
                    ],
                    'additionalProperties': False,
                },
            },
        },
        'required': [
            'partner_id',
            'picking_type_id',
            'origin',
            'partner_ref',
            'lines',
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        self._validate_header(env, args)
        lines = self._validate_purchase_lines(env, args.get('lines') or [])

        po_vals = {
            'partner_id': args['partner_id'],
            'picking_type_id': args['picking_type_id'],
            'origin': args['origin'],
            'partner_ref': args['partner_ref'],
        }
        if args.get('date_planned'):
            po_vals['date_planned'] = args['date_planned']

        po = env['purchase.order'].create(po_vals)
        date_planned = args.get('date_planned') or po.date_planned
        warnings = []
        for line in lines:
            warning = validate_uom_is_meter(env, line['product_id'])
            if warning:
                warnings.append(warning)
            env['purchase.order.line'].create({
                'order_id': po.id,
                'product_id': line['product_id'],
                'product_qty': line['product_qty'],
                'product_uom_id': line['product_uom'],
                'price_unit': line['price_unit'],
                'name': line.get('name') or self._product_name(
                    env, line['product_id']
                ),
                'date_planned': date_planned,
            })

        po.message_post(
            body=(
                'Черновик закупки создан AI-ассистентом по запросу %s. '
                'Строк: %s.'
            ) % (env.user.name, len(lines)),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'po_id': po.id,
            'name': po.name,
            'url': '/odoo/purchase/%s' % po.id,
            'warnings': warnings,
        }

    def idempotency_key(self, args):
        payload = {
            'partner_id': args.get('partner_id'),
            'origin': args.get('origin'),
            'partner_ref': args.get('partner_ref'),
            'lines': sorted(
                args.get('lines') or [],
                key=lambda item: (
                    item.get('product_id') or 0,
                    item.get('product_qty') or 0,
                    item.get('product_uom') or 0,
                    item.get('price_unit') or 0,
                    item.get('name') or '',
                ),
            ),
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _validate_header(self, env, args):
        validate_partner_is_supplier(env, args['partner_id'])
        validate_picking_type_is_object(env, args['picking_type_id'])
        picking_type = env['stock.picking.type'].browse(
            args['picking_type_id']
        )
        if picking_type.code != 'incoming':
            raise ValidationError(
                'Для закупки нужен тип операции поступления (incoming).'
            )

    def _validate_purchase_lines(self, env, lines):
        if not lines:
            raise ValidationError('Добавьте хотя бы одну строку закупки.')
        for line in lines:
            if line.get('product_qty', 0) <= 0:
                raise ValidationError(
                    'Количество в каждой строке закупки должно быть '
                    'больше нуля.'
                )
            validate_product_is_storable(env, line['product_id'])
        return lines

    def _product_name(self, env, product_id):
        product = env['product.product'].browse(product_id)
        return product.display_name or product.name


default_registry.register(
    CreatePurchaseOrderDraftTool()
)


class CreateInternalPickingDraftTool(AbstractWriteTool):
    name = 'create_internal_picking_draft'
    description = 'Создать черновик внутреннего перемещения на склад объекта.'
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'picking_type_id': {'type': 'integer'},
            'location_id': {'type': 'integer'},
            'location_dest_id': {'type': 'integer'},
            'origin': {'type': 'string', 'minLength': 1},
            'scheduled_date': {'type': ['string', 'null']},
            'moves': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'object',
                    'properties': {
                        'product_id': {'type': 'integer'},
                        'product_uom_qty': {
                            'type': 'number',
                            'exclusiveMinimum': 0,
                        },
                        'product_uom': {'type': 'integer'},
                        'name': {'type': ['string', 'null']},
                    },
                    'required': [
                        'product_id',
                        'product_uom_qty',
                        'product_uom',
                    ],
                    'additionalProperties': False,
                },
            },
        },
        'required': [
            'picking_type_id',
            'location_id',
            'location_dest_id',
            'origin',
            'moves',
        ],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        self._validate_picking_header(env, args)
        moves = self._validate_moves(env, args.get('moves') or [])

        move_commands = [
            (
                0,
                0,
                {
                    'product_id': move['product_id'],
                    'product_uom_qty': move['product_uom_qty'],
                    'product_uom': move['product_uom'],
                    'description_picking': (
                        move.get('name')
                        or self._product_name(env, move['product_id'])
                    ),
                    'location_id': args['location_id'],
                    'location_dest_id': args['location_dest_id'],
                },
            )
            for move in moves
        ]
        picking_vals = {
            'picking_type_id': args['picking_type_id'],
            'location_id': args['location_id'],
            'location_dest_id': args['location_dest_id'],
            'origin': args['origin'],
            'move_ids': move_commands,
        }
        if args.get('scheduled_date'):
            picking_vals['scheduled_date'] = args['scheduled_date']

        picking = env['stock.picking'].create(picking_vals)
        picking.message_post(
            body=(
                'Черновик внутреннего перемещения создан AI-ассистентом '
                'по запросу %s. Строк: %s.'
            ) % (env.user.name, len(moves)),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'picking_id': picking.id,
            'name': picking.name,
            'url': '/odoo/stock.picking/%s' % picking.id,
        }

    def idempotency_key(self, args):
        payload = {
            'picking_type_id': args.get('picking_type_id'),
            'location_id': args.get('location_id'),
            'location_dest_id': args.get('location_dest_id'),
            'origin': args.get('origin'),
            'moves': sorted(
                args.get('moves') or [],
                key=lambda item: (
                    item.get('product_id') or 0,
                    item.get('product_uom_qty') or 0,
                    item.get('product_uom') or 0,
                    item.get('name') or '',
                ),
            ),
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _validate_picking_header(self, env, args):
        picking_type = env['stock.picking.type'].browse(
            args['picking_type_id']
        )
        if not picking_type.exists():
            raise ValidationError('Тип операции склада не найден.')
        if picking_type.code != 'internal':
            raise ValidationError(
                'Для перемещения нужен тип операции internal.'
            )
        self._validate_dest_location_is_object(env, args['location_dest_id'])

    def _validate_dest_location_is_object(self, env, location_dest_id):
        location = env['stock.location'].browse(location_dest_id)
        if not location.exists():
            raise ValidationError('Локация назначения не найдена.')
        warehouses = env['stock.warehouse'].search([
            ('code', 'ilike', 'ОбМ-'),
        ])
        for warehouse in warehouses:
            if location.id in env['stock.location'].search([
                ('id', 'child_of', warehouse.view_location_id.id),
            ]).ids:
                return
        raise ValidationError(
            'Локация назначения должна относиться к складу объекта ОбМ-*.'
        )

    def _validate_moves(self, env, moves):
        if not moves:
            raise ValidationError('Добавьте хотя бы одну строку перемещения.')
        for move in moves:
            if move.get('product_uom_qty', 0) <= 0:
                raise ValidationError(
                    'Количество в каждой строке перемещения должно быть '
                    'больше нуля.'
                )
            validate_product_is_storable(env, move['product_id'])
        return moves

    def _product_name(self, env, product_id):
        product = env['product.product'].browse(product_id)
        return product.display_name or product.name


default_registry.register(
    CreateInternalPickingDraftTool()
)


class PostChatterNoteTool(AbstractWriteTool):
    name = 'post_chatter_note'
    description = 'Добавить внутреннюю заметку в chatter разрешённой записи.'
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    allowed_models = {'object.request', 'purchase.order', 'stock.picking'}
    parameters_schema = {
        'type': 'object',
        'properties': {
            'model': {
                'type': 'string',
                'enum': [
                    'object.request',
                    'purchase.order',
                    'stock.picking',
                ],
            },
            'record_id': {'type': 'integer'},
            'body': {'type': 'string', 'minLength': 1, 'maxLength': 2000},
        },
        'required': ['model', 'record_id', 'body'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        model = args['model']
        if model not in self.allowed_models:
            raise ValidationError(
                'Заметки разрешены только для OR, PO и складских операций.'
            )
        record = env[model].browse(args['record_id']).exists()
        if not record:
            raise ValidationError('Запись для chatter не найдена.')
        record.message_post(
            body=args['body'],
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'model': model,
            'record_id': record.id,
            'message': 'posted',
        }

    def idempotency_key(self, args):
        payload = {
            'model': args.get('model'),
            'record_id': args.get('record_id'),
            'body': args.get('body'),
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()


default_registry.register(
    PostChatterNoteTool()
)
