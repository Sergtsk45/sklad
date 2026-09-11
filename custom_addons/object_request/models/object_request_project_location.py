from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ObjectRequestProjectLocationMixin(models.AbstractModel):
    _name = "object.request.project.location.mixin"
    _description = "Project Location Dictionary Mixin"

    @api.model_create_multi
    def create(self, vals_list):
        self._check_duplicate_vals(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        if {"project_id", "name"} & set(vals):
            for rec in self:
                rec._check_duplicate_vals_for_record(vals)
        return super().write(vals)

    def _check_duplicate_vals(self, vals_list):
        for vals in vals_list:
            project_id = vals.get("project_id")
            name = vals.get("name")
            if project_id and name:
                self._raise_if_duplicate(project_id, name)

    def _check_duplicate_vals_for_record(self, vals):
        self.ensure_one()
        project_id = vals.get("project_id", self.project_id.id)
        name = vals.get("name", self.name)
        if project_id and name:
            self._raise_if_duplicate(project_id, name, exclude_id=self.id)

    def _raise_if_duplicate(self, project_id, name, exclude_id=False):
        domain = [
            ("project_id", "=", project_id),
            ("name", "=", name),
        ]
        if exclude_id:
            domain.append(("id", "!=", exclude_id))
        if self.search(domain, limit=1):
            raise ValidationError(self._duplicate_name_message())

    @api.constrains("project_id", "name")
    def _check_unique_name_per_project(self):
        for rec in self:
            if not rec.project_id or not rec.name:
                continue
            duplicate = self.search(
                [
                    ("project_id", "=", rec.project_id.id),
                    ("name", "=", rec.name),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(rec._duplicate_name_message())

    def _duplicate_name_message(self):
        return "Значение с таким названием уже есть у этого объекта."


class ObjectRequestProjectCapture(models.Model):
    _name = "object.request.project.capture"
    _description = "Project Capture for Object Request"
    _inherit = ["object.request.project.location.mixin"]
    _order = "project_id, sequence, name, id"

    name = fields.Char(string="Захватка", required=True, index=True)
    project_id = fields.Many2one(
        "object.request.project",
        string="Объект",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Последовательность", default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
        readonly=True,
    )

    _project_name_uniq = models.Constraint(
        "UNIQUE(project_id, name)",
        "Захватка с таким названием уже есть у этого объекта.",
    )

    def _duplicate_name_message(self):
        return "Захватка с таким названием уже есть у этого объекта."


class ObjectRequestProjectFloor(models.Model):
    _name = "object.request.project.floor"
    _description = "Project Floor for Object Request"
    _inherit = ["object.request.project.location.mixin"]
    _order = "project_id, sequence, name, id"

    name = fields.Char(string="Этаж", required=True, index=True)
    project_id = fields.Many2one(
        "object.request.project",
        string="Объект",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Последовательность", default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
        readonly=True,
    )

    _project_name_uniq = models.Constraint(
        "UNIQUE(project_id, name)",
        "Этаж с таким названием уже есть у этого объекта.",
    )

    def _duplicate_name_message(self):
        return "Этаж с таким названием уже есть у этого объекта."


class ObjectRequestProjectSection(models.Model):
    _name = "object.request.project.section"
    _description = "Project Section for Object Request"
    _inherit = ["object.request.project.location.mixin"]
    _order = "project_id, sequence, name, id"

    name = fields.Char(string="Участок", required=True, index=True)
    project_id = fields.Many2one(
        "object.request.project",
        string="Объект",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Последовательность", default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
        readonly=True,
    )

    _project_name_uniq = models.Constraint(
        "UNIQUE(project_id, name)",
        "Участок с таким названием уже есть у этого объекта.",
    )

    def _duplicate_name_message(self):
        return "Участок с таким названием уже есть у этого объекта."
