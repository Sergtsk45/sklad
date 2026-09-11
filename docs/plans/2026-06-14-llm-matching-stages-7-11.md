# Plan: Odoo 19 LLM-Assisted Product Matching — этапы 7–11

**Created:** 2026-06-14
**Orchestration:** orch-v2-stages-7-11
**Status:** 🟢 Ready
**Goal:** Реализовать этапы 7–11 pipeline LLM-сопоставления товаров в модуле `object_request`
**Total Tasks:** 32
**Priority:** High

---

## Граф зависимостей

```
PREV-001 (этапы 1-6, уже завершены)
    │
    ├──► PRV-001..PRV-006  (Этап 7: Preview + AI)      ──┐
    │                                                      │
    ├──► SEC-001..SEC-007  (Этап 8: Аудит/безопасность) ──┤
    │                                                      │
    └──► MEM-001..MEM-007  (Этап 9: Память)             ──┤
                                                           │
                                              REG-001..REG-003  (Этап 10: Регрессия)
                                                           │
                                              DOC-001..DOC-005  (Этап 11: Документация)
```

**Параллельное выполнение:** PRV-* и SEC-* и MEM-* можно запускать одновременно.
**Этап 10** стартует только после завершения PRV-*, SEC-*, MEM-*.
**Этап 11** стартует только после завершения REG-*.

---

## Этап 7: Preview импорта с AI-кандидатами

### PRV-001 — Добавить AI-поля в `ObjectRequestImportPreview`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** нет
- **Файлы:** `custom_addons/object_request/wizards/import_excel_wizard.py`
- **Описание:**
  В модель `ObjectRequestImportPreview` (`object.request.import.preview`) добавить поля:
  - `ai_suggested_product_id = fields.Many2one('product.product', string='AI-предложение', readonly=True)`
  - `ai_match_confidence = fields.Float(string='Уверенность AI', readonly=True)`
  - `ai_match_reason = fields.Text(string='Причина AI', readonly=True)`
  - `matching_source = fields.Selection([('deterministic','Детерминированный'),('ai','AI'),('memory','Память'),('manual','Ручной')], string='Источник', readonly=True)`
- **Критерий приёмки:** поля присутствуют на модели, не вызывают ошибок при миграции

### PRV-002 — Добавить `ai_mode` и `ai_matched_count` в `ObjectRequestImportWizard`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** PRV-001
- **Файлы:** `custom_addons/object_request/wizards/import_excel_wizard.py`
- **Описание:**
  В модель `ObjectRequestImportWizard` добавить:
  - `ai_mode = fields.Selection([('none','Без AI'),('suggest','AI-подсказки'),('auto','AI-автоприменение')], default='none', string='Режим AI')`
  - `ai_matched_count = fields.Integer(string='Строк с AI-кандидатом', compute='_compute_ai_matched_count', store=False)`
  - Compute-метод `_compute_ai_matched_count`: считает preview_ids с ai_suggested_product_id != False
- **Критерий приёмки:** вычисляемое поле корректно отражает кол-во строк с AI-кандидатом

### PRV-003 — Обновить `_build_preview_vals` для AI-режима
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** PRV-002
- **Файлы:** `custom_addons/object_request/wizards/import_excel_wizard.py`
- **Описание:**
  В методе `_build_preview_vals` (или в `action_load_preview`) добавить логику:
  ```python
  if self.ai_mode in ('suggest', 'auto'):
      cand_svc = self.env['object.request.matching.candidate.service']
      # Для каждой preview-строки без matched_product_id вызвать build_candidates
      # Записать ai_suggested_product_id, ai_match_confidence, ai_match_reason, matching_source='ai'
  ```
  Вызов лениво — только для строк с `match_status` != 'matched' и `matching_required = True`.
  Batch: обрабатывать не более `ai_matching_batch_size` строк.
- **Критерий приёмки:** в режиме `suggest` preview-строки получают AI-поля; в режиме `none` поля пусты

