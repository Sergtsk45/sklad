## [2026-08-17] — Закупки: колонки Объект и Склад в списках

### Добавлено
- В списках заказов на закупку (RFQ и PO) колонки **Объект** и **Склад**.
- В истории закупок товара (смарт-кнопка «Закупки») те же колонки, чтобы
  не открывать каждый заказ.

### Изменено
- Версия: `object_request` `19.0.1.10.13`.
- Prod deploy `014463b`: backup
  `/opt/project_odoo/backups/po-object-warehouse-columns-20260817-070623/`,
  `-u object_request` → `19.0.1.10.14`, restart; health `pass`, `/web/login`
  HTTP 200.

## [2026-08-17] — Закупки: полное наименование в строке PO из каталога

### Исправлено
- При создании закупки из требования в Description строки PO записывается
  `product_id.display_name`, а не сокращённый `name_raw` из Excel (например,
  «сетка» → полное имя из каталога).
- Версия: `object_request` `19.0.1.10.14`.

## [2026-08-17] — Закупки: подпись кнопки печати передаточной ведомости

### Изменено
- В форме заказа на закупку (модуль «Комплектация объектов») кнопка «Печать»
  переименована в «Печать передаточной ведомости» (RFQ и подтверждённый PO).
- В AI-ассистенте действие печати закупки использует ту же подпись.
- Prod deploy `5bf466d`: backup
  `/opt/project_odoo/backups/po-print-transfer-act-20260817-063922/`,
  `-u object_request,ai_assistant`, restart; `/web/login` HTTP 200.

## [2026-08-13] — OR: статус строки «Ожидает счёт от поставщика» (OBR-039)

### Добавлено
- Ручная отметка строки **«Счёт запрошен»** (`supplier_invoice_requested`).
- Вычисляемый статус **«Ожидает счёт от поставщика»** (синий `decoration-info`).
- Фильтр строк **«Ожидает счёт»**.
- Галочку ставит снабженец при выбранном поставщике; товар и завершённое
  сопоставление не обязательны. Статус информационный: закупку и выдачу
  не блокирует.

### Изменено
- Версия: `object_request` `19.0.1.10.12`.
- Prod deploy `a42e2f3`: backup
  `/opt/project_odoo/backups/or-obr039-line-wait-invoice-20260812-233620/`,
  `-u object_request` → `19.0.1.10.12`, restart; health `pass`, `/web/login`
  HTTP 200.

## [2026-08-13] — OR: фиксация состава строк в статусе «В работе»

### Изменено
- В `object.request` со статусом `in_progress` (а также `closed`/`cancelled`)
  нельзя добавлять и удалять строки и менять `qty_requested`.
- Серверная защита в `object.request.line` (`create` / `unlink` / `write`);
  в UI снабженца `create`/`delete` доступны только в черновике через
  `options` на `line_ids` (`state = draft`). Сопоставление и план
  выдачи/закупки в работе не блокируются.
- Дубликат требования всегда создаётся как черновик (`state` `copy=False`).
- Версия: `object_request` `19.0.1.10.11`.

### Исправлено
- Удаление строки в `in_progress` больше нельзя обойти RPC-контекстом
  `object_request_allow_line_unlink`. Каскад при удалении документа идёт
  через приватный `_unlink_from_parent_request`.
- `create`/`delete` на `<list>` больше не используют выражение
  `parent.state == 'draft'`: в Odoo 19 это статически True. Условие
  перенесено в `options` поля `line_ids`.

## [2026-08-12] — OR: основной поставщик в поиске товара без vendor (OBR-038)

### Исправлено
- Без выбранного поставщика в строке OR `web_name_search` показывает в
  `__formatted_display_name` основного seller по `_prepare_sellers()` компании
  требования (тот же порядок, что в onchange).
- Без `CTX_REQUEST_COMPANY` или без seller у товара поведение не меняется.
- Версия: `object_request` `19.0.1.10.8`.
- Prod deploy `b5b9e58`: backup
  `/opt/project_odoo/backups/or-primary-seller-web-search-20260812-083027/`,
  `-u object_request` → `19.0.1.10.8`, restart; health `pass`, `/web/login` HTTP 200.

## [2026-08-12] — OR: суффикс поставщика в web_name_search (OBR-038)

### Исправлено
- При выбранном поставщике в OR формирование `__formatted_display_name`
  использует суффикс `— {vendor}` без дублирования; `display_name` остаётся
  чистым.
- Обновлены regression-тесты Odoo 19 web_name_search под новый формат.
- Версия: `object_request` `19.0.1.10.9`.
- Prod deploy `9941895`: backup
  `/opt/project_odoo/backups/or-suffix-vendor-web-name-search-20260812-085716/`,
  `-u object_request` → `19.0.1.10.9`, restart; health `pass`, `/web/login`
  HTTP 200.

## [2026-08-12] — OR: префикс поставщика в поиске товара (OBR-038)

### Исправлено
- При выбранном поставщике в OR метки поиска товара показывают
  `[Поставщик]` и торговое имя из прайса; `display_name` остаётся чистым.
- `web_name_search` (Odoo 19) декорирует `__formatted_display_name` без
  дублирования префикса; пустой поиск и ранний limit тоже получают префикс.
- Версия: `object_request` `19.0.1.10.7`.
- Prod deploy `6a14505`: backup
  `/opt/project_odoo/backups/or-vendor-web-name-search-20260812-080448/`,
  `-u object_request` → `19.0.1.10.7`, restart; health `pass`, `/web/login` HTTP 200.

## [2026-08-12] — feat(ai_assistant): флаг пополнения в Настройки

### Добавлено
- В «Настройки → AI-консультант → Поведение» отдельный переключатель
  **«Пополнение товара через чат»** (`ai_assistant.replenishment_enabled`).
- Gate пополнения: `enabled` + `actions_enabled` + `replenishment_enabled`
  (если параметр ещё не создан — считается включённым, как до флага).
- Версия: `19.0.1.2.2`.
- Prod deploy `2636928`: `-u ai_assistant` → `19.0.1.2.2`; параметр
  `replenishment_enabled=True` (как работало до флага).

## [2026-08-12] — fix(ai_assistant): флаг перемещений в меню Настройки

### Исправлено
- Блок настроек AI обёрнут в `<app>` (как Purchase/Stock в Odoo 19), чтобы
  раздел **«AI-консультант»** появился в левом меню «Настройки».
- Флаг `ai_assistant.moving_enabled` вынесен в отдельный `setting`
  «Перемещения между складами через чат». Версия: `19.0.1.2.1`.

## [2026-08-11] — AI Assistant: перемещение товара между складами через чат

### Добавлено
- Гибридный moving workflow: LLM извлекает только дословные параметры, а поиск
  записей, UoM, остаток, переходы и создание draft `stock.picking` выполняет
  детерминированный backend.
- Button-first диалог с server-driven кнопками выбора, изменения и отмены на
  каждом нетерминальном шаге; непонятный текст не изменяет сессию.
- Проверка доступного остатка по внутренним дочерним локациям источника,
  отдельное разрешение недостачи и повторная revalidation перед Execute.
- Generic ResultCard для workflow-записей с защищёнными действиями Reserve,
  Open, Print и Cancel; Validate остаётся только в стандартном UI Odoo.
- Отдельный выключенный по умолчанию feature flag
  `ai_assistant.moving_enabled`; доступ требует групп «AI Assistant /
  Снабжение» и Stock User.

