# Заметки для обновления Odoo (19 → 20)

Сейчас прод и локальная разработка — **Odoo 19**. Этот файл — реестр кастомных
переопределений ядра, которые при смене мажорной версии **нужно сразу
перепроверить и при необходимости починить**. Ядро в `odoo/` не правим: всё
живёт в `custom_addons/`.

Смежное:

- подписи кнопок/колонок (xpath, OWL) — таблица в [`docs/project.md`](project.md)
  («Переопределения UI при обновлении Odoo») и чеклист в [`docs/deploy.md`](deploy.md);
- технический долг — [`docs/technical-debt.md`](technical-debt.md).

После перехода на 20: пройти все открытые пункты `UPG-*`, прогнать теги тестов,
отправить тестовый RFQ, отметить `[x]` и дату.

---

## UPG-002 — Архивирование дубля `m` при политике труб TD-002

- **Статус**: актуально на Odoo 19 после решения TD-002, требует перепроверки при апгрейде на 20
- **Зачем**: в TD-002 выбрано архивировать стандартную единицу длины `m` (id 9), чтобы для труб оставалась единственная рабочая единица `метр` (id 32). При апгрейде важно убедиться, что архивированная `m` не подхватилась новыми данными ядра и не появилась в новых карточках, прайс-листах или `purchase.order.line`.
- **Что проверить в 20**:
  1. `uom.uom` id 9 остаётся архивным и не становится снова доступным по умолчанию.
  2. Новые товары труб создаются только с `метр` (32), а не с `m` (9).
  3. Любые XML/CSV/демо-данные ядра Odoo 20, которые могут ссылаться на `m`, не переактивируют её для труб.
  4. Отчёты и правила конвертации по трубам продолжают использовать `kg_per_meter` и рабочую единицу `метр`.
- **Связано с**: [`docs/technical-debt.md`](technical-debt.md) TD-002, [`docs/tasktracker-td002-pipe-uom.md`](tasktracker-td002-pipe-uom.md)

---

## UPG-001 — Письмо RFQ без кнопки портала и шапки P00xxx

- **Статус**: актуально на Odoo 19 (`object_request` `19.0.1.10.20`, 2026-08-27)
- **Зачем**: поставщику не нужна кнопка «Посмотреть предложение»
  (`/my/purchase/<id>` + персональный токен), номер заказа и срок в шапке письма.
  Нужны только тема «Заявка на счёт», таблица позиций и подпись
  «С уважением &lt;user_id.name&gt; ООО "Теплосервис-Комплект"».
  Контрольная копия — на партнёра компании (`675001@mail.ru`).

### Как сделано в 19

Модуль `object_request`, файл
`custom_addons/object_request/models/purchase_order_ext.py`:

| Метод | Поведение |
|-------|-----------|
| `_notify_get_recipients_groups` | Для `state` в `draft` / `sent` у всех групп `has_button_access=False`. Иначе layout снова рисует фиолетовую кнопку. |
| `_notify_by_email_prepare_rendering_context` | Для RFQ `subtitles = []` (иначе рядом с кнопкой остаются P00xxx и «Срок исполнения заказа»). |
| `_setup_rfq_copy_mail_template` | Пишет стандартный `purchase.email_template_edi_purchase` (noupdate): `partner_to` = вендор + `company_id.partner_id`, свой `body_html`. Вызов из `data/purchase_mail_template.xml` при `-u`. |
| `_message_get_default_recipients` | Копия на партнёра компании, если у него есть email. |

Подтверждённый заказ (`state=purchase`, кнопка «Отправить заказ») **не** трогаем:
стандартная кнопка «View Order» там может остаться.

Тесты: `custom_addons/object_request/tests/test_purchase_rfq_copy_recipient.py`,
тег `or_rfq_copy`.

### Upstream Odoo 19 (что сломается первым)

| Место | Что смотреть |
|-------|----------------|
| `purchase/models/purchase_order.py` | `_notify_get_recipients_groups` (группа `portal_customer`, title View Quotation / View Order, URL `get_confirm_url()`); `_notify_by_email_prepare_rendering_context` (subtitles: имя записи + срок); `action_rfq_send` → `default_email_layout_xmlid` = `mail.mail_notification_layout_with_responsible_signature`. |
| `portal/models/mail_thread.py` | Группа `portal_customer`: кнопка только у `partner_id` документа, URL с `access_token` / hash. |
| `mail/data/mail_templates_email_layouts.xml` | Шапка: `has_button_access` + `subtitles`. Без кнопки шапка с номером/сроком тоже скрывается (`show_header`). |
| `mail.template` xmlid `purchase.email_template_edi_purchase` | noupdate: при установке 20 шаблон ядра может не перезаписаться нашим XML, зато `-u object_request` снова вызовет `_setup_rfq_copy_mail_template`. |

### Что сделать на Odoo 20

1. Сверить сигнатуры трёх методов notify/template. Если переименовали группы
   (`portal_customer`), layout или `action_rfq_send` — поправить override.
2. Прогнать:  
   `docker exec odoo19-local odoo --test-enable --test-tags or_rfq_copy -u object_request -d <db> --stop-after-init --http-port=8093`
3. Живая проверка: «Отправить запрос» → у поставщика и на `675001@mail.ru`
   нет кнопки портала, нет P00xxx и срока в шапке; таблица и подпись на месте.
4. «Отправить заказ» после подтверждения — отдельно: кнопка портала PO
   допустима, пока бизнес не попросит убрать и её.
5. Если 20 вставляет CTA иначе (composer, Discuss, другой xmlid layout) —
   отключить там же: `has_button_access` / пустые `subtitles` / более простой
   `email_layout_xmlid` только для RFQ.

---

## Как добавлять следующие заметки

Формат: `UPG-NNN` — краткий заголовок, статус, файл в `custom_addons/`,
upstream-пути текущей версии, чеклист для следующей. Не дублировать весь
changelog: только то, что **привязано к API/шаблонам ядра** и отвалится
при смене версии.

**Обязательно:** при такой правке сразу писать `UPG-*` сюда же (правило
проекта: `.cursor/rules/odoo-upgrade-notes.mdc`, `docs/rulesworkproject.md`).
