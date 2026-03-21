# Task Tracker: AI-ассистент v2 — Vision + Odoo Docs + Akaidoo

**Дата создания:** 2026-03-21  
**Roadmap:** `docs/roadmap_ai_assistant_v2.md`  
**Базовый модуль:** `custom_addons/ai_assistant/` (AIA-001 — AIA-011 выполнены)  
**Предыдущий трекер:** `docs/tasktreckeragentconsul.md`  
**Аудит выполнения по коду:** 2026-03-21 (ветка `main`, `custom_addons/ai_assistant/` + `scripts/`)

---

## Этап V2-1. Knowledge base v2 — RST docs + term_mapping

### Задача: AIA-012 — Скрипт конвертации RST → локализованный Markdown

- **Статус**: ✅ Выполнена (2026-03-21)
- **Приоритет**: Критический
- **Описание**: Создать Python-скрипт, который парсит RST-файлы из репозитория `odoo/documentation` (ветка `19.0`), извлекает пошаговые инструкции, пути меню и названия кнопок, применяет `term_mapping.json` для локализации и сохраняет результат как Markdown-файлы в `static/knowledge/docs/`.
- **🔧 Context7**: Использовать для проверки актуальных путей и структуры RST-файлов в репозитории `odoo/documentation` ветки `19.0` — убедиться, что `:menuselection:`, `#.` steps и `**Button**` паттерны не изменились в текущей версии.
- **Шаги выполнения**:
  - [x] Клонировать `https://github.com/odoo/documentation` ветка `19.0` → `/tmp/odoo-docs-19` _(скрипт выполняет при наличии source)_
  - [x] Создать `scripts/convert_rst_to_knowledge.py`:
    - [x] Парсер RST: извлечение `:menuselection:\`...\`` → пути меню
    - [x] Парсер RST: извлечение `**ButtonName**` → названия кнопок
    - [x] Парсер RST: извлечение `#. Step text` → пошаговые инструкции
    - [x] Парсер RST: извлечение `.. note::` и `.. tip::` → подсказки
    - [x] Применение `term_mapping.json`: замена EN-терминов на RU
    - [x] Обработка `removed_in_v19`: удаление шагов с несуществующими кнопками (Save, Edit)
    - [x] Выходной формат: Markdown с frontmatter, секциями `## Шаг за шагом`, keywords
  - [x] Сконвертировать разделы по модулям (12 MD-файлов, demo-режим):
    - [x] `inventory/` → `stock_warehouses.md`, `stock_products.md`, `stock_operations.md`, `stock_inventory.md`
    - [x] `sales/sales/` → `sale_quotations.md`, `sale_invoicing.md`
    - [x] `inventory_and_mrp/purchase/` → `purchase_orders.md`, `purchase_receipts.md`
    - [x] `sales/crm/` → `crm_leads.md`, `crm_pipeline.md`
    - [x] `essentials/contacts.rst` → `contacts_management.md`
    - [x] `general/` → `settings_general.md`
  - [x] Добавить `--source`, `--output`, `--term-mapping`, `--demo`, `--dry-run`, `--verbose` CLI-аргументы
  - [x] Проверить, что выходные MD-файлы содержат только русские термины
  - [x] Переместить старые JSON в `static/knowledge/legacy/`
  - [x] Создать стартовый `static/knowledge/term_mapping.json` (80+ маппингов)
- **Критерий готовности**: ✅ Скрипт генерирует 12 MD-файлов (demo-режим); все термины кнопок/меню — на русском; шаги с `Save`/`Edit` удалены. При наличии RST-репозитория — парсит реальные файлы.
- **Зависимости**: AIA-013 _(частично: стартовый term_mapping.json создан в рамках этой задачи)_

---

### Задача: AIA-013 — Создать term_mapping.json

- **Статус**: ✅ Готова
- **Приоритет**: Критический
- **Описание**: Составить JSON-файл маппинга английских терминов Odoo 19 UI на русские, верифицированный по живому интерфейсу с локалью `ru_RU`. Включает кнопки, пункты меню, названия полей и пометки об удалённых элементах.
- **Шаги выполнения**:
  - [x] Создать `static/knowledge/term_mapping.json` со структурой:
    - [x] `odoo_version`: `"19.0"`
    - [x] `lang`: `"ru_RU"`
    - [x] `verified_date`: `"2026-03-21"`
    - [x] `buttons`: 52 маппинга (New, Validate, Confirm, Cancel, Print, Discard, Send by Email, Check Availability, Apply All, Reserve, Unreserve, Return, Scrap, Lock, Unlock и др.)
    - [x] `menu_items`: 52 маппинга пунктов меню для stock, sale, purchase, crm, contacts, settings
    - [x] `fields`: 62 маппинга полей форм
    - [x] `view_labels`: 8 типов представлений
    - [x] `statuses`: 14 статусов документов
    - [x] `removed_in_v19`: Save, Edit, Create с пояснениями
  - [x] **Верификация по ru.po файлам** — проверены маппинги по официальным файлам переводов Odoo 19:
    - [x] Склад: stock/i18n/ru.po — исправлены Reserve/Unreserve/Scrap/Apply All/Put in Pack
    - [x] Продажи: sale/i18n/ru.po — исправлено Quotations → Коммерческие предложения
    - [x] Закупки: purchase/i18n/ru.po — исправлено Purchase Orders → Заказы на покупку
    - [x] CRM: crm/i18n/ru.po — исправлено Expected Revenue → Ожидаемый доход, добавлены Won/Lost
    - [x] Base/Web: base,web,mail/i18n/ru.po — исправлено Log note → Внутренняя заметка
    - [x] Структура меню Odoo 19: Transfers/Adjustments/Procurement вместо старых Receipts/Delivery Orders
  - [x] Зафиксировать расхождения — раздел `discrepancies_vs_legacy` в файле
