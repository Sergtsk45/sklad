from odoo import models, fields, api

RFQ_MAIL_BODY_HTML = """\
<div style="margin:0;padding:0;font-size:13px;">
    <p style="margin:0 0 12px 0;">Добрый день, прошу выставить счёт:</p>
    <table style="border-collapse:collapse;width:100%;max-width:640px;font-size:13px;">
        <thead>
            <tr>
                <th style="text-align:left;border-bottom:1px solid #ccc;padding:4px 8px 4px 0;">Наименование</th>
                <th style="text-align:right;border-bottom:1px solid #ccc;padding:4px 8px;">Кол-во</th>
                <th style="text-align:left;border-bottom:1px solid #ccc;padding:4px 0 4px 8px;">Ед.</th>
            </tr>
        </thead>
        <tbody>
            <t t-foreach="object.order_line" t-as="line">
                <tr>
                    <td style="padding:4px 8px 4px 0;vertical-align:top;">
                        <t t-out="line.name or ''"/>
                    </td>
                    <td style="text-align:right;padding:4px 8px;vertical-align:top;white-space:nowrap;">
                        <t t-out="'{:g}'.format(line.product_qty)"/>
                    </td>
                    <td style="padding:4px 0 4px 8px;vertical-align:top;">
                        <t t-out="line.product_uom_id.name or ''"/>
                    </td>
                </tr>
            </t>
        </tbody>
    </table>
    <p style="margin:16px 0 0 0;">
        С уважением
        <t t-out="object.user_id.name or ''"/>
        ООО &quot;Теплосервис-Комплект&quot;
    </p>
</div>
"""


class PurchaseOrderExt(models.Model):
    _inherit = "purchase.order"

    is_object_request_purchase = fields.Boolean(
        string="Закупка по требованию",
        default=False,
        index=True,
    )
    object_request_project_id = fields.Many2one(
        "object.request.project",
        string="Объект требования",
        index=True,
    )
    dest_warehouse_id = fields.Many2one(
        related="picking_type_id.warehouse_id",
        string="Склад",
        readonly=True,
    )
    # Reverse side of object.request.purchase_order_ids many2many
    object_request_ids = fields.Many2many(
        "object.request",
        "object_request_purchase_order_rel",
        "purchase_id",
        "request_id",
        string="Требования на комплектацию",
    )
    object_request_count = fields.Integer(
        compute="_compute_object_request_count",
        string="Требований",
    )

    def _compute_object_request_count(self):
        for rec in self:
            rec.object_request_count = len(rec.object_request_ids)

    def _get_transfer_report_filename(self):
        self.ensure_one()
        warehouse = (
            self.object_request_project_id.warehouse_id
            or self.picking_type_id.warehouse_id
        )
        suffix = (
            warehouse.display_name
            or self.object_request_project_id.display_name
        )
        invoice_ref = self.partner_ref or self.name
        return "Передаточная ведомость №%s%s" % (
            invoice_ref or "",
            " %s" % suffix if suffix else "",
        )

    def get_transfer_delivery_address_display(self):
        """Текст адреса доставки для передаточной ведомости."""
        self.ensure_one()
        if self.dest_address_id:
            partner = self.dest_address_id
            return partner.contact_address or partner.display_name
        project = self.object_request_project_id
        if not project and self.object_request_ids:
            project = self.object_request_ids[:1].project_id
        if not project:
            return False
        return (project.address or project.name or "").strip() or False

    def action_open_object_requests(self):
        self.ensure_one()
        if len(self.object_request_ids) == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Требование на комплектацию",
                "res_model": "object.request",
                "res_id": self.object_request_ids[0].id,
                "view_mode": "form",
                "target": "current",
            }
        return {
            "type": "ir.actions.act_window",
            "name": "Требования на комплектацию",
            "res_model": "object.request",
            "view_mode": "list,form",
            "domain": [("id", "in", self.object_request_ids.ids)],
            "target": "current",
        }

    @api.model
    def _setup_rfq_copy_mail_template(self):
        """Копия заявки на партнёра компании (675001@mail.ru на prod)."""
        template = self.env.ref(
            "purchase.email_template_edi_purchase",
            raise_if_not_found=False,
        )
        if not template:
            return
        template.write(
            {
                "use_default_to": False,
                "partner_to": (
                    "{{ object.partner_id.id }},"
                    "{{ object.company_id.partner_id.id }}"
                ),
                "body_html": RFQ_MAIL_BODY_HTML,
            }
        )

    def _message_get_default_recipients(self, *args, **kwargs):
        result = super()._message_get_default_recipients(*args, **kwargs)
        for order in self:
            copy_partner = order.company_id.partner_id
            if not copy_partner.email:
                continue
            values = result.get(order.id)
            if not values:
                continue
            partner_ids = list(values.get("partner_ids") or [])
            if copy_partner.id not in partner_ids:
                partner_ids.append(copy_partner.id)
            values["partner_ids"] = partner_ids
        return result

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=False):
        """RFQ: не вставлять «Посмотреть предложение» и ссылку /my/purchase/."""
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups
        self.ensure_one()
        if self.state not in ("draft", "sent"):
            return groups
        for _name, _func, opts in groups:
            opts["has_button_access"] = False
        return groups

    def _notify_by_email_prepare_rendering_context(
        self,
        message,
        msg_vals=False,
        model_description=False,
        force_email_company=False,
        force_email_lang=False,
        force_record_name=False,
    ):
        """RFQ: без номера P00xxx и срока рядом с кнопкой портала."""
        render_context = super()._notify_by_email_prepare_rendering_context(
            message,
            msg_vals=msg_vals,
            model_description=model_description,
            force_email_company=force_email_company,
            force_email_lang=force_email_lang,
            force_record_name=force_record_name,
        )
        if self.state in ("draft", "sent"):
            render_context["subtitles"] = []
        return render_context
