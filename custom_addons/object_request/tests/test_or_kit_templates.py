"""Шаблоны типовых узлов: сохранение, варианты Ду, создание требования."""
from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRequestKitTemplates(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env['product.product']
        names = {
            'z80': 'Задвижка KIT Ду80', 'z100': 'Задвижка KIT Ду100',
            'bolt': 'Болт KIT М16×70', 'pipe80': 'Труба KIT 89×3,5',
            'pipe100': 'Труба KIT 108×4', 'gofra': 'Гофра KIT Ду20',
        }
        cls.p = {
            key: Product.create({'name': name, 'type': 'consu'})
            for key, name in names.items()
        }
        cls.vendor = cls.env['res.partner'].create(
            {'name': 'Vendor KIT', 'supplier_rank': 1}
        )
        cls.project = cls.env['object.request.project'].create(
            {'name': 'Объект KIT'}
        )
        cls.req80 = cls._request([
            (10, 'Задвижка Ду80', 'z80', 3.0),
            (20, 'болт оцинк. М16х70', 'bolt', 100.0),
            (30, 'труба ст. Ду 80мм', 'pipe80', 3.0),
        ])
        cls.req100 = cls._request([
            (10, 'Задвижка Ду100', 'z100', 3.0),
            (20, 'болт оцинк. М16х70', 'bolt', 100.0),
            (30, 'труба ст. Ду 100мм', 'pipe100', 3.0),
            (40, 'гофра ПВХ д20', 'gofra', 10.0),
        ])
        cls.kit = cls._save(cls.req80, 'new', 80, kit_name='ВУ KIT')
        cls._save(cls.req100, 'variant', 100, kit=cls.kit)

    @classmethod
    def _request(cls, rows):
        return cls.env['object.request'].create({
            'project_id': cls.project.id,
            'foreman_user_id': cls.env.uid,
            'need_date': fields.Date.today(),
            'line_ids': [(0, 0, {
                'sequence': seq,
                'name_raw': name,
                'product_id': cls.p[key].id,
                'qty_requested': qty,
                'preferred_vendor_id': cls.vendor.id,
            }) for seq, name, key, qty in rows],
        })

    @classmethod
    def _save(cls, request, mode, size, kit_name=None, kit=None):
        wizard = cls.env['object.request.kit.save.wizard'].create({
            'request_id': request.id,
            'mode': mode,
            'kit_name': kit_name,
            'kit_id': kit.id if kit else False,
            'size': size,
        })
        action = wizard.action_save()
        return cls.env['object.request.kit'].browse(action['res_id'])

    def _create(self, size, multiplier=1, user=None):
        Wizard = self.env['object.request.kit.create.wizard']
        if user:
            Wizard = Wizard.with_user(user)
        wizard = Wizard.create({
            'kit_id': self.kit.id,
            'size': size,
            'multiplier': multiplier,
            'project_id': self.project.id,
            'need_date': fields.Date.today(),
        })
        action = wizard.action_create()
        return self.env['object.request'].browse(action['res_id'])

    def _products(self, request):
        lines = request.line_ids.sorted('sequence')
        return [line.product_id for line in lines]

    def test_kit_sizes_and_dependent_lines(self):
        self.assertEqual(self.kit._get_sizes(), [80, 100])
        lines = {line.sequence: line for line in self.kit.line_ids}
        self.assertTrue(lines[10].size_dependent)
        self.assertFalse(lines[20].size_dependent)
        self.assertTrue(lines[40].base_skip)

    def test_create_for_variant_size(self):
        request = self._create(100)
        p = self.p
        self.assertEqual(
            self._products(request),
            [p['z100'], p['bolt'], p['pipe100'], p['gofra']],
        )
        self.assertEqual(
            set(request.line_ids.mapped('matching_source')), {'kit'}
        )
        self.assertFalse(any(request.line_ids.mapped('matching_required')))

    def test_create_for_base_size_skips_extra_line(self):
        request = self._create(80)
        p = self.p
        self.assertEqual(
            self._products(request), [p['z80'], p['bolt'], p['pipe80']]
        )

    def test_unknown_size_leaves_dependent_lines_unmatched(self):
        request = self._create(65)
        unmatched = request.line_ids.filtered('matching_required')
        self.assertEqual(len(unmatched), 3)
        bolt = request.line_ids.filtered(lambda line: line.sequence == 20)
        self.assertEqual(bolt.product_id, self.p['bolt'])
        self.assertIn('ВУ KIT', unmatched[0].matching_note)

    def test_multiplier_scales_quantities(self):
        request = self._create(100, multiplier=2)
        bolt = request.line_ids.filtered(lambda line: line.sequence == 20)
        self.assertEqual(bolt.qty_requested, 200.0)

    def test_created_request_is_clean_draft(self):
        request = self._create(100)
        self.assertEqual(request.state, 'draft')
        self.assertFalse(request.line_ids.mapped('purchase_order_id'))
        self.assertEqual(
            set(request.line_ids.mapped('line_state')), {'ready'}
        )

    def test_third_size_backfills_previous_sizes(self):
        req65 = self._request([
            (10, 'Задвижка Ду65', 'z80', 3.0),
            (20, 'болт оцинк. М16х70', 'bolt', 50.0),
            (30, 'труба ст. Ду 65мм', 'pipe80', 5.0),
        ])
        self._save(req65, 'variant', 65, kit=self.kit)
        bolt100 = self._create(100).line_ids.filtered(
            lambda line: line.sequence == 20
        )
        bolt65 = self._create(65).line_ids.filtered(
            lambda line: line.sequence == 20
        )
        self.assertEqual((bolt100.qty_requested, bolt65.qty_requested),
                         (100.0, 50.0))

    def test_base_size_cannot_be_added_as_variant(self):
        with self.assertRaises(UserError):
            self._save(self.req100, 'variant', 80, kit=self.kit)

    def test_foreman_creates_request_but_cannot_edit_kit(self):
        foreman = self.env['res.users'].create({
            'name': 'Foreman KIT',
            'login': 'foreman_kit',
            'group_ids': [
                (4, self.env.ref('base.group_user').id),
                (4, self.env.ref('object_request.group_foreman').id),
            ],
        })
        request = self._create(100, user=foreman)
        self.assertEqual(len(request.line_ids), 4)
        with self.assertRaises(AccessError):
            self.kit.with_user(foreman).write({'name': 'Изменено'})