### PRV-004 — Обновить `action_import` для переноса AI-полей в строки заявки
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** PRV-003
- **Файлы:** `custom_addons/object_request/wizards/import_excel_wizard.py`
- **Описание:**
  При создании строк `object.request.line` из preview переносить:
  - `ai_suggested_product_id` → поле строки (если `ai_mode = 'auto'` и confidence >= auto_threshold, применять автоматически через `action_accept_ai_candidate`)
  - `ai_match_confidence`, `ai_match_reason`, `matching_source`
  В режиме `auto`: строки с confidence >= threshold получают `matched_product_id = ai_suggested_product_id`.
- **Критерий приёмки:** после импорта в `auto`-режиме строки с высокой уверенностью имеют `matched_product_id`

### PRV-005 — Обновить validation messages визарда
- **Приоритет:** Medium
- **Сложность:** Simple
- **Зависимости:** PRV-004
- **Файлы:** `custom_addons/object_request/wizards/import_excel_wizard.py`, `import_excel_wizard_views.xml`
- **Описание:**
  В сообщении о результатах импорта показывать:
  - Сколько строк сопоставлено детерминированно
  - Сколько AI предложило кандидата
  - Сколько будет авто-применено (только в `auto`-режиме)
  - Сколько требуют ручного ввода
  Добавить compute-поля `deterministic_matched_count`, `manual_required_count` на wizard.
  Обновить XML-форму: добавить блок статистики AI рядом с кнопкой "Импортировать".
- **Критерий приёмки:** форма визарда отображает статистику AI

### PRV-006 — Тесты этапа 7
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** PRV-005
- **Файлы:** `custom_addons/object_request/tests/test_obr030_preview_ai.py`
- **Описание:**
  Создать новый файл тестов (класс `TestPreviewAI`, `@tagged('post_install', '-at_install')`):
  - `test_preview_ai_suggest_mode_populates_fields` — режим suggest заполняет AI-поля
  - `test_preview_ai_auto_mode_applies_confident_matches` — режим auto применяет уверенные
  - `test_preview_ai_none_mode_skips_llm` — режим none не вызывает LLM
  - `test_import_transfers_ai_fields_to_lines` — поля переносятся в строки заявки
  - `test_validation_message_shows_ai_stats` — статистика отображается
  Добавить импорт в `tests/__init__.py`.
- **Критерий приёмки:** все 5 тестов зелёные

---

## Этап 8: Аудит, безопасность и стоимость

### SEC-001 — `ir.config_parameter` и хелпер `_get_ai_config`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** нет
- **Файлы:** `custom_addons/object_request/models/llm_matching_service.py` (или новый `ai_config.py`)
- **Описание:**
  Реализовать функцию (или метод AbstractModel `_get_ai_config`):
  ```python
  def _get_ai_config(self):
      get = self.env['ir.config_parameter'].sudo().get_param
      return {
          'enabled': get('object_request.ai_matching_enabled', 'True') == 'True',
          'auto_threshold': float(get('object_request.ai_matching_auto_threshold', '0.90')),
          'suggest_threshold': float(get('object_request.ai_matching_suggest_threshold', '0.70')),
          'batch_size': int(get('object_request.ai_matching_batch_size', '50')),
      }
  ```
  Добавить дефолтные значения в `post-migrate.py` новой версии или через `data/` XML.
- **Критерий приёмки:** параметры читаются корректно, тест изолирован от реальных значений

### SEC-002 — Rate limit (`batch_size`) в `action_prepare_ai_candidates`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** SEC-001
- **Файлы:** `custom_addons/object_request/models/object_request.py`
- **Описание:**
  В методе `action_prepare_ai_candidates` применить `batch_size`:
  - Брать только первые N строк без AI-кандидата за один вызов
  - Добавить message_post с информацией о батче (напр. "Обрабатывается батч 1/3: строки 1–50")
  - Вернуть к пользователю уведомление, если обработаны не все строки
- **Критерий приёмки:** при >50 строк обрабатывается только batch_size, не все

### SEC-003 — Логирование AI-сопоставлений в chatter
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** SEC-001
- **Файлы:** `custom_addons/object_request/models/object_request.py`, `object_request_line.py`
- **Описание:**
  После `action_prepare_ai_candidates` делать `message_post` в чаттер заявки с:
  - Количество обработанных строк
  - Количество auto-match (confidence >= auto_threshold)
  - Количество suggest (confidence >= suggest_threshold, < auto_threshold)
  - Количество manual_review (не нашло кандидата или confidence < suggest_threshold)
  - Название модели LLM (если доступно из ответа `OpenRouterClient`)
  - Использованные токены (если доступно из ответа)
  Формат: HTML-таблица или структурированный текст.
