## [2026-05-11] — OBR: чистка тестов multi-warehouse
### Добавлено
- Multi-warehouse сценарии в `test_obr011_issue_picking.py` и `test_obr012_confirm_issue.py`: одна строка требования может создавать выдачи по нескольким складам, а синхронизация `qty_issued` суммирует движения по всем выдачам строки.
### Изменено
- Тестовые фабрики `object_request` очищены от старого шапочного `warehouse_id` в `object.request.create()`.
- `test_obr024_warehouse.py` и `test_obr025_multiwarehouse_check.py` переписаны под новую схему `object.request.line.stock` и расчёт по всем активным складам.
- `object.request.line.stock` хранит ссылку на `stock.move`, чтобы multi-picking выдача корректно синхронизировала фактически выданное количество.

## [2026-05-11] — OBR: закупка, UX распределения и миграция складов
### Добавлено
- `purchase_wizard`: явный `picking_type_id` для склада приёмки; по умолчанию берётся `request.project_id.warehouse_id.in_type_id`, при отсутствии склада объекта используется fallback на входящий тип операции компании.
- Массовые действия для строк требования: «Закупить всё», «Выдать максимум», «Сбросить разбивку»; доступны как кнопки на форме требования и как server actions для выбранных строк.
- Миграция `19.0.1.1.0`: pre-backup старых складских связей в `_legacy_object_request_warehouse`, post-создание складов объектов и перенос старых остатков строк в `object.request.line.stock`.
### Изменено
- UI строк разделён по ролям: прораб видит итоговые количества, снабженец редактирует распределение по складам, кладовщик видит распределение только на чтение.
- `object.request.project` в форме блокирует изменение `name` после создания; `code` остаётся read-only.

## [2026-05-11] — OBR: удаление склада из шапки требования
### Изменено
- `object.request`: удалены шапочные поля `warehouse_id`, `check_warehouse_ids`, `stock_check_confirmed`.
- `action_check_stock` временно считает остатки по всем активным складам компании до переноса расчёта в `object.request.line.stock`.
- Wizard импорта больше не требует склад; wizard закупки берёт склад приёмки из склада объекта (`request.project_id.warehouse_id`).

## [2026-05-11] — OBR: распределение выдачи по складам
### Добавлено
- Модель `object.request.line.stock` для хранения остатков, плана выдачи, резерва и созданной выдачи по каждой паре строка/склад.
- `object.request.issue.preview.wizard`: предпросмотр выдач с группировкой по складам и созданием одного `stock.picking` на каждый выбранный склад.
- `object.request.auto.split.confirm.wizard`: подтверждение перезаписи распределения, если снабженец вручную менял план.
### Изменено
- `action_check_stock` создаёт/обновляет строки распределения через агрегированный `stock.quant.read_group`.
- `action_auto_split` распределяет выдачу по складам по убыванию доступного остатка и считает остаток к закупке.

## [2026-05-11] — OBR: склад закреплён за объектом
### Добавлено
- `object.request.project`: поле `company_id`, `warehouse_id` и автогенерация кода через новую последовательность `object.request.project.code` (`O001`, `O002`, …).
- Автосоздание склада при создании объекта (имя `{name} склад`, код = код объекта, компания из объекта) + каскадная синхронизация активности.
- Защита от удаления объекта с активными требованиями или остатками на складе; новые Odoo тесты `test_obr026_project_warehouse` покрывают авто-склад, запрет переименования, архивацию, unlink-ограничения.
### Изменено
- Поля `name`/`code` объекта после создания доступны только администраторам; при переименовании админом название склада обновляется автоматически.
- Формы/списки объектов показывают склад и компанию, `code` стал только для чтения.

## [2026-05-11] — Уточнение логики проверки наличия (два режима)
### Изменено
- `action_check_stock` теперь работает в двух режимах: режим прораба (check_warehouse_ids пуст → проверка склада объекта → wizard актуальности) и режим снабженца (check_warehouse_ids заполнен → проверка по выбранным складам → toast «Найдено X из Y позиций»)
- Текст wizard изменён: «Часть позиций уже есть на складе объекта. Проверьте актуальность требования»
- После «Проверено» прораб самостоятельно решает: скорректировать строки или нажать «В работу»

## [2026-05-11] — Проверка наличия по нескольким складам
### Добавлено
- Поле `check_warehouse_ids` (Many2many → `stock.warehouse`) в `object.request` — список складов для проверки наличия; если пустой, используется `warehouse_id` документа
- Поле `stock_check_confirmed` (Boolean) — флаг подтверждения результатов проверки
- Wizard `object.request.stock.check.wizard` — показывает позиции с ненулевым остатком, кнопка «Проверено» устанавливает флаг подтверждения
### Изменено
- `action_check_stock` теперь суммирует остатки по всем складам из `check_warehouse_ids`; при нулевых остатках возвращает warning-уведомление, при наличии товаров открывает wizard подтверждения


