"""Product variant search v2 extension."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain

from .product_search_utils import normalize_product_search_text


SMART_NAME_SEARCH_OPERATORS = ('ilike',)
AI_SEARCH_MAX_LIMIT = 100
AI_EXACT_MIN_SCORE = 1.0


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'product.search.mixin']

    x_search_name = fields.Char(
        string='Normalized Search Name',
        compute='_compute_x_search_name',
        store=True,
        index=True,
    )

    @api.depends('name', 'product_template_attribute_value_ids.name')
    def _compute_x_search_name(self):
        """Compute normalized search text from name and variant values."""
        for product in self:
            product.x_search_name = normalize_product_search_text(
                product._get_variant_search_name(),
            )

    @api.depends(
        'name',
        'default_code',
        'product_template_attribute_value_ids.name',
    )
    def _compute_x_search_tokens(self):
        """Compute search tokens from name, variant values and code."""
        return super()._compute_x_search_tokens()

    def _get_variant_search_name(self):
        self.ensure_one()
        variant = (
            self.product_template_attribute_value_ids._get_combination_name()
        )
        return f'{self.name} {variant}' if variant else (self.name or '')

    def _get_search_tokens_source(self):
        self.ensure_one()
        return f'{self._get_variant_search_name()} {self.default_code or ""}'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Rank products by search tokens, then append standard matches.

        Exact internal code, barcode and supplier code come first; the
        standard Odoo lookup fills the rest of the limit.
        """
        if not name or operator not in SMART_NAME_SEARCH_OPERATORS:
            return super().name_search(name, domain, operator, limit)

        base_domain = Domain(domain or Domain.TRUE)
        return self._smart_name_search(
            name,
            base_domain,
            limit,
            self._get_exact_code_product_ids(name, base_domain),
            lambda standard_domain, remaining: super(
                ProductProduct, self,
            ).name_search(name, standard_domain, operator, remaining),
        )

    @api.model
    def _get_exact_code_product_ids(self, query, domain=None):
        """Return ids whose internal, bar or supplier code equals ``query``."""
        query = query.strip()
        code_domains = [
            Domain('default_code', '=ilike', query),
            Domain('barcode', '=', query),
        ]
        skip_supplier_search = self.env.context.get(
            'object_request_skip_global_supplier_search'
        )
        if not skip_supplier_search:
            code_domains.append(Domain(
                'product_tmpl_id.seller_ids.product_code', '=ilike', query,
            ))
        search_domain = Domain(domain or Domain.TRUE) & Domain.OR(code_domains)
        return self.search(search_domain).ids

    @api.model
    def ai_search_products(
        self,
        query,
        limit=20,
        warehouse_id=None,
        only_available=False,
    ):
        """Return product data for AI using normal Odoo access rules.

        Every query word must match, including words unknown to the catalog:
        callers auto-select a single result. ``match_type`` is ``exact``
        without typo tolerance, ``morphology`` when a word matched only
        approximately and needs explicit confirmation.
        """
        if not query:
            return []

        product_model = self._with_ai_search_warehouse(warehouse_id)
        search_limit = self._sanitize_ai_search_limit(limit)
        domain = Domain.TRUE
        if only_available:
            domain = Domain('qty_available', '>', 0)

        product_ids, match_type = product_model._get_ai_search_product_ids(
            query, domain, search_limit,
        )
        products = product_model.browse(product_ids[:search_limit])
        result = products.read([
            'id',
            'display_name',
            'default_code',
            'barcode',
            'qty_available',
            'uom_id',
        ])
        for item in result:
            item['match_type'] = match_type
        return result

    @api.model
    def _get_ai_search_product_ids(self, query, domain, limit):
        """Return (ids, match_type): exact words first, then typo-tolerant."""
        product_ids = self._get_exact_code_product_ids(query, domain)
        product_ids += [
            product_id
            for product_id in self._smart_search_ids(
                query, domain, limit,
                min_score=AI_EXACT_MIN_SCORE, keep_unknown=True,
            )
            if product_id not in product_ids
        ]
        if product_ids:
            return product_ids, 'exact'
        return self._smart_search_ids(
            query, domain, limit, strict=True, keep_unknown=True,
        ), 'morphology'

    @api.model
    def _sanitize_ai_search_limit(self, limit):
        try:
            sanitized_limit = int(limit)
        except (TypeError, ValueError):
            sanitized_limit = 20
        return max(1, min(sanitized_limit, AI_SEARCH_MAX_LIMIT))

    @api.model
    def _with_ai_search_warehouse(self, warehouse_id):
        if not warehouse_id:
            return self

        try:
            warehouse = (
                self.env['stock.warehouse']
                .browse(int(warehouse_id))
                .exists()
            )
        except (TypeError, ValueError):
            raise UserError(_('Invalid warehouse identifier.')) from None

        if not warehouse:
            raise UserError(_('Warehouse not found.'))

        warehouse.check_access('read')
        return self.with_context(warehouse_id=warehouse.id)
