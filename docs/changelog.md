## [2026-06-16] — fix(object_request): фильтр распределения по складам

### Исправлено
- Путаница тегов «Склады выдачи» с фильтром таблицы: добавлено отдельное поле
  **«Фильтр по складу»** только для отображения.
- «Склады выдачи» переведены на чекбоксы — это настройка разрешённых складов
  выдачи, а не фильтр просмотра.
- Исключение склада из выдачи больше **не удаляет** строки распределения —
  сбрасывается только план `qty_to_issue` (данные «Рассчитать наличие»
  сохраняются).
- Таблица распределения обновляется сразу при смене фильтров
  (`stock_distribution_refresh_key`), без переключения «Показать нулевые остатки».

### Изменено
- Версия модуля: `19.0.1.7.0`.

---

## [2026-06-16] — feat(object_request): склады выдачи и фильтр распределения

### Добавлено
- Поле **«Склады выдачи»** (`issue_warehouse_ids`) на требовании: выбор складов,
  с которых разрешено планировать и оформлять выдачу.
- Переключатель **«Показать нулевые остатки»** на вкладке «Размещение по складам»:
  по умолчанию таблица показывает только строки с остатком, планом выдачи или
  резервом.
- Поисковые фильтры для списка `object.request.line.stock` (есть остаток / к
  выдаче / скрыть нулевые).

### Изменено
- «Рассчитать наличие», «Авто-разбивка», «Выдать максимум» и «Создать выдачу»
  учитывают только выбранные склады выдачи.
- Исключение склада из списка сбрасывает план выдачи с него и удаляет пустые
  строки распределения.
- Новые требования по умолчанию получают все активные склады компании в
  `issue_warehouse_ids`.
- Версия модуля: `19.0.1.6.0`.

### Проверено
- `TestObr034IssueWarehouseFilter`: 5/5 pass.

---

## [2026-06-14] — feat(object_request): проектные справочники размещения строк

### Добавлено
- Концепт `Зона` переименован в `Захватка` для пользовательского описания места выполнения работ.
- Добавлены независимые справочники размещения в разрезе объекта:
  `object.request.project.capture`, `object.request.project.floor`,
  `object.request.project.section`.
- В форме `object.request.project` появились редактируемые вкладки со списками
  `Захватки`, `Этажи`, `Участки`.
- В строках требования добавлены Many2one-поля `capture_id`, `floor_id`,
  `section_id`; старые текстовые поля `zone`, `floor`, `section` сохранены как
  переходный fallback.
- Добавлена кнопка «Отсортировать строки»: порядок строк строится по
  `Захватка → Этаж → Участок → Поставщик`.

### Изменено
- Печатные формы требований и выдач показывают названия новых Many2one-записей
  и используют старые текстовые значения только как fallback.
- Версия миграции `19.0.1.5.0` переносит существующие текстовые значения в
  проектные справочники, создаёт записи по каждому объекту и назначает
  `capture_id`/`floor_id`/`section_id` строкам требования.

### Проверено
- `flake8` чист.
- Focused tests `TestObjectRequestProjectLocations`: 5/5 pass.
- Полный suite `object_request`: 358 tests, 0 failed, 0 errors.

---

## [2026-06-14] — fix(object_request): прокрутка таблицы строк требования

### Исправлено
- Таблица строк требования получила собственную область прокрутки, чтобы
  горизонтальный scrollbar был доступен внутри вкладки «Строки», а не только
  у нижней границы всей страницы.

---

## [2026-06-14] — fix(object_request): мгновенное обновление UI после AI-действий

### Исправлено
- После нажатия «Принять AI» или «Отклонить AI» форма требования теперь
  сразу перезагружается, чтобы цвет строки и видимость AI-кнопок обновлялись
  без ручного обновления страницы.

---

## [2026-06-14] — fix(object_request): разделение артикула и технического обозначения

### Изменено
- Версия модуля `object_request` повышена до `19.0.1.4.0`.
- Excel-колонка `Обозначение` больше не считается артикулом поставщика: реальные артикулы остаются в `supplier_article`, а технические обозначения, ГОСТ, Ду/Ру, модели и строки вида `L=...` сохраняются в `technical_designation`.
- Combined search, scoring и LLM-shortlist используют `technical_designation` как контекст строки потребности, но не применяют его для exact matching через `product.supplierinfo` или `default_code`.
- Поиск памяти сопоставлений теперь предпочитает точную пару `name + designation` и безопасно откатывается к записям без designation.

### Исправлено
- Исправлен Excel import/matching для `OR/2026/06/0014` и `OR/2026/06/0016`: технические значения из `Обозначение` (`L=0.13`, `21.3`, `Ду 80`, `ГОСТ`, модельные строки) больше не подавляют генерацию кандидатов и не трактуются как ключи supplierinfo/default_code.
- Миграция `custom_addons/object_request/migrations/19.0.1.4.0/post-migrate.py` переносит старые значения `supplier_article` в `technical_designation` и очищает `supplier_article` для затронутых документов `OR/2026/06/0014` и `OR/2026/06/0016`.

### Проверено
- `flake8` чист по изменённым файлам.
- Focused Odoo tests: `TestObr028CombinedMatching` + `TestObr032Memory` — 22/22 pass.
- Полный suite `object_request` был зелёным после реализации: 353/353 в test-runner после debugger; ранее 727 full module run без функциональных failures до исправления lint.

---

## [2026-06-14] — feat(object_request): LLM-Assisted Matching v2 (этапы 7–11)

### Добавлено
- AI-поля и режим `ai_mode` (none/suggest/auto) в wizarde импорта Excel
- Модель `object.request.matching.memory` — хранит подтверждённые сопоставления, используется до LLM
- `_get_ai_config()` — чтение конфигурации AI из `ir.config_parameter`
- Логирование AI-действий в chatter заявки (`_post_ai_candidates_note`)
- Rate limiting (`batch_size`) для LLM-вызовов в `action_prepare_ai_candidates`

### Изменено
- `action_accept_and_remember_ai_candidate`: теперь сохраняет И в память, И в `product.supplierinfo`
- `build_candidates`: проверяет память перед детерминированным поиском
- `object_request_project.code`: `size=5` → `size=10` (предотвращение коллизий при длинных тест-сессиях)
- Версия модуля: `19.0.1.2.0` → `19.0.1.3.0`

### Исправлено
- Регрессия `test_obr032`: `groups_id` → `group_ids` (Odoo 19)
- ACL matching_memory: снабженец получил права на создание/изменение записей

### Проверено
- 346 тестов, 0 failed, 0 errors
- flake8 чист по всему модулю `object_request`

---

## [2026-06-14] — feat(object_request): UI действий AI-кандидатов (этап 6)

### Добавлено
- На форме требования добавлены кнопки «Подобрать AI-кандидатов» и
  «Применить уверенные AI-сопоставления».
- На строках требования добавлены поля AI-подсказок:
  `ai_suggested_product_id`, `ai_match_confidence`, `ai_match_reason`,
  `ai_candidate_product_ids`.
- Добавлены действия строки: «Принять AI», «Отклонить AI»,
  «Принять и запомнить».
