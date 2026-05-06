"""Product template normalized search extension."""

from odoo import api, fields, models
from odoo.fields import Domain

from .product_search_utils import normalize_product_search_text


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_search_name = fields.Char(
        string='Normalized Search Name',
        compute='_compute_x_search_name',
        store=True,
        index=True,
    )

    @api.depends('name')
    def _compute_x_search_name(self):
        """Compute normalized search text from product template name."""
        for template in self:
            template.x_search_name = normalize_product_search_text(
                template.name,
            )

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Extend template lookup to support normalized token search."""
        if not name or operator in Domain.NEGATIVE_OPERATORS:
            return super().name_search(name, domain, operator, limit)

        standard_results = super().name_search(name, domain, operator, limit)
        remaining_limit = self._get_remaining_search_limit(
            limit,
            standard_results,
        )
        if remaining_limit == 0:
            return standard_results

        normalized_domain = self._get_normalized_template_search_domain(name)
        if normalized_domain.is_false():
            return standard_results

        base_domain = Domain(domain or Domain.TRUE)
        standard_ids = [
            template_id
            for template_id, _display_name in standard_results
        ]
        search_domain = base_domain & normalized_domain
        if standard_ids:
            search_domain &= Domain('id', 'not in', standard_ids)

        templates = self.search_fetch(
            search_domain,
            ['display_name'],
            limit=remaining_limit,
        )
        custom_results = [
            (template.id, template.display_name)
            for template in templates.sudo()
        ]
        return standard_results + custom_results

    @api.model
    def _get_remaining_search_limit(self, limit, results):
        if limit is None:
            return None
        return max(limit - len(results), 0)

    @api.model
    def _get_normalized_template_search_domain(self, query):
        normalized = normalize_product_search_text(query)
        if not normalized:
            return Domain.FALSE

        domains = [
            Domain('name', 'ilike', query),
            Domain('x_search_name', 'ilike', normalized),
        ]
        if 'default_code' in self._fields:
            domains.append(Domain('default_code', 'ilike', query))
        if 'barcode' in self._fields:
            domains.append(Domain('barcode', '=', query))

        token_domain = self._get_normalized_token_search_domain(normalized)
        if not token_domain.is_false():
            domains.append(token_domain)

        return Domain.OR(domains)

    @api.model
    def _get_normalized_token_search_domain(self, normalized_query):
        tokens = normalized_query.split()
        if len(tokens) <= 1:
            return Domain.FALSE
        return Domain.AND([
            Domain('x_search_name', 'ilike', token)
            for token in tokens
        ])