- **Критерий приёмки:** после вызова action в чаттере появляется структурированная заметка

### SEC-004 — Обработка `ai_matching_enabled = False`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** SEC-001
- **Файлы:** `custom_addons/object_request/models/object_request.py`, `llm_matching_service.py`
- **Описание:**
  Когда `ai_matching_enabled = False`:
  - `action_prepare_ai_candidates` работает только с детерминированным shortlist (без вызова LLM)
  - Логирует заметку: "AI-сопоставление отключено, использован детерминированный поиск"
  - Кнопка "Подготовить AI-кандидатов" не скрывается, но работает иначе
  В `llm_matching_service._call_llm` добавить проверку флага вначале.
- **Критерий приёмки:** при disabled LLM не вызывается (мок-проверка)

### SEC-005 — Обработка ошибок LLM в чаттере
- **Приоритет:** Medium
- **Сложность:** Simple
- **Зависимости:** SEC-003
- **Файлы:** `custom_addons/object_request/models/object_request.py`, `llm_matching_service.py`
- **Описание:**
  При исключении в LLM-вызове (сеть, timeout, неверный ответ):
  - Поймать `Exception` в `_call_llm`
  - Записать `_logger.warning` с деталями
  - Добавить `message_post` в чаттер с текстом ошибки
  - Вернуть пустой список кандидатов (не пробрасывать исключение)
  - Строке поставить `ai_match_confidence = 0`, `ai_match_reason = 'Ошибка LLM: ...'`
- **Критерий приёмки:** при сетевой ошибке LLM процесс не прерывается, ошибка видна в чаттере

### SEC-006 — Новая версия manifest и migration
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** SEC-001
- **Файлы:** `custom_addons/object_request/__manifest__.py`, `migrations/19.0.1.3.0/post-migrate.py`
- **Описание:**
  Поднять версию до `19.0.1.3.0` в `__manifest__.py`.
  Создать `migrations/19.0.1.3.0/post-migrate.py`:
  - Установить дефолты `ir.config_parameter` если не существуют
  - Логировать миграцию
- **Критерий приёмки:** модуль обновляется без ошибок, параметры появляются в БД

### SEC-007 — Тесты этапа 8
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** SEC-002, SEC-003, SEC-004, SEC-005
- **Файлы:** `custom_addons/object_request/tests/test_obr031_ai_security.py`
- **Описание:**
  Создать файл тестов (класс `TestAISecurity`, `@tagged`):
  - `test_ai_disabled_skips_llm` — при флаге False LLM не вызывается (мок)
  - `test_batch_size_limits_processing` — batch_size ограничивает количество строк
  - `test_llm_error_logged_to_chatter` — ошибка LLM пишется в чаттер
  - `test_chatter_note_after_ai_action` — после action_prepare_ai_candidates есть заметка
  - `test_config_params_defaults` — дефолтные значения параметров корректны
  Добавить импорт в `tests/__init__.py`.
- **Критерий приёмки:** все 5 тестов зелёные

---

## Этап 9: Память сопоставлений

### MEM-001 — Создать модель `object.request.matching.memory`
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** нет
- **Файлы:** `custom_addons/object_request/models/matching_memory.py` (новый файл)
- **Описание:**
  Создать класс `ObjectRequestMatchingMemory(models.Model)`:
  ```python
  _name = 'object.request.matching.memory'
  _description = 'Память сопоставлений'
  _order = 'create_date desc'

  name_normalized = fields.Char(required=True, index=True)
  designation_normalized = fields.Char(index=True)
  product_id = fields.Many2one('product.product', required=True, ondelete='cascade')
  confirmed_by = fields.Many2one('res.users', ondelete='set null')
  source_request_id = fields.Many2one('object.request', ondelete='set null')
  confidence = fields.Float(default=1.0)
  active = fields.Boolean(default=True)
  ```
  Добавить `_sql_constraints` на уникальность `(name_normalized, product_id)`.
  Добавить импорт в `models/__init__.py`.
