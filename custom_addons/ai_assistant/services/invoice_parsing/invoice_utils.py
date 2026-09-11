# @file: invoice_utils.py
# @description: Общие эвристики парсинга счетов (имя контрагента, фильтр мусорных строк).
# @dependencies: —
# @created: 2026-05-30

from __future__ import annotations

import re


def extract_party_name(block: str) -> str:
    """Имя контрагента: текст до первого «, ИНН» / « ИНН », без ролевых пометок."""
    cleaned = re.sub(r"\(исполнитель\)|\(заказчик\)", "", block, flags=re.I)
    cleaned = cleaned.strip().strip(":").strip()
    parts = re.split(r",?\s*ИНН\b", cleaned, maxsplit=1, flags=re.I)
    name = parts[0].strip().rstrip(",")
    name = re.sub(r'["«»\']', "", name)
    return " ".join(name.split())


def is_garbage_item(name: str, unit: str = "") -> bool:
    """Строка заголовка таблицы или мусор pdfplumber (например «1 2 4 5 6 7»)."""
    name = (name or "").strip()
    unit = (unit or "").strip()
    if not name:
        return True
    if re.match(r"^[1-7](?:\s+[1-7])+$", name):
        return True
    if re.match(r"^\d{1,2}$", name):
        return True
    if unit.isdigit() and len(unit) <= 2:
        return True
    if not re.search(r"[A-Za-zА-Яа-яЁё]", name):
        return True
    return False