### Деплой
- Prod `77c4b45`: backup
  `/opt/project_odoo/backups/ai-moving-20260811-203912/`,
  `-u ai_assistant` → `19.0.1.2.0`, restart; health `pass`.
  Флаг `moving_enabled` по умолчанию выключен.

### Ограничения
- TTL-сессии и execute-lock пока process-local. Для production с несколькими
  Odoo workers требуется общее DB/Redis-хранилище и распределённый execute-once;
  работа отслеживается в TD-011.

## [2026-08-11] — Номенклатура: полная синхронизация переводов name (весь каталог)

### Исправлено
- По всему активному каталогу (`1106` карточек) синхронизированы все
  рассинхроны `en_US ≠ ru_RU` в `product.template.name`: **127** записей.
- Канон — значение `en_US` (результат нормализаций); запись в оба языка
  через `context lang` по правилу `odoo-product-catalog.mdc`.
- Повторный скан: **0** расхождений; `отвод стальн` (ru_RU) = **38**.
- Затронуты в т.ч. переходы, краны, тройники, теплоизоляция, фланцы Ру10,
  батарейки/элементы питания и др.; `product.supplierinfo` не менялся.

## [2026-08-11] — Номенклатура: синхронизация переводов названий в ru_RU + en_US

### Исправлено
- Синхронизированы переводы названий товаров на основе языковой политики, 
  определённой в `.cursor/rules/odoo-product-catalog.mdc` (основной язык ru_RU, 
  write с context lang, синхрон ru_RU+en_US).
- 38 отводов стальных: исправлено 35 записей (3 уже совпадали); 
  search_count ru_RU «отвод стальн» = 38.
- 6 фланцев (id 715–720): исправлены переводы названий.
- Всего изменено 41 карточка товара.
- supplierinfo не трогали.
- Пример: id 77 ru было «Отвод 57х3.5» → синхронизировано с нормализованным 
  «Отвод стальной 57×3,5 (Ду50)» в обе стороны.

## [2026-08-11] — AI Assistant: словоформы в поиске пополнения

### Исправлено
- Формы «пополнения», «пополнению» и «пополнением» запускают workflow так же,
  как «пополнение».
- `product_query` сохраняется дословно из сообщения: если structured LLM
  склонил или перефразировал товар, backend восстанавливает исходную фразу.
- После нулевого точного результата выполняется консервативный поиск по русским
  основам слов. Морфологические совпадения помечаются как нечёткие и всегда
  требуют ручного выбора, даже при одном кандидате.
- Версии: `ai_assistant` `19.0.1.1.1`, `custom_product_search` `19.0.1.1.0`.
- Prod deploy `fb8cc98`: backup
  `/opt/project_odoo/backups/ai-assistant-morph-search-20260811-125958/`,
  `-u ai_assistant,custom_product_search` → `19.0.1.1.1` / `19.0.1.1.0`,
  restart; health `pass`, `/web/login` HTTP 200.

## [2026-08-11] — AI Assistant: пополнение товара через чат

### Добавлено
- Гибридный workflow пополнения: structured LLM-extractor без action tools и
  детерминированная state machine товар → количество/UoM → поставщик → склад → PO.
- Выбор применимой vendor-строки через штатный `_select_seller()` Odoo с учётом
  `min_qty`, скидки, UoM, валюты будущего PO и округления закупочного количества.
- ResultCard с защищёнными действиями Send RFQ / Confirm / Print / Cancel только
  для PO текущей server-side сессии.
- Раздельный lifecycle active-token диалога и post-PO token карточки.
- Версия модуля: `19.0.1.1.0`.

### Безопасность
- Закупочные цены доступны только группе «AI Assistant / Снабжение».
- PO-действия не зарегистрированы в ToolRegistry и не вызываются LLM.
- ID товара, supplierinfo, склада и PO проверяются по server-side состоянию.

### Изменено
- Prod deploy `8bdb07b`: backup
  `/opt/project_odoo/backups/ai-assistant-replenishment-20260811-120028/`,
  `-u ai_assistant` → `19.0.1.1.0`, restart; health `pass`, `/web/login` HTTP 200.
  На VPS установлен `jsonschema` в volume `odoo-web-data` (`/var/lib/odoo/.local`).

## [2026-08-11] — Docs: частичная приёмка и бэкордер

### Добавлено
- Инструкция [`docs/instruction-partial-receipt-backorder.md`](instruction-partial-receipt-backorder.md)
  со скриншотами (`docs/screenshots/partial-receipt-backorder/`): принять факт,
  создать обратный заказ при ожидаемом довозе; счёт не трогать.
- Пример prod: `P00090` → `Офис/IN/00015` (5) → `Офис/IN/00016` (1).

## [2026-08-11] — Склады: включён Buy to Resupply на всех складах

### Исправлено
- На 7 складах включено «Покупать для пополнения» (`buy_to_resupply`):
  Офис. Стеллаж, Основной склад, Склад металла, Цех, БАЗА, Сервис,
  Кабинет Директора.
- Восстановлены правила Buy (в т.ч. «Офис: Полки (Buy)») — пополнение
  на «Офис/Полки» снова возможно.
- Остальные 10 складов уже имели Buy; итого все 17 складов с активным
  маршрутом Buy.

## [2026-08-11] — Номенклатура: разделение фланцев Ду32 Ру10 и Ру16

### Добавлено
- Карточка id **1231** `Фланец стальной Ду32 Ру10` с vendor-строками Башняк
  и Татаринов.

### Исправлено
- Из карточки `Фланец стальной Ду32 Ру16` перенесены vendor-строки, где
  поставщики явно указывали PN10; PN10 и PN16 больше не смешиваются.

## [2026-08-11] — Номенклатура: нормализация фланцев Ду32–100 Ру16

### Изменено
- Единый формат имени: **«Фланец стальной Ду{N} Ру16»**.
- Мастера: id **715–720**; переименованы с серии «DN…, PN 16» (у Ду32 исправлено
  ошибочное «PN 10» в названии).
- Слиты дубли (vendor + остатки, архив):
  - Ду32: 547, 1059 → 715
  - Ду40: 548 → 716
  - Ду50: 549, 1060 → 717
  - Ду65: 550 → 718 (+12 шт)
  - Ду80: 551 → 719 (+2 шт)
  - Ду100: только переименование 720

## [2026-08-11] — Номенклатура: слияние LR-отводов в нормализованные карточки

### Изменено
- По принципу «один типоразмер — одна карточка, бренды/LR в vendor»:
  - **Ду32** id 73 ← архив 721 (ранее)
  - **Ду40** id 74 ← архив 722 (+ остаток 40 шт на Ос.ск)
  - **Ду50** id 77 ← архив 723 (+ 11 шт)
  - **Ду65** id 76 ← архив 724 (+ 58 шт)
  - **Ду80** id 82 ← архив 725 (+ 36 шт)
  - **Ду100** id 114 ← архив 726 (+ 40 шт)
- Vendor Башняк (торговое имя «Отвод 90° LR…») перенесён на мастера.
- **Не сливались** (другое исполнение): оцинкованные, толстостенные (×5/×6/×8),
  короткие, резьбовые, 114×4 vs 108×4.

## [2026-08-11] — Номенклатура: слияние отводов Ду32

