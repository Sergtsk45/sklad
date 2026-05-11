# Tasktracker: Удаление поля «Склад» у прораба и multi-warehouse выдача

## Контекст и цель

**Проблема.** Сейчас на требовании (`object.request`) поле `warehouse_id` (Склад) обязательно и фактически фиксирует «один склад на весь документ». Прораб вынужден его выбирать, а вся выдача идёт одной накладной из одной локации, даже если позиции лежат на разных складах. Для расчёта остатков существует `check_warehouse_ids`, но это лишь сумма — без понимания, что и откуда выдавать.

**Цель.** Перенести логику склада на уровень **строки/распределения**:
- прораб **не выбирает склад** при создании требования;
- расчёт наличия идёт **по всем активным складам компании** автоматически;
- по каждой строке видно: **сколько и с какого склада к выдаче** и **сколько к закупке**;
- снабженец **может вручную перенаправить** распределение (вплоть до «купить всё, даже если есть на складе»);
- при формировании выдачи создаётся **по одному `stock.picking` на каждый склад**;
- склад **приёмки** для PO определяется **складом объекта** (создаётся автоматически при создании объекта).

## Принятые решения (по итогам уточнений)

| # | Развилка | Решение |
|---|----------|---------|
| 1 | Судьба `object.request.warehouse_id` | **Полностью удалить** из модели; склад приёмки PO выбирается в wizard закупки (см. п. 7) |
| 2 | Источник списка складов для расчёта остатков | **Все активные склады компании** автоматически (без UI-выбора) |
| 3 | Хранение распределения по складам в строке | Новая модель **`object.request.line.stock`** (строка, склад, на_складе, к_выдаче); основная строка хранит итоги (компьютед/store) |
| 4 | Алгоритм авто-разбивки между складами | **Минимизация числа складов**: один склад, где хватает; иначе подключаются следующие по убыванию остатка |
| 5 | UX «купить всё, хотя есть на складе» | **Ручная правка** + **массовые кнопки** «Закупить всё», «Выдать максимум», «Сбросить разбивку» |
| 6 | Создание нескольких выдач | **Wizard-предпросмотр** с группировкой по складам: по каждой группе можно подтвердить/исключить, задать дату/комментарий |
| 7 | Склад приёмки PO | При создании **объекта** (`object.request.project`) автоматически создаётся **`stock.warehouse`** с именем «{project.name} склад» и привязкой к объекту; этот склад — приёмочный по умолчанию для PO |
| 8 | Код склада объекта (≤ 5 симв.) | **Сквозная нумерация** `O001`, `O002`, … при создании объекта; код склада хранится на объекте и используется как `stock.warehouse.code` |
| 9 | Переименование объекта | **Не допускается** (бизнес-правило): после `create()` поле `name`/`code` объекта недоступно для изменения (read-only кроме админа). Соответственно, склад тоже не переименовывается |
| 10 | Архивация объекта | При `active=False` объекта **архивируется и склад** вместе с остатками; перспективно — списание на объект через **КС-2** (отдельная задача) |
| 11 | Видимость распределения у прораба | Только **итог** (`qty_to_issue`, `qty_to_buy`, `qty_issued`); вложенный список `stock_ids` прорабу скрыт |
| 12 | Wizard «есть на складе» (`stock_check_wizard`) | **Оставляем как предупреждение**; после «ОК» закрывается без сохранения флага в требовании (`stock_check_confirmed` удалён) |
| 13 | Перерасчёт авто-разбивки при ручных правках | **Предупреждать** снабженца перед перезаписью `qty_to_issue` (модальное окно «План был отредактирован вручную — перезаписать?») |
| 14 | Регенерация AI knowledge pack | **Отдельная задача**, не блокирует эту |

## Затронутые сущности и файлы

