from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

from .excel_parser import _SKIP_ARTICLES


class ObjectRequestLine(models.Model):
    _name = "object.request.line"
    _description = "Object Supply Request Line"
    _order = "request_id, sequence, id"

    # --- Связь с шапкой ---
    request_id = fields.Many2one(
        "object.request",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # --- Поля импорта ---
    sequence = fields.Integer(string="№", default=10, index=True)
    source_row_no = fields.Integer(string="Строка Excel", index=True)
    supplier_article = fields.Char(string="Артикул поставщика", index=True)
    technical_designation = fields.Char(string="Обозначение", index=True)
    name_raw = fields.Char(
        string="Наименование (из файла)", required=True, index=True
    )
    uom_raw = fields.Char(string="Ед. изм. (из файла)")
    qty_requested = fields.Float(
        string="Запрошено",
        required=True,
        digits="Product Unit of Measure",
    )
    price_raw = fields.Float(string="Цена (из файла)", digits="Product Price")
    comment = fields.Text(string="Комментарий")
    supplier_raw = fields.Char(string="Поставщик (из файла)", index=True)

    # --- Поля размещения ---
    capture_id = fields.Many2one(
        "object.request.project.capture",
        string="Захватка",
        domain="[('project_id', '=', request_id.project_id)]",
        ondelete="restrict",
        index=True,
    )
    floor_id = fields.Many2one(
        "object.request.project.floor",
        string="Этаж",
        domain="[('project_id', '=', request_id.project_id)]",
        ondelete="restrict",
        index=True,
    )
    section_id = fields.Many2one(
        "object.request.project.section",
        string="Участок",
        domain="[('project_id', '=', request_id.project_id)]",
        ondelete="restrict",
        index=True,
    )
    zone = fields.Char(string="Захватка (старое)", index=True)
    floor = fields.Char(string="Этаж (старое)", index=True)
    section = fields.Char(string="Участок (старое)", index=True)

    # --- Поля номенклатуры ---
    product_id = fields.Many2one("product.product", string="Товар", index=True)
    product_tmpl_id = fields.Many2one(
        "product.template",
        related="product_id.product_tmpl_id",
        store=True,
        index=True,
    )
    uom_id = fields.Many2one("uom.uom", string="Ед. изм.")
    preferred_vendor_id = fields.Many2one(
        "res.partner",
        string="Предпочтительный поставщик",
        domain="[('supplier_rank', '>', 0)]",
        index=True,
    )
    allowed_substitute_ids = fields.Many2many(
        "product.product",
        "object_request_line_substitute_rel",
        "line_id",
        "product_id",
        string="Допустимые замены",
    )

    # --- Поля сопоставления ---
    matching_required = fields.Boolean(
        string="Требует сопоставления",
        default=False,
        index=True,
    )
    matching_state = fields.Selection(
        [
            ("matched", "Сопоставлено"),
            ("requires_mapping", "Требует сопоставления"),
            ("manual_review", "Требует проверки"),
        ],
        string="Статус сопоставления",
        default="matched",
        required=True,
        index=True,
    )
    matching_note = fields.Text(string="Примечание по сопоставлению")
    matching_source = fields.Selection(
        [
            ("unknown", "Неизвестно"),
            ("import_auto", "Авто при импорте"),
            ("rematch_auto", "Авто при пересопоставлении"),
            ("combined_auto", "Combined search"),
            ("manual", "Ручной выбор"),
            ("llm_auto", "AI авто"),
            ("llm_confirmed", "AI подтверждено"),
        ],
        string="Источник сопоставления",
        default="unknown",
        index=True,
    )
    ai_candidate_product_ids = fields.Many2many(
        "product.product",
        "object_request_line_ai_candidate_rel",
        "line_id",
        "product_id",
        string="AI-кандидаты",
    )
    ai_suggested_product_id = fields.Many2one(
        "product.product",
        string="AI-кандидат",
        index=True,
    )
    ai_match_confidence = fields.Float(
        string="AI confidence",
        digits=(16, 2),
    )
    ai_match_reason = fields.Text(string="AI пояснение")
    stock_match_warning = fields.Boolean(
        string="Есть похожий товар на складе",
        default=False,
        index=True,
    )
    stock_match_candidate_id = fields.Many2one(
        "product.product",
        string="Складской кандидат",
        index=True,
    )
    stock_match_candidate_qty = fields.Float(
        string="Остаток кандидата",
        digits="Product Unit of Measure",
    )
    stock_match_warning_text = fields.Text(
        string="Предупреждение по номенклатуре"
    )
    substitute_rule_id = fields.Many2one(
        "object.request.product.substitute.rule",
        string="Правило аналога",
        index=True,
        readonly=True,
    )
    substitute_product_id = fields.Many2one(
        "product.product",
        string="Разрешённый аналог",
        index=True,
        readonly=True,
    )
    substitute_stock_qty = fields.Float(
        string="Остаток аналога",
        digits="Product Unit of Measure",
        readonly=True,
    )
    substitute_stock_warehouse_names = fields.Char(
        string="Склады аналога",
        readonly=True,
    )
    substitute_warning_text = fields.Text(
        string="Предупреждение по аналогу",
        readonly=True,
    )
    manual_vendor_required = fields.Boolean(
        string="Требует выбора поставщика",
        default=False,
        index=True,
    )

    # --- Поля обработки ---
    procurement_mode = fields.Selection(
        [
            ("manual", "Ручное решение"),
            ("issue", "Выдать"),
            ("buy", "Закупить"),
            ("mixed", "Частично выдать / частично закупить"),
        ],
        string="Способ обеспечения",
        default="manual",
        index=True,
    )
    qty_to_issue = fields.Float(
        string="К выдаче (план)", digits="Product Unit of Measure"
    )
    qty_to_buy = fields.Float(
        string="К закупке (план)", digits="Product Unit of Measure"
    )
    qty_reserved = fields.Float(
        string="Зарезервировано",
        digits="Product Unit of Measure",
    )
    issue_reserved = fields.Boolean(
        string="Резерв создан",
        default=False,
        index=True,
    )
    qty_issued = fields.Float(
        string="Обеспечено", digits="Product Unit of Measure"
    )
    qty_issued_from_stock = fields.Float(
        string="Со склада",
        digits="Product Unit of Measure",
        readonly=True,
    )
    qty_received_purchase = fields.Float(
        string="Поступило по закупке",
        digits="Product Unit of Measure",
        readonly=True,
    )

    # --- Технические поля склада ---
    stock_ids = fields.One2many(
        "object.request.line.stock",
        "line_id",
        string="Распределение по складам",
    )
    stock_qty_on_hand = fields.Float(
        string="Остаток на складе",
        digits="Product Unit of Measure",
    )
    stock_check_date = fields.Datetime(string="Дата проверки остатка")
    manual_plan_override = fields.Boolean(
        string="План изменён вручную",
        default=False,
        index=True,
    )

    # --- Статус строки (computed + writeable для ручной отмены) ---
    is_cancelled = fields.Boolean(
        string="Отменена",
        default=False,
        index=True,
    )
    line_state = fields.Selection(
        [
            ("draft", "Черновик"),
            ("requires_mapping", "Требует сопоставления"),
            ("ready", "Готово к обработке"),
            ("partially_issued", "Частично обеспечено"),
            ("fully_supplied", "Полностью обеспечено"),
            ("cancelled", "Отменено"),
        ],
        string="Статус строки",
        compute="_compute_line_state",
        store=True,
        index=True,
    )

    # --- Связи со стандартными документами ---
    issue_picking_id = fields.Many2one(
        "stock.picking", string="Выдача", index=True
    )
    issue_move_id = fields.Many2one(
        "stock.move", string="Движение", index=True
    )
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Закупка", index=True
    )
    purchase_order_line_id = fields.Many2one(
        "purchase.order.line",
        string="Строка закупки",
        index=True,
    )

    # --- Служебные поля ---
    company_id = fields.Many2one(
        "res.company",
        related="request_id.company_id",
        store=True,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="request_id.currency_id",
        store=True,
    )

    # --- Computed flags ---
    has_substitutes = fields.Boolean(
        compute="_compute_has_substitutes", store=True
    )
    is_fully_matched = fields.Boolean(
        compute="_compute_matching_flags", store=True
    )
    is_ready_for_issue = fields.Boolean(
        compute="_compute_readiness_flags", store=True
    )
    is_ready_for_purchase = fields.Boolean(
        compute="_compute_readiness_flags",
        store=True,
    )

    _qty_requested_positive = models.Constraint(
        "CHECK(qty_requested > 0)",
        "Запрошенное количество должно быть больше нуля.",
    )
    _qty_to_issue_non_negative = models.Constraint(
        "CHECK(qty_to_issue >= 0)",
        "Количество к выдаче не может быть отрицательным.",
    )
    _qty_to_buy_non_negative = models.Constraint(
        "CHECK(qty_to_buy >= 0)",
        "Количество к закупке не может быть отрицательным.",
    )
    _qty_issued_non_negative = models.Constraint(
        "CHECK(qty_issued >= 0)",
        "Выданное количество не может быть отрицательным.",
    )

    @api.depends(
        "sequence",
        "name_raw",
        "product_id",
        "supplier_article",
        "technical_designation",
    )
    def _compute_display_name(self):
        """Человекочитаемое имя строки для Many2one и списков."""
        for line in self:
            parts = []
            if line.sequence:
                parts.append(f"#{line.sequence}")
            article = (
                (line.supplier_article or line.technical_designation or "")
                .strip()
            )
            if article:
                parts.append(f"[{article}]")
            label = (line.name_raw or "").strip()
            if not label and line.product_id:
                label = line.product_id.display_name
            if label:
                parts.append(label)
            line.display_name = (
                " ".join(parts)
                if parts
                else f"Строка требования #{line.id}"
            )

    @api.depends(
        "product_id",
        "matching_required",
        "qty_issued",
        "qty_requested",
        "is_cancelled",
    )
    def _compute_line_state(self):
        for line in self:
            if line.is_cancelled:
                line.line_state = "cancelled"
            elif not line.product_id or line.matching_required:
                line.line_state = "requires_mapping"
            elif line.qty_issued >= line.qty_requested:
                line.line_state = "fully_supplied"
            elif line.qty_issued > 0:
                line.line_state = "partially_issued"
            elif line.product_id:
                line.line_state = "ready"
            else:
                line.line_state = "draft"

    @api.constrains("request_id", "capture_id", "floor_id", "section_id")
    def _check_location_project(self):
        for line in self:
            project = line.request_id.project_id
            line._check_location_value_project(line.capture_id, project)
            line._check_location_value_project(line.floor_id, project)
            line._check_location_value_project(line.section_id, project)

    def _check_location_value_project(self, value, project):
        if value and value.project_id != project:
            raise ValidationError(
                "Значения размещения должны относиться к объекту требования."
            )

    @api.depends("allowed_substitute_ids")
    def _compute_has_substitutes(self):
        for line in self:
            line.has_substitutes = bool(line.allowed_substitute_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("allowed_substitute_ids"):
                self._check_supply_manager_substitution_action()
        return super().create(vals_list)

    def write(self, vals):
        if "allowed_substitute_ids" in vals:
            self._check_supply_manager_substitution_action()
        return super().write(vals)

    def _check_supply_manager_substitution_action(self):
        if not self.env.user.has_group("object_request.group_supply_manager"):
            if self.env.user.has_group("base.group_system"):
                return
            raise UserError(
                "Подтверждение и ведение замен доступно только снабженцу."
            )

    @api.depends("product_id", "matching_required")
    def _compute_matching_flags(self):
        for line in self:
            line.is_fully_matched = bool(
                line.product_id and not line.matching_required
            )

    @api.depends(
        "product_id",
        "matching_required",
        "qty_to_issue",
        "qty_to_buy",
        "preferred_vendor_id",
    )
    def _compute_readiness_flags(self):
        for line in self:
            base = bool(line.product_id and not line.matching_required)
            line.is_ready_for_issue = base and line.qty_to_issue > 0
            line.is_ready_for_purchase = (
                base and line.qty_to_buy > 0 and bool(line.preferred_vendor_id)
            )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.uom_id = self.product_id.uom_id
        if not self.preferred_vendor_id and self.product_id.seller_ids:
            self.preferred_vendor_id = self.product_id.seller_ids[0].partner_id
        if self.matching_required:
            self.matching_required = False
        self.matching_source = "manual"
        self.matching_state = "matched"
        if self.request_id:
            candidate = self._find_stock_match_warning_candidate()
            if candidate:
                for key, value in self._stock_match_warning_vals(
                    candidate
                ).items():
                    self[key] = value
            else:
                for key, value in self._stock_match_warning_clear_vals(
                ).items():
                    self[key] = value

    @api.onchange("preferred_vendor_id")
    def _onchange_preferred_vendor_id(self):
        if self.preferred_vendor_id and self.manual_vendor_required:
            self.manual_vendor_required = False

    def _check_supply_manager_matching_action(self):
        if not self.env.user.has_group("object_request.group_supply_manager"):
            if self.env.user.has_group("base.group_system"):
                return
            raise UserError(
                "Запоминание сопоставлений доступно только снабженцу."
            )

    def _object_request_issue_moves(self):
        self.ensure_one()
        moves = self.stock_ids.mapped("move_id").filtered(
            lambda move: move.exists()
            and move.picking_id.is_object_request_issue
            and move.state == "done"
        )
        if (
            not moves
            and self.issue_move_id
            and self.issue_move_id.state == "done"
        ):
            moves = self.issue_move_id
        return moves

    def _object_request_purchase_receipt_moves(self):
        self.ensure_one()
        if not self.purchase_order_line_id:
            return self.env["stock.move"]
        return self.env["stock.move"].search(
            [
                ("purchase_line_id", "=", self.purchase_order_line_id.id),
                ("picking_type_id.code", "=", "incoming"),
                ("state", "=", "done"),
            ]
        )

    def _object_request_move_qty_in_line_uom(self, moves):
        self.ensure_one()
        total = 0.0
        target_uom = self.uom_id or self.product_id.uom_id
        for move in moves:
            source_uom = (
                move.product_uom
                if "product_uom" in move._fields
                else move.product_uom_id
            ) or move.product_id.uom_id
            total += source_uom._compute_quantity(move.quantity, target_uom)
        return total

    def _get_object_request_supply_quantities(self):
        self.ensure_one()
        stock_qty = self._object_request_move_qty_in_line_uom(
            self._object_request_issue_moves()
        )
        purchase_qty = self._object_request_move_qty_in_line_uom(
            self._object_request_purchase_receipt_moves()
        )
        return {
            "stock_qty": stock_qty,
            "purchase_qty": purchase_qty,
            "total_qty": stock_qty + purchase_qty,
        }

    def _get_object_request_original_issue_plan_qty(self):
        self.ensure_one()
        total = 0.0
        target_uom = self.uom_id or self.product_id.uom_id
        for stock in self.stock_ids:
            if stock.qty_planned_to_issue:
                total += stock.qty_planned_to_issue
            elif stock.move_id:
                source_uom = (
                    stock.move_id.product_uom
                    if "product_uom" in stock.move_id._fields
                    else stock.move_id.product_uom_id
                ) or stock.move_id.product_id.uom_id
                total += source_uom._compute_quantity(
                    stock.move_id.product_uom_qty,
                    target_uom,
                )
            else:
                total += stock.qty_to_issue
        return total

    def _get_object_request_original_purchase_plan_qty(self):
        self.ensure_one()
        if not self.purchase_order_line_id:
            return self.qty_to_buy
        purchase_line = self.purchase_order_line_id
        source_uom = (
            purchase_line.product_uom_id
            if "product_uom_id" in purchase_line._fields
            else purchase_line.product_uom
        )
        target_uom = self.uom_id or self.product_id.uom_id
        if source_uom:
            return source_uom._compute_quantity(
                purchase_line.product_qty,
                target_uom,
            )
        return purchase_line.product_qty

    def _get_object_request_procurement_mode(self, qty_to_issue, qty_to_buy):
        if qty_to_issue > 0 and qty_to_buy > 0:
            return "mixed"
        if qty_to_issue > 0:
            return "issue"
        if qty_to_buy > 0:
            return "buy"
        return "manual"

    def _get_object_request_supply_recompute_vals(self):
        self.ensure_one()
        quantities = self._get_object_request_supply_quantities()
        supplied = quantities["total_qty"]
        remaining_need = max(self.qty_requested - supplied, 0.0)
        issue_plan = min(
            max(
                self._get_object_request_original_issue_plan_qty()
                - quantities["stock_qty"],
                0.0,
            ),
            remaining_need,
        )
        buy_plan = min(
            max(
                self._get_object_request_original_purchase_plan_qty()
                - quantities["purchase_qty"],
                0.0,
            ),
            max(remaining_need - issue_plan, 0.0),
        )
        return {
            "qty_issued_from_stock": quantities["stock_qty"],
            "qty_received_purchase": quantities["purchase_qty"],
            "qty_issued": supplied,
            "qty_to_issue": issue_plan,
            "qty_to_buy": buy_plan,
            "procurement_mode": self._get_object_request_procurement_mode(
                issue_plan,
                buy_plan,
            ),
        }

    def recompute_supply_state_from_done_moves(self):
        """Synchronize supply quantities and remaining plan from done moves."""
        for line in self:
            line.write(line._get_object_request_supply_recompute_vals())
            line._sync_object_request_remaining_stock_plan()
        return True

    def _sync_object_request_remaining_stock_plan(self):
        self.ensure_one()
        target_uom = self.uom_id or self.product_id.uom_id
        remaining_issue_plan = self.qty_to_issue
        unlinked_plan_qty = {
            stock.id: stock.qty_to_issue
            for stock in self.stock_ids
            if not stock.move_id
        }
        sync_context = {
            "auto_stock_distribution": True,
            "supply_state_recompute": True,
            "skip_qty_to_issue_limit": True,
            "skip_stock_total_sync": True,
        }
        self.stock_ids.with_context(**sync_context).write(
            {"qty_to_issue": 0.0}
        )
        for stock in self.stock_ids:
            if stock.move_id:
                move = stock.move_id
                if stock.qty_planned_to_issue:
                    planned_qty = stock.qty_planned_to_issue
                else:
                    source_uom = (
                        move.product_uom
                        if "product_uom" in move._fields
                        else move.product_uom_id
                    ) or move.product_id.uom_id
                    planned_qty = source_uom._compute_quantity(
                        move.product_uom_qty,
                        target_uom,
                    )
                done_qty = (
                    self._object_request_move_qty_in_line_uom(move)
                    if move.state == "done"
                    else 0.0
                )
                desired_qty = max(planned_qty - done_qty, 0.0)
            else:
                desired_qty = unlinked_plan_qty.get(stock.id, 0.0)
            desired_qty = min(desired_qty, remaining_issue_plan)
            stock.with_context(**sync_context).write(
                {"qty_to_issue": desired_qty}
            )
            remaining_issue_plan = max(remaining_issue_plan - desired_qty, 0.0)
        self.stock_ids._check_qty_to_issue_limit()
        self._sync_stock_totals_from_stock_ids()

    def action_recompute_supply_state(self):
        self.recompute_supply_state_from_done_moves()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Обеспечение пересчитано",
                "message": f"Обработано строк: {len(self)}.",
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def _ai_candidate_clear_vals(self):
        return {
            "ai_candidate_product_ids": [(5, 0, 0)],
            "ai_suggested_product_id": False,
            "ai_match_confidence": 0.0,
            "ai_match_reason": False,
        }

    def _ai_candidate_result_vals(self, candidate_result):
        candidates = candidate_result.get("candidates", [])
        if not candidates:
            vals = self._ai_candidate_clear_vals()
            vals["ai_match_reason"] = (
                candidate_result.get("note") or "Кандидаты не найдены."
            )
            return vals
        best = candidates[0]
        reason_parts = [
            best.get("reason") or "Найден локальным shortlist.",
            "Источник: %s." % best.get("source", "unknown"),
        ]
        missing_tokens = best.get("missing_tokens") or []
        if missing_tokens:
            reason_parts.append(
                "Не совпали токены: %s." % ", ".join(missing_tokens[:6])
            )
        stock_note = self._candidate_matching_stock_note(best)
        if stock_note:
            reason_parts.append(stock_note)
        feature_note = self._candidate_feature_note(best)
        if feature_note:
            reason_parts.append(feature_note)
        requires_substitution_confirmation = (
            best.get("substitution_decision") == "allowed_with_confirmation"
            and best.get("substitution_requires_confirmation")
        )
        if requires_substitution_confirmation:
            reason_parts.append("Замена требует ручного подтверждения.")
        confidence = self._ai_candidate_confidence(
            best,
            candidates,
            requires_substitution_confirmation,
        )
        if requires_substitution_confirmation:
            confidence = min(confidence, 0.89)
        vals = {
            "ai_candidate_product_ids": [
                (6, 0, [item["product_id"] for item in candidates])
            ],
            "ai_suggested_product_id": best["product_id"],
            "ai_match_confidence": confidence,
            "ai_match_reason": " ".join(reason_parts),
        }
        if stock_note:
            vals["matching_note"] = self._append_matching_note(stock_note)
        return vals

    def _ai_candidate_confidence(
        self,
        best,
        candidates,
        requires_substitution_confirmation=False,
    ):
        confidence = best.get("local_score", 0.0)
        if best.get("substitution_decision") == "blocked":
            return min(confidence, 0.85)
        if requires_substitution_confirmation:
            return min(confidence, 0.89)
        if self._candidate_has_feature_conflict(best):
            return min(confidence, 0.85)
        if (
            best.get("has_issue_stock")
            and best.get("local_score", 0.0) >= 0.84
        ):
            confidence = max(confidence, 0.90)
        if self._candidate_has_better_stock_alternative(best, candidates):
            confidence = min(confidence, 0.85)
        return confidence

    def _candidate_has_better_stock_alternative(self, best, candidates):
        if best.get("has_issue_stock"):
            return False
        best_score = best.get("local_score", 0.0)
        for candidate in candidates:
            if candidate.get("product_id") == best.get("product_id"):
                continue
            if not candidate.get("has_issue_stock"):
                continue
            if candidate.get("substitution_decision") == "blocked":
                continue
            if self._candidate_has_feature_conflict(candidate):
                continue
            if candidate.get("local_score", 0.0) >= best_score - 0.05:
                return True
        return False

    def _candidate_has_feature_conflict(self, candidate):
        requested = candidate.get("requested_features") or {}
        features = candidate.get("candidate_features") or {}
        for key in ("product_family", "diameter_nominal"):
            if requested.get(key) and features.get(key):
                if requested[key] != features[key]:
                    return True
        requested_pn = requested.get("pressure_nominal")
        candidate_pn = features.get("pressure_nominal")
        if requested_pn and candidate_pn and candidate_pn < requested_pn:
            return True
        return False

    def _candidate_feature_note(self, candidate):
        features = candidate.get("candidate_features") or {}
        parts = []
        family = features.get("product_family")
        diameter = features.get("diameter_nominal")
        pressure = features.get("pressure_nominal")
        material = features.get("material")
        if family:
            parts.append("семейство=%s" % family)
        if diameter:
            parts.append("DN%s" % diameter)
        if pressure:
            parts.append("PN%s" % pressure)
        if material:
            parts.append("материал=%s" % material)
        if not parts:
            return ""
        return "Признаки кандидата: %s." % ", ".join(parts)

    def _safe_stock_rematch_apply_vals(self, candidate_result):
        self.ensure_one()
        candidates = candidate_result.get("candidates", [])
        if not candidates:
            return {}
        best = candidates[0]
        requires_confirmation = (
            best.get("substitution_decision") == "allowed_with_confirmation"
            and best.get("substitution_requires_confirmation")
            and bool(self.product_id)
        )
        confidence = self._ai_candidate_confidence(
            best,
            candidates,
            requires_confirmation,
        )
        if confidence < 0.90:
            return {}
        if not best.get("has_issue_stock"):
            return {}
        if requires_confirmation:
            return {}
        if best.get("substitution_decision") == "blocked":
            return {}
        if self._candidate_has_feature_conflict(best):
            return {}
        product = self.env["product.product"].browse(best["product_id"])
        if not product:
            return {}
        stock_note = self._candidate_matching_stock_note(best)
        return {
            "product_id": product.id,
            "uom_id": product.uom_id.id,
            "matching_required": False,
            "matching_state": "matched",
            "matching_source": "combined_auto",
            "matching_note": self._append_matching_note(
                "Переподобрано с учётом остатков: %s. %s"
                % (product.display_name, stock_note)
            ),
        }

    def _candidate_matching_stock_note(self, candidate):
        qty = candidate.get("stock_qty_on_issue_warehouses") or 0.0
        if qty <= 0:
            return ""
        warehouses = candidate.get("stock_warehouse_names") or "склад выдачи"
        return "Есть остаток на Ос.ск: %g шт (%s)." % (qty, warehouses)

    def _append_matching_note(self, note):
        self.ensure_one()
        current = (self.matching_note or "").strip()
        if not note:
            return current or False
        if note in current:
            return current
        return ("%s\n%s" % (current, note)).strip() if current else note

    def _apply_ai_suggestion_vals(self):
        self.ensure_one()
        product = self.ai_suggested_product_id
        if not product:
            raise UserError("Нет AI-кандидата для применения.")
        return {
            "product_id": product.id,
            "uom_id": product.uom_id.id,
            "matching_required": False,
            "matching_state": "matched",
            "matching_source": "llm_confirmed",
            "matching_note": self.ai_match_reason or "AI-кандидат принят.",
        }

    def action_accept_ai_candidate(self):
        self._check_supply_manager_matching_action()
        for line in self:
            line.write(line._apply_ai_suggestion_vals())
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_reject_ai_candidate(self):
        self._check_supply_manager_matching_action()
        for line in self:
            vals = line._ai_candidate_clear_vals()
            vals["ai_match_reason"] = "AI-кандидат отклонён."
            line.write(vals)
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _stock_match_warning_clear_vals(self):
        return {
            "stock_match_warning": False,
            "stock_match_candidate_id": False,
            "stock_match_candidate_qty": 0.0,
            "stock_match_warning_text": False,
            "substitute_rule_id": False,
            "substitute_product_id": False,
            "substitute_stock_qty": 0.0,
            "substitute_stock_warehouse_names": False,
            "substitute_warning_text": False,
            "allowed_substitute_ids": [(5, 0, 0)],
        }

    def _stock_match_warning_vals(self, candidate):
        if candidate.get("substitute_rule_id"):
            return self._substitute_stock_warning_vals(candidate)
        stock_note = self._candidate_matching_stock_note(candidate)
        return {
            "stock_match_warning": True,
            "stock_match_candidate_id": candidate["product_id"],
            "stock_match_candidate_qty": candidate.get(
                "stock_qty_on_issue_warehouses",
                0.0,
            ),
            "stock_match_warning_text": (
                "Выбранный товар без остатка. Есть похожий товар "
                "на складах выдачи: %s (%g; %s). %s"
            )
            % (
                candidate["display_name"],
                candidate.get("stock_qty_on_issue_warehouses", 0.0),
                candidate.get("stock_warehouse_names") or "склад не указан",
                candidate.get("substitution_reason") or "",
            ),
            "matching_note": self._append_matching_note(stock_note),
        }

    def _substitute_stock_warning_vals(self, candidate):
        stock_note = self._candidate_matching_stock_note(candidate)
        rule = self.env["object.request.product.substitute.rule"].browse(
            candidate["substitute_rule_id"]
        )
        warning = (
            "Выбранный товар без остатка. Есть разрешённый аналог "
            "по правилу: %s (%g; %s). Причина: %s"
        ) % (
            candidate["display_name"],
            candidate.get("stock_qty_on_issue_warehouses", 0.0),
            candidate.get("stock_warehouse_names") or "склад не указан",
            candidate.get("substitution_reason") or rule.reason or "",
        )
        return {
            "stock_match_warning": True,
            "stock_match_candidate_id": candidate["product_id"],
            "stock_match_candidate_qty": candidate.get(
                "stock_qty_on_issue_warehouses",
                0.0,
            ),
            "stock_match_warning_text": warning,
            "substitute_rule_id": rule.id,
            "substitute_product_id": candidate["product_id"],
            "substitute_stock_qty": candidate.get(
                "stock_qty_on_issue_warehouses",
                0.0,
            ),
            "substitute_stock_warehouse_names": (
                candidate.get("stock_warehouse_names") or False
            ),
            "substitute_warning_text": warning,
            "allowed_substitute_ids": [(6, 0, [candidate["product_id"]])],
            "matching_note": self._append_matching_note(stock_note),
        }

    def _find_substitute_stock_candidate(self, warehouses=None):
        self.ensure_one()
        if not self.product_id or self.is_cancelled:
            return None
        request = self.request_id
        warehouses = warehouses or request._get_issue_warehouses()
        if not warehouses:
            return None
        Rule = self.env["object.request.product.substitute.rule"]
        rules = Rule.search(
            Rule._applicable_domain(self.product_id, self.company_id)
        )
        if not rules:
            return None
        products = self.env["product.product"].browse()
        rule_products = []
        for rule in rules:
            product = rule.substitute_for(self.product_id)
            if not product:
                continue
            rule_products.append((rule, product))
            products |= product
        if not products:
            return None
        qty_by_key = request._get_stock_qty_by_product_warehouse(
            products,
            warehouses,
        )
        candidates = []
        for rule, product in rule_products:
            total_qty = 0.0
            stock_items = []
            for warehouse in warehouses:
                qty = qty_by_key.get((product.id, warehouse.id), 0.0)
                if qty <= 0:
                    continue
                total_qty += qty
                stock_items.append("%s: %g" % (warehouse.display_name, qty))
            if total_qty <= 0:
                continue
            candidates.append(
                {
                    "product": product,
                    "product_id": product.id,
                    "display_name": product.display_name,
                    "local_score": 1.0,
                    "source": "substitute_rule",
                    "reason": rule.reason,
                    "stock_qty_on_issue_warehouses": total_qty,
                    "stock_warehouse_names": ", ".join(stock_items),
                    "has_issue_stock": True,
                    "stock_rank_bonus": 1.0,
                    "substitution_decision": "allowed_with_confirmation",
                    "substitution_reason": rule.reason,
                    "substitution_rule_applied": True,
                    "substitution_requires_confirmation": True,
                    "substitute_rule_id": rule.id,
                }
            )
        if not candidates:
            return None
        candidates.sort(
            key=lambda item: item["stock_qty_on_issue_warehouses"],
            reverse=True,
        )
        return candidates[0]

    def _find_stock_match_warning_candidate(self, warehouses=None):
        self.ensure_one()
        if not self.product_id or self.is_cancelled:
            return None
        request = self.request_id
        warehouses = warehouses or request._get_issue_warehouses()
        if not warehouses:
            return None
        selected_qty_by_key = request._get_stock_qty_by_product_warehouse(
            self.product_id,
            warehouses,
        )
        selected_qty = sum(
            selected_qty_by_key.get((self.product_id.id, warehouse.id), 0.0)
            for warehouse in warehouses
        )
        if selected_qty > 0:
            return None
        substitute = self._find_substitute_stock_candidate(
            warehouses=warehouses,
        )
        if substitute:
            return substitute
        service = self.env["object.request.matching.candidate.service"]
        candidate_result = service.build_candidates(
            self.name_raw,
            self.supplier_article,
            vendor=self.preferred_vendor_id,
            technical_designation=self.technical_designation,
            request=request,
            issue_warehouses=warehouses,
        )
        for candidate in candidate_result.get("candidates", []):
            if candidate.get("product_id") == self.product_id.id:
                continue
            if not candidate.get("has_issue_stock"):
                continue
            if candidate.get("substitution_decision") == "blocked":
                continue
            if candidate.get("local_score", 0.0) < 0.25:
                continue
            return candidate
        return None

    def action_refresh_stock_match_warning(self):
        self._check_supply_manager_matching_action()
        updated = 0
        warnings = 0
        by_request = {}
        for line in self:
            by_request.setdefault(line.request_id, self.env[self._name])
            by_request[line.request_id] |= line
        for request, lines in by_request.items():
            warehouses = request._get_issue_warehouses()
            for line in lines:
                candidate = line._find_stock_match_warning_candidate(
                    warehouses=warehouses,
                )
                if candidate:
                    line.write(line._stock_match_warning_vals(candidate))
                    warnings += 1
                else:
                    line.write(line._stock_match_warning_clear_vals())
                updated += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Проверка номенклатуры выполнена",
                "message": (
                    f"Обработано строк: {updated}. "
                    f"Предупреждений: {warnings}."
                ),
                "type": "warning" if warnings else "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_use_substitute_product(self):
        self._check_supply_manager_matching_action()
        updated = 0
        updated_lines = self.env["object.request.line"]
        for line in self:
            candidate = line._find_substitute_stock_candidate()
            if not candidate:
                raise UserError(
                    "Разрешённый аналог с остатком больше не найден."
                )
            if (
                line.substitute_product_id
                and candidate["product_id"] != line.substitute_product_id.id
            ):
                raise UserError(
                    "Разрешённый аналог изменился. Обновите проверку строки."
                )
            product = self.env["product.product"].browse(
                candidate["product_id"]
            )
            rule = self.env["object.request.product.substitute.rule"].browse(
                candidate["substitute_rule_id"]
            )
            stock_note = line._candidate_matching_stock_note(candidate)
            old_product = line.product_id
            line.write(
                {
                    "product_id": product.id,
                    "uom_id": product.uom_id.id,
                    "matching_required": False,
                    "matching_source": "manual",
                    "matching_note": line._append_matching_note(
                        "Использован разрешённый аналог: %s вместо %s. "
                        "Правило: %s. %s"
                        % (
                            product.display_name,
                            old_product.display_name,
                            rule.reason,
                            stock_note,
                        )
                    ),
                    **line._stock_match_warning_clear_vals(),
                }
            )
            rule.mark_used()
            updated_lines |= line
            line.request_id.message_post(
                body=(
                    "Снабженец применил разрешённый аналог в строке %s: "
                    "«%s» заменён на «%s». Причина правила: %s."
                )
                % (
                    line.display_name,
                    old_product.display_name,
                    product.display_name,
                    rule.reason,
                ),
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )
            updated += 1
        for request in updated_lines.mapped("request_id"):
            request.action_check_stock()
            updated_lines.filtered(
                lambda line: line.request_id == request
            ).action_issue_max()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Аналог применён",
                "message": f"Обновлено строк: {updated}.",
                "type": "success" if updated else "warning",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_select_stock_match_candidate(self):
        self._check_supply_manager_matching_action()
        if self and all(line.substitute_rule_id for line in self):
            return self.action_use_substitute_product()
        updated = 0
        for line in self:
            if not line.stock_match_candidate_id:
                continue
            candidate = line._find_stock_match_warning_candidate()
            if not candidate:
                raise UserError(
                    "Складской кандидат больше не найден или не имеет "
                    "доступного остатка."
                )
            if candidate["product_id"] != line.stock_match_candidate_id.id:
                raise UserError(
                    "Складской кандидат изменился. Обновите проверку строки."
                )
            if candidate.get("substitute_rule_id"):
                line.action_use_substitute_product()
                updated += 1
                continue
            product = line.stock_match_candidate_id
            stock_note = line._candidate_matching_stock_note(candidate)
            line.write(
                {
                    "product_id": product.id,
                    "uom_id": product.uom_id.id,
                    "matching_required": False,
                    "matching_source": "manual",
                    "matching_note": line._append_matching_note(
                        "Выбран складской кандидат: %s. %s"
                        % (product.display_name, stock_note)
                    ),
                    **line._stock_match_warning_clear_vals(),
                }
            )
            updated += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Складской кандидат выбран",
                "message": f"Обновлено строк: {updated}.",
                "type": "success" if updated else "warning",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_accept_and_remember_ai_candidate(self):
        self._check_supply_manager_matching_action()
        for line in self:
            line._accept_ai_and_save_memory()
        return self.action_remember_matching()

    def _accept_ai_and_save_memory(self):
        """Принять AI-кандидата и сохранить в память сопоставлений."""
        self.ensure_one()
        self.write(self._apply_ai_suggestion_vals())
        self._save_matching_memory_for_product(
            confidence=self.ai_match_confidence or 1.0,
        )

    def _save_matching_memory_for_product(self, confidence=1.0):
        self.ensure_one()
        if not self.product_id:
            return False
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str(self.name_raw or '')
        if not self._should_save_to_memory_str(name_norm):
            return False
        designation_norm = parser.normalize_str(
            self.technical_designation or self.supplier_article or ''
        )
        Memory = self.env['object.request.matching.memory']
        existing = Memory.search([
            ('name_normalized', '=', name_norm),
            ('product_id', '=', self.product_id.id),
        ], limit=1)
        if existing:
            return False
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': designation_norm or False,
            'product_id': self.product_id.id,
            'confirmed_by': self.env.uid,
            'source_request_id': self.request_id.id,
            'confidence': confidence or 1.0,
        })
        return True

    @staticmethod
    def _should_save_to_memory_str(name_norm):
        """
        Проверить, стоит ли сохранять строку в память.

        Возвращает False для пустых, коротких, L=..., числовых строк.
        """
        if not name_norm or len(name_norm) < 3:
            return False
        if name_norm.lower().startswith('l='):
            return False
        if name_norm.replace('.', '').replace(',', '').isdigit():
            return False
        return True

    def _should_save_to_memory(self):
        """Проверить контекст строки перед сохранением в память."""
        self.ensure_one()
        if not self.ai_suggested_product_id:
            return False
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str(self.name_raw or '')
        return self._should_save_to_memory_str(name_norm)

    def _normalized_supplier_article(self):
        self.ensure_one()
        return self.env["object.request.excel.parser"].normalize_str(
            self.supplier_article
        )

    def _supplierinfo_vendor(self):
        self.ensure_one()
        return (
            self.preferred_vendor_id
            or self.product_id.seller_ids[:1].partner_id
        )

    def _supplierinfo_product(self, supplier_info):
        self.ensure_one()
        if supplier_info.product_id:
            return supplier_info.product_id
        if supplier_info.product_tmpl_id:
            return supplier_info.product_tmpl_id.product_variant_ids[:1]
        return self.env["product.product"].browse()

    def _is_manual_match_protected(self):
        self.ensure_one()
        if not self.product_id or self.matching_required:
            return False
        return self.matching_source == "manual"

    def _requires_nomenclature_review(self):
        """Нужна ли проверка номенклатуры до закупки."""
        self.ensure_one()
        if self.matching_required:
            return True
        if (
            self.matching_state == "manual_review"
            and not self._is_manual_match_protected()
        ):
            return True
        return False

    def _validate_remember_matching_values(self):
        self.ensure_one()
        article = self._normalized_supplier_article()
        if not self.product_id:
            raise UserError("Выберите товар перед запоминанием сопоставления.")
        if not article or article.lower() in _SKIP_ARTICLES:
            raise UserError(
                "Заполните корректный артикул перед запоминанием."
            )
        if len(article) < 3:
            raise UserError("Артикул должен быть не короче 3 символов.")
        vendor = self._supplierinfo_vendor()
        if not vendor:
            raise UserError(
                "Выберите поставщика перед запоминанием сопоставления."
            )
        return article, vendor

    def _supplierinfo_identical_domain(self, article, vendor):
        self.ensure_one()
        return [
            ("product_code", "=ilike", article),
            ("partner_id", "=", vendor.id),
            ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
            ("product_id", "=", self.product_id.id),
        ]

    def _supplierinfo_conflicts(self, article):
        self.ensure_one()
        infos = self.env["product.supplierinfo"].search(
            [("product_code", "=ilike", article)]
        )
        return infos.filtered(
            lambda info: (
                self._supplierinfo_product(info)
                and self._supplierinfo_product(info) != self.product_id
            )
        )

    def _supplierinfo_conflict_message(self, conflicts):
        self.ensure_one()
        lines = []
        for info in conflicts:
            product = self._supplierinfo_product(info)
            vendor = info.partner_id.display_name or "без поставщика"
            lines.append(
                f"- {info.product_code}: {product.display_name} ({vendor})"
            )
        return (
            "По этому артикулу уже есть сопоставление с другим товаром:\n"
            + "\n".join(lines)
        )

    def _supplierinfo_create_vals(self, article, vendor):
        self.ensure_one()
        return {
            "partner_id": vendor.id,
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "product_id": self.product_id.id,
            "product_code": article,
        }

    def _remember_matching_conflict_action(self, conflict_lines):
        message = "\n\n".join(
            line._supplierinfo_conflict_message(
                line._supplierinfo_conflicts(
                    line._normalized_supplier_article()
                )
            )
            for line in conflict_lines
        )
        wizard = self.env["object.request.remember.matching.wizard"].create(
            {
                "line_ids": [(6, 0, conflict_lines.ids)],
                "message": message,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Подтвердить конфликт сопоставления",
            "res_model": "object.request.remember.matching.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_remember_matching(self):
        self._check_supply_manager_matching_action()
        SupplierInfo = self.env["product.supplierinfo"].sudo()
        conflict_lines = self.env["object.request.line"].browse()
        prepared = []
        memory_created = 0
        for line in self:
            if not line.product_id:
                raise UserError(
                    "Выберите товар перед запоминанием сопоставления."
                )
            if line._save_matching_memory_for_product():
                memory_created += 1
            article = line._normalized_supplier_article()
            vendor = line._supplierinfo_vendor()
            if (
                not article
                or article.lower() in _SKIP_ARTICLES
                or len(article) < 3
                or not vendor
            ):
                prepared.append((line, article, vendor, "memory_only"))
                continue
            identical = SupplierInfo.search(
                line._supplierinfo_identical_domain(article, vendor),
                limit=1,
            )
            if identical:
                prepared.append((line, article, vendor, "skipped"))
                continue
            conflicts = line._supplierinfo_conflicts(article)
            if conflicts and not self.env.context.get(
                "confirm_supplierinfo_conflict"
            ):
                conflict_lines |= line
                continue
            prepared.append((line, article, vendor, "create"))

        if conflict_lines:
            return self._remember_matching_conflict_action(conflict_lines)

        created = 0
        skipped = 0
        memory_only = 0
        for line, article, vendor, action in prepared:
            if action == "skipped":
                skipped += 1
                continue
            if action == "memory_only":
                memory_only += 1
                continue
            vals = line._supplierinfo_create_vals(article, vendor)
            SupplierInfo.create(vals)
            created += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Сопоставление запомнено",
                "message": (
                    f"Память: создано {memory_created}. "
                    f"Supplierinfo: создано {created}, "
                    f"уже существовало {skipped}, "
                    f"пропущено {memory_only}."
                ),
                "type": "success" if created or memory_created else "info",
                "sticky": False,
            },
        }

    @api.onchange("qty_to_issue")
    def _onchange_qty_to_issue(self):
        """Авто-заполнение qty_to_buy = qty_requested - qty_to_issue."""
        if self.qty_requested > 0 and self.qty_to_issue >= 0:
            self.qty_to_buy = max(0.0, self.qty_requested - self.qty_to_issue)

    @api.onchange("qty_to_issue", "qty_to_buy")
    def _onchange_qty_distribution(self):
        if self.qty_to_issue > 0 and self.qty_to_buy > 0:
            self.procurement_mode = "mixed"
        elif self.qty_to_issue > 0:
            self.procurement_mode = "issue"
        elif self.qty_to_buy > 0:
            self.procurement_mode = "buy"
        else:
            self.procurement_mode = "manual"

    @api.constrains("qty_to_issue", "qty_to_buy", "qty_requested")
    def _check_qty_distribution(self):
        for line in self:
            if (
                line.qty_to_issue + line.qty_to_buy
                > line.qty_requested + 0.00001
            ):
                raise ValidationError(
                    "Сумма к выдаче и закупке не может превышать "
                    "запрошенное количество."
                )

    def _sync_stock_totals_from_stock_ids(self):
        for line in self:
            allowed_warehouses = line.request_id._get_issue_warehouses()
            stock_ids = line.stock_ids.filtered(
                lambda stock: stock.warehouse_id in allowed_warehouses
            )
            last_check_dates = stock_ids.mapped("last_check_date")
            vals = {
                "stock_qty_on_hand": sum(stock_ids.mapped("qty_on_hand")),
                "stock_check_date": max(last_check_dates)
                if last_check_dates
                else False,
                "qty_reserved": sum(stock_ids.mapped("qty_reserved")),
            }
            if not self.env.context.get("stock_check_only"):
                qty_to_issue = sum(stock_ids.mapped("qty_to_issue"))
                qty_to_buy = max(
                    line.qty_requested - line.qty_issued - qty_to_issue,
                    0.0,
                )
                if qty_to_issue > 0 and qty_to_buy > 0:
                    mode = "mixed"
                elif qty_to_issue > 0:
                    mode = "issue"
                elif qty_to_buy > 0:
                    mode = "buy"
                else:
                    mode = "manual"
                vals.update(
                    {
                        "qty_to_issue": qty_to_issue,
                        "qty_to_buy": qty_to_buy,
                        "procurement_mode": mode,
                    }
                )
            line.write(vals)

    def action_buy_all(self):
        self._check_supply_manager_mass_action()
        stock_context = {"auto_stock_distribution": True}
        for line in self.filtered(lambda ln: not ln.is_cancelled):
            line.stock_ids.with_context(**stock_context).write(
                {"qty_to_issue": 0.0}
            )
            qty_to_buy = max(line.qty_requested - line.qty_issued, 0.0)
            line.write(
                {
                    "qty_to_issue": 0.0,
                    "qty_to_buy": qty_to_buy,
                    "procurement_mode": "buy" if qty_to_buy else "manual",
                    "manual_plan_override": True,
                }
            )
        return True

    def action_issue_max(self):
        self._check_supply_manager_mass_action()
        lines = self.filtered(lambda ln: ln.product_id and not ln.is_cancelled)
        for request in lines.mapped("request_id"):
            request_lines = lines.filtered(
                lambda line: line.request_id == request
            ).sorted(key=lambda line: (line.sequence, line.id))
            request_lines._apply_auto_issue_distribution_for_lines(
                reset_manual_override=True
            )
        return True

    def _apply_auto_issue_distribution_for_lines(
        self,
        reset_manual_override=False,
    ):
        """Распределить выбранные строки с общим лимитом остатка."""
        if not self:
            return
        requests = self.mapped("request_id")
        if len(requests) != 1:
            for request in requests:
                request_lines = self.filtered(
                    lambda line: line.request_id == request
                )
                request_lines._apply_auto_issue_distribution_for_lines(
                    reset_manual_override=reset_manual_override,
                )
            return

        request = requests[0]
        stock_context = {"auto_stock_distribution": True}
        allowed_warehouse_ids = set(request._get_issue_warehouses().ids)
        selected_lines = self.filtered(
            lambda line: line.product_id and not line.is_cancelled
        ).sorted(key=lambda line: (line.sequence, line.id))
        if not selected_lines:
            return

        availability = {}
        for line in request.line_ids.filtered(
            lambda item: item.product_id and not item.is_cancelled
        ):
            for stock in line.stock_ids.filtered(
                lambda item: item.warehouse_id.id in allowed_warehouse_ids
            ):
                key = (line.product_id.id, stock.warehouse_id.id)
                availability[key] = max(
                    availability.get(key, 0.0),
                    max(stock.qty_on_hand, 0.0),
                )

        for stock in (request.line_ids - selected_lines).mapped("stock_ids"):
            if stock.qty_to_issue <= 0 or not stock.line_id.product_id:
                continue
            key = (stock.line_id.product_id.id, stock.warehouse_id.id)
            availability[key] = max(
                availability.get(key, 0.0) - stock.qty_to_issue,
                0.0,
            )

        selected_lines.mapped("stock_ids").with_context(
            **stock_context
        ).write({"qty_to_issue": 0.0})

        project_warehouse = request.project_id.warehouse_id
        for line in selected_lines:
            requested = max(line.qty_requested - line.qty_issued, 0.0)
            allowed_stocks = line.stock_ids.filtered(
                lambda stock: stock.warehouse_id.id in allowed_warehouse_ids
            )
            project_stock = allowed_stocks.filtered(
                lambda stock: stock.warehouse_id == project_warehouse
                and availability.get(
                    (line.product_id.id, stock.warehouse_id.id),
                    0.0,
                ) > 0
            )[:1]
            other_stock_ids = (allowed_stocks - project_stock).sorted(
                key=lambda stock: availability.get(
                    (line.product_id.id, stock.warehouse_id.id),
                    0.0,
                ),
                reverse=True,
            )
            stock_ids = project_stock | other_stock_ids
            remaining = requested
            single_stock = next(
                (
                    stock
                    for stock in stock_ids
                    if (
                        availability.get(
                            (line.product_id.id, stock.warehouse_id.id),
                            0.0,
                        )
                        >= requested
                        and stock.id not in project_stock.ids
                    )
                ),
                False,
            )
            if single_stock and not project_stock:
                key = (line.product_id.id, single_stock.warehouse_id.id)
                single_stock.with_context(**stock_context).write(
                    {"qty_to_issue": requested}
                )
                availability[key] = max(
                    availability.get(key, 0.0) - requested,
                    0.0,
                )
                remaining = 0.0
            else:
                for stock in stock_ids:
                    if remaining <= 0:
                        break
                    key = (line.product_id.id, stock.warehouse_id.id)
                    available = availability.get(key, 0.0)
                    qty = min(available, remaining)
                    if qty <= 0:
                        continue
                    stock.with_context(**stock_context).write(
                        {"qty_to_issue": qty}
                    )
                    availability[key] = max(available - qty, 0.0)
                    remaining -= qty

            qty_to_issue = sum(line.stock_ids.mapped("qty_to_issue"))
            qty_to_buy = max(requested - qty_to_issue, 0.0)
            if qty_to_issue > 0 and qty_to_buy > 0:
                mode = "mixed"
            elif qty_to_issue > 0:
                mode = "issue"
            elif qty_to_buy > 0:
                mode = "buy"
            else:
                mode = "manual"
            line_vals = {
                "qty_to_issue": qty_to_issue,
                "qty_to_buy": qty_to_buy,
                "procurement_mode": mode,
            }
            if reset_manual_override:
                line_vals["manual_plan_override"] = False
            line.write(line_vals)
        request._check_issue_plan_stock_limits()

    def _apply_auto_issue_distribution(self, reset_manual_override=False):
        """Распределить qty_to_issue по разрешённым складам требования."""
        self.ensure_one()
        self._apply_auto_issue_distribution_for_lines(
            reset_manual_override=reset_manual_override,
        )

    def action_reset_split(self):
        self._check_supply_manager_mass_action()
        stock_context = {"auto_stock_distribution": True}
        for line in self:
            line.stock_ids.with_context(**stock_context).write(
                {"qty_to_issue": 0.0}
            )
            line.write(
                {
                    "qty_to_issue": 0.0,
                    "qty_to_buy": 0.0,
                    "procurement_mode": "manual",
                    "manual_plan_override": False,
                }
            )
        return True

    def _check_supply_manager_mass_action(self):
        if not self.env.user.has_group("object_request.group_supply_manager"):
            if self.env.user.has_group("base.group_system"):
                return
            raise UserError(
                "Массовые действия с распределением доступны только снабженцу."
            )

    def _get_stock_breakdown_label(self):
        self.ensure_one()
        allowed_ids = set(self.request_id._get_issue_warehouses().ids)
        parts = [
            f"{stock.warehouse_id.display_name}: {stock.qty_on_hand:g}"
            for stock in self.stock_ids.filtered(
                lambda item: (
                    item.qty_on_hand > 0
                    and item.warehouse_id.id in allowed_ids
                )
            )
        ]
        return ", ".join(parts)
