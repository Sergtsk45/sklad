"""OBR-027: Тесты улучшенного сопоставления строк импорта Excel."""

import base64
import io

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _make_excel_bytes(rows):
    try:
        import openpyxl
    except ImportError:
        return None
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


REFERENCE_MATCHING_CASES = [
    {
        "name": "Термометр общетехнического назначения",
        "article": "БиТ-63-120-40, G1/2",
        "expected_product_id": 674,
        "expected_product_name": "Термометр биметаллический БиТ-63-120-40",
        "should_match": True,
    },
    {
        "name": "Манометр технический показывающий",
        "article": "МТ-100 0-1,6 МПа (G1/2) КИПИКА-100",
        "expected_product_id": 671,
        "expected_product_name": "Манометр МТ-100 0-1,6 МПа (G1/2) КИПИКА",
        "should_match": True,
    },
    {
        "name": "Кран трехходовой для манометра",
        "article": "11б27пм(М)2 Ру16 Ду15 G1/2xG1/2",
        "expected_product_id": 675,
        "expected_product_name": "Кран шаровый трёхходовой для манометра",
        "should_match": True,
    },
    {
        "name": "Кран муфтовый латунный Ду15 В-В",
        "article": "",
        "expected_product_id": None,
        "expected_product_name": "Кран латунный Ду15 В-В",
        "should_match": None,
    },
    {
        "name": "Переход",
        "article": "80x50 ГОСТ 17378-2001",
        "expected_product_id": None,
        "expected_product_name": None,
        "should_match": False,
    },
    {
        "name": "Бобышка",
        "article": "Б.П.1.20Х1.5.40.1",
        "expected_product_id": 651,
        "expected_product_name": "Бобышка ОВЕН Б.П.1.20х1,5.40.1",
        "should_match": True,
    },
]


