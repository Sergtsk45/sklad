#!/bin/bash
# AIA-015: update_knowledge_v2.sh
# Полное обновление knowledge base AI-ассистента Odoo 19.
#
# Использование:
#   ./scripts/update_knowledge_v2.sh [--dry-run] [--skip-docs] [--skip-akaidoo]
#
# Шаги:
#   1. Клонировать/обновить репозиторий документации Odoo 19
#   2. Конвертировать RST → Markdown с применением term_mapping
#   3. Пересобрать akaidoo-контекст для каждого модуля
#   4. Обновить index.json
#   5. Вывод summary

set -e

# ── Настройки ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$PROJECT_DIR/custom_addons/ai_assistant/static/knowledge"
DOCS_REPO="/tmp/odoo-docs-19"
AKAIDOO_CONF="$PROJECT_DIR/akaidoo.conf"
TERM_MAPPING="$KNOWLEDGE_DIR/term_mapping.json"
GENERATED_DIR="$KNOWLEDGE_DIR/generated"

# Флаги
DRY_RUN=false
SKIP_DOCS=false
SKIP_AKAIDOO=false

for arg in "$@"; do
    case $arg in
        --dry-run)    DRY_RUN=true ;;
        --skip-docs)  SKIP_DOCS=true ;;
        --skip-akaidoo) SKIP_AKAIDOO=true ;;
    esac
done

# ── Вспомогательные функции ────────────────────────────────────────────────────
log()  { echo "[$(date '+%H:%M:%S')] $*"; }
warn() { echo "[$(date '+%H:%M:%S')] WARNING: $*" >&2; }
step() { echo; echo "=== $* ==="; }

WARNINGS=()
FILES_CREATED=0
FILES_TOTAL_SIZE=0

add_warning() { WARNINGS+=("$1"); warn "$1"; }

count_file() {
    local f="$1"
    if [ -f "$f" ]; then
        FILES_CREATED=$((FILES_CREATED + 1))
        local sz
        sz=$(wc -c < "$f")
        FILES_TOTAL_SIZE=$((FILES_TOTAL_SIZE + sz))
    fi
}

# ── Шаг 1: Документация Odoo 19 ────────────────────────────────────────────────
step "Шаг 1: Репозиторий документации Odoo 19"

if [ "$SKIP_DOCS" = true ]; then
    log "Пропускаем (--skip-docs)"
else
    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] Проверка/клонирование $DOCS_REPO"
    elif [ -d "$DOCS_REPO/.git" ]; then
        log "Обновляем существующий репозиторий..."
        git -C "$DOCS_REPO" pull --quiet || add_warning "git pull failed в $DOCS_REPO"
        log "OK: $DOCS_REPO обновлён"
    else
        log "Клонируем odoo/documentation ветка 19.0..."
        git clone --branch 19.0 --depth 1 \
            https://github.com/odoo/documentation.git "$DOCS_REPO" \
            || add_warning "git clone failed — продолжаем без обновления RST"
        log "OK: клонировано в $DOCS_REPO"
    fi
fi

# ── Шаг 2: RST → Markdown ──────────────────────────────────────────────────────
step "Шаг 2: Конвертация RST → Markdown"

if [ "$SKIP_DOCS" = true ]; then
    log "Пропускаем (--skip-docs)"
elif [ -d "$DOCS_REPO/content/applications" ]; then
    log "Конвертируем RST документацию..."
    CONVERT_ARGS=(
        --source "$DOCS_REPO/content/applications"
        --output "$KNOWLEDGE_DIR/docs"
        --term-mapping "$TERM_MAPPING"
    )
    [ "$DRY_RUN" = true ] && CONVERT_ARGS+=(--dry-run)
    [ "$DRY_RUN" = true ] && CONVERT_ARGS+=(--verbose)

    if $DRY_RUN; then
        log "[dry-run] python $SCRIPT_DIR/convert_rst_to_knowledge.py ${CONVERT_ARGS[*]}"
    else
        python3 "$SCRIPT_DIR/convert_rst_to_knowledge.py" "${CONVERT_ARGS[@]}" \
            && log "OK: RST конвертация завершена" \
            || add_warning "Ошибка конвертации RST → MD"
    fi
