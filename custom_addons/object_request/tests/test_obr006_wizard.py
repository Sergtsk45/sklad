import base64
import io

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged


def _make_xlsx(rows):
    """Создаёт Excel-файл в памяти и возвращает base64-строку."""
    try:
        import openpyxl
    except ImportError:
        return None
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


VALID_HEADER = ['№ п/п', 'Артикул', 'Наименование', 'Ед. изм.', 'Кол-во', 'Цена', 'Комм.', 'Поставщик']
VALID_ROW_1 = [1, 'ART-001', 'Цемент М500', 'мешок', 10, 500.0, '', 'ООО Стройснаб']
VALID_ROW_2 = [2, 'ART-002', 'Песок речной', 'т', 5, 800.0, 'для фундамента', 'ИП Иванов']


@tagged('post_install', '-at_install')
class TestOBR006ImportWizard(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR006',
            'code': 'OBR006-TEST',
        })
        self.wizard_defaults = {
            'project_id': self.project.id,
            'foreman_user_id': self.env.user.id,
            'need_date': '2026-04-01',
            'priority': '1',
            'file_name': 'test.xlsx',
        }

    def _create_wizard(self, extra=None):
        vals = dict(self.wizard_defaults)
        if extra:
            vals.update(extra)
        return self.env['object.request.import.wizard'].create(vals)

    # ------------------------------------------------------------------
    # Тесты создания wizard
    # ------------------------------------------------------------------

    def test_wizard_created_with_defaults(self):
        """Wizard создаётся с дефолтными значениями."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        self.assertEqual(wizard.validation_state, 'not_checked')
        self.assertEqual(wizard.line_preview_count, 0)
        self.assertEqual(wizard.problem_line_count, 0)

    # ------------------------------------------------------------------
    # Тесты action_validate
    # ------------------------------------------------------------------

    def test_validate_valid_file(self):
        """Корректный файл: validation_state='valid', строки создаются."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1, VALID_ROW_2])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'valid')
        self.assertEqual(wizard.line_preview_count, 2)
        self.assertEqual(wizard.problem_line_count, 0)
        self.assertEqual(len(wizard.preview_line_ids), 2)

    def test_validate_line_fields_parsed_correctly(self):
        """Поля строки правильно извлекаются из Excel."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        line = wizard.preview_line_ids[0]
        self.assertEqual(line.supplier_article, 'ART-001')
        self.assertEqual(line.name_raw, 'Цемент М500')
        self.assertEqual(line.uom_raw, 'мешок')
        self.assertAlmostEqual(line.qty, 10.0)
        self.assertAlmostEqual(line.price, 500.0)
        self.assertEqual(line.supplier_raw, 'ООО Стройснаб')
        self.assertFalse(line.has_error)

    def test_validate_skips_empty_rows(self):
        """Полностью пустые строки пропускаются при парсинге."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1, [None]*8, VALID_ROW_2])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.line_preview_count, 2)

    def test_validate_marks_row_with_empty_name_as_error(self):
        """Строка с пустым наименованием помечается как ошибочная."""
        bad_row = [3, 'ART-003', '', 'шт', 5, 100.0, '', '']
        file_b64 = _make_xlsx([VALID_HEADER, bad_row])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'valid')
        self.assertEqual(wizard.problem_line_count, 1)
        line = wizard.preview_line_ids[0]
        self.assertTrue(line.has_error)
        self.assertIn('наименование', line.error_message.lower())

    def test_validate_marks_row_with_zero_qty_as_error(self):
        """Строка с нулевым количеством помечается как ошибочная."""
        bad_row = [3, 'ART-003', 'Кирпич', 'шт', 0, 100.0, '', '']
        file_b64 = _make_xlsx([VALID_HEADER, bad_row])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'valid')
        line = wizard.preview_line_ids[0]
        self.assertTrue(line.has_error)

    def test_validate_file_too_few_columns_returns_invalid(self):
        """Файл с менее 5 колонок → validation_state='invalid'."""
        file_b64 = _make_xlsx([['A', 'B'], ['1', '2']])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'invalid')
        self.assertEqual(wizard.line_preview_count, 0)

    def test_validate_only_header_no_data_rows(self):
        """Файл только с заголовком → validation_state='invalid'."""
        file_b64 = _make_xlsx([VALID_HEADER])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'invalid')

    def test_validate_clears_previous_preview_on_revalidation(self):
        """Повторная валидация очищает предыдущие строки предпросмотра."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1, VALID_ROW_2])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        self.assertEqual(wizard.line_preview_count, 2)

        file_b64_2 = _make_xlsx([VALID_HEADER, VALID_ROW_1])
        wizard.write({'file': file_b64_2})
        wizard.action_validate()
        self.assertEqual(wizard.line_preview_count, 1)

    # ------------------------------------------------------------------
    # Тест action_import (заглушка OBR-007)
    # ------------------------------------------------------------------

    def test_action_import_without_validation_raises_user_error(self):
        """action_import без предварительной валидации поднимает UserError."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        # validation_state остаётся 'not_checked' — импорт должен упасть
        with self.assertRaises(UserError):
            wizard.action_import()

    # ------------------------------------------------------------------
    # Тест source_row_no
    # ------------------------------------------------------------------

    def test_source_row_no_is_correct(self):
        """source_row_no соответствует реальному номеру строки в Excel."""
        file_b64 = _make_xlsx([VALID_HEADER, VALID_ROW_1, VALID_ROW_2])
        if file_b64 is None:
            self.skipTest('openpyxl не установлен')
        wizard = self._create_wizard({'file': file_b64})
        wizard.action_validate()
        lines = wizard.preview_line_ids.sorted('sequence')
        self.assertEqual(lines[0].source_row_no, 2)
        self.assertEqual(lines[1].source_row_no, 3)
