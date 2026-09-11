# -*- coding: utf-8 -*-
"""
@file: test_td015_request_comment_list.py
@description: Колонка и поиск по комментарию шапки в списке требований.
@dependencies: object.request, object_request_views.xml
@created: 2026-09-11
"""

from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_HEADER_MARKER = "TD015-HEADER-COMMENT-XYZ"
_LINE_MARKER = "TD015-LINE-COMMENT-XYZ"


@tagged("post_install", "-at_install", "td015")
class TestTd015RequestCommentList(TransactionCase):
    """Комментарий шапки виден в list и участвует в поиске документов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["object.request.project"].create(
            {"name": "Объект TD-015"}
        )
        cls.foreman = cls.env.ref("base.user_admin")

    def _create_request(self, comment=""):
        return self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": "2026-09-11",
                "comment": comment,
            }
        )

    def test_list_view_contains_comment_column(self):
        view = self.env.ref("object_request.view_object_request_list")
        arch = self.env["object.request"].get_view(view.id, "list")["arch"]
        self.assertIn('name="comment"', arch)
        self.assertIn('string="Комментарий"', arch)

    def test_search_view_searches_name_or_comment(self):
        view = self.env.ref("object_request.view_object_request_search")
        root = etree.fromstring(view.arch_db)
        name_field = root.xpath("//field[@name='name']")[0]
        filter_domain = name_field.get("filter_domain") or ""
        self.assertIn("comment", filter_domain)
        self.assertIn("ilike", filter_domain)
        comment_fields = root.xpath("//search/field[@name='comment']")
        self.assertTrue(
            comment_fields,
            "В search view нет поля comment",
        )
        self.assertEqual(comment_fields[0].get("string"), "Комментарий")

    def test_search_finds_header_comment_not_line_comment(self):
        header_req = self._create_request(comment=_HEADER_MARKER)
        line_only_req = self._create_request()
        self.env["object.request.line"].create(
            {
                "request_id": line_only_req.id,
                "name_raw": "Строка TD-015",
                "qty_requested": 1.0,
                "comment": _HEADER_MARKER,
            }
        )
        found = self.env["object.request"].search(
            [("comment", "ilike", _HEADER_MARKER)]
        )
        self.assertIn(header_req, found)
        self.assertNotIn(line_only_req, found)

    def test_omnibox_domain_matches_name_or_header_comment(self):
        by_comment = self._create_request(comment=_LINE_MARKER)
        by_name = self._create_request()
        line_only = self._create_request()
        self.env["object.request.line"].create(
            {
                "request_id": line_only.id,
                "name_raw": "Строка только line.comment",
                "qty_requested": 1.0,
                "comment": _LINE_MARKER,
            }
        )
        found = self.env["object.request"].search(
            [
                "|",
                ("name", "ilike", _LINE_MARKER),
                ("comment", "ilike", _LINE_MARKER),
            ]
        )
        self.assertIn(by_comment, found)
        self.assertNotIn(by_name, found)
        self.assertNotIn(line_only, found)
