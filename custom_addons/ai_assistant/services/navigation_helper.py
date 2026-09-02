import re

from odoo.addons.ai_assistant.services.action_tools.navigation_catalog import (
    NAVIGATION_CATALOG,
)
from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    GetNavigationLinkTool,
)

_NAVIGATION_INTENT = re.compile(
    r'(?:^|\s)(?:как|где|куда)\s+(?:\S+\s+){0,6}'
    r'(?:посмотреть|открыть|перейти|попасть|'
    r'найти\s+(?:раздел|список|меню|экран))',
    re.IGNORECASE | re.UNICODE,
)
_NAVIGATION_INTENT_ALT = re.compile(
    r'(?:покажи|подскажи|объясни).{0,30}'
    r'(?:где|как).{0,30}(?:посмотреть|открыть|перейти|найти)',
    re.IGNORECASE | re.UNICODE,
)
_ENTITY_SEARCH = re.compile(
    r'(?:^|\s)найди(?:те)?\s+\S',
    re.IGNORECASE | re.UNICODE,
)
_NONE_LINK = re.compile(r'\[[^\]]+\]\(None\)', re.IGNORECASE)


class NavigationHelper:
    """Server-side navigation: detect intent, resolve topic, enrich answer."""

    def __init__(self, env):
        self.env = env
        self._tool = GetNavigationLinkTool()

    def is_navigation_question(self, message):
        text = (message or '').strip()
        if not text:
            return False
        if _ENTITY_SEARCH.search(text) and not _NAVIGATION_INTENT.search(text):
            return False
        return bool(
            _NAVIGATION_INTENT.search(text)
            or _NAVIGATION_INTENT_ALT.search(text)
        )

    def resolve_topic(self, message):
        text = self._tool._normalize_topic(message)
        if not text:
            return None

        best_key = None
        best_len = 0
        for record in NAVIGATION_CATALOG:
            for key in record['topic_keys']:
                normalized = self._tool._normalize_topic(key)
                if normalized in text and len(normalized) > best_len:
                    best_key = normalized
                    best_len = len(normalized)
        if best_key:
            return best_key

        if self._tool._find_record(text):
            return text
        return None

    def fetch_link(self, message):
        if not self.is_navigation_question(message):
            return None
        topic = self.resolve_topic(message)
        if not topic:
            return None
        result = self._tool.execute(self.env, {'topic': topic})
        if not result.get('url'):
            return None
        return result

    def build_context_message(self, nav_result):
        if not nav_result or not nav_result.get('url'):
            return None
        return (
            'NAVIGATION_LINK (обязательно используй в ответе): '
            'label=%(label)s url=%(url)s menu=%(menu_breadcrumb)s'
        ) % nav_result

    def enrich_answer(self, answer, nav_result):
        if not nav_result or not nav_result.get('url'):
            return answer or ''

        url = nav_result['url']
        label = nav_result['label']
        text = answer or ''
        link_md = '[Открыть «%s»](%s)' % (label, url)

        if _NONE_LINK.search(text):
            return _NONE_LINK.sub(link_md, text, count=1)

        if url in text:
            return text

        if text and not text.endswith('\n'):
            text += '\n'
        return text + link_md

    def response_links(self, nav_result):
        if not nav_result or not nav_result.get('url'):
            return []
        return [{
            'label': nav_result['label'],
            'url': nav_result['url'],
            'menu_breadcrumb': nav_result.get('menu_breadcrumb') or '',
        }]
