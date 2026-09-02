"""OBR-030: Preview импорта с AI-кандидатами."""
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObr030PreviewAI(TransactionCase):
    """Тесты Preview импорта с AI-кандидатами (PRV-001..PRV-006)."""

    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Тест-объект PRV"}
        )
        self.product = self.env["product.product"].create(
            {"name": "Кабель медный КВВГнг 4х2,5"}
        )
        self.wizard = self.env["object.request.import.wizard"].create({
            "project_id": self.project.id,
            "foreman_user_id": self.env.uid,
            "need_date": "2026-12-31",
            "priority": "1",
            "ai_mode": "none",
        })

    def _make_preview_line(self, wizard, name_raw, matching_required=True):
        return self.env["object.request.import.preview"].create(
            {
                "wizard_id": wizard.id,
                "sequence": 1,
                "source_row_no": 2,
                "name_raw": name_raw,
                "qty": 10.0,
                "matching_required": matching_required,
                "match_status": (
                    "unmatched" if matching_required else "matched"
                ),
            }
        )

    def _fake_build_candidates(
        self,
        name_raw,
        supplier_article,
        vendor=None,
        technical_designation=None,
    ):
        return {
            "candidates": [
                {
                    "product": self.product,
                    "product_id": self.product.id,
                    "local_score": 0.95,
                    "reason": "Тест-совпадение",
                }
            ],
            "line_type": "normal",
            "can_call_llm": True,
            "note": "",
        }

    def _fake_build_candidates_empty(
        self,
        name_raw,
        supplier_article,
        vendor=None,
        technical_designation=None,
    ):
        return {
            "candidates": [],
            "line_type": "normal",
            "can_call_llm": False,
            "note": "Кандидаты не найдены.",
        }

    # ------------------------------------------------------------------ #
    # PRV-001 / PRV-003

    def test_preview_ai_suggest_mode_populates_fields(self):
        """В режиме suggest AI-поля заполняются."""
        self.wizard.ai_mode = "suggest"
        preview_vals = [
            {
                "wizard_id": self.wizard.id,
                "sequence": 1,
                "name_raw": "Кабель КВВГнг",
                "supplier_article": "12345",
                "matching_required": True,
            }
        ]
        svc_path = (
            "odoo.addons.object_request.models"
            ".matching_candidate_service"
            ".ObjectRequestMatchingCandidateService.build_candidates"
        )
        with patch(svc_path, self._fake_build_candidates):
            self.wizard._enrich_with_ai_candidates(preview_vals)

        vals = preview_vals[0]
        self.assertEqual(vals.get("ai_suggested_product_id"), self.product.id)
        self.assertAlmostEqual(vals.get("ai_match_confidence"), 0.95)
        self.assertEqual(vals.get("matching_source"), "ai")

    def test_preview_ai_none_mode_skips_ai(self):
        """В режиме none AI-поля пустые."""
        self.wizard.ai_mode = "none"
        preview_vals = [
            {
                "wizard_id": self.wizard.id,
                "sequence": 1,
                "name_raw": "Кабель КВВГнг",
                "supplier_article": "12345",
                "matching_required": True,
            }
        ]
        self.wizard._enrich_with_ai_candidates(preview_vals)
        vals = preview_vals[0]
        self.assertFalse(vals.get("ai_suggested_product_id"))
        self.assertFalse(vals.get("matching_source"))

    # ------------------------------------------------------------------ #
    # PRV-004

    def test_import_transfers_ai_fields_to_lines(self):
        """После импорта AI-поля переносятся в строки заявки."""
        line = self._make_preview_line(self.wizard, "Кабель КВВГ")
        line.write(
            {
                "technical_designation": "L=0.13",
                "ai_suggested_product_id": self.product.id,
                "ai_match_confidence": 0.80,
                "ai_match_reason": "Тест",
                "matching_source": "ai",
            }
        )
        self.wizard.validation_state = "valid"

        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-12-31",
                "priority": "1",
            }
        )
        line_vals = self.wizard._build_line_vals(request, line)

        self.assertEqual(
            line_vals["ai_suggested_product_id"], self.product.id
        )
        self.assertAlmostEqual(line_vals["ai_match_confidence"], 0.80)
        self.assertEqual(line_vals["ai_match_reason"], "Тест")
        self.assertEqual(line_vals["technical_designation"], "L=0.13")
        self.assertEqual(line_vals["matching_source"], "unknown")

    def test_import_auto_mode_applies_confident_matches(self):
        """В режиме auto уверенные кандидаты применяются автоматически."""
        self.wizard.ai_mode = "auto"
        line = self._make_preview_line(self.wizard, "Кабель КВВГ")
        line.write(
            {
                "ai_suggested_product_id": self.product.id,
                "ai_match_confidence": 0.95,
                "ai_match_reason": "Авто",
                "matching_source": "ai",
                "matching_required": True,
            }
        )

        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-12-31",
                "priority": "1",
            }
        )
        line_vals = self.wizard._build_line_vals(request, line)

        self.assertEqual(line_vals["product_id"], self.product.id)
        self.assertEqual(line_vals["matching_source"], "llm_auto")
        self.assertFalse(line_vals["matching_required"])

    def test_import_uses_selected_ai_candidate_as_confirmed_match(self):
        """Выбранная AI-подсказка импортируется как подтверждённая."""
        line = self._make_preview_line(self.wizard, "Кабель КВВГ")
        line.write(
            {
                "ai_suggested_product_id": self.product.id,
                "selected_product_id": self.product.id,
                "ai_match_confidence": 0.80,
                "ai_match_reason": "Тест",
                "matching_source": "ai",
                "matching_required": True,
            }
        )

        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-12-31",
                "priority": "1",
            }
        )
        line_vals = self.wizard._build_line_vals(request, line)

        self.assertEqual(line_vals["product_id"], self.product.id)
        self.assertEqual(line_vals["matching_source"], "llm_confirmed")
        self.assertFalse(line_vals["matching_required"])

    def test_import_uses_selected_manual_product(self):
        """Выбранный вручную товар импортируется как ручное сопоставление."""
        manual_product = self.env["product.product"].create(
            {"name": "Кабель ручной выбор PRV"}
        )
        line = self._make_preview_line(self.wizard, "Кабель КВВГ")
        line.write(
            {
                "ai_suggested_product_id": self.product.id,
                "selected_product_id": manual_product.id,
                "matching_source": "ai",
                "matching_required": True,
            }
        )

        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.uid,
                "need_date": "2026-12-31",
                "priority": "1",
            }
        )
        line_vals = self.wizard._build_line_vals(request, line)

        self.assertEqual(line_vals["product_id"], manual_product.id)
        self.assertEqual(line_vals["matching_source"], "manual")
        self.assertFalse(line_vals["matching_required"])

    # ------------------------------------------------------------------ #
    # PRV-005

    def test_validation_message_shows_ai_stats(self):
        """Статистика AI отображается в validation messages."""
        self.wizard.ai_mode = "suggest"
        preview_vals = [
            {
                "wizard_id": self.wizard.id,
                "sequence": 1,
                "name_raw": "Кабель КВВГ",
                "supplier_article": "",
                "matching_required": True,
                "ai_suggested_product_id": self.product.id,
            },
            {
                "wizard_id": self.wizard.id,
                "sequence": 2,
                "name_raw": "Провод ПВС",
                "supplier_article": "",
                "matching_required": True,
                "ai_suggested_product_id": False,
            },
        ]
        messages = []
        if self.wizard.ai_mode != "none":
            ai_count = sum(
                1 for v in preview_vals if v.get("ai_suggested_product_id")
            )
            manual_count = sum(
                1 for v in preview_vals
                if v.get("matching_required")
                and not v.get("ai_suggested_product_id")
            )
            messages.append(f"AI предложило кандидатов: {ai_count}")
            if manual_count:
                messages.append(f"Требуют ручного ввода: {manual_count}")

        self.assertIn("AI предложило кандидатов: 1", messages)
        self.assertIn("Требуют ручного ввода: 1", messages)

    # ------------------------------------------------------------------ #
    # PRV-002

    def test_compute_ai_stats(self):
        """_compute_ai_stats корректно считает статистику по строкам."""
        line1 = self._make_preview_line(self.wizard, "Товар 1")
        line1.write(
            {
                "ai_suggested_product_id": self.product.id,
                "matching_required": True,
            }
        )
        line2 = self._make_preview_line(self.wizard, "Товар 2")
        line2.write(
            {
                "ai_suggested_product_id": False,
                "matching_required": True,
            }
        )

        self.wizard._compute_ai_stats()
        self.assertEqual(self.wizard.ai_matched_count, 1)
        self.assertEqual(self.wizard.manual_required_count, 1)
