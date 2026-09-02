import json
import time
from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

from odoo.addons.ai_assistant.services.moving_intent import (
    MovingIntentExtractor,
    is_moving_candidate,
    keyword_moving_fallback,
)
from odoo.addons.ai_assistant.services.moving_picking_actions import (
    MovingPickingActionsService,
)
from odoo.addons.ai_assistant.services.moving_session_store import (
    MovingSessionStore,
)
from odoo.addons.ai_assistant.services.moving_stock import (
    MovingAvailabilityService,
    MovingWarehouseResolver,
)
from odoo.addons.ai_assistant.services.moving_workflow import MovingWorkflow


@tagged('post_install', '-at_install')
class TestMovingServices(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Moving Exact Product',
            'default_code': 'MOVE-EXACT',
            'is_storable': True,
        })
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Moving Resolver Warehouse',
            'code': 'MVRW',
            'company_id': cls.env.company.id,
        })

    def test_candidate_gate_requires_stock_context(self):
        self.assertTrue(is_moving_candidate(
            'Перемести 2 шт товара с основного склада на O002'
        ))
        self.assertFalse(is_moving_candidate('Переведи текст на русский'))

    def test_keyword_fallback_extracts_verbatim_route_and_quantity(self):
        result = keyword_moving_fallback(
            'Перемести 20 шт пена противопожарная '
            'с Основного склада на O002'
        )
        self.assertTrue(result['intent'])
        self.assertEqual(result['quantity'], 20)
        self.assertEqual(result['uom_text'], 'шт')
        self.assertEqual(result['source_warehouse_query'], 'Основного склада')
        self.assertEqual(result['destination_warehouse_query'], 'O002')
        self.assertEqual(result['product_query'], 'пена противопожарная')

    def test_extractor_replaces_non_verbatim_fields_with_fallback(self):
        client = MagicMock()
        client.send_structured_chat.return_value = {
            'intent': True, 'product_query': 'пену противопожарную',
            'quantity': 20, 'uom_text': 'шт',
            'source_warehouse_query': 'Основной склад',
            'destination_warehouse_query': 'O002',
            'scheduled_date_text': None, 'correction': False,
            'selection_ordinal': None, 'confidence': .95,
        }
        result = MovingIntentExtractor(self.env, client=client).extract(
            'Перемести 20 шт пена противопожарная '
            'с Основного склада на O002'
        )
        self.assertEqual(result['product_query'], 'пена противопожарная')
        self.assertEqual(result['source_warehouse_query'], 'Основного склада')
        schema = client.send_structured_chat.call_args.args[1]
        self.assertTrue(schema['strict'])
        self.assertNotIn('id', schema['schema']['properties'])

    def test_session_store_is_uid_scoped_and_expires(self):
        store = MovingSessionStore(ttl_seconds=.01)
        token = store.put(10, {'product_query': 'X'})
        self.assertIsNotNone(store.get_session(10, token))
        self.assertIsNone(store.get_session(11, token))
        time.sleep(.02)
        self.assertIsNone(store.get_session(10, token))

    def test_warehouse_resolver_classifies_exact_and_fuzzy(self):
        warehouse = self.warehouse
        resolver = MovingWarehouseResolver(self.env)
        exact = resolver.resolve(warehouse.code)
        self.assertEqual(exact[0]['match_type'], 'exact_code')
        fuzzy_query = warehouse.name[:max(2, len(warehouse.name) // 2)]
        if fuzzy_query.casefold() != warehouse.name.casefold():
            fuzzy = resolver.resolve(fuzzy_query)
            self.assertTrue(fuzzy)
            self.assertTrue(all(item['match_type'] == 'fuzzy' for item in fuzzy))

    def test_general_product_search_substring_is_not_moving_exact(self):
        workflow = MovingWorkflow(self.env, MovingSessionStore())
        products = [{'id': self.product.id}]
        self.assertEqual(
            workflow._exact_product_ids('Moving Exact Product', products),
            {self.product.id},
        )
        self.assertEqual(workflow._exact_product_ids('Exact Product', products), set())
        self.assertEqual(workflow._exact_product_ids('MOVE-EXACT', products),
                         {self.product.id})

    def test_wrong_action_does_not_mutate_and_repeats_buttons(self):
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        before = dict(session)
        workflow = MovingWorkflow(self.env, store)
        result = workflow.dispatch(
            self.env.uid, token, action=workflow.ACTION_EXECUTE,
        )
        self.assertEqual(session, before)
        self.assertEqual(result['meta']['moving_state'], workflow.AWAITING_PRODUCT)
        self.assertIn(workflow.ACTION_CANCEL,
                      {item['action'] for item in result['suggestions']})

    def test_forged_selection_id_is_rejected_without_mutation(self):
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        session['last_options'] = [{'id': self.product.id}]
        before = dict(session)
        result = MovingWorkflow(self.env, store).dispatch(
            self.env.uid, token,
            action=MovingWorkflow.ACTION_SELECT_PRODUCT,
            payload={'product_id': self.product.id + 999999},
        )
        self.assertEqual(session, before)
        self.assertIn('текущему шагу', result['answer'])

    def test_text_confirmation_never_executes_plan(self):
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        session['state'] = MovingWorkflow.AWAITING_PLAN
        result = MovingWorkflow(self.env, store).dispatch(
            self.env.uid, token, message='создавай',
        )
        self.assertFalse(session['executed'])
        self.assertFalse(session['picking_id'])
        self.assertEqual(result['meta']['moving_state'], MovingWorkflow.AWAITING_PLAN)

    def test_result_card_uses_generic_workflow_contract(self):
        picking = MagicMock()
        picking.id = 42
        picking.name = 'INT/00042'
        picking.state = 'assigned'
        picking.location_id.display_name = 'WH/Stock'
        picking.location_dest_id.display_name = 'O002/Stock'
        picking.move_ids = self.env['stock.move']
        picking.show_check_availability = False
        card = MovingPickingActionsService(self.env).card(picking, 'token-42')
        self.assertEqual(card['workflow'], {'type': 'moving', 'token': 'token-42'})
        self.assertEqual(card['record']['model'], 'stock.picking')
        disabled = {item['action']: item['disabled'] for item in card['actions']}
        self.assertTrue(disabled['reserve'])
        self.assertFalse(disabled['open'])
        self.assertFalse(disabled['print'])
        self.assertFalse(disabled['cancel'])

    def test_partial_assigned_picking_can_offer_check_availability(self):
        picking = MagicMock(state='assigned', show_check_availability=True)
        self.assertTrue(MovingPickingActionsService(self.env)._can_reserve(picking))

    def test_noun_trigger_and_quantity_evidence_gate(self):
        self.assertTrue(is_moving_candidate(
            'Перемещение товара со склада WH на O002'
        ))
        client = MagicMock()
        client.send_structured_chat.return_value = {
            'intent': True, 'product_query': 'пена', 'quantity': 20,
            'uom_text': None, 'source_warehouse_query': 'WH',
            'destination_warehouse_query': 'O002',
            'scheduled_date_text': None, 'correction': False,
            'selection_ordinal': None, 'confidence': .95,
        }
        result = MovingIntentExtractor(self.env, client=client).extract(
            'Перемещение пена со склада WH на O002'
        )
        self.assertIsNone(result['quantity'])

    def test_selection_ordinal_only_uses_current_allowlist(self):
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        session['last_options'] = [{
            'id': self.product.id, 'display_name': self.product.display_name,
        }]
        workflow = MovingWorkflow(self.env, store)
        result = workflow.dispatch(
            self.env.uid, token, message='первый',
            extracted={'selection_ordinal': 1},
        )
        self.assertEqual(result['meta']['moving_state'], workflow.AWAITING_QTY)
        self.assertEqual(session['product_id'], self.product.id)

        session['state'] = workflow.AWAITING_QTY
        before = dict(session)
        rejected = workflow.dispatch(
            self.env.uid, token, message='первый',
            extracted={'selection_ordinal': 1},
        )
        self.assertEqual(session, before)
        self.assertIn('текущему шагу', rejected['answer'])


@tagged('post_install', '-at_install')
class TestMovingHttpCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Moving HTTP Exact Product',
            'default_code': 'MOVE-HTTP',
            'is_storable': True,
        })
        cls.source = cls.env['stock.warehouse'].create({
            'name': 'Moving HTTP Source', 'code': 'MHSA',
            'company_id': cls.env.company.id,
        })
        cls.destination = cls.env['stock.warehouse'].create({
            'name': 'Moving HTTP Destination', 'code': 'MHDA',
            'company_id': cls.env.company.id,
        })
        cls.env['stock.quant']._update_available_quantity(
            cls.product, cls.source.lot_stock_id, 20,
        )
        params = cls.env['ir.config_parameter'].sudo()
        params.set_param('ai_assistant.enabled', 'True')
        params.set_param('ai_assistant.actions_enabled', 'True')
        params.set_param('ai_assistant.moving_enabled', 'True')

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')

    def _post(self, params):
        response = self.url_open(
            '/ai_assistant/chat',
            data=json.dumps({
                'jsonrpc': '2.0', 'method': 'call', 'params': params,
            }).encode(),
            headers={'Content-Type': 'application/json'},
        )
        return response.json().get('result') or {}

    def test_full_phrase_plan_execute_creates_one_draft_without_quant_change(self):
        extracted = {
            'intent': True,
            'product_query': 'Moving HTTP Exact Product',
            'quantity': 5,
            'uom_text': None,
            'source_warehouse_query': 'MHSA',
            'destination_warehouse_query': 'MHDA',
            'scheduled_date_text': None,
            'correction': False,
            'selection_ordinal': None,
            'confidence': .99,
        }
        domain = [('origin', '=', 'Перемещение (AI): MHSA → MHDA')]
        before_count = self.env['stock.picking'].search_count(domain)
        before_available = self.env['stock.quant']._get_available_quantity(
            self.product, self.source.lot_stock_id,
        )
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'MovingIntentExtractor.extract',
            return_value=extracted,
        ):
            plan = self._post({
                'message': (
                    'Перемести 5 Moving HTTP Exact Product '
                    'со склада MHSA на MHDA'
                ),
            })
        self.assertEqual(plan.get('meta', {}).get('moving_state'), 'AWAITING_PLAN')
        token = plan['meta']['moving_token']
        executed = self._post({
            'message': '', 'moving_token': token,
            'moving_action': 'moving_execute_plan',
            'moving_payload': {}, 'active_workflow_kind': 'moving',
        })
        self.assertTrue(executed.get('meta', {}).get('moving_terminal'))
        self.assertEqual(self.env['stock.picking'].search_count(domain),
                         before_count + 1)
        picking = self.env['stock.picking'].search(domain, order='id desc', limit=1)
        self.assertEqual(picking.state, 'draft')
        self.assertEqual(picking.location_id, self.source.lot_stock_id)
        self.assertEqual(picking.location_dest_id,
                         self.destination.lot_stock_id)
        self.assertTrue(self.env['ai_assistant.audit'].sudo().search([
            ('tool_name', '=', 'moving_execute_plan'),
            ('record_ref', '=', 'stock.picking,%s' % picking.id),
            ('result_status', '=', 'success'),
        ], limit=1))
        self.assertEqual(self.env['stock.quant']._get_available_quantity(
            self.product, self.source.lot_stock_id,
        ), before_available)

        repeated = self._post({
            'message': '', 'moving_token': token,
            'moving_action': 'moving_execute_plan',
            'moving_payload': {}, 'active_workflow_kind': 'moving',
        })
        self.assertTrue(
            repeated.get('meta', {}).get('moving_terminal'), repeated,
        )
        self.assertEqual(self.env['stock.picking'].search_count(domain),
                         before_count + 1)

    def test_mixed_foreground_tokens_return_workflow_conflict(self):
        result = self._post({
            'message': '',
            'moving_token': 'moving-token',
            'replenishment_token': 'replenishment-token',
        })
        self.assertEqual(result.get('error_code'), 'workflow_conflict')
        self.assertFalse(result.get('cards'))

    def test_overlapping_candidate_gates_offer_explicit_workflow_choice(self):
        result = self._post({
            'message': (
                'Перемести и пополни 5 шт Moving HTTP Exact Product '
                'со склада MHSA на MHDA'
            ),
        })
        self.assertEqual(result.get('error_code'), 'workflow_conflict')
        self.assertEqual(
            {item['action'] for item in result.get('suggestions') or []},
            {'workflow_start_moving', 'workflow_start_replenishment'},
        )

    def test_unrepresentable_stock_uom_qty_requires_button_choice(self):
        self.product.uom_id.rounding = 1
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        session.update({
            'state': MovingWorkflow.AWAITING_QTY,
            'product_id': self.product.id,
            'requested_uom_id': self.product.uom_id.id,
            'move_uom_id': self.product.uom_id.id,
        })
        result = MovingWorkflow(self.env, store)._set_quantity(
            self.env.uid, token, .5, self.product.uom_id.name,
        )
        self.assertEqual(session['state'], MovingWorkflow.AWAITING_QTY)
        self.assertIsNone(session['move_qty'])
        self.assertIn('нельзя точно представить', result['answer'])
        self.assertTrue(any(
            item['action'] == MovingWorkflow.ACTION_CHANGE_QTY
            for item in result['suggestions']
        ))

    def test_scheduled_date_is_user_timezone_utc_and_past_rejected(self):
        workflow = MovingWorkflow(self.env, MovingSessionStore())
        user = self.env.user
        previous_tz = user.tz
        user.tz = 'Asia/Yakutsk'
        try:
            parsed = workflow._parse_scheduled_date('31.12.2099 09:00')
            self.assertEqual(parsed, '2099-12-31 00:00:00')
            with self.assertRaises(Exception):
                workflow._parse_scheduled_date('01.01.2000')
        finally:
            user.tz = previous_tz

    def test_execute_creates_one_draft_and_is_idempotent(self):
        source = self.source
        destination = self.env['stock.warehouse'].create({
            'name': 'Moving Destination', 'code': 'MVDST',
        })
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        workflow = MovingWorkflow(self.env, store)
        session.update({
            'state': workflow.AWAITING_PLAN,
            'product_id': self.product.id,
            'requested_qty': 2,
            'requested_uom_id': self.product.uom_id.id,
            'move_qty': 2,
            'move_uom_id': self.product.uom_id.id,
            'source': workflow._warehouse_snapshot(source),
            'destination': workflow._warehouse_snapshot(destination),
            'availability_snapshot': {
                'on_hand': 5, 'reserved': 0, 'available': 5,
            },
            'generated_origin': 'Перемещение (AI): %s → %s' % (
                source.code, destination.code,
            ),
        })
        workflow.availability.totals = MagicMock(return_value={
            'on_hand': 5, 'reserved': 0, 'available': 5,
        })
        before_quants = MovingAvailabilityService(self.env).totals(
            self.product.id, source,
        )
        first = workflow.execute_plan(self.env.uid, token)
        second = workflow.execute_plan(self.env.uid, token)
        picking_id = first['cards'][0]['record']['id']
        self.assertEqual(second['cards'][0]['record']['id'], picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertEqual(picking.state, 'draft')
        self.assertEqual(picking.location_id, source.lot_stock_id)
        self.assertEqual(picking.location_dest_id, destination.lot_stock_id)
        self.assertEqual(picking.picking_type_id, destination.int_type_id)
        self.assertEqual(picking.move_ids.product_uom_qty, 2)
        self.assertEqual(
            picking.origin,
            'Перемещение (AI): %s → %s' % (
                source.code, destination.code,
            ),
        )
        self.assertEqual(
            MovingAvailabilityService(self.env).totals(self.product.id, source),
            before_quants,
        )

        forged = self.env['stock.picking'].create({
            'picking_type_id': destination.int_type_id.id,
            'location_id': source.lot_stock_id.id,
            'location_dest_id': destination.lot_stock_id.id,
        })
        action_result = MovingPickingActionsService(
            self.env
        ).dispatch_for_session(
            store, self.env.uid, token, 'cancel',
            advisory_picking_id=forged.id,
        )
        self.assertTrue(action_result['ok'])
        self.assertEqual(picking.state, 'cancel')
        self.assertEqual(forged.state, 'draft')

    def test_stale_availability_blocks_execute(self):
        source = self.source
        destination = self.destination
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        workflow = MovingWorkflow(self.env, store)
        session.update({
            'state': workflow.AWAITING_PLAN,
            'product_id': self.product.id, 'requested_qty': 2,
            'requested_uom_id': self.product.uom_id.id,
            'move_qty': 2, 'move_uom_id': self.product.uom_id.id,
            'source': workflow._warehouse_snapshot(source),
            'destination': workflow._warehouse_snapshot(destination),
            'availability_snapshot': {
                'on_hand': 5, 'reserved': 0, 'available': 5,
            },
        })
        workflow.availability.totals = MagicMock(return_value={
            'on_hand': 1, 'reserved': 0, 'available': 1,
        })
        before = self.env['stock.picking'].search_count([
            ('origin', 'like', 'Перемещение (AI):'),
        ])
        result = workflow.execute_plan(self.env.uid, token)
        after = self.env['stock.picking'].search_count([
            ('origin', 'like', 'Перемещение (AI):'),
        ])
        self.assertEqual(before, after)
        self.assertEqual(result['meta']['moving_state'],
                         workflow.AWAITING_STOCK_RESOLUTION)

    def test_deactivated_warehouse_between_plan_and_execute_is_blocked(self):
        source = self.env['stock.warehouse'].create({
            'name': 'Moving Active Source', 'code': 'MVACT',
        })
        destination = self.env['stock.warehouse'].create({
            'name': 'Moving Deactivated Destination', 'code': 'MVOFF',
        })
        store = MovingSessionStore()
        token = store.put(self.env.uid, {})
        session = store.get_session(self.env.uid, token)
        workflow = MovingWorkflow(self.env, store)
        session.update({
            'state': workflow.AWAITING_PLAN,
            'product_id': self.product.id, 'requested_qty': 1,
            'requested_uom_id': self.product.uom_id.id,
            'move_qty': 1, 'move_uom_id': self.product.uom_id.id,
            'source': workflow._warehouse_snapshot(source),
            'destination': workflow._warehouse_snapshot(destination),
            'availability_snapshot': {
                'on_hand': 1, 'reserved': 0, 'available': 1,
            },
        })
        try:
            destination.active = False
            with self.assertRaises(Exception):
                workflow.execute_plan(self.env.uid, token)
        finally:
            destination.active = True
        self.assertFalse(session['executed'])
        self.assertFalse(session['picking_id'])
