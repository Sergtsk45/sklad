"""Tokenizer and ranking for product search v2.

Pure Python without Odoo imports: the same code is used by the models and by
the offline benchmark in ``tests/bench``.
"""

import bisect
import difflib
import math
import re

from .product_search_utils import normalize_product_search_text


# Bump when tokenization rules change: the module upgrade recomputes tokens.
TOKENIZER_VERSION = '1'

STEM_LENGTH = 5
FUZZY_MIN_LENGTH = 4
FUZZY_CUTOFF = 0.75
FUZZY_FACTOR = 0.7
PREFIX_MIN_LENGTH = 2
MAX_EXPANSIONS = 60

STOP_TOKENS = frozenset({
    'мм', 'см', 'шт', 'кг', 'мм2', 'мм3',
    'для', 'на', 'по', 'из', 'под', 'со',
})

# Outer diameter of steel pipe and fittings -> nominal size: «76×3,5»
# is also found by «Ду65» when the card has no explicit Ду.
STEEL_PIPE_OUTER_DIAMETERS = {
    '21.3': '15', '26.8': '20', '33.5': '25', '42.3': '32', '48': '40',
    '57': '50', '76': '65', '89': '80', '108': '100', '114': '100',
    '133': '125', '159': '150', '219': '200', '273': '250', '325': '300',
    '377': '350', '426': '400',
}
MAX_PIPE_WALL = 12

_CHUNK_RE = re.compile(r'[a-zа-я0-9]+(?:[./]\d+)*')
# Cyrillic letters that look like Latin ones, unified in codes and sizes:
# «М16» and «M16», «1р» and «1P» give the same token.
_HOMOGLYPHS = str.maketrans('авекмнорстух', 'abekmhopctyx')
_PIECE_RE = re.compile(
    r'(?P<dim>\d+(?:\.\d+)?(?:x\d+(?:\.\d+)?)+)'
    r'|(?P<frac>\d+/\d+)'
    r'|(?P<num>\d+(?:\.\d+)?)'
    r'|(?P<word>[a-zа-я]+)'
)


def _stem(word):
    return word[:STEM_LENGTH]


def _word_tokens(word, synonyms):
    return [
        _stem(part)
        for part in synonyms.get(word, word).split()
        if len(part) >= 2 and part not in STOP_TOKENS
    ]


def _unify(token):
    if token.isalpha():
        return token
    return token.translate(_HOMOGLYPHS)


def _pipe_size_token(dim):
    parts = dim.split('x')
    nominal = STEEL_PIPE_OUTER_DIAMETERS.get(parts[0])
    if len(parts) != 2 or not nominal or float(parts[1]) > MAX_PIPE_WALL:
        return []
    return ['ду' + nominal]


def _number_tokens(kind, text):
    if kind == 'dim':
        return [text] + text.split('x') + _pipe_size_token(text)
    if kind == 'frac':
        return [text] + text.split('/')
    return [text]


def _chunk_tokens(chunk, synonyms):
    pieces = [
        (match.lastgroup, match.group())
        for match in _PIECE_RE.finditer(chunk)
    ]
    # «Ду25мм», «15мм» -> «Ду25», «15»: a glued unit is not part of the code.
    while len(pieces) > 1 and pieces[-1][1] in STOP_TOKENS:
        pieces.pop()
    if len(pieces) == 1 and pieces[0][0] == 'word':
        return _word_tokens(pieces[0][1], synonyms)

    tokens = []
    if len(pieces) > 1:
        head_kind, head = pieces[0]
        if head_kind == 'word':
            head = synonyms.get(head, head).replace(' ', '')
            tokens.append(head + ''.join(text for _kind, text in pieces[1:]))
            if pieces[1][0] != 'word':
                tokens.append(head + re.split('[x/]', pieces[1][1])[0])
        else:
            tokens.append(''.join(text for _kind, text in pieces))
    for kind, text in pieces:
        if kind == 'word':
            tokens.extend(_word_tokens(text, synonyms))
        else:
            tokens.extend(_number_tokens(kind, text))
    return tokens


def tokenize_product_text(value, synonyms=None):
    """Return ordered unique search tokens for a product name or a query.

    ``М16×70`` gives ``м16x70``, ``м16``, ``16x70``, ``16``, ``70``;
    words are cut to ``STEM_LENGTH`` characters after synonym replacement.
    """
    synonyms = synonyms or {}
    normalized = normalize_product_search_text(value)
    result = []
    for chunk in _CHUNK_RE.findall(normalized):
        for token in map(_unify, _chunk_tokens(chunk, synonyms)):
            if token not in result:
                result.append(token)
    return result