- Массовое применение пишет товар только для подсказок с confidence `>= 0.90`;
  low-confidence строки остаются без изменения.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request /mnt/extra-addons/custom_product_search`
- `docker exec odoo19-local odoo --test-enable --test-tags /object_request -u object_request -d odoo19_local --stop-after-init --http-port=8071` — 326 post-tests, 0 failed, 0 errors.

---

## [2026-06-14] — feat(object_request): LLM-rerank сервис (этап 5)

### Добавлено
- Сервис `object.request.llm.matching.service` (AbstractModel): принимает shortlist
  кандидатов, формирует prompt, вызывает `OpenRouterClient.send_chat`, валидирует
  JSON-ответ и возвращает структурированный результат без записи в БД.
- Системный prompt: LLM оценивает `name_raw` + `supplier_article` вместе, выбирает
  только из переданного shortlist, добавляет `risk_flags` при конфликте размеров.
- Валидация ответа LLM: `decision` из allowlist, `product_id` строго из shortlist,
  `confidence` в `0..1`, critical risk_flags снижают confidence до ≤ 0.85.
- Пороги: `≥ 0.90` + нет критических флагов → `auto_applicable = True`;
  `0.70..0.89` → предложить снабженцу; `< 0.70` → manual review.
- Graceful fallback: любая ошибка (нет ключа, timeout, 429, невалидный JSON,
  недоступная модель) возвращает `decision="error"` без исключения наружу.
- Тест `test_obr029_llm_matching.py` — 9 тестов с mock OpenRouter.

### Проверено
- `flake8` — чисто по `object_request/models/llm_matching_service.py` и тестам.
- 318 тестов `object_request`, 0 failed, 0 errors.

---

## [2026-06-14] — feat(object_request): MVP v2 сопоставления Excel-строк

### Добавлено
- Кнопка «Пересопоставить все строки» в требовании: пересматривает auto-matched строки, пишет старый товар в `matching_note`, очищает старые автоматические совпадения, если новый алгоритм не нашёл товар.
- Защита ручного выбора товара при all-lines rematch через консервативную эвристику по `matching_note`.
- Combined query `name_raw + supplier_article` в `object.request.excel.parser`, классификация строк `length_or_pipe_fragment`, `empty_article`, `ambiguous`, `product_candidate`.
- Shortlist кандидатов через `product.product.ai_search_products()` без LLM; несколько/спорные кандидаты не применяются автоматически.
- Сервис `object.request.matching.candidate.service`: собирает кандидатов из `supplierinfo`, `default_code`, `name_score`, combined search, дедуплицирует по товару и отдаёт лимиты 15/8/3 для internal/LLM/preview.
- Поле `matching_source` на строке требования: импорт, rematch, combined auto и ручной выбор теперь различаются явно; защита all-lines rematch больше не зависит от текста `matching_note`.
- Маркер `matching_note = "import auto match"` для новых строк, сопоставленных при импорте.
- Зависимость `object_request` от `custom_product_search`.

### Изменено
- Нормализация `custom_product_search` синхронизирована с техническими обозначениями импорта: `Ду/Ру/DN/PN`, `х/x/×`, десятичная запятая/точка.
- `docs/deploy.md` дополнен явной инструкцией recompute stored `x_search_name` после изменения нормализации и backfill старых `matching_source`.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request /mnt/extra-addons/custom_product_search`
- `docker exec odoo19-local odoo --test-enable --test-tags /object_request -u object_request -d odoo19_local --stop-after-init --http-port=8071` — 307 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --test-enable --test-tags /custom_product_search -u custom_product_search -d odoo19_local --stop-after-init --http-port=8071` — 6 post-tests, 0 failed, 0 errors.

---

## [2026-06-13] — feat(object_request): улучшенное автосопоставление Excel-импорта

### Добавлено
- Нормализация артикулов и названий при импорте: `ё/е`, NBSP, `Ду/Ру`, размеры через `х/x/×`, десятичная запятая/точка.
- Консервативный token-scoring для сопоставления товаров по названию с порогом уверенности и запретом авто-match для однословных запросов без обозначения.
- «Память сопоставлений» через явное действие «Запомнить сопоставление»: создаётся `product.supplierinfo` по подтверждённой паре артикул/товар/поставщик.
- Обработка конфликтных supplierinfo: при разных товарах на один артикул без поставщика авто-сопоставление запрещено, кандидаты показываются в preview импорта.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
- `docker exec odoo19-local odoo -u object_request -d odoo19_local --test-enable --test-tags /object_request --stop-after-init --http-port=8071` — 291 post-tests, 0 failed, 0 errors.

---

## [2026-06-12] — docs: TD-007 — превью изображения товара в колонке «Товар»

### Добавлено
- `docs/technical-debt.md` — **TD-007**: превью `image_128` при наведении на пункт выпадающего списка номенклатуры в колонке «Товар» таблицы строк требования на комплектацию (`object_request`).

---

## [2026-06-12] — feat(ai_assistant): контрагенты через чат

### Добавлено
- Справочник категорий контрагентов (`Поставщик`, `Заказчик`, `Покупатель`, `Подрядчик`) с маппингом на ранги и теги.
- Tools: `update_partner_draft`, `add_partner_bank_draft`, `add_partner_contact_draft`.
- `create_partner_draft` теперь принимает обязательную категорию, `ref`, регион и создаёт тег категории.
- `find_partner` поддерживает `role=any|supplier|customer` и возвращает ранги, теги и город.
- Prompt-правила для сценария контрагентов, chips выбора категории и knowledge doc `static/knowledge/docs/partner_workflow.md`.
- UI-карточки подтверждения/результата для новых tools.
- ACL для группы `AI Assistant / Снабжение` на партнёров, теги, банки и банковские счета без `sudo()`.

### Проверено
- `docker exec odoo19-local python3 -m flake8 ...`
- `docker exec odoo19-local /bin/bash -lc "odoo -u ai_assistant -d odoo19_local --test-enable --stop-after-init --http-port=8071 ..."` — 0 failed, 0 error.

---

## [2026-06-12] — docs: переименование трекера контрагентов v2

### Изменено
- `docs/plan-ai-assistant-partner-workflow.md` переименован в `docs/tasktrecker-creat-partner-v2.md`; обновлены ссылки в `tasktracker.md`, `changelog.md`, скилле `odoo-add-partner`, `tasktrecker-creat-partner.md`.
- `docs/tasktrecker-creat-partner-v2.md` переформатирован в принятый в проекте вид пошаговых задач (CPV-001…014: статус, приоритет, шаги-чекбоксы, зависимости, DoD, порядок инкрементов).

---

## [2026-06-12] — docs: план доработки ai_assistant (контрагенты через чат)

### Добавлено
- `docs/tasktrecker-creat-partner-v2.md` — трекер реализации workflow контрагентов в чате ассистента: новые tools (`update_partner_draft`, `add_partner_bank_draft`, `add_partner_contact_draft`), категория-enum с маппингом на ранги и теги, правила в системном промпте, chips категорий, UI-карточки, тесты.
- Задача в `docs/tasktracker.md` с этапами 1–5.

### Изменено
- Скилл `odoo-add-partner`: правила обновления существующего контрагента (только пустые поля, не обнулять ранги, запрет смены ИНН, поиск по имени с выбором кандидата), раздел синхронизации с `ai_assistant`.

---

## [2026-06-12] — docs(skills): добавление контрагента в Odoo

### Добавлено
- `.cursor/skills/odoo-add-partner/SKILL.md` — проектный скилл для создания и обновления контрагентов в Odoo через MCP.
- В скилле закреплены: явная команда перед записью в Odoo, проверка дубликатов по ИНН, обязательное уточнение категории (`Поставщик`, `Заказчик`, `Покупатель`, `Подрядчик`), создание тега категории, заполнение банковских реквизитов и контактных лиц.

---

## [2026-06-12] — feat(ai_assistant): статус поставщика при upload + ИНН-первый поиск (счёт 2594)

### Добавлено
- После upload счёта в `summary` явно пишется: ✅ «Поставщик найден в Odoo: … (id N)» или ⚠ предупреждение.
- `_execute_tool_call` при вызове `find_partner` + активный `extraction_token` подставляет ИНН из счёта вместо текстового запроса LLM.
- В системный промпт добавлено правило: при поиске поставщика из счёта всегда использовать `supplier_extracted.inn`.

---

## [2026-06-12] — feat(ai_assistant): LLM-fallback для извлечения поставщика из счёта

### Добавлено
- `services/invoice_parsing/llm_header_extractor.py` — вызывает LLM через `OpenRouterClient` когда regex не смог распознать `supplier.name` или `inn`. Отправляет только шапку (до таблицы, ≤80 строк), экономя токены. Валидирует ИНН/КПП в ответе.
- `extract_invoice(file_bytes, env=None)` — новый опциональный параметр `env`. При наличии env и пустом name/inn включается LLM fallback. Без env (тесты, внешние вызовы) поведение не изменилось.
- Если LLM заполнил поля — добавляется предупреждение `llm_header: поставщик распознан через LLM`.
- 4 новых теста: fallback вызван, не вызван при успехе regex, не вызван без env, не перезаписывает найденное regex.

### Изменено
- `controllers/chat_controller.py`: `extract_invoice` теперь вызывается с `env=request.env`.

---

## [2026-06-12] — fix(ai_assistant): поставщик «имя до Поставщик:» (счёт 1214 / Пензапромарматура)

### Исправлено
- `_SUPPLIER_RE` и `_BUYER_RE` не матчат словоформы «Поставщика», «Покупателя» (добавлен `(?![а-яёА-ЯЁA-Za-z])`).
- Новый формат: `Поставщик: <ИНН_число>` — название берётся из строки выше, краткая форма из скобок `(ООО ...)` предпочтительна.
- Голый ИНН в начале блока поставщика не путается с ИНН покупателя.

### Добавлено
- Тест `test_supplier_name_before_inline_label_inv1214` в `test_invoice_parsing.py`.

---

## [2026-06-12] — fix(ai_assistant): поставщик в счётах «ИНН первым» (счёт 234 / ООО ЭСКО 3Э)

### Исправлено
- Если строка поставщика начинается с ИНН (`ИНН … КПП … ООО "Название" адрес`), имя теперь извлекается корректно через `_ORG_NAME_AFTER_INN_RE`.
- `_extract_address` больше не матчит 6 цифр внутри ИНН/КПП (`816402` из `7733816402`); добавлены `(?<!\d)` / `(?!\d)` вокруг шаблона почтового индекса.
- `_compose_supplier_address` обрезает продолжение от `тел.` (и без двоеточия) и от строки следующего контрагента.

### Добавлено
- Тест `test_supplier_name_after_inn_block_inv234` в `test_invoice_parsing.py`.

---

## [2026-06-12] — fix(ai_assistant): поставщик в счётах 1С/Т-Банк (ЦБ-675)

### Исправлено
- Парсер счёта: если реквизиты поставщика (`ООО …`, ИНН) стоят **на строке выше** метки «Поставщик:», а после метки — только продолжение адреса, в `supplier.name` больше не попадает «дом № …, тел.: …» (счёт ЦБ-675 / ООО «АРМОСТ»).
- Покупатель: блок обрезается перед таблицей позиций (`№ Товары`), а не до конца PDF.

### Добавлено
- Тест `test_supplier_name_from_line_before_label_cb675` в `test_invoice_parsing.py`.

---

## [2026-06-12] — feat(ai_assistant): поставщик из счёта

### Добавлено
- `create_partner_draft`: создание нового поставщика `res.partner` из реквизитов счёта только после ConfirmationCard; ИНН обязателен, дубликат по `vat` блокируется, банковские реквизиты не переносятся.
- Invoice workflow теперь ведёт сценарий в порядке поставщик → товары → PO; PO draft использует `created_partner_id` из invoice-сессии.
- UI чата показывает chip «Создать поставщика…», preview реквизитов поставщика и ResultCard со ссылкой на карточку.
- `tests/test_e2e_unknown_supplier_invoice_to_po.py`: E2E неизвестный поставщик → `create_partner_draft` → `create_product_draft` → `create_purchase_order_draft`.

### Проверено
- `docker exec odoo19-local odoo --test-enable --test-tags /ai_assistant -d odoo19_local --stop-after-init --http-port=8071`

---

## [2026-06-11] — docs: TD-006 — неверный итог «к оплате» в счёте Метиз Комплект

### Добавлено
- `docs/technical-debt.md` — **TD-006**: разобрать и исправить извлечение суммы «к оплате» для счёта `ЗаказПокупателя_ООО_«ДВ_Партнёр»_МК000051249_10_06_2026.pdf` (14 560 ₽ вместо 17 185,57 ₽; предупреждение валидации НДС).

---

## [2026-06-11] — fix(ai_assistant): устаревшая модель OpenRouter и заглушка чата

### Исправлено
- `google/gemini-2.0-flash-001` снята с OpenRouter (01.06.2026) → HTTP 404 маскировался заглушкой «Я пока не подключён к AI…»; вместо mock теперь понятное сообщение об ошибке.
- Дефолтная текстовая модель: `google/gemini-2.5-flash`; улучшена обработка HTTP 401/404/4xx в `OpenRouterClient`.
- `/ai_assistant/upload_invoice`: тексты предупреждений валидации счёта выводятся в сводке сразу после загрузки.

### Изменено
- Рекомендация в настройках AI-консультанта обновлена на `google/gemini-2.5-flash`.

---

## [2026-06-11] — docs: черновик user guide AI-ассистента

### Добавлено
- `docs/ai-assistant-user-guide.md` — черновик руководства для конечного пользователя Odoo: краткий перечень возможностей, расширенное описание процессов и tools, план перспективных функций на основе цикла снабжения и техдолга (TD-002, TD-003).

---

## [2026-06-10] — fix(object_request): закупка из OR в Odoo 19

### Исправлено
- `object.request.purchase.wizard`: убрана ссылка на удалённое в Odoo 19 поле `product.uom_po_id`; единица закупки берётся из `line.uom_id` или `product.uom_id`.

---

## [2026-06-10] — feat(object_request): гибкий Excel-импорт Wizard V2

### Добавлено
- `object.request.import.wizard` определяет назначение колонок Excel по заголовкам и поддерживает синонимы для артикула/обозначения, наименования, единицы измерения, количества, цены, комментария и поставщика.
- Поддержан формат спецификации УУТЭ: `Наименование`, `Обозначение`, `Единица измерения`, `Количество`; `Обозначение` сохраняется как артикул поставщика.
- Сообщения валидации показывают распознанный формат, найденные заголовки и поддерживаемые варианты при отсутствии обязательных колонок.

### Изменено
- Preview импорта показывает колонку `Артикул / Обозначение`.
- `_build_preview_vals()` читает строки через mapping колонок, сохраняя существующую нормализацию, matching товаров/поставщиков и номера строк Excel.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request/wizards/import_excel_wizard.py /mnt/extra-addons/object_request/tests/test_obr006_wizard.py`
- `docker exec odoo19-local odoo --test-enable -u object_request -d odoo19_local --stop-after-init --http-port=8071`

