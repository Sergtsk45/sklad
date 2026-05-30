# @file: test_e2e_nf504_invoice_to_po.py
# @description: E2E-тест «НФ-504 → PO draft» (AIA-060).
#   Фикстура счёта → InvoiceContextHelper → create_product_draft (1 позиция)
#   → create_purchase_order_draft (14 строк) → state=draft, сумма 72 096,22.
# @dependencies: invoice_context_helper, invoice_extraction_store, action_tools
# @created: 2026-05-30

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.action_tools.executor import (
    ToolExecutor,
    ToolRateLimiter,
)
from odoo.addons.ai_assistant.services.invoice_context_helper import (
    InvoiceContextHelper,
)
from odoo.addons.ai_assistant.services.invoice_extraction_store import (
    InvoiceExtractionStore,
)


# ── НФ-504: данные позиций (name, unit, qty, price_wo_vat) ──────────────

_NF504_ITEM_DATA = [
    ("Переход 89-45 ст.", "шт", 16.0, 239.59),
    ("Переход 108-57 ст.", "шт", 8.0, 279.66),
    ("Отвод 89 ст. 90°", "шт", 20.0, 179.49),
    ("Отвод 108 ст. 90°", "шт", 10.0, 239.59),
    ("Тройник 89×45×3,5 ГОСТ 17376-2001", "шт", 4.0, 599.00),
    ("Тройник 76х3,5-45х3-20 ГОСТ 17376-2001", "шт", 6.0, 549.00),
    ("Муфта 89 ст.", "шт", 30.0, 119.80),
    ("Муфта 108 ст.", "шт", 15.0, 139.75),
    ("Заглушка 89 ст.", "шт", 10.0, 99.50),
    ("Заглушка 108 ст.", "шт", 5.0, 119.80),
    ("Труба ст. 89×3,5 ГОСТ 8732", "м", 50.0, 350.00),
    ("Труба ст. 108×4 ГОСТ 8732", "м", 30.0, 480.00),
    ("Фланец 89 ст. Ду80 ГОСТ 12820", "шт", 12.0, 289.00),
    # item 14 — not pre-created → create_product_draft
    ("Фланец 108 ст. Ду100 ГОСТ 12820", "шт", 8.0, 349.00),
]

# Нормализованный dict счёта — без реального файла/HTTP
_NF504_NORMALIZED_INVOICE = {
    "document_type": "supplier_invoice",
    "invoice_number": "НФ-504",
    "invoice_date": "2026-05-20",
    "supplier": {
        "name": "ИП Татаринов Вадим Владимирович",
        "inn": "280110406377",
        "kpp": "",
        "address": "",
        "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
    },
    "buyer": {
        "name": "ООО ТЕПЛОСЕРВИС-КОМПЛЕКТ",
        "inn": "2801131520",
        "kpp": "280101001",
        "address": "",
    },
    "items": [
        {
            "line_no": idx + 1,
            "name": name,
            "unit": unit,
            "qty": qty,
            "price": price,
            "amount_wo_vat": round(qty * price, 2),
            "vat_rate": "20%",
            "vat_amount": round(qty * price * 0.2, 2),
            "amount_w_vat": round(qty * price * 1.2, 2),
            "article": "",
            "discount": "",
        }
        for idx, (name, unit, qty, price) in enumerate(_NF504_ITEM_DATA)
    ],
    "totals": {
        "total_wo_vat": 60191.67,
        "vat_total": 12437.14,
        "total_w_vat": 72096.22,
    },
    "pages": 1,
    "warnings": [],
}

# Индекс последней позиции, которая НЕ имеет pre-created продукта
_MISSING_ITEM_IDX = 13  # "Фланец 108 ст. Ду100 ГОСТ 12820"


