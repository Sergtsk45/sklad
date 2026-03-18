"""OBR-007: Тесты парсинга, автосопоставления и создания строк из Excel."""
import base64
import io

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


def _make_excel_bytes(rows):
    """Создаёт минимальный xlsx-файл в памяти из списка строк."""
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
    return buf.getvalue()


@tagged('post_install', '-at_install')
class TestExcelParser(TransactionCase):
    """Тесты сервиса object.request.excel.parser."""

    def setUp(self):
        super().setUp()
        self.parser = self.env['object.request.excel.parser']

    def test_normalize_uom_variants(self):
        cases = [
            ('шт', 'шт.'), ('шт.', 'шт.'),
            ('Штука', 'шт.'), ('штук', 'шт.'),
            ('кг', 'кг.'), ('кг.', 'кг.'), ('Килограмм', 'кг.'),
            ('м', 'м.'), ('М.', 'м.'), ('метр', 'м.'),
            ('л', 'л.'), ('Литр', 'л.'),
            ('уп', 'уп.'), ('упаковка', 'уп.'),
            ('м2', 'м²'), ('кв.м', 'м²'),
            ('м3', 'м³'), ('куб.м', 'м³'),
            ('тонна', 'тонна'),  # неизвестное — без изменений
            ('', ''),
        ]
        for raw, expected in cases:
            result = self.parser.normalize_uom(raw)
            self.assertEqual(
                result, expected,
                f'normalize_uom({raw!r}) → {result!r}, ожидалось {expected!r}',
            )

    def test_normalize_str(self):
        self.assertEqual(self.parser.normalize_str('  текст  '), 'текст')
        self.assertEqual(
            self.parser.normalize_str('два  пробела'), 'два пробела',
        )
        self.assertEqual(self.parser.normalize_str(''), '')
        self.assertIsNone(self.parser.normalize_str(None) or None)

    def test_match_product_by_article_empty(self):
        result = self.parser.match_product_by_article('')
        self.assertFalse(result)

    def test_match_product_by_article_none_string(self):
        result = self.parser.match_product_by_article('none')
        self.assertFalse(result)

    def test_match_product_by_name_empty(self):
        result = self.parser.match_product_by_name('')
        self.assertFalse(result)

    def test_match_vendor_by_name_empty(self):
        result = self.parser.match_vendor_by_name('')
        self.assertFalse(result)

    def test_match_row_no_data(self):
        result = self.parser.match_row('', 'НесуществующийТовар12345', '')
        self.assertIsNone(result['product'] or None)
        self.assertTrue(result['matching_required'])
        self.assertTrue(result['manual_vendor_required'])


