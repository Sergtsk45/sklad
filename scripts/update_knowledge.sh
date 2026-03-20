#!/usr/bin/env bash
# update_knowledge.sh — пересборка knowledge base для ai_assistant
# Pipeline: akaidoo → /tmp/akaidoo_raw/ → extract_schema.py → generated/
#
# Использование: ./scripts/update_knowledge.sh [--no-cleanup]
#   --no-cleanup  не удалять /tmp/akaidoo_raw/ после завершения

set -euo pipefail

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AKAIDOO_CONF="$PROJECT_ROOT/akaidoo.conf"
EXTRACT_SCRIPT="$SCRIPT_DIR/extract_schema.py"
RAW_DIR="/tmp/akaidoo_raw"
OUT_DIR="$PROJECT_ROOT/custom_addons/ai_assistant/static/knowledge/generated"

# ---------------------------------------------------------------------------
# Цвета
# ---------------------------------------------------------------------------
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }
header()  { echo -e "\n${BOLD}$*${NC}"; }

NO_CLEANUP=false
for arg in "$@"; do
  [[ "$arg" == "--no-cleanup" ]] && NO_CLEANUP=true
done

# ---------------------------------------------------------------------------
# Шаг 1: Проверка зависимостей
# ---------------------------------------------------------------------------
header "=== Проверка зависимостей ==="

if ! command -v akaidoo &>/dev/null; then
  error "akaidoo not found, run: pip install akaidoo"
  exit 1
fi
ok "akaidoo $(akaidoo --version 2>&1 | head -1 | grep -oP '\d+\.\d+\.\d+')"

if [[ ! -f "$EXTRACT_SCRIPT" ]]; then
  error "extract_schema.py not found: $EXTRACT_SCRIPT"
  exit 1
fi
ok "extract_schema.py найден"

if [[ ! -f "$AKAIDOO_CONF" ]]; then
  error "akaidoo.conf не найден: $AKAIDOO_CONF"
  exit 1
fi
ok "akaidoo.conf найден"

# ---------------------------------------------------------------------------
# Шаг 2: Очистка директорий
# ---------------------------------------------------------------------------
header "=== Подготовка директорий ==="

