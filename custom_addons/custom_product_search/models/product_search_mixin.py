"""Ranked token search shared by product templates and variants."""

from odoo import api, fields, models
from odoo.fields import Domain
from odoo.tools import SQL
from odoo.tools.sql import create_index

from .product_search_tokens import (
    TOKENIZER_VERSION,
    build_search_plan,
    build_vocabulary_from_counts,
    passes_filter,
    plan_lexemes,
    rank_candidates,
    tokenize_product_text,
)


TOKENIZER_VERSION_PARAM = 'custom_product_search.tokenizer_version'
CANDIDATE_LIMIT = 2000
# List filter: every token matched, or this share of the query weight.
LIST_FILTER_MIN_SCORE = 0.8
POSITIVE_SMART_SEARCH_OPERATORS = ('ilike', '=ilike', 'like', '=like', '=')
SEARCH_TOKENS_EXPRESSION = (
    "array_to_tsvector(string_to_array(x_search_tokens, ' '))"
)

# {(dbname, table): (cache key, vocabulary)}; the key changes with any
# product or synonym write, so every worker reloads after a commit.
# Within one transaction write_date is constant, so computing tokens also
# drops the local entries.
_VOCABULARY_CACHE = {}


class ProductSearchMixin(models.AbstractModel):
    _name = 'product.search.mixin'
    _description = 'Product Search v2 Mixin'

    x_search_tokens = fields.Char(
        string='Search Tokens',
        compute='_compute_x_search_tokens',
        store=True,
        readonly=True,
        copy=False,
    )
    x_smart_search = fields.Char(
        string='Smart Search',
        compute='_compute_x_smart_search',
        search='_search_x_smart_search',
    )

    def _auto_init(self):
        result = super()._auto_init()
        if self._abstract:
            return result
        create_index(
            self.env.cr,
            f'{self._table}_x_search_tokens_gin_idx',
            self._table,
            [SEARCH_TOKENS_EXPRESSION],
            method='gin',
        )
        return result

    def _get_search_tokens_source(self):
        """Return the text indexed for this record."""
        self.ensure_one()
        return self.name or ''

    def _compute_x_search_tokens(self):
        self._drop_search_vocabulary_cache()
        synonyms = self.env['product.search.synonym']._get_synonym_map()
        for record in self:
            tokens = tokenize_product_text(
                record._get_search_tokens_source(), synonyms,
            )
            record.x_search_tokens = ' '.join(tokens) or False

    def _compute_x_smart_search(self):
        self.x_smart_search = False

    def _search_x_smart_search(self, operator, value):
        if operator not in POSITIVE_SMART_SEARCH_OPERATORS or not value:
            return NotImplemented
        return Domain('id', 'in', self._smart_search_ids(
            value, strict=True, min_score=LIST_FILTER_MIN_SCORE,
        ))

    @api.model
    def _recompute_search_tokens(self):
        """Recompute search fields of every record, archived ones included."""
        records = self.with_context(active_test=False).search([])
        field_names = [
            name for name in ('x_search_tokens', 'x_search_name')
            if name in self._fields
        ]
        for name in field_names:
            self.env.add_to_compute(self._fields[name], records)
        records.flush_recordset(field_names)

    @api.model
    def _refresh_search_tokens_if_outdated(self):
        """Recompute tokens after the tokenizer rules changed (on upgrade)."""
        params = self.env['ir.config_parameter'].sudo()
        param = f'{TOKENIZER_VERSION_PARAM}.{self._table}'
        if params.get_param(param) == TOKENIZER_VERSION:
            return
        self._recompute_search_tokens()
        params.set_param(param, TOKENIZER_VERSION)

    @api.model
    def _drop_search_vocabulary_cache(self):
        dbname = self.env.cr.dbname
        for table in ('product_template', 'product_product'):
            _VOCABULARY_CACHE.pop((dbname, table), None)

    @api.model
    def _get_search_vocabulary(self):
        cr = self.env.cr
        cr.execute(SQL("""
            SELECT (SELECT count(*) FROM product_template),
                   (SELECT max(write_date) FROM product_template),
                   (SELECT count(*) FROM product_product),
                   (SELECT max(write_date) FROM product_product),
                   (SELECT count(*) FROM product_search_synonym),
                   (SELECT max(write_date) FROM product_search_synonym)
        """))
        key = cr.fetchone()
        cache_key = (cr.dbname, self._table)
        cached = _VOCABULARY_CACHE.get(cache_key)
        if cached and cached[0] == key:
            return cached[1]
        table = SQL.identifier(self._table)
        cr.execute(SQL(
            "SELECT count(*) FROM %s WHERE active", table,
        ))
        total = cr.fetchone()[0]
        cr.execute(SQL(
            """SELECT token, count(*)
                 FROM %s, unnest(string_to_array(x_search_tokens, ' ')) token
                WHERE active
                GROUP BY token""",
            table,
        ))
        vocabulary = build_vocabulary_from_counts(cr.fetchall(), total)
        _VOCABULARY_CACHE[cache_key] = (key, vocabulary)
        return vocabulary

    @api.model
    def _get_search_plan(self, query, keep_unknown=False):
        synonyms = self.env['product.search.synonym']._get_synonym_map()
        return build_search_plan(
            query, self._get_search_vocabulary(), synonyms, keep_unknown,
        )

    @api.model
    def _fetch_search_candidates(self, plan, domain, limit=CANDIDATE_LIMIT):
        lexemes = plan_lexemes(plan)
        if not lexemes:
            return []
        ts_query = ' | '.join(
            "'%s'" % lexeme.replace("'", "''") for lexeme in lexemes
        )
        query = self._search(Domain(domain or Domain.TRUE))
        tokens_sql = SQL(
            "array_to_tsvector(string_to_array(%s, ' '))",
            SQL.identifier(self._table, 'x_search_tokens'),
        )
        query.add_where(SQL("%s @@ %s::tsquery", tokens_sql, ts_query))
        if limit:
            query.order = SQL(
                "ts_rank(%s, %s::tsquery) DESC", tokens_sql, ts_query,
            )
            query.limit = limit
        self.env.cr.execute(query.select(
            SQL.identifier(self._table, 'id'),
            SQL.identifier(self._table, 'x_search_tokens'),
            SQL.identifier(self._table, 'x_search_name'),
        ))
        return [
            (record_id, (tokens or '').split(), label or '')
            for record_id, tokens, label in self.env.cr.fetchall()
        ]

    @api.model
    def _smart_search_ids(
        self, query, domain=None, limit=None, strict=False, min_score=0.0,
        keep_unknown=False,
    ):
        """Return record ids ranked by relevance to ``query``.

        Uses the normal ``_search`` for ``domain``, so access rules apply.
        Without filters partial matches are ranked below full ones
        (autocomplete); ``strict`` / ``min_score`` filter them as described
        in ``passes_filter`` (list view, AI). ``keep_unknown`` makes words
        unknown to the catalog count as unmatched (see ``build_search_plan``).
        """
        # Vocabulary and candidates are read with raw SQL.
        self.env['product.template'].flush_model()
        self.env['product.product'].flush_model()
        self.env['product.search.synonym'].flush_model()
        plan = self._get_search_plan(query, keep_unknown)
        # Filters must see every match; ranking alone may cut the tail.
        candidate_limit = None if strict or min_score else CANDIDATE_LIMIT
        candidates = self._fetch_search_candidates(
            plan, domain, candidate_limit,
        )
        if strict or min_score:
            candidates = [
                candidate for candidate in candidates
                if passes_filter(plan, candidate[1], strict, min_score)
            ]
        return rank_candidates(plan, candidates, limit)

    @api.model
    def _smart_name_search(
        self, name, domain, limit, exact_ids, standard_search,
    ):
        """Return exact code hits, ranked token hits, then standard ones.

        ``standard_search(domain, limit)`` is the parent ``name_search``;
        it fills the rest of the limit with records not found yet.
        """
        record_ids = list(exact_ids)
        record_ids += [
            record_id
            for record_id in self._smart_search_ids(name, domain, limit)
            if record_id not in record_ids
        ]
        if limit:
            record_ids = record_ids[:limit]
        records = self.browse(record_ids).sudo()
        results = [(record.id, record.display_name) for record in records]
        if limit and len(results) >= limit:
            return results

        standard_domain = domain
        if record_ids:
            standard_domain &= Domain('id', 'not in', record_ids)
        remaining = limit - len(results) if limit else limit
        return results + standard_search(standard_domain, remaining)