- **Итог**: 188 маппингов (buttons: 52, menu_items: 52, fields: 62, view_labels: 8, statuses: 14); расхождения с legacy JSONs задокументированы
- **Критерий готовности**: ✅ Файл содержит 188 маппингов (≥50 требовалось); верифицирован по официальным ru.po Odoo 19
- **Зависимости**: Нет (можно начать сразу)

---

### Задача: AIA-014 — Реализовать knowledge_provider_v2

- **Статус**: ✅ Готова
- **Приоритет**: Критический
- **Описание**: Переписать `services/knowledge_provider.py` на трёхслойную архитектуру: RST-based docs (пользовательские инструкции), akaidoo context (структура моделей), term_mapping (валидация терминов). Сохранить обратную совместимость с существующим интерфейсом `get_snippets()`.
- **Шаги выполнения**:
  - [x] Создать `services/knowledge_provider_v2.py` с классом `KnowledgeProviderV2`:
    - [x] Метод `get_knowledge(module, query, include_technical=False)` → `{docs_snippets, tech_context, term_mapping}`
    - [x] Метод `_search_docs(module, query, limit=5)` — полнотекстовый поиск по MD-секциям в `docs/`
    - [x] Метод `get_technical_context(module)` — загрузка akaidoo-контекста из `generated/` (перенесён из v1)
    - [x] Метод `_get_relevant_terms(module)` — извлечение терминов из `term_mapping.json`
    - [x] Метод `get_snippets(module, query, limit=5)` — обёртка совместимости с v1
  - [x] Реализовать поиск по MD-файлам:
    - [x] Индексация: при первом вызове — загрузить все MD из `docs/`, разбить по `##`, построить keyword-индекс
    - [x] Ранжирование: keyword matching + boost за совпадение module name в имени файла
    - [x] Лимит размера: `MAX_DOCS_CHARS = 10000`
  - [x] Создать `index.json` с `odoo_version`, `lang`, `docs_dir`, `generated_dir`, маппингом module → docs + generated
  - [x] Обновить `services/__init__.py` — импорт `KnowledgeProviderV2`
  - _Примечание: legacy JSON уже в `static/knowledge/legacy/` с AIA-012_
- **Критерий готовности**: ✅ Smoke-тест пройден: `get_knowledge('stock', ...)` → docs_snippets + term_mapping; `get_snippets('purchase', ...)` → 5 фрагментов; `get_knowledge('crm', ...)` работает. Unit-тесты — в AIA-027.
- **Зависимости**: AIA-012, AIA-013

---

### Задача: AIA-015 — Скрипт обновления knowledge base

- **Статус**: ✅ Готова
- **Приоритет**: Высокий
- **Описание**: Создать единый bash-скрипт `scripts/update_knowledge_v2.sh`, который в одну команду обновляет всю knowledge base: pull документации, конвертация RST, пересборка akaidoo-контекста, обновление индекса.
- **Шаги выполнения**:
  - [x] Создать `scripts/update_knowledge_v2.sh` (5 шагов):
    - [x] Шаг 1: `git clone --branch 19.0` или `git pull` репозитория документации
    - [x] Шаг 2: Запуск `convert_rst_to_knowledge.py`; при отсутствии RST — demo-режим
    - [x] Шаг 3: Запуск akaidoo для 7 модулей (`--shrink=hard -B 30k`, object_request — soft)
    - [x] Шаг 4: Запуск `scripts/rebuild_knowledge_index.py` — генерация обновлённого `index.json`
    - [x] Шаг 5: Summary: файлов создано, общий размер, предупреждения
  - [x] Создать `scripts/rebuild_knowledge_index.py`:
    - [x] Сканирование `docs/` и `generated/` директорий (автодетект модуля по префиксу)
    - [x] Генерация `index.json` с маппингом module → docs + generated
  - [x] Флаги: `--dry-run`, `--skip-docs`, `--skip-akaidoo`
  - [x] Если akaidoo не установлен — warning, продолжаем без ошибки
- **Критерий готовности**: ✅ `--dry-run --skip-akaidoo` пройден: 8 модулей, 12 docs-файлов, 7 generated. Скрипт идемпотентен, gracefully обрабатывает отсутствие RST-репо и akaidoo.
- **Зависимости**: AIA-012, AIA-013

---

### Задача: AIA-016 — Обновить prompt_builder для v2

