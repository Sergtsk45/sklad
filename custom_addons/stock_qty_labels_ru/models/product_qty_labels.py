from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available = fields.Float(string="На складе")
    virtual_available = fields.Float(string="Доступно")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available = fields.Float(string="На складе")
    virtual_available = fields.Float(string="Доступно")
