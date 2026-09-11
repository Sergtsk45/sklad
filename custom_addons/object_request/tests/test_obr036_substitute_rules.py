from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObr036SubstituteRules(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["object.request.project"].create(
            {"name": "OBR036 аналоги"}
        )
        cls.user = cls.env.ref("base.user_admin")
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Поставщик OBR036", "supplier_rank": 1}
        )

    def _product(self, name):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
            }
        )

    def _request(self):
        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.user.id,
                "need_date": "2026-07-06",
            }
        )
        request.write(
            {
                "issue_warehouse_ids": [
                    (6, 0, [self.project.warehouse_id.id])
                ]
            }
        )
        return request

    def _line(self, request, product, name=None, qty=5.0):
        return self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": name or product.name,
                "product_id": product.id,
                "uom_id": product.uom_id.id,
                "qty_requested": qty,
                "qty_to_buy": qty,
                "preferred_vendor_id": self.vendor.id,
            }
        )

    def _rule(self, product, substitute, direction="one_way"):
        return self.env["object.request.product.substitute.rule"].create(
            {
                "product_id": product.id,
                "substitute_product_id": substitute.id,
                "direction": direction,
                "reason": "Технически допустимый аналог OBR036",
            }
        )

    def _put_stock(self, product, qty=20.0):
        self.env["stock.quant"]._update_available_quantity(
            product,
            self.project.warehouse_id.lot_stock_id,
            qty,
        )

    def test_one_way_rule_works_only_allowed_direction(self):
        source = self._product("Фланец ст. Ду65 1.0МПа OBR036-ONE")
        substitute = self._product("Фланец DN65 PN16 OBR036-ONE")
        self._rule(source, substitute, "one_way")
        self._put_stock(substitute, 11.0)

        request = self._request()
        line = self._line(request, source)
        line.action_refresh_stock_match_warning()
        self.assertEqual(line.substitute_product_id, substitute)
        self.assertEqual(line.allowed_substitute_ids, substitute)

        reverse_source = self._product("Фланец DN65 PN16 OBR036-ONE-R A")
        reverse_substitute = self._product("Фланец DN65 PN16 OBR036-ONE-R B")
        self._rule(reverse_source, reverse_substitute, "one_way")
        self._put_stock(reverse_source, 12.0)
        reverse = self._line(request, reverse_substitute)
        reverse.action_refresh_stock_match_warning()
        self.assertFalse(reverse.substitute_product_id)

    def test_two_way_rule_works_both_directions(self):
        product_a = self._product("Фланец DN65 PN16 OBR036-TWO A")
        product_b = self._product("Фланец DN65 PN16 OBR036-TWO B")
        self._rule(product_a, product_b, "two_way")
        self._put_stock(product_b, 9.0)

        request = self._request()
        line_a = self._line(request, product_a)
        line_a.action_refresh_stock_match_warning()
        self.assertEqual(line_a.substitute_product_id, product_b)

        product_c = self._product("Фланец DN65 PN16 OBR036-TWO C")
        product_d = self._product("Фланец DN65 PN16 OBR036-TWO D")
        self._rule(product_c, product_d, "two_way")
        self._put_stock(product_c, 7.0)
        line_d = self._line(request, product_d)
        line_d.action_refresh_stock_match_warning()

        self.assertEqual(line_d.substitute_product_id, product_c)

    def test_blocked_policy_rule_cannot_be_created(self):
        source = self._product("Фланец DN65 PN16 OBR036-BLOCK")
        lower = self._product("Фланец DN65 PN10 OBR036-BLOCK")

        with self.assertRaises(ValidationError):
            self._rule(source, lower, "one_way")

    def test_substitute_with_stock_is_shown_separately_and_applied(self):
        source = self._product("Фланец ст. Ду65 1.0МПа OBR036-APPLY")
        substitute = self._product("Фланец DN65 PN16 OBR036-APPLY")
        rule = self._rule(source, substitute)
        self._put_stock(substitute, 13.0)
        request = self._request()
        line = self._line(
            request,
            source,
            name="Фланец ст. Ду 65мм 1,0МПа OBR036-APPLY",
        )

        line.action_refresh_stock_match_warning()

        self.assertTrue(line.stock_match_warning)
        self.assertEqual(line.stock_qty_on_hand, 0.0)
        self.assertEqual(line.substitute_product_id, substitute)
        self.assertAlmostEqual(line.substitute_stock_qty, 13.0)
        self.assertIn("разрешённый аналог", line.substitute_warning_text)

        line.action_use_substitute_product()

        line.invalidate_recordset()
        rule.invalidate_recordset()
        self.assertEqual(line.product_id, substitute)
        self.assertFalse(line.substitute_product_id)
        self.assertEqual(line.procurement_mode, "issue")
        self.assertAlmostEqual(line.qty_to_issue, 5.0)
        self.assertAlmostEqual(line.qty_to_buy, 0.0)
        self.assertEqual(rule.usage_count, 1)
        self.assertTrue(
            any(
                substitute.display_name in body
                for body in request.message_ids.mapped("body")
            )
        )

    def test_purchase_guard_blocks_allowed_substitute_with_stock(self):
        source = self._product("Фланец ст. Ду65 1.0МПа OBR036-PO")
        substitute = self._product("Фланец DN65 PN16 OBR036-PO")
        self._rule(source, substitute)
        self._put_stock(substitute, 17.0)
        request = self._request()
        self._line(
            request,
            source,
            name="Фланец ст. Ду 65мм 1,0МПа OBR036-PO",
        )
        request.write({"state": "in_progress"})
        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=request.id)
            .create({"request_id": request.id})
        )

        result = wizard.action_create_purchase()

        self.assertEqual(result["res_model"], "object.request.purchase.wizard")
        self.assertIn("разрешённый аналог", wizard.stock_guard_warning_text)
        self.assertIn(substitute.display_name, wizard.stock_guard_warning_text)
        self.assertFalse(request.purchase_order_ids)

    def test_purchase_guard_override_logs_allowed_substitute_rejection(self):
        source = self._product("Фланец ст. Ду65 1.0МПа OBR036-KEEP")
        substitute = self._product("Фланец DN65 PN16 OBR036-KEEP")
        self._rule(source, substitute)
        self._put_stock(substitute, 19.0)
        request = self._request()
        self._line(
            request,
            source,
            name="Фланец ст. Ду 65мм 1,0МПа OBR036-KEEP",
        )
        request.write({"state": "in_progress"})
        wizard = (
            self.env["object.request.purchase.wizard"]
            .with_context(default_request_id=request.id)
            .create({"request_id": request.id})
        )

        result = wizard.action_keep_purchase_despite_stock_candidate()

        self.assertEqual(result["res_model"], "purchase.order")
        self.assertTrue(request.purchase_order_ids)
        self.assertTrue(
            any(
                "разрешённый аналог" in body
                and substitute.display_name in body
                for body in request.message_ids.mapped("body")
            )
        )
