# Task Tracker: Требование на комплектацию объекта (object_request)

**Дата создания:** 2026-03-15
**Роадмап:** [roadmapobjectrequest.md](roadmapobjectrequest.md)
**Functional spec:** [functionalspecobjectrequest.md](functionalspecobjectrequest.md)
**Data model spec:** [datamodelspecobjectrequest.md](datamodelspecobjectrequest.md)
**Модуль:** `custom_addons/object_request/`

---

## Этап 0. Подготовка справочников

### Задача: OBR-001 — Подготовить минимальные справочные данные

- **Статус**: В работе (ожидает проверки загрузки после OBR-004)
- **Приоритет**: Критический
- **Описание**: До полноценной работы модуля необходимо иметь хотя бы минимальную базу справочников. Без этого даже корректный импорт Excel быстро упрётся в массовое ручное сопоставление.
- **Шаги выполнения**:
  - [x] ~~Определить модель объекта~~ → решено в [data model spec](datamodelspecobjectrequest.md): отдельная модель `object.request.project`
  - [x] ~~Определить модель пользователя для ролей~~ → решено: `res.users` (не `res.partner`, не `hr.employee`)
  - [x] ~~Определить формат хранения зон/этажей/участков~~ → решено: отдельные `Char`-поля (`zone`, `floor`, `section`)
  - [x] Подготовить demo-данные объектов `object.request.project` (4 объекта: JK-001, OC-002, TC-003, PZ-004)
  - [x] Подготовить demo-данные прорабов (3 пользователя `res.users`: foreman.ivanov, foreman.petrov, foreman.sidorov)
  - [x] Подготовить demo-данные товаров (`product.product`) — 26 позиций строительной номенклатуры
  - [x] Подготовить demo-данные поставщиков (`res.partner`, supplier_rank=1) — 4 поставщика
  - [x] Настроить `vendor info` (`product.supplierinfo`) — 26 записей (каждый товар привязан к 1 поставщику)
  - [x] Создать XML-файл demo-данных `data/demo_data.xml` (XML синтаксис проверен)
  - [ ] Проверить, что demo-данные загружаются без ошибок (выполнить после OBR-004)
- **Критерий готовности**: В системе есть объекты, прорабы (пользователи), товары, поставщики и vendor info; данные загружаются через demo-файл.
- **Зависимости**: Рабочий Docker-стек Odoo 19 + PostgreSQL
- **Принятые решения** (см. [data model spec](datamodelspecobjectrequest.md)):
  - Модель объекта: `object.request.project` (отдельная легковесная модель)
  - Роли через `res.users`, не через `res.partner` или `hr.employee`
  - Зоны/этажи/участки: `Char`-поля в строке

---

## Этап 1. Каркас модуля

### Задача: OBR-002 — Создать каркас модуля `object_request`

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Описание**: Инициализировать структуру Odoo-модуля со всеми подкаталогами, манифестом, зависимостями и пустыми заглушками.
- **Шаги выполнения**:
  - [x] Создать директорию `custom_addons/object_request/` со структурой подкаталогов (`models/`, `views/`, `wizards/`, `security/`, `reports/`, `data/`, `tests/`, `static/description/`)
  - [x] Создать `__manifest__.py`: name, version, category, depends (`base`, `mail`, `stock`, `purchase`, `product`, `contacts`), data, demo
  - [x] Создать корневой `__init__.py` с импортами `models`, `wizards`
  - [x] Создать `__init__.py` в каждом подкаталоге (`models/`, `wizards/`, `tests/`)
  - [x] Создать `static/description/icon.png` (иконка модуля)
  - [x] Установить модуль и убедиться, что он ставится без ошибок
- **Критерий готовности**: Модуль устанавливается в Odoo без ошибок; зависимости разрешаются корректно.
- **Зависимости**: OBR-001 (решение по модели объекта)

### Задача: OBR-003 — Создать группы доступа и security

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Описание**: Настроить модель прав доступа для четырёх ролей: Прораб, Снабженец, Кладовщик, Согласующий.
- **Шаги выполнения**:
  - [x] Создать `security/object_request_security.xml`:
    - [x] Категория модуля `object_request`
    - [x] Группа `Прораб` (`object_request.group_foreman`)
    - [x] Группа `Снабженец` (`object_request.group_supply_manager`)
    - [x] Группа `Кладовщик` (`object_request.group_storekeeper`)
    - [x] Группа `Согласующий` (`object_request.group_approver`) — заглушка
  - [x] Создать `security/ir.model.access.csv`:
    - [x] Права на `object.request` для каждой группы (CRUD по ролям)
    - [x] Права на `object.request.line` для каждой группы
    - [x] Права на wizard импорта
  - [x] Создать `security/object_request_rules.xml`:
    - [x] Record rule: Прораб видит только свои документы
    - [x] Record rule: Снабженец видит все документы (без ограничений)
    - [x] Record rule: Кладовщик видит документы в работе
  - [x] Подключить security-файлы в `__manifest__.py`
  - [ ] Проверить, что права применяются корректно (выполнить после OBR-004)
- **Критерий готовности**: Группы созданы; ACL-правила разграничивают доступ по ролям; record rules ограничивают видимость.
- **Зависимости**: OBR-002

