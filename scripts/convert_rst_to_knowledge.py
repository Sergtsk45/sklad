#!/usr/bin/env python3
"""
AIA-012: Конвертер RST-документации Odoo 19 → локализованный Markdown.

Парсит RST-файлы из репозитория odoo/documentation (ветка 19.0),
извлекает пошаговые инструкции, пути меню и названия кнопок,
применяет term_mapping.json для локализации EN→RU,
сохраняет результат как Markdown в static/knowledge/docs/.

Использование:
    python scripts/convert_rst_to_knowledge.py \
        --source /tmp/odoo-docs-19/content/applications \
        --output custom_addons/ai_assistant/static/knowledge/docs \
        --term-mapping custom_addons/ai_assistant/static/knowledge/term_mapping.json

    python scripts/convert_rst_to_knowledge.py --demo --output .../docs
"""
import argparse
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------

# Маппинг ключей RST-разделов → имена выходных MD-файлов.
# Ключ — суффикс пути относительно --source (без .rst).
# Значение — имя выходного файла.
FILE_MAP = {
    # Склад
    'inventory_and_mrp/inventory/warehouses_storage': 'stock_warehouses.md',
    'inventory_and_mrp/inventory/products': 'stock_products.md',
    'inventory_and_mrp/inventory/operations': 'stock_operations.md',
    'inventory_and_mrp/inventory/inventory_adjustments': 'stock_inventory.md',
    # Продажи
    'sales/sales/quotations': 'sale_quotations.md',
    'sales/sales/invoicing': 'sale_invoicing.md',
    # Закупки
    'inventory_and_mrp/purchase/purchase_orders': 'purchase_orders.md',
    'inventory_and_mrp/purchase/receipts': 'purchase_receipts.md',
    # CRM
    'sales/crm/leads': 'crm_leads.md',
    'sales/crm/pipeline': 'crm_pipeline.md',
    # Контакты
    'essentials/contacts': 'contacts_management.md',
    # Настройки
    'general': 'settings_general.md',
}

# Модуль по имени выходного файла (для frontmatter).
MODULE_BY_OUTPUT = {
    'stock_warehouses.md': 'stock',
    'stock_products.md': 'stock',
    'stock_operations.md': 'stock',
    'stock_inventory.md': 'stock',
    'sale_quotations.md': 'sale',
    'sale_invoicing.md': 'sale',
    'purchase_orders.md': 'purchase',
    'purchase_receipts.md': 'purchase',
    'crm_leads.md': 'crm',
    'crm_pipeline.md': 'crm',
    'contacts_management.md': 'contacts',
    'settings_general.md': 'settings',
}

