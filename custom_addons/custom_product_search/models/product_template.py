"""Product template normalized search extension."""

from odoo import api, fields, models

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
