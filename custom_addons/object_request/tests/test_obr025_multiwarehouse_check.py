"""
OBR-025: Тесты мультисклада для проверки наличия в object.request.

Проверяет:
- Fallback на warehouse_id при пустом check_warehouse_ids
- Использование check_warehouse_ids вместо warehouse_id
- Суммирование остатков по нескольким складам
- Возврат warning-уведомления при нулевых остатках
- Открытие wizard при наличии остатков
- Действия wizard: action_confirm и action_recheck
"""
import datetime

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestObr025MultiwarehouseCheck(TransactionCase):
    """Проверка мультисклада: check_warehouse_ids, суммирование остатков, wizard."""

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-025',
            'code': 'TST-025',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб OBR025',
            'login': 'foreman_test_obr025',
            'email': 'foreman_obr025@test.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Цемент OBR025',
            'default_code': 'CEMENT-025',
            'type': 'consu',
            'is_storable': True,
        })
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=2,
        )
        self.warehouse1 = warehouses[0]
        if len(warehouses) >= 2:
            self.warehouse2 = warehouses[1]
        else:
            group_user = self.env.ref('base.group_user')
            multi_wh_group = self.env.ref('stock.group_stock_multi_warehouses')
            multi_loc_group = self.env.ref('stock.group_stock_multi_locations')
            if multi_wh_group not in group_user.implied_ids:
                group_user.write({'implied_ids': [
                    (4, multi_wh_group.id),
                    (4, multi_loc_group.id),
                ]})
            self.warehouse2 = self.env['stock.warehouse'].sudo().create({
                'name': 'Склад OBR025-2',
                'code': 'OBR2',
            })
        self.request = self._create_request(warehouse_id=self.warehouse1.id)
        self.line = self._add_line(self.request)

    def _create_request(self, **extra):
        vals = {
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        }
        vals.update(extra)
        return self.env['object.request'].create(vals)

    def _add_line(self, request):
        return self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 10.0,
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
        })

    def _put_stock(self, warehouse, qty):
        """Разместить qty единиц товара на складе warehouse через stock.quant."""
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': warehouse.lot_stock_id.id,
            'quantity': qty,
        })

    # ── 1. Fallback на warehouse_id ──────────────────────────────────────────

    def test_check_stock_fallback_to_warehouse_id(self):
        """Если check_warehouse_ids пуст — stock_check_date заполняется на строках."""
        self._put_stock(self.warehouse1, 5.0)
        self.request.action_check_stock()
        self.assertTrue(self.line.stock_check_date, 'stock_check_date должен быть заполнен')

    def test_check_stock_fallback_reads_warehouse_id_qty(self):
        """Fallback: qty_on_hand берётся из склада warehouse_id."""
        self._put_stock(self.warehouse1, 5.0)
        self.request.action_check_stock()
        self.assertAlmostEqual(self.line.stock_qty_on_hand, 5.0)

    # ── 2. Использует check_warehouse_ids вместо warehouse_id ───────────────

    def test_check_stock_uses_check_warehouses(self):
        """Если указаны check_warehouse_ids — остаток берётся из них, а не warehouse_id."""
        self._put_stock(self.warehouse2, 7.0)
        self.request.write({'check_warehouse_ids': [(6, 0, [self.warehouse2.id])]})
        self.request.action_check_stock()
        self.assertGreater(
            self.line.stock_qty_on_hand, 0,
            'Должен обнаружить остаток на втором складе из check_warehouse_ids',
        )

    def test_check_stock_ignores_warehouse_id_when_check_set(self):
        """Остаток из warehouse_id не учитывается при заданных check_warehouse_ids."""
        self._put_stock(self.warehouse1, 10.0)
        self.request.write({'check_warehouse_ids': [(6, 0, [self.warehouse2.id])]})
        self.request.action_check_stock()
        self.assertAlmostEqual(
            self.line.stock_qty_on_hand, 0.0,
            msg='Остаток warehouse1 не должен попасть в результат для check_warehouse_ids=[warehouse2]',
        )

    # ── 3. Суммирование остатков по нескольким складам ───────────────────────

    def test_check_stock_sums_multiple_warehouses(self):
        """Остатки по двум складам суммируются: 5 + 3 = 8."""
        self._put_stock(self.warehouse1, 5.0)
        self._put_stock(self.warehouse2, 3.0)
        self.request.write({
            'check_warehouse_ids': [(6, 0, [self.warehouse1.id, self.warehouse2.id])],
        })
        self.request.action_check_stock()
        self.assertAlmostEqual(
            self.line.stock_qty_on_hand, 8.0,
            msg='Суммарный остаток по двум складам должен быть 8',
        )

    # ── 4. Warning если ничего не найдено ────────────────────────────────────

    def test_check_stock_returns_warning_type_client(self):
        """Если нет остатков — тип ответа ir.actions.client."""
        result = self.request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.client')

    def test_check_stock_returns_warning_tag_notification(self):
        """Если нет остатков — тег ответа display_notification."""
        result = self.request.action_check_stock()
        self.assertEqual(result['tag'], 'display_notification')

    def test_check_stock_returns_warning_if_nothing_found(self):
        """Если нет остатков — уведомление имеет type='warning'."""
        result = self.request.action_check_stock()
        self.assertEqual(result['params']['type'], 'warning')

    # ── 5. Открывает wizard если есть остаток ────────────────────────────────

    def test_check_stock_opens_wizard_if_found(self):
        """Если есть остаток — возвращает ir.actions.act_window."""
        self._put_stock(self.warehouse1, 10.0)
        result = self.request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.act_window')

    def test_check_stock_wizard_model_is_correct(self):
        """Если есть остаток — res_model в ответе = stock.check.wizard."""
        self._put_stock(self.warehouse1, 10.0)
        result = self.request.action_check_stock()
        self.assertEqual(result['res_model'], 'object.request.stock.check.wizard')

    # ── 6. Wizard: action_confirm устанавливает флаг ─────────────────────────

    def test_wizard_action_confirm_sets_flag(self):
        """action_confirm() устанавливает request.stock_check_confirmed = True."""
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        wizard.action_confirm()
        self.assertTrue(
            self.request.stock_check_confirmed,
            'stock_check_confirmed должен стать True после action_confirm',
        )

    def test_wizard_action_confirm_returns_close(self):
        """action_confirm() возвращает ir.actions.act_window_close."""
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        result = wizard.action_confirm()
        self.assertEqual(result['type'], 'ir.actions.act_window_close')

    # ── 7. Wizard: action_recheck закрывает ──────────────────────────────────

    def test_wizard_action_recheck_closes(self):
        """action_recheck() возвращает ir.actions.act_window_close."""
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        result = wizard.action_recheck()
        self.assertEqual(result['type'], 'ir.actions.act_window_close')

    def test_wizard_action_recheck_does_not_set_flag(self):
        """action_recheck() не должен устанавливать stock_check_confirmed."""
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        wizard.action_recheck()
        self.assertFalse(
            self.request.stock_check_confirmed,
            'stock_check_confirmed не должен меняться при action_recheck',
        )
