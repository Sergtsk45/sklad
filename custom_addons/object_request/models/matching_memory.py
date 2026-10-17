# @file: matching_memory.py
# @description: Модель памяти сопоставлений — хранит подтверждённые пары
#   (нормализованное имя + обозначение) → товар.
# @dependencies: object.request.line, excel_parser, substitution_policy
# @created: 2026-06-14

import logging

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


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

    _unique_name_product = models.Constraint(
        'UNIQUE(name_normalized, product_id)',
        'Такая пара имя+товар уже сохранена в памяти.',
    )

    @api.model
    def _remember_pair(self, vals):
        """Save a confirmed name+product pair; return True if it was saved.

        An active pair is left as is (False). An archived pair is reactivated
        with the new confirmation: the pair is unique, a second create would
        violate ``_unique_name_product``.
        """
        existing = self.with_context(active_test=False).search([
            ('name_normalized', '=', vals['name_normalized']),
            ('product_id', '=', vals['product_id']),
        ], limit=1)
        if existing.active:
            return False
        if existing:
            existing.write(dict(vals, active=True))
            return True
        self.create(vals)
        return True

    @api.model
    def backfill_flange_pn16_memory(self):
        """Create safe starter memory for PN10 flange names to PN16 cards."""
        Product = self.env['product.product'].with_context(active_test=False)
        parser = self.env['object.request.excel.parser']
        policy = self.env['object.request.substitution.policy']
        flange_products = Product.search([
            ('active', '=', True),
            ('name', 'ilike', 'Фланец'),
        ])
        candidates_by_diameter = {}
        source_products = []
        for product in flange_products:
            features = policy._extract_features(product.display_name)
            if features['family'] != 'flange' or not features['diameter']:
                continue
            if features['pn'] == 16:
                candidates_by_diameter.setdefault(
                    features['diameter'],
                    Product.browse(),
                )
                candidates_by_diameter[features['diameter']] |= product
            elif features['pn'] == 10:
                source_products.append(product)

        stats = {
            'created': 0,
            'existing': 0,
            'ambiguous': 0,
            'blocked': 0,
            'no_candidate': 0,
            'archived': 0,
        }
        for source in source_products:
            source_features = policy._extract_features(source.display_name)
            name_norm = parser.normalize_str(source.display_name)
            if not name_norm:
                stats['blocked'] += 1
                continue
            existing = self.search([
                ('name_normalized', '=', name_norm),
                ('active', '=', True),
            ], limit=1)
            if existing:
                stats['existing'] += 1
                continue
            candidates = candidates_by_diameter.get(
                source_features['diameter'],
                Product.browse(),
            ) - source
            allowed = Product.browse()
            for candidate in candidates:
                decision = policy.evaluate_texts(
                    source.display_name,
                    candidate.display_name,
                )
                if decision['decision'] == 'allowed_with_confirmation':
                    allowed |= candidate
            if not allowed:
                stats['no_candidate'] += 1
                continue
            if len(allowed) != 1:
                stats['ambiguous'] += 1
                continue
            # Пара в архиве отключена вручную — не восстанавливаем.
            if self.with_context(active_test=False).search_count([
                ('name_normalized', '=', name_norm),
                ('product_id', '=', allowed.id),
            ]):
                stats['archived'] += 1
                continue
            self.create({
                'name_normalized': name_norm,
                'designation_normalized': False,
                'product_id': allowed.id,
                'confirmed_by': self.env.uid,
                'confidence': 0.95,
            })
            stats['created'] += 1
        _logger.info(
            'object_request: flange PN16 memory backfill stats: %s',
            stats,
        )
        return stats