### Задача: OBR-004 — Создать базовые модели документа и строк

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Описание**: Реализовать модели `object.request` (шапка) и `object.request.line` (строка) со всеми полями из roadmap и functional spec.
- **Шаги выполнения**:
  - [x] Создать модель `object.request.project` (справочник объектов):
    - [x] `name`, `code`, `partner_id`, `address`, `comment`, `active`
    - [x] `request_ids` — One2many, `request_count` — computed
    - [x] SQL constraint: уникальность `code` при заполненном значении
  - [x] Создать `models/object_request.py` с моделью `object.request`:
    - [x] `_inherit = ['mail.thread', 'mail.activity.mixin']`
    - [x] `name` — Char, номер документа (sequence), readonly, copy=False
    - [x] `project_id` — Many2one `object.request.project`, required, index
    - [x] `foreman_user_id` — Many2one `res.users` (прораб), required, index
    - [x] `need_date` — Date, required, index
    - [x] `priority` — Selection (`0`-Низкий, `1`-Обычный, `2`-Высокий, `3`-Критический), default='1'
    - [x] `comment` — Text
    - [x] `state` — Selection (`draft`, `in_progress`, `closed`, `cancelled`), default='draft', tracking
    - [x] `line_ids` — One2many на `object.request.line`, copy=True
    - [x] `issue_picking_ids` — Many2many `stock.picking` (через rel-таблицу)
    - [x] `purchase_order_ids` — Many2many `purchase.order` (через rel-таблицу)
    - [x] `matching_state` — Selection, computed, store=True
    - [x] `approval_state` — Selection, заглушка, default='stub'
    - [x] `source_file_name` — Char, `source_file_checksum` — Char (index)
    - [x] `imported_at` — Datetime, `imported_by_user_id` — Many2one `res.users`
    - [x] `buyer_user_id` — Many2one `res.users` (снабженец)
    - [x] `warehouse_user_id` — Many2one `res.users` (кладовщик)
    - [x] `approver_user_id` — Many2one `res.users` (согласующий, заглушка)
    - [x] `company_id` — Many2one `res.company`, required, default=lambda
    - [x] `currency_id` — related от company_id
    - [x] `active` — Boolean, default=True
    - [x] Агрегатные счётчики: `line_count`, `line_problem_count`, `line_matched_count`, `line_to_issue_count`, `line_to_buy_count`, `line_fully_supplied_count` — computed, store=True
    - [x] Количественные агрегаты: `qty_total_requested`, `qty_total_to_issue`, `qty_total_to_buy`, `qty_total_issued` — computed, store=True
    - [x] `issue_picking_count`, `purchase_order_count` — computed
  - [x] Реализовать автонумерацию через `ir.sequence` (формат `OR/%(year)s/%(month)s/%(seq)s`)
  - [x] Создать `data/ir_sequence_data.xml` с sequence `object.request.sequence`
  - [x] Реализовать методы смены статуса: `action_in_progress()`, `action_close()`, `action_cancel()`
  - [x] Реализовать `@api.constrains` для бизнес-правил:
    - [x] Нельзя закрыть документ с полностью необработанными строками
    - [x] Нельзя перевести в работу без строк
  - [x] Создать `models/object_request_line.py` с моделью `object.request.line`:
    - [x] `_order = 'request_id, sequence, id'`
    - [x] Поля импорта: `request_id` (cascade), `sequence`, `source_row_no`, `supplier_article`, `name_raw` (required), `uom_raw`, `qty_requested` (required), `price_raw`, `comment`, `supplier_raw`
    - [x] Поля размещения: `zone`, `floor`, `section` (все Char, index)
    - [x] Поля номенклатуры: `product_id` (Many2one `product.product`), `product_tmpl_id` (related, store), `uom_id`, `preferred_vendor_id` (domain supplier_rank>0), `allowed_substitute_ids` (Many2many через rel-таблицу)
    - [x] Поля сопоставления: `matching_required` (Boolean), `matching_state` (Selection: matched/requires_mapping/manual_review), `matching_note`, `manual_vendor_required`
    - [x] Поля обработки: `procurement_mode` (Selection: manual/issue/buy/mixed), `qty_to_issue`, `qty_to_buy`, `qty_reserved`, `qty_issued`
    - [x] Технические поля: `stock_qty_on_hand`, `stock_check_date`
    - [x] Статус строки: `line_state` (Selection: draft/requires_mapping/ready/partially_issued/fully_supplied/cancelled)
    - [x] Связи с Odoo: `issue_picking_id`, `issue_move_id`, `purchase_order_id`, `purchase_order_line_id`
    - [x] Служебные: `company_id` (related), `currency_id` (related)
    - [x] SQL constraints: qty_requested > 0, qty_to_issue >= 0, qty_to_buy >= 0, qty_issued >= 0
    - [x] Python constraints: qty_to_issue + qty_to_buy <= qty_requested
  - [x] Реализовать computed-поля: `line_state`, `has_substitutes`, `is_fully_matched`, `is_ready_for_issue`, `is_ready_for_purchase`
  - [x] Реализовать `@api.onchange('product_id')`: автозаполнение UOM, предложение vendor
  - [x] Реализовать `@api.onchange('qty_to_issue'/'qty_to_buy')`: обновление `procurement_mode`
  - [x] Подключить модели в `models/__init__.py`
  - [x] Проверить, что модели создаются в БД без ошибок
- **Критерий готовности**: Обе модели создаются; автонумерация работает; computed-поля вычисляются; смена статусов через методы.
- **Зависимости**: OBR-002, OBR-003

### Задача: OBR-005 — Создать меню, tree/form views и search view

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Описание**: Реализовать все пользовательские экраны: список документов, форму документа, search view с фильтрами и группировками.
- **Шаги выполнения**:
  - [x] Создать `views/object_request_menu.xml`:
    - [x] Корневое меню модуля
    - [x] Подменю `Требования на комплектацию`
    - [x] Action для открытия списка
  - [x] Создать `views/object_request_views.xml`:
    - [x] **List view** с колонками: номер, объект, прораб, дата потребности, приоритет, статус, кол-во строк, кол-во несопоставленных, дата создания
    - [x] **Form view** с полной структурой:
      - [x] Header: кнопки действий с правилами видимости по `state` и `groups`
      - [x] Statusbar с `state`
      - [x] Шапка: поля документа с `readonly` по статусам
      - [x] Smart buttons: строки, выдачи, закупки, проблемные строки
      - [x] Notebook tabs: Строки, Обработка, Связанные документы, Импорт
      - [x] Chatter для логирования действий
    - [x] **Search view** с фильтрами:
      - [x] `Мои` (по текущему пользователю/прорабу)
      - [x] `Черновик`, `В работе`, `Закрыто`, `Отменено`
      - [x] `Есть несопоставленные строки`
      - [x] `Требуют поставщика`
    - [x] **Search view** с группировками:
      - [x] По объекту, прорабу, статусу, приоритету, дате потребности
  - [x] Создать `views/object_request_line_views.xml`:
    - [x] List view для строк (smart-button) с колонками
    - [x] Визуальные индикаторы (badges/decoration): `Требует сопоставления`, `Требует поставщика`, `Частично выдано`, `Полностью обеспечено`
    - [x] Search view для строк с фильтрами
  - [x] Создать `views/object_request_project_views.xml` (список и форма объектов)
  - [x] Добавить методы smart buttons в модель (`action_open_lines`, `action_open_problem_lines`, `action_open_issue_pickings`, `action_open_purchase_orders`)
  - [x] Добавить заглушки `action_check_stock_stub`, `action_prepare_purchase_stub`
  - [x] Подключить views в `__manifest__.py`
  - [x] Проверить, что модуль обновляется без ошибок