### Изменено
- Мастер: id **73** «Отвод стальной 42,3×2,6 (Ду32)».
- Vendor Башняк («Отвод 90° LR, Ду 32», 48 ₽) перенесён с id 721 на мастер.
- Дубль id **721** «Отвод стальной 90° LR, Ду32» заархивирован.
- На мастере два поставщика: Татаринов + Башняк.

## [2026-08-11] — fix(object_request): усиление поиска по прайсу поставщика

### Исправлено
- Variant-specific строка `product.supplierinfo` больше не показывает соседние
  варианты того же шаблона; template-wide строка по-прежнему разрешает все
  варианты.
- Поиск учитывает компанию требования и не использует артикул другого
  поставщика для товара, который продают несколько поставщиков.
- SQL-домен каталога применяется до `limit`; весь прайс не загружается в
  Python для autocomplete.
- При смене поставщика несовместимый товар и UoM очищаются, строка возвращается
  в состояние сопоставления, пользователь получает предупреждение.
- Автоподстановка поставщика учитывает вариант товара и компанию.
- Добавлены regression-тесты OBR-038; версия `19.0.1.10.6`.
- Prod deploy `5c84aa9`: backup
  `/opt/project_odoo/backups/or-vendor-search-hardening-20260810-222014/`,
  `-u object_request` → `19.0.1.10.6`, restart; health `pass`.

## [2026-08-10] — feat(object_request): поиск товара по прайсу поставщика в OR

### Изменено
- В строках OR поле «Поставщик» стоит перед «Товар».
- Если `preferred_vendor_id` задан: `product_id` ограничен номенклатурой
  этого поставщика (`seller_ids`); поиск также идёт по торговому имени и
  артикулу в `product.supplierinfo` (в подсказке: нормализованное —
  торговое имя).
- Если поставщик не указан — обычный поиск по нормализованным названиям.
- Версия: `19.0.1.10.5`.
- Prod deploy `9766686`: backup
  `/opt/project_odoo/backups/or-vendor-product-search-20260810-145507/`,
  `-u object_request` → `19.0.1.10.5`, restart; health `pass`.

## [2026-08-10] — fix(object_request): запрет создания товара из закупки

### Изменено
- В строках `purchase.order` для `product_id` отключены `create` /
  `create_and_edit`; в контекст добавлен
  `block_product_create_from_purchase`.
- `product.product` / `product.template`: `name_create` и `create` с этим
  флагом поднимают `UserError` — карточки только через нормализованный
  каталог. Версия: `19.0.1.10.4`.
- Prod deploy `ec4e948`: backup
  `/opt/project_odoo/backups/purchase-create-guard-20260810-131418/`,
  `-u object_request` → `19.0.1.10.4`, restart; health `pass`.

## [2026-08-10] — Нормализация гофры ПВХ Ду16/Ду20 в метрах

### Изменено
- Вместо карточек 643/692 (Units, бухты) созданы нормализованные:
  - **1228** `Труба гофрированная ПВХ Ду16, серая, бухта 100 м` —
    **500 м** на Офис/Полки; vendor Электро Центр `SQ0401-0001`, **23 ₽/м**.
  - **1229** `Труба гофрированная ПВХ Ду20, серая, с зондом, бухта 100 м` —
    **182 м** на Ос.ск/Полки; vendor Электро Центр `SQ0401-0002`, **23 ₽/м**.
- Старые 643/692 архивированы (UoM нельзя сменить из‑за журнала).
- Строка OR/2026/08/0033 → product 1229.

## [2026-08-10] — fix(object_request): сброс stock_match_warning после «Оставить закупку»

### Исправлено
- При явном подтверждении закупки несмотря на похожий остаток
  (`confirm_stock_guard_override` / «Оставить закупку») предупреждение
  `stock_match_warning` на строках требования сбрасывается; решение
  по-прежнему фиксируется в chatter. Версия модуля: `19.0.1.10.3`.
- Prod deploy `86145c4`: backup
  `/opt/project_odoo/backups/stock-match-clear-20260810-112717/`,
  `-u object_request` → `19.0.1.10.3`, restart; health `pass`.
  На OR/2026/08/0032 сняты 6 устаревших `stock_match_warning`.

## [2026-08-10] — TD-010: tooltips кнопок комплектации объектов

### Добавлено
- В `docs/technical-debt.md` задача **TD-010**: подписать всплывающими
  подсказками (`title`) кнопки во всех окнах модуля «Комплектация объектов»
  (по аналогии с подсказкой на «Получить» в закупке).

## [2026-08-10] — Складской учёт на всех материалах

### Изменено
- На VPS (`odoo19`): у **468** активных товарных карточек (`type=consu`)
  включён `is_storable=true`; без складского учёта активных товаров не осталось
  (итого складских активных: **1118**).
- В правилах создания номенклатуры зафиксировано: новые материалы всегда с
  `is_storable=true` (`odoo-product-catalog.mdc`, скилл `purchase-from-invoice`,
  `purchase-from-invoice.mdc`). Услуги не затрагиваются.

## [2026-08-10] — Правило агента: номенклатура Odoo

### Добавлено
- `.cursor/rules/odoo-product-catalog.mdc` — нормализация имён, один товар /
  много поставщиков, слияние дублей, vendor pricelist, категории, сверка счёта.
- В `purchase-from-invoice.mdc` шаг «Товары» ссылается на это правило.

## [2026-08-10] — Слияние дублей + vendor pricelist TDCS (УТБФ0006533)

### Изменено
- Слиты дубли: фильтр Ду65 (**500→701**, остаток 1+3=4), термометр 0–120 °C
  (**1132→674**), резьба Ду32 (**453→1022**); архивированы 500, 1132, 453.
- На 27 мастер-карточек по счёту УТБФ0006533 добавлен/обновлён vendor pricelist
  ООО «ТД Центр Снабжения» (артикулы и цены со счёта).

## [2026-08-10] — Карточки по счёту АМУРСНАБСБЫТ ЦБ-16030

### Добавлено
- 4 нормализованные карточки по счёту № ЦБ-16030 (OSB, плёнка 150 мкм,
  пена B1, саморез 4,2×70) с vendor pricelist у АО «АМУРСНАБСБЫТ»:
  id 1224–1227.

## [2026-08-10] — Нормализация вспененной трубной теплоизоляции (ВПЭ)

### Изменено
- Все активные карточки трубной теплоизоляции из вспененного полиэтилена
  приведены к единому имени: `Трубка теплоизоляционная ВПЭ {Ø}/13, L2000 мм`
  (категория «Теплоизоляция»), без бренда в названии.
- Бренды (Трубофлекс, Тилит Супер и др.) и цены хранятся в vendor pricelist
  у поставщиков: ИП Башняк, ОАО УПТК «Амурстрой», ООО ТД Центр Снабжения.
- Для размера **60/13** добавлен поставщик Башняк (цена 129,18 ₽ со счёта № 45).

### Исправлено
- Слиты дубли по типоразмерам; архивированы 8 карточек:
  1028, 1030, 1031, 1032, 1033, 1034, 1043, 1044.
- Мастерами оставлены карточки с историей закупок P00039 (704–714) и 1029 для 60/13.
- Итого активных типоразмеров: **12** (22…60, 64, 76, 89, 110 /13).

## [2026-08-08] — feat(object_request_calendar): встречи после оплаты bill

