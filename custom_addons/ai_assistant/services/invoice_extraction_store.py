# @file: invoice_extraction_store.py
# @description: In-memory TTL-хранилище результатов парсинга счетов.
# @dependencies: secrets, time
# @created: 2026-05-30

import secrets
import time


class InvoiceExtractionStore:
    """
    In-memory store for parsed invoice data awaiting use in a chat message.
    Keyed by (uid, extraction_token). Default TTL: 30 minutes.
    """

    def __init__(self, ttl_seconds=1800):
        self._items = {}
        self._ttl_seconds = ttl_seconds

    def put(self, uid, invoice_data):
        """Сохраняет данные счёта, возвращает extraction_token."""
        self._purge_expired()
        token = secrets.token_urlsafe(18)
        self._items[(uid, token)] = {
            'data': invoice_data,
            'session': {
                'created_by_line': {},
                'created_partner_id': None,
            },
            'expires_at': time.time() + self._ttl_seconds,
        }
        return token

    def get_session(self, uid, token):
        item = self._get_item(uid, token)
        if not item:
            return None
        return item.get('session')

    def ensure_session(self, uid, token):
        item = self._get_item(uid, token)
        if not item:
            return None
        if 'session' not in item:
            item['session'] = {
                'created_by_line': {},
                'created_partner_id': None,
            }
        if 'created_by_line' not in item['session']:
            item['session']['created_by_line'] = {}
        if 'created_partner_id' not in item['session']:
            item['session']['created_partner_id'] = None
        return item['session']

    def find_latest_token(self, uid):
        """Последний неистёкший token пользователя."""
        self._purge_expired()
        latest = None
        latest_expires = 0
        for (item_uid, token), item in self._items.items():
            if item_uid != uid:
                continue
            if item['expires_at'] >= latest_expires:
                latest_expires = item['expires_at']
                latest = token
        return latest

    def _get_item(self, uid, token):
        self._purge_expired()
        item = self._items.get((uid, token))
        if not item:
            return None
        if item['expires_at'] < time.time():
            self._items.pop((uid, token), None)
            return None
        return item

    def get(self, uid, token):
        """Возвращает данные счёта или None если не найдено/истекло."""
        item = self._get_item(uid, token)
        if not item:
            return None
        return item['data']

    def pop(self, uid, token):
        """Извлекает данные счёта (удаляет из store)."""
        item = self._items.pop((uid, token), None)
        if item is None:
            return None
        if item['expires_at'] < time.time():
            return None
        return item['data']

    def _purge_expired(self):
        now = time.time()
        for key in list(self._items):
            if self._items[key]['expires_at'] < now:
                self._items.pop(key, None)
