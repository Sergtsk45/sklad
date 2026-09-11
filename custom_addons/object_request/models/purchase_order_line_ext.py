# -*- coding: utf-8 -*-
"""
@file: purchase_order_line_ext.py
@description: Связанные объект и склад поступления на строке закупки.
@dependencies: purchase.order.line, purchase.order
@created: 2026-08-17
"""

from odoo import fields, models


class PurchaseOrderLineExt(models.Model):
    _inherit = "purchase.order.line"

    object_request_project_id = fields.Many2one(
        related="order_id.object_request_project_id",
        string="Объект",
        readonly=True,
    )
    dest_warehouse_id = fields.Many2one(
        related="order_id.dest_warehouse_id",
        string="Склад",
        readonly=True,
    )
