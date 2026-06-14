import re

from odoo import api, models

_UOM_MAP = {
    "шт": "шт.",
    "шт.": "шт.",
    "штука": "шт.",
    "штук": "шт.",
    "штуки": "шт.",
    "кг": "кг.",
    "кг.": "кг.",
    "килограмм": "кг.",
    "килограммов": "кг.",
    "м": "м.",
    "м.": "м.",
    "метр": "м.",
    "метров": "м.",
    "л": "л.",
    "л.": "л.",
    "литр": "л.",
    "литров": "л.",
    "уп": "уп.",
    "уп.": "уп.",
    "упаковка": "уп.",
    "упаковок": "уп.",
    "м2": "м²",
    "кв.м": "м²",
    "кв.м.": "м²",
    "кв м": "м²",
    "м3": "м³",
    "куб.м": "м³",
    "куб.м.": "м³",
    "куб м": "м³",
}

_SKIP_ARTICLES = {"", "none", "н/а", "-", "—", "нет", "n/a"}

_MATCH_STOP_TOKENS = {
    "без",
    "в",
    "во",
    "для",
    "и",
    "из",
    "к",
    "на",
    "от",
    "по",
    "под",
    "при",
    "с",
    "со",
    "у",
}

_ARTICLE_NAME_MIN_CHARS = 5
_ARTICLE_NAME_SEARCH_LIMIT = 200
_ARTICLE_NAME_MIN_SCORE = 0.7
_ARTICLE_NAME_MIN_MARGIN = 0.15
_NAME_SEARCH_LIMIT = 200
_NAME_MIN_SCORE = 0.7
_NAME_MIN_MARGIN = 0.15
_ARTICLE_TOKEN_WEIGHT = 0.5
_LINE_LENGTH_RE = re.compile(r"^l\s*=\s*\d+(?:[.,]\d+)?$", re.IGNORECASE)
_LINE_SINGLE_SIZE_RE = re.compile(r"^\d+(?:[.,]\d+)?$")


