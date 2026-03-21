# Roadmap: AI-ассистент v2 — Vision + Odoo Docs + Akaidoo

**Дата:** 2026-03-21  
**Статус:** Проект  
**Базируется на:** существующий модуль `custom_addons/ai_assistant/` (AIA-001 — AIA-011 выполнены)

---

## 1. Новые критерии

| # | Критерий | Описание |
|---|----------|----------|
| К1 | Актуальная документация | Ответы опираются на официальное руководство Odoo 19 (RST) и Akaidoo-контекст, а не на ручные JSON-сниппеты |
| К2 | Анализ экрана | По триггерам («у меня на экране», «смотри на экран», «в открытой вкладке», «что я вижу», «помоги с тем что открыто») — захват скриншота и ответ на основе изображения |
| К3 | Мощная модель | Использовать vision-совместимую модель для анализа скриншотов; для текстовых вопросов допустимо использовать более дешёвую модель |

---

## 2. Текущее состояние и что меняется

### Что есть сейчас

```
Frontend (OWL)               Backend (Python)
┌─────────────┐    POST     ┌──────────────────────┐
│ ai_chat_     │───/chat───▶│ chat_controller.py   │
│ service.js   │            │   ├── context_resolver│
│ (text only)  │◀───JSON────│   ├── knowledge_provider (JSON snippets)
│              │            │   ├── prompt_builder  │
└─────────────┘            │   └── openrouter_client│
                           │       model: gpt-4o-mini (text only)
                           └──────────────────────┘
```

### Что нужно изменить

```
Frontend (OWL)               Backend (Python)
┌─────────────┐    POST     ┌──────────────────────────────┐
│ ai_chat_     │───/chat───▶│ chat_controller.py           │
│ service.js   │  + image   │   ├── context_resolver       │
│ + screenshot │◀───JSON────│   ├── knowledge_provider_v2  │
│   capture    │            │   │   ├── RST docs (Odoo 19) │
└─────────────┘            │   │   ├── Akaidoo context     │
                           │   │   └── term_mapping.json   │
                           │   ├── prompt_builder_v2       │
                           │   │   └── vision mode         │
                           │   ├── screenshot_trigger      │
                           │   └── openrouter_client_v2    │
                           │       ├── text model (дешёвый) │
                           │       └── vision model (мощный)│
                           └──────────────────────────────┘
```

---

## 3. Выбор моделей

### Стратегия: двухуровневая маршрутизация

| Режим | Когда | Модель | Цена (OpenRouter) |
|-------|-------|--------|-------------------|
| **Текстовый** | Обычные вопросы по Odoo | `google/gemini-2.0-flash-001` | $0.075/M input, $0.30/M output |
| **Vision** | Пользователь просит посмотреть на экран | `openai/gpt-4o` или `anthropic/claude-sonnet-4` | $2.50–3.00/M input, $10–15/M output |

### Почему такой выбор

- **Gemini 2.0 Flash** для текста: дешёвый, быстрый, 1M контекст (влезает вся knowledge base), хорошо работает с русским языком. Заменяет `gpt-4o-mini` как дефолтный.
- **GPT-4o / Claude Sonnet 4** для vision: лучшее распознавание UI-элементов на скриншотах, точно читает кнопки, меню, формы Odoo. Вызывается только при триггере — расход контролируемый.

### Конфигурация в Settings

Добавить два поля модели вместо одного:

```python
# models/ai_assistant_config.py — новые параметры
'ai_assistant_text_model': fields.Char(
    default='google/gemini-2.0-flash-001'
),
'ai_assistant_vision_model': fields.Char(
    default='openai/gpt-4o'
),
```

---

## 4. Блок 1: Knowledge base v2 — RST docs + Akaidoo

### 4.1. Источники знаний

| Источник | Что даёт | Формат |
|----------|----------|--------|
| Odoo 19 RST docs | Пошаговые инструкции, названия кнопок/меню, сценарии | Markdown (переработанные RST) |
| Akaidoo context | Структура моделей, поля, связи | Markdown (сгенерированный) |
| term_mapping.json | Маппинг English UI → Russian UI (ru_RU) | JSON |

### 4.2. Подготовка RST-документации

**Шаг 1.** Клонировать репозиторий документации:

```bash
git clone --branch 19.0 --depth 1 \
    https://github.com/odoo/documentation.git \
    /tmp/odoo-docs-19
```