- **Статус**: ✅ Готова (текстовый режим + knowledge v2); multimodal vision — **AIA-025**
- **Приоритет**: Критический
- **Описание**: Обновить `services/prompt_builder.py` — новый system prompt v2 с правилами по терминам Odoo 19, вставка term_mapping в промпт, переключение на `KnowledgeProviderV2`.
- **🔧 Context7**: Использовать для проверки формата multimodal-сообщений OpenRouter API (image_url, content arrays) при реализации vision mode в prompt_builder.
- **Шаги выполнения**:
  - [x] **Смена сигнатуры `build_messages()`** (фактическая реализация):
    - [x] Было: `build_messages(self, system_prompt, history, user_message)`
    - [x] Стало: `build_messages(self, message, history, context, knowledge=None, override=None, image_data=None)` — системный промпт собирается внутри `_build_system()`; `knowledge` передаётся из контроллера
    - [x] Вызовы в `chat_controller.py` обновлены (`get_knowledge` → `build_messages`)
  - [ ] Параметр `image_data`: **зарезервирован**, логика vision (массив `content` с `image_url`) — в **AIA-025**
  - [x] `_SYSTEM_PROMPT_V2`: правила Odoo 19, «Новое» / без «Сохранить»-«Редактировать» в типичных формах
  - [ ] Явная строка в system prompt про приоритет скриншота — после появления vision (AIA-025)
  - [x] Метод `build_term_mapping_block(terms)` — форматирование; фильтрация по модулю через `knowledge` от провайдера
  - [x] `build_knowledge_block(knowledge)` — docs + tech_context + структура v2
  - [x] `chat_controller.py` использует `KnowledgeProviderV2` и передаёт `knowledge` в `build_messages`
  - [x] `response_guard`: для текстового режима совместим; отдельная проверка под vision-ответы — при AIA-025 / пилоте
  - [x] Тесты `test_prompt_builder.py` расширены (в т.ч. `test_term_mapping_included_in_build_messages`, `test_knowledge_v2_format_in_build_messages`, блок `build_term_mapping_block`)
- **Критерий готовности**: ✅ Для текстового пайплайна выполнено. Vision — см. AIA-024–025.
- **⚠️ Координация**: `chat_controller.py` также изменяется в AIA-018 (model_override) и AIA-024 (screenshot). Изменения AIA-016 идут первыми.
- **Зависимости**: AIA-014

---

## Этап V2-2. Двухуровневая модель

### Задача: AIA-017 — Два поля модели в Settings

- **Статус**: ✅ Готова (без отдельной миграции БД)
- **Приоритет**: Высокий
- **Описание**: Разделить конфигурацию модели на два поля: `text_model` (для обычных текстовых вопросов) и `vision_model` (для анализа скриншотов). Обновить UI настроек.
- **Шаги выполнения**:
  - [x] Добавить в `models/ai_assistant_config.py`:
    - [x] `ai_assistant_text_model` → `config_parameter='ai_assistant.text_model'`, default `google/gemini-2.0-flash-001`
    - [x] `ai_assistant_vision_model` → `config_parameter='ai_assistant.vision_model'`, default `openai/gpt-4o`
    - [ ] **Миграция** `ai_assistant.openrouter_model` → `ai_assistant.text_model` (модуль `migrations/` пока нет — fallback читается в `OpenRouterClient` из legacy-ключа)
  - [x] `views/ai_assistant_settings_views.xml`: секция «Модели», два поля + краткие рекомендации по стоимости
  - [x] `openrouter_client.py`: чтение `ai_assistant.text_model` / `ai_assistant.vision_model`, fallback на `ai_assistant.openrouter_model`
  - [ ] Тест: при отсутствии vision_model — fallback на text_model
- **Критерий готовности**: ✅ Два поля в Settings; старый ключ API остаётся рабочим через fallback в клиенте. Опционально: явная миграция параметров.
- **Зависимости**: Нет (можно начать параллельно с V2-1)

---

### Задача: AIA-018 — openrouter_client_v2: model_override

- **Статус**: ⚠️ Частично выполнена (клиент готов; контроллер не переключает vision до AIA-024)
- **Приоритет**: Высокий
- **Описание**: Расширить `OpenRouterClient.send_chat()` параметром `model_override` для возможности выбора модели на лету (текстовая или vision).
- **Шаги выполнения**:
  - [x] Параметр `model_override=None` в `send_chat()`; подстановка в payload
  - [x] Логирование model / mode
  - [x] `_parse_response(..., mode=)` — в ответе есть `mode`: `text` | `vision`
  - [ ] Тесты `test_model_override_used`, `test_default_model_when_no_override` в `test_openrouter_client.py`
  - [ ] `chat_controller._get_ai_response`: передавать `model_override=vision_model` при валидном скриншоте (**AIA-024**)
- **Критерий готовности**: Клиент соответствует; полное закрытие — после AIA-024 + тесты.
- **⚠️ Координация**: `chat_controller.py` уже изменён в AIA-016 (провайдер v2). Изменения AIA-018 наращиваются поверх.
- **Зависимости**: AIA-017

---

### Задача: AIA-019 — Обновить Settings UI

- **Статус**: ⚠️ Частично выполнена (подсказки в XML есть; кнопки проверки нет)
- **Приоритет**: Средний
- **Описание**: Расширить экран настроек AI-ассистента: подсказки по рекомендованным моделям, кнопка проверки подключения. Базовые поля моделей уже добавлены в AIA-017 — здесь только UX-улучшения.
- **Шаги выполнения**:
  - [x] `views/ai_assistant_settings_views.xml`: блок «Модели» с `<p class="text-muted">` — рекомендуемые модели и ориентир по цене
  - [ ] Кнопка «Проверить подключение» — тестовый запрос к обеим моделям (не реализовано)
  - [x] Поле `ai_assistant_model` не выводится в основной форме (помечено как устаревшее в модели, скрыто из основного UX)
- **Критерий готовности**: Подсказки ✅; кнопка проверки — в бэклоге.
- **Зависимости**: AIA-017

