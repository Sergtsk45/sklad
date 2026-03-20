Role: Senior Odoo Architect enforcing OCA standards.
Context: The following is a codebase dump produced by the akaidoo CLI.
Command: /home/serg45/.local/bin/akaidoo addon object_request -c akaidoo.conf --shrink=soft -B 20k -o custom_addons/ai_assistant/static/knowledge/generated/object_request_context.md
Conventions:
1. Files start with `# FILEPATH: [path]`.
2. Some files were filtered out to save tokens; ask for them if you need.
3. `# shrunk` indicates code removed to save tokens; ask for full content if a specific logic flow is unclear.

# FILEPATH: custom_addons/object_request/__manifest__.py
{
    'name': 'Object Request — Требование на комплектацию объекта',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Управление требованиями на комплектацию строительных объектов',
    'description': """
Модуль для управления требованиями на комплектацию объектов строительства.

Основные функции:
- Создание требований на комплектацию по объектам
- Импорт потребностей из Excel
- Ручное сопоставление строк с номенклатурой
- Создание складских документов выдачи
- Формирование черновиков закупок
- Печатные формы требования и расходной накладной
    """,
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
        'purchase',
        'contacts',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/object_request_security.xml',
        'security/ir.model.access.csv',
        'security/object_request_rules.xml',
        'reports/object_request_report.xml',
        'reports/issue_picking_report.xml',
        'wizards/import_excel_wizard_views.xml',
        'wizards/assign_lines_wizard_views.xml',
        'wizards/issue_wizard_views.xml',
        'wizards/confirm_state_wizard_views.xml',
        'wizards/purchase_wizard_views.xml',
        'views/stock_picking_inherit_views.xml',
        'views/purchase_order_inherit_views.xml',
        'views/object_request_project_views.xml',
        'views/object_request_line_views.xml',
        'views/object_request_views.xml',
        'views/object_request_analytics_views.xml',
        'views/object_request_menu.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}


# FILEPATH: custom_addons/object_request/models/excel_parser.py
_UOM_MAP = {
    'шт': 'шт.', 'шт.': 'шт.', 'штука': 'шт.',
    'штук': 'шт.', 'штуки': 'шт.',
    'кг': 'кг.', 'кг.': 'кг.', 'килограмм': 'кг.',
    'килограммов': 'кг.',
    'м': 'м.', 'м.': 'м.', 'метр': 'м.', 'метров': 'м.',
    'л': 'л.', 'л.': 'л.', 'литр': 'л.', 'литров': 'л.',
    'уп': 'уп.', 'уп.': 'уп.', 'упаковка': 'уп.',
    'упаковок': 'уп.',
    'м2': 'м²', 'кв.м': 'м²', 'кв.м.': 'м²', 'кв м': 'м²',
    'м3': 'м³', 'куб.м': 'м³', 'куб.м.': 'м³', 'куб м': 'м³',
}
_SKIP_ARTICLES = {'', 'none', 'н/а', '-', '—', 'нет', 'n/a'}
class ExcelParser(models.AbstractModel):
    _name = 'object.request.excel.parser'
    _description = 'Сервис парсинга и автосопоставления строк Excel'

    @api.model
    def normalize_uom(self, uom_str):
        if not uom_str:
            return ''
        key = re.sub(r'\s+', ' ', str(uom_str).strip().lower())
        return _UOM_MAP.get(key, str(uom_str).strip())

    @api.model
    def normalize_str(self, s):
        if not s:
            return ''
        return re.sub(r'\s+', ' ', str(s).strip())

    @api.model
    def match_product_by_article(self, supplier_article):
        """Поиск product по артикулу поставщика через product.supplierinfo."""
        article = self.normalize_str(supplier_article)
        if not article or article.lower() in _SKIP_ARTICLES:
            return self.env['product.product'].browse()
        info = self.env['product.supplierinfo'].search(
            [('product_code', '=ilike', article)], limit=1,
        )
        if info and info.product_id:
            return info.product_id
        if info and info.product_tmpl_id:
            return info.product_tmpl_id.product_variant_ids[:1]
        return self.env['product.product'].browse()

    @api.model
    def match_product_by_name(self, name_raw):
        """Поиск product по наименованию: exact, затем ilike."""
        name = self.normalize_str(name_raw)
        if not name:
            return self.env['product.product'].browse()
        Product = self.env['product.product']
        product = Product.search(
            [('name', '=', name), ('active', '=', True)], limit=1,
        )
        if not product:
            product = Product.search(
                [('name', 'ilike', name), ('active', '=', True)], limit=1,
            )
        return product

    @api.model
    def match_vendor_by_name(self, supplier_raw):
        """Поиск res.partner по имени поставщика (ilike, supplier_rank > 0)."""
        name = self.normalize_str(supplier_raw)
        if not name:
            return self.env['res.partner'].browse()
        Partner = self.env['res.partner']
        partner = Partner.search(
            [('name', '=ilike', name), ('supplier_rank', '>', 0)], limit=1,
        )
        if not partner:
            partner = Partner.search(
                [('name', 'ilike', name), ('supplier_rank', '>', 0)], limit=1,
            )
        return partner

    @api.model
    def match_row(self, supplier_article, name_raw, supplier_raw):
        """Комбинированное сопоставление строки Excel.

        Returns:
            dict: product, vendor, matching_required, manual_vendor_required
        """
        product = self.match_product_by_article(supplier_article)
        if not product:
            product = self.match_product_by_name(name_raw)
        vendor = self.match_vendor_by_name(supplier_raw)
        return {
            'product': product,
            'vendor': vendor,
            'matching_required': not bool(product),
            'manual_vendor_required': not bool(vendor),
        }


# FILEPATH: custom_addons/object_request/models/object_request.py
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
        """Запросить qty_available со склада для каждой строки с product_id."""
        self.ensure_one()
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1,
        )
        location = warehouse.lot_stock_id if warehouse else False
        lines = self.line_ids.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled
        )
        if not lines:
            raise UserError(
                'Нет строк с сопоставленным товаром для проверки наличия.'
            )
        now = fields.Datetime.now()
        for line in lines:
            product = line.product_id
            qty = (
                product.with_context(location=location.id).qty_available
                if location
                else product.qty_available
            )
            line.write({'stock_qty_on_hand': qty, 'stock_check_date': now})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Расчёт наличия выполнен',
                'message': f'Проверено строк: {len(lines)}.',
                'type': 'success',
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


# FILEPATH: custom_addons/object_request/models/object_request_line.py
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


# FILEPATH: custom_addons/object_request/models/object_request_project.py
class ObjectRequestProject(models.Model):
    _name = 'object.request.project'
    _description = 'Project Object for Supply Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='Наименование', required=True, tracking=True)
    code = fields.Char(string='Код объекта', index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик')
    address = fields.Char(string='Адрес')
    comment = fields.Text(string='Комментарий')
    active = fields.Boolean(default=True)

    request_ids = fields.One2many(
        'object.request', 'project_id', string='Требования',
    )
    request_count = fields.Integer(
        compute='_compute_request_count', string='Количество требований',
    )

    @api.depends('request_ids')
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)

    def action_open_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Требования',
            'res_model': 'object.request',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    @api.constrains('code')
    def _check_unique_code(self):
        for rec in self:
            if not rec.code:
                continue
            duplicate = self.search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if duplicate:
                raise ValidationError(
                    f'Код объекта "{rec.code}" уже используется другим объектом.'
                )


# FILEPATH: custom_addons/object_request/models/purchase_order_ext.py
class PurchaseOrderExt(models.Model):
    _inherit = 'purchase.order'

    is_object_request_purchase = fields.Boolean(
        string='Закупка по требованию', default=False, index=True,
    )
    object_request_project_id = fields.Many2one(
        'object.request.project',
        string='Объект требования', index=True,
    )
    # Reverse side of object.request.purchase_order_ids many2many
    object_request_ids = fields.Many2many(
        'object.request',
        'object_request_purchase_order_rel', 'purchase_id', 'request_id',
        string='Требования на комплектацию',
    )
    object_request_count = fields.Integer(
        compute='_compute_object_request_count', string='Требований',
    )

    def _compute_object_request_count(self):
        for rec in self:
            rec.object_request_count = len(rec.object_request_ids)

    def action_open_object_requests(self):
        self.ensure_one()
        if len(self.object_request_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Требование на комплектацию',
                'res_model': 'object.request',
                'res_id': self.object_request_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Требования на комплектацию',
            'res_model': 'object.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.object_request_ids.ids)],
            'target': 'current',
        }


# FILEPATH: custom_addons/object_request/models/stock_picking_inherit.py
class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    is_object_request_issue = fields.Boolean(
        string='Выдача по требованию', default=False, index=True,
    )
    object_request_project_id = fields.Many2one(
        'object.request.project',
        string='Объект требования', index=True,
    )
    # Reverse side of object.request.issue_picking_ids many2many
    object_request_ids = fields.Many2many(
        'object.request',
        'object_request_stock_picking_rel', 'picking_id', 'request_id',
        string='Требования на комплектацию',
    )
    object_request_count = fields.Integer(
        compute='_compute_object_request_count', string='Требований',
    )

    def _compute_object_request_count(self):
        for rec in self:
            rec.object_request_count = len(rec.object_request_ids)

    def action_open_object_requests(self):
        self.ensure_one()
        if len(self.object_request_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Требование на комплектацию',
                'res_model': 'object.request',
                'res_id': self.object_request_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Требования на комплектацию',
            'res_model': 'object.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.object_request_ids.ids)],
            'target': 'current',
        }

    # --- OBR-012: синхронизация qty_issued после подтверждения выдачи ---

    def _action_done(self):
        """Override: после подтверждения выдачи обновить qty_issued в строках требования."""
        result = super()._action_done()
        request_issues = self.filtered(lambda p: p.is_object_request_issue)
        if request_issues:
            request_issues._sync_qty_issued_to_request_lines()
        return result

    def _sync_qty_issued_to_request_lines(self):
        """Обновить qty_issued в строках объектного требования на основе done-количества."""
        for picking in self:
            request_lines = self.env['object.request.line'].search([
                ('issue_picking_id', '=', picking.id),
            ])
            for line in request_lines:
                if not line.issue_move_id:
                    continue
                qty_done = line.issue_move_id.quantity
                line.write({'qty_issued': qty_done})
            for request in picking.object_request_ids:
                request._notify_if_all_lines_supplied()


# FILEPATH: odoo/addons/account/__manifest__.py
{   'data': [   'security/account_security.xml',
                'security/ir.model.access.csv',
                'data/account_data.xml',
                'data/digest_data.xml',
                'views/account_report.xml',
                'data/mail_template_data.xml',
                'data/onboarding_data.xml',
                'data/account_tour.xml',
                'data/ir_sequence.xml',
                'data/res_country_group.xml',
                'views/account_payment_view.xml',
                'wizard/account_automatic_entry_wizard_views.xml',
                'wizard/account_autopost_bills_wizard.xml',
                'wizard/account_unreconcile_view.xml',
                'wizard/account_move_reversal_view.xml',
                'wizard/account_resequence_views.xml',
                'wizard/account_payment_register_views.xml',
                'views/account_move_views.xml',
                'wizard/setup_wizards_view.xml',
                'views/account_account_views.xml',
                'views/account_group_views.xml',
                'views/account_journal_views.xml',
                'views/account_account_tag_views.xml',
                'views/account_bank_statement_views.xml',
                'views/account_reconcile_model_views.xml',
                'views/account_tax_views.xml',
                'views/account_full_reconcile_views.xml',
                'views/account_payment_term_views.xml',
                'views/account_payment_method.xml',
                'views/res_partner_bank_views.xml',
                'views/report_statement.xml',
                'views/terms_template.xml',
                'wizard/account_validate_move_view.xml',
                'views/res_company_views.xml',
                'views/product_view.xml',
                'views/account_analytic_plan_views.xml',
                'views/account_analytic_account_views.xml',
                'views/account_analytic_distribution_model_views.xml',
                'views/account_analytic_line_views.xml',
                'views/report_invoice.xml',
                'report/account_invoice_report_view.xml',
                'views/account_cash_rounding_view.xml',
                'views/ir_actions_views.xml',
                'views/ir_module_views.xml',
                'views/base_document_layout_views.xml',
                'views/res_config_settings_views.xml',
                'views/partner_view.xml',
                'views/account_journal_dashboard_view.xml',
                'views/account_portal_templates.xml',
                'views/report_payment_receipt_templates.xml',
                'data/service_cron.xml',
                'views/account_incoterms_view.xml',
                'data/account_incoterms_data.xml',
                'views/digest_views.xml',
                'wizard/account_move_send_wizard.xml',
                'wizard/account_move_send_batch_wizard.xml',
                'report/account_hash_integrity_templates.xml',
                'views/res_currency.xml',
                'views/res_country_group_view.xml',
                'views/account_menuitem.xml',
                'wizard/account_secure_entries_wizard.xml',
                'views/mail_message_views.xml',
                'wizard/accrued_orders.xml',
                'views/bill_preview_template.xml',
                'data/account_reports_data.xml',
                'views/uom_uom_views.xml',
                'views/product_views.xml',
                'views/tests_shared_js_python.xml',
                'views/account_lock_exception_views.xml',
                'views/report_templates.xml',
                'wizard/account_merge_wizard_views.xml'],
    'depends': [   'base_setup',
                   'onboarding',
                   'product',
                   'analytic',
                   'portal',
                   'digest'],
    'name': 'Invoicing',
    'post_init_hook': '_account_post_init',
    'summary': 'Invoices & Payments'}