### Добавлено
- Поле `warehouse_id` (Склад) в модель `object.request` — обязательное, с дефолтом (первый склад компании), отображается в форме и списке заявок
- Поле `warehouse_id` в wizard импорта Excel — передаётся в создаваемую заявку

### Изменено
- `action_check_stock` теперь считает остатки по складу, указанному в заявке (не первый попавшийся)
- Wizard выдачи (`issue_wizard`) использует склад заявки как приоритетный
- Wizard закупки (`purchase_wizard`) передаёт `picking_type_id` входящего склада в `purchase.order` — приёмки теперь создаются на нужном складе

## [2026-05-06] - Улучшенный поиск товаров custom_product_search
### Добавлено
- Новый addon `custom_product_search` для Odoo 19: normalized stored поле `x_search_name` на `product.template` и `product.product`, расширенный backend-поиск товаров и сервис `ai_search_products()` для AI-ассистента.
- `post_init_hook` для включения `pg_trgm` и создания GIN trigram-индексов на `product_template.x_search_name` и `product_product.x_search_name`.
- README и Odoo tests для сценариев поиска `кран шаровый Ду50`, `кран ду50`, `шаровый ду 50`, `ДУ50`.

### Изменено
- Поиск `product.product.name_search()` расширен совместимым с Odoo 19 способом: стандартный поиск Odoo выполняется первым, затем применяется fallback по `default_code`, `barcode`, `name`, `x_search_name`, `product_tmpl_id.x_search_name` и токенам нормализованного запроса.

## [2026-03-31] - fix: fallback-логика _search_docs (ai_assistant)
### Изменено
- `services/knowledge_provider_v2.py` — убран fallback `scored[:3]` в `_search_docs`: при отсутствии секций с `score > 0` теперь возвращается пустая строка вместо нерелевантных секций. Это предотвращает ложный отказ модели отвечать из-за попадания в промпт контента из чужих модулей (purchase/sale).

## [2026-03-21] - AIA-029+030: Шаблоны для пилотных сценариев и аудита term_mapping
### Добавлено
- `docs/pilot_results_v2.md` (AIA-029) — шаблон 15 пилотных сценариев: T-01..T-10 (текстовые) и V-01..V-05 (vision). Для каждого: контекст, вопрос, ожидаемый результат, колонки для результатов. Инструкция по прогону с командами для логов.
- `docs/audit_term_mapping_checklist.md` (AIA-030) — чеклист 175 маппингов term_mapping.json по 15 секциям (Склад, Продажи, Закупки, CRM, Контакты, Настройки, общие элементы). Структура: EN → RU в маппинге → реальный RU → статус. Итоговая статистика и таблица расхождений.

## [2026-03-21] - AIA-027+028: Unit-тесты KnowledgeProviderV2 + vision pipeline (ai_assistant)
### Добавлено
- `tests/test_knowledge_provider_v2.py` (AIA-027) — 24 unit-теста: загрузка/кеш term_mapping, построение индекса docs, поиск секций `_search_docs`, соблюдение MAX_DOCS_CHARS, boost по модулю, get_technical_context (кеш, обрезание, отсутствующий файл), get_knowledge (интеграция трёх слоёв), get_snippets (compat v1), extract_keywords, score_section.
- `tests/test_vision_pipeline.py` (AIA-028) — 36 unit-тестов в 4 классах: `TestScreenshotTrigger` (15 тестов: позитивные/негативные фразы-триггеры), `TestParseScreenshot` (8 тестов: JPEG/PNG, None, неправильный prefix, oversized, malformed), `TestVisionRateLimit` (5 тестов: первый запрос, в пределах лимита, превышение, разные пользователи, устаревшие метки), `TestPromptBuilderVisionMode` (8 тестов: multimodal content, image_url, text mode fallback, контекст в промпте).
### Изменено
- `tests/__init__.py` — добавлены импорты `test_knowledge_provider_v2` и `test_vision_pipeline`.

## [2026-03-21] - AIA-020..026: Screenshot capture + Vision pipeline (ai_assistant)
### Добавлено
- `static/lib/html2canvas.min.js` v1.4.1 (199 KB) — библиотека захвата DOM в canvas.
- `static/src/js/screenshot_trigger.js` — 22 триггерных фразы на русском; `needsScreenshot(message)` → boolean; case-insensitive.
- `services/prompt_builder.py` — vision mode (AIA-025): `build_messages()` при `image_data` формирует multimodal content `[{type:text},{type:image_url}]`; `_build_vision_prompt()` — специальный промпт с контекстом экрана.
### Изменено
- `static/src/js/ai_chat_service.js` — `captureScreen()`: скрывает виджет → html2canvas(scale=0.7, JPEG 0.8) → проверка 500 KB → восстанавливает виджет; `maybeCapture(msg)` — оркестрация trigger+capture; `saveHistory()` никогда не сохраняет скриншоты.
- `static/src/js/ai_chat_boot.js` — интеграция: `isCapturing` state, loadingLabel «Делаю скриншот...» / «Думаю...», `_callBackend()` вызывает `maybeCapture()`, добавляет `screenshot` в params, `_buildHistory()` исключает скриншоты.
- `controllers/chat_controller.py` — `chat()` принимает `screenshot=None`; `_parse_screenshot()` валидирует format/размер; `_vision_rate_ok()` rate limit 5/мин на пользователя; выбор vision-модели из настроек при наличии скриншота.
- `__manifest__.py` — добавлены `html2canvas.min.js` и `screenshot_trigger.js` в `web.assets_backend`.

