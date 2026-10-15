"""
TD-016: метизы в требовании вводятся в шт., учёт и закупка — в кг.
"""
import datetime
import importlib.util
import os

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _load_migration():
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "migrations",
        "19.0.1.12.0",
        "post-migrate.py",
    )
    spec = importlib.util.spec_from_file_location("td016_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@tagged("post_install", "-at_install")
class TestTD016PieceToKg(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.nut = cls.env["product.product"].create(
            {
                "name": "Гайка М16 TD016",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.kg.id,
                "kg_per_piece": 0.019,
            }
        )
        cls.wire = cls.env["product.product"].create(
            {
                "name": "Проволока TD016",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.kg.id,
            }
        )
        cls.valve = cls.env["product.product"].create(
            {"name": "Кран TD016", "type": "consu", "uom_id": cls.unit.id}
        )
        cls.project = cls.env["object.request.project"].create(
            {"name": "Объект TD-016"}
        )
        cls.foreman = cls.env["res.users"].create(
            {"name": "Прораб TD016", "login": "foreman_td016"}
        )

    def setUp(self):
        super().setUp()
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )

    def _line(self, **vals):
        return self.env["object.request.line"].create(
            {"request_id": self.request.id, "name_raw": "Гайка М16", **vals}
        )

    # --- Карточка ---

    def test_kg_per_piece_requires_weight_uom(self):
        """«Масса 1 шт.» нельзя задать товару в штуках."""
        with self.assertRaises(ValidationError):
            self.valve.kg_per_piece = 0.5

    # --- Ввод и импорт ---

    def test_pieces_converted_to_kg(self):
        """100 шт. × 0,019 = 1,9 кг."""
        line = self._line(product_id=self.nut.id, qty_requested_pcs=100.0,
                          qty_requested=1.0)
        self.assertAlmostEqual(line.qty_requested, 1.9)
        self.assertEqual(line.uom_id, self.kg)

    def test_import_in_pieces_converted(self):
        """Импорт «шт.» на кг-товар: количество файла — штуки."""
        line = self._line(product_id=self.nut.id, uom_id=self.kg.id,
                          uom_raw="шт.", qty_requested=100.0)
        self.assertAlmostEqual(line.qty_requested_pcs, 100.0)
        self.assertAlmostEqual(line.qty_requested, 1.9)

    def test_import_in_kg_not_converted(self):
        """Импорт «кг» на метиз остаётся в кг."""
        line = self._line(product_id=self.nut.id, uom_id=self.kg.id,
                          uom_raw="кг", qty_requested=2.0)
        self.assertAlmostEqual(line.qty_requested, 2.0)
        self.assertFalse(line.qty_requested_pcs)

    def test_product_without_factor_ignores_pieces(self):
        """Без «Массы 1 шт.» пересчёта нет."""
        line = self._line(product_id=self.wire.id, uom_raw="шт.",
                          qty_requested=5.0)
        self.assertAlmostEqual(line.qty_requested, 5.0)
        self.assertFalse(line.qty_requested_pcs)

    def test_onchange_pieces_shows_kg(self):
        """В форме «Запрошено» пересчитывается сразу."""
        line = self.env["object.request.line"].new(
            {"product_id": self.nut.id, "qty_requested_pcs": 100.0}
        )
        line._onchange_qty_requested_pcs()
        self.assertAlmostEqual(line.qty_requested, 1.9)

    # --- Сопоставление ---

    def test_matching_converts_piece_line(self):
        """Сопоставление строки «шт.» с метизом переводит её в кг."""
        line = self._line(uom_raw="шт.", qty_requested=100.0)
        line.write({"product_id": self.nut.id, "uom_id": self.kg.id})
        self.assertAlmostEqual(line.qty_requested, 1.9)
        self.assertAlmostEqual(line.qty_requested_pcs, 100.0)

    def test_matching_in_progress_converts_despite_lock(self):
        """Смена товара в работе — пересчёт единицы, а не потребности."""
        line = self._line(uom_raw="шт.", qty_requested=100.0)
        self.request.write({"state": "in_progress"})
        line.write({"product_id": self.nut.id})
        self.assertAlmostEqual(line.qty_requested, 1.9)

    def test_pieces_change_in_progress_is_locked(self):
        """Изменить штуки в работе нельзя — это изменение потребности."""
        line = self._line(product_id=self.nut.id, qty_requested_pcs=100.0,
                          qty_requested=1.0)
        self.request.write({"state": "in_progress"})
        with self.assertRaises(UserError):
            line.write({"qty_requested_pcs": 120.0})

    def test_switch_to_piece_product_restores_pieces(self):
        """Замена метиза на товар в шт. возвращает количество в штуки."""
        line = self._line(product_id=self.nut.id, qty_requested_pcs=100.0,
                          qty_requested=1.0)
        line.write({"product_id": self.valve.id, "uom_id": self.unit.id})
        self.assertAlmostEqual(line.qty_requested, 100.0)
        self.assertFalse(line.qty_requested_pcs)

    # --- Склад ---

    def test_auto_split_reserves_kg(self):
        """Остаток 5 кг: 100 шт. = 1,9 кг в резерве."""
        line = self._line(product_id=self.nut.id, qty_requested_pcs=100.0,
                          qty_requested=1.0)
        warehouse = self.request._get_issue_warehouses()[:1]
        self.env["stock.quant"]._update_available_quantity(
            self.nut, warehouse.lot_stock_id, 5.0
        )
        self.request.write({"state": "in_progress"})
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.assertAlmostEqual(line.qty_reserved, 1.9)

    # --- Миграция строк #929 / #362 ---

    def test_migration_converts_piece_line(self):
        """Строка в шт. на кг-карточке пересчитывается миграцией."""
        line = self._line(product_id=self.nut.id, uom_id=self.kg.id,
                          qty_requested=1.0)
        line.with_context(or_piece_conversion_done=True).write(
            {"qty_requested": 100.0, "qty_to_buy": 100.0}
        )
        self.request.write({"state": "in_progress"})
        _load_migration()._convert_piece_line(self.env, line)
        self.assertAlmostEqual(line.qty_requested, 1.9)
        self.assertAlmostEqual(line.qty_to_buy, 0.0)

    def test_migration_skips_line_with_purchase(self):
        """Строку с закупкой миграция не трогает."""
        line = self._line(product_id=self.nut.id, uom_id=self.kg.id,
                          qty_requested=100.0)
        line.qty_requested_pcs = 0.0
        line.with_context(or_piece_conversion_done=True).write(
            {"qty_requested": 100.0, "qty_requested_pcs": 0.0}
        )
        line.purchase_order_line_id = self._purchase_line()
        converted = _load_migration()._convert_piece_line(self.env, line)
        self.assertFalse(converted)

    def _purchase_line(self):
        vendor = self.env["res.partner"].create({"name": "Татаринов TD016"})
        order = self.env["purchase.order"].create(
            {
                "partner_id": vendor.id,
                "order_line": [
                    (0, 0, {"product_id": self.nut.id, "product_qty": 1.0})
                ],
            }
        )
        return order.order_line
