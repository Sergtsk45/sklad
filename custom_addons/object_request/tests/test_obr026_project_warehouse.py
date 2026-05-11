from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestObjectRequestProjectWarehouse(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Объект OBR-026',
        })
        self.product = self.env['product.product'].create({
            'name': 'Материал OBR-026',
            'type': 'consu',
            'is_storable': True,
        })
        self.foreman = self.env.user
        self.supply_user = self._create_supply_user()

    def _create_supply_user(self):
        supply_group = self.env.ref('object_request.group_supply_manager')
        user_group = self.env.ref('base.group_user')
        user = self.env['res.users'].create({
            'name': 'Снабженец OBR026',
            'login': 'supply_obr026',
            'email': 'supply_obr026@example.com',
        })
        user.group_ids = [(6, 0, [user_group.id, supply_group.id])]
        return user

    def test_project_creates_warehouse(self):
        self.assertTrue(self.project.warehouse_id)
        self.assertEqual(
            self.project.warehouse_id.name,
            f'{self.project.name} склад',
        )
        self.assertEqual(self.project.warehouse_id.code, self.project.code)

    def test_supply_manager_cannot_rename_project(self):
        with self.assertRaises(UserError):
            self.project.with_user(self.supply_user).write({'name': 'Новый объект'})

    def test_admin_rename_updates_warehouse(self):
        self.project.write({'name': 'Обновлённый объект'})
        self.assertEqual(
            self.project.warehouse_id.name,
            'Обновлённый объект склад',
        )

    def test_archive_syncs_warehouse(self):
        self.project.write({'active': False})
        self.project.invalidate_recordset(['active'])
        self.assertFalse(self.project.warehouse_id.active)
        self.project.write({'active': True})
        self.project.invalidate_recordset(['active'])
        self.assertTrue(self.project.warehouse_id.active)

    def test_unlink_blocked_with_requests(self):
        self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': fields.Date.today(),
        })
        with self.assertRaises(UserError):
            self.project.unlink()

    def test_unlink_blocked_with_stock(self):
        location = self.project.warehouse_id.lot_stock_id
        quant = self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product.id,
            'location_id': location.id,
            'inventory_quantity': 2.0,
        })
        quant.action_apply_inventory()
        with self.assertRaises(UserError):
            self.project.unlink()