## [2026-03-21] - Аудит roadmap/tasktracker AI-ассистент v2 (документация)
### Изменено
- `docs/tasktracker_ai_assistant_v2.md` — сверка с кодом: закрыты противоречия в AIA-016 (шаги/статус); AIA-017 отмечена выполненной (без отдельной миграции БД); AIA-018 и AIA-019 — **частично**; AIA-025 — **заготовка** (`image_data` в сигнатуре); сноска к таблице задач; чеклист готовности v2 с фактическими отметками.
- `docs/roadmap_ai_assistant_v2.md` — таблица «Фактическое выполнение», обновлён §11 (критерии готовности) в соответствии с репозиторием.

## [2026-03-21] - Этапы V2-1 и V2-2 завершены (ai_assistant)
### Итог
Завершены оба подготовительных этапа roadmap AI-ассистента v2:
- **V2-1 (Knowledge base v2):** AIA-012..016 — RST-конвертер, term_mapping (188 маппингов, верифицирован по ru.po), KnowledgeProviderV2 (трёхслойный: docs/akaidoo/term_mapping), скрипты update_knowledge_v2.sh + rebuild_knowledge_index.py, PromptBuilder v2 (system prompt Odoo 19, term_mapping в промпте, новая сигнатура build_messages).
- **V2-2 (Двухуровневая модель):** AIA-017..019 — раздельные поля text_model/vision_model в Settings, model_override в OpenRouterClient, обновлённый Settings UI с рекомендациями.

Система готова к этапу V2-3: Screenshot capture + Vision (AIA-020..026).

## [2026-03-21] - AIA-017+018+019: двухуровневая модель + Settings UI (ai_assistant)
### Добавлено
- `models/ai_assistant_config.py` — два новых поля: `ai_assistant_text_model` (default: `google/gemini-2.0-flash-001`) и `ai_assistant_vision_model` (default: `openai/gpt-4o`); старое поле `ai_assistant_model` оставлено для обратной совместимости.
- `services/openrouter_client.py` — параметр `model_override=None` в `send_chat()`; автоматический fallback с `text_model` на legacy `openrouter_model`; логирование режима (`text`/`vision`); `_parse_response()` возвращает поле `mode`.
### Изменено
- `views/ai_assistant_settings_views.xml` — раздел «Модели» заменяет одно поле двумя (`text_model` + `vision_model`) с help-подсказками (рекомендованные модели, цены/M token).
- `controllers/chat_controller.py` — `_get_ai_response()` принимает `model_override`, передаёт в `send_chat()`; `meta` дополнен полем `mode`.

## [2026-03-21] - AIA-016: PromptBuilder v2 + chat_controller на KnowledgeProviderV2 (ai_assistant)
### Изменено
- `custom_addons/ai_assistant/services/prompt_builder.py` — обновлён до v2: новый system prompt с явными правилами Odoo 19 (нет «Сохранить»/«Редактировать», «Новое» вместо «Создать»); новая сигнатура `build_messages(message, history, context, knowledge=None, override=None, image_data=None)`; добавлен `build_term_mapping_block()` — вставляет maппинг EN→RU в системный промпт; `build_knowledge_block()` поддерживает оба формата — v2 dict (`{docs_snippets, tech_context, term_mapping}`) и v1 list (обратная совместимость).
- `custom_addons/ai_assistant/controllers/chat_controller.py` — переключён на `KnowledgeProviderV2`; вызов `build_messages()` обновлён под новую сигнатуру; логика `_resolve_module()` вынесена в отдельный метод.
- `custom_addons/ai_assistant/tests/test_prompt_builder.py` — адаптированы 22 теста под новую сигнатуру; добавлено 5 новых тестов: `test_v19_rules_in_system_prompt`, `test_build_knowledge_block_v2_format_*`, `test_build_term_mapping_block_*`, `test_term_mapping_included_in_build_messages`, `test_knowledge_v2_format_in_build_messages`.

