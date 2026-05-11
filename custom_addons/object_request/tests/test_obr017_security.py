from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo.tests import tagged


def _make_user(env, name, login, group):
    """Вспомогательная функция создания пользователя с указанной группой модуля."""
    return env['res.users'].create({
        'name': name,
        'login': login,
        'group_ids': [(4, group.id)],
    })


@tagged('post_install', '-at_install')
class TestACLForeman(TransactionCase):
    """Тесты прав доступа прораба (group_foreman).

    Прораб:
    - создаёт/читает/редактирует объекты object.request и object.request.line
    - не может удалять документы и строки
    - видит только свои документы (record rule: foreman_user_id = user.id)
    - использует wizard импорта
    """

    def setUp(self):
        super().setUp()
        self.foreman_group = self.env.ref('object_request.group_foreman')
        self.foreman = _make_user(
            self.env, 'Прораб ACL', 'foreman_obr017@test.com',
            self.foreman_group,
        )
        self.project = self.env['object.request.project'].create({
            'name': 'Объект ACL прораб',
        })
        self.product = self.env['product.product'].create({
            'name': 'Товар ACL', 'type': 'consu',
        })

    # --- Создание ---

    def test_foreman_can_create_request(self):
        """Прораб может создать документ на себя."""
        env = self.env(user=self.foreman)
        request = env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        self.assertTrue(request.id)
        self.assertEqual(request.state, 'draft')

    def test_foreman_can_create_line(self):
        """Прораб может создать строку в своём документе."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        env = self.env(user=self.foreman)
        line = env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Материал прораба',
            'qty_requested': 5.0,
        })
        self.assertTrue(line.id)

    # --- Record rule: прораб видит только свои документы ---

    def test_foreman_sees_own_request(self):
        """Прораб видит документ, где foreman_user_id = он сам."""
        own = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        env = self.env(user=self.foreman)
        found = env['object.request'].search([('id', '=', own.id)])
        self.assertEqual(len(found), 1)

    def test_foreman_cannot_see_others_request(self):
        """Прораб не видит документ другого прораба."""
        other = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.env.user.id,  # admin
            'need_date': '2026-04-01',
        })
        env = self.env(user=self.foreman)
        found = env['object.request'].search([('id', '=', other.id)])
        self.assertEqual(len(found), 0)

    # --- Запрет удаления ---

    def test_foreman_cannot_delete_request(self):
        """Прораб не может удалять документы (perm_unlink=0)."""
        own = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        env = self.env(user=self.foreman)
        with self.assertRaises(AccessError):
            env['object.request'].browse(own.id).unlink()

    def test_foreman_cannot_delete_line(self):
        """Прораб не может удалять строки документа (perm_unlink=0)."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Строка',
            'qty_requested': 3.0,
        })
        env = self.env(user=self.foreman)
        with self.assertRaises(AccessError):
            env['object.request.line'].browse(line.id).unlink()

    # --- Wizard импорта ---

    def test_foreman_can_use_import_wizard(self):
        """Прораб имеет доступ к wizard импорта (perm_create=1)."""
        env = self.env(user=self.foreman)
        wizard = env['object.request.import.wizard'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
            'priority': '1',
        })
        self.assertTrue(wizard.id)


@tagged('post_install', '-at_install')
class TestACLSupplyManager(TransactionCase):
    """Тесты прав доступа снабженца (group_supply_manager).

    Снабженец:
    - полный CRUD на object.request и object.request.line
    - видит все документы (нет record rule)
    - может назначать товар и поставщика строкам
    """

    def setUp(self):
        super().setUp()
        self.supply_group = self.env.ref('object_request.group_supply_manager')
        self.supply = _make_user(
            self.env, 'Снабженец ACL', 'supply_obr017@test.com',
            self.supply_group,
        )
        self.project = self.env['object.request.project'].create({
            'name': 'Объект ACL снабженец',
        })
        self.product = self.env['product.product'].create({
            'name': 'Товар снабженца', 'type': 'consu',
        })

    def _make_request(self, foreman_id=None):
        return self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': foreman_id or self.env.user.id,
            'need_date': '2026-04-01',
        })

    # --- Видимость всех документов ---

    def test_supply_sees_all_requests(self):
        """Снабженец видит документы любого прораба."""
        req1 = self._make_request(foreman_id=self.env.user.id)
        req2 = self._make_request(foreman_id=self.supply.id)
        env = self.env(user=self.supply)
        found = env['object.request'].search([
            ('id', 'in', [req1.id, req2.id])
        ])
        self.assertIn(req1.id, found.ids)
        self.assertIn(req2.id, found.ids)

    # --- Полный CRUD ---

    def test_supply_can_create_request(self):
        """Снабженец может создавать документы."""
        env = self.env(user=self.supply)
        request = env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.supply.id,
            'need_date': '2026-04-01',
        })
        self.assertTrue(request.id)

    def test_supply_can_delete_request(self):
        """Снабженец может удалять документы (perm_unlink=1)."""
        request = self._make_request()
        req_id = request.id
        env = self.env(user=self.supply)
        env['object.request'].browse(req_id).unlink()
        self.assertFalse(self.env['object.request'].browse(req_id).exists())

    def test_supply_can_delete_line(self):
        """Снабженец может удалять строки (perm_unlink=1)."""
        request = self._make_request()
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Строка снабженца',
            'qty_requested': 10.0,
        })
        line_id = line.id
        env = self.env(user=self.supply)
        env['object.request.line'].browse(line_id).unlink()
        self.assertFalse(self.env['object.request.line'].browse(line_id).exists())

    # --- Редактирование строк ---

    def test_supply_can_assign_product_to_line(self):
        """Снабженец может назначить товар на строку (ручное сопоставление)."""
        request = self._make_request()
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Несопоставленный материал',
            'qty_requested': 10.0,
            'matching_required': True,
        })
        env = self.env(user=self.supply)
        env['object.request.line'].browse(line.id).write({
            'product_id': self.product.id,
            'matching_required': False,
        })
        line.invalidate_recordset()
        self.assertEqual(line.product_id.id, self.product.id)
        self.assertFalse(line.matching_required)

    def test_supply_can_set_qty_to_issue(self):
        """Снабженец может указывать количество к выдаче."""
        request = self._make_request()
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Материал',
            'qty_requested': 10.0,
            'product_id': self.product.id,
        })
        env = self.env(user=self.supply)
        env['object.request.line'].browse(line.id).write({'qty_to_issue': 6.0})
        line.invalidate_recordset()
        self.assertAlmostEqual(line.qty_to_issue, 6.0)

    def test_supply_can_use_import_wizard(self):
        """Снабженец имеет доступ к wizard импорта."""
        env = self.env(user=self.supply)
        wizard = env['object.request.import.wizard'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.supply.id,
            'need_date': '2026-04-01',
            'priority': '1',
        })
        self.assertTrue(wizard.id)


