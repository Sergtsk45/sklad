"""
TD-016: масса 1 шт. болтов и гаек по ГОСТ, карточки метизов ГОСТ.
"""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.fastener_mass import (
    gost_fastener_specs,
    parse_fastener,
    suggest_kg_per_piece,
    theoretical_mass_kg,
)


@tagged("post_install", "-at_install")
class TestTD016FastenerParse(TransactionCase):
    def test_bolt_with_length(self):
        self.assertEqual(parse_fastener("Болт М16×55"), ("bolt", 16, 55))

    def test_bolt_gost_designation(self):
        """«М16-6gх55.58 ГОСТ 7798-70» — длина 55, класс точности пропущен."""
        self.assertEqual(
            parse_fastener("Болт М16-6gх55.58 ГОСТ 7798-70"),
            ("bolt", 16, 55),
        )

    def test_bolt_fine_pitch(self):
        self.assertEqual(parse_fastener("Болт M16x1,5x60"), ("bolt", 16, 60))

    def test_nut_latin_m(self):
        self.assertEqual(
            parse_fastener("Гайка M20 DIN 934"), ("nut", 20, None)
        )

    def test_bolt_without_length_is_unknown(self):
        self.assertIsNone(parse_fastener("Болт М10"))

    def test_other_nut_standard_is_unknown(self):
        """Низкая гайка ГОСТ 5916 — другие размеры, без расчёта."""
        self.assertIsNone(parse_fastener("Гайка М16 ГОСТ 5916-70"))

    def test_special_fasteners_excluded(self):
        for name in (
            "Болт анкерный М12х100",
            "Болт мебельный М6х40",
            "Гайка-барашек М8",
            "Шпилька М8х2000",
        ):
            with self.subTest(name=name):
                self.assertIsNone(parse_fastener(name))

    def test_size_outside_table_is_unknown(self):
        self.assertIsNone(parse_fastener("Гайка М36"))

    def test_nut_m16_table_mass(self):
        """Гайка М16 — табличная масса ГОСТ 5915: 37,61 г."""
        self.assertAlmostEqual(
            suggest_kg_per_piece("Гайка М16 ГОСТ 5915-70"), 0.03761
        )

    def test_bolt_m16x55_table_mass(self):
        """Болт М16×55 — табличная масса ГОСТ 7798: 121,5 г."""
        self.assertAlmostEqual(suggest_kg_per_piece("Болт М16×55"), 0.1215)

    def test_bolt_outside_table_is_calculated(self):
        """М12×100 нет в таблице — масса по размерам стандарта."""
        self.assertAlmostEqual(
            suggest_kg_per_piece("Болт М12х100"),
            theoretical_mass_kg("bolt", 12, 100),
        )

    def test_longer_bolt_is_heavier(self):
        self.assertGreater(
            suggest_kg_per_piece("Болт М12х80"),
            suggest_kg_per_piece("Болт М12х50"),
        )