---

## [2026-06-09] — chore(warehouse): финализация WHM-005/WHM-010 и legacy остатки

### Выполнено
- WHM-005: тестовый `ОбМ-1/INT/00002` отменён штатным `stock.picking.action_cancel`; тестовые остатки `ОбМ-1` обнулены через inventory adjustment; `ОбМ-1` архивирован.
- `ОбМ-1`, `ОбМ-3`, `ОбМ-5` теперь inactive; на тестовых складах нет ненулевых quants.
- WHM-010: регламент обновлён под production-схему `O001` (Ломоносова 164) и `O002` (Б. Хмельницкого, 112).

### Изменено
- `search_stock_quants` нормализует legacy `warehouse_codes`: `ОбМ-2` → `O001`, `ОбМ-4` → `O002`.
- Документация снабжения и technical debt обновлены: новые операции должны использовать `O001/O002`, legacy `ОбМ-*` остаются только как временные aliases.

### Проверено
- Prod: `ОбМ-1/INT/00002` в `cancel`; `ОбМ-1`, `ОбМ-3`, `ОбМ-5` inactive; ненулевые quants на них отсутствуют.

---

## [2026-06-09] — chore(warehouse): WHM-008–WHM-009 stage/prod validation

### Выполнено
- WHM-008: свежий prod dump восстановлен в локальную stage-БД `odoo19_whm_stage`; upgrade `object_request,ai_assistant` прошёл без ошибок.
- WHM-009: финальный prod smoke выполнен на базе `odoo19` после деплоя и рестарта контейнера `odoo`.
- `find_warehouse("O")` исправлен как односимвольный префикс для production-складов `O001/O002`; обычные слишком короткие запросы по-прежнему отклоняются.
- Rollback-smoke создает OR/PO/internal picking для `O001` и `O002` и затем откатывает транзакцию.

