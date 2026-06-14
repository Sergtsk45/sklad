# @file: matching_memory.py
# @description: Модель памяти сопоставлений — хранит подтверждённые пары
#   (нормализованное имя + обозначение) → товар.
# @dependencies: object.request.line, excel_parser
# @created: 2026-06-14

from odoo import models, fields


class ObjectRequestMatchingMemory(models.Model):
    _name = 'object.request.matching.memory'
    _description = 'Память сопоставлений требований'
    _order = 'create_date desc'
    _rec_name = 'name_normalized'

    name_normalized = fields.Char(
        string='Нормализованное наименование',
        required=True,
        index=True,
    )
    designation_normalized = fields.Char(
        string='Нормализованное обозначение',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Товар',
        required=True,
        ondelete='cascade',
        index=True,
    )
    confirmed_by = fields.Many2one(
        'res.users',
        string='Подтвердил',
        ondelete='set null',
    )
    source_request_id = fields.Many2one(
        'object.request',
        string='Источник (требование)',
        ondelete='set null',
    )
    confidence = fields.Float(
        string='Уверенность',
        default=1.0,
        digits=(16, 2),
    )
    active = fields.Boolean(
        string='Активна',
        default=True,
        index=True,
    )

    _sql_constraints = [
        (
            'unique_name_product',
            'UNIQUE(name_normalized, product_id)',
            'Такая пара имя+товар уже сохранена в памяти.',
        )
    ]