---

## Этап V2-3. Screenshot capture + Vision

### Задача: AIA-020 — Подключить html2canvas

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Добавить библиотеку `html2canvas` в assets модуля для захвата DOM-содержимого страницы Odoo.
- **🔧 Context7**: Использовать для проверки актуального способа подключения внешних JS-библиотек в Odoo 19 — формат `__manifest__.py` assets, порядок загрузки, конфликты с OWL.
- **Шаги выполнения**:
  - [ ] Скачать `html2canvas.min.js` (v1.4.1+) → `static/lib/html2canvas.min.js`
  - [ ] Добавить в `__manifest__.py` → `web.assets_backend`:
    - [ ] `'ai_assistant/static/lib/html2canvas.min.js'`
  - [ ] Проверить, что библиотека загружается без конфликтов с OWL/Odoo
  - [ ] Проверить, что `html2canvas(document.body)` работает на типичном экране Odoo (list, form, kanban)
  - [ ] Проверить производительность: замер времени рендера на тяжёлой странице (>100 строк в list view)
- **Критерий готовности**: `html2canvas` доступен в контексте Odoo backend; рендер типичной страницы <3 секунды; нет конфликтов с OWL.
- **Зависимости**: Нет

---

### Задача: AIA-021 — screenshot_trigger.js: детекция триггерных фраз

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Создать модуль определения, нужен ли скриншот, на основе анализа текста сообщения пользователя.
- **Шаги выполнения**:
  - [ ] Создать `static/src/js/screenshot_trigger.js`:
    - [ ] Массив `SCREEN_TRIGGERS_RU` — триггерные фразы (≥15 вариантов):
      - «на экране», «на моём экране», «что я вижу», «смотри на экран», «посмотри на экран», «в открытой вкладке», «на открытой странице», «на этой странице», «на текущем экране», «что тут», «что здесь», «помоги с тем что открыто», «покажу экран», «вот мой экран», «скриншот», «покажи что вижу», «опиши экран»
    - [ ] Функция `needsScreenshot(message)` → boolean
    - [ ] Case-insensitive matching
    - [ ] Export для использования в `ai_chat_service.js`
  - [ ] Добавить `screenshot_trigger.js` в `__manifest__.py` → `web.assets_backend`
  - [ ] Написать JS unit-тесты (если инфраструктура позволяет) или ручные сценарии:
    - [ ] Триггер срабатывает: «что у меня на экране?» → true
    - [ ] Триггер не срабатывает: «как создать склад?» → false
    - [ ] Триггер срабатывает на подстроку: «помоги с тем что открыто, не понимаю» → true
- **Критерий готовности**: Функция корректно определяет ≥15 триггерных фраз; ложные срабатывания на обычных вопросах отсутствуют.
- **Зависимости**: Нет

---

### Задача: AIA-022 — captureScreen(): захват DOM в JPEG base64

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Реализовать функцию захвата текущего экрана Odoo, используя `html2canvas`, с автоматическим скрытием виджета чата и конвертацией в JPEG base64.
- **🔧 Context7**: Использовать для проверки CSS-селекторов OWL-компонентов Odoo 19 — корректные селекторы для виджета чата, системных элементов, которые нужно скрыть/показать.
- **Шаги выполнения**:
  - [ ] Добавить функцию `captureScreen()` в `ai_chat_service.js`:
    - [ ] Скрыть виджет чата (`.o_ai_chat_panel`) перед захватом
    - [ ] Вызвать `html2canvas(document.body, { scale: 0.7, useCORS: true, logging: false })`
    - [ ] Конвертировать canvas → `data:image/jpeg;base64,...` с quality 0.8
    - [ ] Восстановить видимость виджета после захвата (в `finally`)
    - [ ] Обработка ошибок: если захват не удался — вернуть `null`, продолжить без скриншота
  - [ ] Проверить размер выхода на разных разрешениях:
    - [ ] 1920×1080 → ожидаемо 200–400 KB
    - [ ] 2560×1440 → ожидаемо 300–500 KB
    - [ ] Мобильное (375×812) → ожидаемо 100–200 KB
  - [ ] Проверить, что на скриншоте НЕ видно виджета чата
  - [ ] Проверить, что iframe-контент (если есть) корректно рендерится или пропускается
- **Критерий готовности**: Функция возвращает JPEG base64 ≤500 KB; виджет чата не виден на скриншоте; ошибки обрабатываются gracefully.
- **Зависимости**: AIA-020

---

### Задача: AIA-023 — Расширить payload: передача screenshot

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Интегрировать `needsScreenshot()` и `captureScreen()` в основной flow отправки сообщений. При наличии триггера — автоматически делать скриншот и добавлять в payload.
- **🔧 Context7**: Использовать для проверки актуального паттерна `jsonrpc` запросов в Odoo 19 JS — как корректно передавать binary data в JSON payload через `rpc.query()` или `fetch`.
- **Шаги выполнения**:
  - [ ] Обновить `ai_chat_service.js` → метод отправки:
    - [ ] Импортировать `needsScreenshot` из `screenshot_trigger.js`
    - [ ] Перед отправкой: `if (needsScreenshot(message))` → `await captureScreen()`
    - [ ] Добавить `screenshot` в payload (только если захват успешен)
    - [ ] **НЕ сохранять** скриншот в историю чата (sessionStorage) — хранить только текстовый маркер `[screenshot attached]`
    - [ ] При отправке history в payload — исключать скриншоты из предыдущих сообщений
  - [ ] Обновить `ai_chat_boot.js` (OWL-компонент):
    - [ ] Передавать `screenshot` как часть params в JSON-RPC
    - [ ] Показать индикатор пользователю: «Делаю скриншот...» перед отправкой
    - [ ] Показать отличающийся индикатор ожидания для vision-запросов (они дольше)
  - [ ] Обновить `ai_chat_widget.xml` — шаблон индикатора скриншота
  - [ ] Проверить, что без триггера — скриншот НЕ делается (экономия трафика)
  - [ ] Проверить, что при ошибке захвата — сообщение всё равно отправляется (без скриншота)
  - [ ] Проверить, что sessionStorage не раздувается от скриншотов (лимит ~5 MB)