### Добавлено
- Новый модуль `object_request_calendar`: при переходе vendor bill в
  `payment_state = paid` создаёт отдельную встречу для каждого связанного
  требования на комплектацию.
- Первый свободный час ищется по календарю снабженца в рабочих слотах
  09:00–16:00 по часовому поясу компании, с пропуском обеда и выходных и
  30-дневным горизонтом поиска.
- Встреча связывается со счётом и требованием, показывает снабженца и прораба
  участниками и доступна через смарт-кнопку «Встречи» в требовании.
- Триггер учитывает вычисляемый характер `payment_state`: переход ставится в
  дедуплицированную precommit-очередь, а статус повторно проверяется перед
  созданием. Advisory lock и SQL UNIQUE защищают пару bill/requirement от
  параллельных дублей.
- Автотесты резолвера, поиска слотов и реальной оплаты через
  `account.payment.register`.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request_calendar`.
- `docker exec odoo19-local odoo -i object_request_calendar -d odoo19_local
  --test-enable --test-tags /object_request_calendar --stop-after-init
  --http-port=8092` — 22 post-tests, 0 failed, 0 errors.
- Prod deploy `d429771`: backup
  `/opt/project_odoo/backups/object-request-calendar-20260808-113823/`,
  `-i object_request_calendar`, restart; module `installed` 19.0.1.0.0;
  `https://skladtsk.duckdns.org/web/login` HTTP 200.

## [2026-08-08] — fix(ai_assistant): сопоставление позиций счёта по артикулу поставщика

### Исправлено
- `InvoiceContextHelper._match_item` сначала ищет товар по `article`
  через `product.supplierinfo.product_code` (с приоритетом найденного
  поставщика) и `default_code`, затем — по названию. Раньше артикул
  из счёта игнорировался, и позиции с другим каноническим именем
  помечались как `needs_create_product_draft`.
- `custom_product_search.ai_search_products` / поиск шаблона учитывают
  точное совпадение `seller_ids.product_code`, чтобы tool `search_products`
  находил товар по артикулу поставщика (например `00-00036296`).

### Добавлено
- Тесты: match по supplier article и default_code в
  `test_invoice_context_helper`; AI-поиск по vendor code в
  `test_product_search`.

## [2026-08-08] — fix(ai_assistant): улучшение парсинга таблиц из PDF счетов

### Исправлено
- В `extractor.py` (`_parse_table`) увеличен охват поиска заголовка с 5
  до 10 строк. Добавлена проверка на наличие минимального числа
  колонок (`_MIN_HEADER_COLS`), чтобы отсеивать ложные совпадения.
- При извлечении ячейки с артикулом из `pdfplumber` теперь берётся только
  первое слово до пробела или переноса строки (т.к. бренд и артикул
  в счетах могут склеиваться в одну ячейку, например `141551\nFLEXTRON`).
- Удалены переносы строк (`\n`) из названий товаров и единиц 
  измерения.

---

## [2026-08-06] — docs: инструкция пополнения Ос.ск / Расх

### Добавлено
- `docs/instruction-base-warehouse-replenish.md` — пополнение базовых складов
  **Ос.ск** и **Расходники** через обычную закупку (не через `object.request`):
  поле «Доставить в», приход IN, Validate; оплата в 1С.
- Скриншоты: `docs/screenshots/base-warehouse-replenish/` (примеры `P00040`,
  `P00048`, `Ос.ск/IN/00015`).

---

## [2026-08-06] — docs: мини-инструкция по закупке с разными поставщиками

### Добавлено
- `docs/instruction-purchase-split-vendors.md` — две рабочие ситуации снабженца:
  закупка у двух поставщиков сразу и закупка только части строк с отложением
  остальных до появления на складе (пример `OR/2026/08/0032`).
- Скриншоты UI: `docs/screenshots/purchase-split-vendors/`.

---

## [2026-08-06] — docs: TD-008 — недавние поставщики в колонке «Поставщик»

### Добавлено
- `docs/technical-debt.md` — **TD-008**: при ручном выборе и при фокусе на пустом поле «Поставщик» (`preferred_vendor_id`) в таблице строк требования на комплектацию показывать последние выбранные поставщики в выпадающем списке.

---

## [2026-07-27] — change(object_request): объединение вкладок «Строки» и «Обработка»

### Изменено
- Вкладка требования **«Обработка»** удалена: действия «Рассчитать наличие»,
  «Авто-разбивка» и «Подготовить закупку» перенесены на вкладку **«Строки»**
  в одну панель с «Отсортировать строки» и «Проверить номенклатуру».
- «Статистика строк» и статус сопоставления перенесены в шапку формы рядом с
  блоками «Основные данные» и «Ответственные».
- UI-блок «Сводка по количествам» больше не показывается на форме требования;
  поля модели сохранены для совместимости.

### Проверено
- Prod upgrade `object_request` до `19.0.1.10.2` (ветка
  `feature/import-matching-v2`, HEAD `8e1dfd0`); backup:
  `/opt/project_odoo/backups/ui-merge-tabs-20260727-080108/`.
- `https://skladtsk.duckdns.org/web/login` — HTTP 200 после restart.

---

## [2026-07-27] — fix(object_request): подпись складов в проверке наличия

### Исправлено
- В мастере «Проверка актуальности требования» поле «Проверено по складам»
  больше не перечисляет все активные склады компании: показываются только
  склады выдачи текущего требования (`issue_warehouse_ids` /
  `_get_issue_warehouses()`).
- Раскладка остатков по строке в этом мастере также ограничена складами
  выдачи требования.

---

## [2026-07-20] — fix(object_request): обеспечение строк выдачей и закупкой

### Исправлено
- `qty_issued` теперь пересчитывается как общее фактически обеспеченное
  количество по завершённым складским выдачам и входящим движениям связанной
  строки закупки.
- Статус `fully_supplied` ставится только когда обеспечено всё
  `qty_requested`; частичная выдача всего складского плана больше не закрывает
  строку, если остаётся закупочная или ручная потребность.
- После подтверждения выдачи или поступления пересчитываются оставшиеся планы
  `К выдаче (план)` и `К закупке (план)` без повторного включения уже
  обеспеченного количества.

### Добавлено
- Диагностические readonly-поля строки требования: `qty_issued_from_stock`
  («Со склада») и `qty_received_purchase` («Поступило по закупке»).
- Служебное действие «Пересчитать обеспечение» для идемпотентного пересчёта
  выбранных строк по завершённым движениям.
- Техническое поле `qty_planned_to_issue` в распределении по складам для
  сохранения исходного плана выдачи при частичных подтверждениях.

### Проверено
- `docker exec odoo19-local python3 -m flake8 ...` по затронутым файлам.
- `docker exec odoo19-local odoo --test-enable --test-tags /object_request -u object_request -d odoo19_local --stop-after-init --http-port=8071`
  — 438 post-tests, 0 failed, 0 errors.
- Prod upgrade `object_request` до `19.0.1.10.0`; backup:
  `/opt/project_odoo/backups/sup-001-007-20260720-070944/`.
- Для `OR/2026/07/0029` пересчитаны строки P00073: болт M6 и гайка M6
  получили `qty_to_buy=0` и `fully_supplied`.

---

## [2026-07-20] — fix(object_request): ручной выбор товара снимает блокировку закупки

### Исправлено
- Строка с `manual_review` больше не блокирует закупку, если прораб или
  снабженец уже вручную выбрал товар для этого требования
  (`matching_source=manual`, товар указан). Действие **«Запомнить»** для этого
  не требуется — оно нужно только для глобальной памяти сопоставлений.
