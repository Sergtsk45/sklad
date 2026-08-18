# -*- coding: utf-8 -*-
"""
@file: partner_recent_search.py
@description: Недавние поставщики в autocomplete preferred_vendor_id (TD-008).
@dependencies: res.partner, object.request.line, product_vendor_search
@created: 2026-08-19
"""

from odoo import api, models
from odoo.fields import Domain

from odoo.addons.object_request.models.product_vendor_search import (
    CTX_REQUEST_COMPANY,
)

CTX_RECENT_VENDORS = "object_request_recent_vendors"
RECENT_VENDOR_LIMIT = 8
RECENT_VENDOR_SCAN_LIMIT = 200


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        if not self._or_recent_vendors_enabled() or (name or "").strip():
            return super().name_search(name, domain, operator, limit)

        recent_ids = self._or_recent_vendor_ids()
        if not recent_ids:
            return super().name_search(name, domain, operator, limit)
        return self._or_name_search_with_recents(
            recent_ids, name, domain, operator, limit
        )

    @api.model
    def _or_recent_vendors_enabled(self):
        return bool(self.env.context.get(CTX_RECENT_VENDORS))

    @api.model
    def _or_recent_vendor_company_id(self):
        raw = self.env.context.get(CTX_REQUEST_COMPANY)
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else False
        try:
            company_id = int(raw)
        except (TypeError, ValueError):
            return self.env.company.id
        if not company_id:
            return self.env.company.id
        return company_id

    @api.model
    def _or_recent_vendor_ids(self, limit=RECENT_VENDOR_LIMIT):
        rows = self.env["object.request.line"].search_read(
            [
                ("preferred_vendor_id", "!=", False),
                ("company_id", "=", self._or_recent_vendor_company_id()),
            ],
            ["preferred_vendor_id"],
            order="write_date desc, id desc",
            limit=RECENT_VENDOR_SCAN_LIMIT,
        )
        seen = []
        for row in rows:
            vendor = row.get("preferred_vendor_id")
            vendor_id = vendor[0] if vendor else False
            if not vendor_id or vendor_id in seen:
                continue
            seen.append(vendor_id)
            if len(seen) >= limit:
                break
        return seen

    @api.model
    def _or_name_search_with_recents(
        self, recent_ids, name, domain, operator, limit
    ):
        allowed = self.search(
            Domain(domain or Domain.TRUE) & Domain("id", "in", recent_ids)
        )
        allowed_ids = set(allowed.ids)
        ordered = [
            partner_id
            for partner_id in recent_ids
            if partner_id in allowed_ids
        ]
        if limit not in (None, 0):
            ordered = ordered[:limit]
        partners = self.browse(ordered)
        results = [
            (partner.id, partner.display_name) for partner in partners
        ]
        remaining = self._or_remaining_name_search_limit(limit, results)
        if remaining == 0:
            return results
        rest_domain = Domain(domain or Domain.TRUE)
        if ordered:
            rest_domain &= Domain("id", "not in", ordered)
        return results + super().name_search(
            name, rest_domain, operator, remaining
        )

    @api.model
    def _or_remaining_name_search_limit(self, limit, results):
        if limit in (None, 0):
            return None
        return max(limit - len(results), 0)
