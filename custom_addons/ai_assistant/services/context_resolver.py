import logging

_logger = logging.getLogger(__name__)

CONTEXT_WHITELIST = frozenset([
    'module', 'action', 'model', 'view_type', 'lang', 'user_groups', 'url',
])

ALLOWED_MODULES = frozenset([
    'crm', 'sale', 'purchase', 'stock', 'contacts',
    'settings', 'account', 'project', 'hr',
])

ALLOWED_VIEW_TYPES = frozenset([
    'list', 'form', 'kanban', 'dashboard', 'pivot', 'graph', 'calendar',
])


class ContextResolver:
    """Validates and enriches client context with server-side user data."""

    def resolve(self, raw_context, env):
        """
        Filter client context through whitelist and add server-side fields.

        :param raw_context: dict from frontend (untrusted)
        :param env: Odoo environment
        :return: validated context dict
        """
        if not isinstance(raw_context, dict):
            raw_context = {}

        ctx = {}
        for field in CONTEXT_WHITELIST:
            if field in raw_context:
                ctx[field] = raw_context[field]

        ctx = self._sanitize_fields(ctx)
        ctx['lang'] = self._get_lang(env)
        ctx['user_groups'] = self._get_user_groups(env)

        return ctx

    def _sanitize_fields(self, ctx):
        result = {}

        if 'module' in ctx:
            val = str(ctx['module'])[:64]
            result['module'] = val

        if 'action' in ctx:
            result['action'] = str(ctx['action'])[:128]

        if 'model' in ctx:
            result['model'] = str(ctx['model'])[:128]

        if 'view_type' in ctx:
            vt = str(ctx['view_type'])
            result['view_type'] = vt if vt in ALLOWED_VIEW_TYPES else ''

        if 'url' in ctx:
            result['url'] = str(ctx['url'])[:256]

        return result

    def _get_lang(self, env):
        try:
            return env.user.lang or 'ru_RU'
        except Exception:
            return 'ru_RU'

    def _get_user_groups(self, env):
        try:
            groups = env.user.groups_id
            names = groups.filtered(
                lambda g: g.category_id and g.category_id.name not in (
                    'Technical', 'Extra Rights'
                )
            ).mapped('full_name')
            return names[:20]
        except Exception:
            _logger.warning('Failed to fetch user groups for context')
            return []