def _is_word(token):
    return token.isalpha()


class SearchVocabulary(dict):
    """Token -> number of products containing it, plus sorted words."""

    def __init__(self, counts, total):
        super().__init__(counts)
        self.total = max(total, 1)
        self.words = sorted(token for token in counts if _is_word(token))


def _prefix_words(token, words):
    start = bisect.bisect_left(words, token)
    result = []
    for word in words[start:start + MAX_EXPANSIONS]:
        if not word.startswith(token):
            break
        result.append(word)
    return result


def _token_expansions(token, vocabulary):
    """Return {vocabulary token: factor} matched by one query token."""
    expansions = {}
    if token in vocabulary:
        expansions[token] = 1.0
    if not _is_word(token):
        return expansions
    if len(token) >= PREFIX_MIN_LENGTH:
        for word in _prefix_words(token, vocabulary.words):
            expansions.setdefault(word, 1.0)
    if not expansions and len(token) >= FUZZY_MIN_LENGTH:
        close = difflib.get_close_matches(
            token, vocabulary.words, n=5, cutoff=FUZZY_CUTOFF,
        )
        for word in close:
            expansions[word] = FUZZY_FACTOR
    return expansions


def build_search_plan(query, vocabulary, synonyms=None, keep_unknown=False):
    """Resolve query tokens against a ``SearchVocabulary``.

    Returns ``[(token, weight, {vocabulary token: factor})]``; the weight is
    the token IDF. Tokens unknown to the catalog are dropped, so extra words
    in a query (``4м``, ``(кор)``) do not hide matching products; with
    ``keep_unknown`` they stay in the plan and no product matches them all.
    """
    plan = []
    for token in tokenize_product_text(query, synonyms):
        expansions = _token_expansions(token, vocabulary)
        if not expansions and not keep_unknown:
            continue
        doc_freq = max(
            (vocabulary.get(word, 1) for word in expansions), default=1,
        )
        weight = math.log(1 + vocabulary.total / doc_freq)
        plan.append((token, weight, expansions))
    return plan


def plan_lexemes(plan):
    """Return every vocabulary token the plan can match."""
    return sorted({word for _token, _weight, exp in plan for word in exp})


def score_tokens(plan, doc_tokens):
    """Return (score, matched_all) for a product token list."""
    if not plan:
        return 0.0, False
    doc_set = set(doc_tokens)
    total = matched = 0.0
    matched_all = True
    for _token, weight, expansions in plan:
        factor = max(
            (expansions[word] for word in doc_set if word in expansions),
            default=0.0,
        )
        total += weight
        matched += weight * factor
        if not factor:
            matched_all = False
    return matched / total, matched_all


def passes_filter(plan, doc_tokens, strict=False, min_score=0.0):
    """Tell whether a product passes the strict / minimum score filter.

    ``strict`` keeps products matching every query token; with ``min_score``
    as well, products covering at least that share of the query weight are
    kept too. Without both every product with a match passes.
    """
    score, matched_all = score_tokens(plan, doc_tokens)
    if strict and matched_all:
        return True
    if min_score:
        return score >= min_score
    return not strict and score > 0


def rank_candidates(plan, candidates, limit=None):
    """Order ``[(id, tokens, label)]`` by relevance, best first.

    Ties go to the product whose own tokens are covered better (a shorter,
    more specific name) and then to the first token being a query token.
    """
    lexemes = set(plan_lexemes(plan))
    first_tokens = {
        word for word, factor in plan[0][2].items() if factor == 1.0
    } if plan else set()
    scored = []
    for record_id, tokens, label in candidates:
        score, _matched_all = score_tokens(plan, tokens)
        if not score:
            continue
        coverage = sum(1 for token in tokens if token in lexemes)
        coverage /= max(len(tokens), 1)
        head_bonus = 1 if tokens and tokens[0] in first_tokens else 0
        scored.append((-score, -head_bonus, -coverage, label, record_id))
    scored.sort()
    ordered = [row[-1] for row in scored]
    return ordered[:limit] if limit else ordered


def build_vocabulary(token_lists):
    """Return a ``SearchVocabulary`` for in-memory token lists."""
    counts = {}
    total = 0
    for tokens in token_lists:
        total += 1
        for token in set(tokens):
            counts[token] = counts.get(token, 0) + 1
    return SearchVocabulary(counts, total)


def build_vocabulary_from_counts(rows, total):
    """Return a ``SearchVocabulary`` from ``[(token, count)]`` rows."""
    return SearchVocabulary(dict(rows), total)
