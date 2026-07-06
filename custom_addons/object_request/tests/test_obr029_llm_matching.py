"""OBR-029: LLM rerank matching service tests."""

import json
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


def _mock_openrouter_patch(answer_dict):
    """Создать patch для OpenRouterClient.send_chat с фиксированным ответом."""
    return patch(
        "odoo.addons.ai_assistant.services.openrouter_client"
        ".OpenRouterClient.send_chat",
        return_value={
            "answer": json.dumps(answer_dict, ensure_ascii=False),
            "model_used": "test-model",
            "tokens_used": 120,
        },
    )


@tagged("post_install", "-at_install")
class TestObr029LlmMatching(TransactionCase):

    def setUp(self):
        super().setUp()
        self.service = self.env["object.request.llm.matching.service"]

    def _create_product(self, name, default_code=False):
        return self.env["product.product"].create(
            {
                "name": name,
                "default_code": default_code or False,
                "type": "consu",
            }
        )

    def _make_candidate(
        self,
        product,
        score=0.8,
        source="name_score",
        requested_features=None,
        has_stock=False,
        stock_qty=0.0,
        substitution_decision="unknown_requires_review",
        substitution_requires_confirmation=False,
    ):
        candidate_features = {
            "product_family": product.or_product_family or False,
            "diameter_nominal": product.or_diameter_nominal or False,
            "pressure_nominal": product.or_pressure_nominal or False,
            "material": product.or_material or False,
            "standard": product.or_standard or False,
            "connection_type": product.or_connection_type or False,
        }
        return {
            "product": product,
            "product_id": product.id,
            "display_name": product.display_name,
            "default_code": product.default_code or "",
            "uom_id": product.uom_id.id if product.uom_id else False,
            "source": source,
            "local_score": score,
            "matched_tokens": [],
            "missing_tokens": [],
            "requested_features": requested_features or {},
            "candidate_features": candidate_features,
            "stock_qty_on_issue_warehouses": stock_qty,
            "stock_warehouse_names": "Основной склад: %g" % stock_qty
            if has_stock else "",
            "has_issue_stock": has_stock,
            "stock_rank_bonus": 0.0,
            "substitution_decision": substitution_decision,
            "substitution_reason": "",
            "substitution_rule_applied": False,
            "substitution_requires_confirmation": (
                substitution_requires_confirmation
            ),
        }

    # ------------------------------------------------------------------
    # Тест: mock возвращает match → товар назначается, auto_applicable
    # ------------------------------------------------------------------

    def test_match_returns_correct_product(self):
        product = self._create_product("Кран латунный Ду15 В-В")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "match",
            "product_id": product.id,
            "confidence": 0.93,
            "reason": "Совпадает тип, материал, Ду15 и В-В",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Кран муфтовый латунный Ду15 В-В", "11Б27п1", candidates
            )

        self.assertEqual(result["decision"], "match")
        self.assertEqual(result["product"], product)
        self.assertEqual(result["product_id"], product.id)
        self.assertAlmostEqual(result["confidence"], 0.93)
        self.assertTrue(result["auto_applicable"])
        self.assertIsNone(result["error"])

    # ------------------------------------------------------------------
    # Тест: mock возвращает несуществующий product_id → ошибка, не пишет
    # ------------------------------------------------------------------

    def test_nonexistent_product_id_in_shortlist_rejected(self):
        product = self._create_product("Кран Ду15 test")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "match",
            "product_id": 9999999,
            "confidence": 0.95,
            "reason": "Совпало",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Кран Ду15", "", candidates
            )

        self.assertEqual(result["decision"], "error")
        self.assertIsNotNone(result["error"])
        self.assertFalse(bool(result["product"]))
        self.assertFalse(result["auto_applicable"])

    # ------------------------------------------------------------------
    # Тест: mock возвращает невалидный JSON → error state
    # ------------------------------------------------------------------

    def test_invalid_json_response_returns_error_state(self):
        product = self._create_product("Труба стальная обр029")
        candidates = [self._make_candidate(product)]

        with patch(
            "odoo.addons.ai_assistant.services.openrouter_client"
            ".OpenRouterClient.send_chat",
            return_value={
                "answer": "это не JSON {broken text",
                "model_used": "test-model",
                "tokens_used": 30,
            },
        ):
            result = self.service.rerank_candidates(
                "Труба стальная", "", candidates
            )

        self.assertEqual(result["decision"], "error")
        self.assertIsNotNone(result["error"])
        self.assertFalse(result["auto_applicable"])

    # ------------------------------------------------------------------
    # Тест: confidence ниже AUTO_MATCH_THRESHOLD → не авто-применяется
    # ------------------------------------------------------------------

    def test_low_confidence_not_auto_applicable(self):
        product = self._create_product("Кран Ду25 обр029")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "match",
            "product_id": product.id,
            "confidence": 0.65,
            "reason": "Похожий тип, но неточный",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Кран Ду25", "", candidates
            )

        self.assertEqual(result["decision"], "match")
        self.assertAlmostEqual(result["confidence"], 0.65)
        self.assertFalse(result["auto_applicable"])

    # ------------------------------------------------------------------
    # Тест: confidence >= 0.90 но есть critical risk_flag → auto запрещён
    # ------------------------------------------------------------------

    def test_critical_risk_flag_prevents_auto_applicable(self):
        product = self._create_product("Кран Ду50 обр029")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "match",
            "product_id": product.id,
            "confidence": 0.91,
            "reason": "Тип совпадает, Ду конфликт",
            "risk_flags": ["size_conflict"],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Кран Ду25", "", candidates
            )

        self.assertFalse(result["auto_applicable"])
        self.assertIn("size_conflict", result["risk_flags"])
        self.assertLessEqual(result["confidence"], 0.85)

    # ------------------------------------------------------------------
    # Тест: пустой shortlist → error без LLM-вызова
    # ------------------------------------------------------------------

    def test_empty_candidates_returns_error_without_llm_call(self):
        with patch(
            "odoo.addons.ai_assistant.services.openrouter_client"
            ".OpenRouterClient.send_chat",
        ) as mock_send:
            result = self.service.rerank_candidates("Кран Ду15", "", [])

        self.assertEqual(result["decision"], "error")
        self.assertIsNotNone(result["error"])
        mock_send.assert_not_called()

    # ------------------------------------------------------------------
    # Тест: LLM возвращает manual_review → product пустой, не авто
    # ------------------------------------------------------------------

    def test_manual_review_decision_returns_empty_product(self):
        product = self._create_product("Переход 108-57 обр029")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "manual_review",
            "product_id": 0,
            "confidence": 0.55,
            "reason": "Несколько кандидатов, конфликт размера обозначения",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Переход", "80x50 ГОСТ 17378-2001", candidates
            )

        self.assertEqual(result["decision"], "manual_review")
        self.assertFalse(bool(result["product"]))
        self.assertEqual(result["product_id"], 0)
        self.assertFalse(result["auto_applicable"])

    # ------------------------------------------------------------------
    # Тест: timeout/ConnectionError → graceful fallback, импорт не ломается
    # ------------------------------------------------------------------

    def test_api_timeout_returns_error_gracefully(self):
        product = self._create_product("Бобышка ОВЕН обр029")
        candidates = [self._make_candidate(product)]

        with patch(
            "odoo.addons.ai_assistant.services.openrouter_client"
            ".OpenRouterClient.send_chat",
            side_effect=ConnectionError("OpenRouter: таймаут запроса"),
        ):
            result = self.service.rerank_candidates(
                "Бобышка", "Б.П.1.20Х1.5.40.1", candidates
            )

        self.assertEqual(result["decision"], "error")
        self.assertIsNotNone(result["error"])
        self.assertFalse(result["auto_applicable"])
        self.assertEqual(result["confidence"], 0.0)

    # ------------------------------------------------------------------
    # Тест: decision "not_found" → product_id = 0
    # ------------------------------------------------------------------

    def test_not_found_decision_returns_zero_product_id(self):
        product = self._create_product("Фланец обр029")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "not_found",
            "product_id": 0,
            "confidence": 0.3,
            "reason": "Ни один кандидат не соответствует описанию",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Отвод 90°", "Ду50 ст.", candidates
            )

        self.assertEqual(result["decision"], "not_found")
        self.assertEqual(result["product_id"], 0)
        self.assertFalse(bool(result["product"]))
        self.assertFalse(result["auto_applicable"])

    # ------------------------------------------------------------------
    # Тест: risk_flags не список → нормализуется без падения
    # ------------------------------------------------------------------

    def test_invalid_risk_flags_type_normalised(self):
        product = self._create_product("Вентиль обр029")
        candidates = [self._make_candidate(product)]
        answer = {
            "decision": "match",
            "product_id": product.id,
            "confidence": 0.88,
            "reason": "Совпадает",
            "risk_flags": "generic_name",
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Вентиль Ду15", "", candidates
            )

        self.assertIsInstance(result["risk_flags"], list)
        self.assertIsNone(result["error"])

    # ------------------------------------------------------------------
    # Тест: markdown в ответе LLM (```json...) парсится корректно
    # ------------------------------------------------------------------

    def test_markdown_wrapped_json_is_parsed(self):
        product = self._create_product("Манометр обр029")
        candidates = [self._make_candidate(product)]
        raw_answer = (
            "```json\n"
            + json.dumps(
                {
                    "decision": "match",
                    "product_id": product.id,
                    "confidence": 0.90,
                    "reason": "Совпадает",
                    "risk_flags": [],
                },
                ensure_ascii=False,
            )
            + "\n```"
        )

        with patch(
            "odoo.addons.ai_assistant.services.openrouter_client"
            ".OpenRouterClient.send_chat",
            return_value={
                "answer": raw_answer,
                "model_used": "test-model",
                "tokens_used": 90,
            },
        ):
            result = self.service.rerank_candidates(
                "Манометр Ду25", "", candidates
            )

        self.assertEqual(result["decision"], "match")
        self.assertEqual(result["product"], product)
        self.assertTrue(result["auto_applicable"])

    def test_user_message_contains_features_stock_and_policy(self):
        product = self._create_product("Фланец DN65 PN16 OBR029-PAYLOAD")
        requested_features = {
            "product_family": "flange",
            "diameter_nominal": 65,
            "pressure_nominal": 10,
        }
        candidates = [
            self._make_candidate(
                product,
                score=0.84,
                source="feature",
                requested_features=requested_features,
                has_stock=True,
                stock_qty=201.0,
                substitution_decision="allowed_with_confirmation",
                substitution_requires_confirmation=True,
            )
        ]

        payload = json.loads(
            self.service._build_user_message(
                "Фланец ст. Ду65 1,0МПа",
                "",
                candidates,
            )
        )

        self.assertEqual(
            payload["requested_features"]["diameter_nominal"],
            65,
        )
        candidate = payload["candidates"][0]
        self.assertTrue(candidate["has_issue_stock"])
        self.assertEqual(
            candidate["stock_qty_on_issue_warehouses"],
            201.0,
        )
        self.assertEqual(
            candidate["candidate_features"]["pressure_nominal"],
            16,
        )
        self.assertEqual(
            candidate["substitution_decision"],
            "allowed_with_confirmation",
        )

    def test_stock_candidate_confidence_is_boosted_without_conflicts(self):
        product = self._create_product("Фланец DN65 PN16 OBR029-STOCK")
        requested_features = {
            "product_family": "flange",
            "diameter_nominal": 65,
            "pressure_nominal": 16,
        }
        candidates = [
            self._make_candidate(
                product,
                score=0.88,
                source="feature",
                requested_features=requested_features,
                has_stock=True,
                stock_qty=10.0,
                substitution_decision="allowed_with_confirmation",
            )
        ]
        answer = {
            "decision": "match",
            "product_id": product.id,
            "confidence": 0.86,
            "reason": "Совпали DN и PN",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Фланец DN65 PN16",
                "",
                candidates,
            )

        self.assertEqual(result["decision"], "match")
        self.assertGreaterEqual(result["confidence"], 0.90)
        self.assertTrue(result["auto_applicable"])
        self.assertIn("остаток", result["reason"])

    def test_equal_stock_alternative_caps_no_stock_candidate(self):
        no_stock = self._create_product("Фланец DN65 PN16 OBR029-NOSTOCK")
        stock = self._create_product("Фланец DN65 PN16 OBR029-STOCK-ALT")
        requested_features = {
            "product_family": "flange",
            "diameter_nominal": 65,
            "pressure_nominal": 16,
        }
        candidates = [
            self._make_candidate(
                no_stock,
                score=0.90,
                source="name_score",
                requested_features=requested_features,
                substitution_decision="allowed_with_confirmation",
            ),
            self._make_candidate(
                stock,
                score=0.88,
                source="feature",
                requested_features=requested_features,
                has_stock=True,
                stock_qty=7.0,
                substitution_decision="allowed_with_confirmation",
            ),
        ]
        answer = {
            "decision": "match",
            "product_id": no_stock.id,
            "confidence": 0.94,
            "reason": "Текстовое совпадение",
            "risk_flags": [],
        }
        with _mock_openrouter_patch(answer):
            result = self.service.rerank_candidates(
                "Фланец DN65 PN16",
                "",
                candidates,
            )

        self.assertFalse(result["auto_applicable"])
        self.assertLessEqual(result["confidence"], 0.85)
        self.assertIn("stock_alternative_available", result["risk_flags"])
