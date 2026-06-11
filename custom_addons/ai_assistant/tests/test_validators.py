from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.action_tools.validators import (
    infer_is_company,
    normalize_vat,
    validate_partner_create_args,
    validate_partner_is_supplier,
    validate_picking_type_for_purchase,
    validate_picking_type_is_object,
    validate_product_is_storable,
    validate_state_in,
    validate_uom_is_meter,
    validate_vat_unique,
    validate_warehouse_code_pattern,
)


class DummyRecord:
    def __init__(self, state):
        self.state = state


@tagged('post_install', '-at_install')
class TestActionToolValidators(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.object_warehouse = cls.env['stock.warehouse'].create({
            'name': 'O777 Validator Test',
            'code': 'O777',
        })
        cls.object_project = cls.env['object.request.project'].create({
            'name': 'Validator Object',
            'code': 'O777',
            'warehouse_id': cls.object_warehouse.id,
        })
        cls.default_warehouse = cls.env.ref('stock.warehouse0')
        cls.pipe_category = cls.env['product.category'].create({
            'name': 'Трубы validator',
        })
        cls.stock_product = cls.env['product.product'].create({
            'name': 'Труба складируемая',
            'is_storable': True,
            'categ_id': cls.pipe_category.id,
            'uom_id': cls.env.ref('uom.product_uom_meter').id,
        })
        cls.consumable_product = cls.env['product.product'].create({
            'name': 'Услуга не склад',
            'is_storable': False,
        })
        cls.unit_pipe = cls.env['product.product'].create({
            'name': 'Труба в штуках',
            'is_storable': True,
            'categ_id': cls.pipe_category.id,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Поставщик validator',
            'vat': '1435000360',
            'supplier_rank': 1,
        })
        cls.customer = cls.env['res.partner'].create({
            'name': 'Не поставщик validator',
            'supplier_rank': 0,
        })

    def test_validate_picking_type_for_purchase_happy_object(self):
        validate_picking_type_for_purchase(
            self.env, self.object_warehouse.in_type_id.id
        )

    def test_validate_picking_type_for_purchase_happy_default(self):
        validate_picking_type_for_purchase(
            self.env, self.default_warehouse.in_type_id.id
        )

    def test_validate_picking_type_is_object_happy(self):
        validate_picking_type_is_object(
            self.env, self.object_warehouse.in_type_id.id
        )

    def test_validate_picking_type_is_object_rejects_non_object(self):
        with self.assertRaises(ValidationError):
            validate_picking_type_is_object(
                self.env, self.default_warehouse.in_type_id.id
            )

    def test_validate_product_is_storable_happy(self):
        validate_product_is_storable(self.env, self.stock_product.id)

    def test_validate_product_is_storable_rejects_consumable(self):
        with self.assertRaises(ValidationError):
            validate_product_is_storable(self.env, self.consumable_product.id)

    def test_validate_state_in_happy(self):
        validate_state_in(DummyRecord('draft'), {'draft', 'in_progress'})

    def test_validate_state_in_rejects_forbidden_state(self):
        with self.assertRaises(ValidationError):
            validate_state_in(DummyRecord('done'), {'draft', 'in_progress'})

    def test_validate_warehouse_code_pattern_happy(self):
        validate_warehouse_code_pattern(self.env, self.object_warehouse.id)

    def test_validate_warehouse_code_pattern_rejects_non_object(self):
        with self.assertRaises(ValidationError):
            validate_warehouse_code_pattern(
                self.env,
                self.default_warehouse.id,
            )

    def test_validate_partner_is_supplier_happy(self):
        validate_partner_is_supplier(self.env, self.supplier.id)

    def test_validate_partner_is_supplier_rejects_customer(self):
        with self.assertRaises(ValidationError):
            validate_partner_is_supplier(self.env, self.customer.id)

    def test_normalize_vat_keeps_only_digits(self):
        self.assertEqual(normalize_vat('ИНН 7727 123-456'), '7727123456')

    def test_validate_vat_unique_returns_existing_id(self):
        self.assertEqual(
            validate_vat_unique(self.env, '1435 000360'),
            self.supplier.id,
        )

    def test_validate_vat_unique_returns_none_for_new_vat(self):
        self.assertFalse(validate_vat_unique(self.env, '7727123456'))

    def test_infer_is_company_for_ooo(self):
        self.assertTrue(infer_is_company('ООО "Ромашка"'))

    def test_infer_is_company_for_ip(self):
        self.assertFalse(infer_is_company('ИП Иванов Иван Иванович'))

    def test_validate_partner_create_args_rejects_empty_vat(self):
        errors = validate_partner_create_args({
            'name': 'ООО Ромашка',
            'vat': '',
        })
        self.assertTrue(errors)
        self.assertIn('ИНН', errors[0])

    def test_validate_partner_create_args_rejects_bad_vat_length(self):
        errors = validate_partner_create_args({
            'name': 'ООО Ромашка',
            'vat': '123',
        })
        self.assertTrue(errors)
        self.assertIn('10 или 12', errors[0])

    def test_validate_partner_create_args_accepts_ip_vat(self):
        errors = validate_partner_create_args({
            'name': 'ИП Иванов Иван Иванович',
            'vat': '143500036001',
        })
        self.assertEqual(errors, [])

    def test_validate_uom_is_meter_happy(self):
        warning = validate_uom_is_meter(self.env, self.stock_product.id)
        self.assertEqual(warning, '')

    def test_validate_uom_is_meter_warns_for_pipe_non_meter(self):
        warning = validate_uom_is_meter(self.env, self.unit_pipe.id)
        self.assertIn('метр', warning)
        self.assertIn('TD-002', warning)
