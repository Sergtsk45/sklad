# @file: llm_header_extractor.py
# @description: LLM-fallback для извлечения реквизитов поставщика из шапки счёта.
#   Вызывается только когда regex-парсер не смог распознать name или inn.
#   Не импортирует Odoo-специфику напрямую — env передаётся извне.
# @dependencies: openrouter_client, extractor (использует как fallback)
# @created: 2026-06-12

from __future__ import annotations

import json
import logging
import re

_logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Ты — парсер реквизитов российских счетов-фактур.
Получаешь сырой текст счёта (первые строки, шапка). Найди блок ПОСТАВЩИКА \
(не покупателя, не банка, не грузополучателя) и верни ТОЛЬКО валидный JSON без \
пояснений и markdown:
{"name":"","inn":"","kpp":"","address":""}

Правила:
- name: краткое название организации (ООО/АО/ИП/ОАО/...), без кавычек,
  без «Общество с ограниченной ответственностью»; если есть скобочная форма \
(ООО "X") — предпочти её.
- inn: ровно 10 или 12 цифр ИНН, без пробелов и символов; только цифры.
- kpp: ровно 9 цифр КПП или пустая строка.
- address: почтовый адрес без телефонов, e-mail, сайтов.

Покупатель, банки-получатели, реквизиты платёжного поручения — игнорировать.
Если поле не найдено — пустая строка "".
Отвечай только JSON.\
"""

_INN_RE = re.compile(r'^\d{10}(?:\d{2})?$')
_KPP_RE = re.compile(r'^\d{9}$')

# Строки, с которых начинается таблица позиций — дальше не нужны.
_TABLE_START_RE = re.compile(
    r'^\s*(?:№\s+(?:артикул|товар|наимено|услуга)|'
    r'n[o°]?\s+(?:name|goods))',
    re.I,
)


def _get_header_text(full_text: str, max_lines: int = 80) -> str:
    """Возвращает первые max_lines строк текста до начала таблицы позиций."""
    lines = full_text.splitlines()
    for i, line in enumerate(lines[:max_lines]):
        if _TABLE_START_RE.match(line):
            return '\n'.join(lines[:i])
    return '\n'.join(lines[:max_lines])


def llm_extract_supplier_header(full_text: str, env) -> dict | None:
    """
    Вызывает LLM для извлечения реквизитов поставщика из шапки счёта.

    Возвращает dict {name, inn, kpp, address} или None при любой ошибке
    (сеть, API, невалидный JSON, пустое имя).

    Вызывается ТОЛЬКО как fallback — когда regex не распознал name или inn.
    """
    try:
        # Импорт здесь, чтобы модуль не требовал Odoo при unit-тестах без env.
        from odoo.addons.ai_assistant.services.openrouter_client import (
            OpenRouterClient,
        )
        client = OpenRouterClient(env)
    except Exception as exc:
        _logger.warning('[llm_header] cannot init client: %s', exc)
        return None

    header = _get_header_text(full_text)
    if not header.strip():
        return None

    messages = [
        {'role': 'system', 'content': _SYSTEM_PROMPT},
        {'role': 'user', 'content': header},
    ]
    try:
        resp = client.send_chat(messages, max_tokens=300)
    except Exception as exc:
        _logger.warning('[llm_header] LLM call failed: %s', exc)
        return None

    raw = (resp.get('answer') or '').strip()
    # Убираем ```json ... ``` если модель завернула
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.I)
    raw = re.sub(r'\s*```\s*$', '', raw).strip()

    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        _logger.warning('[llm_header] invalid JSON from LLM: %r', raw[:300])
        return None

    name = str(data.get('name') or '').strip()
    inn_raw = str(data.get('inn') or '')
    inn = re.sub(r'\D', '', inn_raw)
    kpp_raw = str(data.get('kpp') or '')
    kpp = re.sub(r'\D', '', kpp_raw)
    address = str(data.get('address') or '').strip()

    if not name:
        _logger.warning('[llm_header] LLM returned empty name')
        return None

    if inn and not _INN_RE.match(inn):
        _logger.warning('[llm_header] invalid INN from LLM: %r', inn)
        inn = ''

    if kpp and not _KPP_RE.match(kpp):
        kpp = ''

    _logger.info(
        '[llm_header] extracted: name=%r inn=%s tokens=%s',
        name, inn or '?', resp.get('tokens_used', '?'),
    )
    return {'name': name, 'inn': inn, 'kpp': kpp, 'address': address}
