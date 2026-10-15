"""
TD-016: расчётная масса 1 шт. болтов и гаек по размерам ГОСТ.
"""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.fastener_mass import parse_fastener, suggest_kg_per_piece


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

    def test_nut_m16_mass(self):
        """Гайка М16: S=24, m=13 → ≈ 33,6 г."""
        self.assertAlmostEqual(
            suggest_kg_per_piece("Гайка М16 ГОСТ 5915-70"), 0.0336
        )

    def test_bolt_m16x55_mass(self):
        """Болт М16×55: головка k=10, резьба b=38 → ≈ 116,6 г."""
        self.assertAlmostEqual(suggest_kg_per_piece("Болт М16×55"), 0.1166)

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
        self.assertAlmostEqual(card.kg_per_piece, 0.0336)

    def test_piece_card_not_filled(self):
        """Карточка в шт. массу 1 шт. не получает."""
        card = self._template("Гайка М16 ГОСТ 5915-70", self.unit)
        self.assertFalse(card.kg_per_piece)
        self.assertAlmostEqual(card.kg_per_piece_suggested, 0.0336)

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
        self.assertAlmostEqual(card.kg_per_piece, 0.1166)

    def test_apply_suggestion_button(self):
        """Кнопка «Подставить» заменяет временный коэффициент."""
        card = self._template("Болт М16×55", self.kg, kg_per_piece=0.091)
        card.action_apply_kg_per_piece_suggestion()
        self.assertAlmostEqual(card.kg_per_piece, 0.1166)

    def test_unknown_fastener_not_filled(self):
        card = self._template("Проволока вязальная", self.kg)
        self.assertFalse(card.kg_per_piece)
