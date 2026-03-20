# Что такое akaidoo и зачем он тебе

**Akaidoo** — это CLI-инструмент, который сканирует исходники Odoo-модулей и генерирует оптимизированный контекст: список моделей, полей, связей между ними, методов — в формате, который помещается в контекстное окно LLM. Вместо того чтобы руками описывать в `stock.json`, что «в модуле Склад есть приёмка, отгрузка, перемещение», akaidoo автоматически извлекает реальную структуру из кода.

## Установка и базовая настройка

У тебя Odoo 19 в Docker, исходники лежат в `odoo/` (ветка 19.0). Akaidoo работает на хосте (в WSL2/Cursor), а не внутри контейнера.

### Шаг 1 — установить

```bash
pip install akaidoo
```

### Шаг 2 — конфиг Odoo

Нужен конфиг Odoo, чтобы akaidoo знал, где искать аддоны. Создай минимальный файл `akaidoo.conf` (или используй существующий `config/odoo.local.conf`):

```ini
[options]
addons_path = ./odoo/addons,./custom_addons
```

Главное — чтобы `addons_path` указывал на реальные директории с модулями на хосте (не внутри контейнера).

## Разведка — посмотреть дерево модуля

Начни с обзора без дампа. Это покажет дерево зависимостей и файлы:

```bash
# Посмотреть структуру модуля stock и его зависимости
akaidoo stock -c akaidoo.conf

# Посмотреть свой кастомный модуль
akaidoo object_request -c akaidoo.conf
```

Вывод покажет дерево вроде:

```
Module: stock
Path: odoo/addons/stock
├── models/stock_picking.py (45KB) [Models: stock.picking (full)]
├── models/stock_move.py (38KB) [Models: stock.move (full)]
├── models/stock_warehouse.py (12KB) [Models: stock.warehouse (full)]
│
└── Module: product
    Path: odoo/addons/product
    ├── models/product.py (32KB) [Models: product.product (soft)]
```

## Генерация knowledge-контекста для ai_assistant

Вот тут начинается практическая польза. Тебе нужно сгенерировать файлы, которые заменят (или дополнят) твои текущие curated JSON.

Для каждого модуля, который поддерживает ai_assistant, делаешь дамп:

```bash
# Склад — модели + поля + ключевые методы, ужатые до разумного размера
akaidoo stock -c akaidoo.conf --shrink=hard -o knowledge/stock_context.md

# Закупки
akaidoo purchase -c akaidoo.conf --shrink=hard -o knowledge/purchase_context.md

# Продажи
akaidoo sale -c akaidoo.conf --shrink=hard -o knowledge/sale_context.md

# CRM
akaidoo crm -c akaidoo.conf --shrink=hard -o knowledge/crm_context.md

# Контакты (base + contacts)
akaidoo contacts -c akaidoo.conf --shrink=hard -o knowledge/contacts_context.md

# Твой кастомный модуль — тут можно мягче, он маленький
akaidoo object_request -c akaidoo.conf --shrink=soft -o knowledge/object_request_context.md
```

### Уровни сжатия и когда что использовать

- **`--shrink=hard`** — оставляет только поля и структуру классов, убирает тела методов. Для knowledge base ассистента это оптимально: ассистенту не нужен код compute-методов, ему нужно знать какие поля есть и как модели связаны.
- **`--shrink=max`** — совсем скелет: только реляционные поля. Если модуль большой и контекст не влезает.
- **`--shrink=soft`** — оставляет сигнатуры методов. Для кастомных модулей, где ассистент должен знать бизнес-логику.

## Контроль размера — бюджет токенов

Для knowledge provider критично, чтобы сниппеты не раздувались. Akaidoo умеет ограничивать размер:

```bash
# Ограничить контекст stock до ~50k токенов
akaidoo stock -c akaidoo.conf -B 50k -o knowledge/stock_context.md

# Для маленького модуля достаточно 20k
akaidoo object_request -c akaidoo.conf -B 20k -o knowledge/object_request_context.md
```

Флаг `-B` (budget) автоматически повышает уровень сжатия, если контекст не влезает в бюджет.

## Фокус на конкретных моделях

Если для ассистента важны только определённые модели, а не весь модуль:

```bash
# Из модуля stock — только stock.picking и stock.move в полном виде,
# остальное — сжато
akaidoo stock -c akaidoo.conf -E stock.picking,stock.move --shrink=hard \
    -o knowledge/stock_picking_context.md

# Из purchase — только purchase.order
akaidoo purchase -c akaidoo.conf -E purchase.order --shrink=hard \
    -o knowledge/purchase_context.md
```

