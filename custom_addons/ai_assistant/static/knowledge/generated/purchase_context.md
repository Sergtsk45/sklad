Role: Senior Odoo Architect enforcing OCA standards.
Context: The following is a codebase dump produced by the akaidoo CLI.
Command: /home/serg45/.local/bin/akaidoo addon purchase -c akaidoo.conf --shrink=hard -B 30k -o custom_addons/ai_assistant/static/knowledge/generated/purchase_context.md
Conventions:
1. Files start with `# FILEPATH: [path]`.
2. Some files were filtered out to save tokens; ask for them if you need.
3. `# shrunk` indicates code removed to save tokens; ask for full content if a specific logic flow is unclear.
4. Method definitions were eventually entirely skipped to save tokens and focus on the data model only.

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
    _description = "Account"
    _order = "code, placeholder_code"
    _check_company_auto = True
    _check_company_domain = models.check_companies_domain_parent_of
    tax_ids = fields.Many2many('account.tax', 'account_account_tax_default_rel', 'account_id', 'tax_id')
    code_mapping_ids.write_sequence = 19
    # Shrunk non computed fields: name, description, currency_id, code_store, active, tax_ids, note, company_ids, code_mapping_ids, non_trade, display_mapping_tab
    # Shrunk computed_fields: company_currency_id (_compute_company_currency_id), company_fiscal_country_code (_compute_company_fiscal_country_code), code (_compute_code), placeholder_code (_compute_placeholder_code), used (_compute_used), account_type (_compute_account_type), include_initial_balance (_compute_include_initial_balance), internal_group (_compute_internal_group), reconcile (_compute_reconcile), tag_ids (_compute_account_tags), group_id (_compute_account_group), root_id (_compute_account_root), opening_debit (_compute_opening_debit_credit), opening_credit (_compute_opening_debit_credit), opening_balance (_compute_opening_debit_credit), current_balance (_compute_current_balance), related_taxes_amount (_compute_related_taxes_amount)


# FILEPATH: odoo/addons/account/models/account_account.py (lines 1484-1628)
class AccountGroup(models.Model):
    _name = 'account.group'


# FILEPATH: odoo/addons/account/models/account_account_tag.py
class AccountAccountTag(models.Model):
    _name = 'account.account.tag'


# FILEPATH: odoo/addons/account/models/account_analytic_account.py
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    # Shrunk computed_fields: invoice_count (_compute_invoice_count), vendor_bill_count (_compute_vendor_bill_count)


# FILEPATH: odoo/addons/account/models/account_analytic_distribution_model.py
class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.distribution.model'


# FILEPATH: odoo/addons/account/models/account_analytic_line.py
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = 'Analytic Line'
    product_id = fields.Many2one('product.product')
    general_account_id = fields.Many2one('account.account', compute='_compute_general_account_id', store=True)
    journal_id = fields.Many2one('account.journal', related='move_line_id.journal_id', store=True)
    move_line_id = fields.Many2one('account.move.line')
    # Shrunk non computed fields: product_id, journal_id, move_line_id, code, ref, category
    # Shrunk computed_fields: general_account_id (_compute_general_account_id), partner_id (_compute_partner_id)


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
    _description = "Bank Statement Line"
    _order = "internal_index desc"
    _check_company_auto = True
    move_id = fields.Many2one(comodel_name='account.move')
    journal_id = fields.Many2one(comodel_name='account.journal', related='move_id.journal_id', store=True)
    payment_ids = fields.Many2many(comodel_name='account.payment', relation='account_payment_account_bank_statement_line_rel')
    _unreconciled_idx = models.Index("(journal_id, company_id, internal_index) WHERE is_reconciled IS NOT TRUE")
    _orphan_idx = models.Index("(journal_id, company_id, internal_index) WHERE statement_id IS NULL")
    _main_idx = models.Index("(journal_id, company_id, internal_index)")
    # Shrunk non computed fields: move_id, journal_id, company_id, statement_id, payment_ids, sequence, partner_id, account_number, partner_name, transaction_type, payment_ref, amount, foreign_currency_id, country_code, statement_complete, statement_valid, statement_balance_end_real, statement_name, transaction_details
    # Shrunk computed_fields: currency_id (_compute_currency_id), running_balance (_compute_running_balance), amount_currency (_compute_amount_currency), amount_residual (_compute_is_reconciled), internal_index (_compute_internal_index), is_reconciled (_compute_is_reconciled)


# FILEPATH: odoo/addons/account/models/account_bank_statement_line.py (lines 839-842)
class AccountMove(models.Model):
    _inherit = 'account.move'
    statement_line_ids = fields.One2many('account.bank.statement.line', 'move_id')
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
    _description = "Account Journal Group"
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of
    excluded_journal_ids = fields.Many2many(comodel_name='account.journal')
    _uniq_name = models.Constraint(
        'unique(company_id, name)',
        'A Ledger group name must be unique per company.')
    # Shrunk non computed fields: name, company_id, excluded_journal_ids, sequence


# FILEPATH: odoo/addons/account/models/account_journal.py (lines 42-1300)
class AccountJournal(models.Model):
    _name = 'account.journal'
    _description = "Journal"
    _order = 'sequence, type, code'
    _inherit = ['portal.mixin',
                'mail.alias.mixin.optional',
                'mail.thread',
                'mail.activity.mixin',
               ]
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of
    _rec_names_search = ['name', 'code']
    default_account_id = fields.Many2one(comodel_name='account.account')
    suspense_account_id = fields.Many2one(comodel_name='account.account', store=True, compute='_compute_suspense_account_id')
    non_deductible_account_id = fields.Many2one(comodel_name='account.account', store=True)
    invoice_template_pdf_report_id = fields.Many2one(comodel_name='ir.actions.report')
    available_invoice_template_pdf_report_ids = fields.One2many(comodel_name='ir.actions.report', compute='_compute_available_invoice_template_pdf_report_ids')
    profit_account_id = fields.Many2one(comodel_name='account.account')
    loss_account_id = fields.Many2one(comodel_name='account.account')
    journal_group_ids = fields.Many2many('account.journal.group')
    _code_company_uniq = models.Constraint(
        'unique (company_id, code)',
        'Journal codes must be unique per company.')
    # Shrunk non computed fields: name, active, type, is_self_billing, default_account_id, non_deductible_account_id, restrict_mode_hash_table, sequence, invoice_reference_type, invoice_reference_model, currency_id, company_id, country_code, account_fiscal_country_group_codes, invoice_template_pdf_report_id, display_invoice_template_pdf_report_id, sequence_override_regex, profit_account_id, loss_account_id, company_partner_id, bank_account_id, bank_statements_source, bank_acc_number, bank_id, alias_name, journal_group_ids, incoming_einvoice_notification_email
    # Shrunk computed_fields: name_placeholder (_compute_name_placeholder), code (_compute_code), default_account_type (_compute_default_account_type), suspense_account_id (_compute_suspense_account_id), refund_sequence (_compute_refund_sequence), payment_sequence (_compute_payment_sequence), available_invoice_template_pdf_report_ids (_compute_available_invoice_template_pdf_report_ids), inbound_payment_method_line_ids (_compute_inbound_payment_method_line_ids), outbound_payment_method_line_ids (_compute_outbound_payment_method_line_ids), available_payment_method_ids (_compute_available_payment_method_ids), selected_payment_method_codes (_compute_selected_payment_method_codes), accounting_date (_compute_accounting_date), display_alias_fields (_compute_display_alias_fields), has_invalid_statements (_compute_has_invalid_statements), show_fetch_in_einvoices_button (_compute_show_fetch_in_einvoices_button), show_refresh_out_einvoices_status_button (_compute_show_refresh_out_einvoices_status_button)