# FILEPATH: odoo/addons/account/models/account_account.py (lines 19-1481)
ACCOUNT_REGEX = re.compile(r'(?:(\S*\d+\S*))?(.*)')
ACCOUNT_CODE_REGEX = re.compile(r'^[A-Za-z0-9.]+$')
ACCOUNT_CODE_NUMBER_REGEX = re.compile(r'(.*?)(\d*)(\D*?)$')
class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']


# FILEPATH: odoo/addons/account/models/account_account.py (lines 1484-1628)
class AccountGroup(models.Model):
    _name = 'account.group'


# FILEPATH: odoo/addons/account/models/account_account_tag.py
class AccountAccountTag(models.Model):
    _name = 'account.account.tag'


# FILEPATH: odoo/addons/account/models/account_analytic_account.py
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


# FILEPATH: odoo/addons/account/models/account_analytic_distribution_model.py
class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.distribution.model'


# FILEPATH: odoo/addons/account/models/account_analytic_line.py
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


# FILEPATH: odoo/addons/account/models/account_analytic_plan.py
class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'


# FILEPATH: odoo/addons/account/models/account_bank_statement.py
class AccountBankStatement(models.Model):
    _name = 'account.bank.statement'


# FILEPATH: odoo/addons/account/models/account_bank_statement_line.py (lines 11-832)
class AccountBankStatementLine(models.Model):
    _name = 'account.bank.statement.line'
    _inherits = {'account.move': 'move_id'}


# FILEPATH: odoo/addons/account/models/account_bank_statement_line.py (lines 839-842)
class AccountMove(models.Model):
    _inherit = 'account.move'
    # Shrunk non computed fields: statement_line_ids


# FILEPATH: odoo/addons/account/models/account_cash_rounding.py
class AccountCashRounding(models.Model):
    _name = 'account.cash.rounding'


# FILEPATH: odoo/addons/account/models/account_code_mapping.py
COMPANY_OFFSET = 10000
class AccountCodeMapping(models.Model):
    # This model is used purely for UI, to display the account codes for each company.
    # It is not stored in DB. Instead, records are only populated in cache by the
    # `_search` override when accessing the One2many on `account.account`.
    _name = 'account.code.mapping'


# FILEPATH: odoo/addons/account/models/account_document_import_mixin.py
_logger = logging.getLogger(__name__)
class AccountDocumentImportMixin(models.AbstractModel):
    _name = 'account.document.import.mixin'
    _description = "Business document import mixin"


# FILEPATH: odoo/addons/account/models/account_full_reconcile.py
class AccountFullReconcile(models.Model):
    _name = 'account.full.reconcile'


# FILEPATH: odoo/addons/account/models/account_incoterms.py
class AccountIncoterms(models.Model):
    _name = 'account.incoterms'
    _description = 'Incoterms'
    # Shrunk non computed fields: name, code, active


# FILEPATH: odoo/addons/account/models/account_journal.py (lines 16-39)
_logger = logging.getLogger(__name__)
class AccountJournalGroup(models.Model):
    _name = 'account.journal.group'


# FILEPATH: odoo/addons/account/models/account_journal.py (lines 42-1300)
class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['portal.mixin',
                'mail.alias.mixin.optional',
                'mail.thread',
                'mail.activity.mixin',
               ]


# FILEPATH: odoo/addons/account/models/account_journal_dashboard.py
class AccountJournal(models.Model):
    _inherit = "account.journal"


# FILEPATH: odoo/addons/account/models/account_lock_exception.py
class AccountLock_Exception(models.Model):
    _name = 'account.lock_exception'


# FILEPATH: odoo/addons/account/models/account_move.py
_logger = logging.getLogger(__name__)
MAX_HASH_VERSION = 4
PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('blocked', 'Blocked'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
]
TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'out_invoice',
    'in_invoice': 'in_refund',
    'in_refund': 'in_invoice',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}
