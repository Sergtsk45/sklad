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
- requested_features: распознанные признаки строки (family, DN, PN, material)
- candidates: список кандидатов с признаками, остатками и policy-решением

Обязательные правила:
1. Отвечай ТОЛЬКО валидным JSON без markdown, без пояснений вне JSON.
2. Выбирай ТОЛЬКО product_id из переданного списка candidates.
3. Оценивай name_raw и supplier_article ВМЕСТЕ как единое описание потребности.
4. При конфликте диаметра (Ду/DN), резьбы (М..., дюймы), давления (Ру/PN), \
   размера, модели — добавляй соответствующий risk_flag.
5. Учитывай candidate_features, stock_qty_on_issue_warehouses и \
   substitution_decision.
6. Если подходящий кандидат есть на складе выдачи и нет конфликтов — \
   предпочитай его кандидату без остатка.
7. Если substitution_decision = "blocked" — не выбирай этот товар.
8. Если substitution_requires_confirmation = true — не завышай confidence; \
   такая замена требует ручного подтверждения.
9. Если уверенности нет — верни decision: "manual_review".
10. Не создавай новые товары, не указывай product_id вне списка кандидатов.

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

        return self._build_result(llm_result, valid_ids, candidates)

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
        requested_features = {}
        for item in candidates:
            requested_features = item.get("requested_features") or {}
            if requested_features:
                break
        candidate_list = [
            {
                "product_id": item["product_id"],
                "display_name": item.get("display_name", ""),
                "default_code": item.get("default_code") or "",
                "uom": str(item.get("uom_id") or ""),
                "source": item.get("source") or "",
                "local_score": item.get("local_score", 0.0),
                "matched_tokens": item.get("matched_tokens") or [],
                "missing_tokens": item.get("missing_tokens") or [],
                "candidate_features": (
                    item.get("candidate_features")
                    or self._candidate_feature_payload(item)
                ),
                "stock_qty_on_issue_warehouses": item.get(
                    "stock_qty_on_issue_warehouses", 0.0
                ),
                "stock_warehouse_names": (
                    item.get("stock_warehouse_names") or ""
                ),
                "has_issue_stock": bool(item.get("has_issue_stock")),
                "substitution_decision": (
                    item.get("substitution_decision") or ""
                ),
                "substitution_reason": (
                    item.get("substitution_reason") or ""
                ),
                "substitution_requires_confirmation": bool(
                    item.get("substitution_requires_confirmation")
                ),
            }
            for item in candidates
        ]
        data = {
            "name_raw": name_raw or "",
            "supplier_article": supplier_article or "",
            "requested_features": requested_features,
            "candidates": candidate_list,
        }
        return json.dumps(data, ensure_ascii=False)

    @api.model
    def _candidate_feature_payload(self, candidate):
        return {
            "product_family": candidate.get("product_family") or False,
            "diameter_nominal": candidate.get("diameter_nominal") or False,
            "pressure_nominal": candidate.get("pressure_nominal") or False,
            "material": candidate.get("material") or False,
            "standard": candidate.get("standard") or False,
            "connection_type": candidate.get("connection_type") or False,
        }

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
    def _build_result(self, llm_result, valid_ids, candidates=None):
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
            validated = self._adjust_result_by_candidate_context(
                validated,
                candidates or [],
            )
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
    def _adjust_result_by_candidate_context(self, validated, candidates):
        if validated["decision"] != "match" or not validated["product_id"]:
            return validated
        by_id = {
            item.get("product_id"): item
            for item in candidates
            if item.get("product_id")
        }
        selected = by_id.get(validated["product_id"]) or {}
        risk_flags = list(validated.get("risk_flags") or [])
        reason = validated.get("reason") or ""
        confidence = validated.get("confidence", 0.0)

        if selected.get("substitution_decision") == "blocked":
            if "policy_blocked" not in risk_flags:
                risk_flags.append("policy_blocked")
            confidence = min(confidence, 0.85)
            reason = self._append_reason(
                reason,
                "Кандидат заблокирован правилом замен: %s"
                % (
                    selected.get("substitution_reason")
                    or "причина не указана"
                ),
            )

        if selected.get("substitution_requires_confirmation"):
            confidence = min(confidence, 0.89)
            reason = self._append_reason(
                reason,
                "Замена требует ручного подтверждения.",
            )

        if self._has_feature_conflict(selected):
            if "feature_conflict" not in risk_flags:
                risk_flags.append("feature_conflict")
            confidence = min(confidence, 0.85)
            reason = self._append_reason(
                reason,
                "Есть конфликт структурных признаков DN/PN/семейства.",
            )

        if (
            selected.get("has_issue_stock")
            and not risk_flags
            and not selected.get("substitution_requires_confirmation")
            and selected.get("substitution_decision") != "blocked"
            and selected.get("local_score", 0.0) >= 0.84
            and confidence >= 0.84
        ):
            confidence = max(confidence, AUTO_MATCH_THRESHOLD)
            reason = self._append_reason(
                reason,
                "Кандидат имеет остаток на складах выдачи.",
            )

        stock_alternative = self._better_stock_alternative(
            selected,
            candidates,
        )
        if stock_alternative:
            if "stock_alternative_available" not in risk_flags:
                risk_flags.append("stock_alternative_available")
            confidence = min(confidence, 0.85)
            reason = self._append_reason(
                reason,
                "Есть равноценный кандидат с остатком: %s."
                % stock_alternative.get("display_name", ""),
            )

        critical_flags = CRITICAL_RISK_FLAGS | frozenset({
            "policy_blocked",
            "feature_conflict",
            "stock_alternative_available",
        })
        has_critical_risks = bool(critical_flags & set(risk_flags))
        if has_critical_risks:
            confidence = min(confidence, 0.85)

        validated.update(
            {
                "confidence": max(0.0, min(1.0, confidence)),
                "reason": reason,
                "risk_flags": risk_flags,
                "has_critical_risks": has_critical_risks,
            }
        )
        return validated

    @api.model
    def _has_feature_conflict(self, candidate):
        requested = candidate.get("requested_features") or {}
        features = (
            candidate.get("candidate_features")
            or self._candidate_feature_payload(candidate)
        )
        pairs = [
            ("product_family", "feature_conflict"),
            ("diameter_nominal", "diameter_conflict"),
        ]
        for key, _flag in pairs:
            if requested.get(key) and features.get(key):
                if requested[key] != features[key]:
                    return True
        requested_pn = requested.get("pressure_nominal")
        candidate_pn = features.get("pressure_nominal")
        if requested_pn and candidate_pn and candidate_pn < requested_pn:
            return True
        return False

    @api.model
    def _better_stock_alternative(self, selected, candidates):
        if not selected or selected.get("has_issue_stock"):
            return None
        selected_score = selected.get("local_score", 0.0)
        alternatives = [
            item
            for item in candidates
            if item.get("product_id") != selected.get("product_id")
            and item.get("has_issue_stock")
            and item.get("substitution_decision") != "blocked"
            and not self._has_feature_conflict(item)
            and item.get("local_score", 0.0) >= selected_score - 0.05
        ]
        if not alternatives:
            return None
        alternatives.sort(
            key=lambda item: (
                item.get("local_score", 0.0),
                item.get("stock_qty_on_issue_warehouses", 0.0),
            ),
            reverse=True,
        )
        return alternatives[0]

    @api.model
    def _append_reason(self, reason, addition):
        reason = (reason or "").strip()
        addition = (addition or "").strip()
        if not addition or addition in reason:
            return reason
        return ("%s %s" % (reason, addition)).strip() if reason else addition

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
