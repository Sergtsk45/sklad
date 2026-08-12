# -*- coding: utf-8 -*-
"""
@file: product_vendor_search.py
@description: Поиск товара в OR по прайсу и торговым именам поставщика.
@dependencies: product, product.supplierinfo, custom_product_search
@created: 2026-08-10
"""

from odoo import api, models
from odoo.fields import Domain

CTX_PREFERRED_VENDOR = "object_request_preferred_vendor_id"
CTX_REQUEST_COMPANY = "object_request_company_id"
CTX_SKIP_GLOBAL_SUPPLIER_SEARCH = "object_request_skip_global_supplier_search"
POSITIVE_OPS = ("=", "ilike", "=ilike", "like", "=like")
VENDOR_SEARCH_MAX_LABEL_INFOS = 500


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    @api.readonly
    def web_name_search(
        self,
        name,
        specification,
        domain=None,
        operator="ilike",
        limit=100,
    ):
        vendor_id = self._or_preferred_vendor_id_from_context()
        vendor = self.env["res.partner"].browse(vendor_id).exists()
        if not vendor:
            return super().web_name_search(
                name,
                specification,
                domain=domain,
                operator=operator,
                limit=limit,
            )

        id_name_pairs = self.name_search(name, domain, operator, limit)
        search_labels = dict(id_name_pairs)
        if len(specification) == 1 and "display_name" in specification:
            formatted_products = self.with_context(
                formatted_display_name=True
            ).browse([product_id for product_id, _label in id_name_pairs])
            formatted_names = {
                product.id: product.display_name
                for product in formatted_products
            }
            rows = [
                {
                    "id": product_id,
                    "display_name": label,
                    "__formatted_display_name": formatted_names[product_id],
                }
                for product_id, label in id_name_pairs
            ]
        else:
            records = self.browse(
                [product_id for product_id, _label in id_name_pairs]
            )
            rows = records.web_read(specification)

        if "display_name" not in specification:
            return rows

        product_ids = [row["id"] for row in rows]
        clean_names = {
            product.id: product.display_name
            for product in self.browse(product_ids)
        }
        if len(specification) != 1:
            formatted_names = {
                product.id: product.display_name
                for product in self.with_context(
                    formatted_display_name=True
                ).browse(product_ids)
            }
        prefix = f"[{vendor.display_name}] "
        for row in rows:
            product_id = row["id"]
            clean_name = clean_names[product_id]
            search_label = search_labels.get(product_id, "")
            if search_label.startswith(prefix):
                search_label = search_label[len(prefix):]
            trade_suffix = search_label.removeprefix(clean_name)
            if not trade_suffix.startswith(" — "):
                trade_suffix = ""
            row["display_name"] = clean_name
            row["__formatted_display_name"] = (
                f"{prefix}{formatted_names[product_id]}{trade_suffix}"
            )
        return rows

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        vendor_id = self._or_preferred_vendor_id_from_context()
        if not vendor_id:
            return super().name_search(name, domain, operator, limit)

        search_domain = Domain(domain or Domain.TRUE)
        search_domain &= self._or_vendor_catalog_domain(vendor_id)
        results = super(
            ProductProduct,
            self.with_context(**{CTX_SKIP_GLOBAL_SUPPLIER_SEARCH: True}),
        ).name_search(
            name,
            search_domain,
            operator,
            limit,
        )

        if name and operator in POSITIVE_OPS:
            remaining = self._or_remaining_name_search_limit(limit, results)
            if remaining != 0:
                vendor_hits = self._or_search_by_vendor_trade_name(
                    name,
                    operator,
                    vendor_id,
                    domain=domain,
                    exclude_ids=[row[0] for row in results],
                    limit=remaining,
                )
                results += vendor_hits

        return self._or_add_vendor_to_labels(results, vendor_id)

    @api.model
    def _or_add_vendor_to_labels(self, results, vendor_id):
        vendor = self.env["res.partner"].browse(vendor_id).exists()
        if not vendor:
            return results
        prefix = f"[{vendor.display_name}] "
        return [
            (product_id, f"{prefix}{label}")
            for product_id, label in results
        ]

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
        if limit in (None, 0):
            return None
        return max(limit - len(results), 0)

    @api.model
    def _or_supplierinfo_base_domain(self, vendor_id):
        raw_company_id = self.env.context.get(CTX_REQUEST_COMPANY)
        if isinstance(raw_company_id, (list, tuple)):
            raw_company_id = raw_company_id[0] if raw_company_id else False
        try:
            company_id = int(raw_company_id)
        except (TypeError, ValueError):
            company_id = self.env.company.id
        return [
            ("partner_id", "=", vendor_id),
            ("company_id", "in", [False, company_id]),
        ]

    @api.model
    def _or_vendor_catalog_domain(self, vendor_id):
        """Build an SQL-backed domain with exact supplier variant semantics."""
        SupplierInfo = self.env["product.supplierinfo"]
        base_domain = self._or_supplierinfo_base_domain(vendor_id)
        specific_query = SupplierInfo._search(
            base_domain + [("product_id", "!=", False)]
        )
        global_query = SupplierInfo._search(
            base_domain + [("product_id", "=", False)]
        )
        return Domain.OR(
            [
                Domain("id", "in", specific_query.subselect("product_id")),
                Domain(
                    "product_tmpl_id",
                    "in",
                    global_query.subselect("product_tmpl_id"),
                ),
            ]
        )

    @api.model
    def _or_search_by_vendor_trade_name(
        self,
        name,
        operator,
        vendor_id,
        domain=None,
        exclude_ids=None,
        limit=None,
    ):
        """Find variants by supplier product_name / product_code for vendor."""
        SupplierInfo = self.env["product.supplierinfo"]
        trade_domain = self._or_supplierinfo_base_domain(vendor_id) + [
            "|",
            ("product_name", operator, name),
            ("product_code", operator, name),
        ]
        specific_query = SupplierInfo._search(
            trade_domain + [("product_id", "!=", False)]
        )
        global_query = SupplierInfo._search(
            trade_domain + [("product_id", "=", False)]
        )
        candidate_domain = Domain.OR(
            [
                Domain("id", "in", specific_query.subselect("product_id")),
                Domain(
                    "product_tmpl_id",
                    "in",
                    global_query.subselect("product_tmpl_id"),
                ),
            ]
        )
        product_domain = Domain(domain or Domain.TRUE) & candidate_domain
        if exclude_ids:
            product_domain &= Domain("id", "not in", exclude_ids)

        products = self.search_fetch(
            product_domain,
            ["display_name", "product_tmpl_id"],
            limit=limit,
        )
        if not products:
            return []

        label_domain = trade_domain + [
            "|",
            ("product_id", "in", products.ids),
            "&",
            ("product_id", "=", False),
            ("product_tmpl_id", "in", products.product_tmpl_id.ids),
        ]
        infos = SupplierInfo.search_fetch(
            label_domain,
            ["product_id", "product_tmpl_id", "product_name"],
            limit=VENDOR_SEARCH_MAX_LABEL_INFOS,
        )
        info_by_product = {}
        info_by_tmpl = {}
        for info in infos:
            if info.product_id:
                info_by_product.setdefault(info.product_id.id, info)
            elif info.product_tmpl_id:
                info_by_tmpl.setdefault(info.product_tmpl_id.id, info)

        rows = []
        for product in products:
            info = info_by_product.get(product.id)
            if not info:
                info = info_by_tmpl.get(product.product_tmpl_id.id)
            label = product.display_name
            if info and info.product_name:
                label = f"{product.display_name} — {info.product_name}"
            rows.append((product.id, label))
        return rows