- `custom_addons/object_request/models/object_request.py` — удалить `warehouse_id`, `check_warehouse_ids`, `stock_check_confirmed`; переписать `action_check_stock`, `action_auto_split`, `action_open_issue_wizard`, `action_open_purchase_wizard`.
- `custom_addons/object_request/models/object_request_line.py` — заменить `stock_qty_on_hand`/`stock_check_date` на агрегаты по дочерней модели; добавить `stock_ids` (One2many).
- `custom_addons/object_request/models/object_request_project.py` — добавить `warehouse_id` (M2O, авто-создание), хук `create()`/`write()` для имени склада.
- **Новая модель** `custom_addons/object_request/models/object_request_line_stock.py` — `(line_id, warehouse_id, qty_on_hand, qty_to_issue, qty_reserved, last_check_date)`.
- `custom_addons/object_request/wizards/issue_wizard.py` + views — переделать в **multi-picking preview wizard** (группы по складам).
- `custom_addons/object_request/wizards/purchase_wizard.py` + views — брать склад приёмки из объекта (`request.project_id.warehouse_id`).
- `custom_addons/object_request/wizards/import_excel_wizard.py` + views — убрать выбор склада в импорте.
- `custom_addons/object_request/wizards/stock_check_wizard.py` — переосмыслить или удалить (предупреждение «есть на складе» теперь имеет смысл per-line per-warehouse).
- `custom_addons/object_request/views/object_request_views.xml` — убрать поля шапки, добавить вложенный список распределения по складам в строке (или отдельный таб «Размещение по складам»).
- `custom_addons/object_request/security/*` — настроить, кто может править распределение (только снабженец/админ).
- `custom_addons/object_request/migrations/19.0.x.x.x/pre-migrate.py` и `post-migrate.py` — миграция данных.
- Тесты `tests/test_obr0XX_*` — обновить все падающие на отсутствие `warehouse_id`; добавить новые на multi-warehouse.

## План работ

### Этап 0. Подготовка и заморозка решений
- [ ] Подтвердить с пользователем оставшиеся открытые вопросы (см. ниже).
- [x] Зафиксировать в `docs/changelog.md` начало миграции структуры данных модуля `object_request`.
- [x] Зафиксировать в `docs/project.md` обновлённую схему данных и поток выдачи (mermaid-диаграмма).

### Этап 1. Склад на уровне объекта
- [x] Добавить в `object.request.project`:
  - `warehouse_id = Many2one('stock.warehouse', readonly=True, copy=False)` — связанный склад объекта.
  - Изменить `code` на **автогенерируемое** поле (sequence `object.request.project.code`, формат `O%(num)03d`, ≤ 5 символов, `readonly=True, copy=False`).
- [x] `name` и `code` объекта: **запрет на изменение** после `create()`:
  - реализовать через `write()`-override: при попытке сменить `name`/`code` — `UserError('Переименование объекта запрещено')`;
  - в UI пометить поля `readonly="id != False"`.
- [x] При `create()` объекта автоматически создавать `stock.warehouse`:
  - `name = f"{project.name} склад"`;
  - `code = project.code` (готовая `O001` форма из sequence; коллизий не будет за счёт уникальности sequence);
  - `company_id = project.company_id` (или `env.company`).
- [x] При `write({'active': False})` объекта — каскадно `warehouse_id.active = False` (и наоборот при разархивации, если задано).
- [x] Запрет `unlink` объекта, если есть `request_ids` или остатки на складе (`stock.quant` с `quantity > 0` в локациях склада) → `UserError`.
- [x] Sequence-запись `object_request_project_code_sequence` в `data/sequence.xml`.
- [x] Тесты:
  - создание объекта без указания склада → склад создан, `code` имеет формат `O001`;
  - попытка переименовать объект → `UserError`;
  - архивация объекта → склад тоже архивирован;
  - удаление объекта с остатками → `UserError`.

### Этап 2. Удаление шапочных полей склада из требования
- [x] Удалить из `object.request`: `warehouse_id`, `check_warehouse_ids`, `stock_check_confirmed`.
- [x] Перенести зависимые методы (см. этапы 3–6).
- [x] Удалить эти поля из XML-вью, wizard-форм и тестовых фабрик актуального пользовательского потока.
- [x] Удалить таблицу M2M `object_request_check_warehouse_rel` (миграция).

### Этап 3. Модель распределения по складам в строке
- [x] Создать `object.request.line.stock`:
  ```
  line_id (M2O object.request.line, required, ondelete=cascade, index)
  warehouse_id (M2O stock.warehouse, required, index)
  qty_on_hand (Float)               # рассчитан Рассчитать наличие
  qty_to_issue (Float, default=0)   # план выдачи с этого склада
  qty_reserved (Float, default=0)   # резерв (этап 2)
  last_check_date (Datetime)
  picking_id (M2O stock.picking)    # созданная выдача
  UNIQUE(line_id, warehouse_id)
  ```
