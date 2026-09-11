# -*- coding: utf-8 -*-
"""Pure helpers for converting pipe quantities to meters."""

import re

from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

METER_TOKENS = {
    "m",
    "meter",
    "meters",
    "metre",
    "metres",
    "м",
    "метр",
    "метры",
    "метров",
}
KILO_TOKENS = {
    "kg",
    "kgs",
    "кг",
    "килограмм",
    "килограммы",
}
TON_TOKENS = {
    "t",
    "ton",
    "tons",
    "tonne",
    "tonnes",
    "т",
    "тонна",
    "тонны",
    "тонн",
}
PIECE_TOKENS = {
    "pcs",
    "pc",
    "piece",
    "pieces",
    "шт",
    "штука",
    "штуки",
    "штук",
    "хлыст",
    "хлысты",
}

_LENGTH_HINT_PATTERNS = (
    re.compile(
        r"(?i)\b(?:l|length|длина)\s*[:=]?\s*"
        r"(?P<value>\d+(?:[.,]\d+)?)\s*(?:м\b)?"
    ),
    re.compile(
        r"(?i)\b(?P<value>\d+(?:[.,]\d+)?)\s*м\b"
    ),
)


def normalize_pipe_unit(unit):
    return (unit or "").strip().lower()


def extract_pipe_length_m(text):
    source = (text or "").strip()
    if not source:
        return None
    for pattern in _LENGTH_HINT_PATTERNS:
        match = pattern.search(source)
        if match:
            return float(match.group("value").replace(",", "."))
    return None


def convert_pipe_quantity(
    quantity,
    unit,
    *,
    kg_per_meter=None,
    length_m=None,
    description=None,
    precision_digits=2,
):
    """Convert invoice quantity to meters and return a human readable trace."""
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError("Некорректное количество для пересчёта трубы.")
    if quantity <= 0:
        raise ValidationError("Количество для пересчёта трубы должно быть > 0.")

    token = normalize_pipe_unit(unit)
    if token in METER_TOKENS:
        meters = quantity
        formula = "%s м = %s м" % (
            _format_number(quantity),
            _format_number(meters),
        )
    elif token in KILO_TOKENS:
        kg_per_meter = _require_kg_per_meter(kg_per_meter)
        meters = quantity / kg_per_meter
        formula = "%s кг / %s кг/м = %s м" % (
            _format_number(quantity),
            _format_number(kg_per_meter),
            _format_number(meters),
        )
    elif token in TON_TOKENS:
        kg_per_meter = _require_kg_per_meter(kg_per_meter)
        meters = quantity * 1000.0 / kg_per_meter
        formula = "%s т × 1000 / %s кг/м = %s м" % (
            _format_number(quantity),
            _format_number(kg_per_meter),
            _format_number(meters),
        )
    elif token in PIECE_TOKENS:
        length_m = _require_pipe_length_m(
            length_m,
            description=description,
        )
        meters = quantity * length_m
        formula = "%s шт × %s м = %s м" % (
            _format_number(quantity),
            _format_number(length_m),
            _format_number(meters),
        )
    else:
        raise ValidationError(
            'Единица "%s" не поддерживается для пересчёта труб.'
            % (unit or "не задана")
        )

    return {
        "source_quantity": quantity,
        "source_unit": unit,
        "kg_per_meter": kg_per_meter,
        "length_m": length_m,
        "meters": float_round(meters, precision_digits=precision_digits),
        "formula": formula,
    }


def _require_kg_per_meter(kg_per_meter):
    try:
        kg_per_meter = float(kg_per_meter)
    except (TypeError, ValueError):
        kg_per_meter = 0.0
    if kg_per_meter <= 0:
        raise ValidationError(
            'Для трубы не заполнен коэффициент "кг/м". '
            'Укажите его в карточке товара.'
        )
    return kg_per_meter


def _require_pipe_length_m(length_m, description=None):
    if length_m is None:
        length_m = extract_pipe_length_m(description)
    try:
        length_m = float(length_m)
    except (TypeError, ValueError):
        length_m = 0.0
    if length_m <= 0:
        raise ValidationError(
            'Для хлыста не удалось определить длину. '
            'Укажите её в наименовании или в строке счёта.'
        )
    return length_m


def _format_number(value):
    text = ("%.6f" % float(value)).rstrip("0").rstrip(".")
    return text or "0"
