"""OBR-031: AI security, config params, chatter logging."""
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_CANDIDATE_PATCH = (
    'odoo.addons.object_request.models.'
    'matching_candidate_service.'
    'ObjectRequestMatchingCandidateService.build_candidates'
)
_OPENROUTER_PATCH = (
    'odoo.addons.ai_assistant.services.openrouter_client'
    '.OpenRouterClient.send_chat'
)
_EMPTY_RESULT = {
    'line_type': 'product_candidate',
    'combined_query': '',
    'candidates': [],
    'can_call_llm': False,
    'note': 'Кандидаты не найдены.',
    'limits': {'internal': 15, 'llm': 8, 'preview': 3},
}


@tagged('post_install', '-at_install')
class TestObr031AISecurity(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create(
            {'name': 'Тест OBR-031'}
        )
        self.user = self.env.user
        self.request = self.env['object.request'].create(
            {
                'project_id': self.project.id,
                'foreman_user_id': self.user.id,
                'need_date': '2026-06-01',
            }
        )
        self.service = self.env[
            'object.request.llm.matching.service'
        ]

    def _create_unmatched_line(self, name='Труба Ду50'):
        return self.env['object.request.line'].create(
            {
                'request_id': self.request.id,
                'name_raw': name,
                'qty_requested': 1.0,
                'matching_required': True,
            }
        )

    def test_config_params_defaults(self):
        """Дефолтные значения параметров корректны."""
        config = self.service._get_ai_config()
        self.assertTrue(config['enabled'])
        self.assertAlmostEqual(config['auto_threshold'], 0.90)
        self.assertAlmostEqual(config['suggest_threshold'], 0.70)
        self.assertEqual(config['batch_size'], 50)

    def test_config_param_enabled_false(self):
        """Параметр enabled=False читается из ir.config_parameter."""
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_enabled', 'False'
        )
        config = self.service._get_ai_config()
        self.assertFalse(config['enabled'])

    def test_ai_disabled_skips_llm(self):
        """При ai_matching_enabled=False LLM (OpenRouter) не вызывается."""
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_enabled', 'False'
        )
        self._create_unmatched_line()
        with patch(_CANDIDATE_PATCH, return_value=_EMPTY_RESULT):
            with patch(_OPENROUTER_PATCH) as mock_send:
                self.request.action_prepare_ai_candidates()
        mock_send.assert_not_called()

    def test_ai_disabled_posts_chatter_note(self):
        """При disabled в чаттере появляется заметка об отключении."""
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_enabled', 'False'
        )
        self._create_unmatched_line()
        msg_before = len(self.request.message_ids)
        with patch(_CANDIDATE_PATCH, return_value=_EMPTY_RESULT):
            self.request.action_prepare_ai_candidates()
        self.assertGreater(len(self.request.message_ids), msg_before)
        bodies = ''.join(
            m.body for m in self.request.message_ids
        )
        self.assertIn('отключено', bodies)

    def test_batch_size_limits_processing(self):
        """batch_size ограничивает количество строк в одном запуске."""
        for i in range(5):
            self._create_unmatched_line(f'Материал {i}')
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_batch_size', '2'
        )
        call_count = []

        def fake_build(
            name_raw,
            article,
            vendor=None,
            technical_designation=None,
        ):
            call_count.append(1)
            return _EMPTY_RESULT

        with patch(_CANDIDATE_PATCH, side_effect=fake_build):
            self.request.action_prepare_ai_candidates()
        self.assertEqual(sum(call_count), 2)

    def test_chatter_note_after_ai_action(self):
        """После action_prepare_ai_candidates есть заметка в чаттере."""
        self._create_unmatched_line('Кран шаровой Ду25')
        msg_before = len(self.request.message_ids)
        with patch(_CANDIDATE_PATCH, return_value=_EMPTY_RESULT):
            self.request.action_prepare_ai_candidates()
        self.assertGreater(len(self.request.message_ids), msg_before)
        bodies = ''.join(
            m.body for m in self.request.message_ids
        )
        self.assertIn('AI-подбор кандидатов', bodies)
        self.assertIn('Обработано строк', bodies)

    def test_llm_error_does_not_break_import(self):
        """Ошибка build_candidates не прерывает процесс."""
        line = self._create_unmatched_line('Отвод 90 Ду50')

        def raise_error(
            name_raw,
            article,
            vendor=None,
            technical_designation=None,
        ):
            raise RuntimeError('Test LLM error')

        with patch(_CANDIDATE_PATCH, side_effect=raise_error):
            result = self.request.action_prepare_ai_candidates()
        self.assertIsNotNone(result)
        self.assertEqual(result.get('type'), 'ir.actions.client')
        line.invalidate_recordset()
        self.assertIn('Test LLM error', line.ai_match_reason or '')

    def test_call_llm_raises_when_disabled(self):
        """_call_llm выбрасывает ValueError при enabled=False."""
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_enabled', 'False'
        )
        with self.assertRaises(ValueError):
            self.service._call_llm('test', 'art', [{'product_id': 1}])

    def test_batch_size_custom_value(self):
        """Кастомный batch_size читается из ir.config_parameter."""
        self.env['ir.config_parameter'].set_param(
            'object_request.ai_matching_batch_size', '10'
        )
        config = self.service._get_ai_config()
        self.assertEqual(config['batch_size'], 10)
