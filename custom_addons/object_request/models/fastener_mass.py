"""
@file: fastener_mass.py
@description: Масса 1 шт. болтов (ГОСТ 7798/7805) и гаек (ГОСТ 5915)
@dependencies: stdlib
@created: 2026-10-15

Сначала — табличная масса ГОСТ 7798-70 / ГОСТ 5915-70 (масса 1000 шт.,
кг = масса 1 шт., г). Для типоразмеров вне таблицы — расчёт по размерам
стандарта, сталь 7,85 г/см³: шестигранник (размер под
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

# ГОСТ 7798-70: d → {длина l, мм: масса 1 шт., г}
_BOLT_LENGTHS_M6_M10 = (10, 20, 25, 30)
_BOLT_LENGTHS_M12_M16 = tuple(range(30, 95, 5))
_BOLT_LENGTHS_M18_M24 = tuple(range(60, 125, 5))
GOST_7798_BOLT_MASS_G = {
    6: dict(zip(_BOLT_LENGTHS_M6_M10, (4.712, 6.742, 7.871, 8.981))),
    8: dict(zip(_BOLT_LENGTHS_M6_M10, (9.394, 13.02, 14.84, 17.12))),
    10: dict(zip(_BOLT_LENGTHS_M6_M10, (16.68, 22.37, 25.22, 28.52))),
    12: dict(zip(_BOLT_LENGTHS_M12_M16, (
        40.96, 45.34, 49.78, 54.22, 58.67, 63.11, 67.55, 71.99, 76.44,
        80.88, 85.33, 89.77, 94.20,
    ))),
    14: dict(zip(_BOLT_LENGTHS_M12_M16, (
        59.64, 65.24, 71.25, 77.30, 83.35, 89.39, 95.44, 101.5, 107.5,
        113.6, 119.6, 125.7, 131.7,
    ))),
    16: dict(zip(_BOLT_LENGTHS_M12_M16, (
        83.24, 90.62, 97.99, 105.7, 113.6, 121.5, 129.4, 137.3, 145.2,
        153.1, 161.0, 168.9, 176.8,
    ))),
    18: dict(zip(_BOLT_LENGTHS_M18_M24, (
        172.4, 182.4, 192.4, 202.4, 212.4, 222.4, 232.4, 242.4, 252.4,
        262.4, 272.3, 282.3, 292.3,
    ))),
    20: dict(zip(_BOLT_LENGTHS_M18_M24, (
        216.0, 228.4, 240.7, 253.0, 265.0, 277.7, 290.1, 302.4, 314.7,
        327.1, 339.4, 351.8, 364.1,
    ))),
    22: dict(zip(_BOLT_LENGTHS_M18_M24, (
        278.9, 293.8, 308.8, 323.7, 338.6, 353.6, 368.5, 383.4, 398.3,
        413.3, 428.2, 443.1, 458.1,
    ))),
    24: dict(zip(_BOLT_LENGTHS_M18_M24, (
        329.9, 348.8, 366.5, 384.3, 402.1, 419.8, 437.6, 455.4, 473.2,
        490.9, 508.7, 526.5, 544.2,
    ))),
}
# ГОСТ 5915-70: d → масса 1 шт., г
GOST_5915_NUT_MASS_G = {
    6: 2.573, 8: 5.548, 10: 10.22, 12: 15.67, 14: 25.33, 16: 37.61,
    18: 53.27, 20: 71.44, 22: 103.15, 24: 122.87,
}
KG_PER_PIECE_DIGITS = 5

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
    return round(volume * STEEL_DENSITY_G_MM3 / 1000.0, KG_PER_PIECE_DIGITS)


def gost_table_mass_kg(kind, diameter, length=None):
    """Табличная масса 1 шт. по ГОСТ 7798 / 5915, кг; None — нет в таблице."""
    if kind == "nut":
        grams = GOST_5915_NUT_MASS_G.get(diameter)
    else:
        grams = GOST_7798_BOLT_MASS_G.get(diameter, {}).get(length)
    if grams is None:
        return None
    return round(grams / 1000.0, KG_PER_PIECE_DIGITS)


def suggest_kg_per_piece(name):
    """Масса 1 шт. по наименованию или 0.0, если тип не распознан.

    Табличная масса ГОСТ, если типоразмер есть в таблице, иначе расчётная.
    """
    parsed = parse_fastener(name)
    if not parsed:
        return 0.0
    table_mass = gost_table_mass_kg(*parsed)
    if table_mass is not None:
        return table_mass
    return theoretical_mass_kg(*parsed)


def gost_fastener_specs():
    """Типоразмеры таблиц ГОСТ: [(kind, d, length, масса 1 шт., кг)]."""
    specs = []
    for diameter, lengths in sorted(GOST_7798_BOLT_MASS_G.items()):
        for length in sorted(lengths):
            specs.append((
                "bolt", diameter, length,
                gost_table_mass_kg("bolt", diameter, length),
            ))
    for diameter in sorted(GOST_5915_NUT_MASS_G):
        specs.append((
            "nut", diameter, None, gost_table_mass_kg("nut", diameter),
        ))
    return specs


def gost_fastener_name(kind, diameter, length=None, zinc=False):
    """Наименование карточки: «Болт М16×55 ГОСТ 7798-70 оцинкованный»."""
    if kind == "nut":
        name = f"Гайка М{diameter} ГОСТ 5915-70"
        return f"{name} оцинкованная" if zinc else name
    name = f"Болт М{diameter}×{length} ГОСТ 7798-70"
    return f"{name} оцинкованный" if zinc else name


def is_zinc_coated(name):
    """Оцинкованный метиз по наименованию («оцинк», «цинк», «Zn»)."""
    lowered = (name or "").lower()
    return "цинк" in lowered or re.search(r"\bzn\b", lowered) is not None