- **Критерий приёмки:** модель создаётся, `env['object.request.matching.memory'].create(...)` работает

### MEM-002 — Добавить rights/security для новой модели
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** MEM-001
- **Файлы:** `custom_addons/object_request/security/ir.model.access.csv`
- **Описание:**
  Добавить записи доступа:
  - `access_object_request_matching_memory_user` — group_user: read
  - `access_object_request_matching_memory_manager` — group_manager: read,write,create,unlink
  Проверить, что группы определены в `security/` модуля.
- **Критерий приёмки:** модель доступна без ошибок прав доступа

### MEM-003 — Интегрировать память в `build_candidates`
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** MEM-001
- **Файлы:** `custom_addons/object_request/models/matching_candidate_service.py`
- **Описание:**
  В `build_candidates` добавить первый шаг: проверка памяти.
  ```python
  # 1. Проверить память
  memory = self.env['object.request.matching.memory'].search([
      ('name_normalized', '=', normalized_name),
      ('active', '=', True),
  ], limit=1)
  if memory:
      return [{
          'product_id': memory.product_id.id,
          'confidence': memory.confidence,
          'reason': 'Из памяти сопоставлений',
          'source': 'memory',
      }]
  # 2. Детерминированный поиск ...
  # 3. LLM ...
  ```
  При нескольких записях памяти для одного имени — брать наиболее свежую или с наивысшей confidence.
- **Критерий приёмки:** при наличии записи в памяти LLM не вызывается

### MEM-004 — Реализовать `action_accept_and_remember_ai_candidate`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** MEM-001, MEM-003
- **Файлы:** `custom_addons/object_request/models/object_request_line.py`
- **Описание:**
  В существующем методе `action_accept_and_remember_ai_candidate` добавить запись в память:
  ```python
  # Фильтр: не сохранять L=..., пустые, < 3 символов
  if name_normalized and len(name_normalized) >= 3 and not name_normalized.startswith('l='):
      self.env['object.request.matching.memory'].create({
          'name_normalized': name_normalized,
          'designation_normalized': designation_normalized,
          'product_id': self.ai_suggested_product_id.id,
          'confirmed_by': self.env.uid,
          'source_request_id': self.request_id.id,
          'confidence': self.ai_match_confidence or 1.0,
      })
  ```
  Использовать `_normalize_name` из `excel_parser.py` или аналог для нормализации.
- **Критерий приёмки:** после вызова action в БД появляется запись memory

### MEM-005 — Фильтрация при сохранении в память
- **Приоритет:** Medium
- **Сложность:** Simple
- **Зависимости:** MEM-004
- **Файлы:** `custom_addons/object_request/models/object_request_line.py`
- **Описание:**
  Создать вспомогательный метод `_should_save_to_memory(name_normalized)`:
  - Возвращает `False` если строка пустая, None, len < 3
  - Возвращает `False` если начинается с `l=` (артикул вида L=...)
  - Возвращает `False` если состоит только из цифр (чистый артикул)
  - Возвращает `True` в остальных случаях
  Использовать в `action_accept_and_remember_ai_candidate`.
- **Критерий приёмки:** L=123, "", "ab" не сохраняются; "шаровой кран dn50" сохраняется

### MEM-006 — Новая версия manifest и migration для MEM
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** MEM-001
- **Файлы:** `custom_addons/object_request/__manifest__.py`, `migrations/19.0.1.3.0/post-migrate.py`
- **Описание:**
  Версия `19.0.1.3.0` уже создаётся в SEC-006. Убедиться, что миграция охватывает:
  - Создание таблицы `object_request_matching_memory` (Odoo делает автоматически)
  - Заполнение `ir.config_parameter` дефолтами (SEC-001)
  **Примечание:** если SEC-006 уже создал файл миграции — дополнить его, не создавать новый.
- **Критерий приёмки:** `odoo -u object_request` не выдаёт ошибок