**Шаг 2.** Извлечь нужные разделы:

| Модуль | Путь в репозитории |
|--------|-------------------|
| stock | `content/applications/inventory_and_mrp/inventory/` |
| sale | `content/applications/sales/sales/` |
| purchase | `content/applications/inventory_and_mrp/purchase/` |
| crm | `content/applications/sales/crm/` |
| contacts | `content/applications/essentials/contacts.rst` |
| settings | `content/applications/general/` |

**Шаг 3.** Конвертировать RST → Markdown (с сохранением `:menuselection:` и `**кнопок**`):

```bash
# scripts/convert_rst_to_knowledge.py
# Для каждого RST-файла:
# 1. Извлечь :menuselection:`...` → пути меню
# 2. Извлечь **Button Name** → кнопки
# 3. Извлечь пошаговые инструкции (#. ...)
# 4. Применить term_mapping.json для локализации
# 5. Сохранить как markdown в static/knowledge/docs/
```

**Шаг 4.** Создать `term_mapping.json`:

```json
{
  "odoo_version": "19.0",
  "lang": "ru_RU",
  "verified_date": "2026-03-21",
  "buttons": {
    "New": "Новое",
    "Validate": "Подтвердить",
    "Check Availability": "Проверить наличие",
    "Apply All": "Применить всё",
    "Confirm": "Подтвердить",
    "Cancel": "Отмена",
    "Print": "Печать",
    "Discard": "Отменить изменения",
    "Send by Email": "Отправить по эл. почте"
  },
  "menu_items": {
    "Inventory": "Склад",
    "Configuration": "Конфигурация",
    "Warehouses": "Склады",
    "Products": "Товары",
    "Operations": "Операции",
    "Receipts": "Поступления",
    "Delivery Orders": "Отгрузки",
    "Internal Transfers": "Перемещения",
    "Replenishment": "Пополнение",
    "Sales": "Продажи",
    "Purchase": "Закупки",
    "CRM": "CRM",
    "Contacts": "Контакты",
    "Settings": "Настройки"
  },
  "fields": {
    "Warehouse Name": "Название склада",
    "Short Name": "Краткое имя",
    "Product Type": "Тип товара",
    "Storable": "Хранимый",
    "Consumable": "Расходный",
    "Service": "Услуга",
    "Unit of Measure": "Единица измерения"
  },
  "removed_in_v19": {
    "Save": "В Odoo 19 автосохранение — кнопки «Сохранить» нет",
    "Edit": "В Odoo 19 форма сразу в режиме редактирования"
  }
}
```

### 4.3. Структура файлов knowledge v2

```
static/knowledge/
├── index.json                     ← обновлённый индекс
├── term_mapping.json              ← маппинг терминов EN→RU
├── docs/                          ← переработанные RST → MD
│   ├── stock_warehouses.md
│   ├── stock_products.md
│   ├── stock_operations.md
│   ├── stock_inventory.md
│   ├── sale_quotations.md
│   ├── sale_invoicing.md
│   ├── purchase_orders.md
│   ├── purchase_receipts.md
│   ├── crm_leads.md
│   ├── crm_pipeline.md
│   ├── contacts_management.md
│   └── settings_general.md
├── generated/                     ← akaidoo-контекст (уже есть)
│   ├── stock_context.md
│   ├── purchase_context.md
│   ├── sale_context.md
│   ├── object_request_context.md
│   └── ...
└── legacy/                        ← старые JSON (для справки)
    ├── stock.json
    ├── sale.json
    └── ...
```

### 4.4. Обновлённый knowledge_provider.py

```python
class KnowledgeProviderV2:
    """
    Трёхслойный провайдер знаний:
    1. RST-based docs (пользовательские инструкции с актуальными терминами)
    2. Akaidoo context (структура моделей и полей)
    3. Term mapping (для валидации терминов в ответе)
    """

    def get_knowledge(self, module, query, include_technical=False):
        """
        Возвращает:
        - docs_snippets: релевантные фрагменты из RST-документации
        - tech_context: akaidoo-контекст модели (если include_technical=True)
        - term_mapping: актуальные термины для данного модуля
        """
        docs = self._search_docs(module, query)       # из docs/*.md
        tech = None
        if include_technical:
            tech = self.get_technical_context(module)   # из generated/*.md
        terms = self._get_relevant_terms(module)        # из term_mapping.json

        return {
            'docs_snippets': docs,
            'tech_context': tech,
            'term_mapping': terms,
        }
```