- **Критерий готовности**: Пользователь видит меню модуля; список отображает документы; форма содержит все поля, кнопки, tabs; search view работает.
- **Зависимости**: OBR-004

---

## Этап 2. Excel импорт

### Задача: OBR-006 — Создать wizard загрузки Excel-файла

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Описание**: Реализовать TransientModel-wizard для загрузки Excel-файла с предварительной проверкой.
- **Шаги выполнения**:
  - [x] Создать `wizards/import_excel_wizard.py` с моделью `object.request.import.wizard`:
    - [x] `file` — Binary, required (файл Excel)
    - [x] `file_name` — Char, required
    - [x] `project_id` — Many2one `object.request.project`, required
    - [x] `foreman_user_id` — Many2one `res.users`, required (прораб)
    - [x] `need_date` — Date, required
    - [x] `priority` — Selection, required, default='1'
    - [x] `comment` — Text
    - [x] `line_preview_count` — Integer, readonly
    - [x] `problem_line_count` — Integer, readonly
    - [x] `validation_state` — Selection (`not_checked`, `valid`, `invalid`)
    - [x] `validation_messages` — Text
  - [x] Реализовать метод `action_validate()` — «Загрузить и проверить»:
    - [x] Чтение файла через `openpyxl`
    - [x] Проверка структуры колонок (минимум 5: п/п, артикул, наименование, ед.изм., количество)
    - [x] Валидация обязательных колонок
    - [x] Обработка ошибок формата с понятными сообщениями
    - [x] Заполнение preview-строк (bulk create)
    - [x] Подсчёт статистики (total, problem_count)
  - [x] Реализовать preview-модель `object.request.import.preview`:
    - [x] Поля: `sequence`, `source_row_no`, `supplier_article`, `name_raw`, `uom_raw`, `qty`, `price`, `comment`, `supplier_raw`, `matched_product_id`, `match_status`, `has_error`, `error_message`
  - [x] Подключить wizard в `wizards/__init__.py` (уже был подключён)
  - [x] Создать `wizards/import_excel_wizard_views.xml`:
    - [x] Форма wizard с полями шапки, кнопками, блоком preview
    - [x] Кнопки: `Загрузить и проверить`, `Импортировать`, `Отмена`
  - [x] Проверить, что wizard открывается и файл загружается (11 тестов — ✅)
- **Критерий готовности**: Wizard открывается; Excel загружается; валидация показывает статистику; preview-строки отображаются.
- **Зависимости**: OBR-004, OBR-005

### Задача:   OBR-007 — Реализовать парсинг, сопоставление и создание строк

- **Статус**: Выполнена ✅
- **Приоритет**: Критический
- **Дата выполнения**: 2026-03-15
- **Описание**: Реализовать логику парсинга Excel, автоматическое сопоставление товаров и создание документа со строками.
- **Шаги выполнения**:
  - [x] Реализовать сервис автосопоставления `models/excel_parser.py`:
    - [x] Нормализация строк (trim/whitespace) и единиц измерения (`normalize_str()`, `normalize_uom()`)
    - [x] Автопоиск товара по артикулу поставщика через `product.supplierinfo` (`match_product_by_article()`)
    - [x] Автопоиск товара по наименованию (exact → ilike) (`match_product_by_name()`)
    - [x] Автопоиск поставщика по имени через `res.partner` (`match_vendor_by_name()`)
    - [x] Флаги несопоставления: `matching_required=True`, `manual_vendor_required=True` (`match_row()`)
  - [x] Реализовать парсинг/нормализацию строк Excel в wizard `wizards/import_excel_wizard.py` (через `openpyxl` в `action_validate()`):
    - [x] Обработка «грязных» данных (пробелы/пустые значения) и нормализация UOM/поставщиков перед созданием preview
    - [x] Частичное несопоставление не блокирует импорт (через флаги и статистику)
  - [x] Реализовать `action_import()` в wizard:
    - [x] Создание документа `object.request`
    - [x] Создание строк `object.request.line` из preview
    - [x] Сохранение имени файла и даты импорта в шапке (`source_file_name`, `imported_at`)
    - [x] Перенаправление на форму созданного документа
  - [x] Обработка ошибок:
    - [x] Критическая ошибка формата → блокировка импорта с сообщением (валидация колонок/файла)
    - [x] Частичное несопоставление → предупреждение, импорт разрешён
  - [x] `openpyxl` доступен в окружении выполнения (в контейнере установлен; используется в wizard и тестах)
  - [x] Проверить end-to-end тестами: загрузка Excel → preview → импорт → документ со строками (`tests/test_obr007_import.py`)
- **Критерий готовности**: Excel фиксированного формата импортируется; товары сопоставляются автоматически (где возможно); несопоставленные строки помечаются; документ создаётся со всеми строками.
- **Зависимости**: OBR-006, OBR-001 (demo-данные для проверки сопоставления)

---

## Этап 3. Ручное сопоставление