### MEM-007 — Тесты этапа 9
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** MEM-004, MEM-005
- **Файлы:** `custom_addons/object_request/tests/test_obr032_memory.py`
- **Описание:**
  Создать файл тестов (класс `TestMatchingMemory`, `@tagged`):
  - `test_accept_and_remember_creates_memory_record` — подтверждение создаёт запись
  - `test_memory_used_in_build_candidates` — повторный импорт применяет memory без LLM
  - `test_memory_not_saved_for_short_names` — "ab", "L=5" не сохраняются
  - `test_memory_duplicate_does_not_error` — повторное сохранение не вызывает исключения
  - `test_memory_inactive_not_used` — `active=False` запись игнорируется
  Добавить импорт в `tests/__init__.py`.
- **Критерий приёмки:** все 5 тестов зелёные

---

## Этап 10: Регрессия

### REG-001 — Полный прогон тестов `object_request`
- **Приоритет:** Critical
- **Сложность:** Simple
- **Зависимости:** PRV-006, SEC-007, MEM-007
- **Команда:**
  ```bash
  docker exec odoo19-local odoo --test-enable -u object_request -d odoo19_local --stop-after-init
  ```
- **Описание:**
  Запустить полный тест-сьют модуля. Фиксировать:
  - Количество тестов (было N, стало M)
  - Все ли проходят
  - Время выполнения
- **Критерий приёмки:** 0 ошибок, 0 fallen

### REG-002 — Прогон тестов `custom_product_search`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** REG-001
- **Команда:**
  ```bash
  docker exec odoo19-local odoo --test-enable -u custom_product_search -d odoo19_local --stop-after-init
  ```
- **Описание:**
  Убедиться, что изменения в `matching_candidate_service` не сломали `custom_product_search`.
- **Критерий приёмки:** 0 ошибок

### REG-003 — Lint (flake8) всех затронутых файлов
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** REG-001
- **Команда:**
  ```bash
  docker exec odoo19-local python -m flake8 /mnt/extra-addons/object_request
  ```
- **Описание:**
  Убедиться в отсутствии lint-ошибок во всех изменённых файлах.
- **Критерий приёмки:** flake8 возвращает 0

---

## Этап 11: Документация

### DOC-001 — Обновить `docs/project.md`: pipeline v2
- **Приоритет:** High
- **Сложность:** Moderate
- **Зависимости:** REG-001
- **Файлы:** `docs/project.md`
- **Описание:**
  Добавить/обновить раздел "LLM-Assisted Product Matching":
  - Mermaid-диаграмма pipeline v2:
    ```
    Input → Memory check → Deterministic search →
    (if no match) → LLM rerank shortlist →
    Result: auto/suggest/manual_review
    ```
  - Описание порогов confidence (auto_threshold, suggest_threshold)
  - Описание архитектуры сервисов (candidate_service → llm_service)
  - Ограничения безопасности (batch_size, enabled flag, error handling)
  - Описание модели `matching.memory`

### DOC-002 — Обновить `docs/tasktrecker-comparison-v2.md`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** REG-001
- **Файлы:** `docs/tasktrecker-comparison-v2.md`
- **Описание:**
  Отметить все пункты этапов 7–11 как выполненные (`[x]`).
  Обновить статус задачи на "Завершена".

### DOC-003 — Обновить `docs/changelog.md`
- **Приоритет:** High
- **Сложность:** Simple
- **Зависимости:** REG-001
- **Файлы:** `docs/changelog.md`
- **Описание:**
  Добавить запись для версии `19.0.1.3.0`:
  ```
  ## [2026-06-14] — LLM-Assisted Matching v2 (этапы 7–11)
  ### Добавлено
  - AI-поля и режим ai_mode в визарде импорта (Preview)
  - ir.config_parameter параметры управления AI (enabled, thresholds, batch_size)
  - Логирование AI-действий в chatter заявки
  - Rate limiting (batch_size) для LLM-вызовов
  - Модель object.request.matching.memory
  - Фильтрация нерелевантных записей при сохранении в память
  ### Изменено
  - matching_candidate_service.build_candidates: проверка памяти перед LLM
  - action_accept_and_remember_ai_candidate: сохранение в память
  - Версия модуля: 19.0.1.3.0
  ```