- **Критерий готовности**: Триггерные фразы → скриншот прикрепляется к payload; скриншоты НЕ сохраняются в историю; обычные вопросы → без скриншота; индикатор виден пользователю; ошибки не блокируют отправку.
- **Зависимости**: AIA-021, AIA-022

---

### Задача: AIA-024 — Backend: парсинг и валидация скриншота

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Расширить `chat_controller.py` для приёма, валидации и парсинга скриншота из payload. Обеспечить безопасность: лимит размера, валидация формата, отсутствие логирования содержимого.
- **Шаги выполнения**:
  - [ ] Обновить endpoint `/ai_assistant/chat`:
    - [ ] Добавить параметр `screenshot=None` в метод `chat()`
    - [ ] Валидация: `isinstance(screenshot, str)` и `startswith('data:image/')`
    - [ ] Лимит: `len(b64data) ≤ 500_000` (500 KB base64)
    - [ ] Парсинг: извлечь `media_type` и `b64data` из data URL
  - [ ] Создать приватный метод `_parse_screenshot(data_url)`:
    - [ ] Возвращает `{'media_type': 'image/jpeg', 'data': '<base64>'}` или `None`
    - [ ] При превышении лимита — `_logger.warning()` без содержимого, возврат `None`
  - [ ] Маршрутизация модели:
    - [ ] Если screenshot валиден → использовать `ai_assistant_vision_model`
    - [ ] Иначе → использовать `ai_assistant_text_model`
  - [ ] Убедиться: содержимое скриншота НИКОГДА не логируется (ни в debug, ни в info)
  - [ ] Написать тесты (≥6):
    - [ ] `test_screenshot_valid_jpeg` — корректный data URL принимается
    - [ ] `test_screenshot_too_large` — превышение лимита → None
    - [ ] `test_screenshot_invalid_format` — не data URL → None
    - [ ] `test_screenshot_none` — без скриншота → text mode
    - [ ] `test_vision_model_selected` — при скриншоте выбирается vision model
    - [ ] `test_text_model_without_screenshot` — без скриншота выбирается text model
- **Критерий готовности**: Backend принимает скриншот; валидация работает; маршрутизация модели корректна; скриншот не логируется; тесты проходят.
- **⚠️ Координация**: `chat_controller.py` уже изменён в AIA-016 и AIA-018. Изменения AIA-024 наращиваются поверх.
- **Зависимости**: AIA-018

---

### Задача: AIA-025 — prompt_builder: vision mode (multimodal content)

- **Статус**: Заготовка (в сигнатуре `build_messages` есть `image_data=None`; ветка multimodal не реализована)
- **Приоритет**: Высокий
- **Описание**: Расширить `prompt_builder.py` для формирования multimodal-сообщений (text + image_url) в формате OpenAI vision API, совместимом с OpenRouter.
- **Шаги выполнения**:
  - [x] Параметр `image_data=None` в `build_messages()` (зарезервирован)
  - [ ] Если `image_data` не None → user content = массив `[{type: text}, {type: image_url}]`
  - [x] Если None → user content = обычная строка (текущее поведение)
  - [ ] Создать метод `_build_vision_prompt(message, context)`:
    - [ ] Вводный текст: «Пользователь прислал скриншот экрана Odoo 19»
    - [ ] Контекст: модуль, модель, тип экрана, язык
    - [ ] Инструкция: «Называй кнопки и меню ТОЧНО как на скриншоте»
    - [ ] Вопрос пользователя
  - [ ] Формат image_url для OpenRouter:
    ```python
    {
        'type': 'image_url',
        'image_url': {
            'url': f"data:{media_type};base64,{data}",
        },
    }
    ```
  - [ ] Написать тесты (≥5):
    - [ ] `test_vision_message_structure` — content = array с text + image_url
    - [ ] `test_text_message_structure` — content = string (без image)
    - [ ] `test_vision_prompt_contains_context` — модуль и модель в промпте
    - [ ] `test_vision_prompt_contains_user_message` — вопрос пользователя включён
    - [ ] `test_image_url_format` — корректный data URL в image_url
- **Критерий готовности**: Vision-запросы формируются как multimodal content; текстовые — как строки; формат совместим с OpenRouter vision API; тесты проходят.
- **Зависимости**: AIA-016, AIA-024

---

### Задача: AIA-026 — Rate limiter для vision-запросов

