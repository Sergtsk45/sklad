"""Product variant normalized search extension."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain

from .product_search_utils import normalize_product_search_text


POSITIVE_NAME_SEARCH_OPERATORS = ('=', 'ilike', '=ilike', 'like', '=like')
AI_SEARCH_MAX_LIMIT = 100


class ProductProduct(models.Model):
    _inherit = 'product.product'

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
            variant = (
                product.product_template_attribute_value_ids
                ._get_combination_name()
            )
            if variant:
                search_name = f'{product.name} {variant}'
            else:
                search_name = product.name
            product.x_search_name = normalize_product_search_text(search_name)

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Extend Odoo 19 product lookup with normalized product search."""
        if not name or operator in Domain.NEGATIVE_OPERATORS:
            return super().name_search(name, domain, operator, limit)

        standard_results = super().name_search(name, domain, operator, limit)
        if operator not in POSITIVE_NAME_SEARCH_OPERATORS:
            return standard_results

        remaining_limit = self._get_remaining_search_limit(
            limit,
            standard_results,
        )
        if remaining_limit == 0:
            return standard_results

        normalized_domain = self._get_normalized_product_search_domain(
            name,
            operator,
        )
        if normalized_domain.is_false():
            return standard_results

        base_domain = Domain(domain or Domain.TRUE)
        standard_ids = [
            product_id
            for product_id, _display_name in standard_results
        ]
        search_domain = base_domain & normalized_domain
        if standard_ids:
            search_domain &= Domain('id', 'not in', standard_ids)

        products = self.search_fetch(
            search_domain,
            ['display_name'],
            limit=remaining_limit,
        )
        custom_results = [
            (product.id, product.display_name)
            for product in products.sudo()
        ]
        return standard_results + custom_results

    @api.model
    def ai_search_products(
        self,
        query,
        limit=20,
        warehouse_id=None,
        only_available=False,
    ):
        """Return product data for AI using normal Odoo access rules."""
        if not query:
            return []

        product_model = self._with_ai_search_warehouse(warehouse_id)
        search_limit = self._sanitize_ai_search_limit(limit)
        search_domain = product_model._get_normalized_product_search_domain(
            query,
            'ilike',
        )
        if only_available:
            search_domain &= Domain('qty_available', '>', 0)

        products = product_model.search(search_domain, limit=search_limit)
        return products.read([
            'id',
            'display_name',
            'default_code',
            'barcode',
            'qty_available',
            'uom_id',
        ])

    @api.model
    def _get_normalized_product_search_domain(self, query, operator='ilike'):
        normalized = normalize_product_search_text(query)
        if not normalized:
            return Domain.FALSE

        search_domains = [
            Domain('default_code', operator, query),
            Domain('barcode', '=', query),
            Domain('name', operator, query),
            Domain('x_search_name', 'ilike', normalized),
            Domain('product_tmpl_id.x_search_name', 'ilike', normalized),
        ]

        token_domain = self._get_normalized_token_search_domain(normalized)
        if not token_domain.is_false():
            search_domains.append(token_domain)

        return Domain.OR(search_domains)

    @api.model
    def _get_normalized_token_search_domain(self, normalized_query):
        tokens = normalized_query.split()
        if len(tokens) <= 1:
            return Domain.FALSE

        product_token_domain = Domain.AND([
            Domain('x_search_name', 'ilike', token)
            for token in tokens
        ])
        template_token_domain = Domain.AND([
            Domain('product_tmpl_id.x_search_name', 'ilike', token)
            for token in tokens
        ])
        return Domain.OR([product_token_domain, template_token_domain])

    @api.model
    def _get_remaining_search_limit(self, limit, results):
        if limit is None:
            return None
        return max(limit - len(results), 0)

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