## [2026-03-21] - AIA-014 + AIA-015: KnowledgeProviderV2 + скрипты обновления (ai_assistant)
### Добавлено
- `custom_addons/ai_assistant/services/knowledge_provider_v2.py` — трёхслойный провайдер знаний: RST-based docs (поиск по секциям MD), akaidoo context, term_mapping. Методы: `get_knowledge()`, `_search_docs()` (keyword index + boost), `get_snippets()` (совместимость с v1), `get_technical_context()`, `_get_relevant_terms()`. MAX_DOCS_CHARS=10000.
- `custom_addons/ai_assistant/static/knowledge/index.json` — индекс knowledge base: 8 модулей с маппингом docs + generated файлов, odoo_version/lang метаданные.
- `scripts/rebuild_knowledge_index.py` — Python-скрипт пересборки index.json: автодетект модуля по префиксу имени файла, --dry-run режим, summary.
- `scripts/update_knowledge_v2.sh` — единый bash-скрипт полного обновления knowledge base: 5 шагов (git pull/clone, RST→MD, akaidoo, index). Флаги: --dry-run, --skip-docs, --skip-akaidoo. Graceful при отсутствии akaidoo или RST-репозитория.

## [2026-03-21] - AIA-013: Верификация и расширение term_mapping.json (ai_assistant)
### Изменено
- `custom_addons/ai_assistant/static/knowledge/term_mapping.json` — верифицирован и расширен по официальным `ru.po` файлам Odoo 19: 188 маппингов (было ~80). Исправлены расхождения: Reserve→«Резерв», Unreserve→«Отменить бронирование», Scrap→«Брак», Apply All→«Применить все», Put in Pack→«Положить в упаковку», Log note→«Внутренняя заметка», Quotations→«Коммерческие предложения», Purchase Orders→«Заказы на покупку», Expected Revenue→«Ожидаемый доход». Добавлены: раздел `statuses` (14 статусов), новые кнопки (Won/Lost/Mark Lost/Confirm Order/Receive Products/Convert/Update Quantity), новые пункты меню (Transfers/Adjustments/Procurement — актуальная структура Odoo 19). Задокументированы расхождения с legacy JSON-сниппетами в разделе `discrepancies_vs_legacy`.

## [2026-03-21] - AIA-012: Скрипт конвертации RST → локализованный Markdown (ai_assistant)
### Добавлено
- `scripts/convert_rst_to_knowledge.py` — Python-скрипт конвертации RST-документации Odoo 19 → Markdown для knowledge base AI-ассистента. Парсит `:menuselection:`, `**Кнопки**`, `#. Шаги`, `.. note::/tip::`. Применяет `term_mapping.json` (EN→RU). Удаляет шаги с устаревшими кнопками (`Save`, `Edit`) из `removed_in_v19`. CLI: `--source`, `--output`, `--term-mapping`, `--demo`, `--dry-run`, `--verbose`. Demo-режим генерирует 12 заглушек-файлов при отсутствии RST-репозитория.
- `custom_addons/ai_assistant/static/knowledge/term_mapping.json` — маппинг EN→RU терминов Odoo 19: 80+ маппингов (кнопки, пункты меню, поля форм, типы представлений, `removed_in_v19`).
- `custom_addons/ai_assistant/static/knowledge/docs/` — 12 MD-файлов knowledge base (stock, sale, purchase, crm, contacts, settings), сгенерированных в demo-режиме.
- `custom_addons/ai_assistant/static/knowledge/legacy/` — старые JSON-сниппеты перемещены для отката.

## [2026-03-20] - Документация: Akaidoo для knowledge base ai_assistant
### Добавлено
- `docs/roadmap_akaidoo.md` — дорожная карта: установка Akaidoo на хосте, `akaidoo.conf`, разведка модулей, генерация контекста (`--shrink`, `-B`, `-E`, `--agent`), интеграция с `knowledge_provider` / `prompt_builder`, скрипт `update_knowledge.sh`, план действий.

## [2026-03-18] - OBR-020: Резервирование товаров под требование (object_request)
### Добавлено
- `models/object_request_line.py` — поле `issue_reserved` (Boolean, `Резерв создан`): флаг что по строке выполнено резервирование на складе.
- `models/object_request.py` — поле `qty_total_reserved` (Float, computed+store): суммарное зарезервированное количество по всем строкам документа.
- `wizards/issue_wizard.py` — в `action_create_issue()` после создания `stock.picking` вызывается `picking.action_assign()` для автоматического резервирования; `qty_reserved` и `issue_reserved` синхронизируются из `move_line_ids.quantity`.
- `tests/test_obr020_reservation.py` — 5 тестов: резервирование при создании picking, снятие резерва при отмене документа, пересчёт `qty_total_reserved`, отмена без picking, `issue_reserved=False` при отсутствии стока.
### Изменено
- `models/object_request.py` — `action_cancel()`: перед сменой статуса вызывает `picking.do_unreserve()` для всех связанных picking в состоянии `confirmed/assigned/waiting`, сбрасывает `qty_reserved=0`, `issue_reserved=False` в строках.
- `views/object_request_views.xml` — добавлена колонка `Зарезервировано` (`qty_reserved`) в inline-листе строк; добавлено поле `qty_total_reserved` на вкладке «Обработка».
- `views/object_request_line_views.xml` — добавлена колонка `Зарезервировано` в standalone list view строк.
- `tests/__init__.py` — добавлен импорт `test_obr020_reservation`.

