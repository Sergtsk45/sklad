from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ObjectRequestLine(models.Model):
    _name = 'object.request.line'
    _description = 'Object Supply Request Line'
    _order = 'request_id, sequence, id'

    # --- Связь с шапкой ---
    request_id = fields.Many2one(
        'object.request', required=True, ondelete='cascade', index=True,
    )

    # --- Поля импорта ---
    sequence = fields.Integer(string='№', default=10, index=True)
    source_row_no = fields.Integer(string='Строка Excel', index=True)
    supplier_article = fields.Char(string='Артикул поставщика', index=True)
    name_raw = fields.Char(string='Наименование (из файла)', required=True, index=True)
    uom_raw = fields.Char(string='Ед. изм. (из файла)')
    qty_requested = fields.Float(
        string='Запрошено', required=True, digits='Product Unit of Measure',
    )
    price_raw = fields.Float(string='Цена (из файла)', digits='Product Price')
    comment = fields.Text(string='Комментарий')
    supplier_raw = fields.Char(string='Поставщик (из файла)', index=True)

    # --- Поля размещения ---
    zone = fields.Char(string='Зона', index=True)
    floor = fields.Char(string='Этаж', index=True)
    section = fields.Char(string='Участок', index=True)

    # --- Поля номенклатуры ---
    product_id = fields.Many2one('product.product', string='Товар', index=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='product_id.product_tmpl_id',
        store=True, index=True,
    )
    uom_id = fields.Many2one('uom.uom', string='Ед. изм.')
    preferred_vendor_id = fields.Many2one(
        'res.partner',
        string='Предпочтительный поставщик',
        domain="[('supplier_rank', '>', 0)]",
        index=True,
    )
    allowed_substitute_ids = fields.Many2many(
        'product.product',
        'object_request_line_substitute_rel', 'line_id', 'product_id',
        string='Допустимые замены',
    )

    # --- Поля сопоставления ---
    matching_required = fields.Boolean(
        string='Требует сопоставления', default=False, index=True,
    )
    matching_state = fields.Selection(
        [
            ('matched', 'Сопоставлено'),
            ('requires_mapping', 'Требует сопоставления'),
            ('manual_review', 'Требует проверки'),
        ],
        string='Статус сопоставления',
        default='matched', required=True, index=True,
    )
    matching_note = fields.Text(string='Примечание по сопоставлению')
    manual_vendor_required = fields.Boolean(
        string='Требует выбора поставщика', default=False, index=True,
    )

    # --- Поля обработки ---
    procurement_mode = fields.Selection(
        [
            ('manual', 'Ручное решение'),
            ('issue', 'Выдать'),
            ('buy', 'Закупить'),
            ('mixed', 'Частично выдать / частично закупить'),
        ],
        string='Способ обеспечения', default='manual', index=True,
    )
    qty_to_issue = fields.Float(string='К выдаче', digits='Product Unit of Measure')
    qty_to_buy = fields.Float(string='К закупке', digits='Product Unit of Measure')
    qty_reserved = fields.Float(
        string='Зарезервировано', digits='Product Unit of Measure',
    )
    issue_reserved = fields.Boolean(
        string='Резерв создан', default=False, index=True,
    )
    qty_issued = fields.Float(string='Выдано', digits='Product Unit of Measure')

    # --- Технические поля склада ---
    stock_qty_on_hand = fields.Float(
        string='Остаток на складе', digits='Product Unit of Measure',
    )
    stock_check_date = fields.Datetime(string='Дата проверки остатка')

    # --- Статус строки (computed + writeable для ручной отмены) ---
    is_cancelled = fields.Boolean(
        string='Отменена', default=False, index=True,
    )
    line_state = fields.Selection(
        [
            ('draft', 'Черновик'),
            ('requires_mapping', 'Требует сопоставления'),
            ('ready', 'Готово к обработке'),
            ('partially_issued', 'Частично выдано'),
            ('fully_supplied', 'Полностью обеспечено'),
            ('cancelled', 'Отменено'),
        ],
        string='Статус строки',
        compute='_compute_line_state', store=True,
        index=True,
    )

    # --- Связи со стандартными документами ---
    issue_picking_id = fields.Many2one('stock.picking', string='Выдача', index=True)
    issue_move_id = fields.Many2one('stock.move', string='Движение', index=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Закупка', index=True)
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', string='Строка закупки', index=True,
    )

    # --- Служебные поля ---
    company_id = fields.Many2one(
        'res.company', related='request_id.company_id', store=True, index=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='request_id.currency_id', store=True,
    )

    # --- Computed flags ---
    has_substitutes = fields.Boolean(compute='_compute_has_substitutes', store=True)
    is_fully_matched = fields.Boolean(compute='_compute_matching_flags', store=True)
    is_ready_for_issue = fields.Boolean(compute='_compute_readiness_flags', store=True)
    is_ready_for_purchase = fields.Boolean(
        compute='_compute_readiness_flags', store=True,
    )

    _qty_requested_positive = models.Constraint(
        'CHECK(qty_requested > 0)',
        'Запрошенное количество должно быть больше нуля.',
    )
    _qty_to_issue_non_negative = models.Constraint(
        'CHECK(qty_to_issue >= 0)',
        'Количество к выдаче не может быть отрицательным.',
    )
    _qty_to_buy_non_negative = models.Constraint(
        'CHECK(qty_to_buy >= 0)',
        'Количество к закупке не может быть отрицательным.',
    )
    _qty_issued_non_negative = models.Constraint(
        'CHECK(qty_issued >= 0)',
        'Выданное количество не может быть отрицательным.',
    )

    @api.depends(
        'product_id', 'matching_required', 'qty_issued',
        'qty_to_issue', 'qty_requested', 'is_cancelled',
    )
    def _compute_line_state(self):
        for line in self:
            if line.is_cancelled:
                line.line_state = 'cancelled'
            elif not line.product_id or line.matching_required:
                line.line_state = 'requires_mapping'
            elif line.qty_issued >= line.qty_to_issue > 0:
                line.line_state = 'fully_supplied'
            elif line.qty_issued > 0:
                line.line_state = 'partially_issued'
            elif line.product_id:
                line.line_state = 'ready'
            else:
                line.line_state = 'draft'

    @api.depends('allowed_substitute_ids')
    def _compute_has_substitutes(self):
        for line in self:
            line.has_substitutes = bool(line.allowed_substitute_ids)

    @api.depends('product_id', 'matching_required')
    def _compute_matching_flags(self):
        for line in self:
            line.is_fully_matched = bool(line.product_id and not line.matching_required)

    @api.depends('product_id', 'matching_required', 'qty_to_issue', 'qty_to_buy',
                 'preferred_vendor_id')
    def _compute_readiness_flags(self):
        for line in self:
            base = bool(line.product_id and not line.matching_required)
            line.is_ready_for_issue = base and line.qty_to_issue > 0
            line.is_ready_for_purchase = (
                base and line.qty_to_buy > 0 and bool(line.preferred_vendor_id)
            )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.uom_id = self.product_id.uom_id
        if not self.preferred_vendor_id and self.product_id.seller_ids:
            self.preferred_vendor_id = self.product_id.seller_ids[0].partner_id
        if self.matching_required:
            self.matching_required = False

    @api.onchange('preferred_vendor_id')
    def _onchange_preferred_vendor_id(self):
        if self.preferred_vendor_id and self.manual_vendor_required:
            self.manual_vendor_required = False

    @api.onchange('qty_to_issue')
    def _onchange_qty_to_issue(self):
        """Авто-заполнение qty_to_buy = qty_requested - qty_to_issue."""
        if self.qty_requested > 0 and self.qty_to_issue >= 0:
            self.qty_to_buy = max(0.0, self.qty_requested - self.qty_to_issue)

    @api.onchange('qty_to_issue', 'qty_to_buy')
    def _onchange_qty_distribution(self):
        if self.qty_to_issue > 0 and self.qty_to_buy > 0:
            self.procurement_mode = 'mixed'
        elif self.qty_to_issue > 0:
            self.procurement_mode = 'issue'
        elif self.qty_to_buy > 0:
            self.procurement_mode = 'buy'
        else:
            self.procurement_mode = 'manual'

    @api.constrains('qty_to_issue', 'qty_to_buy', 'qty_requested')
    def _check_qty_distribution(self):
        for line in self:
            if line.qty_to_issue + line.qty_to_buy > line.qty_requested + 0.00001:
                raise ValidationError(
                    'Сумма к выдаче и к закупке не может превышать запрошенное количество.'
                )
