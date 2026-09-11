from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestObjectRequestProjectLocations(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {"name": "Объект OBR033"}
        )
        self.other_project = self.env["object.request.project"].create(
            {"name": "Другой объект OBR033"}
        )
        self.vendor_a = self.env["res.partner"].create(
            {"name": "Альфа поставщик", "supplier_rank": 1}
        )
        self.vendor_b = self.env["res.partner"].create(
            {"name": "Бета поставщик", "supplier_rank": 1}
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.env.user.id,
                "need_date": "2026-06-14",
            }
        )

    def _create_locations(self):
        capture_1 = self.env["object.request.project.capture"].create(
            {
                "name": "Захватка 1",
                "project_id": self.project.id,
                "sequence": 10,
            }
        )
        capture_2 = self.env["object.request.project.capture"].create(
            {
                "name": "Захватка 2",
                "project_id": self.project.id,
                "sequence": 20,
            }
        )
        floor_1 = self.env["object.request.project.floor"].create(
            {"name": "1", "project_id": self.project.id, "sequence": 10}
        )
        floor_2 = self.env["object.request.project.floor"].create(
            {"name": "2", "project_id": self.project.id, "sequence": 20}
        )
        section_a = self.env["object.request.project.section"].create(
            {"name": "А", "project_id": self.project.id, "sequence": 10}
        )
        section_b = self.env["object.request.project.section"].create(
            {"name": "Б", "project_id": self.project.id, "sequence": 20}
        )
        return capture_1, capture_2, floor_1, floor_2, section_a, section_b

    def _make_line(self, **kwargs):
        vals = {
            "request_id": self.request.id,
            "name_raw": "Материал OBR033",
            "qty_requested": 1.0,
        }
        vals.update(kwargs)
        return self.env["object.request.line"].create(vals)

    def test_project_has_independent_location_dictionaries(self):
        capture, floor, section = (
            self.env["object.request.project.capture"].create(
                {"name": "Общая метка", "project_id": self.project.id}
            ),
            self.env["object.request.project.floor"].create(
                {"name": "Общая метка", "project_id": self.project.id}
            ),
            self.env["object.request.project.section"].create(
                {"name": "Общая метка", "project_id": self.project.id}
            ),
        )

        self.assertIn(capture, self.project.capture_ids)
        self.assertIn(floor, self.project.floor_ids)
        self.assertIn(section, self.project.section_ids)

    def test_duplicate_location_name_for_same_project_raises(self):
        self.env["object.request.project.capture"].create(
            {"name": "Повтор", "project_id": self.project.id}
        )

        with self.assertRaises(ValidationError):
            self.env["object.request.project.capture"].create(
                {"name": "Повтор", "project_id": self.project.id}
            )

    def test_line_rejects_location_from_other_project(self):
        capture = self.env["object.request.project.capture"].create(
            {"name": "Чужая", "project_id": self.other_project.id}
        )

        with self.assertRaises(ValidationError):
            self._make_line(capture_id=capture.id)

    def test_project_change_clears_line_locations(self):
        capture, _capture_2, floor, _floor_2, section, _section_b = (
            self._create_locations()
        )
        line = self._make_line(
            capture_id=capture.id,
            floor_id=floor.id,
            section_id=section.id,
        )

        self.request.project_id = self.other_project
        line.invalidate_recordset()

        self.assertFalse(line.capture_id)
        self.assertFalse(line.floor_id)
        self.assertFalse(line.section_id)

    def test_sort_lines_by_location_reassigns_sequence(self):
        (
            capture_1,
            capture_2,
            floor_1,
            floor_2,
            section_a,
            section_b,
        ) = self._create_locations()
        last = self._make_line(
            capture_id=capture_2.id,
            floor_id=floor_1.id,
            section_id=section_a.id,
            preferred_vendor_id=self.vendor_a.id,
            sequence=10,
        )
        first = self._make_line(
            capture_id=capture_1.id,
            floor_id=floor_1.id,
            section_id=section_a.id,
            preferred_vendor_id=self.vendor_a.id,
            sequence=20,
        )
        third = self._make_line(
            capture_id=capture_1.id,
            floor_id=floor_2.id,
            section_id=section_a.id,
            preferred_vendor_id=self.vendor_a.id,
            sequence=30,
        )
        second = self._make_line(
            capture_id=capture_1.id,
            floor_id=floor_1.id,
            section_id=section_b.id,
            preferred_vendor_id=self.vendor_b.id,
            sequence=40,
        )

        result = self.request.action_sort_lines_by_location()
        lines = self.request.line_ids.sorted("sequence")

        self.assertEqual(lines.ids, [first.id, second.id, third.id, last.id])
        self.assertEqual(result["tag"], "display_notification")
