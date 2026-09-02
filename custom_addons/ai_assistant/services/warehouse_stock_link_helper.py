import re

from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindWarehouseTool,
    GetWarehouseStockLinkTool,
)

_WAREHOUSE_CODE = re.compile(
    r'(?:ОбМ-\d+|O\d{3})',
    re.IGNORECASE | re.UNICODE,
)
_STOCK_LINK_INTENT = re.compile(
    r'(?:'
    r'(?:дай|дайте|нужна|нужен|предостав|получ).{0,20}(?:ссылк|url|фильтр)|'
    r'(?:ссылк|фильтр|открыть|посмотреть|показать).{0,40}'
    r'(?:остат|товар|налич|склад)'
    r')',
    re.IGNORECASE | re.UNICODE,
)
_STOCK_ON_WAREHOUSE = re.compile(
    r'(?:'
    r'что\s+есть|все\s+товар|остатки|наличие|список\s+товар'
    r').{0,50}(?:склад|обм-|этом\s+склад|этого\s+склад)',
    re.IGNORECASE | re.UNICODE,
)
_NONE_LINK = re.compile(r'\[[^\]]+\]\(None\)', re.IGNORECASE)
_WAREHOUSE_NAME_AFTER = re.compile(
    r'склад(?:е)?\s+([^?.!\n,]{3,80})',
    re.IGNORECASE | re.UNICODE,
)


class WarehouseStockLinkHelper:
    """Server-side stock report links filtered by warehouse."""

    def __init__(self, env):
        self.env = env
        self._tool = GetWarehouseStockLinkTool()
        self._find_warehouse = FindWarehouseTool()

    def is_stock_link_request(self, message):
        text = (message or '').strip()
        if not text:
            return False
        return bool(
            _STOCK_LINK_INTENT.search(text)
            or _STOCK_ON_WAREHOUSE.search(text)
        )

    def fetch_link(self, message, history=None):
        if not self.is_stock_link_request(message):
            return None
        warehouse = self._resolve_warehouse(message, history)
        if not warehouse:
            return None
        result = self._tool.execute(self.env, {
            'warehouse_id': warehouse['id'],
            'only_available': self._only_available(message),
        })
        if not result.get('url'):
            return None
        return result

    def _only_available(self, message):
        text = (message or '').lower()
        if 'все товар' in text or 'весь товар' in text:
            return False
        return True

    def _resolve_warehouse(self, message, history):
        texts = self._conversation_texts(message, history)
        for text in texts:
            warehouse = self._find_warehouse_in_text(text)
            if warehouse:
                return warehouse
        return None

    def _conversation_texts(self, message, history):
        texts = [message or '']
        for item in reversed(history or []):
            content = (item or {}).get('content') or ''
            if content:
                texts.append(content)
            if len(texts) >= 8:
                break
        return texts

    def _find_warehouse_in_text(self, text):
        if not text:
            return None
        for query in self._warehouse_queries(text):
            warehouses = self._find_warehouse.execute(
                self.env,
                {'query': query},
            ).get('warehouses') or []
            if len(warehouses) == 1:
                return warehouses[0]
            if len(warehouses) > 1:
                exact = self._pick_exact_code(warehouses, query)
                if exact:
                    return exact
        return None

    def _warehouse_queries(self, text):
        queries = []
        seen = set()
        for match in _WAREHOUSE_CODE.finditer(text):
            value = match.group()
            key = value.lower()
            if key not in seen:
                seen.add(key)
                queries.append(value)
        for match in _WAREHOUSE_NAME_AFTER.finditer(text):
            value = match.group(1).strip()
            if len(value) >= 2 and value.lower() not in seen:
                seen.add(value.lower())
                queries.append(value)
        if 'хмельницк' in text.lower() and 'хмельницк' not in seen:
            queries.append('Хмельницкого')
        return queries

    def _pick_exact_code(self, warehouses, query):
        normalized = query.strip().lower()
        for warehouse in warehouses:
            if warehouse.get('code', '').lower() == normalized:
                return warehouse
        return None

    def build_context_message(self, stock_result):
        if not stock_result or not stock_result.get('url'):
            return None
        return (
            'WAREHOUSE_STOCK_LINK (обязательно используй в ответе): '
            'label=%(label)s url=%(url)s warehouse=%(warehouse_code)s '
            'menu=%(menu_breadcrumb)s'
        ) % stock_result

    def enrich_answer(self, answer, stock_result):
        if not stock_result or not stock_result.get('url'):
            return answer or ''

        url = stock_result['url']
        label = stock_result['label']
        text = answer or ''
        link_md = '[Открыть «%s»](%s)' % (label, url)

        if _NONE_LINK.search(text):
            return _NONE_LINK.sub(link_md, text, count=1)

        if url in text:
            return text

        if text and not text.endswith('\n'):
            text += '\n'
        return text + link_md

    def response_links(self, stock_result):
        if not stock_result or not stock_result.get('url'):
            return []
        return [{
            'label': stock_result['label'],
            'url': stock_result['url'],
            'menu_breadcrumb': stock_result.get('menu_breadcrumb') or '',
        }]
