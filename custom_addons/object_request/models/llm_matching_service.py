# @file: llm_matching_service.py
# @description: LLM-rerank сервис для сопоставления строк Excel с товарами.
#   Получает shortlist кандидатов от matching_candidate_service,
#   ранжирует через OpenRouter, валидирует ответ и возвращает результат.
#   Не пишет в БД напрямую — все решения применяются вышестоящим слоем.
# @dependencies: object.request.matching.candidate.service,
#   ai_assistant.services.openrouter_client (опциональная; импорт внутри)
# @created: 2026-06-14

from __future__ import annotations

import json
import logging
import re

from odoo import api, models

_logger = logging.getLogger(__name__)

AUTO_MATCH_THRESHOLD = 0.90
SUGGEST_THRESHOLD = 0.70

CRITICAL_RISK_FLAGS = frozenset({
    "size_conflict",
    "diameter_conflict",
    "thread_conflict",
    "model_conflict",
    "pressure_conflict",
})

VALID_DECISIONS = frozenset({"match", "manual_review", "not_found"})

_SYSTEM_PROMPT = """\
Ты — эксперт по сопоставлению строк технических требований с каталогом.

Задача: выбрать ОДИН товар из предложенного shortlist кандидатов, который \
наилучшим образом соответствует строке потребности.

Входные данные:
- name_raw: наименование из Excel
- supplier_article: обозначение/артикул из Excel (ГОСТ, типоразмер, модель)
- candidates: список [{product_id, display_name, default_code, uom}]

Обязательные правила:
1. Отвечай ТОЛЬКО валидным JSON без markdown, без пояснений вне JSON.
2. Выбирай ТОЛЬКО product_id из переданного списка candidates.
3. Оценивай name_raw и supplier_article ВМЕСТЕ как единое описание потребности.
4. При конфликте диаметра (Ду/DN), резьбы (М..., дюймы), давления (Ру/PN), \
   размера, модели — добавляй соответствующий risk_flag.
5. Если уверенности нет — верни decision: "manual_review".
6. Не создавай новые товары, не указывай product_id вне списка кандидатов.

Схема ответа:
{
  "decision": "match|manual_review|not_found",
  "product_id": 0,
  "confidence": 0.0,
  "reason": "краткое объяснение на русском языке",
  "risk_flags": []
}

Значения decision:
- "match": найден подходящий кандидат, product_id указывает на него
- "manual_review": кандидаты неоднозначны или нет уверенного выбора
- "not_found": ни один кандидат не подходит

При decision != "match" — product_id должен быть 0 или null.
Если присутствуют risk_flags — confidence не может превышать 0.85.\
"""