EMPTY = object()
BYPASS_LOCK_CHECK = object()
class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin', 'sequence.mixin', 'product.catalog.mixin', 'account.document.import.mixin']
    _description = "Journal Entry"
    _order = 'date desc, name desc, invoice_date desc, id desc'
    _mail_post_access = 'read'
    _check_company_auto = True
    _sequence_index = "journal_id"
    _rec_names_search = ['name', 'partner_id.name', 'ref']
    _mailing_enabled = True
    line_ids = fields.One2many('account.move.line', 'move_id')
    journal_line_ids = fields.One2many(comodel_name='account.move.line', inverse_name='move_id')
    adjusting_entry_origin_move_ids = fields.Many2many(comodel_name='account.move', relation='adjusting_entries__account_move', column1='move_id', column2='adjusting_entry_move_id')
    adjusting_entries_move_ids = fields.Many2many(comodel_name='account.move', relation='adjusting_entries__account_move', column1='adjusting_entry_move_id', column2='move_id')
    tax_cash_basis_origin_move_id = fields.Many2one(comodel_name='account.move')
    tax_cash_basis_created_move_ids = fields.One2many(comodel_name='account.move', inverse_name='tax_cash_basis_origin_move_id')
    auto_post_origin_id = fields.Many2one(comodel_name='account.move')
    invoice_line_ids = fields.One2many('account.move.line', 'move_id')
    invoice_payment_term_id = fields.Many2one(comodel_name='account.payment.term', compute='_compute_invoice_payment_term_id', store=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', compute='_compute_fiscal_position_id', store=True)
    reversed_entry_id = fields.Many2one(comodel_name='account.move')
    reversal_move_ids = fields.One2many('account.move', 'reversed_entry_id')
    invoice_vendor_bill_id = fields.Many2one('account.move', store=False)
    invoice_user_id = fields.Many2one(comodel_name='res.users', compute='_compute_invoice_default_sale_person', store=True)
    invoice_incoterm_id = fields.Many2one(comodel_name='account.incoterms', compute='_compute_incoterm', store=True)
    tax_country_id = fields.Many2one(comodel_name='res.country', compute='_compute_tax_country_id')
    duplicated_ref_ids = fields.Many2many(comodel_name='account.move', compute='_compute_duplicated_ref_ids')
    _checked_idx = models.Index("(journal_id) WHERE (checked IS NOT TRUE)")
    _payment_idx = models.Index("(journal_id, state, payment_state, move_type, date)")
    _unique_name = models.UniqueIndex(
        "(name, journal_id) WHERE (state = 'posted'AND name != '/')",
        "Another entry with the same name already exists.")
    _journal_id_company_id_idx = models.Index('(journal_id, company_id, date)')
    _made_gaps = models.Index('(journal_id, state, payment_state, move_type, date) WHERE (made_sequence_gap IS TRUE)')
    _duplicate_bills_idx = models.Index("(ref) WHERE (move_type IN ('in_invoice', 'in_refund'))")
    # Shrunk non computed fields: ref, state, move_type, journal_group_id, line_ids, journal_line_ids, exchange_diff_partial_ids, origin_payment_id, matched_payment_ids, statement_line_id, statement_id, adjusting_entry_origin_move_ids, adjusting_entries_move_ids, tax_cash_basis_rec_id, tax_cash_basis_origin_move_id, tax_cash_basis_created_move_ids, auto_post, auto_post_origin_id, posted_before, show_name_warning, country_code, account_fiscal_country_group_codes, company_price_include, attachment_ids, audit_trail_message_ids, restrict_mode_hash_table, secure_sequence_number, inalterable_hash, invoice_line_ids, invoice_date, tax_calculation_rounding_method, partner_id, qr_code_method, company_currency_id, reversed_entry_id, reversal_move_ids, invoice_vendor_bill_id, invoice_source_email, is_manually_modified, quick_edit_total_amount, is_move_sent, user_id, invoice_origin, invoice_cash_rounding_id, sending_data, invoice_pdf_report_id, invoice_pdf_report_file, show_update_fpos
    # Shrunk computed_fields: name (_compute_name), name_placeholder (_compute_name_placeholder), date (_compute_date), is_storno (_compute_is_storno), journal_id (_compute_journal_id), company_id (_compute_company_id), reconciled_payment_ids (_compute_reconciled_payment_ids), payment_count (_compute_payment_count), adjusting_entry_origin_label (_compute_adjusting_entry_origin_label), adjusting_entry_origin_moves_count (_compute_adjusting_entry_origin_moves_count), adjusting_entries_count (_compute_adjusting_entries_count), always_tax_exigible (_compute_always_tax_exigible), auto_post_until (_compute_auto_post_until), hide_post_button (_compute_hide_post_button), checked (_compute_checked), suitable_journal_ids (_compute_suitable_journal_ids), highest_name (_compute_highest_name), made_sequence_gap (_compute_made_sequence_gap), type_name (_compute_type_name), no_followup (_compute_no_followup), secured (_compute_secured), invoice_date_due (_compute_invoice_date_due), delivery_date (_compute_delivery_date), show_delivery_date (_compute_show_delivery_date), taxable_supply_date (_compute_taxable_supply_date), show_taxable_supply_date (_compute_show_taxable_supply_date), taxable_supply_date_placeholder (_compute_taxable_supply_date_placeholder), invoice_payment_term_id (_compute_invoice_payment_term_id), needed_terms (_compute_needed_terms), needed_terms_dirty (_compute_needed_terms), show_journal (_compute_show_journal), commercial_partner_id (_compute_commercial_partner_id), partner_shipping_id (_compute_partner_shipping_id), partner_bank_id (_compute_partner_bank_id), fiscal_position_id (_compute_fiscal_position_id), payment_reference (_compute_payment_reference), display_qr_code (_compute_display_qr_code), display_link_qr_code (_compute_display_link_qr_code), invoice_outstanding_credits_debits_widget (_compute_payments_widget_to_reconcile_info), invoice_has_outstanding (_compute_invoice_has_outstanding), invoice_payments_widget (_compute_payments_widget_reconciled_info), preferred_payment_method_line_id (_compute_preferred_payment_method_line_id), currency_id (_compute_currency_id), expected_currency_rate (_compute_expected_currency_rate), invoice_currency_rate (_compute_invoice_currency_rate), direction_sign (_compute_direction_sign), amount_untaxed (_compute_amount), amount_tax (_compute_amount), amount_total (_compute_amount), amount_residual (_compute_amount), amount_untaxed_signed (_compute_amount), amount_untaxed_in_currency_signed (_compute_amount), amount_tax_signed (_compute_amount), amount_total_signed (_compute_amount), amount_total_in_currency_signed (_compute_amount), amount_residual_signed (_compute_amount), tax_totals (_compute_tax_totals), payment_state (_compute_payment_state), status_in_payment (_compute_status_in_payment), amount_total_words (_compute_amount_total_words), invoice_partner_display_name (_compute_invoice_partner_display_info), quick_edit_mode (_compute_quick_edit_mode), quick_encoding_vals (_compute_quick_encoding_vals), narration (_compute_narration), is_being_sent (_compute_is_being_sent), move_sent_values (compute_move_sent_values), invoice_user_id (_compute_invoice_default_sale_person), invoice_incoterm_id (_compute_incoterm), incoterm_location (_compute_incoterm_location), invoice_incoterm_placeholder (_compute_invoice_incoterm_placeholder), invoice_filter_type_domain (_compute_invoice_filter_type_domain), bank_partner_id (_compute_bank_partner_id), tax_lock_date_message (_compute_tax_lock_date_message), display_inactive_currency_warning (_compute_display_inactive_currency_warning), tax_country_id (_compute_tax_country_id), tax_country_code (_compute_tax_country_code), has_reconciled_entries (_compute_has_reconciled_entries), show_reset_to_draft_button (_compute_show_reset_to_draft_button), partner_credit_warning (_compute_partner_credit_warning), duplicated_ref_ids (_compute_duplicated_ref_ids), is_draft_duplicated_ref_ids (_compute_is_draft_duplicated_ref_ids), need_cancel_request (_compute_need_cancel_request), payment_term_details (_compute_payment_term_details), show_payment_term_details (_compute_show_payment_term_details), show_discount_details (_compute_show_payment_term_details), abnormal_amount_warning (_compute_abnormal_warnings), abnormal_date_warning (_compute_abnormal_warnings), alerts (_compute_alerts), taxes_legal_notes (_compute_taxes_legal_notes), next_payment_date (_compute_next_payment_date), display_send_button (_compute_display_send_button), highlight_send_button (_compute_highlight_send_button), is_sale_installed (_compute_is_sale_installed)


# FILEPATH: odoo/addons/account/models/account_move_line.py
_logger = logging.getLogger(__name__)
class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ["analytic.mixin"]
    _description = "Journal Item"
    _order = "date desc, move_name desc, id"
    _check_company_auto = True
    _rec_names_search = ['name', 'move_id', 'product_id']
    move_id = fields.Many2one(comodel_name='account.move')
    tax_ids = fields.Many2many(comodel_name='account.tax', compute='_compute_tax_ids', store=True)
    group_tax_id = fields.Many2one(comodel_name='account.tax')
    tax_line_id = fields.Many2one(comodel_name='account.tax', related='tax_repartition_line_id.tax_id', store=True)
    reconciled_lines_ids = fields.Many2many(comodel_name='account.move.line', compute='_compute_reconciled_lines_ids')
    reconciled_lines_excluding_exchange_diff_ids = fields.Many2many(comodel_name='account.move.line', compute='_compute_reconciled_lines_excluding_exchange_diff_ids')
    parent_id = fields.Many2one('account.move.line', compute='_compute_parent_id')
    product_id = fields.Many2one(comodel_name='product.product')
    _check_credit_debit = models.Constraint(
        "CHECK(display_type IN ('line_section', 'line_subsection', 'line_note') OR credit * debit=0)",
        'Wrong credit or debit value in accounting entry!')
    _check_amount_currency_balance_sign = models.Constraint(
        "CHECK(\n                display_type IN ('line_section', 'line_subsection', 'line_note')\n                OR (\n                    (balance <= 0 AND amount_currency <= 0)\n                    OR\n                    (balance >= 0 AND amount_currency >= 0)\n                )\n            )",
        'The amount expressed in the secondary currency must be positive when account is debited and negative when account is credited. If the currency is the same as the one from the company, this amount must strictly be equal to the balance.')
    _check_accountable_required_fields = models.Constraint(
        "CHECK(display_type IN ('line_section', 'line_subsection', 'line_note') OR account_id IS NOT NULL)",
        'Missing required account on accountable line.')
    _check_non_accountable_fields_null = models.Constraint(
        "CHECK(display_type NOT IN ('line_section', 'line_subsection', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
        'Forbidden balance or account on non-accountable line')
    _partner_id_ref_idx = models.Index("(partner_id, ref)")
    _date_name_id_idx = models.Index("(date desc, move_name desc, id)")
    _unreconciled_index = models.Index("(account_id, partner_id) WHERE reconciled IS NOT TRUE")
    _journal_id_neg_amnt_residual_idx = models.Index("(journal_id) WHERE amount_residual < 0")
    _account_id_date_idx = models.Index("(account_id, date)")
    # Shrunk non computed fields: move_id, journal_id, journal_group_id, company_id, company_currency_id, move_name, parent_state, date, invoice_date, ref, move_type, account_name, account_code, search_account_id, is_imported, reconcile_model_id, payment_id, statement_line_id, statement_id, commercial_partner_country, group_tax_id, tax_line_id, tax_group_id, tax_base_amount, tax_repartition_line_id, tax_tag_ids, extra_tax_data, full_reconcile_id, matched_debit_ids, matched_credit_ids, matching_number, is_account_reconcile, account_type, account_internal_group, account_root_id, product_category_id, collapse_composition, collapse_prices, product_id, date_maturity, discount, tax_calculation_rounding_method, deductible_amount, analytic_line_ids, analytic_distribution, discount_date, discount_amount_currency, discount_balance
    # Shrunk computed_fields: is_storno (_compute_is_storno), sequence (_compute_sequence), account_id (_compute_account_id), name (_compute_name), translated_product_name (_compute_translated_product_name), debit (_compute_debit_credit), credit (_compute_debit_credit), balance (_compute_balance), cumulated_balance (_compute_cumulated_balance), currency_rate (_compute_currency_rate), amount_currency (_compute_amount_currency), currency_id (_compute_currency_id), is_same_currency (_compute_same_currency), partner_id (_compute_partner_id), tax_ids (_compute_tax_ids), amount_residual (_compute_amount_residual), amount_residual_currency (_compute_amount_residual), reconciled (_compute_amount_residual), reconciled_lines_ids (_compute_reconciled_lines_ids), reconciled_lines_excluding_exchange_diff_ids (_compute_reconciled_lines_excluding_exchange_diff_ids), display_type (_compute_display_type), parent_id (_compute_parent_id), allowed_uom_ids (_compute_allowed_uom_ids), product_uom_id (_compute_product_uom_id), quantity (_compute_quantity), price_unit (_compute_price_unit), price_subtotal (_compute_totals), price_total (_compute_totals), term_key (_compute_term_key), epd_key (_compute_epd_key), epd_needed (_compute_epd_needed), epd_dirty (_compute_epd_needed), discount_allocation_key (_compute_discount_allocation_key), discount_allocation_needed (_compute_discount_allocation_needed), discount_allocation_dirty (_compute_discount_allocation_needed), has_invalid_analytics (_compute_has_invalid_analytics), payment_date (_compute_payment_date), is_refund (_compute_is_refund), no_followup (_compute_no_followup)


# FILEPATH: odoo/addons/account/models/account_move_line_tax_details.py
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


# FILEPATH: odoo/addons/account/models/account_move_send.py
_logger = logging.getLogger(__name__)
class AccountMoveSend(models.AbstractModel):
    _name = 'account.move.send'


# FILEPATH: odoo/addons/account/models/account_partial_reconcile.py
class AccountPartialReconcile(models.Model):
    _name = 'account.partial.reconcile'


# FILEPATH: odoo/addons/account/models/account_payment.py (lines 7-1235)
class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']


# FILEPATH: odoo/addons/account/models/account_payment.py (lines 1242-1245)
class AccountMove(models.Model):
    _inherit = 'account.move'
    # Shrunk non computed fields: payment_ids


# FILEPATH: odoo/addons/account/models/account_payment_method.py (lines 7-92)
class AccountPaymentMethod(models.Model):
    _name = 'account.payment.method'


# FILEPATH: odoo/addons/account/models/account_payment_method.py (lines 95-173)
class AccountPaymentMethodLine(models.Model):
    _name = 'account.payment.method.line'


# FILEPATH: odoo/addons/account/models/account_payment_term.py (lines 11-278)
class AccountPaymentTerm(models.Model):
    _name = 'account.payment.term'
    _description = "Payment Terms"
    _order = "sequence, id"
    _check_company_domain = models.check_company_domain_parent_of
    # Shrunk non computed fields: name, active, note, line_ids, company_id, sequence, display_on_invoice, example_amount, example_date, discount_percentage, discount_days, early_discount
    # Shrunk computed_fields: fiscal_country_codes (_compute_fiscal_country_codes), currency_id (_compute_currency_id), example_invalid (_compute_example_invalid), example_preview (_compute_example_preview), example_preview_discount (_compute_example_preview), early_pay_discount_computation (_compute_discount_computation)


# FILEPATH: odoo/addons/account/models/account_payment_term.py (lines 281-367)
class AccountPaymentTermLine(models.Model):
    _name = 'account.payment.term.line'


# FILEPATH: odoo/addons/account/models/account_reconcile_model.py (lines 8-88)
class AccountReconcileModelLine(models.Model):
    _name = 'account.reconcile.model.line'
    _inherit = ['analytic.mixin']


# FILEPATH: odoo/addons/account/models/account_reconcile_model.py (lines 91-200)
class AccountReconcileModel(models.Model):
    _name = 'account.reconcile.model'
    _inherit = ['mail.thread']


# FILEPATH: odoo/addons/account/models/account_report.py (lines 44-346)
FIGURE_TYPE_SELECTION_VALUES = [
    ('monetary', "Monetary"),
    ('percentage', "Percentage"),
    ('integer', "Integer"),
    ('float', "Float"),
    ('date', "Date"),
    ('datetime', "Datetime"),
    ('boolean', 'Boolean'),
    ('string', 'String'),
]
DOMAIN_REGEX = re.compile(r'(-?sum)\((.*)\)')
CROSS_REPORT_REGEX = re.compile(r'^cross_report\((.+)\)$')
ACCOUNT_CODES_ENGINE_SPLIT_REGEX = re.compile(r"(?=[+-])")
ACCOUNT_CODES_ENGINE_TERM_REGEX = re.compile(
    r"^(?P<sign>[+-]?)"
    r"(?P<prefix>([A-Za-z\d.]*|tag\([\w.]+\))((?=\\)|(?<=[^CD])))"
    r"(\\\((?P<excluded_prefixes>([A-Za-z\d.]+)*[A-Za-z\d.]*)\))?"
    r"(?P<balance_character>[DC]?)$"
)
number_regex = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
report_line_code_regex = r"[+-]?[\s(]*[^().\s*/+\-]+\.[^().\s*/+\-]+"
operator_regex = r"[\s*/+\-]"
hard_formulas = ['sum_children']
AGGREGATION_ENGINE_FORMULA_REGEX = re.compile(
    f'{"|".join(hard_formulas)}|'
    rf"[\s(]*(?:{number_regex}|{report_line_code_regex})[\s)]*"
    rf"(?:{operator_regex}[\s(]*(?:{number_regex}|{report_line_code_regex})[\s)]*)*"
)
class AccountReport(models.Model):
    _name = 'account.report'


# FILEPATH: odoo/addons/account/models/account_report.py (lines 349-576)
class AccountReportLine(models.Model):
    _name = 'account.report.line'


# FILEPATH: odoo/addons/account/models/account_report.py (lines 579-929)
class AccountReportExpression(models.Model):
    _name = 'account.report.expression'


# FILEPATH: odoo/addons/account/models/account_report.py (lines 932-944)
class AccountReportColumn(models.Model):
    _name = 'account.report.column'


# FILEPATH: odoo/addons/account/models/account_report.py (lines 947-967)
class AccountReportExternalValue(models.Model):
    _name = 'account.report.external.value'


# FILEPATH: odoo/addons/account/models/account_root.py
class AccountRoot(models.Model):
    _name = 'account.root'


# FILEPATH: odoo/addons/account/models/account_tax.py (lines 25-68)
TYPE_TAX_USE = [
    ('sale', 'Sales'),
    ('purchase', 'Purchases'),
    ('none', 'None'),
]
class AccountTaxGroup(models.Model):
    _name = 'account.tax.group'


# FILEPATH: odoo/addons/account/models/account_tax.py (lines 71-5001)
class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = ['mail.thread']
    _description = 'Tax'
    _order = 'sequence,id'
    _check_company_auto = True
    _rec_names_search = ['name', 'description', 'invoice_label']
    _check_company_domain = models.check_company_domain_parent_of
    fiscal_position_ids = fields.Many2many(comodel_name='account.fiscal.position', relation='account_fiscal_position_account_tax_rel', column1='account_tax_id', column2='account_fiscal_position_id')
    original_tax_ids = fields.Many2many(comodel_name='account.tax', relation='account_tax_alternatives', column1='dest_tax_id', column2='src_tax_id')
    replacing_tax_ids = fields.Many2many(comodel_name='account.tax', relation='account_tax_alternatives', column1='src_tax_id', column2='dest_tax_id')
    children_tax_ids = fields.Many2many('account.tax', 'account_tax_filiation_rel', 'parent_tax', 'child_tax')
    country_id = fields.Many2one(comodel_name='res.country', compute='_compute_country_id', store=True)
    # Shrunk non computed fields: name, type_tax_use, tax_scope, amount_type, fiscal_position_ids, original_tax_ids, replacing_tax_ids, active, company_id, children_tax_ids, sequence, amount, description, invoice_label, company_price_include, price_include_override, include_base_amount, is_base_affected, analytic, hide_tax_exigibility, tax_exigibility, cash_basis_transition_account_id, repartition_line_ids, country_code, invoice_legal_notes
    # Shrunk computed_fields: display_alternative_taxes_field (_compute_display_alternative_taxes_field), is_domestic (_compute_is_domestic), tax_label (_compute_tax_label), price_include (_compute_price_include), tax_group_id (_compute_tax_group_id), invoice_repartition_line_ids (_compute_invoice_repartition_line_ids), refund_repartition_line_ids (_compute_refund_repartition_line_ids), country_id (_compute_country_id), is_used (_compute_is_used), repartition_lines_str (_compute_repartition_lines_str), has_negative_factor (_compute_has_negative_factor)


# FILEPATH: odoo/addons/account/models/account_tax.py (lines 5004-5072)
class AccountTaxRepartitionLine(models.Model):
    _name = 'account.tax.repartition.line'


# FILEPATH: odoo/addons/account/models/chart_template.py
_logger = logging.getLogger(__name__)
TEMPLATE_MODELS = (
    'account.group',
    'account.account',
    'account.fiscal.position',
    'account.tax.group',
    'account.tax',
    'account.journal',
    'account.reconcile.model')
TAX_TAG_DELIMITER = '||'
SYSCOHADA_LIST = ['BJ', 'BF', 'CM', 'CF', 'KM', 'CG', 'CI', 'GA', 'GN', 'GW', 'GQ', 'ML', 'NE',
                  'CD', 'SN', 'TD', 'TG']
class AccountChartTemplate(models.AbstractModel):
    _name = 'account.chart.template'


# FILEPATH: odoo/addons/account/models/company.py
MONTH_SELECTION = [
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]
PEPPOL_DEFAULT_COUNTRIES = [
    'AT', 'BE', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
    'FR', 'GR', 'IE', 'IS', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL',
    'NO', 'PL', 'PT', 'RO', 'SE', 'SI',
]
PEPPOL_MAILING_COUNTRIES = [
    'BE', 'LU', 'NL', 'SE', 'NO',
]
PEPPOL_LIST = PEPPOL_DEFAULT_COUNTRIES + [
    'AD', 'AL', 'BA', 'BG', 'BL', 'GB', 'GF', 'GP', 'HR', 'HU', 'LI', 'MC', 'ME', 'MF',
    'MK', 'MQ', 'NC', 'PF', 'PM', 'RE', 'RS', 'SK', 'SM', 'TF', 'TR', 'VA', 'WF', 'YT',
]
STORNO_MANDATORY_COUNTRIES = {'BA', 'CN', 'CZ', 'HR', 'PL', 'RO', 'RS', 'RU', 'SI', 'SK', 'UA'}
STORNO_OPTIONAL_COUNTRIES = {'AT', 'CH', 'DE', 'IT'}
INTEGRITY_HASH_BATCH_SIZE = 1000
SOFT_LOCK_DATE_FIELDS = [
    'fiscalyear_lock_date',
    'tax_lock_date',
    'sale_lock_date',
    'purchase_lock_date',
]
LOCK_DATE_FIELDS = [
    *SOFT_LOCK_DATE_FIELDS,
    'hard_lock_date',
]
class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = ["res.company", "mail.thread"]


# FILEPATH: odoo/addons/account/models/decimal_precision.py
class DecimalPrecision(models.Model):
    _inherit = 'decimal.precision'


# FILEPATH: odoo/addons/account/models/digest.py
class DigestDigest(models.Model):
    _inherit = 'digest.digest'


# FILEPATH: odoo/addons/account/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'


# FILEPATH: odoo/addons/account/models/ir_attachment.py
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


# FILEPATH: odoo/addons/account/models/ir_http.py
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'


# FILEPATH: odoo/addons/account/models/ir_module.py
template_module = lambda m: ismodule(m) and m.__name__.split('.')[-1].startswith('template_')
template_class = isclass
template_function = lambda f: isfunction(f) and hasattr(f, '_l10n_template') and f._l10n_template[1] == 'template_data'
class IrModuleModule(models.Model):
    _inherit = "ir.module.module"


# FILEPATH: odoo/addons/account/models/kpi_provider.py
class KpiProvider(models.AbstractModel):
    _inherit = 'kpi.provider'


# FILEPATH: odoo/addons/account/models/mail_message.py
bypass_token = object()
DOMAINS = {
    'res.company':
        lambda rec, operator, value: _subselect_domain(rec.env['account.move.line'], 'company_id',
            Domain('company_id.restrictive_audit_trail', operator, value)
        ),
    'account.move':
        lambda rec, operator, value: [('company_id.restrictive_audit_trail', operator, value)],
    'account.account':
        lambda rec, operator, value: [('used', operator, value), ('company_ids.restrictive_audit_trail', operator, value)],
    'account.tax':
        lambda rec, operator, value: _subselect_domain(rec.env['account.move.line'], 'tax_line_id',
            Domain('company_id.restrictive_audit_trail', operator, value)),
    'res.partner':
        lambda rec, operator, value: _subselect_domain(rec.env['account.move.line'], 'partner_id',
            Domain('company_id.restrictive_audit_trail', operator, value)),
    }
class MailMessage(models.Model):
    _inherit = 'mail.message'


# FILEPATH: odoo/addons/account/models/mail_template.py
class MailTemplate(models.Model):
    _inherit = 'mail.template'


# FILEPATH: odoo/addons/account/models/mail_tracking_value.py
class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'


# FILEPATH: odoo/addons/account/models/merge_partner_automatic.py
class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'


# FILEPATH: odoo/addons/account/models/onboarding_onboarding.py
class OnboardingOnboarding(models.Model):
    _inherit = 'onboarding.onboarding'


# FILEPATH: odoo/addons/account/models/onboarding_onboarding_step.py
class OnboardingOnboardingStep(models.Model):
    _inherit = 'onboarding.onboarding.step'


# FILEPATH: odoo/addons/account/models/partner.py (lines 26-300)
_logger = logging.getLogger(__name__)
_ref_company_registry = {
    'jp': '7000012050002',
    'dk': '58403288',
    'fi': '8763054-9',
}
class AccountFiscalPosition(models.Model):
    _name = 'account.fiscal.position'
    _description = 'Fiscal Position'
    _order = 'sequence'
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of
    tax_ids = fields.Many2many(comodel_name='account.tax', relation='account_fiscal_position_account_tax_rel', column1='account_fiscal_position_id', column2='account_tax_id')
    country_id = fields.Many2one('res.country')
    # Shrunk non computed fields: sequence, name, active, company_id, account_ids, tax_ids, note, auto_apply, vat_required, company_country_id, fiscal_country_codes, country_id, country_group_id, state_ids, zip_from, zip_to, foreign_vat
    # Shrunk computed_fields: account_map (_compute_account_map), tax_map (_compute_tax_map), is_domestic (_compute_is_domestic), states_count (_compute_states_count), foreign_vat_header_mode (_compute_foreign_vat_header_mode)


# FILEPATH: odoo/addons/account/models/partner.py (lines 303-323)
class AccountFiscalPositionAccount(models.Model):
    _name = 'account.fiscal.position.account'


# FILEPATH: odoo/addons/account/models/partner.py (lines 326-1077)
class ResPartner(models.Model):
    _inherit = 'res.partner'


# FILEPATH: odoo/addons/account/models/product.py (lines 11-27)
ACCOUNT_DOMAIN = "[('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card','off_balance'))]"
class ProductCategory(models.Model):
    _inherit = "product.category"


# FILEPATH: odoo/addons/account/models/product.py (lines 34-209)
class ProductTemplate(models.Model):
    _inherit = "product.template"
    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id')
    supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id')
    # Shrunk non computed fields: taxes_id, supplier_taxes_id, property_account_income_id, property_account_expense_id, account_tag_ids
    # Shrunk computed_fields: tax_string (_compute_tax_string), fiscal_country_codes (_compute_fiscal_country_codes)


# FILEPATH: odoo/addons/account/models/product.py (lines 212-346)
class ProductProduct(models.Model):
    _inherit = "product.product"
    # Shrunk computed_fields: tax_string (_compute_tax_string)


# FILEPATH: odoo/addons/account/models/product_catalog_mixin.py
class ProductCatalogMixin(models.AbstractModel):
    _inherit = 'product.catalog.mixin'


# FILEPATH: odoo/addons/account/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


# FILEPATH: odoo/addons/account/models/res_country_group.py
class ResCountryGroup(models.Model):
    _inherit = 'res.country.group'


# FILEPATH: odoo/addons/account/models/res_currency.py
class ResCurrency(models.Model):
    _inherit = 'res.currency'


# FILEPATH: odoo/addons/account/models/res_partner_bank.py
class ResPartnerBank(models.Model):
    _name = 'res.partner.bank'
    _inherit = ['res.partner.bank', 'mail.thread', 'mail.activity.mixin']


# FILEPATH: odoo/addons/account/models/res_users.py
class ResGroups(models.Model):
    _inherit = 'res.groups'


# FILEPATH: odoo/addons/account/models/sequence_mixin.py
_logger = logging.getLogger(__name__)
class SequenceMixin(models.AbstractModel):
    _name = 'sequence.mixin'


# FILEPATH: odoo/addons/account/models/template_generic_coa.py
class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"


# FILEPATH: odoo/addons/account/models/uom_uom.py
UOM_TO_UNECE_CODE = {
    'uom.product_uom_unit': 'C62',
    'uom.product_uom_dozen': 'DZN',
    'uom.product_uom_kgm': 'KGM',
    'uom.product_uom_gram': 'GRM',
    'uom.product_uom_day': 'DAY',
    'uom.product_uom_hour': 'HUR',
    'uom.product_uom_minute': 'MIN',
    'uom.product_uom_ton': 'TNE',
    'uom.product_uom_meter': 'MTR',
    'uom.product_uom_km': 'KMT',
    'uom.product_uom_cm': 'CMT',
    'uom.product_uom_litre': 'LTR',
    'uom.product_uom_lb': 'LBR',
    'uom.product_uom_oz': 'ONZ',
    'uom.product_uom_inch': 'INH',
    'uom.product_uom_foot': 'FOT',
    'uom.product_uom_mile': 'SMI',
    'uom.product_uom_floz': 'OZA',
    'uom.product_uom_qt': 'QTL',
    'uom.product_uom_gal': 'GLL',
    'uom.product_uom_cubic_meter': 'MTQ',
    'uom.product_uom_cubic_inch': 'INQ',
    'uom.product_uom_cubic_foot': 'FTQ',
    'uom.uom_square_meter': 'MTK',
    'uom.uom_square_foot': 'FTK',
    'uom.product_uom_yard': 'YRD',
    'uom.product_uom_millimeter': 'MMT',
    'uom.product_uom_kwh': 'KWH',
}
class UomUom(models.Model):
    _inherit = "uom.uom"


# FILEPATH: odoo/addons/analytic/__manifest__.py
{   'data': [   'security/analytic_security.xml',
                'security/ir.model.access.csv',
                'views/analytic_line_views.xml',
                'views/analytic_account_views.xml',
                'views/analytic_plan_views.xml',
                'views/analytic_distribution_model_views.xml',
                'data/analytic_data.xml'],
    'depends': ['base', 'mail', 'uom'],
    'name': 'Analytic Accounting'}

# FILEPATH: odoo/addons/analytic/models/analytic_account.py
class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = ['mail.thread']


# FILEPATH: odoo/addons/analytic/models/analytic_distribution_model.py
class AccountAnalyticDistributionModel(models.Model):
    _name = 'account.analytic.distribution.model'
    _inherit = ['analytic.mixin']


# FILEPATH: odoo/addons/analytic/models/analytic_line.py (lines 11-151)
class AnalyticPlanFieldsMixin(models.AbstractModel):
    _name = 'analytic.plan.fields.mixin'


# FILEPATH: odoo/addons/analytic/models/analytic_line.py (lines 154-265)
class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['analytic.plan.fields.mixin']


# FILEPATH: odoo/addons/analytic/models/analytic_mixin.py
class AnalyticMixin(models.AbstractModel):
    _name = 'analytic.mixin'
    _description = 'Analytic Mixin'
    # Shrunk non computed fields: analytic_precision
    # Shrunk computed_fields: analytic_distribution (_compute_analytic_distribution), distribution_analytic_account_ids (_compute_distribution_analytic_account_ids)


# FILEPATH: odoo/addons/analytic/models/analytic_plan.py (lines 14-390)
class AccountAnalyticPlan(models.Model):
    _name = 'account.analytic.plan'


# FILEPATH: odoo/addons/analytic/models/analytic_plan.py (lines 393-430)
class AccountAnalyticApplicability(models.Model):
    _name = 'account.analytic.applicability'


# FILEPATH: odoo/addons/analytic/models/ir_config_parameter.py
class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'


# FILEPATH: odoo/addons/analytic/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


# FILEPATH: odoo/addons/barcodes/__manifest__.py
{   'data': [   'data/barcodes_data.xml',
                'views/barcodes_view.xml',
                'security/ir.model.access.csv'],
    'depends': ['web'],
    'name': 'Barcode',
    'post_init_hook': '_assign_default_nomeclature_id',
    'summary': 'Scan and Parse Barcodes'}

# FILEPATH: odoo/addons/barcodes/models/barcode_events_mixin.py
class BarcodesBarcode_Events_Mixin(models.AbstractModel):
    _name = 'barcodes.barcode_events_mixin'


# FILEPATH: odoo/addons/barcodes/models/barcode_nomenclature.py
UPC_EAN_CONVERSIONS = [
    ('none', 'Never'),
    ('ean2upc', 'EAN-13 to UPC-A'),
    ('upc2ean', 'UPC-A to EAN-13'),
    ('always', 'Always'),
]
class BarcodeNomenclature(models.Model):
    _name = 'barcode.nomenclature'


# FILEPATH: odoo/addons/barcodes/models/barcode_rule.py
class BarcodeRule(models.Model):
    _name = 'barcode.rule'


# FILEPATH: odoo/addons/barcodes/models/ir_http.py
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'


# FILEPATH: odoo/addons/barcodes/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'


# FILEPATH: odoo/addons/barcodes_gs1_nomenclature/__manifest__.py
{   'data': ['data/barcodes_gs1_rules.xml', 'views/barcodes_view.xml'],
    'depends': ['barcodes', 'uom'],
    'name': 'Barcode - GS1 Nomenclature',
    'summary': 'Parse barcodes according to the GS1-128 specifications'}

# FILEPATH: odoo/addons/barcodes_gs1_nomenclature/models/barcode_nomenclature.py
FNC1_CHAR = '\x1D'
class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'


# FILEPATH: odoo/addons/barcodes_gs1_nomenclature/models/barcode_rule.py
class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'


# FILEPATH: odoo/addons/barcodes_gs1_nomenclature/models/ir_http.py
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'


# FILEPATH: odoo/addons/contacts/__manifest__.py
{   'data': ['views/contact_views.xml'],
    'depends': ['base', 'mail'],
    'name': 'Contacts',
    'summary': 'Centralize your address book'}

# FILEPATH: odoo/addons/contacts/models/res_partner.py
class ResPartner(models.Model):
    _inherit = "res.partner"


# FILEPATH: odoo/addons/contacts/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'


# FILEPATH: odoo/addons/html_editor/__manifest__.py
{   'data': ['security/ir.model.access.csv'],
    'depends': ['base', 'bus', 'web'],
    'name': 'HTML Editor',
    'summary': '\n        A Html Editor component and plugin system\n    '}

# FILEPATH: odoo/addons/html_editor/models/diff_utils.py
OPERATION_SEPARATOR = "\n"
LINE_SEPARATOR = "<"
PATCH_OPERATION_LINE_AT = "@"
PATCH_OPERATION_CONTENT = ":"
PATCH_OPERATION_ADD = "+"
PATCH_OPERATION_REMOVE = "-"
PATCH_OPERATION_REPLACE = "R"
PATCH_OPERATIONS = dict(
    insert=PATCH_OPERATION_ADD,
    delete=PATCH_OPERATION_REMOVE,
    replace=PATCH_OPERATION_REPLACE)
HTML_ATTRIBUTES_TO_REMOVE = ["data-last-history-steps"]
HTML_TAG_ISOLATION_REGEX = r"^([^>]*>)(.*)$"
ADDITION_COMPARISON_REGEX = r"\1<added>\2</added>"
ADDITION_1ST_REPLACE_COMPARISON_REGEX = r"added>\2</added>"
DELETION_COMPARISON_REGEX = r"\1<removed>\2</removed>"
EMPTY_OPERATION_TAG = r"<(added|removed)><\/(added|removed)>"
SAME_TAG_REPLACE_FIXER = r"<\/added><(?:[^\/>]|(?:><))+><removed>"
UNNECESSARY_REPLACE_FIXER = (
    r"<added>([^<](?!<\/added>)*)<\/added>"
    r"<removed>([^<](?!<\/removed>)*)<\/removed>"
)


# FILEPATH: odoo/addons/html_editor/models/html_field_history_mixin.py
class HtmlFieldHistoryMixin(models.AbstractModel):
    _name = 'html.field.history.mixin'


# FILEPATH: odoo/addons/html_editor/models/ir_attachment.py
SUPPORTED_IMAGE_MIMETYPES = {
    'image/gif': '.gif',
    'image/jpe': '.jpe',
    'image/jpeg': '.jpeg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/svg+xml': '.svg',
    'image/webp': '.webp',
}
class IrAttachment(models.Model):
    _inherit = "ir.attachment"


# FILEPATH: odoo/addons/html_editor/models/ir_http.py
CONTEXT_KEYS = ['editable', 'edit_translations', 'translatable']
class IrHttp(models.AbstractModel):
    _inherit = "ir.http"


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 37-170)
REMOTE_CONNECTION_TIMEOUT = 2.5
logger = logging.getLogger(__name__)
class IrQweb(models.AbstractModel):
    _inherit = 'ir.qweb'


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 178-209)
class IrQwebField(models.AbstractModel):
    _name = 'ir.qweb.field'
    _inherit = ['ir.qweb.field']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 212-221)
