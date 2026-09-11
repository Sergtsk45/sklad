from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo import Command, SUPERUSER_ID, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import AccessError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPaidBillCalendar(AccountTestInvoicingCommon):
    """Paid vendor bill -> object request calendar event integration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            user=SUPERUSER_ID,
            context=dict(
                cls.env.context,
                tracking_disable=True,
                mail_notrack=True,
                mail_create_nolog=True,
            ),
        )
        cls.company = cls.env.company
        cls.company.partner_id.tz = "UTC"
        cls.buyer = cls.env.ref("base.user_admin")
        cls.foreman = cls.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "Calendar test foreman",
            "login": "calendar-test-foreman",
            "email": "calendar-test-foreman@example.com",
            "company_id": cls.company.id,
            "company_ids": [Command.set(cls.company.ids)],
            "group_ids": [Command.set([
                cls.env.ref("base.group_user").id,
                cls.env.ref("account.group_account_invoice").id,
                cls.env.ref("purchase.group_purchase_user").id,
            ])],
        })
        cls.project = cls.env["object.request.project"].create({
            "name": "Calendar integration test project",
        })
        cls.vendor = cls.env["res.partner"].create({
            "name": "Calendar test vendor",
            "supplier_rank": 1,
        })
        cls.po = cls.env["purchase.order"].create({
            "partner_id": cls.vendor.id,
            "company_id": cls.company.id,
            "order_line": [Command.create({
                "name": "Calendar test product",
                "product_id": cls.product_a.id,
                "product_qty": 1.0,
                "product_uom_id": cls.product_a.uom_id.id,
                "price_unit": 100.0,
            })],
        })

    def _create_request(self, need_date="2026-08-10", buyer=True, po=None):
        vals = {
            "project_id": self.project.id,
            "foreman_user_id": self.foreman.id,
            "buyer_user_id": self.buyer.id if buyer else False,
            "need_date": need_date,
            "company_id": self.company.id,
        }
        if po is not False:
            vals["purchase_order_ids"] = [Command.set((po or self.po).ids)]
        return self.env["object.request"].create(vals)

    def _create_bill(self, po=None, post=False):
        po = po or self.po
        return self._create_invoice(
            move_type="in_invoice",
            partner_id=self.vendor,
            invoice_line_ids=[self._prepare_invoice_line(
                product_id=self.product_a,
                price_unit=100.0,
                purchase_line_id=po.order_line,
            )],
            post=post,
        )

    def _create_event(
        self,
        start,
        stop,
        *,
        organizer=None,
        attendee=None,
        show_as="busy",
        active=True,
    ):
        organizer = organizer or self.buyer
        partners = (attendee or organizer).partner_id
        return self.env["calendar.event"].with_context(
            no_mail_to_attendees=True
        ).create({
            "name": "Existing calendar event",
            "start": start,
            "stop": stop,
            "user_id": organizer.id,
            "partner_ids": [Command.set(partners.ids)],
            "show_as": show_as,
            "active": active,
        })

    def _slot(self, request):
        return request._find_free_calendar_slot(self.company)

    def _assert_slot(self, request, start, stop, forced=False):
        actual_start, actual_stop, actual_forced = self._slot(request)
        self.assertEqual(actual_start, fields.Datetime.to_datetime(start))
        self.assertEqual(actual_stop, fields.Datetime.to_datetime(stop))
        self.assertEqual(actual_forced, forced)

    def _pay(self, bill):
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({})
        payment = wizard._create_payments()
        # TransactionCase never commits. Running the hooks explicitly exercises
        # the same callback used immediately before a real transaction commit.
        self.env.cr.precommit.run()
        bill.invalidate_recordset()
        return payment

    def test_resolver_finds_request_through_purchase_line(self):
        request = self._create_request()
        bill = self._create_bill()

        self.assertEqual(bill._get_object_requests(), request)

    def test_resolver_returns_all_requests_and_ignores_unrelated(self):
        requests = self._create_request() | self._create_request()
        unrelated_po = self.env["purchase.order"].create({
            "partner_id": self.vendor.id,
            "company_id": self.company.id,
        })
        self._create_request(po=unrelated_po)
        bill = self._create_bill()

        self.assertEqual(bill._get_object_requests(), requests)

    def test_resolver_without_purchase_line_is_empty(self):
        bill = self._create_invoice_one_line(
            move_type="in_invoice",
            partner_id=self.vendor,
            product_id=self.product_a,
            price_unit=100.0,
        )

        self.assertFalse(bill._get_object_requests())

    def test_resolver_uses_sudo_for_user_without_request_access(self):
        request = self._create_request()
        bill = self._create_bill()

        with self.assertRaises(AccessError):
            self.env["object.request"].with_user(self.foreman).search([])
        self.assertEqual(
            bill.with_user(self.foreman)._get_object_requests(),
            request,
        )

    def test_first_slot_on_free_day(self):
        request = self._create_request()

        self._assert_slot(
            request, "2026-08-10 09:00:00", "2026-08-10 10:00:00"
        )

    def test_busy_slot_uses_next_slot(self):
        request = self._create_request()
        self._create_event(
            datetime(2026, 8, 10, 9), datetime(2026, 8, 10, 10)
        )

        self._assert_slot(
            request, "2026-08-10 10:00:00", "2026-08-10 11:00:00"
        )

    def test_free_event_does_not_block_slot(self):
        request = self._create_request()
        self._create_event(
            datetime(2026, 8, 10, 9),
            datetime(2026, 8, 10, 10),
            show_as="free",
        )

        self._assert_slot(
            request, "2026-08-10 09:00:00", "2026-08-10 10:00:00"
        )

    def test_partial_overlap_blocks_slot_and_lunch_is_skipped(self):
        request = self._create_request()
        self._create_event(
            datetime(2026, 8, 10, 8, 55), datetime(2026, 8, 10, 10, 5)
        )
        self._create_event(
            datetime(2026, 8, 10, 10, 30), datetime(2026, 8, 10, 11, 5)
        )

        self._assert_slot(
            request, "2026-08-10 13:00:00", "2026-08-10 14:00:00"
        )

    def test_full_friday_moves_to_monday(self):
        request = self._create_request(need_date="2026-08-14")
        self._create_event(
            datetime(2026, 8, 14, 9), datetime(2026, 8, 14, 16)
        )

        self._assert_slot(
            request, "2026-08-17 09:00:00", "2026-08-17 10:00:00"
        )

    def test_all_day_event_blocks_whole_day(self):
        request = self._create_request()
        self.env["calendar.event"].with_context(
            no_mail_to_attendees=True
        ).create({
            "name": "All day",
            "allday": True,
            "start": datetime(2026, 8, 10, 8),
            "stop": datetime(2026, 8, 10, 18),
            "start_date": date(2026, 8, 10),
            "stop_date": date(2026, 8, 10),
            "user_id": self.buyer.id,
            "partner_ids": [Command.set(self.buyer.partner_id.ids)],
            "show_as": "busy",
        })

        self._assert_slot(
            request, "2026-08-11 09:00:00", "2026-08-11 10:00:00"
        )

    def test_declined_attendee_does_not_block(self):
        request = self._create_request()
        attendee_event = self._create_event(
            datetime(2026, 8, 10, 9),
            datetime(2026, 8, 10, 10),
            organizer=self.foreman,
            attendee=self.buyer,
        )
        attendee_event.attendee_ids.filtered(
            lambda attendee: attendee.partner_id == self.buyer.partner_id
        ).state = "declined"

        self._assert_slot(
            request, "2026-08-10 09:00:00", "2026-08-10 10:00:00"
        )

    def test_declined_organizer_still_blocks(self):
        request = self._create_request()
        organizer_event = self._create_event(
            datetime(2026, 8, 10, 9), datetime(2026, 8, 10, 10)
        )
        organizer_event.attendee_ids.filtered(
            lambda attendee: attendee.partner_id == self.buyer.partner_id
        ).state = "declined"

        self._assert_slot(
            request, "2026-08-10 10:00:00", "2026-08-10 11:00:00"
        )

    def test_archived_event_does_not_block(self):
        request = self._create_request()
        self._create_event(
            datetime(2026, 8, 10, 9),
            datetime(2026, 8, 10, 10),
            active=False,
        )

        self._assert_slot(
            request, "2026-08-10 09:00:00", "2026-08-10 10:00:00"
        )

    def test_request_without_buyer_keeps_weekend_need_date(self):
        request = self._create_request(need_date="2026-08-15", buyer=False)

        self._assert_slot(
            request, "2026-08-15 09:00:00", "2026-08-15 10:00:00"
        )

    def test_past_need_date_is_not_moved_to_today(self):
        request = self._create_request(need_date="2025-01-06")

        self._assert_slot(
            request, "2025-01-06 09:00:00", "2025-01-06 10:00:00"
        )

    def test_timezone_is_converted_to_utc_and_empty_timezone_falls_back(self):
        request = self._create_request()
        self.company.partner_id.tz = "Asia/Yakutsk"
        self._assert_slot(
            request, "2026-08-10 00:00:00", "2026-08-10 01:00:00"
        )

        self.company.partner_id.tz = False
        self._assert_slot(
            request, "2026-08-10 09:00:00", "2026-08-10 10:00:00"
        )

    def test_horizon_fallback_is_forced_on_first_weekday_after_30_days(self):
        request = self._create_request()
        # A single long busy event is enough to cover every candidate slot.
        self._create_event(
            datetime(2026, 8, 10), datetime(2026, 9, 10, 23, 59)
        )

        start, stop, forced = self._slot(request)
        self.assertTrue(forced)
        self.assertEqual(start.hour, 9)
        self.assertEqual(stop - start, timedelta(hours=1))
        self.assertGreater((start.date() - request.need_date).days, 30)
        self.assertLess(start.weekday(), 5)

    def test_real_payment_register_creates_traced_event_once(self):
        request = self._create_request()
        bill = self._create_bill(post=True)

        self._pay(bill)

        events = self.env["calendar.event"].search([
            ("source_bill_id", "=", bill.id),
            ("object_request_id", "=", request.id),
        ])
        self.assertEqual(bill.payment_state, "paid")
        self.assertEqual(len(events), 1)
        self.assertEqual(events.name, f"Оплата {bill.name} — {request.name}")
        self.assertEqual(events.start, datetime(2026, 8, 10, 9))
        self.assertEqual(events.stop, datetime(2026, 8, 10, 10))
        self.assertEqual(events.user_id, self.buyer)
        self.assertEqual(
            events.partner_ids,
            self.buyer.partner_id | self.foreman.partner_id,
        )

        bill._create_paid_bill_calendar_events()
        self.assertEqual(
            self.env["calendar.event"].search_count([
                ("source_bill_id", "=", bill.id),
                ("object_request_id", "=", request.id),
            ]),
            1,
        )

    def test_one_bill_creates_sequential_events_for_multiple_requests(self):
        requests = self._create_request() | self._create_request()
        bill = self._create_bill(post=True)

        self._pay(bill)

        events = self.env["calendar.event"].search([
            ("source_bill_id", "=", bill.id),
            ("object_request_id", "in", requests.ids),
        ], order="start")
        self.assertEqual(len(events), 2)
        self.assertEqual(
            events.mapped("start"),
            [datetime(2026, 8, 10, 9), datetime(2026, 8, 10, 10)],
        )

    def test_paid_bill_without_request_is_safely_ignored(self):
        bill = self._create_invoice_one_line(
            move_type="in_invoice",
            partner_id=self.vendor,
            product_id=self.product_a,
            price_unit=100.0,
            post=True,
        )

        self._pay(bill)

        self.assertFalse(self.env["calendar.event"].search([
            ("source_bill_id", "=", bill.id),
        ]))
        self.assertTrue(bill.message_ids)

    def test_precommit_rechecks_that_bill_is_still_paid(self):
        request = self._create_request()
        bill = self._create_bill(post=True)

        bill._queue_paid_bill_calendar_events([bill.id])
        self.env.cr.precommit.run()

        self.assertEqual(bill.payment_state, "not_paid")
        self.assertFalse(self.env["calendar.event"].search([
            ("source_bill_id", "=", bill.id),
            ("object_request_id", "=", request.id),
        ]))

    def test_auto_create_suppresses_only_initial_attendee_email(self):
        request = self._create_request()
        bill = self._create_bill(post=True)
        notification_contexts = []
        attendee_model = type(self.env["calendar.attendee"])

        def fake_notify(attendees, *args, **kwargs):
            notification_contexts.append(
                bool(attendees.env.context.get("no_mail_to_attendees"))
            )
            return False

        with patch.object(attendee_model, "_notify_attendees", fake_notify):
            self._pay(bill)
            event = self.env["calendar.event"].search([
                ("source_bill_id", "=", bill.id),
                ("object_request_id", "=", request.id),
            ])
            event.with_context(no_mail_to_attendees=False).write({
                "start": event.start + timedelta(hours=1),
            })

        self.assertTrue(notification_contexts)
        self.assertTrue(notification_contexts[0])
        self.assertFalse(notification_contexts[-1])
