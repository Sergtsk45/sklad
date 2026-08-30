from odoo import api, fields, models


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