### Проверено
- Stage report: `docs/reports/whm_008_2026-06-09-stage.json`.
- Prod report: `docs/reports/whm_009_2026-06-09-prod-smoke.json`.
- Prod validation: `O001` — 17 quant rows / total qty `200.00`; `O002` — 16 quant rows / total qty `1668.00`.
- AI Assistant: `O001`, `O002`, `O`, `Ломоносова`, `Хмельницкого`, `ОбМ-2`, `ОбМ-4`.

### Backup
- WHM-008/009: `/opt/project_odoo/backups/whm-008-009-20260609-220424/`.

---

## [2026-06-09] — chore(warehouse): WHM-005–WHM-007 prod follow-up

### Выполнено
- WHM-005: архивированы тестовые склады `ОбМ-3` и `ОбМ-5`; физического удаления складов, документов и остатков не выполнялось.
- `ОбМ-1` оставлен активным: архивирование заблокировано незавершенным `ОбМ-1/INT/00002` (`confirmed`, origin `OR/2026/05/0004`), остатки сохранены.
- WHM-006: добавлена migration `object_request` `19.0.1.2.0/post-migrate.py`, версия модуля поднята до `19.0.1.2.0`.
- WHM-007: AI Assistant переведен на определение объектного склада через `object.request.project.warehouse_id`, добавлены legacy aliases `ОбМ-2 -> O001`, `ОбМ-4 -> O002`.
- Prod upgrade `object_request,ai_assistant` выполнен, контейнер `odoo` перезапущен.

### Проверено
- Local `/ai_assistant`: 327 post-tests, 0 failed, 0 errors.
- Prod smoke: `find_warehouse("ОбМ-4") -> O002`, `find_warehouse("ОбМ-2") -> O001`, validators проходят для `O001/O002`.

### Backup
- WHM-005: `/opt/project_odoo/backups/whm-005-20260609-214301/`.
- WHM-006/007: `/opt/project_odoo/backups/whm-006-007-20260609-215752/`.

---

## [2026-06-09] — chore(object_request): WHM-001–WHM-004 prod warehouse migration

### Выполнено
- Production backup перед миграцией: `/opt/project_odoo/backups/whm-001-004-20260609-0636/`.
- Warehouse id `10`: `ОбМ-2` → `O001`, имя → `Ломоносова 164 склад`; локации и picking types сохранены.
- Warehouse id `16`: `ОбМ-4` → `O002`, имя → `Б. Хмельницкого, 112 склад`; локации и picking types сохранены.
- Созданы production projects `O001`/`O002`, привязанные к warehouse id `10`/`16`.
- Тестовые projects `O001`–`O004` архивированы как `X001`–`X004`; физического удаления складов/остатков не выполнялось.

### Отчеты
- `docs/reports/whm_001_004_2026-06-09-prod.json` — prod audit/action/validation report.
- `docs/reports/whm_001_004_2026-06-09.json` — локальный diagnostic run.

---

## [2026-05-31] — fix(ai_assistant): дублирование карточки, LLM обходит workflow

### Исправлено
- `_confirmPending` (JS): убрано дублирование result card — карточка теперь вставляется только в исходное сообщение через `_markPendingCardResolved`.
- `_dispatch_invoice_workflow`: перехват ключевых фраз «добавь на склад», «создай закупку» и т.д. до LLM — если есть незавершённые карточки, сначала workflow товаров.

### Изменено
- Промпт INVOICE_CONTEXT: жёсткий порядок (шаг A — все карточки, шаг Б — PO); запрет `create_purchase_order_draft` при наличии `needs_create_product_draft=true`.

---

## [2026-06-01] — fix(ai_assistant): увеличен rate limit write-операций

### Изменено
- `ToolRateLimiter`: `write_max` увеличен с 5 до 25 для workflow создания карточек по счёту (9+ товаров).

---

## [2026-05-31] — feat(ai_assistant): пошаговый workflow счёта (товар → PO)

### Добавлено
- `InvoiceWorkflow` и сессия `created_by_line` в `InvoiceExtractionStore`.
- `create_product_draft`: `list_price`, `standard_price`, `default_code`; цена подтягивается из счёта при pending.
- После каждого товара — кнопки «Создать следующий» / «Создать закупку на склад»; PO с qty/price из счёта.
- UI: chips suggestions в сообщениях ассистента.
- Тесты `test_invoice_workflow.py`.