else
    log "RST-репозиторий не найден ($DOCS_REPO) — запускаем в --demo режиме"
    DEMO_ARGS=(
        --output "$KNOWLEDGE_DIR/docs"
        --term-mapping "$TERM_MAPPING"
        --demo
    )
    [ "$DRY_RUN" = true ] && DEMO_ARGS+=(--dry-run)

    if $DRY_RUN; then
        log "[dry-run] python $SCRIPT_DIR/convert_rst_to_knowledge.py ${DEMO_ARGS[*]}"
    else
        python3 "$SCRIPT_DIR/convert_rst_to_knowledge.py" "${DEMO_ARGS[@]}" \
            && log "OK: Demo-файлы сгенерированы" \
            || add_warning "Ошибка генерации demo-файлов"
    fi
fi

# ── Шаг 3: Akaidoo-контекст ────────────────────────────────────────────────────
step "Шаг 3: Пересборка akaidoo-контекста"

AKAIDOO_MODULES=(stock purchase sale crm contacts account object_request)

if [ "$SKIP_AKAIDOO" = true ]; then
    log "Пропускаем (--skip-akaidoo)"
elif ! command -v akaidoo &>/dev/null; then
    add_warning "akaidoo не установлен — пропускаем генерацию технического контекста"
    log "Установите akaidoo: pip install akaidoo (или см. документацию)"
else
    mkdir -p "$GENERATED_DIR"
    for mod in "${AKAIDOO_MODULES[@]}"; do
        AKAIDOO_ARGS=(-c "$AKAIDOO_CONF" -B 30k -o "$GENERATED_DIR/${mod}_context.md")

        # Кастомные модули — мягкое сжатие
        if [[ "$mod" == "object_request" ]]; then
            AKAIDOO_ARGS+=(--shrink=soft)
        else
            AKAIDOO_ARGS+=(--shrink=hard)
        fi

        log "  Генерируем $mod..."
        if $DRY_RUN; then
            log "  [dry-run] akaidoo $mod ${AKAIDOO_ARGS[*]}"
        else
            akaidoo "$mod" "${AKAIDOO_ARGS[@]}" 2>/dev/null \
                && count_file "$GENERATED_DIR/${mod}_context.md" \
                || add_warning "akaidoo failed для модуля $mod"
        fi
    done
    log "OK: akaidoo-контексты обновлены"
fi

# ── Шаг 4: Обновление index.json ───────────────────────────────────────────────
step "Шаг 4: Обновление index.json"

INDEX_ARGS=(
    --docs-dir "$KNOWLEDGE_DIR/docs"
    --generated-dir "$GENERATED_DIR"
    --output "$KNOWLEDGE_DIR/index.json"
)
[ "$DRY_RUN" = true ] && INDEX_ARGS+=(--dry-run)

if $DRY_RUN; then
    log "[dry-run] python $SCRIPT_DIR/rebuild_knowledge_index.py ${INDEX_ARGS[*]}"
    python3 "$SCRIPT_DIR/rebuild_knowledge_index.py" "${INDEX_ARGS[@]}"
else
    python3 "$SCRIPT_DIR/rebuild_knowledge_index.py" "${INDEX_ARGS[@]}" \
        && log "OK: index.json обновлён" \
        || add_warning "Ошибка пересборки index.json"
fi

# Считаем docs-файлы
if [ "$DRY_RUN" = false ] && [ -d "$KNOWLEDGE_DIR/docs" ]; then
    for f in "$KNOWLEDGE_DIR/docs/"*.md; do
        count_file "$f"
    done
fi

# ── Шаг 5: Summary ─────────────────────────────────────────────────────────────
step "Готово!"

TOTAL_KB=$((FILES_TOTAL_SIZE / 1024))
log "Создано/обновлено файлов: $FILES_CREATED"
log "Общий размер: ${TOTAL_KB} KB"

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo
    echo "Предупреждения (${#WARNINGS[@]}):"
    for w in "${WARNINGS[@]}"; do
        echo "  ! $w"
    done
fi

if [ "$DRY_RUN" = false ]; then
    echo
    echo "Перезапустите Odoo для применения изменений:"
    echo "  docker compose -f docker-compose.local.yml restart odoo"
fi
