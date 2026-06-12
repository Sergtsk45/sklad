# @file: test_invoice_parsing.py
# @description: Тесты парсера счетов services/invoice_parsing (НФ-504 fixture).
# @dependencies: services/invoice_parsing, unittest.mock
# @created: 2026-05-30

from __future__ import annotations

from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.invoice_parsing.invoice_utils import (
    extract_party_name,
    is_garbage_item,
)
from odoo.addons.ai_assistant.services.invoice_parsing.normalizer import normalize_invoice
from odoo.addons.ai_assistant.services.invoice_parsing.validators import validate_invoice_data
from odoo.addons.ai_assistant.services.invoice_parsing.extractor import (
    _INVOICE_NO_RE,
    _parse_header,
    extract_invoice,
)

# ── Фикстура: текст счёта НФ-504 (14 позиций, поставщик ИП Татаринов) ──────────

_NF504_HEADER_TEXT = """
Счет на оплату № НФ-504 от 20 мая 2026 г.
Поставщик ИП Татаринов Вадим Владимирович, ИНН 280110406377, КПП ,
675000, Амурская обл, г. Благовещенск
Грузоотправитель: тот же
Покупатель ООО "ТЕПЛОСЕРВИС-КОМПЛЕКТ", ИНН 2801131520, КПП 280101001, 675002, Амурская обл
Грузополучатель: тот же
Банк получателя: АО "Тинькофф Банк"
БИК: 044525974
р/с 40802810000001234567
к/с 30101810145250000974
"""

_CB675_HEADER_TEXT = """
Счет на оплату № ЦБ-675 от 9 июня 2026 г.
ООО "АРМОСТ", ИНН 5404959909, КПП 540401001, 630096, Новосибирская обл, Новосибирск г, Станционная ул,
Поставщик:
дом № 46Б, тел.: +7 (383) 3832253
Покупатель: Розничный покупатель
№ Товары (работы, услуги) Количество Цена Сумма
"""

_INV234_HEADER_TEXT = """
Счет № 237 от 02.04.26
ИНН 7733816402 КПП 773301001 ООО "ЭСКО 3Э" 125362, г. Москва, ул. Водников, д. 2, стр.
Поставщик:
4, Б.1, А, К 16, тел. (499) 929-82-35, 5-000-217
ИНН 2801138406/280101001 КПП ООО "ДВ ПАРТНЁР" 675002, Амурская Область, г.
Покупатель:
Благовещенск, ул. Фрунзе, д. 91, офис 3, тел. (4162) 66-01-06
"""

_INV1214_HEADER_TEXT = """
Внимание! Счет действителен до 01.10.2025.
Оплата данного счета означает согласие с условиями поставки товара.
Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности.
Счет на оплату № 1214 от 1 октября 2025 г.
Общество с ограниченной ответственностью "Пензапромарматура" (ООО "Пензапромарматура"), ИНН
Поставщик: 5835036366, КПП 583501001, 440066, Пензенская обл, Пенза г, Строителей пр-кт, дом № 89, тел.: (8412) 90-93-00
ООО "ДВ Партнёр", ИНН 2801138406, КПП 280101001
Покупатель: 675000, Амурская обл, Благовещенск г
"""