@tagged('post_install', '-at_install')
class TestImportWizardOBR007(TransactionCase):
    """Тесты wizard импорта: автосопоставление и создание строк."""

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-007',
            'code': 'OBR007-TEST',
        })
        self.wizard_model = self.env['object.request.import.wizard']

    def _make_wizard(self, rows):
        xlsx = _make_excel_bytes(rows)
        if xlsx is None:
            self.skipTest('openpyxl не установлен')
        return self.wizard_model.create({
            'file': base64.b64encode(xlsx),
            'file_name': 'test.xlsx',
            'project_id': self.project.id,
            'foreman_user_id': self.env.uid,
            'need_date': '2026-04-01',
            'priority': '1',
        })

    def test_action_import_requires_validation(self):
        """action_import() без валидации → UserError."""
        wizard = self._make_wizard([
            ['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во'],
            [1, 'ART-1', 'Гвоздь 100мм', 'шт', 100],
        ])
        with self.assertRaises(UserError):
            wizard.action_import()

    def test_action_validate_then_import_creates_document(self):
        """Полный цикл validate → import создаёт документ и строки."""
        wizard = self._make_wizard([
            ['№', 'Артикул', 'Наим.', 'Ед.', 'Кол', 'Цена', 'Ком.', 'Пост.'],
            [1, '', 'Уникальный_товар_OBR007_A', 'шт', 5, 100.0, '', ''],
            [2, '', 'Уникальный_товар_OBR007_B', 'кг', 10, 50.0, '', ''],
        ])
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'valid')
        self.assertEqual(wizard.line_preview_count, 2)

        result = wizard.action_import()
        self.assertEqual(result['res_model'], 'object.request')
        self.assertEqual(result['view_mode'], 'form')
        self.assertEqual(result['target'], 'current')

        request = self.env['object.request'].browse(result['res_id'])
        self.assertTrue(request.exists())
        self.assertEqual(request.project_id, self.project)
        self.assertEqual(len(request.line_ids), 2)

    def test_import_sets_source_file_name(self):
        """Имя файла и дата импорта сохраняются в документе."""
        wizard = self._make_wizard([
            ['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во'],
            [1, '', 'Товар для проверки имени файла', 'шт', 3],
        ])
        wizard.action_validate()
        result = wizard.action_import()
        request = self.env['object.request'].browse(result['res_id'])
        self.assertEqual(request.source_file_name, 'test.xlsx')
        self.assertTrue(request.imported_at)

    def test_import_unmatched_lines_flagged(self):
        """Несопоставленные строки имеют matching_required=True."""
        wizard = self._make_wizard([
            ['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во'],
            [1, '', 'Совсем_Неизвестный_Товар_XYZ_12345', 'шт', 1],
        ])
        wizard.action_validate()
        preview = wizard.preview_line_ids
        self.assertEqual(len(preview), 1)
        self.assertEqual(preview.match_status, 'unmatched')
        self.assertTrue(preview.matching_required)

        result = wizard.action_import()
        request = self.env['object.request'].browse(result['res_id'])
        line = request.line_ids
        self.assertEqual(len(line), 1)
        self.assertTrue(line.matching_required)
        self.assertFalse(line.product_id)

    def test_import_line_fields_copied_correctly(self):
        """Все поля строки (qty, price, comment) корректно переносятся."""
        wizard = self._make_wizard([
            ['№', 'Арт.', 'Наим.', 'Ед.', 'Кол.', 'Цена', 'Ком.', 'Пост.'],
            [1, 'SUPPART-42', 'Тест OBR007', 'кг.', 15, 200.0, 'тест', ''],
        ])
        wizard.action_validate()
        result = wizard.action_import()
        request = self.env['object.request'].browse(result['res_id'])
        line = request.line_ids[0]
        self.assertAlmostEqual(line.qty_requested, 15.0)
        self.assertAlmostEqual(line.price_raw, 200.0)
        self.assertEqual(line.comment, 'тест')
        self.assertEqual(line.name_raw, 'Тест OBR007')

    def test_import_uom_normalization(self):
        """UOM нормализуется при парсинге (штука → шт.)."""
        wizard = self._make_wizard([
            ['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во'],
            [1, '', 'Товар с UOM', 'штука', 7],
        ])
        wizard.action_validate()
        preview = wizard.preview_line_ids
        self.assertEqual(preview.uom_raw, 'шт.')

    def test_import_empty_file_raises(self):
        """Пустой xlsx (только заголовок) → validation_state=invalid."""
        xlsx = _make_excel_bytes(
            [['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во']]
        )
        if xlsx is None:
            self.skipTest('openpyxl не установлен')
        wizard = self.wizard_model.create({
            'file': base64.b64encode(xlsx),
            'file_name': 'empty.xlsx',
            'project_id': self.project.id,
            'foreman_user_id': self.env.uid,
            'need_date': '2026-04-01',
            'priority': '1',
        })
        wizard.action_validate()
        self.assertEqual(wizard.validation_state, 'invalid')

    def test_import_no_preview_raises(self):
        """action_import() без preview_line_ids → UserError."""
        xlsx = _make_excel_bytes([
            ['№', 'Артикул', 'Наименование', 'Ед.', 'Кол-во'],
            [1, '', 'Товар', 'шт', 5],
        ])
        if xlsx is None:
            self.skipTest('openpyxl не установлен')
        wizard = self.wizard_model.create({
            'file': base64.b64encode(xlsx),
            'file_name': 'test2.xlsx',
            'project_id': self.project.id,
            'foreman_user_id': self.env.uid,
            'need_date': '2026-04-01',
            'priority': '1',
            'validation_state': 'valid',
        })
        with self.assertRaises(UserError):
            wizard.action_import()
