"""
AIA-028: Unit-тесты vision pipeline.
Покрывают: screenshot_trigger (Python-stub), _parse_screenshot,
_vision_rate_ok, prompt_builder vision mode, multimodal content.
"""
import time
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.prompt_builder import PromptBuilder


# --------------------------------------------------------------------------
# Вспомогательные константы
# --------------------------------------------------------------------------

_VALID_JPEG_B64 = 'A' * 1000          # < 500KB
_OVERSIZED_B64  = 'A' * 600_000       # > 500KB
_VALID_DATA_URL = f'data:image/jpeg;base64,{_VALID_JPEG_B64}'
_PNG_DATA_URL   = f'data:image/png;base64,{_VALID_JPEG_B64}'
_OVERSIZED_URL  = f'data:image/jpeg;base64,{_OVERSIZED_B64}'


# --------------------------------------------------------------------------
# Тесты needsScreenshot (Python-эквивалент screenshot_trigger.js)
# --------------------------------------------------------------------------

def _needs_screenshot_py(message):
    """Python-версия JS needsScreenshot для тестирования логики."""
    TRIGGERS = [
        'на экране', 'на моём экране', 'на моем экране',
        'что я вижу', 'что вижу', 'смотри на экран',
        'посмотри на экран', 'глянь на экран',
        'в открытой вкладке', 'на открытой странице',
        'на этой странице', 'на текущем экране',
        'что тут', 'что здесь', 'помоги с тем что открыто',
        'покажу экран', 'вот мой экран', 'скриншот',
        'покажи что вижу', 'опиши экран', 'опиши что вижу',
        'что открыто',
    ]
    if not message:
        return False
    lower = message.lower()
    return any(t in lower for t in TRIGGERS)


@tagged('post_install', '-at_install')
class TestScreenshotTrigger(TransactionCase):

    # --- Позитивные случаи ---

    def test_trigger_на_экране(self):
        self.assertTrue(_needs_screenshot_py('что у меня на экране?'))

    def test_trigger_смотри_на_экран(self):
        self.assertTrue(_needs_screenshot_py('смотри на экран'))

    def test_trigger_что_я_вижу(self):
        self.assertTrue(_needs_screenshot_py('что я вижу здесь?'))

    def test_trigger_скриншот(self):
        self.assertTrue(_needs_screenshot_py('сделай скриншот'))

    def test_trigger_подстрока(self):
        self.assertTrue(_needs_screenshot_py('помоги с тем что открыто, не понимаю'))

    def test_trigger_case_insensitive(self):
        self.assertTrue(_needs_screenshot_py('СМОТРИ НА ЭКРАН'))

    def test_trigger_на_этой_странице(self):
        self.assertTrue(_needs_screenshot_py('что есть на этой странице?'))

    def test_trigger_опиши_экран(self):
        self.assertTrue(_needs_screenshot_py('опиши экран'))

    # --- Негативные случаи ---

    def test_no_trigger_normal_question(self):
        self.assertFalse(_needs_screenshot_py('как создать склад?'))

    def test_no_trigger_empty_string(self):
        self.assertFalse(_needs_screenshot_py(''))

    def test_no_trigger_none(self):
        self.assertFalse(_needs_screenshot_py(None))

    def test_no_trigger_invoice_question(self):
        self.assertFalse(_needs_screenshot_py('как выставить счёт покупателю?'))

    def test_no_trigger_product_question(self):
        self.assertFalse(_needs_screenshot_py('как добавить товар на склад?'))

    def test_no_trigger_settings_question(self):
        self.assertFalse(_needs_screenshot_py('где настройки складского учёта?'))

    def test_no_trigger_crm_question(self):
        self.assertFalse(_needs_screenshot_py('как создать лид в crm?'))


# --------------------------------------------------------------------------
# Тесты _parse_screenshot (backend AIA-024)
# --------------------------------------------------------------------------

