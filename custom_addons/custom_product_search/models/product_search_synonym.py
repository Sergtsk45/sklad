"""Editable synonyms for product search v2."""

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from .product_search_synonyms_data import default_synonym_map
from .product_search_utils import normalize_product_search_text


SEEDED_PARAM = 'custom_product_search.synonyms_seeded'


class ProductSearchSynonym(models.Model):
    _name = 'product.search.synonym'
    _description = 'Product Search Synonym'
    _order = 'canonical, term'

    term = fields.Char(
        required=True,
        help='Word as written in requests or product names, e.g. «оцинк».',
    )
    canonical = fields.Char(
        required=True,
        help='Form the word is replaced with, e.g. «оцинкованный».',
    )
    active = fields.Boolean(default=True)

    _term_unique = models.Constraint(
        'unique(term)',
        'A synonym for this word already exists.',
    )

    @api.constrains('term', 'canonical')
    def _check_term(self):
        """Require a single-word term that differs from its canonical form."""
        for synonym in self:
            if len(synonym.term.split()) != 1:
                raise ValidationError(_('The word must be a single word.'))
            if synonym.term == synonym.canonical:
                raise ValidationError(
                    _('The word and its canonical form must differ.')
                )

    @api.model
    def _normalize_vals(self, vals):
        for key in ('term', 'canonical'):
            if vals.get(key):
                vals[key] = normalize_product_search_text(vals[key])
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """Store normalized words and reindex products."""
        records = super().create(
            [self._normalize_vals(dict(vals)) for vals in vals_list]
        )
        self._after_synonyms_changed()
        return records

    def write(self, vals):
        """Store normalized words and reindex products."""
        result = super().write(self._normalize_vals(dict(vals)))
        self._after_synonyms_changed()
        return result

    def unlink(self):
        """Reindex products without the removed synonyms."""
        result = super().unlink()
        self._after_synonyms_changed()
        return result

    @api.model
    @tools.ormcache()
    def _get_synonym_map(self):
        """Return {term: canonical} for active synonyms."""
        records = self.sudo().search_fetch([], ['term', 'canonical'])
        return {record.term: record.canonical for record in records}

    @api.model
    def _after_synonyms_changed(self):
        self.env.registry.clear_cache()
        if self.env.context.get('product_search_skip_reindex'):
            return
        # The whole catalog, not only the companies of the current user.
        self.env['product.template'].sudo()._recompute_search_tokens()
        self.env['product.product'].sudo()._recompute_search_tokens()

    @api.model
    def _seed_default_synonyms(self):
        """Create the starter synonyms once; later edits are kept."""
        params = self.env['ir.config_parameter'].sudo()
        if params.get_param(SEEDED_PARAM):
            return
        existing = set(
            self.with_context(active_test=False).search([]).mapped('term')
        )
        vals_list = [
            {'term': term, 'canonical': canonical}
            for term, canonical in default_synonym_map().items()
            if term not in existing and term != canonical
        ]
        self.with_context(product_search_skip_reindex=True).create(vals_list)
        params.set_param(SEEDED_PARAM, '1')