- [x] В `object.request.line` добавить `stock_ids = One2many('object.request.line.stock', 'line_id')`.
- [x] Перевести `stock_qty_on_hand`, `qty_to_issue` на **сумму по `stock_ids`** (stored sync при изменении распределения).
- [x] `stock_check_date` → `max(stock_ids.last_check_date)` через stored sync.
- [x] Добавить ACL и record rules в `ir.model.access.csv` / `*_security.xml` для прораба/снабженца/кладовщика.

### Этап 4. Расчёт наличия по всем складам компании
- [x] Переписать `action_check_stock`:
  - получить `warehouses = env['stock.warehouse'].search([('company_id', '=', request.company_id.id), ('active', '=', True)])`;
  - для каждой строки c `product_id` для каждого склада посчитать `qty_available` через `read_group` по `stock.quant` (одним запросом по всем (product_id, location_id) парам — избегаем N×M обращений);
  - upsert строк `object.request.line.stock` (создать/обновить `qty_on_hand`, `last_check_date`);
  - удалить `line.stock_ids`, ссылающиеся на неактивные/удалённые склады;
  - повторно показывать предупреждение при наличии остатков (без `stock_check_confirmed`, поле удалено в этапе 2).
- [x] `stock_check_wizard` оставить как предупреждение:
  - открывается, если хотя бы одна строка с `sum(stock_ids.qty_on_hand) > 0`;
  - показывает наименование, товар и **складскую раскладку** (с какого склада сколько);
  - кнопка «ОК, ознакомлен» закрывает предупреждение (без сохранения `stock_check_confirmed`, поле удалено в этапе 2).
- [x] Тесты: 1 склад / N складов / товар без остатков / товар не сопоставлен / wizard открывается при наличии и не открывается без.

### Этап 5. Авто-разбивка с минимизацией числа складов
- [x] Переписать `action_auto_split` по строке:
  1. отсортировать `stock_ids` по убыванию `qty_on_hand`;
  2. найти **первый** склад, где `qty_on_hand >= qty_requested - qty_issued` → выдать всё с него;
  3. иначе жадно сверху: брать `min(qty_on_hand, остаток_к_выдаче)` пока не закроем требование или не закончатся склады;
  4. остаток → `qty_to_buy` (на уровне строки, без склада; склад приёмки = склад объекта).
- [x] Защита ручных правок: если у требования есть строки c `manual_plan_override = True` (новое булево на строке, ставится при ручной правке `qty_to_issue` в `stock_ids`), запускать `auto_split` через **подтверждающий wizard** `object.request.auto.split.confirm.wizard`:
  - текст: «План распределения был отредактирован вручную для N строк. Перезаписать?»
  - кнопки «Перезаписать» / «Отмена»; при перезаписи флаг `manual_plan_override` сбрасывается.
- [x] Алгоритм игнорирует склад объекта (`project.warehouse_id`), если на нём **нулевые** остатки, и использует его первым при положительном остатке.
- [x] Тесты: хватает на одном складе; нужно с двух; не хватает суммарно (часть в закупку); требование уже частично выдано; ручная правка → wizard предупреждения.

### Этап 6. Wizard выдачи с группировкой по складам
- [x] Новый transient `object.request.issue.preview.wizard`:
  - поля: `request_id`, `group_ids = One2many('object.request.issue.preview.group')`;
  - дочерняя `object.request.issue.preview.group`: `(wizard_id, warehouse_id, picking_type_id, source_location_id, dest_location_id, scheduled_date, comment, line_ids, included)`;
  - default_get: разложить `request.line_ids.stock_ids.filtered(qty_to_issue > 0)` по складам, заполнить параметры из `warehouse`.
- [x] Кнопка `Создать выдачи`: для каждой включённой группы → один `stock.picking` + moves; результат — действие открыть список созданных pickings.
- [x] Сохранить `picking_id` в каждой `object.request.line.stock` строке группы.
- [x] Тесты: 1 склад → 1 picking; 2 склада → 2 picking; исключение группы; пустой план.

### Этап 7. Wizard закупки
- [x] В `purchase_wizard` склад приёмки = `request.project_id.warehouse_id.in_type_id`; при отсутствии — fallback (предложить snabzhenec выбрать склад приёмки в самом wizard).
- [x] Тесты: PO создан с правильным `picking_type_id` объекта; fallback при отсутствии склада объекта.

