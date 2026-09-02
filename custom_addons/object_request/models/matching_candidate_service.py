from odoo import api, models


INTERNAL_CANDIDATE_LIMIT = 15
LLM_CANDIDATE_LIMIT = 8
PREVIEW_CANDIDATE_LIMIT = 3
AUTO_MATCH_MIN_SCORE = 0.9
NAME_TOKEN_SEARCH_LIMIT = 200


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
        request=None,
        issue_warehouses=None,
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
        substitution_source_text = " ".join(
            value
            for value in [name_raw, designation_context]
            if value
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
                "substitution_source_text": substitution_source_text,
            }
            self._add_candidate(
                result,
                memory_match.product_id,
                "memory",
                memory_match.confidence,
                "Из памяти сопоставлений.",
            )
            self._enrich_candidates_with_issue_stock(
                result,
                request=request,
                issue_warehouses=issue_warehouses,
            )
            return result
        result = {
            "line_type": line_type,
            "combined_query": combined_query,
            "candidates": [],
            "can_call_llm": False,
            "note": "",
            "limits": limits,
            "substitution_source_text": substitution_source_text,
        }
        if line_type == "manual_only":
            result["note"] = "Строка оставлена для ручного сопоставления."
            return result

        self._add_supplierinfo_candidates(result, supplier_article, vendor)
        self._add_default_code_candidate(result, supplier_article)
        self._add_feature_candidates(result)
        self._add_name_score_candidates(result, name_raw, designation_context)
        self._add_combined_search_candidates(
            result,
            name_raw,
            designation_context,
        )
        self._enrich_candidates_with_issue_stock(
            result,
            request=request,
            issue_warehouses=issue_warehouses,
        )
        self._sort_candidates(result)
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
        if candidate.get("substitution_requires_confirmation"):
            return self.env["product.product"].browse()
        if candidate.get("substitution_decision") == "blocked":
            return self.env["product.product"].browse()
        return candidate["product"]

    @api.model
    def _add_candidate(self, result, product, source, score, reason=""):
        if not product:
            return
        parser = self.env["object.request.excel.parser"]
        if parser._has_diameter_conflict(result["combined_query"], product):
            return
        if self._has_feature_conflict(result, product):
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
        policy = self.env["object.request.substitution.policy"]
        substitution = policy.evaluate_texts(
            result.get("substitution_source_text") or result["combined_query"],
            product.display_name,
        )
        feature_parser = self.env["object.request.product.feature.parser"]
        source_features = feature_parser.parse_text(
            result.get("substitution_source_text") or result["combined_query"]
        )
        candidate_features = self._product_feature_payload(product)
        substitution_reason = substitution.get("reason") or ""
        if substitution_reason:
            reason = ("%s %s" % (reason or "", substitution_reason)).strip()
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
                "requested_features": source_features,
                "candidate_features": candidate_features,
                "product_family": candidate_features.get("product_family"),
                "diameter_nominal": candidate_features.get(
                    "diameter_nominal"
                ),
                "pressure_nominal": candidate_features.get(
                    "pressure_nominal"
                ),
                "material": candidate_features.get("material"),
                "standard": candidate_features.get("standard"),
                "connection_type": candidate_features.get(
                    "connection_type"
                ),
                "stock_qty_on_issue_warehouses": 0.0,
                "stock_warehouse_names": "",
                "has_issue_stock": False,
                "stock_rank_bonus": 0.0,
                "substitution_decision": substitution["decision"],
                "substitution_reason": substitution_reason,
                "substitution_rule_applied": substitution["rule_applied"],
                "substitution_requires_confirmation": substitution[
                    "requires_confirmation"
                ],
            }
        )

    @api.model
    def _product_feature_payload(self, product):
        if not product:
            return {}
        return {
            "product_family": product.or_product_family or False,
            "diameter_nominal": product.or_diameter_nominal or False,
            "pressure_nominal": product.or_pressure_nominal or False,
            "material": product.or_material or False,
            "standard": product.or_standard or False,
            "connection_type": product.or_connection_type or False,
            "feature_key": product.or_feature_key or False,
            "parse_warning": product.or_feature_parse_warning or False,
        }

    @api.model
    def _has_feature_conflict(self, result, product):
        parser = self.env["object.request.product.feature.parser"]
        source = parser.parse_text(
            result.get("substitution_source_text") or result["combined_query"]
        )
        candidate = parser.parse_text(product.display_name)
        source_family = source.get("product_family")
        candidate_family = candidate.get("product_family")
        if (
            source_family
            and candidate_family
            and source_family != candidate_family
        ):
            return True
        source_diameter = source.get("diameter_nominal")
        candidate_diameter = candidate.get("diameter_nominal")
        if (
            source_diameter
            and candidate_diameter
            and source_diameter != candidate_diameter
        ):
            return True
        return False

    @api.model
    def _sort_candidates(self, result):
        source_rank = {
            "memory": 4,
            "supplierinfo": 3,
            "default_code": 3,
            "feature": 2,
            "name_score": 2,
            "combined_search": 1,
        }
        for index, candidate in enumerate(result["candidates"]):
            candidate["_original_order"] = index
        result["candidates"].sort(
            key=lambda item: (
                1 if item.get("source") == "memory" else 0,
                item.get("local_score", 0.0)
                + item.get("stock_rank_bonus", 0.0),
                item.get("local_score", 0.0),
                source_rank.get(item.get("source"), 0),
                -item.get("_original_order", 0),
            ),
            reverse=True,
        )
        for candidate in result["candidates"]:
            candidate.pop("_original_order", None)

    @api.model
    def _enrich_candidates_with_issue_stock(
        self,
        result,
        request=None,
        issue_warehouses=None,
    ):
        warehouses = issue_warehouses
        if not warehouses and request:
            warehouses = request._get_issue_warehouses()
        candidates = result.get("candidates", [])
        if not candidates or not warehouses:
            return
        products = self.env["product.product"].browse(
            [
                item["product_id"]
                for item in candidates
                if item.get("product_id")
            ]
        )
        qty_by_key = self._get_stock_qty_by_product_warehouse(
            products,
            warehouses,
            request=request,
        )
        for candidate in candidates:
            product_id = candidate.get("product_id")
            stock_items = []
            total_qty = 0.0
            for warehouse in warehouses:
                qty = qty_by_key.get((product_id, warehouse.id), 0.0)
                if qty <= 0:
                    continue
                total_qty += qty
                stock_items.append("%s: %g" % (warehouse.display_name, qty))
            if not total_qty:
                continue
            candidate["stock_qty_on_issue_warehouses"] = total_qty
            candidate["stock_warehouse_names"] = ", ".join(stock_items)
            candidate["has_issue_stock"] = True
            if candidate.get("substitution_decision") == "blocked":
                candidate["stock_rank_bonus"] = 0.0
            else:
                candidate["stock_rank_bonus"] = self._stock_rank_bonus(
                    candidate
                )
            stock_note = "Есть остаток на складах выдачи: %s." % (
                candidate["stock_warehouse_names"]
            )
            reason = candidate.get("reason") or ""
            candidate["reason"] = (
                "%s %s" % (reason, stock_note)
            ).strip()
        if any(item.get("has_issue_stock") for item in candidates):
            note = result.get("note") or ""
            stock_note = "Кандидаты с остатком подняты выше в shortlist."
            result["note"] = ("%s %s" % (note, stock_note)).strip()

    @api.model
    def _stock_rank_bonus(self, candidate):
        score = candidate.get("local_score", 0.0)
        if score >= 0.9:
            return 0.3
        if score >= 0.55:
            return 0.45
        if score >= 0.25:
            return 0.55
        return 0.0

    @api.model
    def _get_stock_qty_by_product_warehouse(
        self,
        products,
        warehouses,
        request=None,
    ):
        if request:
            return request._get_stock_qty_by_product_warehouse(
                products,
                warehouses,
            )
        locations_by_warehouse = self._get_stock_locations_by_warehouse(
            warehouses
        )
        all_locations = self.env["stock.location"].browse()
        for locations in locations_by_warehouse.values():
            all_locations |= locations
        if not products or not all_locations:
            return {}

        location_to_warehouse = {}
        for warehouse_id, locations in locations_by_warehouse.items():
            for location in locations:
                location_to_warehouse[location.id] = warehouse_id

        result = {}
        groups = self.env["stock.quant"].read_group(
            [
                ("product_id", "in", products.ids),
                ("location_id", "in", all_locations.ids),
            ],
            [
                "product_id",
                "location_id",
                "quantity:sum",
                "reserved_quantity:sum",
            ],
            ["product_id", "location_id"],
            lazy=False,
        )
        for group in groups:
            product_id = group["product_id"][0]
            location_id = group["location_id"][0]
            warehouse_id = location_to_warehouse.get(location_id)
            if not warehouse_id:
                continue
            qty = group.get("quantity", 0.0) - group.get(
                "reserved_quantity", 0.0
            )
            key = (product_id, warehouse_id)
            result[key] = result.get(key, 0.0) + max(qty, 0.0)
        return result

    @api.model
    def _get_stock_locations_by_warehouse(self, warehouses):
        locations_by_warehouse = {}
        location_model = self.env["stock.location"].with_context(
            active_test=False
        )
        for warehouse in warehouses:
            root = warehouse.view_location_id or warehouse.lot_stock_id
            if not root:
                locations_by_warehouse[warehouse.id] = location_model.browse()
                continue
            locations_by_warehouse[warehouse.id] = location_model.search(
                [
                    ("id", "child_of", root.id),
                    ("usage", "=", "internal"),
                ]
            )
        return locations_by_warehouse

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
            products |= Product.search(
                [("name", "ilike", key_token), ("active", "=", True)],
                limit=NAME_TOKEN_SEARCH_LIMIT,
            )
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
    def _add_feature_candidates(self, result):
        feature_parser = self.env["object.request.product.feature.parser"]
        features = feature_parser.parse_text(
            result.get("substitution_source_text") or result["combined_query"]
        )
        family = features.get("product_family")
        diameter = features.get("diameter_nominal")
        if not family or not diameter:
            return
        domain = [
            ("active", "=", True),
            ("or_product_family", "=", family),
            ("or_diameter_nominal", "=", diameter),
        ]
        pressure = features.get("pressure_nominal")
        if pressure:
            domain.append(("or_pressure_nominal", ">=", pressure))
        products = self.env["product.product"].search(
            domain,
            limit=NAME_TOKEN_SEARCH_LIMIT,
        )
        for product in products:
            score = 0.78
            reason_parts = [
                "Совпали структурные признаки: %s, DN%s."
                % (family, diameter)
            ]
            if pressure and product.or_pressure_nominal:
                if product.or_pressure_nominal == pressure:
                    score = 0.88
                    reason_parts.append("PN совпадает: PN%s." % pressure)
                elif product.or_pressure_nominal > pressure:
                    score = 0.84
                    reason_parts.append(
                        "PN кандидата выше: PN%s -> PN%s."
                        % (pressure, product.or_pressure_nominal)
                    )
            self._add_candidate(
                result,
                product,
                "feature",
                score,
                " ".join(reason_parts),
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
