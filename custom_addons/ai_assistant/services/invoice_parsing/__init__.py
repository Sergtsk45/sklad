# @file: __init__.py
# @description: Пакет парсинга PDF/XLSX-счетов поставщиков (text-first, без vision).
# @dependencies: pdfplumber (external), normalizer, validators, invoice_utils
# @created: 2026-05-30

from .extractor import extract_invoice
from .validators import validate_invoice_data

__all__ = ["extract_invoice", "validate_invoice_data"]