_NF504_ITEMS_ROWS = [
    # строка-заголовок
    ["№", "Наименование товара", "Ед.", "Кол-во", "Цена",
     "Сумма без НДС", "Ставка НДС", "Сумма НДС", "Итого"],
    # мусорная строка-нумератор (pdfplumber артефакт)
    ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
    # 14 реальных позиций
    ["1", "Переход 89-45 ст.", "шт", "16", "239,59",
     "3833,44", "20%", "766,69", "4600,13"],
    ["2", "Переход 108-57 ст.", "шт", "8", "279,66",
     "2237,28", "20%", "447,46", "2684,74"],
    ["3", "Отвод 89 ст. 90°", "шт", "20", "179,49",
     "3589,80", "20%", "717,96", "4307,76"],
    ["4", "Отвод 108 ст. 90°", "шт", "10", "239,59",
     "2395,90", "20%", "479,18", "2875,08"],
    ["5", "Тройник 89×45×3,5 ГОСТ 17376-2001", "шт", "4", "599,00",
     "2396,00", "20%", "479,20", "2875,20"],
    ["6", "Тройник 76х3,5-45х3-20 ГОСТ 17376-2001", "шт", "6", "549,00",
     "3294,00", "20%", "658,80", "3952,80"],
    ["7", "Муфта 89 ст.", "шт", "30", "119,80",
     "3594,00", "20%", "718,80", "4312,80"],
    ["8", "Муфта 108 ст.", "шт", "15", "139,75",
     "2096,25", "20%", "419,25", "2515,50"],
    ["9", "Заглушка 89 ст.", "шт", "10", "99,50",
     "995,00", "20%", "199,00", "1194,00"],
    ["10", "Заглушка 108 ст.", "шт", "5", "119,80",
     "599,00", "20%", "119,80", "718,80"],
    ["11", "Труба ст. 89×3,5 ГОСТ 8732", "м", "50", "350,00",
     "17500,00", "20%", "3500,00", "21000,00"],
    ["12", "Труба ст. 108×4 ГОСТ 8732", "м", "30", "480,00",
     "14400,00", "20%", "2880,00", "17280,00"],
    ["13", "Фланец 89 ст. Ду80 ГОСТ 12820", "шт", "12", "289,00",
     "3468,00", "20%", "693,60", "4161,60"],
    ["14", "Фланец 108 ст. Ду100 ГОСТ 12820", "шт", "8", "349,00",
     "2792,00", "20%", "558,40", "3350,40"],
]

_NF504_TOTALS_TEXT = """
Итого: 60 191,67
В том числе НДС 20%: 12 437,14
Всего к оплате: 72 096,22
"""

# Минимальный валидный PDF (magic bytes + EOF)
_MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<</Type /Catalog>>endobj\n%%EOF\n"


