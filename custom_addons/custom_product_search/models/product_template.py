"""Product template search v2 extension."""

from odoo import api, fields, models
from odoo.fields import Domain

from .product_search_utils import normalize_product_search_text


SMART_NAME_SEARCH_OPERATORS = ('ilike',)


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'product.search.mixin']

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

    @api.depends('name', 'default_code')
    def _compute_x_search_tokens(self):
        """Compute search tokens from template name and code."""
        return super()._compute_x_search_tokens()

    def _get_search_tokens_source(self):
        self.ensure_one()
        return f'{self.name or ""} {self.default_code or ""}'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Rank templates by search tokens, then append standard matches."""
        if not name or operator not in SMART_NAME_SEARCH_OPERATORS:
            return super().name_search(name, domain, operator, limit)

        base_domain = Domain(domain or Domain.TRUE)
        return self._smart_name_search(
            name,
            base_domain,
            limit,
            self._get_exact_code_template_ids(name, base_domain),
            lambda standard_domain, remaining: super(
                ProductTemplate, self,
            ).name_search(name, standard_domain, operator, remaining),
        )

    @api.model
    def _get_exact_code_template_ids(self, query, domain=None):
        """Return ids whose internal, bar or supplier code equals ``query``."""
        query = query.strip()
        code_domain = Domain.OR([
            Domain('default_code', '=ilike', query),
            Domain('barcode', '=', query),
            Domain('seller_ids.product_code', '=ilike', query),
        ])
        return self.search(Domain(domain or Domain.TRUE) & code_domain).ids