class IrQwebFieldInteger(models.AbstractModel):
    _name = 'ir.qweb.field.integer'
    _inherit = ['ir.qweb.field.integer']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 224-234)
class IrQwebFieldFloat(models.AbstractModel):
    _name = 'ir.qweb.field.float'
    _inherit = ['ir.qweb.field.float']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 237-280)
class IrQwebFieldMany2one(models.AbstractModel):
    _name = 'ir.qweb.field.many2one'
    _inherit = ['ir.qweb.field.many2one']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 283-298)
class IrQwebFieldContact(models.AbstractModel):
    _name = 'ir.qweb.field.contact'
    _inherit = ['ir.qweb.field.contact']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 301-336)
class IrQwebFieldDate(models.AbstractModel):
    _name = 'ir.qweb.field.date'
    _inherit = ['ir.qweb.field.date']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 339-400)
class IrQwebFieldDatetime(models.AbstractModel):
    _name = 'ir.qweb.field.datetime'
    _inherit = ['ir.qweb.field.datetime']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 403-410)
class IrQwebFieldText(models.AbstractModel):
    _name = 'ir.qweb.field.text'
    _inherit = ['ir.qweb.field.text']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 413-427)
class IrQwebFieldSelection(models.AbstractModel):
    _name = 'ir.qweb.field.selection'
    _inherit = ['ir.qweb.field.selection']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 430-470)