# FILEPATH: odoo/addons/account/models/account_journal_dashboard.py
class AccountJournal(models.Model):
    _inherit = "account.journal"
    # Shrunk non computed fields: show_on_dashboard, color
    # Shrunk computed_fields: kanban_dashboard (_kanban_dashboard), kanban_dashboard_graph (_kanban_dashboard_graph), json_activity_data (_get_json_activity_data), current_statement_balance (_compute_current_statement_balance), has_statement_lines (_compute_current_statement_balance), entries_count (_compute_entries_count), has_posted_entries (_compute_has_entries), has_entries (_compute_has_entries), has_sequence_holes (_compute_has_sequence_holes), has_unhashed_entries (_compute_has_unhashed_entries), last_statement_id (_compute_last_bank_statement)


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
    journal_id = fields.Many2one('account.journal', compute='_compute_journal_id', store=True)
    journal_group_id = fields.Many2one('account.journal.group', store=False)
    line_ids = fields.One2many('account.move.line', 'move_id')
    journal_line_ids = fields.One2many(comodel_name='account.move.line', inverse_name='move_id')
    origin_payment_id = fields.Many2one(comodel_name='account.payment')
    matched_payment_ids = fields.Many2many(comodel_name='account.payment', relation='account_move__account_payment', column1='invoice_id', column2='payment_id')
    reconciled_payment_ids = fields.Many2many('account.payment', compute='_compute_reconciled_payment_ids')
    statement_line_id = fields.Many2one(comodel_name='account.bank.statement.line')
    adjusting_entry_origin_move_ids = fields.Many2many(comodel_name='account.move', relation='adjusting_entries__account_move', column1='move_id', column2='adjusting_entry_move_id')
    adjusting_entries_move_ids = fields.Many2many(comodel_name='account.move', relation='adjusting_entries__account_move', column1='adjusting_entry_move_id', column2='move_id')
    tax_cash_basis_origin_move_id = fields.Many2one(comodel_name='account.move')
    tax_cash_basis_created_move_ids = fields.One2many(comodel_name='account.move', inverse_name='tax_cash_basis_origin_move_id')
    auto_post_origin_id = fields.Many2one(comodel_name='account.move')
    suitable_journal_ids = fields.Many2many('account.journal', compute='_compute_suitable_journal_ids')
    audit_trail_message_ids = fields.One2many('mail.message', 'res_id')
    invoice_line_ids = fields.One2many('account.move.line', 'move_id')
    invoice_payment_term_id = fields.Many2one(comodel_name='account.payment.term', compute='_compute_invoice_payment_term_id', store=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', compute='_compute_fiscal_position_id', store=True)
    reversed_entry_id = fields.Many2one(comodel_name='account.move')
    reversal_move_ids = fields.One2many('account.move', 'reversed_entry_id')
    invoice_vendor_bill_id = fields.Many2one('account.move', store=False)
    invoice_user_id = fields.Many2one(comodel_name='res.users', compute='_compute_invoice_default_sale_person', store=True)
    invoice_incoterm_id = fields.Many2one(comodel_name='account.incoterms', compute='_compute_incoterm', store=True)
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
    journal_group_id = fields.Many2one(comodel_name='account.journal.group', store=False)
    account_id = fields.Many2one(comodel_name='account.account', compute='_compute_account_id', store=True)
    search_account_id = fields.Many2one('account.account', store=False)
    payment_id = fields.Many2one(comodel_name='account.payment', related='move_id.origin_payment_id', store=True)
    statement_line_id = fields.Many2one(comodel_name='account.bank.statement.line', related='move_id.statement_line_id', store=True)
    tax_ids = fields.Many2many(comodel_name='account.tax', compute='_compute_tax_ids', store=True)
    group_tax_id = fields.Many2one(comodel_name='account.tax')
    tax_line_id = fields.Many2one(comodel_name='account.tax', related='tax_repartition_line_id.tax_id', store=True)
    reconciled_lines_ids = fields.Many2many(comodel_name='account.move.line', compute='_compute_reconciled_lines_ids')
    reconciled_lines_excluding_exchange_diff_ids = fields.Many2many(comodel_name='account.move.line', compute='_compute_reconciled_lines_excluding_exchange_diff_ids')
    parent_id = fields.Many2one('account.move.line', compute='_compute_parent_id')
    product_id = fields.Many2one(comodel_name='product.product')
    analytic_line_ids = fields.One2many(comodel_name='account.analytic.line', inverse_name='move_line_id')
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
    _description = "Payments"
    _order = "date desc, name desc"
    _check_company_auto = True
    move_id = fields.Many2one(comodel_name='account.move')
    journal_id = fields.Many2one(comodel_name='account.journal', compute='_compute_journal_id', store=True)
    paired_internal_transfer_payment_id = fields.Many2one('account.payment')
    available_journal_ids = fields.Many2many(comodel_name='account.journal', compute='_compute_available_journal_ids')
    outstanding_account_id = fields.Many2one(comodel_name='account.account', store=True, compute='_compute_outstanding_account_id')
    destination_account_id = fields.Many2one(comodel_name='account.account', store=True, compute='_compute_destination_account_id')
    invoice_ids = fields.Many2many(comodel_name='account.move', relation='account_move__account_payment', column1='payment_id', column2='invoice_id')
    reconciled_invoice_ids = fields.Many2many('account.move', compute='_compute_stat_buttons_from_reconciliation')
    reconciled_bill_ids = fields.Many2many('account.move', compute='_compute_stat_buttons_from_reconciliation')
    reconciled_statement_line_ids = fields.Many2many(comodel_name='account.bank.statement.line', compute='_compute_stat_buttons_from_reconciliation')
    duplicate_payment_ids = fields.Many2many(comodel_name='account.payment', compute='_compute_duplicate_payment_ids')
    _check_amount_not_negative = models.Constraint(
        'CHECK(amount >= 0.0)',
        'The payment amount cannot be negative.')
    _journal_id_company_id_idx = models.Index("(journal_id, company_id)")
    _unmatched_idx = models.Index("(journal_id, company_id) WHERE is_matched IS NOT TRUE")
    # Shrunk non computed fields: date, move_id, is_sent, paired_internal_transfer_payment_id, payment_method_id, amount, payment_type, partner_type, memo, payment_reference, company_currency_id, partner_id, invoice_ids, payment_method_code, need_cancel_request, country_code, attachment_ids
    # Shrunk computed_fields: name (_compute_name), journal_id (_compute_journal_id), company_id (_compute_company_id), state (_compute_state), is_reconciled (_compute_reconciliation_status), is_matched (_compute_reconciliation_status), available_partner_bank_ids (_compute_available_partner_bank_ids), partner_bank_id (_compute_partner_bank_id), qr_code (_compute_qr_code), payment_method_line_id (_compute_payment_method_line_id), available_payment_method_line_ids (_compute_payment_method_line_fields), available_journal_ids (_compute_available_journal_ids), currency_id (_compute_currency_id), outstanding_account_id (_compute_outstanding_account_id), destination_account_id (_compute_destination_account_id), reconciled_invoice_ids (_compute_stat_buttons_from_reconciliation), reconciled_invoices_count (_compute_stat_buttons_from_reconciliation), reconciled_invoices_type (_compute_stat_buttons_from_reconciliation), reconciled_bill_ids (_compute_stat_buttons_from_reconciliation), reconciled_bills_count (_compute_stat_buttons_from_reconciliation), reconciled_statement_line_ids (_compute_stat_buttons_from_reconciliation), reconciled_statement_lines_count (_compute_stat_buttons_from_reconciliation), payment_receipt_title (_compute_payment_receipt_title), show_partner_bank_account (_compute_show_require_partner_bank), require_partner_bank_account (_compute_show_require_partner_bank), amount_signed (_compute_amount_signed), amount_company_currency_signed (_compute_amount_company_currency_signed), duplicate_payment_ids (_compute_duplicate_payment_ids)


# FILEPATH: odoo/addons/account/models/account_payment.py (lines 1242-1245)
class AccountMove(models.Model):
    _inherit = 'account.move'
    payment_ids = fields.One2many('account.payment', 'move_id')
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
    cash_basis_transition_account_id = fields.Many2one(comodel_name='account.account')
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
    # Shrunk non computed fields: is_invoice_report


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
    account_audit_log_move_id = fields.Many2one(comodel_name='account.move', compute="_compute_account_audit_log_move_id")
    account_audit_log_account_id = fields.Many2one(comodel_name='account.account', compute="_compute_account_audit_log_account_id")
    account_audit_log_tax_id = fields.Many2one(comodel_name='account.tax', compute="_compute_account_audit_log_tax_id")
    # Shrunk computed_fields: account_audit_log_preview (_compute_account_audit_log_preview), account_audit_log_move_id (_compute_account_audit_log_move_id), account_audit_log_partner_id (_compute_account_audit_log_partner_id), account_audit_log_account_id (_compute_account_audit_log_account_id), account_audit_log_tax_id (_compute_account_audit_log_tax_id), account_audit_log_company_id (_compute_account_audit_log_company_id), account_audit_log_restricted (_compute_account_audit_log_restricted)


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
    property_account_income_id = fields.Many2one('account.account')
    property_account_expense_id = fields.Many2one('account.account')
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
    _description = "Automatic sequence"
    _sequence_field = "name"
    _sequence_date_field = "date"
    _sequence_index = False
    prefix = r'(?P<prefix1>.*?)'
    prefix2 = r'(?P<prefix2>\D)'
    prefix3 = r'(?P<prefix3>\D+?)'
    seq = r'(?P<seq>\d*)'
    month = r'(?P<month>(0[1-9]|1[0-2]))'
    year = r'(?P<year>((?<=\D)|(?<=^))((19|20|21)\d{2}|(\d{2}(?=\D))))'
    year_end = r'(?P<year_end>((?<=\D)|(?<=^))((19|20|21)\d{2}|(\d{2}(?=\D))))'
    suffix = r'(?P<suffix>\D*?)'
    _sequence_year_range_monthly_regex = fr'^{prefix}{year}{prefix2}{year_end}(?P<prefix3>\D){month}(?P<prefix4>\D+?){seq}{suffix}$'
    _sequence_year_range_regex = fr'^(?:{prefix}{year}{prefix2}{year_end}{prefix3})?{seq}{suffix}$'
    _sequence_monthly_regex = fr'^{prefix}{year}(?P<prefix2>\D*?){month}{prefix3}{seq}{suffix}$'
    _sequence_yearly_regex = fr'^{prefix}(?P<year>((?<=\D)|(?<=^))((19|20|21)?\d{{2}}))(?P<prefix2>\D+?){seq}{suffix}$'
    _sequence_fixed_regex = fr'^{prefix}(?P<seq>\d{{0,9}}){suffix}$'
    # Shrunk computed_fields: sequence_prefix (_compute_split_sequence), sequence_number (_compute_split_sequence)


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
    _description = 'Analytic Account'
    _order = 'plan_id, name asc'
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of
    _rec_names_search = ['name', 'code']
    plan_id = fields.Many2one('account.analytic.plan')
    root_plan_id = fields.Many2one('account.analytic.plan', related="plan_id.root_id", store=True)
    line_ids = fields.One2many('account.analytic.line', 'auto_account_id')
    # Shrunk non computed fields: name, code, active, plan_id, root_plan_id, color, line_ids, company_id, partner_id, currency_id
    # Shrunk computed_fields: balance (_compute_debit_credit_balance), debit (_compute_debit_credit_balance), credit (_compute_debit_credit_balance)


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
    _description = 'Analytic Line'
    _order = 'date desc, id desc'
    _check_company_auto = True
    user_id = fields.Many2one('res.users')
    # Shrunk non computed fields: name, date, amount, unit_amount, product_uom_id, partner_id, user_id, company_id, currency_id, category, fiscal_year_search, analytic_precision
    # Shrunk computed_fields: analytic_distribution (_compute_analytic_distribution)


# FILEPATH: odoo/addons/analytic/models/analytic_mixin.py
class AnalyticMixin(models.AbstractModel):
    _name = 'analytic.mixin'
    _description = 'Analytic Mixin'
    distribution_analytic_account_ids = fields.Many2many(comodel_name='account.analytic.account', compute='_compute_distribution_analytic_account_ids')
    # Shrunk non computed fields: analytic_precision
    # Shrunk computed_fields: analytic_distribution (_compute_analytic_distribution), distribution_analytic_account_ids (_compute_distribution_analytic_account_ids)


# FILEPATH: odoo/addons/analytic/models/analytic_plan.py (lines 14-390)
class AccountAnalyticPlan(models.Model):
    _name = 'account.analytic.plan'
    _description = 'Analytic Plans'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'sequence asc, id'
    parent_id = fields.Many2one('account.analytic.plan')
    root_id = fields.Many2one('account.analytic.plan', compute='_compute_root_id')
    children_ids = fields.One2many('account.analytic.plan', 'parent_id')
    account_ids = fields.One2many('account.analytic.account', 'plan_id')
    # Shrunk non computed fields: name, description, parent_id, parent_path, children_ids, account_ids, color, sequence, default_applicability, applicability_ids
    # Shrunk computed_fields: root_id (_compute_root_id), children_count (_compute_children_count), complete_name (_compute_complete_name), account_count (_compute_analytic_account_count), all_account_count (_compute_all_analytic_account_count)


# FILEPATH: odoo/addons/analytic/models/analytic_plan.py (lines 393-430)
class AccountAnalyticApplicability(models.Model):
    _name = 'account.analytic.applicability'


# FILEPATH: odoo/addons/analytic/models/ir_config_parameter.py
class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'


# FILEPATH: odoo/addons/analytic/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


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

{
    'name': 'Purchase',
    'version': '1.2',
    'category': 'Supply Chain/Purchase',
    'sequence': 35,
    'summary': 'Purchase orders, tenders and agreements',
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['account'],
    'data': [
        'security/purchase_security.xml',
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
        'data/purchase_tour.xml',
    ],
    'demo': [
        'data/purchase_demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'purchase/static/src/components/**/*',
            'purchase/static/src/product_catalog/**/*',
            'purchase/static/src/toaster_button/*',
            'purchase/static/src/views/*.js',
            'purchase/static/src/js/tours/purchase.js',
            'purchase/static/src/js/tours/purchase_steps.js',
            'purchase/static/src/**/*.xml',
            'purchase/static/src/**/*.scss',
        ],
        'web.assets_frontend': [
            'purchase/static/src/interactions/**/*',
            'purchase/static/src/scss/purchase_portal.scss',
        ],
        'web.assets_tests': [
            'purchase/static/tests/tours/**/*',
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}


# FILEPATH: odoo/addons/purchase/models/account_invoice.py (lines 16-518)
_logger = logging.getLogger(__name__)
TOLERANCE = 0.02
class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_vendor_bill_id = fields.Many2one('purchase.bill.union', store=False, readonly=False,
        string='Auto-complete',
        help="Auto-complete from a previous bill, refund, or purchase order.")
    purchase_id = fields.Many2one('purchase.order', store=False, readonly=False,
        string='Purchase Order',
        help="Auto-complete from a past purchase order.")
    purchase_order_count = fields.Integer(compute="_compute_origin_po_count", string='Purchase Order Count')
    purchase_order_name = fields.Char(compute='_compute_purchase_order_name')
    is_purchase_matched = fields.Boolean(compute='_compute_is_purchase_matched')  # 0: PO not required or partially linked. 1: All lines linked
    purchase_warning_text = fields.Text(
        "Purchase Warning",
        help="Internal warning for the partner or the products as set by the user.",
        compute='_compute_purchase_warning_text')

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        r''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        has_invoice_lines = bool(self.invoice_line_ids.filtered(lambda x: x.display_type not in ('line_section', 'line_subsection', 'line_note')))
        new_currency_id = self.currency_id if has_invoice_lines else invoice_vals.get('currency_id')
        del invoice_vals['company_id']  # avoid recomputing the currency
        if self.move_type == invoice_vals['move_type']:
            del invoice_vals['move_type'] # no need to be updated if it's same value, to avoid recomputes
        self.update(invoice_vals)
        self.currency_id = new_currency_id

        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id')
        self._add_purchase_order_lines(po_lines)

        # Compute invoice_origin.
        origins = set(self.invoice_line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Copy company_id (only changes if the id is of a child company (branch))
        if self.company_id != self.purchase_id.company_id:
            self.company_id = self.purchase_id.company_id

        self.purchase_id = False

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()

        currency_id = (
                self.partner_id.property_purchase_currency_id
                or self.env['res.currency'].browse(self.env.context.get("default_currency_id"))
                or self.currency_id
        )

        if self.partner_id and self.move_type in ['in_invoice', 'in_refund'] and self.currency_id != currency_id:
            if not self.env.context.get('default_journal_id'):
                journal_domain = [
                    *self.env['account.journal']._check_company_domain(self.company_id),
                    ('type', '=', 'purchase'),
                    ('currency_id', '=', currency_id.id),
                ]
                default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                if default_journal_id:
                    self.journal_id = default_journal_id

            self.currency_id = currency_id

        return res

    @api.depends('line_ids.purchase_line_id')
    def _compute_is_purchase_matched(self):
        for move in self:
            if any(il.display_type == 'product' and not bool(il.purchase_line_id) for il in move.invoice_line_ids):
                move.is_purchase_matched = False
                continue
            move.is_purchase_matched = True

    @api.depends('line_ids.purchase_line_id')
    def _compute_origin_po_count(self):
        for move in self:
            move.purchase_order_count = len(move.line_ids.purchase_line_id.order_id)

    @api.depends('purchase_order_count')
    def _compute_purchase_order_name(self):
        for move in self:
            if move.purchase_order_count == 1:
                move.purchase_order_name = move.invoice_line_ids.purchase_order_id.display_name
            else:
                move.purchase_order_name = False

    @api.depends('partner_id.name', 'partner_id.purchase_warn_msg', 'invoice_line_ids.product_id.purchase_line_warn_msg', 'invoice_line_ids.product_id.display_name')
    def _compute_purchase_warning_text(self):
        if not self.env.user.has_group('purchase.group_warning_purchase'):
            self.purchase_warning_text = ''
            return
        for move in self:
            if move.move_type != 'in_invoice':
                move.purchase_warning_text = ''
                continue
            warnings = OrderedSet()
            if partner_msg := move.partner_id.purchase_warn_msg:
                warnings.add((move.partner_id.name or move.partner_id.display_name) + ' - ' + partner_msg)
            if partner_parent_msg := move.partner_id.parent_id.purchase_warn_msg:
                parent = move.partner_id.parent_id
                warnings.add((parent.name or parent.display_name) + ' - ' + partner_parent_msg)
            for product in move.invoice_line_ids.product_id:
                if product_msg := product.purchase_line_warn_msg:
                    warnings.add(product.display_name + ' - ' + product_msg)
            move.purchase_warning_text = '\n'.join(warnings)

    def action_purchase_matching(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Purchase Matching"),
            'res_model': 'purchase.bill.line.match',
            'domain': [
                ('partner_id', 'in', (self.partner_id | self.partner_id.commercial_partner_id).ids),
                ('company_id', 'in', self.env.companies.ids),
                ('company_id', 'child_of', self.company_id.ids),
                ('account_move_id', 'in', [self.id, False]),
            ],
            'views': [(self.env.ref('purchase.purchase_bill_line_match_tree').id, 'list')],
        }

    def action_view_source_purchase_orders(self):
        self.ensure_one()
        source_orders = self.line_ids.purchase_line_id.order_id
        result = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('purchase.purchase_order_form', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.reversed_entry_id:
                continue
            purchases = move.line_ids.purchase_line_id.order_id
            if not purchases:
                continue
            refs = [purchase._get_html_link() for purchase in purchases]
            message = _("This vendor bill has been created from: ") + Markup(',').join(refs)
            move.message_post(body=message)
        return moves

    def write(self, vals):
        # OVERRIDE
        old_purchases = [move.mapped('line_ids.purchase_line_id.order_id') for move in self]
        res = super(AccountMove, self).write(vals)
        for i, move in enumerate(self):
            new_purchases = move.mapped('line_ids.purchase_line_id.order_id')
            if not new_purchases:
                continue
            diff_purchases = new_purchases - old_purchases[i]
            if diff_purchases:
                refs = [purchase._get_html_link() for purchase in diff_purchases]
                message = _("This vendor bill has been modified from: ") + Markup(',').join(refs)
                move.message_post(body=message)
        return res

    def _add_purchase_order_lines(self, purchase_order_lines):
        """ Creates new invoice lines from purchase order lines """
        self.ensure_one()
        new_line_ids = self.env['account.move.line']

        for po_line in purchase_order_lines:
            new_line_values = po_line._prepare_account_move_line(self)
            new_line_ids += self.env['account.move.line'].new(new_line_values)

        self.invoice_line_ids += new_line_ids

    def _find_matching_subset_po_lines(self, po_lines_with_amount, goal_total, timeout):
        """Finds the purchase order lines adding up to the goal amount.

        The problem of finding the subset of `po_lines_with_amount` which sums up to `goal_total` reduces to
        the 0-1 Knapsack problem. The dynamic programming approach to solve this problem is most of the time slower
        than this because identical sub-problems don't arise often enough. It returns the list of purchase order lines
        which sum up to `goal_total` or an empty list if multiple or no solutions were found.

        :param po_lines_with_amount: a dict (str: float|recordset) containing:
            * line: an `purchase.order.line`
            * amount_to_invoice: the remaining amount to be invoiced of the line
        :param goal_total: the total amount to match with a subset of purchase order lines
        :param timeout: the max time the line matching algorithm can take before timing out
        :return: list of `purchase.order.line` whose remaining sum matches `goal_total`
        """
        def find_matching_subset_po_lines(lines, goal):
            if time.time() - start_time > timeout:
                raise TimeoutError
            solutions = []
            for i, line in enumerate(lines):
                if line['amount_to_invoice'] < goal - TOLERANCE:
                    # The amount to invoice of the current purchase order line is less than the amount we still need on
                    # the vendor bill.
                    # We try finding purchase order lines that match the remaining vendor bill amount minus the amount
                    # to invoice of the current purchase order line. We only look in the purchase order lines that we
                    # haven't passed yet.
                    sub_solutions = find_matching_subset_po_lines(lines[i + 1:], goal - line['amount_to_invoice'])
                    # We add all possible sub-solutions' purchase order lines in a tuple together with our current
                    # purchase order line.
                    solutions.extend((line['line'], *solution) for solution in sub_solutions)
                elif goal - TOLERANCE <= line['amount_to_invoice'] <= goal + TOLERANCE:
                    # The amount to invoice of the current purchase order line matches the remaining vendor bill amount.
                    # We add this purchase order line to our list of solutions.
                    solutions.append([line['line']])
                if len(solutions) > 1:
                    # More than one solution was found. We can't know for sure which is the correct one, so we don't
                    # return any solution.
                    return []
            return solutions
        start_time = time.time()
        try:
            subsets = find_matching_subset_po_lines(
                sorted(po_lines_with_amount, key=lambda line: line['amount_to_invoice'], reverse=True),
                goal_total
            )
            return subsets[0] if subsets else []
        except TimeoutError:
            _logger.warning("Timed out during search of a matching subset of purchase order lines")
            return []

    def _find_matching_po_and_inv_lines(self, po_lines, inv_lines, timeout):
        """Finds purchase order lines that match some of the invoice lines.

        We try to find a purchase order line for every invoice line matching on the unit price and having at least
        the same quantity to invoice.

        :param po_lines: list of purchase order lines that can be matched
        :param inv_lines: list of invoice lines to be matched
        :param timeout: how long this function can run before we consider it too long
        :return: a tuple (list, list) containing:
            * matched 'purchase.order.line'
            * tuple of purchase order line ids and their matched 'account.move.line'
        """
        # Sort the invoice lines by unit price and quantity to speed up matching
        invoice_lines = sorted(inv_lines, key=lambda line: (line.price_unit, line.quantity), reverse=True)
        # Sort the purchase order lines by unit price and remaining quantity to speed up matching
        purchase_lines = sorted(
            po_lines,
            key=lambda line: (line.price_unit, line.product_qty - line.qty_invoiced),
            reverse=True
        )
        matched_po_lines = []
        matched_inv_lines = []
        try:
            start_time = time.time()
            for invoice_line in invoice_lines:
                # There are no purchase order lines left. We are done matching.
                if not purchase_lines:
                    break
                # A dict of purchase lines mapping to a diff score for the name
                purchase_line_candidates = {}
                for purchase_line in purchase_lines:
                    if time.time() - start_time > timeout:
                        raise TimeoutError

                    # The lists are sorted by unit price descendingly.
                    # When the unit price of the purchase line is lower than the unit price of the invoice line,
                    # we cannot get a match anymore.
                    if purchase_line.price_unit < invoice_line.price_unit:
                        break

                    if (invoice_line.price_unit == purchase_line.price_unit
                            and invoice_line.quantity <= purchase_line.product_qty - purchase_line.qty_invoiced):
                        # The current purchase line is a possible match for the current invoice line.
                        # We calculate the name match ratio and continue with other possible matches.
                        #
                        # We could match on more fields coming from an EDI invoice, but that requires extending the
                        # account.move.line model with the extra matching fields and extending the EDI extraction
                        # logic to fill these new fields.
                        purchase_line_candidates[purchase_line] = difflib.SequenceMatcher(
                            None, invoice_line.name, purchase_line.name).ratio()

                if len(purchase_line_candidates) > 0:
                    # We take the best match based on the name.
                    purchase_line_match = max(purchase_line_candidates, key=purchase_line_candidates.get)
                    if purchase_line_match:
                        # We found a match. We remove the purchase order line so it does not get matched twice.
                        purchase_lines.remove(purchase_line_match)
                        matched_po_lines.append(purchase_line_match)
                        matched_inv_lines.append((purchase_line_match.id, invoice_line))

            return (matched_po_lines, matched_inv_lines)

        except TimeoutError:
            _logger.warning('Timed out during search of matching purchase order lines')
            return ([], [])

    def _set_purchase_orders(self, purchase_orders, force_write=True):
        """Link the given purchase orders to this vendor bill and add their lines as invoice lines.

        :param purchase_orders: a list of purchase orders to be linked to this vendor bill
        :param force_write: whether to delete all existing invoice lines before adding the vendor bill lines
        """
        with self.env.cr.savepoint():
            with self._get_edi_creation() as invoice:
                if force_write and invoice.line_ids:
                    invoice.invoice_line_ids = [Command.clear()]
                for purchase_order in purchase_orders:
                    invoice.invoice_line_ids = [Command.create({
                        'display_type': 'line_section',
                        'name': _('From %s', purchase_order.name)
                    })]
                    invoice.purchase_id = purchase_order
                    invoice._onchange_purchase_auto_complete()

    def _match_purchase_orders(self, po_references, partner_id, amount_total, from_ocr, timeout):
        """Tries to match open purchase order lines with this invoice given the information we have.

        :param po_references: a list of potential purchase order references/names
        :param partner_id: the vendor id inferred from the vendor bill
        :param amount_total: the total amount of the vendor bill
        :param from_ocr: indicates whether this vendor bill was created from an OCR scan (less reliable)
        :param timeout: the max time the line matching algorithm can take before timing out
        :return: tuple (str, recordset, dict) containing:
            * the match method:
                * `total_match`: purchase order reference(s) and total amounts match perfectly
                * `subset_total_match`: a subset of the referenced purchase orders' lines matches the total amount of
                    this invoice (OCR only)
                * `po_match`: only the purchase order reference matches (OCR only)
                * `subset_match`: a subset of the referenced purchase orders' lines matches a subset of the invoice
                    lines based on unit prices (EDI only)
                * `no_match`: no result found
            * recordset of `purchase.order.line` containing purchase order lines matched with an invoice line
            * list of tuple containing every `purchase.order.line` id and its related `account.move.line`
        """

        common_domain = [
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'purchase'),
            ('invoice_status', 'in', ('to invoice', 'no'))
        ]

        matching_purchase_orders = self.env['purchase.order']

        # We have purchase order references in our vendor bill and a total amount.
        if po_references and amount_total:
            # We first try looking for purchase orders whose names match one of the purchase order references in the
            # vendor bill.
            matching_purchase_orders |= self.env['purchase.order'].search(
                common_domain + [('name', 'in', po_references)])

            if not matching_purchase_orders:
                # If not found, we try looking for purchase orders whose `partner_ref` field matches one of the
                # purchase order references in the vendor bill.
                matching_purchase_orders |= self.env['purchase.order'].search(
                    common_domain + [('partner_ref', 'in', po_references)])

            if matching_purchase_orders:
                # We found matching purchase orders and are extracting all purchase order lines together with their
                # amounts still to be invoiced.
                po_lines = [line for line in matching_purchase_orders.order_line if line.product_qty]
                po_lines_with_amount = [{
                    'line': line,
                    'amount_to_invoice': (1 - line.qty_invoiced / line.product_qty) * line.price_total,
                } for line in po_lines]

                # If the sum of all remaining amounts to be invoiced for these purchase orders' lines is within a
                # tolerance from the vendor bill total, we have a total match. We return all purchase order lines
                # summing up to this vendor bill's total (could be from multiple purchase orders).
                if (amount_total - TOLERANCE
                        < sum(line['amount_to_invoice'] for line in po_lines_with_amount)
                        < amount_total + TOLERANCE):
                    return 'total_match', matching_purchase_orders.order_line, None

                elif from_ocr:
                    # The invoice comes from an OCR scan.
                    # We try to match the invoice total with purchase order lines.
                    matching_po_lines = self._find_matching_subset_po_lines(
                        po_lines_with_amount, amount_total, timeout)
                    if matching_po_lines:
                        return 'subset_total_match', self.env['purchase.order.line'].union(*matching_po_lines), None
                    else:
                        # We did not find a match for the invoice total.
                        # We return all purchase order lines based only on the purchase order reference(s) in the
                        # vendor bill.
                        return 'po_match', matching_purchase_orders.order_line, None

                else:
                    # We have an invoice from an EDI document, so we try to match individual invoice lines with
                    # individual purchase order lines from referenced purchase orders.
                    matching_po_lines, matching_inv_lines = self._find_matching_po_and_inv_lines(
                        po_lines, self.invoice_line_ids, timeout)

                    if matching_po_lines:
                        # We found a subset of purchase order lines that match a subset of the vendor bill lines.
                        # We return the matching purchase order lines and vendor bill lines.
                        return ('subset_match',
                                self.env['purchase.order.line'].union(*matching_po_lines),
                                matching_inv_lines)

        # As a last resort we try matching a purchase order by vendor and total amount.
        if partner_id and amount_total:
            purchase_id_domain = common_domain + [
                ('partner_id', 'child_of', [partner_id]),
                ('amount_total', '>=', amount_total - TOLERANCE),
                ('amount_total', '<=', amount_total + TOLERANCE)
            ]
            matching_purchase_orders = self.env['purchase.order'].search(purchase_id_domain)
            if len(matching_purchase_orders) == 1:
                # We found exactly one match on vendor and total amount (within tolerance).
                # We return all purchase order lines of the purchase order whose total amount matched our vendor bill.
                return 'total_match', matching_purchase_orders.order_line, None

        # We couldn't find anything, so we return no lines.
        return ('no_match', matching_purchase_orders.order_line, None)

    def _find_and_set_purchase_orders(self, po_references, partner_id, amount_total, from_ocr=False, timeout=10):
        """Finds related purchase orders that (partially) match the vendor bill and links the matching lines on this
        vendor bill.

        :param po_references: a list of potential purchase order references/names
        :param partner_id: the vendor id matched on the vendor bill
        :param amount_total: the total amount of the vendor bill
        :param from_ocr: indicates whether this vendor bill was created from an OCR scan (less reliable)
        :param timeout: the max time the line matching algorithm can take before timing out
        """
        self.ensure_one()

        method, matched_po_lines, matched_inv_lines = self._match_purchase_orders(
            po_references, partner_id, amount_total, from_ocr, timeout
        )

        if method in ('total_match', 'po_match'):
            # The purchase order reference(s) and total amounts match perfectly or there is only one purchase order
            # reference that matches with an OCR invoice. We replace the invoice lines with the purchase order lines.
            self._set_purchase_orders(matched_po_lines.order_id, force_write=True)

        elif method == 'subset_total_match':
            # A subset of the referenced purchase order lines matches the total amount of this invoice.
            # We keep the invoice lines, but add all the lines from the partially matched purchase orders:
            #   * "naively" matched purchase order lines keep their quantity
            #   * unmatched purchase order lines are added with their quantity set to 0
            self._set_purchase_orders(matched_po_lines.order_id, force_write=False)

            with self._get_edi_creation() as invoice:
                unmatched_lines = invoice.invoice_line_ids.filtered(
                    lambda l: l.purchase_line_id and l.purchase_line_id not in matched_po_lines)
                invoice.invoice_line_ids = [Command.update(line.id, {'quantity': 0}) for line in unmatched_lines]

        elif method == 'subset_match':
            # A subset of the referenced purchase order lines matches a subset of the invoice lines.
            # We add the purchase order lines, but adjust the quantity to the quantities in the invoice.
            # The original invoice lines that correspond with a purchase order line are removed.
            self._set_purchase_orders(matched_po_lines.order_id, force_write=False)

            with self._get_edi_creation() as invoice:
                unmatched_lines = invoice.invoice_line_ids.filtered(
                    lambda l: l.purchase_line_id and l.purchase_line_id not in matched_po_lines)
                invoice.invoice_line_ids = [Command.delete(line.id) for line in unmatched_lines]

                # We remove the original matched invoice lines and apply their quantities and taxes to the matched
                # purchase order lines.
                inv_and_po_lines = list(map(lambda line: (
                        invoice.invoice_line_ids.filtered(
                            lambda l: l.purchase_line_id and l.purchase_line_id.id == line[0]),
                        invoice.invoice_line_ids.filtered(
                            lambda l: l in line[1])
                    ),
                    matched_inv_lines
                ))
                invoice.invoice_line_ids = [
                    Command.update(po_line.id, {'quantity': inv_line.quantity, 'tax_ids': inv_line.tax_ids})
                    for po_line, inv_line in inv_and_po_lines
                ]
                invoice.invoice_line_ids = [Command.delete(inv_line.id) for dummy, inv_line in inv_and_po_lines]

                # If there are lines left not linked to a purchase order, we add a header
                unmatched_lines = invoice.invoice_line_ids.filtered(lambda l: not l.purchase_line_id)
                if len(unmatched_lines) > 0:
                    invoice.invoice_line_ids = [Command.create({
                        'display_type': 'line_section',
                        'name': _('From Electronic Document'),
                        'sequence': -1,
                    })]

        if not any(line.purchase_order_id for line in self.line_ids):
            self.invoice_origin = False


# FILEPATH: odoo/addons/purchase/models/account_invoice.py (lines 521-558)
class AccountMoveLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.move.line'

    is_downpayment = fields.Boolean()
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', ondelete='set null', index='btree_not_null', copy=False)
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', related='purchase_line_id.order_id', readonly=True)
    purchase_line_warn_msg = fields.Text(compute='_compute_purchase_line_warn_msg')

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'purchase_line_id' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['purchase_line_id'] = self.purchase_line_id.id

    def _prepare_line_values_for_purchase(self):
        return [
            {
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom_id': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            for line in self
        ]

    def _related_analytic_distribution(self):
        # EXTENDS 'account'
        vals = super()._related_analytic_distribution()
        if self.purchase_line_id and not self.analytic_distribution:
            vals |= self.purchase_line_id.analytic_distribution or {}
        return vals

    @api.depends('product_id.purchase_line_warn_msg')
    def _compute_purchase_line_warn_msg(self):
        has_group = self.env.user.has_group('purchase.group_warning_purchase')
        for line in self:
            line.purchase_line_warn_msg = line.product_id.purchase_line_warn_msg if has_group else ""


# FILEPATH: odoo/addons/purchase/models/account_tax.py
class AccountTax(models.Model):
    _inherit = "account.tax"

    def _hook_compute_is_used(self, taxes_to_compute):
        # OVERRIDE in order to fetch taxes used in purchase

        used_taxes = super()._hook_compute_is_used(taxes_to_compute)
        taxes_to_compute -= used_taxes

        if taxes_to_compute:
            self.env['purchase.order.line'].flush_model(['tax_ids'])
            self.env.cr.execute("""
                SELECT id
                FROM account_tax
                WHERE EXISTS(
                    SELECT 1
                    FROM account_tax_purchase_order_line_rel AS pur
                    WHERE account_tax_id IN %s
                    AND account_tax.id = pur.account_tax_id
                )
            """, [tuple(taxes_to_compute)])

            used_taxes.update([tax[0] for tax in self.env.cr.fetchall()])

        return used_taxes


# FILEPATH: odoo/addons/purchase/models/analytic_account.py
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    purchase_order_count = fields.Integer("Purchase Order Count", compute='_compute_purchase_order_count')

    @api.depends('line_ids')
    def _compute_purchase_order_count(self):
        for account in self:
            account.purchase_order_count = self.env['purchase.order'].search_count([
                ('order_line.invoice_lines.analytic_line_ids.account_id', 'in', account.ids)
            ])

    def action_view_purchase_orders(self):
        self.ensure_one()
        purchase_orders = self.env['purchase.order'].search([
            ('order_line.invoice_lines.analytic_line_ids.account_id', '=', self.id)
        ])
        result = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "domain": [['id', 'in', purchase_orders.ids]],
            "name": _("Purchase Orders"),
            'view_mode': 'list,form',
        }
        if len(purchase_orders) == 1:
            result['view_mode'] = 'form'
            result['res_id'] = purchase_orders.id
        return result


# FILEPATH: odoo/addons/purchase/models/analytic_applicability.py
class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'
    _description = "Analytic Plan's Applicabilities"
    business_domain = fields.Selection(
        selection_add=[
            ('purchase_order', 'Purchase Order'),
        ],
        ondelete={'purchase_order': 'cascade'},
    )


# FILEPATH: odoo/addons/purchase/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        # EXTENDS base
        collected_streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)

        if (
            collected_streams
            and res_ids
            and len(res_ids) == 1
            and self._is_purchase_order_report(report_ref)
        ):
            purchase_order = self.env['purchase.order'].browse(res_ids)
            builders = purchase_order._get_edi_builders()

            if len(builders) == 0:
                return collected_streams

            # Read pdf content.
            pdf_stream = collected_streams[purchase_order.id]['stream']
            pdf_content = pdf_stream.getvalue()
            reader_buffer = io.BytesIO(pdf_content)
            reader = OdooPdfFileReader(reader_buffer, strict=False)
            writer = OdooPdfFileWriter()
            writer.cloneReaderDocumentRoot(reader)

            # Generate and attach EDI documents from each builder
            for builder in builders:
                xml_content = builder._export_order(purchase_order)

                writer.addAttachment(
                    builder._export_invoice_filename(purchase_order),  # works even if it's a SO or PO
                    xml_content,
                    subtype='text/xml'
                )

            # Replace the current content.
            pdf_stream.close()
            new_pdf_stream = io.BytesIO()
            writer.write(new_pdf_stream)
            collected_streams[purchase_order.id]['stream'] = new_pdf_stream

        return collected_streams

    def _is_purchase_order_report(self, report_ref):
        return self._get_report(report_ref).report_name in (
            'purchase.report_purchasequotation',
            'purchase.report_purchaseorder'
        )


# FILEPATH: odoo/addons/purchase/models/product.py (lines 10-55)
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchased_product_qty = fields.Float(compute='_compute_purchased_product_qty', string='Purchased', digits='Product Unit')
    purchase_method = fields.Selection([
        ('purchase', 'On ordered quantities'),
        ('receive', 'On received quantities'),
    ], string="Control Policy", compute='_compute_purchase_method', precompute=True, store=True, readonly=False,
        help="On ordered quantities: Control bills based on ordered quantities.\n"
            "On received quantities: Control bills based on received quantities.")
    purchase_line_warn_msg = fields.Text('Message for Purchase Order Line')

    @api.depends('type')
    def _compute_purchase_method(self):
        default_purchase_method = self.env['product.template'].default_get(['purchase_method']).get('purchase_method', 'receive')
        for product in self:
            if product.type == 'service':
                product.purchase_method = 'purchase'
            else:
                product.purchase_method = default_purchase_method

    def _compute_purchased_product_qty(self):
        for template in self.with_context(active_test=False):
            template.purchased_product_qty = template.uom_id.round(sum(p.purchased_product_qty for p in template.product_variant_ids))

    def _get_backend_root_menu_ids(self):
        return super()._get_backend_root_menu_ids() + [self.env.ref('purchase.menu_purchase_root').id]

    @api.model
    def get_import_templates(self):
        res = super(ProductTemplate, self).get_import_templates()
        if self.env.context.get('purchase_product_template'):
            return [{
                'label': _('Import Template for Products'),
                'template': '/purchase/static/xls/product_purchase.xls'
            }]
        return res

    def action_view_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_history")
        action['domain'] = ['&',
            ('state', '=', 'purchase'),
            ('product_id', 'in', self.with_context(active_test=False).product_variant_ids.ids)
        ]
        action['display_name'] = _("Purchase History for %s", self.display_name)
        return action


# FILEPATH: odoo/addons/purchase/models/product.py (lines 58-141)
class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchased_product_qty = fields.Float(compute='_compute_purchased_product_qty', string='Purchased',
        digits='Product Unit')

    is_in_purchase_order = fields.Boolean(
        compute='_compute_is_in_purchase_order',
        search='_search_is_in_purchase_order',
    )

    def _compute_purchased_product_qty(self):
        date_from = fields.Datetime.to_string(fields.Date.context_today(self) - relativedelta(years=1))
        domain = [
            ('order_id.state', '=', 'purchase'),
            ('product_id', 'in', self.ids),
            ('order_id.date_approve', '>=', date_from)
        ]
        order_lines = self.env['purchase.order.line']._read_group(domain, ['product_id'], ['product_uom_qty:sum'])
        purchased_data = {product.id: qty for product, qty in order_lines}
        for product in self:
            if not product.id:
                product.purchased_product_qty = 0.0
                continue
            product.purchased_product_qty = product.uom_id.round(purchased_data.get(product.id, 0))

    @api.depends_context('order_id')
    def _compute_is_in_purchase_order(self):
        order_id = self.env.context.get('order_id')
        if not order_id:
            self.is_in_purchase_order = False
            return

        read_group_data = self.env['purchase.order.line']._read_group(
            domain=[('order_id', '=', order_id)],
            groupby=['product_id'],
            aggregates=['__count'],
        )
        data = {product.id: count for product, count in read_group_data}
        for product in self:
            product.is_in_purchase_order = bool(data.get(product.id, 0))

    def _search_is_in_purchase_order(self, operator, value):
        if operator != 'in':
            return NotImplemented
        product_ids = self.env['purchase.order.line'].search([
            ('order_id', 'in', [self.env.context.get('order_id', '')]),
        ]).product_id.ids
        return [('id', 'in', product_ids)]

    def action_view_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_history")
        action['domain'] = ['&', ('state', '=', 'purchase'), ('product_id', 'in', self.ids)]
        action['display_name'] = _("Purchase History for %s", self.display_name)
        return action

    def _get_backend_root_menu_ids(self):
        return super()._get_backend_root_menu_ids() + [self.env.ref('purchase.menu_purchase_root').id]

    def _update_uom(self, to_uom_id):
        for uom, product, po_lines in self.env['purchase.order.line']._read_group(
            [('product_id', 'in', self.ids)],
            ['product_uom_id', 'product_id'],
            ['id:recordset'],
        ):
            if uom != product.product_tmpl_id.uom_id:
                raise UserError(_(
                    'As other units of measure (ex : %(problem_uom)s) '
                    'than %(uom)s have already been used for this product, the change of unit of measure can not be done.'
                    'If you want to change it, please archive the product and create a new one.',
                    problem_uom=uom.display_name, uom=product.product_tmpl_id.uom_id.display_name))
            po_lines.product_uom_id = to_uom_id
            po_lines.flush_recordset()

        return super()._update_uom(to_uom_id)

    def _trigger_uom_warning(self):
        res = super()._trigger_uom_warning()
        if res:
            return res
        po_lines = self.env['purchase.order.line'].sudo().search_count(
            [('product_id', 'in', self.ids)], limit=1
        )
        return bool(po_lines)


# FILEPATH: odoo/addons/purchase/models/product.py (lines 144-154)
class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id

    def _get_filtered_supplier(self, company_id, product_id, params=False):
        if params and 'order_id' in params and params['order_id'].company_id:
            company_id = params['order_id'].company_id
        return super()._get_filtered_supplier(company_id, product_id, params)


# FILEPATH: odoo/addons/purchase/models/purchase_bill_line_match.py
class PurchaseBillLineMatch(models.Model):
    _name = 'purchase.bill.line.match'
    _description = "Purchase Line and Vendor Bill line matching view"
    _auto = False
    _order = 'product_id, aml_id, pol_id'

    pol_id = fields.Many2one(comodel_name='purchase.order.line', readonly=True)
    aml_id = fields.Many2one(comodel_name='account.move.line', readonly=True)
    company_id = fields.Many2one(comodel_name='res.company', readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', readonly=True)
    product_id = fields.Many2one(comodel_name='product.product', readonly=True)
    line_qty = fields.Float(readonly=True)
    line_uom_id = fields.Many2one(comodel_name='uom.uom', readonly=True)
    qty_invoiced = fields.Float(readonly=True)
    qty_to_invoice = fields.Float('Qty to invoice', readonly=True)
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', readonly=True)
    account_move_id = fields.Many2one(comodel_name='account.move', readonly=True)
    line_amount_untaxed = fields.Monetary(readonly=True)
    currency_id = fields.Many2one(comodel_name='res.currency', readonly=True)
    state = fields.Char(readonly=True)

    product_uom_id = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id')
    product_uom_qty = fields.Float(compute='_compute_product_uom_qty', inverse='_inverse_product_uom_qty', readonly=False)
    product_uom_price = fields.Float(compute='_compute_product_uom_price', inverse='_inverse_product_uom_price', readonly=False)
    billed_amount_untaxed = fields.Monetary(compute='_compute_amount_untaxed_fields', currency_field='currency_id')
    purchase_amount_untaxed = fields.Monetary(compute='_compute_amount_untaxed_fields', currency_field='currency_id')
    reference = fields.Char(compute='_compute_reference')

    @api.onchange('product_uom_price')
    def _inverse_product_uom_price(self):
        for line in self:
            if line.aml_id:
                line.aml_id.price_unit = line.product_uom_price
            else:
                line.pol_id.price_unit = line.product_uom_price

    @api.onchange('product_uom_qty')
    def _inverse_product_uom_qty(self):
        for line in self:
            if line.aml_id:
                line.aml_id.quantity = line.product_uom_qty
            else:
                # on POL, setting product_qty will recompute price_unit to have the old value
                # this prevents the price to revert by saving the previous price and re-setting them again
                previous_price_unit = line.pol_id.price_unit
                line.pol_id.product_qty = line.product_uom_qty
                line.pol_id.price_unit = previous_price_unit

    def _compute_amount_untaxed_fields(self):
        for line in self:
            line.billed_amount_untaxed = line.line_amount_untaxed if line.account_move_id else False
            line.purchase_amount_untaxed = line.line_amount_untaxed if line.purchase_order_id else False

    def _compute_reference(self):
        for line in self:
            line.reference = line.purchase_order_id.display_name or line.account_move_id.display_name

    def _compute_display_name(self):
        for line in self:
            line.display_name = line.product_id.display_name or line.aml_id.name or line.pol_id.name

    def _compute_product_uom_qty(self):
        for line in self:
            line.product_uom_qty = line.line_uom_id._compute_quantity(line.line_qty, line.product_uom_id)

    @api.depends('aml_id.price_unit', 'pol_id.price_unit')
    def _compute_product_uom_price(self):
        for line in self:
            line.product_uom_price = line.aml_id.price_unit if line.aml_id else line.pol_id.price_unit

    @api.model
    def _select_po_line(self):
        return SQL("""
            SELECT pol.id,
                   pol.id as pol_id,
                   NULL as aml_id,
                   pol.company_id as company_id,
                   pol.partner_id as partner_id,
                   pol.product_id as product_id,
                   pol.product_qty as line_qty,
                   pol.product_uom_id as line_uom_id,
                   pol.qty_invoiced as qty_invoiced,
                   pol.qty_to_invoice as qty_to_invoice,
                   po.id as purchase_order_id,
                   NULL as account_move_id,
                   pol.price_subtotal as line_amount_untaxed,
                   po.currency_id as currency_id,
                   po.state as state
              FROM purchase_order_line pol
         LEFT JOIN purchase_order po ON pol.order_id = po.id
             WHERE po.state = 'purchase'
               AND (pol.product_qty > pol.qty_invoiced OR pol.qty_to_invoice != 0)
                OR ((pol.display_type = '' OR pol.display_type IS NULL) AND pol.is_downpayment AND pol.qty_invoiced > 0)
        """)

    @api.model
    def _select_am_line(self):
        return SQL("""
            SELECT -aml.id,
                   NULL as pol_id,
                   aml.id as aml_id,
                   aml.company_id as company_id,
                   am.partner_id as partner_id,
                   aml.product_id as product_id,
                   aml.quantity as line_qty,
                   aml.product_uom_id as line_uom_id,
                   NULL as qty_invoiced,
                   NULL as qty_to_invoice,
                   NULL as purchase_order_id,
                   am.id as account_move_id,
                   aml.amount_currency as line_amount_untaxed,
                   aml.currency_id as currency_id,
                   aml.parent_state as state
              FROM account_move_line aml
         LEFT JOIN account_move am on aml.move_id = am.id
             WHERE aml.display_type = 'product'
               AND am.move_type in ('in_invoice', 'in_refund')
               AND aml.parent_state in ('draft', 'posted')
               AND aml.purchase_line_id IS NULL
        """)

    @property
    def _table_query(self):
        return SQL("%s UNION ALL %s", self._select_po_line(), self._select_am_line())

    def action_open_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move' if self.account_move_id else 'purchase.order',
            'view_mode': 'form',
            'res_id': self.account_move_id.id if self.account_move_id else self.purchase_order_id.id,
        }

    @api.model
    def _action_create_bill_from_po_lines(self, partner, po_lines):
        """ Create a new vendor bill with the selected PO lines and returns an action to open it """
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': partner.id,
        })
        bill._add_purchase_order_lines(po_lines)
        return bill._get_records_action()

    def action_match_lines(self):
        if not self.pol_id:  # we need POL(s) to either match or create bill
            raise UserError(_("You must select at least one Purchase Order line to match or create bill."))
        if not self.aml_id:  # select POL(s) without AML -> create a draft bill with the POL(s)
            return self._action_create_bill_from_po_lines(self.partner_id, self.pol_id)

        pol_by_product = self.pol_id.grouped('product_id')
        aml_by_product = self.aml_id.grouped('product_id')
        residual_purchase_order_lines = self.pol_id
        residual_account_move_lines = self.aml_id

        # Match all matchable POL-AML lines and remove them from the residual group
        for product, po_line in pol_by_product.items():
            po_line = po_line[0]  # in case of multiple POL with same product, only match the first one
            matching_bill_lines = aml_by_product.get(product)
            if matching_bill_lines:
                matching_bill_lines.purchase_line_id = po_line.id
                residual_purchase_order_lines -= po_line
                residual_account_move_lines -= matching_bill_lines

        if len(residual_bill := self.aml_id.move_id) == 1:
            # Delete all unmatched selected AML
            if residual_account_move_lines:
                residual_account_move_lines.unlink()

            # Add all remaining POL to the residual bill
            residual_bill._add_purchase_order_lines(residual_purchase_order_lines)

    def action_add_to_po(self):
        if not self or not self.aml_id:
            raise UserError(_("Select Vendor Bill lines to add to a Purchase Order"))
        partner = self.mapped("partner_id.commercial_partner_id")
        if len(partner) > 1:
            raise UserError(_("Please select bill lines with the same vendor."))
        context = {
            'default_partner_id': partner.id,
            'dialog_size': 'medium',
            'has_products': bool(self.aml_id.product_id),
        }
        if len(self.purchase_order_id) > 1:
            raise UserError(_("Vendor Bill lines can only be added to one Purchase Order."))
        elif self.purchase_order_id:
            context['default_purchase_order_id'] = self.purchase_order_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': _("Add to Purchase Order"),
            'res_model': 'bill.to.po.wizard',
            'target': 'new',
            'views': [(self.env.ref('purchase.bill_to_po_wizard_form').id, 'form')],
            'context': context,
        }


