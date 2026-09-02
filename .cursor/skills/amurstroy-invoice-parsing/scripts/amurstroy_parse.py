#!/usr/bin/env python3
"""
@file: amurstroy_parse.py
@description: Парсер договор-счетов ОАО УПТК «Амурстрой» (скан, OCR)
@dependencies: pdfplumber, pytesseract, Pillow; ocr_parse._ocr_page, _extract_header
@created: 2026-06-25
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Переиспользуем OCR-инфраструктуру общего скана
_SCRIPTS = Path(__file__).resolve().parents[2] / "scanned-invoice-parsing" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import pdfplumber  # noqa: E402
from ocr_parse import (  # noqa: E402
    KNOWN_SUPPLIERS,
    _CONTRACT_RE,
    _TOTAL_RE,
    _VAT_RE,
    _extract_header,
    _fix_text,
    _ocr_page,
    _to_float,
)

AMURSTROY_INN = "2801019127"
DEFAULT_DISCOUNT = 5.0

# OCR-исправления, специфичные для таблицы Амурстроя
_TABLE_REPLACEMENTS = [
    (r"750лл", '750мл'),
    (r"лл\b", "мл"),
    (r"Сунна", "Сумма"),
    (r"д\.\s*Цена", "Ед."),
    (r"т\s+00\b", "427.00"),
    (r"O37\s+50", "237.50"),
    (r"1865\.20", "186.20"),
    (r"мешкз0", "мешок 30"),
    (r"^ate армированный", "Лента армированный"),
    (r"Пacreapirene", "Растворитель"),
    (r"мля", "для"),
    (r"г-утые", "гнутые"),
    (r"ШТА/ПУ", ""),
    (r"^\[Уп Шт\.\)$", ""),
    (r"^Л аштА мп$", ""),
]

_GARBAGE_LINE = re.compile(
    r"продаже|уважа|директор|бухгалтер|всего наименований|"
    r"рублей|копеек|матов|дерев\s*ян|черенком|нижний нов|"
    r"^\s*[\|\[\]ИЕЕНЫhere]+\s*$",
    re.I,
)

_LINE_NO = re.compile(r"^[\[\|]?\s*(\d+)\s*[\|\s]+")
# OCR «95 00 4750.00» вместо «95 шт …»
_QTY_OCR_00 = re.compile(r"(\d+)\s+00\s+([\d'\"])")
# Единицы в таблице заказа (не «м» из «48 мм х 50 м» в названии)
_QTY_UNIT = re.compile(
    r"(\d+)\s*(шт|уп\.?|пара|кг)\s+(?=[\d'\"])",
    re.I,
)
_MONEY_TOKEN = re.compile(r"\d[\d'\u2019]*[,.]\d{2}")
_SUBTOTAL_RE = re.compile(
    r"на\s+сумму\s+([\d\s]+[,.][\d]{2})\s*руб",
    re.I,
)


def is_amurstroy_text(text: str) -> bool:
    """Определить договор-счёт Амурстроя по тексту OCR."""
    if AMURSTROY_INN in text:
        return True
    if re.search(r"Амурстрой|УПТК", text, re.I) and _CONTRACT_RE.search(text):
        return True
    return False


def _fix_table_text(text: str) -> str:
    text = _fix_text(text)
    for pattern, repl in _TABLE_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.I | re.M)
    text = _QTY_OCR_00.sub(r"\1 шт \2", text)
    # OCR: «(36 308.00» — номер строки склеен с ценой
    text = re.sub(r"\(\d{1,2}\s+([\d'\"])", r"\1", text)
    # Склеить разорванные суммы: "15'741 .50" → "15741.50"
    text = re.sub(
        r"(\d[\d'\s]*)\s+\.\s*(\d{2})\b",
        lambda m: m.group(1).replace(" ", "").replace("'", "") + "." + m.group(2),
        text,
    )
    return text


def _money_tokens(line: str) -> list[float]:
    vals = []
    for m in _MONEY_TOKEN.finditer(line):
        v = _to_float(m.group(0))
        if v is not None:
            vals.append(v)

    # OCR: «4389.00» → «10 389.00» при известном gross
    if len(vals) >= 5:
        gross = vals[-4]
        tail = vals[-1]
        expected_net = round(gross * 0.95, 2)
        if gross > 0 and abs(expected_net % 1000 - tail) < 1.5:
            vals = vals[:-2] + [expected_net]
        else:
            a, b = vals[-2], vals[-1]
            for merged in (a * 100 + b, a * 1000 + b):
                if gross > 0 and abs(merged - expected_net) / gross < 0.015:
                    vals = vals[:-2] + [merged]
                    break

    # OCR: net «4389» распознан как «231.00» + хвост «389.00»
    if len(vals) == 4:
        price, gross, disc, tail = vals
        expected_net = round(gross * 0.95, 2)
        if gross > 100 and abs(expected_net % 1000 - tail) < 1.5:
            vals[-1] = expected_net

    return vals


def _pick_money_columns(vals: list[float]) -> list[float]:
    """Выбрать 4 колонки цена / сумма без скидки / скидка / сумма из списка OCR-токенов."""
    if len(vals) < 4:
        return vals
    best = vals[-4:]
    best_score = 999.0
    for i in range(len(vals) - 3):
        price, gross, disc, net = vals[i], vals[i + 1], vals[i + 2], vals[i + 3]
        if gross <= 0 or net <= 0:
            continue
        score = abs(net - gross * 0.95) / gross
        if disc > 0 and gross > 0:
            score = min(score, abs(disc - gross * 0.05) / gross)
        if score < best_score:
            best_score = score
            best = [price, gross, disc, net]
    return best


def _reconcile_qty_price(
    qty: float, price: float, gross: float, net: float,
) -> tuple[float, float]:
    """Подобрать qty и price при сдвиге колонок OCR."""
    if price > 0 and gross > 0:
        inferred = round(gross / price)
        if inferred > 0 and abs(inferred * price - gross) / gross < 0.02:
            return float(inferred), price

    if qty > 0 and net > 0 and price > 0:
        expected_net = qty * price * (1 - DEFAULT_DISCOUNT / 100)
        if abs(expected_net - net) / net > 0.02:
            implied_price = net / (qty * (1 - DEFAULT_DISCOUNT / 100))
            if implied_price > 0:
                price = round(implied_price, 2)

    if price > 0 and net > 0:
        for pct in (DEFAULT_DISCOUNT, 10.0, 0.0):
            factor = 1 - pct / 100
            if factor <= 0:
                continue
            inferred = round(net / (price * factor))
            if inferred > 0:
                g = inferred * price
                n = g * factor
                if abs(n - net) / net < 0.02:
                    return float(inferred), price

    if gross > 0 and net > 0 and price > 0:
        inferred = round(gross / price)
        if inferred > 0:
            return float(inferred), price

    return qty, price


def _infer_discount(price: float, qty: float, gross: float, discount: float, net: float) -> float:
    """Вернуть скидку % для PO; по умолчанию 5% у Амурстроя."""
    if gross > 0 and net > 0:
        pct = round((1 - net / gross) * 100, 2)
        if 0 < pct <= 30:
            return pct
    if price > 0 and qty > 0 and net > 0:
        pct = round((1 - net / (price * qty)) * 100, 2)
        if 0 < pct <= 30:
            return pct
    return DEFAULT_DISCOUNT


def _parse_row(
    name: str, qty: float, unit: str, monies: list[float], *, explicit_qty: bool = False,
) -> dict | None:
    """Разобрать строку по колонкам цена / сумма без скидки / скидка / сумма."""
    if len(monies) == 3 and qty > 0:
        gross, discount_amt, net = monies
        price = round(gross / qty, 2) if qty else 0.0
    elif len(monies) >= 4:
        picked = _pick_money_columns(monies)
        price, gross, discount_amt, net = picked
        if not explicit_qty and price > 0 and gross > 0 and net > 0:
            inferred_qty = round(gross / price)
            if (
                inferred_qty > 1
                and abs(inferred_qty * price * 0.95 - net) / net < 0.02
            ):
                qty = float(inferred_qty)
        if explicit_qty and qty > 0 and net > 0:
            if price > 0 and abs(qty * price * 0.95 - net) / net > 0.02:
                price = round(net / (qty * (1 - DEFAULT_DISCOUNT / 100)), 2)
                gross = round(qty * price, 2)
                discount_amt = round(gross - net, 2)
        elif qty > 0 and net > 0 and abs(gross * 0.95 - net) / max(net, 1) > 0.05:
            price = round(net / (qty * (1 - DEFAULT_DISCOUNT / 100)), 2)
            gross = round(qty * price, 2)
            discount_amt = round(gross - net, 2)
    else:
        return None

    qty, price = _reconcile_qty_price(qty, price, gross, net)

    if net <= 0 or price <= 0 or qty <= 0:
        return None

    name = re.sub(r"^[\d\|\[\]\s]+", "", name).strip(" -|")
    name = re.sub(r"\s{2,}", " ", name)
    # Убрать ценовые хвосты, попавшие в наименование
    m0 = _MONEY_TOKEN.search(name)
    if m0:
        name = name[:m0.start()].strip()
    if len(name) < 3:
        return None

    return {
        "name": name,
        "qty": qty,
        "unit": unit,
        "price": price,
        "amount_before_discount": gross,
        "discount_amount": discount_amt,
        "amount": net,
        "discount_percent": _infer_discount(price, qty, gross, discount_amt, net),
    }


def _extract_qty_unit(
    line: str, monies: list[float],
) -> tuple[float, str, int, bool] | None:
    """Найти кол-во и единицу. explicit=True, если в тексте есть «N шт/уп/пара»."""
    matches = list(_QTY_UNIT.finditer(line))
    if matches:
        m = matches[-1]
        return float(m.group(1)), m.group(2).lower(), m.start(), True

    if len(monies) >= 3:
        picked = _pick_money_columns(monies) if len(monies) >= 4 else monies
        price = picked[0]
        gross = picked[1] if len(picked) > 1 else picked[0]
        net = picked[-1]
        qty, _ = _reconcile_qty_price(1.0, price, gross, net)
        if qty > 0:
            pos = line.find(str(int(qty)))
            return qty, "шт", pos if pos >= 0 else 0, False

    return None


def extract_amurstroy_items(table_text: str) -> list[dict]:
    """
    Извлечь позиции из OCR-текста таблицы договор-счёта Амурстроя.

    Формат колонок: Товар | Кол-во | Ед. | Цена | Сумма без скидки | Скидка | Сумма
    Типичная скидка: 5%.
    """
    table_text = _fix_table_text(table_text)
    lines = table_text.splitlines()
    items: list[dict] = []
    buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        block = " ".join(buffer)
        buffer = []

        monies = _money_tokens(block)
        if len(monies) < 3:
            return

        qu = _extract_qty_unit(block, monies)
        if not qu:
            return

        qty, unit, pos, explicit = qu
        name = block[:pos] if pos else block
        row = _parse_row(name, qty, unit, monies, explicit_qty=explicit)
        if row:
            items.append(row)

    started = False
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.search(r"без скидки", line, re.I):
            started = True
            continue
        if not started:
            continue
        if _TOTAL_RE.search(line) or _SUBTOTAL_RE.search(line):
            flush_buffer()
            break
        if _GARBAGE_LINE.search(line):
            continue

        # Новая строка с номером — сбросить буфер
        if _LINE_NO.match(line) and buffer:
            flush_buffer()

        monies = _money_tokens(line)
        qu = _extract_qty_unit(line, monies)

        if qu and len(monies) >= 3:
            flush_buffer()
            qty, unit, pos, explicit = qu
            name = line[:pos] if pos else line
            row = _parse_row(name, qty, unit, monies, explicit_qty=explicit)
            if row:
                items.append(row)
            continue

        # Строка только с ценами (название в буфере)
        if buffer and len(monies) >= 3:
            block = " ".join(buffer + [line])
            buffer = []
            monies = _money_tokens(block)
            qu = _extract_qty_unit(block, monies)
            if qu:
                qty, unit, pos, explicit = qu
                name = block[:pos] if pos else block
                row = _parse_row(name, qty, unit, monies, explicit_qty=explicit)
                if row:
                    items.append(row)
            continue

        buffer.append(line)

    flush_buffer()
    return items


def _partner_ref(invoice_number: str) -> str:
    """Нормализовать номер счёта для partner_ref."""
    num = invoice_number.strip()
    if num.upper().startswith("П"):
        digits = re.sub(r"\D", "", num)
        return f"П{digits.zfill(9)}" if digits else num
    # Короткий номер из OCR «14101» → П000014101
    if num.isdigit() and len(num) <= 6:
        return f"П0000{num}"
    return num


def _validation_state(items: list[dict], target: float | None, items_sum: float) -> tuple[list[str], bool]:
    """Вернуть warnings и needs_review для fail-closed workflow."""
    warnings: list[str] = ["pdf_is_scan", "ocr_tesseract", "format_amurstroy"]

    if not items:
        warnings.append("items_empty")
        return warnings, True

    if target is None:
        warnings.append("validation_target_missing")
        return warnings, True

    diff = abs(items_sum - target)
    if diff > 1.0:
        warnings.append(f"sum_mismatch: items={items_sum:.2f} expected={target:.2f}")
        return warnings, True

    if diff > 0.02:
        warnings.append(f"sum_rounding: items={items_sum:.2f} expected={target:.2f}")

    return warnings, False


def parse_amurstroy_texts(full_text: str, table_text: str, file: str = "") -> dict:
    """Разобрать уже распознанные OCR-тексты договор-счёта Амурстроя."""
    if not is_amurstroy_text(full_text):
        return {
            "source": "ocr",
            "format": "unknown",
            "message": "Не похоже на договор-счёт Амурстроя — используйте scanned-invoice-parsing",
            "needs_review": True,
        }

    header = _extract_header(full_text)
    items = extract_amurstroy_items(table_text)

    total_m = _TOTAL_RE.search(table_text) or _TOTAL_RE.search(full_text)
    vat_m = _VAT_RE.search(table_text) or _VAT_RE.search(full_text)
    sub_m = _SUBTOTAL_RE.search(table_text) or _SUBTOTAL_RE.search(full_text)

    total = _to_float(total_m.group(1)) if total_m else None
    vat = _to_float(vat_m.group(1)) if vat_m else None
    subtotal_wo_vat = _to_float(sub_m.group(1)) if sub_m else None

    items_sum = round(sum(i["amount"] for i in items), 2)
    target = subtotal_wo_vat or total
    warnings, needs_review = _validation_state(items, target, items_sum)

    inv_num = header.get("invoice_number", "")
    return {
        "source": "ocr",
        "format": "amurstroy_contract_invoice",
        "file": file,
        "partner_ref": _partner_ref(inv_num),
        "validation_target": "subtotal_wo_vat" if subtotal_wo_vat else "total",
        "needs_review": needs_review,
        "warnings": warnings,
        **header,
        "items": items,
        "totals": {
            "total": total,
            "vat": vat,
            "subtotal_wo_vat": subtotal_wo_vat,
            "items_sum": items_sum,
        },
        "_raw_full": full_text,
        "_raw_table": table_text,
    }


def parse_amurstroy_pdf(path: Path) -> dict:
    """Полный разбор PDF договор-счёта Амурстроя."""
    with pdfplumber.open(path) as pdf:
        if not pdf.pages:
            raise ValueError("PDF без страниц")
        page = pdf.pages[0]
        if page.chars:
            return {
                "source": "text_layer",
                "message": "Текстовый PDF — используйте extract_invoice() из ai_assistant",
                "chars": len(page.chars),
            }
        full_text, table_text = _ocr_page(page)

    return parse_amurstroy_texts(full_text, table_text, file=str(path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Парсер договор-счетов ОАО УПТК «Амурстрой» (OCR)",
    )
    parser.add_argument("pdf", type=Path, help="Путь к PDF")
    parser.add_argument("--json", action="store_true", help="Только JSON")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"Файл не найден: {args.pdf}", file=sys.stderr)
        return 1

    result = parse_amurstroy_pdf(args.pdf)

    if args.json:
        out = {k: v for k, v in result.items() if not str(k).startswith("_raw")}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if result.get("message") and not result.get("items"):
        print(result["message"])
        return 0

    print(f"Формат: {result.get('format', '?')}")
    print(f"Счёт № {result.get('partner_ref')} от {result.get('invoice_date')}")
    s = result["supplier"]
    print(f"Поставщик: {s['name']} ИНН {s['inn']}")
    t = result["totals"]
    print(f"Итого: {t.get('total')}  без НДС: {t.get('subtotal_wo_vat')}  НДС: {t.get('vat')}")
    for i, item in enumerate(result.get("items", []), 1):
        print(
            f"  {i}. {item['name']} — {item['qty']} {item['unit']} × "
            f"{item['price']} −{item['discount_percent']}% = {item['amount']}"
        )
    if result.get("warnings"):
        print("Предупреждения:", ", ".join(result["warnings"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