## [2026-03-18] - OBR-019: Автоматический расчёт наличия по физическому остатку (object_request)
### Добавлено
- `models/object_request.py` — метод `action_check_stock()`: запрашивает `qty_available` со склада компании для каждой строки с `product_id`, заполняет `stock_qty_on_hand` и `stock_check_date`, возвращает уведомление.
- `models/object_request.py` — метод `action_auto_split()`: на основе `stock_qty_on_hand` вычисляет `qty_to_issue = min(stock, qty_requested)` и `qty_to_buy = qty_requested − qty_to_issue`, обновляет `procurement_mode`. Требует предварительного вызова `action_check_stock()`.
- `tests/test_obr019_stock_check.py` — 15 тестов: расчёт наличия (заполнение полей, нулевой остаток, реальный остаток, пропуск строк без товара, уведомление), авто-разбивка (полный остаток, нулевой, частичный, точный, не превышает запрошенное, пропуск отменённых, повторный вызов).
### Изменено
- `views/object_request_views.xml` — кнопка «Рассчитать наличие» заменена с заглушки на `action_check_stock`; добавлена кнопка «Авто-разбивка» (`action_auto_split`); обновлена секция «Автоматическая обработка».
- `tests/__init__.py` — добавлен импорт `test_obr019_stock_check`.

## [2026-03-16] - OBR-014: Печатная форма расходной накладной (object_request)
### Добавлено
- `reports/issue_picking_report.xml` — QWeb-отчёт `report_issue_picking` для модели `stock.picking`: шапка (номер документа, ссылка на требование, объект, дата, склад, назначение), таблица позиций (товар, ед. изм., запрошено, выдано, зона/этаж/участок, примечание из строки требования), блок подписей (кладовщик, получатель/прораб).
- `tests/test_obr014_report.py` — 8 тестов: проверка регистрации action, binding, флаг `is_object_request_issue`, HTML-рендеринг, объект, ссылка на требование, подписи, зоны/участки.
### Изменено
- `views/stock_picking_inherit_views.xml` — добавлена кнопка `Расходная накладная` в header формы picking (видна только при `is_object_request_issue=True`).
- `__manifest__.py` — добавлен `reports/issue_picking_report.xml` в data.
- `tests/__init__.py` — подключён `test_obr014_report`.

## [2026-03-16] - OBR-013: Печатная форма требования на комплектацию (object_request)
### Добавлено
- `reports/object_request_report.xml` — QWeb-отчёт `report_object_request` для модели `object.request`: action `ir.actions.report`, шаблон с шапкой документа, таблицей строк (№, зона, этаж, участок, наименование, ед. изм., количество, выдано, примечание) и блоком подписей (Прораб, Снабженец, Согласующий).
- `tests/test_obr013_report.py` — 5 тестов: проверка регистрации action, binding к модели, HTML-рендеринг с проверкой содержимого (шапка, строки), блок подписей, зоны/этажи/участки.
### Изменено
- `views/object_request_views.xml` — добавлена кнопка `Распечатать требование` в header формы (невидима при state=cancelled).
- `__manifest__.py` — добавлен `reports/object_request_report.xml` в data (перед views).
- `tests/__init__.py` — подключён `test_obr013_report`.

## [2026-03-15] - OBR-007: Парсинг, сопоставление и создание строк Excel-импорта (object_request)
### Добавлено
- `models/excel_parser.py` — AbstractModel `object.request.excel.parser`: нормализация UOM (шт/шт./штука→шт. и т.д.), нормализация строк, поиск товара по артикулу (`product.supplierinfo`) и по наименованию (exact/ilike), поиск поставщика по имени (`res.partner`), комбинированный `match_row()`.
- `tests/test_obr007_import.py` — 14 тестов: нормализация UOM, автосопоставление, полный цикл validate→import, перенос полей строк, флаги matching_required/manual_vendor_required.
### Изменено
- `wizards/import_excel_wizard.py` — `ObjectRequestImportPreview`: добавлены поля `matched_vendor_id`, `matching_required`, `manual_vendor_required`. `action_validate()`: вызывает `excel_parser` для нормализации и автосопоставления каждой строки. `action_import()`: реализована — создаёт документ `object.request` со строками, перенаправляет на форму.
- `models/__init__.py` — добавлен импорт `excel_parser`.
- `tests/__init__.py` — подключён `test_obr007_import`.
- `tests/test_obr006_wizard.py` — `test_action_import_raises_user_error` переименован и скорректирован под новое поведение (UserError при отсутствии валидации).

