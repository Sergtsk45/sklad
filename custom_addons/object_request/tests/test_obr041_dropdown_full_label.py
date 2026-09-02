# -*- coding: utf-8 -*-
"""
@file: test_obr041_dropdown_full_label.py
@description: Полная подпись «наименование + поставщик» в autocomplete.
@dependencies: object_request views, autocomplete_full_label.xml
@created: 2026-08-19
"""

from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

FULL_DROPDOWN_CLASS = "o_or_full_dropdown"


@tagged("post_install", "-at_install", "obr041")
class TestObr041DropdownFullLabel(TransactionCase):
    def _assert_field_has_class(self, xml_id, field_name):
        view = self.env.ref(xml_id)
        root = etree.fromstring(view.arch_db)
        fields = root.xpath(f"//field[@name='{field_name}']")
        self.assertTrue(fields, f"{xml_id}: нет поля {field_name}")
        classes = [node.get("class") or "" for node in fields]
        self.assertTrue(
            any(FULL_DROPDOWN_CLASS in css for css in classes),
            f"{xml_id}.{field_name} без {FULL_DROPDOWN_CLASS}: {classes}",
        )

    def test_request_form_product_and_vendor_use_full_dropdown(self):
        self._assert_field_has_class(
            "object_request.view_object_request_form",
            "product_id",
        )
        self._assert_field_has_class(
            "object_request.view_object_request_form",
            "preferred_vendor_id",
        )

    def test_line_list_and_assign_wizard_use_full_dropdown(self):
        self._assert_field_has_class(
            "object_request.view_object_request_line_list",
            "product_id",
        )
        self._assert_field_has_class(
            "object_request.view_assign_lines_wizard_form",
            "vendor_id",
        )
        self._assert_field_has_class(
            "object_request.view_assign_lines_wizard_form",
            "product_id",
        )