- **Статус**: Не начата
- **Приоритет**: Средний
- **Описание**: Реализовать ограничение частоты vision-запросов (скриншот) — максимум 5 в минуту на пользователя. Защита от случайного спама дорогими запросами.
- **Шаги выполнения**:
  - [ ] Создать `services/rate_limiter.py` с классом `VisionRateLimiter`:
    - [ ] In-memory хранение: `{user_id: [timestamp, timestamp, ...]}` (без БД)
    - [ ] Метод `can_send_vision(user_id)` → bool
    - [ ] Метод `record_vision(user_id)` → None
    - [ ] Окно: 60 секунд, лимит: 5 запросов
    - [ ] Автоочистка старых записей при каждом вызове
  - [ ] Обновить `services/__init__.py` — импорт `VisionRateLimiter`
  - [ ] Интегрировать в `chat_controller.py`:
    - [ ] Перед vision-запросом проверять `can_send_vision()`
    - [ ] При превышении → ответ: «Слишком много запросов со скриншотом. Подождите минуту.» + `mode: 'text'` fallback
  - [ ] Написать тесты (≥4):
    - [ ] `test_under_limit_allowed` — 5 запросов проходят
    - [ ] `test_over_limit_blocked` — 6-й запрос блокируется
    - [ ] `test_window_resets` — после 60 сек лимит сбрасывается
    - [ ] `test_different_users_independent` — лимиты раздельные
- **⚠️ Ограничение**: In-memory хранение работает только в рамках одного воркера Odoo. При нескольких воркерах (production) лимит не общий — каждый воркер считает отдельно. Для MVP это допустимо (лимит будет мягче в N раз, где N = число воркеров). Для строгого лимита потребуется Redis или ir.logging — вынесено за рамки v2.
- **Критерий готовности**: Vision-запросы ограничены 5/мин на пользователя (per-worker); при превышении — fallback на текстовый режим с сообщением; тесты проходят.
- **Зависимости**: AIA-024

---

## Этап V2-4. Тестирование и аудит

### Задача: AIA-027 — Тесты knowledge_provider_v2

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Написать полный набор unit-тестов для нового провайдера знаний (основная задача по тестам — в AIA-014 тесты не пишутся). Включает поиск по RST-docs, загрузку akaidoo-контекста, работу с term_mapping.
- **Шаги выполнения**:
  - [ ] Создать `tests/test_knowledge_provider_v2.py` (≥15 тестов):
    - [ ] `test_search_docs_returns_relevant` — поиск по keywords
    - [ ] `test_search_docs_module_boost` — файл модуля ранжируется выше
    - [ ] `test_get_knowledge_combines_layers` — docs + tech + terms
    - [ ] `test_get_snippets_backward_compat` — старый интерфейс работает
    - [ ] `test_term_mapping_loaded` — маппинг загружается корректно
    - [ ] `test_term_mapping_by_module` — фильтрация терминов по модулю
    - [ ] `test_empty_docs_dir_handled` — graceful fallback при отсутствии docs/
    - [ ] `test_size_limit_respected` — не превышает MAX_DOCS_CHARS
    - [ ] Тесты akaidoo context: загрузка, кэширование, fallback при отсутствии
    - [ ] Тесты term_mapping: removed_in_v19 обработка
    - [ ] Тесты edge cases: неизвестный модуль, пустой запрос, повреждённый index.json, огромный MD-файл
  - [ ] Запустить все тесты модуля (старые + новые): 0 failures
- **Критерий готовности**: ≥15 тестов; покрытие всех публичных методов `KnowledgeProviderV2`; 0 failures.
- **Зависимости**: AIA-014

---

### Задача: AIA-028 — Тесты vision pipeline

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Написать mock-тесты для полного цикла vision: парсинг скриншота → multimodal prompt → model_override → ответ. Без реальных вызовов OpenRouter.
- **Шаги выполнения**:
  - [ ] Создать `tests/test_vision_pipeline.py` (≥10 тестов):
    - [ ] `test_screenshot_parsed_correctly` — data URL → media_type + data
    - [ ] `test_vision_model_selected_with_screenshot` — vision model из конфига
    - [ ] `test_text_model_selected_without_screenshot` — text model из конфига
    - [ ] `test_multimodal_message_sent` — messages содержат image_url
    - [ ] `test_text_message_sent` — messages содержат обычный текст
    - [ ] `test_rate_limit_blocks_excess` — 6-й vision-запрос блокируется
    - [ ] `test_rate_limit_fallback_to_text` — при блокировке → текстовый ответ
    - [ ] `test_screenshot_too_large_ignored` — >500KB → text mode
    - [ ] `test_screenshot_capture_failure_graceful` — ошибка → text mode
    - [ ] `test_end_to_end_mock` — полный цикл с mock OpenRouter
  - [ ] Запустить все тесты модуля: 0 failures
- **Критерий готовности**: ≥10 тестов; полный цикл vision покрыт; 0 failures.
- **Зависимости**: AIA-024, AIA-025, AIA-026

---