rm -rf "$RAW_DIR"
mkdir -p "$RAW_DIR"
ok "Очищен $RAW_DIR"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/*.md
ok "Очищен $OUT_DIR"

# ---------------------------------------------------------------------------
# Конфигурация модулей
# ---------------------------------------------------------------------------
# Формат: "module_name|shrink_mode|exclude_list"
STANDARD_MODULES=(
  "stock|max|account,digest,portal,auth_signup,web,mail"
  "purchase|max|account,digest,portal,auth_signup,web,mail"
  "sale|max|account,digest,portal,auth_signup,web,mail"
  "crm|max|account,digest,portal,auth_signup,web,mail"
  "contacts|max|account,digest,portal,auth_signup,web,mail"
  "account|max|digest,portal,auth_signup,web,mail"
)

CUSTOM_MODULES=(
  "object_request|soft|account,digest,portal,auth_signup,web,mail"
)

# Счётчики
TOTAL=0
SUCCESS=0
FAILED_DUMP=()
FAILED_EXTRACT=()

# ---------------------------------------------------------------------------
# Функция: akaidoo dump для одного модуля
# ---------------------------------------------------------------------------
run_dump() {
  local module="$1"
  local shrink="$2"
  local exclude="$3"
  local raw_file="$RAW_DIR/${module}_raw.md"

  info "Дамп: $module (shrink=$shrink, exclude=$exclude)"

  local output
  if output=$(
    akaidoo "$module" \
      -c "$AKAIDOO_CONF" \
      --shrink="$shrink" \
      --exclude="$exclude" \
      -o "$raw_file" 2>&1
  ); then
    local size
    size=$(du -sh "$raw_file" 2>/dev/null | cut -f1)
    ok "  → $raw_file ($size)"
    return 0
  else
    # akaidoo пишет в stdout даже при warning'ах — проверим что файл создан
    if [[ -f "$raw_file" && -s "$raw_file" ]]; then
      local size
      size=$(du -sh "$raw_file" 2>/dev/null | cut -f1)
      ok "  → $raw_file ($size) [с предупреждениями]"
      return 0
    else
      warn "  Модуль '$module' не сгенерирован: $(echo "$output" | tail -2)"
      return 1
    fi
  fi
}

# ---------------------------------------------------------------------------
# Функция: extract_schema для одного модуля
# ---------------------------------------------------------------------------
run_extract() {
  local module="$1"
  local raw_file="$RAW_DIR/${module}_raw.md"
  local out_file="$OUT_DIR/${module}_context.md"

  info "Схема: $module"

  local output
  if output=$(python3 "$EXTRACT_SCRIPT" "$raw_file" -o "$out_file" 2>&1); then
    ok "  → $out_file | $output"
    return 0
  else
    warn "  extract_schema.py упал для '$module': $output"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Шаг 3+4: Генерация сырых дампов
# ---------------------------------------------------------------------------
header "=== Генерация сырых дампов (akaidoo) ==="

process_module() {
  local entry="$1"
  local module shrink exclude
  module=$(echo "$entry" | cut -d'|' -f1)
  shrink=$(echo "$entry" | cut -d'|' -f2)
  exclude=$(echo "$entry" | cut -d'|' -f3)

  TOTAL=$((TOTAL + 1))

  if run_dump "$module" "$shrink" "$exclude"; then
    if run_extract "$module"; then
      SUCCESS=$((SUCCESS + 1))
    else
      FAILED_EXTRACT+=("$module")
    fi
  else
    FAILED_DUMP+=("$module")
  fi
}

for entry in "${STANDARD_MODULES[@]}"; do
  process_module "$entry"
done

header "=== Кастомные модули ==="
for entry in "${CUSTOM_MODULES[@]}"; do
  process_module "$entry"
done

# ---------------------------------------------------------------------------
# Шаг 6: Таблица размеров
# ---------------------------------------------------------------------------
header "=== Результат: generated/ ==="

printf "%-40s %8s %10s %10s\n" "Файл" "Размер" "Строк" "Статус"
printf '%.0s-' {1..72}; echo

for f in "$OUT_DIR"/*.md; do
  [[ -f "$f" ]] || continue
  fname=$(basename "$f")
  size=$(du -sh "$f" | cut -f1)
  lines=$(wc -l < "$f")
  # Статус: предупреждаем если > 50KB
  size_bytes=$(wc -c < "$f")
  if (( size_bytes > 51200 )); then
    status="${YELLOW}> 50KB${NC}"
  else
    status="${GREEN}OK${NC}"
  fi
  printf "%-40s %8s %10s  " "$fname" "$size" "$lines"
  echo -e "$status"
done

echo ""
echo -e "${BOLD}Итого:${NC} $SUCCESS/$TOTAL модулей успешно"

if (( ${#FAILED_DUMP[@]} > 0 )); then
  warn "Не удалось сгенерировать дампы: ${FAILED_DUMP[*]}"
fi
if (( ${#FAILED_EXTRACT[@]} > 0 )); then
  warn "Не удалось извлечь схему: ${FAILED_EXTRACT[*]}"
fi

# ---------------------------------------------------------------------------
# Шаг 7: Очистка tmp
# ---------------------------------------------------------------------------
if [[ "$NO_CLEANUP" == "false" ]]; then
  header "=== Очистка /tmp/akaidoo_raw/ ==="
  rm -rf "$RAW_DIR"
  ok "Удалён $RAW_DIR"
else
  info "Флаг --no-cleanup: $RAW_DIR сохранён"
fi

echo ""
echo -e "${GREEN}${BOLD}Готово.${NC} Контексты: $OUT_DIR"
