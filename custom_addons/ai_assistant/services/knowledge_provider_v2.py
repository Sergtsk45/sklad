import json
import logging
import os
import re

_logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'static', 'knowledge'
)

DOCS_DIR = os.path.join(_KNOWLEDGE_DIR, 'docs')
GENERATED_DIR = os.path.join(_KNOWLEDGE_DIR, 'generated')

MAX_DOCS_CHARS = 10000     # ~2500 tokens
MAX_TECH_CONTEXT_CHARS = 6000  # ~1500 tokens

TECH_TRIGGERS = [
    'модель', 'model', 'поле', 'поля', 'field', 'fields',
    'api', 'python', 'код', 'code', 'метод', 'method',
    'compute', 'onchange', 'override', 'inherit',
    'many2one', 'one2many', 'many2many',
    'orm', 'recordset', 'domain', 'search',
    'xml', 'view', 'qweb', 'xpath',
    'разработка', 'разработчик', 'developer',
    'technical', 'техническ',
]

MODULE_CONTEXT_FILES = {
    'stock': 'stock_context.md',
    'purchase': 'purchase_context.md',
    'sale': 'sale_context.md',
    'crm': 'crm_context.md',
    'contacts': 'contacts_context.md',
    'account': 'account_context.md',
    'object_request': 'object_request_context.md',
}

# Маппинг модулей к MD-файлам документации
MODULE_DOCS_FILES = {
    'stock': [
        'stock_warehouses.md',
        'stock_products.md',
        'stock_operations.md',
        'stock_inventory.md',
    ],
    'sale': [
        'sale_quotations.md',
        'sale_invoicing.md',
    ],
    'purchase': [
        'purchase_orders.md',
        'purchase_receipts.md',
    ],
    'crm': [
        'crm_leads.md',
        'crm_pipeline.md',
    ],
    'contacts': [
        'contacts_management.md',
    ],
    'settings': [
        'settings_general.md',
    ],
}


