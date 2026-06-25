"""
OBR-034: Фильтр распределения по складам и выбор складов выдачи.
"""
import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


DEFAULT_ISSUE_WAREHOUSE_DATA = (
    ("Офис", "Офис. Стеллаж"),
    ("Ос.ск", "Основной склад"),
    ("метал", "Склад металла"),
    ("Расх", "Расходники"),
)


@tagged("post_install", "-at_install", "obr034")
class TestObr034IssueWarehouseFilter(TransactionCase):
    """Склады выдачи и скрытие нулевых остатков в распределении."""

    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR-034"}
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR034",
                "login": "foreman_test_obr034",
                "email": "foreman_obr034@test.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Товар OBR034",
                "default_code": "OBR034-ITEM",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.default_issue_warehouses = self._ensure_default_issue_warehouses()
        self.warehouse1 = self.default_issue_warehouses[0]
        self.warehouse2 = self.default_issue_warehouses[1]
        self.request = self._create_request()
        self.line = self._add_line(self.request)

    def _ensure_default_issue_warehouses(self):
        Warehouse = (
            self.env["stock.warehouse"].with_context(active_test=False).sudo()
        )
        warehouses = self.env["stock.warehouse"]
        for code, name in DEFAULT_ISSUE_WAREHOUSE_DATA:
            warehouse = Warehouse.search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("code", "=", code),
                ],
                limit=1,
            )
            if warehouse:
                warehouse.write({"name": name, "active": True})
            else:
                warehouse = Warehouse.create(
                    {
                        "name": name,
                        "code": code,
                        "company_id": self.env.company.id,
                    }
                )
            warehouses |= warehouse
        return warehouses

    def _create_request(self):
        return self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )

    def _add_line(self, request):
        return self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Материал OBR034",
                "qty_requested": 10.0,
                "product_id": self.product.id,
                "uom_id": self.product.uom_id.id,
            }
        )

    def _put_stock(self, warehouse, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            warehouse.lot_stock_id,
            qty,
        )

    def test_new_request_gets_default_issue_warehouses(self):
        """Новое требование получает базовые склады и склад объекта."""
        allowed = self.request._get_issue_warehouses()
        expected = (
            self.default_issue_warehouses | self.project.warehouse_id
        )
        expected_names = {
            "Офис. Стеллаж",
            "Основной склад",
            "Склад металла",
            "Расходники",
            self.project.warehouse_id.name,
        }
        self.assertEqual(set(allowed.ids), set(expected.ids))
        self.assertTrue(expected_names <= set(allowed.mapped("name")))

    def test_project_change_updates_defaults_until_manual_selection(self):
        """Смена объекта обновляет дефолт, но не ручной выбор складов."""
        other_project = self.env["object.request.project"].create(
            {"name": "Другой объект OBR-034"}
        )

        self.request.write({"project_id": other_project.id})
        expected = (
            self.default_issue_warehouses | other_project.warehouse_id
        )
        self.assertFalse(self.request.issue_warehouse_selection_manual)
        self.assertEqual(
            set(self.request.issue_warehouse_ids.ids),
            set(expected.ids),
        )

        self.request.write(
            {"issue_warehouse_ids": [(6, 0, [self.warehouse2.id])]}
        )
        self.assertTrue(self.request.issue_warehouse_selection_manual)
        self.request.write({"project_id": self.project.id})
        self.assertEqual(
            set(self.request.issue_warehouse_ids.ids),
            {self.warehouse2.id},
        )

    def test_line_stock_ids_hide_zero_rows_by_default(self):
        """По умолчанию в таблице видны только строки с остатком/планом."""
        self._put_stock(self.warehouse1, 5.0)
        self.request.action_check_stock()

        visible = self.request.line_stock_ids
        self.assertTrue(all(row.qty_on_hand > 0 for row in visible))
        self.assertEqual(len(visible), 1)

    def test_show_zero_toggle_displays_all_selected_warehouse_rows(self):
        """Переключатель показывает нулевые строки по выбранным складам."""
        self._put_stock(self.warehouse1, 5.0)
        self.request.write(
            {
                "issue_warehouse_ids": [
                    (6, 0, [self.warehouse1.id, self.warehouse2.id])
                ],
            }
        )
        self.request.action_check_stock()
        self.assertEqual(len(self.request.line_stock_ids), 1)

        self.request.stock_distribution_show_zero = True
        self.request.invalidate_recordset(["line_stock_ids"])
        self.assertEqual(len(self.request.line_stock_ids), 2)

    def test_excluded_warehouse_not_used_in_issue_max(self):
        """Авто-разбивка не берёт товар со склада, исключённого из выдачи."""
        self._put_stock(self.warehouse1, 10.0)
        self._put_stock(self.warehouse2, 10.0)
        self.request.write(
            {
                "issue_warehouse_ids": [(6, 0, [self.warehouse2.id])],
            }
        )
        self.request.action_check_stock()
        self.line.action_issue_max()

        stock_wh1 = self.line.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.warehouse1
        )
        stock_wh2 = self.line.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.warehouse2
        )
        self.assertAlmostEqual(self.line.qty_to_issue, 10.0)
        if stock_wh1:
            self.assertAlmostEqual(stock_wh1.qty_to_issue, 0.0)
        self.assertAlmostEqual(stock_wh2.qty_to_issue, 10.0)

    def test_removing_warehouse_clears_issue_plan(self):
        """Исключение склада из списка сбрасывает план выдачи с него."""
        self._put_stock(self.warehouse1, 10.0)
        self.request.write(
            {
                "issue_warehouse_ids": [
                    (6, 0, [self.warehouse1.id, self.warehouse2.id])
                ],
            }
        )
        self.request.action_check_stock()
        self.line.action_issue_max()
        stock_wh1 = self.line.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.warehouse1
        )
        self.assertAlmostEqual(stock_wh1.qty_to_issue, 10.0)

        self.request.write(
            {"issue_warehouse_ids": [(6, 0, [self.warehouse2.id])]}
        )
        self.line.invalidate_recordset()
        stock_wh1 = self.line.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.warehouse1
        )
        self.assertTrue(stock_wh1)
        self.assertAlmostEqual(stock_wh1.qty_to_issue, 0.0)
        self.assertAlmostEqual(stock_wh1.qty_on_hand, 10.0)
        self.assertAlmostEqual(self.line.qty_to_issue, 0.0)
        self.assertAlmostEqual(self.line.qty_to_buy, 10.0)

    def test_warehouse_filter_shows_only_selected_warehouse_rows(self):
        """Фильтр по складу не требует переключателя нулевых остатков."""
        self._put_stock(self.warehouse1, 5.0)
        self._put_stock(self.warehouse2, 7.0)
        self.request.action_check_stock()
        self.assertEqual(len(self.request.line_stock_ids), 2)

        self.request.write(
            {
                "stock_distribution_filter_warehouse_id": self.warehouse1.id,
            }
        )
        visible = self.request.line_stock_ids
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible.warehouse_id, self.warehouse1)
        self.assertAlmostEqual(visible.qty_on_hand, 5.0)

    def test_refresh_key_bumps_on_distribution_filter_change(self):
        """Изменение фильтров увеличивает ключ обновления таблицы."""
        key_before = self.request.stock_distribution_refresh_key
        self.request.write({"stock_distribution_show_zero": True})
        self.assertGreater(
            self.request.stock_distribution_refresh_key,
            key_before,
        )