### Этап 8. Массовые UX-действия для снабженца
- [x] На вкладке «Строки» (или «Размещение по складам») добавить **серверные кнопки** над списком строк:
  - «Закупить всё» (выбранные строки): обнулить `qty_to_issue` во всех `stock_ids`, выставить `qty_to_buy = qty_requested - qty_issued`.
  - «Выдать максимум»: re-запустить алгоритм авто-разбивки только для выбранных строк.
  - «Сбросить разбивку»: обнулить `qty_to_issue`/`qty_to_buy` для выбранных.
- [x] Inline-редактирование `stock_ids`: снабженец может править `qty_to_issue` по складам вручную (с валидацией суммы ≤ `qty_requested - qty_issued`).
- [x] Видимость кнопок и редактирования — по группам безопасности (`group_supply_manager`).

### Этап 9. UI прораба vs снабженца
- [x] **Прораб**: в строках видит только **итоги** (`qty_requested`, `qty_to_issue`, `qty_to_buy`, `qty_issued`, `stock_qty_on_hand_total`). Вложенный список `stock_ids` **скрыт** через `groups="object_request.group_supply_manager"` на полях/таблице.
- [x] **Снабженец**: полный доступ к `stock_ids` (inline-таблица в expand row или отдельный таб «Размещение по складам»), массовые кнопки, ручное редактирование `qty_to_issue` по складам.
- [x] **Кладовщик**: просмотр распределения по складам без правки (`readonly="1"`).
- [x] Поле объекта `code` и `name` — readonly после `create()` в form view; sequence-код виден в read-only.

### Этап 10. Миграция БД
- [x] `pre-migrate.py`:
  - забэкапить в noupdate-таблицу `_legacy_object_request_warehouse` пары `(request_id, warehouse_id)` и `(request_id, check_warehouse_id)` — для возможного отката.
- [x] `post-migrate.py`:
  - для каждого существующего объекта без `warehouse_id`:
    - если у объекта **не задан** `code` — сгенерировать через новый sequence (`O001` и далее);
    - создать `stock.warehouse` с `name = f"{project.name} склад"`, `code = project.code`;
    - привязать `project.warehouse_id`.
  - для каждой существующей строки требования с `stock_qty_on_hand > 0`:
    - создать одну `object.request.line.stock` (warehouse = старый `request.warehouse_id`, `qty_on_hand` из строки, `qty_to_issue` = текущее значение строки).
- [ ] DROP колонок `object_request.warehouse_id`, M2M-таблицы `object_request_check_warehouse_rel`, поля `stock_qty_on_hand`/`stock_check_date` на строке (после переноса).
  - [x] `object_request.warehouse_id`, `object_request.stock_check_confirmed` и `object_request_check_warehouse_rel` удаляются post-migrate.
  - [ ] `stock_qty_on_hand`/`stock_check_date` пока оставлены как агрегатные поля текущей модели; удалить после перевода их в computed/store или замены во всех view/tests.
- [x] Smoke-тест миграции на копии текущей dev-БД `odoo19_local`.

### Этап 11. Чистка тестов и фабрик
- [x] Все тесты, использующие `'warehouse_id': self.warehouse.id` в `object.request.create()`, переписаны.
- [x] `test_obr024_warehouse.py` заменён тестами новой схемы: склад на объекте + `object.request.line.stock`.
- [x] `test_obr025_multiwarehouse_check.py` переписан под расчёт по всем активным складам и новую модель `line.stock`.
- [x] `test_obr011_issue_picking.py`, `test_obr012_confirm_issue.py` дополнены сценариями multi-warehouse.

### Этап 12. Документация
- [x] Обновить `docs/datamodelspecobjectrequest.md`: новая модель `object.request.line.stock`, склад на объекте.
- [x] Обновить `docs/functionalspecobjectrequest.md`: UI прораба/снабженца, новый wizard, массовые действия.
- [x] Обновить `docs/changelog.md` (Изменено: схема склада; Добавлено: per-warehouse распределение, multi-picking wizard).
- [x] Дополнить `docs/project.md`: mermaid-диаграмма потока «требование → расчёт → разбивка → выдача N pickings + PO».
- [x] Обновить `docs/tasktracker.md`: добавить ссылку на этот файл, статус «В процессе».