class ExcelParser(models.AbstractModel):
    _name = "object.request.excel.parser"
    _description = "Сервис парсинга и автосопоставления строк Excel"

    @api.model
    def normalize_uom(self, uom_str):
        if not uom_str:
            return ""
        key = re.sub(r"\s+", " ", str(uom_str).strip().lower())
        return _UOM_MAP.get(key, str(uom_str).strip())

    @api.model
    def normalize_str(self, s):
        if not s:
            return ""
        return re.sub(r"\s+", " ", str(s).strip())

    @api.model
    def _normalize_for_match(self, s):
        """Normalize product names/articles before matching."""
        if not s:
            return ""
        value = str(s).replace("\xa0", " ").strip().lower()
        value = value.replace("ё", "е")
        value = re.sub(r"\b(ду|ру|dn|pn)\s*-?\s*(\d+)\b", r"\1\2", value)
        value = re.sub(r"(?<=\d)\s*[xх×]\s*(?=\d)", "x", value)
        value = re.sub(r"(?<=\d),(?=\d)", ".", value)
        value = re.sub(r"\s+", " ", value)
        return value

    @api.model
    def _tokenize(self, s):
        """Split normalized text into significant matching tokens."""
        normalized = self._normalize_for_match(s)
        tokens = re.findall(
            r"[0-9a-zа-я]+(?:[./,x-][0-9a-zа-я]+)*",
            normalized,
        )
        return [
            token
            for token in tokens
            if len(token) > 1 and token not in _MATCH_STOP_TOKENS
        ]

    @api.model
    def _significant_match_chars(self, s):
        return len(re.sub(r"[^0-9a-zа-я]+", "", self._normalize_for_match(s)))

    @api.model
    def _select_best_scored_candidate(self, scored_candidates):
        """Return the best candidate only when the score is unambiguous."""
        Product = self.env["product.product"]
        if not scored_candidates:
            return Product.browse()
        scored_candidates = sorted(
            scored_candidates,
            key=lambda item: item[0],
            reverse=True,
        )
        best_score, best_product = scored_candidates[0]
        if best_score < _ARTICLE_NAME_MIN_SCORE:
            return Product.browse()
        if len(scored_candidates) == 1:
            return best_product
        second_score = scored_candidates[1][0]
        if best_score - second_score >= _ARTICLE_NAME_MIN_MARGIN:
            return best_product
        return Product.browse()

    @api.model
    def _score_article_name_candidate(self, article_tokens, product):
        product_name = self._normalize_for_match(product.name)
        matched_tokens = [
            token for token in article_tokens if token in product_name
        ]
        return len(matched_tokens) / len(article_tokens)

    @api.model
    def _match_product_by_article_in_name(self, article):
        """Search product names for normalized article/designation tokens."""
        if self._significant_match_chars(article) < _ARTICLE_NAME_MIN_CHARS:
            return self.env["product.product"].browse()
        article_tokens = self._tokenize(article)
        if not article_tokens:
            return self.env["product.product"].browse()
        Product = self.env["product.product"]
        candidates = Product.browse()
        for key_token in sorted(article_tokens, key=len, reverse=True):
            candidates = Product.search(
                [("name", "ilike", key_token), ("active", "=", True)],
                limit=_ARTICLE_NAME_SEARCH_LIMIT,
            )
            if candidates:
                break
        scored_candidates = []
        for product in candidates:
            score = self._score_article_name_candidate(article_tokens, product)
            if score:
                scored_candidates.append((score, product))
        return self._select_best_scored_candidate(scored_candidates)

    @api.model
    def _supplierinfo_products(self, supplier_infos):
        Product = self.env["product.product"]
        products = Product.browse()
        for info in supplier_infos:
            if info.product_id:
                products |= info.product_id
            elif info.product_tmpl_id:
                products |= info.product_tmpl_id.product_variant_ids[:1]
        return products

    @api.model
    def _product_from_supplierinfos(self, supplier_infos):
        products = self._supplierinfo_products(supplier_infos)
        if len(products) == 1:
            return products
        return self.env["product.product"].browse()

    @api.model
    def _match_product_by_supplierinfo(self, article, vendor=None):
        SupplierInfo = self.env["product.supplierinfo"]
        product = self.env["product.product"].browse()
        if vendor:
            vendor_infos = SupplierInfo.search(
                [
                    ("product_code", "=ilike", article),
                    ("partner_id", "=", vendor.id),
                ],
            )
            product = self._product_from_supplierinfos(vendor_infos)
            if product:
                return product
        infos = SupplierInfo.search([("product_code", "=ilike", article)])
        return self._product_from_supplierinfos(infos)

    @api.model
    def _supplierinfo_candidate_products(self, article, vendor=None):
        SupplierInfo = self.env["product.supplierinfo"]
        if not article:
            return self.env["product.product"].browse()
        domains = []
        if vendor:
            domains.append(
                [
                    ("product_code", "=ilike", article),
                    ("partner_id", "=", vendor.id),
                ]
            )
        domains.append([("product_code", "=ilike", article)])
        for domain in domains:
            products = self._supplierinfo_products(SupplierInfo.search(domain))
            if len(products) > 1:
                return products
        return self.env["product.product"].browse()

    @api.model
    def _select_best_name_candidate(self, scored_candidates):
        Product = self.env["product.product"]
        if not scored_candidates:
            return Product.browse()
        scored_candidates = sorted(
            scored_candidates,
            key=lambda item: item[0],
            reverse=True,
        )
        best_score, best_product = scored_candidates[0]
        if best_score < _NAME_MIN_SCORE:
            return Product.browse()
        if len(scored_candidates) == 1:
            return best_product
        second_score = scored_candidates[1][0]
        if best_score - second_score >= _NAME_MIN_MARGIN:
            return best_product
        return Product.browse()

    @api.model
    def _weighted_query_tokens(self, name_raw, supplier_article=None):
        weighted_tokens = [(token, 1.0) for token in self._tokenize(name_raw)]
        name_tokens = {token for token, _weight in weighted_tokens}
        for token in self._tokenize(supplier_article):
            if token not in name_tokens:
                weighted_tokens.append((token, _ARTICLE_TOKEN_WEIGHT))
        return weighted_tokens

    @api.model
    def _is_noise_article(self, supplier_article):
        article = self._normalize_for_match(supplier_article)
        if not article or article in _SKIP_ARTICLES:
            return True
        return bool(
            _LINE_LENGTH_RE.match(article)
            or _LINE_SINGLE_SIZE_RE.match(article)
        )

    @api.model
    def _classify_import_line(self, name_raw, supplier_article):
        name_tokens = self._tokenize(name_raw)
        article = self._normalize_for_match(supplier_article)
        if not name_tokens and not article:
            return "manual_only"
        if (
            _LINE_LENGTH_RE.match(article)
            or _LINE_SINGLE_SIZE_RE.match(article)
        ):
            return "length_or_pipe_fragment"
        if not article or article in _SKIP_ARTICLES:
            return "empty_article"
        if len(name_tokens) <= 1 and len(self._tokenize(article)) <= 1:
            return "ambiguous"
        return "product_candidate"

    @api.model
    def _combined_match_query(self, name_raw, supplier_article):
        tokens = []
        seen = set()
        for source in (name_raw, supplier_article):
            if source == supplier_article and self._is_noise_article(source):
                continue
            for token in self._tokenize(source):
                if token not in seen:
                    tokens.append(token)
                    seen.add(token)
        return " ".join(tokens)

    @api.model
    def _score_name_candidate(self, weighted_tokens, product):
        product_name = self._normalize_for_match(product.name)
        total_weight = sum(weight for _token, weight in weighted_tokens)
        if not total_weight:
            return 0
        matched_weight = sum(
            weight
            for token, weight in weighted_tokens
            if token in product_name
        )
        return matched_weight / total_weight

    @api.model
    def _match_product_by_normalized_exact_name(self, name):
        Product = self.env["product.product"]
        name_tokens = self._tokenize(name)
        if not name_tokens:
            return Product.browse()
        for key_token in sorted(name_tokens, key=len, reverse=True):
            candidates = Product.search(
                [("name", "ilike", key_token), ("active", "=", True)],
                limit=_NAME_SEARCH_LIMIT,
            )
            exact_candidates = candidates.filtered(
                lambda product: self._normalize_for_match(product.name)
                == self._normalize_for_match(name)
            )
            if len(exact_candidates) == 1:
                return exact_candidates
            if len(exact_candidates) > 1:
                return Product.browse()
        return Product.browse()

    @api.model
    def _match_product_by_tokenized_name(
        self,
        name_raw,
        supplier_article=None,
    ):
        Product = self.env["product.product"]
        name_tokens = self._tokenize(name_raw)
        if not name_tokens:
            return Product.browse()
        if len(name_tokens) == 1 and not self._tokenize(supplier_article):
            return Product.browse()

        candidates = Product.browse()
        for key_token in sorted(name_tokens, key=len, reverse=True):
            candidates = Product.search(
                [("name", "ilike", key_token), ("active", "=", True)],
                limit=_NAME_SEARCH_LIMIT,
            )
            if candidates:
                break
        weighted_tokens = self._weighted_query_tokens(
            name_raw,
            supplier_article=supplier_article,
        )
        scored_candidates = []
        for product in candidates:
            score = self._score_name_candidate(weighted_tokens, product)
            if score:
                scored_candidates.append((score, product))
        return self._select_best_name_candidate(scored_candidates)

    @api.model
    def _combined_candidate_products(self, name_raw, supplier_article):
        service = self.env["object.request.matching.candidate.service"]
        result = service.build_candidates(
            name_raw,
            supplier_article,
        )
        return (
            service.candidate_products(result),
            result["line_type"],
            result["combined_query"],
        )

    @api.model
    def _auto_match_combined_candidate(
        self,
        candidates,
        name_raw,
        supplier_article,
    ):
        service = self.env["object.request.matching.candidate.service"]
        result = service.build_candidates(
            name_raw,
            supplier_article,
        )
        candidate_ids = set(candidates.ids)
        result["candidates"] = [
            item
            for item in result["candidates"]
            if item["product_id"] in candidate_ids
        ]
        return service.auto_match_candidate(result)

    @api.model
    def match_product_by_article(self, supplier_article, vendor=None):
        """Поиск product по артикулу/обозначению."""
        article = self.normalize_str(supplier_article)
        if not article or article.lower() in _SKIP_ARTICLES:
            return self.env["product.product"].browse()
        Product = self.env["product.product"]
        product = self._match_product_by_supplierinfo(article, vendor=vendor)
        if product:
            return product
        product = Product.search(
            [("default_code", "=ilike", article), ("active", "=", True)],
            limit=1,
        )
        if product:
            return product
        return self._match_product_by_article_in_name(article)

    @api.model
    def match_product_by_name(self, name_raw, supplier_article=None):
        """Поиск product по наименованию: exact, затем токенный скоринг."""
        name = self.normalize_str(name_raw)
        if not name:
            return self.env["product.product"].browse()
        Product = self.env["product.product"]
        product = Product.search(
            [("name", "=", name), ("active", "=", True)],
            limit=1,
        )
        if not product:
            product = self._match_product_by_normalized_exact_name(name)
        if not product:
            product = self._match_product_by_tokenized_name(
                name,
                supplier_article=supplier_article,
            )
        return product

    @api.model
    def match_vendor_by_name(self, supplier_raw):
        """Поиск res.partner по имени поставщика (ilike, supplier_rank > 0)."""
        name = self.normalize_str(supplier_raw)
        if not name:
            return self.env["res.partner"].browse()
        Partner = self.env["res.partner"]
        partner = Partner.search(
            [("name", "=ilike", name), ("supplier_rank", ">", 0)],
            limit=1,
        )
        if not partner:
            partner = Partner.search(
                [("name", "ilike", name), ("supplier_rank", ">", 0)],
                limit=1,
            )
        return partner

    @api.model
    def match_row(self, supplier_article, name_raw, supplier_raw):
        """Комбинированное сопоставление строки Excel.

        Returns:
            dict: product, vendor, matching_required, manual_vendor_required
        """
        vendor = self.match_vendor_by_name(supplier_raw)
        product = self.match_product_by_article(
            supplier_article,
            vendor=vendor,
        )
        match_source = "deterministic_auto" if product else ""
        candidate_products = self.env["product.product"].browse()
        if not product:
            candidate_products = self._supplierinfo_candidate_products(
                self.normalize_str(supplier_article),
                vendor=vendor,
            )
        if not product:
            product = self.match_product_by_name(
                name_raw,
                supplier_article=supplier_article,
            )
            if product:
                match_source = "deterministic_auto"
        service = self.env["object.request.matching.candidate.service"]
        candidate_result = service.build_candidates(
            name_raw,
            supplier_article,
            vendor=vendor,
        )
        line_type = candidate_result["line_type"]
        combined_query = ""
        if not product:
            combined_query = candidate_result["combined_query"]
            combined_candidates = service.candidate_products(candidate_result)
            product = service.auto_match_candidate(candidate_result)
            if product:
                match_source = "combined_auto"
            if not product and combined_candidates:
                candidate_products |= combined_candidates
        return {
            "product": product,
            "vendor": vendor,
            "matching_required": not bool(product),
            "manual_vendor_required": not bool(vendor),
            "candidate_products": candidate_products if not product else False,
            "candidate_details": (
                candidate_result["candidates"] if not product else []
            ),
            "line_type": line_type,
            "combined_query": combined_query,
            "match_source": match_source,
        }