### DOC-004 — Добавить docstring к публичным методам
- **Приоритет:** Medium
- **Сложность:** Simple
- **Зависимости:** REG-001
- **Файлы:** все затронутые `.py` файлы
- **Описание:**
  Добавить docstring к новым публичным методам:
  - `_get_ai_config`
  - `_should_save_to_memory`
  - `build_candidates` (если отсутствует)
  - `action_accept_and_remember_ai_candidate` (обновить)
  Формат: Google-style или стандартный Odoo (`""" Краткое описание. :param ...: :returns: """`).

### DOC-005 — Итоговая проверка плана
- **Приоритет:** Low
- **Сложность:** Simple
- **Зависимости:** DOC-001, DOC-002, DOC-003, DOC-004
- **Описание:**
  Убедиться, что:
  - Все новые файлы содержат файловую шапку (header)
  - `models/__init__.py` импортирует все новые модули
  - `__manifest__.py` содержит новые файлы в `data`/`security` если нужно
  - Версия `19.0.1.3.0` везде консистентна

---

## Прогресс

### Этап 7: Preview импорта с кандидатами
- [ ] PRV-001: AI-поля в ObjectRequestImportPreview (⏳ Pending)
- [ ] PRV-002: ai_mode и ai_matched_count в wizard (⏳ Pending)
- [ ] PRV-003: _build_preview_vals для AI-режима (⏳ Pending)
- [ ] PRV-004: action_import переносит AI-поля (⏳ Pending)
- [ ] PRV-005: Validation messages с AI-статистикой (⏳ Pending)
- [ ] PRV-006: Тесты этапа 7 (⏳ Pending)

### Этап 8: Аудит, безопасность и стоимость
- [ ] SEC-001: ir.config_parameter и _get_ai_config (⏳ Pending)
- [ ] SEC-002: Rate limit batch_size в action (⏳ Pending)
- [ ] SEC-003: Логирование в chatter (⏳ Pending)
- [ ] SEC-004: ai_matching_enabled=False обработка (⏳ Pending)
- [ ] SEC-005: Обработка ошибок LLM (⏳ Pending)
- [ ] SEC-006: Версия manifest + migration (⏳ Pending)
- [ ] SEC-007: Тесты этапа 8 (⏳ Pending)

### Этап 9: Память сопоставлений
- [ ] MEM-001: Модель object.request.matching.memory (⏳ Pending)
- [ ] MEM-002: Security rights для модели (⏳ Pending)
- [ ] MEM-003: Интеграция памяти в build_candidates (⏳ Pending)
- [ ] MEM-004: action_accept_and_remember записывает в память (⏳ Pending)
- [ ] MEM-005: _should_save_to_memory фильтрация (⏳ Pending)
- [ ] MEM-006: Migration для новой таблицы (⏳ Pending)
- [ ] MEM-007: Тесты этапа 9 (⏳ Pending)

### Этап 10: Регрессия
- [ ] REG-001: Полный прогон тестов object_request (⏳ Pending)
- [ ] REG-002: Прогон тестов custom_product_search (⏳ Pending)
- [ ] REG-003: Lint flake8 (⏳ Pending)

### Этап 11: Документация
- [ ] DOC-001: docs/project.md pipeline v2 (⏳ Pending)
- [ ] DOC-002: tasktrecker-comparison-v2.md (⏳ Pending)
- [ ] DOC-003: changelog.md (⏳ Pending)
- [ ] DOC-004: Docstring к публичным методам (⏳ Pending)
- [ ] DOC-005: Итоговая проверка (⏳ Pending)

---

## Архитектурные решения

### Почему память проверяется ДО LLM
Снижает стоимость API и latency. Подтверждённые пользователем сопоставления надёжнее LLM.

### Почему `ai_matching_enabled` в `ir.config_parameter`
Позволяет отключить LLM без перезапуска Odoo. Администратор меняет через Settings → Technical → Parameters.

### Почему ленивый импорт OpenRouterClient
Избегает циклической зависимости. `ai_assistant` не в `depends` манифеста — только runtime import.

### Версионирование: 1.2.0 → 1.3.0
Этапы 7–9 создают новую модель (`matching.memory`) и новые `ir.config_parameter` — требуется миграция.
