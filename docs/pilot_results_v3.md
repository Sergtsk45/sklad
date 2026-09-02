# AI Assistant V3 Pilot Results

## 2026-06-12 — Partner draft from invoice

### Scope

Пилот закрывает сценарий: счёт распознан, поставщик по ИНН отсутствует в
`res.partner`, пользователь создаёт поставщика через ConfirmationCard, затем
создаёт недостающий товар и draft PO.

### Scenario

| Step | Result | Notes |
|------|--------|-------|
| Загрузка счёта с новым ИНН | Passed | После upload появляется chip «Создать поставщика…». |
| `create_partner_draft` | Passed | Создаёт `res.partner` с `supplier_rank=1`; КПП сохраняется в `comment`; `bank_ids` не создаются. |
| Продолжение workflow | Passed | `created_partner_id` сохраняется в invoice session; следующий chip ведёт к товару или PO. |
| `create_purchase_order_draft` | Passed | PO создаётся в `draft` с `partner_id` нового поставщика и `partner_ref` номером счёта. |
| Обход confirm | Passed | Текстовое «да» не исполняет write-tool; нужен pending confirmation key. |

### Verification

- E2E: `test_e2e_unknown_supplier_invoice_to_po.py`.
- Локальный прогон `/ai_assistant`: 352 post-tests, 0 failed, 0 errors.
- Prod smoke: passed after CPP-015 deploy; shell smoke created partner/product/PO in a transaction and rolled it back.

## 2026-05-24 — Pilot summary

### Scope

AI Assistant v3 adds a guarded action layer for supply workflows:

- read tools: products, partners, warehouses, picking types, stock quants, object requests;
- write tools: draft object request, draft purchase order, draft internal picking, chatter note;
- frontend confirmation cards and result cards;
- pending confirmation store with idempotency;
- per-user tool rate limits;
- denylist guard for forbidden operations;
- optional `ai_assistant.audit` model.

No tool confirms purchase orders or validates pickings. `button_confirm` and
`button_validate` remain manual UI steps until TD-003 is explicitly closed.

### Scenarios

| Scenario | Result | Notes |
|----------|--------|-------|
| УТ-1132 → draft PO на ОбМ-4 | Passed | E2E creates draft PO for `ОбМ-4`, `partner_ref=УТ-1132`, total qty `1098` m. |
| Draft object request from chat plan | Passed | Write tool creates `object.request` draft and posts chatter note. |
| Draft internal picking to object warehouse | Passed | Write tool creates internal picking draft only, no validation. |
| Read tool loop for supplier lookup | Passed | Controller executes read tool calls and continues LLM loop. |
| Wrong or expired confirmation key | Passed | `/ai_assistant/confirm` returns safe error. |

### Metrics

| Metric | Value |
|--------|-------|
| Draft-producing write tools | 3 |
| Chatter-only write tools | 1 |
| Read tools | 8 |
| Confirmation/result frontend card types | 2 |
| Rate limits | 30 read/min, 5 write/min per user |
| E2E pilot draft PO quantity | 1098 m |
| Confirm/Validate actions by AI | 0 |

### Known limitations

- Full module flake8 still fails on pre-existing style debt outside the v3 action changes.
- Coverage percentage is not available in the current Odoo test workflow.
- Pipe kg/ton to meter conversion is now handled by the workflow; remaining follow-up is catalog cleanup and coefficient population.
- Receipt validation and stock quant creation remain manual until TD-003 is closed.
- `pending_action` and tool rate limits are in-memory and reset on Odoo worker restart.

### Closed after pilot

- AIA-051: `find_warehouse` now accepts `query` and finds object warehouses by code or by address/name fragment, for example `Хмельницкого` -> `ОбМ-4`.

## 2026-05-24 — AIA-053 Navigation Links

### Scope

- Added `get_navigation_link` read-tool for consult/actions navigation questions.
- Added `NAVIGATION_CATALOG` with 22 common Odoo topics.
- Added `navigation_map.md` knowledge snippet without hardcoded URLs.
- Added system prompt rule: links must come only from `get_navigation_link`.

### Examples

| User asks | Tool topic | Expected response link |
|-----------|------------|------------------------|
| `как посмотреть заказы поставщикам?` | `заказы поставщикам` | `[Открыть «Заказы поставщикам»](/odoo/purchase-orders?search_default_my_purchases=1)` |
| `где найти требования прорабов?` | `требования прорабов` | link to the resolved `object_request.action_object_request` action |
| `как открыть инвентаризацию?` | `инвентаризация` | link to the resolved stock inventory action |

### Verification

- `/ai_assistant` tests: 250 post-tests, 0 failed, 0 errors.
- `ai_assistant` stats: 288 tests, 6334 queries.
- Targeted flake8 on changed Python files: passed.

## 2026-05-24 — AIA-047 verification

### Tests

Command:

```bash
docker exec odoo19-local odoo --test-enable --test-tags /ai_assistant -d odoo19_local --stop-after-init --http-port=8071
```

Result:

- Passed: 237 post-tests
- Failed: 0
- Errors: 0
- Odoo summary: `ai_assistant: 275 tests 2.94s 5777 queries`
- Assets: JS/CSS bundles pregenerated successfully

### Lint

Command:

```bash
docker exec odoo19-local python3 -m flake8 /mnt/extra-addons/ai_assistant
```

Result:

- Failed on existing style debt outside the AIA-041..046 touched Python files.
- Main categories: `E501` long lines, `F401` unused imports, `E401` multiple imports on one line, `F841` unused locals, `E221` spacing.
- Touched Python files for AIA-045/AIA-049 pass targeted flake8:
  - `controllers/chat_controller.py`
  - `services/action_tools/executor.py`
  - `services/pending_action.py`
  - `services/action_tools/write_tools.py`
  - `models/ai_assistant_audit.py`
  - `tests/test_chat_controller.py`
  - `tests/test_tool_executor_security.py`
  - `tests/test_e2e_supply_cycle.py`

Coverage tooling:

- No coverage command was available in the current Odoo test workflow.
- Coverage percentage was not generated in this pass.