class KnowledgeProviderV2:
    """
    Трёхслойный провайдер знаний для AI-ассистента Odoo 19:
    1. RST-based docs (пользовательские инструкции из docs/*.md)
    2. Akaidoo context (структура моделей из generated/*.md)
    3. Term mapping (актуальные EN→RU термины из term_mapping.json)

    Обратно совместим с v1 через метод get_snippets().
    """

    def __init__(self):
        self._docs_index = None      # {section_text: [sections]}
        self._term_mapping = None
        self._tech_cache = {}

    # ------------------------------------------------------------------
    # Публичный интерфейс
    # ------------------------------------------------------------------

    def get_knowledge(self, module, query, include_technical=None):
        """
        Вернуть знания из всех трёх слоёв.

        :param include_technical: если None — определяется автоматически
            через _is_technical_query(). Передать True/False для явного управления.
        :returns dict: {
            'docs_snippets': str,   # релевантные фрагменты из docs/
            'tech_context': str|None,
            'term_mapping': dict,
        }
        """
        docs_snippets = self._search_docs(module, query)
        if include_technical is None:
            include_technical = self._is_technical_query(query)
        tech_context = (
            self.get_technical_context(module) if include_technical else None
        )
        term_mapping = self._get_relevant_terms(module)

        return {
            'docs_snippets': docs_snippets,
            'tech_context': tech_context,
            'term_mapping': term_mapping,
        }

    def get_snippets(self, module, query, limit=5):
        """Обёртка совместимости с v1 — делегирует в _search_docs."""
        raw = self._search_docs(module, query, limit=limit)
        if not raw:
            return []
        # Возвращаем список dict-ов, как в v1
        return [{'content': section} for section in raw.split('\n\n---\n\n') if section.strip()]

    def get_technical_context(self, module):
        """Загрузить akaidoo-контекст из generated/."""
        if module in self._tech_cache:
            return self._tech_cache[module]

        filename = MODULE_CONTEXT_FILES.get(module, f'{module}_context.md')
        path = os.path.join(GENERATED_DIR, filename)

        if not os.path.isfile(path):
            _logger.warning(
                'Technical context not found for module %r: %s', module, path
            )
            self._tech_cache[module] = None
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            _logger.warning(
                'Failed to read technical context for module %r', module
            )
            self._tech_cache[module] = None
            return None

        if len(content) > MAX_TECH_CONTEXT_CHARS:
            content = content[:MAX_TECH_CONTEXT_CHARS] + '\n...(обрезано)'

        self._tech_cache[module] = content
        return content

    def _is_technical_query(self, query):
        """Определить, нужен ли tech_context для этого вопроса."""
        lower = query.lower()
        return any(trigger in lower for trigger in TECH_TRIGGERS)

    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------

    def _expand_query(self, query):
        """
        Расширить запрос синонимами из term_mapping.
        'категории хранения' → 'категории хранения storage categories storage category'
        'storage category' → 'storage category категории хранения'
        """
        if not self._term_mapping:
            self._load_term_mapping()

        mapping = self._term_mapping or {}
        query_lower = query.lower()
        extra_terms = set()

        # Собрать все маппинги в один плоский словарь EN→RU
        all_pairs = {}
        for section in ['buttons', 'menu_items', 'fields', 'view_labels', 'statuses']:
            section_data = mapping.get(section, {})
            if isinstance(section_data, dict):
                for en, ru in section_data.items():
                    if ru and isinstance(ru, str):
                        all_pairs[en.lower()] = ru.lower()

        # Если запрос содержит русский термин → добавить английский и наоборот
        for en, ru in all_pairs.items():
            if ru in query_lower:
                extra_terms.add(en)
            if en in query_lower:
                extra_terms.add(ru)

        # Кастомные пары для составных терминов модуля Склад
        CUSTOM_PAIRS = {
            'storage categories': 'категории хранения',
            'storage category': 'категория хранения',
            'putaway rules': 'правила размещения',
            'putaway rule': 'правило размещения',
            'reordering rules': 'правила пополнения',
            'serial numbers': 'серийные номера',
            'lot': 'партия',
            'packages': 'упаковки',
            'locations': 'местонахождения',
            'warehouses': 'склады',
        }
        for en, ru in CUSTOM_PAIRS.items():
            if ru in query_lower:
                extra_terms.add(en)
            if en in query_lower:
                extra_terms.add(ru)

        if extra_terms:
            return query + ' ' + ' '.join(extra_terms)
        return query

    def _search_docs(self, module, query, limit=5):
        """
        Полнотекстовый поиск по MD-секциям из docs/.
        Boost: +2 за совпадение module name в имени файла.
        """
        index = self._build_docs_index()
        if not index:
            return ''

        expanded = self._expand_query(query)
        query_lower = expanded.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        scored = []
        for section in index:
            score = self._score_section(section, query_lower, query_words, module)
            scored.append((score, section))

        scored.sort(key=lambda x: x[0], reverse=True)
        positive = [(sc, s) for sc, s in scored if sc > 0]
        candidates = [s for _, s in positive[:limit]] if positive else [s for _, s in scored[:3]]

        return self._join_sections(candidates)

    def _build_docs_index(self):
        """Построить индекс секций из всех MD-файлов в docs/. Кешируется."""
        if self._docs_index is not None:
            return self._docs_index

        self._docs_index = []
        if not os.path.isdir(DOCS_DIR):
            _logger.warning('Docs directory not found: %s', DOCS_DIR)
            return self._docs_index

        for filename in sorted(os.listdir(DOCS_DIR)):
            if not filename.endswith('.md'):
                continue
            path = os.path.join(DOCS_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            # Определяем модуль по имени файла (stock_xxx → stock)
            file_module = filename.split('_')[0] if '_' in filename else filename[:-3]

            # Разбиваем по заголовкам ## (секции второго уровня)
            sections = re.split(r'\n(?=## )', content)
            for section in sections:
                if section.strip():
                    self._docs_index.append({
                        'text': section,
                        'filename': filename,
                        'module': file_module,
                        'keywords': self._extract_keywords(section),
                    })

        return self._docs_index

    def _score_section(self, section, query_lower, query_words, target_module):
        """Подсчитать релевантность секции к запросу."""
        score = 0
        text_lower = section['text'].lower()
        keywords = section['keywords']

        # Keyword matching
        for kw in keywords:
            if kw in query_lower:
                score += 2
            elif any(word in kw for word in query_words if len(word) > 3):
                score += 1

        # Полнотекстовый поиск
        for word in query_words:
            if len(word) > 3 and word in text_lower:
                score += 1

        # Boost за совпадение модуля
        if section['module'] == target_module:
            score += 2

        return score

    def _extract_keywords(self, text):
        """Извлечь ключевые слова из текста секции."""
        # Из строки Ключевые слова/keywords если есть
        match = re.search(
            r'\*\*Ключевые слова\*\*:\s*([^\n]+)', text, re.IGNORECASE
        )
        if match:
            return [kw.strip().lower() for kw in match.group(1).split(',')]

        # Из заголовков и жирного текста
        words = re.findall(r'\*\*([^*]+)\*\*', text)
        headers = re.findall(r'#{2,3}\s+(.+)', text)
        all_text = ' '.join(words + headers).lower()
        return list(set(re.findall(r'\w{4,}', all_text)))

    def _join_sections(self, sections):
        """Объединить секции в строку с лимитом по символам."""
        result = []
        total = 0
        for section in sections:
            text = section['text'].strip()
            if total + len(text) > MAX_DOCS_CHARS:
                break
            result.append(text)
            total += len(text)
        return '\n\n---\n\n'.join(result)

    def _get_relevant_terms(self, module):
        """
        Извлечь термины из term_mapping.json, релевантные для модуля.
        Возвращает dict с buttons, menu_items, fields, removed_in_v19.
        """
        mapping = self._load_term_mapping()
        if not mapping:
            return {}

        # Фильтруем menu_items по модулю: возвращаем все (небольшой размер)
        return {
            'buttons': mapping.get('buttons', {}),
            'menu_items': mapping.get('menu_items', {}),
            'fields': mapping.get('fields', {}),
            'statuses': mapping.get('statuses', {}),
            'removed_in_v19': mapping.get('removed_in_v19', {}),
        }

    def _load_term_mapping(self):
        """Загрузить term_mapping.json. Кешируется."""
        if self._term_mapping is not None:
            return self._term_mapping

        path = os.path.join(_KNOWLEDGE_DIR, 'term_mapping.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._term_mapping = json.load(f)
        except Exception:
            _logger.warning('Failed to load term_mapping.json from %s', path)
            self._term_mapping = {}

        return self._term_mapping