class ObjectRequestLlmMatchingService(models.AbstractModel):
    _name = "object.request.llm.matching.service"
    _description = "LLM rerank service for object request line matching"

    @api.model
    def _get_ai_config(self):
        """Читать параметры AI-сопоставления из ir.config_parameter."""
        get = self.env['ir.config_parameter'].sudo().get_param
        return {
            'enabled': get(
                'object_request.ai_matching_enabled', 'True'
            ) == 'True',
            'auto_threshold': float(
                get(
                    'object_request.ai_matching_auto_threshold',
                    '0.90',
                )
            ),
            'suggest_threshold': float(
                get(
                    'object_request.ai_matching_suggest_threshold',
                    '0.70',
                )
            ),
            'batch_size': int(
                get('object_request.ai_matching_batch_size', '50')
            ),
        }

    @api.model
    def rerank_candidates(self, name_raw, supplier_article, candidates):
        """
        Ранжировать кандидатов через LLM и вернуть структурированный результат.

        :param name_raw: str — наименование из строки Excel
        :param supplier_article: str — артикул/обозначение из строки Excel
        :param candidates: list[dict] — shortlist (макс. 8 записей),
            каждая запись: product_id, display_name, default_code, uom_id
        :returns: dict с ключами:
            decision: "match"|"manual_review"|"not_found"|"error"
            product: product.product (пустой при не-match или ошибке)
            product_id: int
            confidence: float 0..1
            reason: str
            risk_flags: list[str]
            raw_response: str
            model_used: str
            tokens_used: int
            auto_applicable: bool (True если >= 0.90 и нет critical flags)
            error: str|None
        """
        if not candidates:
            return self._error_result("Список кандидатов пуст.")

        valid_ids = {item["product_id"] for item in candidates}

        try:
            llm_result = self._call_llm(name_raw, supplier_article, candidates)
        except Exception as exc:
            _logger.warning(
                "[llm_matching] LLM call failed: name=%r article=%r err=%s",
                name_raw,
                supplier_article,
                exc,
            )
            return self._error_result(str(exc))

        return self._build_result(llm_result, valid_ids)

    @api.model
    def _call_llm(self, name_raw, supplier_article, candidates):
        """Вызвать OpenRouter и вернуть сырой результат."""
        config = self._get_ai_config()
        if not config['enabled']:
            raise ValueError(
                'AI-сопоставление отключено в настройках.'
            )
        try:
            from odoo.addons.ai_assistant.services.openrouter_client import (
                OpenRouterClient,
            )
            client = OpenRouterClient(self.env)
        except Exception as exc:
            raise ConnectionError(
                "OpenRouter клиент недоступен: %s" % exc
            ) from exc

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": self._build_user_message(
                    name_raw, supplier_article, candidates
                ),
            },
        ]
        resp = client.send_chat(messages, max_tokens=400)
        return {
            "raw": resp.get("answer", ""),
            "model_used": resp.get("model_used", ""),
            "tokens_used": resp.get("tokens_used", 0),
        }

    @api.model
    def _build_user_message(self, name_raw, supplier_article, candidates):
        """Сформировать JSON-сообщение пользователя для LLM."""
        candidate_list = [
            {
                "product_id": item["product_id"],
                "display_name": item.get("display_name", ""),
                "default_code": item.get("default_code") or "",
                "uom": str(item.get("uom_id") or ""),
            }
            for item in candidates
        ]
        data = {
            "name_raw": name_raw or "",
            "supplier_article": supplier_article or "",
            "candidates": candidate_list,
        }
        return json.dumps(data, ensure_ascii=False)

    @api.model
    def _parse_llm_response(self, raw_text):
        """Парсить текстовый ответ LLM в dict. Raises ValueError при ошибке."""
        text = (raw_text or "").strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```\s*$", "", text).strip()
        try:
            return json.loads(text)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "Невалидный JSON от LLM: %r" % text[:200]
            ) from exc

    @api.model
    def _validate_llm_data(self, data, valid_ids):
        """
        Валидировать и нормализовать поля ответа LLM.

        Raises ValueError при недопустимых значениях.
        """
        decision = data.get("decision")
        if decision not in VALID_DECISIONS:
            raise ValueError(
                "Недопустимый decision: %r. Ожидается одно из %s"
                % (decision, sorted(VALID_DECISIONS))
            )

        product_id = data.get("product_id") or 0
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            product_id = 0

        if decision == "match" and product_id and product_id not in valid_ids:
            raise ValueError(
                "product_id %d не найден в shortlist candidates" % product_id
            )

        confidence = data.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        risk_flags = data.get("risk_flags") or []
        if not isinstance(risk_flags, list):
            risk_flags = []
        risk_flags = [str(f) for f in risk_flags if f]

        has_critical_risks = bool(CRITICAL_RISK_FLAGS & set(risk_flags))
        if has_critical_risks and confidence > 0.85:
            confidence = 0.85

        return {
            "decision": decision,
            "product_id": product_id if decision == "match" else 0,
            "confidence": confidence,
            "reason": str(data.get("reason") or ""),
            "risk_flags": risk_flags,
            "has_critical_risks": has_critical_risks,
        }

    @api.model
    def _build_result(self, llm_result, valid_ids):
        """Собрать финальный результат из сырого LLM-ответа."""
        raw = llm_result.get("raw", "")
        base = {
            "raw_response": raw,
            "model_used": llm_result.get("model_used", ""),
            "tokens_used": llm_result.get("tokens_used", 0),
            "error": None,
        }
        try:
            data = self._parse_llm_response(raw)
            validated = self._validate_llm_data(data, valid_ids)
        except Exception as exc:
            _logger.warning("[llm_matching] validation failed: %s", exc)
            base.update(self._error_fields(str(exc)))
            return base

        product = self.env["product.product"].browse()
        if validated["decision"] == "match" and validated["product_id"]:
            product = (
                self.env["product.product"]
                .browse(validated["product_id"])
                .exists()
            )

        auto_applicable = (
            validated["decision"] == "match"
            and bool(product)
            and validated["confidence"] >= AUTO_MATCH_THRESHOLD
            and not validated["has_critical_risks"]
        )

        base.update(
            {
                "decision": validated["decision"],
                "product": product,
                "product_id": validated["product_id"],
                "confidence": validated["confidence"],
                "reason": validated["reason"],
                "risk_flags": validated["risk_flags"],
                "auto_applicable": auto_applicable,
            }
        )
        return base

    @api.model
    def _error_result(self, message):
        """Вернуть стандартный результат ошибки."""
        return {
            "decision": "error",
            "product": self.env["product.product"].browse(),
            "product_id": 0,
            "confidence": 0.0,
            "reason": "",
            "risk_flags": [],
            "raw_response": "",
            "model_used": "",
            "tokens_used": 0,
            "auto_applicable": False,
            "error": message,
        }

    @api.model
    def _error_fields(self, message):
        """Поля ошибки для слияния с base dict."""
        return {
            "decision": "error",
            "product": self.env["product.product"].browse(),
            "product_id": 0,
            "confidence": 0.0,
            "reason": "",
            "risk_flags": [],
            "auto_applicable": False,
            "error": message,
        }