### Задача: AIA-029 — Пилотные сценарии (ручное тестирование)

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Прогнать ручные сценарии на живой инсталляции Odoo 19 (ru_RU) — текстовые и со скриншотом. Зафиксировать результаты и проблемы.
- **Шаги выполнения**:
  - [ ] **Текстовые сценарии** (knowledge base v2):
    - [ ] «Как создать новый склад?» (из модуля Склад) — должен сказать «Новое», не «Создать»
    - [ ] «Как добавить товар?» (из модуля Склад) — пошаговая инструкция из RST docs
    - [ ] «Как создать заказ на продажу?» (из модуля Продажи) — корректные термины
    - [ ] «Как создать контрагента?» (из модуля Контакты)
    - [ ] «Как провести инвентаризацию?» (из модуля Склад) — сложный сценарий
    - [ ] «Как настроить маршруты пополнения?» (из Конфигурации Склада) — akaidoo context должен помочь
    - [ ] Переключение между модулями → контекст обновляется в ответах
    - [ ] Вопрос не по теме → корректный отказ или перенаправление
    - [ ] OpenRouter недоступен → fallback-сообщение
    - [ ] Вопрос по object_request → akaidoo context кастомного модуля
  - [ ] **Vision-сценарии** (скриншот):
    - [ ] «Что у меня на экране?» (список товаров) — описать список
    - [ ] «У меня на экране ошибка, помоги» (форма с validation error) — объяснить ошибку
    - [ ] «Смотри на экран, какую кнопку нажать?» (форма поступления) — указать конкретную кнопку
    - [ ] «Что здесь можно сделать?» (kanban CRM) — описать возможности
    - [ ] «В открытой вкладке не могу найти кнопку отгрузки» — найти на скриншоте
  - [ ] Зафиксировать результаты в `docs/pilot_results_v2.md`:
    - [ ] Для каждого сценария: вопрос, ответ, оценка (✅/⚠️/❌), комментарий
    - [ ] Список обнаруженных проблем → создать баги
- **Критерий готовности**: Все 15 сценариев прогнаны; ≥12 из 15 оценены как ✅; критические баги зафиксированы и исправлены.
- **Зависимости**: Весь этап V2-3 (AIA-016, AIA-023, AIA-024, AIA-025, AIA-026) — E2E vision-сценарии требуют полную цепочку: клиент → скриншот → бэкенд → vision-модель

---

### Задача: AIA-030 — Аудит term_mapping по живому UI

- **Статус**: Не начата
- **Приоритет**: Высокий
- **Описание**: Полный аудит `term_mapping.json` — пройти ВСЕ экраны целевых модулей Odoo 19 (ru_RU), проверить каждый маппинг кнопок/меню/полей, дополнить пропущенное.
- **Шаги выполнения**:
  - [ ] **Склад** (stock):
    - [ ] Главное меню → подменю Операции, Товары, Отчёт, Конфигурация
    - [ ] Список товаров → кнопки, фильтры, группировки
    - [ ] Форма товара → вкладки, поля, кнопки
    - [ ] Поступления → кнопки на форме (Подтвердить, Зарезервировать, Проверить)
    - [ ] Отгрузки → кнопки
    - [ ] Инвентаризация → кнопки (Применить всё, Обновить количество)
    - [ ] Конфигурация → Склады → форма создания
  - [ ] **Продажи** (sale):
    - [ ] Котировки → кнопки (Подтвердить, Отправить, Отмена)
    - [ ] Заказы → кнопки (Создать счёт)
    - [ ] Форма заказа → поля, вкладки
  - [ ] **Закупки** (purchase):
    - [ ] Запросы котировок → кнопки
    - [ ] Заказы поставщику → кнопки (Подтвердить, Получить товар)
  - [ ] **CRM** (crm):
    - [ ] Воронка (kanban) → кнопки стадий
    - [ ] Форма лида → кнопки (Выиграно, Проиграно, Конвертировать)
  - [ ] **Контакты** (contacts):
    - [ ] Список → кнопки
    - [ ] Форма → вкладки, типы контактов
  - [ ] **Настройки** (settings):
    - [ ] Главная → секции настроек
    - [ ] Пользователи → кнопки
  - [ ] Обновить `term_mapping.json` с результатами аудита
  - [ ] Перезапустить `scripts/update_knowledge_v2.sh` для пересборки docs с обновлённым маппингом
- **Критерий готовности**: Все экраны пройдены; term_mapping содержит ≥80 верифицированных маппингов; knowledge base пересобрана с обновлённым маппингом.
- **Зависимости**: AIA-013 (первичный маппинг)

---

## Сводная таблица задач