## [2026-03-15] - OBR-006: Wizard загрузки Excel-файла (object_request)
### Добавлено
- `wizards/import_excel_wizard.py` — полная реализация. Модель `object.request.import.wizard` (wizard) + `object.request.import.preview` (предпросмотр строк).
- `wizards/import_excel_wizard_views.xml` — form view wizard с блоком загрузки файла, параметрами документа, блоком статуса проверки, вкладкой предпросмотра строк; action `action_object_request_import_wizard`.
- `tests/test_obr006_wizard.py` — 11 unit-тестов: валидация файла, парсинг строк, обработка ошибочных строк, очистка предпросмотра при повторной проверке.
- Пункт меню "Импорт из Excel" в модуле.
### Изменено
- `security/ir.model.access.csv` — добавлены права на `object.request.import.preview` для ролей Прораб и Снабженец.
- `__manifest__.py` — добавлен `wizards/import_excel_wizard_views.xml` в раздел `data`.
- `views/object_request_menu.xml` — добавлен пункт меню "Импорт из Excel" (sequence=15).
- `tests/__init__.py` — подключён `test_obr006_wizard`.

## [2026-03-15] - OBR-005: Меню, list/form views, search view (object_request)
### Добавлено
- `views/object_request_menu.xml` — корневое меню "Комплектация объектов", подменю "Требования" и "Объекты".
- `views/object_request_project_views.xml` — list/form views для `object.request.project` (справочник объектов) + action.
- `views/object_request_line_views.xml` — list view + search view для `object.request.line` (используется в smart-buttons).
- `views/object_request_views.xml` — list view (с decoration по статусу), form view (header кнопки, statusbar, smart buttons, notebook с вкладками Строки/Обработка/Связанные документы/Импорт, chatter), search view (фильтры и группировки).
- Методы smart buttons в `object_request.py`: `action_open_lines`, `action_open_problem_lines`, `action_open_issue_pickings`, `action_open_purchase_orders`.
- Заглушки кнопок этапа 2: `action_check_stock_stub`, `action_prepare_purchase_stub`.
- Метод `action_open_requests` в `object_request_project.py` для smart button объекта.

### Изменено
- `__manifest__.py` — добавлены 4 файла views в раздел `data`.

## [2026-03-15] - OBR-004: Базовые модели документа и строк (object_request)
### Добавлено
- `models/object_request_project.py` — модель `object.request.project` (справочник объектов) с автосчётчиком требований и уникальностью кода.
- `models/object_request.py` — модель `object.request` (шапка документа) с автонумерацией, методами смены статуса (`action_in_progress`, `action_close`, `action_cancel`), computed-агрегатами по строкам.
- `models/object_request_line.py` — модель `object.request.line` (строки) с computed `line_state` через `is_cancelled`, SQL-ограничениями на qty, onchange-хелперами.
- `wizards/import_excel_wizard.py` — заглушка wizard для ACL CSV (полная реализация в OBR-006).
- `data/ir_sequence_data.xml` — sequence `object.request.sequence` с форматом `OR/YYYY/MM/XXXX`.
- `tests/test_obr004_models.py` — 27 unit-тестов на все три модели.
- Исправлен `security/object_request_security.xml` под Odoo 19: добавлен `res.groups.privilege`; убран несуществующий `category_id` в `res.groups`.

### Изменено
- `models/__init__.py`, `wizards/__init__.py`, `tests/__init__.py` — подключены новые файлы.
- `__manifest__.py` — добавлен `data/ir_sequence_data.xml`.

## [2026-03-15] - Data model spec для требования на комплектацию объекта
### Добавлено
- `docs/datamodelspecobjectrequest.md` — data model spec по Odoo-моделям, полям, связям, ограничениям и вычисляемым полям для модуля `Требование на комплектацию объекта`.
- Зафиксирован рекомендуемый выбор отдельной модели объекта `object.request.project` для MVP.
- Описаны основные модели: объект, шапка требования, строки требования, transient wizards, а также расширения `stock.picking` и `purchase.order`.
- Зафиксированы поля под MVP и под этап 2, чтобы не ломать структуру при развитии модуля.

### Изменено
- Документация по модулю требования дополнена слоем модели данных поверх roadmap и functional spec.

### Исправлено
- Нет.

## [2026-03-15] - Functional spec экранов и кнопок для требования на комплектацию объекта
### Добавлено
- `docs/functionalspecobjectrequest.md` — functional spec по экранным формам, кнопкам, ролям и пользовательским сценариям для модуля `Требование на комплектацию объекта`.
- Зафиксированы UI-экраны: список документов, форма документа, wizard импорта Excel, встроенный режим сопоставления, форма выдачи, печатные формы.
- Зафиксированы правила видимости кнопок по статусам документа и ролям пользователей.
- Зафиксированы состав шапки формы, структура строк, smart buttons, tabs и UI-заглушки для этапа 2.

