#!/usr/bin/env python3
"""
@file: test_invoice_identity.py
@description: Тесты отпечатка файла счёта и разбора шапки 1С «Счет на оплату»
@dependencies: invoice_identity.py, ocr_parse.py
@created: 2026-09-15
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from invoice_identity import file_identity, sha256_file
from ocr_parse import _PAY_INVOICE_RE, _SUPPLIER_LINE_RE, _extract_header


class InvoiceIdentityTests(unittest.TestCase):
    def test_same_bytes_detected_after_copy_with_other_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = folder / "Маска электросварщика.pdf"
            original.write_bytes(b"%PDF-1.4 fake invoice body\n")
            renamed = folder / "Маска 3 шт..pdf"
            shutil.copy2(original, renamed)

            ident = file_identity(renamed, scan_dir=folder)
            self.assertEqual(ident["sha256"], sha256_file(original))
            self.assertEqual(ident["same_bytes"], [str(original.resolve())])

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            file_identity(Path("/tmp/definitely-missing-invoice-xyz.pdf"))


class PayInvoiceHeaderTests(unittest.TestCase):
    SAMPLE = (
        "Счет на оплату № УТ-133 от 31 августа 2026 г. WhatsApp: +7 (914) 577-71-14\n"
        "Поставщик: ИП Цыплухин Сергей Александрович, ИНН 280108797268, 675004, "
        "Амурская обл, г Благовещенск\n"
        "reanarent: ООО\"Теплосервис-Комплект\", ИНН 2801131520, КПП 280101001\n"
        "Итого: 6 864,00\n"
    )

    def test_pay_invoice_number_from_1c_header(self) -> None:
        match = _PAY_INVOICE_RE.search(self.SAMPLE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "УТ-133")
        self.assertEqual(match.group(2), "31 августа 2026")

    def test_extract_header_prefers_1c_number_and_supplier_inn(self) -> None:
        header = _extract_header(self.SAMPLE)
        self.assertEqual(header["invoice_number"], "УТ-133")
        self.assertEqual(header["supplier"]["inn"], "280108797268")
        self.assertIn("Цыплухин", header["supplier"]["name"])
        self.assertEqual(header["buyer"]["inn"], "2801131520")

    def test_account_digits_are_not_kpp(self) -> None:
        text = (
            "ИНН 280108797268 40802810570000015841\n"
            "Поставщик: ИП Цыплухин Сергей Александрович, ИНН 280108797268, 675004\n"
        )
        header = _extract_header(text)
        self.assertEqual(header["supplier"]["inn"], "280108797268")
        self.assertEqual(header["supplier"]["kpp"], "")

    def test_supplier_line_regex(self) -> None:
        match = _SUPPLIER_LINE_RE.search(self.SAMPLE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(2), "280108797268")


if __name__ == "__main__":
    unittest.main()
