# @file: test_amurstroy_parse.py
# @description: Тесты парсера договор-счетов Амурстроя
# @created: 2026-06-25

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "amurstroy_parse.py"
)
_spec = importlib.util.spec_from_file_location("amurstroy_parse", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_OCR_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scanned-invoice-parsing"
    / "scripts"
    / "ocr_parse.py"
)
_ocr_spec = importlib.util.spec_from_file_location("ocr_parse", _OCR_SCRIPT)
_ocr_mod = importlib.util.module_from_spec(_ocr_spec)
sys.modules["ocr_parse"] = _ocr_mod
_ocr_spec.loader.exec_module(_ocr_mod)

INVOICES = Path(__file__).resolve().parents[4] / "docs" / "invoices"


@unittest.skipUnless(INVOICES.is_dir(), "docs/invoices not found")
class TestAmurstroyParse(unittest.TestCase):
    def test_kley_four_items_sum(self):
        path = INVOICES / "Клей schetП000014101.pdf"
        if not path.is_file():
            self.skipTest("fixture missing")
        result = _mod.parse_amurstroy_pdf(path)
        self.assertEqual(result["format"], "amurstroy_contract_invoice")
        self.assertEqual(result["partner_ref"], "П000014101")
        self.assertEqual(len(result["items"]), 4)
        self.assertTrue(result["needs_review"])
        items_sum = sum(i["amount"] for i in result["items"])
        subtotal = result["totals"]["subtotal_wo_vat"]
        self.assertLess(abs(items_sum - subtotal), 15.0)

    def test_is_amurstroy_by_inn(self):
        self.assertTrue(_mod.is_amurstroy_text("ИНН 2801019127 Договор-Счет"))
        self.assertFalse(_mod.is_amurstroy_text("ИНН 280110406377 счет"))

    def test_money_merge_split_net(self):
        vals = _mod._money_tokens("308.00 4620.00 231.00 389.00")
        self.assertEqual(vals[-1], 4389.0)

    def test_partner_ref_normalizes_short_p_number(self):
        self.assertEqual(_mod._partner_ref("П14101"), "П000014101")

    def test_sum_mismatch_sets_needs_review(self):
        result = _mod.parse_amurstroy_texts(
            "ИНН 2801019127 Договор-Счет № П14101 от 23.06.26",
            """
без скидки
1  |Клей Момент "88", 750мл 10 шт 1657.00 16570.00 828.50 15741.50
Итого: 20000.00
Всего наименований 1, на сумму 20000.00 руб.
""",
        )
        self.assertTrue(result["needs_review"])
        self.assertTrue(any("sum_mismatch" in w for w in result["warnings"]))

    def test_empty_items_sets_needs_review(self):
        result = _mod.parse_amurstroy_texts(
            "ИНН 2801019127 Договор-Счет № П14101 от 23.06.26",
            "без скидки\nИтого: 20000.00",
        )
        self.assertTrue(result["needs_review"])
        self.assertIn("items_empty", result["warnings"])

    def test_common_ocr_delegates_to_amurstroy_contract(self):
        path = INVOICES / "Клей schetП000014101.pdf"
        if not path.is_file():
            self.skipTest("fixture missing")
        result = _ocr_mod.parse_invoice_pdf(path)
        self.assertEqual(result["format"], "amurstroy_contract_invoice")
        self.assertEqual(result["partner_ref"], "П000014101")
        self.assertIn("needs_review", result)

    def test_common_ocr_parser_failure_is_fail_closed(self):
        path = INVOICES / "Клей schetП000014101.pdf"
        if not path.is_file():
            self.skipTest("fixture missing")

        original_module = sys.modules.get("amurstroy_parse")
        fake_module = types.ModuleType("amurstroy_parse")

        def _raise_parser_error(*args, **kwargs):
            raise RuntimeError("boom")

        fake_module.parse_amurstroy_texts = _raise_parser_error
        sys.modules["amurstroy_parse"] = fake_module
        try:
            result = _ocr_mod.parse_invoice_pdf(path)
        finally:
            if original_module is None:
                sys.modules.pop("amurstroy_parse", None)
            else:
                sys.modules["amurstroy_parse"] = original_module

        self.assertTrue(result["needs_review"])
        self.assertTrue(any("amurstroy_parser_failed" in w for w in result["warnings"]))

    def test_extract_items_from_table_snippet(self):
        table = """
без скидки
1  |Клей Момент "88", 750мл 10 шт 1657.00 16570.00 828.50 15741.50
Итого: 15741.50
"""
        items = _mod.extract_amurstroy_items(table)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["qty"], 10)
        self.assertAlmostEqual(items[0]["amount"], 15741.5, places=2)


if __name__ == "__main__":
    unittest.main()
