#!/usr/bin/env python3
"""
@file: ocr_parse.py
@description: OCR-парсинг сканированного PDF-счёта (Tesseract + pdfplumber)
@dependencies: pdfplumber, pytesseract, Pillow; системный tesseract (rus)
@created: 2026-06-25

Usage:
    python3 ocr_parse.py <path-to.pdf> [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import ImageEnhance

# ── OCR-исправления (синхронизировать с ocr-corrections.md) ──
_REPLACEMENTS = [
    (r"Анурстрой", "Амурстрой"),
    (r"Анурская", "Амурская"),
    (r"Гамка", "Гайка"),
    (r"шестигоан\.?", "шестигран."),
    (r"шестиган\.?", "шестигран."),
    (r"шеститан\.?", "шестигран."),
    (r"\bМЕ\b", "М6"),
    (r"\bМВ\b", "М6"),
    (r"СУМ\s*934", "DIN 934"),
    (r"ГОСТ\s*934", "DIN 934"),
    (r"Теплосервис-\s*Комплект", "Теплосервис-Комплект"),
    (r"Теплосервис-\s*Конплект", "Теплосервис-Комплект"),
    (r"imailru", "mail.ru"),
    (r"gamail", "gmail"),
]

_INN_RE = re.compile(r"(\d{10}|\d{12})")
_KPP_AFTER_INN = re.compile(r"(\d{10,12})[/:\s]+(\d{9})")
_CONTRACT_RE = re.compile(
    r"Договор[-\s]?Счет\s*№\s*([Пп]?\d+)\s+от\s+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
    re.I,
)
_TOTAL_RE = re.compile(r"Итого:\s*([\d\s]+[,.][\d]{2})", re.I)
_VAT_RE = re.compile(r"НДС:\s*([\d\s]+[,.][\d]{2})", re.I)
_BIK_RE = re.compile(r"БИК\s*[\[:\s]*(\d{9})", re.I)
_RS_RE = re.compile(r"(\d{20})")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
_PHONE_RE = re.compile(r"\+?7[-\s(]?\d{3}[-\s)]?\d{3}[-\s]?\d{2}[-\s]?\d{2}")

KNOWN_SUPPLIERS = {
    "2801019127": 'ОАО УПТК "Амурстрой"',
}
KNOWN_BUYERS = {
    "2801131520": 'ООО "Теплосервис-Комплект"',
}


def _looks_like_amurstroy(full_text: str) -> bool:
    """Быстро определить договор-счёт Амурстроя до импорта спецпарсера."""
    if "2801019127" in full_text:
        return True
    return bool(re.search(r"Амурстрой|УПТК", full_text, re.I) and _CONTRACT_RE.search(full_text))


def _fix_text(text: str) -> str:
    for pattern, repl in _REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.I)
    return text


def _to_float(s: str) -> float | None:
    s = s.replace("\u00a0", "").replace(" ", "").replace(",", ".")
    s = re.sub(r"[^\d.]", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def _ocr_page(page, resolution: int = 400) -> tuple[str, str]:
    """Возвращает (полный текст, текст кропа таблицы)."""
    img = page.to_image(resolution=resolution).original.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.5)
    w, h = img.size
    full = pytesseract.image_to_string(img, lang="rus+eng", config="--psm 6")
    crop = img.crop((int(w * 0.02), int(h * 0.52), int(w * 0.98), int(h * 0.78)))
    table = pytesseract.image_to_string(crop, lang="rus+eng", config="--psm 4")
    return _fix_text(full), _fix_text(table)


def _extract_header(full_text: str) -> dict:
    result = {
        "document_type": "contract_invoice",
        "invoice_number": "",
        "invoice_date": "",
        "supplier": {"name": "", "inn": "", "kpp": "", "address": ""},
        "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        "bank": {"bik": "", "account": "", "corr_account": "", "name": ""},
        "contacts": {"phones": [], "emails": []},
    }

    m = _CONTRACT_RE.search(full_text)
    if m:
        result["invoice_number"] = m.group(1)
        result["invoice_date"] = m.group(2)

    for inn_m in _INN_RE.finditer(full_text):
        inn = inn_m.group(1)
        if inn in KNOWN_SUPPLIERS and not result["supplier"]["inn"]:
            result["supplier"]["inn"] = inn
            result["supplier"]["name"] = KNOWN_SUPPLIERS[inn]
        elif inn in KNOWN_BUYERS and not result["buyer"]["inn"]:
            result["buyer"]["inn"] = inn
            result["buyer"]["name"] = KNOWN_BUYERS[inn]

    for m in _KPP_AFTER_INN.finditer(full_text):
        inn, kpp = m.group(1), m.group(2)
        if inn == result["supplier"]["inn"]:
            result["supplier"]["kpp"] = kpp
        elif inn == result["buyer"]["inn"]:
            result["buyer"]["kpp"] = kpp

    bik = _BIK_RE.search(full_text)
    if bik:
        result["bank"]["bik"] = bik.group(1)

    accounts = _RS_RE.findall(full_text)
    if accounts:
        result["bank"]["account"] = accounts[0]
        if len(accounts) > 1:
            result["bank"]["corr_account"] = accounts[1]

    result["contacts"]["emails"] = list(dict.fromkeys(_EMAIL_RE.findall(full_text)))
    result["contacts"]["phones"] = list(dict.fromkeys(_PHONE_RE.findall(full_text)))

    return result


def _extract_items(table_text: str) -> list[dict]:
    """Простой парсер строк таблицы по паттерну qty+unit+prices."""
    items = []
    line_re = re.compile(
        r"(.+?)\s+(\d+)\s+(шт|кг|м|уп)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)",
        re.I,
    )
    for m in line_re.finditer(table_text):
        name = m.group(1).strip(" -|")
        if any(x in name.lower() for x in ("продаже", "уважа", "маты")):
            continue
        items.append({
            "name": name,
            "qty": _to_float(m.group(2)),
            "unit": m.group(3),
            "price": _to_float(m.group(4)),
            "amount_before_discount": _to_float(m.group(5)),
            "discount_or_vat": _to_float(m.group(6)),
            "amount": _to_float(m.group(7)),
        })
    return items


def parse_invoice_pdf(path: Path) -> dict:
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        if page.chars:
            return {
                "source": "text_layer",
                "message": "PDF содержит текстовый слой — используйте extract_invoice() из ai_assistant",
                "chars": len(page.chars),
            }

        full_text, table_text = _ocr_page(page)

    header = _extract_header(full_text)
    items = _extract_items(table_text)

    # Договор-счёт Амурстроя — возвращаем полный контракт спецпарсера.
    if _looks_like_amurstroy(full_text):
        try:
            _amur_path = Path(__file__).resolve().parents[2] / "amurstroy-invoice-parsing" / "scripts"
            if str(_amur_path) not in sys.path:
                sys.path.insert(0, str(_amur_path))
            from amurstroy_parse import parse_amurstroy_texts  # noqa: WPS433

            return parse_amurstroy_texts(full_text, table_text, file=str(path))
        except Exception as exc:
            return {
                "source": "ocr",
                "format": "amurstroy_contract_invoice",
                "file": str(path),
                "warnings": [
                    "pdf_is_scan",
                    "ocr_tesseract",
                    f"amurstroy_parser_failed: {exc}",
                ],
                "needs_review": True,
                **header,
                "items": items,
                "totals": {"total": None, "vat": None, "items_sum": 0},
                "_raw_full": full_text,
                "_raw_table": table_text,
            }

    total_m = _TOTAL_RE.search(table_text) or _TOTAL_RE.search(full_text)
    vat_m = _VAT_RE.search(table_text) or _VAT_RE.search(full_text)
    total = _to_float(total_m.group(1)) if total_m else None
    vat = _to_float(vat_m.group(1)) if vat_m else None

    items_sum = sum(i["amount"] or 0 for i in items)
    warnings = ["pdf_is_scan", "ocr_tesseract"]
    needs_review = False
    if not items:
        warnings.append("items_empty")
        needs_review = True
    if total and items and abs(items_sum - total) > 0.02:
        warnings.append(f"sum_mismatch: items={items_sum:.2f} total={total:.2f}")
        needs_review = True

    return {
        "source": "ocr",
        "file": str(path),
        "warnings": warnings,
        "needs_review": needs_review,
        **header,
        "items": items,
        "totals": {"total": total, "vat": vat, "items_sum": items_sum},
        "_raw_full": full_text,
        "_raw_table": table_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR parse scanned invoice PDF")
    parser.add_argument("pdf", type=Path, help="Path to PDF file")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"File not found: {args.pdf}", file=sys.stderr)
        return 1

    result = parse_invoice_pdf(args.pdf)

    if args.json:
        # omit raw OCR blobs in json mode unless needed
        out = {k: v for k, v in result.items() if not k.startswith("_raw")}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"Источник: {result.get('source')}")
    if result.get("message"):
        print(result["message"])
        return 0

    print(f"Счёт № {result.get('invoice_number')} от {result.get('invoice_date')}")
    s = result["supplier"]
    print(f"Поставщик: {s['name']} ИНН {s['inn']} КПП {s['kpp']}")
    b = result["buyer"]
    print(f"Покупатель: {b['name']} ИНН {b['inn']} КПП {b['kpp']}")
    print(f"Итого: {result['totals'].get('total')}  НДС: {result['totals'].get('vat')}")
    for i, item in enumerate(result["items"], 1):
        print(f"  {i}. {item['name']} — {item['qty']} {item['unit']} × {item['price']} = {item['amount']}")
    if result.get("warnings"):
        print("Предупреждения:", ", ".join(result["warnings"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
