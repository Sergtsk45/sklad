from odoo import api, models


PURCHASE_TRANSFER_REPORT_NAME = "object._get_transfer_report_filename()"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _object_request_set_purchase_report_names(self):
        reports = (
            self.env.ref(
                "purchase.action_report_purchase_order",
                raise_if_not_found=False,
            )
            | self.env.ref(
                "purchase.report_purchase_quotation",
                raise_if_not_found=False,
            )
        )
        reports = reports.exists()
        if not reports:
            return

        reports.with_context(lang=None).write(
            {"print_report_name": PURCHASE_TRANSFER_REPORT_NAME}
        )
        for lang in self.env["res.lang"].search([("active", "=", True)]):
            reports.with_context(lang=lang.code).write(
                {"print_report_name": PURCHASE_TRANSFER_REPORT_NAME}
            )
