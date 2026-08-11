import re

from .action_tools.read_tools import (
    FindWarehouseTool,
    GetProductSupplierInfoTool,
    SearchProductsTool,
    uoms_are_compatible,
)
from .action_tools.write_tools import CreatePurchaseOrderDraftTool
from .purchase_order_actions import PurchaseOrderActionsService


class ReplenishmentWorkflow:
    ACTION_SELECT_PRODUCT = 'replenishment_select_product'
    ACTION_SELECT_VENDOR = 'replenishment_select_vendor'
    ACTION_SELECT_WAREHOUSE = 'replenishment_select_warehouse'
    ACTION_EXECUTE_PLAN = 'replenishment_execute_plan'
    ACTION_CANCEL = 'replenishment_cancel'

    AWAITING_PRODUCT = 'AWAITING_PRODUCT'
    AWAITING_QTY = 'AWAITING_QTY'
    AWAITING_VENDOR = 'AWAITING_VENDOR'
    AWAITING_WAREHOUSE = 'AWAITING_WAREHOUSE'
    AWAITING_PLAN = 'AWAITING_PLAN'
    EXECUTED = 'EXECUTED'
    CANCELLED = 'CANCELLED'

    def __init__(self, env, store):
        self.env = env
        self.store = store
        self.products = SearchProductsTool()
        self.offers = GetProductSupplierInfoTool()
        self.warehouses = FindWarehouseTool()

    def begin(self, uid, extracted):
        token = self.store.put(uid, extracted)
        session = self.store.get_session(uid, token)
        query = (extracted or {}).get('product_query')
        if not query:
            return token, self._response(
                token, session, 'Какой товар нужно пополнить?'
            )
        return token, self._resolve_product(uid, token, query)

    def dispatch(self, uid, token, action=None, payload=None, message=None,
                 extracted=None):
        session = self.store.get_session(uid, token)
        if not session:
            return self._expired_response()
        payload = payload or {}
        if action == self.ACTION_CANCEL:
            if session['state'] != self.AWAITING_PLAN:
                return self._unexpected(token, session)
            session['state'] = self.CANCELLED
            return self._response(
                token, session, 'План отменён. Изменений в Odoo нет.',
                terminal=True,
            )
        expected = {
            self.ACTION_SELECT_PRODUCT: self.AWAITING_PRODUCT,
            self.ACTION_SELECT_VENDOR: self.AWAITING_VENDOR,
            self.ACTION_SELECT_WAREHOUSE: self.AWAITING_WAREHOUSE,
            self.ACTION_EXECUTE_PLAN: self.AWAITING_PLAN,
        }
        if action and expected.get(action) != session['state']:
            return self._unexpected(token, session)
        if action and not self._payload_is_allowlisted(session, action, payload):
            return self._response(
                token, session,
                'Выбранный вариант недоступен. Используйте предложенные кнопки.'
            )
        if action == self.ACTION_SELECT_PRODUCT:
            allowed = {
                item.get('id') for item in session.get('last_options', [])
            }
            if payload.get('product_id') not in allowed:
                return self._unexpected(token, session)
            return self._select_product(uid, token, payload.get('product_id'))
        if action == self.ACTION_SELECT_VENDOR:
            return self._select_vendor(uid, token, payload.get('supplierinfo_id'))
        if action == self.ACTION_SELECT_WAREHOUSE:
            allowed = {
                item.get('id') for item in session.get('last_options', [])
            }
            if payload.get('warehouse_id') not in allowed:
                return self._unexpected(token, session)
            return self._select_warehouse(uid, token, payload.get('warehouse_id'))
        if action == self.ACTION_EXECUTE_PLAN:
            return self.execute_plan(uid, token)
        return self._handle_text(uid, token, message, extracted or {})

    def _payload_is_allowlisted(self, session, action, payload):
        field_by_action = {
            self.ACTION_SELECT_PRODUCT: ('product_id', 'id'),
            self.ACTION_SELECT_VENDOR: ('supplierinfo_id', 'supplierinfo_id'),
            self.ACTION_SELECT_WAREHOUSE: ('warehouse_id', 'id'),
        }
        if action not in field_by_action:
            return action in (self.ACTION_EXECUTE_PLAN, self.ACTION_CANCEL)
        payload_field, option_field = field_by_action[action]
        selected_id = payload.get(payload_field)
        return bool(selected_id) and selected_id in {
            option.get(option_field)
            for option in session.get('last_options') or []
        }

    def _handle_text(self, uid, token, message, extracted):
        session = self.store.get_session(uid, token)
        state = session['state']
        if state == self.AWAITING_PRODUCT:
            return self._resolve_product(
                uid, token, extracted.get('product_query') or message or ''
            )
        if state == self.AWAITING_QTY:
            qty = extracted.get('quantity') or self._parse_quantity(message)
            return self._set_quantity(uid, token, qty, extracted.get('uom_text'))
        if state == self.AWAITING_VENDOR:
            return self._choose_vendor(
                uid, token, extracted.get('vendor_query') or message,
                extracted.get('vendor_preference'),
                extracted.get('selection_ordinal'),
            )
        if state == self.AWAITING_WAREHOUSE:
            return self._resolve_warehouse(
                uid, token, extracted.get('warehouse_query') or message or ''
            )
        return self._unexpected(token, session)

    def _resolve_product(self, uid, token, query):
        session = self.store.get_session(uid, token)
        query = (query or '').strip()
        if len(query) < 2:
            return self._response(token, session, 'Уточните наименование товара.')
        products = self.products.execute(
            self.env, {'query': query, 'limit': 10}
        ).get('products') or []
        if not products:
            session['state'] = self.AWAITING_PRODUCT
            return self._response(
                token, session, 'Товар не найден — уточните наименование.'
            )
        if len(products) > 1:
            session['last_options'] = products
            return self._response(token, session, 'Выберите товар:', [
                self._suggestion(item['display_name'], self.ACTION_SELECT_PRODUCT,
                                 {'product_id': item['id']})
                for item in products
            ])
        return self._select_product(uid, token, products[0]['id'])

    def _select_product(self, uid, token, product_id):
        session = self.store.get_session(uid, token)
        product = self.env['product.product'].browse(product_id).exists()
        if not product:
            return self._response(token, session, 'Товар не найден.')
        session.update({'product_id': product.id,
                        'requested_uom_id': product.uom_id.id,
                        'state': self.AWAITING_QTY})
        stock = self._stock_totals(product.id)
        extracted = session['extracted_raw']
        qty = extracted.get('quantity')
        prefix = ('Остаток: %(on_hand)s, зарезервировано: %(reserved)s, '
                  'доступно: %(available)s. ') % stock
        if qty and qty > 0:
            response = self._set_quantity(
                uid, token, qty, extracted.get('uom_text')
            )
            response['answer'] = prefix + response['answer']
            return response
        return self._response(token, session, prefix + 'Сколько нужно пополнить?')

    def _stock_totals(self, product_id):
        domain = [('product_id', '=', product_id),
                  ('location_id.usage', '=', 'internal'),
                  ('company_id', '=', self.env.company.id)]
        rows = self.env['stock.quant']._read_group(
            domain, [], ['quantity:sum', 'reserved_quantity:sum']
        )
        quantity, reserved = rows[0] if rows else (0.0, 0.0)
        return {'on_hand': quantity or 0.0, 'reserved': reserved or 0.0,
                'available': (quantity or 0.0) - (reserved or 0.0)}

    def _set_quantity(self, uid, token, qty, uom_text=None):
        session = self.store.get_session(uid, token)
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            qty = 0
        if qty <= 0:
            return self._response(token, session,
                                  'Количество должно быть больше нуля.')
        product = self.env['product.product'].browse(session['product_id'])
        uom = self._resolve_uom(product, uom_text)
        if not uom:
            return self._response(
                token, session, 'Уточните совместимую единицу измерения.'
            )
        session.update({'qty': qty,
                        'qty_source': ('extracted'
                                       if session['extracted_raw'].get('quantity')
                                       else 'asked'),
                        'requested_uom_id': uom.id,
                        'state': self.AWAITING_VENDOR})
        result = self._load_offers(uid, token)
        result['answer'] = ('Распознано количество: %s %s. ' %
                            (qty, uom.display_name)) + result['answer']
        return result

    def _resolve_uom(self, product, text):
        if not text:
            return product.uom_id
        candidates = self.env['uom.uom'].search([
            ('name', 'ilike', text.strip()),
        ], limit=20)
        return candidates.filtered(
            lambda uom: uoms_are_compatible(uom, product.uom_id)
        )[:1]

    def _load_offers(self, uid, token):
        session = self.store.get_session(uid, token)
        result = self.offers.execute(self.env, {
            'product_id': session['product_id'], 'quantity': session['qty'],
            'uom_id': session['requested_uom_id'],
        })
        offers = result.get('offers') or []
        session['last_options'] = offers
        if not offers:
            return self._response(
                token, session,
                'Нет применимых предложений поставщиков. Проверьте vendor-строки, '
                'валюту и единицы измерения.',
                terminal=True,
            )
        extracted = session['extracted_raw']
        if len(offers) == 1:
            session['vendor'] = offers[0]
            session['state'] = self.AWAITING_WAREHOUSE
            answer = 'Выбран единственный поставщик: %s. ' % offers[0]['partner_name']
            next_response = self._resolve_warehouse(
                uid, token, extracted.get('warehouse_query') or ''
            )
            next_response['answer'] = answer + next_response['answer']
            return next_response
        return self._choose_vendor(
            uid, token, extracted.get('vendor_query'),
            extracted.get('vendor_preference'),
            extracted.get('selection_ordinal'),
        )

    def _choose_vendor(self, uid, token, query=None, preference=None, ordinal=None):
        session = self.store.get_session(uid, token)
        offers = session.get('last_options') or []
        selected = None
        if preference == 'cheapest' and offers:
            selected = min(offers, key=lambda item: item['comparison_price'])
        elif ordinal and 0 < ordinal <= len(offers):
            selected = offers[ordinal - 1]
        elif query:
            matches = [item for item in offers
                       if str(query).lower() in item['partner_name'].lower()]
            selected = matches[0] if len(matches) == 1 else None
        if selected:
            return self._select_vendor(uid, token, selected['supplierinfo_id'])
        return self._response(token, session, 'Выберите поставщика:', [
            self._suggestion(
                '%s — %s %s/%s' % (
                    item['partner_name'], item['normalized_price_discounted'],
                    item['currency_id']['symbol'], item['requested_uom_name']),
                self.ACTION_SELECT_VENDOR,
                {'supplierinfo_id': item['supplierinfo_id']},
            ) for item in offers
        ])

    def _select_vendor(self, uid, token, supplierinfo_id):
        session = self.store.get_session(uid, token)
        selected = next((item for item in session.get('last_options', [])
                         if item['supplierinfo_id'] == supplierinfo_id), None)
        if not selected:
            return self._response(token, session,
                                  'Предложение устарело. Выберите снова.')
        session.update({'vendor': selected, 'state': self.AWAITING_WAREHOUSE})
        query = session['extracted_raw'].get('warehouse_query') or ''
        return self._resolve_warehouse(uid, token, query)

    def _resolve_warehouse(self, uid, token, query):
        session = self.store.get_session(uid, token)
        if query:
            warehouses = self.warehouses.execute(
                self.env, {'query': str(query)}
            ).get('warehouses') or []
            if len(warehouses) == 1:
                return self._select_warehouse(uid, token, warehouses[0]['id'])
        warehouses = self.env['stock.warehouse'].search_read(
            [], ['id', 'name', 'code', 'in_type_id'], limit=10
        )
        session['last_options'] = warehouses
        return self._response(token, session, 'Выберите склад приёмки:', [
            self._suggestion('%s (%s)' % (wh['name'], wh['code']),
                             self.ACTION_SELECT_WAREHOUSE,
                             {'warehouse_id': wh['id']})
            for wh in warehouses
        ])

    def _select_warehouse(self, uid, token, warehouse_id):
        session = self.store.get_session(uid, token)
        warehouse = self.env['stock.warehouse'].browse(warehouse_id).exists()
        if not warehouse or not warehouse.in_type_id or warehouse.in_type_id.code != 'incoming':
            return self._response(token, session,
                                  'У склада нет операции поступления.')
        session.update({'warehouse': {'id': warehouse.id,
                                      'name': warehouse.display_name,
                                      'picking_type_id': warehouse.in_type_id.id},
                        'state': self.AWAITING_PLAN})
        return self._plan_response(token, session)

    def _plan_response(self, token, session):
        product = self.env['product.product'].browse(session['product_id'])
        vendor = session['vendor']
        total = vendor['purchase_qty'] * vendor['price_discounted']
        rounding = ''
        if vendor.get('rounding_adjusted'):
            rounding = ' Количество округлено вверх до допустимой кратности UoM.'
        answer = (
            'План пополнения:\nТовар: %s\nЗапрошено: %s %s\n'
            'Поставщик: %s\nЦена со скидкой: %s %s/%s\n'
            'Заказ: %s %s по %s, сумма %s %s\nСклад: %s.%s'
        ) % (
            product.display_name, session['qty'], vendor['requested_uom_name'],
            vendor['partner_name'], vendor['normalized_price_discounted'],
            vendor['currency_id']['symbol'], vendor['requested_uom_name'],
            vendor['purchase_qty'], vendor['product_uom_name'], vendor['price'],
            total, vendor['currency_id']['symbol'], session['warehouse']['name'],
            rounding,
        )
        return self._response(token, session, answer, [
            self._suggestion('Выполнить', self.ACTION_EXECUTE_PLAN, {}),
            self._suggestion('Отмена', self.ACTION_CANCEL, {}),
        ])

    def execute_plan(self, uid, token):
        with self.store.get_lock(uid, token):
            session = self.store.get_session(uid, token)
            if not session:
                return self._expired_response()
            if session.get('executed') and session.get('po_id'):
                po = self.env['purchase.order'].browse(session['po_id'])
                return self._executed_response(token, session, po)
            if session['state'] != self.AWAITING_PLAN:
                return self._unexpected(token, session)
            fresh_result = self.offers.execute(self.env, {
                'product_id': session['product_id'],
                'quantity': session['qty'],
                'uom_id': session['requested_uom_id'],
            })
            fresh_offers = fresh_result.get('offers') or []
            fresh_vendor = next((
                item for item in fresh_offers
                if item['supplierinfo_id'] == session['vendor']['supplierinfo_id']
            ), None)
            if not fresh_vendor:
                session.update({
                    'state': self.AWAITING_VENDOR,
                    'last_options': fresh_offers,
                    'vendor': None,
                })
                suggestions = [
                    self._suggestion(
                        '%s — %s %s/%s' % (
                            item['partner_name'],
                            item['normalized_price_discounted'],
                            item['currency_id']['symbol'],
                            item['requested_uom_name'],
                        ),
                        self.ACTION_SELECT_VENDOR,
                        {'supplierinfo_id': item['supplierinfo_id']},
                    )
                    for item in fresh_offers
                ]
                return self._response(
                    token, session,
                    'Выбранное предложение больше недоступно. '
                    'Выберите поставщика заново.', suggestions,
                )
            if self._offer_changed(session['vendor'], fresh_vendor):
                session.update({'vendor': fresh_vendor,
                                'last_options': fresh_offers})
                response = self._plan_response(token, session)
                response['answer'] = (
                    'Условия поставщика изменились. '
                    'Проверьте обновлённый план и подтвердите его ещё раз.\n\n'
                    + response['answer']
                )
                return response
            product = self.env['product.product'].browse(session['product_id'])
            vendor = session['vendor']
            result = CreatePurchaseOrderDraftTool().execute(self.env, {
                'partner_id': vendor['partner_id'],
                'picking_type_id': session['warehouse']['picking_type_id'],
                'origin': ('Пополнение (AI): %s' % product.display_name)[:60],
                'lines': [{
                    'product_id': product.id,
                    'product_qty': vendor['purchase_qty'],
                    'product_uom': vendor['product_uom_id'],
                    'price_unit': vendor['price'],
                    'discount': vendor['discount'],
                    'supplierinfo_id': vendor['supplierinfo_id'],
                    'name': self._vendor_line_name(product, vendor),
                }],
            })
            session.update({'po_id': result['po_id'], 'executed': True,
                            'state': self.EXECUTED})
            po = self.env['purchase.order'].browse(result['po_id'])
            return self._executed_response(token, session, po)

    def _offer_changed(self, previous, current):
        keys = (
            'partner_id', 'price', 'discount', 'purchase_qty',
            'product_uom_id', 'price_discounted',
        )
        return any(previous.get(key) != current.get(key) for key in keys) or (
            (previous.get('currency_id') or {}).get('id')
            != (current.get('currency_id') or {}).get('id')
        )

    def _vendor_line_name(self, product, vendor):
        name = vendor.get('product_name') or product.display_name
        code = vendor.get('product_code') or ''
        return '[%s] %s' % (code, name) if code else name

    def _executed_response(self, token, session, po):
        return self._response(
            token, session, 'Черновик заказа %s создан.' % po.name,
            cards=[PurchaseOrderActionsService(self.env).card(po, token)],
            terminal=True,
        )

    def _parse_quantity(self, text):
        match = re.search(r'(?<!\w)(\d+(?:[.,]\d+)?)', text or '')
        return float(match.group(1).replace(',', '.')) if match else None

    def _suggestion(self, label, action, payload):
        return {'label': label, 'action': action, 'payload': payload}

    def _response(self, token, session, answer, suggestions=None, cards=None,
                  terminal=False):
        return {'status': session['state'], 'answer': answer,
                'suggestions': suggestions or [], 'cards': cards or [],
                'meta': {'replenishment_token': token,
                         'replenishment_state': session['state'],
                         'replenishment_terminal': terminal}}

    def _unexpected(self, token, session):
        return self._response(
            token, session,
            'Этот ответ не соответствует текущему шагу пополнения.'
        )

    def _expired_response(self):
        return {'status': 'expired',
                'answer': 'Сессия пополнения истекла. Начните заново.',
                'suggestions': [], 'cards': [],
                'meta': {'replenishment_terminal': True}}