@tagged('post_install', '-at_install')
class TestParseScreenshot(TransactionCase):

    def setUp(self):
        super().setUp()
        # Импортируем контроллер напрямую для тестирования приватных методов
        from odoo.addons.ai_assistant.controllers.chat_controller import (
            AiAssistantController,
        )
        self.ctrl = AiAssistantController()

    def test_valid_jpeg_returns_dict(self):
        result = self.ctrl._parse_screenshot(_VALID_DATA_URL)
        self.assertIsNotNone(result)
        self.assertEqual(result['media_type'], 'image/jpeg')
        self.assertEqual(result['data'], _VALID_JPEG_B64)

    def test_valid_png_returns_dict(self):
        result = self.ctrl._parse_screenshot(_PNG_DATA_URL)
        self.assertIsNotNone(result)
        self.assertEqual(result['media_type'], 'image/png')

    def test_none_returns_none(self):
        self.assertIsNone(self.ctrl._parse_screenshot(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(self.ctrl._parse_screenshot(''))

    def test_wrong_prefix_returns_none(self):
        self.assertIsNone(self.ctrl._parse_screenshot('data:text/plain;base64,abc'))

    def test_oversized_returns_none(self):
        self.assertIsNone(self.ctrl._parse_screenshot(_OVERSIZED_URL))

    def test_malformed_no_comma_returns_none(self):
        self.assertIsNone(self.ctrl._parse_screenshot('data:image/jpeg;base64'))

    def test_unknown_media_type_returns_none(self):
        url = 'data:image/bmp;base64,' + _VALID_JPEG_B64
        self.assertIsNone(self.ctrl._parse_screenshot(url))


# --------------------------------------------------------------------------
# Тесты _vision_rate_ok (AIA-026)
# --------------------------------------------------------------------------

@tagged('post_install', '-at_install')
class TestVisionRateLimit(TransactionCase):

    def setUp(self):
        super().setUp()
        from odoo.addons.ai_assistant.controllers import chat_controller
        # Очищаем глобальный словарь перед каждым тестом
        chat_controller._VISION_RATE.clear()
        from odoo.addons.ai_assistant.controllers.chat_controller import (
            AiAssistantController,
        )
        self.ctrl = AiAssistantController()

    def test_first_request_allowed(self):
        self.assertTrue(self.ctrl._vision_rate_ok(uid=999))

    def test_within_limit_allowed(self):
        for _ in range(4):
            self.assertTrue(self.ctrl._vision_rate_ok(uid=888))

    def test_exceeds_limit_blocked(self):
        from odoo.addons.ai_assistant.controllers.chat_controller import VISION_RATE_MAX
        for _ in range(VISION_RATE_MAX):
            self.ctrl._vision_rate_ok(uid=777)
        # Следующий должен быть заблокирован
        self.assertFalse(self.ctrl._vision_rate_ok(uid=777))

    def test_different_users_independent(self):
        from odoo.addons.ai_assistant.controllers.chat_controller import VISION_RATE_MAX
        for _ in range(VISION_RATE_MAX):
            self.ctrl._vision_rate_ok(uid=100)
        # Другой пользователь не заблокирован
        self.assertTrue(self.ctrl._vision_rate_ok(uid=200))

    def test_old_timestamps_expire(self):
        from odoo.addons.ai_assistant.controllers import chat_controller
        # Заполняем старыми метками (за пределами окна)
        old_time = time.time() - 120  # 2 минуты назад
        chat_controller._VISION_RATE[555] = [old_time] * 10
        # Должно пройти (старые метки удалены)
        self.assertTrue(self.ctrl._vision_rate_ok(uid=555))


# --------------------------------------------------------------------------
# Тесты prompt_builder vision mode (AIA-025)
# --------------------------------------------------------------------------

@tagged('post_install', '-at_install')
class TestPromptBuilderVisionMode(TransactionCase):

    def setUp(self):
        super().setUp()
        self.builder = PromptBuilder()

    def _make_image_data(self):
        return {'media_type': 'image/jpeg', 'data': _VALID_JPEG_B64}

    def test_vision_message_is_list(self):
        """При image_data пользовательское сообщение — массив content."""
        msgs = self.builder.build_messages(
            'Что на экране?', [], context=None,
            image_data=self._make_image_data(),
            override='SYS',
        )
        user_msg = msgs[-1]
        self.assertEqual(user_msg['role'], 'user')
        self.assertIsInstance(user_msg['content'], list)

    def test_vision_content_has_text_and_image(self):
        """Массив content должен содержать text и image_url элементы."""
        msgs = self.builder.build_messages(
            'Что на экране?', [], context=None,
            image_data=self._make_image_data(),
            override='SYS',
        )
        content = msgs[-1]['content']
        types = [item['type'] for item in content]
        self.assertIn('text', types)
        self.assertIn('image_url', types)

    def test_vision_image_url_contains_base64(self):
        """image_url должен содержать data URL с base64."""
        msgs = self.builder.build_messages(
            'Покажи что вижу', [], context=None,
            image_data=self._make_image_data(),
            override='SYS',
        )
        content = msgs[-1]['content']
        img_item = next(i for i in content if i['type'] == 'image_url')
        url = img_item['image_url']['url']
        self.assertTrue(url.startswith('data:image/jpeg;base64,'))
        self.assertIn(_VALID_JPEG_B64, url)

    def test_text_mode_user_message_is_string(self):
        """Без image_data пользовательское сообщение — строка."""
        msgs = self.builder.build_messages(
            'Как создать склад?', [], context=None, override='SYS'
        )
        self.assertIsInstance(msgs[-1]['content'], str)
        self.assertEqual(msgs[-1]['content'], 'Как создать склад?')

    def test_vision_prompt_contains_context(self):
        """vision prompt должен включать контекст модуля."""
        ctx = {'module': 'stock', 'model': 'stock.picking', 'view_type': 'list'}
        msgs = self.builder.build_messages(
            'Что вижу?', [], context=ctx,
            image_data=self._make_image_data(),
            override='SYS',
        )
        content = msgs[-1]['content']
        text_item = next(i for i in content if i['type'] == 'text')
        self.assertIn('stock', text_item['text'])
        self.assertIn('list', text_item['text'])

    def test_vision_prompt_instructs_real_screen(self):
        """vision prompt должен требовать анализа реального экрана."""
        msgs = self.builder.build_messages(
            'Что вижу?', [], context=None,
            image_data=self._make_image_data(),
            override='SYS',
        )
        content = msgs[-1]['content']
        text_item = next(i for i in content if i['type'] == 'text')
        self.assertIn('скриншот', text_item['text'].lower())

    def test_build_vision_prompt_method_directly(self):
        vp = self.builder._build_vision_prompt(
            'что это?',
            {'module': 'crm', 'view_type': 'kanban', 'lang': 'ru_RU'},
        )
        self.assertIn('crm', vp)
        self.assertIn('kanban', vp)
        self.assertIn('что это?', vp)

    def test_no_image_data_none_is_text_mode(self):
        """image_data=None → текстовый режим."""
        msgs = self.builder.build_messages(
            'Вопрос', [], context=None, image_data=None, override='SYS'
        )
        self.assertIsInstance(msgs[-1]['content'], str)
