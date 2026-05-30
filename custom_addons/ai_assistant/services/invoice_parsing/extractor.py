# @file: extractor.py
# @description: Text-first извлечение данных из PDF-счёта (pdfplumber). Vision-fallback — TD-005.
# @dependencies: pdfplumber (external), normalizer, invoice_utils
# @created: 2026-05-30

from __future__ import annotations

import io
import logging
import re
from typing import Any

import pdfplumber

from .invoice_utils import extract_party_name, is_garbage_item
from .normalizer import normalize_invoice

_logger = logging.getLogger(__name__)

# ── Заголовки колонок (синонимы) ──────────────────────────────
_COL_PATTERNS = {
    "line_no":        re.compile(r"^№|^#|^n[o°]?$", re.I),
    "article":        re.compile(r"артикул|арт\.?|код|article", re.I),
    "name":           re.compile(r"наимено|товар|услуга|описание|name|goods", re.I),
    "qty":            re.compile(r"кол[-\s]?во|количество|qty|count", re.I),
    "unit":           re.compile(r"^ед\.?|единиц|unit|шт|м$", re.I),
    "price":          re.compile(r"цена|price|стоимость|тариф", re.I),
    "amount_wo_vat":  re.compile(r"сумм.*без|без.*ндс|sum.*excl", re.I),
    "discount":       re.compile(r"скид|discount|наценк", re.I),
    "vat_rate":       re.compile(r"ставк.*ндс|%.*ндс|vat.*rate", re.I),
    "vat_amount":     re.compile(r"сумм.*ндс|ндс.*сумм|vat.*amount", re.I),
    "amount_w_vat":   re.compile(r"итого|всего|сумма$|total|amount", re.I),
}

_HEADER_TRIGGER = re.compile(
    r"наимено|товар|услуга|кол[-\s]?во|количество|цена|сумма", re.I
)
_NUM_TOKEN = re.compile(r"^\d[\d\s\u00a0]*[,.]?\d*$")
_MIN_HEADER_COLS = 3


# ═════════════════════════════════════════════════════════════
#  Публичный интерфейс
# ═════════════════════════════════════════════════════════════

def extract_invoice(file_bytes: bytes) -> dict:
    """
    Принимает содержимое PDF-файла (bytes), возвращает нормализованный dict счёта.

    Raises:
        ValueError: если файл не является PDF или не содержит текстового слоя.
    """
    if not file_bytes:
        raise ValueError("Пустой файл")
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("Файл не является PDF (magic bytes %PDF отсутствуют)")

    data = _extract_text_mode(io.BytesIO(file_bytes))
    result = normalize_invoice(data)
    return result


# ═════════════════════════════════════════════════════════════
#  TEXT-FIRST режим
# ═════════════════════════════════════════════════════════════

def _extract_text_mode(pdf_stream: io.BytesIO) -> dict:
    result: dict[str, Any] = {
        "document_type": "supplier_invoice",
        "invoice_number": "",
        "invoice_date": "",
        "supplier": {
            "name": "", "inn": "", "kpp": "", "address": "",
            "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
        },
        "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        "items": [],
        "totals": {"total_wo_vat": "", "vat_total": "", "total_w_vat": ""},
        "pages": 0,
        "warnings": [],
    }

    with pdfplumber.open(pdf_stream) as pdf:
        result["pages"] = len(pdf.pages)
        all_text_lines: list[str] = []

        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
            all_text_lines.extend(text.splitlines())

            tables = page.extract_tables()
            for tbl in tables:
                if not tbl:
                    continue
                items = _parse_table(tbl)
                if items:
                    result["items"].extend(items)

    full_text = "\n".join(all_text_lines)
    _parse_header(full_text, result)
    _parse_totals(full_text, result)

    if not result["items"]:
        result["items"] = _heuristic_table_from_lines(all_text_lines)

    return result


# ── Парсинг шапки счёта ──────────────────────────────────────

