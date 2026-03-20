#!/usr/bin/env python3
"""
extract_schema.py — extracts Odoo model/field schema from akaidoo markdown dumps.

Usage:
    python scripts/extract_schema.py <input.md> [-o output.md]

Output: markdown tables (model name, fields, types, relations).
"""

import re
import sys
import argparse
from pathlib import Path

FIELD_TYPES = [
    'Char', 'Text', 'Integer', 'Float', 'Boolean', 'Date', 'Datetime',
    'Selection', 'Many2one', 'One2many', 'Many2many', 'Html', 'Binary',
    'Monetary', 'Reference', 'Image', 'Json',
]

ODOO_MODEL_BASES = {
    'models.Model', 'models.TransientModel', 'models.AbstractModel',
    'Model', 'TransientModel', 'AbstractModel',
}

SKIP_PATH_FRAGMENTS = [
    '__manifest__', 'tests/', 'test_', '/static/', 'controllers/',
    'migrations/', 'tools.py', 'utils.py', 'diff_utils', 'logging.py',
    'const.py', 'wizard_views', 'ir_qweb',
]


# ---------------------------------------------------------------------------
# Step 1: split akaidoo dump into {filepath: code} sections
# ---------------------------------------------------------------------------

def split_dump(content: str) -> dict:
    sections = {}
    parts = re.split(r'^# FILEPATH: (.+)$', content, flags=re.MULTILINE)
    # parts[0] = header text; then pairs [filepath, code_block, ...]
    for i in range(1, len(parts), 2):
        filepath = parts[i].strip()
        code = parts[i + 1] if i + 1 < len(parts) else ''
        sections[filepath] = code
    return sections


# ---------------------------------------------------------------------------
# Step 2: parse a single Python code block for model/field definitions
# ---------------------------------------------------------------------------

