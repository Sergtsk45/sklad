import hashlib
import json
from datetime import datetime, timedelta

from odoo.exceptions import AccessError, ValidationError

from .base import AbstractWriteTool
from .registry import default_registry
from .validators import (
    PARTNER_CATEGORIES,
    get_or_create_partner_tag,
    infer_is_company,
    normalize_partner_categories,
    normalize_phone,
    normalize_vat,
    validate_acc_number,
    validate_bic,
    validate_partner_create_args,
    validate_partner_is_supplier,
    validate_picking_type_for_purchase,
    validate_product_is_storable,
    validate_uom_is_meter,
    validate_vat_unique,
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
    description = 'Создать черновик заказа поставщику на указанный склад.'
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
        date_planned = (
            args.get('date_planned')
            or po.date_planned
            or (datetime.now() + timedelta(days=1)).strftime(
                '%Y-%m-%d 08:00:00'
            )
        )
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
                'Черновик закупки создан AI Assistant '
                '(AI-ассистентом) по запросу %s. Строк: %s.'
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
        validate_picking_type_for_purchase(env, args['picking_type_id'])
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


class CreatePartnerDraftTool(AbstractWriteTool):
    name = 'create_partner_draft'
    description = (
        'Создать нового контрагента res.partner. Перед вызовом всегда '
        'проверь дубликат через find_partner по ИНН. Если пользователь не '
        'указал категорию, сначала спроси: Поставщик, Заказчик, Покупатель '
        'или Подрядчик. Не обновляет существующих контрагентов.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1},
            'ref': {'type': ['string', 'null']},
            'vat': {
                'type': 'string',
                'pattern': r'^\D*\d(?:\D*\d){9}(?:(?:\D*\d){2})?\D*$',
            },
            'category': {
                'type': ['string', 'array'],
                'items': {'type': 'string', 'enum': list(PARTNER_CATEGORIES)},
            },
            'is_company': {'type': ['boolean', 'null']},
            'street': {'type': ['string', 'null']},
            'city': {'type': ['string', 'null']},
            'state_name': {'type': ['string', 'null']},
            'zip': {'type': ['string', 'null']},
            'phone': {'type': ['string', 'null']},
            'email': {'type': ['string', 'null']},
            'comment': {'type': ['string', 'null']},
        },
        'required': ['name', 'vat', 'category'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        errors = validate_partner_create_args(args)
        if errors:
            raise ValidationError('\n'.join(errors))

        vat = normalize_vat(args.get('vat'))
        duplicate_id = validate_vat_unique(env, vat)
        if duplicate_id:
            duplicate = env['res.partner'].browse(duplicate_id)
            raise ValidationError(
                'Контрагент с таким ИНН уже существует: ID %s, %s.'
                % (duplicate.id, duplicate.display_name)
            )

        name = (args.get('name') or '').strip()
        categories = normalize_partner_categories(args.get('category'))
        vals = {
            'name': name,
            'vat': vat,
            'is_company': self._is_company(args, name),
            'supplier_rank': 0,
            'customer_rank': 0,
        }
        self._apply_categories(env, vals, categories)
        self._apply_country_and_state(env, vals, vat, args.get('state_name'))
        for field_name in (
            'ref',
            'street',
            'city',
            'zip',
            'phone',
            'email',
            'comment',
        ):
            value = self._clean_optional(args.get(field_name))
            if value:
                if field_name == 'phone':
                    value = normalize_phone(value)
                vals[field_name] = value

        partner = env['res.partner'].create(vals)
        partner.message_post(
            body=(
                'Создано AI-ассистентом по запросу %s. Категории: %s.'
            ) % (env.user.name, ', '.join(categories)),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'partner_id': partner.id,
            'name': partner.display_name,
            'vat': partner.vat,
            'categories': categories,
            'url': '/odoo/res.partner/%s' % partner.id,
        }

    def idempotency_key(self, args):
        return hashlib.sha256(
            normalize_vat(args.get('vat')).encode('utf-8')
        ).hexdigest()

    def _is_company(self, args, name):
        if args.get('is_company') is not None:
            return bool(args.get('is_company'))
        return infer_is_company(name)

    def _clean_optional(self, value):
        if value is None:
            return ''
        return str(value).strip()

    def _apply_categories(self, env, vals, categories):
        tag_ids = []
        for category in categories:
            for rank_field, rank_value in PARTNER_CATEGORIES[category].items():
                vals[rank_field] = max(vals.get(rank_field, 0), rank_value)
            tag_ids.append(get_or_create_partner_tag(env, category).id)
        vals['category_id'] = [(6, 0, tag_ids)]

    def _apply_country_and_state(self, env, vals, vat, state_name=None):
        if len(vat or '') not in (10, 12):
            return
        country = self._russia(env)
        if not country:
            return
        vals['country_id'] = country.id
        state_name = self._clean_optional(state_name)
        if state_name:
            state = env['res.country.state'].search([
                ('country_id', '=', country.id),
                '|',
                ('name', '=ilike', state_name),
                ('name', 'ilike', state_name),
            ], limit=1)
            if state:
                vals['state_id'] = state.id

    def _russia(self, env):
        country = env.ref('base.ru', raise_if_not_found=False)
        if country:
            return country
        return env['res.country'].search([
            '|',
            ('code', '=', 'RU'),
            ('name', 'ilike', 'Россия'),
        ], limit=1)


default_registry.register(
    CreatePartnerDraftTool()
)


class UpdatePartnerDraftTool(AbstractWriteTool):
    name = 'update_partner_draft'
    description = (
        'Безопасно дополнить существующего контрагента. Заполняет только '
        'пустые поля, добавляет категорию/тег и повышает ранги 0→1. '
        'ИНН существующей записи не меняет.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'partner_id': {'type': 'integer'},
            'name': {'type': ['string', 'null']},
            'ref': {'type': ['string', 'null']},
            'vat': {'type': ['string', 'null']},
            'category': {
                'type': ['string', 'array', 'null'],
                'items': {'type': 'string', 'enum': list(PARTNER_CATEGORIES)},
            },
            'is_company': {'type': ['boolean', 'null']},
            'street': {'type': ['string', 'null']},
            'city': {'type': ['string', 'null']},
            'state_name': {'type': ['string', 'null']},
            'zip': {'type': ['string', 'null']},
            'phone': {'type': ['string', 'null']},
            'email': {'type': ['string', 'null']},
            'comment': {'type': ['string', 'null']},
        },
        'required': ['partner_id'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        partner = env['res.partner'].browse(args['partner_id']).exists()
        if not partner:
            raise ValidationError('Контрагент не найден.')

        self._validate_vat_unchanged(partner, args)
        vals = {}
        updated_fields = []
        skipped_fields = []
        for field_name in (
            'name',
            'ref',
            'street',
            'city',
            'zip',
            'phone',
            'email',
            'comment',
        ):
            value = self._clean_optional(args.get(field_name))
            if not value:
                continue
            if field_name == 'phone':
                value = normalize_phone(value)
            if self._is_empty(partner, field_name):
                vals[field_name] = value
                updated_fields.append(field_name)
            else:
                skipped_fields.append(field_name)

        if args.get('is_company') is not None:
            if self._is_empty(partner, 'is_company'):
                vals['is_company'] = bool(args['is_company'])
                updated_fields.append('is_company')
            else:
                skipped_fields.append('is_company')

        if args.get('state_name') and self._is_empty(partner, 'state_id'):
            state = self._find_state(env, partner, args['state_name'])
            if state:
                vals['state_id'] = state.id
                updated_fields.append('state_id')
        elif args.get('state_name'):
            skipped_fields.append('state_id')

        categories = []
        if args.get('category'):
            categories = normalize_partner_categories(args.get('category'))
            self._apply_category_update(env, partner, vals, categories)
            updated_fields.append('category')

        if vals:
            partner.write(vals)
        partner.message_post(
            body=(
                'Контрагент дополнен AI-ассистентом по запросу %s. '
                'Обновлено: %s. Пропущено: %s.'
            ) % (
                env.user.name,
                ', '.join(updated_fields) or 'нет',
                ', '.join(skipped_fields) or 'нет',
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'partner_id': partner.id,
            'name': partner.display_name,
            'url': '/odoo/res.partner/%s' % partner.id,
            'updated_fields': updated_fields,
            'skipped_fields': skipped_fields,
            'categories': categories,
        }

    def idempotency_key(self, args):
        payload = {
            'partner_id': args.get('partner_id'),
            'values': {
                key: args[key]
                for key in sorted(args)
                if key != 'partner_id'
            },
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _validate_vat_unchanged(self, partner, args):
        vat = normalize_vat(args.get('vat'))
        if vat and vat != (partner.vat or ''):
            raise ValidationError(
                'Изменение ИНН существующего контрагента запрещено.'
            )

    def _is_empty(self, record, field_name):
        value = record[field_name]
        return not bool(value)

    def _clean_optional(self, value):
        if value is None:
            return ''
        return str(value).strip()

    def _find_state(self, env, partner, state_name):
        country = partner.country_id or env.ref(
            'base.ru',
            raise_if_not_found=False,
        )
        domain = [
            '|',
            ('name', '=ilike', state_name),
            ('name', 'ilike', state_name),
        ]
        if country:
            domain = [('country_id', '=', country.id)] + domain
        return env['res.country.state'].search(domain, limit=1)

    def _apply_category_update(self, env, partner, vals, categories):
        tag_ids = list(partner.category_id.ids)
        for category in categories:
            for rank_field, rank_value in PARTNER_CATEGORIES[category].items():
                if getattr(partner, rank_field) < rank_value:
                    vals[rank_field] = rank_value
            tag = get_or_create_partner_tag(env, category)
            if tag.id not in tag_ids:
                tag_ids.append(tag.id)
        vals['category_id'] = [(6, 0, tag_ids)]


default_registry.register(
    UpdatePartnerDraftTool()
)


class AddPartnerBankDraftTool(AbstractWriteTool):
    name = 'add_partner_bank_draft'
    description = (
        'Добавить банковские реквизиты контрагента через плоские поля: '
        'partner_id, acc_number, bic, bank_name.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'partner_id': {'type': 'integer'},
            'acc_number': {'type': 'string', 'minLength': 1},
            'bic': {'type': 'string', 'minLength': 1},
            'bank_name': {'type': 'string', 'minLength': 1},
            'acc_holder_name': {'type': ['string', 'null']},
            'note': {'type': ['string', 'null']},
        },
        'required': ['partner_id', 'acc_number', 'bic', 'bank_name'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        partner = env['res.partner'].browse(args['partner_id']).exists()
        if not partner:
            raise ValidationError('Контрагент не найден.')
        acc_number = validate_acc_number(args.get('acc_number'))
        bic = validate_bic(args.get('bic'))
        duplicate = env['res.partner.bank'].search([
            ('partner_id', '=', partner.id),
            ('acc_number', '=', acc_number),
        ], limit=1)
        if duplicate:
            raise ValidationError(
                'Банковский счёт уже добавлен этому контрагенту.'
            )
        bank = self._get_or_create_bank(env, args['bank_name'], bic)
        bank_vals = {
            'partner_id': partner.id,
            'acc_number': acc_number,
            'bank_id': bank.id,
        }
        acc_holder_name = (args.get('acc_holder_name') or '').strip()
        if acc_holder_name:
            bank_vals['acc_holder_name'] = acc_holder_name
        partner_bank = env['res.partner.bank'].create(bank_vals)
        note = (args.get('note') or '').strip()
        if note:
            partner.comment = self._append_note(
                partner.comment,
                'Банковские реквизиты: %s' % note,
            )
        partner.message_post(
            body=(
                'Банковские реквизиты добавлены AI-ассистентом по запросу %s.'
            ) % env.user.name,
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'partner_bank_id': partner_bank.id,
            'partner_id': partner.id,
            'name': partner.display_name,
            'url': '/odoo/res.partner/%s' % partner.id,
        }

    def idempotency_key(self, args):
        raw_payload = json.dumps(
            {
                'partner_id': args.get('partner_id'),
                'acc_number': validate_acc_number(args.get('acc_number')),
                'bic': validate_bic(args.get('bic')),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _get_or_create_bank(self, env, bank_name, bic):
        bank = env['res.bank'].search([('bic', '=', bic)], limit=1)
        if bank:
            return bank
        vals = {'name': bank_name.strip(), 'bic': bic}
        country = env.ref('base.ru', raise_if_not_found=False)
        if country:
            vals['country'] = country.id
        return env['res.bank'].create(vals)

    def _append_note(self, current, note):
        current = (current or '').strip()
        if not current:
            return note
        if note in current:
            return current
        return current + '\n' + note


default_registry.register(
    AddPartnerBankDraftTool()
)


class AddPartnerContactDraftTool(AbstractWriteTool):
    name = 'add_partner_contact_draft'
    description = (
        'Добавить контактное лицо контрагента как дочерний res.partner.'
    )
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'partner_id': {'type': 'integer'},
            'name': {'type': 'string', 'minLength': 1},
            'function': {'type': ['string', 'null']},
            'phone': {'type': ['string', 'null']},
            'email': {'type': ['string', 'null']},
        },
        'required': ['partner_id', 'name'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        partner = env['res.partner'].browse(args['partner_id']).exists()
        if not partner:
            raise ValidationError('Контрагент не найден.')
        name = (args.get('name') or '').strip()
        duplicate = env['res.partner'].search([
            ('parent_id', '=', partner.id),
            ('name', '=ilike', name),
        ], limit=1)
        if duplicate:
            raise ValidationError(
                'Контактное лицо с таким именем уже есть у контрагента.'
            )
        vals = {
            'parent_id': partner.id,
            'type': 'contact',
            'name': name,
        }
        for field_name in ('function', 'phone', 'email'):
            value = (args.get(field_name) or '').strip()
            if value:
                if field_name == 'phone':
                    value = normalize_phone(value)
                vals[field_name] = value
        contact = env['res.partner'].create(vals)
        partner.message_post(
            body=(
                'Контактное лицо добавлено AI-ассистентом по запросу %s: %s.'
            ) % (env.user.name, contact.display_name),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'contact_id': contact.id,
            'partner_id': partner.id,
            'name': contact.display_name,
            'url': '/odoo/res.partner/%s' % partner.id,
        }

    def idempotency_key(self, args):
        raw_payload = json.dumps(
            {
                'partner_id': args.get('partner_id'),
                'name': (args.get('name') or '').strip().lower(),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()


default_registry.register(
    AddPartnerContactDraftTool()
)


class CreateProductDraftTool(AbstractWriteTool):
    name = 'create_product_draft'
    description = (
        'Создать черновик номенклатуры product.product '
        '(storable, purchase_ok).'
    )
    required_groups = ['ai_assistant.group_ai_assistant_supply']
    parameters_schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1},
            'categ_id': {'type': ['integer', 'null']},
            'uom_id': {'type': ['integer', 'null']},
            'list_price': {'type': ['number', 'null']},
            'standard_price': {'type': ['number', 'null']},
            'default_code': {'type': ['string', 'null']},
            'purchase_ok': {'type': 'boolean'},
            'sale_ok': {'type': 'boolean'},
        },
        'required': ['name'],
        'additionalProperties': False,
    }

    def execute(self, env, args):
        _ensure_tool_required_groups(self, env)
        name = (args.get('name') or '').strip()
        if not name:
            raise ValidationError('Укажите наименование товара.')

        categ_id = args.get('categ_id') or self._default_category_id(env)
        uom_id = args.get('uom_id') or self._default_uom_id(env)
        self._validate_category(env, categ_id)
        self._validate_uom(env, uom_id)
        self._ensure_no_duplicate(env, name, categ_id)

        product_vals = {
            'name': name,
            'is_storable': True,
            'categ_id': categ_id,
            'uom_id': uom_id,
            'purchase_ok': args.get('purchase_ok', True),
            'sale_ok': args.get('sale_ok', False),
        }
        list_price = args.get('list_price')
        if list_price is not None:
            product_vals['list_price'] = list_price
        standard_price = args.get('standard_price')
        if standard_price is not None:
            product_vals['standard_price'] = standard_price
        elif list_price is not None:
            product_vals['standard_price'] = list_price
        default_code = (args.get('default_code') or '').strip()
        if default_code:
            product_vals['default_code'] = default_code

        product = env['product.product'].create(product_vals)
        product.product_tmpl_id.message_post(
            body=(
                'Товар создан AI-ассистентом по запросу %s.'
            ) % env.user.name,
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        return {
            'product_id': product.id,
            'name': product.display_name,
            'url': '/odoo/product.product/%s' % product.id,
        }

    def idempotency_key(self, args):
        payload = {
            'name': (args.get('name') or '').strip(),
            'categ_id': args.get('categ_id') or 0,
        }
        raw_payload = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(',', ':'),
        )
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def _default_category_id(self, env):
        category = env.ref(
            'product.product_category_goods',
            raise_if_not_found=False,
        )
        if category:
            return category.id
        category = env['product.category'].search([], limit=1)
        if not category:
            raise ValidationError('Категория товаров по умолчанию не найдена.')
        return category.id

    def _default_uom_id(self, env):
        return env.ref('uom.product_uom_unit').id

    def _validate_category(self, env, categ_id):
        category = env['product.category'].browse(categ_id)
        if not category.exists():
            raise ValidationError('Категория товара не найдена.')

    def _validate_uom(self, env, uom_id):
        uom = env['uom.uom'].browse(uom_id)
        if not uom.exists():
            raise ValidationError('Единица измерения не найдена.')

    def _ensure_no_duplicate(self, env, name, categ_id):
        duplicate = env['product.product'].search([
            ('name', '=ilike', name),
            ('categ_id', '=', categ_id),
        ], limit=1)
        if duplicate:
            raise ValidationError(
                'Товар с таким наименованием уже существует: %s.'
                % duplicate.display_name
            )


default_registry.register(
    CreateProductDraftTool()
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
        projects = env['object.request.project'].with_context(
            active_test=False
        ).search([('warehouse_id', '!=', False)])
        for warehouse in projects.mapped('warehouse_id'):
            if location.id in env['stock.location'].search([
                ('id', 'child_of', warehouse.view_location_id.id),
            ]).ids:
                return
        raise ValidationError(
            'Локация назначения должна относиться к складу объекта.'
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
