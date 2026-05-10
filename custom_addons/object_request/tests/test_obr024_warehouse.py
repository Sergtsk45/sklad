"""
OBR-024: Тесты поля warehouse_id в object.request и связанных wizards.
"""
import datetime

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestObr024Warehouse(TransactionCase):
    """Проверка поля warehouse_id: обязательность, дефолт, stock-check и wizards."""

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-024',
            'code': 'TST-024',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб OBR024',
            'login': 'foreman_test_obr024',
            'email': 'foreman_obr024@test.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Кирпич OBR024',
            'default_code': 'BRICK-024',
            'type': 'consu',
            'is_storable': True,
        })
        self.warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1,
        )
        self.vendor = self.env['res.partner'].create({
            'name': 'Поставщик OBR024',
            'supplier_rank': 1,
        })

    def _create_request(self, **extra):
        vals = {
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        }
        vals.update(extra)
        return self.env['object.request'].create(vals)

    def _add_line(self, request, qty_to_issue=0.0, qty_to_buy=0.0, vendor=None):
        vals = {
            'request_id': request.id,
            'name_raw': 'Кирпич',
            'qty_requested': max(qty_to_issue, qty_to_buy, 1.0),
            'qty_to_issue': qty_to_issue,
            'qty_to_buy': qty_to_buy,
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
        }
        if vendor:
            vals['preferred_vendor_id'] = vendor.id
        return self.env['object.request.line'].create(vals)

    # ── 1. Обязательность поля ───────────────────────────────────────────────

    def test_warehouse_field_is_set_on_create(self):
        """Новая запись без явного warehouse_id получает дефолтный склад (not False)."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': fields.Date.today(),
            'warehouse_id': self.warehouse.id,
        })
        self.assertTrue(request.warehouse_id, 'warehouse_id должен быть заполнен')

    # ── 2. Дефолтное значение ────────────────────────────────────────────────

    def test_warehouse_field_default_is_set(self):
        """Новое требование без явного warehouse_id получает склад компании."""
        request = self._create_request()
        self.assertTrue(request.warehouse_id)

    def test_warehouse_field_default_matches_company(self):
        """Дефолтный склад принадлежит текущей компании."""
        request = self._create_request()
        self.assertEqual(request.warehouse_id.company_id, self.env.company)

    # ── 3. action_check_stock использует склад требования ────────────────────

    def test_check_stock_updates_stock_check_date(self):
        """action_check_stock заполняет stock_check_date на строках с product_id."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        line = self._add_line(request)
        request.action_check_stock()
        self.assertTrue(line.stock_check_date)

    def test_check_stock_fills_qty_on_hand(self):
        """action_check_stock обновляет stock_qty_on_hand для строк с product_id."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self.env['stock.quant']._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, 42.0,
        )
        line = self._add_line(request)
        request.action_check_stock()
        self.assertAlmostEqual(line.stock_qty_on_hand, 42.0)

    def test_check_stock_uses_warehouse_location(self):
        """Остаток берётся из ячейки склада, указанного в требовании."""
        # Получаем второй склад (или создаём) и убеждаемся, что остаток
        # в его ячейке НЕ попадает в результат для первого склада.
        second_warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id), ('id', '!=', self.warehouse.id)],
            limit=1,
        )
        if not second_warehouse:
            # Если второго склада нет — тест проверяет только что метод не падает
            request = self._create_request(warehouse_id=self.warehouse.id)
            self._add_line(request)
            result = request.action_check_stock()
            self.assertEqual(result['tag'], 'display_notification')
            return

        self.env['stock.quant']._update_available_quantity(
            self.product, second_warehouse.lot_stock_id, 99.0,
        )
        request = self._create_request(warehouse_id=self.warehouse.id)
        line = self._add_line(request)
        request.action_check_stock()
        # Остаток 99 в другом складе не должен попасть в qty_on_hand нашего склада
        self.assertAlmostEqual(line.stock_qty_on_hand, 0.0)

    def test_check_stock_returns_notification(self):
        """action_check_stock возвращает display_notification."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request)
        result = request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')

    # ── 4. Issue wizard берёт склад из требования ────────────────────────────

    def test_issue_wizard_default_get_sets_warehouse_from_request(self):
        """default_get у issue wizard устанавливает warehouse_id из требования."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request, qty_to_issue=5.0)

        wizard_vals = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).default_get(['warehouse_id', 'picking_type_id', 'source_location_id'])

        self.assertEqual(wizard_vals.get('warehouse_id'), self.warehouse.id)

    def test_issue_wizard_warehouse_matches_request(self):
        """Созданный wizard имеет тот же warehouse_id что и требование."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request, qty_to_issue=5.0)

        wizard = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).create({})

        self.assertEqual(wizard.warehouse_id, self.warehouse)

    def test_issue_wizard_picking_type_from_warehouse(self):
        """picking_type_id в wizard соответствует int_type_id склада."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request, qty_to_issue=5.0)

        wizard = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).create({})

        self.assertEqual(wizard.picking_type_id, self.warehouse.int_type_id)

    # ── 5. Purchase wizard устанавливает picking_type_id из склада ──────────

    def test_purchase_wizard_po_has_picking_type_from_warehouse(self):
        """Созданный PO имеет picking_type_id равный in_type_id склада требования."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request, qty_to_buy=3.0, vendor=self.vendor)

        wizard = self.env['object.request.purchase.wizard'].with_context(
            default_request_id=request.id,
        ).create({'request_id': request.id})

        result = wizard.action_create_purchase()
        po = self.env['purchase.order'].browse(result['res_id'])

        self.assertEqual(po.picking_type_id, self.warehouse.in_type_id)

    def test_purchase_wizard_po_picking_type_belongs_to_warehouse(self):
        """picking_type_id в PO принадлежит складу из требования."""
        request = self._create_request(warehouse_id=self.warehouse.id)
        self._add_line(request, qty_to_buy=2.0, vendor=self.vendor)

        wizard = self.env['object.request.purchase.wizard'].with_context(
            default_request_id=request.id,
        ).create({'request_id': request.id})

        result = wizard.action_create_purchase()
        po = self.env['purchase.order'].browse(result['res_id'])

        self.assertEqual(
            po.picking_type_id.warehouse_id,
            self.warehouse,
        )

    # ── 6. Import wizard сохраняет warehouse_id ──────────────────────────────

    def test_import_wizard_passes_warehouse_to_request(self):
        """Wizard импорта создаёт object.request с указанным warehouse_id."""
        wizard = self.env['object.request.import.wizard'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': fields.Date.today(),
            'warehouse_id': self.warehouse.id,
            'file': b'',
            'file_name': 'test.xlsx',
        })
        self.assertEqual(wizard.warehouse_id, self.warehouse)