### Задача: OBR-008 — Реализовать поля и UI сопоставления строк

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Описание**: Дать снабженцу возможность вручную сопоставить строки документа с товарами, поставщиками и заменами.
- **Шаги выполнения**:
  - [x] В модели `object.request.line`:
    - [x] `product_id` — Many2one `product.product` — было с OBR-004
    - [x] `preferred_vendor_id` — Many2one `res.partner` — было с OBR-004
    - [x] `allowed_substitute_ids` — Many2many `product.product` — было с OBR-004
    - [x] `matching_required` — Boolean — было с OBR-004
    - [x] `matching_note` — Text — было с OBR-004
    - [x] `@api.onchange('product_id')`: автозаполнение `uom_id`, очистка `matching_required`
    - [x] `@api.onchange('preferred_vendor_id')`: очистка `manual_vendor_required`
  - [x] В form view таблицы строк:
    - [x] Визуальная маркировка строк `matching_required=True` (decoration-danger)
    - [x] Визуальная маркировка строк `manual_vendor_required=True` (decoration-warning)
    - [x] `supplier_raw` рядом с `preferred_vendor_id` (optional="show")
    - [x] `uom_raw` рядом с `uom_id` (optional="show")
    - [x] `allowed_substitute_ids` с widget="many2many_tags" (optional="hide")
    - [x] `matching_note` добавлен в inline-список (optional="hide")
  - [x] В search view строк:
    - [x] Фильтр `Только проблемные строки` (matching_required OR manual_vendor_required)
  - [x] 10 тестов — ✅
- **Критерий готовности**: Снабженец может в таблице строк выбрать товар, поставщика, указать замены; проблемные строки визуально выделены; фильтрация по проблемным строкам работает.
- **Зависимости**: OBR-005, OBR-007

### Задача: OBR-009 — Массовые действия и ускорение сопоставления

- **Статус**: Выполнена ✅
- **Приоритет**: Средний
- **Дата выполнения**: 2026-03-16
- **Описание**: Добавить массовые операции для ускорения работы снабженца при ручном сопоставлении.
- **Шаги выполнения**:
  - [x] Реализовать server action `Назначить поставщика` для выбранных строк (`wizards/assign_lines_wizard.py`, `wizards/assign_lines_wizard_views.xml`)
  - [x] Реализовать server action `Назначить товар` для выбранных строк (wizard с `assign_type='product'`)
  - [x] Добавить кнопку `Пересопоставить` на форме документа:
    - [x] Повторно запускает автосопоставление по несопоставленным строкам (`action_rematch_lines()`)
    - [x] Полезно после наполнения справочников
  - [x] Быстрый поиск товара в Many2one: по имени, артикулу, default_code (`context="{'display_default_code': True}"`)
  - [x] Реализовать smart button `Проблемные строки`:
    - [x] Показывает количество строк с matching_required или manual_vendor_required (исправлен `line_problem_count`)
    - [x] При нажатии — фильтрация таблицы (уже был `action_open_problem_lines`)
  - [x] 14 тестов — ✅
- **Критерий готовности**: Массовые действия работают; пересопоставление по кнопке; быстрый поиск товара; smart button показывает count и фильтрует.
- **Зависимости**: OBR-008

---

## Этап 4. Складская обработка MVP

### Задача: OBR-010 — Ручное управление количествами к выдаче

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Дать снабженцу возможность вручную указать количества к выдаче и к закупке по каждой строке.
- **Шаги выполнения**:
  - [x] В модели `object.request.line`:
    - [x] `qty_to_issue` — Float (количество к выдаче), редактируемое вручную
    - [x] `qty_to_buy` — Float (количество к закупке), редактируемое вручную
    - [x] `qty_issued` — Float (фактически выдано; computed от picking — в OBR-012)
    - [x] `procurement_mode` — Selection (`manual`, `issue`, `buy`, `mixed`)
    - [x] `@api.constrains`: qty_to_issue + qty_to_buy <= qty_requested
    - [x] `@api.onchange('qty_to_issue')`: автозаполнение qty_to_buy = qty_requested - qty_to_issue
  - [x] В form view строк:
    - [x] Колонки: `Запрошено`, `К выдаче`, `К закупке`, `Выдано`
    - [x] Условная раскраска: зелёный для fully_supplied, жёлтый для partially_issued
    - [x] `qty_to_issue`/`qty_to_buy` readonly когда state != 'in_progress'
  - [x] Computed-поля шапки документа: `qty_total_to_issue`, `qty_total_to_buy`, `qty_total_issued`
  - [x] Сводка на вкладке `Обработка`
  - [x] 13 тестов — ✅
- **Критерий готовности**: Снабженец может вручную указать qty_to_issue/qty_to_buy; constrains валидируют; сводка отображается на вкладке Обработка.
- **Зависимости**: OBR-008

### Задача: OBR-011 — Создание документа выдачи (stock.picking)

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: По кнопке `Создать выдачу` формировать складской документ `stock.picking` из строк с заполненным qty_to_issue.
- **Шаги выполнения**:
  - [x] Создать `wizards/issue_wizard.py` с моделью `object.request.issue.wizard`:
    - [x] `request_id` — Many2one, required, readonly
    - [x] `line_ids` — Many2many `object.request.line`
    - [x] `warehouse_id` — Many2one `stock.warehouse`
    - [x] `picking_type_id` — Many2one `stock.picking.type`
    - [x] `source_location_id`, `destination_location_id` — Many2one `stock.location`
    - [x] `scheduled_date` — Datetime
    - [x] `comment` — Text
    - [x] `default_get()` — авто-заполнение строк и локаций из warehouse
  - [x] Реализовать метод `action_create_issue()` в wizard:
    - [x] Фильтрация строк: qty_to_issue > 0 и product_id
    - [x] Валидация: если нет строк — UserError
    - [x] Picking type: задаётся в wizard (по умолчанию — internal transfer склада)
    - [x] Создать `stock.picking`: origin, is_object_request_issue, object_request_project_id, move_ids
    - [x] Обновить связи: `issue_picking_ids` в шапке, `issue_picking_id` и `issue_move_id` в строке
    - [x] Открыть форму созданного picking
  - [x] Добавить кнопку `Создать выдачу` на форме документа:
    - [x] Visible: state == 'in_progress' и line_to_issue_count > 0
    - [x] Groups: group_supply_manager
  - [x] Smart button `Выдачи` — показывает count, открывает tree/form (был с OBR-005)
  - [x] Возврат к требованию из picking: smart button на форме picking (`action_open_object_requests`)
  - [x] Расширить `stock.picking`: `is_object_request_issue`, `object_request_project_id`, `object_request_ids` (reverse M2M)
  - [x] View inherit на форме picking: smart button «Требования»
  - [x] 12 тестов — ✅