- При ручном выборе товара в строке статус сопоставления сразу переводится
  в `matched`.

---

## [2026-07-20] — fix(object_request): имя PDF расходной накладной при выдаче

### Изменено
- PDF по кнопке «Расходная накладная» в выдаче сохраняется как
  `Расходная накладная №<номер> <склад> <объект назначения>`.

---

## [2026-07-20] — fix(object_request): имя PDF при печати требования

### Изменено
- PDF по кнопке «Распечатать требование» сохраняется с префиксом
  `Требование на комплектацию №` вместо `Передаточная ведомость №`.

---

## [2026-07-18] — chore(ai_assistant): переход с OpenRouter на ProxyAPI

### Изменено
- LLM-провайдер для `ai_assistant` сменён с OpenRouter на **ProxyAPI**
  (`proxyapi.ru`) — российский OpenAI-совместимый прокси-сервис с оплатой
  в рублях по счёту для юрлица, без VPN.
- Причина: OpenRouter блокировал весь API (`/api/v1/key`, `/api/v1/models`,
  все модели) с egress IP прод-VPS `195.209.210.27` — `403 Access denied by
  security policy`. Подтверждено, что это гео-ограничение по IP/аккаунту, а
  не баг конфигурации Referer/tools (см. `docs/deep-research-report.md`).
  Та же блокировка воспроизведена у n8n на том же VPS с другими ключами
  OpenRouter.
- Изменение чисто конфигурационное, без изменений кода `openrouter_client.py`:
  - `ai_assistant.openrouter_base_url` → `https://openai.api.proxyapi.ru/v1`
  - `ai_assistant.openrouter_api_key` → ключ ProxyAPI
  - `ai_assistant.text_model` → `gemini/gemini-2.5-flash` (было `google/gemini-2.5-flash`)
  - `ai_assistant.vision_model` → `openai/gpt-4o` (не изменилось — совпадает с форматом ProxyAPI)
- Проверено на проде: прямые запросы к ProxyAPI (текст, vision, tool-calling)
  — 200 OK; живой чат в Odoo — 200 OK, без ошибок `security policy`.

---

## [2026-07-10] — fix(ai_assistant): fallback при OpenRouter 403 security policy

### Исправлено
- При ошибке OpenRouter `403 Access denied by security policy` ассистент
  повторяет запрос в облегчённом режиме (без tools, consult-промпт).
- `HTTP-Referer` берётся из `web.base.url` вместо захардкоженного localhost
  (на проде `localhost` мог провоцировать security policy).
- В лог пишется тело ответа OpenRouter при 403; текст ошибки в чате
  указывает на keys/privacy OpenRouter.
- `context_resolver`: `groups_id` → `group_ids`/`all_group_ids` (Odoo 19).

---

## [2026-07-08] — test(object_request): регрессия на layout-scope в action context

### Добавлено
- Регрессионные проверки, что `action_open_lines`, `action_open_problem_lines`
  и `action_check_purchase_stock_matches` возвращают правильный
  `object_request_column_layout_scope` в `context` (новый тест
  `test_action_open_lines_sets_column_layout_scope` в
  `tests/test_obr035_regressions.py`; дополнительные assert в существующих
  тестах `tests/test_obr021_purchase.py`).
- Полный прогон модуля: 818 post-tests, 0 failed, 0 errors.

---

## [2026-07-08] — fix(object_request): сохранение позиции скрытых колонок при drag

### Исправлено
- В `object_request_line_column_layout.js` перестановка колонок drag-and-drop
  больше не перезаписывает весь сохранённый порядок только видимыми
  колонками: добавлен `buildObjectRequestFullColumnOrder()`, восстанавливающий
  полный порядок (видимые + скрытые optional-колонки) перед вычислением
  перестановки. Ранее скрытая на момент drag колонка при повторном включении
  уезжала в конец таблицы вместо ожидаемой позиции.
- Найдено при ревью реализации из `docs/tasktracker-column-fix.md`.

---

## [2026-07-08] — feat(object_request): пользовательская раскладка колонок строк требования

### Добавлено
- Для таблиц строк требования добавлено browser-local сохранение раскладки
  колонок: ширины, порядка и набора optional-колонок.
- Настройки разделены по сценариям: встроенная вкладка **«Строки»**,
  smart-button **«Строки»**, smart-button **«Проблем»** и список после
  **«Диагностика PO»**.
- Frontend-расширение ограничено `object.request.line` и явными layout-scope
  в context, чтобы не затрагивать остальные list-view Odoo.
- В заголовках поддерживаемых таблиц добавлен drag-and-drop field-колонок;
  selector/action/open-form/button columns не участвуют в перестановке.

### Проверено
- `python3 -m py_compile custom_addons/object_request/models/object_request.py custom_addons/object_request/__manifest__.py`
  — 0 ошибок.
- `python3 -m xml.etree.ElementTree custom_addons/object_request/views/object_request_views.xml`
  — 0 ошибок.