def _find_matching_paren(text: str, start: int) -> int:
    """Return index of closing ')' that matches the '(' at `start`."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def _extract_relation(field_str: str, field_type: str) -> str:
    if field_type in ('Many2one', 'One2many', 'Many2many'):
        # positional first arg or comodel_name=
        m = re.search(
            r'fields\.' + field_type + r"\(\s*['\"]([^'\"]+)['\"]", field_str
        )
        if not m:
            m = re.search(r"comodel_name\s*=\s*['\"]([^'\"]+)['\"]", field_str)
        return m.group(1) if m else '?'

    if field_type == 'Selection':
        # collect all quoted keys in the first list [...] or tuple
        m = re.search(r'\[([^\]]+)\]', field_str)
        if not m:
            m = re.search(r'\(([^)]+)\)', field_str)
        if m:
            keys = re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))[::2]
            if keys:
                result = ','.join(keys[:7])
                return result + ',…' if len(keys) > 7 else result
    return '—'


def _extract_string(field_str: str) -> str:
    m = re.search(r'string\s*=\s*["\']([^"\']+)["\']', field_str)
    return m.group(1) if m else ''


def parse_py_block(code: str, filepath: str) -> list:
    """Return list of model dicts extracted from a Python code block."""
    # Strip shrunk markers so they don't confuse the parser
    code = re.sub(r'#\s*shrunk[^\n]*', '', code)

    field_type_re = '|'.join(FIELD_TYPES)
    class_re = re.compile(r'^class\s+(\w+)\s*\(([^)]+)\)\s*:', re.MULTILINE)
    field_re = re.compile(
        r'^    (\w+)\s*=\s*fields\.(' + field_type_re + r')\s*\(',
        re.MULTILINE,
    )

    class_matches = list(class_re.finditer(code))
    models_found = []

    for idx, cm in enumerate(class_matches):
        bases_str = cm.group(2)
        bases = {b.strip() for b in bases_str.split(',')}
        if not bases & ODOO_MODEL_BASES:
            continue

        # Body of this class = from match start to next class start (or EOF)
        body_start = cm.start()
        body_end = class_matches[idx + 1].start() if idx + 1 < len(class_matches) else len(code)
        body = code[body_start:body_end]

        # _name
        nm = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", body)
        model_name = nm.group(1) if nm else cm.group(1)

        # _inherit (string or list)
        inherit = []
        inh = re.search(r"_inherit\s*=\s*\[([^\]]+)\]", body)
        if inh:
            inherit = re.findall(r"['\"]([^'\"]+)['\"]", inh.group(1))
        else:
            inh = re.search(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]", body)
            if inh:
                inherit = [inh.group(1)]

        # _description
        desc_m = re.search(r"_description\s*=\s*['\"]([^'\"]+)['\"]", body)
        model_desc = desc_m.group(1) if desc_m else ''

        # Fields
        fields = []
        seen_field_names = set()
        for fm in field_re.finditer(body):
            fname = fm.group(1)
            ftype = fm.group(2)
            if fname.startswith('_') or fname in seen_field_names:
                continue
            seen_field_names.add(fname)

            # Grab full field call including multiline args
            paren_open = body.find('(', fm.start())
            paren_close = _find_matching_paren(body, paren_open)
            full_call = body[fm.start():paren_close + 1]

            relation = _extract_relation(full_call, ftype)
            fdesc = _extract_string(full_call)

            fields.append({
                'name': fname,
                'type': ftype,
                'relation': relation,
                'description': fdesc,
            })

        # Only record if it has a _name or fields (skip bare mixin stubs)
        if nm or fields:
            models_found.append({
                'model_name': model_name,
                'inherit': inherit,
                'description': model_desc,
                'fields': fields,
                'filepath': filepath,
            })

    return models_found


# ---------------------------------------------------------------------------
# Step 3: merge models with same _name (extensions across files)
# ---------------------------------------------------------------------------

def merge_models(raw_models: list) -> dict:
    merged = {}
    for m in raw_models:
        key = m['model_name']
        if key not in merged:
            merged[key] = {
                'model_name': key,
                'inherit': m['inherit'],
                'description': m['description'],
                'fields': list(m['fields']),
                'filepath': m['filepath'],
            }
        else:
            # Add fields not already present
            existing = {f['name'] for f in merged[key]['fields']}
            for f in m['fields']:
                if f['name'] not in existing:
                    merged[key]['fields'].append(f)
                    existing.add(f['name'])
            # Fill in missing description
            if not merged[key]['description'] and m['description']:
                merged[key]['description'] = m['description']
    return merged


# ---------------------------------------------------------------------------
# Step 4: render markdown
# ---------------------------------------------------------------------------

def render_markdown(merged: dict, source_path: str) -> str:
    lines = [
        f'# Odoo Schema: `{Path(source_path).stem}`',
        '',
        f'> Сгенерировано из `{source_path}` скриптом `extract_schema.py`.  ',
        f'> Модели: {len(merged)}, полей всего: '
        f'{sum(len(m["fields"]) for m in merged.values())}.',
        '',
    ]

    for model_name in sorted(merged):
        m = merged[model_name]
        inherit_str = ''
        if m['inherit']:
            inherit_str = f" ← {', '.join(m['inherit'])}"

        lines.append(f"## `{model_name}`{inherit_str}")
        if m['description']:
            lines.append(f"*{m['description']}*  ")
        lines.append(f"Файл: `{m['filepath']}`  ")
        lines.append('')

        if m['fields']:
            lines.append('| Поле | Тип | Связь / Выбор | Описание |')
            lines.append('|------|-----|---------------|----------|')
            for f in m['fields']:
                rel = (f['relation'] or '—').replace('|', '/')
                desc = (f['description'] or '').replace('|', '/')
                lines.append(f"| `{f['name']}` | {f['type']} | {rel} | {desc} |")
            lines.append('')
        else:
            lines.append('*Полей нет (абстрактная модель или наследование)*  ')
            lines.append('')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Extract Odoo model/field schema from akaidoo markdown dump'
    )
    parser.add_argument('input', help='Path to akaidoo .md dump file')
    parser.add_argument('-o', '--output', help='Output .md file (default: stdout)')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Error: {input_path} not found', file=sys.stderr)
        sys.exit(1)

    content = input_path.read_text(encoding='utf-8')
    sections = split_dump(content)

    all_models = []
    for filepath, code in sections.items():
        if not filepath.endswith('.py'):
            continue
        if any(frag in filepath for frag in SKIP_PATH_FRAGMENTS):
            continue
        models = parse_py_block(code, filepath)
        all_models.extend(models)

    merged = merge_models(all_models)
    output = render_markdown(merged, str(input_path))

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding='utf-8')
        model_count = len(merged)
        field_count = sum(len(m['fields']) for m in merged.values())
        size_kb = len(output) / 1024
        print(
            f'  {out_path.name}: {model_count} моделей, '
            f'{field_count} полей, {size_kb:.1f} KB',
            file=sys.stderr,
        )
    else:
        print(output)


if __name__ == '__main__':
    main()
