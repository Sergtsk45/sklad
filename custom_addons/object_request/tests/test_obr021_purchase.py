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

    def test_purchase_blocks_unresolved_manual_review_line(self):
        """Закупка не создаётся, если строка требует проверки номенклатуры."""
        request = self._create_request()
        line = self._add_line(request, self.product1, 5.0, self.vendor1)
        line.write(
            {
                "matching_required": True,
                "matching_state": "manual_review",
            }
        )
        request.write({"state": "in_progress"})
        wizard = self._open_wizard(request)

        with self.assertRaisesRegex(UserError, "нерешённые предупреждения"):
            wizard.action_create_purchase()

    def test_purchase_allows_manual_review_after_foreman_product_choice(self):
        """Ручной выбор товара прорабом снимает блокировку закупки."""
        request = self._create_request()
        line = self._add_line(request, self.product1, 5.0, self.vendor1)
        line.write(
            {
                "matching_state": "manual_review",
                "matching_source": "manual",
                "matching_required": False,
                "matching_note": (
                    "Требует проверки: найдено несколько сильных кандидатов."
                ),
            }
        )
        request.write({"state": "in_progress"})
        wizard = self._open_wizard(request)

        result = wizard.action_create_purchase()

        po = self.env["purchase.order"].browse(result["res_id"])
        self.assertEqual(po.partner_id, self.vendor1)
        self.assertEqual(len(po.order_line), 1)

    def test_object_request_po_report_filename(self):
        """PDF закупки по требованию получает имя передаточной ведомости."""
        request = self._create_request()
        self._add_line(request, self.product1, 5.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])
        po.partner_ref = "INV-OBR021-001"

        expected = (
            f"Передаточная ведомость №{po.partner_ref} "
            f"{self.project.warehouse_id.display_name}"
        )
        for report_xmlid in (
            "purchase.action_report_purchase_order",
            "purchase.report_purchase_quotation",
        ):
            for lang in (False, "ru_RU"):
                report = (
                    self.env.ref(report_xmlid).with_context(lang=lang)
                    if lang
                    else self.env.ref(report_xmlid)
                )
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
                "partner_ref": "680",
            }
        )

        expected = (
            f"Передаточная ведомость №{po.partner_ref} "
            f"{self.project.warehouse_id.display_name}"
        )
        report = self.env.ref(
            "purchase.action_report_purchase_order"
        ).with_context(lang="ru_RU")
        filename = safe_eval(report.print_report_name, {"object": po})
        self.assertFalse(po.is_object_request_purchase)
        self.assertEqual(filename, expected)

    def test_po_report_filename_falls_back_to_order_number(self):
        """Если номер счёта поставщика пустой, используется номер заказа."""
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
        self.assertEqual(po._get_transfer_report_filename(), expected)

    def test_purchase_report_renders_compact_template(self):
        """Кнопка печати закупки использует компактный шаблон."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor1.id,
                "picking_type_id": self.project.warehouse_id.in_type_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": "Компактная строка отчёта",
                            "product_qty": 2.0,
                            "product_uom_id": self.product1.uom_id.id,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )

        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "purchase.action_report_purchase_order",
            [po.id],
        )
        html = html.decode() if isinstance(html, bytes) else html
        report = self.env.ref("purchase.action_report_purchase_order")
        self.assertEqual(report.paperformat_id.margin_top, 0)
        self.assertIn("o_object_request_compact_purchase_report", html)
        self.assertIn("o_object_request_compact_meta", html)
        self.assertIn("o_object_request_compact_lines", html)
        self.assertIn("line-height: 1.265", html)
        self.assertIn("сдал:", html)
        self.assertIn("принял:", html)

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

    def test_validated_receipt_updates_request_qty_issued(self):
        """Проведённый приход PO отражается в колонке 'Выдано'."""
        product = self.env["product.product"].create(
            {
                "name": "Продукт receipt OBR021",
                "type": "consu",
                "is_storable": True,
            }
        )
        request = self._create_request()
        line = self._add_line(request, product, 4.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])
        po.button_confirm()
        picking = po.picking_ids.filtered(
            lambda item: item.picking_type_id.code == "incoming"
        )[:1]

        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.with_context(skip_backorder=True).button_validate()

        line.invalidate_recordset()
        self.assertEqual(line.qty_issued, 4.0)
        self.assertEqual(request.qty_total_issued, 4.0)

    def test_receipt_qty_issued_is_added_to_internal_issue_qty(self):
        """Выдано суммирует внутреннюю выдачу и закупочный приход."""
        product = self.env["product.product"].create(
            {
                "name": "Продукт mixed receipt OBR021",
                "type": "consu",
                "is_storable": True,
            }
        )
        request = self._create_request()
        line = self._add_line(request, product, 4.0, self.vendor1)
        line.write({"qty_requested": 10.0, "qty_to_issue": 6.0})
        request.write({"state": "in_progress"})
        warehouse = request._get_issue_warehouses()[:1]
        self.env["object.request.line.stock"].with_context(
            auto_stock_distribution=True,
        ).create(
            {
                "line_id": line.id,
                "warehouse_id": warehouse.id,
                "qty_on_hand": 6.0,
                "qty_to_issue": 6.0,
            }
        )
        issue_wizard = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(default_request_id=request.id)
            .create({})
        )
        issue_wizard.action_create_issues()
        issue_picking = line.stock_ids.picking_id
        self.env["stock.quant"]._update_available_quantity(
            product,
            warehouse.lot_stock_id,
            6.0,
        )
        issue_picking.action_confirm()
        issue_picking.action_assign()
        for move_line in issue_picking.move_line_ids:
            move_line.quantity = move_line.move_id.product_uom_qty
        issue_picking.with_context(skip_backorder=True).button_validate()

        purchase_wizard = self._open_wizard(request)
        result = purchase_wizard.action_create_purchase()
        po = self.env["purchase.order"].browse(result["res_id"])
        po.button_confirm()
        picking = po.picking_ids.filtered(
            lambda item: item.picking_type_id.code == "incoming"
        )[:1]
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.with_context(skip_backorder=True).button_validate()

        line.invalidate_recordset()
        self.assertEqual(line.qty_issued, 10.0)

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

    def test_purchase_guard_blocks_similar_product_with_issue_stock(self):
        """PO не создаётся молча, если похожий товар есть на складе выдачи."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-GUARD",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-GUARD",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-GUARD"})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "object.request.purchase.wizard")
        self.assertEqual(result["res_id"], wizard.id)
        self.assertTrue(wizard.show_stock_guard_override)
        self.assertFalse(wizard.confirm_stock_guard_override)
        self.assertIn("Закупка остановлена", wizard.stock_guard_warning_text)
        self.assertIn(
            stock_product.display_name,
            wizard.stock_guard_warning_text,
        )
        self.assertFalse(request.purchase_order_ids)

    def test_purchase_guard_override_creates_po_and_logs_note(self):
        """Явное подтверждение создаёт PO и пишет решение в chatter."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-OVERRIDE",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-OVERRIDE",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-OVERRIDE"})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        wizard.confirm_stock_guard_override = True
        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "purchase.order")
        messages = request.message_ids.mapped("body")
        self.assertTrue(
            any(stock_product.display_name in body for body in messages)
        )

    def test_purchase_guard_replace_candidate_moves_line_to_issue(self):
        """Замена в guard переводит строку на складскую выдачу."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-REPLACE",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-REPLACE",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-REPLACE"})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        wizard.action_create_purchase()
        result = wizard.action_replace_with_stock_candidate()

        self.assertEqual(result["res_model"], "object.request.purchase.wizard")
        self.assertEqual(line.product_id, stock_product)
        self.assertEqual(line.procurement_mode, "issue")
        self.assertAlmostEqual(line.qty_to_issue, 5.0)
        self.assertAlmostEqual(line.qty_to_buy, 0.0)
        self.assertFalse(line.stock_match_warning)
        self.assertFalse(request.purchase_order_ids)
        self.assertIn("Перед закупкой выбран", line.matching_note)

    def test_purchase_guard_without_similar_stock_creates_po(self):
        """Строка без похожего остатка не блокирует создание закупки."""
        request = self._create_request()
        product = self.env["product.product"].create(
            {
                "name": "Непохожий товар OBR021-NOGUARD",
                "type": "consu",
                "is_storable": True,
            }
        )
        request.write(
            {"issue_warehouse_ids": [(6, 0, [self.project.warehouse_id.id])]}
        )
        self._add_line(request, product, 5.0, self.vendor1)
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "purchase.order")
        self.assertFalse(wizard.show_stock_guard_override)
        self.assertTrue(request.purchase_order_ids)

    def test_stock_match_warning_marks_problem_line(self):
        """Проверка номенклатуры помечает строку проблемной."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-MVP2",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-MVP2",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-MVP2"})

        request.action_refresh_stock_match_warnings()

        line.invalidate_recordset()
        request.invalidate_recordset()
        self.assertTrue(line.stock_match_warning)
        self.assertEqual(line.stock_match_candidate_id, stock_product)
        self.assertAlmostEqual(line.stock_match_candidate_qty, 201.0)
        self.assertEqual(request.line_problem_count, 1)
        action = request.action_open_problem_lines()
        self.assertIn(("stock_match_warning", "=", True), action["domain"])
        self.assertEqual(
            action["context"].get("object_request_column_layout_scope"),
            "request_problem_lines",
        )

    def test_select_stock_match_candidate_applies_product(self):
        """Кнопка выбора складского кандидата записывает его в строку."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-SELECT",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-SELECT",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-SELECT"})
        line.action_refresh_stock_match_warning()

        action = line.action_select_stock_match_candidate()

        line.invalidate_recordset()
        self.assertEqual(line.product_id, stock_product)
        self.assertFalse(line.stock_match_warning)
        self.assertIn("Выбран складской кандидат", line.matching_note)
        self.assertEqual(action["params"]["type"], "success")

    def test_product_onchange_refreshes_stock_match_warning(self):
        """Ручной выбор товара сразу показывает складского кандидата."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-ONCHANGE",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-ONCHANGE",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-ONCHANGE",
                "qty_requested": 5.0,
                "matching_required": True,
            }
        )

        line.product_id = wrong_product
        line._onchange_product_id()

        self.assertTrue(line.stock_match_warning)
        self.assertEqual(line.stock_match_candidate_id, stock_product)
        self.assertIn("Есть остаток на Ос.ск: 201", line.matching_note)

    def test_prepare_ai_candidates_writes_stock_matching_note(self):
        """AI shortlist пишет stock-note в matching_note."""
        request = self._create_request()
        no_stock = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-NOTE",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-NOTE",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-NOTE",
                "qty_requested": 5.0,
                "matching_required": True,
            }
        )

        request.action_prepare_ai_candidates()

        line.invalidate_recordset()
        self.assertIn(no_stock, line.ai_candidate_product_ids)
        self.assertEqual(line.ai_suggested_product_id, stock_product)
        self.assertIn("Есть остаток на Ос.ск: 201", line.matching_note)
        self.assertLess(line.ai_match_confidence, 0.9)

    def test_existing_po_diagnostic_opens_stock_match_lines(self):
        """Диагностика созданной PO находит похожий складской товар."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец ст. Ду65 1.0МПа кованый OBR021-DIAG",
                "type": "consu",
                "is_storable": True,
            }
        )
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-DIAG",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-DIAG"})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        wizard.confirm_stock_guard_override = True
        wizard.action_create_purchase()

        action = request.action_check_purchase_stock_matches()

        line.invalidate_recordset()
        self.assertTrue(line.stock_match_warning)
        self.assertEqual(action["res_model"], "object.request.line")
        self.assertEqual(action["domain"], [("id", "in", line.ids)])
        self.assertEqual(
            action["context"].get("object_request_column_layout_scope"),
            "request_po_diagnostics",
        )
        messages = request.message_ids.mapped("body")
        self.assertTrue(
            any("Проверка закупок нашла строки" in body for body in messages)
        )

    def test_existing_po_diagnostic_flags_purchase_line_product_mismatch(self):
        """Диагностика PO ловит расхождение товара PO и строки требования."""
        request = self._create_request()
        wrong_product = self.env["product.product"].create(
            {
                "name": "Фланец 65-10 кованый OBR021-MISMATCH-OLD",
                "type": "consu",
                "is_storable": True,
            }
        )
        correct_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR021-MISMATCH-NEW",
                "type": "consu",
                "is_storable": True,
            }
        )
        warehouse = self.project.warehouse_id
        request.write({"issue_warehouse_ids": [(6, 0, [warehouse.id])]})
        self.env["stock.quant"]._update_available_quantity(
            correct_product,
            warehouse.lot_stock_id,
            201.0,
        )
        line = self._add_line(request, wrong_product, 5.0, self.vendor1)
        line.write({"name_raw": "Фланец ст. Ду 65мм 1,0МПа OBR021-MISMATCH"})
        request.write({"state": "in_progress"})

        wizard = self._open_wizard(request)
        wizard.confirm_stock_guard_override = True
        wizard.action_create_purchase()
        line.write({"product_id": correct_product.id})

        action = request.action_check_purchase_stock_matches()

        line.invalidate_recordset()
        self.assertTrue(line.stock_match_warning)
        self.assertIn(
            "отличается от товара требования",
            line.stock_match_warning_text,
        )
        self.assertEqual(line.stock_match_candidate_id, correct_product)
        self.assertEqual(action["res_model"], "object.request.line")
        self.assertEqual(action["domain"], [("id", "in", line.ids)])