# FILEPATH: odoo/addons/purchase/models/purchase_order.py
_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'account.document.import.mixin']
    _description = "Purchase Order"
    _rec_names_search = ['name', 'partner_ref']
    _order = 'priority desc, id desc'

    @api.depends('order_line.price_subtotal', 'company_id', 'currency_id')
    def _amount_all(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            order.amount_untaxed = tax_totals['base_amount_currency']
            order.amount_tax = tax_totals['tax_amount_currency']
            order.amount_total = tax_totals['total_amount_currency']
            order.amount_total_cc = tax_totals['total_amount']

    @api.depends('state', 'order_line.qty_to_invoice')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        for order in self:
            if order.state != 'purchase':
                order.invoice_status = 'no'
                continue

            if any(
                not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.invoice_status = 'to invoice'
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
                )
                and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    @api.depends('order_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('order_line.invoice_lines.move_id')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    name = fields.Char('Order Reference', required=True, index='trigram', copy=False, default='New')
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    origin = fields.Char('Source', copy=False,
        help="Reference of the document that generated this purchase order "
             "request (e.g. a sales order)")
    partner_ref = fields.Char('Vendor Reference', copy=False,
        help="Reference of the sales order or bid sent by the vendor. "
             "It's used to do the matching when you receive the "
             "products as this reference is usually written on the "
             "delivery order sent by your vendor.")
    date_order = fields.Datetime('Order Deadline', required=True, index=True, copy=False, default=fields.Datetime.now,
        help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.")
    date_approve = fields.Datetime('Confirmation Date', readonly=True, index=True, copy=False)
    partner_id = fields.Many2one(
        'res.partner', string='Vendor', required=True, change_default=True,
        tracking=True, check_company=True, index=True,
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    dest_address_id = fields.Many2one('res.partner', check_company=True, string='Dropship Address',
        help="Put an address if you want to deliver directly from the vendor to the customer. "
             "Otherwise, keep empty to deliver to your own company.")
    currency_id = fields.Many2one('res.currency', 'Currency',
        required=True,
        compute='_compute_currency_id',
        store=True,
        readonly=False,
        precompute=True,
    )
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    locked = fields.Boolean(
        help="Locked Purchase Orders cannot be modified.",
        default=False,
        copy=False,
        tracking=True)
    lock_confirmed_po = fields.Selection(related="company_id.po_lock")
    order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', copy=True)
    acknowledged = fields.Boolean(
        'Acknowledged', copy=False, tracking=True,
        help="It indicates that the vendor has acknowledged the receipt of the purchase order.")
    note = fields.Html('Terms and Conditions')

    partner_bill_count = fields.Integer(related='partner_id.supplier_invoice_count')
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no')
    date_planned = fields.Datetime(
        string='Expected Arrival', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")
    date_calendar_start = fields.Datetime(compute='_compute_date_calendar_start', readonly=True, store=True)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=True)
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    amount_total_cc = fields.Monetary(string="Total in currency", store=True, readonly=True, compute="_amount_all", currency_field="company_currency_id")

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position, when reading a purchase order with company != user.company_ids
        compute_sudo=True,
        help="Technical field to filter the available taxes depending on the fiscal country and fiscal position.")
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        string='Tax calculation rounding method', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")

    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product')
    user_id = fields.Many2one(
        'res.users', string='Buyer', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    company_currency_id = fields.Many2one(related="company_id.currency_id", string="Company Currency")
    country_code = fields.Char(related='company_id.account_fiscal_country_id.code', string="Country code")
    company_price_include = fields.Selection(related='company_id.account_price_include')
    currency_rate = fields.Float(
        string="Currency Rate",
        compute='_compute_currency_rate',
        digits=0,
        store=True,
        precompute=True,
    )
    duplicated_order_ids = fields.Many2many(comodel_name='purchase.order', compute='_compute_duplicated_order_ids')

    receipt_reminder_email = fields.Boolean('Receipt Reminder Email', compute='_compute_receipt_reminder_email', store=True, readonly=False)
    reminder_date_before_receipt = fields.Integer('Days Before Receipt', compute='_compute_receipt_reminder_email', store=True, readonly=False)

    is_late = fields.Boolean('Is Late', store=False, search='_search_is_late')
    show_comparison = fields.Boolean('Show Comparison', compute='_compute_show_comparison')

    purchase_warning_text = fields.Text(
        "Purchase Warning",
        help="Internal warning for the partner or the products as set by the user.",
        compute='_compute_purchase_warning_text')

    @api.constrains('company_id', 'order_line')
    def _check_order_line_company_id(self):
        for order in self:
            invalid_companies = order.order_line.product_id.company_id.filtered(
                lambda c: order.company_id not in c._accessible_branches()
            )
            if invalid_companies:
                bad_products = order.order_line.product_id.filtered(
                    lambda p: p.company_id and p.company_id in invalid_companies
                )
                raise ValidationError(_(
                    "Your quotation contains products from company %(product_company)s whereas your quotation belongs to company %(quote_company)s. \n Please change the company of your quotation or remove the products from other companies (%(bad_products)s).",
                    product_company=', '.join(invalid_companies.sudo().mapped('display_name')),
                    quote_company=order.company_id.display_name,
                    bad_products=', '.join(bad_products.mapped('display_name')),
                ))

    def _compute_access_url(self):
        super(PurchaseOrder, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/purchase/%s' % (order.id)

    @api.depends('state', 'date_order', 'date_approve')
    def _compute_date_calendar_start(self):
        for order in self:
            order.date_calendar_start = order.date_approve if (order.state == 'purchase') else order.date_order

    @api.depends('currency_id', 'date_order', 'company_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env['res.currency']._get_conversion_rate(
                from_currency=order.company_id.currency_id,
                to_currency=order.currency_id,
                company=order.company_id,
                date=(order.date_order or fields.Datetime.now()).date(),
            )

    @api.depends('amount_total', 'currency_rate')
    def _compute_amount_total_cc(self):
        for order in self:
            order.amount_total_cc = order.amount_total / order.currency_rate

    @api.depends('order_line.date_planned')
    def _compute_date_planned(self):
        """ date_planned = the earliest date_planned across all order lines. """
        for order in self:
            dates_list = order.order_line.filtered(lambda x: not x.display_type and x.date_planned).mapped('date_planned')
            if dates_list:
                order.date_planned = min(dates_list)
            else:
                order.date_planned = False

    @api.depends('name', 'partner_ref', 'amount_total', 'currency_id')
    @api.depends_context('show_total_amount')
    def _compute_display_name(self):
        for po in self:
            name = po.name
            if po.partner_ref:
                name += ' (' + po.partner_ref + ')'
            if self.env.context.get('show_total_amount') and po.amount_total:
                name += ': ' + formatLang(self.env, po.amount_total, currency_obj=po.currency_id)
            po.display_name = name

    @api.depends('company_id', 'partner_id', 'partner_id.reminder_date_before_receipt')
    def _compute_receipt_reminder_email(self):
        for order in self:
            order.receipt_reminder_email = order.partner_id.with_company(order.company_id).receipt_reminder_email
            order.reminder_date_before_receipt = order.partner_id.with_company(order.company_id).reminder_date_before_receipt

    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            if not order.company_id:
                order.tax_totals = False
                continue
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            if order.currency_id != order.company_currency_id:
                order.tax_totals['amount_total_cc'] = f"({formatLang(self.env, order.amount_total_cc, currency_obj=order.company_currency_id)})"

    @api.depends('company_id.account_fiscal_country_id', 'fiscal_position_id.country_id', 'fiscal_position_id.foreign_vat')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    @api.depends('order_line', 'order_line.product_id')
    def _compute_show_comparison(self):
        line_groupby_product = self.env['purchase.order.line']._read_group(
            [('product_id', 'in', self.order_line.product_id.ids), ('state', '=', 'purchase')],
            ['product_id'],
            ['order_id:array_agg']
        )

        order_by_product = {p: set(o_ids) for p, o_ids in line_groupby_product}
        for record in self:
            record.show_comparison = any(set(record.ids) != order_by_product[p] for p in record.order_line.product_id if p in order_by_product)

    @api.depends('partner_id.name', 'partner_id.purchase_warn_msg', 'order_line.purchase_line_warn_msg')
    def _compute_purchase_warning_text(self):
        if not self.env.user.has_group('purchase.group_warning_purchase'):
            self.purchase_warning_text = ''
            return
        for order in self:
            warnings = OrderedSet()
            if partner_msg := order.partner_id.purchase_warn_msg:
                warnings.add((order.partner_id.name or order.partner_id.display_name) + ' - ' + partner_msg)
            if partner_parent_msg := order.partner_id.parent_id.purchase_warn_msg:
                parent = order.partner_id.parent_id
                warnings.add((parent.name or parent.display_name) + ' - ' + partner_parent_msg)
            for line in order.order_line:
                if product_msg := line.purchase_line_warn_msg:
                    warnings.add(line.product_id.display_name + ' - ' + product_msg)
            order.purchase_warning_text = '\n'.join(warnings)

    @api.depends('partner_ref', 'origin', 'partner_id')
    def _compute_duplicated_order_ids(self):
        """Compute duplicated purchase orders based on key fields."""
        draft_orders = self.filtered(lambda o: o.state == 'draft')
        order_to_duplicate_orders = draft_orders._fetch_duplicate_orders()
        for order in draft_orders:
            duplicate_ids = order_to_duplicate_orders.get(order.id, [])
            order.duplicated_order_ids = [Command.set(duplicate_ids)]
        (self - draft_orders).duplicated_order_ids = False

    def _fetch_duplicate_orders(self):
        """ Fetch duplicated orders.

        :return: Dictionary mapping order to its related duplicated orders.
        :rtype: dict
        """
        orders = self.filtered(lambda order: order.id and order.partner_ref)
        if not orders:
            return {}

        self.env['purchase.order'].flush_model(['company_id', 'partner_id', 'partner_ref', 'origin', 'state'])

        result = self.env.execute_query(SQL("""
            SELECT
                po.id AS order_id,
                array_agg(duplicate_po.id) AS duplicate_ids
            FROM purchase_order po
            JOIN purchase_order AS duplicate_po
                ON po.company_id = duplicate_po.company_id
                AND po.id != duplicate_po.id
                AND duplicate_po.state != 'cancel'
                AND po.partner_id = duplicate_po.partner_id
                AND (
                    po.origin = duplicate_po.name
                    OR po.partner_ref = duplicate_po.partner_ref
                )
            WHERE po.id IN %(orders)s
            GROUP BY po.id
        """, orders=tuple(orders.ids)))

        return {order_id: set(duplicate_ids) for order_id, duplicate_ids in result}

    def action_open_business_doc(self):
        self.ensure_one()
        return {
            'name': _("Order"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.id,
            'views': [(False, 'form')],
        }

    @api.onchange('date_planned')
    def onchange_date_planned(self):
        if self.date_planned:
            self.order_line.filtered(lambda line: not line.display_type).date_planned = self.date_planned

    def _search_is_late(self, operator, value):
        if operator not in ["=", "!="]:
            raise ValidationError(self.env._("Unsupported operator"))
        purchase_domain = self._get_domain_is_late(operator, value)
        if operator == "=" and value or operator == "!=" and not value:
            purchase_lines_late = Domain('order_id', 'any', purchase_domain) & Domain.custom(
                to_sql=lambda model, alias, query: SQL(
                    "%s < %s",
                    model._field_to_sql(alias, 'qty_received', query),
                    model._field_to_sql(alias, 'product_qty', query),
                )
            )
            return Domain('order_line', 'any', purchase_lines_late)
        else:
            purchase_lines_on_time = Domain('order_id', 'any', purchase_domain) & Domain.custom(
                to_sql=lambda model, alias, query: SQL(
                    "%s >= %s",
                    model._field_to_sql(alias, 'qty_received', query),
                    model._field_to_sql(alias, 'product_qty', query),
                )
            )
            return Domain('order_line', 'any', purchase_lines_on_time)

    def _get_domain_is_late(self, operator, value):
        return Domain([('state', '=', 'purchase'), ('date_planned', '<=', fields.Datetime.now())])

    @api.model_create_multi
    def create(self, vals_list):
        orders = self.browse()
        for vals in vals_list:
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
            # Ensures default picking type and currency are taken from the right company.
            self_comp = self.with_company(company_id)
            if vals.get('name', 'New') == 'New':
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
            orders |= super(PurchaseOrder, self_comp).create(vals)
        return orders

    @api.ondelete(at_uninstall=False)
    def _unlink_if_cancelled(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a purchase order, you must cancel it first.'))

    def copy(self, default=None):
        ctx = dict(self.env.context)
        ctx.pop('default_product_id', None)
        self = self.with_context(ctx)
        new_pos = super().copy(default=default)
        for line in new_pos.order_line:
            if line.product_id:
                line.date_planned = line._get_date_planned(line.selected_seller_id)
        return new_pos

    def _must_delete_date_planned(self, field_name):
        # To be overridden
        return field_name == 'order_line'

    def onchange(self, values, field_names, fields_spec):
        """
        Override onchange to NOT update all date_planned on PO lines when
        date_planned on PO is updated by the change of date_planned on PO lines.
        """
        result = super().onchange(values, field_names, fields_spec)
        if any(self._must_delete_date_planned(field) for field in field_names) and 'value' in result:
            for line in result['value'].get('order_line', []):
                if line[0] == Command.UPDATE and 'date_planned' in line[2]:
                    del line[2]['date_planned']
        return result

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Purchase Order-%s' % (self.name)

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        # Ensures all properties and fiscal positions
        # are taken with the company of the order
        # if not defined, with_company doesn't change anything.
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.fiscal_position_id = False
        else:
            self.fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(self.partner_id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            if self.partner_id.buyer_id:
                self.user_id = self.partner_id.buyer_id
        return {}

    @api.depends('partner_id', 'company_id')
    def _compute_currency_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            if not order.partner_id:
                order.currency_id = order.company_id.currency_id
            else:
                order.currency_id = order.partner_id.property_purchase_currency_id or order.company_id.currency_id

    @api.onchange('fiscal_position_id', 'company_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the PO.
        """
        self.order_line._compute_tax_id()

    # ------------------------------------------------------------
    # MAIL.THREAD
    # ------------------------------------------------------------

    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
            kwargs['notify_author_mention'] = kwargs.get('notify_author_mention', True)
        return super().message_post(**kwargs)

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=False):
        # Tweak 'view document' button for portal customers, calling directly routes for confirm specific to PO model.
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups

        self.ensure_one()
        try:
            customer_portal_group = next(group for group in groups if group[0] == 'portal_customer')
        except StopIteration:
            pass
        else:
            access_opt = customer_portal_group[2].setdefault('button_access', {})
            if self.env.context.get('is_reminder'):
                access_opt['title'] = _('View')
            else:
                access_opt.update(
                    title=_("View Quotation") if self.state in ('draft', 'sent') else _("View Order"),
                    url=self.get_base_url() + self.get_confirm_url(),
                )

        return groups

    def _notify_by_email_prepare_rendering_context(self, message, msg_vals=False, model_description=False,
                                                   force_email_company=False, force_email_lang=False,
                                                   force_record_name=False):
        render_context = super()._notify_by_email_prepare_rendering_context(
            message, msg_vals=msg_vals, model_description=model_description,
            force_email_company=force_email_company, force_email_lang=force_email_lang,
            force_record_name=force_record_name,
        )
        subtitles = [render_context['record'].name]
        # don't show price on RFQ mail
        if self.state in ['draft', 'sent']:
            subtitles.append(_('Order\N{NO-BREAK SPACE}due\N{NO-BREAK SPACE}%(date)s',
                date=format_date(self.env, self.date_order, lang_code=render_context.get('lang'))
            ))
        else:
            subtitles.append(format_amount(self.env, self.amount_total, self.currency_id, lang_code=render_context.get('lang')))
        render_context['subtitles'] = subtitles
        return render_context

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'purchase':
            if init_values['state'] == 'to approve':
                return self.env.ref('purchase.mt_rfq_approved')
            return self.env.ref('purchase.mt_rfq_confirmed')
        elif 'state' in init_values and self.state == 'to approve':
            return self.env.ref('purchase.mt_rfq_confirmed')
        elif 'state' in init_values and self.state == 'sent':
            return self.env.ref('purchase.mt_rfq_sent')
        return super(PurchaseOrder, self)._track_subtype(init_values)

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_ids': self.ids,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'email_notification_allow_footer': True,
            'force_email': True,
            'hide_mail_template_management_options': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = _('Request for Quotation')
        else:
            ctx['model_description'] = _('Purchase Order')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_acknowledge(self):
        self.acknowledged = True

    def action_purchase_comparison(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_history")
        action['domain'] = [('product_id', 'in', self.order_line.product_id.ids)]
        action['display_name'] = _("Purchase Comparison for %s", self.display_name)
        return action

    def print_quotation(self):
        self.filtered(lambda po: po.state == 'draft').write({'state': "sent"})
        return self.env.ref('purchase.report_purchase_quotation').report_action(self)

    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
        self.filtered(lambda p: p.lock_confirmed_po == 'lock').write({'locked': True})
        return {}

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            error_msg = order._confirmation_error_message()
            if error_msg:
                raise UserError(error_msg)
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    def button_cancel(self):
        locked_purchase_orders = self.filtered(lambda po: po.locked)
        if locked_purchase_orders:
            raise UserError(self.env._("Unable to cancel purchase order(s): %s. You must first unlock them.", locked_purchase_orders.mapped('display_name')))

        purchase_orders_with_invoices = self.filtered(lambda po: any(i.state not in ('cancel', 'draft') for i in po.invoice_ids))
        if purchase_orders_with_invoices:
            raise UserError(_("Unable to cancel purchase order(s): %s. You must first cancel their related vendor bills.", purchase_orders_with_invoices.mapped('display_name')))
        self.write({'state': 'cancel'})

    def button_lock(self):
        self.locked = True

    def button_unlock(self):
        self.locked = False

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then return error message. """
        self.ensure_one()
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("Some order lines are missing a product, you need to correct them before going further.")

        return False

    def _prepare_supplier_info(self, partner, line, price, currency):
        # Prepare supplierinfo data when adding a product
        return {
            'partner_id': partner.id,
            'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
            'min_qty': 1.0,
            'price': price,
            'currency_id': currency.id,
            'discount': line.discount,
            'delay': 0,
        }

    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            already_seller = (partner | self.partner_id) & line.product_id.seller_ids.mapped('partner_id')
            if line.product_id and not already_seller and len(line.product_id.seller_ids) <= 10:
                price = line.price_unit
                # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_id != line.product_uom_id:
                    default_uom = line.product_id.product_tmpl_id.uom_id
                    price = line.product_uom_id._compute_price(price, default_uom)

                supplierinfo = self._prepare_supplier_info(partner, line, price, line.currency_id)
                # In case the order partner is a contact address, a new supplierinfo is created on
                # the parent company. In this case, we keep the product name and code.
                if line.selected_seller_id:
                    supplierinfo['product_name'] = line.selected_seller_id.product_name
                    supplierinfo['product_code'] = line.selected_seller_id.product_code
                    supplierinfo['product_uom_id'] = line.product_uom.id
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                # supplier info should be added regardless of the user access rights
                line.product_id.product_tmpl_id.sudo().write(vals)

    def action_bill_matching(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Bill Matching"),
            'res_model': 'purchase.bill.line.match',
            'domain': [
                ('partner_id', 'in', (self.partner_id | self.partner_id.commercial_partner_id).ids),
                ('company_id', 'in', self.env.company.ids),
                ('purchase_order_id', 'in', [self.id, False]),
            ],
            'views': [(self.env.ref('purchase.purchase_bill_line_match_tree').id, 'list')],
        }

    def _prepare_down_payment_section_values(self):
        self.ensure_one()
        context = {'lang': self.partner_id.lang}
        res = {
            'product_qty': 0.0,
            'order_id': self.id,
            'display_type': 'line_section',
            'is_downpayment': True,
            'sequence': (self.order_line[-1:].sequence or 9) + 1,
            'name': _("Down Payments"),
        }
        del context
        return res

    def _create_downpayments(self, line_vals):
        self.ensure_one()

        # create section
        if not any(line.display_type and line.is_downpayment for line in self.order_line):
            section_line = self.order_line.create(self._prepare_down_payment_section_values())
        else:
            section_line = self.order_line.filtered(lambda line: line.display_type and line.is_downpayment)
        vals = [
            {
                **line_val,
                'sequence': section_line.sequence + i,
            }
            for i, line_val in enumerate(line_vals, start=1)
        ]
        downpayment_lines = self.env['purchase.order.line'].create(vals)
        self.order_line = [
            Command.link(line_id)
            for line_id in downpayment_lines.ids
        ]  # a simple concatenation would cause all order_line to recompute, we do not want it to happen
        return downpayment_lines

    def action_create_invoice(self, attachment_ids=False):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type in ('line_section', 'line_subsection'):
                    pending_section = line
                    continue
                if pending_section:
                    line_vals = pending_section._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
                    pending_section = None
                line_vals = line._prepare_account_move_line()
                line_vals.update({'sequence': sequence})
                invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                sequence += 1
            invoice_vals_list.append(invoice_vals)

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for _grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
            ref_invoice_vals.update({
                'invoice_origin': ', '.join(origins),
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        invoices = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            invoices |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        invoices.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_move_type()

        # 5) Link the attachments to the invoice
        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            return self.action_view_invoice(invoices)

        if len(invoices) != 1:
            raise ValidationError(_("You can only upload a bill for a single vendor at a time."))
        invoices.with_context(skip_is_manually_modified=True)._extend_with_attachments(
            invoices._to_files_data(attachments),
            new=True,
        )

        invoices.message_post(attachment_ids=attachments.ids)

        attachments.write({'res_model': 'account.move', 'res_id': invoices.id})
        return self.action_view_invoice(invoices)

    def action_merge(self):
        all_origin = []
        all_vendor_references = []
        rfq_to_merge = self.filtered(lambda r: r.state in ['draft', 'sent'])

        # Group RFQs by vendor
        if len(rfq_to_merge) < 2:
            raise UserError(_("Please select at least two purchase orders with state RFQ and RFQ sent to merge."))

        rfqs_grouped = defaultdict(lambda: self.env['purchase.order'])
        for rfq in rfq_to_merge:
            key = self._prepare_grouped_data(rfq)
            rfqs_grouped[key] += rfq

        bunches_of_rfq_to_be_merge = list(rfqs_grouped.values())
        if all(len(rfq_bunch) == 1 for rfq_bunch in list(bunches_of_rfq_to_be_merge)):
            raise UserError(_("In selected purchase order to merge these details must be same\nVendor, currency, destination, dropship address and agreement"))
        bunches_of_rfq_to_be_merge = [rfqs for rfqs in bunches_of_rfq_to_be_merge if len(rfqs) > 1]

        merged_rfq_ids = []

        for rfqs in bunches_of_rfq_to_be_merge:
            if len(rfqs) <= 1:
                continue
            oldest_rfq = min(rfqs, key=lambda r: r.date_order)
            if oldest_rfq:
                # Merge RFQs into the oldest purchase order
                rfqs -= oldest_rfq
                for rfq_line in rfqs.order_line:
                    existing_line = oldest_rfq.order_line.filtered(lambda l: l.display_type not in ['line_section', 'line_subsection', 'line_note'] and
                                                                                l.product_id == rfq_line.product_id and
                                                                                l.product_uom_id == rfq_line.product_uom_id and
                                                                                l.analytic_distribution == rfq_line.analytic_distribution and
                                                                                l.discount == rfq_line.discount and
                                                                                abs(l.date_planned - rfq_line.date_planned).total_seconds() <= 86400  # 24 hours in seconds
                                                                        )
                    if len(existing_line) > 1:
                        existing_line[0].product_qty += sum(existing_line[1:].mapped('product_qty'))
                        existing_line[1:].unlink()
                        existing_line = existing_line[0]

                    if existing_line:
                        existing_line._merge_po_line(rfq_line)
                    else:
                        rfq_line.order_id = oldest_rfq

                # Merge source documents and vendor references
                all_origin = rfqs.mapped('origin')
                all_vendor_references = rfqs.mapped('partner_ref')

                oldest_rfq.origin = ', '.join(filter(None, [oldest_rfq.origin, *all_origin]))
                oldest_rfq.partner_ref = ', '.join(filter(None, [oldest_rfq.partner_ref, *all_vendor_references]))

                rfq_names = rfqs.mapped('name')
                merged_names = ", ".join(rfq_names)
                oldest_rfq_message = _("RFQ merged with %(oldest_rfq_name)s and %(cancelled_rfq)s", oldest_rfq_name=oldest_rfq.name, cancelled_rfq=merged_names)

                for rfq in rfqs:
                    cancelled_rfq_message = _("RFQ merged with %s", oldest_rfq._get_html_link())
                    rfq.message_post(body=cancelled_rfq_message)
                oldest_rfq.message_post(body=oldest_rfq_message)

                rfqs.filtered(lambda r: r.state != 'cancel').button_cancel()
                oldest_rfq._merge_alternative_po(rfqs)

                # Keep the oldest RFQ IDs
                merged_rfq_ids.append(oldest_rfq.id)

        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,kanban,form',
            'res_model': 'purchase.order',
        }
        if len(merged_rfq_ids) == 1:
            action['res_id'] = merged_rfq_ids[0]
            action['view_mode'] = 'form'
        else:
            action['name'] = _("Merged RFQs")
            action['domain'] = [('id', 'in', merged_rfq_ids)]
        return action

    def _merge_alternative_po(self, rfqs):
        pass

    def _prepare_grouped_data(self, rfq):
        return (rfq.partner_id.id, rfq.currency_id.id, rfq.dest_address_id.id)

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self.env.context.get('default_move_type', 'in_invoice')

        partner_invoice = self.env['res.partner'].browse(self.partner_id.address_get(['invoice'])['invoice'])
        partner_bank_id = self.partner_id.commercial_partner_id.bank_ids.filtered_domain(['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])[:1]

        invoice_vals = {
            'move_type': move_type,
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'partner_id': partner_invoice.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(partner_invoice)).id,
            'partner_bank_id': partner_bank_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            self.invalidate_model(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        result['context'] = literal_eval(result['context'])
        if len(self.partner_id) == 1:
            result['context']['default_partner_id'] = self.partner_id.id
        return result

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the purchase order views.
        """
        if not self.env.user._is_internal():
            raise AccessDenied()
        self.browse().check_access('read')

        result = {
            'global': {
                'draft': {'all': 0, 'priority': 0},
                'sent':  {'all': 0, 'priority': 0},
                'late':  {'all': 0, 'priority': 0},
                'not_acknowledged': {'all': 0, 'priority': 0},
                'late_receipt': {'all': 0, 'priority': 0},
                'days_to_order': 0,
            },
            'my': {
                'draft': {'all': 0, 'priority': 0},
                'sent':  {'all': 0, 'priority': 0},
                'late':  {'all': 0, 'priority': 0},
                'not_acknowledged': {'all': 0, 'priority': 0},
                'late_receipt': {'all': 0, 'priority': 0},
                'days_to_order': 0,
            },
            'days_to_purchase': 0,
        }

        def _update(key, dict_to_update, group):
            for priority, user_id, count in group:
                my = user_id == self.env.user
                dict_to_update['global'][key]['all'] += count
                if priority != '0':
                    dict_to_update['global'][key]['priority'] += count
                if not my:
                    continue
                dict_to_update['my'][key]['all'] += count
                if priority != '0':
                    dict_to_update['my'][key]['priority'] += count

        # easy counts
        groupby = ['priority', 'user_id']
        aggregate = ['id:count_distinct']
        rfq_draft_domain = [('state', '=', 'draft')]
        rfq_draft_group = self.env['purchase.order']._read_group(rfq_draft_domain, groupby, aggregate)
        _update('draft', result, rfq_draft_group)

        rfq_sent_domain = [('state', '=', 'sent')]
        rfq_sent_group = self.env['purchase.order']._read_group(rfq_sent_domain, groupby, aggregate)
        _update('sent', result, rfq_sent_group)

        rfq_late_domain = [('state', 'in', ['draft', 'sent', 'to approve']), ('date_order', '<', fields.Datetime.now())]
        rfq_late_group = self.env['purchase.order']._read_group(rfq_late_domain, groupby, aggregate)
        _update('late', result, rfq_late_group)

        rfq_not_acknowledge = [('state', 'in', ['purchase', 'done']), ('acknowledged', '=', False)]
        rfq_not_acknowledge_group = self.env['purchase.order']._read_group(rfq_not_acknowledge, groupby, aggregate)
        _update('not_acknowledged', result, rfq_not_acknowledge_group)

        rfq_late_receipt = [('state', 'in', ['purchase', 'done']), ('is_late', '=', True)]
        rfq_late_receipt_group = self.env['purchase.order']._read_group(rfq_late_receipt, groupby, aggregate)
        _update('late_receipt', result, rfq_late_receipt_group)

        three_months_ago = fields.Datetime.to_string(fields.Datetime.now() - relativedelta(months=3))

        purchases = self.env['purchase.order'].search_fetch(
            [('state', '=', 'purchase'), ('create_date', '>=', three_months_ago), ('date_approve', '!=', False)],
            ['create_date', 'date_approve', 'user_id'])

        global_deliveries_seconds = 0
        my_deliveries_seconds = 0
        my_deliveries_count = 0

        for po in purchases:
            delivery_seconds = (po.date_approve - po.create_date).total_seconds()
            global_deliveries_seconds += delivery_seconds
            if po.user_id == self.env.user:
                my_deliveries_seconds += delivery_seconds
                my_deliveries_count += 1

        avg_global_deliveries_seconds = global_deliveries_seconds / len(purchases) if purchases else 0
        avg_my_deliveries_seconds = my_deliveries_seconds / my_deliveries_count if my_deliveries_count else 0
        result['global']['days_to_order'] = float_repr(avg_global_deliveries_seconds / 60 / 60 / 24, precision_digits=2)
        result['my']['days_to_order'] = float_repr(avg_my_deliveries_seconds / 60 / 60 / 24, precision_digits=2)

        return result

    def _send_reminder_mail(self, send_single=False):
        if not self.env.user.has_group('purchase.group_send_reminder'):
            return

        template = self.env.ref('purchase.email_template_edi_purchase_reminder', raise_if_not_found=False)
        if template:
            orders = self if send_single else self._get_orders_to_remind()
            for order in orders:
                date = order.date_planned
                if date and (send_single or (date - relativedelta(days=order.reminder_date_before_receipt)).date() == datetime.today().date()):
                    if send_single:
                        return order._send_reminder_open_composer(template.id)
                    else:
                        order.with_context(is_reminder=True).message_post_with_source(
                            template,
                            email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
                            subtype_xmlid='mail.mt_comment',
                        )

    def send_reminder_preview(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase.group_send_reminder'):
            return

        template = self.env.ref('purchase.email_template_edi_purchase_reminder', raise_if_not_found=False)
        if template and self.env.user.email and self.id:
            template.with_context(is_reminder=True).send_mail(
                self.id,
                force_send=True,
                raise_exception=False,
                email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
                email_values={'email_to': self.env.user.email, 'recipient_ids': []},
            )
            return {'toast_message': escape(_("A sample email has been sent to %s.", self.env.user.email))}

    def _send_reminder_open_composer(self,template_id):
        self.ensure_one()
        try:
            compose_form_id = self.env['ir.model.data']._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_ids': self.ids,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]
        self = self.with_context(lang=lang)
        ctx['model_description'] = _('Purchase Order')
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _get_orders_to_remind(self):
        """When auto sending a reminder mail, only send for unconfirmed purchase
        order and not all products are service."""
        return self.search([
            ('partner_id', '!=', False),
            ('state', '=', 'purchase'),
            ('acknowledged', '=', False),
            ('receipt_reminder_email', '=', True)
        ]).filtered(lambda p: p.mapped('order_line.product_id.product_tmpl_id.type') != ['service'])

    def _default_order_line_values(self, child_field=False):
        default_data = super()._default_order_line_values(child_field)
        new_default_data = self.env['purchase.order.line']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def action_add_from_catalog(self):
        res = super().action_add_from_catalog()
        kanban_view_id = self.env.ref('purchase.product_view_kanban_catalog_purchase_only').id
        res['views'][0] = (kanban_view_id, 'kanban')
        res['search_view_id'] = [self.env.ref('purchase.product_view_search_catalog').id, 'search']
        res['context']['partner_id'] = self.partner_id.id
        return res

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            'precision': self.env['decimal.precision'].precision_get('Product Unit'),
            'product_catalog_currency_id': self.currency_id.id,
            'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
            'search_default_seller_ids': self.partner_id.name,
            'show_sections': bool(self.id),
        }

    def _get_product_catalog_domain(self):
        return super()._get_product_catalog_domain() & Domain('purchase_ok', '=', True)

    def _get_product_catalog_order_data(self, products, **kwargs):
        res = super()._get_product_catalog_order_data(products, **kwargs)
        for product in products:
            res[product.id] |= self._get_product_price_and_data(product)
        return res

    def _get_product_catalog_record_lines(self, product_ids, *, section_id=None, **kwargs):
        grouped_lines = defaultdict(lambda: self.env['purchase.order.line'])
        if section_id is None:
            section_id = (
                self.order_line[:1].id
                if self.order_line[:1].display_type == 'line_section'
                else False
            )
        for line in self.order_line:
            if (
                line.display_type
                or line.product_id.id not in product_ids
                or line.get_parent_section_line().id != section_id
            ):
                continue
            grouped_lines[line.product_id] |= line
        return grouped_lines

    def _get_product_price_and_data(self, product):
        """ Fetch the product's data used by the purchase's catalog.

        :return: the product's price and, if applicable, the minimum quantity to
                 buy and the product's packaging data.
        :rtype: dict
        """
        self.ensure_one()
        product_infos = {
            'price': product.standard_price,
            'uomDisplayName': product.uom_id.display_name
        }
        params = {'order_id': self}
        # Check if there is a price and a minimum quantity for the order's vendor.
        seller = product._select_seller(
            partner_id=self.partner_id,
            quantity=None,
            date=self.date_order and self.date_order.date(),
            uom_id=product.uom_id,
            ordered_by='min_qty',
            params=params
        )
        if seller:
            product_uom = (seller.product_id or seller.product_tmpl_id).uom_id
            price = seller.price_discounted
            if seller.currency_id != self.currency_id:
                price = seller.currency_id._convert(price, self.currency_id)
            if seller.product_uom_id != product_uom:
                # The discounted price is expressed in the product's UoM, not in the vendor
                # price's UoM, so we need to convert it into to match the displayed UoM.
                price = product_uom._compute_price(price, seller.product_uom_id)
                product_infos.update(uomFactor=seller.product_uom_id.factor / product_uom.factor)
            product_infos.update(
                price=price,
                min_qty=seller.min_qty,
                uomDisplayName=seller.product_uom_id.display_name,
            )

        return product_infos

    def get_acknowledge_url(self):
        return self.get_portal_url(query_string='&acknowledge=True')

    def get_confirm_url(self, confirm_type=None):
        """Create url for confirm reminder or purchase reception email for sending
        in mail. Unsuported anymore. We only use the acknowledge mechanism. Keep it
        for backward compatibility"""
        if confirm_type in ['reminder', 'reception', 'decline']:
            return self.get_acknowledge_url()
        return self.get_portal_url()

    def get_update_url(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        update_param = url_encode({'update': 'True'})
        return self.get_portal_url(query_string='&%s' % update_param)

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
            self.company_id.po_double_validation == 'one_step'
            or (self.company_id.po_double_validation == 'two_step'
                and self.amount_total < self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
            or self.env.user.has_group('purchase.group_purchase_manager'))

    def get_localized_date_planned(self, date_planned=False):
        """Returns the localized date planned in the timezone of the order's user or the
        company's partner or UTC if none of them are set."""
        self.ensure_one()
        date_planned = date_planned or self.date_planned
        if not date_planned:
            return False
        if isinstance(date_planned, str):
            date_planned = fields.Datetime.from_string(date_planned)
        tz = self.get_order_timezone()
        return date_planned.astimezone(tz)

    def get_order_timezone(self):
        """ Returns the timezone of the order's user or the company's partner
        or UTC if none of them are set. """
        self.ensure_one()
        return timezone(self.user_id.tz or self.company_id.partner_id.tz or 'UTC')

    def _update_date_planned_for_lines(self, updated_dates):
        # create or update the activity
        activity = self.env['mail.activity'].search([
            ('summary', '=', _('Date Updated')),
            ('res_model_id', '=', 'purchase.order'),
            ('res_id', '=', self.id),
            ('user_id', '=', self.user_id.id)], limit=1)
        if activity:
            self._update_update_date_activity(updated_dates, activity)
        else:
            self._create_update_date_activity(updated_dates)

        # update the date on PO line
        for line, date in updated_dates:
            line._update_date_planned(date)

    def _update_order_line_info(
        self, product_id, quantity, *, section_id=False, child_field='order_line', **kwargs
    ):
        """ Update purchase order line information for a given product or create
        a new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :param int quantity: The quantity selected in the catalog.
        :param int section_id: The id of section selected in the catalog.
        :return: The unit price of the product, based on the pricelist of the
                 purchase order and the quantity selected.
        :rtype: float
        """
        self.ensure_one()
        pol = self.order_line.filtered(
            lambda l: l.product_id.id == product_id
            and l.get_parent_section_line().id == section_id
        )
        if pol:
            if quantity != 0:
                pol.product_qty = quantity
            elif self.state in ['draft', 'sent']:
                price_unit = self._get_product_price_and_data(pol.product_id)['price']
                pol.unlink()
                return price_unit
            else:
                pol.product_qty = 0
        elif quantity > 0:
            pol = self.env['purchase.order.line'].create({
                'order_id': self.id,
                'product_id': product_id,
                'product_qty': quantity,
                'sequence': self._get_new_line_sequence(child_field, section_id),
            })
            if pol.selected_seller_id:
                # Fix the PO line's price on the seller's one.
                seller = pol.selected_seller_id
                price = seller.price
                if seller.currency_id != self.currency_id:
                    price = seller.currency_id._convert(price, self.currency_id)
                pol.price_unit = pol.technical_price_unit = price
                pol.discount = seller.discount
        return pol.price_unit_discounted

    def _get_default_create_section_values(self):
        """ Return the default values for creating a section line in the purchase order through
        catalog.

        :return: A dictionary with default values for creating a new section.
        :rtype: dict
        """
        return {'product_qty': 0}

    def _get_parent_field_on_child_model(self):
        return 'order_id'

    def _create_update_date_activity(self, updated_dates):
        note = Markup('<p>%s</p>\n') % _('%s modified receipt dates for the following products:', self.partner_id.name)
        for line, date in updated_dates:
            note += Markup('<p> - %s</p>\n') % _(
                '%(product)s from %(original_receipt_date)s to %(new_receipt_date)s',
                product=line.product_id.display_name,
                original_receipt_date=line.date_planned.date(),
                new_receipt_date=date.date()
            )
        activity = self.activity_schedule(
            'mail.mail_activity_data_warning',
            summary=_("Date Updated"),
            user_id=self.user_id.id
        )
        # add the note after we post the activity because the note can be soon
        # changed when updating the date of the next PO line. So instead of
        # sending a mail with incomplete note, we send one with no note.
        activity.note = note
        return activity

    def _update_update_date_activity(self, updated_dates, activity):
        for line, date in updated_dates:
            activity.note += Markup('<p> - %s</p>\n') %  _(
                '%(product)s from %(original_receipt_date)s to %(new_receipt_date)s',
                product=line.product_id.display_name,
                original_receipt_date=line.date_planned.date(),
                new_receipt_date=date.date()
            )

    def _is_readonly(self):
        """ Return whether the purchase order is read-only or not based on the state.
        A purchase order is considered read-only if its state is 'cancel'.

        :return: Whether the purchase order is read-only or not.
        :rtype: bool
        """
        self.ensure_one()
        return self.state == 'cancel'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Requests for Quotation'),
            'template': '/purchase/static/xls/requests_for_quotation_import_template.xlsx',
        }]

    # ------------------------------------------------------------
    # EDI
    # ------------------------------------------------------------

    def _get_edi_builders(self):
        return []

    def create_document_from_attachment(self, attachment_ids):
        """ Create the purchase orders from given attachment_ids
        and redirect newly create order view.

        :param list attachment_ids: List of attachments process.
        :return: An action redirecting to related sale order view.
        :rtype: dict
        """
        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            raise UserError(_("No attachment was provided"))

        orders = self.with_context(default_partner_id=self.env.user.partner_id.id)._create_records_from_attachments(attachments)
        return orders._get_records_action(name=_("Generated Orders"))


# FILEPATH: odoo/addons/purchase/models/purchase_order_line.py
class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['analytic.mixin']
    _description = 'Purchase Order Line'
    _order = 'order_id, sequence, id'

    name = fields.Text(
        string='Description', required=True, compute='_compute_price_unit_and_date_planned_and_name', store=True, readonly=False)
    translated_product_name = fields.Text(compute='_compute_translated_product_name')
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits='Product Unit', required=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    date_planned = fields.Datetime(
        string='Expected Arrival', index=True,
        compute="_compute_price_unit_and_date_planned_and_name", readonly=False, store=True,
        help="Delivery date expected from vendor. This date respectively defaults to vendor pricelist lead time then today's date.")
    discount = fields.Float(
        string="Discount (%)",
        compute='_compute_price_unit_and_date_planned_and_name',
        digits='Discount',
        store=True, readonly=False)
    tax_ids = fields.Many2many('account.tax', string='Taxes', context={'active_test': False, 'hide_original_tax_ids': True})
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    product_uom_id = fields.Many2one('uom.uom', string='Unit', domain="[('id', 'in', allowed_uom_ids)]", ondelete='restrict')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, index='btree_not_null', ondelete='restrict')
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(
        string='Unit Price', required=True, min_display_digits='Product Price', aggregator='avg',
        compute="_compute_price_unit_and_date_planned_and_name", readonly=False, store=True)
    price_unit_product_uom = fields.Float(
        string='Unit Price Product UoM', min_display_digits='Product Price', compute="_compute_price_unit_product_uom",
        help="The Price of one unit of the product's Unit of Measure")
    price_unit_discounted = fields.Float('Unit Price (Discounted)', compute='_compute_price_unit_discounted')

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')

    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True)
    state = fields.Selection(related='order_id.state')

    invoice_lines = fields.One2many('account.move.line', 'purchase_line_id', string="Bill Lines", readonly=True, copy=False)

    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits='Product Unit', store=True)

    qty_received_method = fields.Selection([('manual', 'Manual')], string="Received Qty Method", compute='_compute_qty_received_method', store=True,
        help="According to product configuration, the received quantity can be automatically computed by mechanism:\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")
    qty_received = fields.Float("Received Qty", compute='_compute_qty_received', inverse='_inverse_qty_received', compute_sudo=True, store=True, digits='Product Unit')
    qty_received_manual = fields.Float("Manual Received Qty", digits='Product Unit', copy=False)
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True,
                                  digits='Product Unit')

    # Same than `qty_received` and `qty_to_invoice` but non-stored and depending of the context.
    qty_received_at_date = fields.Float(
        string="Received",
        compute='_compute_qty_received_at_date',
        digits='Product Unit'
    )
    qty_invoiced_at_date = fields.Float(
        string="Billed",
        compute='_compute_qty_invoiced_at_date',
        digits='Product Unit'
    )

    amount_to_invoice_at_date = fields.Float(string='Amount', compute='_compute_amount_to_invoice_at_date')

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True, store=True, index='btree_not_null')
    currency_id = fields.Many2one(related='order_id.currency_id', string='Currency')
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    date_approve = fields.Datetime(related="order_id.date_approve", string='Confirmation Date', readonly=True)
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        string='Tax calculation rounding method', readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_subsection', "Subsection"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    is_downpayment = fields.Boolean()
    selected_seller_id = fields.Many2one('product.supplierinfo', compute='_compute_selected_seller_id', help='Technical field to get the vendor pricelist used to generate this line')

    _accountable_required_fields = models.Constraint(
        'CHECK(display_type IS NOT NULL OR is_downpayment OR (product_id IS NOT NULL AND product_uom_id IS NOT NULL AND date_planned IS NOT NULL))',
        'Missing required fields on accountable purchase order line.',
    )
    _non_accountable_null_fields = models.Constraint(
        'CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom_id IS NULL AND date_planned is NULL))',
        'Forbidden values on non-accountable purchase order line',
    )
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids', readonly=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Product attribute values that do not create variants', ondelete='restrict')
    purchase_line_warn_msg = fields.Text(compute='_compute_purchase_line_warn_msg')
    parent_id = fields.Many2one(
        'purchase.order.line',
        string="Parent Section Line",
        compute='_compute_parent_id',
    )
    technical_price_unit = fields.Float(help="Technical field for price computation")

    @api.depends('product_qty', 'price_unit', 'tax_ids', 'discount')
    def _compute_amount(self):
        AccountTax = self.env['account.tax']
        for line in self:
            company = line.company_id or self.env.company
            base_line = line._prepare_base_line_for_taxes_computation()
            AccountTax._add_tax_details_in_base_line(base_line, company)
            AccountTax._round_base_lines_tax_details([base_line], company)
            line.price_subtotal = base_line['tax_details']['total_excluded_currency']
            line.price_total = base_line['tax_details']['total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    def _prepare_base_line_for_taxes_computation(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        company = self.order_id.company_id or self.env.company
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            tax_ids=self.tax_ids,
            quantity=self.product_qty,
            partner_id=self.order_id.partner_id,
            currency_id=self.order_id.currency_id or company.currency_id,
            rate=self.order_id.currency_rate,
            name=self.name,
        )

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id._get_fiscal_position(line.order_id.partner_id)
            # filter taxes by company
            taxes = line.product_id.supplier_taxes_id._filter_taxes_by_company(line.company_id)
            line.tax_ids = fpos.map_tax(taxes)

    @api.depends('discount', 'price_unit')
    def _compute_price_unit_discounted(self):
        for line in self:
            line.price_unit_discounted = line.price_unit * (1 - line.discount / 100)

    @api.depends('product_uom_id', 'price_unit')
    def _compute_price_unit_product_uom(self):
        for line in self:
            line.price_unit_product_uom = not line.display_type and not line.is_downpayment and line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_id)

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        invoiced_quantities = self._prepare_qty_invoiced()
        for line in self:
            line.qty_invoiced = invoiced_quantities[line]

            # compute qty_to_invoice
            if line.order_id.state == 'purchase':
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('qty_invoiced')
    @api.depends_context('accrual_entry_date')
    def _compute_qty_invoiced_at_date(self):
        if not self._date_in_the_past():
            for line in self:
                line.qty_invoiced_at_date = line.qty_invoiced
            return
        invoiced_quantities = self._prepare_qty_invoiced()
        for line in self:
            line.qty_invoiced_at_date = invoiced_quantities[line]

    def _prepare_qty_invoiced(self):
        # Compute qty_invoiced
        invoiced_qties = defaultdict(float)
        for line in self:
            for inv_line in line._get_invoice_lines():
                if inv_line.move_id.state not in ['cancel'] or inv_line.move_id.payment_state == 'invoicing_legacy':
                    if inv_line.move_id.move_type == 'in_invoice':
                        invoiced_qties[line] += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom_id)
                    elif inv_line.move_id.move_type == 'in_refund':
                        invoiced_qties[line] -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom_id)
        return invoiced_qties

    def _get_invoice_lines(self):
        self.ensure_one()
        if self.env.context.get('accrual_entry_date'):
            accrual_date = fields.Date.from_string(self.env.context['accrual_entry_date'])
            return self.invoice_lines.filtered(
                lambda l: l.move_id.invoice_date and l.move_id.invoice_date <= accrual_date
            )
        else:
            return self.invoice_lines

    @api.depends('product_id.purchase_line_warn_msg')
    def _compute_purchase_line_warn_msg(self):
        has_warning_group = self.env.user.has_group('purchase.group_warning_purchase')
        for line in self:
            line.purchase_line_warn_msg = line.product_id.purchase_line_warn_msg if has_warning_group else ""

    @api.depends('product_id', 'product_id.type')
    def _compute_qty_received_method(self):
        for line in self:
            if line.product_id and line.product_id.type in ['consu', 'service']:
                line.qty_received_method = 'manual'
            else:
                line.qty_received_method = False

    @api.depends('qty_received_method', 'qty_received_manual')
    def _compute_qty_received(self):
        received_qties = self._prepare_qty_received()
        for line in self:
            if not line.qty_received or line in received_qties:
                line.qty_received = received_qties[line]

    @api.depends('qty_received')
    @api.depends_context('accrual_entry_date')
    def _compute_qty_received_at_date(self):
        if not self._date_in_the_past():
            for line in self:
                line.qty_received_at_date = line.qty_received
            return
        received_quantities = self._prepare_qty_received()
        for line in self:
            line.qty_received_at_date = received_quantities[line]

    def _prepare_qty_received(self):
        received_qties = defaultdict(float)
        for line in self:
            if line.qty_received_method == 'manual':
                received_qties[line] = line.qty_received_manual or 0.0
            else:
                received_qties[line] = 0.0
        return received_qties

    @api.onchange('qty_received')
    def _inverse_qty_received(self):
        """ When writing on qty_received, if the value should be modify manually (`qty_received_method` = 'manual' only),
            then we put the value in `qty_received_manual`. Otherwise, `qty_received_manual` should be False since the
            received qty is automatically compute by other mecanisms.
        """
        for line in self:
            if line.qty_received_method == 'manual':
                line.qty_received_manual = line.qty_received
            else:
                line.qty_received_manual = 0.0

    @api.depends('product_id', 'product_id.seller_ids', 'partner_id', 'product_qty', 'order_id.date_order', 'product_uom_id')
    def _compute_selected_seller_id(self):
        for line in self:
            if line.product_id:
                params = line._get_select_sellers_params()
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=abs(line.product_qty),
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                    uom_id=line.product_uom_id,
                    params=params)
                line.selected_seller_id = seller.id if seller else False
            else:
                line.selected_seller_id = False

    @api.depends('price_unit', 'qty_invoiced_at_date', 'qty_received_at_date')
    @api.depends_context('accrual_entry_date')
    def _compute_amount_to_invoice_at_date(self):
        for line in self:
            line.amount_to_invoice_at_date = (line.qty_received_at_date - line.qty_invoiced_at_date) * line.price_unit

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom_id=False, date_planned=False)
            else:
                values.update(self._prepare_add_missing_fields(values))
            if values.get('price_unit') and not values.get('technical_price_unit'):
                values['technical_price_unit'] = values['price_unit']

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == 'purchase':
                msg = _("Extra line with %s ", line.product_id.display_name)
                line.order_id.message_post(body=msg)
        return lines

    def write(self, vals):
        values = vals
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a purchase order line. Instead you should delete the current line and create a new line of the proper type."))

        if 'product_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit')
            for line in self:
                if (
                    line.order_id.state == "purchase"
                    and float_compare(line.product_qty, values["product_qty"], precision_digits=precision) != 0
                ):
                    line.order_id.message_post_with_source(
                        'purchase.track_po_line_template',
                        render_values={'line': line, 'product_qty': values['product_qty']},
                        subtype_xmlid='mail.mt_note',
                    )

        if 'qty_received' in values:
            for line in self:
                line._track_qty_received(values['qty_received'])
        return super().write(values)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_purchase(self):
        for line in self:
            if line.order_id.state == 'purchase' and line.display_type not in ['line_section', 'line_subsection', 'line_note']:
                state_description = {state_desc[0]: state_desc[1] for state_desc in self._fields['state']._description_selection(self.env)}
                raise UserError(_('Cannot delete a purchase order line which is in state “%s”.', state_description.get(line.state)))

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Return the datetime value to use as Schedule Date (``date_planned``) for
           PO Lines that correspond to the given product.seller_ids,
           when ordered at `date_order_str`.

           :param Model seller: used to fetch the delivery delay (if no seller
                                is provided, the delay is 0)
           :param Model po: purchase.order, necessary only if the PO line is
                            not yet attached to a PO.
           :rtype: datetime
           :return: desired Schedule Date for the PO line
        """
        date_order = po.date_order if po else self.order_id.date_order
        if date_order:
            return date_order + relativedelta(days=seller.delay if seller else 0)
        else:
            return datetime.today() + relativedelta(days=seller.delay if seller else 0)

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution

    @api.onchange('product_id')
    def onchange_product_id(self):
        # TODO: Remove when onchanges are replaced with computes
        if not self.product_id or (self.env.context.get('origin_po_id') and self.product_qty):
            return

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.price_unit = self.product_qty = self.technical_price_unit = 0.0

        self._product_id_change()

        self._suggest_quantity()

    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_uom_id = self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=None,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)

        self._compute_tax_id()

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids', 'product_id.seller_ids', 'product_id.seller_ids.product_uom_id')
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids | line.product_id.seller_ids.product_uom_id

    @api.depends('product_qty', 'product_uom_id', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id or self.env.context.get('skip_uom_conversion') or (line.technical_price_unit != line.price_unit):
                continue
            params = line._get_select_sellers_params()

            if line.selected_seller_id or not line.date_planned:
                line.date_planned = line._get_date_planned(line.selected_seller_id).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not line.selected_seller_id:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom_id == line._origin.product_uom_id:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                line.discount = 0
                po_line_uom = line.product_uom_id or line.product_id.uom_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.tax_ids,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = line.technical_price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')))

            elif line.selected_seller_id:
                price_unit = line.env['account.tax']._fix_tax_included_price_company(line.selected_seller_id.price, line.product_id.supplier_taxes_id, line.tax_ids, line.company_id) if line.selected_seller_id else 0.0
                price_unit = line.selected_seller_id.currency_id._convert(price_unit, line.currency_id, line.company_id, line.date_order or fields.Date.context_today(line), False)
                price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')))
                line.price_unit = line.technical_price_unit = line.selected_seller_id.product_uom_id._compute_price(price_unit, line.product_uom_id)
                line.discount = line.selected_seller_id.discount or 0.0

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers(params=params)
            product_ctx = {'seller_id': None, 'partner_id': None, 'lang': get_lang(line.env, line.partner_id.lang).code}
            default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': line.selected_seller_id.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))

    @api.depends('product_id')
    def _compute_translated_product_name(self):
        for line in self:
            line.translated_product_name = line.product_id.with_context(
                lang=line.partner_id.lang,
            ).display_name

    @api.depends('product_uom_id', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id and line.product_id.uom_id != line.product_uom_id:
                line.product_uom_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty

    def _get_gross_price_unit(self):
        self.ensure_one()
        price_unit = self.price_unit
        if self.discount:
            price_unit = price_unit * (1 - self.discount / 100)
        if self.tax_ids:
            qty = self.product_qty or 1
            price_unit = self.tax_ids.compute_all(
                price_unit,
                currency=self.order_id.currency_id,
                quantity=qty,
                rounding_method='round_globally',
            )['total_void']
            price_unit = price_unit / qty
        if self.product_uom_id.id != self.product_id.uom_id.id:
            price_unit *= self.product_id.uom_id.factor / self.product_uom_id.factor
        return price_unit

    def _compute_parent_id(self):
        purchase_order_lines = set(self)
        for order, lines in self.grouped('order_id').items():
            if not order:
                lines.parent_id = False
                continue
            last_section = False
            last_sub = False
            for line in order.order_line.sorted('sequence'):
                if line.display_type == 'line_section':
                    last_section = line
                    if line in purchase_order_lines:
                        line.parent_id = False
                    last_sub = False
                elif line.display_type == 'line_subsection':
                    if line in purchase_order_lines:
                        line.parent_id = last_section
                    last_sub = line
                elif line in purchase_order_lines:
                    line.parent_id = last_sub or last_section

    def action_add_from_catalog(self):
        order = self.env['purchase.order'].browse(self.env.context.get('order_id'))
        return order.with_context(child_field='order_line').action_add_from_catalog()

    def _suggest_quantity(self):
        ''' Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return
        date = self.order_id.date_order and self.order_id.date_order.date() or fields.Date.context_today(self)
        seller_min_qty = self.product_id.seller_ids\
            .filtered(lambda r: r.partner_id == self.order_id.partner_id and
                      (not r.product_id or r.product_id == self.product_id) and
                      (not r.date_start or r.date_start <= date) and
                      (not r.date_end or r.date_end >= date))\
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom_id = seller_min_qty[0].product_uom_id
        else:
            self.product_qty = 1.0

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Return information about purchase order lines in `self`.

        If `self` is empty, this method returns only the default value(s) needed for the product
        catalog. In this case, the quantity that equals 0.

        Otherwise, it returns a quantity and a price based on the product of the POL(s) and whether
        the product is read-only or not.

        A product is considered read-only if the order is considered read-only (see
        ``PurchaseOrder._is_readonly`` for more details) or if `self` contains multiple records.

        Note: This method cannot be called with multiple records that have different products linked.

        :raise odoo.exceptions.ValueError: ``len(self.product_id) != 1``
        :rtype: dict
        :return: A dict with the following structure:
            {
                'quantity': float,
                'price': float,
                'readOnly': bool,
                'uomDisplayName': String,
                'packaging': dict,
                'warning': String,
            }
        """
        if len(self) == 1:
            catalog_info = self.order_id._get_product_price_and_data(self.product_id)
            catalog_info.update(
                quantity=self.product_qty,
                price=self.price_unit * (1 - self.discount / 100),
                readOnly=self.order_id._is_readonly(),
            )
            if self.product_id.uom_id != self.product_uom_id:
                catalog_info['uomDisplayName'] = self.product_uom_id.display_name
            return catalog_info
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            catalog_info = order_line.order_id._get_product_price_and_data(order_line.product_id)
            catalog_info['quantity'] = sum(self.mapped(
                lambda line: line.product_uom_id._compute_quantity(
                    qty=line.product_qty,
                    to_unit=line.product_id.uom_id,
            )))
            catalog_info['readOnly'] = True
            return catalog_info
        return {'quantity': 0}

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()

        res = {
            'display_type': self.display_type or 'product',
            'name': self.env['account.move.line']._get_journal_items_full_name(self.name, self.product_id.display_name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': -self.qty_to_invoice if move and move.move_type == 'in_refund' else self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.tax_ids.ids)],
            'purchase_line_id': self.id,
            'is_downpayment': self.is_downpayment,
        }
        return res

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_qty', 'product_uom_id', 'tax_ids', 'date_planned']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.onchange_product_id()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, partner_id, po):
        values = self.env.context.get('procurement_values', {})
        uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_id, rounding_method='HALF-UP')
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        today = fields.Date.today()
        seller = product_id.with_company(company_id)._select_seller(
            partner_id=partner_id,
            quantity=product_qty if values.get('force_uom') else uom_po_qty,
            date=po.date_order and max(po.date_order.date(), today) or today,
            uom_id=product_uom if values.get('force_uom') else product_id.uom_id,
            params={'force_uom': values.get('force_uom')}
        )
        if seller and (seller.product_uom_id or seller.product_tmpl_id.uom_id) != product_uom:
            uom_po_qty = product_id.uom_id._compute_quantity(uom_po_qty, seller.product_uom_id, rounding_method='HALF-UP')

        tax_domain = self.env['account.tax']._check_company_domain(company_id)
        product_taxes = product_id.supplier_taxes_id.filtered_domain(tax_domain)
        taxes = po.fiscal_position_id.map_tax(product_taxes)

        if seller:
            price_unit = (seller.product_uom_id._compute_price(seller.price, product_uom) if product_uom else seller.price)
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
            price_unit, product_taxes, taxes, company_id)
        else:
            price_unit = 0
        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today())

        product_lang = product_id.with_prefetch().with_context(
            lang=partner_id.lang,
            partner_id=partner_id.id,
        )
        name = product_lang.with_context(seller_id=seller.id).display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        date_planned = self.order_id.date_planned or self._get_date_planned(seller, po=po)
        discount = seller.discount or 0.0

        return {
            'name': name,
            'product_qty': product_qty if product_uom else uom_po_qty,
            'product_id': product_id.id,
            'product_uom_id': product_uom.id or seller.product_uom_id.id,
            'price_unit': price_unit,
            'date_planned': date_planned,
            'tax_ids': [(6, 0, taxes.ids)],
            'order_id': po.id,
            'discount': discount,
        }

    def _convert_to_middle_of_day(self, date):
        """Return a datetime which is the noon of the input date(time) according
        to order user's time zone, convert to UTC time.
        """
        return self.order_id.get_order_timezone().localize(datetime.combine(date, time(12))).astimezone(UTC).replace(tzinfo=None)

    @api.model
    def _date_in_the_past(self):
        if not 'accrual_entry_date' in self.env.context:
            return False
        accrual_date = fields.Date.from_string(self.env.context['accrual_entry_date'])
        return accrual_date < fields.Date.today()

    def _update_date_planned(self, updated_date):
        self.date_planned = updated_date

    def _track_qty_received(self, new_qty):
        self.ensure_one()
        # don't track anything when coming from the accrued expense entry wizard, as it is only computing fields at a past date to get relevant amounts
        # and doesn't actually change anything to the current record
        if  self.env.context.get('accrual_entry_date'):
            return
        if new_qty != self.qty_received and self.order_id.state == 'purchase':
            self.order_id.message_post_with_source(
                'purchase.track_po_line_qty_received_template',
                render_values={'line': self, 'qty_received': new_qty},
                subtype_xmlid='mail.mt_note',
            )

    def _validate_analytic_distribution(self):
        for line in self:
            if line.display_type:
                continue
            line._validate_distribution(
                product=line.product_id.id,
                business_domain='purchase_order',
                company_id=line.company_id.id,
            )

    def action_open_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.order_id.id,
            'view_mode': 'form',
        }

    def _merge_po_line(self, rfq_line):
        self.product_qty += rfq_line.product_qty
        self.price_unit = min(self.price_unit, rfq_line.price_unit)

    def _get_select_sellers_params(self):
        self.ensure_one()
        return {
            "order_id": self.order_id,
            "force_uom": True,
        }

    def get_parent_section_line(self):
        if not self.display_type and self.parent_id.display_type == 'line_subsection':
            return self.parent_id.parent_id

        return self.parent_id


