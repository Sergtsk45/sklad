from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestOBR021Purchase(TransactionCase):
    """OBR-021: Создание черновиков закупки (RFQ / Purchase Order)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.project = cls.env["object.request.project"].create(
            {
                "name": "Тест закупки",
            }
        )
        cls.user = cls.env.ref("base.user_admin")

        cls.vendor1 = cls.env["res.partner"].create(
            {
                "name": "Поставщик Альфа",
                "supplier_rank": 1,
            }
        )
        cls.vendor2 = cls.env["res.partner"].create(
            {
                "name": "Поставщик Бета",
                "supplier_rank": 1,
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Продукт А",
                "type": "consu",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Продукт Б",
                "type": "consu",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Продукт В",
                "type": "consu",
            }
        )

    def _create_request(self):
        return self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.user.id,
                "need_date": "2026-05-01",
            }
        )

    def _add_line(self, request, product, qty_to_buy, vendor=None):
        vals = {
            "request_id": request.id,
            "name_raw": product.name,
            "product_id": product.id,
            "uom_id": product.uom_id.id,
            "qty_requested": qty_to_buy,
            "qty_to_buy": qty_to_buy,
        }
        if vendor:
            vals["preferred_vendor_id"] = vendor.id
        return self.env["object.request.line"].create(vals)

    def _open_wizard(self, request):
        return (
            self.env["object.request.purchase.wizard"]
            .with_context(
                default_request_id=request.id,
            )
            .create({"request_id": request.id})
        )

    # --- Тесты ---

    def test_create_po_single_vendor(self):
        """Для одного поставщика создаётся один PO."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0, self.vendor1)
        self._add_line(request, self.product2, 3.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "purchase.order")
        self.assertEqual(result["view_mode"], "form")

        po = self.env["purchase.order"].browse(result["res_id"])
        self.assertEqual(po.partner_id, self.vendor1)
        self.assertEqual(len(po.order_line), 2)
        self.assertTrue(po.is_object_request_purchase)
        self.assertEqual(po.object_request_project_id, self.project)
        self.assertEqual(
            po.picking_type_id, self.project.warehouse_id.in_type_id
        )

    def test_object_request_po_report_filename(self):
        """PDF закупки по требованию получает имя передаточной ведомости."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        expected = (
            f"Передаточная ведомость №{po.name} "
            f"{self.project.warehouse_id.display_name}"
        )
        for report_xmlid in (
            "purchase.action_report_purchase_order",
            "purchase.report_purchase_quotation",
        ):
            report = self.env.ref(report_xmlid)
            filename = safe_eval(
                report.print_report_name,
                {"object": po},
            )
            self.assertEqual(filename, expected)

    def test_regular_po_report_filename_uses_receipt_warehouse(self):
        """PDF обычной закупки тоже получает склад из типа поступления."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor1.id,
                "picking_type_id": self.project.warehouse_id.in_type_id.id,
            }
        )

        expected = (
            f"Передаточная ведомость №{po.name} "
            f"{self.project.warehouse_id.display_name}"
        )
        report = self.env.ref("purchase.action_report_purchase_order")
        filename = safe_eval(
            report.print_report_name,
            {"object": po},
        )
        self.assertFalse(po.is_object_request_purchase)
        self.assertEqual(filename, expected)

    def test_create_po_grouped_by_vendor(self):
        """Строки группируются по поставщику — создаётся PO на каждого."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0, self.vendor1)
        self._add_line(request, self.product2, 3.0, self.vendor2)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "purchase.order")
        self.assertEqual(result["view_mode"], "list,form")

        pos = self.env["purchase.order"].search(
            [("id", "in", result["domain"][0][2])]
        )
        self.assertEqual(len(pos), 2)
        vendors = pos.mapped("partner_id")
        self.assertIn(self.vendor1, vendors)
        self.assertIn(self.vendor2, vendors)

    def test_po_links_back_to_request(self):
        """purchase_order_ids в шапке документа ссылается на созданные PO."""
        request = self._create_request()
        self._add_line(request, self.product1, 4.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        self.assertIn(po, request.purchase_order_ids)
        self.assertEqual(request.purchase_order_count, 1)

    def test_line_links_to_po(self):
        """Строка документа получает ссылки на PO и POL."""
        request = self._create_request()
        line = self._add_line(request, self.product1, 6.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        line.invalidate_recordset()
        self.assertEqual(line.purchase_order_id, po)
        self.assertTrue(line.purchase_order_line_id)
        self.assertEqual(line.purchase_order_line_id.order_id, po)

    def test_lines_without_vendor_marked(self):
        """Строки без поставщика помечаются manual_vendor_required=True."""
        request = self._create_request()
        line_with = self._add_line(request, self.product1, 5.0, self.vendor1)
        line_no_vendor = self._add_line(request, self.product2, 3.0)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        wizard.action_create_purchase()

        line_no_vendor.invalidate_recordset()
        self.assertTrue(line_no_vendor.manual_vendor_required)
        # Строка с поставщиком не тронута
        line_with.invalidate_recordset()
        self.assertFalse(line_with.manual_vendor_required)

    def test_no_lines_raises_error(self):
        """Если нет строк к закупке — UserError."""
        request = self._create_request()
        # Создаём строку без qty_to_buy, чтобы можно было поставить in_progress
        self._add_line(request, self.product1, 5.0)
        request.write({"state": "in_progress"})

        # Wizard без строк в line_ids
        wizard = self.env["object.request.purchase.wizard"].create(
            {
                "request_id": request.id,
                "line_ids": [],
            }
        )
        with self.assertRaises(UserError):
            wizard.action_create_purchase()

    def test_all_lines_without_vendor_raises_error(self):
        """Если все строки без поставщика — UserError."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0)  # нет поставщика
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        with self.assertRaises(UserError):
            wizard.action_create_purchase()

    def test_po_order_line_qty(self):
        """Количество в строке PO соответствует qty_to_buy."""
        request = self._create_request()
        self._add_line(request, self.product1, 7.5, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        pol = po.order_line[0]
        self.assertAlmostEqual(pol.product_qty, 7.5)
        self.assertEqual(pol.product_id, self.product1)

    def test_po_origin_is_request_name(self):
        """Поле origin в PO совпадает с номером документа требования."""
        request = self._create_request()
        self._add_line(request, self.product1, 2.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        self.assertEqual(po.origin, request.name)

    def test_purchase_order_reverse_link(self):
        """purchase.order.object_request_ids содержит требование."""
        request = self._create_request()
        self._add_line(request, self.product1, 3.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])

        self.assertIn(request, po.object_request_ids)
        self.assertEqual(po.object_request_count, 1)

    def test_purchase_wizard_defaults_project_receipt_type(self):
        """Wizard по умолчанию принимает на склад объекта."""
        request = self._create_request()
        self._add_line(request, self.product1, 3.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)

        self.assertEqual(
            wizard.picking_type_id,
            self.project.warehouse_id.in_type_id,
        )

    def test_purchase_wizard_fallback_receipt_type_without_project_warehouse(
        self,
    ):
        """Если у объекта нет склада, wizard требует явный тип приёмки."""
        request = self._create_request()
        self._add_line(request, self.product1, 3.0, self.vendor1)
        self.project.write({"warehouse_id": False})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)

        self.assertEqual(wizard.picking_type_id.code, "incoming")

    def test_default_get_prefills_lines(self):
        """default_get заполняет line_ids строками с qty_to_buy > 0."""
        request = self._create_request()
        self._add_line(request, self.product1, 4.0, self.vendor1)
        line_no_buy = self._add_line(request, self.product2, 5.0, self.vendor2)
        line_no_buy.write({"qty_to_buy": 0.0})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].product_id, self.product1)

    def test_open_purchase_wizard_action(self):
        """action_open_purchase_wizard возвращает действие wizard."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0, self.vendor1)
        request.write({"state": "in_progress"})

        action = request.action_open_purchase_wizard()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "object.request.purchase.wizard")

    def test_open_purchase_wizard_no_lines_error(self):
        """action_open_purchase_wizard без строк к закупке — UserError."""
        request = self._create_request()
        # Строка без qty_to_buy — не считается строкой к закупке
        line = self._add_line(request, self.product1, 5.0, self.vendor1)
        line.write({"qty_to_buy": 0.0})
        request.write({"state": "in_progress"})

        with self.assertRaises(UserError):
            request.action_open_purchase_wizard()

    def test_multiple_vendors_multiple_po_lines(self):
        """Два поставщика, три строки — правильное кол-во строк в PO."""
        request = self._create_request()
        self._add_line(request, self.product1, 1.0, self.vendor1)
        self._add_line(request, self.product2, 2.0, self.vendor1)
        self._add_line(request, self.product3, 3.0, self.vendor2)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()

        pos = self.env["purchase.order"].search(
            [("id", "in", result["domain"][0][2])]
        )
        po_vendor1 = pos.filtered(lambda p: p.partner_id == self.vendor1)
        po_vendor2 = pos.filtered(lambda p: p.partner_id == self.vendor2)

        self.assertEqual(len(po_vendor1.order_line), 2)
        self.assertEqual(len(po_vendor2.order_line), 1)