- **Критерий готовности**: По кнопке создаётся stock.picking с корректными move_ids; smart button отображает связанные выдачи; ссылка обратно на требование работает.
- **Зависимости**: OBR-010

### Задача: OBR-012 — Подтверждение выдачи кладовщиком и фиксация

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Реализовать цикл подтверждения выдачи кладовщиком и обратную синхронизацию с документом требования.
- **Шаги выполнения**:
  - [x] Расширить `stock.picking` — было в OBR-011 (`object_request_ids`, `is_object_request_issue`, `object_request_project_id`, кнопка возврата)
  - [x] Override `_action_done()` на `stock.picking`:
    - [x] После подтверждения вызывает `_sync_qty_issued_to_request_lines()`
    - [x] `_sync_qty_issued_to_request_lines()` — читает `move.quantity` и пишет `line.qty_issued`
  - [x] Computed `line_state` в `object.request.line` (из OBR-004):
    - [x] `requires_mapping` / `ready` / `partially_issued` / `fully_supplied` / `cancelled`
    - [x] Автоматически пересчитывается после обновления `qty_issued`
  - [x] Визуальные индикаторы строк — badges были в OBR-005/OBR-010 (желтый, зеленый)
  - [x] `_notify_if_all_lines_supplied()` на `object.request` — chatter-уведомление, когда все строки `fully_supplied`
  - [x] Примечание по Odoo 19: `stock.move.line.reserved_uom_qty` → `ml.move_id.product_uom_qty`; `type='storable'` → `type='consu' + is_storable=True`
  - [x] 12 тестов — ✅
- **Критерий готовности**: Кладовщик подтверждает выдачу; qty_issued обновляется; line_state пересчитывается; badges отображаются.
- **Зависимости**: OBR-011

---

## Этап 5. Печатные формы

### Задача: OBR-013 — Печатная форма требования на комплектацию

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Создать QWeb-отчёт для печати/PDF документа требования.
- **Шаги выполнения**:
  - [x] Создать `reports/object_request_report.xml`:
    - [x] Action report: `ir.actions.report` для `object.request`
    - [x] QWeb-шаблон `report_object_request`
  - [x] Реализовать layout отчёта:
    - [x] Шапка: номер документа, объект, прораб, дата потребности, приоритет, комментарий
    - [x] Таблица строк: №, зона, этаж, участок, наименование, ед. изм., количество, выдано, комментарий
    - [x] Блок подписей: прораб, снабженец, согласующий (заглушка)
    - [x] Стандартный paper format (paperformat_euro)
  - [x] Добавить кнопку `Распечатать требование` в header формы
  - [x] Подключить отчёт в `__manifest__.py`
  - [x] 5 тестов — ✅
- **Критерий готовности**: PDF генерируется; содержит все данные шапки и строк; подписи на месте; отступы и таблица читаемы.
- **Зависимости**: OBR-005, OBR-004

### Задача: OBR-014 — Печатная форма расходной накладной

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Создать QWeb-отчёт для печати расходной накладной (выдачи со склада).
- **Шаги выполнения**:
  - [x] Создать `reports/issue_picking_report.xml`:
    - [x] Action report: `ir.actions.report` для `stock.picking`
    - [x] QWeb-шаблон `report_issue_picking`
  - [x] Реализовать layout отчёта:
    - [x] Шапка: номер документа выдачи, ссылка на требование, объект, дата
    - [x] Таблица: №, товар, ед. изм., запрошено, выдано, зона/этаж/участок, примечание
    - [x] Блок подписей: кладовщик, получатель / прораб
  - [x] Добавить кнопку `Расходная накладная` на форме picking (через inherit view)
  - [x] Подключить отчёт в `__manifest__.py`
  - [x] 8 тестов — ✅
- **Критерий готовности**: PDF расходной накладной генерируется; зоны/этажи/участки выводятся корректно; подписи на месте.
- **Зависимости**: OBR-011, OBR-012

---

## Этап 6. State machine и заглушки

### Задача: OBR-015 — Финализировать state machine документа и строк

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Отладить полный жизненный цикл документа и правила перехода между статусами.
- **Шаги выполнения**:
  - [x] Зафиксировать и реализовать правила переходов:
    - [x] `Черновик → В работе`: может нажать Прораб или Снабженец; предупреждение если есть несопоставленные строки
    - [x] `in_progress → closed`: может нажать Снабженец; подтверждение если не все строки обработаны
    - [x] `draft → cancelled`: может нажать Снабженец/админ
    - [x] `in_progress → cancelled`: может нажать Снабженец/админ
    - [x] Из `closed` и `cancelled` — переходов нет (финальные статусы)
  - [x] Реализовать правила редактируемости формы по статусам:
    - [x] `Черновик`: полное редактирование шапки и строк
    - [x] `В работе`: ограниченное — project_id, foreman_user_id, need_date, priority readonly; редактируются только comment и строки (qty_to_issue/qty_to_buy)
    - [x] `Закрыто` и `Отменено`: только чтение
  - [x] Реализовать warning-диалоги (`wizards/confirm_state_wizard.py`):
    - [x] Предупреждение при переводе в работу с несопоставленными строками (wizard, не блокирует)
    - [x] Подтверждение при отмене документа (`confirm` на кнопке)
    - [x] Подтверждение при закрытии с частично обработанными строками (wizard, позволяет закрыть)
  - [x] 14 тестов — ✅
- **Критерий готовности**: Все переходы работают корректно; предупреждения показываются; форма блокируется в финальных статусах.
- **Зависимости**: OBR-004, OBR-012

### Задача: OBR-016 — Заглушки для этапа 2 (согласование, расчёт наличия, закупка)