# FILEPATH: odoo/addons/purchase/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'
    po_lock = fields.Selection([
        ('edit', 'Allow to edit purchase orders'),
        ('lock', 'Confirmed purchase orders are not editable')
        ], string="Purchase Order Modification", default="edit",
        help='Purchase Order Modification used when you want to purchase order editable after confirm')
    po_double_validation = fields.Selection([
        ('one_step', 'Confirm purchase orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a purchase order')
        ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for purchases")
    po_double_validation_amount = fields.Monetary(string='Double validation amount', default=5000,
        help="Minimum amount for which a double validation is required")


# FILEPATH: odoo/addons/purchase/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    lock_confirmed_po = fields.Boolean("Lock Confirmed Orders", default=lambda self: self.env.company.po_lock == 'lock')
    po_lock = fields.Selection(related='company_id.po_lock', string="Purchase Order Modification *", readonly=False)
    po_order_approval = fields.Boolean("Purchase Order Approval", default=lambda self: self.env.company.po_double_validation == 'two_step')
    po_double_validation = fields.Selection(related='company_id.po_double_validation', string="Levels of Approvals *", readonly=False)
    po_double_validation_amount = fields.Monetary(related='company_id.po_double_validation_amount', string="Minimum Amount", currency_field='company_currency_id', readonly=False)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    group_warning_purchase = fields.Boolean("Purchase Warnings", implied_group='purchase.group_warning_purchase')
    module_account_3way_match = fields.Boolean("3-way matching: purchases, receptions and bills")
    module_purchase_requisition = fields.Boolean("Purchase Agreements")
    module_purchase_product_matrix = fields.Boolean("Purchase Grid Entry")
    group_send_reminder = fields.Boolean("Receipt Reminder", implied_group='purchase.group_send_reminder', default=True,
        help="Allow automatically send email to remind your vendor the receipt date")
    @api.onchange('group_product_variant')
    def _onchange_group_product_variant_purchase(self):
        pass  # shrunk (lines 24-28)
    @api.onchange('module_purchase_product_matrix')
    def _onchange_module_purchase_product_matrix(self):
        pass  # shrunk (lines 30-35)
    def set_values(self):
        pass  # shrunk (lines 37-44)


# FILEPATH: odoo/addons/purchase/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'
    def _compute_purchase_order_count(self):
        pass  # shrunk (lines 9-29)
    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency", company_dependent=True,
        help="This currency will be used for purchases from the current partner")
    purchase_order_count = fields.Integer(
        string="Purchase Order Count",
        groups='purchase.group_purchase_user',
        compute='_compute_purchase_order_count',
    )
    purchase_warn_msg = fields.Text('Message for Purchase Order')
    receipt_reminder_email = fields.Boolean('Receipt Reminder', company_dependent=True,
        help="Automatically send a confirmation email to the vendor X days before the expected receipt date, asking him to confirm the exact date.")
    reminder_date_before_receipt = fields.Integer('Days Before Receipt', company_dependent=True,
        help="Number of days to send reminder email before the promised receipt date")
    buyer_id = fields.Many2one('res.users', string='Buyer')
    def _compute_application_statistics_hook(self):
        pass  # shrunk (lines 47-54)


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
