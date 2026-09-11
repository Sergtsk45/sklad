from markupsafe import Markup

from odoo import api, models, _
from odoo.fields import Command

_PRECOMMIT_KEY = "object_request_calendar.paid_bill_ids"


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        "amount_residual",
        "move_type",
        "state",
        "company_id",
        "reconciled_payment_ids.state",
    )
    def _compute_payment_state(self):
        previous_states = {
            move.id: move.payment_state
            for move in self
            if isinstance(move.id, int)
        }
        super()._compute_payment_state()
        paid_bill_ids = [
            move.id
            for move in self
            if isinstance(move.id, int)
            and move.move_type == "in_invoice"
            and previous_states.get(move.id) != "paid"
            and move.payment_state == "paid"
        ]
        if paid_bill_ids:
            self._queue_paid_bill_calendar_events(paid_bill_ids)

    @api.model
    def _queue_paid_bill_calendar_events(self, bill_ids):
        precommit_data = self.env.cr.precommit.data
        if _PRECOMMIT_KEY not in precommit_data:
            precommit_data[_PRECOMMIT_KEY] = set()
            self.env.cr.precommit.add(
                self._process_queued_paid_bill_calendar_events
            )
        precommit_data[_PRECOMMIT_KEY].update(bill_ids)

    @api.model
    def _process_queued_paid_bill_calendar_events(self):
        bill_ids = self.env.cr.precommit.data.get(_PRECOMMIT_KEY, set())
        while bill_ids:
            self.env.flush_all()
            current_ids = tuple(bill_ids)
            bill_ids.difference_update(current_ids)
            self.env.cr.execute(
                """
                    SELECT id
                      FROM account_move
                     WHERE id = ANY(%s)
                       AND move_type = 'in_invoice'
                       AND payment_state = 'paid'
                """,
                (list(current_ids),),
            )
            paid_bills = self.browse(
                [row[0] for row in self.env.cr.fetchall()]
            ).exists()
            paid_bills._create_paid_bill_calendar_events()

    def _get_object_requests(self):
        self.ensure_one()
        purchase_orders = self.invoice_line_ids.purchase_line_id.order_id
        if not purchase_orders:
            return self.env["object.request"].sudo().browse()
        return self.env["object.request"].sudo().search([
            ("purchase_order_ids", "in", purchase_orders.ids),
            ("company_id", "=", self.company_id.id),
        ], order="id")

    def _prepare_paid_bill_calendar_event_values(self, request):
        self.ensure_one()
        start, stop, forced = request._find_free_calendar_slot(self.company_id)
        partners = request.buyer_user_id.partner_id
        partners |= request.foreman_user_id.partner_id
        organizer = request.buyer_user_id or self.env.user
        description = Markup(
            "<p>Счёт поставщика: %(bill)s<br/>"
            "Сумма: %(amount)s %(currency)s<br/>"
            "Требование: %(request)s</p>"
        ) % {
            "bill": self._get_html_link(),
            "amount": self.amount_total,
            "currency": self.currency_id.name,
            "request": request._get_html_link(),
        }
        return {
            "name": _(
                "Оплата %(bill)s — %(request)s",
                bill=self.name,
                request=request.name,
            ),
            "description": description,
            "start": start,
            "stop": stop,
            "duration": 1.0,
            "allday": False,
            "show_as": "busy",
            "user_id": organizer.id,
            "partner_ids": [Command.set(partners.ids)],
            "object_request_id": request.id,
            "source_bill_id": self.id,
        }, forced

    def _create_paid_bill_calendar_events(self):
        CalendarEvent = self.env["calendar.event"]
        for bill in self:
            if bill.move_type != "in_invoice" or bill.payment_state != "paid":
                continue
            requests = bill._get_object_requests()
            if not requests:
                bill.message_post(
                    body=_(
                        "Для оплаченного счёта поставщика не найдено "
                        "связанное "
                        "требование. Встреча не создана."
                    ),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
                continue

            for request in requests:
                self.env.cr.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (
                        "object_request_calendar:%s:%s"
                        % (bill.id, request.id),
                    ),
                )
                duplicate = CalendarEvent.search_count([
                    ("object_request_id", "=", request.id),
                    ("source_bill_id", "=", bill.id),
                ], limit=1)
                if duplicate:
                    continue
                values, forced = bill._prepare_paid_bill_calendar_event_values(
                    request
                )
                event = CalendarEvent.with_context(
                    no_mail_to_attendees=True
                ).create(values)

                fallback_note = ""
                if forced:
                    fallback_note = _(
                        " Свободный слот не найден за 30 календарных дней; "
                        "использован принудительный слот с допустимым "
                        "пересечением."
                    )
                body = Markup(
                    "Встреча %s создана по оплаченному счёту %s.%s"
                ) % (
                    event._get_html_link(),
                    bill._get_html_link(),
                    fallback_note,
                )
                request.message_post(
                    body=body,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
                bill.message_post(
                    body=body,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )

        return True
