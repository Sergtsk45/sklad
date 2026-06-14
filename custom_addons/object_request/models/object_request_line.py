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
    zone = fields.Char(string="Зона", index=True)
    floor = fields.Char(string="Этаж", index=True)
    section = fields.Char(string="Участок", index=True)

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
        string="К выдаче", digits="Product Unit of Measure"
    )
    qty_to_buy = fields.Float(
        string="К закупке", digits="Product Unit of Measure"
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
        string="Выдано", digits="Product Unit of Measure"
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
            ("partially_issued", "Частично выдано"),
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
        "product_id",
        "matching_required",
        "qty_issued",
        "qty_to_issue",
        "qty_requested",
        "is_cancelled",
    )
    def _compute_line_state(self):
        for line in self:
            if line.is_cancelled:
                line.line_state = "cancelled"
            elif not line.product_id or line.matching_required:
                line.line_state = "requires_mapping"
            elif line.qty_issued >= line.qty_to_issue > 0:
                line.line_state = "fully_supplied"
            elif line.qty_issued > 0:
                line.line_state = "partially_issued"
            elif line.product_id:
                line.line_state = "ready"
            else:
                line.line_state = "draft"

    @api.depends("allowed_substitute_ids")
    def _compute_has_substitutes(self):
        for line in self:
            line.has_substitutes = bool(line.allowed_substitute_ids)

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
        return {
            "ai_candidate_product_ids": [
                (6, 0, [item["product_id"] for item in candidates])
            ],
            "ai_suggested_product_id": best["product_id"],
            "ai_match_confidence": best["local_score"],
            "ai_match_reason": " ".join(reason_parts),
        }

    def _apply_ai_suggestion_vals(self):
        self.ensure_one()
        product = self.ai_suggested_product_id
        if not product:
            raise UserError("Нет AI-кандидата для применения.")
        return {
            "product_id": product.id,
            "uom_id": product.uom_id.id,
            "matching_required": False,
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

    def action_accept_and_remember_ai_candidate(self):
        self._check_supply_manager_matching_action()
        for line in self:
            line._accept_ai_and_save_memory()
        return self.action_remember_matching()

    def _accept_ai_and_save_memory(self):
        """Принять AI-кандидата и сохранить в память сопоставлений."""
        self.ensure_one()
        self.write(self._apply_ai_suggestion_vals())
        if not self._should_save_to_memory():
            return
        parser = self.env['object.request.excel.parser']
        name_norm = parser.normalize_str(self.name_raw or '')
        designation_norm = parser.normalize_str(
            self.technical_designation or self.supplier_article or ''
        )
        Memory = self.env['object.request.matching.memory']
        existing = Memory.search([
            ('name_normalized', '=', name_norm),
            ('product_id', '=', self.ai_suggested_product_id.id),
        ], limit=1)
        if existing:
            return
        Memory.create({
            'name_normalized': name_norm,
            'designation_normalized': designation_norm or False,
            'product_id': self.ai_suggested_product_id.id,
            'confirmed_by': self.env.uid,
            'source_request_id': self.request_id.id,
            'confidence': self.ai_match_confidence or 1.0,
        })

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
        for line in self:
            article, vendor = line._validate_remember_matching_values()
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
        for line, article, vendor, action in prepared:
            if action == "skipped":
                skipped += 1
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
                    f"Создано записей: {created}. "
                    f"Уже существовало: {skipped}."
                ),
                "type": "success" if created else "info",
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
            stock_ids = line.stock_ids
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
        stock_context = {"auto_stock_distribution": True}
        for line in self.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled
        ):
            requested = max(line.qty_requested - line.qty_issued, 0.0)
            project_warehouse = line.request_id.project_id.warehouse_id
            project_stock = line.stock_ids.filtered(
                lambda stock: (
                    stock.warehouse_id == project_warehouse
                    and stock.qty_on_hand > 0
                )
            )[:1]
            other_stock_ids = (line.stock_ids - project_stock).sorted(
                key=lambda stock: stock.qty_on_hand,
                reverse=True,
            )
            stock_ids = project_stock | other_stock_ids
            stock_ids.with_context(**stock_context).write(
                {
                    "qty_to_issue": 0.0,
                }
            )
            remaining = requested
            single_stock = next(
                (
                    stock
                    for stock in stock_ids
                    if (
                        stock.qty_on_hand >= requested
                        and stock.id not in project_stock.ids
                    )
                ),
                False,
            )
            if single_stock and not project_stock:
                single_stock.with_context(**stock_context).write(
                    {
                        "qty_to_issue": requested,
                    }
                )
                remaining = 0.0
            else:
                for stock in stock_ids:
                    if remaining <= 0:
                        break
                    qty = min(max(stock.qty_on_hand, 0.0), remaining)
                    if qty <= 0:
                        continue
                    stock.with_context(**stock_context).write(
                        {"qty_to_issue": qty}
                    )
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
            line.write(
                {
                    "qty_to_issue": qty_to_issue,
                    "qty_to_buy": qty_to_buy,
                    "procurement_mode": mode,
                    "manual_plan_override": False,
                }
            )
        return True

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
        parts = [
            f"{stock.warehouse_id.display_name}: {stock.qty_on_hand:g}"
            for stock in self.stock_ids.filtered(
                lambda item: item.qty_on_hand > 0
            )
        ]
        return ", ".join(parts)