class IrQwebFieldHtml(models.AbstractModel):
    _name = 'ir.qweb.field.html'
    _inherit = ['ir.qweb.field.html']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 473-563)
class IrQwebFieldImage(models.AbstractModel):
    _name = 'ir.qweb.field.image'
    _inherit = ['ir.qweb.field.image']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 566-576)
class IrQwebFieldMonetary(models.AbstractModel):
    _inherit = 'ir.qweb.field.monetary'


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 579-596)
class IrQwebFieldDuration(models.AbstractModel):
    _name = 'ir.qweb.field.duration'
    _inherit = ['ir.qweb.field.duration']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 599-604)
class IrQwebFieldRelative(models.AbstractModel):
    _name = 'ir.qweb.field.relative'
    _inherit = ['ir.qweb.field.relative']


# FILEPATH: odoo/addons/html_editor/models/ir_qweb_fields.py (lines 607-610)
class IrQwebFieldQweb(models.AbstractModel):
    _name = 'ir.qweb.field.qweb'
    _inherit = ['ir.qweb.field.qweb']

_PADDED_BLOCK = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}
_MISC_BLOCK = {"address", "article", "aside", "audio", "blockquote", "canvas",
               "dd", "dl", "div", "figcaption", "figure", "footer", "form",
               "header", "hgroup", "hr", "ol", "output", "pre", "section", "tfoot",
               "ul", "video"}


# FILEPATH: odoo/addons/html_editor/models/ir_ui_view.py
_logger = logging.getLogger(__name__)
EDITING_ATTRIBUTES = MOVABLE_BRANDING + [
    'data-oe-type',
    'data-oe-expression',
    'data-oe-translation-id',
    'data-note-id'
]
class IrUiView(models.Model):
    _inherit = 'ir.ui.view'


# FILEPATH: odoo/addons/html_editor/models/ir_websocket.py
class IrWebsocket(models.AbstractModel):
    _inherit = 'ir.websocket'


# FILEPATH: odoo/addons/html_editor/models/models.py
class Base(models.AbstractModel):
    _inherit = 'base'


# FILEPATH: odoo/addons/html_editor/models/test_models.py (lines 6-29)
class Html_EditorConverterTest(models.Model):
    _name = 'html_editor.converter.test'


# FILEPATH: odoo/addons/html_editor/models/test_models.py (lines 32-36)
class Html_EditorConverterTestSub(models.Model):
    _name = 'html_editor.converter.test.sub'


# FILEPATH: odoo/addons/html_editor/tools.py
logger = logging.getLogger(__name__)
valid_url_regex = r'^(http://|https://|//)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?$'
player_regexes = {
    'youtube': r'^(?:(?:https?:)?//)?(?:www\.|m\.)?(?:youtu\.be/|youtube(-nocookie)?\.com/(?:embed/|v/|shorts/|live/|watch\?v=|watch\?.+&v=))((?:\w|-){11})\S*$',
    'vimeo': r'//(player.)?vimeo.com/([a-z]*/)?(?P<id>[^/\?]+)(?:/(?P<hash>[^/\?]+))?(?:\?(?P<params>[^\s]+))?$',
    'dailymotion': r'(https?:\/\/)(www\.)?(dailymotion\.com\/(embed\/video\/|embed\/|video\/|hub\/.*#video=)|geo\.dailymotion\.com\/player\.html\?video=|dai\.ly\/)(?P<id>[A-Za-z0-9]{6,7})',
    'instagram': r'(?:(.*)instagram.com|instagr\.am)/p/(.[a-zA-Z0-9-_\.]*)',
    "facebook": r'^(?:(?:https?:)?//)?(?:www\.)?facebook\.com(?:/(?:[^/]+/)?videos/|/watch/?\?v=|/reel/|/plugins/video\.php\?[^ ]*?href=.*?(?:videos|reel)%2[Ff])(?P<id>\d+)',
}
diverging_history_regex = 'data-last-history-steps="([0-9,]+)"'


# FILEPATH: odoo/addons/onboarding/__manifest__.py
{   'data': [   'views/onboarding_templates.xml',
                'views/onboarding_views.xml',
                'views/onboarding_menus.xml',
                'security/ir.model.access.csv'],
    'depends': ['web'],
    'name': 'Onboarding Toolbox'}

# FILEPATH: odoo/addons/onboarding/models/onboarding_onboarding.py
class OnboardingOnboarding(models.Model):
    _name = 'onboarding.onboarding'


# FILEPATH: odoo/addons/onboarding/models/onboarding_onboarding_step.py
class OnboardingOnboardingStep(models.Model):
    _name = 'onboarding.onboarding.step'


# FILEPATH: odoo/addons/onboarding/models/onboarding_progress.py
ONBOARDING_PROGRESS_STATES = [
    ('not_done', 'Not done'),
    ('just_done', 'Just done'),
    ('done', 'Done'),
]
class OnboardingProgress(models.Model):
    _name = 'onboarding.progress'


