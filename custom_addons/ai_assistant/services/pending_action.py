import secrets
import time


class PendingActionStore:
    """In-memory store for write tool calls awaiting UI confirmation."""

    def __init__(self, ttl_seconds=600):
        self._items = {}
        self._ttl_seconds = ttl_seconds

    def put(self, uid, tool_name, args, idempotency_key=None):
        self._purge_expired()
        if idempotency_key:
            existing_key = self._find_existing(
                uid,
                tool_name,
                idempotency_key,
            )
            if existing_key:
                return existing_key
        key = secrets.token_urlsafe(18)
        self._items[(uid, key)] = {
            'tool_name': tool_name,
            'args': args,
            'idempotency_key': idempotency_key,
            'expires_at': time.time() + self._ttl_seconds,
        }
        return key

    def get(self, uid, key):
        self._purge_expired()
        item = self._items.get((uid, key))
        if not item:
            return None
        if item['expires_at'] < time.time():
            self._items.pop((uid, key), None)
            return None
        return item

    def pop(self, uid, key):
        item = self._items.pop((uid, key), None)
        if item is None:
            return None
        if item['expires_at'] < time.time():
            return None
        return item

    def clear(self, uid):
        for item_key in list(self._items):
            if item_key[0] == uid:
                self._items.pop(item_key, None)

    def _purge_expired(self):
        now = time.time()
        for item_key, item in list(self._items.items()):
            if item['expires_at'] < now:
                self._items.pop(item_key, None)

    def _find_existing(self, uid, tool_name, idempotency_key):
        for (item_uid, key), item in self._items.items():
            if (
                item_uid == uid and
                item['tool_name'] == tool_name and
                item.get('idempotency_key') == idempotency_key
            ):
                return key
        return None
