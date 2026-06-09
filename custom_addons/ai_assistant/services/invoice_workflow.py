# @file: invoice_workflow.py
# @description: Пошаговое создание номенклатуры и PO по счёту.
# @dependencies: invoice_context_helper, invoice_extraction_store
# @created: 2026-05-31

from odoo.exceptions import ValidationError

from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindWarehouseTool,
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

    ACTION_NEXT_PRODUCT = 'invoice_next_product'
    ACTION_PREPARE_PO = 'invoice_prepare_po'

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

    def suggestions_after_product_created(self, uid, extraction_token):
        next_line = self._next_line_to_create(uid, extraction_token)
        if next_line:
            short_name = self._short_name(next_line['name'])
            return [{
                'label': 'Создать следующий: %s' % short_name,
                'action': self.ACTION_NEXT_PRODUCT,
            }]
        if self.all_products_ready(uid, extraction_token):
            return [{
                'label': 'Создать закупку на склад',
                'action': self.ACTION_PREPARE_PO,
            }]
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
                'Можно создать закупку на склад.'
            ),
            'suggestions': [{
                'label': 'Создать закупку на склад',
                'action': self.ACTION_PREPARE_PO,
            }],
            'cards': [],
            'meta': {'status': 'all_products_ready'},
        }

    def prepare_po_draft(self, uid, extraction_token, warehouse_query=None):
        """
        Подготовить args для create_purchase_order_draft.
        """
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
        partner_id = self._resolve_partner_id(context)
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
            uom_id = (
                self._resolve_uom_id(item.get('unit')) or product.uom_id.id
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

    def _resolve_partner_id(self, context):
        partner = (context or {}).get('partner') or {}
        if partner.get('status') == 'matched':
            return partner.get('partner_id')
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

    def _short_name(self, name, limit=48):
        text = (name or '').strip()
        if len(text) <= limit:
            return text
        return text[: limit - 1] + '…'