- `node --check custom_addons/object_request/static/src/js/object_request_line_column_layout.js`
  — 0 ошибок.
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --http-port=8089 --test-enable -u object_request -d odoo19_local --stop-after-init`
  — 817 post-tests, 0 failed, 0 errors.

---

## [2026-07-07] — feat(object_request): складской контекст для AI/combined-подбора

### Контроль качества строк
- Excel preview теперь помечает строку `manual_review`, если найдено
  несколько сильных кандидатов, выбранный товар без остатка при наличии
  похожего складского кандидата или есть конфликт DN/PN/семейства.
- При импорте `manual_review` сохраняет выбранный товар, но оставляет
  `matching_required=True` и `matching_state='manual_review'` до ручного
  решения снабженца.
- `line_problem_count` учитывает `manual_review`, а wizard закупки блокирует
  создание PO при нерешённых критических предупреждениях по номенклатуре.
- На требовании добавлено действие **«Переподобрать с учётом остатков»**:
  shortlist строится со складами выдачи, AI-подсказки обновляются, а товар
  записывается только для безопасного складского совпадения с confidence
  `≥0.90`.

### Изменено
- `object.request.matching.candidate.service` теперь добавляет в payload
  кандидатов структурные признаки строки и товара: семейство, DN/Ду, PN,
  материал, ГОСТ, тип соединения, а также складские остатки и policy-решение
  замены.
- `object.request.llm.matching.service` передаёт в LLM JSON-контекст с
  `requested_features`, `candidate_features`,
  `stock_qty_on_issue_warehouses`, `stock_warehouse_names`,
  `substitution_decision` и `substitution_requires_confirmation`.
- Confidence пост-валидируется по складскому сценарию: уверенный кандидат с
  остатком и без конфликтов поднимается до `0.90`, а выбор товара без остатка
  при наличии равноценного складского кандидата ограничивается до `≤0.85` и
  получает risk flag `stock_alternative_available`.
- `ai_match_reason` в строке требования дополняется складским объяснением и
  структурными признаками кандидата; замены с ручным подтверждением остаются
  ниже порога массового автоприменения.

### Проверено
- `python3 -m py_compile` по изменённым Python-файлам — 0 ошибок.
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --http-port=8079 --test-enable --test-tags /object_request:TestObr029LlmMatching -u object_request -d odoo19_local --stop-after-init`
  — 14 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --http-port=8079 --test-enable --test-tags /object_request:TestOBR021Purchase -u object_request -d odoo19_local --stop-after-init`
  — 32 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --http-port=8079 --test-enable --test-tags /object_request:TestImportWizardOBR007,/object_request:TestObr009MassActions,/object_request:TestOBR021Purchase,/object_request:TestObr029LlmMatching -u object_request -d odoo19_local --stop-after-init`
  — 86 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --http-port=8079 --test-enable --test-tags /object_request -u object_request -d odoo19_local --stop-after-init`
  — 434 post-tests, 0 failed, 0 errors.

---

## [2026-07-06] — feat(object_request): нормализация признаков номенклатуры

### Добавлено
- `object.request.product.feature.parser` — общий parser технических признаков
  товара: семейство, DN/Ду, PN/Ру/МПа, материал, ГОСТ и тип соединения.
- Stored-поля на `product.template` и related stored-поля на
  `product.product`: `or_product_family`, `or_diameter_nominal`,
  `or_pressure_nominal`, `or_material`, `or_standard`,
  `or_connection_type`, `or_feature_key`, `or_feature_parse_warning`.
- Отчёт **Аудит номенклатуры** для ручной чистки справочника: потенциальные
  дубли, позиции без DN/Ду и конфликтующие PN.
- Shell-команда `custom_addons/object_request/scripts/product_feature_audit.py`
  для вывода audit-summary в `odoo shell`.

### Изменено
- `object.request.substitution.policy` теперь использует общий parser
  признаков.
- `object.request.matching.candidate.service` добавляет источник кандидатов
  `feature` и ищет по `family + DN + PN>=requested`, чтобы подбор использовал
  структуру товара, а не только текстовые токены.
- Конфликт семейства или DN отсекается до ранжирования; PN downgrade остаётся
  видимым как `blocked`-кандидат без складского бонуса.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request:TestObr037ProductFeatures,/object_request:TestObr028CombinedMatching -d odoo19_local --stop-after-init --http-port=8090`
  — 30 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request -d odoo19_local --stop-after-init --http-port=8091`
  — 428 post-tests, 0 failed, 0 errors.

---

## [2026-07-06] — feat(object_request): каталог допустимых аналогов

### Добавлено
- Модель `object.request.product.substitute.rule` для управляемых правил
  аналогов с направлением `one_way` / `two_way`, причиной, подтверждением,
  компанией и счётчиками использования.
- Меню **Комплектация объектов → Правила аналогов** и smart-button
  **Аналоги** на карточке варианта товара.
- В строках требования отдельные поля для разрешённого аналога:
  `substitute_product_id`, `substitute_stock_qty`,
  `substitute_stock_warehouse_names`, `substitute_warning_text`.
- Действие строки **«Использовать аналог»**: явно заменяет `product_id` на
  разрешённый аналог, пересчитывает наличие и пишет решение в chatter.

### Защита
- Правило аналога нельзя создать, если `object.request.substitution.policy`
  считает замену запрещённой; для `two_way` проверяются оба направления.
- Прораб и кладовщик могут читать каталог аналогов, но создание/изменение
  доступно только снабженцу или системному администратору.
- Закупочный wizard отдельно предупреждает о разрешённом аналоге с остатком и
  не создаёт PO без явного решения пользователя; обход логируется в chatter.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request:TestObr036SubstituteRules,/object_request:TestACLForeman,/object_request:TestACLSupplyManager -d odoo19_local --stop-after-init --http-port=8088`
  — 24 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request -d odoo19_local --stop-after-init --http-port=8089`
  — 423 post-tests, 0 failed, 0 errors.

---

## [2026-07-06] — feat(object_request): правила замен и стартовая память фланцев

### Добавлено
- `object.request.substitution.policy` — единый кодовый контракт допустимых,
  запрещённых и требующих проверки замен.
- Кандидаты сопоставления обогащаются полями `substitution_decision`,
  `substitution_reason`, `substitution_requires_confirmation`; запрещённые
  замены не получают складской бонус и не блокируют закупку как допустимый
  складской аналог.
- `object.request.matching.memory.backfill_flange_pn16_memory()` создаёт
  стартовые записи памяти для однозначных замен фланцев `PN10` / `1,0МПа`
  на `PN16` того же диаметра.
- Миграция `19.0.1.7.5` запускает backfill при обновлении модуля.
- `matching_note` теперь получает объяснение по складскому кандидату:
  «Есть остаток на Ос.ск: ...».
- В строках требования добавлена кнопка **«Выбрать кандидата»**, которая
  записывает найденный складской товар в `product_id` и фиксирует решение в
  `matching_note`.
- `@api.onchange('product_id')` сразу обновляет предупреждение о похожем
  товаре с остатком при ручном выборе товара.
- В wizard закупки добавлены действия **«Заменить на этот товар»**,
  **«Оставить закупку»** и **«Отмена»** после срабатывания складского
  guard-а.

### Защита
- Для фланцев реализовано правило: `PN10` можно рекомендовать как `PN16`, но
  обратная замена `PN16` → `PN10` блокируется.
- Автосопоставление не применяет кандидатов, требующих ручного подтверждения
  по policy.
- AI-кандидаты, требующие подтверждения замены, не попадают под массовое
  автоприменение: confidence ограничивается ниже `0.90`.
- Действие **«Заменить на этот товар»** переводит строку из закупки в выдачу
  только после явного выбора пользователя и пересчёта наличия.
- Подтверждение допустимых замен ограничено ролью снабженца или системного
  администратора.
- Backfill не создаёт запись, если по диаметру найдено несколько допустимых
  `PN16`-кандидатов или `object.request.substitution.policy` видит конфликт.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request:TestObr028CombinedMatching,/object_request:TestACLForeman,/object_request:TestACLSupplyManager -d odoo19_local --stop-after-init --http-port=8083`
  — 41 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo -u object_request --test-enable --test-tags /object_request -d odoo19_local --stop-after-init --http-port=8078`
  — 415 post-tests, 0 failed, 0 errors.

---

## [2026-07-02] — fix(object_request): стабилизация release suite

### Исправлено
- Генерация кода склада объекта стала устойчивой к уже существующим
  `stock.warehouse.code`: при конфликте подбирается детерминированный
  свободный suffix.
- Проверка выдачи валидирует превышение `qty_to_issue` над доступным остатком
  до открытия wizard-а, включая ручное распределение по строкам.
- Тестовые сценарии выдачи и расчёта наличия приведены к контракту складов
  выдачи: остатки и планы создаются на разрешённых складах требования.

### Проверено
- `docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/object_request`
  — 0 ошибок.
- `docker exec odoo19-local odoo --test-enable -u object_request --test-tags /object_request -d odoo19_local --stop-after-init --http-port=8080`
  — 395 post-tests, 0 failed, 0 errors.
- `docker exec odoo19-local odoo --test-enable --test-tags /object_request:TestOBR021Purchase,/object_request:TestObr032Memory,/object_request:TestObr028CombinedMatching,/object_request:TestObr009MassActions -d odoo19_local --stop-after-init --http-port=8078`
  — 80 post-tests, 0 failed, 0 errors.

---

## [2026-07-02] — fix(object_request): память сопоставлений и диагностика PO

### Исправлено
- Кнопки **«Запомнить»** и **«Принять и запомнить»** доступны без
  `supplier_article`: строка сохраняется в `object.request.matching.memory`,
  а создание `product.supplierinfo` пропускается.
- Диагностика закупок теперь помечает строку предупреждением, если товар в
  строке PO отличается от текущего товара строки требования.

### Проверено
- `python3 -m py_compile` по изменённым Python-файлам.
- `python3 -m flake8` по изменённым тестам `test_obr021_purchase.py`,
  `test_obr032_memory.py`.
- `git diff --check` по изменённым файлам.
- `docker exec odoo19-local odoo -u object_request --test-enable --test-tags /object_request:TestOBR021Purchase,/object_request:TestObr032Memory -d odoo19_local --stop-after-init --http-port=8075`
  — 35 post-tests, 0 failed, 0 errors.
- Полный `/object_request` запускался той же базой:
  `382 post-tests, 17 failed, 9 errors`; падения остались в существующих
  складских/проектных сценариях вне scope изменения (`OBR-012`, `OBR-018`,
  `OBR-019`, `OBR-033`, `OBR-034`, `OBR-035`, duplicate warehouse code).

---

## [2026-07-02] — feat(object_request): упрощение UI сценария требования

### Добавлено
- Отдельная вкладка **«Сопоставление»** с блоком
  **«Сопоставление номенклатуры»** для пересопоставления и AI-действий.
- В wizard закупки добавлен двухшаговый сценарий складского guard-а:
  сначала показывается список конфликтов, затем становится доступен флаг
  **«Закупить несмотря на похожий остаток»**.
- View-тесты фиксируют, что массовые/опасные действия не находятся в header
  и основной вкладке строк.

### Изменено
- Из header требования убраны действия пересопоставления и AI-применения.
- Из верхней панели вкладки **«Строки»** убраны кнопки **«Закупить всё»**,
  **«Выдать максимум»**, **«Сбросить разбивку»**; эти операции остаются
  массовыми действиями списка строк.
- Построчная кнопка **«Проверить склад»** переименована в
  **«Проверить складской кандидат»**.
- Smart-button **«Проверить PO»** переименован в **«Диагностика PO»**.

### Проверено
- `python3 -m py_compile` по изменённым Python-файлам.
- `python3 -m flake8` по изменённым Python-файлам.
- `git diff --check` по изменённым файлам.
- `docker exec odoo19-local odoo -u object_request --test-enable --test-tags /object_request:TestObr009MassActions,/object_request:TestOBR021Purchase -d odoo19_local --stop-after-init --http-port=8074`
  — 53 post-tests, 0 failed, 0 errors.

---

## [2026-06-30] — feat(object_request): MVP-2 UI и диагностика складских кандидатов

### Добавлено
- Поля строки требования для складского предупреждения:
  `stock_match_warning`, `stock_match_candidate_id`,
  `stock_match_candidate_qty`, `stock_match_warning_text`.
- Действие **«Проверить номенклатуру»** на требовании и
  **«Проверить склад»** на строке: пересчитывает похожие товары с остатком
  на складах выдачи.
- В списках строк видны `AI shortlist`, складской кандидат, остаток кандидата
  и текст предупреждения; строки с предупреждением подсвечиваются.
- Search-фильтр **«Есть похожий товар на складе»** и включение таких строк в
  smart-button **«Проблемы»**.
- Smart-button **«Проверить PO»** на требовании: диагностирует уже связанные
  строки закупки, открывает найденные проблемные строки и пишет note в chatter.

### Изменено
- Защита закупочного wizard-а теперь заполняет поля `stock_match_*`, чтобы
  результат блокировки был виден в UI и фильтрах.
- `line_problem_count` учитывает складские предупреждения, а не только
  отсутствие сопоставления или поставщика.

### Проверено
- `python3 -m py_compile` по изменённым Python-файлам.
- `git diff --check` по изменённым файлам.
- `docker exec odoo19-local odoo -u object_request --test-enable --test-tags /object_request:TestOBR021Purchase -d odoo19_local --stop-after-init --http-port=8073`
  — 24 post-tests, 0 failed, 0 errors.

### Ограничения MVP
- Live-onchange при ручном выборе `product_id` не реализован: предупреждения
  пересчитываются явным действием или при создании закупки.
- Диагностика существующих PO не удаляет и не заменяет строки PO автоматически;
  она показывает строки и пишет chatter-note для ручного исправления.

---

## [2026-06-30] — feat(object_request): MVP-1 защита от ошибочной закупки похожей номенклатуры

### Добавлено
- `object.request.matching.candidate.service` теперь принимает контекст
  требования/складов выдачи и добавляет в shortlist складские поля:
  `stock_qty_on_issue_warehouses`, `stock_warehouse_names`,
  `has_issue_stock`, `stock_rank_bonus`.
- Кандидаты с остатком на складах выдачи получают приоритет в shortlist,
  если текстовое совпадение достаточно сильное и нет конфликта диаметра.
- Ручное действие **«Запомнить»** для строки требования сохраняет выбранный
  товар в `object.request.matching.memory` по нормализованному имени строки.
- Wizard создания закупки блокирует создание PO, если выбранный товар без
  остатка, но найден похожий кандидат с остатком на складах выдачи.
- В wizard добавлен явный флаг `confirm_stock_guard_override` для осознанного
  продолжения закупки; решение пишется в chatter требования.

### Изменено
- `product.supplierinfo` при запоминании сопоставления остаётся
  дополнительным механизмом для строк с корректным артикулом и поставщиком,
  но память сопоставлений больше не зависит от наличия артикула.
- Для MVP-1 вместо отдельного blocking wizard используется blocking `UserError`
  с описанием строки, выбранного товара, складского кандидата, остатка и склада.

### Проверено
- `python3 -m py_compile` по изменённым Python-файлам.
- `python3 -m flake8` по изменённым Python-файлам.
- `docker exec odoo19-local odoo -u object_request --test-enable --test-tags /object_request:TestOBR021Purchase,/object_request:TestObr028CombinedMatching,/object_request:TestObr032Memory -d odoo19_local --stop-after-init --http-port=8073`
  — 48 post-tests, 0 failed, 0 errors.

### Примечание
- Полный `/object_request` на текущей базе остаётся красным по существующим
  складским сценариям вне scope MVP-1 (`OBR-011/012/018/019/024/035` и
  duplicate warehouse code в части проектных тестов).

---

## [2026-06-25] — feat(ai_assistant): state machine закупки по счёту

### Добавлено
- Кнопочный purchase flow после загрузки счёта: `Создать закупку?` → выбор
  склада → `Привязать счёт?` → `Провести приёмку?` → итоговый план →
  `Выполнить`.
- `purchase_flow` в invoice session с состоянием, выбранным складом,
  решениями пользователя, `po_id`, `attachment_id`, `picking_id` и защитой от
  повторного выполнения.
- Финальный action `invoice_po_execute_plan`: создаёт и подтверждает PO,
  idempotent прикрепляет PDF счёта и при необходимости проводит incoming
  picking через `button_validate`.
- Frontend transport `suggestions[].payload` и сохранение `purchase_flow` в
  session storage.

### Изменено
- Старый shortcut `invoice_prepare_po` больше не создаёт pending write card для
  PO; он переводит пользователя в безопасный сценарий сбора решений.
- PDF исходного счёта сохраняется в in-memory invoice store и создаётся как
  `ir.attachment` только после финальной кнопки `Выполнить`.

### Проверено
- `python3 -m flake8` по изменённым Python-файлам.
- `docker exec odoo19-local odoo --test-enable -u ai_assistant --test-tags /ai_assistant -d odoo19_local --stop-after-init --http-port=8071`
  — 383 post-tests, 0 failed, 0 errors.

---

## [2026-06-25] — feat(cursor): парсер договор-счетов ОАО УПТК «Амурстрой»

### Добавлено
- Скилл `.cursor/skills/amurstroy-invoice-parsing/` — OCR-парсер таблицы со скидкой 5%.
- Скрипт `scripts/amurstroy_parse.py` — извлечение позиций, `partner_ref`, валидация сумм.
- Правило `.cursor/rules/amurstroy-invoice-parsing.mdc`.
- Тесты `tests/test_amurstroy_parse.py`.

### Изменено
- `ocr_parse.py` — при ИНН Амурстроя делегирует разбор таблицы в `amurstroy_parse`.
- Правила `invoice-parsing`, `purchase-from-invoice` — ссылки на скилл Амурстроя.
- После senior-review добавлен fail-closed режим: `needs_review`, `items_empty`, `sum_mismatch` блокируют автоматическое создание PO до подтверждения пользователя.
- Общий OCR теперь возвращает полный контракт `amurstroy_contract_invoice`, включая `partner_ref`, `subtotal_wo_vat`, `validation_target` и `needs_review`.

---

## [2026-06-25] — feat(purchase): закупки по 13 счетам из docs/invoices на склад Ломоносова 164

### Добавлено
- 13 закупок `P00055`–`P00067` по счетам из `docs/invoices/` на склад **Ломоносова 164 склад** (picking_type_id 73).
- Контрагенты: ИП Васильев И.В. (ИНН 280125303381), ИП Малов И.Н. (ИНН 282600003388).

### Примечание
- Сканы ОАО УПТК «Амурстрой» (Клей, Родбант, ручка) — позиции восстановлены из OCR вручную при расхождении с парсером.

---

## [2026-06-25] — feat(cursor): правило и скилл закупки из счёта поставщика

### Добавлено
- Правило `.cursor/rules/purchase-from-invoice.mdc` — чеклист создания `purchase.order` из счёта.
- Скилл `.cursor/skills/purchase-from-invoice/` — полный workflow: дубликаты, склад, товары, скидки, валидация.

### Изменено
- Правило `invoice-parsing.mdc` — ссылка на закупку из счёта.

---

## [2026-06-25] — chore(stock): склад «Расходники» с полками 1–3

### Добавлено
- Склад **Расходники** (код `Расх`, id 23) с операциями поступления и отгрузки.
- Внутренние локации: **Полка 1**, **Полка 2**, **Полка 3** под `Расх/Наличие`.

---

## [2026-06-25] — feat(cursor): скилл и правило OCR-парсинга сканированных счетов

### Добавлено
- Скилл `.cursor/skills/scanned-invoice-parsing/` — распознавание PDF-счетов без
  текстового слоя (Tesseract OCR, постобработка, валидация сумм).
- Скрипт `scripts/ocr_parse.py` — CLI для OCR-парсинга счетов.
- Словарь OCR-исправлений `ocr-corrections.md` (DIN 934, Амурстрой, М6 и др.).
- Правило `.cursor/rules/invoice-parsing.mdc` для файлов `docs/invoices/**`.

### Изменено
- Скилл `odoo-supplier-from-invoice` — ссылка на OCR-пайплайн для сканов.

---

## [2026-06-20] — fix(object_request): читаемые имена строк на вкладке «Размещение по складам»

### Исправлено
- У `object.request.line` добавлен `_compute_display_name`: вместо
  `object.request.line,152` показывается `#<№> [<артикул>] <наименование>`.
- На вкладке «Размещение по складам» колонка связи со строкой подписана как
  **Строка**.

---

## [2026-06-18] — fix(object_request): компактная передаточная ведомость закупки

### Исправлено
- Кнопка **Печать** в форме «Требование / запрос на закупку» теперь формирует
  PDF с названием `Передаточная ведомость №<счёт поставщика> <склад>`.
- Для отчётов заказа и запроса котировки закупки подключён компактный QWeb-шаблон
  на базе `purchase` без шапки компании, логотипа, страны и Tax ID.
- Печатная форма выровнена к верхнему краю страницы через отдельный paperformat
  с `margin_top = 0`.

### Изменено
- Блоки адреса доставки, поставщика и номера заказа подняты вверх и приведены к
  компактному шрифту 9px.
- Таблица материалов получила видимые границы ячеек для читаемости строк и
  количества.
- Высота строк таблицы увеличена на 15% относительно предыдущей компактной версии
  (`line-height: 1.265`).
- Внизу печатной формы добавлены строки подписей `сдал:` и `принял:`.

### Проверено
- Локальный прогон `object_request`: 376 тестов, 0 ошибок.
- Прод обновлён через `-u object_request` и рестарт Odoo.
- На проде для `P00035` подтверждены: `margin_top = 0`, компактный шаблон,
  увеличенная высота строк и имя файла
  `Передаточная ведомость №680 Основной склад (20 футовый контейнер)`.

---

## [2026-06-18] — feat(object_request): подсказки кнопок RFQ и заказа на закупку

### Добавлено
- Всплывающие подсказки (`help` / `title`) для кнопок формы запроса котировки и
  заказа на закупку: отправка, подтверждение, согласование, печать, приход,
  счета, smart-кнопки, каталог.
- Переименование **Acknowledge** → «Поставщик принял заказ» с пояснением, что это
  не складской приход.
- Зависимость `purchase_stock` для подсказок кнопки «Получить».

### Изменено
- Русские подписи оставшихся кнопок шапки: Подтвердить заказ, Согласовать,
  Печать, Отменить, Заблокировать и др.
- Версия модуля: `19.0.1.7.4`.

---

## [2026-06-18] — fix(object_request): xpath локализации кнопок закупок

### Исправлено
- Наследование формы `purchase.order`: Odoo 19 запрещает `@string` в xpath-селекторе;
  кнопки Send RFQ / Send PO переопределяются по атрибуту `invisible`.

### Изменено
- Версия модуля: `19.0.1.7.3`.

---

## [2026-06-18] — feat(object_request): русские подписи кнопок закупок

### Добавлено
- Локализация кнопок формы заказа на закупку в модуле `object_request`:
  - **Send RFQ** → «Отправить запрос»
  - **Send PO** → «Отправить заказ»
  - **Acknowledge** → «Подтвердить получение»
  - **Upload Bill** → «Загрузить счёт» (OWL-наследование шаблона `purchase.DocumentFileUploader`).
- Раздел **«Переопределения UI при обновлении Odoo»** в `docs/project.md` и чеклист в `docs/deploy.md`.

### Изменено
- Версия модуля: `19.0.1.7.2`.

---

## [2026-06-18] — fix(ai_assistant): схема create_partner_draft для Gemini/OpenRouter

### Исправлено
- JSON Schema поля `category` в tools `create_partner_draft` и `update_partner_draft`:
  union `type: ["string", "array"]` с `items` отклонялся Google Gemini через OpenRouter
  (HTTP 400 «Provider returned error») при создании поставщика из чата.
- В `odoo19_whm_stage` модель AI обновлена с `google/gemini-2.0-flash-001` на
  `google/gemini-2.5-flash`.

---

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