### 4.5. Скрипт полного обновления knowledge base

```bash
#!/bin/bash
# scripts/update_knowledge_v2.sh

set -e

DOCS_REPO="/tmp/odoo-docs-19"
KNOWLEDGE_DIR="custom_addons/ai_assistant/static/knowledge"
AKAIDOO_CONF="akaidoo.conf"

echo "=== Шаг 1: Обновить репозиторий документации ==="
if [ -d "$DOCS_REPO" ]; then
    cd "$DOCS_REPO" && git pull
else
    git clone --branch 19.0 --depth 1 \
        https://github.com/odoo/documentation.git "$DOCS_REPO"
fi

echo "=== Шаг 2: Конвертировать RST → MD с локализацией ==="
python scripts/convert_rst_to_knowledge.py \
    --source "$DOCS_REPO/content/applications" \
    --output "$KNOWLEDGE_DIR/docs" \
    --term-mapping "$KNOWLEDGE_DIR/term_mapping.json"

echo "=== Шаг 3: Обновить Akaidoo-контекст ==="
GENERATED="$KNOWLEDGE_DIR/generated"
mkdir -p "$GENERATED"

for mod in stock purchase sale crm contacts account; do
    echo "  Generating $mod..."
    akaidoo "$mod" -c "$AKAIDOO_CONF" --shrink=hard -B 30k \
        -o "$GENERATED/${mod}_context.md" 2>/dev/null || true
done

# Кастомные модули — мягче
akaidoo object_request -c "$AKAIDOO_CONF" --shrink=soft -B 30k \
    -o "$GENERATED/object_request_context.md" 2>/dev/null || true

echo "=== Шаг 4: Обновить индекс ==="
python scripts/rebuild_knowledge_index.py \
    --docs-dir "$KNOWLEDGE_DIR/docs" \
    --generated-dir "$GENERATED" \
    --output "$KNOWLEDGE_DIR/index.json"

echo "=== Готово ==="
echo "Перезапустите Odoo для применения: docker compose restart odoo"
```

---

## 5. Блок 2: Screenshot capture + Vision

### 5.1. Frontend: захват экрана

**Библиотека:** `html2canvas` — рендерит DOM текущей страницы в canvas, затем в JPEG data URL (base64).

**Триггеры** (определяются на frontend перед отправкой):

```javascript
// static/src/js/screenshot_trigger.js

const SCREEN_TRIGGERS_RU = [
    'на экране', 'на моём экране', 'на моем экране',
    'что я вижу', 'что вижу', 'смотри на экран',
    'посмотри на экран', 'глянь на экран',
    'в открытой вкладке', 'на открытой странице',
    'на этой странице', 'на текущем экране',
    'что тут', 'что здесь', 'помоги с тем что открыто',
    'покажу экран', 'вот мой экран', 'скриншот',
];

export function needsScreenshot(message) {
    const lower = message.toLowerCase();
    return SCREEN_TRIGGERS_RU.some(trigger => lower.includes(trigger));
}
```

**Захват скриншота:**

```javascript
// static/src/js/ai_chat_service.js — дополнение

async function captureScreen() {
    // html2canvas подключается через CDN или бандл
    const { default: html2canvas } = await import(
        '/ai_assistant/static/lib/html2canvas.min.js'
    );

    // Скрываем виджет чата перед скриншотом
    const chatWidget = document.querySelector('.o_ai_chat_panel');
    if (chatWidget) chatWidget.style.display = 'none';

    try {
        const canvas = await html2canvas(document.body, {
            scale: 0.7,           // 70% масштаб — баланс качества и размера
            useCORS: true,
            logging: false,
            width: window.innerWidth,
            height: window.innerHeight,
        });

        // Конвертируем в JPEG для экономии размера
        return canvas.toDataURL('image/jpeg', 0.8);
        // ~200-400 KB для типичного экрана Odoo
    } finally {
        if (chatWidget) chatWidget.style.display = '';
    }
}
```

**Отправка с изображением:**

```javascript
// Изменённый метод sendMessage в ai_chat_service.js

async function sendMessage(message, history) {
    const context = collectContext();
    const payload = { message, context, history };

    if (needsScreenshot(message)) {
        try {
            payload.screenshot = await captureScreen();
        } catch (e) {
            console.warn('Screenshot capture failed:', e);
            // Продолжаем без скриншота
        }
    }

    const response = await fetch('/ai_assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: payload }),
    });

    return response.json();
}
```