# Шаблоны демо-контента для каждого MD-файла (режим --demo).
DEMO_TEMPLATES = {
    'stock_warehouses.md': {
        'title': 'Управление складами в Odoo 19',
        'sections': [
            {
                'heading': 'Создание нового склада',
                'steps': [
                    'Перейдите в **Склад** → **Конфигурация** → **Склады**.',
                    'Нажмите **Новое**.',
                    'Заполните поле **Название склада** и **Краткое имя**.',
                    'Настройте маршруты склада в разделе **Конфигурация**.',
                ],
                'notes': [
                    'В Odoo 19 форма сохраняется автоматически.',
                ],
            },
            {
                'heading': 'Настройка местонахождений',
                'steps': [
                    'Перейдите в **Склад** → **Конфигурация** → **Местонахождения**.',
                    'Выберите местонахождение или создайте новое через **Новое**.',
                    'Укажите тип местонахождения и родительское местонахождение.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['склад', 'warehouse', 'местонахождение', 'маршрут'],
    },
    'stock_products.md': {
        'title': 'Управление товарами на складе',
        'sections': [
            {
                'heading': 'Создание нового товара',
                'steps': [
                    'Перейдите в **Склад** → **Товары** → **Товары**.',
                    'Нажмите **Новое**.',
                    'Укажите **Тип товара**: Хранимый, Расходный или Услуга.',
                    'Заполните **Единица измерения** и установите цены.',
                ],
                'notes': [
                    'Только товары типа «Хранимый» формируют складские остатки.',
                ],
            },
            {
                'heading': 'Инвентаризация',
                'steps': [
                    'Перейдите в **Склад** → **Операции** → **Инвентаризация**.',
                    'Нажмите **Новое** для создания записи инвентаризации.',
                    'Добавьте товары и укажите фактические количества.',
                    'Нажмите **Подтвердить** для применения корректировки.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['товар', 'product', 'хранимый', 'инвентаризация'],
    },
    'stock_operations.md': {
        'title': 'Складские операции: поступления и отгрузки',
        'sections': [
            {
                'heading': 'Обработка поступления товаров',
                'steps': [
                    'Перейдите в **Склад** → **Операции** → **Поступления**.',
                    'Откройте поступление в статусе «Готово».',
                    'Проверьте количества в колонке **Выполнено**.',
                    'Нажмите **Проверить наличие** если количества не заполнены.',
                    'Нажмите **Подтвердить** для завершения поступления.',
                ],
                'notes': [
                    'Если количество меньше заказанного — система предложит создать дозаказ.',
                ],
            },
            {
                'heading': 'Обработка отгрузки товаров',
                'steps': [
                    'Перейдите в **Склад** → **Операции** → **Отгрузки**.',
                    'Откройте отгрузку в статусе «Готово».',
                    'Нажмите **Проверить наличие** для резервирования товаров.',
                    'Проверьте и скорректируйте количества при необходимости.',
                    'Нажмите **Подтвердить** для подтверждения отгрузки.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['поступление', 'receipt', 'отгрузка', 'delivery', 'перемещение'],
    },
    'stock_inventory.md': {
        'title': 'Инвентаризация склада',
        'sections': [
            {
                'heading': 'Проведение инвентаризации',
                'steps': [
                    'Перейдите в **Склад** → **Операции** → **Инвентаризация**.',
                    'Нажмите **Новое** для создания акта инвентаризации.',
                    'Выберите местонахождение и добавьте товары.',
                    'Заполните фактические количества в колонке **Количество**.',
                    'Нажмите **Подтвердить** для сохранения результатов.',
                ],
                'notes': [
                    'Разница между учётным и фактическим количеством '
                    'автоматически корректируется при подтверждении.',
                ],
            },
        ],
        'keywords': ['инвентаризация', 'inventory', 'остатки', 'корректировка'],
    },
    'sale_quotations.md': {
        'title': 'Котировки и заказы на продажу',
        'sections': [
            {
                'heading': 'Создание котировки',
                'steps': [
                    'Перейдите в **Продажи** → **Заказы** → **Котировки**.',
                    'Нажмите **Новое**.',
                    'Выберите **Клиента** в поле «Клиент».',
                    'Добавьте товары в раздел «Строки заказа» через **Добавить строку**.',
                    'Укажите количество и цену для каждого товара.',
                    'Нажмите **Отправить по эл. почте** или **Подтвердить** для оформления заказа.',
                ],
                'notes': [
                    'После подтверждения котировка становится заказом на продажу.',
                ],
            },
            {
                'heading': 'Выставление счёта',
                'steps': [
                    'Откройте подтверждённый заказ на продажу.',
                    'Нажмите **Выставить счёт**.',
                    'Проверьте данные счёта и нажмите **Подтвердить**.',
                    'Отправьте счёт клиенту через **Отправить по эл. почте**.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['котировка', 'quotation', 'заказ', 'продажа', 'счёт'],
    },
    'sale_invoicing.md': {
        'title': 'Выставление счетов в модуле Продажи',
        'sections': [
            {
                'heading': 'Политики выставления счетов',
                'steps': [
                    'Перейдите в **Продажи** → **Конфигурация** → **Настройки**.',
                    'В разделе «Выставление счетов» выберите политику: '
                    'по заказанному или по доставленному количеству.',
                    'Нажмите **Подтвердить** для сохранения.',
                ],
                'notes': [
                    'Политика «по доставленному» требует подтверждения доставки '
                    'перед выставлением счёта.',
                ],
            },
        ],
        'keywords': ['счёт', 'invoicing', 'оплата', 'выставление'],
    },
    'purchase_orders.md': {
        'title': 'Заказы на закупку',
        'sections': [
            {
                'heading': 'Создание запроса котировки',
                'steps': [
                    'Перейдите в **Закупки** → **Заказы** → **Запросы котировок**.',
                    'Нажмите **Новое**.',
                    'Выберите **Поставщика**.',
                    'Добавьте товары через **Добавить строку**.',
                    'Укажите количество, цену и ожидаемую дату поставки.',
                    'Нажмите **Подтвердить заказ** для создания заказа поставщику.',
                ],
                'notes': [
                    'После подтверждения запрос котировки становится заказом поставщику.',
                ],
            },
            {
                'heading': 'Отправка заказа поставщику',
                'steps': [
                    'Откройте подтверждённый заказ поставщику.',
                    'Нажмите **Отправить по эл. почте** для отправки заказа.',
                    'Заполните тему и текст письма.',
                    'Нажмите **Отправить**.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['закупка', 'purchase', 'поставщик', 'запрос котировки', 'заказ поставщику'],
    },
    'purchase_receipts.md': {
        'title': 'Приёмка товаров по заказу закупки',
        'sections': [
            {
                'heading': 'Приёмка поступления',
                'steps': [
                    'Откройте заказ поставщику.',
                    'Нажмите кнопку **Поступления** (счётчик в верхней части).',
                    'В поступлении проверьте количества в колонке **Выполнено**.',
                    'Отредактируйте фактические количества при необходимости.',
                    'Нажмите **Подтвердить** для завершения приёмки.',
                ],
                'notes': [
                    'При частичной приёмке система предложит создать дозаказ '
                    'на оставшееся количество.',
                ],
            },
        ],
        'keywords': ['приёмка', 'receipt', 'поступление', 'закупка'],
    },
    'crm_leads.md': {
        'title': 'Работа с лидами в CRM',
        'sections': [
            {
                'heading': 'Создание лида',
                'steps': [
                    'Перейдите в **CRM** → **Лиды**.',
                    'Нажмите **Новое**.',
                    'Заполните имя контакта, компанию и контактные данные.',
                    'Укажите **Ожидаемую выручку** и **Вероятность**.',
                    'Назначьте **Ответственного** менеджера.',
                ],
                'notes': [
                    'Лиды можно конвертировать в возможности через меню **Действие**.',
                ],
            },
            {
                'heading': 'Конвертация лида в возможность',
                'steps': [
                    'Откройте лид.',
                    'Нажмите **Конвертировать в возможность**.',
                    'Укажите клиента и контактное лицо.',
                    'Выберите воронку продаж и этап.',
                    'Нажмите **Конвертировать**.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['лид', 'lead', 'crm', 'возможность', 'opportunity'],
    },
    'crm_pipeline.md': {
        'title': 'Воронка продаж CRM',
        'sections': [
            {
                'heading': 'Управление воронкой',
                'steps': [
                    'Перейдите в **CRM** → **Продажи** → **Воронка**.',
                    'Просматривайте возможности в виде **Канбан** или **Список**.',
                    'Перетащите карточку в следующий этап для обновления статуса.',
                    'Кликните на карточку для просмотра деталей возможности.',
                ],
                'notes': [
                    'Этапы воронки настраиваются в **CRM** → **Конфигурация** → **Этапы**.',
                ],
            },
            {
                'heading': 'Планирование активностей',
                'steps': [
                    'Откройте возможность.',
                    'Нажмите **Запланировать активность** в разделе активностей.',
                    'Выберите тип активности (звонок, встреча, email).',
                    'Укажите дедлайн и ответственного.',
                    'Нажмите **Запланировать**.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['воронка', 'pipeline', 'kanban', 'этап', 'возможность'],
    },
    'contacts_management.md': {
        'title': 'Управление контактами',
        'sections': [
            {
                'heading': 'Создание контакта',
                'steps': [
                    'Перейдите в **Контакты**.',
                    'Нажмите **Новое**.',
                    'Укажите тип контакта: физическое лицо или компания.',
                    'Заполните **Имя контакта**, **Телефон**, **Эл. почта**.',
                    'Добавьте адрес: **Улица**, **Город**, **Страна**.',
                ],
                'notes': [
                    'Контакты-сотрудники компании создаются как дочерние '
                    'контакты от записи компании.',
                ],
            },
            {
                'heading': 'Поиск и фильтрация контактов',
                'steps': [
                    'В списке контактов используйте поле поиска.',
                    'Примените **Фильтры** для отбора по типу, стране или тегу.',
                    'Используйте **Группировать по** для группировки по компании или стране.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['контакт', 'contact', 'клиент', 'поставщик', 'компания'],
    },
    'settings_general.md': {
        'title': 'Общие настройки Odoo 19',
        'sections': [
            {
                'heading': 'Настройка компании',
                'steps': [
                    'Перейдите в **Настройки** → **Общие настройки**.',
                    'В разделе «Компании» проверьте название и реквизиты.',
                    'Загрузите логотип компании через кнопку загрузки изображения.',
                    'Укажите **Валюту** и **Страну** компании.',
                ],
                'notes': [
                    'В Odoo 19 форма сохраняется автоматически.',
                ],
            },
            {
                'heading': 'Управление пользователями',
                'steps': [
                    'Перейдите в **Настройки** → **Пользователи и компании** → **Пользователи**.',
                    'Нажмите **Новое** для создания пользователя.',
                    'Укажите имя, email и установите права доступа.',
                    'Пользователь получит приглашение на email для установки пароля.',
                ],
                'notes': [],
            },
        ],
        'keywords': ['настройки', 'settings', 'пользователь', 'компания', 'конфигурация'],
    },
}

# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

logger = logging.getLogger('convert_rst')


def load_term_mapping(path: Path) -> dict:
    """Загрузить term_mapping.json."""
    if not path.exists():
        logger.warning('term_mapping not found: %s — используется пустой маппинг', path)
        return {'buttons': {}, 'menu_items': {}, 'fields': {}, 'removed_in_v19': {}}
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def _build_replace_table(term_mapping: dict) -> list:
    """
    Построить таблицу замен (EN → RU), отсортированную от длинных к коротким
    чтобы «Check Availability» заменялось раньше «Check».
    Приоритет: buttons > menu_items > fields.
    """
    combined = {}
    for section in ('fields', 'menu_items', 'buttons'):
        combined.update(term_mapping.get(section, {}))
    return sorted(combined.items(), key=lambda kv: -len(kv[0]))


def apply_term_mapping(text: str, replace_table: list) -> tuple:
    """
    Применить маппинг терминов к тексту.
    Возвращает (новый_текст, число_замен).
    Замена выполняется только для слов с заглавной буквы внутри **...** или отдельно.
    """
    count = 0
    for en, ru in replace_table:
        if en in text:
            text = text.replace(en, ru)
            count += 1
    return text, count


def _is_removed_in_v19(text: str, removed: dict) -> bool:
    """Проверить, содержит ли строк/шаг устаревший термин из removed_in_v19."""
    for term in removed:
        if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------------
# Парсинг RST
# ---------------------------------------------------------------------------

# Символы подчёркивания для уровней заголовков RST
RST_HEADING_CHARS = set('=-~^"\'`#+*')


def _detect_headings(lines: list) -> list:
    """
    Найти заголовки RST по паттерну: строка текста, строка из одного символа.
    Возвращает список (line_index, heading_text, level_char).
    """
    headings = []
    for i in range(len(lines) - 1):
        line = lines[i].rstrip()
        underline = lines[i + 1].rstrip()
        if (line and underline
                and len(underline) >= len(line)
                and len(set(underline)) == 1
                and underline[0] in RST_HEADING_CHARS
                and not line.startswith('...')):
            headings.append((i, line.strip(), underline[0]))
    return headings


def _extract_directive_block(lines: list, start: int) -> list:
    """
    Извлечь тело директивы (.. note::, .. tip::) начиная со строки start.
    Тело — непустые строки с отступом после строки директивы.
    """
    body_lines = []
    i = start + 1
    # Пропустить пустые строки сразу после директивы
    while i < len(lines) and not lines[i].strip():
        i += 1
    # Определить отступ тела
    if i < len(lines):
        indent = len(lines[i]) - len(lines[i].lstrip())
        if indent == 0:
            return []
        while i < len(lines):
            stripped = lines[i].rstrip()
            if stripped and (len(stripped) - len(stripped.lstrip())) < indent:
                break
            body_lines.append(stripped.strip())
            i += 1
    return [line for line in body_lines if line]


def parse_rst_file(path: Path, term_mapping: dict) -> dict:
    """
    Парсит один RST-файл.

    Возвращает:
    {
        'title': str,
        'sections': [{'heading': str, 'steps': [str], 'menus': [str],
                       'buttons': [str], 'notes': [str]}],
        'keywords': [str],
    }
    """
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()

    replace_table = _build_replace_table(term_mapping)
    removed_in_v19 = term_mapping.get('removed_in_v19', {})

    # 1. Найти заголовки
    headings = _detect_headings(lines)
    title = headings[0][1] if headings else path.stem.replace('_', ' ').title()

    # 2. Разбить на секции по заголовкам
    heading_indices = [h[0] for h in headings]
    sections_raw = []
    for idx, (line_idx, heading, _) in enumerate(headings):
        end = heading_indices[idx + 1] if idx + 1 < len(headings) else len(lines)
        sections_raw.append({
            'heading': heading,
            'lines': lines[line_idx + 2:end],  # +2: пропустить саму строку и underline
        })

    # 3. Обработать каждую секцию
    all_menus = []
    all_buttons = []
    sections = []

    for sec in sections_raw:
        steps = []
        menus = []
        buttons = []
        notes = []
        sec_lines = sec['lines']

        i = 0
        while i < len(sec_lines):
            raw = sec_lines[i]
            stripped = raw.strip()

            # Пошаговые инструкции: #. text
            if re.match(r'^#\.\s+', stripped):
                step_text = re.sub(r'^#\.\s+', '', stripped)
                # Проверить удалённые термины ДО маппинга (пока термин ещё на EN)
                if _is_removed_in_v19(step_text, removed_in_v19):
                    i += 1
                    continue
                step_text, _ = apply_term_mapping(step_text, replace_table)
                steps.append(_rst_inline_to_md(step_text))

            # Нумерованные шаги через цифру: 1. text
            elif re.match(r'^\d+\.\s+\S', stripped):
                step_text = re.sub(r'^\d+\.\s+', '', stripped)
                if _is_removed_in_v19(step_text, removed_in_v19):
                    i += 1
                    continue
                step_text, _ = apply_term_mapping(step_text, replace_table)
                steps.append(_rst_inline_to_md(step_text))

            # Пути меню: :menuselection:`A --> B --> C`
            menu_matches = re.findall(
                r':menuselection:`([^`]+)`', stripped
            )
            for menu_raw in menu_matches:
                menu = menu_raw.replace(' --> ', ' → ')
                menu, _ = apply_term_mapping(menu, replace_table)
                menus.append(menu)
                all_menus.append(menu)

            # Кнопки: **ButtonName** (слова с заглавной буквы, не длиннее 5 слов)
            btn_matches = re.findall(r'\*\*([A-Z][^*]{1,40})\*\*', stripped)
            for btn in btn_matches:
                btn_ru, _ = apply_term_mapping(btn, replace_table)
                if btn_ru not in buttons:
                    buttons.append(btn_ru)
                    all_buttons.append(btn_ru)

            # Блоки note / tip
            if re.match(r'^\.\.\s+(note|tip|warning|important)::', stripped):
                note_body = _extract_directive_block(sec_lines, i)
                if note_body:
                    note_text = ' '.join(note_body)
                    note_text, _ = apply_term_mapping(note_text, replace_table)
                    notes.append(_rst_inline_to_md(note_text))

            i += 1

        heading_ru, _ = apply_term_mapping(sec['heading'], replace_table)
        sections.append({
            'heading': heading_ru,
            'steps': steps,
            'menus': list(dict.fromkeys(menus)),
            'buttons': list(dict.fromkeys(buttons)),
            'notes': notes,
        })

    # 4. Ключевые слова из меню и кнопок
    keywords = list(dict.fromkeys(all_menus + all_buttons))

    return {
        'title': title,
        'sections': sections,
        'keywords': keywords[:20],  # ограничить
    }


def _rst_inline_to_md(text: str) -> str:
    """Преобразовать RST inline-разметку в Markdown."""
    # :menuselection:`A --> B` → **A → B**
    text = re.sub(
        r':menuselection:`([^`]+)`',
        lambda m: '**' + m.group(1).replace(' --> ', ' → ') + '**',
        text,
    )
    # :guilabel:`X` → **X**
    text = re.sub(r':guilabel:`([^`]+)`', r'**\1**', text)
    # `code` → `code` (оставляем)
    # ``code`` → `code`
    text = re.sub(r'``([^`]+)``', r'`\1`', text)
    # :ref:`label <target>` → label
    text = re.sub(r':ref:`([^<`]+)\s*<[^>]+>`', r'\1', text)
    # :ref:`target` → target
    text = re.sub(r':ref:`([^`]+)`', r'\1', text)
    # Одиночный backtick: `text`_ → text
    text = re.sub(r'`([^`]+)`_+', r'\1', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Поиск RST-файлов в source директории
# ---------------------------------------------------------------------------

def find_rst_files(source: Path) -> dict:
    """
    Найти RST-файлы соответствующие FILE_MAP.
    Возвращает {rst_key: Path} для найденных файлов.
    """
    found = {}
    for key, out_name in FILE_MAP.items():
        # Ищем как файл или директорию с index.rst
        candidates = [
            source / (key + '.rst'),
            source / key / 'index.rst',
        ]
        for cand in candidates:
            if cand.exists():
                found[key] = cand
                break
        else:
            # Попробуем найти любой RST в директории
            dir_path = source / key
            if dir_path.is_dir():
                rst_files = list(dir_path.glob('*.rst'))
                if rst_files:
                    found[key] = rst_files[0]
    return found


# ---------------------------------------------------------------------------
# Генерация Markdown
# ---------------------------------------------------------------------------

def render_markdown(
    parsed: dict,
    source_key: str,
    output_name: str,
    generated_date: str,
) -> str:
    """Сгенерировать Markdown из распарсенных данных."""
    module = MODULE_BY_OUTPUT.get(output_name, 'unknown')
    keywords_str = ', '.join(parsed['keywords']) if parsed['keywords'] else ''

    lines = [
        '---',
        f'source: {source_key}',
        f'module: {module}',
        f'generated: {generated_date}',
        '---',
        '',
        f'# {parsed["title"]}',
        '',
    ]

    if keywords_str:
        lines += [f'**Ключевые слова**: {keywords_str}', '']

    lines += ['## Шаг за шагом', '']

    for sec in parsed['sections']:
        if not sec['steps'] and not sec['notes']:
            continue

        lines.append(f'### {sec["heading"]}')
        lines.append('')

        # Пути меню (если есть уникальные)
        if sec['menus']:
            lines.append('**Навигация:**')
            for menu in sec['menus'][:3]:
                lines.append(f'- {menu}')
            lines.append('')

        # Шаги
        for i, step in enumerate(sec['steps'], 1):
            lines.append(f'{i}. {step}')
        if sec['steps']:
            lines.append('')

        # Примечания
        for note in sec['notes']:
            lines.append(f'> **Примечание**: {note}')
        if sec['notes']:
            lines.append('')

    return '\n'.join(lines)


def render_demo_markdown(output_name: str, generated_date: str) -> str:
    """Сгенерировать демо-заглушку Markdown для тестирования пайплайна."""
    template = DEMO_TEMPLATES.get(output_name)
    if not template:
        source_key = output_name.replace('.md', '')
        template = {
            'title': output_name.replace('_', ' ').replace('.md', '').title(),
            'sections': [],
            'keywords': [],
        }

    source_key = output_name.replace('.md', '').replace('_', '/')
    module = MODULE_BY_OUTPUT.get(output_name, 'unknown')
    keywords_str = ', '.join(template.get('keywords', []))

    lines = [
        '---',
        f'source: {source_key}',
        f'module: {module}',
        f'generated: {generated_date}',
        'demo: true',
        '---',
        '',
        f'# {template["title"]}',
        '',
        '> **[DEMO - RST not available]** '
        'Этот файл сгенерирован как заглушка. '
        'Для получения реального контента выполните клонирование '
        'репозитория odoo/documentation и запустите скрипт без --demo.',
        '',
    ]

    if keywords_str:
        lines += [f'**Ключевые слова**: {keywords_str}', '']

    lines += ['## Шаг за шагом', '']

    for sec in template.get('sections', []):
        lines.append(f'### {sec["heading"]}')
        lines.append('')

        for i, step in enumerate(sec['steps'], 1):
            lines.append(f'{i}. {step}')
        if sec.get('steps'):
            lines.append('')

        for note in sec.get('notes', []):
            lines.append(f'> **Примечание**: {note}')
        if sec.get('notes'):
            lines.append('')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Основная логика
# ---------------------------------------------------------------------------

def convert_all(
    source: Path,
    output: Path,
    term_mapping_path: Path,
    dry_run: bool = False,
    demo: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Основной процесс конвертации.
    Возвращает summary: {'processed': int, 'skipped': int,
    'term_replacements': int, 'warnings': list}.
    """
    term_mapping = load_term_mapping(term_mapping_path)
    replace_table = _build_replace_table(term_mapping)
    generated_date = date.today().isoformat()

    if not dry_run:
        output.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0
    total_replacements = 0
    warnings = []

    # Определить, работаем ли в demo-режиме
    source_exists = source.exists() if source else False
    use_demo = demo or not source_exists

    if use_demo and not demo:
        logger.warning(
            'Source directory не найден: %s — переключаемся в demo-режим', source
        )
        warnings.append(f'Source не найден: {source} — использован demo-режим')

    if use_demo:
        logger.info('Режим: DEMO — генерируются заглушки')
        for out_name in FILE_MAP.values():
            content = render_demo_markdown(out_name, generated_date)
            out_path = output / out_name

            if dry_run:
                logger.info('[dry-run] Создать: %s (%d байт)', out_path, len(content))
            else:
                out_path.write_text(content, encoding='utf-8')
                if verbose:
                    logger.info('Записан: %s', out_path)

            processed += 1

    else:
        # Реальный режим парсинга RST
        found_files = find_rst_files(source)
        logger.info('Найдено RST-файлов: %d из %d', len(found_files), len(FILE_MAP))

        for key, out_name in FILE_MAP.items():
            if key not in found_files:
                msg = f'RST не найден для {key!r} → {out_name}'
                logger.warning('%s', msg)
                warnings.append(msg)
                skipped += 1
                continue

            rst_path = found_files[key]
            try:
                parsed = parse_rst_file(rst_path, term_mapping)
            except Exception as e:
                msg = f'Ошибка парсинга {rst_path}: {e}'
                logger.error('%s', msg)
                warnings.append(msg)
                skipped += 1
                continue

            # Подсчёт замен (применить маппинг к всему тексту для статистики)
            raw_text = rst_path.read_text(encoding='utf-8', errors='replace')
            _, replacements = apply_term_mapping(raw_text, replace_table)
            total_replacements += replacements

            content = render_markdown(parsed, key, out_name, generated_date)
            out_path = output / out_name

            if dry_run:
                sections_count = len(parsed['sections'])
                steps_count = sum(len(s['steps']) for s in parsed['sections'])
                logger.info(
                    '[dry-run] %s → %s (секций: %d, шагов: %d)',
                    rst_path.name, out_name, sections_count, steps_count,
                )
            else:
                out_path.write_text(content, encoding='utf-8')
                if verbose:
                    logger.info('Записан: %s (%d байт)', out_path, len(content))

            processed += 1

    return {
        'processed': processed,
        'skipped': skipped,
        'term_replacements': total_replacements,
        'warnings': warnings,
        'demo_mode': use_demo,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'AIA-012: Конвертер RST-документации Odoo 19 → '
            'локализованный Markdown для knowledge base AI-ассистента.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Конвертация реальных RST (предварительно клонировать репозиторий):
  git clone --branch 19.0 --depth 1 \\
      https://github.com/odoo/documentation.git /tmp/odoo-docs-19

  python scripts/convert_rst_to_knowledge.py \\
      --source /tmp/odoo-docs-19/content/applications \\
      --output custom_addons/ai_assistant/static/knowledge/docs \\
      --term-mapping custom_addons/ai_assistant/static/knowledge/term_mapping.json

  # Режим демо (без клонирования):
  python scripts/convert_rst_to_knowledge.py --demo \\
      --output custom_addons/ai_assistant/static/knowledge/docs

  # Просмотр без записи:
  python scripts/convert_rst_to_knowledge.py --demo --dry-run
""",
    )
    parser.add_argument(
        '--source', '-s',
        type=Path,
        default=Path('/tmp/odoo-docs-19/content/applications'),
        help='Путь к директории applications в репозитории odoo/documentation '
             '(default: /tmp/odoo-docs-19/content/applications)',
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('custom_addons/ai_assistant/static/knowledge/docs'),
        help='Директория для сохранения MD-файлов '
             '(default: custom_addons/ai_assistant/static/knowledge/docs)',
    )
    parser.add_argument(
        '--term-mapping', '-t',
        type=Path,
        dest='term_mapping',
        default=Path('custom_addons/ai_assistant/static/knowledge/term_mapping.json'),
        help='Путь к term_mapping.json '
             '(default: custom_addons/ai_assistant/static/knowledge/term_mapping.json)',
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Генерировать демо-заглушки вместо реального парсинга RST',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Показать что будет создано без записи файлов',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод',
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
    )

    logger.info('=== AIA-012: RST → Knowledge Base ===')
    logger.info('Source:       %s', args.source)
    logger.info('Output:       %s', args.output)
    logger.info('Term mapping: %s', args.term_mapping)
    if args.dry_run:
        logger.info('Режим:        DRY RUN (файлы не записываются)')
    if args.demo:
        logger.info('Режим:        DEMO (заглушки)')

    summary = convert_all(
        source=args.source,
        output=args.output,
        term_mapping_path=args.term_mapping,
        dry_run=args.dry_run,
        demo=args.demo,
        verbose=args.verbose,
    )

    # Итоговый отчёт
    logger.info('')
    logger.info('=== Итоги ===')
    logger.info('Обработано файлов:   %d', summary['processed'])
    logger.info('Пропущено файлов:    %d', summary['skipped'])
    logger.info('Замен терминов:      %d', summary['term_replacements'])
    if summary['demo_mode']:
        logger.info('Режим:               DEMO')
    if summary['warnings']:
        logger.warning('Предупреждения (%d):', len(summary['warnings']))
        for w in summary['warnings']:
            logger.warning('  - %s', w)

    if not args.dry_run and summary['processed'] > 0:
        logger.info('')
        logger.info(
            'Готово. Перезапустите Odoo для применения: '
            'docker compose -f docker-compose.local.yml restart odoo'
        )

    return 0 if summary['skipped'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