# FILEPATH: odoo/addons/onboarding/models/onboarding_progress_step.py
class OnboardingProgressStep(models.Model):
    _name = 'onboarding.progress.step'


# FILEPATH: odoo/addons/purchase/__manifest__.py
{   'data': [   'security/purchase_security.xml',
                'security/ir.model.access.csv',
                'data/digest_data.xml',
                'views/account_move_views.xml',
                'data/purchase_data.xml',
                'data/ir_cron_data.xml',
                'report/purchase_reports.xml',
                'views/purchase_views.xml',
                'views/purchase_bill_line_match_views.xml',
                'views/res_config_settings_views.xml',
                'views/product_views.xml',
                'views/res_partner_views.xml',
                'report/purchase_bill_views.xml',
                'report/purchase_report_views.xml',
                'data/mail_templates.xml',
                'data/mail_template_data.xml',
                'views/portal_templates.xml',
                'report/purchase_order_templates.xml',
                'report/purchase_quotation_templates.xml',
                'views/analytic_account_views.xml',
                'wizard/bill_to_po_wizard_views.xml',
                'data/purchase_tour.xml'],
    'depends': ['account'],
    'name': 'Purchase',
    'summary': 'Purchase orders, tenders and agreements'}

# FILEPATH: odoo/addons/purchase/models/account_invoice.py (lines 16-518)
_logger = logging.getLogger(__name__)
TOLERANCE = 0.02
class AccountMove(models.Model):
    _inherit = 'account.move'
    purchase_id = fields.Many2one('purchase.order', store=False)
    # Shrunk non computed fields: purchase_vendor_bill_id, purchase_id
    # Shrunk computed_fields: purchase_order_count (_compute_origin_po_count), purchase_order_name (_compute_purchase_order_name), is_purchase_matched (_compute_is_purchase_matched), purchase_warning_text (_compute_purchase_warning_text)


# FILEPATH: odoo/addons/purchase/models/account_invoice.py (lines 521-558)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', related='purchase_line_id.order_id')
    # Shrunk non computed fields: is_downpayment, purchase_line_id, purchase_order_id
    # Shrunk computed_fields: purchase_line_warn_msg (_compute_purchase_line_warn_msg)


# FILEPATH: odoo/addons/purchase/models/account_tax.py
class AccountTax(models.Model):
    _inherit = "account.tax"


# FILEPATH: odoo/addons/purchase/models/analytic_account.py
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


# FILEPATH: odoo/addons/purchase/models/analytic_applicability.py
class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'


# FILEPATH: odoo/addons/purchase/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'


# FILEPATH: odoo/addons/purchase/models/product.py (lines 10-55)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # Shrunk non computed fields: purchase_line_warn_msg
    # Shrunk computed_fields: purchased_product_qty (_compute_purchased_product_qty), purchase_method (_compute_purchase_method)


# FILEPATH: odoo/addons/purchase/models/product.py (lines 58-141)
class ProductProduct(models.Model):
    _inherit = 'product.product'
    # Shrunk computed_fields: purchased_product_qty (_compute_purchased_product_qty), is_in_purchase_order (_compute_is_in_purchase_order)


# FILEPATH: odoo/addons/purchase/models/product.py (lines 144-154)
class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"


# FILEPATH: odoo/addons/purchase/models/purchase_bill_line_match.py
class PurchaseBillLineMatch(models.Model):
    _name = 'purchase.bill.line.match'


# FILEPATH: odoo/addons/purchase/models/purchase_order.py
_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'account.document.import.mixin']
    _description = "Purchase Order"
    _rec_names_search = ['name', 'partner_ref']
    _order = 'priority desc, id desc'
    order_line = fields.One2many('purchase.order.line', 'order_id')
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", store=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position')
    tax_country_id = fields.Many2one(comodel_name='res.country', compute='_compute_tax_country_id')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm')
    product_id = fields.Many2one('product.product', related='order_line.product_id')
    user_id = fields.Many2one('res.users')
    duplicated_order_ids = fields.Many2many(comodel_name='purchase.order', compute='_compute_duplicated_order_ids')
    # Shrunk non computed fields: name, priority, origin, partner_ref, date_order, date_approve, partner_id, dest_address_id, state, locked, lock_confirmed_po, order_line, acknowledged, note, partner_bill_count, fiscal_position_id, tax_calculation_rounding_method, payment_term_id, incoterm_id, product_id, user_id, company_id, company_currency_id, country_code, company_price_include, is_late
    # Shrunk computed_fields: currency_id (_compute_currency_id), invoice_count (_compute_invoice), invoice_ids (_compute_invoice), invoice_status (_get_invoiced), date_planned (_compute_date_planned), date_calendar_start (_compute_date_calendar_start), amount_untaxed (_amount_all), tax_totals (_compute_tax_totals), amount_tax (_amount_all), amount_total (_amount_all), amount_total_cc (_amount_all), tax_country_id (_compute_tax_country_id), currency_rate (_compute_currency_rate), duplicated_order_ids (_compute_duplicated_order_ids), receipt_reminder_email (_compute_receipt_reminder_email), reminder_date_before_receipt (_compute_receipt_reminder_email), show_comparison (_compute_show_comparison), purchase_warning_text (_compute_purchase_warning_text)


# FILEPATH: odoo/addons/purchase/models/purchase_order_line.py
class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['analytic.mixin']
    _description = 'Purchase Order Line'
    _order = 'order_id, sequence, id'
    tax_ids = fields.Many2many('account.tax')
    product_id = fields.Many2one('product.product')
    order_id = fields.Many2one('purchase.order')
    invoice_lines = fields.One2many('account.move.line', 'purchase_line_id')
    selected_seller_id = fields.Many2one('product.supplierinfo', compute='_compute_selected_seller_id')
    _accountable_required_fields = models.Constraint(
        'CHECK(display_type IS NOT NULL OR is_downpayment OR (product_id IS NOT NULL AND product_uom_id IS NOT NULL AND date_planned IS NOT NULL))',
        'Missing required fields on accountable purchase order line.')
    _non_accountable_null_fields = models.Constraint(
        'CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom_id IS NULL AND date_planned is NULL))',
        'Forbidden values on non-accountable purchase order line')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value')
    parent_id = fields.Many2one('purchase.order.line', compute='_compute_parent_id')
    # Shrunk non computed fields: sequence, product_qty, tax_ids, product_uom_id, product_id, product_type, order_id, company_id, state, invoice_lines, qty_received_manual, partner_id, currency_id, date_order, date_approve, tax_calculation_rounding_method, display_type, is_downpayment, product_template_attribute_value_ids, product_no_variant_attribute_value_ids, technical_price_unit
    # Shrunk computed_fields: name (_compute_price_unit_and_date_planned_and_name), translated_product_name (_compute_translated_product_name), product_uom_qty (_compute_product_uom_qty), date_planned (_compute_price_unit_and_date_planned_and_name), discount (_compute_price_unit_and_date_planned_and_name), allowed_uom_ids (_compute_allowed_uom_ids), price_unit (_compute_price_unit_and_date_planned_and_name), price_unit_product_uom (_compute_price_unit_product_uom), price_unit_discounted (_compute_price_unit_discounted), price_subtotal (_compute_amount), price_total (_compute_amount), price_tax (_compute_amount), qty_invoiced (_compute_qty_invoiced), qty_received_method (_compute_qty_received_method), qty_received (_compute_qty_received), qty_to_invoice (_compute_qty_invoiced), qty_received_at_date (_compute_qty_received_at_date), qty_invoiced_at_date (_compute_qty_invoiced_at_date), amount_to_invoice_at_date (_compute_amount_to_invoice_at_date), selected_seller_id (_compute_selected_seller_id), purchase_line_warn_msg (_compute_purchase_line_warn_msg), parent_id (_compute_parent_id)


# FILEPATH: odoo/addons/purchase/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'


# FILEPATH: odoo/addons/purchase/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


# FILEPATH: odoo/addons/purchase/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'


# FILEPATH: odoo/addons/resource/__manifest__.py
{   'data': [   'data/resource_data.xml',
                'security/ir.model.access.csv',
                'security/resource_security.xml',
                'views/resource_resource_views.xml',
                'views/resource_calendar_leaves_views.xml',
                'views/resource_calendar_attendance_views.xml',
                'views/resource_calendar_views.xml',
                'views/menuitems.xml'],
    'depends': ['base', 'web'],
    'name': 'Resource'}

# FILEPATH: odoo/addons/resource/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'


# FILEPATH: odoo/addons/resource/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'
    # Shrunk non computed fields: resource_ids, resource_calendar_id


# FILEPATH: odoo/addons/resource/models/resource_calendar.py
class DummyAttendance(NamedTuple):
    pass  # pruned

class ResourceCalendar(models.Model):
    _name = 'resource.calendar'


# FILEPATH: odoo/addons/resource/models/resource_calendar_attendance.py
class ResourceCalendarAttendance(models.Model):
    _name = 'resource.calendar.attendance'


# FILEPATH: odoo/addons/resource/models/resource_calendar_leaves.py
class ResourceCalendarLeaves(models.Model):
    _name = 'resource.calendar.leaves'


# FILEPATH: odoo/addons/resource/models/resource_mixin.py
class ResourceMixin(models.AbstractModel):
    _name = 'resource.mixin'


# FILEPATH: odoo/addons/resource/models/resource_resource.py
class ResourceResource(models.Model):
    _name = 'resource.resource'


# FILEPATH: odoo/addons/resource/models/utils.py
HOURS_PER_DAY = 8


# FILEPATH: odoo/addons/stock/__manifest__.py
{   'data': [   'security/stock_security.xml',
                'security/ir.model.access.csv',
                'data/digest_data.xml',
                'data/mail_templates.xml',
                'data/default_barcode_patterns.xml',
                'data/stock_data.xml',
                'data/stock_sequence_data.xml',
                'data/stock_traceability_report_data.xml',
                'report/report_stock_quantity.xml',
                'report/report_stock_reception.xml',
                'report/stock_report_views.xml',
                'report/report_package_barcode.xml',
                'report/report_lot_barcode.xml',
                'report/report_location_barcode.xml',
                'report/report_stockpicking_operations.xml',
                'report/report_deliveryslip.xml',
                'report/report_stockinventory.xml',
                'report/report_stock_rule.xml',
                'report/package_templates.xml',
                'report/packaging_barcode.xml',
                'report/picking_templates.xml',
                'report/product_templates.xml',
                'report/report_return_slip.xml',
                'data/mail_template_data.xml',
                'views/stock_menu_views.xml',
                'wizard/stock_picking_return_views.xml',
                'wizard/stock_inventory_conflict.xml',
                'wizard/stock_backorder_confirmation_views.xml',
                'wizard/stock_quantity_history.xml',
                'wizard/stock_request_count.xml',
                'wizard/stock_replenishment_info.xml',
                'wizard/stock_rules_report_views.xml',
                'wizard/stock_warn_insufficient_qty_views.xml',
                'wizard/product_replenish_views.xml',
                'wizard/product_label_layout_views.xml',
                'wizard/stock_orderpoint_snooze_views.xml',
                'wizard/stock_package_destination_views.xml',
                'wizard/stock_inventory_adjustment_name.xml',
                'wizard/stock_inventory_warning.xml',
                'wizard/stock_label_type.xml',
                'wizard/stock_lot_label_layout.xml',
                'wizard/stock_quant_relocate.xml',
                'wizard/stock_put_in_pack_views.xml',
                'views/res_partner_views.xml',
                'views/product_strategy_views.xml',
                'views/stock_lot_views.xml',
                'views/stock_scrap_views.xml',
                'views/stock_quant_views.xml',
                'views/stock_warehouse_views.xml',
                'views/stock_move_line_views.xml',
                'views/stock_move_views.xml',
                'views/stock_picking_views.xml',
                'views/stock_picking_type_views.xml',
                'views/product_views.xml',
                'views/stock_location_views.xml',
                'views/stock_orderpoint_views.xml',
                'views/stock_storage_category_views.xml',
                'views/res_config_settings_views.xml',
                'views/report_stock_traceability.xml',
                'views/stock_template.xml',
                'views/stock_rule_views.xml',
                'views/stock_package_history_views.xml',
                'views/stock_package_type_view.xml',
                'views/stock_package_views.xml',
                'views/stock_forecasted.xml',
                'views/stock_reference_views.xml',
                'views/uom_uom_views.xml'],
    'depends': ['product', 'barcodes_gs1_nomenclature', 'digest'],
    'name': 'Inventory',
    'post_init_hook': '_assign_default_mail_template_picking_id',
    'pre_init_hook': 'pre_init_hook',
    'summary': 'Manage your stock and logistics activities',
    'uninstall_hook': 'uninstall_hook'}