_INVOICE_NO_RE = re.compile(
    r"счет[а-яё\s]*(?:на\s+оплату\s*)?"
    r"№\s*("
    r"[A-Za-zА-Яа-яЁё]{1,5}[\-\s]?\d[\w\-/]*|"  # НФ-504, УТ-1132, …
    r"\d[\w\-/]*"
    r").*?от\s+(\d{1,2}[.\s/]\w+[.\s/]\d{2,4})",
    re.I | re.S,
)
_INN_RE = re.compile(r"инн[\s:]+(\d{10,12})", re.I)
_KPP_RE = re.compile(r"кпп[\s:]+(\d{9})", re.I)
_BIK_RE = re.compile(r"бик[\s:]+(\d{9})", re.I)
_ACC_RE = re.compile(r"(?:р/?с|расч[её]тный)\s*(?:счет|сч\.?)[\s№:]*(\d{20})", re.I)
_CACC_RE = re.compile(r"к/?с[\s:№]*(\d{20})", re.I)
_BANK_RE = re.compile(
    r'(?:банк[а-я\s]*получател[яи]?|наименование банка)[:\s]+"?([^\n"]+)', re.I
)
_SUPPLIER_RE = re.compile(
    r"поставщик(?:\s*\([^)]*\))?\s*[:：]?\s*"
    r"(.*?)(?=\n(?:грузоотправитель|покупатель|грузополучатель)\b|$)",
    re.I | re.S,
)
_BUYER_RE = re.compile(
    r"покупатель(?:\s*\([^)]*\))?\s*[:：]?\s*"
    r"(.*?)(?=\n(?:грузополучатель|основание)\b|\n\s*\n|$)",
    re.I | re.S,
)


def _first(pattern: re.Pattern, text: str, group: int = 1) -> str:
    m = pattern.search(text)
    return m.group(group).strip() if m else ""


def _parse_header(text: str, result: dict) -> None:
    m = _INVOICE_NO_RE.search(text)
    if m:
        result["invoice_number"] = m.group(1).strip().replace(" ", "-")
        result["invoice_date"] = _normalize_date(m.group(2).strip())

    sup_block = _first(_SUPPLIER_RE, text)
    if sup_block:
        result["supplier"]["name"] = extract_party_name(sup_block)
        result["supplier"]["inn"] = _first(_INN_RE, sup_block)
        result["supplier"]["kpp"] = _first(_KPP_RE, sup_block)
        result["supplier"]["address"] = _extract_address(sup_block)

    buy_block = _first(_BUYER_RE, text)
    if buy_block:
        result["buyer"]["name"] = extract_party_name(buy_block)
        result["buyer"]["inn"] = _first(_INN_RE, buy_block)
        result["buyer"]["kpp"] = _first(_KPP_RE, buy_block)
        result["buyer"]["address"] = _extract_address(buy_block)

    result["supplier"]["bank"]["name"] = _first(_BANK_RE, text)
    result["supplier"]["bank"]["bik"] = _first(_BIK_RE, text)
    result["supplier"]["bank"]["account"] = _first(_ACC_RE, text)
    result["supplier"]["bank"]["corr_account"] = _first(_CACC_RE, text)


_DATE_MONTHS = {
    "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
    "мая": "05", "июня": "06", "июля": "07", "августа": "08",
    "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12",
}


def _normalize_date(raw: str) -> str:
    """29 января 2026 г. → 2026-01-29"""
    raw = raw.replace("г.", "").strip()
    for ru, num in _DATE_MONTHS.items():
        raw = raw.replace(ru, num)
    parts = re.split(r"[\s./]+", raw)
    parts = [p for p in parts if p]
    if len(parts) == 3:
        d, m, y = parts
        if len(y) == 2:
            y = "20" + y
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return raw


def _extract_address(text: str) -> str:
    m = re.search(r"\d{6}[,\s]+(.*?)(?:тел\.|e-mail|$)", text, re.I | re.S)
    if m:
        return " ".join(m.group(1).split())
    return ""


# ── Парсинг итогов ───────────────────────────────────────────

_TOTAL_RE = re.compile(r"итого[:\s]+([\d\s\u00a0]+[,.][\d]{2})", re.I)
_VAT_TOTAL_RE = re.compile(
    r"(?:в том числе|в т\.ч\.)\s+ндс[^:]*:?\s+([\d\s\u00a0]+[,.][\d]{2})", re.I
)
_TOPAY_RE = re.compile(r"всего к оплате[:\s]+([\d\s\u00a0]+[,.][\d]{2})", re.I)


def _parse_totals(text: str, result: dict) -> None:
    def grab(pattern):
        m = pattern.search(text)
        return _parse_number(m.group(1)) if m else ""

    result["totals"]["total_wo_vat"] = grab(_TOTAL_RE)
    result["totals"]["vat_total"] = grab(_VAT_TOTAL_RE)
    result["totals"]["total_w_vat"] = grab(_TOPAY_RE)


