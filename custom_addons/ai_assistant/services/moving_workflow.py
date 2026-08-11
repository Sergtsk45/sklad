import re
from datetime import datetime, time, timedelta

import pytz

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round

from .action_tools.read_tools import SearchProductsTool, uoms_are_compatible
from .moving_draft import MovingDraftService
from .moving_picking_actions import MovingPickingActionsService
from .moving_stock import (
    MovingAvailabilityService,
    MovingWarehouseResolver,
    ensure_moving_access,
)


class MovingWorkflow:
    AWAITING_PRODUCT = 'AWAITING_PRODUCT'
    AWAITING_QTY = 'AWAITING_QTY'
    AWAITING_SOURCE = 'AWAITING_SOURCE'
    AWAITING_STOCK_RESOLUTION = 'AWAITING_STOCK_RESOLUTION'
    AWAITING_DESTINATION = 'AWAITING_DESTINATION'
    AWAITING_PLAN = 'AWAITING_PLAN'
    EXECUTED = 'EXECUTED'
    CANCELLED = 'CANCELLED'

    ACTION_SELECT_PRODUCT = 'moving_select_product'
    ACTION_SELECT_SOURCE = 'moving_select_source'
    ACTION_SELECT_DESTINATION = 'moving_select_destination'
    ACTION_CHANGE_PRODUCT = 'moving_change_product'
    ACTION_CHANGE_QTY = 'moving_change_qty'
    ACTION_CHANGE_SOURCE = 'moving_change_source'
    ACTION_CHANGE_DESTINATION = 'moving_change_destination'
    ACTION_CHANGE_DATE = 'moving_change_scheduled_date'
    ACTION_EXECUTE = 'moving_execute_plan'
    ACTION_CANCEL = 'moving_cancel'

    AWAITING = {
        AWAITING_PRODUCT, AWAITING_QTY, AWAITING_SOURCE,
        AWAITING_STOCK_RESOLUTION, AWAITING_DESTINATION, AWAITING_PLAN,
    }

    def __init__(self, env, store):
        self.env = env
        self.store = store
        self.products = SearchProductsTool()
        self.warehouses = MovingWarehouseResolver(env)
        self.availability = MovingAvailabilityService(env)

    def begin(self, uid, extracted):
        ensure_moving_access(self.env)
        token = self.store.put(uid, extracted)
        session = self.store.get_session(uid, token)
        query = (extracted or {}).get('product_query')
        if not query:
            return token, self._current_response(token, session)
        return token, self._resolve_product(uid, token, query)

    def dispatch(self, uid, token, action=None, payload=None, message=None,
                 extracted=None):
        ensure_moving_access(self.env)
        session = self.store.get_session(uid, token)
        if not session:
            return self._expired()
        payload = payload or {}
        if action == self.ACTION_CANCEL:
            if session['state'] not in self.AWAITING:
                return self._unexpected(token, session)
            session['state'] = self.CANCELLED
            session['last_options'] = []
            return self._response(token, session,
                                  'План отменён. Изменений в Odoo нет.',
                                  terminal=True)
        if (action == self.ACTION_CHANGE_QTY and payload.get('quantity')
                and session['state'] == self.AWAITING_QTY
                and self._quantity_option_allowlisted(session, payload)):
            uom = self.env['uom.uom'].browse(payload['uom_id']).exists()
            return self._set_quantity(uid, token, payload['quantity'], uom.name)
        if action in self._change_actions():
            return self._change(uid, token, action)
        expected = {
            self.ACTION_SELECT_PRODUCT: self.AWAITING_PRODUCT,
            self.ACTION_SELECT_SOURCE: self.AWAITING_SOURCE,
            self.ACTION_SELECT_DESTINATION: self.AWAITING_DESTINATION,
            self.ACTION_EXECUTE: self.AWAITING_PLAN,
        }
        idempotent_execute = (
            action == self.ACTION_EXECUTE and
            session['state'] == self.EXECUTED and
            session.get('executed') and session.get('picking_id')
        )
        if action and expected.get(action) != session['state'] and not idempotent_execute:
            return self._unexpected(token, session)
        if action and not self._allowlisted(session, action, payload):
            return self._unexpected(token, session)
        if action == self.ACTION_SELECT_PRODUCT:
            return self._select_product(uid, token, payload['product_id'])
        if action == self.ACTION_SELECT_SOURCE:
            return self._select_source(uid, token, payload['warehouse_id'])
        if action == self.ACTION_SELECT_DESTINATION:
            return self._select_destination(uid, token, payload['warehouse_id'])
        if action == self.ACTION_EXECUTE:
            return self.execute_plan(uid, token)
        return self._handle_text(uid, token, message, extracted or {})

    def _handle_text(self, uid, token, message, extracted):
        session = self.store.get_session(uid, token)
        state = session['state']
        ordinal = extracted.get('selection_ordinal')
        if ordinal is not None:
            selected = self._select_ordinal(uid, token, ordinal)
            if selected is not None:
                return selected
            return self._unexpected(token, session)
        if state == self.AWAITING_PRODUCT:
            query = extracted.get('product_query') or message or ''
            if len(query.strip()) < 2:
                return self._unexpected(token, session)
            return self._resolve_product(uid, token, query)
        if state == self.AWAITING_QTY:
            qty = extracted.get('quantity')
            uom_text = extracted.get('uom_text')
            if qty is None:
                qty, parsed_uom = self._parse_qty(message)
                uom_text = uom_text or parsed_uom
            if qty is None:
                return self._unexpected(token, session)
            return self._set_quantity(uid, token, qty, uom_text)
        if state == self.AWAITING_SOURCE:
            query = extracted.get('source_warehouse_query') or message or ''
            if not query.strip():
                return self._unexpected(token, session)
            return self._resolve_source(uid, token, query)
        if state == self.AWAITING_DESTINATION:
            if session.get('editing_date'):
                date_text = extracted.get('scheduled_date_text') or message or ''
                if date_text.strip().casefold() in (
                    'без даты', 'по умолчанию', 'очистить', 'null',
                ):
                    session['scheduled_date_utc'] = None
                    session['scheduled_date_text'] = None
                    session['editing_date'] = False
                    session['state'] = self.AWAITING_PLAN
                    return self._plan_response(token, session)
                try:
                    session['scheduled_date_utc'] = self._parse_scheduled_date(date_text)
                except ValidationError as error:
                    return self._current_response(token, session, str(error))
                session['scheduled_date_text'] = date_text.strip()
                session['editing_date'] = False
                session['state'] = self.AWAITING_PLAN
                return self._plan_response(token, session)
            query = extracted.get('destination_warehouse_query') or message or ''
            if not query.strip():
                return self._unexpected(token, session)
            return self._resolve_destination(uid, token, query)
        return self._unexpected(token, session)

    def _resolve_product(self, uid, token, query):
        session = self.store.get_session(uid, token)
        products = self.products.execute(
            self.env, {'query': query.strip(), 'limit': 10}
        ).get('products') or []
        products = [item for item in products if item.get('is_storable')]
        session['state'] = self.AWAITING_PRODUCT
        session['last_options'] = products
        if not products:
            return self._current_response(
                token, session, 'Складской товар не найден. Уточните название.'
            )
        exact_ids = self._exact_product_ids(query, products)
        if len(products) != 1 or products[0]['id'] not in exact_ids:
            return self._current_response(
                token, session, 'Выберите товар из найденных вариантов.'
            )
        return self._select_product(uid, token, products[0]['id'])

    def _select_product(self, uid, token, product_id):
        session = self.store.get_session(uid, token)
        product = self.env['product.product'].browse(product_id).exists()
        if not product or not product.active or not product.is_storable:
            return self._unexpected(token, session)
        session.update({
            'product_id': product.id, 'requested_uom_id': product.uom_id.id,
            'move_uom_id': product.uom_id.id, 'state': self.AWAITING_QTY,
            'last_options': [],
        })
        raw = session['extracted_raw']
        if raw.get('quantity') is not None:
            return self._set_quantity(uid, token, raw['quantity'], raw.get('uom_text'))
        return self._current_response(token, session)

    def _set_quantity(self, uid, token, quantity, uom_text=None):
        session = self.store.get_session(uid, token)
        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 0
        if quantity <= 0:
            return self._current_response(
                token, session, 'Количество должно быть больше нуля.'
            )
        product = self.env['product.product'].browse(session['product_id']).exists()
        requested_uom = self._resolve_uom(product, uom_text)
        if not requested_uom:
            return self._current_response(
                token, session, 'Уточните совместимую единицу измерения.'
            )
        move_qty = requested_uom._compute_quantity(
            quantity, product.uom_id, round=False,
        )
        if not self._is_representable(move_qty, product.uom_id.rounding):
            lower = float_round(move_qty, precision_rounding=product.uom_id.rounding,
                                rounding_method='DOWN')
            upper = float_round(move_qty, precision_rounding=product.uom_id.rounding,
                                rounding_method='UP')
            session['last_options'] = [
                {
                    'quantity': product.uom_id._compute_quantity(
                        option, requested_uom, round=False,
                    ),
                    'uom_id': requested_uom.id,
                }
                for option in (lower, upper) if option > 0
            ]
            return self._current_response(
                token, session,
                'Количество нельзя точно представить в %s. '
                'Ближайшие варианты: %s и %s.' % (
                    product.uom_id.name, lower, upper,
                ),
            )
        session.update({
            'requested_qty': quantity, 'requested_uom_id': requested_uom.id,
            'move_qty': move_qty, 'move_uom_id': product.uom_id.id,
            'state': self.AWAITING_SOURCE, 'last_options': [],
        })
        if session.get('source'):
            try:
                return self._select_source(uid, token, session['source']['id'])
            except ValidationError:
                session['source'] = None
        query = session['extracted_raw'].get('source_warehouse_query')
        if query:
            return self._resolve_source(uid, token, query)
        return self._show_sources(token, session)

    def _resolve_source(self, uid, token, query):
        session = self.store.get_session(uid, token)
        matches = self.warehouses.resolve(query)
        session['state'] = self.AWAITING_SOURCE
        session['last_options'] = matches
        if len(matches) == 1 and matches[0]['match_type'].startswith('exact_'):
            return self._select_source(uid, token, matches[0]['id'])
        if not matches:
            return self._show_sources(token, session,
                                      'Склад не найден. Выберите источник.')
        return self._current_response(
            token, session, 'Подтвердите склад-источник.'
        )

    def _show_sources(self, token, session, answer=None):
        session['last_options'] = self.warehouses.list_candidates(
            product_id=session['product_id'], positive_available=True,
        )
        return self._current_response(
            token, session, answer or 'Выберите склад-источник.'
        )

    def _select_source(self, uid, token, warehouse_id):
        session = self.store.get_session(uid, token)
        warehouse = self.warehouses.validate(warehouse_id)
        totals = self.availability.totals(session['product_id'], warehouse)
        session.update({
            'source': self._warehouse_snapshot(warehouse),
            'source_hint_id': warehouse.id,
            'availability_snapshot': totals, 'last_options': [],
        })
        product = self.env['product.product'].browse(session['product_id'])
        if float_compare(
            session['move_qty'], totals['available'],
            precision_rounding=product.uom_id.rounding,
        ) > 0:
            session['state'] = self.AWAITING_STOCK_RESOLUTION
            return self._current_response(
                token, session,
                'На складе %s доступно %s %s из запрошенных %s.' % (
                    warehouse.display_name, totals['available'], product.uom_id.name,
                    session['move_qty'],
                ),
            )
        session['state'] = self.AWAITING_DESTINATION
        destination = session.get('destination')
        if destination:
            if destination['id'] == warehouse.id:
                session['destination'] = None
                session['destination_hint_id'] = None
            else:
                try:
                    return self._select_destination(
                        uid, token, destination['id'],
                    )
                except ValidationError:
                    session['destination'] = None
                    session['destination_hint_id'] = None
        query = session['extracted_raw'].get('destination_warehouse_query')
        if query:
            return self._resolve_destination(uid, token, query)
        return self._show_destinations(token, session)

    def _resolve_destination(self, uid, token, query):
        session = self.store.get_session(uid, token)
        matches = self.warehouses.resolve(query, exclude_id=session['source']['id'])
        session['state'] = self.AWAITING_DESTINATION
        session['last_options'] = matches
        if len(matches) == 1 and matches[0]['match_type'].startswith('exact_'):
            return self._select_destination(uid, token, matches[0]['id'])
        if not matches:
            return self._show_destinations(
                token, session, 'Склад назначения не найден. Выберите вариант.'
            )
        return self._current_response(
            token, session, 'Подтвердите склад назначения.'
        )

    def _show_destinations(self, token, session, answer=None):
        session['last_options'] = self.warehouses.list_candidates(
            exclude_id=session['source']['id'],
        )
        return self._current_response(
            token, session, answer or 'Выберите склад назначения.'
        )

    def _select_destination(self, uid, token, warehouse_id):
        session = self.store.get_session(uid, token)
        warehouse = self.warehouses.validate(warehouse_id, session['source']['id'])
        session['destination'] = self._warehouse_snapshot(warehouse)
        session['destination_hint_id'] = warehouse.id
        raw_date = session['extracted_raw'].get('scheduled_date_text')
        if raw_date and not session.get('scheduled_date_text'):
            try:
                session['scheduled_date_utc'] = self._parse_scheduled_date(raw_date)
                session['scheduled_date_text'] = raw_date
            except ValidationError as error:
                session['state'] = self.AWAITING_DESTINATION
                session['editing_date'] = True
                return self._current_response(token, session, str(error))
        session['generated_origin'] = 'Перемещение (AI): %s → %s' % (
            session['source']['code'], session['destination']['code'],
        )
        session['state'] = self.AWAITING_PLAN
        session['last_options'] = []
        return self._plan_response(token, session)

    def _change(self, uid, token, action):
        session = self.store.get_session(uid, token)
        allowed_states = {
            self.ACTION_CHANGE_PRODUCT: self.AWAITING,
            self.ACTION_CHANGE_QTY: self.AWAITING - {self.AWAITING_PRODUCT},
            self.ACTION_CHANGE_SOURCE: {
                self.AWAITING_SOURCE, self.AWAITING_STOCK_RESOLUTION,
                self.AWAITING_DESTINATION, self.AWAITING_PLAN,
            },
            self.ACTION_CHANGE_DESTINATION: {
                self.AWAITING_DESTINATION, self.AWAITING_PLAN,
            },
            self.ACTION_CHANGE_DATE: {self.AWAITING_PLAN},
        }
        if session['state'] not in allowed_states[action]:
            return self._unexpected(token, session)
        if action == self.ACTION_CHANGE_PRODUCT:
            session.update({'state': self.AWAITING_PRODUCT, 'product_id': None,
                            'requested_qty': None, 'requested_uom_id': None,
                            'move_qty': None, 'move_uom_id': None,
                            'availability_snapshot': None})
        elif action == self.ACTION_CHANGE_QTY:
            session.update({'state': self.AWAITING_QTY, 'requested_qty': None,
                            'move_qty': None, 'availability_snapshot': None})
        elif action == self.ACTION_CHANGE_SOURCE:
            session.update({'state': self.AWAITING_SOURCE, 'source': None,
                            'availability_snapshot': None})
        elif action == self.ACTION_CHANGE_DESTINATION:
            session.update({'state': self.AWAITING_DESTINATION,
                            'destination': None,
                            'destination_hint_id': None})
        else:
            session.update({'state': self.AWAITING_DESTINATION,
                            'scheduled_date_text': None,
                            'scheduled_date_utc': None,
                            'editing_date': True})
        session.update({'last_options': [], 'generated_origin': None})
        if session['state'] == self.AWAITING_SOURCE:
            return self._show_sources(token, session)
        if session['state'] == self.AWAITING_DESTINATION and not session.get('editing_date'):
            return self._show_destinations(token, session)
        return self._current_response(token, session)

    def execute_plan(self, uid, token):
        with self.store.get_lock(uid, token):
            session = self.store.get_session(uid, token)
            if not session:
                return self._expired()
            if session.get('executed') and session.get('picking_id'):
                picking = self.env['stock.picking'].browse(session['picking_id']).exists()
                return self._executed_response(token, session, picking)
            if session['state'] != self.AWAITING_PLAN:
                return self._unexpected(token, session)
            product = self.env['product.product'].browse(session['product_id']).exists()
            if not product or not product.active or not product.is_storable:
                return self._current_response(
                    token, session, 'Товар больше недоступен. Измените план.'
                )
            requested_uom = self.env['uom.uom'].browse(
                session['requested_uom_id']
            ).exists()
            if not requested_uom or not uoms_are_compatible(
                requested_uom, product.uom_id,
            ):
                session['state'] = self.AWAITING_QTY
                return self._current_response(
                    token, session, 'Единица измерения больше недоступна. '
                    'Укажите количество заново.'
                )
            fresh_move_qty = requested_uom._compute_quantity(
                session['requested_qty'], product.uom_id, round=False,
            )
            if (not self._is_representable(
                    fresh_move_qty, product.uom_id.rounding,
                ) or float_compare(
                    fresh_move_qty, session['move_qty'],
                    precision_rounding=product.uom_id.rounding,
                )):
                session['state'] = self.AWAITING_QTY
                return self._current_response(
                    token, session, 'Количество или его конвертация изменились. '
                    'Укажите количество заново.'
                )
            source = self.warehouses.validate(session['source']['id'])
            destination = self.warehouses.validate(
                session['destination']['id'], source.id,
            )
            fresh = self.availability.totals(product.id, source)
            if float_compare(session['move_qty'], fresh['available'],
                             precision_rounding=product.uom_id.rounding) > 0:
                session.update({'state': self.AWAITING_STOCK_RESOLUTION,
                                'availability_snapshot': fresh})
                return self._current_response(
                    token, session,
                    'Остаток изменился: сейчас доступно %s %s. '
                    'Измените план.' % (fresh['available'], product.uom_id.name),
                )
            picking = MovingDraftService(self.env).create(
                product.id, session['move_qty'], source.id, destination.id,
                session.get('scheduled_date_utc'),
            )
            session.update({'picking_id': picking.id, 'executed': True,
                            'state': self.EXECUTED,
                            'availability_snapshot': fresh})
            return self._executed_response(token, session, picking)

    def _plan_response(self, token, session):
        product = self.env['product.product'].browse(session['product_id'])
        requested_uom = self.env['uom.uom'].browse(session['requested_uom_id'])
        stock_uom = product.uom_id
        stock = session['availability_snapshot']
        warning = (
            '\nВнимание: партия/серийный номер указываются в форме Odoo.'
            if product.tracking != 'none' else ''
        )
        answer = (
            'План перемещения:\nТовар: %s\nЗапрошено: %s %s\n'
            'К перемещению: %s %s\nДоступно: %s '
            '(на руках %s, резерв %s)\nМаршрут: %s → %s\n'
            'Тип: %s\nДата: %s\nOrigin: %s%s'
        ) % (
            product.display_name, session['requested_qty'], requested_uom.name,
            session['move_qty'], stock_uom.name, stock['available'],
            stock['on_hand'], stock['reserved'], session['source']['display_name'],
            session['destination']['display_name'], session['destination']['picking_type_name'],
            session.get('scheduled_date_text') or 'по умолчанию Odoo',
            session['generated_origin'], warning,
        )
        return self._current_response(token, session, answer)

    def _current_response(self, token, session, answer=None):
        if session.get('editing_date') and not answer:
            answer = (
                'Укажите дату: ДД.ММ.ГГГГ [ЧЧ:ММ], сегодня, '
                'завтра или выберите «Без даты».'
            )
        answers = {
            self.AWAITING_PRODUCT: 'Какой товар нужно переместить?',
            self.AWAITING_QTY: 'Укажите количество и единицу измерения.',
            self.AWAITING_SOURCE: 'Выберите склад-источник.',
            self.AWAITING_STOCK_RESOLUTION: 'Доступного остатка недостаточно. Измените план.',
            self.AWAITING_DESTINATION: 'Выберите склад назначения.',
        }
        suggestions = self._state_suggestions(session)
        return self._response(token, session, answer or answers.get(session['state'], ''),
                              suggestions=suggestions)

    def _state_suggestions(self, session):
        state = session['state']
        suggestions = []
        if session.get('editing_date'):
            return [
                self._suggestion('Без даты', None,
                                 {'message': 'без даты'}),
                self._suggestion('Отмена', self.ACTION_CANCEL, {}),
            ]
        if state == self.AWAITING_QTY and session.get('last_options'):
            suggestions.extend(self._suggestion(
                '%s %s' % (option['quantity'], self.env['uom.uom'].browse(
                    option['uom_id']
                ).name),
                self.ACTION_CHANGE_QTY,
                {'quantity': option['quantity'], 'uom_id': option['uom_id']},
            ) for option in session['last_options'])
        option_action, option_field = {
            self.AWAITING_PRODUCT: (self.ACTION_SELECT_PRODUCT, 'product_id'),
            self.AWAITING_SOURCE: (self.ACTION_SELECT_SOURCE, 'warehouse_id'),
            self.AWAITING_DESTINATION: (self.ACTION_SELECT_DESTINATION, 'warehouse_id'),
        }.get(state, (None, None))
        if option_action:
            for option in session.get('last_options') or []:
                label = option.get('display_name') or option.get('name')
                if state in (self.AWAITING_SOURCE, self.AWAITING_DESTINATION):
                    label = '%s (%s)' % (option['name'], option['code'])
                    if 'available' in option:
                        label += ' — доступно %s' % option['available']
                suggestions.append(self._suggestion(
                    label, option_action, {option_field: option['id']},
                ))
        nav = {
            self.AWAITING_QTY: [('Изменить товар', self.ACTION_CHANGE_PRODUCT)],
            self.AWAITING_SOURCE: [
                ('Изменить товар', self.ACTION_CHANGE_PRODUCT),
                ('Изменить количество', self.ACTION_CHANGE_QTY),
            ],
            self.AWAITING_STOCK_RESOLUTION: [
                ('Изменить товар', self.ACTION_CHANGE_PRODUCT),
                ('Изменить количество', self.ACTION_CHANGE_QTY),
                ('Другой склад', self.ACTION_CHANGE_SOURCE),
            ],
            self.AWAITING_DESTINATION: [
                ('Изменить источник', self.ACTION_CHANGE_SOURCE),
                ('Изменить количество', self.ACTION_CHANGE_QTY),
            ],
            self.AWAITING_PLAN: [
                ('Создать перемещение', self.ACTION_EXECUTE),
                ('Изменить товар', self.ACTION_CHANGE_PRODUCT),
                ('Изменить количество', self.ACTION_CHANGE_QTY),
                ('Изменить источник', self.ACTION_CHANGE_SOURCE),
                ('Изменить назначение', self.ACTION_CHANGE_DESTINATION),
                ('Изменить дату', self.ACTION_CHANGE_DATE),
            ],
        }.get(state, [])
        suggestions.extend(self._suggestion(label, action, {}) for label, action in nav)
        if state in self.AWAITING:
            suggestions.append(self._suggestion('Отмена', self.ACTION_CANCEL, {}))
        return suggestions

    def _allowlisted(self, session, action, payload):
        if action == self.ACTION_EXECUTE:
            return True
        payload_field = {
            self.ACTION_SELECT_PRODUCT: 'product_id',
            self.ACTION_SELECT_SOURCE: 'warehouse_id',
            self.ACTION_SELECT_DESTINATION: 'warehouse_id',
        }.get(action)
        return bool(payload_field and payload.get(payload_field) in {
            option.get('id') for option in session.get('last_options') or []
        })

    def _quantity_option_allowlisted(self, session, payload):
        return any(
            option.get('quantity') == payload.get('quantity')
            and option.get('uom_id') == payload.get('uom_id')
            for option in session.get('last_options') or []
        )

    def _resolve_uom(self, product, text):
        if not text:
            return product.uom_id
        normalized = self._normalized(text)
        aliases = {
            'шт': 'uom.product_uom_unit', 'штука': 'uom.product_uom_unit',
            'штуки': 'uom.product_uom_unit', 'штук': 'uom.product_uom_unit',
            'кг': 'uom.product_uom_kgm', 'килограмм': 'uom.product_uom_kgm',
            'м': 'uom.product_uom_meter', 'метр': 'uom.product_uom_meter',
            'л': 'uom.product_uom_litre', 'литр': 'uom.product_uom_litre',
        }
        alias_ref = aliases.get(normalized)
        if alias_ref:
            candidate = self.env.ref(alias_ref, raise_if_not_found=False)
            return candidate if uoms_are_compatible(candidate, product.uom_id) else None
        candidates = self.env['uom.uom'].search([], limit=300).filtered(
            lambda uom: self._normalized(uom.name) == normalized
        )
        compatible = candidates.filtered(
            lambda uom: uoms_are_compatible(uom, product.uom_id)
        )
        return compatible if len(compatible) == 1 else None

    def _exact_product_ids(self, query, products):
        normalized = self._normalized(query)
        records = self.env['product.product'].browse(
            [item['id'] for item in products]
        ).exists()
        return {
            product.id for product in records
            if normalized in {
                self._normalized(product.name),
                self._normalized(product.default_code),
                self._normalized(product.barcode),
            }
        }

    def _normalized(self, value):
        return re.sub(r'\s+', ' ', (value or '').replace('\xa0', ' ')).strip().casefold()

    def _is_representable(self, quantity, rounding):
        if not rounding or rounding <= 0:
            return False
        ratio = quantity / rounding
        return abs(ratio - round(ratio)) <= 1e-9 * max(1.0, abs(ratio))

    def _parse_scheduled_date(self, text_value):
        value = (text_value or '').strip().casefold()
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        now_utc = fields.Datetime.to_datetime(fields.Datetime.now()).replace(
            tzinfo=pytz.UTC,
        )
        local_now = now_utc.astimezone(user_tz)
        if value in ('сегодня', 'завтра'):
            day = local_now.date() + timedelta(days=value == 'завтра')
            naive = datetime.combine(day, time(9, 0))
        else:
            naive = None
            for pattern in ('%d.%m.%Y %H:%M', '%d.%m.%Y',
                            '%Y-%m-%d %H:%M', '%Y-%m-%d'):
                try:
                    naive = datetime.strptime(value, pattern)
                    if '%H' not in pattern:
                        naive = datetime.combine(naive.date(), time(9, 0))
                    break
                except ValueError:
                    continue
            if naive is None:
                raise ValidationError(
                    'Дата не распознана. Используйте ДД.ММ.ГГГГ [ЧЧ:ММ].'
                )
        try:
            utc_value = user_tz.localize(naive, is_dst=None).astimezone(pytz.UTC)
        except (pytz.AmbiguousTimeError, pytz.NonExistentTimeError) as error:
            raise ValidationError(
                'Указанное местное время неоднозначно из-за перевода часов. '
                'Укажите другое время.'
            ) from error
        if utc_value <= now_utc:
            raise ValidationError('Дата перемещения не может быть в прошлом.')
        return fields.Datetime.to_string(utc_value.replace(tzinfo=None))

    def _parse_qty(self, message):
        match = re.search(r'(?<!\w)(\d+(?:[.,]\d+)?)\s*([^\d\s]+)?', message or '')
        return ((float(match.group(1).replace(',', '.')), match.group(2))
                if match else (None, None))

    def _select_ordinal(self, uid, token, ordinal):
        session = self.store.get_session(uid, token)
        try:
            index = int(ordinal) - 1
        except (TypeError, ValueError):
            return None
        options = session.get('last_options') or []
        if index < 0 or index >= len(options):
            return None
        option_id = options[index].get('id')
        if session['state'] == self.AWAITING_PRODUCT:
            return self._select_product(uid, token, option_id)
        if session['state'] == self.AWAITING_SOURCE:
            return self._select_source(uid, token, option_id)
        if session['state'] == self.AWAITING_DESTINATION:
            return self._select_destination(uid, token, option_id)
        return None

    def _warehouse_snapshot(self, warehouse):
        return {'id': warehouse.id, 'name': warehouse.name, 'code': warehouse.code,
                'display_name': warehouse.display_name,
                'location_id': warehouse.lot_stock_id.id,
                'picking_type_id': warehouse.int_type_id.id,
                'picking_type_name': warehouse.int_type_id.display_name}

    def _change_actions(self):
        return {self.ACTION_CHANGE_PRODUCT, self.ACTION_CHANGE_QTY,
                self.ACTION_CHANGE_SOURCE, self.ACTION_CHANGE_DESTINATION,
                self.ACTION_CHANGE_DATE}

    def _executed_response(self, token, session, picking):
        if not picking:
            return self._expired()
        return self._response(
            token, session, 'Черновик перемещения %s создан.' % picking.name,
            cards=[MovingPickingActionsService(self.env).card(picking, token)],
            terminal=True,
        )

    def _unexpected(self, token, session):
        return self._current_response(
            token, session,
            'Этот ответ не соответствует текущему шагу. '
            'Выберите один из доступных вариантов.'
        )

    def _suggestion(self, label, action, payload):
        return {'label': label, 'action': action, 'payload': payload}

    def _response(self, token, session, answer, suggestions=None, cards=None,
                  terminal=False):
        return {'status': session['state'], 'answer': answer,
                'suggestions': suggestions or [], 'cards': cards or [],
                'meta': {'moving_token': token, 'moving_state': session['state'],
                         'moving_terminal': terminal}}

    def _expired(self):
        return {'status': 'expired',
                'answer': 'Сессия перемещения истекла. Начните заново.',
                'suggestions': [], 'cards': [],
                'meta': {'moving_terminal': True}}