- **Статус**: Выполнена ✅
- **Приоритет**: Низкий
- **Дата выполнения**: 2026-03-16
- **Описание**: Добавить в UI элементы, которые будут реализованы позже, но уже должны быть предусмотрены.
- **Шаги выполнения**:
  - [x] Поле `Физический остаток` (`stock_qty_on_hand`) — disabled optional колонка в таблице строк, tooltip «Заполняется автоматически на Этапе 2»
  - [x] Поле `К закупке (авто)` — placeholder с tooltip в секции «Автоматическая обработка (Этап 2)» на вкладке Обработка
  - [x] Кнопка `Рассчитать наличие` — disabled с подробным tooltip, видна в draft/in_progress
  - [x] Кнопка `Подготовить закупку` — disabled с подробным tooltip (`action_prepare_purchase_stub` — UserError с сообщением)
  - [x] Поле `Согласование` в шапке — `approval_state` default изменён на `not_required` («Не требуется»), добавлен tooltip, значение 'stub' удалено из Selection
  - [x] Исправлены lint-ошибки E741/F401/F841 по всему модулю (pre-existing)
  - [x] 141 тест — ✅
- **Критерий готовности**: Все заглушки видны в UI; disabled-элементы имеют tooltip; пользователь понимает, что функция запланирована.
- **Зависимости**: OBR-005, OBR-015

---

## Этап 7. Тестирование MVP

### Задача: OBR-017 — Unit- и интеграционные тесты

- **Статус**: Выполнена ✅
- **Приоритет**: Высокий
- **Дата выполнения**: 2026-03-16
- **Описание**: Покрыть ключевую бизнес-логику модуля unit- и интеграционными тестами.
- **Шаги выполнения**:
  - [x] Создать `tests/__init__.py` и структуру тестов
  - [x] **Тесты модели `object.request`**:
    - [x] Тест создания документа с автонумерацией (test_obr004)
    - [x] Тест переходов статусов (draft → in_progress → closed) (test_obr015)
    - [x] Тест отмены документа (test_obr015)
    - [x] Тест constrains: нельзя перевести в работу без строк (test_obr004)
    - [x] Тест constrains: нельзя закрыть необработанный документ (test_obr015)
    - [x] Тест computed-полей: line_count, unmatched_line_count (test_obr004)
  - [x] **Тесты модели `object.request.line`**:
    - [x] Тест создания строки с полями импорта (test_obr004)
    - [x] Тест constrains: qty_to_issue + qty_to_buy <= qty_requested (test_obr010)
    - [x] Тест onchange: автозаполнение qty_to_buy (test_obr010)
    - [x] Тест computed line_state (test_obr008)
  - [x] **Тесты Excel-импорта**:
    - [x] Тест парсинга корректного файла (test_obr007)
    - [x] Тест парсинга файла с пустыми артикулами (test_obr007)
    - [x] Тест парсинга файла с невалидной структурой → ошибка (test_obr006)
    - [x] Тест автосопоставления товаров (test_obr007)
    - [x] Тест создания документа через wizard (test_obr007)
  - [x] **Тесты складской обработки**:
    - [x] Тест создания picking из документа требования (test_obr011)
    - [x] Тест обратной синхронизации qty_issued после подтверждения picking (test_obr012)
    - [x] Тест обновления line_state при частичной выдаче (test_obr012)
  - [x] **Тесты ACL/security** (`tests/test_obr017_security.py` — 18 тестов):
    - [x] Тест прав доступа прораба (создание, чтение, ограниченное редактирование, record rule)
    - [x] Тест прав доступа снабженца (полный CRUD, видит все документы, сопоставление строк)
    - [x] Тест прав доступа кладовщика (только in_progress, нет создания, нет wizard импорта)
  - [x] Попутно исправлен баг: `ir.sequence.next_by_code` в `create` теперь вызывается через `sudo()`
  - [x] 161 тест — ✅ (0 failed, 0 errors)
- **Критерий готовности**: Все unit/интеграционные тесты проходят; покрыты все ключевые бизнес-правила и edge cases.
- **Зависимости**: OBR-001 — OBR-016

### Задача: OBR-018 — Ручные пилотные сценарии

- **Статус**: Выполнена ✅
- **Приоритет**: Средний
- **Дата выполнения**: 2026-03-16
- **Описание**: Прогнать все пользовательские сценарии из functional spec — реализованы как автоматизированные интеграционные тесты (`tests/test_obr018_pilot_scenarios.py`).
- **Шаги выполнения**:
  - [x] **Сценарий 1**: Прораб создаёт документ вручную, заполняет шапку, сохраняет
  - [x] **Сценарий 2**: Прораб импортирует Excel; часть строк не сопоставляется; проблемные строки видны
  - [x] **Сценарий 3**: Снабженец открывает проблемные строки; назначает товар и поставщика; переводит в работу
  - [x] **Сценарий 4**: Снабженец формирует выдачу; кладовщик подтверждает фактическое количество
  - [x] **Сценарий 5**: Печать требования и расходной накладной (PDF)
  - [x] **Сценарий 6**: Полный lifecycle: Черновик → В работе → Закрыто
  - [x] **Сценарий 7**: Отмена документа из Черновика и из В работе
  - [x] **Сценарий 8**: Частичная выдача → повторная выдача по оставшимся позициям
  - [x] **Сценарий 9**: Проверка прав: прораб не может создать выдачу; кладовщик не может создавать документы и wizard импорта
  - [x] Критических багов не обнаружено; все 174 теста зелёные
- **Уточнение по сценарию 9 (кладовщик)**: кладовщик имеет право редактировать строки (для подтверждения qty), но не может создавать документы `object.request` и не имеет доступа к wizard импорта — это и проверяется.
- **Критерий готовности**: Все сценарии пройдены; критических багов нет; UX соответствует functional spec.
- **Зависимости**: OBR-017

---

## Этап 8. Автоматизация (этап 2 roadmap)

### Задача: OBR-019 — Автоматический расчёт наличия по физическому остатку

