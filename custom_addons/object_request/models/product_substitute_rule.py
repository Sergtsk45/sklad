from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ObjectRequestProductSubstituteRule(models.Model):
    _name = "object.request.product.substitute.rule"
    _description = "Object request product substitute rule"
    _order = "product_id, substitute_product_id, id"

    product_id = fields.Many2one(
        "product.product",
        string="Исходный товар",
        required=True,
        index=True,
        ondelete="restrict",
    )
    substitute_product_id = fields.Many2one(
        "product.product",
        string="Аналог",
        required=True,
        index=True,
        ondelete="restrict",
    )
    direction = fields.Selection(
        [
            ("one_way", "Односторонняя"),
            ("two_way", "Двунаправленная"),
        ],
        string="Направление",
        default="one_way",
        required=True,
        index=True,
    )
    confirmation_policy = fields.Selection(
        [
            ("always_confirm", "Всегда подтверждать"),
        ],
        string="Правило подтверждения",
        default="always_confirm",
        required=True,
    )
    reason = fields.Char(string="Причина допустимости", required=True)
    note = fields.Text(string="Пояснение для снабженца")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Компания",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    confirmed_by = fields.Many2one(
        "res.users",
        string="Подтвердил",
        readonly=True,
        copy=False,
    )
    confirmed_date = fields.Datetime(
        string="Дата подтверждения",
        readonly=True,
        copy=False,
    )
    usage_count = fields.Integer(
        string="Использований",
        default=0,
        readonly=True,
        copy=False,
    )
    last_used_date = fields.Datetime(
        string="Последнее использование",
        readonly=True,
        copy=False,
    )

    _substitute_pair_unique = models.Constraint(
        "UNIQUE(product_id, substitute_product_id, direction, company_id)",
        "Такое правило аналога уже существует для этой компании.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        self._check_supply_manager_substitute_rule_action()
        now = fields.Datetime.now()
        for vals in vals_list:
            vals.setdefault("confirmed_by", self.env.uid)
            vals.setdefault("confirmed_date", now)
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - {"active", "usage_count", "last_used_date"}:
            self._check_supply_manager_substitute_rule_action()
            vals = dict(vals)
            vals["confirmed_by"] = self.env.uid
            vals["confirmed_date"] = fields.Datetime.now()
        return super().write(vals)

    def unlink(self):
        raise UserError(
            "Правила аналогов не удаляются. Архивируйте правило вместо "
            "удаления."
        )

    @api.constrains("product_id", "substitute_product_id")
    def _check_different_products(self):
        for rule in self:
            if rule.product_id == rule.substitute_product_id:
                raise ValidationError(
                    "Исходный товар и аналог должны отличаться."
                )

    @api.constrains(
        "product_id",
        "substitute_product_id",
        "direction",
        "company_id",
        "active",
    )
    def _check_reverse_two_way_duplicate(self):
        for rule in self.filtered(lambda item: item.direction == "two_way"):
            duplicate = self.search(
                [
                    ("id", "!=", rule.id),
                    ("active", "=", True),
                    ("company_id", "=", rule.company_id.id),
                    ("direction", "=", "two_way"),
                    ("product_id", "=", rule.substitute_product_id.id),
                    ("substitute_product_id", "=", rule.product_id.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    "Для двунаправленного аналога уже есть обратное правило."
                )

    @api.constrains("product_id", "substitute_product_id")
    def _check_policy_allows_rule(self):
        policy = self.env["object.request.substitution.policy"]
        for rule in self:
            decision = policy.evaluate_texts(
                rule.product_id.display_name,
                rule.substitute_product_id.display_name,
            )
            if decision.get("decision") == "blocked":
                raise ValidationError(
                    "Нельзя создать правило аналога: %s"
                    % (decision.get("reason") or "замена запрещена")
                )
            if rule.direction == "two_way":
                reverse = policy.evaluate_texts(
                    rule.substitute_product_id.display_name,
                    rule.product_id.display_name,
                )
                if reverse.get("decision") == "blocked":
                    raise ValidationError(
                        "Нельзя создать двунаправленное правило: %s"
                        % (
                            reverse.get("reason")
                            or "обратная замена запрещена"
                        )
                    )

    def name_get(self):
        result = []
        for rule in self:
            arrow = "<->" if rule.direction == "two_way" else "->"
            result.append(
                (
                    rule.id,
                    "%s %s %s"
                    % (
                        rule.product_id.display_name,
                        arrow,
                        rule.substitute_product_id.display_name,
                    ),
                )
            )
        return result

    @api.model
    def _check_supply_manager_substitute_rule_action(self):
        if self.env.user.has_group("object_request.group_supply_manager"):
            return
        if self.env.user.has_group("base.group_system"):
            return
        raise UserError("Управление правилами аналогов доступно снабженцу.")

    @api.model
    def _applicable_domain(self, product, company):
        company_id = company.id if company else self.env.company.id
        return [
            ("active", "=", True),
            ("company_id", "=", company_id),
            "|",
            ("product_id", "=", product.id),
            "&",
            ("direction", "=", "two_way"),
            ("substitute_product_id", "=", product.id),
        ]

    def substitute_for(self, product):
        self.ensure_one()
        if self.product_id == product:
            return self.substitute_product_id
        if (
            self.direction == "two_way"
            and self.substitute_product_id == product
        ):
            return self.product_id
        return self.env["product.product"].browse()

    def mark_used(self):
        now = fields.Datetime.now()
        for rule in self:
            rule.write(
                {
                    "usage_count": rule.usage_count + 1,
                    "last_used_date": now,
                }
            )
