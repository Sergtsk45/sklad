import secrets
import threading
import time


class MovingSessionStore:
    """UID-scoped process-local sessions; cross-worker storage is future work."""

    def __init__(self, ttl_seconds=1800):
        self._items = {}
        self._locks = {}
        self._guard = threading.Lock()
        self._ttl_seconds = ttl_seconds

    def put(self, uid, extracted=None):
        self._purge_expired()
        token = secrets.token_urlsafe(18)
        with self._guard:
            self._items[(uid, token)] = {
                'session': self._default_session(extracted),
                'expires_at': time.time() + self._ttl_seconds,
            }
            self._locks[(uid, token)] = threading.Lock()
        return token

    def get_session(self, uid, token):
        self._purge_expired()
        item = self._items.get((uid, token))
        return item and item['session']

    ensure_session = get_session

    def get_lock(self, uid, token):
        if not self.get_session(uid, token):
            raise KeyError('Сессия перемещения не найдена или истекла.')
        with self._guard:
            return self._locks.setdefault((uid, token), threading.Lock())

    def find_latest_token(self, uid, foreground_only=False):
        self._purge_expired()
        candidates = []
        for (item_uid, token), item in self._items.items():
            session = item['session']
            if item_uid != uid:
                continue
            if foreground_only and session['state'] in ('EXECUTED', 'CANCELLED'):
                continue
            candidates.append((item['expires_at'], token))
        return max(candidates)[1] if candidates else None

    def _purge_expired(self):
        now = time.time()
        with self._guard:
            expired = [key for key, item in self._items.items()
                       if item['expires_at'] < now]
            for key in expired:
                self._items.pop(key, None)
                self._locks.pop(key, None)

    def _default_session(self, extracted):
        return {
            'state': 'AWAITING_PRODUCT', 'product_id': None,
            'requested_qty': None, 'requested_uom_id': None,
            'move_qty': None, 'move_uom_id': None,
            'source': None, 'destination': None,
            'source_hint_id': None, 'destination_hint_id': None,
            'availability_snapshot': None, 'generated_origin': None,
            'scheduled_date_text': None, 'scheduled_date_utc': None,
            'editing_date': False,
            'last_options': [], 'picking_id': None, 'executed': False,
            'extracted_raw': dict(extracted or {}),
        }


moving_session_store = MovingSessionStore()
