# -*- coding: utf-8 -*-
"""
@file: product_vendor_search.py
@description: Поиск товара в OR: с поставщиком — только его прайс и торговые имена.
@dependencies: product, product.supplierinfo, custom_product_search
@created: 2026-08-10
"""

from odoo import api, models
from odoo.fields import Domain

CTX_PREFERRED_VENDOR = "object_request_preferred_vendor_id"
POSITIVE_OPS = ("=", "ilike", "=ilike", "like", "=like")


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        vendor_id = self._or_preferred_vendor_id_from_context()
        search_domain = Domain(domain or Domain.TRUE)
        if vendor_id:
            search_domain &= Domain("seller_ids.partner_id", "=", vendor_id)

        results = super().name_search(
            name,
            search_domain,
            operator,
            limit,
        )
        if not vendor_id or not name or operator not in POSITIVE_OPS:
            return results

        remaining = self._or_remaining_name_search_limit(limit, results)
        if remaining == 0:
            return results

        vendor_hits = self._or_search_by_vendor_trade_name(
            name,
            operator,
            vendor_id,
            exclude_ids=[row[0] for row in results],
            limit=remaining,
        )
        return results + vendor_hits

    @api.model
    def _or_preferred_vendor_id_from_context(self):
        raw = self.env.context.get(CTX_PREFERRED_VENDOR)
        if not raw:
            return False
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else False
        try:
            return int(raw)
        except (TypeError, ValueError):
            return False

    @api.model
    def _or_remaining_name_search_limit(self, limit, results):
        if limit is None:
            return None
        return max(limit - len(results), 0)

    @api.model
    def _or_search_by_vendor_trade_name(
        self,
        name,
        operator,
        vendor_id,
        exclude_ids=None,
        limit=None,
    ):
        """Find variants by supplier product_name / product_code for vendor."""
        infos = self.env["product.supplierinfo"].search(
            [
                ("partner_id", "=", vendor_id),
                "|",
                ("product_name", operator, name),
                ("product_code", operator, name),
            ],
        )
        if not infos:
            return []

        tmpl_ids = infos.mapped("product_tmpl_id").ids
        product_domain = Domain("product_tmpl_id", "in", tmpl_ids)
        product_domain &= Domain("seller_ids.partner_id", "=", vendor_id)
        if exclude_ids:
            product_domain &= Domain("id", "not in", exclude_ids)

        products = self.search_fetch(
            product_domain,
            ["display_name", "product_tmpl_id"],
            limit=limit,
        )
        info_by_tmpl = {
            info.product_tmpl_id.id: info
            for info in infos
            if info.product_tmpl_id
        }
        rows = []
        for product in products:
            info = info_by_tmpl.get(product.product_tmpl_id.id)
            label = product.display_name
            if info and info.product_name:
                label = f"{product.display_name} — {info.product_name}"
            rows.append((product.id, label))
        return rows
