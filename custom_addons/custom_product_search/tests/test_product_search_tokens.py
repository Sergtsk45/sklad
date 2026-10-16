"""Unit tests for the search v2 tokenizer and ranking (no database)."""

from odoo.tests import BaseCase, tagged

from ..models.product_search_synonyms_data import default_synonym_map
from ..models.product_search_tokens import (
    build_search_plan,
    build_vocabulary,
    passes_filter,
    rank_candidates,
    tokenize_product_text,
)


CATALOG = [
    'Болт М16×70 ГОСТ 7798-70',
    'Болт М16×75 ГОСТ 7798-70',
    'Болт М16×70 ГОСТ 7798-70 оцинкованный',
    'Шайба 160',
    'Отвод стальной 57×3,5',
    'Тройник стальной 76×3,5 мм',
    'Кран шаровой латунный ВР/ВР Ду15',
    'Труба PPR, армированная алюминием, Ду63, PN25',
    'Выключатель автоматический 1P, 6 А',
]


@tagged('post_install', '-at_install')
class TestProductSearchTokens(BaseCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.synonyms = default_synonym_map()
        cls.docs = [
            (index, tokenize_product_text(name, cls.synonyms), name)
            for index, name in enumerate(CATALOG)
        ]
        cls.vocabulary = build_vocabulary(doc[1] for doc in cls.docs)

    def _search(self, query, limit=None):
        plan = build_search_plan(query, self.vocabulary, self.synonyms)
        return [
            CATALOG[index]
            for index in rank_candidates(plan, self.docs, limit)
        ]

    def _tokens(self, value):
        return tokenize_product_text(value, self.synonyms)

    def test_compound_size_tokens(self):
        self.assertEqual(
            self._tokens('Болт М16×70'),
            ['болт', 'm16x70', 'm16', '16x70', '16', '70'],
        )

    def test_latin_and_cyrillic_codes_are_unified(self):
        self.assertEqual(self._tokens('M16х70'), self._tokens('М16×70'))
        self.assertIn('1p', self._tokens('Автомат 6А, 1р'))

    def test_nominal_size_spellings(self):
        expected = self._tokens('Ду50')[0]
        for query in ('Ду 50', 'DN50', 'dn 50', 'd50', 'ДУ-50'):
            with self.subTest(query=query):
                self.assertEqual(self._tokens(query)[0], expected)

    def test_steel_pipe_outer_diameter_gives_nominal_size(self):
        self.assertIn(self._tokens('Ду50')[0], self._tokens('57×3,5'))

    def test_decimal_comma_and_fraction(self):
        self.assertIn('3.5', self._tokens('57х3,5'))
        self.assertEqual(self._tokens('1/2'), ['1/2', '1', '2'])

    def test_glued_unit_is_dropped_from_codes(self):
        self.assertEqual(self._tokens('Ду25мм'), self._tokens('Ду25'))
        self.assertEqual(self._tokens('15мм'), ['15'])

    def test_synonyms_stems_and_stop_words(self):
        self.assertEqual(
            self._tokens('оцинк.'), self._tokens('оцинкованный'),
        )
        self.assertEqual(self._tokens('шаровой'), self._tokens('шаровый'))
        self.assertNotIn('мм', self._tokens('Тройник 76×3,5 мм'))

    def test_full_match_ranks_first(self):
        self.assertEqual(
            self._search('болт оцинк. М16х70')[0],
            'Болт М16×70 ГОСТ 7798-70 оцинкованный',
        )

    def test_number_is_not_matched_as_prefix(self):
        self.assertNotIn('Шайба 160', self._search('болт 16'))

    def test_unknown_query_words_are_ignored(self):
        self.assertEqual(
            self._search('труба ППР 63(ХВС) 4м', 1),
            ['Труба PPR, армированная алюминием, Ду63, PN25'],
        )

    def test_typo_is_tolerated(self):
        self.assertIn('Болт М16×70 ГОСТ 7798-70', self._search('болд м16'))

    def test_nominal_size_finds_pipe_fitting_by_outer_diameter(self):
        self.assertEqual(
            self._search('тройник ст. Ду 65', 1),
            ['Тройник стальной 76×3,5 мм'],
        )

    def test_strict_filter(self):
        plan = build_search_plan('болт м16х75', self.vocabulary, self.synonyms)
        kept = [
            name for _index, tokens, name in self.docs
            if passes_filter(plan, tokens, strict=True)
        ]
        self.assertEqual(kept, ['Болт М16×75 ГОСТ 7798-70'])

    def test_min_score_filter_without_strict(self):
        plan = build_search_plan('болд м16', self.vocabulary, self.synonyms)
        tokens = self._tokens('Болт М16×70 ГОСТ 7798-70')
        self.assertFalse(passes_filter(plan, tokens, min_score=1.0))
        self.assertTrue(passes_filter(plan, tokens, min_score=0.5))

    def test_empty_query(self):
        self.assertEqual(self._search(''), [])
        self.assertEqual(self._search('(кор)'), [])