# ── Парсинг таблицы из pdfplumber extract_tables ─────────────

def _parse_table(rows: list[list]) -> list[dict]:
    if len(rows) < 2:
        return []

    header_row_idx = None
    col_map: dict[str, int] = {}

    for i, row in enumerate(rows[:5]):
        if row is None:
            continue
        matched = _map_columns(row)
        if len(matched) >= _MIN_HEADER_COLS:
            header_row_idx = i
            col_map = matched
            break

    if header_row_idx is None:
        return []

    items = []
    for row in rows[header_row_idx + 1:]:
        if row is None or all(c is None or str(c).strip() == "" for c in row):
            continue
        item = _row_to_item(row, col_map)
        if item:
            items.append(item)
    return items


def _map_columns(header_row: list) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(header_row):
        if cell is None:
            continue
        cell_str = str(cell).strip()
        for field, pattern in _COL_PATTERNS.items():
            if field not in mapping and pattern.search(cell_str):
                mapping[field] = idx
                break
    return mapping


def _row_to_item(row: list, col_map: dict[str, int]) -> dict | None:
    def get(field: str) -> str:
        idx = col_map.get(field)
        if idx is None or idx >= len(row):
            return ""
        v = row[idx]
        return str(v).strip() if v is not None else ""

    name = get("name")
    unit = get("unit")
    if not name or re.match(r"^итого|^всего|^в том числе", name, re.I):
        return None
    if is_garbage_item(name, unit):
        return None

    return {
        "line_no":       get("line_no"),
        "article":       get("article"),
        "name":          name,
        "unit":          unit,
        "qty":           _parse_number(get("qty")),
        "price":         _parse_number(get("price")),
        "amount_wo_vat": _parse_number(get("amount_wo_vat")),
        "discount":      _parse_number(get("discount")),
        "vat_rate":      _parse_vat_rate(get("vat_rate")),
        "vat_amount":    _parse_number(get("vat_amount")),
        "amount_w_vat":  _parse_number(get("amount_w_vat")),
    }


# ── Эвристика: таблица из текстовых строк ───────────────────

def _heuristic_table_from_lines(lines: list[str]) -> list[dict]:
    """Ищем блок строк между заголовком таблицы и «итого»."""
    start_idx = None
    for i, line in enumerate(lines):
        if _HEADER_TRIGGER.search(line):
            start_idx = i + 1
            break

    if start_idx is None:
        return []

    items = []
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        if re.match(r"итого|всего к оплате", line, re.I):
            break

        parts = re.split(r"  +|\t", line)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) < 3:
            continue

        line_no = ""
        if re.match(r"^\d{1,3}$", parts[0]):
            line_no = parts[0]
            parts = parts[1:]

        if len(parts) < 2:
            continue

        amount = ""
        if _NUM_TOKEN.match(parts[-1].replace(" ", "").replace("\u00a0", "")):
            amount = _parse_number(parts[-1])
            parts = parts[:-1]

        price = ""
        if parts and _NUM_TOKEN.match(parts[-1].replace(" ", "").replace("\u00a0", "")):
            price = _parse_number(parts[-1])
            parts = parts[:-1]

        name = " ".join(parts).strip()
        if not name or is_garbage_item(name):
            continue

        items.append({
            "line_no":       line_no,
            "article":       "",
            "name":          name,
            "unit":          "",
            "qty":           "",
            "price":         price,
            "amount_wo_vat": "",
            "discount":      "",
            "vat_rate":      "",
            "vat_amount":    "",
            "amount_w_vat":  amount,
        })

    return items


# ── Вспомогательные числовые парсеры ─────────────────────────

def _parse_number(raw: str) -> float | str:
    """'1 234,56' → 1234.56"""
    if not raw:
        return ""
    s = str(raw).replace("\u00a0", "").replace(" ", "").replace(",", ".")
    s = re.sub(r"[^\d.]", "", s)
    try:
        return float(s)
    except ValueError:
        return ""


def _parse_vat_rate(raw: str) -> str:
    if not raw:
        return ""
    r = str(raw).lower()
    if "без" in r or "не облагается" in r:
        return "без НДС"
    m = re.search(r"\d+", r)
    return m.group() if m else raw