- **Статус**: Выполнена
- **Дата выполнения**: 2026-03-18
- **Приоритет**: Средний
- **Описание**: Автоматически определять qty_on_hand для каждой строки и предлагать разбивку на выдачу/закупку.
- **Шаги выполнения**:
  - [x] Реализовать метод `action_check_stock()` в `object.request`:
    - [x] Для каждой строки с product_id: запросить `qty_available` со склада компании
    - [x] Заполнить `stock_qty_on_hand` и `stock_check_date`
  - [x] Реализовать метод `action_auto_split()`:
    - [x] Для каждой строки: если stock_qty_on_hand >= qty_requested → qty_to_issue = qty_requested
    - [x] Иначе: qty_to_issue = stock_qty_on_hand, qty_to_buy = qty_requested - stock_qty_on_hand
    - [x] Если stock_qty_on_hand == 0 → qty_to_buy = qty_requested
  - [x] Добавить кнопки `Рассчитать наличие` и `Авто-разбивка` (заменить заглушку)
  - [x] `qty_available` уже учитывает резервы (free qty = on_hand − reserved)
- **Критерий готовности**: Автоматический расчёт наличия работает; split на выдачу/закупку корректен. Все 15 тестов зелёные.
- **Зависимости**: OBR-010, OBR-016

### Задача: OBR-020 — Резервирование товаров под требование

- **Статус**: Выполнена ✅
- **Дата выполнения**: 2026-03-18
- **Приоритет**: Средний
- **Описание**: Реализовать резервирование товаров под документ требования до фактической выдачи.
- **Шаги выполнения**:
  - [x] Реализовать резервирование через стандартный механизм `stock.move` / `stock.quant` (через `picking.action_assign()`)
  - [x] Добавить поле `issue_reserved` — Boolean в строке
  - [x] Автоматическое резервирование при создании picking (в `issue_wizard.action_create_issue()`)
  - [x] Снятие резерва при отмене документа (`action_cancel()` вызывает `do_unreserve()`)
  - [x] Отображение зарезервированных количеств в UI (`qty_reserved` в таблице строк, `qty_total_reserved` на вкладке Обработка)
- **Критерий готовности**: Товары резервируются; резерв виден в UI; при отмене — резерв снимается. Все 5 тестов зелёные.
- **Зависимости**: OBR-019, OBR-011

### Задача: OBR-021 — Создание черновиков закупки (RFQ / Purchase Order)

- **Статус**: Не начата
- **Приоритет**: Средний
- **Описание**: По строкам дефицита создавать черновики закупок, сгруппированные по поставщику.
- **Шаги выполнения**:
  - [ ] Создать `wizards/purchase_wizard.py` с моделью `object.request.purchase.wizard`:
    - [ ] `request_id`, `line_ids`, `group_by_vendor` (default=True), `create_draft_only` (default=True), `comment`
  - [ ] Расширить модель `purchase.order` (`_inherit = 'purchase.order'`):
    - [ ] `object_request_ids` — Many2many (обратная сторона rel-таблицы)
    - [ ] `is_object_request_purchase` — Boolean, index
    - [ ] `object_request_project_id` — Many2one `object.request.project`, index
  - [ ] Реализовать метод `action_create_purchase()` в wizard / `object.request`:
    - [ ] Фильтрация строк: qty_to_buy > 0 и product_id и preferred_vendor_id
    - [ ] Группировка строк по preferred_vendor_id
    - [ ] Создание draft `purchase.order` для каждого поставщика
    - [ ] Создание `purchase.order.line` по каждой строке
    - [ ] Обновление связей: `purchase_order_ids` в шапке, `purchase_order_id` и `purchase_order_line_id` в строке
  - [ ] Обработка строк без поставщика:
    - [ ] Оставить в документе как `manual_vendor_required`
    - [ ] Показать предупреждение с количеством таких строк
  - [ ] Реализовать smart button `Закупки`:
    - [ ] Показывает count связанных purchase.order
    - [ ] Открывает tree/form
  - [ ] Заменить заглушку кнопки `Подготовить закупку`
  - [ ] Проверить, что черновики создаются и группируются корректно
- **Критерий готовности**: Черновики закупок создаются; строки сгруппированы по поставщику; связи с документом требования сохраняются.
- **Зависимости**: OBR-019, OBR-010

### Задача: OBR-022 — Модуль согласования

- **Статус**: Не начата
- **Приоритет**: Низкий
- **Описание**: Реализовать workflow согласования документа перед переводом в работу.
- **Шаги выполнения**:
  - [ ] Определить процесс согласования: кто, сколько уровней, правила
  - [ ] Расширить `approval_state`: `not_required`, `pending`, `approved`, `rejected`
  - [ ] Добавить кнопки `Отправить на согласование`, `Согласовать`, `Отклонить`
  - [ ] Реализовать уведомления согласующему
  - [ ] Связать с переходом Черновик → В работе
  - [ ] Проверить workflow согласования
- **Критерий готовности**: Документ проходит согласование; уведомления отправляются; переход в работу блокируется до согласования.
- **Зависимости**: OBR-015

### Задача: OBR-023 — Отчёты и аналитика

- **Статус**: Не начата
- **Приоритет**: Низкий
- **Описание**: Создать отчёты по документам требований, загрузке по объектам, статистику выдач и закупок.
- **Шаги выполнения**:
  - [ ] Определить список отчётов:
    - [ ] Сводка по объекту: всего требований, строк, выдано, закуплено
    - [ ] Незакрытые требования с просроченной датой потребности
    - [ ] Статистика сопоставления: % автоматических, % ручных
  - [ ] Реализовать отчёты через QWeb или pivot view
  - [ ] Добавить меню отчётов в модуль
  - [ ] Проверить корректность данных
- **Критерий готовности**: Отчёты отображают актуальные данные; доступны из меню модуля.
- **Зависимости**: OBR-015, OBR-021

---

## Сводная таблица задач

