from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObr037ProductFeatures(TransactionCase):
    def _product(self, name):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
            }
        )

    def test_parser_normalizes_diameter_and_pressure(self):
        parser = self.env["object.request.product.feature.parser"]

        a = parser.parse_text("Фланец ст. Ду 65мм 1,0МПа")
        b = parser.parse_text("Фланец DN65 PN16")

        self.assertEqual(a["product_family"], "flange")
        self.assertEqual(a["diameter_nominal"], 65)
        self.assertEqual(a["pressure_nominal"], 10)
        self.assertEqual(a["material"], "steel")
        self.assertEqual(b["diameter_nominal"], 65)
        self.assertEqual(b["pressure_nominal"], 16)

    def test_parser_supports_pilot_families(self):
        parser = self.env["object.request.product.feature.parser"]
        cases = {
            "Прокладка паронитовая Ду50 PN16": ("gasket", 50, 16),
            "Переход стальной DN80x50 PN10": ("reducer", 80, 10),
            "Отвод стальной Ду40": ("elbow", 40, False),
            "Кран муфтовый латунный Ду15 В-В": ("valve", 15, False),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                features = parser.parse_text(text)
                self.assertEqual(features["product_family"], expected[0])
                self.assertEqual(features["diameter_nominal"], expected[1])
                self.assertEqual(features["pressure_nominal"], expected[2])

    def test_product_template_stores_parsed_features(self):
        product = self._product("Фланец DN65 PN16 ГОСТ 33259 стальной")

        self.assertEqual(product.or_product_family, "flange")
        self.assertEqual(product.or_diameter_nominal, 65)
        self.assertEqual(product.or_pressure_nominal, 16)
        self.assertEqual(product.or_material, "steel")
        self.assertEqual(product.or_standard, "33259")
        self.assertEqual(product.or_feature_key, "flange|DN65|PN16")

    def test_candidate_service_uses_structured_features(self):
        lower = self._product("Фланец ст. Ду65 1.0МПа OBR037")
        higher = self._product("Фланец DN65 PN16 OBR037")
        self._product("Фланец DN40 PN16 OBR037")

        result = self.env[
            "object.request.matching.candidate.service"
        ].build_candidates("Фланец ст. Ду 65мм 1,0МПа OBR037", "")

        ids = [item["product_id"] for item in result["candidates"]]
        self.assertIn(lower.id, ids)
        self.assertIn(higher.id, ids)
        self.assertNotIn(
            self.env["product.product"].search(
                [("name", "=", "Фланец DN40 PN16 OBR037")],
                limit=1,
            ).id,
            ids,
        )
        higher_candidate = next(
            item for item in result["candidates"]
            if item["product_id"] == higher.id
        )
        self.assertEqual(higher_candidate["source"], "feature")
        self.assertIn("структурные признаки", higher_candidate["reason"])

    def test_audit_report_finds_duplicates_missing_dn_and_pressure_conflict(
        self,
    ):
        dup_a = self._product("Фланец DN65 PN16 OBR037-DUP A")
        dup_b = self._product("Фланец Ду65 Ру16 OBR037-DUP B")
        missing = self._product("Кран шаровый OBR037-MISSING")
        conflict = self._product("Фланец DN65 PN10 OBR037-CONFLICT")

        Audit = self.env["object.request.product.feature.audit.line"]
        Audit.refresh_report()

        duplicate_lines = Audit.search(
            [
                ("issue_type", "=", "duplicate"),
                ("product_id", "in", [dup_a.id, dup_b.id]),
            ]
        )
        missing_lines = Audit.search(
            [
                ("issue_type", "=", "missing_diameter"),
                ("product_id", "=", missing.id),
            ]
        )
        conflict_lines = Audit.search(
            [
                ("issue_type", "=", "pressure_conflict"),
                ("product_id", "in", [dup_a.id, dup_b.id, conflict.id]),
            ]
        )

        self.assertEqual(len(duplicate_lines), 2)
        self.assertEqual(len(missing_lines), 1)
        self.assertTrue(conflict_lines)
