"""
OBR-009: Тесты массовых действий и ускорения сопоставления.
"""
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError
from lxml import etree
import datetime


@tagged("post_install", "-at_install")
class TestObr009MassActions(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR-009",
            }
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб Тест OBR009",
                "login": "foreman_test_obr009",
                "email": "foreman_obr009@test.com",
            }
        )
        self.vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик ООО Тест",
                "supplier_rank": 1,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Цемент М500",
                "default_code": "CEM-500",
                "type": "consu",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_code": "ART-001",
                "price": 100.0,
            }
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        # Несопоставленная строка
        self.line_unmatched = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 10.0,
                "matching_required": True,
                "manual_vendor_required": True,
            }
        )
        # Строка с поставщиком, но без товара
        self.line_no_vendor = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Краска белая",
                "qty_requested": 5.0,
                "manual_vendor_required": True,
            }
        )

    # ----- line_problem_count -----

    def test_line_problem_count_includes_vendor_required(self):
        """line_problem_count считает строки с manual_vendor_required тоже."""
        self.request._compute_line_counters()
        # line_unmatched: matching_required + manual_vendor_required
        # line_no_vendor: manual_vendor_required
        self.assertEqual(self.request.line_problem_count, 2)

    def test_line_problem_count_decreases_after_fix(self):
        """Счётчик уменьшается, когда проблемы устраняются."""
        self.line_no_vendor.write({"manual_vendor_required": False})
        self.request._compute_line_counters()
        self.assertEqual(self.request.line_problem_count, 1)

    def test_line_problem_count_zero_when_all_matched(self):
        """Счётчик 0, когда все строки сопоставлены."""
        self.line_unmatched.write(
            {
                "matching_required": False,
                "manual_vendor_required": False,
                "product_id": self.product.id,
            }
        )
        self.line_no_vendor.write({"manual_vendor_required": False})
        self.request._compute_line_counters()
        self.assertEqual(self.request.line_problem_count, 0)

    # ----- action_rematch_lines -----

    def test_rematch_finds_product_by_article(self):
        """Пересопоставление находит товар по артикулу поставщика."""
        self.request.action_rematch_lines()
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.product_id, self.product)

    def test_rematch_finds_vendor(self):
        """Пересопоставление находит поставщика по имени."""
        self.request.action_rematch_lines()
        self.assertEqual(self.line_unmatched.preferred_vendor_id, self.vendor)

    def test_rematch_returns_notification(self):
        """action_rematch_lines возвращает display_notification."""
        result = self.request.action_rematch_lines()
        self.assertEqual(result.get("type"), "ir.actions.client")
        self.assertEqual(result.get("tag"), "display_notification")

    def test_rematch_no_unmatched_lines(self):
        """Пересопоставление без проблемных строк даёт info уведомление."""
        self.line_unmatched.write(
            {
                "matching_required": False,
                "product_id": self.product.id,
            }
        )
        self.line_no_vendor.write(
            {
                "matching_required": False,
                "product_id": self.product.id,
                "manual_vendor_required": False,
            }
        )
        result = self.request.action_rematch_lines()
        self.assertEqual(result["params"]["type"], "info")

    def test_rematch_lines_does_not_touch_already_matched(self):
        """Обычное пересопоставление не трогает уже сопоставленные строки."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Ошибочный товар OBR009",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_lines()

        self.assertEqual(line.product_id, wrong_product)

    def test_rematch_all_lines_updates_auto_matched_line(self):
        """Пересопоставление всех строк пересматривает auto matched строки."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Ошибочный товар OBR009 all",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.matching_source, "rematch_auto")
        self.assertIn("old product:", line.matching_note)

    def test_rematch_all_lines_clears_false_auto_match(self):
        """All-lines очищает старый auto match, если товар не найден."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Переход 108-57 ст.",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Переход",
                "supplier_article": "80x50 ГОСТ 17378-2001",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertFalse(line.product_id)
        self.assertTrue(line.matching_required)
        self.assertEqual(line.matching_source, "unknown")
        self.assertIn("old product:", line.matching_note)

    def test_rematch_all_lines_keeps_manual_match(self):
        """All-lines не перезаписывает строку, похожую на ручной выбор."""
        manual_product = self.env["product.product"].create(
            {
                "name": "Ручной товар OBR009",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": manual_product.id,
                "matching_required": False,
                "matching_note": "выбрано снабженцем",
                "matching_source": "manual",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertEqual(line.product_id, manual_product)

    def test_rematch_with_stock_context_applies_safe_stock_candidate(self):
        """Переподбор применяет безопасный складской товар."""
        stock_product = self.env["product.product"].create(
            {
                "name": "Фланец DN65 PN16 OBR009-STOCK",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            stock_product,
            self.project.warehouse_id.lot_stock_id,
            15.0,
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Фланец DN65 PN16 OBR009-STOCK",
                "qty_requested": 1.0,
                "matching_required": True,
            }
        )

        result = self.request.action_rematch_with_stock_context()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(line.product_id, stock_product)
        self.assertFalse(line.matching_required)
        self.assertEqual(line.matching_state, "matched")
        self.assertEqual(line.matching_source, "combined_auto")
        self.assertIn("учётом остатков", line.matching_note)

    # ----- Wizard массового назначения: Назначить поставщика -----

    def test_assign_vendor_wizard(self):
        """Wizard назначает поставщика выбранным строкам."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id, self.line_no_vendor.id],
                active_model="object.request.line",
            )
            .create(
                {
                    "assign_type": "vendor",
                    "vendor_id": self.vendor.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.preferred_vendor_id, self.vendor)
        self.assertEqual(self.line_no_vendor.preferred_vendor_id, self.vendor)
        self.assertFalse(self.line_unmatched.manual_vendor_required)
        self.assertFalse(self.line_no_vendor.manual_vendor_required)

    def test_assign_vendor_wizard_no_vendor_raises(self):
        """Wizard без выбранного поставщика — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create({"assign_type": "vendor"})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    def test_assign_vendor_wizard_no_lines_raises(self):
        """Wizard без active_ids — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[],
            )
            .create({"assign_type": "vendor", "vendor_id": self.vendor.id})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    # ----- Wizard массового назначения: Назначить товар -----

    def test_assign_product_wizard(self):
        """Wizard назначает товар и снимает флаг matching_required."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
                active_model="object.request.line",
            )
            .create(
                {
                    "assign_type": "product",
                    "product_id": self.product.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.product_id, self.product)
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.matching_source, "manual")

    def test_assign_product_wizard_sets_uom(self):
        """Wizard при назначении товара выставляет uom_id."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create(
                {
                    "assign_type": "product",
                    "product_id": self.product.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.uom_id, self.product.uom_id)

    def test_assign_product_wizard_no_product_raises(self):
        """Wizard без выбранного товара — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create({"assign_type": "product"})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    # ----- AI candidates -----

    def test_prepare_ai_candidates_fills_line_suggestion(self):
        result = self.request.action_prepare_ai_candidates()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(
            self.line_unmatched.ai_suggested_product_id,
            self.product,
        )
        self.assertIn(
            self.product,
            self.line_unmatched.ai_candidate_product_ids,
        )
        self.assertGreaterEqual(self.line_unmatched.ai_match_confidence, 0.9)
        self.assertTrue(self.line_unmatched.ai_match_reason)

    def test_apply_confident_ai_matches_sets_product(self):
        self.request.action_prepare_ai_candidates()
        self.line_unmatched.write(
            {
                "product_id": False,
                "matching_required": True,
            }
        )

        self.request.action_apply_confident_ai_matches()

        self.assertEqual(self.line_unmatched.product_id, self.product)
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.matching_source, "llm_auto")

    def test_apply_confident_ai_matches_skips_low_confidence(self):
        self.line_unmatched.write(
            {
                "ai_suggested_product_id": self.product.id,
                "ai_match_confidence": 0.7,
            }
        )

        self.request.action_apply_confident_ai_matches()

        self.assertFalse(self.line_unmatched.product_id)
        self.assertTrue(self.line_unmatched.matching_required)

    def test_accept_ai_candidate_sets_manual_confirmation_source(self):
        self.request.action_prepare_ai_candidates()

        self.line_unmatched.action_accept_ai_candidate()

        self.assertEqual(self.line_unmatched.product_id, self.product)
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.matching_source, "llm_confirmed")

    def test_reject_ai_candidate_clears_suggestion(self):
        self.request.action_prepare_ai_candidates()

        self.line_unmatched.action_reject_ai_candidate()

        self.assertFalse(self.line_unmatched.ai_suggested_product_id)
        self.assertFalse(self.line_unmatched.ai_candidate_product_ids)
        self.assertEqual(
            self.line_unmatched.ai_match_reason,
            "AI-кандидат отклонён.",
        )

    def test_accept_and_remember_ai_candidate_creates_supplierinfo(self):
        product = self.env["product.product"].create(
            {
                "name": "OBR009 AI remember product",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "OBR009 AI remember product",
                "supplier_article": "OBR009-AI-MEM-001",
                "qty_requested": 1.0,
                "preferred_vendor_id": self.vendor.id,
                "matching_required": True,
                "ai_suggested_product_id": product.id,
                "ai_match_confidence": 0.95,
                "ai_match_reason": "Тестовая AI-подсказка.",
            }
        )

        line.action_accept_and_remember_ai_candidate()

        info = self.env["product.supplierinfo"].search(
            [
                ("product_code", "=ilike", "OBR009-AI-MEM-001"),
                ("partner_id", "=", self.vendor.id),
                ("product_id", "=", product.id),
            ]
        )
        self.assertEqual(len(info), 1)
        self.assertEqual(line.product_id, product)
        self.assertEqual(line.matching_source, "llm_confirmed")

    def test_foreman_cannot_accept_ai_candidate(self):
        self.request.action_prepare_ai_candidates()

        with self.assertRaises(UserError):
            self.line_unmatched.with_user(
                self.foreman
            ).action_accept_ai_candidate()

    def test_ai_matching_buttons_are_present_in_form_view(self):
        view = self.env.ref("object_request.view_object_request_form")

        self.assertIn("action_prepare_ai_candidates", view.arch_db)
        self.assertIn("action_apply_confident_ai_matches", view.arch_db)
        self.assertIn("action_accept_ai_candidate", view.arch_db)

    def test_object_request_form_keeps_risky_actions_out_of_main_flow(self):
        view = self.env.ref("object_request.view_object_request_form")
        root = etree.fromstring(view.arch_db.encode())

        header_risky_buttons = root.xpath(
            "//header//button[@name='action_rematch_lines' "
            "or @name='action_rematch_all_lines' "
            "or @name='action_prepare_ai_candidates' "
            "or @name='action_apply_confident_ai_matches']"
        )
        self.assertFalse(header_risky_buttons)

        main_line_risky_buttons = root.xpath(
            "//page[@name='page_lines']//button[@name='action_lines_buy_all' "
            "or @name='action_lines_issue_max' "
            "or @name='action_lines_reset_split']"
        )
        self.assertFalse(main_line_risky_buttons)

        matching_buttons = root.xpath(
            "//page[@name='page_matching']"
            "//button[@name='action_rematch_lines' "
            "or @name='action_rematch_all_lines' "
            "or @name='action_prepare_ai_candidates' "
            "or @name='action_apply_confident_ai_matches']"
        )
        self.assertEqual(len(matching_buttons), 4)

        po_diagnostic = root.xpath(
            "//button[@name='action_check_purchase_stock_matches']"
            "//field[@string='Диагностика PO']"
        )
        self.assertTrue(po_diagnostic)

    def test_purchase_wizard_hides_stock_guard_override_initially(self):
        view = self.env.ref(
            "object_request.view_object_request_purchase_wizard_form"
        )
        root = etree.fromstring(view.arch_db.encode())

        override_fields = root.xpath(
            "//field[@name='confirm_stock_guard_override']"
        )
        self.assertEqual(len(override_fields), 1)
        self.assertEqual(
            override_fields[0].get("invisible"),
            "not show_stock_guard_override",
        )
        warning_groups = root.xpath(
            "//group[@string='Проверка складских кандидатов']"
        )
        self.assertEqual(len(warning_groups), 1)
        self.assertEqual(
            warning_groups[0].get("invisible"),
            "not show_stock_guard_override",
        )

    # ----- line_count в wizard -----

    def test_wizard_line_count(self):
        """Wizard корректно отображает количество выбранных строк."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id, self.line_no_vendor.id],
            )
            .create({"assign_type": "vendor", "vendor_id": self.vendor.id})
        )
        self.assertEqual(wizard.line_count, 2)
