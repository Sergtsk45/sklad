#!/usr/bin/env python3
"""
AIA-015: rebuild_knowledge_index.py
Пересобирает index.json из текущего состояния docs/ и generated/ директорий.

Использование:
    python scripts/rebuild_knowledge_index.py [--docs-dir PATH] [--generated-dir PATH]
                                               [--output PATH] [--dry-run]
"""

import argparse
import json
import os
import re
import sys


# Маппинг имени файла → модуль (по префиксу)
FILENAME_MODULE_MAP = {
    'stock': 'stock',
    'sale': 'sale',
    'purchase': 'purchase',
    'crm': 'crm',
    'contacts': 'contacts',
    'settings': 'settings',
    'account': 'account',
    'object_request': 'object_request',
}

MODULE_LABELS = {
    'stock': 'Склад',
    'sale': 'Продажи',
    'purchase': 'Закупки',
    'crm': 'CRM',
    'contacts': 'Контакты',
    'settings': 'Настройки',
    'account': 'Бухгалтерия',
    'object_request': 'Запрос объекта',
}

FALLBACK_MODULE = 'settings'


def detect_module(filename):
    """Определить модуль по имени файла."""
    stem = os.path.splitext(filename)[0]
    for prefix, module in FILENAME_MODULE_MAP.items():
        if stem.startswith(prefix):
            return module
    return None


def extract_keywords_from_md(path):
    """Извлечь ключевые слова из заголовков MD-файла."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []

    # Строка ключевых слов
    kw_match = re.search(r'\*\*Ключевые слова\*\*:\s*([^\n]+)', content)
    if kw_match:
        return [kw.strip().lower() for kw in kw_match.group(1).split(',')]

    # Заголовки как ключевые слова
    headers = re.findall(r'^#{1,3}\s+(.+)', content, re.MULTILINE)
    words = set()
    for h in headers:
        words.update(re.findall(r'\w{4,}', h.lower()))
    return sorted(words)[:10]


def scan_docs_dir(docs_dir):
    """Сканировать docs/ и вернуть {module: [relative_paths]}."""
    result = {}
    if not os.path.isdir(docs_dir):
        return result

    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith('.md'):
            continue
        module = detect_module(filename)
        if module:
            result.setdefault(module, []).append(os.path.join('docs', filename))

    return result


def scan_generated_dir(generated_dir):
    """Сканировать generated/ и вернуть {module: relative_path}."""
    result = {}
    if not os.path.isdir(generated_dir):
        return result

    for filename in sorted(os.listdir(generated_dir)):
        if not filename.endswith('.md'):
            continue
        module = detect_module(filename)
        if module:
            result[module] = os.path.join('generated', filename)

    return result


def build_index(docs_dir, generated_dir):
    """Собрать index.json."""
    docs_map = scan_docs_dir(docs_dir)
    generated_map = scan_generated_dir(generated_dir)

    all_modules = sorted(set(list(docs_map.keys()) + list(generated_map.keys())))

    modules = []
    for module in all_modules:
        entry = {
            'module': module,
            'label': MODULE_LABELS.get(module, module),
            'docs': docs_map.get(module, []),
            'generated': generated_map.get(module),
        }
        modules.append(entry)

    return {
        'odoo_version': '19.0',
        'lang': 'ru_RU',
        'generated': _today(),
        'docs_dir': 'docs',
        'generated_dir': 'generated',
        'fallback_module': FALLBACK_MODULE,
        'modules': modules,
    }


def _today():
    from datetime import date
    return date.today().isoformat()


def print_summary(index, warnings):
    total_docs = sum(len(m['docs']) for m in index['modules'])
    total_gen = sum(1 for m in index['modules'] if m['generated'])
    print(f'  Модулей: {len(index["modules"])}')
    print(f'  Docs-файлов: {total_docs}')
    print(f'  Generated-файлов: {total_gen}')
    if warnings:
        print(f'  Предупреждения ({len(warnings)}):')
        for w in warnings:
            print(f'    ! {w}')


def main():
    parser = argparse.ArgumentParser(description='Пересборка index.json для knowledge base')
    parser.add_argument('--docs-dir', default=None, help='Путь к docs/ директории')
    parser.add_argument('--generated-dir', default=None, help='Путь к generated/ директории')
    parser.add_argument('--output', default=None, help='Путь для записи index.json')
    parser.add_argument('--dry-run', action='store_true', help='Показать что будет, без записи')
    args = parser.parse_args()

    # Определяем пути по умолчанию (относительно скрипта)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_dir = os.path.join(
        script_dir, '..', 'custom_addons', 'ai_assistant', 'static', 'knowledge'
    )
    knowledge_dir = os.path.normpath(knowledge_dir)

    docs_dir = args.docs_dir or os.path.join(knowledge_dir, 'docs')
    generated_dir = args.generated_dir or os.path.join(knowledge_dir, 'generated')
    output_path = args.output or os.path.join(knowledge_dir, 'index.json')

    warnings = []
    if not os.path.isdir(docs_dir):
        warnings.append(f'docs/ не найдена: {docs_dir}')
    if not os.path.isdir(generated_dir):
        warnings.append(f'generated/ не найдена: {generated_dir}')

    index = build_index(docs_dir, generated_dir)

    if args.dry_run:
        print('[dry-run] Сгенерированный index.json:')
        print(json.dumps(index, ensure_ascii=False, indent=2))
        print()
        print('[dry-run] Summary:')
        print_summary(index, warnings)
        return 0

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'Ошибка записи {output_path}: {e}', file=sys.stderr)
        return 1

    print(f'index.json записан: {output_path}')
    print_summary(index, warnings)
    return 0


if __name__ == '__main__':
    sys.exit(main())
