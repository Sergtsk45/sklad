from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fastener_mass import suggest_kg_per_piece


PRODUCT_FAMILY_SELECTION = [
    ("flange", "Фланец"),
    ("gasket", "Прокладка"),
    ("reducer", "Переход"),
    ("elbow", "Отвод"),
    ("valve", "Кран/клапан"),
    ("pipe", "Труба"),
]

MATERIAL_SELECTION = [
    ("steel", "Сталь"),
    ("stainless", "Нержавеющая сталь"),
    ("brass", "Латунь"),
    ("cast_iron", "Чугун"),
    ("paronite", "Паронит"),
    ("rubber", "Резина"),
    ("pvc", "ПВХ"),
    ("polypropylene", "Полипропилен"),
]

CONNECTION_SELECTION = [
    ("flanged", "Фланцевое"),
    ("threaded", "Резьбовое/муфтовое"),
    ("welded", "Под приварку"),
    ("socket", "Раструбное"),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    or_product_family = fields.Selection(
        PRODUCT_FAMILY_SELECTION,
        string="Семейство",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_diameter_nominal = fields.Integer(
        string="DN/Ду",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_pressure_nominal = fields.Integer(
        string="PN",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_material = fields.Selection(
        MATERIAL_SELECTION,
        string="Материал",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_standard = fields.Char(
        string="Стандарт",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_connection_type = fields.Selection(
        CONNECTION_SELECTION,
        string="Тип соединения",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
        readonly=False,
    )
    or_feature_key = fields.Char(
        string="Ключ признаков",
        compute="_compute_object_request_product_features",
        store=True,
        index=True,
    )
    or_feature_parse_warning = fields.Char(
        string="Предупреждение признаков",
        compute="_compute_object_request_product_features",
        store=True,
    )
    kg_per_meter = fields.Float(
        string="Кг/м",
        digits="Product Unit of Measure",
        help=(
            "Коэффициент массы погонного метра трубы. "
            "Используется для пересчёта кг/т в метры."
        ),
    )
    kg_per_piece = fields.Float(
        string="Масса 1 шт., кг",
        digits=(16, 4),
        help=(
            "Для метизов, которые учитываются и закупаются в кг: "
            "в требовании потребность вводится в шт. и пересчитывается "
            "в кг по этому коэффициенту (TD-016)."
        ),
    )

    kg_per_piece_suggested = fields.Float(
        string="Расчётная масса 1 шт., кг",
        digits=(16, 4),
        compute="_compute_kg_per_piece_suggested",
        help=(
            "Теоретическая масса болта (ГОСТ 7798) или гайки (ГОСТ 5915) "
            "по наименованию: размеры стандарта, сталь 7,85 г/см³, без "
            "фасок. Проверьте по счёту или взвешиванием."
        ),
    )

    @api.depends("name")
    def _compute_kg_per_piece_suggested(self):
        for template in self:
            template.kg_per_piece_suggested = suggest_kg_per_piece(
                template.name
            )

    def _is_weight_uom(self, uom):
        kg = self.env.ref("uom.product_uom_kgm", raise_if_not_found=False)
        return bool(uom and kg and uom._has_common_reference(kg))

    @api.model_create_multi
    def create(self, vals_list):
        """Новый метиз в кг сразу получает расчётную массу 1 шт."""
        templates = super().create(vals_list)
        templates._fill_kg_per_piece_from_suggestion()
        return templates

    def write(self, vals):
        result = super().write(vals)
        if {"uom_id", "name"} & set(vals) and "kg_per_piece" not in vals:
            self._fill_kg_per_piece_from_suggestion()
        return result

    def _fill_kg_per_piece_from_suggestion(self):
        for template in self:
            if (
                not template.kg_per_piece
                and template.kg_per_piece_suggested
                and template._is_weight_uom(template.uom_id)
            ):
                template.kg_per_piece = template.kg_per_piece_suggested

    @api.onchange("name", "uom_id")
    def _onchange_kg_per_piece_suggestion(self):
        """В форме подставить расчётную массу, если поле пустое."""
        if (
            not self.kg_per_piece
            and self.kg_per_piece_suggested
            and self._is_weight_uom(self.uom_id)
        ):
            self.kg_per_piece = self.kg_per_piece_suggested

    def action_apply_kg_per_piece_suggestion(self):
        """Заменить массу 1 шт. расчётной по ГОСТ."""
        for template in self.filtered("kg_per_piece_suggested"):
            template.kg_per_piece = template.kg_per_piece_suggested
        return True

    @api.constrains("kg_per_piece", "uom_id")
    def _check_kg_per_piece_uom(self):
        """Масса 1 шт. имеет смысл только для товара в единицах веса."""
        kg = self.env.ref("uom.product_uom_kgm", raise_if_not_found=False)
        for template in self:
            if template.kg_per_piece < 0:
                raise ValidationError(
                    "Масса 1 шт. не может быть отрицательной."
                )
            if (
                template.kg_per_piece
                and kg
                and not template.uom_id._has_common_reference(kg)
            ):
                raise ValidationError(
                    f"«Масса 1 шт.» задаётся только для товара в единицах "
                    f"веса: у «{template.display_name}» единица "
                    f"«{template.uom_id.name}»."
                )

    @api.depends("name")
    def _compute_object_request_product_features(self):
        parser = self.env["object.request.product.feature.parser"]
        for template in self:
            features = parser.parse_text(template.name)
            template.or_product_family = features["product_family"]
            template.or_diameter_nominal = (
                features["diameter_nominal"] or 0
            )
            template.or_pressure_nominal = (
                features["pressure_nominal"] or 0
            )
            template.or_material = features["material"]
            template.or_standard = features["standard"]
            template.or_connection_type = features["connection_type"]
            template.or_feature_key = parser.feature_key(features)
            template.or_feature_parse_warning = features["warning"]


class ProductProduct(models.Model):
    _inherit = "product.product"

    or_product_family = fields.Selection(
        related="product_tmpl_id.or_product_family",
        store=True,
        index=True,
        readonly=False,
    )
    or_diameter_nominal = fields.Integer(
        related="product_tmpl_id.or_diameter_nominal",
        store=True,
        index=True,
        readonly=False,
    )
    or_pressure_nominal = fields.Integer(
        related="product_tmpl_id.or_pressure_nominal",
        store=True,
        index=True,
        readonly=False,
    )
    or_material = fields.Selection(
        related="product_tmpl_id.or_material",
        store=True,
        index=True,
        readonly=False,
    )
    or_standard = fields.Char(
        related="product_tmpl_id.or_standard",
        store=True,
        index=True,
        readonly=False,
    )
    or_connection_type = fields.Selection(
        related="product_tmpl_id.or_connection_type",
        store=True,
        index=True,
        readonly=False,
    )
    or_feature_key = fields.Char(
        related="product_tmpl_id.or_feature_key",
        store=True,
        index=True,
    )
    or_feature_parse_warning = fields.Char(
        related="product_tmpl_id.or_feature_parse_warning",
        store=True,
    )
    kg_per_meter = fields.Float(
        related="product_tmpl_id.kg_per_meter",
        store=True,
        readonly=False,
    )
    kg_per_piece = fields.Float(
        related="product_tmpl_id.kg_per_piece",
        readonly=False,
    )
    kg_per_piece_suggested = fields.Float(
        related="product_tmpl_id.kg_per_piece_suggested",
    )

    def action_apply_kg_per_piece_suggestion(self):
        """Заменить массу 1 шт. расчётной по ГОСТ."""
        return self.product_tmpl_id.action_apply_kg_per_piece_suggestion()
