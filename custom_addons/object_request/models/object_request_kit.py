# -*- coding: utf-8 -*-
"""
@file: object_request_kit.py
@description: Шаблоны типовых узлов (ВУ, АИТП, щит): строки требования
    по умолчанию и варианты строк для разных Ду. Требование создаётся из
    шаблона вместо копирования старого требования.
@dependencies: object.request, object.request.line
@created: 2026-10-17
"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ObjectRequestKit(models.Model):
    _name = "object.request.kit"
    _description = "Шаблон типового узла"
    _order = "name"

    name = fields.Char(string="Название", required=True)
    active = fields.Boolean(default=True)
    note = fields.Text(string="Примечание")
    base_size = fields.Integer(
        string="Ду базового варианта",
        required=True,
        help="Ду, для которого заданы значения строк по умолчанию.",
    )
    known_sizes = fields.Char(
        string="Варианты Ду",
        readonly=True,
        help="Ду, для которых строки шаблона проверены по требованиям.",
    )
    source_request_ids = fields.Many2many(
        "object.request",
        string="Требования-источники",
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        "object.request.kit.line",
        "kit_id",
        string="Строки",
        copy=True,
    )
    line_count = fields.Integer(
        string="Строк", compute="_compute_line_count"
    )

    @api.depends("line_ids")
    def _compute_line_count(self):
        for kit in self:
            kit.line_count = len(kit.line_ids)

    def _get_sizes(self):
        """Вернуть отсортированный список известных Ду шаблона."""
        self.ensure_one()
        sizes = {self.base_size}
        for part in (self.known_sizes or "").split(","):
            if part.strip().isdigit():
                sizes.add(int(part))
        return sorted(sizes)

    def _set_sizes(self, sizes):
        self.known_sizes = ", ".join(str(size) for size in sorted(sizes))

    def _prepare_request_line_vals(self, size, multiplier=1):
        """Вернуть значения строк требования для узла с указанным Ду."""
        self.ensure_one()
        vals_list = []
        for line in self.line_ids.sorted("sequence"):
            resolved = line._resolve(size)
            if resolved is None:
                continue
            vals_list.append(line._request_line_vals(resolved, multiplier))
        return vals_list

    def _add_size_from_request(self, request, size):
        """Добавить или обновить вариант Ду по строкам требования."""
        self.ensure_one()
        if size == self.base_size:
            raise UserError(_(
                "Ду %s — базовый вариант шаблона; строки по умолчанию "
                "меняются в самом шаблоне.", size,
            ))
        lines_by_seq = {line.sequence: line for line in self.line_ids}
        seen = self.env["object.request.kit.line"]
        for req_line in request._kit_source_lines():
            kit_line = lines_by_seq.get(req_line.sequence)
            if kit_line:
                kit_line._store_size_values(size, req_line)
                seen |= kit_line
            else:
                seen |= self._add_line_for_size_only(req_line, size)
        for kit_line in self.line_ids - seen:
            kit_line._set_variant(size, {"skip": True})
        self._set_sizes(set(self._get_sizes()) | {size})
        self.source_request_ids = [(4, request.id)]

    def _add_line_for_size_only(self, req_line, size):
        """Строка есть только в этом Ду: в остальных вариантах её нет."""
        kit_line = self.env["object.request.kit.line"].create(
            dict(
                self.env["object.request.kit.line"]._values_from_request_line(
                    req_line
                ),
                kit_id=self.id,
                sequence=req_line.sequence,
                base_skip=True,
            )
        )
        for other in self._get_sizes():
            if other != self.base_size:
                kit_line._set_variant(other, {"skip": True})
        kit_line._set_variant(
            size, kit_line._values_from_request_line(req_line)
        )
        return kit_line


class ObjectRequestKitLine(models.Model):
    _name = "object.request.kit.line"
    _description = "Строка шаблона типового узла"
    _order = "kit_id, sequence, id"

    kit_id = fields.Many2one(
        "object.request.kit",
        string="Шаблон",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="№", default=10)
    name_raw = fields.Char(string="Текст строки", required=True)
    qty_requested = fields.Float(
        string="Количество",
        digits="Product Unit of Measure",
    )
    qty_requested_pcs = fields.Float(
        string="Количество, шт.",
        digits="Product Unit of Measure",
        help="Для метизов, которые учитываются в кг (TD-016).",
    )
    uom_id = fields.Many2one("uom.uom", string="Ед. изм.")
    product_id = fields.Many2one("product.product", string="Товар")
    preferred_vendor_id = fields.Many2one(
        "res.partner",
        string="Поставщик",
        domain="[('supplier_rank', '>', 0)]",
    )
    base_skip = fields.Boolean(
        string="Нет в базовом Ду",
        help="Строки нет в узле базового Ду.",
    )
    variant_ids = fields.One2many(
        "object.request.kit.line.variant",
        "line_id",
        string="Варианты по Ду",
        copy=True,
    )
    size_dependent = fields.Boolean(
        string="Зависит от Ду",
        compute="_compute_size_dependent",
    )

    @api.depends("variant_ids")
    def _compute_size_dependent(self):
        for line in self:
            line.size_dependent = bool(line.variant_ids)

    @api.model
    def _values_from_request_line(self, req_line):
        return {
            "name_raw": req_line.name_raw,
            "qty_requested": req_line.qty_requested,
            "qty_requested_pcs": req_line.qty_requested_pcs,
            "uom_id": req_line.uom_id.id,
            "product_id": req_line.product_id.id,
            "preferred_vendor_id": req_line.preferred_vendor_id.id,
        }

    def _base_values(self):
        self.ensure_one()
        return {
            "name_raw": self.name_raw,
            "qty_requested": self.qty_requested,
            "qty_requested_pcs": self.qty_requested_pcs,
            "uom_id": self.uom_id.id,
            "product_id": self.product_id.id,
            "preferred_vendor_id": self.preferred_vendor_id.id,
        }

    def _resolve(self, size):
        """Значения строки для Ду; None — строки нет в этом варианте.

        Строка без вариантов одинакова для всех Ду. У строки с вариантами
        для неизвестного Ду товар не подставляется: снабженец подберёт его.
        """
        self.ensure_one()
        variant = self.variant_ids.filtered(lambda v: v.size == size)
        if variant:
            return None if variant.skip else variant._values()
        if size == self.kit_id.base_size or not self.size_dependent:
            return None if self.base_skip else self._base_values()
        return dict(
            self._base_values(),
            product_id=False,
            preferred_vendor_id=False,
            unknown_size=True,
        )

    def _request_line_vals(self, resolved, multiplier):
        self.ensure_one()
        product_id = resolved.get("product_id")
        vals = {
            "sequence": self.sequence,
            "name_raw": resolved["name_raw"],
            "qty_requested": resolved["qty_requested"] * multiplier,
            "qty_requested_pcs": (
                (resolved.get("qty_requested_pcs") or 0.0) * multiplier
            ),
            "uom_id": resolved.get("uom_id") or False,
            "product_id": product_id or False,
            "preferred_vendor_id": (
                resolved.get("preferred_vendor_id") or False
            ),
            "matching_required": not product_id,
            "matching_state": "matched" if product_id else "requires_mapping",
            "matching_source": "kit" if product_id else "unknown",
        }
        if resolved.get("unknown_size"):
            vals["matching_note"] = _(
                "Шаблон «%s»: для этого Ду вариант строки не задан.",
                self.kit_id.name,
            )
        return vals

    def _store_size_values(self, size, req_line):
        """Сохранить значения строки требования как вариант Ду."""
        self.ensure_one()
        values = self._values_from_request_line(req_line)
        same_as_base = values == self._base_values() and not self.base_skip
        if not self.size_dependent and same_as_base:
            return
        if not self.size_dependent:
            self._backfill_known_sizes()
        self._set_variant(size, dict(values, skip=False))

    def _backfill_known_sizes(self):
        """Строка стала зависеть от Ду: прежние Ду совпадали с базовым."""
        base = dict(self._base_values(), skip=self.base_skip)
        for size in self.kit_id._get_sizes():
            if size != self.kit_id.base_size:
                self._set_variant(size, base)

    def _set_variant(self, size, values):
        self.ensure_one()
        variant = self.variant_ids.filtered(lambda v: v.size == size)
        if variant:
            variant.write(values)
        else:
            self.env["object.request.kit.line.variant"].create(
                dict(values, line_id=self.id, size=size)
            )


class ObjectRequestKitLineVariant(models.Model):
    _name = "object.request.kit.line.variant"
    _description = "Вариант строки шаблона для Ду"
    _order = "size"

    line_id = fields.Many2one(
        "object.request.kit.line",
        string="Строка шаблона",
        required=True,
        ondelete="cascade",
        index=True,
    )
    size = fields.Integer(string="Ду", required=True)
    skip = fields.Boolean(
        string="Нет в этом Ду",
        help="В узле с этим Ду строки нет.",
    )
    name_raw = fields.Char(string="Текст строки")
    qty_requested = fields.Float(
        string="Количество",
        digits="Product Unit of Measure",
    )
    qty_requested_pcs = fields.Float(
        string="Количество, шт.",
        digits="Product Unit of Measure",
    )
    uom_id = fields.Many2one("uom.uom", string="Ед. изм.")
    product_id = fields.Many2one("product.product", string="Товар")
    preferred_vendor_id = fields.Many2one(
        "res.partner",
        string="Поставщик",
        domain="[('supplier_rank', '>', 0)]",
    )

    _line_size_unique = models.Constraint(
        "UNIQUE(line_id, size)",
        "Для этого Ду вариант строки уже задан.",
    )

    def _values(self):
        self.ensure_one()
        base = self.line_id
        return {
            "name_raw": self.name_raw or base.name_raw,
            "qty_requested": self.qty_requested,
            "qty_requested_pcs": self.qty_requested_pcs,
            "uom_id": self.uom_id.id or base.uom_id.id,
            "product_id": self.product_id.id,
            "preferred_vendor_id": self.preferred_vendor_id.id,
        }