### 5.2. Backend: обработка скриншота

**Controller — расширение payload (псевдокод, в реальности `request.env['ir.config_parameter']`):**

```python
# controllers/chat_controller.py

@http.route('/ai_assistant/chat', type='json', auth='user')
def chat(self, message='', context=None, history=None, screenshot=None):
    # ... существующая валидация ...

    has_screenshot = bool(screenshot and isinstance(screenshot, str)
                         and screenshot.startswith('data:image/'))

    # Выбор модели (реально: request.env['ir.config_parameter'].sudo().get_param())
    if has_screenshot:
        model_key = 'ai_assistant.vision_model'
        image_data = self._parse_screenshot(screenshot)
    else:
        model_key = 'ai_assistant.text_model'
        image_data = None

    # Сборка промпта
    messages = self.prompt_builder.build_messages(
        message, history, resolved_context,
        image_data=image_data,
    )

    # Отправка с нужной моделью
    params = request.env['ir.config_parameter'].sudo()
    result = self.openrouter_client.send_chat(
        messages,
        model_override=params.get_param(model_key),
    )

    return result
```

**Лимит размера скриншота:**

```python
MAX_SCREENSHOT_SIZE = 500_000  # ~500 KB base64

def _parse_screenshot(self, data_url):
    """Извлечь base64 из data URL, проверить размер."""
    try:
        # data:image/jpeg;base64,/9j/4AAQ...
        header, b64data = data_url.split(',', 1)
        if len(b64data) > MAX_SCREENSHOT_SIZE:
            _logger.warning('Screenshot too large, skipping')
            return None
        media_type = header.split(':')[1].split(';')[0]
        return {'media_type': media_type, 'data': b64data}
    except Exception:
        return None
```

### 5.3. OpenRouter client — поддержка multimodal

```python
# services/openrouter_client.py — расширение send_chat

def send_chat(self, messages, max_tokens=1500, model_override=None):
    """
    Отправить сообщения в OpenRouter.
    model_override: если передан — используется вместо дефолтного.
    messages: может содержать content с type image_url (vision).
    """
    model = model_override or self._model
    # ... остальное без изменений, model подставляется в payload ...
```

### 5.4. Prompt builder — vision mode

> **⚠️ Ломающее изменение:** текущая сигнатура `build_messages(self, system_prompt, history, user_message)` меняется — вместо готового `system_prompt` теперь принимает `context` и строит промпт внутри. Это затрагивает `chat_controller.py` и все тесты `prompt_builder`. Детали миграции — в AIA-016.

```python
# services/prompt_builder.py — дополнение

def build_messages(self, message, history, context,
                   image_data=None):
    """
    Если image_data не None — формируем multimodal сообщение:
    content становится массивом [{type: text}, {type: image_url}]
    """
    system = self._build_system(context)
    msgs = [{'role': 'system', 'content': system}]

    # History
    for h in (history or [])[-self._max_history:]:
        msgs.append({'role': h['role'], 'content': h['content']})

    # User message
    if image_data:
        user_content = [
            {'type': 'text', 'text': self._build_vision_prompt(message, context)},
            {
                'type': 'image_url',
                'image_url': {
                    'url': f"data:{image_data['media_type']};base64,{image_data['data']}",
                },
            },
        ]
    else:
        user_content = message

    msgs.append({'role': 'user', 'content': user_content})
    return msgs

def _build_vision_prompt(self, message, context):
    """Специальный промпт для анализа скриншота."""
    return (
        f"Пользователь прислал скриншот экрана Odoo 19.\n"
        f"Текущий контекст: модуль={context.get('module', '?')}, "
        f"модель={context.get('model', '?')}, "
        f"экран={context.get('view_type', '?')}.\n"
        f"Язык интерфейса: {context.get('lang', 'ru_RU')}.\n\n"
        f"Вопрос пользователя: {message}\n\n"
        f"Проанализируй скриншот и ответь, опираясь на то, "
        f"что РЕАЛЬНО видно на экране. Называй кнопки и меню "
        f"ТОЧНО так, как они отображены на скриншоте."
    )
```

---

## 6. Блок 3: System prompt v2

### Обновлённый базовый промпт

