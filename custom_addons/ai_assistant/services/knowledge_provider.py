import json
import logging
import os
import re

_logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'static', 'knowledge'
)

GENERATED_DIR = os.path.join(_KNOWLEDGE_DIR, 'generated')

MAX_SNIPPET_CHARS = 8000  # ~2000 tokens
MAX_TECH_CONTEXT_CHARS = 15000  # ~4000 tokens

MODULE_CONTEXT_FILES = {
    'stock': 'stock_context.md',
    'purchase': 'purchase_context.md',
    'sale': 'sale_context.md',
    'crm': 'crm_context.md',
    'contacts': 'contacts_context.md',
    'account': 'account_context.md',
    'object_request': 'object_request_context.md',
}


class KnowledgeProvider:

    def __init__(self):
        self._index = None
        self._cache = {}
        self._tech_cache = {}

    def load_knowledge_index(self):
        if self._index is not None:
            return self._index
        index_path = os.path.join(_KNOWLEDGE_DIR, 'index.json')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                self._index = json.load(f)
        except Exception:
            _logger.warning(
                'Failed to load knowledge index from %s', index_path
            )
            self._index = {'modules': [], 'fallback_module': 'settings'}
        return self._index

    def get_snippets(self, module, query, limit=5):
        index = self.load_knowledge_index()
        entry = self._find_module_entry(index, module)

        if entry is None:
            fallback = index.get('fallback_module', 'settings')
            entry = self._find_module_entry(index, fallback)

        if entry is None:
            return []

        snippets = self._load_snippets(entry['file'])
        ranked = self._rank_snippets(snippets, query)
        return self._apply_size_limit(ranked[:limit])

    def _find_module_entry(self, index, module):
        for entry in index.get('modules', []):
            if entry.get('module') == module:
                return entry
        return None

    def _load_snippets(self, filename):
        if filename in self._cache:
            return self._cache[filename]
        path = os.path.join(_KNOWLEDGE_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            snippets = data.get('snippets', [])
            self._cache[filename] = snippets
            return snippets
        except Exception:
            _logger.warning('Failed to load knowledge file: %s', filename)
            return []

    def _rank_snippets(self, snippets, query):
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        scored = []
        for snippet in snippets:
            score = 0
            keywords = [kw.lower() for kw in snippet.get('keywords', [])]
            for kw in keywords:
                if kw in query_lower:
                    score += 2
            for word in query_words:
                if any(word in kw for kw in keywords):
                    score += 1
            scored.append((score, snippet))
        scored.sort(key=lambda x: x[0], reverse=True)
        positive = [(sc, s) for sc, s in scored if sc > 0]
        if positive:
            return [s for _, s in positive]
        return [s for _, s in scored[:3]]

    def get_technical_context(self, module):
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
                'Failed to read technical context for module %r: %s', module, path
            )
            self._tech_cache[module] = None
            return None

        if len(content) > MAX_TECH_CONTEXT_CHARS:
            content = content[:MAX_TECH_CONTEXT_CHARS] + '\n...(обрезано)'

        self._tech_cache[module] = content
        return content

    def _apply_size_limit(self, snippets):
        result = []
        total = 0
        for snippet in snippets:
            content = snippet.get('content', '')
            if total + len(content) > MAX_SNIPPET_CHARS:
                break
            result.append(snippet)
            total += len(content)
        return result