### Изменено
- Документация по модулю требования дополнена отдельным функциональным слоем поверх roadmap.

### Исправлено
- Нет.

## [2026-03-15] - Roadmap модуля "Требование на комплектацию объекта"
### Добавлено
- `ai_docs/develop/plans/2026-03-15-object-kit-demand-roadmap.md` — детальный roadmap для кастомного Odoo 19 модуля требований на комплектацию объекта.
- `.cursor/workspace/active/orch-2026-03-15-18-22-object-kit-demand/` — orchestration workspace с `progress.json`, `tasks.json`, `links.json` для дальнейшего исполнения roadmap.

### Изменено
- `docs/tasktracker.md` — добавлена завершённая задача по подготовке roadmap-документа.

### Исправлено
- Нет.

---

## [2026-03-15] - Roadmap модуля требования на комплектацию объекта
### Добавлено
- `docs/roadmapobjectrequest.md` — детальный roadmap кастомного Odoo 19 модуля `Требование на комплектацию объекта`.
- Описан целевой workflow: импорт Excel -> ручное сопоставление -> выдача со склада -> черновик закупки на дефицит.
- Зафиксированы состав MVP и границы этапа 2.
- Зафиксирована модель данных документа, строк, ролей и статусов.
- В roadmap добавлена опора на стандартные механики Odoo, проверенные через Context7: vendor info, stock transfer/reservation, purchase RFQ.

### Изменено
- Уточнена документированная архитектурная линия проекта в части будущего кастомного supply-request модуля.

### Исправлено
- Нет.

## [2026-03-15] - AIA-007: Knowledge pack Odoo 19
### Добавлено
- `static/knowledge/` — директория с базой знаний по Odoo 19 (JSON-формат)
- `static/knowledge/index.json` — индекс: маппинг модуль → файл + ключевые слова для роутинга
- `static/knowledge/stock.json` — 8 сниппетов: навигация, товары, приёмка, отгрузка, перемещение, инвентаризация, маршруты
- `static/knowledge/crm.json` — 6 сниппетов: навигация, лиды, воронка, активности, выиграно/проиграно, команды
- `static/knowledge/contacts.json` — 6 сниппетов: навигация, создание, типы, теги, редактирование, клиент/поставщик
- `static/knowledge/sale.json` — 6 сниппетов: навигация, котировки, счёт, товары, доставка, отмена
- `static/knowledge/purchase.json` — 6 сниппетов: навигация, RFQ, приёмка, счёт поставщика, прайс, отмена
- `static/knowledge/settings.json` — 7 сниппетов: навигация, настройки, модули, пользователи, группы, компания, язык

---

## [2026-03-15] - AIA-006: Context resolver
### Добавлено
- `services/context_resolver.py` — класс `ContextResolver`:
  - Метод `resolve(raw_context, env)` — фильтрация по whitelist + серверные поля
  - Whitelist: `module`, `action`, `model`, `view_type`, `lang`, `user_groups`, `url`
  - Добавляет `lang` из `env.user.lang`, `user_groups` — имена групп пользователя (не ID)
  - Отбрасывает все поля вне whitelist; санирует длины строк
- `tests/test_context_resolver.py` — 10 unit-тестов
### Изменено
- `static/src/js/ai_chat_service.js` — добавлен `collectContext()`: собирает module, action, model, view_type, url из DOM и URL hash
- `static/src/js/ai_chat_boot.js` — `_callBackend` передаёт `context` в каждом запросе к `/ai_assistant/chat`
- `controllers/chat_controller.py` — подключён `ContextResolver`; добавлен `_build_messages(message, history, context)` — вставляет system-сообщение с контекстом экрана перед историей

---

## [2026-03-15] - AIA-005: OpenRouter client
### Добавлено
- `services/openrouter_client.py` — класс `OpenRouterClient`:
  - Читает конфиг из `ir.config_parameter` (api_key, base_url, model, timeout)
  - Метод `send_chat(messages, max_tokens)` → `{answer, model_used, tokens_used}`
  - Обработка ошибок: Timeout, 429, 5xx, невалидный JSON
  - Безопасное логирование (без api_key и текста сообщений)
- `tests/test_openrouter_client.py` — 2 теста (no api key raises, mocked send_chat)
### Изменено
- `controllers/chat_controller.py` — подключён `OpenRouterClient`:
  - При наличии API key — реальный запрос к OpenRouter
  - При `ValueError` (нет key) — fallback на mock-ответ
  - При `ConnectionError` — возвращает сообщение об ошибке
  - DTO расширен полем `meta.model_used`

---

