# @file: test_upload_invoice.py
# @description: Тесты эндпоинта /ai_assistant/upload_invoice (AIA-056).
# @dependencies: chat_controller, invoice_parsing, invoice_extraction_store
# @created: 2026-05-30

from __future__ import annotations

import io
from unittest.mock import patch

from odoo.tests.common import HttpCase
from odoo.tests import tagged

_MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<</Type /Catalog>>endobj\n%%EOF\n"
_FAKE_XLSX = b"PK\x03\x04fake_xlsx_content"
_NF504_SUPPLIER = "ИП Татаринов Вадим Владимирович"

_MOCK_INVOICE_DATA = {
    "document_type": "supplier_invoice",
    "invoice_number": "НФ-504",
    "invoice_date": "2026-05-20",
    "supplier": {
        "name": _NF504_SUPPLIER,
        "inn": "280110406377",
        "kpp": "",
        "address": "",
        "bank": {"name": "", "bik": "", "account": "", "corr_account": ""},
    },
    "buyer": {"name": "ООО ТЕПЛОСЕРВИС-КОМПЛЕКТ", "inn": "2801131520",
              "kpp": "280101001", "address": ""},
    "items": [
        {"line_no": i, "name": f"Товар {i}", "unit": "шт",
         "qty": 1.0, "price": 100.0, "amount_wo_vat": 100.0,
         "amount_w_vat": 120.0, "vat_rate": "20%",
         "vat_amount": 20.0, "article": "", "discount": ""}
        for i in range(1, 15)
    ],
    "totals": {
        "total_wo_vat": 60191.67,
        "vat_total": 12437.14,
        "total_w_vat": 72096.22,
    },
    "pages": 1,
    "warnings": [],
}


def _upload(
    client,
    file_bytes,
    filename="invoice.pdf",
    content_type="application/pdf",
):
    """Вспомогательная функция для POST multipart к /upload_invoice."""
    return client.url_open(
        "/ai_assistant/upload_invoice",
        data={"file": (io.BytesIO(file_bytes), filename)},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )


@tagged('post_install', '-at_install')
class TestUploadInvoiceController(HttpCase):

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')

    # ── helpers ──────────────────────────────────────────────────────────

    def _upload(self, file_bytes, filename="invoice.pdf"):
        """Отправить multipart POST на /ai_assistant/upload_invoice."""
        boundary = b"testboundary12345"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mime = (
            "application/pdf"
            if ext == "pdf" else "application/octet-stream"
        )
        body = (
            b"--" + boundary + b"\r\n"
            + b'Content-Disposition: form-data; name="file"; filename="'
            + filename.encode() + b'"\r\n'
            + b"Content-Type: " + mime.encode() + b"\r\n\r\n"
            + file_bytes
            + b"\r\n--" + boundary + b"--\r\n"
        )
        return self.url_open(
            "/ai_assistant/upload_invoice",
            data=body,
            headers={
                "Content-Type": (
                    "multipart/form-data; boundary=" + boundary.decode()
                ),
                "X-Requested-With": "XMLHttpRequest",
            },
        )

    @patch(
        "odoo.addons.ai_assistant.controllers.chat_controller.extract_invoice",
        return_value=_MOCK_INVOICE_DATA,
    )
    def test_happy_case_returns_summary(self, mock_extract):
        resp = self._upload(_MINIMAL_PDF)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(
            body.get("success"),
            msg=f"Ожидали success=True: {body}",
        )
        self.assertIn("extraction_token", body)
        self.assertTrue(
            body.get("extraction_token"),
            "Token должен быть непустым",
        )
        summary = body.get("summary", "")
        self.assertIn(
            "14",
            summary,
            msg=f"В summary должно быть кол-во позиций: {summary}",
        )
        meta = body.get("meta", {})
        self.assertEqual(meta.get("item_count"), 14)
        self.assertEqual(meta.get("total_w_vat"), 72096.22)
        self.assertEqual(meta.get("supplier_name"), _NF504_SUPPLIER)

    @patch(
        "odoo.addons.ai_assistant.controllers.chat_controller.extract_invoice",
        return_value={
            **_MOCK_INVOICE_DATA,
            "supplier": {
                "name": "ООО Upload Новый Поставщик",
                "inn": "7727123407",
                "kpp": "772701007",
                "address": "",
                "bank": {
                    "name": "",
                    "bik": "",
                    "account": "",
                    "corr_account": "",
                },
            },
        },
    )
    def test_happy_case_returns_create_partner_suggestion(self, mock_extract):
        resp = self._upload(_MINIMAL_PDF)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        suggestions = body.get("suggestions") or []
        self.assertTrue(suggestions)
        self.assertEqual(suggestions[0]["action"], "invoice_create_partner")
        self.assertIn("Создать поставщика", suggestions[0]["label"])
        self.assertEqual(
            body["meta"]["supplier_name"],
            "ООО Upload Новый Поставщик",
        )

    def test_rejects_wrong_extension(self):
        resp = self._upload(_MINIMAL_PDF, filename="document.txt")
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertFalse(body.get("success"))
        self.assertIn("тип", body.get("error", "").lower())

    def test_rejects_file_too_large(self):
        big_file = b"%PDF-1.4\n" + b"A" * (6 * 1024 * 1024)
        resp = self._upload(big_file)
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertFalse(body.get("success"))
        self.assertIn("большой", body.get("error", "").lower())

    def test_rejects_wrong_magic_bytes(self):
        resp = self._upload(b"NOT_A_PDF_CONTENT", filename="invoice.pdf")
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertFalse(body.get("success"))

    def test_rejects_xlsx_with_informative_message(self):
        resp = self._upload(_FAKE_XLSX, filename="invoice.xlsx")
        self.assertIn(resp.status_code, (400, 200))
        body = resp.json()
        self.assertFalse(body.get("success"))

    def test_rejects_missing_file(self):
        resp = self.url_open(
            "/ai_assistant/upload_invoice",
            data=b"--boundary\r\n\r\n--boundary--\r\n",
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "multipart/form-data; boundary=boundary",
            },
        )
        body = resp.json()
        self.assertFalse(body.get("success"))
        self.assertIn("передан", body.get("error", "").lower())

    @patch(
        "odoo.addons.ai_assistant.controllers.chat_controller.extract_invoice",
        side_effect=ValueError("Нет текстового слоя"),
    )
    def test_parse_error_returns_400(self, mock_extract):
        resp = self._upload(_MINIMAL_PDF)
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertFalse(body.get("success"))
        self.assertIn("Не удалось распознать", body.get("error", ""))


@tagged('post_install', '-at_install')
class TestUploadInvoiceAccessControl(HttpCase):

    def setUp(self):
        super().setUp()
        demo_user = self.env.ref('base.user_demo', raise_if_not_found=False)
        if demo_user:
            self.authenticate(demo_user.login, demo_user.login)
            supply_group = self.env.ref(
                'ai_assistant.group_ai_assistant_supply',
                raise_if_not_found=False,
            )
            if supply_group:
                supply_group.sudo().write({'user_ids': [(3, demo_user.id)]})

    def test_non_supply_user_gets_403(self):
        if not self.session:
            self.skipTest("demo user not available")
        resp = self.url_open(
            "/ai_assistant/upload_invoice",
            data={"file": (io.BytesIO(_MINIMAL_PDF), "invoice.pdf")},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        body = resp.json()
        self.assertFalse(body.get("success"))
        self.assertIn("Доступ", body.get("error", ""))