@tagged("post_install", "-at_install")
class TestTD016FastenerCard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.unit = cls.env.ref("uom.product_uom_unit")

    def _template(self, name, uom, **vals):
        return self.env["product.template"].create(
            {"name": name, "type": "consu", "uom_id": uom.id, **vals}
        )

    def test_new_kg_card_gets_suggested_mass(self):
        """Новая гайка в кг сразу получает расчётную массу."""
        card = self._template("Гайка М16 ГОСТ 5915-70", self.kg)
        self.assertAlmostEqual(card.kg_per_piece, 0.03761)

    def test_piece_card_not_filled(self):
        """Карточка в шт. массу 1 шт. не получает."""
        card = self._template("Гайка М16 ГОСТ 5915-70", self.unit)
        self.assertFalse(card.kg_per_piece)
        self.assertAlmostEqual(card.kg_per_piece_suggested, 0.03761)

    def test_explicit_mass_kept(self):
        """Указанная вручную масса не перезаписывается."""
        card = self._template(
            "Гайка М16 ГОСТ 5915-70", self.kg, kg_per_piece=0.035
        )
        self.assertAlmostEqual(card.kg_per_piece, 0.035)

    def test_switch_to_kg_fills_mass(self):
        """Перевод карточки в кг подставляет расчётную массу."""
        card = self._template("Болт М16×55", self.unit)
        card.uom_id = self.kg
        self.assertAlmostEqual(card.kg_per_piece, 0.1215)

    def test_apply_suggestion_button(self):
        """Кнопка «Подставить» заменяет временный коэффициент."""
        card = self._template("Болт М16×55", self.kg, kg_per_piece=0.091)
        card.action_apply_kg_per_piece_suggestion()
        self.assertAlmostEqual(card.kg_per_piece, 0.1215)

    def test_unknown_fastener_not_filled(self):
        card = self._template("Проволока вязальная", self.kg)
        self.assertFalse(card.kg_per_piece)


@tagged("post_install", "-at_install")
class TestTD016GostFastenerCards(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.Template = cls.env["product.template"]

    def _card(self, name):
        return self.Template.search([("name", "=", name)])

    def test_black_and_zinc_card_per_size(self):
        """113 типоразмеров ГОСТ → 226 карточек: чёрная и оцинкованная."""
        created = self.Template._create_gost_fastener_templates()
        self.assertEqual(len(created), 2 * len(gost_fastener_specs()))

    def test_card_in_kg_with_table_mass(self):
        self.Template._create_gost_fastener_templates()
        card = self._card("Болт М20×100 ГОСТ 7798-70 оцинкованный")
        self.assertEqual(card.uom_id, self.kg)
        self.assertTrue(card.is_storable)
        self.assertAlmostEqual(card.kg_per_piece, 0.3147)

    def test_zinc_nut_name(self):
        self.Template._create_gost_fastener_templates()
        card = self._card("Гайка М24 ГОСТ 5915-70 оцинкованная")
        self.assertAlmostEqual(card.kg_per_piece, 0.12287)

    def test_existing_kg_card_not_duplicated(self):
        """Чёрный болт М16×55 в кг уже есть — создаётся только оцинкованный."""
        self.Template.create(
            {"name": "Болт М16×55", "type": "consu", "uom_id": self.kg.id}
        )
        created = self.Template._create_gost_fastener_templates()
        names = created.mapped("name")
        self.assertNotIn("Болт М16×55 ГОСТ 7798-70", names)
        self.assertIn("Болт М16×55 ГОСТ 7798-70 оцинкованный", names)

    def test_piece_card_does_not_block_creation(self):
        """Карточка в шт. не считается дублем кг-карточки."""
        self.Template.create({
            "name": "Гайка М16 ГОСТ 5915-70",
            "type": "consu",
            "uom_id": self.env.ref("uom.product_uom_unit").id,
        })
        created = self.Template._create_gost_fastener_templates()
        self.assertIn("Гайка М16 ГОСТ 5915-70", created.mapped("name"))

    def test_second_run_creates_nothing(self):
        self.Template._create_gost_fastener_templates()
        self.assertFalse(self.Template._create_gost_fastener_templates())

    def test_cards_in_fastener_category(self):
        """«Метизы и крепёж» важнее «Расходников»."""
        Category = self.env["product.category"]
        Category.create({"name": "Расходники"})
        metizy = Category.create({"name": "Метизы и крепёж"})
        created = self.Template._create_gost_fastener_templates()
        self.assertEqual(created.categ_id, metizy)

    def test_consumables_category_fallback(self):
        Category = self.env["product.category"]
        Category.search([("name", "=", "Метизы и крепёж")]).name = "Другое"
        consumables = Category.create({"name": "Расходники"})
        created = self.Template._create_gost_fastener_templates()
        self.assertEqual(created.categ_id, consumables)
