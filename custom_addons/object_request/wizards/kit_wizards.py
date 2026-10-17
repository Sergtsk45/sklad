# -*- coding: utf-8 -*-
"""
@file: kit_wizards.py
@description: Мастера шаблонов узлов: сохранить требование в шаблон
    (новый или вариант Ду существующего) и создать требование из шаблона.
@dependencies: object.request.kit, object.request
@created: 2026-10-17
"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ObjectRequestKitSaveWizard(models.TransientModel):
    _name = "object.request.kit.save.wizard"
    _description = "Сохранить требование в шаблон узла"

    request_id = fields.Many2one(
        "object.request", string="Требование", required=True
    )
    mode = fields.Selection(
        [
            ("new", "Новый шаблон"),
            ("variant", "Вариант Ду существующего шаблона"),
        ],
        string="Действие",
        required=True,
        default="new",
    )
    kit_name = fields.Char(string="Название шаблона")
    kit_id = fields.Many2one("object.request.kit", string="Шаблон")
    size = fields.Integer(string="Ду узла", required=True)

    def action_save(self):
        """Сохранить строки требования и открыть шаблон."""
        self.ensure_one()
        if self.size <= 0:
            raise UserError(_("Укажите Ду узла, например 80."))
        if not self.request_id._kit_source_lines():
            raise UserError(_("В требовании нет строк."))
        kit = self._save_new() if self.mode == "new" else self._save_variant()
        self.request_id.message_post(body=_(
            "Строки сохранены в шаблон узла «%(kit)s», Ду%(size)s.",
            kit=kit.name, size=self.size,
        ))
        return {
            "type": "ir.actions.act_window",
            "res_model": "object.request.kit",
            "res_id": kit.id,
            "view_mode": "form",
        }

    def _save_new(self):
        if not self.kit_name:
            raise UserError(_("Укажите название шаблона."))
        KitLine = self.env["object.request.kit.line"]
        return self.env["object.request.kit"].create({
            "name": self.kit_name,
            "base_size": self.size,
            "source_request_ids": [(6, 0, self.request_id.ids)],
            "line_ids": [
                (0, 0, dict(
                    KitLine._values_from_request_line(line),
                    sequence=line.sequence,
                ))
                for line in self.request_id._kit_source_lines()
            ],
        })

    def _save_variant(self):
        if not self.kit_id:
            raise UserError(_("Выберите шаблон."))
        self.kit_id._add_size_from_request(self.request_id, self.size)
        return self.kit_id


class ObjectRequestKitCreateWizard(models.TransientModel):
    _name = "object.request.kit.create.wizard"
    _description = "Создать требование из шаблона узла"

    kit_id = fields.Many2one(
        "object.request.kit", string="Шаблон", required=True
    )
    known_sizes = fields.Char(
        string="Варианты Ду в шаблоне", compute="_compute_known_sizes"
    )
    size = fields.Integer(string="Ду узла", required=True)
    multiplier = fields.Integer(
        string="Количество узлов",
        default=1,
        required=True,
        help="Количества строк шаблона умножаются на это число.",
    )
    project_id = fields.Many2one(
        "object.request.project", string="Объект", required=True
    )
    need_date = fields.Date(string="Нужно к", required=True)
    foreman_user_id = fields.Many2one(
        "res.users",
        string="Прораб",
        required=True,
        default=lambda self: self.env.user,
    )

    @api.depends("kit_id")
    def _compute_known_sizes(self):
        for wizard in self:
            sizes = wizard.kit_id._get_sizes() if wizard.kit_id else []
            wizard.known_sizes = ", ".join(str(size) for size in sizes)

    @api.onchange("kit_id")
    def _onchange_kit_id(self):
        if self.kit_id and not self.size:
            self.size = self.kit_id.base_size

    def action_create(self):
        """Создать требование-черновик из шаблона и открыть его."""
        self.ensure_one()
        if self.size <= 0 or self.multiplier <= 0:
            raise UserError(_("Ду и количество узлов должны быть больше 0."))
        line_vals = self.kit_id._prepare_request_line_vals(
            self.size, self.multiplier
        )
        request = self.env["object.request"].create({
            "project_id": self.project_id.id,
            "foreman_user_id": self.foreman_user_id.id,
            "need_date": self.need_date,
            "line_ids": [(0, 0, vals) for vals in line_vals],
        })
        request.message_post(body=self._creation_note(request))
        return {
            "type": "ir.actions.act_window",
            "res_model": "object.request",
            "res_id": request.id,
            "view_mode": "form",
        }

    def _creation_note(self, request):
        unmatched = len(request.line_ids.filtered("matching_required"))
        note = _(
            "Создано из шаблона узла «%(kit)s», Ду%(size)s, узлов: %(n)s.",
            kit=self.kit_id.name, size=self.size, n=self.multiplier,
        )
        if self.size not in self.kit_id._get_sizes():
            note += " " + _(
                "Вариант Ду%(size)s в шаблоне не задан: строк без товара — "
                "%(count)s.", size=self.size, count=unmatched,
            )
        return note