@tagged('post_install', '-at_install')
class TestACLStorekeeper(TransactionCase):
    """Тесты прав доступа кладовщика (group_storekeeper).

    Кладовщик:
    - читает и редактирует только документы в статусе 'in_progress' (record rule)
    - не может создавать документы (perm_create=0)
    - не может создавать строки (perm_create=0)
    - не может использовать wizard импорта (perm=0)
    """

    def setUp(self):
        super().setUp()
        self.store_group = self.env.ref('object_request.group_storekeeper')
        self.storekeeper = _make_user(
            self.env, 'Кладовщик ACL', 'store_obr017@test.com',
            self.store_group,
        )
        self.project = self.env['object.request.project'].create({
            'name': 'Объект ACL кладовщик',
        })
        self.product = self.env['product.product'].create({
            'name': 'Товар кладовщика', 'type': 'consu',
        })

    def _make_in_progress_request(self):
        """Создаёт документ со строкой и переводит в 'in_progress'."""
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.env.user.id,
            'need_date': '2026-04-01',
        })
        self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Материал',
            'qty_requested': 10.0,
            'product_id': self.product.id,
            'matching_required': False,
        })
        request.action_in_progress()
        return request

    # --- Record rule: только документы in_progress ---

    def test_storekeeper_sees_in_progress_request(self):
        """Кладовщик видит документы в статусе 'in_progress'."""
        request = self._make_in_progress_request()
        env = self.env(user=self.storekeeper)
        found = env['object.request'].search([('id', '=', request.id)])
        self.assertEqual(len(found), 1)

    def test_storekeeper_cannot_see_draft_request(self):
        """Кладовщик не видит документы в статусе 'draft'."""
        draft = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.env.user.id,
            'need_date': '2026-04-01',
        })
        env = self.env(user=self.storekeeper)
        found = env['object.request'].search([('id', '=', draft.id)])
        self.assertEqual(len(found), 0)

    # --- Запрет создания ---

    def test_storekeeper_cannot_create_request(self):
        """Кладовщик не может создавать документы (perm_create=0)."""
        env = self.env(user=self.storekeeper)
        with self.assertRaises(AccessError):
            env['object.request'].create({
                'project_id': self.project.id,
                'foreman_user_id': self.storekeeper.id,
                'need_date': '2026-04-01',
            })

    def test_storekeeper_cannot_create_line(self):
        """Кладовщик не может создавать строки документа (perm_create=0)."""
        request = self._make_in_progress_request()
        env = self.env(user=self.storekeeper)
        with self.assertRaises(AccessError):
            env['object.request.line'].create({
                'request_id': request.id,
                'name_raw': 'Строка кладовщика',
                'qty_requested': 2.0,
            })

    # --- Чтение документов ---

    def test_storekeeper_can_read_in_progress_request(self):
        """Кладовщик может читать поля документа в работе."""
        request = self._make_in_progress_request()
        env = self.env(user=self.storekeeper)
        rec = env['object.request'].browse(request.id)
        self.assertEqual(rec.state, 'in_progress')
        self.assertEqual(rec.project_id.id, self.project.id)

    # --- Запрет wizard импорта ---

    def test_storekeeper_cannot_use_import_wizard(self):
        """Кладовщик не имеет доступа к wizard импорта (perm=0)."""
        env = self.env(user=self.storekeeper)
        with self.assertRaises(AccessError):
            env['object.request.import.wizard'].create({
                'project_id': self.project.id,
                'foreman_user_id': self.storekeeper.id,
                'need_date': '2026-04-01',
                'priority': '1',
            })