Флаг `-E` (expand) говорит: «покажи эти модели полностью, остальные сожми».

## Agent mode — для продвинутого сценария

Если в будущем твой ассистент будет уметь читать файлы (например, через серверный доступ), agent mode генерирует карту с путями к файлам вместо самого кода:

```bash
akaidoo stock -c akaidoo.conf --agent -o knowledge/stock_agent_map.md
```

Пример вывода:

```markdown
## SCHEMA MAP
(Summarized models - use for navigation)

## LOGIC & SOURCE CODE
| Model         | Type | Path                              | Range   |
| stock.picking | Core | odoo/addons/stock/models/stock_picking.py | 1-580   |
| stock.move    | Core | odoo/addons/stock/models/stock_move.py    | 1-420   |
```

Для текущей версии ai_assistant (без файлового доступа) это менее полезно, но пригодится когда добавишь RAG.

## Как интегрировать в knowledge_provider.py

Сейчас у тебя knowledge provider работает так: по ключевым словам ищет фрагменты в JSON-файлах. Вот как это можно расширить.

### Вариант 1 — простая замена (минимальные изменения)

Вместо ручных JSON с описаниями подставляешь сгенерированные akaidoo markdown-файлы. Меняешь `knowledge_provider.py`:

```python
# Вместо загрузки stock.json с ручным описанием
# загружаешь stock_context.md, сгенерированный akaidoo

import os

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'knowledge')

def get_module_context(module_name):
    """Загрузить контекст модуля, сгенерированный akaidoo."""
    filename = f"{module_name}_context.md"
    filepath = os.path.join(KNOWLEDGE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None
```

### Вариант 2 — гибридный (рекомендую)

Оставляешь curated JSON для «человеческих» описаний (пошаговые инструкции, подсказки по интерфейсу), а akaidoo-контекст добавляешь как техническую справку по моделям. В `prompt_builder` комбинируешь:

```python
def build_knowledge_block(self, module, query):
    # 1. Человеческие подсказки из curated JSON
    human_snippets = self.knowledge_provider.get_snippets(module, query)

    # 2. Техническая карта моделей из akaidoo
    model_context = self.get_akaidoo_context(module)

    knowledge = ""
    if human_snippets:
        knowledge += "## Подсказки по интерфейсу\n"
        knowledge += "\n".join(human_snippets)
    if model_context:
        knowledge += "\n\n## Структура данных модуля\n"
        knowledge += model_context  # тут akaidoo markdown

    return knowledge
```

## Автоматизация — скрипт обновления knowledge base

Создай скрипт `scripts/update_knowledge.sh` для пересборки знаний при обновлении Odoo:

```bash
#!/bin/bash
# scripts/update_knowledge.sh
# Пересобрать knowledge base для ai_assistant из исходников Odoo

CONF="akaidoo.conf"
OUT="custom_addons/ai_assistant/static/knowledge/generated"
BUDGET="30k"

mkdir -p "$OUT"

modules=("stock" "purchase" "sale" "crm" "contacts" "account")

for mod in "${modules[@]}"; do
    echo "Generating context for $mod..."
    akaidoo "$mod" -c "$CONF" --shrink=hard -B "$BUDGET" \
        -o "$OUT/${mod}_context.md" 2>/dev/null
done

# Кастомные модули — мягче сжимаем
echo "Generating context for object_request..."
akaidoo object_request -c "$CONF" --shrink=soft -B "$BUDGET" \
    -o "$OUT/object_request_context.md" 2>/dev/null

echo "Done. Knowledge base updated in $OUT/"
```

Запускай его раз после обновления Odoo или добавления новых кастомных модулей.

## MCP-сервер — для будущего

Akaidoo умеет работать как MCP-сервер. Это значит, что в перспективе твой ai_assistant мог бы обращаться к akaidoo динамически: пользователь спрашивает про `stock.picking`, ассистент через MCP запрашивает у akaidoo контекст именно этой модели в реальном времени. Но это следующий уровень — для текущей архитектуры достаточно статических файлов.

## Итого — план действий

1. `pip install akaidoo` на хосте (WSL2)
2. Создать `akaidoo.conf` с путями к аддонам
3. Прогнать `akaidoo stock -c akaidoo.conf` — убедиться, что видит модули
4. Сгенерировать контексты для stock, purchase, sale, crm, contacts, object_request
5. Положить `.md`-файлы в `static/knowledge/generated/`
6. Обновить `knowledge_provider.py` — добавить загрузку akaidoo-контекста
7. Обновить `prompt_builder.py` — включить технический контекст в промпт
8. Протестировать: спросить ассистента «какие поля есть у stock.picking» — он должен ответить точно, а не выдумывать