### Изменено
- `/ai_assistant/confirm` — suggestions и tracking по `extraction_token`.
- Промпт: один товар за подтверждение.

---

## [2026-05-31] — feat(ai_assistant): PO на любой склад (не только ОбМ-*)

### Изменено
- `create_purchase_order_draft`: вместо `validate_picking_type_is_object` — `validate_picking_type_for_purchase` (любой склад с incoming picking type).
- Промпт, `invoice_context_helper`, `supply_cycle_context.md`: уточнение склада через `find_warehouse` по коду/названию (`Ос.ск`, «Основной склад» и т.д.).
- Внутренние перемещения по-прежнему только на склады объектов `ОбМ-*`.

### Добавлено
- Тесты `validate_picking_type_for_purchase_*`, `test_create_purchase_order_accepts_non_object_picking_type`.

---

## [2026-05-31] — chore: prod Docker Compose и Dockerfile для VPS

### Добавлено
- `docker-compose.yml` — production-стек Odoo + Postgres (сеть `n8n_web` для reverse proxy на VPS).
- `docker-compose.override.yml` — сборка кастомного образа `project-odoo-odoo:latest` с pdfplumber.

### Изменено
- `Dockerfile`: `pip install --break-system-packages` для Odoo 19 (Debian Bookworm).
- `.gitignore`: исключены `backups/` и `Dockerfile.bak.*`.

---

## [2026-05-31] — fix(ai_assistant): дефолтная категория товара для Odoo 19

### Исправлено
- `CreateProductDraftTool._default_category_id`: заменён устаревший XML ID `product.product_category_all` (Odoo ≤16) на `product.product_category_goods` с fallback через `search`.
- `object_request/data/demo_data.xml`: родитель категории «Строительные материалы» — `product.product_category_goods`.

### Добавлено
- Тест `test_create_product_draft_uses_default_category_when_omitted` — проверка создания товара без явного `categ_id`.

### Изменено
- `group_ai_assistant_supply`: добавлено право `product.group_product_manager` для `create_product_draft`.

---

## [2026-05-30] — feat(AIA-060): E2E «НФ-504 → PO draft»

### Добавлено
- `tests/test_e2e_nf504_invoice_to_po.py` — сквозной тест: фикстура нормализованного счёта НФ-504 (14 позиций, поставщик ИП Татаринов, 72 096,22 ₽) → `InvoiceContextHelper` (partner matched, 1 not_found) → `create_product_draft` → `create_purchase_order_draft` (14 строк) → state=draft, chatter.

---

## [2026-05-30] — feat(AIA-059): ResultCard — инструкции Confirm→Validate после создания PO

### Добавлено
- `_next_steps(tool_name)` в `chat_controller.py` — пошаговые инструкции для каждого write-tool: PO (5 шагов: Confirm → Receipt → Validate → напоминание 1С), internal picking, OR, product draft.
- Поле `steps` в `ResultCard` (backend JSON, OWL props, XML-рендер нумерованным списком, SCSS `.o_ai_result_steps`).
- Тест `test_result_card_po_has_confirm_validate_steps` в `test_chat_controller.py`.

### Изменено
- `controllers/chat_controller.py`: `_result_card_success` возвращает `steps` + `next_hint = steps[0]`.
- `static/src/js/ai_chat_actions.js`: `ResultCard.props` — добавлен `steps: Array (optional)`.
- `static/src/xml/ai_chat_widget.xml`: рендер `steps` как `<ol>` при наличии, иначе `next_hint`.
- `static/src/scss/ai_chat_widget.scss`: стили `.o_ai_result_steps`.

---

## [2026-05-30] — feat(AIA-057): InvoiceContextHelper + инъекция данных счёта в промпт

### Добавлено
- `services/invoice_context_helper.py` — сопоставление счёта с `find_partner` (ИНН) и `search_products` (позиции), system-блок `INVOICE_CONTEXT`.
- Тесты `tests/test_invoice_context_helper.py` и интеграционный тест инъекции в `test_chat_controller.py`.

### Изменено
- `controllers/chat_controller.py`: параметр `extraction_token` в `/ai_assistant/chat`, инъекция контекста в `_get_tools_response` (actions-режим).
- `services/prompt_builder.py`: правило §7 в `_ACTIONS_RULES_BLOCK` — сопоставление позиций, уточнение объекта/склад (D3), план PO, `create_product_draft`.
- `static/src/js/ai_chat_boot.js`: хранение и передача `extraction_token` после загрузки счёта.

---

## [2026-05-30] — feat(AIA-058): write-tool create_product_draft

### Добавлено
- `CreateProductDraftTool` — создание storable `product.product` после подтверждения (группа supply): `name`, `categ_id`, `uom_id`, `purchase_ok`, `sale_ok`; без запрещённых полей `state`/`company_id`/`currency_id`.
- Проверка дубля по `name`+`categ_id`, `idempotency_key`, заметка в chatter шаблона товара.
- Тесты в `test_write_tools.py`; `ResultCard` поддерживает `product.product`.

---

## [2026-05-30] — feat(AIA-056): эндпоинт /upload_invoice + кнопка-скрепка в чат-виджете

### Добавлено
- `services/invoice_extraction_store.py` — TTL-хранилище (30 мин) результатов парсинга счетов по uid+token.
- `controllers/chat_controller.py`: маршрут `POST /ai_assistant/upload_invoice` (multipart, auth=user, только supply); валидация расширения/размера (5 МБ)/magic bytes; сводка + `extraction_token` в ответе.
- `static/src/js/ai_chat_service.js`: функция `uploadInvoice(file)` — fetch multipart к эндпоинту.
- `static/src/js/ai_chat_boot.js`: `hasSupply` state, `fileInputRef`, `onAttachClick`, `onFileSelected`, `_uploadInvoice` — полный цикл загрузки с превью в чате.
- `static/src/xml/ai_chat_widget.xml`: кнопка-скрепка + hidden `<input type="file">` (только для supply).
- `static/src/scss/ai_chat_widget.scss`: стили `.o_ai_attach_btn`, `.o_ai_file_input_hidden`.
- `tests/test_upload_invoice.py` — 8 HttpCase тестов: happy-case (mock), отказ по типу/размеру/magic, parse error, access control.

### Изменено
- `controllers/chat_controller.py`: `check_access` теперь возвращает `has_supply`; добавлен `import json` в заголовок.
- `security/security_groups.xml`: добавлен `base.user_admin` в `group_ai_assistant_supply` (паритет с admin group).
- `tests/__init__.py`: добавлен `test_upload_invoice`.

---

## [2026-05-30] — feat(AIA-055): порт парсера счетов в services/invoice_parsing/

