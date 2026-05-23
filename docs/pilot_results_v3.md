# AI Assistant V3 Pilot Results

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
- Pipe kg/ton to meter conversion remains manual until TD-002 is closed.
- Receipt validation and stock quant creation remain manual until TD-003 is closed.
- `pending_action` and tool rate limits are in-memory and reset on Odoo worker restart.

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