| ID       | Задача                                                     | Этап | Приоритет    | Статус     | Зависимости                |
|----------|------------------------------------------------------------|------|-------------|------------|----------------------------|
| OBR-001  | Подготовка справочников и demo-данных                      | 0    | Критический | Не начата  | —                          |
| OBR-002  | Каркас модуля `object_request`                             | 1    | Критический | Не начата  | OBR-001                    |
| OBR-003  | Группы доступа и security                                  | 1    | Критический | Выполнена ✅ | OBR-002                  |
| OBR-004  | Базовые модели документа и строк                           | 1    | Критический | Выполнена ✅ | OBR-002, OBR-003          |
| OBR-005  | Меню, tree/form views, search view                         | 1    | Критический | Выполнена ✅ | OBR-004                   |
| OBR-006  | Wizard загрузки Excel-файла                                | 2    | Критический | Выполнена ✅ | OBR-004, OBR-005          |
| OBR-007  | Парсинг, сопоставление и создание строк                    | 2    | Критический | Выполнена ✅ | OBR-006, OBR-001          |
| OBR-008  | Поля и UI сопоставления строк                              | 3    | Высокий     | Выполнена ✅ | OBR-005, OBR-007          |
| OBR-009  | Массовые действия и ускорение сопоставления                | 3    | Средний     | Выполнена ✅ | OBR-008                  |
| OBR-010  | Ручное управление количествами к выдаче                    | 4    | Высокий     | Выполнена ✅ | OBR-008                  |
| OBR-011  | Создание документа выдачи (stock.picking)                  | 4    | Высокий     | Выполнена ✅ | OBR-010                  |
| OBR-012  | Подтверждение выдачи кладовщиком и фиксация                | 4    | Высокий     | Выполнена ✅ | OBR-011                  |
| OBR-013  | Печатная форма требования                                  | 5    | Высокий     | Выполнена ✅ | OBR-005, OBR-004          |
| OBR-014  | Печатная форма расходной накладной                         | 5    | Высокий     | Выполнена ✅ | OBR-011, OBR-012          |
| OBR-015  | State machine документа и строк                            | 6    | Высокий     | Выполнена ✅ | OBR-004, OBR-012          |
| OBR-016  | Заглушки этапа 2                                           | 6    | Низкий      | Выполнена ✅ | OBR-005, OBR-015          |
| OBR-017  | Unit- и интеграционные тесты                               | 7    | Высокий     | Выполнена ✅ | OBR-001 — OBR-016         |
| OBR-018  | Ручные пилотные сценарии                                   | 7    | Средний     | Выполнена ✅ | OBR-017                  |
| OBR-019  | Автоматический расчёт наличия                              | 8    | Средний     | Не начата  | OBR-010, OBR-016           |
| OBR-020  | Резервирование товаров                                     | 8    | Средний     | Выполнена ✅ | OBR-019, OBR-011          |
| OBR-021  | Черновики закупки (RFQ / Purchase Order)                   | 8    | Средний     | Не начата  | OBR-019, OBR-010           |
| OBR-022  | Модуль согласования                                        | 8    | Низкий      | Не начата  | OBR-015                    |
| OBR-023  | Отчёты и аналитика                                         | 8    | Низкий      | Не начата  | OBR-015, OBR-021           |

---

## Рекомендуемый порядок реализации

### Инкремент 1 — Каркас и модели (MVP foundation)
1. **OBR-001** — Подготовка справочников и demo-данных
2. **OBR-002** — Каркас модуля
3. **OBR-003** — Группы доступа и security
4. **OBR-004** — Базовые модели документа и строк
5. **OBR-005** — Меню, views, search

### Инкремент 2 — Excel импорт
6. **OBR-006** — Wizard загрузки Excel
7. **OBR-007** — Парсинг и создание строк

### Инкремент 3 — Сопоставление и обработка
8. **OBR-008** — Поля и UI сопоставления
9. **OBR-009** — Массовые действия
10. **OBR-010** — Количества к выдаче

### Инкремент 4 — Складская обработка
11. **OBR-011** — Создание выдачи
12. **OBR-012** — Подтверждение кладовщиком

### Инкремент 5 — Печать и финализация MVP
13. **OBR-013** — Печатная форма требования
14. **OBR-014** — Печатная форма расходной накладной
15. **OBR-015** — State machine
16. **OBR-016** — Заглушки этапа 2

### Инкремент 6 — Тестирование
17. **OBR-017** — Unit- и интеграционные тесты
18. **OBR-018** — Ручные пилотные сценарии

### Инкремент 7 — Автоматизация (этап 2)
19. **OBR-019** — Расчёт наличия
20. **OBR-020** — Резервирование
21. **OBR-021** — Черновики закупки
22. **OBR-022** — Согласование
23. **OBR-023** — Отчёты

---

## Критерии готовности MVP (чеклист)

- [ ] Пользователь может создать документ по объекту
- [ ] Можно импортировать Excel фиксированного формата
- [ ] Строки сохраняются даже при несопоставленной номенклатуре
- [ ] Снабженец может вручную сопоставить строки
- [ ] Можно указать поставщика и допустимые замены
- [ ] Можно частично выдать материалы со склада
- [ ] Кладовщик может подтвердить фактическую выдачу
- [ ] Доступны печатные формы требования и выдачи
- [ ] Документ проходит путь Черновик → В работе → Закрыто
- [ ] Права доступа разграничены по ролям
- [ ] Unit-тесты проходят
- [ ] Пилотные сценарии пройдены без критических багов

---

## Принятые решения (из [data model spec](datamodelspecobjectrequest.md))

1. ~~**Модель объекта**~~ → отдельная модель `object.request.project` (не `project.project`)
2. ~~**Зоны/этажи/участки**~~ → отдельные `Char`-поля (`zone`, `floor`, `section`); нормализация в отдельные модели — позже
3. ~~**Роли**~~ → привязка к `res.users` (не `res.partner`, не `hr.employee`)
4. **Цена из Excel** → сохраняется как `price_raw` (Float, справочное поле без бизнес-логики в MVP)

## Открытые вопросы (требуют решения до реализации)

1. **Закрытие документа**: только после полного обеспечения или по явному решению пользователя?
2. **Тип picking для выдачи**: Internal Transfer или отдельный picking type?
