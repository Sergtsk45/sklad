import logging
import re

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


class ToolExecutor:
    """Execute registered action tools with ACL, schema and guard checks."""

    def __init__(self, env, user_id=None, registry=None):
        self.env = (
            env(user=env['res.users'].browse(user_id)) if user_id else env
        )
        self.registry = registry or default_registry

    def execute(self, name, args):
        try:
            tool = self.registry.get(name)
        except KeyError:
            return self._error('unknown_tool', 'Неизвестный tool: %s' % name)

        try:
            self._check_forbidden_tool(tool)
            self._check_groups(tool)
            tool.validate_args(args or {})
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
                raise AccessError(
                    'Запрещённая операция AI-ассистента: %s.' % tool.name
                )
        if isinstance(tool, AbstractWriteTool):
            properties = (tool.parameters_schema or {}).get('properties', {})
            forbidden = _FORBIDDEN_WRITE_FIELDS & set(properties)
            if forbidden:
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

    def _error(self, code, message):
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message,
            },
        }
