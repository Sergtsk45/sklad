"""OBR-028: combined matching for imported Excel rows."""

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObr028CombinedMatching(TransactionCase):
    def setUp(self):
        super().setUp()
        self.parser = self.env["object.request.excel.parser"]
        self.service = self.env["object.request.matching.candidate.service"]
        self.vendor = self.env["res.partner"].create(
            {"name": "Поставщик OBR028", "supplier_rank": 1}
        )

    def _create_product(self, name, default_code=False):
        return self.env["product.product"].create(
            {
                "name": name,
                "default_code": default_code,
                "type": "consu",
            }
        )

    def _create_supplierinfo(self, article, product):
        return self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_code": article,
            }
        )

    def test_combined_match_query_keeps_name_first_and_deduplicates(self):
        query = self.parser._combined_match_query(
            "Кран муфтовый латунный Ду15 В-В",
            "ДУ 15 11Б27п1",
        )

        self.assertEqual(
            query,
            "кран муфтовый латунный ду15 в-в 11б27п1",
        )

    def test_diameter_extraction_keeps_du15_distinct_from_du150(self):
        self.assertEqual(
            self.parser._extract_diameter_values("Кран Ду15 Ду-20 DN25"),
            {15, 20, 25},
        )
        self.assertEqual(
            self.parser._extract_diameter_values("Кран Ду150"),
            {150},
        )

    def test_combined_match_query_ignores_length_article(self):
        query = self.parser._combined_match_query(
            "Труба стальная",
            "L=0.13",
        )

        self.assertEqual(query, "труба стальная")

    def test_classify_length_fragment(self):
        self.assertEqual(
            self.parser._classify_import_line("Отрезок трубы", "L=0.13"),
            "length_or_pipe_fragment",
        )
        self.assertEqual(
            self.parser._classify_import_line("Отрезок трубы", "21.3"),
            "length_or_pipe_fragment",
        )

    def test_combined_candidates_use_ai_search_products(self):
        product = self._create_product(
            "Кран муфтовый латунный Ду15 В-В бабочка"
        )

        (
            candidates,
            line_type,
            query,
        ) = self.parser._combined_candidate_products(
            "Кран муфтовый латунный Ду15 В-В", "11Б27п1"
        )

        self.assertEqual(line_type, "product_candidate")
        self.assertIn("11б27п1", query)
        self.assertIn(product, candidates)

    def test_candidate_service_deduplicates_and_keeps_stable_order(self):
        product = self._create_product(
            "Клапан OBR028 service primary",
            default_code="OBR028-SVC-001",
        )
        secondary = self._create_product("Клапан OBR028 service secondary")
        self._create_supplierinfo("OBR028-SVC-001", product)

        result = self.service.build_candidates(
            "Клапан OBR028 service",
            "OBR028-SVC-001",
            vendor=self.vendor,
        )

        candidate_ids = [item["product_id"] for item in result["candidates"]]
        self.assertEqual(candidate_ids[0], product.id)
        self.assertIn(secondary.id, candidate_ids)
        self.assertEqual(candidate_ids.count(product.id), 1)
        self.assertEqual(result["candidates"][0]["source"], "supplierinfo")
        self.assertTrue(result["can_call_llm"])

    def test_candidate_service_returns_explainable_candidate_fields(self):
        product = self._create_product("Фильтр OBR028 explain Ду15")

        result = self.service.build_candidates(
            "Фильтр OBR028 explain Ду15",
            "",
        )

        candidate = next(
            item
            for item in result["candidates"]
            if item["product_id"] == product.id
        )
        self.assertEqual(candidate["display_name"], product.display_name)
        self.assertIn("source", candidate)
        self.assertIn("local_score", candidate)
        self.assertIn("matched_tokens", candidate)
        self.assertIn("missing_tokens", candidate)

    def test_candidate_service_filters_wrong_diameter_and_keeps_likely_valves(self):
        lever = self._create_product(
            "Кран латунный Ду15 В-В рычаг OBR028-DU"
        )
        butterfly = self._create_product(
            "Кран латунный Ду15 В-В бабочка OBR028-DU"
        )
        wrong_diameter = self._create_product(
            "Кран латунный Ду20 В-В рычаг OBR028-DU"
        )
        wrong_large_diameter = self._create_product(
            "Кран латунный Ду150 В-В рычаг OBR028-DU"
        )
        same_diameter_muftovy = self._create_product(
            "Кран стальной муфтовый Ду15 OBR028-DU"
        )

        result = self.service.build_candidates(
            "Кран муфтовый латунный Ду15 В-В OBR028-DU",
            "",
        )

        candidate_ids = [item["product_id"] for item in result["candidates"]]
        self.assertIn(lever.id, candidate_ids)
        self.assertIn(butterfly.id, candidate_ids)
        self.assertIn(same_diameter_muftovy.id, candidate_ids)
        self.assertNotIn(wrong_diameter.id, candidate_ids)
        self.assertNotIn(wrong_large_diameter.id, candidate_ids)

    def test_candidate_service_limits_llm_and_preview_candidates(self):
        for index in range(10):
            self._create_product("Насос OBR028 limit %02d" % index)

        result = self.service.build_candidates("Насос OBR028 limit", "")

        self.assertLessEqual(len(result["candidates"]), 15)
        self.assertEqual(len(self.service.llm_candidates(result)), 8)
        self.assertEqual(len(self.service.preview_candidates(result)), 3)

    def test_candidate_service_empty_shortlist_blocks_llm(self):
        result = self.service.build_candidates("", "")

        self.assertEqual(result["line_type"], "manual_only")
        self.assertFalse(result["candidates"])
        self.assertFalse(result["can_call_llm"])

    def test_transition_size_does_not_match_wrong_product_automatically(self):
        self._create_product("Переход 108-57 ст.")

        result = self.parser.match_row(
            "",
            "Переход",
            "",
            technical_designation="80x50 ГОСТ 17378-2001",
        )

        self.assertFalse(result["product"])
        self.assertTrue(result["matching_required"])
        self.assertTrue(result["candidate_products"])
        self.assertTrue(result["candidate_details"])

    def test_noisy_designation_keeps_name_candidates(self):
        product = self._create_product("Труба d=80 OBR028 length context")

        result = self.service.build_candidates(
            "Труба d=80 OBR028",
            "",
            technical_designation="L=0.13",
        )

        candidate_ids = [item["product_id"] for item in result["candidates"]]
        self.assertIn(product.id, candidate_ids)
        self.assertTrue(result["can_call_llm"])

    def test_real_article_still_matches_default_code(self):
        product = self._create_product(
            "Товар OBR028 real article",
            default_code="OBR028-REAL-ARTICLE",
        )

        result = self.service.build_candidates(
            "Товар OBR028",
            "OBR028-REAL-ARTICLE",
            technical_designation="L=0.13",
        )

        self.assertEqual(result["candidates"][0]["product_id"], product.id)
        self.assertEqual(result["candidates"][0]["source"], "default_code")

    def test_empty_technical_designation_keeps_article_fallback(self):
        product = self._create_product(
            "Товар OBR028 article OBR028-ARTICLE-IN-NAME"
        )

        result = self.parser.match_row(
            "OBR028-ARTICLE-IN-NAME",
            "Позиция без точного имени OBR028",
            "",
            technical_designation="",
        )

        self.assertEqual(result["product"], product)
        self.assertFalse(result["matching_required"])

    def test_bobishka_oven_fixture_matches_exact_designation(self):
        product = self._create_product(
            "Бобышка ОВЕН Б.П.1.20х1,5.40.1"
        )

        result = self.parser.match_row(
            "Б.П.1.20Х1.5.40.1",
            "Бобышка",
            "",
        )

        self.assertEqual(result["product"], product)
        self.assertFalse(result["matching_required"])

    def test_length_designation_falls_back_to_name_search(self):
        product = self._create_product("Труба OBR028 L context")
        with patch.object(
            type(self.env["product.product"]),
            "ai_search_products",
            wraps=self.env["product.product"].ai_search_products,
        ) as search_mock:
            result = self.parser.match_row(
                "",
                "Отрезок трубы OBR028",
                "",
                technical_designation="L=0.13",
            )

        self.assertIn(product, result["candidate_products"])
        self.assertEqual(result["line_type"], "length_or_pipe_fragment")
        search_mock.assert_called()
