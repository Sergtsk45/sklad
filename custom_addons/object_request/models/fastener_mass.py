"""
@file: fastener_mass.py
@description: Теоретическая масса болтов (ГОСТ 7798/7805) и гаек (ГОСТ 5915)
@dependencies: stdlib
@created: 2026-10-15

Расчёт по размерам стандарта, сталь 7,85 г/см³: шестигранник (размер под
ключ × высота) плюс стержень; резьбовая часть — по среднему диаметру
резьбы, длина резьбы болта b = 2d + 6 (ГОСТ 7798, l ≤ 125). Фаски не
учитываются — результат на несколько процентов выше табличной массы.
"""

import math
import re

STEEL_DENSITY_G_MM3 = 7.85e-3

# d: (шаг P, размер под ключ S, высота гайки m, высота головки болта k)
FASTENER_DIMENSIONS = {
    5: (0.8, 8, 4.0, 3.5),
    6: (1.0, 10, 5.0, 4.0),
    8: (1.25, 13, 6.5, 5.5),
    10: (1.5, 17, 8.0, 7.0),
    12: (1.75, 19, 10.0, 8.0),
    14: (2.0, 22, 11.0, 9.0),
    16: (2.0, 24, 13.0, 10.0),
    18: (2.5, 27, 15.0, 12.0),
    20: (2.5, 30, 16.0, 13.0),
    22: (2.5, 32, 18.0, 14.0),
    24: (3.0, 36, 19.0, 15.0),
    27: (3.0, 41, 22.0, 17.0),
    30: (3.5, 46, 24.0, 19.0),
}

SUPPORTED_STANDARDS = ("5915", "7798", "7805", "934", "931", "933", "4014",
                       "4017", "4032")
EXCLUDED_WORDS = ("анкер", "самонар", "фундамент", "лемех", "мебел",
                  "бараш", "колпач", "фланц", "рым", "откидн", "путев",
                  "заклеп", "шпильк", "высок", "низк", "приварн")

_KIND_RE = re.compile(r"\b(болт|гайка)\b", re.IGNORECASE)
# М16, М16×55, М16×1,5×55, М16-6gх55.58
_SIZE_RE = re.compile(
    r"\b[мm]\s*(\d{1,2})(?:\s*[xх×*]\s*\d+[.,]\d+)?"
    r"(?:-\d[a-zа-я])?(?:\s*[xх×*]\s*(\d{1,3}))?",
    re.IGNORECASE,
)
_STANDARD_RE = re.compile(
    r"(?:гост|din|iso)\s*(?:р\s*)?(?:исо\s*)?(\d{3,5})", re.IGNORECASE
)


def parse_fastener(name):
    """Болт/гайка из наименования: (kind, d, length) или None.

    Пример: «Болт М16×55 ГОСТ 7798-70» → ("bolt", 16, 55).
    """
    text = (name or "").replace("ё", "е")
    lowered = text.lower()
    kind_match = _KIND_RE.search(lowered)
    if not kind_match or any(word in lowered for word in EXCLUDED_WORDS):
        return None
    standard = _STANDARD_RE.search(lowered)
    if standard and standard.group(1) not in SUPPORTED_STANDARDS:
        return None
    size = _SIZE_RE.search(text[kind_match.end():])
    if not size:
        return None
    diameter = int(size.group(1))
    if diameter not in FASTENER_DIMENSIONS:
        return None
    if kind_match.group(1).lower() == "гайка":
        return ("nut", diameter, None)
    length = int(size.group(2)) if size.group(2) else None
    if not length:
        return None
    return ("bolt", diameter, length)


def _hexagon_area(across_flats):
    return math.sqrt(3) / 2 * across_flats ** 2


def theoretical_mass_kg(kind, diameter, length=None):
    """Теоретическая масса 1 шт., кг."""
    pitch, across_flats, nut_height, head_height = FASTENER_DIMENSIONS[
        diameter
    ]
    pitch_diameter = diameter - 0.6495 * pitch
    thread_area = math.pi * pitch_diameter ** 2 / 4
    if kind == "nut":
        volume = (_hexagon_area(across_flats) - thread_area) * nut_height
    else:
        thread_length = min(length, 2 * diameter + 6)
        volume = (
            _hexagon_area(across_flats) * head_height
            + thread_area * thread_length
            + math.pi * diameter ** 2 / 4 * (length - thread_length)
        )
    return round(volume * STEEL_DENSITY_G_MM3 / 1000.0, 4)


def suggest_kg_per_piece(name):
    """Масса 1 шт. по наименованию или 0.0, если тип не распознан."""
    parsed = parse_fastener(name)
    if not parsed:
        return 0.0
    return theoretical_mass_kg(*parsed)
