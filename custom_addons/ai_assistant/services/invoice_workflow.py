# @file: invoice_workflow.py
# @description: Пошаговое создание номенклатуры и PO по счёту.
# @dependencies: invoice_context_helper, invoice_extraction_store
# @created: 2026-05-31

import base64

from odoo.exceptions import ValidationError

from odoo.addons.ai_assistant.services.action_tools.write_tools import (
    CreatePurchaseOrderDraftTool,
)
from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindWarehouseTool,
)
from odoo.addons.ai_assistant.services.pipe_qty_converter import (
    convert_pipe_quantity,
)
from odoo.addons.ai_assistant.services.invoice_context_helper import (
    InvoiceContextHelper,
)

_UOM_BY_UNIT = {
    'шт': 'uom.product_uom_unit',
    'штука': 'uom.product_uom_unit',
    'штуки': 'uom.product_uom_unit',
    'м': 'uom.product_uom_meter',
    'метр': 'uom.product_uom_meter',
    'метры': 'uom.product_uom_meter',
    'кг': 'uom.product_uom_kgm',
    'kg': 'uom.product_uom_kgm',
    'л': 'uom.product_uom_litre',
    'л.': 'uom.product_uom_litre',
}


class InvoiceWorkflow:
    """Сессия счёта: по одному товару, затем предложение PO."""

    ACTION_CREATE_PARTNER = 'invoice_create_partner'
    ACTION_NEXT_PRODUCT = 'invoice_next_product'
    ACTION_PREPARE_PO = 'invoice_prepare_po'
    ACTION_PO_START = 'invoice_po_start'
    ACTION_PO_SELECT_WAREHOUSE = 'invoice_po_select_warehouse'
    ACTION_PO_SET_ATTACH_INVOICE = 'invoice_po_set_attach_invoice'
    ACTION_PO_SET_RECEIVE_PICKING = 'invoice_po_set_receive_picking'
    ACTION_PO_EXECUTE_PLAN = 'invoice_po_execute_plan'
    ACTION_PO_CANCEL = 'invoice_po_cancel'

    FLOW_IDLE = 'idle'
    FLOW_AWAITING_CREATE_PO = 'awaiting_create_po'
    FLOW_AWAITING_WAREHOUSE = 'awaiting_warehouse'
    FLOW_AWAITING_ATTACH = 'awaiting_attach_invoice'
    FLOW_AWAITING_RECEIPT = 'awaiting_receive_picking'
    FLOW_AWAITING_EXECUTE = 'awaiting_execute'
    FLOW_DONE = 'done'
    FLOW_CANCELLED = 'cancelled'
    FLOW_EXECUTED = 'executed'

    def __init__(self, env, invoice_store):
        self.env = env
        self._store = invoice_store
        self._context_helper = InvoiceContextHelper(env, invoice_store)
        self._find_warehouse = FindWarehouseTool()

    def attach_to_product_draft(self, uid, extraction_token, args):
        """Дополнить args ценой/UoM из счёта; вернуть metadata для pending."""
        _context, line, line_key = self._resolve_draft_line(
            uid, extraction_token, args
        )
        if not line:
            return args, {}
        enriched = dict(args or {})
        enriched.update(self.build_product_draft_args(line))
        metadata = {
            'extraction_token': extraction_token,
            'invoice_line_key': line_key,
        }
        return enriched, metadata

    def build_product_draft_args(self, line):
        name = (line.get('name') or '').strip()
        args = {
            'name': name,
            'purchase_ok': True,
        }
        price = line.get('price')
        if price is not None:
            try:
                args['list_price'] = float(price)
            except (TypeError, ValueError):
                pass
        article = (line.get('article') or '').strip()
        if article:
            args['default_code'] = article[:64]
        uom_id = self._resolve_uom_id(line.get('unit'))
        if uom_id:
            args['uom_id'] = uom_id
        return args

    def record_product_created(
        self, uid, extraction_token, line_key, product_id
    ):
        session = self._store.ensure_session(uid, extraction_token)
        session['created_by_line'][str(line_key)] = product_id

    def record_partner_created(self, uid, extraction_token, partner_id):
        session = self._store.ensure_session(uid, extraction_token)
        if session is not None:
            session['created_partner_id'] = partner_id

    def partner_ready(self, uid, extraction_token):
        context = self._context_helper.fetch_context(uid, extraction_token)
        return bool(self._resolve_partner_id(context, uid, extraction_token))

    def next_partner_draft(self, uid, extraction_token=None):
        token = extraction_token or self._store.find_latest_token(uid)
        if not token:
            return None
        context = self._context_helper.fetch_context(uid, token)
        partner = (context or {}).get('partner') or {}
        if partner.get('status') == 'matched':
            return None
        session = self._store.get_session(uid, token) or {}
        if session.get('created_partner_id'):
            return None
        if partner.get('needs_create_partner_draft'):
            return {
                'token': token,
                'args': partner.get('partner_draft_args') or {},
                'partner_name': (
                    partner.get('extracted_name')
                    or (partner.get('partner_draft_args') or {}).get('name')
                    or ''
                ),
            }
        return None

    def suggestions_after_product_created(self, uid, extraction_token):
        next_line = self._next_line_to_create(uid, extraction_token)
        if next_line:
            short_name = self._short_name(next_line['name'])
            return [{
                'label': 'Создать следующий: %s' % short_name,
                'action': self.ACTION_NEXT_PRODUCT,
            }]
        if self.all_products_ready(uid, extraction_token):
            return self.purchase_start_suggestions(uid, extraction_token)
        return []

    def suggestions_after_partner_created(self, uid, extraction_token):
        next_line = self._next_line_to_create(uid, extraction_token)
        if next_line:
            short_name = self._short_name(next_line['name'])
            return [{
                'label': 'Создать товар: %s' % short_name,
                'action': self.ACTION_NEXT_PRODUCT,
            }]
        if self.all_products_ready(uid, extraction_token):
            return self.purchase_start_suggestions(uid, extraction_token)
        return []

    def next_product_draft(self, uid, extraction_token=None):
        """
        Следующая позиция для create_product_draft.

        Returns dict with keys args, line_key, token or None if done.
        """
        token = extraction_token or self._store.find_latest_token(uid)
        if not token:
            return None
        line = self._next_line_to_create(uid, token)
        if not line:
            return None
        idx = line['_index']
        line_key = self._line_key(line, idx)
        return {
            'token': token,
            'line_key': line_key,
            'args': self.build_product_draft_args(line),
            'line_name': line.get('name') or '',
        }

    def all_products_done_payload(self):
        return {
            'answer': (
                'Все позиции счёта уже есть в номенклатуре. '
                'Можно перейти к закупке.'
            ),
            'suggestions': self._po_start_yes_no_suggestions(),
            'cards': [],
            'meta': {'status': 'all_products_ready'},
        }

    def current_purchase_flow_state(self, uid, extraction_token):
        session = self._store.ensure_session(uid, extraction_token) or {}
        flow = session.get('purchase_flow') or {}
        return dict(flow)

    def purchase_start_suggestions(self, uid, extraction_token):
        self._ensure_purchase_flow(uid, extraction_token)
        return [{
            'label': 'Создать закупку?',
            'action': self.ACTION_PO_START,
            'payload': {'create_po': True},
        }, {
            'label': 'Нет',
            'action': self.ACTION_PO_START,
            'payload': {'create_po': False},
        }]

    def begin_purchase_flow_prompt(self, uid, extraction_token):
        if not self._ready_for_purchase(uid, extraction_token):
            return self._not_ready_response(uid, extraction_token)
        self._ensure_purchase_flow(uid, extraction_token)
        return {
            'status': self.FLOW_AWAITING_CREATE_PO,
            'answer': 'Создать закупку?',
            'suggestions': self._po_start_yes_no_suggestions(),
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def set_create_po_decision(self, uid, extraction_token, create_po):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('executed') or flow.get('state') == self.FLOW_EXECUTED:
            return self._already_finished_response(uid, extraction_token)
        flow['create_po'] = bool(create_po)
        if not create_po:
            flow['state'] = self.FLOW_DONE
            return {
                'status': self.FLOW_DONE,
                'answer': (
                    'Решение сохранено: закупку не создавать. '
                    'Сценарий завершён без изменений в Odoo.'
                ),
                'suggestions': [],
                'cards': [],
                'meta': self._flow_meta(uid, extraction_token),
            }
        flow['state'] = self.FLOW_AWAITING_WAREHOUSE
        return self.ask_warehouse(uid, extraction_token)

    def ask_warehouse(self, uid, extraction_token, error=None):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        flow['state'] = self.FLOW_AWAITING_WAREHOUSE
        suggestions = []
        warehouses = self.env['stock.warehouse'].search_read(
            [],
            ['id', 'name', 'code', 'in_type_id'],
            limit=5,
        )
        for wh in warehouses:
            label = '%s (%s)' % (wh.get('name'), wh.get('code'))
            suggestions.append({
                'label': self._short_name(label),
                'action': self.ACTION_PO_SELECT_WAREHOUSE,
                'payload': {'warehouse_id': wh['id']},
            })
        answer = error or 'Какой склад? Укажите код или название склада.'
        return {
            'status': self.FLOW_AWAITING_WAREHOUSE,
            'answer': answer,
            'suggestions': suggestions,
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token, {
                'awaiting_po_warehouse': True,
            }),
        }

    def select_warehouse(self, uid, extraction_token, payload=None,
                         warehouse_query=None):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('create_po') is not True:
            return self.begin_purchase_flow_prompt(uid, extraction_token)
        payload = payload or {}
        warehouse = None
        if payload.get('warehouse_id'):
            record = self.env['stock.warehouse'].browse(
                payload['warehouse_id']
            )
            if record.exists():
                warehouse = self._warehouse_payload(record)
        query = (
            payload.get('warehouse_query')
            or payload.get('warehouse_name')
            or warehouse_query
            or ''
        ).strip()
        if not warehouse:
            if not query:
                return self.ask_warehouse(uid, extraction_token)
            warehouses = self._find_warehouse.execute(
                self.env,
                {'query': query},
            ).get('warehouses') or []
            if not warehouses:
                return self.ask_warehouse(
                    uid,
                    extraction_token,
                    'Склад «%s» не найден. Уточните код или название.' % query,
                )
            if len(warehouses) > 1:
                return self._warehouse_ambiguous_response(
                    uid, extraction_token, warehouses
                )
            warehouse = warehouses[0]
        picking_type_id = self._warehouse_picking_type_id(warehouse)
        if not picking_type_id:
            return self.ask_warehouse(
                uid,
                extraction_token,
                'У склада «%s» не найден тип операции поступления.'
                % (warehouse.get('name') or warehouse.get('code')),
            )
        flow.update({
            'state': self.FLOW_AWAITING_ATTACH,
            'warehouse_id': warehouse['id'],
            'warehouse_name': warehouse.get('name') or warehouse.get('code'),
            'picking_type_id': picking_type_id,
        })
        return {
            'status': self.FLOW_AWAITING_ATTACH,
            'answer': (
                'Создать закупку на склад «%s». Привязать счёт?'
            ) % flow['warehouse_name'],
            'suggestions': self._yes_no_suggestions(
                self.ACTION_PO_SET_ATTACH_INVOICE,
                'attach_invoice',
            ),
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token, {
                'awaiting_po_warehouse': False,
                'warehouse_id': flow['warehouse_id'],
            }),
        }

    def set_attach_invoice_decision(self, uid, extraction_token, value):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('state') != self.FLOW_AWAITING_ATTACH:
            return self._unexpected_flow_response(uid, extraction_token)
        flow['attach_invoice'] = bool(value)
        flow['state'] = self.FLOW_AWAITING_RECEIPT
        return {
            'status': self.FLOW_AWAITING_RECEIPT,
            'answer': 'Решение сохранено. Провести приёмку на склад?',
            'suggestions': self._yes_no_suggestions(
                self.ACTION_PO_SET_RECEIVE_PICKING,
                'receive_picking',
            ),
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def set_receive_picking_decision(self, uid, extraction_token, value):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('state') != self.FLOW_AWAITING_RECEIPT:
            return self._unexpected_flow_response(uid, extraction_token)
        flow['receive_picking'] = bool(value)
        flow['state'] = self.FLOW_AWAITING_EXECUTE
        return self.purchase_plan_response(uid, extraction_token)

    def purchase_plan_response(self, uid, extraction_token):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        answer = self._summary_text(uid, extraction_token, flow)
        return {
            'status': self.FLOW_AWAITING_EXECUTE,
            'answer': answer,
            'suggestions': [{
                'label': 'Выполнить',
                'action': self.ACTION_PO_EXECUTE_PLAN,
                'payload': {},
            }, {
                'label': 'Отмена',
                'action': self.ACTION_PO_CANCEL,
                'payload': {},
            }],
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def cancel_purchase_flow(self, uid, extraction_token):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('executed'):
            return self._already_finished_response(uid, extraction_token)
        flow['state'] = self.FLOW_CANCELLED
        return {
            'status': self.FLOW_CANCELLED,
            'answer': 'Итоговый план отменён. Изменений в Odoo нет.',
            'suggestions': [],
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def execute_purchase_plan(self, uid, extraction_token):
        flow = self._ensure_purchase_flow(uid, extraction_token)
        if flow.get('executed'):
            return self._executed_response(flow)
        self._validate_plan_ready(flow)
        po = self._ensure_confirmed_po(uid, extraction_token, flow)
        picking = None
        if flow.get('receive_picking'):
            picking = self._receive_po_picking(po)
            flow['picking_id'] = picking.id if picking else None
        attachment = None
        bill = None
        if flow.get('attach_invoice'):
            attachment, bill = self._bind_vendor_bill(
                uid, extraction_token, po
            )
            flow['attachment_id'] = attachment.id if attachment else None
            flow['bill_id'] = bill.id if bill else None
        steps = self._execution_steps(po, attachment, bill, picking)
        po.message_post(
            body='AI-ассистент выполнил план по счёту:<br/>%s'
            % '<br/>'.join(steps),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        flow['state'] = self.FLOW_EXECUTED
        flow['executed'] = True
        return {
            'status': self.FLOW_EXECUTED,
            'answer': (
                'План выполнен.\n'
                + '\n'.join('• %s' % s for s in steps)
            ),
            'suggestions': [],
            'cards': [self._execution_result_card(
                po, attachment, picking, bill
            )],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def _ensure_confirmed_po(self, uid, extraction_token, flow):
        context = self._context_helper.fetch_context(uid, extraction_token)
        warehouse = {
            'id': flow['warehouse_id'],
            'name': flow['warehouse_name'],
            'in_type_id': flow['picking_type_id'],
        }
        po_args = self._build_po_args(
            context, uid, extraction_token, warehouse
        )
        if flow.get('po_id'):
            po = self.env['purchase.order'].browse(flow['po_id'])
        else:
            tool = CreatePurchaseOrderDraftTool()
            result = tool.execute(self.env, po_args)
            po = self.env['purchase.order'].browse(result['po_id'])
            flow['po_id'] = po.id
        if po.state in ('draft', 'sent'):
            po.button_confirm()
        return po

    def prepare_po_draft(self, uid, extraction_token, warehouse_query=None):
        """
        Подготовить args для create_purchase_order_draft.
        """
        if not self.partner_ready(uid, extraction_token):
            draft = self.next_partner_draft(uid, extraction_token)
            suggestions = []
            if draft:
                suggestions = [{
                    'label': 'Создать поставщика из счёта',
                    'action': self.ACTION_CREATE_PARTNER,
                }]
            return {
                'status': 'partner_incomplete',
                'answer': (
                    'Сначала нужно создать поставщика из реквизитов счёта.'
                ),
                'suggestions': suggestions,
                'meta': {'partner_incomplete': True},
            }
        query = (warehouse_query or '').strip()
        if not query:
            return {
                'status': 'awaiting_po_warehouse',
                'answer': (
                    'Укажите код или название склада приёмки '
                    '(например, Ос.ск или O002; '
                    'legacy ОбМ-4 тоже работает).'
                ),
                'meta': {'awaiting_po_warehouse': True},
            }
        if not self.all_products_ready(uid, extraction_token):
            return {
                'status': 'products_incomplete',
                'answer': (
                    'Сначала создайте номенклатуру по всем позициям счёта.'
                ),
                'suggestions': self.suggestions_after_product_created(
                    uid, extraction_token
                ),
            }
        context = self._context_helper.fetch_context(uid, extraction_token)
        warehouses = self._find_warehouse.execute(
            self.env,
            {'query': query},
        ).get('warehouses') or []
        if not warehouses:
            return {
                'status': 'warehouse_not_found',
                'answer': (
                    'Склад «%s» не найден. Уточните код или название.'
                ) % query,
                'meta': {'awaiting_po_warehouse': True},
            }
        if len(warehouses) > 1:
            names = ', '.join(
                '%s (%s)' % (wh.get('name'), wh.get('code'))
                for wh in warehouses[:5]
            )
            return {
                'status': 'warehouse_ambiguous',
                'answer': (
                    'Найдено несколько складов: %s. Уточните запрос.'
                ) % names,
                'meta': {'awaiting_po_warehouse': True},
            }
        warehouse = warehouses[0]
        try:
            po_args = self._build_po_args(
                context, uid, extraction_token, warehouse
            )
        except ValidationError as err:
            return {
                'status': 'error',
                'answer': str(err),
            }
        return {
            'status': 'pending',
            'answer': (
                'Черновик закупки на склад «%s». Проверьте и подтвердите.'
            ) % (warehouse.get('name') or warehouse.get('code')),
            'po_args': po_args,
            'warehouse_id': warehouse['id'],
        }

    def all_products_ready(self, uid, extraction_token):
        context = self._context_helper.fetch_context(uid, extraction_token)
        if not context:
            return False
        session = self._store.get_session(uid, extraction_token) or {}
        created = session.get('created_by_line') or {}
        for idx, line in enumerate(context.get('items') or []):
            line_key = self._line_key(line, idx)
            product_id = self._product_id_for_line(line, line_key, created)
            if not product_id:
                return False
        return True

    def _next_line_to_create(self, uid, extraction_token):
        context = self._context_helper.fetch_context(uid, extraction_token)
        if not context:
            return None
        session = self._store.get_session(uid, extraction_token) or {}
        created = session.get('created_by_line') or {}
        for idx, line in enumerate(context.get('items') or []):
            product = line.get('product') or {}
            if not product.get('needs_create_product_draft'):
                continue
            line_key = self._line_key(line, idx)
            if str(line_key) in created:
                continue
            if self._product_id_for_line(line, line_key, created):
                continue
            enriched = dict(line)
            enriched['_index'] = idx
            return enriched
        return None

    def _resolve_draft_line(self, uid, extraction_token, args):
        context = self._context_helper.fetch_context(uid, extraction_token)
        if not context:
            return None, None, None
        name = (args.get('name') or '').strip().lower()
        if name:
            for idx, line in enumerate(context.get('items') or []):
                line_name = (line.get('name') or '').strip().lower()
                if line_name == name or name in line_name or line_name in name:
                    return context, line, self._line_key(line, idx)
        next_line = self._next_line_to_create(uid, extraction_token)
        if next_line:
            idx = next_line['_index']
            return context, next_line, self._line_key(next_line, idx)
        return context, None, None

    def _build_po_args(self, context, uid, extraction_token, warehouse):
        partner_id = self._resolve_partner_id(context, uid, extraction_token)
        if not partner_id:
            raise ValidationError(
                'Поставщик счёта не найден в Odoo. Создайте контрагента.'
            )
        session = self._store.get_session(uid, extraction_token) or {}
        created = session.get('created_by_line') or {}
        lines = []
        for idx, item in enumerate(context.get('items') or []):
            line_key = self._line_key(item, idx)
            product_id = self._product_id_for_line(item, line_key, created)
            if not product_id:
                raise ValidationError(
                    'Не для всех позиций счёта есть товар: %s'
                    % (item.get('name') or idx + 1)
                )
            product = self.env['product.product'].browse(product_id)
            qty = item.get('qty') or 0
            try:
                qty = float(qty)
            except (TypeError, ValueError):
                qty = 0
            if qty <= 0:
                raise ValidationError(
                    'Некорректное количество в позиции: %s'
                    % (item.get('name') or idx + 1)
                )
            price = item.get('price') or 0
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = 0.0
            if self._is_pipe_product(product):
                qty, uom_id = self._convert_pipe_item(item, product)
            else:
                uom_id = (
                    self._resolve_uom_id(item.get('unit'))
                    or product.uom_id.id
                )
            lines.append({
                'product_id': product_id,
                'product_qty': qty,
                'product_uom': uom_id,
                'price_unit': price,
                'name': item.get('name') or product.display_name,
            })
        invoice_number = context.get('invoice_number') or 'INVOICE'
        origin = '%s/AIA' % invoice_number
        in_type = warehouse.get('in_type_id')
        picking_type_id = (
            in_type[0] if isinstance(in_type, (list, tuple)) else in_type
        )
        return {
            'partner_id': partner_id,
            'picking_type_id': picking_type_id,
            'origin': origin,
            'partner_ref': str(invoice_number),
            'lines': lines,
        }

    def _resolve_partner_id(self, context, uid=None, extraction_token=None):
        partner = (context or {}).get('partner') or {}
        if partner.get('status') == 'matched':
            return partner.get('partner_id')
        if uid and extraction_token:
            session = self._store.get_session(uid, extraction_token) or {}
            if session.get('created_partner_id'):
                return session['created_partner_id']
        return None

    def _product_id_for_line(self, line, line_key, created):
        product = line.get('product') or {}
        if product.get('status') == 'matched' and product.get('product_id'):
            return product['product_id']
        return created.get(str(line_key))

    def _line_key(self, line, index):
        line_no = line.get('line_no')
        if line_no is not None and line_no != '':
            return str(line_no)
        return 'idx_%s' % index

    def _resolve_uom_id(self, unit):
        token = (unit or '').strip().lower()
        if not token:
            return None
        xmlid = _UOM_BY_UNIT.get(token)
        if not xmlid:
            return None
        uom = self.env.ref(xmlid, raise_if_not_found=False)
        return uom.id if uom else None

    def _is_pipe_product(self, product):
        if not product or not product.exists():
            return False
        category = (product.categ_id.complete_name or product.categ_id.name or '')
        category = category.lower()
        feature = getattr(product.product_tmpl_id, 'or_product_family', False)
        return 'труб' in category or feature == 'pipe'

    def _convert_pipe_item(self, item, product):
        description = ' '.join(
            part for part in (
                item.get('name'),
                product.display_name,
            ) if part
        )
        conversion = convert_pipe_quantity(
            item.get('qty'),
            item.get('unit'),
            kg_per_meter=product.product_tmpl_id.kg_per_meter,
            description=description,
        )
        return conversion['meters'], self.env.ref(
            'uom.product_uom_meter'
        ).id

    def _short_name(self, name, limit=48):
        text = (name or '').strip()
        if len(text) <= limit:
            return text
        return text[: limit - 1] + '…'

    def _ensure_purchase_flow(self, uid, extraction_token):
        session = self._store.ensure_session(uid, extraction_token) or {}
        flow = session.get('purchase_flow')
        if not flow:
            flow = self._store.reset_purchase_flow(uid, extraction_token)
        if flow.get('state') == self.FLOW_IDLE and self._ready_for_purchase(
            uid, extraction_token
        ):
            flow['state'] = self.FLOW_AWAITING_CREATE_PO
        return flow

    def _ready_for_purchase(self, uid, extraction_token):
        return (
            self.partner_ready(uid, extraction_token)
            and self.all_products_ready(uid, extraction_token)
        )

    def _not_ready_response(self, uid, extraction_token):
        if not self.partner_ready(uid, extraction_token):
            return {
                'status': 'partner_incomplete',
                'answer': 'Сначала нужно создать поставщика из счёта.',
                'suggestions': [{
                    'label': 'Создать поставщика из счёта',
                    'action': self.ACTION_CREATE_PARTNER,
                }],
                'cards': [],
                'meta': {'status': 'partner_incomplete'},
            }
        return {
            'status': 'products_incomplete',
            'answer': 'Сначала создайте номенклатуру по всем позициям счёта.',
            'suggestions': self.suggestions_after_product_created(
                uid, extraction_token
            ),
            'cards': [],
            'meta': {'status': 'products_incomplete'},
        }

    def _flow_meta(self, uid, extraction_token, extra=None):
        meta = {
            'status': self.current_purchase_flow_state(
                uid, extraction_token
            ).get('state'),
            'purchase_flow': self.current_purchase_flow_state(
                uid, extraction_token
            ),
        }
        if extra:
            meta.update(extra)
        return meta

    def _po_start_yes_no_suggestions(self):
        return self._yes_no_suggestions(self.ACTION_PO_START, 'create_po')

    def _yes_no_suggestions(self, action, payload_key):
        return [{
            'label': 'Да',
            'action': action,
            'payload': {payload_key: True},
        }, {
            'label': 'Нет',
            'action': action,
            'payload': {payload_key: False},
        }]

    def _warehouse_payload(self, warehouse):
        return {
            'id': warehouse.id,
            'name': warehouse.name,
            'code': warehouse.code,
            'in_type_id': warehouse.in_type_id.id,
        }

    def _warehouse_picking_type_id(self, warehouse):
        in_type = warehouse.get('in_type_id')
        if isinstance(in_type, (list, tuple)):
            return in_type[0] if in_type else None
        return in_type

    def _warehouse_ambiguous_response(self, uid, extraction_token, warehouses):
        suggestions = []
        for wh in warehouses[:5]:
            label = '%s (%s)' % (wh.get('name'), wh.get('code'))
            suggestions.append({
                'label': self._short_name(label),
                'action': self.ACTION_PO_SELECT_WAREHOUSE,
                'payload': {'warehouse_id': wh['id']},
            })
        names = ', '.join(
            '%s (%s)' % (wh.get('name'), wh.get('code'))
            for wh in warehouses[:5]
        )
        return {
            'status': 'warehouse_ambiguous',
            'answer': (
                'Найдено несколько складов: %s. Выберите нужный.'
            ) % names,
            'suggestions': suggestions,
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token, {
                'awaiting_po_warehouse': True,
            }),
        }

    def _unexpected_flow_response(self, uid, extraction_token):
        flow = self.current_purchase_flow_state(uid, extraction_token)
        return {
            'status': flow.get('state') or 'unexpected_state',
            'answer': (
                'Это действие уже неактуально для текущего сценария. '
                'Текущее состояние: %s.'
            ) % (flow.get('state') or 'неизвестно'),
            'suggestions': [],
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def _already_finished_response(self, uid, extraction_token):
        return {
            'status': 'already_finished',
            'answer': 'Сценарий уже завершён / действие уже выполнено.',
            'suggestions': [],
            'cards': [],
            'meta': self._flow_meta(uid, extraction_token),
        }

    def _executed_response(self, flow):
        po = self.env['purchase.order'].browse(flow.get('po_id'))
        attachment = self.env['ir.attachment'].browse(
            flow.get('attachment_id')
        )
        picking = self.env['stock.picking'].browse(flow.get('picking_id'))
        bill = self.env['account.move'].browse(flow.get('bill_id'))
        return {
            'status': self.FLOW_EXECUTED,
            'answer': 'Сценарий уже выполнен. Дубликаты не созданы.',
            'suggestions': [],
            'cards': [self._execution_result_card(
                po, attachment, picking, bill
            )],
            'meta': {'status': self.FLOW_EXECUTED, 'purchase_flow': flow},
        }

    def _validate_plan_ready(self, flow):
        if flow.get('state') != self.FLOW_AWAITING_EXECUTE:
            raise ValidationError(
                'План ещё не готов: ответьте на все вопросы сценария.'
            )
        if flow.get('create_po') is not True:
            raise ValidationError('Создание закупки не подтверждено.')
        if not flow.get('warehouse_id') or not flow.get('picking_type_id'):
            raise ValidationError('Склад закупки не выбран.')
        if flow.get('attach_invoice') is None:
            raise ValidationError('Не выбран ответ по привязке счёта.')
        if flow.get('receive_picking') is None:
            raise ValidationError('Не выбран ответ по приёмке.')

    def _summary_text(self, uid, extraction_token, flow):
        context = self._context_helper.fetch_context(uid, extraction_token)
        partner = (context.get('partner') or {}).get('name') or (
            (context.get('supplier') or {}).get('name')
        ) or 'поставщик из счёта'
        total = ((context.get('totals') or {}).get('total_w_vat') or '')
        lines = len(context.get('items') or [])
        invoice_number = context.get('invoice_number') or 'без номера'
        actions = ['создать и подтвердить закупку']
        if flow.get('attach_invoice'):
            actions.append('создать счёт поставщика и прикрепить PDF')
        if flow.get('receive_picking'):
            actions.append('провести приёмку')
        pipe_lines = self._pipe_conversion_lines(
            uid, extraction_token, context
        )
        pipe_summary = ''
        if pipe_lines:
            pipe_summary = '\n• Пересчёт труб:\n' + '\n'.join(
                '  - %s' % line for line in pipe_lines
            ) + '\n'
        return (
            'Итоговый план:\n'
            '• Поставщик: %s\n'
            '• Склад: %s\n'
            '• Счёт: %s\n'
            '• Строк: %s%s\n'
            '%s'
            '• Действия: %s'
        ) % (
            partner,
            flow.get('warehouse_name') or '',
            invoice_number,
            lines,
            (', сумма %s' % total) if total else '',
            pipe_summary,
            '; '.join(actions),
        )

    def _pipe_conversion_lines(self, uid, extraction_token, context):
        session = self._store.get_session(uid, extraction_token) or {}
        created = session.get('created_by_line') or {}
        lines = []
        for idx, item in enumerate(context.get('items') or []):
            product = self._product_for_line(item, idx, created)
            if not product or not self._is_pipe_product(product):
                continue
            conversion = convert_pipe_quantity(
                item.get('qty'),
                item.get('unit'),
                kg_per_meter=product.product_tmpl_id.kg_per_meter,
                description=' '.join(
                    part for part in (
                        item.get('name'),
                        product.display_name,
                    ) if part
                ),
            )
            lines.append(
                '%s: %s'
                % (item.get('name') or product.display_name, conversion['formula'])
            )
        return lines

    def _product_for_line(self, item, index, created):
        line_key = self._line_key(item, index)
        product_id = self._product_id_for_line(item, line_key, created)
        return self.env['product.product'].browse(product_id) if product_id else None

    def _bind_vendor_bill(self, uid, extraction_token, po):
        attachment = self._attach_invoice(uid, extraction_token, po)
        bill = self._create_vendor_bill(po)
        extra = self._vendor_bill_extra_vals(uid, extraction_token, po)
        if extra:
            bill.write(extra)
        self._attach_pdf_to_bill(bill, attachment)
        return attachment, bill

    def _vendor_bill_extra_vals(self, uid, extraction_token, po):
        context = self._context_helper.fetch_context(uid, extraction_token)
        vals = {}
        invoice_date = context.get('invoice_date')
        if invoice_date:
            vals['invoice_date'] = invoice_date
        ref = po.partner_ref or context.get('invoice_number')
        if ref:
            vals['ref'] = ref
        return vals

    def _create_vendor_bill(self, po):
        existing = po.invoice_ids.filtered(
            lambda move: move.move_type == 'in_invoice'
            and move.state != 'cancel'
        )
        if existing:
            return existing[0]
        if any(line.qty_to_invoice for line in po.order_line):
            po.action_create_invoice()
        else:
            self._create_bill_from_ordered_qty(po)
        bills = po.invoice_ids.filtered(
            lambda move: move.move_type == 'in_invoice'
            and move.state != 'cancel'
        )
        if not bills:
            raise ValidationError('Не удалось создать счёт поставщика.')
        return bills[0]

    def _create_bill_from_ordered_qty(self, po):
        vals = po._prepare_invoice()
        sequence = 10
        for line in po.order_line:
            if line.display_type:
                continue
            line_vals = line._prepare_account_move_line()
            line_vals['quantity'] = line.product_qty
            line_vals['sequence'] = sequence
            sequence += 1
            vals['invoice_line_ids'].append((0, 0, line_vals))
        if not vals.get('invoice_line_ids'):
            raise ValidationError('Нет строк для счёта поставщика.')
        return self.env['account.move'].with_context(
            default_move_type='in_invoice',
        ).create(vals)

    def _attach_pdf_to_bill(self, bill, attachment):
        if not bill or not bill.exists() or not attachment:
            return
        linked = self._ensure_attachment_on(attachment, bill)
        posted = bill.message_ids.mapped('attachment_ids').filtered(
            lambda item: item.name == linked.name
        )
        if posted:
            return
        bill.message_post(
            body='PDF счёта прикреплён AI-ассистентом.',
            attachment_ids=linked.ids,
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )

    def _ensure_attachment_on(self, attachment, record):
        existing = self.env['ir.attachment'].search([
            ('res_model', '=', record._name),
            ('res_id', '=', record.id),
            ('name', '=', attachment.name),
        ], limit=1)
        if existing:
            return existing
        if (
            attachment.res_model == record._name
            and attachment.res_id == record.id
        ):
            return attachment
        return attachment.copy({
            'res_model': record._name,
            'res_id': record.id,
        })

    def _attach_invoice(self, uid, extraction_token, po):
        source = self._store.get_file(uid, extraction_token) or {}
        file_bytes = source.get('bytes')
        filename = source.get('name') or '%s.pdf' % (po.partner_ref or po.name)
        if not file_bytes:
            po.message_post(
                body='AI-ассистент: PDF счёта не найден в текущей сессии.',
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            return None
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', '=', po.id),
            ('name', '=', filename),
        ], limit=1)
        if attachment:
            return attachment
        return self.env['ir.attachment'].create({
            'name': filename,
            'res_model': 'purchase.order',
            'res_id': po.id,
            'type': 'binary',
            'datas': base64.b64encode(file_bytes),
            'mimetype': source.get('mimetype') or 'application/pdf',
        })

    def _receive_po_picking(self, po):
        if po.state not in ('purchase', 'done'):
            raise ValidationError(
                'Приёмка невозможна без подтверждённой закупки.'
            )
        picking = po.picking_ids.filtered(
            lambda item: item.picking_type_id.code == 'incoming'
            and item.state != 'cancel'
        )[:1]
        if not picking:
            raise ValidationError('Входящая приёмка по закупке не найдена.')
        if picking.state == 'done':
            return picking
        for move in picking.move_ids:
            if move.state in ('done', 'cancel'):
                continue
            move.quantity = move.product_uom_qty
        result = picking.with_context(skip_backorder=True).button_validate()
        if isinstance(result, dict):
            model = result.get('res_model')
            res_id = result.get('res_id')
            if model == 'stock.immediate.transfer' and res_id:
                self.env[model].browse(res_id).process()
            elif model == 'stock.backorder.confirmation' and res_id:
                self.env[model].browse(res_id).process_cancel_backorder()
            else:
                raise ValidationError(
                    'Приёмка требует дополнительного действия Odoo: %s.'
                    % (model or 'wizard')
                )
        if picking.state != 'done':
            picking.invalidate_recordset()
        return picking

    def _execution_steps(self, po, attachment, bill, picking):
        steps = ['Закупка создана и подтверждена: %s' % po.name]
        if bill:
            steps.append(
                'Счёт поставщика создан: %s.'
                % (bill.name or bill.display_name)
            )
        if attachment:
            steps.append('PDF счёта прикреплён к счёту поставщика.')
        if picking:
            steps.append('Приёмка проведена: %s' % picking.name)
        return steps

    def _execution_result_card(
        self, po, attachment=None, picking=None, bill=None
    ):
        details = []
        if bill and bill.exists():
            details.append({
                'label': 'Счёт поставщика',
                'value': bill.name or bill.display_name,
            })
        if attachment and attachment.exists():
            details.append({'label': 'Вложение', 'value': attachment.name})
        if picking and picking.exists():
            details.append({'label': 'Приёмка', 'value': picking.name})
        hint = 'Откройте закупку и проверьте результат.'
        if bill and bill.exists():
            hint = (
                'Откройте счёт поставщика: PDF лежит во вложениях счёта.'
            )
        return {
            'type': 'result',
            'status': 'success',
            'record': {
                'model': 'purchase.order',
                'id': po.id if po and po.exists() else None,
                'name': po.name if po and po.exists() else '',
                'url': '/odoo/purchase/%s' % po.id
                if po and po.exists() else '',
            },
            'details': details,
            'next_hint': hint,
            'steps': [],
        }
