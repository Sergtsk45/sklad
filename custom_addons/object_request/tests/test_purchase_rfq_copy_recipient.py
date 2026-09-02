# -*- coding: utf-8 -*-
"""
@file: test_purchase_rfq_copy_recipient.py
@description: В заявке поставщику получатели — вендор и компания ТСК.
@dependencies: object_request.models.purchase_order_ext
@created: 2026-08-24
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "or_rfq_copy")
class TestPurchaseRfqCopyRecipient(TransactionCase):
    """Копия RFQ уходит на партнёра компании (675001@mail.ru на prod)."""

    def test_rfq_template_includes_vendor_and_company(self):
        template = self.env.ref("purchase.email_template_edi_purchase")
        self.assertFalse(
            template.use_default_to,
            "use_default_to блокирует partner_to шаблона",
        )
        vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик копии RFQ",
                "email": "vendor-rfq-copy@example.com",
                "supplier_rank": 1,
            }
        )
        po = self.env["purchase.order"].create({"partner_id": vendor.id})
        rendered = template._render_field("partner_to", po.ids)[po.id]
        partner_ids = {
            int(pid.strip())
            for pid in str(rendered).split(",")
            if pid.strip().isdigit()
        }
        self.assertIn(vendor.id, partner_ids)
        self.assertIn(po.company_id.partner_id.id, partner_ids)

    def test_rfq_template_has_company_signature(self):
        template = self.env.ref("purchase.email_template_edi_purchase")
        body = template.body_html or ""
        self.assertIn("С уважением,", body)
        self.assertIn("get_rfq_mail_signer_name", body)
        self.assertIn("Теплосервис-Комплект", body)
        from odoo.tools.mail import html_sanitize
        sanitized = html_sanitize(body)
        self.assertIn("С уважением,", sanitized)
        self.assertIn("Теплосервис-Комплект", sanitized)
        self.assertNotIn("object.user_id.name", body)
        self.assertNotIn("8 962 285 85 10", body)
        self.assertGreater(
            body.find("</table>"),
            -1,
            "подпись должна идти после таблицы товаров",
        )
        self.assertGreater(body.find("С уважением"), body.find("</table>"))

    def _make_vendor(self, email):
        return self.env["res.partner"].create(
            {
                "name": "Поставщик подписи RFQ",
                "email": email,
                "supplier_rank": 1,
            }
        )

    def test_rfq_signer_admin_is_sergey(self):
        self.assertEqual(
            self.env["purchase.order"].create(
                {
                    "partner_id": self._make_vendor("v-admin@example.com").id,
                    "user_id": self.env.ref("base.user_admin").id,
                }
            ).get_rfq_mail_signer_name(),
            "Сергей",
        )

    def test_rfq_signer_empty_buyer_has_no_name(self):
        po = self.env["purchase.order"].create(
            {"partner_id": self._make_vendor("v-empty@example.com").id}
        )
        po.user_id = False
        self.assertEqual(po.get_rfq_mail_signer_name(), "")
        body = self.env.ref("purchase.email_template_edi_purchase")._render_field(
            "body_html", po.ids
        )[po.id]
        self.assertIn("С уважением", body)
        self.assertNotIn("Сергей", body)
        self.assertIn("Теплосервис-Комплект", body)

    def test_rfq_body_renders_buyer_name(self):
        buyer = self.env["res.users"].create(
            {
                "name": "Иван Снабженец",
                "login": "buyer_rfq_signer_test",
                "email": "buyer-rfq-signer@example.com",
            }
        )
        po = self.env["purchase.order"].create(
            {
                "partner_id": self._make_vendor("vendor-sign-rfq@example.com").id,
                "user_id": buyer.id,
            }
        )
        self.assertEqual(po.get_rfq_mail_signer_name(), "Иван Снабженец")
        body = self.env.ref("purchase.email_template_edi_purchase")._render_field(
            "body_html", po.ids
        )[po.id]
        self.assertIn("Иван Снабженец", body)
        self.assertNotIn("Administrator", body)
        self.assertIn("Теплосервис-Комплект", body)
        self.assertGreater(body.find("С уважением"), body.find("</table>"))

    def test_default_recipients_include_company_when_email_set(self):
        company_partner = self.env.company.partner_id
        company_partner.email = "675001@mail.ru"
        vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик default RFQ",
                "email": "vendor-default-rfq@example.com",
                "supplier_rank": 1,
            }
        )
        po = self.env["purchase.order"].create({"partner_id": vendor.id})
        recipients = po._message_get_default_recipients()[po.id]
        self.assertIn(vendor.id, recipients["partner_ids"])
        self.assertIn(company_partner.id, recipients["partner_ids"])

    def _make_rfq_and_message(self):
        vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик без портал-кнопки",
                "email": "vendor-no-portal@example.com",
                "supplier_rank": 1,
            }
        )
        po = self.env["purchase.order"].create({"partner_id": vendor.id})
        message = self.env["mail.message"].create(
            {
                "model": "purchase.order",
                "res_id": po.id,
                "body": "<p>test</p>",
                "message_type": "comment",
            }
        )
        return po, message

    def test_rfq_notify_groups_have_no_portal_button(self):
        po, message = self._make_rfq_and_message()
        groups = po._notify_get_recipients_groups(message, "Purchase Order")
        self.assertTrue(groups)
        for name, _func, opts in groups:
            self.assertFalse(
                opts.get("has_button_access"),
                "RFQ не должен содержать кнопку портала (группа %s)" % name,
            )

    def test_rfq_email_context_has_no_subtitles(self):
        po, message = self._make_rfq_and_message()
        ctx = po._notify_by_email_prepare_rendering_context(message)
        self.assertFalse(ctx.get("subtitles"))

    def _pdata(self, partner, lang, recipient_type="customer"):
        return {
            "id": partner.id,
            "active": True,
            "email_normalized": partner.email,
            "is_follower": False,
            "name": partner.name,
            "lang": lang,
            "groups": [],
            "notif": "email",
            "share": recipient_type != "user",
            "type": recipient_type,
            "uid": False,
            "ushare": False,
        }

    def test_rfq_vendor_and_company_share_notify_group(self):
        po, message = self._make_rfq_and_message()
        company = po.company_id.partner_id
        groups = po._notify_get_recipients_classify(
            message,
            [
                self._pdata(po.partner_id, "en_US", "customer"),
                self._pdata(company, "ru_RU", "user"),
            ],
            "Purchase Order",
        )
        self.assertEqual(len(groups), 1, groups)
        self.assertEqual(
            groups[0]["notification_group_name"],
            "rfq_vendor_and_company_copy",
        )
        self.assertEqual(
            set(groups[0]["recipients_ids"]),
            {po.partner_id.id, company.id},
        )
        self.assertFalse(groups[0].get("has_button_access"))

    def test_rfq_notify_iterator_unifies_vendor_and_copy_lang(self):
        self.env["res.lang"]._activate_lang("ru_RU")
        po, message = self._make_rfq_and_message()
        company = po.company_id.partner_id
        company.lang = "ru_RU"
        po.partner_id.lang = "en_US"
        items = list(
            po._notify_get_classified_recipients_iterator(
                message,
                [
                    self._pdata(po.partner_id, "en_US", "customer"),
                    self._pdata(company, "ru_RU", "user"),
                ],
            )
        )
        self.assertEqual(len(items), 1, items)
        lang, _render, group = items[0]
        self.assertEqual(lang, "ru_RU")
        self.assertEqual(
            set(group["recipients_ids"]),
            {po.partner_id.id, company.id},
        )

    def test_confirmed_po_does_not_unify_rfq_copy_group(self):
        po, message = self._make_rfq_and_message()
        po.state = "purchase"
        groups = po._notify_get_recipients_groups(message, "Purchase Order")
        names = [name for name, _func, _opts in groups]
        self.assertNotIn("rfq_vendor_and_company_copy", names)