@tagged('post_install', '-at_install')
class TestNF504InvoiceToPODraft(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.store = InvoiceExtractionStore()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'ИП Татаринов Вадим Владимирович',
            'vat': '280110406377',
            'supplier_rank': 1,
        })
        cls.warehouse = cls._get_or_create_obm4_warehouse()
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.uom_meter = cls.env.ref('uom.product_uom_meter')
        cls.category = cls.env['product.category'].create({
            'name': 'AIA-060 трубопроводная арматура',
        })
        cls.products = cls._create_pre_existing_products()
        cls.supply_user = cls._create_supply_user()

    @classmethod
    def _get_or_create_obm4_warehouse(cls):
        wh = cls.env['stock.warehouse'].search(
            [('code', '=', 'ОбМ-4')], limit=1,
        )
        if wh:
            return wh
        return cls.env['stock.warehouse'].create({
            'name': 'Б. Хмельницкого, 112',
            'code': 'ОбМ-4',
        })

    @classmethod
    def _create_pre_existing_products(cls):
        """Создать 13 из 14 позиций (последняя — намеренно отсутствует)."""
        products = {}
        for idx, (name, unit, _qty, _price) in enumerate(_NF504_ITEM_DATA):
            if idx == _MISSING_ITEM_IDX:
                continue
            uom = (
                cls.uom_meter
                if unit == 'м'
                else cls.uom_unit
            )
            products[idx] = cls.env['product.product'].create({
                'name': name,
                'is_storable': True,
                'purchase_ok': True,
                'categ_id': cls.category.id,
                'uom_id': uom.id,
            })
        return products

    @classmethod
    def _create_supply_user(cls):
        groups = [
            cls.env.ref('base.group_user').id,
            cls.env.ref(
                'ai_assistant.group_ai_assistant_supply'
            ).id,
            cls.env.ref('product.group_product_manager').id,
        ]
        return cls.env['res.users'].create({
            'name': 'aia060_supply',
            'login': 'aia060_supply',
            'email': 'aia060_supply@example.invalid',
            'group_ids': [(6, 0, groups)],
        })

    # ── helpers ──────────────────────────────────────────────────────────────

    def _make_executor(self):
        return ToolExecutor(
            self.env(user=self.supply_user),
            rate_limiter=ToolRateLimiter(),
        )

    def _invoice_context(self):
        helper = InvoiceContextHelper(self.env, self.store)
        token = self.store.put(
            self.env.ref('base.user_admin').id,
            _NF504_NORMALIZED_INVOICE,
        )
        return helper.fetch_context(
            self.env.ref('base.user_admin').id,
            token,
        )

    # ── test ─────────────────────────────────────────────────────────────────

    def test_nf504_invoice_to_po_draft(self):
        # ── Step 1: context helper — поставщик найден, итого 72 096,22 ──────
        context = self._invoice_context()
        self.assertIsNotNone(context)
        self.assertEqual(context['invoice_number'], 'НФ-504')
        self.assertEqual(
            context['totals'].get('total_w_vat'),
            72096.22,
        )
        partner = context['partner']
        self.assertEqual(partner['status'], 'matched')
        self.assertEqual(partner['partner_id'], self.supplier.id)
        self.assertEqual(len(context['items']), 14)

        # ── Step 2: item 14 — не найдена → create_product_draft ──────────────
        missing_item = context['items'][_MISSING_ITEM_IDX]
        self.assertEqual(
            missing_item['product']['needs_create_product_draft'],
            True,
        )
        executor = self._make_executor()
        draft_result = executor.execute(
            'create_product_draft',
            {
                'name': missing_item['name'],
                'uom_id': self.uom_unit.id,
                'categ_id': self.category.id,
                'purchase_ok': True,
            },
        )
        self.assertTrue(draft_result['success'])
        new_product_id = draft_result['result']['product_id']
        self.assertTrue(new_product_id)

        # ── Step 3: build PO lines (13 pre-existing + 1 new) ─────────────────
        po_lines = []
        for idx, (name, unit, qty, price) in enumerate(_NF504_ITEM_DATA):
            uom = self.uom_meter if unit == 'м' else self.uom_unit
            if idx == _MISSING_ITEM_IDX:
                product_id = new_product_id
            else:
                product_id = self.products[idx].id
            po_lines.append({
                'product_id': product_id,
                'product_qty': qty,
                'product_uom': uom.id,
                'price_unit': price,
                'name': name,
            })

        # ── Step 4: create_purchase_order_draft ──────────────────────────────
        po_result = executor.execute(
            'create_purchase_order_draft',
            {
                'partner_id': self.supplier.id,
                'picking_type_id': self.warehouse.in_type_id.id,
                'origin': 'НФ-504/AIA-060',
                'partner_ref': 'НФ-504',
                'date_planned': '2026-06-01 08:00:00',
                'lines': po_lines,
            },
        )
        self.assertTrue(
            po_result['success'],
            msg='create_purchase_order_draft failed: %s' % po_result,
        )

        # ── Step 5: assertions ────────────────────────────────────────
        po = self.env['purchase.order'].browse(
            po_result['result']['po_id']
        )
        self.assertEqual(po.state, 'draft')
        self.assertEqual(
            len(po.order_line),
            14,
            msg='Ожидалось 14 строк PO (по числу позиций НФ-504)',
        )
        self.assertEqual(po.partner_ref, 'НФ-504')
        self.assertEqual(po.origin, 'НФ-504/AIA-060')

        # Chatter содержит пометку AI Assistant
        body = '\n'.join(po.message_ids.mapped('body'))
        self.assertIn('AI Assistant', body)