@tagged("post_install", "-at_install")
class TestImportMatchingV2(TransactionCase):
    """Базовые тесты нормализации для будущего скоринга OBR-027."""

    def setUp(self):
        super().setUp()
        self.parser = self.env["object.request.excel.parser"]
        self.Product = self.env["product.product"]
        self.SupplierInfo = self.env["product.supplierinfo"]
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR-027"}
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-06-13",
            }
        )
        self.vendor_a = self.env["res.partner"].create(
            {"name": "Поставщик OBR027 A", "supplier_rank": 1}
        )
        self.vendor_b = self.env["res.partner"].create(
            {"name": "Поставщик OBR027 B", "supplier_rank": 1}
        )

    def _create_product(self, name, default_code=None):
        vals = {
            "name": name,
            "type": "consu",
            "is_storable": True,
        }
        if default_code:
            vals["default_code"] = default_code
        return self.Product.create(vals)

    def _create_line(self, article, product=None, vendor=None, name=None):
        vals = {
            "request_id": self.request.id,
            "supplier_article": article,
            "name_raw": name or "Строка OBR027",
            "qty_requested": 1.0,
            "matching_required": not bool(product),
        }
        if product:
            vals["product_id"] = product.id
        if vendor:
            vals["preferred_vendor_id"] = vendor.id
        return self.env["object.request.line"].create(vals)

    def _create_supplierinfo(self, article, product, vendor):
        return self.SupplierInfo.create(
            {
                "partner_id": vendor.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_code": article,
            }
        )

    def _put_stock(self, product, warehouse, qty):
        self.env["stock.quant"]._update_available_quantity(
            product,
            warehouse.lot_stock_id,
            qty,
        )

    def test_reference_cases_are_fixed_as_test_data(self):
        self.assertEqual(len(REFERENCE_MATCHING_CASES), 6)
        for case in REFERENCE_MATCHING_CASES:
            self.assertIn("name", case)
            self.assertIn("article", case)
            self.assertIn("should_match", case)

    def test_normalize_for_match_unifies_du_ru(self):
        normalized = {
            self.parser._normalize_for_match(value)
            for value in ("Ду15", "ДУ-15", "ду 15")
        }
        self.assertEqual(normalized, {"ду15"})

        self.assertEqual(
            self.parser._normalize_for_match("Ру 16 Ду-15"),
            "ру16 ду15",
        )

    def test_normalize_for_match_unifies_size_separator(self):
        self.assertEqual(
            self.parser._normalize_for_match("М20х1,5"),
            self.parser._normalize_for_match("М20×1,5"),
        )
        self.assertEqual(
            self.parser._normalize_for_match("80 x 50 ГОСТ"),
            "80x50 гост",
        )

    def test_normalize_for_match_unifies_yo_and_spaces(self):
        self.assertEqual(
            self.parser._normalize_for_match("  Трёхходовой\xa0кран  "),
            "трехходовой кран",
        )

    def test_tokenize_drops_short_and_stop_tokens(self):
        self.assertEqual(
            self.parser._tokenize("Кран трехходовой для манометра Ду 15"),
            ["кран", "трехходовой", "манометра", "ду15"],
        )

    def test_tokenize_keeps_articles_and_dimensions(self):
        self.assertIn(
            "б.п.1.20x1.5.40.1",
            self.parser._tokenize("Бобышка Б.П.1.20Х1.5.40.1"),
        )

    def test_match_product_by_article_falls_back_to_default_code(self):
        product = self._create_product(
            "Материал OBR027 default code",
            default_code="OBR027-DEFAULT-CODE",
        )

        self.assertEqual(
            self.parser.match_product_by_article("obr027-default-code"),
            product,
        )

    def test_match_product_by_article_finds_thermometer_code_in_name(self):
        product = self._create_product(
            "Термометр биметаллический "
            "OBR027-БиТ-63-120-40, G1/2",
        )

        self.assertEqual(
            self.parser.match_product_by_article(
                "OBR027-БиТ-63-120-40, G1/2"
            ),
            product,
        )

    def test_match_product_by_article_scores_manometer_name(self):
        best = self._create_product(
            "Манометр OBR027 МТ-100 0-1,6 МПа (G1/2) КИПИКА"
        )
        self._create_product("Манометр OBR027 МТ-100")

        self.assertEqual(
            self.parser.match_product_by_article(
                "OBR027 МТ-100 0-1,6 МПа (G1/2) КИПИКА-100"
            ),
            best,
        )

    def test_match_product_by_article_finds_three_way_valve_name(self):
        product = self._create_product(
            "Кран шаровый трехходовой для манометра OBR027 "
            "11б27пм(М)2 Ру16 Ду15 G1/2xG1/2"
        )

        self.assertEqual(
            self.parser.match_product_by_article(
                "OBR027 11б27пм(М)2 Ру16 Ду15 G1/2×G1/2"
            ),
            product,
        )

    def test_match_product_by_article_unifies_decimal_separator(self):
        product = self._create_product(
            "Бобышка ОВЕН OBR027 Б.П.1.20х1,5.40.1"
        )

        self.assertEqual(
            self.parser.match_product_by_article("OBR027 Б.П.1.20Х1.5.40.1"),
            product,
        )

    def test_match_product_by_article_ignores_short_name_articles(self):
        self._create_product("Клапан OBR027 Ду80")

        self.assertFalse(self.parser.match_product_by_article("ДУ-80"))

    def test_match_product_by_article_rejects_ambiguous_name_candidates(self):
        self._create_product("Переход OBR027-AMB 80x50 ГОСТ 17378-2001")
        self._create_product("Переход OBR027-AMB 80x50 ГОСТ 17378-2001")

        self.assertFalse(
            self.parser.match_product_by_article(
                "OBR027-AMB 80x50 ГОСТ 17378-2001"
            )
        )

    def test_match_product_by_name_selects_clear_tokenized_winner(self):
        best = self._create_product(
            "Кран муфтовый латунный OBR027-NAME Ду15 В-В бабочка"
        )
        self._create_product("Кран латунный OBR027-NAME Ду15")

        self.assertEqual(
            self.parser.match_product_by_name(
                "Кран муфтовый латунный OBR027-NAME Ду15 В-В"
            ),
            best,
        )

    def test_match_product_by_name_uses_article_tokens_with_lower_weight(self):
        product = self._create_product(
            "Грязевик фланцевый OBR027-NAME ГВФ-80-16 Ду80"
        )

        self.assertEqual(
            self.parser.match_product_by_name(
                "Грязевик OBR027-NAME ГВФ-80-16",
                supplier_article="ДУ-80",
            ),
            product,
        )

    def test_match_product_by_name_rejects_single_word_without_article(self):
        self._create_product("Переход OBR027-NAME 80x50")

        self.assertFalse(self.parser.match_product_by_name("Переход"))

    def test_match_product_by_name_rejects_equal_score_candidates(self):
        self._create_product("Кран латунный OBR027-EQUAL Ду15 В-В бабочка")
        self._create_product("Кран латунный OBR027-EQUAL Ду15 В-В рычаг")

        self.assertFalse(
            self.parser.match_product_by_name(
                "Кран латунный OBR027-EQUAL Ду15 В-В"
            )
        )

    def test_candidate_service_payload_contains_stock_reason(self):
        warehouse = self.project.warehouse_id
        self.request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        stock_product = self._create_product(
            "Фланец DN65 PN16 OBR027-STOCK-PAYLOAD"
        )
        self._put_stock(stock_product, warehouse, 201.0)

        result = self.env[
            "object.request.matching.candidate.service"
        ].build_candidates(
            "Фланец ст. Ду65 1,0МПа OBR027-STOCK-PAYLOAD",
            "",
            request=self.request,
        )

        candidate = next(
            item for item in result["candidates"]
            if item["product_id"] == stock_product.id
        )
        self.assertTrue(candidate["has_issue_stock"])
        self.assertAlmostEqual(
            candidate["stock_qty_on_issue_warehouses"],
            201.0,
        )
        self.assertIn("Есть остаток на складах выдачи", candidate["reason"])
        self.assertEqual(
            candidate["substitution_decision"],
            "allowed_with_confirmation",
        )

    def test_remember_matching_creates_supplierinfo_for_repeat_import(self):
        product = self._create_product("Материал OBR027 memory")
        line = self._create_line(
            "OBR027-MEM-001",
            product=product,
            vendor=self.vendor_a,
        )

        line.action_remember_matching()

        info = self.SupplierInfo.search(
            [
                ("product_code", "=ilike", "OBR027-MEM-001"),
                ("partner_id", "=", self.vendor_a.id),
            ]
        )
        self.assertEqual(len(info), 1)
        self.assertEqual(info.product_id, product)
        result = self.parser.match_row(
            "OBR027-MEM-001",
            "Несуществующее имя OBR027",
            self.vendor_a.name,
        )
        self.assertEqual(result["product"], product)
        self.assertFalse(result["matching_required"])

    def test_manual_product_write_does_not_create_supplierinfo(self):
        product = self._create_product("Материал OBR027 no memory")
        line = self._create_line("OBR027-NO-MEM-001")

        line.write({"product_id": product.id})

        self.assertFalse(
            self.SupplierInfo.search(
                [("product_code", "=ilike", "OBR027-NO-MEM-001")]
            )
        )

    def test_supplierinfo_conflict_uses_vendor_pair_when_available(self):
        product_a = self._create_product("Материал OBR027 vendor A")
        product_b = self._create_product("Материал OBR027 vendor B")
        self._create_supplierinfo(
            "OBR027-CONFLICT-001", product_a, self.vendor_a
        )
        self._create_supplierinfo(
            "OBR027-CONFLICT-001", product_b, self.vendor_b
        )

        self.assertEqual(
            self.parser.match_product_by_article(
                "OBR027-CONFLICT-001",
                vendor=self.vendor_a,
            ),
            product_a,
        )
        self.assertEqual(
            self.parser.match_product_by_article(
                "OBR027-CONFLICT-001",
                vendor=self.vendor_b,
            ),
            product_b,
        )
        self.assertFalse(
            self.parser.match_product_by_article("OBR027-CONFLICT-001")
        )

    def test_supplierinfo_conflict_without_vendor_requires_matching(self):
        product_a = self._create_product("Материал OBR027 conflict A")
        product_b = self._create_product("Материал OBR027 conflict B")
        self._create_supplierinfo(
            "OBR027-CONFLICT-002",
            product_a,
            self.vendor_a,
        )
        self._create_supplierinfo(
            "OBR027-CONFLICT-002",
            product_b,
            self.vendor_b,
        )

        result = self.parser.match_row(
            "OBR027-CONFLICT-002",
            "Несуществующее имя OBR027",
            "",
        )

        self.assertFalse(result["product"])
        self.assertTrue(result["matching_required"])
        self.assertEqual(result["candidate_products"], product_a | product_b)

    def test_import_preview_shows_conflict_candidates(self):
        product_a = self._create_product("Материал OBR027 candidate A")
        product_b = self._create_product("Материал OBR027 candidate B")
        self._create_supplierinfo(
            "OBR027-CANDIDATE-001",
            product_a,
            self.vendor_a,
        )
        self._create_supplierinfo(
            "OBR027-CANDIDATE-001",
            product_b,
            self.vendor_b,
        )
        xlsx = _make_excel_bytes(
            [
                ["№", "Артикул", "Наименование", "Ед.", "Кол-во"],
                [
                    1,
                    "OBR027-CANDIDATE-001",
                    "Несуществующее имя OBR027",
                    "шт",
                    1,
                ],
            ]
        )
        if xlsx is None:
            self.skipTest("openpyxl не установлен")

        wizard = self.env["object.request.import.wizard"].create(
            {
                "file": base64.b64encode(xlsx),
                "file_name": "candidate.xlsx",
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-06-13",
                "priority": "1",
            }
        )
        wizard.action_validate()

        preview = wizard.preview_line_ids
        self.assertTrue(preview.matching_required)
        self.assertEqual(preview.candidate_product_ids, product_a | product_b)

    def test_remember_matching_conflict_requires_confirmation(self):
        product_a = self._create_product("Материал OBR027 remembered A")
        product_b = self._create_product("Материал OBR027 remembered B")
        self._create_supplierinfo(
            "OBR027-CONFLICT-003",
            product_a,
            self.vendor_a,
        )
        line = self._create_line(
            "OBR027-CONFLICT-003",
            product=product_b,
            vendor=self.vendor_b,
        )

        action = line.action_remember_matching()
        self.assertEqual(
            action["res_model"],
            "object.request.remember.matching.wizard",
        )
        self.assertFalse(
            self.SupplierInfo.search(
                [
                    ("product_code", "=ilike", "OBR027-CONFLICT-003"),
                    ("product_id", "=", product_b.id),
                ]
            )
        )

        wizard = self.env[action["res_model"]].browse(action["res_id"])
        wizard.action_confirm()

        self.assertTrue(
            self.SupplierInfo.search(
                [
                    ("product_code", "=ilike", "OBR027-CONFLICT-003"),
                    ("product_id", "=", product_b.id),
                    ("partner_id", "=", self.vendor_b.id),
                ],
                limit=1,
            )
        )
