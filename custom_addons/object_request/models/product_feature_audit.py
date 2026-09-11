from odoo import api, fields, models


class ObjectRequestProductFeatureAuditLine(models.Model):
    _name = "object.request.product.feature.audit.line"
    _description = "Product feature audit line"
    _order = (
        "issue_type, product_family, diameter_nominal, "
        "pressure_nominal, id"
    )

    issue_type = fields.Selection(
        [
            ("duplicate", "Потенциальный дубль"),
            ("missing_diameter", "Нет DN/Ду"),
            ("pressure_conflict", "Конфликт PN"),
        ],
        string="Проблема",
        required=True,
        index=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Товар",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        store=True,
        string="Шаблон",
    )
    product_family = fields.Selection(
        related="product_id.or_product_family",
        store=True,
        string="Семейство",
    )
    diameter_nominal = fields.Integer(
        related="product_id.or_diameter_nominal",
        store=True,
        string="DN/Ду",
    )
    pressure_nominal = fields.Integer(
        related="product_id.or_pressure_nominal",
        store=True,
        string="PN",
    )
    feature_key = fields.Char(
        related="product_id.or_feature_key",
        store=True,
        string="Ключ признаков",
    )
    note = fields.Text(string="Комментарий")
    company_id = fields.Many2one(
        "res.company",
        string="Компания",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )

    @api.model
    def action_refresh_report(self):
        return self.refresh_report()

    @api.model
    def refresh_report(self):
        self.search([]).unlink()
        products = self.env["product.product"].with_context(
            active_test=False,
        ).search([("or_product_family", "!=", False)])
        vals_list = []
        vals_list.extend(self._missing_diameter_vals(products))
        vals_list.extend(self._duplicate_vals(products))
        vals_list.extend(self._pressure_conflict_vals(products))
        if vals_list:
            self.create(vals_list)
        return {
            "type": "ir.actions.act_window",
            "name": "Аудит признаков номенклатуры",
            "res_model": self._name,
            "view_mode": "list,form",
            "target": "current",
        }

    @api.model
    def _missing_diameter_vals(self, products):
        pilot = ("flange", "gasket", "reducer", "elbow", "valve")
        return [
            {
                "issue_type": "missing_diameter",
                "product_id": product.id,
                "company_id": self.env.company.id,
                "note": (
                    "Для пилотного семейства не удалось распознать DN/Ду."
                ),
            }
            for product in products.filtered(
                lambda item: (
                    item.or_product_family in pilot
                    and not item.or_diameter_nominal
                )
            )
        ]

    @api.model
    def _duplicate_vals(self, products):
        by_key = {}
        for product in products.filtered("or_feature_key"):
            by_key.setdefault(
                product.or_feature_key,
                self.env["product.product"],
            )
            by_key[product.or_feature_key] |= product
        vals = []
        for key, group in by_key.items():
            if len(group) < 2:
                continue
            names = ", ".join(group.mapped("display_name")[:5])
            for product in group:
                vals.append(
                    {
                        "issue_type": "duplicate",
                        "product_id": product.id,
                        "company_id": self.env.company.id,
                        "note": "Похожие признаки %s: %s" % (key, names),
                    }
                )
        return vals

    @api.model
    def _pressure_conflict_vals(self, products):
        by_key = {}
        for product in products.filtered(
            lambda item: item.or_product_family and item.or_diameter_nominal
        ):
            key = (product.or_product_family, product.or_diameter_nominal)
            by_key.setdefault(key, self.env["product.product"])
            by_key[key] |= product
        vals = []
        for (_family, diameter), group in by_key.items():
            pressures = {
                product.or_pressure_nominal
                for product in group
                if product.or_pressure_nominal
            }
            if len(pressures) < 2:
                continue
            pressure_label = ", ".join("PN%s" % pn for pn in sorted(pressures))
            for product in group:
                vals.append(
                    {
                        "issue_type": "pressure_conflict",
                        "product_id": product.id,
                        "company_id": self.env.company.id,
                        "note": "Для DN%s найдены разные давления: %s"
                        % (diameter, pressure_label),
                    }
                )
        return vals