```
Ты — встроенный AI-консультант по Odoo 19. Язык ответа: русский.

ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе предоставленной документации и контекста.
2. Если тебе передан скриншот — анализируй РЕАЛЬНЫЙ экран пользователя.
   Называй кнопки, поля и меню ТОЧНО как они отображены на скриншоте.
3. Если скриншота нет — используй названия из term_mapping и knowledge base.
4. НИКОГДА не выдумывай кнопки, поля или пути меню. Если не уверен — скажи.
5. В Odoo 19 НЕТ кнопок «Сохранить» и «Редактировать» — формы
   сохраняются автоматически, редактирование начинается сразу.
6. Кнопка создания новой записи называется «Новое», НЕ «Создать».
7. Формат ответа: короткие пошаговые инструкции.
8. Если функционал недоступен — предложи, где его включить в Настройках.

КОНТЕКСТ ЭКРАНА:
{context_block}

ДОКУМЕНТАЦИЯ:
{knowledge_block}

МАППИНГ ТЕРМИНОВ (приоритет при отсутствии скриншота):
{term_mapping_block}
```

---

## 7. Безопасность

### Скриншот — что нужно учитывать

| Риск | Мера |
|------|------|
| Персональные данные на экране | Скриншот НЕ логируется, НЕ сохраняется на диск. Передаётся в OpenRouter и всё |
| Размер payload | Лимит 500 KB на base64, JPEG quality 0.8 |
| Частые vision-запросы (дорого) | Rate limit: max 5 vision-запросов в минуту на пользователя |
| Виджет чата попадает на скриншот | Скрывается перед захватом (display: none) |

### Скриншоты в истории чата

| Риск | Мера |
|------|------|
| Скриншот в sessionStorage (~200-400 KB на сообщение) | НЕ сохранять скриншот в историю — хранить только текстовый маркер `[screenshot attached]` |
| Переотправка скриншота в следующих запросах | Передавать скриншот ТОЛЬКО в текущем запросе, из history исключать |
| Лимит sessionStorage (~5 MB) | При хранении скриншотов в истории лимит достигается за 10–15 vision-запросов |

### Совместимость с response_guard

`response_guard.py` (26 тестов) фильтрует ответы модели. Vision-модель может возвращать ответ в ином формате — нужна проверка совместимости. Если формат ответа vision-модели отличается — адаптировать guard (см. AIA-016).

### Whitelist полей payload (расширенный)

```python
PAYLOAD_WHITELIST = {
    'message': str,       # max 2000 chars
    'context': dict,      # фильтруется через ContextResolver
    'history': list,      # max 12 записей, БЕЗ скриншотов
    'screenshot': str,    # max 500 KB base64, только data:image/*
}
```

---

## 8. Этапы реализации

### Этап V2-1: Knowledge base v2 (RST + term_mapping)

| Задача | ID | Описание |
|--------|----|----------|
| Скрипт конвертации RST | AIA-012 | `scripts/convert_rst_to_knowledge.py` — парсинг RST, извлечение шагов/меню/кнопок, применение term_mapping |
| term_mapping.json | AIA-013 | Создать маппинг EN→RU для Odoo 19; верифицировать по живому UI |
| knowledge_provider_v2 | AIA-014 | Трёхслойный провайдер: RST docs + akaidoo + term_mapping |
| Скрипт обновления | AIA-015 | `scripts/update_knowledge_v2.sh` — полная пересборка knowledge base |
| Обновить prompt_builder | AIA-016 | Вставлять term_mapping в системный промпт; новый system prompt v2 |

**Результат:** Ассистент отвечает на основе актуальной документации Odoo 19 с правильными русскими терминами.

### Этап V2-2: Двухуровневая модель

| Задача | ID | Описание |
|--------|----|----------|
| Два поля модели в Settings | AIA-017 | `ai_assistant_text_model` + `ai_assistant_vision_model` в конфиге |
| openrouter_client_v2 | AIA-018 | Параметр `model_override` в `send_chat()` |
| Обновить Settings UI | AIA-019 | Два поля выбора модели в настройках |

**Результат:** Администратор выбирает отдельно текстовую и vision модель.

### Этап V2-3: Screenshot capture + Vision

| Задача | ID | Описание |
|--------|----|----------|
| Подключить html2canvas | AIA-020 | Добавить библиотеку в assets модуля |
| screenshot_trigger.js | AIA-021 | Детекция триггерных фраз в сообщении |
| captureScreen() | AIA-022 | Захват DOM → JPEG base64, скрытие виджета чата |
| Расширить payload | AIA-023 | Передача screenshot в /ai_assistant/chat |
| Backend: парсинг скриншота | AIA-024 | Валидация, лимит размера, извлечение base64 |
| prompt_builder vision mode | AIA-025 | Multimodal content (text + image_url), vision prompt |
| Rate limiter для vision | AIA-026 | Max 5 vision-запросов/мин на пользователя |

