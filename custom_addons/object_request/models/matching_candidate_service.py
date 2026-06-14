from odoo import api, models


INTERNAL_CANDIDATE_LIMIT = 15
LLM_CANDIDATE_LIMIT = 8
PREVIEW_CANDIDATE_LIMIT = 3
AUTO_MATCH_MIN_SCORE = 0.9


class ObjectRequestMatchingCandidateService(models.AbstractModel):
    _name = "object.request.matching.candidate.service"
    _description = "Shortlist candidates for object request line matching"

    @api.model
    def build_candidates(
        self,
        name_raw,
        supplier_article,
        vendor=None,
        technical_designation=None,
    ):
        parser = self.env["object.request.excel.parser"]
        designation_context = self._designation_context(
            supplier_article,
            technical_designation,
        )
        line_type = parser._classify_import_line(
            name_raw,
            designation_context,
        )
        combined_query = parser._combined_match_query(
            name_raw,
            designation_context,
        )
        limits = {
            "internal": INTERNAL_CANDIDATE_LIMIT,
            "llm": LLM_CANDIDATE_LIMIT,
            "preview": PREVIEW_CANDIDATE_LIMIT,
        }
        memory_match = self._find_in_memory(name_raw, designation_context)
        if memory_match:
            result = {
                "line_type": "product_candidate",
                "combined_query": combined_query,
                "candidates": [],
                "can_call_llm": False,
                "note": "Найдено в памяти сопоставлений.",
                "limits": limits,
            }
            self._add_candidate(
                result,
                memory_match.product_id,
                "memory",
                memory_match.confidence,
                "Из памяти сопоставлений.",
            )
            return result
        result = {
            "line_type": line_type,
            "combined_query": combined_query,
            "candidates": [],
            "can_call_llm": False,
            "note": "",
            "limits": limits,
        }
        if line_type == "manual_only":
            result["note"] = "Строка оставлена для ручного сопоставления."
            return result

        self._add_supplierinfo_candidates(result, supplier_article, vendor)
        self._add_default_code_candidate(result, supplier_article)
        self._add_name_score_candidates(result, name_raw, designation_context)
        self._add_combined_search_candidates(
            result,
            name_raw,
            designation_context,
        )
        result["candidates"] = result["candidates"][:INTERNAL_CANDIDATE_LIMIT]
        result["can_call_llm"] = bool(result["candidates"])
        if not result["candidates"]:
            result["note"] = "Кандидаты не найдены."
        return result

    @api.model
    def candidate_products(self, candidate_result):
        Product = self.env["product.product"]
        product_ids = [
            item["product_id"]
            for item in candidate_result.get("candidates", [])
            if item.get("product_id")
        ]
        return Product.browse(product_ids)

    @api.model
    def _designation_context(self, supplier_article, technical_designation):
        parser = self.env["object.request.excel.parser"]
        return parser.normalize_str(technical_designation) or supplier_article

    @api.model
    def llm_candidates(self, candidate_result):
        return candidate_result.get("candidates", [])[:LLM_CANDIDATE_LIMIT]

    @api.model
    def preview_candidates(self, candidate_result):
        return candidate_result.get("candidates", [])[:PREVIEW_CANDIDATE_LIMIT]

    @api.model
    def auto_match_candidate(self, candidate_result):
        candidates = candidate_result.get("candidates", [])
        if len(candidates) != 1:
            return self.env["product.product"].browse()
        if candidate_result.get("line_type") == "manual_only":
            return self.env["product.product"].browse()
        candidate = candidates[0]
        if candidate["local_score"] < AUTO_MATCH_MIN_SCORE:
            return self.env["product.product"].browse()
        return candidate["product"]

    @api.model
    def _add_candidate(self, result, product, source, score, reason=""):
        if not product:
            return
        if any(
            item["product_id"] == product.id
            for item in result["candidates"]
        ):
            return
        matched_tokens, missing_tokens = self._candidate_token_diff(
            product,
            result["combined_query"],
        )
        result["candidates"].append(
            {
                "product": product,
                "product_id": product.id,
                "display_name": product.display_name,
                "default_code": product.default_code or "",
                "uom_id": product.uom_id.id if product.uom_id else False,
                "source": source,
                "local_score": min(max(score or 0.0, 0.0), 1.0),
                "matched_tokens": matched_tokens,
                "missing_tokens": missing_tokens,
                "reason": reason,
            }
        )

    @api.model
    def _add_supplierinfo_candidates(self, result, supplier_article, vendor):
        parser = self.env["object.request.excel.parser"]
        article = parser.normalize_str(supplier_article)
        if not article:
            return
        SupplierInfo = self.env["product.supplierinfo"]
        domains = []
        if vendor:
            domains.append(
                [
                    ("product_code", "=ilike", article),
                    ("partner_id", "=", vendor.id),
                ]
            )
        domains.append([("product_code", "=ilike", article)])
        products = self.env["product.product"].browse()
        for domain in domains:
            products |= parser._supplierinfo_products(
                SupplierInfo.search(domain)
            )
        reason = "Артикул найден в supplierinfo."
        if len(products) > 1:
            reason = "Артикул найден в нескольких supplierinfo."
        for product in products:
            self._add_candidate(
                result,
                product,
                "supplierinfo",
                1.0,
                reason,
            )

    @api.model
    def _add_default_code_candidate(self, result, supplier_article):
        parser = self.env["object.request.excel.parser"]
        article = parser.normalize_str(supplier_article)
        if not article or parser._is_noise_article(article):
            return
        product = self.env["product.product"].search(
            [("default_code", "=ilike", article), ("active", "=", True)],
            limit=1,
        )
        if product:
            self._add_candidate(
                result,
                product,
                "default_code",
                1.0,
                "Совпадает внутренний артикул товара.",
            )

    @api.model
    def _add_name_score_candidates(self, result, name_raw, supplier_article):
        parser = self.env["object.request.excel.parser"]
        name_tokens = parser._tokenize(name_raw)
        if not name_tokens:
            return
        Product = self.env["product.product"]
        products = Product.browse()
        for key_token in sorted(name_tokens, key=len, reverse=True):
            products = Product.search(
                [("name", "ilike", key_token), ("active", "=", True)],
                limit=INTERNAL_CANDIDATE_LIMIT,
            )
            if products:
                break
        weighted_tokens = parser._weighted_query_tokens(
            name_raw,
            supplier_article=supplier_article,
        )
        scored = []
        for product in products:
            score = parser._score_name_candidate(weighted_tokens, product)
            if score:
                scored.append((score, product))
        for score, product in sorted(
            scored,
            key=lambda item: item[0],
            reverse=True,
        ):
            self._add_candidate(
                result,
                product,
                "name_score",
                score,
                "Совпали значимые токены наименования.",
            )

    @api.model
    def _add_combined_search_candidates(
        self,
        result,
        name_raw,
        supplier_article,
    ):
        parser = self.env["object.request.excel.parser"]
        query = result["combined_query"]
        if not query:
            return
        Product = self.env["product.product"]
        rows = Product.ai_search_products(
            query,
            limit=INTERNAL_CANDIDATE_LIMIT,
        )
        if not rows and not parser._is_noise_article(supplier_article):
            name_query = parser._combined_match_query(name_raw, "")
            if name_query and name_query != query:
                rows = Product.ai_search_products(
                    name_query,
                    limit=INTERNAL_CANDIDATE_LIMIT,
                )
        products = Product.browse([row["id"] for row in rows if row.get("id")])
        weighted_tokens = parser._weighted_query_tokens(
            name_raw,
            supplier_article=supplier_article,
        )
        for product in products:
            score = parser._score_name_candidate(weighted_tokens, product)
            self._add_candidate(
                result,
                product,
                "combined_search",
                score,
                "Найден нормализованным поиском по полной строке.",
            )

    @api.model
    def _find_in_memory(self, name_raw, designation_context):
        """Найти запись в памяти по имени и техническому контексту."""
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str(name_raw or '')
        if not name_norm or len(name_norm) < 3:
            return self.env['object.request.matching.memory'].browse()
        designation_norm = parser.normalize_str(designation_context or '')
        Memory = self.env['object.request.matching.memory']
        base_domain = [
            ('name_normalized', '=', name_norm),
            ('active', '=', True),
        ]
        order = 'confidence desc, create_date desc'
        empty_designation_domain = [
            '|',
            ('designation_normalized', '=', False),
            ('designation_normalized', '=', ''),
        ]
        if designation_norm:
            exact = Memory.search(
                base_domain + [
                    ('designation_normalized', '=', designation_norm),
                ],
                limit=1,
                order=order,
            )
            if exact:
                return exact
            return Memory.search(
                base_domain + empty_designation_domain,
                limit=1,
                order=order,
            )
        empty_designation = Memory.search(
            base_domain + empty_designation_domain,
            limit=1,
            order=order,
        )
        if empty_designation:
            return empty_designation
        legacy_candidates = Memory.search(base_domain, limit=2, order=order)
        if len(legacy_candidates) == 1:
            return legacy_candidates
        return Memory.browse()

    @api.model
    def _candidate_token_diff(self, product, query):
        parser = self.env["object.request.excel.parser"]
        product_text = parser._normalize_for_match(
            " ".join(
                value
                for value in [product.display_name, product.default_code or ""]
                if value
            )
        )
        tokens = parser._tokenize(query)
        matched = [token for token in tokens if token in product_text]
        missing = [token for token in tokens if token not in product_text]
        return matched, missing