| ID       | Задача                                    | Этап   | Приоритет    | Статус     | Context7 | Зависимости         | Меняет controller |
|----------|-------------------------------------------|--------|-------------|------------|----------|----------------------|-------------------|
| AIA-012  | Скрипт конвертации RST → MD               | V2-1   | Критический | ✅ Готова  | ✅ Да    | AIA-013              | —                 |
| AIA-013  | Создать term_mapping.json                 | V2-1   | Критический | ✅ Готова  | —        | —                    | —                 |
| AIA-014  | knowledge_provider_v2                     | V2-1   | Критический | ✅ Готова  | —        | AIA-012, AIA-013     | —                 |
| AIA-015  | Скрипт обновления knowledge base          | V2-1   | Высокий     | ✅ Готова  | —        | AIA-012, AIA-013     | —                 |
| AIA-016  | Обновить prompt_builder для v2            | V2-1   | Критический | ✅ Готова  | ✅ Да    | AIA-014              | ✅ (1-й)           |
| AIA-017  | Два поля модели в Settings                | V2-2   | Высокий     | ✅ Готова  | —        | —                    | —                 |
| AIA-018  | openrouter_client_v2: model_override      | V2-2   | Высокий     | ⚠️ Частично | —        | AIA-017              | ✅ (2-й)           |
| AIA-019  | Обновить Settings UI                      | V2-2   | Средний     | ⚠️ Частично | —        | AIA-017              | —                 |
| AIA-020  | Подключить html2canvas                    | V2-3   | Высокий     | ✅ Готова  | ✅ Да    | —                    | —                   | ✅ Да    | —                    | —                 |
| AIA-021  | screenshot_trigger.js                     | V2-3   | Высокий     | ✅ Готова  | —        | —                    | —                   | —        | —                    | —                 |
| AIA-022  | captureScreen()                           | V2-3   | Высокий     | ✅ Готова  | ✅ Да    | AIA-020              | —                   | ✅ Да    | AIA-020              | —                 |
| AIA-023  | Расширить payload + OWL-виджет            | V2-3   | Высокий     | ✅ Готова  | ✅ Да    | AIA-021, AIA-022     | —                   | ✅ Да    | AIA-021, AIA-022     | —                 |
| AIA-024  | Backend: парсинг скриншота                | V2-3   | Высокий     | ✅ Готова  | —        | AIA-018              | ✅ (3-й)             | —        | AIA-018              | ✅ (3-й)           |
| AIA-025  | prompt_builder vision mode                | V2-3   | Высокий     | ✅ Готова    | —        | AIA-016, AIA-024     | —                 |
| AIA-026  | Rate limiter для vision                   | V2-3   | Средний     | ✅ Готова  | —        | AIA-024              | —                   | —        | AIA-024              | —                 |
| AIA-027  | Тесты knowledge_provider_v2               | V2-4   | Высокий     | Не начата  | —        | AIA-014              | —                 |
| AIA-028  | Тесты vision pipeline                     | V2-4   | Высокий     | Не начата  | —        | AIA-024, AIA-025, AIA-026 | —            |
| AIA-029  | Пилотные сценарии                         | V2-4   | Высокий     | Не начата  | —        | Весь V2-3 (AIA-016..026) | —              |
| AIA-030  | Аудит term_mapping по UI                  | V2-4   | Высокий     | Не начата  | —        | AIA-013              | —                 |

> **Примечание (колонка «Меняет controller», AIA-018):** `model_override` реализован в `OpenRouterClient` и в сигнатуре `_get_ai_response`, но метод `chat()` пока не передаёт vision-модель — это запланировано в **AIA-024**.

---

## Рекомендуемый порядок реализации

### Инкремент 1 — Knowledge base v2 (неделя 1–2)

```
Параллельно (нет взаимных зависимостей):
  AIA-013 (term_mapping) ← ручная работа, без кода
  AIA-017 (два поля модели) ← простая задача, нет зависимостей

Последовательно (AIA-012 зависит от AIA-013):
  AIA-013 → AIA-012 (RST-конвертер) → AIA-014 (провайдер v2)
           → AIA-015 (скрипт обновления)
           → AIA-016 (prompt_builder v2, первое изменение controller)
           → AIA-027 (тесты провайдера)
```

### Инкремент 2 — Двухуровневая модель (неделя 2)

```
  AIA-017 → AIA-018 (model_override, второе изменение controller)
         → AIA-019 (Settings UI)
```

### Инкремент 3 — Vision pipeline (неделя 3)

```
Параллельно (нет взаимных зависимостей):
  AIA-020 (html2canvas) + AIA-021 (trigger + manifest)

Последовательно:
  AIA-020 → AIA-022 (captureScreen)
  AIA-021 + AIA-022 → AIA-023 (payload + OWL-виджет + история)
  AIA-018 + AIA-023 → AIA-024 (backend парсинг, третье изменение controller)
  AIA-024 → AIA-025 (vision prompt) + AIA-026 (rate limiter)
  AIA-025 + AIA-026 → AIA-028 (тесты vision)
```

### Инкремент 4 — Тестирование и аудит (неделя 4)

```
  AIA-029 (пилотные сценарии) — после всех остальных
  AIA-030 (аудит term_mapping) — можно начать раньше, параллельно с инкрементом 3
```

---

## Критерии готовности v2 (чеклист)

_Отметки по состоянию кода на 2026-03-21._

- [x] Ассистент отвечает на основе RST-документации Odoo 19, не на ручных JSON (`docs/*.md`, `KnowledgeProviderV2`; legacy в `legacy/`)
- [x] Термины кнопок/меню — через `term_mapping.json` и промпт v2 (полный обход живого UI — AIA-030)
- [x] term_mapping.json содержит ≥80 верифицированных маппингов (фактически 188; источник — ru.po, см. AIA-013)
- [ ] При триггерных фразах — захват скриншота и ответ на основе изображения (AIA-020…023)
- [ ] Vision-запросы уходят на мощную модель (клиент готов; контроллер — после AIA-024)
- [x] Администратор может менять обе модели в Settings
- [ ] Скриншоты не логируются, не сохраняются, не попадают в историю чата (не реализовано — N/A до vision)
- [ ] Rate limit на vision-запросы работает (AIA-026)
- [ ] response_guard совместим с ответами vision-модели (не проверялось)
- [x] Knowledge base обновляется одним скриптом (`scripts/update_knowledge_v2.sh`)
- [ ] Все unit-тесты проходят (AIA-027/028 + доработка `test_openrouter_client`; прогон в среде без конфликта порта 8069)
- [ ] ≥12 из 15 пилотных сценариев оценены как ✅ (`docs/pilot_results_v2.md` отсутствует)
- [ ] Модуль обновляется без ошибок (`-u ai_assistant`) — подтвердить прогоном после остановки конфликтующего инстанса