> **Примечание:** `chat_controller.py` изменяется в задачах AIA-016 (провайдер v2), AIA-018 (model_override), AIA-024 (screenshot). Изменения наращиваются последовательно: V2-1 → V2-2 → V2-3.

**Результат:** Пользователь пишет «что у меня на экране?» → ассистент делает скриншот, отправляет в vision-модель, отвечает на основе реального UI.

### Этап V2-4: Тестирование

| Задача | ID | Описание |
|--------|----|----------|
| Тесты knowledge_provider_v2 | AIA-027 | Unit-тесты для RST-поиска, term_mapping, akaidoo |
| Тесты vision pipeline | AIA-028 | Mock-тесты для screenshot → multimodal → response |
| Пилотные сценарии | AIA-029 | Ручной прогон: 10 сценариев текстовых + 5 со скриншотом |
| Аудит терминов | AIA-030 | Пройти все экраны Odoo 19 и верифицировать term_mapping.json |

---

## 9. Оценка стоимости (на пользователя)

### Текстовый режим (Gemini 2.0 Flash)

Средний запрос: ~6000 input tokens (system prompt ~500 + docs_snippets ~2500 + term_mapping ~300 + tech_context ~1500 + history ~1200) + ~500 output tokens.

| Запросов/день | Стоимость/день |
|---------------|----------------|
| 20 | ~$0.012 |
| 50 | ~$0.030 |
| 100 | ~$0.060 |

### Vision режим (GPT-4o)

Средний запрос: ~6000 text tokens + ~1000 image tokens input, ~500 output tokens.

| Vision-запросов/день | Стоимость/день |
|----------------------|----------------|
| 5 | ~$0.12 |
| 10 | ~$0.25 |
| 20 | ~$0.50 |

### Итого (типичное использование: 50 текст + 5 vision в день)

**~$0.15/день ≈ $4.5/месяц на пользователя**

---

## 10. Порядок реализации

```
Неделя 1:  AIA-013 (term_mapping) — стартовая задача, без зависимостей
           AIA-017 (два поля модели) — параллельно, нет зависимостей
           AIA-013 → AIA-012 (RST-конвертер) — после готовности term_mapping

Неделя 2:  AIA-012 → AIA-014 (knowledge_provider_v2) + AIA-015 (скрипт обновления)
           AIA-014 → AIA-016 (prompt_builder v2 + system prompt)
           AIA-017 → AIA-018..019 (двухуровневая модель)

Неделя 3:  AIA-020 + AIA-021 (html2canvas + trigger) — параллельно
           AIA-020 → AIA-022 (captureScreen)
           AIA-021 + AIA-022 → AIA-023 (payload + OWL-виджет)
           AIA-018 + AIA-023 → AIA-024 (backend парсинг)
           AIA-024 → AIA-025 (vision prompt) + AIA-026 (rate limiter)

Неделя 4:  AIA-027 (тесты knowledge) + AIA-028 (тесты vision)
           AIA-029 (пилотные сценарии) + AIA-030 (аудит term_mapping)
```

---

## 11. Критерии готовности v2

- [ ] Ассистент отвечает на основе RST-документации Odoo 19, не на ручных JSON
- [ ] Термины кнопок/меню соответствуют реальному UI (ru_RU)
- [ ] term_mapping.json содержит ≥80 верифицированных маппингов
- [ ] При триггерных фразах — захват скриншота и ответ на основе изображения
- [ ] Vision-запросы уходят на мощную модель, текстовые — на дешёвую
- [ ] Администратор может менять обе модели в Settings
- [ ] Скриншоты не логируются, не сохраняются, не попадают в историю чата
- [ ] Rate limit на vision-запросы работает (5/мин на пользователя)
- [ ] response_guard совместим с ответами vision-модели
- [ ] Knowledge base обновляется скриптом за одну команду
- [ ] Все unit-тесты проходят (≥40 новых + адаптированных тестов)
- [ ] ≥12 из 15 пилотных сценариев оценены как ✅
- [ ] Модуль обновляется без ошибок (`-u ai_assistant`)