# FILEPATH: odoo/addons/stock/models/barcode.py
class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'


# FILEPATH: odoo/addons/stock/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'


# FILEPATH: odoo/addons/stock/models/product.py (lines 47-798)
PY_OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne,
    'in': lambda elem, container: elem in container,
    'not in': lambda elem, container: elem not in container,
}
SERIAL_PREFIX_FORMAT_HELP_TEXT = """
    If multiple products share the same prefix, they will share the same sequence, otherwise the sequence will be dedicated to the product.

    * Legend (for prefix):
    - Current Year with Century: %(year)s
    - Current Year without Century: %(y)s
    - Month: %(month)s
    - Day: %(day)s
    - Day of the Year: %(doy)s
    - Week of the Year: %(woy)s
    - Day of the Week (0:Monday): %(weekday)s
    - Hour 00->24: %(h24)s
    - Hour 00->12: %(h12)s
    - Minute: %(min)s
    - Second: %(sec)s
"""
class ProductProduct(models.Model):
    _inherit = "product.product"
    stock_move_ids = fields.One2many('stock.move', 'product_id')
    # Shrunk non computed fields: stock_quant_ids, stock_move_ids, orderpoint_ids, putaway_rule_ids, storage_category_capacity_ids, lot_properties_definition
    # Shrunk computed_fields: qty_available (_compute_quantities), virtual_available (_compute_quantities), free_qty (_compute_quantities), incoming_qty (_compute_quantities), outgoing_qty (_compute_quantities), nbr_moves_in (_compute_nbr_moves), nbr_moves_out (_compute_nbr_moves), nbr_reordering_rules (_compute_nbr_reordering_rules), reordering_min_qty (_compute_nbr_reordering_rules), reordering_max_qty (_compute_nbr_reordering_rules), show_on_hand_qty_status_button (_compute_show_qty_status_button), show_forecasted_qty_status_button (_compute_show_qty_status_button), show_qty_update_button (_compute_show_qty_update_button), valid_ean (_compute_valid_ean)


# FILEPATH: odoo/addons/stock/models/product.py (lines 801-1224)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True
    responsible_id = fields.Many2one('res.users')
    property_stock_production = fields.Many2one('stock.location', "Production Location")
    property_stock_inventory = fields.Many2one('stock.location', "Inventory Location")
    location_id = fields.Many2one('stock.location', 'Location', store=False)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', store=False)
    # Shrunk non computed fields: responsible_id, property_stock_production, property_stock_inventory, sale_delay, lot_sequence_id, description_picking, description_pickingout, description_pickingin, location_id, warehouse_id, route_ids, route_from_categ_ids
    # Shrunk computed_fields: is_storable (compute_is_storable), tracking (_compute_tracking), serial_prefix_format (_compute_serial_prefix_format), next_serial (_compute_next_serial), qty_available (_compute_quantities), virtual_available (_compute_quantities), incoming_qty (_compute_quantities), outgoing_qty (_compute_quantities), has_available_route_ids (_compute_has_available_route_ids), nbr_moves_in (_compute_nbr_moves), nbr_moves_out (_compute_nbr_moves), nbr_reordering_rules (_compute_nbr_reordering_rules), reordering_min_qty (_compute_nbr_reordering_rules), reordering_max_qty (_compute_nbr_reordering_rules), show_on_hand_qty_status_button (_compute_show_qty_status_button), show_forecasted_qty_status_button (_compute_show_qty_status_button), show_qty_update_button (_compute_show_qty_update_button)


# FILEPATH: odoo/addons/stock/models/product.py (lines 1227-1288)
class ProductCategory(models.Model):
    _inherit = 'product.category'


# FILEPATH: odoo/addons/stock/models/product.py (lines 1291-1342)
class UomUom(models.Model):
    _inherit = 'uom.uom'


# FILEPATH: odoo/addons/stock/models/product_catalog_mixin.py
class ProductCatalogMixin(models.AbstractModel):
    _inherit = "product.catalog.mixin"


# FILEPATH: odoo/addons/stock/models/product_strategy.py (lines 8-13)
class ProductRemoval(models.Model):
    _name = 'product.removal'


# FILEPATH: odoo/addons/stock/models/product_strategy.py (lines 16-183)
class StockPutawayRule(models.Model):
    _name = 'stock.putaway.rule'


# FILEPATH: odoo/addons/stock/models/res_company.py
class ResCompany(models.Model):
    _inherit = "res.company"


# FILEPATH: odoo/addons/stock/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


# FILEPATH: odoo/addons/stock/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'


# FILEPATH: odoo/addons/stock/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'


# FILEPATH: odoo/addons/stock/models/stock_location.py (lines 13-514)
class StockLocation(models.Model):
    _name = 'stock.location'
    _description = "Inventory Locations"
    _parent_name = "location_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_names_search = ['complete_name', 'barcode']
    _check_company_auto = True
    location_id = fields.Many2one('stock.location', 'Parent Location')
    child_ids = fields.One2many('stock.location', 'location_id', 'Contains')
    child_internal_location_ids = fields.Many2many('stock.location', compute='_compute_child_internal_location_ids')
    warehouse_view_ids = fields.One2many('stock.warehouse', 'view_location_id')
    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse_id', store=True)
    outgoing_move_line_ids = fields.One2many('stock.move.line', 'location_id')
    incoming_move_line_ids = fields.One2many('stock.move.line', 'location_dest_id')
    _barcode_company_uniq = models.Constraint(
        'unique (barcode,company_id)',
        'The barcode for a location must be unique per company!')
    _inventory_freq_nonneg = models.Constraint(
        'check(cyclic_inventory_frequency >= 0)',
        'The inventory frequency (days) for a location must be non-negative')
    _parent_path_id_idx = models.Index("(parent_path, id)")
    # Shrunk non computed fields: name, active, usage, location_id, child_ids, parent_path, company_id, removal_strategy_id, putaway_rule_ids, barcode, quant_ids, cyclic_inventory_frequency, last_inventory_date, warehouse_view_ids, storage_category_id, outgoing_move_line_ids, incoming_move_line_ids
    # Shrunk computed_fields: complete_name (_compute_complete_name), child_internal_location_ids (_compute_child_internal_location_ids), replenish_location (_compute_replenish_location), next_inventory_date (_compute_next_inventory_date), warehouse_id (_compute_warehouse_id), net_weight (_compute_weight), forecast_weight (_compute_weight), is_empty (_compute_is_empty)


# FILEPATH: odoo/addons/stock/models/stock_location.py (lines 517-595)
class StockRoute(models.Model):
    _name = 'stock.route'


# FILEPATH: odoo/addons/stock/models/stock_lot.py
PY_OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne,
    'in': lambda elem, container: elem in container,
    'not in': lambda elem, container: elem not in container,
}
class StockLot(models.Model):
    _name = 'stock.lot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Lot/Serial'
    _check_company_auto = True
    _order = 'name, id'
    product_id = fields.Many2one('product.product', 'Product')
    delivery_ids = fields.Many2many('stock.picking', compute='_compute_delivery_ids')
    location_id = fields.Many2one('stock.location', 'Location', compute='_compute_single_location', store=True)
    # Shrunk non computed fields: ref, product_id, product_uom_id, quant_ids, note, lot_properties
    # Shrunk computed_fields: name (_compute_name), product_qty (_product_qty), display_complete (_compute_display_complete), company_id (_compute_company_id), delivery_ids (_compute_delivery_ids), delivery_count (_compute_delivery_ids), partner_ids (_compute_partner_ids), location_id (_compute_single_location)


# FILEPATH: odoo/addons/stock/models/stock_move.py
PROCUREMENT_PRIORITIES = [('0', 'Normal'), ('1', 'Urgent')]
class StockMove(models.Model):
    _name = 'stock.move'
    _description = "Stock Move"
    _order = 'sequence, id'
    _rec_name = 'reference'
    product_id = fields.Many2one('product.product', 'Product')
    never_product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value', 'template_attribute_value_stock_move_rel', 'move_id', 'template_attribute_value_id')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    location_id = fields.Many2one('stock.location', 'Source Location', compute='_compute_location_id', store=True)
    location_dest_id = fields.Many2one('stock.location', 'Intermediate Location', store=True, compute='_compute_location_dest_id')
    location_final_id = fields.Many2one('stock.location', 'Final Location', store=True)
    move_dest_ids = fields.Many2many('stock.move', 'stock_move_move_rel', 'move_orig_id', 'move_dest_id', 'Destination Moves')
    move_orig_ids = fields.Many2many('stock.move', 'stock_move_move_rel', 'move_dest_id', 'move_orig_id', 'Original Move')
    picking_id = fields.Many2one('stock.picking', 'Transfer')
    reference_ids = fields.Many2many('stock.reference', 'stock_reference_move_rel', 'move_id', 'reference_id')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', compute='_compute_picking_type_id', store=True)
    move_line_ids = fields.One2many('stock.move.line', 'move_id')
    origin_returned_move_id = fields.Many2one('stock.move', 'Origin return move')
    returned_move_ids = fields.One2many('stock.move', 'origin_returned_move_id', 'All returned moves')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    lot_ids = fields.Many2many('stock.lot', compute='_compute_lot_ids')
    _product_location_index = models.Index("(product_id, location_id, location_dest_id, company_id, state)")
    # Shrunk non computed fields: sequence, date, date_deadline, company_id, product_id, product_category_id, never_product_template_attribute_value_ids, description_picking_manual, product_uom_qty, product_tmpl_id, location_final_id, location_usage, location_dest_usage, move_dest_ids, move_orig_ids, picking_id, state, price_unit, origin, procure_method, scrap_id, procurement_values, reference_ids, rule_id, propagate_cancel, is_inventory, inventory_name, move_line_ids, origin_returned_move_id, returned_move_ids, restrict_partner_id, route_ids, warehouse_id, has_tracking, show_operations, picking_code, is_storable, additional, next_serial, next_serial_count, orderpoint_id
    # Shrunk computed_fields: priority (_compute_priority), description_picking (_compute_description_picking), product_qty (_compute_product_qty), allowed_uom_ids (_compute_allowed_uom_ids), product_uom (_compute_product_uom), location_id (_compute_location_id), location_dest_id (_compute_location_dest_id), partner_id (_compute_partner_id), picked (_compute_picked), delay_alert_date (_compute_delay_alert_date), picking_type_id (_compute_picking_type_id), package_ids (_compute_package_ids), availability (_compute_product_availability), has_lines_without_result_package (_compute_has_lines_without_result_package), quantity (_compute_quantity), show_details_visible (_compute_show_details_visible), is_locked (_compute_is_locked), is_initial_demand_editable (_compute_is_initial_demand_editable), is_date_editable (_compute_is_date_editable), is_quantity_done_editable (_compute_is_quantity_done_editable), reference (_compute_reference), move_lines_count (_compute_move_lines_count), display_assign_serial (_compute_display_assign_serial), display_import_lot (_compute_display_assign_serial), forecast_availability (_compute_forecast_information), forecast_expected_date (_compute_forecast_information), lot_ids (_compute_lot_ids), reservation_date (_compute_reservation_date), packaging_uom_id (_compute_packaging_uom_id), packaging_uom_qty (_compute_packaging_uom_qty), show_quant (_compute_show_info), show_lots_m2o (_compute_show_info), show_lots_text (_compute_show_info)


