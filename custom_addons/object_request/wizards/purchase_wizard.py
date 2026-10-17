from datetime import datetime, time as dt_time

from odoo import models, fields, api
from odoo.exceptions import UserError


class ObjectRequestPurchaseWizard(models.TransientModel):
    _name = "object.request.purchase.wizard"
    _description = "Wizard создания черновиков закупки"

    request_id = fields.Many2one(
        "object.request",
        string="Требование",
        ondelete="cascade",
        readonly=True,
    )
    request_ids = fields.Many2many(
        "object.request",
        "object_request_purchase_wizard_request_rel",
        "wizard_id",
        "request_id",
        string="Требования",
        readonly=True,
        help="Строки к закупке собираются из всех требований.",
    )
    receipt_mode = fields.Selection(
        [
            ("common", "На один склад приёмки"),
            ("object", "На склады объектов"),
        ],
        string="Приход",
        default="common",
        required=True,
        help=(
            "«На склады объектов» — отдельная закупка на каждый склад "
            "объекта, приход сразу засчитывается требованию. «На один "
            "склад» — одна "
            "закупка на поставщика; требованиям других объектов приход "
            "засчитается после выдачи или перемещения на объект."
        ),
    )
    receipt_warning = fields.Char(
        string="Внимание", compute="_compute_receipt_warning"
    )
    append_to_drafts = fields.Boolean(
        string="Добавлять в открытые черновики поставщика",
        help=(
            "Если у поставщика уже есть черновик закупки по требованиям на "
            "этот склад приёмки, строки добавляются в него."
        ),
    )
    line_ids = fields.Many2many(
        "object.request.line",
        "object_request_purchase_wizard_line_rel",
        "wizard_id",
        "line_id",
        string="Строки к закупке",
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Склад приёмки",
        domain=(
            "[('code', '=', 'incoming'), "
            "('company_id', 'in', [False, company_id])]"
        ),
        help="Тип операции поступления для создаваемых закупок.",
    )
    company_id = fields.Many2one(
        "res.company",
        related="request_id.company_id",
        readonly=True,
    )
    group_by_vendor = fields.Boolean(
        string="Группировать по поставщику",
        default=True,
    )
    create_draft_only = fields.Boolean(
        string="Только черновики",
        default=True,
    )
    confirm_stock_guard_override = fields.Boolean(
        string="Закупить несмотря на похожий остаток",
        help=(
            "Разрешает создать закупку, если система нашла похожий товар "
            "с остатком на складах выдачи."
        ),
    )
    show_stock_guard_override = fields.Boolean(
        string="Показать обход складской проверки",
        readonly=True,
    )
    stock_guard_warning_text = fields.Text(
        string="Предупреждение по складским кандидатам",
        readonly=True,
    )
    comment = fields.Text(string="Комментарий")
    line_count = fields.Integer(
        compute="_compute_counts",
        string="Строк к закупке",
    )
    lines_without_vendor_count = fields.Integer(
        compute="_compute_counts",
        string="Строк без поставщика",
    )

    @api.depends(
        "line_ids", "line_ids.preferred_vendor_id", "line_ids.qty_to_buy"
    )  # noqa: E501
    def _compute_counts(self):
        for wiz in self:
            wiz.line_count = len(wiz.line_ids)
            wiz.lines_without_vendor_count = sum(
                1
                for ln in wiz.line_ids
                if ln.qty_to_buy > 0
                and ln.product_id
                and not ln.preferred_vendor_id
            )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        context = self.env.context
        request_ids = context.get("default_request_ids") or (
            [context["default_request_id"]]
            if context.get("default_request_id") else []
        )
        if not request_ids:
            return res
        requests = self.env["object.request"].browse(request_ids)
        lines = requests.line_ids.filtered(
            lambda ln: ln.qty_to_buy > 0 and ln.product_id
        )
        res["request_id"] = requests[0].id
        res["request_ids"] = [(6, 0, requests.ids)]
        lines = lines.filtered(
            lambda ln: not ln.purchase_order_id
            and not ln.purchase_order_line_id
        ) if len(requests) > 1 else lines
        res["line_ids"] = [(6, 0, lines.ids)]
        picking_type = self._get_default_picking_type(requests[0])
        if picking_type:
            res["picking_type_id"] = picking_type.id
        return res

    @api.depends("receipt_mode", "picking_type_id", "request_ids")
    def _compute_receipt_warning(self):
        for wizard in self:
            wizard.receipt_warning = False
            if wizard.receipt_mode != "common" or not wizard.picking_type_id:
                continue
            target = wizard.picking_type_id.warehouse_id
            others = wizard.request_ids.filtered(
                lambda req: req.project_id.warehouse_id
                and req.project_id.warehouse_id != target
            )
            if others:
                wizard.receipt_warning = (
                    "Приход на «%s»: требованиям %s он засчитается после "
                    "выдачи или перемещения на объект."
                    % (target.name, ", ".join(others.mapped("name")))
                )

    def _line_picking_type(self, line):
        if self.receipt_mode == "object":
            return (
                self._get_default_picking_type(line.request_id)
                or self.picking_type_id
            )
        return self.picking_type_id

    def _requests(self):
        """Требования мастера: список или одно требование."""
        self.ensure_one()
        return self.request_ids or self.request_id

    def _check_requests(self):
        for request in self._requests():
            request._check_supply_manager_processing_action()
            request._check_purchase_preparation_state()

    def _post_to_line_requests(self, lines, body):
        """Записать сообщение в историю требований этих строк."""
        for request in lines.request_id:
            request.message_post(
                body=body,
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )

    def action_create_purchase(self):
        self.ensure_one()
        self._check_requests()
        lines = self.line_ids.filtered(
            lambda ln: ln.qty_to_buy > 0 and ln.product_id
        )
        if not lines:
            raise UserError("Нет строк с товаром и количеством к закупке.")
        self._check_unresolved_nomenclature_warnings(lines)
        lines_with_vendor = lines.filtered("preferred_vendor_id")
        lines_no_vendor = lines - lines_with_vendor

        if not self.picking_type_id:
            raise UserError("Выберите склад приёмки для создаваемых закупок.")

        if not lines_with_vendor:
            raise UserError(
                f"Нет строк с указанным поставщиком "
                f"({len(lines_no_vendor)} строк не имеют поставщика). "
                "Назначьте поставщиков перед созданием закупки."
            )
        already_linked = lines_with_vendor.filtered(
            lambda ln: ln.purchase_order_id or ln.purchase_order_line_id
        )
        if already_linked:
            raise UserError(
                "По части строк уже создана закупка. "
                "Повторное создание PO по тем же строкам запрещено."
            )
        stock_warnings = self._find_similar_stock_purchase_warnings(
            lines_with_vendor
        )
        if stock_warnings and not self.confirm_stock_guard_override:
            self.write(
                {
                    "show_stock_guard_override": True,
                    "stock_guard_warning_text": (
                        self._format_stock_guard_warning(stock_warnings)
                    ),
                }
            )
            return self._purchase_guard_warning_action()
        if stock_warnings:
            self._log_stock_guard_override(stock_warnings)
            # Решение «Оставить закупку» принято — жёлтое предупреждение
            # на строках больше не актуально (история остаётся в chatter).
            for item in stock_warnings:
                item["line"].write(
                    item["line"]._stock_match_warning_clear_vals()
                )
        elif self.show_stock_guard_override or self.stock_guard_warning_text:
            self.write(
                {
                    "show_stock_guard_override": False,
                    "confirm_stock_guard_override": False,
                    "stock_guard_warning_text": False,
                }
            )

        created_orders = self._create_orders_by_vendor(lines_with_vendor)

        if lines_no_vendor:
            lines_no_vendor.write({"manual_vendor_required": True})
            self._post_to_line_requests(
                lines_no_vendor,
                f"{len(lines_no_vendor)} строк не имеют поставщика "
                "и остались с флагом «Требует поставщика».",
            )

        if len(created_orders) == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Черновик закупки",
                "res_model": "purchase.order",
                "res_id": created_orders[0].id,
                "view_mode": "form",
                "target": "current",
            }
        return {
            "type": "ir.actions.act_window",
            "name": "Черновики закупок",
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("id", "in", created_orders.ids)],
            "target": "current",
        }

    def _check_unresolved_nomenclature_warnings(self, lines):
        critical = lines.filtered(
            lambda line: line._requires_nomenclature_review()
        )
        if not critical:
            return
        preview = ", ".join(critical[:5].mapped("display_name"))
        suffix = ""
        if len(critical) > 5:
            suffix = " и ещё %s" % (len(critical) - 5)
        raise UserError(
            "Закупка остановлена: есть нерешённые предупреждения по "
            "номенклатуре. Проверьте строки: %s%s."
            % (preview, suffix)
        )

    def action_replace_with_stock_candidate(self):
        """Replace guarded lines and recalculate issue."""
        self.ensure_one()
        self._check_requests()
        lines = self.line_ids.filtered(
            lambda ln: ln.qty_to_buy > 0 and ln.product_id
        )
        warnings = self._find_similar_stock_purchase_warnings(lines)
        if not warnings:
            self.write(
                {
                    "show_stock_guard_override": False,
                    "confirm_stock_guard_override": False,
                    "stock_guard_warning_text": False,
                }
            )
            return self._purchase_guard_warning_action()

        updated_lines = self.env["object.request.line"]
        for item in warnings:
            line = item["line"]
            candidate = item["candidate"]
            product = self.env["product.product"].browse(
                candidate["product_id"]
            )
            stock_note = line._candidate_matching_stock_note(candidate)
            rule = self.env["object.request.product.substitute.rule"]
            if candidate.get("substitute_rule_id"):
                rule = rule.browse(candidate["substitute_rule_id"])
            line.write(
                {
                    "product_id": product.id,
                    "uom_id": product.uom_id.id,
                    "matching_required": False,
                    "matching_source": "manual",
                    "matching_note": line._append_matching_note(
                        (
                            "Перед закупкой использован разрешённый аналог: "
                            "%s. Правило: %s. %s"
                            % (
                                product.display_name,
                                rule.reason,
                                stock_note,
                            )
                        )
                        if rule
                        else (
                            "Перед закупкой выбран складской кандидат: %s. %s"
                            % (product.display_name, stock_note)
                        )
                    ),
                    **line._stock_match_warning_clear_vals(),
                }
            )
            if rule:
                rule.mark_used()
            updated_lines |= line

        if updated_lines:
            for request in updated_lines.request_id:
                request.action_check_stock()
            updated_lines.action_issue_max()
            self.line_ids = [(6, 0, self.line_ids.ids)]
            self.write(
                {
                    "show_stock_guard_override": False,
                    "confirm_stock_guard_override": False,
                    "stock_guard_warning_text": False,
                }
            )
            self._post_to_line_requests(
                updated_lines,
                "Перед созданием закупки выбран складской кандидат "
                "для строк: %s."
                % ", ".join(updated_lines.mapped("display_name")),
            )

        return self._purchase_guard_warning_action()

    def action_keep_purchase_despite_stock_candidate(self):
        """Explicitly keep purchase after stock guard warning."""
        self.ensure_one()
        self.write({"confirm_stock_guard_override": True})
        return self.action_create_purchase()

    def _purchase_guard_warning_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Проверка закупки",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _create_orders_by_vendor(self, lines):
        """Одна закупка на поставщика (и склад приёмки) по всем требованиям."""
        groups = {}
        for line in lines:
            key = (line.preferred_vendor_id, self._line_picking_type(line))
            groups.setdefault(key, []).append(line)

        created = self.env["purchase.order"]
        for (vendor, picking_type), req_lines in groups.items():
            draft = self._find_vendor_draft(vendor, picking_type)
            po = self._create_single_po(
                vendor, req_lines, order=draft, picking_type=picking_type,
            )
            created |= po
            for request in self.env["object.request.line"].concat(
                *req_lines
            ).request_id:
                request.write({"purchase_order_ids": [(4, po.id)]})
        return created

    def _find_vendor_draft(self, vendor, picking_type):
        """Открытый черновик закупки поставщика по требованиям, если нужен."""
        if not self.append_to_drafts:
            return self.env["purchase.order"]
        return self.env["purchase.order"].search(
            [
                ("partner_id", "=", vendor.id),
                ("state", "=", "draft"),
                ("is_object_request_purchase", "=", True),
                ("picking_type_id", "=", picking_type.id),
            ],
            order="id desc",
            limit=1,
        )

    def _find_similar_stock_purchase_warnings(self, lines):
        self.ensure_one()
        warnings = []
        for request in lines.request_id:
            warnings += self._find_request_stock_warnings(
                request, lines.filtered(lambda ln: ln.request_id == request)
            )
        return warnings

    def _find_request_stock_warnings(self, request, lines):
        warehouses = request._get_issue_warehouses()
        if not warehouses:
            return []
        products = lines.mapped("product_id")
        stock_by_key = request._get_stock_qty_by_product_warehouse(
            products,
            warehouses,
        )
        warnings = []
        for line in lines:
            selected_qty = sum(
                stock_by_key.get((line.product_id.id, warehouse.id), 0.0)
                for warehouse in warehouses
            )
            if selected_qty > 0:
                line.write(line._stock_match_warning_clear_vals())
                continue
            candidate = line._find_stock_match_warning_candidate(
                warehouses=warehouses,
            )
            if candidate:
                line.write(line._stock_match_warning_vals(candidate))
                warnings.append(
                    {
                        "line": line,
                        "selected_product": line.product_id.display_name,
                        "candidate": candidate,
                    }
                )
            else:
                line.write(line._stock_match_warning_clear_vals())
        return warnings

    def _format_stock_guard_warning(self, warnings):
        lines = [
            "Закупка остановлена: найдены похожие товары с остатком "
            "на складах выдачи.",
            "",
        ]
        for item in warnings[:10]:
            line = item["line"]
            candidate = item["candidate"]
            if candidate.get("substitute_rule_id"):
                kind = "разрешённый аналог"
            else:
                kind = "похожий товар"
            lines.append(
                "- %s: выбран «%s», но есть %s «%s» (%g; %s). %s"
                % (
                    line.name_raw,
                    item["selected_product"],
                    kind,
                    candidate["display_name"],
                    candidate.get("stock_qty_on_issue_warehouses", 0.0),
                    candidate.get("stock_warehouse_names")
                    or "склад не указан",
                    candidate.get("substitution_reason") or "",
                )
            )
        if len(warnings) > 10:
            lines.append("- ...и ещё %s строк." % (len(warnings) - 10))
        lines.extend(
            [
                "",
                "Выберите складской товар в строке требования или установите "
                "флаг «Закупить несмотря на похожий остаток» ниже, если "
                "кандидат не подходит.",
            ]
        )
        return "\n".join(lines)

    def _log_stock_guard_override(self, warnings):
        self.ensure_one()
        body_lines = [
            "Снабженец подтвердил закупку несмотря на похожие товары "
            "или разрешённые аналоги с остатком на складах выдачи:"
        ]
        for item in warnings:
            line = item["line"]
            candidate = item["candidate"]
            kind = (
                "разрешённый аналог"
                if candidate.get("substitute_rule_id")
                else "кандидат"
            )
            body_lines.append(
                "- %s: выбран «%s», отклонён %s «%s» (%g; %s). %s"
                % (
                    line.name_raw,
                    item["selected_product"],
                    kind,
                    candidate["display_name"],
                    candidate.get("stock_qty_on_issue_warehouses", 0.0),
                    candidate.get("stock_warehouse_names")
                    or "склад не указан",
                    candidate.get("substitution_reason") or "",
                )
            )
        self._post_to_line_requests(
            self.env["object.request.line"].concat(
                *[item["line"] for item in warnings]
            ),
            "<br/>".join(body_lines),
        )

    def _create_single_po(
        self, vendor, req_lines, order=None, picking_type=None,
    ):
        """Создать черновик закупки поставщика или дописать в ``order``."""
        lines = self.env["object.request.line"].concat(*req_lines)
        requests = lines.request_id
        picking_type = picking_type or self.picking_type_id
        po = order or self.env["purchase.order"].create(
            self._po_vals(vendor, requests, picking_type)
        )
        if order:
            names = [name for name in (order.origin or "").split(", ") if name]
            names += [name for name in requests.mapped("name")
                      if name not in names]
            order.origin = ", ".join(names)
        for line in lines:
            pol = self.env["purchase.order.line"].create(
                self._po_line_vals(po, line, multi=len(requests) > 1)
            )
            line.write(
                {
                    "purchase_order_id": po.id,
                    "purchase_order_line_id": pol.id,
                }
            )
        return po

    def _po_vals(self, vendor, requests, picking_type):
        projects = requests.project_id
        vals = {
            "partner_id": vendor.id,
            "origin": ", ".join(requests.mapped("name")),
            "is_object_request_purchase": True,
            "object_request_project_id": (
                projects.id if len(projects) == 1 else False
            ),
        }
        if picking_type:
            vals["picking_type_id"] = picking_type.id
        return vals

    def _po_line_vals(self, po, line, multi=False):
        uom = line.uom_id or line.product_id.uom_id
        need_date = line.request_id.need_date
        name = (
            line.product_id.display_name
            if line.product_id
            else (line.name_raw or "")
        )
        if multi:
            name = "%s (%s)" % (name, line.request_id.name)
        return {
            "order_id": po.id,
            "product_id": line.product_id.id,
            "product_qty": line.qty_to_buy,
            "product_uom_id": uom.id,
            "name": name,
            "price_unit": line.price_raw or 0.0,
            "date_planned": (
                datetime.combine(need_date, dt_time.min)
                if need_date
                else fields.Datetime.now()
            ),
        }

    def _get_default_picking_type(self, request):
        """Return project receipt type or company incoming fallback."""
        warehouse = request.project_id.warehouse_id
        if warehouse and warehouse.in_type_id:
            return warehouse.in_type_id
        return self.env["stock.picking.type"].search(
            [
                ("code", "=", "incoming"),
                ("company_id", "in", [False, request.company_id.id]),
            ],
            limit=1,
        )
