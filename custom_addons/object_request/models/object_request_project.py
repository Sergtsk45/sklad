from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class ObjectRequestProject(models.Model):
    _name = "object.request.project"
    _description = "Project Object for Supply Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc"

    name = fields.Char(string="Наименование", required=True, tracking=True)
    code = fields.Char(
        string="Код объекта",
        index=True,
        tracking=True,
        copy=False,
        readonly=True,
        size=10,
    )
    partner_id = fields.Many2one("res.partner", string="Заказчик")
    address = fields.Char(string="Адрес")
    comment = fields.Text(string="Комментарий")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Компания",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Склад объекта",
        readonly=True,
        copy=False,
        index=True,
    )

    request_ids = fields.One2many(
        "object.request",
        "project_id",
        string="Требования",
    )
    capture_ids = fields.One2many(
        "object.request.project.capture",
        "project_id",
        string="Захватки",
    )
    floor_ids = fields.One2many(
        "object.request.project.floor",
        "project_id",
        string="Этажи",
    )
    section_ids = fields.One2many(
        "object.request.project.section",
        "project_id",
        string="Участки",
    )
    request_count = fields.Integer(
        compute="_compute_request_count",
        string="Количество требований",
    )

    @api.depends("request_ids")
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"].sudo()
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = seq.next_by_code("object.request.project.code")
            vals.setdefault("company_id", self.env.company.id)
        projects = super().create(vals_list)
        for project in projects:
            project._ensure_project_warehouse()
        return projects

    def action_open_requests(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Требования",
            "res_model": "object.request",
            "view_mode": "list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }

    def write(self, vals):
        self._check_project_write_restrictions(vals)
        res = super().write(vals)
        if "name" in vals:
            for rec in self:
                rec._sync_warehouse_name()
        if "code" in vals:
            for rec in self:
                rec._sync_warehouse_code()
        if "company_id" in vals:
            for rec in self:
                rec._sync_warehouse_company()
        if "active" in vals:
            for rec in self:
                rec._sync_warehouse_active()
        return res

    def unlink(self):
        StockQuant = self.env["stock.quant"].sudo()
        for rec in self:
            if rec.request_ids:
                raise UserError(
                    "Нельзя удалить объект, у которого есть требования."
                )
            if rec.warehouse_id and rec.warehouse_id.view_location_id:
                has_stock = StockQuant.search_count(
                    [
                        (
                            "location_id",
                            "child_of",
                            rec.warehouse_id.view_location_id.id,
                        ),
                        ("quantity", ">", 0),
                    ]
                )
                if has_stock:
                    raise UserError(
                        "Нельзя удалить объект со складскими остатками."
                    )
        warehouses = self.warehouse_id
        res = super().unlink()
        warehouses.sudo().unlink()
        return res

    def _check_project_write_restrictions(self, vals):
        restricted = {"name", "code"} & set(vals.keys())
        if not restricted:
            return
        if self.env.user.has_group("base.group_system"):
            return
        raise UserError("Переименование объекта запрещено.")

    def _ensure_project_warehouse(self):
        self.ensure_one()
        if self.warehouse_id:
            return self.warehouse_id
        self._ensure_multiwarehouse_groups_enabled()
        Warehouse = self.env["stock.warehouse"].sudo()
        warehouse = Warehouse.create(self._prepare_project_warehouse_vals())
        super(ObjectRequestProject, self).write(
            {
                "warehouse_id": warehouse.id,
            }
        )
        return warehouse

    def _ensure_multiwarehouse_groups_enabled(self):
        group_user = self.env.ref("base.group_user")
        group_multi_wh = self.env.ref("stock.group_stock_multi_warehouses")
        group_multi_loc = self.env.ref("stock.group_stock_multi_locations")
        commands = []
        implied = group_user.sudo().implied_ids
        if group_multi_loc not in implied:
            commands.append((4, group_multi_loc.id))
        if group_multi_wh not in implied:
            commands.append((4, group_multi_wh.id))
        if commands:
            group_user.sudo().write({"implied_ids": commands})

    def _prepare_project_warehouse_vals(self):
        self.ensure_one()
        return {
            "name": f"{self.name} склад",
            "code": self.code,
            "company_id": self.company_id.id,
        }

    def _sync_warehouse_name(self):
        for rec in self.filtered("warehouse_id"):
            rec.warehouse_id.sudo().write({"name": f"{rec.name} склад"})

    def _sync_warehouse_code(self):
        for rec in self.filtered("warehouse_id"):
            rec.warehouse_id.sudo().write({"code": rec.code})

    def _sync_warehouse_company(self):
        for rec in self.filtered("warehouse_id"):
            rec.warehouse_id.sudo().write({"company_id": rec.company_id.id})

    def _sync_warehouse_active(self):
        for rec in self.filtered("warehouse_id"):
            rec.warehouse_id.sudo().write({"active": rec.active})

    @api.constrains("code")
    def _check_unique_code(self):
        for rec in self:
            if not rec.code:
                continue
            duplicate = self.search(
                [("code", "=", rec.code), ("id", "!=", rec.id)]
            )
            if duplicate:
                raise ValidationError(
                    f'Код "{rec.code}" уже используется другим объектом.'
                )