## [2026-03-15] - AIA-004: Backend controller и DTO
### Добавлено
- `controllers/chat_controller.py` — класс `AiAssistantController`:
  - Endpoint `POST /ai_assistant/chat` (`auth='user'`, `type='json'`)
  - Валидация: пустой message → error, >2000 символов → error
  - History обрезается до 12 записей
  - Mock-ответ: `answer`, `suggestions`, `meta: {mock: True}`
  - try/except с безопасными сообщениями об ошибках
- `tests/test_chat_controller.py` — 3 теста `HttpCase` (mock answer, empty message, too long)

---

## [2026-03-15] - AIA-003: sessionStorage persistence
### Добавлено
- `static/src/js/ai_chat_service.js` — OWL-сервис `aiChatService`:
  - Ключ хранилища: `odoo_ai_assistant_session_v1`
  - Схема: `{ version: 1, messages: [{role, content, timestamp}] }`
  - Методы: `loadHistory()`, `saveHistory(messages)`, `addMessage(messages, role, content)`, `clearHistory()`
  - Лимиты: не более 50 сообщений и 100 КБ (обрезает старые)
  - Проверка версии схемы: при несовместимости сбрасывает историю
  - Очистка при logout: `env.bus.addEventListener("LOGOUT", clearHistory)`
  - Зарегистрирован в `registry.category("services")`
### Изменено
- `static/src/js/ai_chat_boot.js` — подключён `useService("ai_chat")`:
  - `setup()`: история загружается из сервиса при инициализации
  - `_addMessage()`: делегирован в `chatService.addMessage()`
  - `clearSession()`: делегирован в `chatService.clearHistory()`
- `__manifest__.py` — добавлен `ai_chat_service.js` в `web.assets_backend` перед `ai_chat_boot.js`

---

## [2026-03-15] - AIA-002: Floating chat widget
### Изменено
- `static/src/js/ai_chat_boot.js` — полный OWL-компонент `AiChatWidget`:
  - Состояния: `isOpen`, `messages`, `inputText`, `isLoading`, `status`
  - Методы: `toggleChat`, `sendMessage`, `clearSession`, `onSuggestedPrompt`, `_fetchAnswer`
  - Зарегистрирован в `main_components` (floating, не в systray)
  - Вызов `/ai_assistant/chat` (будет подключён в AIA-004)
- `static/src/xml/ai_chat_widget.xml` — полный шаблон:
  - Header: статус-индикатор, кнопки «очистить» и «закрыть»
  - Body: список сообщений user/assistant, suggested prompts, typing indicator
  - Footer: textarea (Enter=отправить, Shift+Enter=новая строка), кнопка отправки, hint
- `static/src/scss/ai_chat_widget.scss` — полные стили:
  - Пузыри сообщений (user — правый/фиолетовый, assistant — левый/серый)
  - Анимация typing (3 точки), slide-in панели
  - Адаптация мобильных (bottom sheet при <768px)

---

## [2026-03-15] - AIA-001: Каркас модуля ai_assistant
### Добавлено
- `custom_addons/ai_assistant/` — новый модуль AI-консультанта для Odoo 19.
- `__manifest__.py` — метаданные модуля (depends: base, web; assets: OWL компонент).
- `static/src/js/ai_chat_boot.js` — OWL-компонент `AiChatWidget` (заглушка), зарегистрирован в `main_components`.
- `static/src/xml/ai_chat_widget.xml` — шаблон компонента (floating button + panel).
- `static/src/scss/ai_chat_widget.scss` — стили: fixed right-bottom, адаптация <768px.
- `security/ir.model.access.csv` — базовый файл прав доступа.
- `tests/test_module_install.py` — тест проверки установки модуля (1 тест, PASS).

---

## [2026-03-15] - Документация структуры и деплоя Odoo 19 (Docker)
### Добавлено
- `docs/rulesworkproject.md` — описание структуры проекта и workflow (Cursor → VPS → деплой через git).
- `docs/deploy.md` — готовая конфигурация деплоя (Traefik + Odoo 19 + Postgres, volumes, шаблон `odoo.conf`, команды запуска/обновления/бэкапов).
- `docs/changelog.md` — журнал изменений.
- `docs/tasktracker.md` — трекинг задач.
- `odoo/` — клонированные исходники Odoo (ветка `19.0`, shallow clone).
- `docker-compose.local.yml` — локальный запуск Odoo 19 на `localhost:8069`.
- `.env.example` — шаблон переменных окружения для локального Docker запуска.
- `config/odoo.local.conf` — локальный конфиг Odoo (DB + addons + data_dir).
- `.gitignore` — исключения для секретов/volumes/бэкапов.
- `tasktreckeragentconsul.md` — детальный архитектурный план AI-консультанта для Odoo через OpenRouter.

### Изменено
- Нет.

### Исправлено
- Нет.
