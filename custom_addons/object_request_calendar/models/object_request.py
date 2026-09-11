from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models


class ObjectRequest(models.Model):
    _inherit = "object.request"

    _CALENDAR_WORK_SLOTS = ((9, 10), (10, 11), (11, 12),
                            (13, 14), (14, 15), (15, 16))
    _CALENDAR_SEARCH_DAYS = 30

    calendar_event_ids = fields.One2many(
        "calendar.event",
        "object_request_id",
        string="Встречи",
    )
    calendar_event_count = fields.Integer(
        string="Количество встреч",
        compute="_compute_calendar_event_count",
    )

    @api.depends("calendar_event_ids")
    def _compute_calendar_event_count(self):
        for request in self:
            request.calendar_event_count = len(request.calendar_event_ids)

    @api.model
    def _calendar_local_datetime_to_utc(self, value, timezone):
        localized = timezone.localize(value)
        return localized.astimezone(pytz.UTC).replace(tzinfo=None)

    def _calendar_slot_bounds(
        self, slot_date, start_hour, stop_hour, timezone
    ):
        start = self._calendar_local_datetime_to_utc(
            datetime.combine(slot_date, time(hour=start_hour)), timezone
        )
        stop = self._calendar_local_datetime_to_utc(
            datetime.combine(slot_date, time(hour=stop_hour)), timezone
        )
        return start, stop

    def _calendar_event_blocks_slot(
        self, event, buyer, slot_date, start, stop
    ):
        if event.allday:
            overlaps = event.start_date <= slot_date <= event.stop_date
        else:
            overlaps = event.start < stop and event.stop > start
        if not overlaps:
            return False
        if event.user_id == buyer:
            return True
        buyer_attendees = event.attendee_ids.filtered(
            lambda attendee: attendee.partner_id == buyer.partner_id
        )
        return any(
            attendee.state != "declined" for attendee in buyer_attendees
        )

    def _find_free_calendar_slot(self, company):
        """Return ``(start, stop, forced)`` using naive UTC datetimes."""
        self.ensure_one()
        timezone = pytz.timezone(company.partner_id.tz or "UTC")
        need_date = fields.Date.to_date(self.need_date)

        if not self.buyer_user_id:
            start, stop = self._calendar_slot_bounds(
                need_date, 9, 10, timezone
            )
            return start, stop, False

        horizon_end = need_date + timedelta(days=self._CALENDAR_SEARCH_DAYS)
        query_start, _unused = self._calendar_slot_bounds(
            need_date, 0, 1, timezone
        )
        query_stop, _unused = self._calendar_slot_bounds(
            horizon_end + timedelta(days=1), 0, 1, timezone
        )
        buyer = self.buyer_user_id
        events = self.env["calendar.event"].search([
            ("active", "=", True),
            ("show_as", "=", "busy"),
            "|",
            ("user_id", "=", buyer.id),
            ("partner_ids", "in", buyer.partner_id.ids),
            ("start", "<", query_stop),
            ("stop", ">", query_start),
        ])

        current_date = need_date
        while current_date <= horizon_end:
            if current_date.weekday() < 5:
                for start_hour, stop_hour in self._CALENDAR_WORK_SLOTS:
                    start, stop = self._calendar_slot_bounds(
                        current_date, start_hour, stop_hour, timezone
                    )
                    if not any(
                        self._calendar_event_blocks_slot(
                            event, buyer, current_date, start, stop
                        )
                        for event in events
                    ):
                        return start, stop, False
            current_date += timedelta(days=1)

        fallback_date = horizon_end + timedelta(days=1)
        while fallback_date.weekday() >= 5:
            fallback_date += timedelta(days=1)
        start, stop = self._calendar_slot_bounds(
            fallback_date, 9, 10, timezone
        )
        return start, stop, True

    def action_open_calendar_events(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Встречи",
            "res_model": "calendar.event",
            "view_mode": "calendar,list,form",
            "domain": [("id", "in", self.calendar_event_ids.ids)],
            "context": {
                "default_object_request_id": self.id,
            },
        }
