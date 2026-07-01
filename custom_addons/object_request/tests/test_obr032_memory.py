"""OBR-032: Память сопоставлений."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestObr032Memory(TransactionCase):

    def setUp(self):
        super().setUp()
        self.vendor = self.env['res.partner'].create(
            {'name': 'Vendor OBR032', 'supplier_rank': 1}
        )
        self.product = self.env['product.product'].create(
            {'name': 'Кран OBR032 Ду15', 'type': 'consu'}
        )
        self.supply_manager = self.env['res.users'].create({
            'name': 'Supply OBR032',
            'login': 'supply_obr032',
            'group_ids': [
                (4, self.env.ref('object_request.group_supply_manager').id),
                (4, self.env.ref('purchase.group_purchase_user').id),
            ],
        })

    def _create_request_with_line(self):
        """Создать тестовое требование с одной строкой."""
        project = self.env['object.request.project'].search([], limit=1)
        if not project:
            project = self.env['object.request.project'].create(
                {'name': 'Test OBR032'}
            )
        request = self.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': self.env.uid,
            'need_date': '2026-07-01',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Кран шаровой Ду15',
            'supplier_article': 'KSH-15',
            'qty_requested': 1.0,
            'matching_required': True,
            'ai_suggested_product_id': self.product.id,
            'ai_match_confidence': 0.95,
            'ai_match_reason': 'Тест OBR032',
            'preferred_vendor_id': self.vendor.id,
        })
        return request, line

    def test_accept_and_remember_creates_memory_record(self):
        """Подтверждение AI-кандидата создаёт запись в памяти."""
        _, line = self._create_request_with_line()
        line.with_user(
            self.supply_manager
        ).action_accept_and_remember_ai_candidate()

        Memory = self.env['object.request.matching.memory']
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        record = Memory.search([('name_normalized', '=', name_norm)])
        self.assertTrue(record)
        self.assertEqual(record.product_id, self.product)

    def test_manual_remember_creates_memory_record(self):
        """Ручная кнопка Запомнить пишет в память по имени строки."""
        _, line = self._create_request_with_line()
        line.write({
            'product_id': self.product.id,
            'matching_required': False,
        })

        line.with_user(self.supply_manager).action_remember_matching()

        Memory = self.env['object.request.matching.memory']
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        record = Memory.search([('name_normalized', '=', name_norm)])
        self.assertTrue(record)
        self.assertEqual(record.product_id, self.product)

    def test_manual_remember_without_supplier_article_is_memory_only(self):
        """Запомнить доступно и без артикула: создаётся только память."""
        _, line = self._create_request_with_line()
        line.write({
            'supplier_article': False,
            'product_id': self.product.id,
            'matching_required': False,
        })

        action = line.with_user(self.supply_manager).action_remember_matching()

        Memory = self.env['object.request.matching.memory']
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        record = Memory.search([('name_normalized', '=', name_norm)])
        self.assertTrue(record)
        self.assertEqual(record.product_id, self.product)
        self.assertIn('Supplierinfo: создано 0', action['params']['message'])
        self.assertIn('пропущено 1', action['params']['message'])

    def test_memory_stores_technical_designation_first(self):
        """Память сохраняет technical_designation перед supplier_article."""
        _, line = self._create_request_with_line()
        line.technical_designation = 'L=0.13'

        line.with_user(
            self.supply_manager
        ).action_accept_and_remember_ai_candidate()

        Memory = self.env['object.request.matching.memory']
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        record = Memory.search([('name_normalized', '=', name_norm)])
        self.assertEqual(record.designation_normalized, 'L=0.13')

    def test_memory_used_before_llm_in_build_candidates(self):
        """Если есть запись в памяти, LLM не вызывается."""
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        self.env['object.request.matching.memory'].create({
            'name_normalized': name_norm,
            'product_id': self.product.id,
            'confidence': 1.0,
        })
        service = self.env['object.request.matching.candidate.service']
        result = service.build_candidates('Кран шаровой Ду15', 'KSH-15')

        self.assertTrue(result['candidates'])
        self.assertEqual(result['candidates'][0]['source'], 'memory')
        self.assertFalse(result['can_call_llm'])

    def test_memory_prefers_exact_designation_match(self):
        """При совпадении имени память учитывает конкретное обозначение."""
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Узел OBR032 общий')
        product_a = self.env['product.product'].create({
            'name': 'Память OBR032 обозначение A',
            'type': 'consu',
        })
        product_b = self.env['product.product'].create({
            'name': 'Память OBR032 обозначение B',
            'type': 'consu',
        })
        Memory = self.env['object.request.matching.memory']
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': 'DES-B',
            'product_id': product_b.id,
            'confidence': 0.8,
        })
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': 'DES-A',
            'product_id': product_a.id,
            'confidence': 1.0,
        })

        service = self.env['object.request.matching.candidate.service']
        result = service.build_candidates(
            'Узел OBR032 общий',
            '',
            technical_designation='DES-B',
        )

        self.assertEqual(result['candidates'][0]['source'], 'memory')
        self.assertEqual(result['candidates'][0]['product_id'], product_b.id)

    def test_memory_designation_fallback_uses_empty_only(self):
        """Fallback не берёт запись с другим обозначением."""
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Узел OBR032 fallback')
        wrong_product = self.env['product.product'].create({
            'name': 'Память OBR032 wrong designation',
            'type': 'consu',
        })
        legacy_product = self.env['product.product'].create({
            'name': 'Память OBR032 empty designation',
            'type': 'consu',
        })
        Memory = self.env['object.request.matching.memory']
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': 'OTHER-DES',
            'product_id': wrong_product.id,
            'confidence': 1.0,
        })
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': False,
            'product_id': legacy_product.id,
            'confidence': 0.8,
        })

        service = self.env['object.request.matching.candidate.service']
        result = service.build_candidates(
            'Узел OBR032 fallback',
            '',
            technical_designation='MISSING-DES',
        )

        self.assertEqual(result['candidates'][0]['source'], 'memory')
        self.assertEqual(
            result['candidates'][0]['product_id'],
            legacy_product.id,
        )

    def test_memory_not_saved_for_short_names(self):
        """Короткие имена и L=... не сохраняются в память."""
        from odoo.addons.object_request.models.object_request_line import (
            ObjectRequestLine,
        )
        self.assertFalse(ObjectRequestLine._should_save_to_memory_str('ab'))
        self.assertFalse(ObjectRequestLine._should_save_to_memory_str('L=5'))
        self.assertFalse(ObjectRequestLine._should_save_to_memory_str(''))
        self.assertTrue(
            ObjectRequestLine._should_save_to_memory_str('кран шаровой')
        )

    def test_memory_duplicate_does_not_error(self):
        """Повторное сохранение одной пары не вызывает исключения."""
        _, line = self._create_request_with_line()
        line.with_user(
            self.supply_manager
        ).action_accept_and_remember_ai_candidate()
        line2 = self.env['object.request.line'].create({
            'request_id': line.request_id.id,
            'name_raw': 'Кран шаровой Ду15',
            'supplier_article': 'KSH-15',
            'qty_requested': 1.0,
            'matching_required': True,
            'ai_suggested_product_id': self.product.id,
            'ai_match_confidence': 0.95,
            'ai_match_reason': 'Тест OBR032 дубль',
            'preferred_vendor_id': self.vendor.id,
        })
        line2.with_user(
            self.supply_manager
        ).action_accept_and_remember_ai_candidate()

    def test_inactive_memory_not_used(self):
        """Запись с active=False не используется."""
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str('Кран шаровой Ду15')
        self.env['object.request.matching.memory'].create({
            'name_normalized': name_norm,
            'product_id': self.product.id,
            'confidence': 1.0,
            'active': False,
        })
        service = self.env['object.request.matching.candidate.service']
        result = service.build_candidates('Кран шаровой Ду15', '')

        sources = [c['source'] for c in result['candidates']]
        self.assertNotIn('memory', sources)
