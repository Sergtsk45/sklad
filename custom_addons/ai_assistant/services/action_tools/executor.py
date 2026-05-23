import logging
import re
import time

from odoo.exceptions import AccessError, UserError, ValidationError

from .base import AbstractWriteTool
from .registry import default_registry

_logger = logging.getLogger(__name__)

_FORBIDDEN_METHOD_PATTERNS = [
    r'button_confirm',
    r'button_validate',
    r'action_done',
    r'action_post',
]
_FORBIDDEN_WRITE_FIELDS = {'state', 'company_id', 'currency_id'}


class ToolRateLimiter:
    """Small in-memory per-user limiter for action tools."""

    def __init__(self, read_max=30, write_max=5, window_seconds=60):
        self._limits = {
            'read': read_max,
            'write': write_max,
        }
        self._window_seconds = window_seconds
        self._hits = {}

    def check(self, uid, kind):
        now = time.time()
        key = (uid, kind)
        hits = [
            ts for ts in self._hits.get(key, [])
            if now - ts < self._window_seconds
        ]
        limit = self._limits[kind]
        if len(hits) >= limit:
            retry_after = int(self._window_seconds - (now - hits[0])) + 1
            self._hits[key] = hits
            return False, max(1, retry_after)
        hits.append(now)
        self._hits[key] = hits
        return True, 0

    def clear(self):
        self._hits.clear()


_TOOL_RATE = ToolRateLimiter()


class ToolExecutor:
    """Execute registered action tools with ACL, schema and guard checks."""

    def __init__(self, env, user_id=None, registry=None, rate_limiter=None):
        self.env = (
            env(user=env['res.users'].browse(user_id)) if user_id else env
        )
        self.registry = registry or default_registry
        self.rate_limiter = rate_limiter or _TOOL_RATE

    def execute(self, name, args):
        try:
            tool = self.registry.get(name)
        except KeyError:
            return self._error('unknown_tool', 'Неизвестный tool: %s' % name)

        try:
            self._check_forbidden_tool(tool)
            self._check_groups(tool)
            tool.validate_args(args or {})
            rate_ok, retry_after = self._check_rate(tool)
            if not rate_ok:
                return self._error(
                    'rate_limited',
                    'Слишком много действий. Повторите позже.',
                    retry_after=retry_after,
                )
            _logger.info(
                'AI tool execute: name=%s write=%s',
                tool.name,
                bool(tool.is_write),
            )
            result = tool.execute(self.env, args or {})
            return {'success': True, 'result': result}
        except AccessError as err:
            return self._error('access_denied', str(err))
        except ValidationError as err:
            return self._error('validation_error', str(err))
        except UserError as err:
            return self._error('user_error', str(err))
        except ValueError as err:
            return self._error('invalid_arguments', str(err))
        except Exception as err:
            _logger.exception('AI tool failed: name=%s', name)
            return self._error('tool_error', str(err))

    def _check_forbidden_tool(self, tool):
        for pattern in _FORBIDDEN_METHOD_PATTERNS:
            if re.search(pattern, tool.name):
                _logger.warning(
                    'AI tool forbidden by name denylist: name=%s pattern=%s',
                    tool.name,
                    pattern,
                )
                raise AccessError(
                    'Запрещённая операция AI-ассистента: %s.' % tool.name
                )
        if isinstance(tool, AbstractWriteTool):
            properties = (tool.parameters_schema or {}).get('properties', {})
            forbidden = _FORBIDDEN_WRITE_FIELDS & set(properties)
            if forbidden:
                _logger.warning(
                    'AI write tool forbidden fields: name=%s fields=%s',
                    tool.name,
                    ','.join(sorted(forbidden)),
                )
                raise AccessError(
                    'Write tool содержит запрещённые поля: %s.'
                    % ', '.join(sorted(forbidden))
                )

    def _check_groups(self, tool):
        for xmlid in tool.required_groups or []:
            if not self.env.user.has_group(xmlid):
                raise AccessError(
                    'Недостаточно прав для выполнения tool: %s.' % tool.name
                )

    def _check_rate(self, tool):
        kind = 'write' if tool.is_write else 'read'
        return self.rate_limiter.check(self.env.uid, kind)

    def _error(self, code, message, **extra):
        error = {
            'code': code,
            'message': message,
        }
        error.update(extra)
        return {
            'success': False,
            'error': error,
        }
