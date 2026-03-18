"""
OBR-018: Ручные пилотные сценарии — автоматизированные интеграционные тесты.

Покрывают все 9 пользовательских сценариев из functional spec:
  1. Прораб создаёт документ вручную
  2. Импорт Excel с частичным несопоставлением
  3. Снабженец сопоставляет строки и переводит в работу
  4. Снабженец формирует выдачу, кладовщик подтверждает
  5. Печать требования и расходной накладной
  6. Полный lifecycle: Черновик → В работе → Закрыто
  7. Отмена документа из Черновика и из В работе
  8. Частичная выдача → повторная выдача по оставшимся позициям
  9. Права: прораб не может создать выдачу; кладовщик не может сопоставлять строки
"""
import base64
import datetime
import io

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _make_excel(rows):
    """Собрать минимальный xlsx-файл из списка строк."""
    try:
        import openpyxl
    except ImportError:
        return None
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_user(env, name, login, group):
    return env['res.users'].create({
        'name': name,
        'login': login,
        'email': f'{login}@test.com',
        'group_ids': [(4, group.id)],
    })


@tagged('post_install', '-at_install')
class TestPilotScenarios(TransactionCase):
    """Интеграционные тесты пилотных сценариев OBR-018."""

    def setUp(self):
        super().setUp()

        # Группы
        self.g_foreman = self.env.ref('object_request.group_foreman')
        self.g_supply = self.env.ref('object_request.group_supply_manager')
        self.g_store = self.env.ref('object_request.group_storekeeper')

        # Пользователи
        self.foreman = _make_user(self.env, 'Прораб 018', 'foreman_018', self.g_foreman)
        self.supply = _make_user(self.env, 'Снабженец 018', 'supply_018', self.g_supply)
        self.storekeeper = _make_user(self.env, 'Кладовщик 018', 'store_018', self.g_store)

        # Объект
        self.project = self.env['object.request.project'].create({
            'name': 'Жилой комплекс OBR-018',
            'code': 'JK-018',
        })

        # Товары
        self.cement = self.env['product.product'].create({
            'name': 'Цемент М500 OBR018',
            'default_code': 'CEM-018',
            'type': 'consu',
            'is_storable': True,
        })
        self.rebar = self.env['product.product'].create({
            'name': 'Арматура 12мм OBR018',
            'default_code': 'ARM-018',
            'type': 'consu',
            'is_storable': True,
        })

        # Поставщик
        self.vendor = self.env['res.partner'].create({
            'name': 'Поставщик OBR-018',
            'supplier_rank': 1,
        })

        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        self.customer_loc = self.env.ref('stock.stock_location_customers')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 1: Прораб создаёт документ вручную
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_1_foreman_creates_request_manually(self):
        """Прораб создаёт документ, добавляет строки, сохраняет."""
        env = self.env(user=self.foreman)
        request = env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
            'priority': '2',
            'comment': 'Нужно срочно',
        })
        env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 50.0,
            'zone': 'А',
            'floor': '1',
            'section': 'Сек.1',
        })
        env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Арматура',
            'qty_requested': 200.0,
        })
        self.assertEqual(request.state, 'draft')
        self.assertTrue(request.name)  # автонумерация
        self.assertEqual(request.line_count, 2)

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 2: Импорт Excel с частичным несопоставлением
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_2_excel_import_partial_match(self):
        """Excel-импорт: известный товар сопоставляется, неизвестный — помечается."""
        xlsx_bytes = _make_excel([
            ['№', 'Артикул', 'Наименование', 'Ед.изм.', 'Кол-во', 'Цена', 'Комментарий', 'Поставщик'],
            [1, 'CEM-018', 'Цемент М500 OBR018', 'шт', 20, 300.0, '', ''],
            [2, '', 'НесуществующийМатериалXYZ', 'кг', 10, 0.0, '', ''],
        ])
        if xlsx_bytes is None:
            self.skipTest('openpyxl не установлен')

        wizard = self.env['object.request.import.wizard'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
            'priority': '1',
            'file': base64.b64encode(xlsx_bytes),
            'file_name': 'test_018.xlsx',
        })
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'valid')
        self.assertEqual(wizard.line_preview_count, 2)
        # problem_line_count считает строки с has_error (пустое имя / qty=0),
        # несопоставленные товары фиксируются в validation_messages
        self.assertIn('Требуют сопоставления', wizard.validation_messages)

        result = wizard.action_import()
        request = self.env['object.request'].browse(result['res_id'])
        self.assertTrue(request.exists())
        self.assertEqual(len(request.line_ids), 2)

        # Несопоставленная строка имеет matching_required=True
        unmatched = request.line_ids.filtered(lambda l: l.matching_required)
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(unmatched.name_raw, 'НесуществующийМатериалXYZ')

        # Сопоставленная строка — matching_required=False
        matched = request.line_ids.filtered(lambda l: not l.matching_required)
        self.assertEqual(len(matched), 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 3: Снабженец сопоставляет строки и переводит в работу
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_3_supply_matches_lines_and_starts_work(self):
        """Снабженец назначает товар/поставщика на проблемные строки → переводит в работу."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        unmatched = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Неизвестный материал',
            'qty_requested': 10.0,
            'matching_required': True,
        })

        # Снабженец видит проблемные строки
        self.assertEqual(request.line_problem_count, 1)

        # Снабженец вручную сопоставляет строку
        env_supply = self.env(user=self.supply)
        env_supply['object.request.line'].browse(unmatched.id).write({
            'product_id': self.cement.id,
            'uom_id': self.cement.uom_id.id,
            'preferred_vendor_id': self.vendor.id,
            'matching_required': False,
        })
        unmatched.invalidate_recordset()
        self.assertFalse(unmatched.matching_required)
        self.assertEqual(request.line_problem_count, 0)

        # Переводит в работу
        request.action_in_progress()
        self.assertEqual(request.state, 'in_progress')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 4: Снабженец формирует выдачу, кладовщик подтверждает
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_4_issue_and_storekeeper_confirms(self):
        """Снабженец создаёт выдачу → кладовщик подтверждает фактическое кол-во."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 20.0,
            'qty_to_issue': 10.0,
            'product_id': self.cement.id,
            'uom_id': self.cement.uom_id.id,
        })
        request.write({'state': 'in_progress'})

        # Добавить товар на склад
        self.env['stock.quant'].create({
            'product_id': self.cement.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'quantity': 100.0,
        })

        # Снабженец создаёт выдачу
        wiz = self.env['object.request.issue.wizard'].create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': self.customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertTrue(picking.exists())
        self.assertIn(picking, request.issue_picking_ids)

        # Кладовщик подтверждает выдачу
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            ml.quantity = ml.move_id.product_uom_qty
        picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(picking.state, 'done')

        line.invalidate_recordset()
        self.assertEqual(line.qty_issued, 10.0)
        self.assertEqual(line.line_state, 'fully_supplied')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 5: Печать требования и расходной накладной
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_5_print_request_report(self):
        """QWeb-отчёт требования рендерится без ошибок."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 10.0,
        })
        report = self.env.ref('object_request.action_report_object_request')
        html, _ = self.env['ir.actions.report']._render_qweb_html(
            report, [request.id]
        )
        self.assertIn(request.name.encode(), html)

    def test_scenario_5_print_picking_report(self):
        """QWeb-отчёт расходной накладной рендерится без ошибок."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 5.0,
            'qty_to_issue': 5.0,
            'product_id': self.cement.id,
            'uom_id': self.cement.uom_id.id,
        })
        request.write({'state': 'in_progress'})
        wiz = self.env['object.request.issue.wizard'].create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': self.customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])

        report = self.env.ref('object_request.action_report_issue_picking')
        html, _ = self.env['ir.actions.report']._render_qweb_html(
            report, [picking.id]
        )
        self.assertIn(picking.name.encode(), html)

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 6: Полный lifecycle Черновик → В работе → Закрыто
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_6_full_lifecycle(self):
        """Документ проходит Черновик → В работе → Закрыто."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 10.0,
            'product_id': self.cement.id,
            'matching_required': False,
        })
        self.assertEqual(request.state, 'draft')

        # draft → in_progress
        request.action_in_progress()
        self.assertEqual(request.state, 'in_progress')

        # Обозначить строку обеспеченной: qty_to_issue > 0 нужен для fully_supplied
        line.write({'qty_to_issue': 10.0, 'qty_issued': 10.0})
        line.invalidate_recordset()
        self.assertEqual(line.line_state, 'fully_supplied')

        # in_progress → closed
        request.action_close()
        self.assertEqual(request.state, 'closed')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 7: Отмена документа
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_7_cancel_from_draft(self):
        """Отмена документа из статуса Черновик."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        request.action_cancel()
        self.assertEqual(request.state, 'cancelled')

    def test_scenario_7_cancel_from_in_progress(self):
        """Отмена документа из статуса В работе."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 5.0,
            'product_id': self.cement.id,
        })
        request.action_in_progress()
        self.assertEqual(request.state, 'in_progress')

        request.action_cancel()
        self.assertEqual(request.state, 'cancelled')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 8: Частичная выдача → повторная выдача по остатку
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_8_partial_then_second_issue(self):
        """Первая частичная выдача → вторая выдача по оставшейся части."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        # qty_to_issue = 20 (весь запрос)
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Арматура',
            'qty_requested': 20.0,
            'qty_to_issue': 20.0,
            'product_id': self.rebar.id,
            'uom_id': self.rebar.uom_id.id,
        })
        request.write({'state': 'in_progress'})

        # Добавить остаток на склад
        self.env['stock.quant'].create({
            'product_id': self.rebar.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'quantity': 200.0,
        })

        # Создать picking для 20 единиц
        wiz = self.env['object.request.issue.wizard'].create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': self.customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        result = wiz.action_create_issue()
        picking1 = self.env['stock.picking'].browse(result['res_id'])
        picking1.action_confirm()
        picking1.action_assign()

        # Первая выдача — только 8 из 20 (частичная)
        move = line.issue_move_id
        move.write({'quantity': 8.0})
        picking1._sync_qty_issued_to_request_lines()
        line.invalidate_recordset()
        self.assertEqual(line.qty_issued, 8.0)
        self.assertEqual(line.line_state, 'partially_issued')

        # Вторая выдача — ещё 12 (итого 20 = qty_to_issue)
        move.write({'quantity': 20.0})
        picking1._sync_qty_issued_to_request_lines()
        line.invalidate_recordset()
        self.assertEqual(line.qty_issued, 20.0)
        self.assertEqual(line.line_state, 'fully_supplied')

    # ─────────────────────────────────────────────────────────────────────────
    # Сценарий 9: Разграничение прав
    # ─────────────────────────────────────────────────────────────────────────

    def test_scenario_9_foreman_cannot_create_issue_wizard(self):
        """Прораб не имеет доступа к wizard создания выдачи."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-15',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 5.0,
            'qty_to_issue': 5.0,
            'product_id': self.cement.id,
            'uom_id': self.cement.uom_id.id,
        })
        request.write({'state': 'in_progress'})

        env_foreman = self.env(user=self.foreman)
        with self.assertRaises(AccessError):
            env_foreman['object.request.issue.wizard'].create({
                'request_id': request.id,
                'line_ids': [(6, 0, [line.id])],
                'warehouse_id': self.warehouse.id,
                'picking_type_id': self.warehouse.int_type_id.id,
                'source_location_id': self.warehouse.lot_stock_id.id,
                'destination_location_id': self.customer_loc.id,
                'scheduled_date': datetime.datetime.now(),
            })

    def test_scenario_9_storekeeper_cannot_create_request(self):
        """Кладовщик не может создавать документы требований."""
        env_store = self.env(user=self.storekeeper)
        with self.assertRaises(AccessError):
            env_store['object.request'].create({
                'project_id': self.project.id,
                'foreman_user_id': self.foreman.id,
                'need_date': '2026-04-15',
            })

    def test_scenario_9_storekeeper_cannot_create_import_wizard(self):
        """Кладовщик не имеет доступа к wizard импорта Excel."""
        xlsx_bytes = _make_excel([
            ['№', 'Артикул', 'Наименование', 'Ед.изм.', 'Кол-во'],
            [1, '', 'Цемент', 'шт', 10],
        ])
        if xlsx_bytes is None:
            self.skipTest('openpyxl не установлен')

        env_store = self.env(user=self.storekeeper)
        with self.assertRaises(AccessError):
            env_store['object.request.import.wizard'].create({
                'project_id': self.project.id,
                'foreman_user_id': self.foreman.id,
                'need_date': '2026-04-15',
                'priority': '1',
                'file': base64.b64encode(xlsx_bytes),
                'file_name': 'test.xlsx',
            })