### Добавлено
- `custom_addons/ai_assistant/services/invoice_parsing/` — новый пакет (5 файлов): `__init__.py`, `extractor.py`, `invoice_utils.py`, `normalizer.py`, `validators.py`.
- `extractor.py`: text-first парсинг PDF через `pdfplumber` (bytes-интерфейс); поддержка НФ-504/УТ-1132 номеров; эвристика по строкам как fallback; валидация magic bytes.
- `invoice_utils.py`: `extract_party_name` (до ИНН), `is_garbage_item` (фильтр мусора).
- `normalizer.py`: нормализация числовых полей, дат, ИНН/КПП/БИК.
- `validators.py`: арифметическая проверка qty×price=sum + сумма строк=итого.
- `tests/test_invoice_parsing.py` — 20 unit-тестов с mock pdfplumber, фикстура НФ-504 (14 позиций, 72 096,22 ₽, поставщик ИП Татаринов).

---

## [2026-05-30] — feat(AIA-054): pdfplumber как external dependency + Dockerfile для образа

### Добавлено
- `Dockerfile` поверх `odoo:19.0` — устанавливает `pdfplumber>=0.11` при сборке образа.
- `custom_addons/ai_assistant/requirements.txt` — фиксирует зависимость `pdfplumber>=0.11`.
- `CLAUDE.md`: команды пересборки образа (`docker compose build`) и проверки (`import pdfplumber`), предупреждение о потере зависимостей при работе без `build`.

### Изменено
- `custom_addons/ai_assistant/__manifest__.py` — добавлен `'external_dependencies': {'python': ['pdfplumber']}`.
- `docker-compose.local.yml` — сервис `odoo` переключён с `image: odoo:19.0` на `build: .` (образ `odoo19-local-custom`).

---

## [2026-05-30] — docs: план приёмки товаров из счёта в чат-ассистенте (V3-10)
### Добавлено
- `docs/roadmap_ai_assistant_v3_invoice.md` — план внедрения сквозного сценария «счёт → склад» в чат-ассистент: загрузка файла, парсинг внутри Odoo, черновики через API, инструкции UI.
- Задачи **AIA-054…060** (этап V3-10) в `docs/tasktracker_ai_assistant_v3.md` + строки в сводной таблице и инкремент 6.
### Решения
- D1: парсинг счетов внутри Odoo (порт логики `invoice-extractor`, без внешней сети). D2: авто-черновик товара `create_product_draft` с подтверждением. D3: склад приёмки всегда уточняется у пользователя.

---

## [2026-05-24] — fix: кнопки «Попробуйте спросить» в чате AI
### Исправлено
- Клик по suggested prompt падал с `Cannot read properties of undefined (reading 'state')`: в OWL-шаблоне вызов без `this.onSuggestedPrompt`.

---
### Исправлено
- URL `/odoo/stock-report?search_warehouse=...` не применял фильтр: Odoo 19 не передаёт `search_warehouse` из query string в context action.
- Ссылка теперь ведёт на server action `/odoo/ai-warehouse-stock?active_id=<warehouse_id>`, который открывает stock-report с `search_warehouse` и фильтром «Available Products» в context.
- В search view stock-report добавлено поле `warehouse_id` для отображения активного фильтра.

---

## [2026-05-24] — feat: AIA-053.UI кликабельные ссылки в чате
### Добавлено
- Кнопки-ссылки под ответом ассистента из `links[]` API и markdown `[label](url)`.
- Сырой URL убирается из текста пузыря; клик ведёт на `/odoo/...` в той же вкладке.

### Изменено
- `ai_chat_widget.xml`, `ai_chat_boot.js`, `ai_chat_format.js`, `ai_chat_service.js`.

---

## [2026-05-24] — feat: AIA-052 get_warehouse_stock_link
### Добавлено
- Read-tool `get_warehouse_stock_link`: URL отчёта `/odoo/stock-report?search_warehouse=...` по складу.
- `WarehouseStockLinkHelper`: server-side подстановка ссылки (в т.ч. склад из history чата).
- Правила промпта и обновление `navigation_map.md`.

### Проверено
- `test_warehouse_stock_link_helper.py`, `test_read_tools`, `test_chat_controller`.

---

## [2026-05-24] — fix: server-side навигация при (None) от LLM
### Исправлено
- `NavigationHelper`: сервер определяет навигационные вопросы, вызывает `get_navigation_link` до LLM и подставляет URL в ответ (замена `(None)` или дополнение ссылки).
- Алиас темы «заказы на закупку» в `NAVIGATION_CATALOG`.
- Read-tools отдают LLM плоский JSON (`url`, `label`) без обёртки `{success, result}`.

### Проверено
- `test_navigation_helper.py`, `test_chat_controller.test_consult_mode_enriches_none_navigation_link`.

---

## [2026-05-24] — fix: навигационные ссылки (None) в consult-режиме
### Исправлено
- Consult-режим теперь вызывает `send_chat_with_tools` только с read-tools (`get_navigation_link`, `find_warehouse` и др.); write-tools недоступны без группы «Снабжение».
- Промпт: запрет ссылок `(None)`; url берётся только из `result.url` ответа tool.

### Проверено
- `TestChatController` — 16 post-tests, 0 failed.

---

## [2026-05-24] — fix: actions mode с скриншотом + уникальные t-key карточек
### Исправлено
- `chat_controller`: в режиме actions запрос со скриншотом больше не уходит в `send_chat()` без tools — используется `_get_actions_response()` / `send_chat_with_tools()` с vision-моделью.
- `ai_chat_widget.xml` / `ai_chat_boot.js`: ключи `t-foreach` для cards уникальны (`pending_key`, `record id` или `type-index`).

### Проверено
- `TestChatController.test_actions_mode_with_screenshot_uses_tools` — 15 post-tests chat controller, 0 failed.

---

## [2026-05-24] - Задача AIA-051: find_warehouse по name (backlog)
### Добавлено
- `docs/tasktracker_ai_assistant_v3.md` — задача **AIA-051**: расширить read-tool `find_warehouse` — поиск склада по `name` (`ilike`, например «Хмельницкого») в дополнение к `code` (`ОбМ-4`); этап V3-9 post-v3.

### Изменено
- `find_warehouse` принимает новый параметр `query` и legacy `code_pattern`, ищет по `code` или `name`.
- `supply_cycle_context.md` уточняет, что склад можно искать по коду или части адреса/названия.

### Проверено
- `tests/test_read_tools.py` покрывает поиск склада по коду, legacy-параметру, фрагменту/полному адресу, пустому результату и префиксу `ОбМ-`.

---

## [2026-05-24] - AI Assistant v3 Actions
### Добавлено
- Action tool layer для AI Assistant: registry/base, read tools, write tools и `ToolExecutor`.
- Tool-call loop в `/ai_assistant/chat`, pending confirmation store и `/ai_assistant/confirm`.
- OWL `ConfirmationCard` и `ResultCard` в floating chat.
- Feature flag `ai_assistant.actions_enabled` и группа `AI Assistant / Снабжение`.
- Rate limit для tools: 30 read/min и 5 write/min на пользователя.
- Idempotency для pending write actions.
- Denylist guard для forbidden tool names и forbidden write fields.
- Модель `ai_assistant.audit` с admin-only меню аудита.
- E2E-тест сценария `УТ-1132 → draft PO на ОбМ-4`.

### Изменено
- `instruction-warehouse-supply-cycle.md` обновлён: AI v3 tools отмечены как draft-only, Confirm/Validate остаются запрещёнными для AI.
- `project.md` дополнен схемой `ai_assistant v3 actions`.
- `pilot_results_v3.md` содержит summary пилота, метрики, ограничения и результаты проверок.