def _make_mock_pdf(table_rows, header_text="", totals_text=""):
    """Создаёт мок pdfplumber.open с одной страницей, содержащей таблицу и текст."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = header_text + "\n" + totals_text
    mock_page.extract_tables.return_value = [table_rows]

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [mock_page]

    return mock_pdf


@tagged('post_install', '-at_install')
class TestExtractPartyName(TransactionCase):

    def test_extracts_name_before_inn(self):
        block = "ИП Татаринов Вадим Владимирович, ИНН 280110406377, 675000, Амурская обл"
        self.assertEqual(extract_party_name(block), "ИП Татаринов Вадим Владимирович")

    def test_strips_quotes_and_role_marker(self):
        block = 'ООО "ТЕПЛОСЕРВИС-КОМПЛЕКТ", ИНН 2801131520, КПП 280101001'
        self.assertEqual(extract_party_name(block), "ООО ТЕПЛОСЕРВИС-КОМПЛЕКТ")

    def test_strips_executor_role(self):
        block = "ООО МОНТАЖ (исполнитель), ИНН 1234567890"
        self.assertEqual(extract_party_name(block), "ООО МОНТАЖ")

    def test_plain_name_without_inn(self):
        block = "ИП Иванов Иван"
        self.assertEqual(extract_party_name(block), "ИП Иванов Иван")


@tagged('post_install', '-at_install')
class TestIsGarbageItem(TransactionCase):

    def test_rejects_column_header_digits(self):
        self.assertTrue(is_garbage_item("2", "5"))

    def test_rejects_number_sequence_row(self):
        self.assertTrue(is_garbage_item("1 2 4 5 6 7"))

    def test_rejects_empty_name(self):
        self.assertTrue(is_garbage_item(""))

    def test_rejects_no_letters(self):
        self.assertTrue(is_garbage_item("123.45"))

    def test_accepts_product_name(self):
        self.assertFalse(is_garbage_item("Переход 89-45 ст.", "шт"))

    def test_accepts_gost_name(self):
        self.assertFalse(is_garbage_item("Тройник 76х3,5-45х3-20 ГОСТ 17376-2001", "шт"))


@tagged('post_install', '-at_install')
class TestInvoiceNumberRegex(TransactionCase):

    def test_nf504_cyrillic_prefix(self):
        text = "Счет на оплату № НФ-504 от 20 мая 2026 г"
        m = _INVOICE_NO_RE.search(text)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).replace(" ", "-"), "НФ-504")

    def test_ut1132_cyrillic_prefix(self):
        text = "Счет на оплату № УТ-1132 от 17 апреля 2026 г"
        m = _INVOICE_NO_RE.search(text)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).replace(" ", "-"), "УТ-1132")

    def test_plain_number(self):
        text = "Счет на оплату № 504 от 20 мая 2026 г"
        m = _INVOICE_NO_RE.search(text)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).replace(" ", "-"), "504")


@tagged('post_install', '-at_install')
class TestParseHeader(TransactionCase):

    def test_supplier_and_buyer_names(self):
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier": {
                "name": "", "inn": "", "kpp": "", "address": "",
                "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
            },
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        _parse_header(_NF504_HEADER_TEXT, result)
        self.assertEqual(result["invoice_number"], "НФ-504")
        self.assertEqual(result["invoice_date"], "2026-05-20")
        self.assertEqual(result["supplier"]["name"], "ИП Татаринов Вадим Владимирович")
        self.assertEqual(result["supplier"]["inn"], "280110406377")
        self.assertIn("ТЕПЛОСЕРВИС-КОМПЛЕКТ", result["buyer"]["name"])

    def test_bank_details_extracted(self):
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier": {
                "name": "", "inn": "", "kpp": "", "address": "",
                "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
            },
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        _parse_header(_NF504_HEADER_TEXT, result)
        self.assertEqual(result["supplier"]["bank"]["bik"], "044525974")

    def test_supplier_name_from_line_before_label_cb675(self):
        """1С/Т-Банк: реквизиты выше метки «Поставщик:», адрес — ниже."""
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier": {
                "name": "", "inn": "", "kpp": "", "address": "",
                "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
            },
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        _parse_header(_CB675_HEADER_TEXT, result)
        self.assertEqual(result["invoice_number"], "ЦБ-675")
        self.assertEqual(result["supplier"]["name"], "ООО АРМОСТ")
        self.assertEqual(result["supplier"]["inn"], "5404959909")
        self.assertEqual(result["supplier"]["kpp"], "540401001")
        self.assertIn("Новосибирская обл", result["supplier"]["address"])
        self.assertIn("Станционная ул", result["supplier"]["address"])
        self.assertIn("дом № 46Б", result["supplier"]["address"])
        self.assertNotIn("КПП", result["supplier"]["address"])
        self.assertNotIn("тел.", result["supplier"]["address"].lower())
        self.assertEqual(result["buyer"]["name"], "Розничный покупатель")

    def test_supplier_name_after_inn_block_inv234(self):
        """Сбербанк/1С: ИНН первым, название после него; тел. без двоеточия."""
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier": {
                "name": "", "inn": "", "kpp": "", "address": "",
                "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
            },
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        _parse_header(_INV234_HEADER_TEXT, result)
        self.assertEqual(result["invoice_number"], "237")
        self.assertEqual(result["supplier"]["name"], "ООО ЭСКО 3Э")
        self.assertEqual(result["supplier"]["inn"], "7733816402")
        self.assertEqual(result["supplier"]["kpp"], "773301001")
        self.assertIn("Водников", result["supplier"]["address"])
        self.assertIn("Б.1", result["supplier"]["address"])
        self.assertNotIn("тел.", result["supplier"]["address"].lower())
        self.assertNotIn("ДВ ПАРТНЁР", result["supplier"]["address"])
        self.assertNotIn("ДВ ПАРТНЁР", result["supplier"]["name"])

    def test_supplier_name_before_inline_label_inv1214(self):
        """Имя строкой до «Поставщик: <ИНН_число>»; «Поставщика» не матчится."""
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier": {
                "name": "", "inn": "", "kpp": "", "address": "",
                "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
            },
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        _parse_header(_INV1214_HEADER_TEXT, result)
        self.assertEqual(result["invoice_number"], "1214")
        # Имя не содержит «самовывозом» или «Образец»
        self.assertNotIn("самовывозом", result["supplier"]["name"])
        self.assertNotIn("Образец", result["supplier"]["name"])
        # Должна быть краткая форма из скобок, а не «Общество с ограниченной...»
        self.assertNotIn("Общество с ограниченной", result["supplier"]["name"])
        self.assertIn("Пензапромарматура", result["supplier"]["name"])
        self.assertEqual(result["supplier"]["inn"], "5835036366")
        self.assertEqual(result["supplier"]["kpp"], "583501001")
        self.assertIn("Пензенская обл", result["supplier"]["address"])
        self.assertNotIn("ДВ Партнёр", result["supplier"]["name"])


@tagged('post_install', '-at_install')
class TestNormalizeInvoice(TransactionCase):

    def test_drops_garbage_rows(self):
        raw = {
            "items": [
                {"name": "2", "unit": "5", "qty": 4, "price": 6, "amount_w_vat": 7},
                {
                    "name": "Переход 89-45 ст.", "unit": "шт",
                    "qty": 16, "price": 239.59, "amount_w_vat": 4600.13,
                },
            ],
            "totals": {},
            "supplier": {"name": "", "inn": "", "kpp": "", "address": ""},
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        result = normalize_invoice(raw)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["name"], "Переход 89-45 ст.")
        self.assertEqual(result["items"][0]["line_no"], 1)

    def test_renumbers_items_sequentially(self):
        raw = {
            "items": [
                {"name": "Товар А", "unit": "шт", "qty": 1,
                 "price": 100, "amount_w_vat": 100},
                {"name": "Товар Б", "unit": "шт", "qty": 2,
                 "price": 200, "amount_w_vat": 400},
            ],
            "totals": {},
            "supplier": {"name": "", "inn": "", "kpp": "", "address": ""},
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        result = normalize_invoice(raw)
        self.assertEqual(result["items"][0]["line_no"], 1)
        self.assertEqual(result["items"][1]["line_no"], 2)

    def test_converts_string_numbers_to_float(self):
        raw = {
            "items": [
                {"name": "Труба", "unit": "м", "qty": "10",
                 "price": "350,00", "amount_w_vat": "3 500,00"},
            ],
            "totals": {"total_w_vat": "3 500,00"},
            "supplier": {"name": "", "inn": "", "kpp": "", "address": ""},
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        }
        result = normalize_invoice(raw)
        self.assertEqual(result["items"][0]["qty"], 10.0)
        self.assertEqual(result["items"][0]["price"], 350.0)
        self.assertEqual(result["totals"]["total_w_vat"], 3500.0)


@tagged('post_install', '-at_install')
class TestValidateInvoiceData(TransactionCase):

    def _make_nf504_data(self):
        items = []
        for row in _NF504_ITEMS_ROWS[2:]:
            items.append({
                "line_no": int(row[0]),
                "name": row[1],
                "unit": row[2],
                "qty": float(row[3]),
                "price": float(row[4].replace(",", ".")),
                "amount_wo_vat": float(row[5].replace(",", ".")),
                "vat_rate": row[6],
                "vat_amount": float(row[7].replace(",", ".")),
                "amount_w_vat": float(row[8].replace(",", ".")),
                "article": "",
                "discount": "",
            })
        return {
            "items": items,
            "totals": {
                "total_wo_vat": 60191.67,
                "vat_total": 12437.14,
                "total_w_vat": 72096.22,
            },
        }

    def test_nf504_zero_arithmetic_warnings(self):
        data = self._make_nf504_data()
        warnings = validate_invoice_data(data)
        arithmetic_warnings = [w for w in warnings if "кол-во×цена" in w]
        self.assertEqual(arithmetic_warnings, [], msg=f"Arithmetic warnings: {warnings}")

    def test_nf504_correct_item_count(self):
        data = self._make_nf504_data()
        self.assertEqual(len(data["items"]), 14)

    def test_empty_items_returns_warning(self):
        warnings = validate_invoice_data({"items": [], "totals": {}})
        self.assertTrue(any("ни одной строки" in w for w in warnings))

    def test_mismatch_qty_price_raises_warning(self):
        data = {
            "items": [{"name": "Товар", "qty": 10.0, "price": 100.0, "amount_wo_vat": 500.0}],
            "totals": {},
        }
        warnings = validate_invoice_data(data)
        self.assertTrue(any("кол-во×цена" in w for w in warnings))


@tagged('post_install', '-at_install')
class TestExtractInvoice(TransactionCase):

    def test_rejects_empty_bytes(self):
        with self.assertRaises(ValueError) as ctx:
            extract_invoice(b"")
        self.assertIn("Пустой файл", str(ctx.exception))

    def test_rejects_non_pdf_magic_bytes(self):
        with self.assertRaises(ValueError) as ctx:
            extract_invoice(b"PK\x03\x04fake_xlsx_content")
        self.assertIn("magic bytes", str(ctx.exception))

    @patch("odoo.addons.ai_assistant.services.invoice_parsing.extractor.pdfplumber")
    def test_nf504_14_items_correct_supplier_total(self, mock_pdfplumber):
        """Основной DoD-тест: 14 позиций, поставщик ИП Татаринов, итого 72 096,22."""
        mock_pdfplumber.open.return_value = _make_mock_pdf(
            table_rows=_NF504_ITEMS_ROWS,
            header_text=_NF504_HEADER_TEXT,
            totals_text=_NF504_TOTALS_TEXT,
        )

        result = extract_invoice(_MINIMAL_PDF)

        self.assertEqual(len(result["items"]), 14,
                         msg=f"Ожидалось 14 позиций, получено {len(result['items'])}")
        self.assertEqual(result["supplier"]["name"], "ИП Татаринов Вадим Владимирович")
        self.assertEqual(result["invoice_number"], "НФ-504")
        self.assertEqual(result["totals"]["total_w_vat"], 72096.22)

    @patch("odoo.addons.ai_assistant.services.invoice_parsing.extractor.pdfplumber")
    def test_garbage_rows_filtered_out(self, mock_pdfplumber):
        """Мусорная строка-нумератор «1 2 4 5 6 7» должна быть отфильтрована."""
        mock_pdfplumber.open.return_value = _make_mock_pdf(
            table_rows=_NF504_ITEMS_ROWS,
        )

        result = extract_invoice(_MINIMAL_PDF)
        names = [item["name"] for item in result["items"]]
        self.assertNotIn("2", names, msg="Мусорная строка '2' не должна попасть в позиции")

    @patch("odoo.addons.ai_assistant.services.invoice_parsing.extractor.pdfplumber")
    def test_nf504_zero_arithmetic_warnings_end_to_end(self, mock_pdfplumber):
        """После extract_invoice на фикстуре НФ-504 — нет arithmetic warnings."""
        mock_pdfplumber.open.return_value = _make_mock_pdf(
            table_rows=_NF504_ITEMS_ROWS,
            header_text=_NF504_HEADER_TEXT,
            totals_text=_NF504_TOTALS_TEXT,
        )

        result = extract_invoice(_MINIMAL_PDF)
        warnings = validate_invoice_data(result)
        arithmetic_warnings = [w for w in warnings if "кол-во×цена" in w]
        self.assertEqual(arithmetic_warnings, [], msg=f"Warnings: {warnings}")