## Зафиксированные ответы (закрытые вопросы)

| Вопрос | Решение |
|--------|---------|
| Код склада объекта | Сквозная нумерация `O001`, `O002`, … через Odoo sequence; поле `code` объекта — readonly, генерируется при `create()` |
| Переименование объекта | **Запрещено**: `name`, `code` объекта read-only после создания (override `write()` + UI `readonly`) |
| Архивация объекта | `active=False` объекта → каскадно `warehouse_id.active = False` (остатки сохраняются для последующего КС-2) |
| Существующие объекты без склада | Миграцией создаём склад; `code` догенерируем через тот же sequence |
| Видимость распределения для прораба | Только **итог** (`qty_requested`, `qty_to_issue`, `qty_to_buy`, `qty_issued`); `stock_ids` скрыт ACL |
| Резервы (`qty_reserved`) | Использовать `free_qty` (`qty_available - reserved_quantity`) из `stock.quant` как «доступно к выдаче» |
| Wizard `stock_check_wizard` | **Остаётся** как предупреждение; после кнопки «ОК, ознакомлен» закрывается без сохранения `stock_check_confirmed` (поле удалено) |
| Перерасчёт авто-разбивки | Если есть `manual_plan_override` — открывается **подтверждающий wizard** перед перезаписью |
| AI knowledge pack | **Отдельная задача** после завершения этой; в её рамках регенерация не делается |

## Перспективные задачи (вне scope)

- **Списание на объект через КС-2.** Архивный склад объекта продолжает хранить движения; для отчётности КС-2 потребуется отдельный модуль/wizard, который читает все `stock.move` со списанием в локации заказчика / на объект и формирует акт. Спроектируется отдельно.
- **Регенерация AI knowledge pack** (`custom_addons/ai_assistant/static/knowledge/generated/object_request_context.md`).

## Зависимости

- Модуль `object_request` (текущая версия).
- Стандартные Odoo: `stock` (warehouse, picking, move, quant), `purchase` (PO, picking_type), `mail` (chatter).
- `docs/datamodelspecobjectrequest.md`, `docs/functionalspecobjectrequest.md`, `docs/roadmapobjectrequest.md` — будут обновлены.

## Риски

| Риск | Митигация |
|------|-----------|
| Сломанная миграция: потеря привязки старых требований к складу | `pre-migrate` бэкап + dry-run на dev-БД |
| Производительность `qty_available` по N складам × M строкам | Кэширование `with_context(location=…).qty_available`, единый поход в `stock.quant` через `read_group` |
| Конфликт имени/кода склада при автосоздании | Атомарный hook + `for code in candidates: try` с retry |
| Чрезмерная сложность UI (вложенные списки складов в строках) | Альтернатива: отдельный таб «Размещение по складам» в форме требования |
| Регрессии в существующих 26+ тестах | Поэтапный запуск `--test-tags` по модулям OBR-XXX |

## Метрика готовности

- [x] Все тесты модуля `object_request` зелёные (`docker exec odoo19-local odoo --test-enable --test-tags /object_request -u object_request -d odoo19_local --stop-after-init --http-port=8071`).
- [ ] flake8 чистый (`docker exec odoo19-local python -m flake8 /mnt/extra-addons/object_request`).
- [ ] Smoke-сценарий вручную:
  1. Создать объект «Тест» — склад «Тест склад» создан автоматически.
  2. Прораб создаёт требование (поля «Склад» нет).
  3. «Рассчитать наличие» — по строкам видны остатки по нескольким складам.
  4. «Авто-разбивка» — план выдачи распределён, остаток в закупку.
  5. Снабженец нажимает «Закупить всё» по одной строке — `qty_to_issue` обнуляется.
  6. «Создать выдачи» — wizard показывает 2 группы (по складам), создаёт 2 `stock.picking`.
  7. «Подготовить закупку» — PO с приёмкой на склад объекта.
- [x] Документация (`changelog`, `project`, `datamodelspec`, `functionalspec`) обновлена.

## Связанные задачи

- `docs/tasktracker.md` → раздел «Поле «Склад» в заявке на комплектацию» (теперь отменяется/переосмысливается этой задачей).
- `docs/tasktracker.md` → раздел «Проверка наличия по нескольким складам в комплектации объектов» (логика переезжает в новую модель).