### Проверено
- `docker exec odoo19-local odoo --test-enable --test-tags /ai_assistant -d odoo19_local --stop-after-init --http-port=8071` — 237 post-tests, 0 failed, 0 errors.
- `TestUT1132PipelineDraft` — 1 post-test, 0 failed, 0 errors.
- Targeted flake8 по новым/затронутым AIA-048/AIA-049 файлам — clean.
- Полный `flake8 /mnt/extra-addons/ai_assistant` всё ещё падает на ранее существующем style debt.

---

## [2026-05-24] — fix: смешанные батчи read+write в _get_actions_response
### Исправлено
- При смешанном батче (read + write tool calls) код немедленно возвращал confirmation card, не исполнив read-вызовы и не добавив их результаты в историю сообщений. Теперь при обнаружении смешанного батча read-вызовы исполняются первыми (ассистентское сообщение включает только их), и цикл продолжается — LLM получает read-контекст и переиздаёт write-вызов чистым батчем.
### Добавлено
- Метод `_read_tool_calls` — симметричный `_first_write_tool_call`, возвращает список read-инструментов из батча.
- Параметр `tool_calls` в `_assistant_tool_calls_message` для явной фильтрации вызовов в assistant-сообщении.

## [2026-05-24] — fix: рекурсивная валидация вложенных структур в AbstractTool
### Исправлено
- `AbstractTool._validate_args_manually`: добавлен метод `_validate_value`, рекурсивно проверяющий `properties` вложенных объектов и `items` массивов. До исправления ручной fallback (без `jsonschema`) пропускал невалидные данные во вложенных структурах, тогда как `jsonschema` их отклонял.

## [2026-05-23] — AIA-040: tool-call loop и pending actions
### Добавлено
- `services/pending_action.py` — in-memory `PendingActionStore` с TTL 10 минут для write tools, ожидающих UI-подтверждения.
- Actions-mode в `chat_controller.py`: выбор режима по `ai_assistant.actions_enabled` и группе `ai_assistant.group_ai_assistant_supply`, отправка `tools[]` в OpenRouter, read tool-call loop до 5 итераций.
- Write tool calls больше не выполняются из `/ai_assistant/chat`; вместо этого сохраняются в pending store и возвращают `cards[].type == 'confirmation'`.
- Endpoint `/ai_assistant/confirm`: `confirm` выполняет pending write через `ToolExecutor`, `cancel` удаляет pending action.
- DTO `cards` для confirmation/result карточек backend-first.

### Тесты
- `tests/test_chat_controller.py` покрывает read tool-call loop, write confirmation card, confirm endpoint, неверный pending key и max-iterations break.

## [2026-05-23] — AIA-038: post_chatter_note и ToolExecutor
### Добавлено
- `PostChatterNoteTool` — write tool для внутренних заметок chatter на allowlist моделей `object.request`, `purchase.order`, `stock.picking`.
- `ToolExecutor` — единая точка исполнения tools с проверкой неизвестных tools, required groups, JSON Schema, базового denylist и error envelope `{success, result|error}`.
- Логирование tool-вызовов пишет имя tool и write/read признак без аргументов.

### Тесты
- `tests/test_tool_executor_security.py` покрывает unknown tool, отказ без группы, schema validation, error envelope, allowlist chatter models и блокировку `button_confirm`-подобного tool.

## [2026-05-23] — AIA-037: create_internal_picking_draft
### Добавлено
- `CreateInternalPickingDraftTool` — write tool для создания `stock.picking` внутреннего перемещения в `draft` с вложенными `move_ids`.
- Валидации `picking_type_id.code == 'internal'`, назначения в локацию склада `ОбМ-*`, складируемости товаров и положительных количеств.
- Chatter-запись в picking с пометкой AI-ассистента и stable `idempotency_key`.

### Тесты
- `tests/test_write_tools.py` покрывает happy-case внутреннего перемещения, отказ при назначении не на `ОбМ-*` и регистрацию tool.

## [2026-05-23] — AIA-036: create_purchase_order_draft
### Добавлено
- `CreatePurchaseOrderDraftTool` — write tool для создания `purchase.order` в `draft` на `picking_type_id` склада объекта `ОбМ-*`.
- Валидации поставщика (`supplier_rank > 0`), object warehouse picking type, `incoming`, складируемости товаров и предупреждения по UoM труб до TD-002.
- Создание строк `purchase.order.line` через фактическое поле Odoo 19 `product_uom_id` при внешнем аргументе tool `product_uom`.
- Chatter-запись в PO с пометкой AI-ассистента и stable `idempotency_key` по `(partner_id, origin, partner_ref, sorted(lines))`.

### Тесты
- `tests/test_write_tools.py` покрывает happy-case ОбМ-4 / ПроМеталл / УТ-1132 / 6 строк труб, отказ для не-ОбМ picking type, отказ для не складируемого товара и warning для трубы в кг.

## [2026-05-23] — AIA-035: create_object_request_draft
### Добавлено
- `CreateObjectRequestDraftTool` — write tool для создания `object.request` в `draft` от имени текущего пользователя без `sudo()`.
- Whitelist полей шапки (`project_id`, `need_date`, `foreman_user_id`) и строк (`name_raw`, `qty_requested`, `preferred_vendor_id`).
- Проверки группы `ai_assistant.group_ai_assistant_supply`, непустого списка строк и положительного `qty_requested`.
- Chatter-запись через `message_post(..., subtype_xmlid='mail.mt_note')` с пометкой AI-ассистента.
- Stable `idempotency_key` по `(project_id, need_date, sorted(lines))`.

### Тесты
- `tests/test_write_tools.py` покрывает happy-case, отказ без Supply-группы, chatter note, валидации строк, регистрацию tool и стабильность idempotency key.

## [2026-05-23] — AIA-039: OpenRouter tool-calling client
### Добавлено
- `OpenRouterClient.send_chat_with_tools()` — отправка `tools/tool_choice` в OpenRouter Chat Completions и структурированный ответ `message` или `tool_calls`.
- Безопасный парсинг `tool_calls[].function.arguments`: JSON-строка превращается в dict, битый JSON возвращает `{}` с `arguments_error='invalid_json'`.
- Логирование tool calls пишет только количество и имена tools, без аргументов.
- `tests/test_openrouter_tools.py` — мок-тесты payload, tool_calls, битого JSON и обычного `finish_reason='stop'`.

## [2026-05-23] — AIA-034: read tools для складов, остатков и OR
### Добавлено
- `search_stock_quants`, `find_warehouse`, `find_picking_type`, `find_object_request`, `read_object_request` в `services/action_tools/read_tools.py`.
- Тесты happy-case для остатков, склада `ОбМ-*`, типа операции, поиска OR и чтения OR со строками.

## [2026-05-23] — AIA-033: read tools для товаров и поставщиков
### Добавлено
- `services/action_tools/read_tools.py` — `search_products`, `find_product_by_id`, `find_partner` с явными JSON Schema и whitelist полей.
- Регистрация read tools в `default_registry`.
- `tests/test_read_tools.py` — проверки поиска товара через `ai_search_products`, чтения товара по ID, поиска поставщика по ИНН и регистрации tools.

