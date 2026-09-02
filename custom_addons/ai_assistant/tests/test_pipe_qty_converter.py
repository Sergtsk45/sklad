# -*- coding: utf-8 -*-
"""TD-002: unit tests for pipe quantity conversion."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.pipe_qty_converter import (
    convert_pipe_quantity,
    extract_pipe_length_m,
)


@tagged("post_install", "-at_install", "td002")
class TestPipeQtyConverter(TransactionCase):
    def test_extract_pipe_length_from_l_hint(self):
        self.assertEqual(extract_pipe_length_m("Труба э/с 89×3,5 L12"), 12.0)

    def test_convert_kg_to_m(self):
        result = convert_pipe_quantity(
            488.0,
            "кг",
            kg_per_meter=4.88,
            description="Труба ВГП 89×3,5",
        )
        self.assertEqual(result["meters"], 100.0)
        self.assertIn("488 кг / 4.88 кг/м = 100 м", result["formula"])

    def test_convert_ton_to_m(self):
        result = convert_pipe_quantity(
            0.488,
            "т",
            kg_per_meter=4.88,
            description="Труба ВГП 89×3,5",
        )
        self.assertEqual(result["meters"], 100.0)

    def test_convert_piece_to_m(self):
        result = convert_pipe_quantity(
            2,
            "шт",
            description="Труба э/с 76×3,5 L12",
        )
        self.assertEqual(result["meters"], 24.0)
        self.assertIn("2 шт × 12 м = 24 м", result["formula"])

