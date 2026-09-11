import secrets
import threading
import time


class ReplenishmentSessionStore:
    """Process-local TTL store; intentionally matches existing invoice store."""

    def __init__(self, ttl_seconds=1800):
        self._items = {}
        self._locks = {}
        self._guard = threading.Lock()
        self._ttl_seconds = ttl_seconds

    def put(self, uid, extracted=None):
        self._purge_expired()
        token = secrets.token_urlsafe(18)
        session = self._default_session(extracted)
        with self._guard:
            self._items[(uid, token)] = {
                'session': session,
                'expires_at': time.time() + self._ttl_seconds,
            }
            self._locks[(uid, token)] = threading.Lock()
        return token

    def get_session(self, uid, token):
        item = self._get_item(uid, token)
        return item and item['session']

    def ensure_session(self, uid, token):
        return self.get_session(uid, token)

    def find_latest_token(self, uid):
        self._purge_expired()
        candidates = [
            (item['expires_at'], token)
            for (item_uid, token), item in self._items.items()
            if item_uid == uid
        ]
        return max(candidates)[1] if candidates else None

    def get_lock(self, uid, token):
        if not self._get_item(uid, token):
            raise KeyError('Сессия пополнения не найдена или истекла.')
        with self._guard:
            return self._locks.setdefault((uid, token), threading.Lock())

    def pop(self, uid, token):
        with self._guard:
            item = self._items.pop((uid, token), None)
            self._locks.pop((uid, token), None)
        if not item or item['expires_at'] < time.time():
            return None
        return item['session']

    def _get_item(self, uid, token):
        self._purge_expired()
        return self._items.get((uid, token))

    def _purge_expired(self):
        now = time.time()
        with self._guard:
            expired = [key for key, item in self._items.items()
                       if item['expires_at'] < now]
            for key in expired:
                self._items.pop(key, None)
                self._locks.pop(key, None)

    def _default_session(self, extracted):
        extracted = dict(extracted or {})
        return {
            'state': 'AWAITING_PRODUCT',
            'product_id': None,
            'qty': None,
            'requested_uom_id': None,
            'qty_source': None,
            'vendor': None,
            'warehouse': None,
            'po_id': None,
            'executed': False,
            'extracted_raw': extracted,
            'last_options': [],
        }


replenishment_session_store = ReplenishmentSessionStore()