## [2026-05-23] — AIA-032: pre-condition валидаторы action tools
### Добавлено
- `services/action_tools/validators.py` — проверки object warehouse picking type, складируемости товара, статуса записи, кода склада `ОбМ-*`, поставщика `supplier_rank > 0` и предупреждение по UoM труб до TD-002.
- `tests/test_validators.py` — happy/edge coverage для каждого валидатора.

## [2026-05-23] — AIA-031: базовый слой action tools
### Добавлено
- `services/action_tools/base.py` — `AbstractTool`, `AbstractReadTool`, `AbstractWriteTool`, JSON Schema validation через `jsonschema` с ручным fallback.
- `services/action_tools/registry.py` — `ToolRegistry`, фильтрация tools по группам пользователя и экспорт в OpenRouter/OpenAI-compatible `tools[]`.
- `tests/test_action_tools_registry.py` — тесты регистрации, групп, формы schema и запрета лишних аргументов.

## [2026-05-23] — AIA-030: PromptBuilder actions mode
### Изменено
- `PromptBuilder.build_messages()` получил параметр `mode='consult'|'actions'`; consult остается дефолтным режимом без изменения поведения.
- В actions-режиме системный prompt дополняется правилами подготовки черновиков OR/PO/picking, требованием UI-подтверждения, запретами `button_confirm`, `button_validate`, прямого `state` и инвентаризации.
- Safety rules параметризованы: actions-режим больше не запрещает формулировки вида «Я создам», но ограничен разрешенными tools снабжения.

### Тесты
- `TestPromptBuilder` покрывает наличие actions-правил, неизменность consult-режима и запреты inventory/validate/confirm/state.

## [2026-05-23] — AIA-029: supply-cycle knowledge для actions
### Добавлено
- `custom_addons/ai_assistant/static/knowledge/supply_cycle_context.md` — компактный контекст снабжения OR → PO/INT → Validate: роли, склады `ОбМ-*`, пересчёт в метры, denylist и пример плана PO по УТ-1132.

### Изменено
- `KnowledgeProviderV2` индексирует `supply_cycle_context.md` для модулей `purchase`, `stock`, `object_request` и добавляет триггеры «снабжение», «закупка», «требование», «приход», «ОбМ».
- `static/knowledge/index.json` регистрирует supply-cycle файл для `purchase`, `stock`, `object_request`.
- `test_knowledge_provider_v2.py` проверяет подгрузку supply context по запросу про закупку на ОбМ-4.

## [2026-05-23] — AIA-044: группа Supply и feature flag actions
### Добавлено
- `ai_assistant.group_ai_assistant_supply` — группа для режима actions снабжения; наследует обычный доступ к AI Assistant, Purchase User и Stock User, без прав администратора Odoo.
- `ai_assistant.actions_enabled` — выключенный по умолчанию feature flag в настройках AI-консультанта.

### Изменено
- `custom_addons/ai_assistant/__manifest__.py` — добавлены зависимости `mail`, `stock`, `purchase`, `object_request`, `custom_product_search`.
- `tests/test_module_install.py` — добавлены проверки зависимостей, supply-группы и дефолтного состояния feature flag.

## [2026-05-23] — Roadmap и tasktracker AI-ассистента v3 (Actions)
### Добавлено
- `docs/roadmap_ai_assistant_v3_actions.md` — план развития модуля `ai_assistant` до режима исполнения действий из чата в Odoo: allowlist/denylist tools, архитектура (`action_tools/*`, `ToolExecutor`, `pending_action`), OpenRouter function calling, UX-карточки подтверждения/результата, безопасность (новая группа `group_ai_assistant_supply`, feature flag `ai_assistant.actions_enabled`), границы (без TD-003 — никаких `button_confirm`/`button_validate`).
- `docs/tasktracker_ai_assistant_v3.md` — детальный трекер задач AIA-029…AIA-050 с разделами «Контекст», «🔧 Context7», «🚫 Запрещено», «✅ DoD» под каждую задачу. Включает рекомендуемый порядок инкрементов и сводную таблицу зависимостей.

### Примечание
- Реализация ещё не начата; документы предназначены для пошагового исполнения агентом из терминала с понятным контекстом.

## [2026-05-23] — TD-003: примечание о `call_model_method` (без кастомного модуля)
### Изменено
- `docs/technical-debt.md` — в TD-003 добавлен блок «Примечание (2026-05-23)» о том, что подзадачу 1 (server-side validate/confirm) можно закрыть без кастомного модуля Odoo через инструмент `call_model_method` пакета `mcp-server-odoo` v0.6.0 (нужны `ODOO_YOLO=true` и `ODOO_MCP_ENABLE_METHOD_CALLS=true` в `~/.cursor/mcp.json` и перезапуск MCP). Согласовано с TD-001.

## [2026-05-12] — Модуль подписей остатков `stock_qty_labels_ru`
### Добавлено
- Модуль `custom_addons/stock_qty_labels_ru`: подписи **На складе** / **Доступно** для `qty_available` и `virtual_available` в основных списках, отчёте наличия, kanban и кнопке прогноза на форме товара (наследование стандартных представлений `stock`).

## [2026-05-12] — OBR: устойчивость wizard предпросмотра выдачи в веб-клиенте
### Изменено
- `object.request.issue.preview.group`: поле «Склад» вычисляется из привязанных строк распределения (`warehouse_id`).
- Перед созданием выдач `action_create_issues` восстанавливает `stock_line_ids` включённых групп из строк требования (на случай, если UI обнулил M2m при переключении «Создать»).
### Добавлено
- Тест `test_issue_preview_relinks_cleared_stock_lines_on_create` в `test_obr011_issue_picking.py`.

## [2026-05-11] — OBR: чистка тестов multi-warehouse
### Добавлено
- Multi-warehouse сценарии в `test_obr011_issue_picking.py` и `test_obr012_confirm_issue.py`: одна строка требования может создавать выдачи по нескольким складам, а синхронизация `qty_issued` суммирует движения по всем выдачам строки.
- Тесты авто-разбивки по двум складам, частично выданной строке, предупреждению при ручной правке, приоритету склада объекта и исключению группы в wizard выдачи.
### Изменено
- Тестовые фабрики `object_request` очищены от старого шапочного `warehouse_id` в `object.request.create()`.
- `test_obr024_warehouse.py` и `test_obr025_multiwarehouse_check.py` переписаны под новую схему `object.request.line.stock` и расчёт по всем активным складам.
- `object.request.line.stock` хранит ссылку на `stock.move`, чтобы multi-picking выдача корректно синхронизировала фактически выданное количество.
- Авто-разбивка использует склад объекта первым, если на нём есть положительный остаток, и не планирует выдачу с него при нуле.
- Legacy `object.request.issue.wizard` оставлен как совместимый wrapper на новый preview wizard без выбора склада в форме.
- Обновлены `datamodelspec`, `functionalspec`, `project` и tasktracker по актуальной multi-warehouse схеме.

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