# FILEPATH: odoo/addons/stock/models/stock_move_line.py
class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _description = "Product Moves (Stock Move Line)"
    _rec_name = "product_id"
    _order = "result_package_id desc, id"
    picking_id = fields.Many2one('stock.picking', 'Transfer')
    move_id = fields.Many2one('stock.move', 'Stock Operation')
    product_id = fields.Many2one('product.product', 'Product')
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number')
    package_history_id = fields.Many2one('stock.package.history')
    location_id = fields.Many2one('stock.location', 'From', compute="_compute_location_id", store=True)
    location_dest_id = fields.Many2one('stock.location', 'To', compute="_compute_location_id", store=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation type', compute='_compute_picking_type_id')
    consume_line_ids = fields.Many2many('stock.move.line', 'stock_move_line_consume_rel', 'consume_line_id', 'produce_line_id')
    produce_line_ids = fields.Many2many('stock.move.line', 'stock_move_line_consume_rel', 'produce_line_id', 'consume_line_id')
    _free_reservation_index = models.Index("""(id, company_id, product_id, lot_id, location_id, owner_id, package_id)
        WHERE (state IS NULL OR state NOT IN ('cancel', 'done')) AND quantity_product_uom > 0 AND picked IS NOT TRUE""")
    # Shrunk non computed fields: picking_id, move_id, company_id, product_id, product_category_name, package_id, lot_id, lot_name, result_package_id, result_package_dest_name, package_history_id, is_entire_pack, date, scheduled_date, owner_id, location_usage, location_dest_usage, picking_partner_id, move_partner_id, picking_code, picking_type_use_create_lots, picking_type_use_existing_lots, state, scrap_id, is_inventory, is_locked, consume_line_ids, produce_line_ids, reference, tracking, origin, description_picking, quant_id, picking_location_id, picking_location_dest_id
    # Shrunk computed_fields: allowed_uom_ids (_compute_allowed_uom_ids), product_uom_id (_compute_product_uom_id), quantity (_compute_quantity), quantity_product_uom (_compute_quantity_product_uom), picked (_compute_picked), location_id (_compute_location_id), location_dest_id (_compute_location_id), lots_visible (_compute_lots_visible), picking_type_id (_compute_picking_type_id)


# FILEPATH: odoo/addons/stock/models/stock_orderpoint.py
_logger = logging.getLogger(__name__)
class StockWarehouseOrderpoint(models.Model):
    _name = 'stock.warehouse.orderpoint'


# FILEPATH: odoo/addons/stock/models/stock_package.py
class StockPackage(models.Model):
    _name = 'stock.package'


# FILEPATH: odoo/addons/stock/models/stock_package_history.py
class StockPackageHistory(models.Model):
    _name = 'stock.package.history'
    _description = "Stock Package History"
    _check_company_auto = True
    location_id = fields.Many2one('stock.location', 'Origin Location')
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    move_line_ids = fields.One2many('stock.move.line', 'package_history_id')
    picking_ids = fields.Many2many('stock.picking')
    # Shrunk non computed fields: company_id, location_id, location_dest_id, move_line_ids, package_id, package_name, package_type_id, parent_orig_id, parent_orig_name, parent_dest_id, parent_dest_name, outermost_dest_id, picking_ids


# FILEPATH: odoo/addons/stock/models/stock_package_type.py
class StockPackageType(models.Model):
    _name = 'stock.package.type'


# FILEPATH: odoo/addons/stock/models/stock_picking.py (lines 20-535)
class StockPickingType(models.Model):
    _name = 'stock.picking.type'
    _description = "Picking Type"
    _order = 'is_favorite desc, sequence, id'
    _rec_names_search = ['name', 'warehouse_id.name']
    _check_company_auto = True
    default_location_src_id = fields.Many2one('stock.location', 'Source Location', compute='_compute_default_location_src_id', store=True)
    default_location_dest_id = fields.Many2one('stock.location', 'Destination Location', compute='_compute_default_location_dest_id', store=True)
    return_picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type for Returns')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', compute='_compute_warehouse_id', store=True)
    favorite_user_ids = fields.Many2many('res.users', 'picking_type_favorite_user_rel', 'picking_type_id', 'user_id')
    # Shrunk non computed fields: name, color, sequence, sequence_id, sequence_code, code, return_picking_type_id, show_entire_packs, set_package_type, active, show_operations, reservation_method, reservation_days_before, reservation_days_before_priority, auto_show_reception_report, auto_print_delivery_slip, auto_print_return_slip, auto_print_product_labels, product_label_format, auto_print_lot_labels, lot_label_format, auto_print_reception_report, auto_print_reception_report_labels, auto_print_packages, auto_print_package_label, package_label_to_print, barcode, company_id, create_backorder, picking_properties_definition, favorite_user_ids, move_type
    # Shrunk computed_fields: default_location_src_id (_compute_default_location_src_id), default_location_dest_id (_compute_default_location_dest_id), warehouse_id (_compute_warehouse_id), use_create_lots (_compute_use_create_lots), use_existing_lots (_compute_use_existing_lots), print_label (_compute_print_label), count_picking_draft (_compute_picking_count), count_picking_ready (_compute_picking_count), count_picking (_compute_picking_count), count_picking_waiting (_compute_picking_count), count_picking_late (_compute_picking_count), count_picking_backorders (_compute_picking_count), count_move_ready (_compute_move_count), hide_reservation_method (_compute_hide_reservation_method), show_picking_type (_compute_show_picking_type), is_favorite (_compute_is_favorite), kanban_dashboard_graph (_compute_kanban_dashboard_graph)


# FILEPATH: odoo/addons/stock/models/stock_picking.py (lines 538-2142)
class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transfer"
    _order = "priority desc, scheduled_date asc, id desc"
    backorder_id = fields.Many2one('stock.picking', 'Back Order of')
    backorder_ids = fields.One2many('stock.picking', 'backorder_id', 'Back Orders')
    return_id = fields.Many2one('stock.picking', 'Return of')
    return_ids = fields.One2many('stock.picking', 'return_id', 'Returns')
    reference_ids = fields.Many2many('stock.reference', related="move_ids.reference_ids")
    location_id = fields.Many2one('stock.location', "Source Location", compute="_compute_location_id", store=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location", compute="_compute_location_id", store=True)
    move_ids = fields.One2many('stock.move', 'picking_id')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    user_id = fields.Many2one('res.users', 'Responsible')
    move_line_ids = fields.One2many('stock.move.line', 'picking_id', 'Operations')
    package_history_ids = fields.Many2many('stock.package.history')
    product_id = fields.Many2one('product.product', 'Product', related='move_ids.product_id')
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number', related='move_line_ids.lot_id')
    partner_country_id = fields.Many2one('res.country', related='partner_id.country_id')
    _name_uniq = models.Constraint(
        'unique(name, company_id)',
        'Reference must be unique per company!')
    # Shrunk non computed fields: name, origin, note, backorder_id, backorder_ids, return_id, return_ids, reference_ids, priority, date_done, move_ids, picking_type_id, warehouse_address_id, picking_type_code, picking_type_entire_packs, use_create_lots, use_existing_lots, partner_id, company_id, user_id, move_line_ids, package_history_ids, owner_id, printed, signature, is_locked, product_id, lot_id, show_operations, picking_properties, search_date_category, partner_country_id
    # Shrunk computed_fields: return_count (_compute_return_count), move_type (_compute_move_type), state (_compute_state), scheduled_date (_compute_scheduled_date), date_deadline (_compute_date_deadline), has_deadline_issue (_compute_has_deadline_issue), delay_alert_date (_compute_delay_alert_date), json_popover (_compute_json_popover), location_id (_compute_location_id), location_dest_id (_compute_location_id), has_scrap_move (_has_scrap_move), packages_count (_compute_packages_count), show_check_availability (_compute_show_check_availability), show_allocation (_compute_show_allocation), is_signed (_compute_is_signed), is_date_editable (_compute_is_date_editable), weight_bulk (_compute_bulk_weight), shipping_weight (_compute_shipping_weight), shipping_volume (_compute_shipping_volume), show_lots_text (_compute_show_lots_text), has_tracking (_compute_has_tracking), products_availability (_compute_products_availability), products_availability_state (_compute_products_availability), show_next_pickings (_compute_show_next_pickings), picking_warning_text (_compute_picking_warning_text)


# FILEPATH: odoo/addons/stock/models/stock_quant.py
_logger = logging.getLogger(__name__)
class StockQuant(models.Model):
    _name = 'stock.quant'


# FILEPATH: odoo/addons/stock/models/stock_reference.py
class StockReference(models.Model):
    _name = 'stock.reference'
    _description = 'Reference between stock documents'
    move_ids = fields.Many2many('stock.move', 'stock_reference_move_rel', 'reference_id', 'move_id')
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking_ids')
    # Shrunk non computed fields: name, move_ids
    # Shrunk computed_fields: picking_ids (_compute_picking_ids)


# FILEPATH: odoo/addons/stock/models/stock_replenish_mixin.py
class StockReplenishMixin(models.AbstractModel):
    _name = 'stock.replenish.mixin'


# FILEPATH: odoo/addons/stock/models/stock_rule.py
_logger = logging.getLogger(__name__)
class ProcurementException(Exception):
    pass  # pruned

class Procurement(NamedTuple):
    pass  # pruned

class StockRule(models.Model):
    _name = 'stock.rule'


# FILEPATH: odoo/addons/stock/models/stock_scrap.py (lines 10-230)
class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['mail.thread']


# FILEPATH: odoo/addons/stock/models/stock_scrap.py (lines 233-245)
class StockScrapReasonTag(models.Model):
    _name = 'stock.scrap.reason.tag'


# FILEPATH: odoo/addons/stock/models/stock_storage_category.py (lines 7-45)
class StockStorageCategory(models.Model):
    _name = 'stock.storage.category'


# FILEPATH: odoo/addons/stock/models/stock_storage_category.py (lines 48-75)
class StockStorageCategoryCapacity(models.Model):
    _name = 'stock.storage.category.capacity'


# FILEPATH: odoo/addons/stock/models/stock_warehouse.py
_lt = LazyTranslate(__name__)
ROUTE_NAMES = {
    'one_step': _lt('Receive in 1 step (stock)'),
    'two_steps': _lt('Receive in 2 steps (input + stock)'),
    'three_steps': _lt('Receive in 3 steps (input + quality + stock)'),
    'ship_only': _lt('Deliver in 1 step (ship)'),
    'pick_ship': _lt('Deliver in 2 steps (pick + ship)'),
    'pick_pack_ship': _lt('Deliver in 3 steps (pick + pack + ship)'),
}
class StockWarehouse(models.Model):
    _name = 'stock.warehouse'
    _description = "Warehouse"
    _order = 'sequence,id'
    _check_company_auto = True
    Routing = namedtuple('Routing', ['from_loc', 'dest_loc', 'picking_type', 'action'])
    view_location_id = fields.Many2one('stock.location', 'View Location')
    lot_stock_id = fields.Many2one('stock.location', 'Location Stock')
    wh_input_stock_loc_id = fields.Many2one('stock.location', 'Input Location')
    wh_qc_stock_loc_id = fields.Many2one('stock.location', 'Quality Control Location')
    wh_output_stock_loc_id = fields.Many2one('stock.location', 'Output Location')
    wh_pack_stock_loc_id = fields.Many2one('stock.location', 'Packing Location')
    pick_type_id = fields.Many2one('stock.picking.type', 'Pick Type')
    pack_type_id = fields.Many2one('stock.picking.type', 'Pack Type')
    out_type_id = fields.Many2one('stock.picking.type', 'Out Type')
    in_type_id = fields.Many2one('stock.picking.type', 'In Type')
    int_type_id = fields.Many2one('stock.picking.type', 'Internal Type')
    qc_type_id = fields.Many2one('stock.picking.type', 'Quality Control Type')
    store_type_id = fields.Many2one('stock.picking.type', 'Storage Type')
    xdock_type_id = fields.Many2one('stock.picking.type', 'Cross Dock Type')
    resupply_wh_ids = fields.Many2many('stock.warehouse', 'stock_wh_resupply_table', 'supplied_wh_id', 'supplier_wh_id', 'Resupply From')
    _warehouse_name_uniq = models.Constraint(
        'unique(name, company_id)',
        'The name of the warehouse must be unique per company!')
    _warehouse_code_uniq = models.Constraint(
        'unique(code, company_id)',
        'The short name of the warehouse must be unique per company!')
    # Shrunk non computed fields: name, active, company_id, partner_id, view_location_id, lot_stock_id, code, route_ids, reception_steps, delivery_steps, wh_input_stock_loc_id, wh_qc_stock_loc_id, wh_output_stock_loc_id, wh_pack_stock_loc_id, mto_pull_id, pick_type_id, pack_type_id, out_type_id, in_type_id, int_type_id, qc_type_id, store_type_id, xdock_type_id, reception_route_id, delivery_route_id, resupply_wh_ids, resupply_route_ids, sequence
