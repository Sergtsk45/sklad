from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ObjectRequest(models.Model):
    _name = 'object.request'
    _description = 'Object Supply Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    # --- Основные поля ---
    name = fields.Char(
        string='Номер документа', required=True, copy=False,
        readonly=True, default='New', tracking=True,
    )
    project_id = fields.Many2one(
        'object.request.project', string='Объект',
        required=True, tracking=True, index=True,
    )
    foreman_user_id = fields.Many2one(
        'res.users', string='Прораб',
        required=True, tracking=True, index=True,
    )
    need_date = fields.Date(
        string='Дата потребности', required=True, tracking=True, index=True,
    )
    priority = fields.Selection(
        [
            ('0', 'Низкий'),
            ('1', 'Обычный'),
            ('2', 'Высокий'),
            ('3', 'Критический'),
        ],
        string='Приоритет', default='1', required=True, tracking=True, index=True,
    )
    comment = fields.Text(string='Комментарий')
    state = fields.Selection(
        [
            ('draft', 'Черновик'),
            ('in_progress', 'В работе'),
            ('closed', 'Закрыто'),
            ('cancelled', 'Отменено'),
        ],
        string='Статус', default='draft', required=True, tracking=True, index=True,
    )
    active = fields.Boolean(default=True)

    # --- Строки ---
    line_ids = fields.One2many(
        'object.request.line', 'request_id', string='Строки', copy=True,
    )

    # --- Поля импорта ---
    source_file_name = fields.Char(string='Имя файла')
    source_file_checksum = fields.Char(string='Контрольная сумма', index=True)
    imported_at = fields.Datetime(string='Дата импорта', readonly=True)
    imported_by_user_id = fields.Many2one(
        'res.users', string='Импортировал', readonly=True,
    )

    # --- Поля процесса ---
    matching_state = fields.Selection(
        [
            ('all_matched', 'Все сопоставлено'),
            ('partial', 'Есть проблемы'),
            ('requires_mapping', 'Требует сопоставления'),
        ],
        string='Статус сопоставления',
        compute='_compute_matching_state', store=True, index=True,
    )
    approval_state = fields.Selection(
        [
            ('not_required', 'Не требуется'),
            ('pending', 'Ожидает согласования'),
            ('approved', 'Согласовано'),
            ('rejected', 'Отклонено'),
        ],
        string='Согласование', default='not_required', tracking=True,
    )

    # --- Ролевые поля ---
    buyer_user_id = fields.Many2one('res.users', string='Снабженец', tracking=True)
    warehouse_user_id = fields.Many2one('res.users', string='Кладовщик', tracking=True)
    approver_user_id = fields.Many2one(
        'res.users', string='Согласующий', tracking=True,
    )

    # --- Связи с документами Odoo ---
    issue_picking_ids = fields.Many2many(
        'stock.picking',
        'object_request_stock_picking_rel', 'request_id', 'picking_id',
        string='Выдачи',
    )
    issue_picking_count = fields.Integer(compute='_compute_issue_picking_count')

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'object_request_purchase_order_rel', 'request_id', 'purchase_id',
        string='Закупки',
    )
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')

    # --- Агрегатные счётчики ---
    line_count = fields.Integer(compute='_compute_line_count', string='Строк')
    line_problem_count = fields.Integer(compute='_compute_line_counters', store=True)
    line_matched_count = fields.Integer(compute='_compute_line_counters', store=True)
    line_to_issue_count = fields.Integer(compute='_compute_line_counters', store=True)
    line_to_buy_count = fields.Integer(compute='_compute_line_counters', store=True)
    line_fully_supplied_count = fields.Integer(
        compute='_compute_line_counters', store=True,
    )

    # --- Количественные агрегаты ---
    qty_total_requested = fields.Float(compute='_compute_qty_totals', store=True)
    qty_total_to_issue = fields.Float(compute='_compute_qty_totals', store=True)
    qty_total_to_buy = fields.Float(compute='_compute_qty_totals', store=True)
    qty_total_issued = fields.Float(compute='_compute_qty_totals', store=True)
    qty_total_reserved = fields.Float(compute='_compute_qty_totals', store=True)

    # --- Служебные поля ---
    company_id = fields.Many2one(
        'res.company', string='Компания', required=True,
        default=lambda self: self.env.company, index=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Склад',
        required=True,
        tracking=True,
        index=True,
        domain="[('company_id', '=', company_id)]",
        default=lambda self: self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1,
        ),
    )
    check_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'object_request_check_warehouse_rel',
        'request_id', 'warehouse_id',
        string='Склады для проверки наличия',
        domain="[('company_id', '=', company_id)]",
    )
    stock_check_confirmed = fields.Boolean(
        string='Наличие подтверждено', default=False,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,
    )

    _name_uniq = models.Constraint(
        'UNIQUE(name)',
        'Номер документа должен быть уникальным.',
    )

    # --- Создание с автонумерацией ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].sudo().next_by_code('object.request.sequence')
                    or 'New'
                )
        return super().create(vals_list)

    # --- Computed methods ---
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.depends('line_ids.matching_required', 'line_ids.product_id')
    def _compute_matching_state(self):
        for rec in self:
            if not rec.line_ids:
                rec.matching_state = 'all_matched'
                continue
            problem = sum(
                1 for ln in rec.line_ids if ln.matching_required or not ln.product_id
            )
            if problem == 0:
                rec.matching_state = 'all_matched'
            elif problem == len(rec.line_ids):
                rec.matching_state = 'requires_mapping'
            else:
                rec.matching_state = 'partial'

    @api.depends(
        'line_ids.line_state', 'line_ids.matching_required',
        'line_ids.manual_vendor_required',
        'line_ids.qty_to_issue', 'line_ids.qty_to_buy',
    )
    def _compute_line_counters(self):
        for rec in self:
            lns = rec.line_ids
            rec.line_problem_count = sum(
                1 for ln in lns if ln.matching_required or ln.manual_vendor_required
            )
            rec.line_matched_count = sum(
                1 for ln in lns if not ln.matching_required and ln.product_id
            )
            rec.line_to_issue_count = sum(1 for ln in lns if ln.qty_to_issue > 0)
            rec.line_to_buy_count = sum(1 for ln in lns if ln.qty_to_buy > 0)
            rec.line_fully_supplied_count = sum(
                1 for ln in lns if ln.line_state == 'fully_supplied'
            )

    @api.depends(
        'line_ids.qty_requested', 'line_ids.qty_to_issue',
        'line_ids.qty_to_buy', 'line_ids.qty_issued', 'line_ids.qty_reserved',
    )
    def _compute_qty_totals(self):
        for rec in self:
            lns = rec.line_ids
            rec.qty_total_requested = sum(ln.qty_requested for ln in lns)
            rec.qty_total_to_issue = sum(ln.qty_to_issue for ln in lns)
            rec.qty_total_to_buy = sum(ln.qty_to_buy for ln in lns)
            rec.qty_total_issued = sum(ln.qty_issued for ln in lns)
            rec.qty_total_reserved = sum(ln.qty_reserved for ln in lns)

    def _compute_issue_picking_count(self):
        for rec in self:
            rec.issue_picking_count = len(rec.issue_picking_ids)

    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.purchase_order_ids)

    # --- Методы согласования ---
    def action_submit_for_approval(self):
        """Отправить документ на согласование."""
        self.ensure_one()
        if not self.approver_user_id:
            raise UserError(
                'Укажите согласующего перед отправкой на согласование.'
            )
        if self.approval_state == 'pending':
            raise UserError('Документ уже отправлен на согласование.')
        self.write({'approval_state': 'pending'})
        self.message_post(
            body=(
                f'Требование отправлено на согласование. '
                f'Согласующий: {self.approver_user_id.name}.'
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=[self.approver_user_id.partner_id.id],
        )

    def action_approve(self):
        """Согласовать документ."""
        self.ensure_one()
        self.write({'approval_state': 'approved'})
        partner_ids = [
            p.id for p in (
                self.foreman_user_id.partner_id
                | self.buyer_user_id.partner_id
            ) if p
        ]
        self.message_post(
            body=(
                f'Требование согласовано ({self.env.user.name}). '
                'Документ можно перевести в работу.'
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=partner_ids,
        )

    def action_reject(self):
        """Отклонить документ."""
        self.ensure_one()
        self.write({'approval_state': 'rejected'})
        partner_ids = [
            p.id for p in (
                self.foreman_user_id.partner_id
                | self.buyer_user_id.partner_id
            ) if p
        ]
        self.message_post(
            body=(
                f'Требование отклонено ({self.env.user.name}). '
                'Исправьте замечания и повторно отправьте на согласование.'
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=partner_ids,
        )

    # --- Методы смены статуса ---
    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError('Нельзя перевести документ в работу без строк.')
        if self.approval_state == 'pending':
            raise UserError(
                'Документ ожидает согласования. '
                'Дождитесь решения согласующего.'
            )
        if self.approval_state == 'rejected':
            raise UserError(
                'Документ отклонён согласующим. '
                'Исправьте замечания и повторно отправьте на согласование.'
            )
        unmatched = self.line_ids.filtered(
            lambda ln: ln.matching_required or not ln.product_id
        )
        if unmatched:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Предупреждение',
                'res_model': 'object.request.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_request_id': self.id,
                    'default_action_type': 'in_progress',
                    'default_message': (
                        f'В документе {len(unmatched)} несопоставленных строк. '
                        'Они потребуют ручного сопоставления снабженцем. '
                        'Перевести документ в работу?'
                    ),
                },
            }
        self.write({'state': 'in_progress'})

    def action_close(self):
        self.ensure_one()
        unprocessed = self.line_ids.filtered(
            lambda ln: ln.line_state not in ('fully_supplied', 'cancelled')
        )
        if unprocessed:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Подтверждение закрытия',
                'res_model': 'object.request.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_request_id': self.id,
                    'default_action_type': 'close',
                    'default_message': (
                        f'{len(unprocessed)} строк не полностью обработаны '
                        '(не в статусе «Полностью обеспечено» или «Отменено»). '
                        'Закрыть документ несмотря на это?'
                    ),
                },
            }
        self.write({'state': 'closed'})

    def action_cancel(self):
        for rec in self:
            for picking in rec.issue_picking_ids.filtered(
                lambda p: p.state in ('confirmed', 'assigned', 'waiting')
            ):
                picking.do_unreserve()
            rec.line_ids.write({'qty_reserved': 0.0, 'issue_reserved': False})
        self.write({'state': 'cancelled'})

    # --- Smart button actions ---
    def action_open_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Строки требования',
            'res_model': 'object.request.line',
            'view_mode': 'list',
            'domain': [('request_id', '=', self.id)],
            'context': {'default_request_id': self.id},
        }

    def action_open_problem_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Проблемные строки',
            'res_model': 'object.request.line',
            'view_mode': 'list',
            'domain': [
                ('request_id', '=', self.id),
                '|',
                ('matching_required', '=', True),
                ('manual_vendor_required', '=', True),
            ],
            'context': {'default_request_id': self.id},
        }

    def action_open_issue_pickings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Выдачи',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.issue_picking_ids.ids)],
        }

    def action_open_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Закупки',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
        }

    def action_rematch_lines(self):
        """Повторно запустить автосопоставление по несопоставленным строкам."""
        self.ensure_one()
        parser = self.env['object.request.excel.parser']
        unmatched = self.line_ids.filtered(
            lambda ln: ln.matching_required or not ln.product_id
        )
        if not unmatched:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Пересопоставление',
                    'message': 'Нет строк, требующих сопоставления.',
                    'type': 'info',
                    'sticky': False,
                },
            }
        newly_matched = 0
        for line in unmatched:
            result = parser.match_row(
                line.supplier_article, line.name_raw, line.supplier_raw
            )
            vals = {
                'matching_required': result['matching_required'],
                'manual_vendor_required': result['manual_vendor_required'],
            }
            if result['product']:
                vals['product_id'] = result['product'].id
                vals['uom_id'] = result['product'].uom_id.id
                if not line.preferred_vendor_id:
                    if result['vendor']:
                        vals['preferred_vendor_id'] = result['vendor'].id
                    elif result['product'].seller_ids:
                        vals['preferred_vendor_id'] = (
                            result['product'].seller_ids[0].partner_id.id
                        )
                newly_matched += 1
            elif result['vendor'] and not line.preferred_vendor_id:
                vals['preferred_vendor_id'] = result['vendor'].id
            line.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Пересопоставление завершено',
                'message': (
                    f'Обработано {len(unmatched)} строк. '
                    f'Сопоставлено новых: {newly_matched}.'
                ),
                'type': 'success' if newly_matched else 'warning',
                'sticky': False,
            },
        }

    def _notify_if_all_lines_supplied(self):
        """Уведомить через chatter, если все активные строки полностью обеспечены."""
        self.ensure_one()
        active_lines = self.line_ids.filtered(lambda ln: not ln.is_cancelled)
        if not active_lines:
            return
        if all(ln.line_state == 'fully_supplied' for ln in active_lines):
            self.message_post(
                body=(
                    'Все строки требования полностью обеспечены. '
                    'Документ можно закрыть.'
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

    def action_check_stock(self):
        """Проверить остатки по складам.

        Если check_warehouse_ids пуст — режим прораба: проверяется склад объекта
        (warehouse_id). При наличии остатков открывается wizard с предупреждением.

        Если check_warehouse_ids заполнен — режим снабженца: проверяется по всем
        указанным складам, результат — toast-уведомление с числом найденных позиций.
        """
        self.ensure_one()
        is_foreman_check = not self.check_warehouse_ids
        warehouses = self.check_warehouse_ids or self.warehouse_id
        locations = warehouses.mapped('lot_stock_id').filtered(bool)
        lines = self.line_ids.filtered(lambda ln: ln.product_id and not ln.is_cancelled)
        if not lines:
            raise UserError('Нет строк с сопоставленным товаром для проверки наличия.')
        now = fields.Datetime.now()
        for line in lines:
            if locations:
                qty = sum(
                    line.product_id.with_context(location=loc.id).qty_available
                    for loc in locations
                )
            else:
                qty = line.product_id.qty_available
            line.write({'stock_qty_on_hand': qty, 'stock_check_date': now})
        lines_with_stock = lines.filtered(lambda ln: ln.stock_qty_on_hand > 0)
        if is_foreman_check and lines_with_stock:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Проверка актуальности требования',
                'res_model': 'object.request.stock.check.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_request_id': self.id},
            }
        found = len(lines_with_stock)
        total = len(lines)
        if found:
            msg = f'Найдено {found} из {total} позиций.'
            ntype = 'success'
        else:
            msg = f'Ни одна из {total} позиций не найдена на выбранных складах.'
            ntype = 'warning'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Расчёт наличия выполнен',
                'message': msg,
                'type': ntype,
                'sticky': False,
            },
        }

    def action_auto_split(self):
        """Авто-разбивка: qty_to_issue = min(stock, requested), qty_to_buy — остаток."""  # noqa: E501
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled
        )
        if not lines:
            raise UserError(
                'Нет строк с сопоставленным товаром для авто-разбивки.'
            )
        not_checked = lines.filtered(lambda ln: not ln.stock_check_date)
        if not_checked:
            raise UserError(
                'Сначала выполните расчёт наличия '
                '(кнопка «Рассчитать наличие»).'
            )
        for line in lines:
            on_hand = line.stock_qty_on_hand
            requested = line.qty_requested
            qty_to_issue = min(max(on_hand, 0.0), requested)
            qty_to_buy = requested - qty_to_issue
            if qty_to_issue > 0 and qty_to_buy > 0:
                mode = 'mixed'
            elif qty_to_issue > 0:
                mode = 'issue'
            elif qty_to_buy > 0:
                mode = 'buy'
            else:
                mode = 'manual'
            line.write({
                'qty_to_issue': qty_to_issue,
                'qty_to_buy': qty_to_buy,
                'procurement_mode': mode,
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Авто-разбивка выполнена',
                'message': f'Обработано строк: {len(lines)}.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_open_issue_wizard(self):
        """Открыть wizard создания выдачи со склада."""
        self.ensure_one()
        lines_to_issue = self.line_ids.filtered(
            lambda ln: ln.qty_to_issue > 0 and ln.product_id
        )
        if not lines_to_issue:
            raise UserError(
                'Нет строк с заполненным количеством к выдаче. '
                'Заполните поле "К выдаче" в строках документа.'
            )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Создать выдачу',
            'res_model': 'object.request.issue.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }

    def action_open_purchase_wizard(self):
        """Открыть wizard создания черновиков закупки."""
        self.ensure_one()
        lines_to_buy = self.line_ids.filtered(
            lambda ln: ln.qty_to_buy > 0 and ln.product_id
        )
        if not lines_to_buy:
            raise UserError(
                'Нет строк с товаром и количеством к закупке. '
                'Заполните поле «К закупке» в строках документа.'
            )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Создать закупки',
            'res_model': 'object.request.purchase.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }

    # --- Constraints ---
    @api.constrains('state', 'line_ids')
    def _check_state_has_lines(self):
        for rec in self:
            if rec.state == 'in_progress' and not rec.line_ids:
                raise ValidationError(
                    'Документ в работе должен содержать хотя бы одну строку.'
                )
