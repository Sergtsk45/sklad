Role: Senior Odoo Architect enforcing OCA standards.
Context: The following is a codebase dump produced by the akaidoo CLI.
Command: /home/serg45/.local/bin/akaidoo addon sale -c akaidoo.conf --shrink=hard -B 30k -o custom_addons/ai_assistant/static/knowledge/generated/sale_context.md
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
    fiscal_position_id = fields.Many2one('account.fiscal.position', compute='_compute_fiscal_position_id', store=True)
    reversed_entry_id = fields.Many2one(comodel_name='account.move')
    reversal_move_ids = fields.One2many('account.move', 'reversed_entry_id')
    invoice_vendor_bill_id = fields.Many2one('account.move', store=False)
    invoice_user_id = fields.Many2one(comodel_name='res.users', compute='_compute_invoice_default_sale_person', store=True)
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


# FILEPATH: odoo/addons/account_payment/__manifest__.py
{   'data': [   'data/ir_config_parameter.xml',
                'security/ir.model.access.csv',
                'security/ir_rules.xml',
                'views/account_payment_menus.xml',
                'views/account_portal_templates.xml',
                'views/account_move_views.xml',
                'views/account_journal_views.xml',
                'views/account_payment_views.xml',
                'views/payment_form_templates.xml',
                'views/payment_provider_views.xml',
                'views/payment_transaction_views.xml',
                'wizards/account_payment_register_views.xml',
                'wizards/payment_link_wizard_views.xml',
                'wizards/payment_refund_wizard_views.xml',
                'wizards/res_config_settings_views.xml'],
    'depends': ['account', 'payment'],
    'name': 'Payment - Account',
    'post_init_hook': 'post_init_hook',
    'summary': 'Enable customers to pay invoices on the portal and post '
               'payments when transactions are processed.',
    'uninstall_hook': 'uninstall_hook'}

# FILEPATH: odoo/addons/account_payment/models/account_journal.py
class AccountJournal(models.Model):
    _inherit = "account.journal"


# FILEPATH: odoo/addons/account_payment/models/account_move.py
class AccountMove(models.Model):
    _inherit = 'account.move'
    transaction_ids = fields.Many2many(comodel_name='payment.transaction', relation='account_invoice_transaction_rel', column1='invoice_id', column2='transaction_id')
    authorized_transaction_ids = fields.Many2many(comodel_name='payment.transaction', compute='_compute_authorized_transaction_ids')
    # Shrunk non computed fields: transaction_ids
    # Shrunk computed_fields: authorized_transaction_ids (_compute_authorized_transaction_ids), transaction_count (_compute_transaction_count), amount_paid (_compute_amount_paid)


# FILEPATH: odoo/addons/account_payment/models/account_payment.py
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    payment_transaction_id = fields.Many2one(comodel_name='payment.transaction')
    source_payment_id = fields.Many2one(comodel_name='account.payment', related='payment_transaction_id.source_transaction_id.payment_id', store=True)
    # Shrunk non computed fields: payment_transaction_id, payment_token_id, source_payment_id
    # Shrunk computed_fields: amount_available_for_refund (_compute_amount_available_for_refund), suitable_payment_token_ids (_compute_suitable_payment_token_ids), use_electronic_payment_method (_compute_use_electronic_payment_method), refunds_count (_compute_refunds_count)


# FILEPATH: odoo/addons/account_payment/models/account_payment_method.py
class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'


# FILEPATH: odoo/addons/account_payment/models/account_payment_method_line.py
class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"


# FILEPATH: odoo/addons/account_payment/models/payment_provider.py
class PaymentProvider(models.Model):
    _inherit = 'payment.provider'


# FILEPATH: odoo/addons/account_payment/models/payment_transaction.py
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    payment_id = fields.Many2one(comodel_name='account.payment')
    invoice_ids = fields.Many2many(comodel_name='account.move', relation='account_invoice_transaction_rel', column1='transaction_id', column2='invoice_id')
    # Shrunk non computed fields: payment_id, invoice_ids
    # Shrunk computed_fields: invoices_count (_compute_invoices_count)


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


# FILEPATH: odoo/addons/payment/__manifest__.py
{   'data': [   'data/ir_actions_server_data.xml',
                'data/payment_method_data.xml',
                'data/payment_provider_data.xml',
                'data/payment_cron.xml',
                'views/express_checkout_templates.xml',
                'views/payment_form_templates.xml',
                'views/portal_templates.xml',
                'views/payment_provider_views.xml',
                'views/payment_method_views.xml',
                'views/payment_transaction_views.xml',
                'views/payment_token_views.xml',
                'views/res_partner_views.xml',
                'security/ir.model.access.csv',
                'security/payment_security.xml',
                'wizards/payment_capture_wizard_views.xml',
                'wizards/payment_link_wizard_views.xml'],
    'depends': ['onboarding', 'portal'],
    'name': 'Payment Engine',
    'summary': 'The payment engine used by payment provider modules.'}

# FILEPATH: odoo/addons/payment/const.py
_lt = LazyTranslate(__name__, default_lang='en_US')
SENSITIVE_KEYS = set()
COUNTRY_NUMERIC_CODES = {
    'AF': '004',
    'AL': '008',
    'DZ': '012',
    'AS': '016',
    'AD': '020',
    'AO': '024',
    'AG': '028',
    'AZ': '031',
    'AR': '032',
    'AU': '036',
    'AT': '040',
    'BS': '044',
    'BH': '048',
    'BD': '050',
    'AM': '051',
    'BB': '052',
    'BE': '056',
    'BM': '060',
    'BT': '064',
    'BO': '068',
    'BA': '070',
    'BW': '072',
    'BV': '074',
    'BR': '076',
    'BZ': '084',
    'IO': '086',
    'SB': '090',
    'VG': '092',
    'BN': '096',
    'BG': '100',
    'MM': '104',
    'BI': '108',
    'BY': '112',
    'KH': '116',
    'CM': '120',
    'CA': '124',
    'CV': '132',
    'KY': '136',
    'CF': '140',
    'LK': '144',
    'TD': '148',
    'CL': '152',
    'CN': '156',
    'TW': '158',
    'CX': '162',
    'CC': '166',
    'CO': '170',
    'KM': '174',
    'YT': '175',
    'CG': '178',
    'CD': '180',
    'CK': '184',
    'CR': '188',
    'HR': '191',
    'CU': '192',
    'CY': '196',
    'CZ': '203',
    'DK': '208',
    'DM': '212',
    'DO': '214',
    'EC': '218',
    'SV': '222',
    'GQ': '226',
    'ET': '231',
    'ER': '232',
    'EE': '233',
    'FO': '234',
    'FK': '238',
    'GS': '239',
    'FJ': '242',
    'FI': '246',
    'AX': '248',
    'FR': '250',
    'GF': '254',
    'PF': '258',
    'TF': '260',
    'DJ': '262',
    'GA': '266',
    'GE': '268',
    'GM': '270',
    'PS': '275',
    'DE': '276',
    'GH': '288',
    'GI': '292',
    'KI': '296',
    'GR': '300',
    'GL': '304',
    'GD': '308',
    'GP': '312',
    'GU': '316',
    'GT': '320',
    'GN': '324',
    'GY': '328',
    'HT': '332',
    'HM': '334',
    'VA': '336',
    'HN': '340',
    'HK': '344',
    'HU': '348',
    'IS': '352',
    'IN': '356',
    'ID': '360',
    'IR': '364',
    'IQ': '368',
    'IE': '372',
    'IL': '376',
    'IT': '380',
    'CI': '384',
    'JM': '388',
    'JP': '392',
    'KZ': '398',
    'JO': '400',
    'KE': '404',
    'KP': '408',
    'KR': '410',
    'KW': '414',
    'KG': '417',
    'LA': '418',
    'LB': '422',
    'LS': '426',
    'LV': '428',
    'LR': '430',
    'LY': '434',
    'LI': '438',
    'LT': '440',
    'LU': '442',
    'MO': '446',
    'MG': '450',
    'MW': '454',
    'MY': '458',
    'MV': '462',
    'ML': '466',
    'MT': '470',
    'MQ': '474',
    'MR': '478',
    'MU': '480',
    'MX': '484',
    'MC': '492',
    'MN': '496',
    'MD': '498',
    'ME': '499',
    'MS': '500',
    'MA': '504',
    'MZ': '508',
    'OM': '512',
    'NA': '516',
    'NR': '520',
    'NP': '524',
    'NL': '528',
    'CW': '531',
    'AW': '533',
    'SX': '534',
    'BQ': '535',
    'NC': '540',
    'VU': '548',
    'NZ': '554',
    'NI': '558',
    'NE': '562',
    'NG': '566',
    'NU': '570',
    'NF': '574',
    'NO': '578',
    'MP': '580',
    'UM': '581',
    'FM': '583',
    'MH': '584',
    'PW': '585',
    'PK': '586',
    'PA': '591',
    'PG': '598',
    'PY': '600',
    'PE': '604',
    'PH': '608',
    'PN': '612',
    'PL': '616',
    'PT': '620',
    'GW': '624',
    'TL': '626',
    'PR': '630',
    'QA': '634',
    'RE': '638',
    'RO': '642',
    'RU': '643',
    'RW': '646',
    'BL': '652',
    'SH': '654',
    'KN': '659',
    'AI': '660',
    'LC': '662',
    'MF': '663',
    'PM': '666',
    'VC': '670',
    'SM': '674',
    'ST': '678',
    'SA': '682',
    'SN': '686',
    'RS': '688',
    'SC': '690',
    'SL': '694',
    'SG': '702',
    'SK': '703',
    'VN': '704',
    'SI': '705',
    'SO': '706',
    'ZA': '710',
    'ZW': '716',
    'ES': '724',
    'SS': '728',
    'SD': '729',
    'EH': '732',
    'SR': '740',
    'SZ': '748',
    'SE': '752',
    'CH': '756',
    'SY': '760',
    'TJ': '762',
    'TH': '764',
    'TG': '768',
    'TK': '772',
    'TO': '776',
    'TT': '780',
    'AE': '784',
    'TN': '788',
    'TR': '792',
    'TM': '795',
    'TC': '796',
    'TV': '798',
    'UG': '800',
    'UA': '804',
    'MK': '807',
    'EG': '818',
    'GB': '826',
    'GG': '831',
    'JE': '832',
    'IM': '833',
    'TZ': '834',
    'US': '840',
    'VI': '850',
    'BF': '854',
    'UY': '858',
    'UZ': '860',
    'VE': '862',
    'WF': '876',
    'WS': '882',
    'YE': '887',
    'ZM': '894'
}
CURRENCY_MINOR_UNITS = {
    'ADF': 2,
    'ADP': 0,
    'AED': 2,
    'AFA': 2,
    'AFN': 2,
    'ALL': 2,
    'AMD': 2,
    'ANG': 2,
    'AOA': 2,
    'AOK': 0,
    'AON': 0,
    'AOR': 0,
    'ARA': 2,
    'ARL': 2,
    'ARP': 2,
    'ARS': 2,
    'ATS': 2,
    'AUD': 2,
    'AWG': 2,
    'AYM': 0,
    'AZM': 2,
    'AZN': 2,
    'BAD': 2,
    'BAM': 2,
    'BBD': 2,
    'BDS': 2,
    'BDT': 2,
    'BEF': 2,
    'BGL': 2,
    'BGN': 2,
    'BHD': 3,
    'BIF': 0,
    'BMD': 2,
    'BND': 2,
    'BOB': 2,
    'BOP': 2,
    'BOV': 2,
    'BRB': 2,
    'BRC': 2,
    'BRE': 2,
    'BRL': 2,
    'BRN': 2,
    'BRR': 2,
    'BSD': 2,
    'BTN': 2,
    'BWP': 2,
    'BYB': 2,
    'BYN': 2,
    'BYR': 0,
    'BZD': 2,
    'CAD': 2,
    'CDF': 2,
    'CHC': 2,
    'CHE': 2,
    'CHF': 2,
    'CHW': 2,
    'CLF': 4,
    'CLP': 0,
    'CNH': 2,
    'CNT': 2,
    'CNY': 2,
    'COP': 2,
    'COU': 2,
    'CRC': 2,
    'CSD': 2,
    'CUC': 2,
    'CUP': 2,
    'CVE': 2,
    'CYP': 2,
    'CZK': 2,
    'DEM': 2,
    'DJF': 0,
    'DKK': 2,
    'DOP': 2,
    'DZD': 2,
    'ECS': 0,
    'ECV': 2,
    'EEK': 2,
    'EGP': 2,
    'ERN': 2,
    'ESP': 0,
    'ETB': 2,
    'EUR': 2,
    'FIM': 2,
    'FJD': 2,
    'FKP': 2,
    'FRF': 2,
    'GBP': 2,
    'GEK': 0,
    'GEL': 2,
    'GGP': 2,
    'GHC': 2,
    'GHP': 2,
    'GHS': 2,
    'GIP': 2,
    'GMD': 2,
    'GNF': 0,
    'GTQ': 2,
    'GWP': 2,
    'GYD': 2,
    'HKD': 2,
    'HNL': 2,
    'HRD': 2,
    'HRK': 2,
    'HTG': 2,
    'HUF': 2,
    'IDR': 2,
    'IEP': 2,
    'ILR': 2,
    'ILS': 2,
    'IMP': 2,
    'INR': 2,
    'IQD': 3,
    'IRR': 2,
    'ISJ': 2,
    'ISK': 0,
    'ITL': 0,
    'JEP': 2,
    'JMD': 2,
    'JOD': 3,
    'JPY': 0,
    'KES': 2,
    'KGS': 2,
    'KHR': 2,
    'KID': 2,
    'KMF': 0,
    'KPW': 2,
    'KRW': 0,
    'KWD': 3,
    'KYD': 2,
    'KZT': 2,
    'LAK': 2,
    'LBP': 2,
    'LKR': 2,
    'LRD': 2,
    'LSL': 2,
    'LTL': 2,
    'LTT': 2,
    'LUF': 2,
    'LVL': 2,
    'LVR': 2,
    'LYD': 3,
    'MAD': 2,
    'MAF': 2,
    'MCF': 2,
    'MDL': 2,
    'MGA': 2,
    'MGF': 0,
    'MKD': 2,
    'MMK': 2,
    'MNT': 2,
    'MOP': 2,
    'MRO': 2,
    'MRU': 2,
    'MTL': 2,
    'MUR': 2,
    'MVR': 2,
    'MWK': 2,
    'MXN': 2,
    'MXV': 2,
    'MYR': 2,
    'MZE': 2,
    'MZM': 2,
    'MZN': 2,
    'NAD': 2,
    'NGN': 2,
    'NIC': 2,
    'NIO': 2,
    'NIS': 2,
    'NLG': 2,
    'NOK': 2,
    'NPR': 2,
    'NTD': 2,
    'NZD': 2,
    'OMR': 3,
    'PAB': 2,
    'PEN': 2,
    'PES': 2,
    'PGK': 2,
    'PHP': 2,
    'PKR': 2,
    'PLN': 2,
    'PLZ': 2,
    'PRB': 2,
    'PTE': 0,
    'PYG': 0,
    'QAR': 2,
    'RHD': 2,
    'RMB': 2,
    'ROL': 0,
    'RON': 2,
    'RSD': 2,
    'RUB': 2,
    'RUR': 2,
    'RWF': 0,
    'SAR': 2,
    'SBD': 2,
    'SCR': 2,
    'SDD': 2,
    'SDG': 2,
    'SEK': 2,
    'SGD': 2,
    'SHP': 2,
    'SIT': 2,
    'SKK': 2,
    'SLE': 2,
    'SLL': 2,
    'SLS': 2,
    'SML': 0,
    'SOS': 2,
    'SRD': 2,
    'SRG': 2,
    'SSP': 2,
    'STD': 2,
    'STG': 2,
    'STN': 2,
    'SVC': 2,
    'SYP': 2,
    'SZL': 2,
    'THB': 2,
    'TJR': 0,
    'TJS': 2,
    'TMM': 2,
    'TMT': 2,
    'TND': 3,
    'TOP': 2,
    'TPE': 0,
    'TRL': 0,
    'TRY': 2,
    'TTD': 2,
    'TVD': 2,
    'TWD': 2,
    'TZS': 2,
    'UAH': 2,
    'UAK': 2,
    'UGX': 0,
    'USD': 2,
    'USN': 2,
    'USS': 2,
    'UYI': 0,
    'UYN': 2,
    'UYU': 2,
    'UYW': 4,
    'UZS': 2,
    'VAL': 0,
    'VEB': 2,
    'VED': 2,
    'VEF': 2,
    'VES': 2,
    'VND': 0,
    'VUV': 0,
    'WST': 2,
    'XAF': 0,
    'XCD': 2,
    'XEU': 0,
    'XOF': 0,
    'XPF': 0,
    'YER': 2,
    'YUD': 2,
    'YUG': 2,
    'YUM': 2,
    'YUN': 2,
    'YUO': 2,
    'YUR': 2,
    'ZAL': 2,
    'ZAR': 2,
    'ZMK': 2,
    'ZMW': 2,
    'ZRN': 2,
    'ZRZ': 2,
    'ZWB': 2,
    'ZWC': 2,
    'ZWD': 2,
    'ZWL': 2,
    'ZWN': 2,
    'ZWR': 2
}
REPORT_REASONS_MAPPING = {
    'exceed_max_amount': _lt("maximum amount exceeded"),
    'express_checkout_not_supported': _lt("express checkout not supported"),
    'incompatible_country': _lt("incompatible country"),
    'incompatible_currency': _lt("incompatible currency"),
    'incompatible_website': _lt("incompatible website"),
    'manual_capture_not_supported': _lt("manual capture not supported"),
    'provider_not_available': _lt("no supported provider available"),
    'tokenization_not_supported': _lt("tokenization not supported"),
    'validation_not_supported': _lt("tokenization without payment no supported"),
}


# FILEPATH: odoo/addons/payment/logging.py
class SensitiveDataFilter(logging.Filter):
    pass  # pruned


# FILEPATH: odoo/addons/payment/models/ir_http.py
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'


# FILEPATH: odoo/addons/payment/models/payment_method.py
class PaymentMethod(models.Model):
    _name = 'payment.method'


# FILEPATH: odoo/addons/payment/models/payment_provider.py
_logger = get_payment_logger(__name__, sensitive_keys=SENSITIVE_KEYS)
class PaymentProvider(models.Model):
    _name = 'payment.provider'


# FILEPATH: odoo/addons/payment/models/payment_token.py
class PaymentToken(models.Model):
    _name = 'payment.token'


# FILEPATH: odoo/addons/payment/models/payment_transaction.py
_logger = get_payment_logger(__name__, sensitive_keys=SENSITIVE_KEYS)
class PaymentTransaction(models.Model):
    _name = 'payment.transaction'
    _description = 'Payment Transaction'
    _order = 'id desc'
    _rec_name = 'reference'
    source_transaction_id = fields.Many2one(comodel_name='payment.transaction')
    child_transaction_ids = fields.One2many(comodel_name='payment.transaction', inverse_name='source_transaction_id')
    _reference_uniq = models.Constraint(
        'unique(reference)',
        'Reference must be unique!')
    # Shrunk non computed fields: provider_id, provider_code, company_id, payment_method_id, payment_method_code, reference, provider_reference, amount, currency_id, token_id, state, state_message, last_state_change, operation, is_live, source_transaction_id, child_transaction_ids, is_post_processed, tokenize, landing_route, partner_id, partner_name, partner_lang, partner_email, partner_address, partner_zip, partner_city, partner_state_id, partner_country_id, partner_phone
    # Shrunk computed_fields: primary_payment_method_id (_compute_primary_payment_method_id), refunds_count (_compute_refunds_count)


# FILEPATH: odoo/addons/payment/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'


# FILEPATH: odoo/addons/payment/models/res_country.py
class ResCountry(models.Model):
    _inherit = 'res.country'


# FILEPATH: odoo/addons/payment/models/res_partner.py
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


# FILEPATH: odoo/addons/sale/__init__.py
def _post_init_hook(env):
    pass  # shrunk (lines 13-15)

def _synchronize_crons(env):
    pass  # shrunk (lines 18-21)

def _setup_downpayment_account(env):
    pass  # shrunk (lines 24-33)


# FILEPATH: odoo/addons/sale/__manifest__.py

{
    'name': 'Sales',
    'version': '1.2',
    'category': 'Sales/Sales',
    'summary': 'Sales internal machinery',
    'description': """
This module contains all the common features of Sales Management and eCommerce.
    """,
    'depends': [
        'sales_team',
        'account_payment',  # -> account, payment, portal
        'utm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/ir_rules.xml',

        'report/account_invoice_report_views.xml',
        'report/ir_actions_report_templates.xml',
        'report/ir_actions_report.xml',
        'report/sale_report_views.xml',

        'data/ir_cron.xml',
        'data/ir_sequence_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/mail_template_data.xml',
        'data/sale_tour.xml',
        'data/ir_config_parameter.xml', # Needs mail_template_data

        'wizard/account_accrued_orders_wizard_views.xml',
        'wizard/mass_cancel_orders_views.xml',
        'wizard/payment_link_wizard_views.xml',
        'wizard/res_config_settings_views.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'wizard/sale_order_discount_views.xml',

        # Define sale order views before their references
        'views/sale_order_views.xml',

        'views/account_views.xml',
        'views/crm_team_views.xml',
        'views/mail_activity_views.xml',
        'views/mail_activity_plan_views.xml',
        'views/payment_views.xml',
        'views/product_document_views.xml',
        'views/product_pricelist_item_views.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_portal_templates.xml',
        'views/utm_campaign_views.xml',

        'views/sale_menus.xml',  # Last because referencing actions defined in previous files
    ],
    'demo': [
        'data/product_demo.xml',
        'data/sale_demo.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'sale/static/src/scss/sale_onboarding.scss',
            'sale/static/src/js/badge_extra_price/*',
            'sale/static/src/js/sale_action_helper/*',
            'sale/static/src/js/combo_configurator_dialog/*',
            'sale/static/src/js/models/*',
            'sale/static/src/js/product/*',
            'sale/static/src/js/product_card/*',
            'sale/static/src/js/product_configurator_dialog/*',
            'sale/static/src/js/product_list/*',
            'sale/static/src/js/product_template_attribute_line/*',
            'sale/static/src/js/quantity_buttons/*',
            'sale/static/src/js/sale_order_line_field/*',
            'sale/static/src/js/sale_progressbar_field.js',
            'sale/static/src/js/tours/sale.js',
            'sale/static/src/js/upload_rfq_cog_menu/*',
            'sale/static/src/js/sale_product_field.js',
            'sale/static/src/js/sale_product_field.scss',
            'sale/static/src/js/sale_utils.js',
            'sale/static/src/xml/**/*',
            'sale/static/src/views/**/*',
        ],
        'web.assets_frontend': [
            'sale/static/src/interactions/**/*',
            'sale/static/src/scss/sale_portal.scss',
        ],
        'web.assets_tests': [
            'sale/static/tests/tours/**/*',
            'sale/static/src/js/tours/combo_configurator_tour_utils.js',
            'sale/static/src/js/tours/product_configurator_tour_utils.js',
            'sale/static/src/js/tours/tour_utils.js',
        ],
        'web.assets_unit_tests': [
            'sale/static/tests/mock_server/**/*',
            'sale/static/tests/sale_test_helpers.js',
            'sale/static/tests/**/*.test.js',
        ],
        'web.report_assets_common': [
            'sale/static/src/scss/sale_report.scss',
        ],
    },
    'post_init_hook': '_post_init_hook',
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}


# FILEPATH: odoo/addons/sale/const.py
PARAM_CRON_MAPPING = {
    'sale.async_emails': 'sale.send_pending_emails_cron',
    'sale.automatic_invoice': 'sale.send_invoice_cron',
}


# FILEPATH: odoo/addons/sale/models/account_move.py
class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'utm.mixin']

    team_id = fields.Many2one(
        'crm.team', string='Sales Team',
        compute='_compute_team_id', store=True, readonly=False,
        ondelete="set null", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    # UTMs - enforcing the fact that we want to 'set null' when relation is unlinked
    campaign_id = fields.Many2one(ondelete='set null')
    medium_id = fields.Many2one(ondelete='set null')
    source_id = fields.Many2one(ondelete='set null')
    sale_order_count = fields.Integer(compute="_compute_origin_so_count", string='Sale Order Count', compute_sudo=True)
    sale_warning_text = fields.Text(
        "Sale Warning",
        help="Internal warning for the partner or the products as set by the user.",
        compute="_compute_sale_warning_text")

    def unlink(self):
        downpayment_lines = self.mapped('line_ids.sale_line_ids').filtered(lambda line: line.is_downpayment and line.invoice_lines <= self.mapped('line_ids'))
        res = super(AccountMove, self).unlink()
        if downpayment_lines:
            downpayment_lines.unlink()
        return res

    @api.depends('invoice_user_id')
    def _compute_team_id(self):
        sale_moves = self.filtered(lambda move: move.is_sale_document(include_receipts=True))
        for ((user_id, company_id), moves) in groupby(
            sale_moves,
            key=lambda m: (m.invoice_user_id.id, m.company_id.id)
        ):
            self.env['account.move'].concat(*moves).team_id = self.env['crm.team'].with_context(
                allowed_company_ids=[company_id],
            )._get_default_team_id(
                user_id=user_id,
            )

    @api.depends('line_ids.sale_line_ids')
    def _compute_origin_so_count(self):
        for move in self:
            move.sale_order_count = len(move.line_ids.sale_line_ids.order_id)

    @api.depends('partner_id.name', 'partner_id.sale_warn_msg', 'invoice_line_ids.product_id.sale_line_warn_msg', 'invoice_line_ids.product_id.display_name')
    def _compute_sale_warning_text(self):
        if not self.env.user.has_group('sale.group_warning_sale'):
            self.sale_warning_text = ''
            return
        for move in self:
            if move.move_type != 'out_invoice':
                move.sale_warning_text = ''
                continue
            warnings = OrderedSet()
            if partner_msg := move.partner_id.sale_warn_msg:
                warnings.add((move.partner_id.name or move.partner_id.display_name) + ' - ' + partner_msg)
            if partner_parent_msg := move.partner_id.parent_id.sale_warn_msg:
                parent = move.partner_id.parent_id
                warnings.add((parent.name or parent.display_name) + ' - ' + partner_parent_msg)
            for product in move.invoice_line_ids.product_id:
                if product_msg := product.sale_line_warn_msg:
                    warnings.add(product.display_name + ' - ' + product_msg)
            move.sale_warning_text = '\n'.join(warnings)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # OVERRIDE
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'campaign_id': move.campaign_id.id,
                'medium_id': move.medium_id.id,
                'source_id': move.source_id.id,
            })
        return super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)

    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()

        # We cannot change lines content on locked SO, changes on invoices are not forwarded to the SO if the SO is locked
        dp_lines = self.line_ids.sale_line_ids.filtered(lambda l: l.is_downpayment and not l.display_type)
        dp_lines._compute_name()  # Update the description of DP lines (Draft -> Posted)
        downpayment_lines = dp_lines.filtered(lambda sol: not sol.order_id.locked)
        other_so_lines = downpayment_lines.order_id.order_line - downpayment_lines
        real_invoices = set(other_so_lines.invoice_lines.move_id)
        for so_dpl in downpayment_lines:
            so_dpl.price_unit = so_dpl._get_downpayment_line_price_unit(real_invoices)
            so_dpl.tax_ids = so_dpl.invoice_lines.tax_ids

        return res

    def button_draft(self):
        res = super().button_draft()

        self.line_ids.filtered('is_downpayment').sale_line_ids.filtered(
            lambda sol: not sol.display_type)._compute_name()

        return res

    def button_cancel(self):
        res = super().button_cancel()

        self.line_ids.filtered('is_downpayment').sale_line_ids.filtered(
            lambda sol: not sol.display_type)._compute_name()

        return res

    def _post(self, soft=True):
        # OVERRIDE
        # Auto-reconcile the invoice with payments coming from transactions.
        # It's useful when you have a "paid" sale order (using a payment transaction) and you invoice it later.
        posted = super()._post(soft)

        for invoice in posted.filtered(lambda move: move.is_invoice()):
            payments = invoice.mapped('transaction_ids.payment_id').filtered(lambda x: x.state == 'in_process')
            move_lines = payments.move_id.line_ids.filtered(lambda line: line.account_type in ('asset_receivable', 'liability_payable') and not line.reconciled)
            for line in move_lines:
                invoice.js_assign_outstanding_line(line.id)
        return posted

    def _invoice_paid_hook(self):
        # OVERRIDE
        res = super(AccountMove, self)._invoice_paid_hook()
        todo = set()
        for invoice in self.filtered(lambda move: move.is_invoice()):
            for line in invoice.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    todo.add((sale_line.order_id, invoice.name))
        for (order, name) in todo:
            order.message_post(body=_("Invoice %s paid", name))
        return res

    def _action_invoice_ready_to_be_sent(self):
        # OVERRIDE
        # Make sure the send invoice CRON is called when an invoice becomes ready to be sent by mail.
        res = super()._action_invoice_ready_to_be_sent()

        send_invoice_cron = self.env.ref('sale.send_invoice_cron', raise_if_not_found=False)
        if send_invoice_cron:
            send_invoice_cron._trigger()

        return res

    def action_view_source_sale_orders(self):
        self.ensure_one()
        source_orders = self.line_ids.sale_line_ids.order_id
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def _is_downpayment(self):
        # OVERRIDE
        self.ensure_one()
        return self.line_ids.sale_line_ids and all(sale_line.is_downpayment for sale_line in self.line_ids.sale_line_ids) or False

    def _get_sale_order_invoiced_amount(self, order):
        """
        Consider all lines on any invoice in self that stem from the sales order `order`. (All those invoices belong to order.company_id)
        This function returns the sum of the totals of all those lines.
        Note that this amount may be bigger than `order.amount_total`.
        """
        order_amount = 0
        for invoice in self:
            prices = sum(invoice.line_ids.filtered(
                lambda x: x.display_type not in ('line_note', 'line_section') and order in x.sale_line_ids.order_id
            ).mapped('price_total'))
            order_amount += invoice.currency_id._convert(
                prices * -invoice.direction_sign,
                order.currency_id,
                invoice.company_id,
                invoice.date,
            )
        return order_amount

    def _get_partner_credit_warning_exclude_amount(self):
        # EXTENDS module 'account'
        # Consider the warning on a draft invoice created from a sales order.
        # After confirming the invoice the (partial) amount (on the invoice)
        # stemming from sales orders will be substracted from the credit_to_invoice.
        # This will reduce the total credit of the partner.
        # The computation should reflect the change of credit_to_invoice from 'res.partner'.
        # (see _compute_credit_to_invoice and _compute_amount_to_invoice from 'sale.order' )
        exclude_amount = super()._get_partner_credit_warning_exclude_amount()
        for order in self.line_ids.sale_line_ids.order_id:
            order_amount = min(self._get_sale_order_invoiced_amount(order), order.amount_to_invoice)
            order_amount_company = order.currency_id._convert(
                max(order_amount, 0),
                self.company_id.currency_id,
                self.company_id,
                fields.Date.context_today(self)
            )
            exclude_amount += order_amount_company
        return exclude_amount


# FILEPATH: odoo/addons/sale/models/account_move_line.py
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_downpayment = fields.Boolean()
    sale_line_ids = fields.Many2many(
        'sale.order.line',
        'sale_order_line_invoice_rel',
        'invoice_line_id', 'order_line_id',
        string='Sales Order Lines', readonly=True, copy=False)
    sale_line_warn_msg = fields.Text(compute='_compute_sale_line_warn_msg')

    @api.depends('product_id.sale_line_warn_msg')
    def _compute_sale_line_warn_msg(self):
        has_warning_group = self.env.user.has_group('sale.group_warning_sale')
        for line in self:
            line.sale_line_warn_msg = line.product_id.sale_line_warn_msg if has_warning_group else ""

    @api.depends('balance')
    def _compute_is_storno(self):
        # EXTENDS 'account'
        super()._compute_is_storno()
        for line in self:
            if line.is_downpayment:
                # Normal downpayments have a negative balance (credit on customer invoice)
                # Positive balance indicate reversal lines for previous downpayments,
                # which should be treated as storno line if storno accounting is enabled.
                line.is_storno = line.company_id.account_storno and line.balance > 0.0

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'sale_line_ids' field as well.
        super()._copy_data_extend_business_fields(values)
        values['sale_line_ids'] = [(6, None, self.sale_line_ids.ids)]

    def _related_analytic_distribution(self):
        # EXTENDS 'account'
        vals = super()._related_analytic_distribution()
        if self.sale_line_ids and not self.analytic_distribution:
            vals |= self.sale_line_ids[0].analytic_distribution or {}
        return vals

    def _prepare_analytic_lines(self):
        """ Note: This method is called only on the move.line that having an analytic distribution, and
            so that should create analytic entries.
        """
        values_list = super()._prepare_analytic_lines()

        # filter the move lines that can be reinvoiced: a cost (negative amount) analytic line without SO line but with a product can be reinvoiced
        move_to_reinvoice = self.env['account.move.line']
        if len(values_list) > 0:
            for index, move_line in enumerate(self):
                values = values_list[index]
                if 'so_line' not in values:
                    if move_line._sale_can_be_reinvoice():
                        move_to_reinvoice |= move_line

        # insert the sale line in the create values of the analytic entries
        if move_to_reinvoice.filtered(lambda aml: not aml.move_id.reversed_entry_id and aml.product_id):  # only if the move line is not a reversal one
            map_sale_line_per_move = move_to_reinvoice._sale_create_reinvoice_sale_line()
            for values in values_list:
                sale_line = map_sale_line_per_move.get(values.get('move_line_id'))
                if sale_line:
                    values['so_line'] = sale_line.id

        return values_list

    def _sale_can_be_reinvoice(self):
        """ determine if the generated analytic line should be reinvoiced or not.
            For Vendor Bill flow, if the product has a 'erinvoice policy' and is a cost, then we will find the SO on which reinvoice the AAL
        """
        self.ensure_one()
        if self.sale_line_ids:
            return False
        uom_precision_digits = self.env['decimal.precision'].precision_get('Product Unit')
        return float_compare(self.credit or 0.0, self.debit or 0.0, precision_digits=uom_precision_digits) != 1 and self.product_id.expense_policy not in [False, 'no']

    def _sale_create_reinvoice_sale_line(self):

        sale_order_map = self._sale_determine_order()

        sale_line_values_to_create = []  # the list of creation values of sale line to create.
        existing_sale_line_cache = {}  # in the sales_price-delivery case, we can reuse the same sale line. This cache will avoid doing a search each time the case happen
        # `map_move_sale_line` is map where
        #   - key is the move line identifier
        #   - value is either a sale.order.line record (existing case), or an integer representing the index of the sale line to create in
        #     the `sale_line_values_to_create` (not existing case, which will happen more often than the first one).
        map_move_sale_line = {}

        for move_line in self:
            sale_order = sale_order_map.get(move_line.id)

            # no reinvoice as no sales order was found
            if not sale_order:
                continue

            # raise if the sale order is not currently open
            if sale_order.state in ('draft', 'sent'):
                raise UserError(_(
                    "The Sales Order %(order)s to be reinvoiced must be validated before registering expenses.",
                    order=sale_order.name,
                ))
            elif sale_order.state == 'cancel':
                raise UserError(_(
                    "The Sales Order %(order)s to be reinvoiced is cancelled."
                    " You cannot register an expense on a cancelled Sales Order.",
                    order=sale_order.name,
                ))
            elif sale_order.locked:
                raise UserError(_(
                    "The Sales Order %(order)s to be reinvoiced is currently locked."
                    " You cannot register an expense on a locked Sales Order.",
                    order=sale_order.name,
                ))

            price = move_line._sale_get_invoice_price(sale_order)

            # find the existing sale.line or keep its creation values to process this in batch
            sale_line = None
            if (
                move_line.product_id.expense_policy == 'sales_price'
                and move_line.product_id.invoice_policy == 'delivery'
                and not self.env.context.get('force_split_lines')
            ):
                # for those case only, we can try to reuse one
                map_entry_key = (sale_order.id, move_line.product_id.id, price)  # cache entry to limit the call to search
                sale_line = existing_sale_line_cache.get(map_entry_key)
                if sale_line:  # already search, so reuse it. sale_line can be sale.order.line record or index of a "to create values" in `sale_line_values_to_create`
                    map_move_sale_line[move_line.id] = sale_line
                    existing_sale_line_cache[map_entry_key] = sale_line
                else:  # search for existing sale line
                    sale_line = self.env['sale.order.line'].search([
                        ('order_id', '=', sale_order.id),
                        ('price_unit', '=', price),
                        ('product_id', '=', move_line.product_id.id),
                        ('is_expense', '=', True),
                    ], limit=1)
                    if sale_line:  # found existing one, so keep the browse record
                        map_move_sale_line[move_line.id] = existing_sale_line_cache[map_entry_key] = sale_line
                    else:  # should be create, so use the index of creation values instead of browse record
                        # save value to create it
                        sale_line_values_to_create.append(move_line._sale_prepare_sale_line_values(sale_order, price))
                        # store it in the cache of existing ones
                        existing_sale_line_cache[map_entry_key] = len(sale_line_values_to_create) - 1  # save the index of the value to create sale line
                        # store it in the map_move_sale_line map
                        map_move_sale_line[move_line.id] = len(sale_line_values_to_create) - 1  # save the index of the value to create sale line

            else:  # save its value to create it anyway
                sale_line_values_to_create.append(move_line._sale_prepare_sale_line_values(sale_order, price))
                map_move_sale_line[move_line.id] = len(sale_line_values_to_create) - 1  # save the index of the value to create sale line

        # create the sale lines in batch
        new_sale_lines = self.env['sale.order.line'].create(sale_line_values_to_create)

        # build result map by replacing index with newly created record of sale.order.line
        result = {}
        for move_line_id, unknown_sale_line in map_move_sale_line.items():
            if isinstance(unknown_sale_line, int):  # index of newly created sale line
                result[move_line_id] = new_sale_lines[unknown_sale_line]
            elif isinstance(unknown_sale_line, models.BaseModel):  # already record of sale.order.line
                result[move_line_id] = unknown_sale_line
        return result

    def _sale_determine_order(self):
        """ Get the mapping of move.line with the sale.order record on which its analytic entries should be reinvoiced
            :return a dict where key is the move line id, and value is sale.order record (or None).
        """
        return {}

    def _sale_prepare_sale_line_values(self, order, price):
        """ Generate the sale.line creation value from the current move line """
        self.ensure_one()
        last_so_line = self.env['sale.order.line'].search([('order_id', '=', order.id)], order='sequence desc', limit=1)
        last_sequence = last_so_line.sequence + 1 if last_so_line else 100

        fpos = order.fiscal_position_id or order.fiscal_position_id._get_fiscal_position(order.partner_id)
        product_taxes = self.product_id.taxes_id._filter_taxes_by_company(order.company_id)
        taxes = fpos.map_tax(product_taxes)

        return {
            'order_id': order.id,
            'name': self.name,
            'sequence': last_sequence,
            'price_unit': price,
            'tax_ids': [x.id for x in taxes],
            'discount': 0.0,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'product_uom_qty': self.quantity,
            'is_expense': True,
            'analytic_distribution': self.analytic_distribution,
        }

    def _sale_get_invoice_price(self, order):
        """ Based on the current move line, compute the price to reinvoice the analytic line that is going to be created (so the
            price of the sale line).
        """
        self.ensure_one()

        unit_amount = self.quantity
        amount = (self.credit or 0.0) - (self.debit or 0.0)

        if self.product_id.expense_policy == 'sales_price':
            return order.pricelist_id._get_product_price(
                self.product_id,
                1.0,
                uom=self.product_uom_id,
                date=order.date_order,
            )

        uom_precision_digits = self.env['decimal.precision'].precision_get('Product Unit')
        if float_is_zero(unit_amount, precision_digits=uom_precision_digits):
            return 0.0

        # Prevent unnecessary currency conversion that could be impacted by exchange rate
        # fluctuations
        if self.company_id.currency_id and amount and self.company_id.currency_id == order.currency_id:
            return self.company_id.currency_id.round(abs(amount / unit_amount))

        price_unit = abs(amount / unit_amount)
        currency_id = self.company_id.currency_id
        if currency_id and currency_id != order.currency_id:
            price_unit = currency_id._convert(price_unit, order.currency_id, order.company_id, order.date_order or fields.Date.today())
        return price_unit

    def _get_downpayment_lines(self):
        # OVERRIDE
        return self.sale_line_ids.filtered('is_downpayment').invoice_lines.filtered(lambda line: line.move_id._is_downpayment())


# FILEPATH: odoo/addons/sale/models/analytic.py (lines 6-9)
class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    so_line = fields.Many2one('sale.order.line', string='Sales Order Item', domain=[('qty_delivered_method', '=', 'analytic')], index='btree_not_null')


# FILEPATH: odoo/addons/sale/models/analytic.py (lines 12-21)
class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'
    _description = "Analytic Plan's Applicabilities"
    business_domain = fields.Selection(
        selection_add=[
            ('sale_order', 'Sale Order'),
        ],
        ondelete={'sale_order': 'cascade'},
    )


# FILEPATH: odoo/addons/sale/models/chart_template.py
class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'
    def _get_property_accounts(self, additional_properties):
        pass  # shrunk (lines 7-10)


# FILEPATH: odoo/addons/sale/models/crm_team.py
class CrmTeam(models.Model):
    _inherit = 'crm.team'

    invoiced = fields.Float(
        compute='_compute_invoiced',
        string='Invoiced This Month', readonly=True,
        help="Invoice revenue for the current month. This is the amount the sales "
                "channel has invoiced this month. It is used to compute the progression ratio "
                "of the current and target revenue on the kanban view.")
    invoiced_target = fields.Float(
        string='Invoicing Target',
        help="Revenue Target for the current month (untaxed total of paid invoices).")
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='# Sale Orders')

    def _compute_invoiced(self):
        if self.ids:
            today = fields.Date.today()
            data_map = dict(self.env.execute_query(SQL(
                ''' SELECT
                        move.team_id AS team_id,
                        SUM(move.amount_untaxed_signed) AS amount_untaxed_signed
                    FROM account_move move
                    WHERE move.move_type IN ('out_invoice', 'out_refund', 'out_receipt')
                    AND move.payment_state IN ('in_payment', 'paid', 'reversed')
                    AND move.state = 'posted'
                    AND move.team_id IN %s
                    AND move.date BETWEEN %s AND %s
                    GROUP BY move.team_id
                ''',
                tuple(self.ids),
                fields.Date.to_string(today.replace(day=1)),
                fields.Date.to_string(today),
            )))
        else:
            data_map = {}

        for team in self:
            team.invoiced = data_map.get(team._origin.id, 0.0)

    def _compute_sale_order_count(self):
        sale_order_data = self.env['sale.order']._read_group([
            ('team_id', 'in', self.ids),
            ('state', '!=', 'cancel'),
        ], ['team_id'], ['__count'])
        data_map = {team.id: count for team, count in sale_order_data}
        for team in self:
            team.sale_order_count = data_map.get(team.id, 0)

    def _in_sale_scope(self):
        return self.env.context.get('in_sales_app')

    def _compute_dashboard_button_name(self):
        super(CrmTeam,self)._compute_dashboard_button_name()
        if self._in_sale_scope():
            self.dashboard_button_name = _("Sales Analysis")

    def action_primary_channel_button(self):
        if self._in_sale_scope():
            return self.env["ir.actions.actions"]._for_xml_id("sale.action_order_report_so_salesteam")
        return super().action_primary_channel_button()

    def update_invoiced_target(self, value):
        return self.write({'invoiced_target': round(float(value or 0))})

    @api.ondelete(at_uninstall=False)
    def _unlink_except_used_for_sales(self):
        """ If more than 5 active SOs, we consider this team to be actively used.
        5 is some random guess based on "user testing", aka more than testing
        CRM feature and less than use it in real life use cases. """
        SO_COUNT_TRIGGER = 5
        for team in self:
            if team.sale_order_count >= SO_COUNT_TRIGGER:
                raise UserError(
                    _('Team %(team_name)s has %(sale_order_count)s active sale orders. Consider cancelling them or archiving the team instead.',
                      team_name=team.name,
                      sale_order_count=team.sale_order_count
                      ))


# FILEPATH: odoo/addons/sale/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        # EXTENDS base
        collected_streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)

        if (
            collected_streams
            and res_ids
            and len(res_ids) == 1
            and self._is_sale_order_report(report_ref)
        ):
            sale_order = self.env['sale.order'].browse(res_ids)
            builders = sale_order._get_edi_builders()
            if len(builders) == 0:
                return collected_streams

            # Read pdf content.
            pdf_stream = collected_streams[sale_order.id]['stream']
            pdf_content = pdf_stream.getvalue()
            reader_buffer = io.BytesIO(pdf_content)
            reader = OdooPdfFileReader(reader_buffer, strict=False)
            writer = OdooPdfFileWriter()
            writer.cloneReaderDocumentRoot(reader)

            # Generate and attach EDI documents from each builder
            for builder in builders:
                xml_content = builder._export_order(sale_order)

                writer.addAttachment(
                    builder._export_invoice_filename(sale_order),  # works even if it's a SO or PO
                    xml_content,
                    subtype='text/xml'
                )

            # Replace the current content.
            pdf_stream.close()
            new_pdf_stream = io.BytesIO()
            writer.write(new_pdf_stream)
            collected_streams[sale_order.id]['stream'] = new_pdf_stream

        return collected_streams

    def _is_sale_order_report(self, report_ref):
        return self._get_report(report_ref).report_name in (
            'sale.report_saleorder_document',
            'sale.report_saleorder',
            'sale.report_saleorder_raw',
        )


# FILEPATH: odoo/addons/sale/models/ir_config_parameter.py
class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model_create_multi
    def create(self, vals_list):
        configs = super().create(vals_list)
        configs._sale_sync_linked_crons()
        return configs

    def write(self, vals):
        res = super().write(vals)
        self._sale_sync_linked_crons()
        return res

    def unlink(self):
        self._sale_sync_linked_crons(unlink=True)
        return super().unlink()

    def _sale_sync_linked_crons(self, unlink=False):
        """Synchronize Sales-related crons' `active` field based on linked configuration parameters.

        :param bool unlink: Whether this sync is triggered by parameter deletion.
        :return: None
        """
        param_cron_mapping = self._get_param_cron_mapping()
        for config in self.filtered(lambda c: c.key in param_cron_mapping):
            linked_cron_xmlid = param_cron_mapping[config.key]
            if linked_cron := self.env.ref(linked_cron_xmlid, raise_if_not_found=False):
                linked_cron.active = False if unlink else str2bool(config.value)

    def _get_param_cron_mapping(self):
        """Return a mapping of config parameters to linked crons' XMLIDs.

        :return: The config-cron mapping.
        :rtype: dict
        """
        return const.PARAM_CRON_MAPPING


# FILEPATH: odoo/addons/sale/models/payment_provider.py
class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    so_reference_type = fields.Selection(string='Communication',
        selection=[
            ('so_name', 'Based on Document Reference'),
            ('partner', 'Based on Customer ID')], default='so_name',
        help='You can set here the communication type that will appear on sales orders.'
             'The communication will be given to the customer when they choose the payment method.')


# FILEPATH: odoo/addons/sale/models/payment_transaction.py
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    sale_order_ids = fields.Many2many('sale.order', 'sale_order_transaction_rel', 'transaction_id', 'sale_order_id',
                                      string='Sales Orders', copy=False, readonly=True)
    sale_order_ids_nbr = fields.Integer(compute='_compute_sale_order_ids_nbr', string='# of Sales Orders')

    def _compute_sale_order_reference(self, order):
        self.ensure_one()
        if self.provider_id.so_reference_type == 'so_name':
            order_reference = order.name
        elif self.provider_id.so_reference_type == 'partner':
            identification_number = order.partner_id.id
            order_reference = '%s/%s' % ('CUST', str(identification_number % 97).rjust(2, '0'))
        else:
            # self.provider_id.so_reference_type is empty
            order_reference = False

        invoice_journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.env.company.id)], limit=1)
        if invoice_journal:
            order_reference = invoice_journal._process_reference_for_sale_order(order_reference)

        return order_reference

    @api.depends('sale_order_ids')
    def _compute_sale_order_ids_nbr(self):
        for trans in self:
            trans.sale_order_ids_nbr = len(trans.sale_order_ids)

    def _post_process(self):
        """ Override of `payment` to add Sales-specific logic to the post-processing.

        In particular, for pending transactions, we send the quotation by email; for authorized
        transactions, we confirm the quotation; for confirmed transactions, we automatically confirm
        the quotation and generate invoices.
        """
        for pending_tx in self.filtered(lambda tx: tx.state == 'pending'):
            super(PaymentTransaction, pending_tx)._post_process()
            sales_orders = pending_tx.sale_order_ids.filtered(
                lambda so: so.state in ['draft', 'sent']
            )
            sales_orders.filtered(
                lambda so: so.state == 'draft'
            ).with_context(tracking_disable=True).action_quotation_sent()

            if pending_tx.provider_id.code == 'custom':
                for order in pending_tx.sale_order_ids:
                    order.reference = pending_tx._compute_sale_order_reference(order)

            if pending_tx.operation == 'validation':
                continue
            # Send the payment status email.
            # The transactions are manually cached while in a sudoed environment to prevent an
            # AccessError: In some circumstances, sending the mail would generate the report assets
            # during the rendering of the mail body, causing a cursor commit, a flush, and forcing
            # the re-computation of the pending computed fields of the `mail.compose.message`,
            # including part of the template. Since that template reads the order's transactions and
            # the re-computation of the field is not done with the same environment, reading fields
            # that were not already available in the cache could trigger an AccessError (e.g., if
            # the payment was initiated by a public user).
            sales_orders.mapped('transaction_ids')
            sales_orders._send_payment_succeeded_for_order_mail()

        for authorized_tx in self.filtered(lambda tx: tx.state == 'authorized'):
            super(PaymentTransaction, authorized_tx)._post_process()
            confirmed_orders = authorized_tx._check_amount_and_confirm_order()
            if authorized_tx.operation == 'validation':
                continue
            if remaining_orders := (authorized_tx.sale_order_ids - confirmed_orders):
                remaining_orders._send_payment_succeeded_for_order_mail()

        super(PaymentTransaction, self.filtered(
            lambda tx: tx.state not in ['pending', 'authorized', 'done'])
        )._post_process()

        for done_tx in self.filtered(lambda tx: tx.state == 'done'):
            if done_tx.operation != 'validation':
                confirmed_orders = done_tx._check_amount_and_confirm_order()
                (done_tx.sale_order_ids - confirmed_orders)._send_payment_succeeded_for_order_mail()

            auto_invoice = str2bool(
                self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice')
            )
            if auto_invoice:
                # Invoice the sales orders of confirmed transactions instead of only confirmed
                # orders to create the invoice even if only a partial payment was made.
                done_tx._invoice_sale_orders()
            super(PaymentTransaction, done_tx)._post_process()  # Post the invoices.
            if auto_invoice and not self.env.context.get('skip_sale_auto_invoice_send'):
                if (
                    str2bool(self.env['ir.config_parameter'].sudo().get_param('sale.async_emails'))
                    and (send_invoice_cron := self.env.ref('sale.send_invoice_cron', raise_if_not_found=False))
                ):
                    send_invoice_cron._trigger()
                else:
                    self._send_invoice()

    def _check_amount_and_confirm_order(self):
        """ Confirm the sales order based on the amount of a transaction.

        Confirm the sales orders only if the transaction amount (or the sum of the partial
        transaction amounts) is equal to or greater than the required amount for order confirmation

        Grouped payments (paying multiple sales orders in one transaction) are not supported.

        :return: The confirmed sales orders.
        :rtype: a `sale.order` recordset
        """
        confirmed_orders = self.env['sale.order']
        for tx in self:
            # We only support the flow where exactly one quotation is linked to a transaction.
            if len(tx.sale_order_ids) == 1:
                quotation = tx.sale_order_ids.filtered(lambda so: so.state in ('draft', 'sent'))
                if quotation and quotation._is_confirmation_amount_reached():
                    quotation.with_context(send_email=True).action_confirm()
                    confirmed_orders |= quotation
        return confirmed_orders

    def _log_message_on_linked_documents(self, message):
        """ Override of payment to log a message on the sales orders linked to the transaction.

        Note: self.ensure_one()

        :param str message: The message to be logged
        :return: None
        """
        super()._log_message_on_linked_documents(message)
        if self.env.uid == SUPERUSER_ID or self.env.context.get('payment_backend_action'):
            author = self.env.user.partner_id
        else:
            author = self.partner_id
        for order in self.sale_order_ids or self.source_transaction_id.sale_order_ids:
            order.message_post(body=message, author_id=author.id)

    def _send_invoice(self):
        # Send messages as OdooBot so that
        #   * logged in users receive the invoice
        #   * the mail and notifications are not sent by the public user
        for tx in self.with_user(SUPERUSER_ID):
            tx = tx.with_company(tx.company_id).with_context(
                company_id=tx.company_id.id,
            )
            invoice_to_send = tx.invoice_ids.filtered(
                lambda i: not i.is_move_sent and i.state == 'posted' and i._is_ready_to_be_sent()
            )
            invoice_to_send.is_move_sent = True # Mark invoice as sent

            send_context = {'allow_raising': False, 'allow_fallback_pdf': True}
            default_template_param = (
                self.env['ir.config_parameter']
                .sudo()
                .get_param('sale.default_invoice_email_template', False)
            )
            if default_template_param:
                mail_template = self.env['mail.template'].sudo().browse(int(default_template_param))
                if mail_template.exists():
                    send_context['mail_template'] = mail_template

            tx.env['account.move.send']._generate_and_send_invoices(
                invoice_to_send,
                **send_context,
            )

    def _cron_send_invoice(self):
        """
            Cron to send invoice that where not ready to be send directly after posting
        """
        if not self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            return

        # No need to retrieve old transactions
        retry_limit_date = datetime.now() - relativedelta.relativedelta(days=2)
        # Retrieve all transactions matching the criteria for post-processing
        self.search([
            ('state', '=', 'done'),
            ('is_post_processed', '=', True),
            ('invoice_ids', 'in', self.env['account.move']._search([
                ('is_move_sent', '=', False),
                ('state', '=', 'posted'),
            ])),
            ('sale_order_ids.state', '=', 'sale'),
            ('last_state_change', '>=', retry_limit_date),
        ])._send_invoice()

    def _invoice_sale_orders(self):
        for tx in self.filtered(lambda tx: tx.sale_order_ids):
            tx = tx.with_company(tx.company_id)

            confirmed_orders = tx.sale_order_ids.filtered(lambda so: so.state == 'sale')
            if confirmed_orders:
                # Filter orders between those fully paid and those partially paid.
                fully_paid_orders = confirmed_orders.filtered(lambda so: so._is_paid())

                # Create a down payment invoice for partially paid orders
                downpayment_invoices = (
                    confirmed_orders - fully_paid_orders
                )._generate_downpayment_invoices()

                # For fully paid orders create a final invoice.
                fully_paid_orders._force_lines_to_invoice_policy_order()
                final_invoices = fully_paid_orders.with_context(
                    raise_if_nothing_to_invoice=False
                )._create_invoices(final=True)
                invoices = downpayment_invoices + final_invoices

                # Setup access token in advance to avoid serialization failure between
                # edi postprocessing of invoice and displaying the sale order on the portal
                for invoice in invoices:
                    invoice._portal_ensure_token()
                tx.invoice_ids = [Command.set(invoices.ids)]

    @api.model
    def _compute_reference_prefix(self, separator, **values):
        """ Override of payment to compute the reference prefix based on Sales-specific values.

        If the `values` parameter has an entry with 'sale_order_ids' as key and a list of (4, id, O)
        or (6, 0, ids) X2M command as value, the prefix is computed based on the sales order name(s)
        Otherwise, the computation is delegated to the super method.

        :param str separator: The custom separator used to separate data references
        :param dict values: The transaction values used to compute the reference prefix. It should
                            have the structure {'sale_order_ids': [(X2M command), ...], ...}.
        :return: The computed reference prefix if order ids are found, the one of `super` otherwise
        :rtype: str
        """
        command_list = values.get('sale_order_ids')
        if command_list:
            # Extract sales order id(s) from the X2M commands
            order_ids = self._fields['sale_order_ids'].convert_to_cache(command_list, self)
            orders = self.env['sale.order'].browse(order_ids).exists()
            if len(orders) == len(order_ids):  # All ids are valid
                return separator.join(orders.mapped('name'))
        return super()._compute_reference_prefix(separator, **values)

    @api.readonly
    def action_view_sales_orders(self):
        action = {
            'name': _('Sales Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }
        sale_order_ids = self.sale_order_ids.ids
        if len(sale_order_ids) == 1:
            action['res_id'] = sale_order_ids[0]
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'list,form'
            action['domain'] = [('id', 'in', sale_order_ids)]
        return action


# FILEPATH: odoo/addons/sale/models/product_document.py
class ProductDocument(models.Model):
    _inherit = 'product.document'
    attached_on_sale = fields.Selection(
        selection=[
            ('hidden', "Hidden"),
            ('quotation', "On quote"),
            ('sale_order', "On confirmed order"),
        ],
        required=True,
        default='hidden',
        string="Sale : Visible at",
        help="Allows you to share the document with your customers within a sale.\n"
            "On quote: the document will be sent to and accessible by customers at any time.\n"
                "e.g. this option can be useful to share Product description files.\n"
            "On order confirmation: the document will be sent to and accessible by customers.\n"
                "e.g. this option can be useful to share User Manual or digital content bought"
                " on ecommerce. ",
        groups='sales_team.group_sale_salesman',
    )


# FILEPATH: odoo/addons/sale/models/product_pricelist_item.py
class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.model
    def _is_discount_feature_enabled(self):
        return self.env['res.groups']._is_feature_enabled('sale.group_discount_per_so_line')

    def _show_discount(self):
        if not self:
            return False

        self.ensure_one()
        return self._is_discount_feature_enabled() and self.compute_price == 'percentage'


# FILEPATH: odoo/addons/sale/models/product_product.py (lines 10-123)
class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_count = fields.Float(compute='_compute_sales_count', string='Sold', digits='Product Unit')

    # Catalog related fields
    product_catalog_product_is_in_sale_order = fields.Boolean(
        compute='_compute_product_is_in_sale_order',
        search='_search_product_is_in_sale_order',
    )

    def _compute_sales_count(self):
        r = {}
        self.sales_count = 0
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            return r
        date_from = fields.Date.today() - timedelta(days=365)

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for product, product_uom_qty in self.env['sale.report']._read_group(domain, ['product_id'], ['product_uom_qty:sum']):
            r[product.id] = product_uom_qty
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            product.sales_count = product.uom_id.round(r.get(product.id, 0))
        return r

    @api.onchange('type')
    def _onchange_type(self):
        if self._origin and self.sales_count > 0:
            return {'warning': {
                'title': _("Warning"),
                'message': _("You cannot change the product's type because it is already used in sales orders.")
            }}

    @api.depends_context('order_id')
    def _compute_product_is_in_sale_order(self):
        order_id = self.env.context.get('order_id')
        if not order_id:
            self.product_catalog_product_is_in_sale_order = False
            return

        read_group_data = self.env['sale.order.line']._read_group(
            domain=[('order_id', '=', order_id)],
            groupby=['product_id'],
            aggregates=['__count'],
        )
        data = {product.id: count for product, count in read_group_data}
        for product in self:
            product.product_catalog_product_is_in_sale_order = bool(data.get(product.id, 0))

    def _search_product_is_in_sale_order(self, operator, value):
        if operator != 'in':
            return NotImplemented
        product_ids = self.env['sale.order.line'].search_fetch([
            ('order_id', 'in', [self.env.context.get('order_id', '')]),
        ], ['product_id']).product_id.ids
        return [('id', 'in', product_ids)]

    @api.readonly
    def action_view_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.report_all_channels_sales_action")
        action['domain'] = [('product_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['product_uom_qty'],
            'active_id': self.env.context.get('active_id'),
            'search_default_Sales': 1,
            'active_model': 'sale.report',
            'search_default_filter_order_date': 1,
        }
        return action

    def _get_backend_root_menu_ids(self):
        return super()._get_backend_root_menu_ids() + [self.env.ref('sale.sale_menu_root').id]

    def _get_invoice_policy(self):
        return self.invoice_policy

    def _filter_to_unlink(self):
        domain = [('product_id', 'in', self.ids)]
        lines = self.env['sale.order.line']._read_group(domain, ['product_id'])
        linked_product_ids = [product.id for [product] in lines]
        return super(ProductProduct, self - self.browse(linked_product_ids))._filter_to_unlink()

    def _update_uom(self, to_uom_id):
        for uom, product, so_lines in self.env['sale.order.line']._read_group(
            [('product_id', 'in', self.ids)],
            ['product_uom_id', 'product_id'],
            ['id:recordset'],
        ):
            if so_lines.product_uom_id != product.product_tmpl_id.uom_id:
                raise UserError(_(
                    'As other units of measure (ex : %(problem_uom)s) '
                    'than %(uom)s have already been used for this product, the change of unit of measure can not be done.'
                    'If you want to change it, please archive the product and create a new one.',
                    problem_uom=uom.display_name, uom=product.product_tmpl_id.uom_id.display_name))
            so_lines.product_uom_id = to_uom_id
        return super()._update_uom(to_uom_id)

    def _trigger_uom_warning(self):        
        res = super()._trigger_uom_warning()
        if res:
            return res
        so_lines = self.env['sale.order.line'].sudo().search_count(
            [('product_id', 'in', self.ids)], limit=1
        )
        return bool(so_lines)


# FILEPATH: odoo/addons/sale/models/product_product.py (lines 126-134)
class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"
    sale_order_line_id = fields.Many2one('sale.order.line', string="Sales Order Line", index='btree_not_null', ondelete='cascade')
    _sol_custom_value_unique = models.Constraint(
        'unique(custom_product_template_attribute_value_id, sale_order_line_id)',
        'Only one Custom Value is allowed per Attribute Value per Sales Order Line.',
    )


# FILEPATH: odoo/addons/sale/models/product_template.py
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    service_type = fields.Selection(
        selection=[('manual', "Manually set quantities on order")],
        string="Track Service",
        compute='_compute_service_type', store=True, readonly=False, precompute=True,
        help="Manually set quantities on order: Invoice based on the manually entered quantity, without creating an analytic account.\n"
             "Timesheets on contract: Invoice based on the tracked hours on the related timesheet.\n"
             "Create a task and track hours: Create a task on the sales order validation and track the work hours.")
    sale_line_warn_msg = fields.Text(string="Sales Order Line Warning")
    expense_policy = fields.Selection(
        selection=[
            ('no', "No"),
            ('cost', "At cost"),
            ('sales_price', "Sales price"),
        ],
        string="Re-Invoice Costs", default='no',
        compute='_compute_expense_policy', store=True, readonly=False,
        help="Validated expenses, vendor bills, or stock pickings (set up to track costs) can be invoiced to the customer at either cost or sales price.")
    visible_expense_policy = fields.Boolean(
        string="Re-Invoice Policy visible", compute='_compute_visible_expense_policy')
    sales_count = fields.Float(
        string="Sold", compute='_compute_sales_count', digits='Product Unit')
    invoice_policy = fields.Selection(
        selection=[
            ('order', "Ordered quantities"),
            ('delivery', "Delivered quantities"),
        ],
        string="Invoicing Policy",
        compute='_compute_invoice_policy',
        precompute=True,
        store=True,
        readonly=False,
        tracking=True,
        help="Ordered Quantity: Invoice quantities ordered by the customer.\n"
             "Delivered Quantity: Invoice quantities delivered to the customer.")
    optional_product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='product_optional_rel',
        column1='src_id',
        column2='dest_id',
        string="Optional Products",
        help="Optional Products are suggested "
             "whenever the customer hits *Add to Cart* (cross-sell strategy, "
             "e.g. for computers: warranty, software, etc.).",
        check_company=True)

    @api.depends('invoice_policy', 'sale_ok', 'service_tracking')
    def _compute_product_tooltip(self):
        super()._compute_product_tooltip()

    def _prepare_tooltip(self):
        tooltip = super()._prepare_tooltip()
        if not self.sale_ok:
            return tooltip

        invoicing_tooltip = self._prepare_invoicing_tooltip()

        tooltip = f'{tooltip} {invoicing_tooltip}' if tooltip else invoicing_tooltip

        if self.type == 'service':
            additional_tooltip = self._prepare_service_tracking_tooltip()
            tooltip = f'{tooltip} {additional_tooltip}' if additional_tooltip else tooltip

        return tooltip

    def _prepare_invoicing_tooltip(self):
        if self.invoice_policy == 'delivery' and self.type != 'consu':
            return _("Invoice after delivery, based on quantities delivered, not ordered.")
        elif self.invoice_policy == 'order' and self.type == 'service':
            return _("Invoice ordered quantities as soon as this service is sold.")
        return ""

    def _prepare_service_tracking_tooltip(self):
        return ""

    @api.depends('sale_ok')
    def _compute_service_tracking(self):
        super()._compute_service_tracking()
        self.filtered(lambda pt: not pt.sale_ok).service_tracking = 'no'

    @api.depends('purchase_ok')
    def _compute_visible_expense_policy(self):
        visibility = self.env.user.has_group('analytic.group_analytic_accounting')
        for product_template in self:
            product_template.visible_expense_policy = visibility and product_template.purchase_ok

    @api.depends('sale_ok')
    def _compute_expense_policy(self):
        self.filtered(lambda t: not t.sale_ok).expense_policy = 'no'

    @api.depends('product_variant_ids.sales_count')
    def _compute_sales_count(self):
        for product in self:
            product.sales_count = product.uom_id.round(sum(p.sales_count for p in product.with_context(active_test=False).product_variant_ids))

    @api.constrains('company_id')
    def _check_sale_product_company(self):
        """Ensure the product is not being restricted to a single company while
        having been sold in another one in the past, as this could cause issues."""
        products_by_compagny = defaultdict(lambda: self.env['product.template'])
        for product in self:
            if not product.product_variant_ids or not product.company_id:
                # No need to check if the product has just being created (`product_variant_ids` is
                # still empty) or if we're writing `False` on its company (should always work.)
                continue
            products_by_compagny[product.company_id] |= product

        for target_company, products in products_by_compagny.items():
            subquery_products = self.env['product.product'].sudo().with_context(active_test=False)._search([('product_tmpl_id', 'in', products.ids)])
            so_lines = self.env['sale.order.line'].sudo().search_read(
                [('product_id', 'in', subquery_products), '!', ('company_id', 'child_of', target_company.id)],
                fields=['id', 'product_id'])
            if so_lines:
                used_products = [sol['product_id'][1] for sol in so_lines]
                raise ValidationError(_('The following products cannot be restricted to the company'
                                        ' %(company)s because they have already been used in quotations or '
                                        'sales orders in another company:\n%(used_products)s\n'
                                        'You can archive these products and recreate them '
                                        'with your company restriction instead, or leave them as '
                                        'shared product.', company=target_company.name, used_products=', '.join(used_products)))

    @api.readonly
    def action_view_sales(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale.report_all_channels_sales_action')
        action['domain'] = [('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['product_uom_qty'],
            'active_id': self.env.context.get('active_id'),
            'active_model': 'sale.report',
            'search_default_Sales': 1,
            'search_default_filter_order_date': 1,
            'search_default_group_by_date': 1,
        }
        return action

    @api.onchange('type')
    def _onchange_type(self):
        res = super()._onchange_type()
        if self._origin and self.sales_count > 0:
            res['warning'] = {
                'title': _("Warning"),
                'message': _("You cannot change the product's type because it is already used in sales orders.")
            }
        return res

    @api.depends('type')
    def _compute_service_type(self):
        self.filtered(lambda t: t.type == 'consu' or not t.service_type).service_type = 'manual'

    @api.depends('type')
    def _compute_invoice_policy(self):
        self.filtered(lambda t: t.type == 'consu' or not t.invoice_policy).invoice_policy = 'order'

    def _get_backend_root_menu_ids(self):
        return super()._get_backend_root_menu_ids() + [self.env.ref('sale.sale_menu_root').id]

    @api.model
    def get_import_templates(self):
        res = super(ProductTemplate, self).get_import_templates()
        if self.env.context.get('sale_multi_pricelist_product_template'):
            if self.env.user.has_group('product.group_product_pricelist'):
                return [{
                    'label': _("Import Template for Products"),
                    'template': '/product/static/xls/product_template.xls'
                }]
        return res

    @api.model
    def _get_incompatible_types(self):
        return []

    @api.constrains(lambda self: self._get_incompatible_types())
    def _check_incompatible_types(self):
        incompatible_types = self._get_incompatible_types()
        if len(incompatible_types) < 2:
            return
        fields = self.env['ir.model.fields'].sudo().search_read(
            [('model', '=', 'product.template'), ('name', 'in', incompatible_types)],
            ['name', 'field_description'])
        field_descriptions = {v['name']: v['field_description'] for v in fields}
        field_list = incompatible_types + ['name']
        values = self.read(field_list)
        for val in values:
            incompatible_fields = [f for f in incompatible_types if val[f]]
            if len(incompatible_fields) > 1:
                raise ValidationError(_(
                    "The product (%(product)s) has incompatible values: %(value_list)s",
                    product=val['name'],
                    value_list=[field_descriptions[v] for v in incompatible_fields],
                ))

    def get_single_product_variant(self):
        """ Method used by the product configurator to check if the product is configurable or not.

        We need to open the product configurator if the product:
        - is configurable (see has_configurable_attributes)
        - has optional products """
        res = super().get_single_product_variant()
        if res.get('product_id', False):
            has_optional_products = False
            for optional_product in self.product_variant_id.optional_product_ids:
                if optional_product.has_dynamic_attributes() or optional_product._get_possible_variants(
                    self.product_variant_id.product_template_attribute_value_ids
                ):
                    has_optional_products = True
                    break
            res.update({
                'has_optional_products': has_optional_products,
                'is_combo': self.type == 'combo',
            })
        return res

    @api.model
    def _get_saleable_tracking_types(self):
        """Return list of salealbe service_tracking types.

        :rtype: list
        """
        return ['no']

    ####################################
    # Product/combo configurator hooks #
    ####################################

    @api.model
    def _get_configurator_display_price(
        self, product_or_template, quantity, date, currency, pricelist, **kwargs
    ):
        """ Return the specified product's display price, to be used by the product and combo
        configurators.

        This is a hook meant to customize the display price computation in overriding modules.

        :param product.product|product.template product_or_template: The product for which to get
            the price.
        :param int quantity: The quantity of the product.
        :param datetime date: The date to use to compute the price.
        :param res.currency currency: The currency to use to compute the price.
        :param product.pricelist pricelist: The pricelist to use to compute the price.
        :param dict kwargs: Locally unused data passed to `_get_configurator_price`.
        :rtype: tuple(float, int or False)
        :return: The specified product's display price (and the applied pricelist rule)
        """
        return self._get_configurator_price(
            product_or_template, quantity, date, currency, pricelist, **kwargs
        )

    @api.model
    def _get_configurator_price(
        self, product_or_template, quantity, date, currency, pricelist, **kwargs
    ):
        """ Return the specified product's price, to be used by the product and combo configurators.

        This is a hook meant to customize the price computation in overriding modules.

        This hook has been extracted from `_get_configurator_display_price` because the price
        computation can be overridden in 2 ways:

        - Either by transforming super's price (e.g. in `website_sale`, we apply taxes to the
          price),
        - Or by computing a different price (e.g. in `sale_subscription`, we ignore super when
          computing subscription prices).
        In some cases, the order of the overrides matters, which is why we need 2 separate methods
        (e.g. in `website_sale_subscription`, we must compute the subscription price before applying
        taxes).

        :param product.product|product.template product_or_template: The product for which to get
            the price.
        :param int quantity: The quantity of the product.
        :param datetime date: The date to use to compute the price.
        :param res.currency currency: The currency to use to compute the price.
        :param product.pricelist pricelist: The pricelist to use to compute the price.
        :param dict kwargs: Locally unused data passed to `_get_product_price`.
        :rtype: tuple(float, int or False)
        :return: The specified product's price (and the applied pricelist rule)
        """
        return pricelist._get_product_price_rule(
            product_or_template, quantity=quantity, currency=currency, date=date, **kwargs
        )

    @api.model
    def _get_additional_configurator_data(
        self, product_or_template, date, currency, pricelist, *, uom=None, **kwargs
    ):
        """Return additional data about the specified product.

        This is a hook meant to append module-specific data in overriding modules.

        :param product.product|product.template product_or_template: The product for which to get
            additional data.
        :param datetime date: The date to use to compute prices.
        :param res.currency currency: The currency to use to compute prices.
        :param product.pricelist pricelist: The pricelist to use to compute prices.
        :param uom.uom uom: The uom to use to compute prices.
        :param dict kwargs: Locally unused data passed to overrides.
        :rtype: dict
        :return: A dict containing additional data about the specified product.
        """
        return {}


# FILEPATH: odoo/addons/sale/models/res_company.py
class ResCompany(models.Model):
    _inherit = 'res.company'
    _check_company_auto = True
    _check_quotation_validity_days = models.Constraint(
        'CHECK(quotation_validity_days >= 0)',
        'You cannot set a negative number for the default quotation validity. Leave empty (or 0) to disable the automatic expiration of quotations.',
    )
    portal_confirmation_sign = fields.Boolean(string="Online Signature", default=True)
    portal_confirmation_pay = fields.Boolean(string="Online Payment")
    prepayment_percent = fields.Float(
        string="Prepayment percentage",
        default=1.0,
        help="The percentage of the amount needed to be paid to confirm quotations.")
    quotation_validity_days = fields.Integer(
        string="Default Quotation Validity",
        default=30,
        help="Days between quotation proposal and expiration."
            " 0 days means automatic expiration is disabled",
    )
    sale_discount_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Discount Product",
        domain=[
            ('type', '=', 'service'),
            ('invoice_policy', '=', 'order'),
        ],
        help="Default product used for discounts",
        check_company=True,
    )
    sale_onboarding_payment_method = fields.Selection(
        selection=[
            ('digital_signature', "Sign online"),
            ('paypal', "PayPal"),
            ('stripe', "Stripe"),
            ('other', "Pay with another payment provider"),
            ('manual', "Manual Payment"),
        ],
        string="Sale onboarding selected payment method")
    downpayment_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Downpayment Account",
        domain=[
            ('account_type', 'in', ('income', 'income_other', 'liability_current')),
        ],
        help="This account will be used on Downpayment invoices.",
        tracking=True,
    )
    @api.constrains('prepayment_percent')
    def _check_prepayment_percent(self):
        pass  # shrunk (lines 60-64)


# FILEPATH: odoo/addons/sale/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'
    sale_order_count = fields.Integer(
        string="Sale Order Count",
        groups='sales_team.group_sale_salesman',
        compute='_compute_sale_order_count',
    )
    sale_order_ids = fields.One2many('sale.order', 'partner_id', 'Sales Order')
    sale_warn_msg = fields.Text('Message for Sales Order')
    @api.model
    def _get_sale_order_domain_count(self):
        pass  # shrunk (lines 18-20)
    def _compute_sale_order_count(self):
        pass  # shrunk (lines 22-42)
    def _compute_application_statistics_hook(self):
        pass  # shrunk (lines 44-52)
    def _has_order(self, partner_domain):
        pass  # shrunk (lines 54-65)
    def _can_edit_country(self):
        pass  # shrunk (lines 67-75)
    def can_edit_vat(self):
        pass  # shrunk (lines 77-81)
    def _compute_credit_to_invoice(self):
    # EXTENDS 'account'
        pass  # shrunk (lines 83-110)


# FILEPATH: odoo/addons/sale/models/sale_order.py
INVOICE_STATUS = [
    ('upselling', 'Upselling Opportunity'),
    ('invoiced', 'Fully Invoiced'),
    ('to invoice', 'To Invoice'),
    ('no', 'Nothing to Invoice')
]
SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin', 'account.document.import.mixin']
    _description = "Sales Order"
    _order = 'date_order desc, id desc'
    _check_company_auto = True

    _date_order_conditional_required = models.Constraint(
        "CHECK((state = 'sale' AND date_order IS NOT NULL) OR state != 'sale')",
        'A confirmed sales order requires a confirmation date.',
    )

    @property
    def _rec_names_search(self):
        if self.env.context.get('sale_show_partner_name'):
            return ['name', 'partner_id.name']
        return ['name']

    #=== FIELDS ===#

    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, change_default=True, index=True,
        tracking=1,
        check_company=True)
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        group_expand=True,
        default='draft')
    locked = fields.Boolean(
        help="Locked orders cannot be modified.",
        default=False,
        copy=False,
        tracking=True)
    has_archived_products = fields.Boolean(compute="_compute_has_archived_products")

    client_order_ref = fields.Char(string="Customer Reference", copy=False)
    create_date = fields.Datetime(  # Override of default create_date field from ORM
        string="Creation Date", index=True, readonly=True)
    commitment_date = fields.Datetime(
        string="Delivery Date", copy=False,
        help="This is the delivery date promised to the customer. "
             "If set, the delivery order will be scheduled based on "
             "this date rather than product lead times.")
    date_order = fields.Datetime(
        string="Order Date",
        required=True, copy=False,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now)
    origin = fields.Char(
        string="Source Document",
        help="Reference of the document that generated this sales order request")
    reference = fields.Char(
        string="Payment Ref.",
        help="The payment communication of this sale order.",
        copy=False)
    pending_email_template_id = fields.Many2one(
        string="Pending Email Template",
        comodel_name='mail.template',
        ondelete='set null',
        readonly=True,
    )  # The template of the pending email that must be sent asynchronously.

    require_signature = fields.Boolean(
        string="Online signature",
        compute='_compute_require_signature',
        store=True, readonly=False, precompute=True,
        help="Request a online signature from the customer to confirm the order.")
    require_payment = fields.Boolean(
        string="Online payment",
        compute='_compute_require_payment',
        store=True, readonly=False, precompute=True,
        help="Request a online payment from the customer to confirm the order.")
    prepayment_percent = fields.Float(
        string="Prepayment percentage",
        compute='_compute_prepayment_percent',
        store=True, readonly=False, precompute=True,
        help="The percentage of the amount needed that must be paid by the customer to confirm the order.")

    signature = fields.Image(
        string="Signature",
        copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char(
        string="Signed By", copy=False)
    signed_on = fields.Datetime(
        string="Signed On", copy=False)

    validity_date = fields.Date(
        string="Expiration",
        help="Validity of the order, after that you will not able to sign & pay the quotation.",
        compute='_compute_validity_date',
        store=True, readonly=False, copy=False, precompute=True)
    journal_id = fields.Many2one(
        'account.journal', string="Invoicing Journal",
        compute="_compute_journal_id", store=True, readonly=False, precompute=True,
        domain=[('type', '=', 'sale')], check_company=True,
        help="If set, the SO will invoice in this journal; "
             "otherwise the sales journal with the lowest sequence is used.")

    # Partner-based computes
    note = fields.Html(
        string="Terms and conditions",
        compute='_compute_note',
        store=True, readonly=False, precompute=True)

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True,
        index='btree_not_null')
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True,
        index='btree_not_null')

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
            "The default value comes from the customer.",
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        compute='_compute_payment_term_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    preferred_payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line", string="Payment Method",
        compute="_compute_preferred_payment_method_line_id",
        store=True, precompute=True, readonly=False, check_company=True,
        domain="[('payment_type', '=', 'inbound'), ('company_id', '=', company_id)]")
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict'
    )
    currency_rate = fields.Float(
        string="Currency Rate",
        compute='_compute_currency_rate',
        digits=0,
        store=True, precompute=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('all_group_ids', 'in', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").ids
        ))
    team_id = fields.Many2one(
        comodel_name='crm.team',
        string="Sales Team",
        compute='_compute_team_id',
        store=True, readonly=False, precompute=True, ondelete="set null",
        change_default=True, check_company=True,  # Unrequired company
        tracking=True, index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    # Lines and line based computes
    order_line = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        string="Order Lines",
        copy=True, bypass_search_access=True)

    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)
    amount_to_invoice = fields.Monetary(string="Un-invoiced Balance", compute='_compute_amount_to_invoice')
    amount_invoiced = fields.Monetary(string="Already invoiced", compute='_compute_amount_invoiced')

    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced')
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        compute='_get_invoiced',
        search='_search_invoice_ids',
        copy=False)
    invoice_status = fields.Selection(
        selection=INVOICE_STATUS,
        string="Invoice Status",
        compute='_compute_invoice_status',
        store=True)

    sale_warning_text = fields.Text(
        "Sale Warning",
        help="Internal warning for the partner or the products as set by the user.",
        compute='_compute_sale_warning_text')

    # Payment fields
    transaction_ids = fields.Many2many(
        comodel_name='payment.transaction',
        relation='sale_order_transaction_rel', column1='sale_order_id', column2='transaction_id',
        string="Transactions",
        groups='account.group_account_invoice',
        copy=False, readonly=True)
    authorized_transaction_ids = fields.Many2many(
        comodel_name='payment.transaction',
        string="Authorized Transactions",
        compute='_compute_authorized_transaction_ids',
        copy=False,
        groups='account.group_account_invoice',
        compute_sudo=True)
    has_authorized_transaction_ids = fields.Boolean(
        string="Has Authorized Transactions",
        compute='_compute_authorized_transaction_ids',
        compute_sudo=True)
    amount_paid = fields.Float(
        string="Payment Transactions Amount",
        help="Sum of transactions made in through the online payment form that are in the state"
             " 'done' or 'authorized' and linked to this order.",
        compute='_compute_amount_paid',
        compute_sudo=True,
    )

    # UTMs - enforcing the fact that we want to 'set null' when relation is unlinked
    campaign_id = fields.Many2one(ondelete='set null')
    medium_id = fields.Many2one(ondelete='set null')
    source_id = fields.Many2one(ondelete='set null')

    # Followup ?
    tag_ids = fields.Many2many(
        comodel_name='crm.tag',
        relation='sale_order_tag_rel', column1='order_id', column2='tag_id',
        groups="sales_team.group_sale_salesman",
        string="Tags")

    # Remaining non stored computed fields (hide/make fields readonly, ...)
    amount_undiscounted = fields.Float(
        string="Amount Before Discount",
        compute='_compute_amount_undiscounted', digits=0)
    country_code = fields.Char(related='company_id.account_fiscal_country_id.code', string="Country code")
    company_price_include = fields.Selection(related='company_id.account_price_include')
    duplicated_order_ids = fields.Many2many(comodel_name='sale.order', compute='_compute_duplicated_order_ids')
    expected_date = fields.Datetime(
        string="Expected Date",
        compute='_compute_expected_date', store=False,  # Note: can not be stored since depends on today()
        help="Delivery date you can promise to the customer, computed from the minimum lead time of the order lines.")
    is_expired = fields.Boolean(string="Is Expired", compute='_compute_is_expired')
    partner_credit_warning = fields.Text(
        compute='_compute_partner_credit_warning')
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        depends=['company_id'])
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position when reading a sale order with company != user.company_ids
        compute_sudo=True)  # used to filter available taxes depending on the fiscal country and position
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    terms_type = fields.Selection(related='company_id.terms_type')
    type_name = fields.Char(string="Type Name", compute='_compute_type_name')

    # Remaining ux fields (not computed, not stored)

    show_update_fpos = fields.Boolean(
        string="Has Fiscal Position Changed", store=False)  # True if the fiscal position was changed
    has_active_pricelist = fields.Boolean(
        compute='_compute_has_active_pricelist')
    show_update_pricelist = fields.Boolean(
        string="Has Pricelist Changed", store=False)  # True if the pricelist was changed

    _date_order_id_idx = models.Index("(date_order desc, id desc)")

    #=== COMPUTE METHODS ===#

    @api.depends('partner_id')
    @api.depends_context('sale_show_partner_name')
    def _compute_display_name(self):
        if not self.env.context.get('sale_show_partner_name'):
            return super()._compute_display_name()
        for order in self:
            name = order.name
            if order.partner_id.name:
                name = f'{name} - {order.partner_id.name}'
            order.display_name = name

    @api.depends('order_line.product_id')
    def _compute_has_archived_products(self):
        for order in self:
            order.has_archived_products = any(
                not product.active for product in order.order_line.product_id
            )

    @api.depends('company_id')
    def _compute_require_signature(self):
        for order in self:
            order.require_signature = order.company_id.portal_confirmation_sign

    @api.depends('company_id')
    def _compute_require_payment(self):
        for order in self:
            order.require_payment = order.company_id.portal_confirmation_pay

    @api.depends('require_payment')
    def _compute_prepayment_percent(self):
        for order in self:
            order.prepayment_percent = order.company_id.prepayment_percent

    @api.depends('company_id')
    def _compute_validity_date(self):
        today = fields.Date.context_today(self)
        for order in self:
            days = order.company_id.quotation_validity_days
            if days > 0:
                order.validity_date = today + timedelta(days)
            else:
                order.validity_date = False

    def _compute_journal_id(self):
        self.journal_id = False

    @api.depends('partner_id')
    def _compute_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if not use_invoice_terms:
            return
        for order in self:
            order = order.with_company(order.company_id)
            if order.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(order._get_note_url() + '/terms')
                context = {'lang': order.partner_id.lang or self.env.user.lang}
                order.note = _('Terms & Conditions: %s', baseurl)
                del context
            elif not is_html_empty(self.env.company.invoice_terms):
                if order.partner_id.lang:
                    order = order.with_context(lang=order.partner_id.lang)
                order.note = order.env.company.invoice_terms

    @api.model
    def _get_note_url(self):
        return self.env.company.get_base_url()

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice'] if order.partner_id else False

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            order.partner_shipping_id = order.partner_id.address_get(['delivery'])['delivery'] if order.partner_id else False

    @api.depends('partner_shipping_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            fpos_id_before = order.fiscal_position_id.id
            key = (order.company_id.id, order.partner_id.id, order.partner_shipping_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id, order.partner_shipping_id).id
            if fpos_id_before != cache[key] and order.order_line:
                order.show_update_fpos = True
            order.fiscal_position_id = cache[key]

    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            order.payment_term_id = order.partner_id.property_payment_term_id

    @api.depends('partner_id', 'company_id')
    def _compute_preferred_payment_method_line_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            order.preferred_payment_method_line_id = order.partner_id.property_inbound_payment_method_line_id

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for order in self:
            if order.state != 'draft':
                continue
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist

    @api.depends('pricelist_id', 'company_id')
    def _compute_currency_id(self):
        for order in self:
            order.currency_id = order.pricelist_id.currency_id or order.company_id.currency_id

    @api.depends('currency_id', 'date_order', 'company_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env['res.currency']._get_conversion_rate(
                from_currency=order.company_id.currency_id,
                to_currency=order.currency_id,
                company=order.company_id,
                date=(order.date_order or fields.Datetime.now()).date(),
            )

    @api.depends('company_id')
    def _compute_has_active_pricelist(self):
        for order in self:
            order.has_active_pricelist = bool(self.env['product.pricelist'].search(
                [('company_id', 'in', (False, order.company_id.id)), ('active', '=', True)],
                limit=1,
            ))

    @api.depends('partner_id')
    def _compute_user_id(self):
        for order in self:
            if order.partner_id and not (order._origin.id and order.user_id):
                # Recompute the salesman on partner change
                #   * if partner is set (is required anyway, so it will be set sooner or later)
                #   * if the order is not saved or has no salesman already
                order.user_id = (
                    order.partner_id.user_id
                    or order.partner_id.commercial_partner_id.user_id
                    or (self.env.user.has_group('sales_team.group_sale_salesman') and self.env.user)
                )

    @api.depends('user_id')
    def _compute_team_id(self):
        cached_teams = {}
        for order in self:
            default_team_id = order._default_team_id()
            user_id = order.user_id.id
            company_id = order.company_id.id
            key = (default_team_id, user_id, company_id)
            if key not in cached_teams:
                cached_teams[key] = self.env['crm.team'].with_context(
                    default_team_id=default_team_id,
                )._get_default_team_id(
                    user_id=user_id,
                    domain=self.env['crm.team']._check_company_domain(company_id),
                )
            order.team_id = cached_teams[key]

    def _default_team_id(self):
        return self.env.context.get('default_team_id', False) or self.team_id.id

    def _get_priced_lines(self):
        return self.order_line.filtered(lambda x: not x.display_type)

    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_amounts(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order._get_priced_lines()
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
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

    def _add_base_lines_for_early_payment_discount(self):
        """
        When applying a payment term with an early payment discount, and when said payment term computes the tax on the
        'mixed' setting, the tax computation is always based on the discounted amount untaxed.
        Creates the necessary line for this behavior to be displayed.
        :returns: array containing the necessary lines or empty array if the payment term isn't epd mixed
        """
        self.ensure_one()
        epd_lines = []
        if (
            self.payment_term_id.early_discount
            and self.payment_term_id.early_pay_discount_computation == 'mixed'
            and self.payment_term_id.discount_percentage
        ):
            percentage = self.payment_term_id.discount_percentage
            currency = self.currency_id or self.company_id.currency_id
            for line in self._get_priced_lines():
                line_amount_after_discount = (line.price_subtotal / 100) * percentage
                epd_lines.append(self.env['account.tax']._prepare_base_line_for_taxes_computation(
                    record=self,
                    price_unit=-line_amount_after_discount,
                    quantity=1.0,
                    currency_id=currency,
                    sign=1,
                    special_type='early_payment',
                    tax_ids=line.tax_ids.flatten_taxes_hierarchy().filtered(lambda tax: tax.amount_type != 'fixed'),
                ))
                epd_lines.append(self.env['account.tax']._prepare_base_line_for_taxes_computation(
                    record=self,
                    price_unit=line_amount_after_discount,
                    quantity=1.0,
                    currency_id=currency,
                    sign=1,
                    special_type='early_payment',
                ))
        return epd_lines

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    def _search_invoice_ids(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS:
            return NotImplemented
        if operator == 'in' and value:
            falsy_domain = []
            if False in value:
                # special case for [('invoice_ids', '=', False)], i.e. "Invoices is not set"
                #
                # We cannot just search [('order_line.invoice_lines', '=', False)]
                # because it returns orders with uninvoiced lines, which is not
                # same "Invoices is not set" (some lines may have invoices and some
                # don't)
                #
                # A solution is using the 'not any' operators with inverted search first
                # ("orders with invoiced lines").
                falsy_domain = [('order_line', 'not any', [
                    ('invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund'))
                ])]
                if len(value) == 1:
                    return falsy_domain
            self.env.cr.execute("""
                SELECT array_agg(so.id)
                    FROM sale_order so
                    JOIN sale_order_line sol ON sol.order_id = so.id
                    JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = sol.id
                    JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                WHERE
                    am.move_type in ('out_invoice', 'out_refund') AND
                    am.id = ANY(%s)
            """, (list(value),))
            so_ids = self.env.cr.fetchone()[0] or []
            return [('id', 'in', so_ids)] + falsy_domain
        return [('order_line.invoice_lines', 'any', [
            ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('move_id', operator, value),
        ])]

    @api.depends('state', 'order_line.invoice_status')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        confirmed_orders = self.filtered(lambda so: so.state == 'sale')
        (self - confirmed_orders).invoice_status = 'no'
        if not confirmed_orders:
            return
        lines_domain = [('is_downpayment', '=', False), ('display_type', '=', False)]
        line_invoice_status_all = [
            (order.id, invoice_status)
            for order, invoice_status in self.env['sale.order.line']._read_group(
                lines_domain + [('order_id', 'in', confirmed_orders.ids)],
                ['order_id', 'invoice_status']
            )
        ]
        for order in confirmed_orders:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.state != 'sale':
                order.invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                if any(invoice_status == 'no' for invoice_status in line_invoice_status):
                    # If only discount/delivery/promotion lines can be invoiced, the SO should not
                    # be invoiceable.
                    invoiceable_domain = lines_domain + [('invoice_status', '=', 'to invoice')]
                    invoiceable_lines = order.order_line.filtered_domain(invoiceable_domain)
                    special_lines = invoiceable_lines.filtered(
                        lambda sol: not sol._can_be_invoiced_alone()
                    )
                    if invoiceable_lines == special_lines:
                        order.invoice_status = 'no'
                    else:
                        order.invoice_status = 'to invoice'
                else:
                    order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

    @api.depends('transaction_ids')
    def _compute_authorized_transaction_ids(self):
        for trans in self:
            trans.authorized_transaction_ids = trans.transaction_ids.filtered(lambda t: t.state == 'authorized')
            trans.has_authorized_transaction_ids = bool(trans.authorized_transaction_ids)

    @api.depends('transaction_ids')
    def _compute_amount_paid(self):
        """ Sum of the amount paid through all transactions for this SO. """
        for order in self:
            order.amount_paid = sum(
                tx.amount for tx in order.transaction_ids if tx.state in ('authorized', 'done')
            )

    def _compute_amount_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.amount_undiscounted = total

    @api.depends('client_order_ref', 'origin', 'partner_id')
    def _compute_duplicated_order_ids(self):
        draft_orders = self.filtered(lambda o: o.state == 'draft')
        order_to_duplicate_orders = draft_orders._fetch_duplicate_orders()
        for order in draft_orders:
            order.duplicated_order_ids = [Command.set(order_to_duplicate_orders.get(order.id, []))]
        (self - draft_orders).duplicated_order_ids = False

    def _fetch_duplicate_orders(self):
        """ Fetch duplicated orders.

        :return: Dictionary mapping order to its related duplicated orders.
        :rtype: dict
        """
        orders = self.filtered(lambda order: order.id and order.client_order_ref)
        if not orders:
            return {}

        self.env['sale.order'].flush_model(['company_id', 'partner_id', 'client_order_ref', 'origin', 'state'])

        result = self.env.execute_query(SQL("""
            SELECT
                sale_order.id AS order_id,
                array_agg(duplicate_order.id) AS duplicate_ids
              FROM sale_order
              JOIN sale_order AS duplicate_order
                ON sale_order.company_id = duplicate_order.company_id
                 AND sale_order.id != duplicate_order.id
                 AND duplicate_order.state != 'cancel'
                 AND sale_order.partner_id = duplicate_order.partner_id
                 AND (
                    sale_order.origin = duplicate_order.name
                    OR sale_order.client_order_ref = duplicate_order.client_order_ref
                )
             WHERE sale_order.id IN %(orders)s
             GROUP BY sale_order.id
            """,
            orders=tuple(orders.ids),
        ))
        return {
            order_id: set(duplicate_ids)
            for order_id, duplicate_ids in result
        }

    @api.depends('order_line.customer_lead', 'date_order', 'state')
    def _compute_expected_date(self):
        """ For service and combo (non-goods) products, we avoid computing the expected date. This method is extended in sale_stock to
            take the picking_policy of SO into account.
        """
        self.mapped("order_line")  # Prefetch indication
        for order in self:
            if order.state == 'cancel':
                order.expected_date = False
                continue
            dates_list = order.order_line.filtered(
                lambda line: line.product_id.type == 'consu' and not line.display_type and not line._is_delivery()
            ).mapped(lambda line: line and line._expected_date())
            if dates_list:
                order.expected_date = order._select_expected_date(dates_list)
            else:
                order.expected_date = False

    def _select_expected_date(self, expected_dates):
        self.ensure_one()
        return min(expected_dates)

    def _compute_is_expired(self):
        today = fields.Date.today()
        for order in self:
            order.is_expired = (
                order.state in ('draft', 'sent')
                and order.validity_date
                and order.validity_date < today
            )

    @api.depends('company_id', 'fiscal_position_id')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    @api.depends('order_line.amount_to_invoice')
    def _compute_amount_to_invoice(self):
        for order in self:
            order.amount_to_invoice = sum(order.order_line.mapped('amount_to_invoice'))

    @api.depends('order_line.amount_invoiced')
    def _compute_amount_invoiced(self):
        for order in self:
            order.amount_invoiced = sum(order.order_line.mapped('amount_invoiced'))

    @api.depends('company_id', 'partner_id', 'amount_total')
    def _compute_partner_credit_warning(self):
        for order in self:
            order.with_company(order.company_id)
            order.partner_credit_warning = ''
            show_warning = order.state in ('draft', 'sent') and \
                           order.company_id.account_use_credit_limit
            if show_warning:
                order.partner_credit_warning = self.env['account.move']._build_credit_warning_message(
                    order.sudo(),  # ensure access to `credit` & `credit_limit` fields
                    current_amount=(order.amount_total / order.currency_rate),
                )

    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order._get_priced_lines()
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            if record.state in ('draft', 'sent', 'cancel'):
                record.type_name = _("Quotation")
            else:
                record.type_name = _("Sales Order")

    # portal.mixin override
    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/my/orders/{order.id}'

    @api.depends('partner_id.name', 'partner_id.sale_warn_msg', 'order_line.sale_line_warn_msg')
    def _compute_sale_warning_text(self):
        if not self.env.user.has_group('sale.group_warning_sale'):
            self.sale_warning_text = ''
            return
        for order in self:
            warnings = OrderedSet()
            if partner_msg := order.partner_id.sale_warn_msg:
                warnings.add((order.partner_id.name or order.partner_id.display_name) + ' - ' + partner_msg)
            if partner_parent_msg := order.partner_id.parent_id.sale_warn_msg:
                parent = order.partner_id.parent_id
                warnings.add((parent.name or parent.display_name) + ' - ' + partner_parent_msg)
            for line in order.order_line:
                if product_msg := line.sale_line_warn_msg:
                    warnings.add(line.product_id.display_name + ' - ' + product_msg)
            order.sale_warning_text = '\n'.join(warnings)

    #=== CONSTRAINT METHODS ===#

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

    @api.constrains('prepayment_percent')
    def _check_prepayment_percent(self):
        for order in self:
            if order.require_payment and not (0 < order.prepayment_percent <= 1.0):
                raise ValidationError(_("Prepayment percentage must be a valid percentage."))

    #=== ONCHANGE METHODS ===#

    def onchange(self, values, field_names, fields_spec):
        self_with_context = self
        if not field_names:
            self_with_context = self.with_context(
                # Some warnings should not be displayed for the first onchange
                sale_onchange_first_call=True,
                # invoice & delivery address with higher `customer_rank` should take priority
                res_partner_search_mode='customer',
            )
        return super(SaleOrder, self_with_context).onchange(values, field_names, fields_spec)

    @api.onchange('commitment_date', 'expected_date')
    def _onchange_commitment_date(self):
        """ Warn if the commitment dates is sooner than the expected date """
        if self.commitment_date and self.expected_date and self.commitment_date < self.expected_date:
            return {
                'warning': {
                    'title': _('Requested date is too soon.'),
                    'message': _("The delivery date is sooner than the expected date."
                                 " You may be unable to honor the delivery date.")
                }
            }

    @api.onchange('company_id')
    def _onchange_company_id_warning(self):
        self.show_update_pricelist = True
        if self.env.context.get('sale_onchange_first_call'):
            return
        if self.order_line and self.state == 'draft':
            return {
                'warning': {
                    'title': _("Warning for the change of your quotation's company"),
                    'message': _("Changing the company of an existing quotation might need some "
                                 "manual adjustments in the details of the lines. You might "
                                 "consider updating the prices."),
                }
            }

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for order in self:
            # This can't be caught by a python constraint as it is only triggered at save
            # and a compute methodd needs this data to be set correctly before saving
            if not order.company_id:
                raise ValidationError(_("The company is required, please select one before making any other changes to the sale order."))

    @api.onchange('fiscal_position_id')
    def _onchange_fpos_id_show_update_fpos(self):
        if self.order_line and (
            not self.fiscal_position_id
            or (self.fiscal_position_id and self._origin.fiscal_position_id != self.fiscal_position_id)
        ):
            self.show_update_fpos = True

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id_show_update_prices(self):
        self.show_update_pricelist = bool(self.order_line and self._origin.pricelist_id != self.pricelist_id)

    @api.onchange('prepayment_percent')
    def _onchange_prepayment_percent(self):
        if not self.prepayment_percent:
            self.require_payment = False

    @api.onchange('order_line')
    def _onchange_order_line(self):
        for index, line in enumerate(self.order_line):
            if line.display_type == 'line_subsection' and not line.parent_id:
                line.display_type = 'line_section'
            combo_item_lines = line._get_linked_lines().filtered('combo_item_id')
            if line.product_template_id.type != 'combo':
                if combo_item_lines:
                    # Delete any linked combo item lines if the line's product is no longer a combo
                    # product.
                    self.order_line = [
                        Command.delete(linked_line.id) for linked_line in combo_item_lines
                    ]
            elif line.selected_combo_items:
                selected_combo_items = json.loads(line.selected_combo_items)
                if (
                    selected_combo_items
                    and len(selected_combo_items) != len(line.product_template_id.sudo().combo_ids)
                ):
                    raise ValidationError(_(
                        "The number of selected combo items must match the number of available"
                        " combo choices."
                    ))

                # Delete any existing combo item lines.
                delete_commands = [Command.delete(linked_line.id) for linked_line in combo_item_lines]
                # Create a new combo item line for each selected combo item.
                create_commands = [Command.create({
                    'product_id': combo_item['product_id'],
                    'product_uom_qty': line.product_uom_qty,
                    'combo_item_id': combo_item['combo_item_id'],
                    'product_no_variant_attribute_value_ids': [
                        Command.set(combo_item['no_variant_attribute_value_ids'])
                    ],
                    'product_custom_attribute_value_ids': [Command.clear()] + [
                        Command.create(attribute_value)
                        for attribute_value in combo_item['product_custom_attribute_values']
                    ],
                    # Combo item lines should come directly after their combo product line.
                    'sequence': line.sequence + item_index + 1,
                    # If the linked line exists in DB, populate linked_line_id, otherwise populate
                    # linked_virtual_id.
                    'linked_line_id': line.id if line._origin else False,
                    'linked_virtual_id': line.virtual_id if not line._origin else False,
                }) for item_index, combo_item in enumerate(selected_combo_items)]
                # Shift any lines coming after the combo product line so that the combo item lines
                # come first.
                update_commands = [Command.update(
                    order_line.id,
                    {'sequence': order_line.sequence + len(selected_combo_items)},
                ) for order_line in self.order_line if order_line.sequence > line.sequence]

                # Clear `selected_combo_items` to avoid applying the same changes multiple times.
                line.selected_combo_items = False
                self.order_line = delete_commands + create_commands + update_commands
            elif (
                combo_item_lines
                # Only update the combo item lines if the line's combo choices haven't changed.
                and combo_item_lines.combo_item_id.combo_id == line.product_template_id.combo_ids
            ):
                combo_item_lines.update({
                    'product_uom_qty': line.product_uom_qty,
                    'discount': line.discount,
                })

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order'])
                ) if 'date_order' in vals else None
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code(
                    'sale.order', sequence_date=seq_date) or _("New")

        return super().create(vals_list)

    def _get_copiable_order_lines(self):
        """Returns the order lines that can be copied to a new order."""
        return self.order_line.filtered(lambda l: not l.is_downpayment)

    def copy_data(self, default=None):
        default = dict(default or {})
        default_has_no_order_line = 'order_line' not in default
        default.setdefault('order_line', [])
        vals_list = super().copy_data(default=default)
        if default_has_no_order_line:
            for order, vals in zip(self, vals_list):
                vals['order_line'] = [
                    Command.create(line_vals)
                    for line_vals in order._get_copiable_order_lines().copy_data()
                ]
        return vals_list

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancel(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_(
                    "You can not delete a sent quotation or a confirmed sales order."
                    " You must first cancel it."))

    def write(self, vals):
        if 'pricelist_id' in vals and any(so.state == 'sale' for so in self):
            raise UserError(_("You cannot change the pricelist of a confirmed order !"))
        return super().write(vals)

    #=== ACTION METHODS ===#

    @api.readonly
    def action_open_discount_wizard(self):
        self.ensure_one()
        return {
            'name': _("Discount"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.discount',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.filtered(lambda so: so.state in ('draft', 'sent')).order_line._validate_analytic_distribution()

        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'email_notification_allow_footer': True,
            'hide_mail_template_management_options': True,
            'proforma': self.env.context.get('proforma', False),
        }

        if len(self) > 1:
            ctx['default_composition_mode'] = 'mass_mail'
        else:
            ctx.update({
                'force_email': True,
            })
            if not self.env.context.get('hide_default_template'):
                mail_template = self._find_mail_template()
                if mail_template:
                    ctx.update({
                        'default_template_id': mail_template.id,
                        'mark_so_as_sent': True,
                    })
            else:
                for order in self:
                    order._portal_ensure_token()

        action = {
            'name': _('Send'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        if (
            self.env.context.get('check_document_layout')
            and not self.env.context.get('discard_logo_check')
            and self.env.is_admin()
            and not self.env.company.external_report_layout_id
        ):
            layout_action = self.env['ir.actions.report']._action_configure_external_report_layout(
                action,
            )
            # Need to remove this context for windows action
            action.pop('close_on_report_download', None)
            layout_action['context']['dialog_size'] = 'extra-large'
            return layout_action
        return action

    def _find_mail_template(self):
        """ Get the appropriate mail template for the current sales order based on its state.

        If the SO is confirmed, we return the mail template for the sale confirmation.
        Otherwise, we return the quotation email template.

        :return: The correct mail template based on the current status
        :rtype: record of `mail.template` or `None` if not found
        """
        self.ensure_one()
        if self.env.context.get('proforma'):
            return self.env.ref('sale.email_template_proforma', raise_if_not_found=False)
        elif self.state != 'sale':
            return self.env.ref('sale.email_template_edi_sale', raise_if_not_found=False)
        else:
            return self._get_confirmation_template()

    def _get_confirmation_template(self):
        """ Get the mail template sent on SO confirmation (or for confirmed SO's).

        :return: `mail.template` record or None if default template wasn't found
        """
        self.ensure_one()
        default_confirmation_template_id = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_confirmation_template'
        )
        default_confirmation_template = default_confirmation_template_id \
            and self.env['mail.template'].browse(int(default_confirmation_template_id)).exists()
        if default_confirmation_template:
            return default_confirmation_template
        else:
            return self.env.ref('sale.mail_template_sale_confirmation', raise_if_not_found=False)

    def action_quotation_sent(self):
        """ Mark the given draft quotation(s) as sent.

        :raise: UserError if any given SO is not in draft state.
        """
        if any(order.state != 'draft' for order in self):
            raise UserError(_("Only draft orders can be marked as sent directly."))

        self.write({'state': 'sent'})

    def action_confirm(self):
        """ Confirm the given quotation(s) and set their confirmation date.

        If the corresponding setting is enabled, also locks the Sale Order.

        :return: True
        :rtype: bool
        :raise: UserError if trying to confirm cancelled SO's
        """
        for order in self:
            error_msg = order._confirmation_error_message()
            if error_msg:
                raise UserError(error_msg)

        self.order_line._validate_analytic_distribution()

        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self.env.context.copy()
        context.pop('default_name', None)
        context.pop('default_user_id', None)

        self.with_context(context)._action_confirm()
        self.filtered(lambda so: so._should_be_locked()).action_lock()

        if self.env.context.get('send_email'):
            self._send_order_confirmation_mail()

        return True

    def _should_be_locked(self):
        self.ensure_one()
        # Public user can confirm SO, so we check the group on any record creator.
        return self.env['res.groups']._is_feature_enabled('sale.group_auto_done_setting')

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("Some order lines are missing a product, you need to correct them before going further.")

        return False

    def _prepare_confirmation_values(self):
        """ Prepare the sales order confirmation values.

        Note: self can contain multiple records.

        :return: Sales Order confirmation values
        :rtype: dict
        """
        return {
            'state': 'sale',
            'date_order': fields.Datetime.now()
        }

    def _action_confirm(self):
        """ Implementation of additional mechanism of Sales Order confirmation.
            This method should be extended when the confirmation should generated
            other documents. In this method, the SO are in 'sale' state (not yet 'done').
        """

    def _send_order_confirmation_mail(self):
        """ Send a mail to the SO customer to inform them that their order has been confirmed.

        :return: None
        """
        for order in self:
            mail_template = order._get_confirmation_template()
            order._send_order_notification_mail(mail_template)

    def _send_payment_succeeded_for_order_mail(self):
        """ Send a mail to the SO customer to inform them that a payment has been initiated.

        :return: None
        """
        mail_template = self.env.ref(
            'sale.mail_template_sale_payment_executed', raise_if_not_found=False
        )
        for order in self:
            order._send_order_notification_mail(mail_template)

    def _send_order_notification_mail(self, mail_template, allow_deferred_sending=True):
        """ Send a mail to the customer.

        If the `sale.async_emails` ICP is set and `allow_deferred_sending` is true, order status
        emails are sent asynchronously through a cron.

        Note: self.ensure_one()

        :param mail.template mail_template: the template used to generate the mail
        :param bool allow_deferred_sending: Whether the email can be sent asynchronously.
        :return: None
        """
        self.ensure_one()

        if not mail_template:
            return

        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)

        async_send = str2bool(self.env['ir.config_parameter'].sudo().get_param('sale.async_emails'))
        cron = self.env.ref('sale.send_pending_emails_cron', raise_if_not_found=False)
        cron_enabled = cron and cron.sudo().active
        if async_send and cron_enabled and allow_deferred_sending:
            # Schedule the email to be sent asynchronously.
            self.pending_email_template_id = mail_template
            cron._trigger()
        else:  # Async emails are disabled, either by the user or we are in the cron job.
            # Send the email synchronously.
            self.with_context(force_send=True).message_post_with_source(
                mail_template,
                email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
                subtype_xmlid='mail.mt_comment',
            )

    def _validate_order(self):
        """Confirm the sale order and send a confirmation email.

        :return: None
        """
        self.with_context(send_email=True).action_confirm()

    @api.model
    def _cron_send_pending_emails(self):
        """ Find and send pending order status emails asynchronously.

        :return: None
        """
        pending_email_orders = self.search([('pending_email_template_id', '!=', False)])
        self.env['ir.cron']._commit_progress(remaining=len(pending_email_orders))
        for order in pending_email_orders:
            order = order[0]  # Avoid pre-fetching after each cache invalidation due to committing.
            order._send_order_notification_mail(
                order.pending_email_template_id, allow_deferred_sending=False
            )  # Resume the email sending.
            order.pending_email_template_id = None
            remaining_time = self.env['ir.cron']._commit_progress(processed=1)
            if not remaining_time:
                break

    def action_lock(self):
        self.locked = True

    def action_unlock(self):
        self.locked = False

    def action_cancel(self):
        """ Cancel sales order and related draft invoices. """
        if any(order.locked for order in self):
            raise UserError(_("You cannot cancel a locked order. Please unlock it first."))
        return self._action_cancel()

    def _action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()
        return self.write({'state': 'cancel'})

    @api.readonly
    def action_preview_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def action_update_taxes(self):
        self.ensure_one()

        self._recompute_taxes()

        if self.partner_id:
            self.message_post(body=_("Product taxes have been recomputed according to fiscal position %s.",
                self.fiscal_position_id._get_html_link() if self.fiscal_position_id else "")
            )

    def _recompute_taxes(self):
        lines_to_recompute = self.order_line.filtered(lambda line: not line.display_type)
        lines_to_recompute._compute_tax_ids()
        self.show_update_fpos = False

    def action_update_prices(self):
        self.ensure_one()

        self._recompute_prices()

        if self.pricelist_id:
            message = _("Product prices have been recomputed according to pricelist %s.",
                self.pricelist_id._get_html_link())
        else:
            message = _("Product prices have been recomputed.")
        self.message_post(body=message)

    def _recompute_prices(self):
        lines_to_recompute = self._get_update_prices_lines()
        lines_to_recompute.invalidate_recordset(['pricelist_item_id'])
        lines_to_recompute.with_context(force_price_recomputation=True)._compute_price_unit()
        # Special case: we want to overwrite the existing discount on _recompute_prices call
        # i.e. to make sure the discount is correctly reset
        # if pricelist rule is different than when the price was first computed.
        lines_to_recompute.discount = 0.0
        lines_to_recompute._compute_discount()
        self.show_update_pricelist = False

    def _default_order_line_values(self, child_field=False):
        default_data = super()._default_order_line_values(child_field)
        new_default_data = self.env['sale.order.line']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            'product_catalog_currency_id': self.currency_id.id,
            'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
            'show_sections': bool(self.id),
        }

    def _get_product_catalog_domain(self):
        return super()._get_product_catalog_domain() & Domain('sale_ok', '=', True)

    @api.readonly
    def action_open_business_doc(self):
        self.ensure_one()
        return {
            'name': _("Order"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.id,
            'views': [(False, 'form')],
        }

    # INVOICING #

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        txs_to_be_linked = self.sudo().transaction_ids.filtered(
            lambda tx: (
                tx.state in ('pending', 'authorized')
                or (tx.state == 'done' and not tx.payment_id.is_reconciled)
            )
        )

        values = {
            'ref': self.client_order_ref or self.name,
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(self.partner_invoice_id)).id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'preferred_payment_method_line_id': self.preferred_payment_method_line_id.id,
            'invoice_user_id': self.user_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [Command.set(txs_to_be_linked.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            'user_id': self.user_id.id,
        }
        if self.journal_id:
            values['journal_id'] = self.journal_id.id
        return values

    @api.readonly
    def action_view_invoice(self, invoices=False):
        if not invoices:
            invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
            })
        action['context'] = context
        return action

    def _get_invoice_grouping_keys(self):
        return ['company_id', 'partner_id', 'partner_shipping_id', 'currency_id', 'fiscal_position_id']

    def _nothing_to_invoice_error_message(self):
        return _(
            "Cannot create an invoice. No items are available to invoice.\n\n"
            "To resolve this issue, please ensure that:\n"
            "   \u2022 The products have been delivered before attempting to invoice them.\n"
            "   \u2022 The invoicing policy of the product is configured correctly.\n\n"
            "If you want to invoice based on ordered quantities instead:\n"
            "   \u2022 For consumable or storable products, open the product, go to the 'General Information' tab and change the 'Invoicing Policy' from 'Delivered Quantities' to 'Ordered Quantities'.\n"
            "   \u2022 For services (and other products), change the 'Invoicing Policy' to 'Prepaid/Fixed Price'.\n"
        )

    def _get_update_prices_lines(self):
        """ Hook to exclude specific lines which should not be updated based on price list recomputation """
        return self.order_line.filtered(lambda line: not line.display_type)

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        section_line_ids = []
        subsection_line_ids = []
        precision = self.env['decimal.precision'].precision_get('Product Unit')

        for line in self.order_line:
            if line.display_type == 'line_section':
                section_line_ids = [line.id]  # Start a new section.
                subsection_line_ids = []
                continue
            if line.display_type == 'line_subsection':
                subsection_line_ids = [line.id]  # Start a new subsection.
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                # If the invoicable line is under subsection
                if subsection_line_ids:
                    if line.display_type:
                        subsection_line_ids.append(line.id)
                        continue
                    # Extend the subsection lines too if altleast one invoicable line is under subsection
                    invoiceable_line_ids.extend(section_line_ids + subsection_line_ids)
                    subsection_line_ids = []
                    section_line_ids = []
                # If the invoicable line is under section
                elif section_line_ids:
                    if line.display_type:
                        section_line_ids.append(line.id)
                        continue
                    invoiceable_line_ids.extend(section_line_ids)
                    section_line_ids = []
                    subsection_line_ids = []
                invoiceable_line_ids.append(line.id)

        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _create_account_invoices(self, invoice_vals_list, final):
        """Small method to allow overriding the behavior right after an invoice is created."""
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        return self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

    def _create_invoices(self, grouped=False, final=False, date=None):
        """ Create invoice(s) for the given Sales Order(s).

        :param bool grouped: if True, invoices are grouped by SO id.
            If False, invoices are grouped by keys returned by :meth:`_get_invoice_grouping_keys`
        :param bool final: if True, refunds will be generated if necessary
        :param date: unused parameter
        :returns: created invoices
        :rtype: `account.move` recordset
        :raises: UserError if one of the orders has no invoiceable lines.
        """
        if not self.env['account.move'].has_access('create'):
            try:
                self.check_access('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            if order.partner_invoice_id.lang:
                order = order.with_context(lang=order.partner_invoice_id.lang)
            order = order.with_company(order.company_id)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if all(line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        Command.create(
                            order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1

                optional_values = {'sequence': invoice_item_sequence}

                # When creating the final invoice, we want to express the lines representing
                # the full order but negate the already created down payment lines.
                # At this point, on the sale order, the down payment lines have a non-empty
                # 'extra_tax_data' containing a price unit greater than zero and a quantity of 0.0.
                if line.is_downpayment:
                    optional_values['quantity'] = -1.0
                    optional_values['extra_tax_data'] = self.env['account.tax']\
                        ._reverse_quantity_base_line_extra_tax_data(line.extra_tax_data)

                for vals in line._prepare_invoice_lines_vals_list(**optional_values):
                    invoice_line_vals.append(Command.create(vals))

                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self.env.context.get('raise_if_nothing_to_invoice', True):
            raise UserError(self._nothing_to_invoice_error_message())

        # 2) Manage 'grouped' parameter: group by (partner_id, partner_shipping_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for _grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        moves = self._create_account_invoices(invoice_vals_list, final)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final and (moves_to_switch := moves.sudo().filtered(lambda m: m.amount_total < 0)):
            with self.env.protecting([moves._fields['team_id']], moves_to_switch):
                moves_to_switch.action_switch_move_type()
                self.invoice_ids._set_reversed_entry(moves_to_switch)

        for move in moves:
            move.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
                subtype_xmlid='mail.mt_note',
            )
        return moves

    # MAIL #

    def _discard_tracking(self):
        self.ensure_one()
        return (
            self.state == 'draft'
            and request and request.env.context.get('catalog_skip_tracking')
        )

    def _track_finalize(self):
        """ Override of `mail` to prevent logging changes when the SO is in a draft state. """
        if (len(self) == 1
            # The method _track_finalize is sometimes called too early or too late and it
            # might cause a desynchronization with the cache, thus this condition is needed.
            and self.env.cache.contains(self, self._fields['state']) and self._discard_tracking()):
            self.env.cr.precommit.data.pop(f'mail.tracking.{self._name}', {})
            self.env.flush_all()
            return
        return super()._track_finalize()

    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'sent'})
            kwargs['notify_author_mention'] = kwargs.get('notify_author_mention', True)
        return super().message_post(**kwargs)

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=False):
        # Give access button to users and portal customer as portal is integrated
        # in sale. Customer and portal group have probably no right to see
        # the document so they don't have the access button.
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups

        self.ensure_one()
        if self.env.context.get('proforma'):
            for group in [g for g in groups if g[0] in ('portal_customer', 'portal', 'follower', 'customer')]:
                group[2]['has_button_access'] = False
            return groups
        local_msg_vals = dict(msg_vals or {})

        # portal customers have full access (existence not granted, depending on partner_id)
        try:
            customer_portal_group = next(group for group in groups if group[0] == 'portal_customer')
        except StopIteration:
            pass
        else:
            access_opt = customer_portal_group[2].setdefault('button_access', {})
            is_tx_pending = self.get_portal_last_transaction().state == 'pending'
            if self._has_to_be_signed():
                if self._has_to_be_paid():
                    access_opt['title'] = _("View Quotation") if is_tx_pending else _("Sign & Pay Quotation")
                else:
                    access_opt['title'] = _("Accept & Sign Quotation")
            elif self._has_to_be_paid() and not is_tx_pending:
                access_opt['title'] = _("Accept & Pay Quotation")
            elif self.state in ('draft', 'sent'):
                access_opt['title'] = _("View Quotation")

        return groups

    def _notify_by_email_prepare_rendering_context(self, message, msg_vals=False, model_description=False,
                                                   force_email_company=False, force_email_lang=False,
                                                   force_record_name=False):
        render_context = super()._notify_by_email_prepare_rendering_context(
            message, msg_vals=msg_vals, model_description=model_description,
            force_email_company=force_email_company, force_email_lang=force_email_lang,
            force_record_name=force_record_name,
        )
        lang_code = render_context.get('lang')
        record = render_context['record']
        subtitles = [f"{record.name} - {record.partner_id.name}" if record.partner_id.name else record.name]
        if self.amount_total:
            # Do not show the price in subtitles if zero (e.g. e-commerce orders are created empty)
            subtitles.append(
                format_amount(self.env, self.amount_total, self.currency_id, lang_code=lang_code),
            )

        render_context['subtitles'] = subtitles
        return render_context

    def _phone_get_number_fields(self):
        """ No phone or mobile field is available on sale model. Instead SMS will
        fallback on partner-based computation using ``_mail_get_partner_fields``. """
        return []

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'sale':
            return self.env.ref('sale.mt_order_confirmed')
        elif 'state' in init_values and self.state == 'sent':
            return self.env.ref('sale.mt_order_sent')
        return super()._track_subtype(init_values)

    # PAYMENT #

    def _force_lines_to_invoice_policy_order(self):
        """Force the qty_to_invoice to be computed as if the invoice_policy
        was set to "Ordered quantities", independently of the product configuration.

        This is needed for the automatic invoice logic, as we want to automatically
        invoice the full SO when it's paid.
        """
        for line in self.order_line:
            if line.state == 'sale':
                # No need to set 0 as it is already the standard logic in the compute method.
                line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced

    def payment_action_capture(self):
        """ Capture all transactions linked to this sale order. """
        self.ensure_one()
        payment_utils.check_rights_on_recordset(self)

        # In sudo mode to bypass the checks on the rights on the transactions.
        return self.sudo().transaction_ids.action_capture()

    def payment_action_void(self):
        """ Void all transactions linked to this sale order. """
        payment_utils.check_rights_on_recordset(self)

        # In sudo mode to bypass the checks on the rights on the transactions.
        self.sudo().authorized_transaction_ids.action_void()

    def get_portal_last_transaction(self):
        self.ensure_one()
        return self.sudo().transaction_ids._get_last()

    def _get_order_lines_to_report(self):
        down_payment_lines = self.order_line.filtered(lambda line:
            line.is_downpayment
            and not line.display_type
            and not line._get_downpayment_state()
        )

        def show_line(line):
            if line.is_downpayment:
                return (
                    # Only show the down payment section if down payments were posted
                    (line.display_type and down_payment_lines)
                    # Only show posted down payments
                    or line in down_payment_lines
                )
            return (
                line.display_type == 'line_section'
                or not (
                    line.parent_id.collapse_composition
                    or line.parent_id.parent_id.collapse_composition
                )
            )

        return self.order_line.filtered(show_line)

    def _get_default_payment_link_values(self):
        """ Override of `payment` to compute the default values of the payment link wizard. """
        self.ensure_one()

        prepayment_amount = self._get_prepayment_required_amount()
        remaining_balance = self.amount_total - self.amount_paid
        if self.state in ('draft', 'sent') and self.require_payment:
            suggested_amount = prepayment_amount  # Suggest the amount needed to confirm the quote.
        else:  # The order is confirmed or doesn't require payment.
            suggested_amount = remaining_balance
        return {
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_invoice_id.id,
            'amount': suggested_amount,
            'amount_max': remaining_balance,
            'amount_paid': self.amount_paid,
            'prepayment_amount': prepayment_amount,
        }

    # EDI #

    def _get_edi_builders(self):
        return []

    def create_document_from_attachment(self, attachment_ids):
        """ Create the sale orders from given attachment_ids and redirect newly create order view.

        :param list attachment_ids: List of attachments process.
        :return: An action redirecting to related sale order view.
        :rtype: dict
        """
        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            raise UserError(_("No attachment was provided"))

        orders = self.with_context(default_partner_id=self.env.user.partner_id.id)._create_records_from_attachments(attachments)

        return orders._get_records_action(name=_("Generated Orders"))

    # PORTAL #

    def _has_to_be_signed(self):
        """A sale order has to be signed when:
        - its state is 'draft' or `sent`
        - it's not expired;
        - it requires a signature;
        - it's not already signed.

        Note: self.ensure_one()

        :return: Whether the sale order has to be signed.
        :rtype: bool
        """
        self.ensure_one()
        return (
            self.state in ['draft', 'sent']
            and not self.is_expired
            and self.require_signature
            and not self.signature
        )

    def _has_to_be_paid(self):
        """A sale order has to be paid when:
        - its state is 'draft' or `sent`;
        - it's not expired;
        - it requires a payment;
        - the last transaction's state isn't `done`;
        - the total amount is strictly positive.
        - confirmation amount is not reached

        Note: self.ensure_one()

        :return: Whether the sale order has to be paid.
        :rtype: bool
        """
        self.ensure_one()
        return (
            self.state in ['draft', 'sent']
            and not self.is_expired
            and self.require_payment
            and self.amount_total > 0
            and not self._is_confirmation_amount_reached()
        )

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('sale.action_quotations_with_onboarding')

    def _get_name_portal_content_view(self):
        """ This method can be inherited by localizations who want to localize the online quotation view. """
        self.ensure_one()
        return 'sale.sale_order_portal_content'

    def _get_name_tax_totals_view(self):
        """ This method can be inherited by localizations who want to localize the taxes displayed on the portal and sale order report. """
        return 'sale.document_tax_totals'

    def _get_report_base_filename(self):
        self.ensure_one()
        return f'{self.type_name} {self.name}'

    #=== CORE METHODS OVERRIDES ===#

    @api.model
    def get_empty_list_help(self, help_message):
        self = self.with_context(
            empty_list_help_document_name=_("sale order"),
        )
        return super().get_empty_list_help(help_message)

    def _compute_field_value(self, field):
        if field.name != 'invoice_status' or self.env.context.get('mail_activity_automation_skip'):
            return super()._compute_field_value(field)

        filtered_self = self.filtered(
            lambda so: so.ids
                and (so.user_id or so.partner_id.user_id)
                and so._origin.invoice_status != 'upselling')
        super()._compute_field_value(field)

        upselling_orders = filtered_self.filtered(lambda so: so.invoice_status == 'upselling')
        upselling_orders._create_upsell_activity()

    #=== BUSINESS METHODS ===#

    def _create_upsell_activity(self):
        if not self:
            return

        self.activity_unlink(['mail.mail_activity_data_todo'])
        for order in self:
            order_ref = order._get_html_link()
            customer_ref = order.partner_id._get_html_link()
            order.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=order.user_id.id or order.partner_id.user_id.id,
                note=_("Upsell %(order)s for customer %(customer)s", order=order_ref, customer=customer_ref))

    def _prepare_analytic_account_data(self, prefix=None):
        """ Prepare SO analytic account creation values.

        :return: `account.analytic.account` creation values
        :rtype: dict
        """
        self.ensure_one()
        name = self.name
        if prefix:
            name = prefix + ": " + self.name
        project_plan, _other_plans = self.env['account.analytic.plan']._get_all_plans()
        return {
            'name': name,
            'code': self.client_order_ref,
            'company_id': self.company_id.id,
            'plan_id': project_plan.id,
            'partner_id': self.partner_id.id,
        }

    def _prepare_down_payment_section_line(self, **optional_values):
        """ Prepare the values to create a new down payment section.

        :param dict optional_values: any parameter that should be added to the returned down payment section
        :return: `account.move.line` creation values
        :rtype: dict
        """
        self.ensure_one()
        context = {'lang': self.partner_id.lang}
        down_payments_section_line = {
            'display_type': 'line_section',
            'name': _("Down Payments"),
            'product_id': False,
            'product_uom_id': False,
            'quantity': 0,
            'discount': 0,
            'price_unit': 0,
            'account_id': False,
            **optional_values
        }
        del context
        return down_payments_section_line

    def _create_down_payment_lines_from_base_lines(self, down_payment_base_lines):
        """ Add the base lines passed as parameter as sale order lines into the current sale order.

        :param down_payment_base_lines: A list of base lines
                                        (see '_prepare_base_line_for_taxes_computation').
        :return The newly created SO lines.
        """
        self.ensure_one()
        sequence = max(self.order_line.mapped('sequence') or [10]) + 1
        return self.env['sale.order.line'] \
            .with_context(sale_no_log_for_new_lines=True) \
            .create([
                {
                    **self._prepare_down_payment_line_values_from_base_line(base_line),
                    'sequence': sequence + index,
                }
                for index, base_line in enumerate(down_payment_base_lines)
            ])

    def _create_down_payment_section_line_if_needed(self):
        """ Add the down section line if not already there on the current SO.

        :return The newly created SO line or None if the section was already there.
        """
        self.ensure_one()
        # If a down payment is already there, then the section is not needed and
        # has already been created.
        if any(line.display_type and line.is_downpayment for line in self.order_line):
            return

        sequence = max(self.order_line.mapped('sequence') or [10]) + 1
        return self.env['sale.order.line'] \
            .with_context(sale_no_log_for_new_lines=True) \
            .create({
                **self._prepare_down_payment_line_section_values(),
                'sequence': sequence,
            })

    def _prepare_down_payment_line_section_values(self):
        """ Prepare the values to create a section line for the down payment on the current SO.

        :return: A dictionary to create a new SO section line.
        """
        self.ensure_one()
        return {
            'order_id': self.id,
            'display_type': 'line_section',
            'is_downpayment': True,
        }

    def _prepare_down_payment_line_values_from_base_line(self, base_line):
        """ Convert the base line passed as parameter representing a down payment into a
        dictionary to be converted into a sale order line in the current sale order.

        :param base_line: A base line (see '_prepare_base_line_for_taxes_computation').
        :return: A dictionary to create a new SO line.
        """
        self.ensure_one()
        extra_tax_data = self.env['account.tax']._export_base_line_extra_tax_data(base_line)
        return {
            'order_id': self.id,
            'is_downpayment': True,
            'product_uom_qty': 0.0,
            'price_unit': base_line['price_unit'],
            'tax_ids': [Command.set(base_line['tax_ids'].ids)],
            'analytic_distribution': base_line['analytic_distribution'],
            'extra_tax_data': extra_tax_data,
        }

    def _get_prepayment_required_amount(self):
        """ Return the minimum amount needed to automatically confirm the quotation.

        Note: self.ensure_one()

        :return: The minimum amount needed to automatically confirm the quotation.
        :rtype: float
        """
        self.ensure_one()

        if not self.require_payment:
            return 0
        else:
            return self.currency_id.round(self.amount_total * self.prepayment_percent)

    def _is_confirmation_amount_reached(self):
        """ Return whether `self.amount_paid` is higher than the prepayment required amount.

        Note: self.ensure_one()

        :return: Whether `self.amount_paid` is higher than the prepayment required amount.
        :rtype: bool
        """
        self.ensure_one()
        amount_comparison = self.currency_id.compare_amounts(
            self._get_prepayment_required_amount(), self.amount_paid,
        )
        return amount_comparison <= 0

    def _generate_downpayment_invoices(self):
        """ Generate invoices as down payments for sale order.

        :return: The generated down payment invoices.
        :rtype: recordset of `account.move`
        """
        generated_invoices = self.env['account.move']

        for order in self:
            downpayment_wizard = order.env['sale.advance.payment.inv'].create({
                'sale_order_ids': order,
                'advance_payment_method': 'fixed',
                'fixed_amount': order.amount_paid,
            })
            generated_invoices |= downpayment_wizard._create_invoices(order)

        return generated_invoices

    # === CATALOG === #

    def _get_product_catalog_order_data(self, products, **kwargs):
        pricelist = self.pricelist_id._get_products_price(
            quantity=1.0,
            products=products,
            currency=self.currency_id,
            date=self.date_order,
            **kwargs,
        )
        res = super()._get_product_catalog_order_data(products, **kwargs)
        has_warning_group = self.env.user.has_group('sale.group_warning_sale')
        for product in products:
            res[product.id]['price'] = pricelist.get(product.id)
            if product.sale_line_warn_msg and has_warning_group:
                res[product.id]['warning'] = product.sale_line_warn_msg
        return res

    def _get_product_catalog_record_lines(self, product_ids, *, section_id=None, **kwargs):
        grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
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

    def _get_parent_field_on_child_model(self):
        return 'order_id'

    def _update_order_line_info(
        self, product_id, quantity, *, section_id=False, child_field='order_line', **kwargs
    ):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :param int quantity: The quantity selected in the catalog.
        :param int section_id: The id of section selected in the catalog.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        request.update_context(catalog_skip_tracking=True)
        sol = self.order_line.filtered(
            lambda l: l.product_id.id == product_id
            and l.get_parent_section_line().id == section_id,
        )
        if sol:
            if quantity != 0:
                sol.product_uom_qty = quantity
            elif self.state in ['draft', 'sent']:
                price_unit = self.pricelist_id._get_product_price(
                    product=sol.product_id,
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                    **kwargs,
                )
                sol.unlink()
                return price_unit
            else:
                sol.product_uom_qty = 0
        elif quantity > 0:
            sol = self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
                'sequence': self._get_new_line_sequence(child_field, section_id),
            })
        else:  # quantity of 0, no line to update, return defaut pricelist price
            return self.pricelist_id._get_product_price(
                product=self.env['product.product'].browse(product_id),
                quantity=1.0,
                currency=self.currency_id,
                date=self.date_order,
                **kwargs,
            )

        return sol._get_discounted_price()

    # === Product Documents === #

    def _get_product_documents(self):
        self.ensure_one()

        documents = (
            self.order_line.product_id.product_document_ids
            | self.order_line.product_template_id.product_document_ids
        )
        return self._filter_product_documents(documents).sorted()

    def _filter_product_documents(self, documents):
        return documents.filtered(
            lambda document:
                document.attached_on_sale == 'quotation'
                or (self.state == 'sale' and document.attached_on_sale == 'sale_order')
        )

    #=== TOOLING ===#

    def _is_readonly(self):
        """ Return Whether the sale order is read-only or not based on the state or the lock status.

        A sale order is considered read-only if its state is 'cancel' or if the sale order is
        locked.

        :return: Whether the sale order is read-only or not.
        :rtype: bool
        """
        self.ensure_one()
        return self.state == 'cancel' or self.locked

    def _is_paid(self):
        """ Return whether the sale order is paid or not based on the linked transactions.

        A sale order is considered paid if the sum of all the linked transaction is equal to or
        higher than `self.amount_total`.

        :return: Whether the sale order is paid or not.
        :rtype: bool
        """
        self.ensure_one()
        return self.currency_id.compare_amounts(self.amount_paid, self.amount_total) >= 0

    def _get_lang(self):
        self.ensure_one()

        if self.partner_id.lang and not self.partner_id.is_public:
            return self.partner_id.lang

        return self.env.lang

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Quotations'),
            'template': '/sale/static/xls/quotations_import_template.xlsx',
        }]

    # For `sale_management`, to control optional products on portal
    def _can_be_edited_on_portal(self):
        self.ensure_one()
        return self.state in ('draft', 'sent')


# FILEPATH: odoo/addons/sale/models/sale_order_line.py
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['analytic.mixin']
    _description = "Sales Order Line"
    _rec_names_search = ['name', 'order_id.name']
    _order = 'order_id, sequence, id'
    _check_company_auto = True

    _accountable_required_fields = models.Constraint(
        'CHECK(display_type IS NOT NULL OR is_downpayment OR (product_id IS NOT NULL AND product_uom_id IS NOT NULL))',
        'Missing required fields on accountable sale order line.',
    )
    _non_accountable_null_fields = models.Constraint(
        'CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom_id IS NULL AND customer_lead = 0))',
        'Forbidden values on non-accountable sale order line',
    )

    # Fields are ordered according by tech & business logics
    # and computed fields are defined after their dependencies.
    # This reduces execution stacks depth when precomputing fields
    # on record creation (and is also a good ordering logic imho)

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string="Sequence", default=10)

    # Order-related fields
    company_id = fields.Many2one(
        related='order_id.company_id',
        store=True, index=True, precompute=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        depends=['order_id.currency_id'],
        store=True, precompute=True)
    order_partner_id = fields.Many2one(
        related='order_id.partner_id',
        string="Customer",
        store=True, index=True, precompute=True)
    salesman_id = fields.Many2one(
        related='order_id.user_id',
        string="Salesperson",
        store=True, precompute=True)
    state = fields.Selection(
        related='order_id.state',
        string="Order Status",
        copy=False, store=True, precompute=True)
    tax_country_id = fields.Many2one(related='order_id.tax_country_id')

    # Fields specifying custom line logic
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_subsection', "Subsection"),
            ('line_note', "Note"),
        ],
        default=False)
    is_configurable_product = fields.Boolean(
        string="Is the product configurable?",
        related='product_template_id.has_configurable_attributes',
        depends=['product_template_id'])
    is_downpayment = fields.Boolean(
        string="Is a down payment",
        help="Down payments are made when creating invoices from a sales order."
            " They are not copied when duplicating a sales order.")
    is_expense = fields.Boolean(
        string="Is expense",
        help="Is true if the sales order line comes from an expense or a vendor bills")

    # Generic configuration fields
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain=lambda self: self._domain_product_id(),
        check_company=True)
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.

        # magic way to make sure the domain integrates the check_company _domain_product_id logics
        # despite not being a check_company=True field
        domain=lambda self: self._fields['product_id']._description_domain(self.env),
    )

    product_template_attribute_value_ids = fields.Many2many(
        related='product_id.product_template_attribute_value_ids',
        depends=['product_id'])
    product_custom_attribute_value_ids = fields.One2many(
        comodel_name='product.attribute.custom.value', inverse_name='sale_order_line_id',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, readonly=False, precompute=True, copy=True)
    # M2M holding the values of product.attribute with create_variant field set to 'no_variant'
    # It allows keeping track of the extra_price associated to those attribute values and add them to the SO line description
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')
    is_product_archived = fields.Boolean(compute="_compute_is_product_archived")

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)
    translated_product_name = fields.Text(compute='_compute_translated_product_name')

    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit', default=1.0,
        store=True, readonly=False, required=True, precompute=True)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit",
        compute='_compute_product_uom_id',
        domain='[("id", "in", allowed_uom_ids)]',
        store=True, readonly=False, precompute=True, ondelete='restrict')
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    linked_line_id = fields.Many2one(
        string="Linked Order Line",
        comodel_name='sale.order.line',
        ondelete='cascade',
        domain="[('order_id', '=', order_id)]",
        copy=False,
        index=True,
    )
    linked_line_ids = fields.One2many(
        string="Linked Order Lines", comodel_name='sale.order.line', inverse_name='linked_line_id',
    )
    categ_id = fields.Many2one(related='product_id.categ_id')
    # Uniquely identifies this sale order line before the record is saved in the DB, i.e. before the
    # record has an `id`.
    virtual_id = fields.Char()
    # Links this sale order line to another sale order line, via its `virtual_id`.
    linked_virtual_id = fields.Char()
    # Local storage of this sale order line's selected combo items, iff this is a combo product
    # line.
    selected_combo_items = fields.Char(store=False)
    combo_item_id = fields.Many2one(comodel_name='product.combo.item')

    # Pricing fields
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_ids',
        store=True, readonly=False, precompute=True,
        context={'active_test': False, 'hide_original_tax_ids': True},
        check_company=True,
        domain="[('type_tax_use', '=', 'sale'), ('country_id', '=', tax_country_id)]",
    )

    # Tech field caching pricelist rule used for price & discount computation
    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id')

    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        min_display_digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
    technical_price_unit = fields.Float()

    discount = fields.Float(
        string="Discount (%)",
        compute='_compute_discount',
        digits='Discount',
        store=True, readonly=False, precompute=True)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True, precompute=True)
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True, precompute=True)
    price_reduce_taxexcl = fields.Monetary(
        string="Price Reduce Tax excl",
        compute='_compute_price_reduce_taxexcl',
        store=True, precompute=True)
    price_reduce_taxinc = fields.Monetary(
        string="Price Reduce Tax incl",
        compute='_compute_price_reduce_taxinc',
        store=True, precompute=True)

    customer_lead = fields.Float(
        string="Lead Time",
        compute='_compute_customer_lead',
        store=True, readonly=False, required=True, precompute=True,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    qty_delivered_method = fields.Selection(
        selection=[
            ('manual', "Manual"),
            ('analytic', "Analytic From Expenses"),
        ],
        string="Method to update delivered qty",
        compute='_compute_qty_delivered_method',
        store=True, precompute=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism:\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")
    qty_delivered = fields.Float(
        string="Delivery Quantity",
        compute='_compute_qty_delivered',
        default=0.0,
        digits='Product Unit',
        store=True, readonly=False, copy=False)

    # Analytic & Invoicing fields
    qty_invoiced = fields.Float(
        string="Invoiced Quantity",
        compute='_compute_qty_invoiced',
        digits='Product Unit',
        store=True)
    qty_invoiced_posted = fields.Float(
        string="Invoiced Quantity (posted)",
        compute='_compute_qty_invoiced_posted',
        digits='Product Unit')
    qty_to_invoice = fields.Float(
        string="Quantity To Invoice",
        compute='_compute_qty_to_invoice',
        digits='Product Unit',
        store=True)

    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='so_line',
        string="Analytic lines")

    invoice_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='sale_order_line_invoice_rel', column1='order_line_id', column2='invoice_line_id',
        string="Invoice Lines",
        copy=False)
    invoice_status = fields.Selection(
        selection=[
            ('upselling', "Upselling Opportunity"),
            ('invoiced', "Fully Invoiced"),
            ('to invoice', "To Invoice"),
            ('no', "Nothing to Invoice"),
        ],
        string="Invoice Status",
        compute='_compute_invoice_status',
        store=True)

    untaxed_amount_invoiced = fields.Monetary(
        string="Untaxed Invoiced Amount",
        compute='_compute_untaxed_amount_invoiced',
        store=True)
    amount_invoiced = fields.Monetary(
        string="Invoiced Amount",
        compute='_compute_amount_invoiced',
        compute_sudo=True,  # ensure same access as `untaxed_amount_invoiced`
    )
    untaxed_amount_to_invoice = fields.Monetary(
        string="Untaxed Amount To Invoice",
        compute='_compute_untaxed_amount_to_invoice',
        store=True)
    amount_to_invoice = fields.Monetary(
        string="Un-invoiced Balance",
        compute='_compute_amount_to_invoice',
        compute_sudo=True,  # ensure same access as `untaxed_amount_to_invoice`
    )
    amount_to_invoice_at_date = fields.Float(string='Amount', compute='_compute_amount_to_invoice_at_date')

    # Same than `qty_delivered` and `qty_invoiced` but non-stored and depending of the context.
    qty_delivered_at_date = fields.Float(
        string="Delivered",
        compute='_compute_qty_delivered_at_date',
        digits='Product Unit')
    qty_invoiced_at_date = fields.Float(
        string="Invoiced",
        compute='_compute_qty_invoiced_at_date',
        digits='Product Unit')

    # Technical field holding custom data for the taxes computation engine.
    extra_tax_data = fields.Json()

    # Technical computed fields for UX purposes (hide/make fields readonly, ...)
    product_type = fields.Selection(related='product_id.type', depends=['product_id'])
    service_tracking = fields.Selection(related='product_id.service_tracking', depends=['product_id'])
    product_updatable = fields.Boolean(
        string="Can Edit Product",
        compute='_compute_product_updatable')
    product_uom_readonly = fields.Boolean(
        compute='_compute_product_uom_readonly')
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        string='Tax calculation rounding method', readonly=True)
    company_price_include = fields.Selection(related="company_id.account_price_include")
    sale_line_warn_msg = fields.Text(compute='_compute_sale_line_warn_msg')

    # Section-related fields
    parent_id = fields.Many2one(
        string="Parent Section Line",
        comodel_name='sale.order.line',
        compute='_compute_parent_id',
    )  # The section or subsection this line belongs to.
    collapse_prices = fields.Boolean(
        string="Collapse Prices",
        copy=True,
        default=False,
    )  # Whether this section's lines' prices will be hidden in reports and in the portal.
    collapse_composition = fields.Boolean(
        string="Collapse Composition",
        copy=True,
        default=False,
    )  # Whether this section's lines will be hidden in reports and in the portal.

    #=== COMPUTE METHODS ===#

    @api.depends('order_partner_id', 'order_id', 'product_id')
    def _compute_display_name(self):
        name_per_id = self._additional_name_per_id()
        for so_line in self.sudo():
            if so_line.order_partner_id.lang:
                so_line = so_line.with_context(lang=so_line.order_id._get_lang())
            if (product := so_line.product_id).display_name:
                default_name = so_line._get_sale_order_line_multiline_description_sale()
                if so_line.name == default_name:
                    description = product.display_name
                else:
                    parts = (so_line.name or "").split('\n', 2)
                    description = parts[1] if len(parts) > 1 and parts[1] else product.display_name
            else:
                description = (so_line.name or "").split('\n', 1)[0]
            name = f"{so_line.order_id.name} - {description}"
            additional_name = name_per_id.get(so_line.id)
            if additional_name:
                name = f'{name} {additional_name}'
            so_line.display_name = name

    def _domain_product_id(self):
        return [('sale_ok', '=', True)]

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.depends('product_id')
    def _compute_is_product_archived(self):
        for line in self:
            line.is_product_archived = line.product_id and not line.product_id.active

    @api.depends('product_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_custom_attribute_value_ids = False
                continue
            if not line.product_custom_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in line.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.product_custom_attribute_value_ids -= pacv

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the no_variant attributes that don't belong to this template
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    @api.depends('product_id', 'linked_line_id', 'linked_line_ids')
    def _compute_name(self):
        for line in self:
            if not line.product_id and not line.is_downpayment:
                continue

            lang = line.order_id._get_lang()
            if lang != self.env.lang:
                line = line.with_context(lang=lang)

            if line.product_id:
                line.name = line._get_sale_order_line_multiline_description_sale()
                continue

            if line.is_downpayment:
                line.name = line._get_downpayment_description()

    def _get_sale_order_line_multiline_description_sale(self):
        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        self.ensure_one()
        description = (
            self.product_id.get_product_multiline_description_sale()
            + self._get_sale_order_line_multiline_description_variants()
        )
        if self.linked_line_id and not self.combo_item_id:
            description += "\n" + _(
                "Option for: %s",
                self.linked_line_id.product_id.with_context(display_default_code=False).display_name
            )
        return description

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin.filtered(
            # Only describe the attributes where a choice was made by the customer
            lambda ptav: ptav.display_type == 'multi' or ptav.attribute_line_id.value_count > 1
        )
        if not self.product_custom_attribute_value_ids and not no_variant_ptavs:
            return ""

        name = ""

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        multi_ptavs = no_variant_ptavs.filtered(lambda ptav: ptav.display_type == 'multi').sorted()

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - multi_ptavs - custom_ptavs):
            name += "\n" + ptav.display_name

        # display the selected values per attribute on a single for a multi checkbox
        for pta, ptavs in groupby(multi_ptavs, lambda ptav: ptav.attribute_id):
            name += "\n" + _(
                "%(attribute)s: %(values)s",
                attribute=pta.name,
                values=", ".join(ptav.name for ptav in ptavs)
            )

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        sorted_custom_ptav = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id.sorted()
        for patv in sorted_custom_ptav:
            pacv = self.product_custom_attribute_value_ids.filtered(lambda pcav: pcav.custom_product_template_attribute_value_id == patv)
            name += "\n" + pacv.display_name

        return name

    def _get_downpayment_description(self):
        self.ensure_one()
        if self.display_type:
            return _("Down Payments")

        dp_state = self._get_downpayment_state()
        name = _("Down Payment")
        if dp_state == 'draft':
            name = _(
                "Down Payment: %(date)s (Draft)",
                date=format_date(self.env, self.create_date.date()),
            )
        elif dp_state == 'cancel':
            name = _("Down Payment (Cancelled)")
        else:
            invoice = self._get_invoice_lines().filtered(
                lambda aml: aml.quantity >= 0
            ).move_id.filtered(lambda move: move.move_type == 'out_invoice')
            if len(invoice) == 1 and invoice.payment_reference and invoice.invoice_date:
                name = _(
                    "Down Payment (ref: %(reference)s on %(date)s)",
                    reference=invoice.payment_reference,
                    date=format_date(self.env, invoice.invoice_date),
                )

        return name

    @api.depends('product_id')
    def _compute_translated_product_name(self):
        for line in self:
            line.translated_product_name = line.product_id.with_context(
                lang=line.order_id._get_lang(),
            ).display_name

    @api.depends('display_type', 'product_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for line in self:
            if not line.product_uom_id or (line.product_id.uom_id.id != line.product_uom_id.id):
                line.product_uom_id = line.product_id.uom_id

    @api.depends('product_id.sale_line_warn_msg')
    def _compute_sale_line_warn_msg(self):
        has_warning_group = self.env.user.has_group('sale.group_warning_sale')
        for line in self:
            line.sale_line_warn_msg = line.product_id.sale_line_warn_msg if has_warning_group else ""

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids')
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids

    @api.depends('product_id', 'company_id')
    def _compute_tax_ids(self):
        lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
        cached_taxes = {}
        for line in self:
            if line.product_type == 'combo':
                line.tax_ids = False
                continue
            lines_by_company[line.company_id] += line
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_ids = False
                    continue
                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_ids = result

    def _get_custom_compute_tax_cache_key(self):
        """Hook method to be able to set/get cached taxes while computing them"""
        return tuple()

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type or not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    # No need for the price context, we're not considering the price here
                    product=line.product_id,
                    **line._get_pricelist_kwargs(),
                )

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_price_unit(self):
        def has_manual_price(line):
            # `line.currency_id` can be False for NewId records
            currency = (
                line.currency_id
                or line.company_id.currency_id
                or line.env.company.currency_id
            )
            return currency.compare_amounts(line.technical_price_unit, line.price_unit)

        force_recompute = self.env.context.get('force_price_recomputation')
        for line in self:
            # Don't compute the price for deleted lines or lines for which the
            # price unit doesn't come from the product.
            if not line.order_id or line.is_downpayment or line._is_global_discount():
                continue

            # check if the price has been manually set or there is already invoiced amount.
            # if so, the price shouldn't change as it might have been manually edited.
            if (
                (not force_recompute and has_manual_price(line))
                or line.qty_invoiced > 0
                or (line.product_id.expense_policy == 'cost' and line.is_expense)
            ):
                continue
            line = line.with_context(sale_write_from_compute=True)
            if not line.product_uom_id or not line.product_id:
                line.price_unit = 0.0
                line.technical_price_unit = 0.0
            else:
                line._reset_price_unit()

    def _reset_price_unit(self):
        self.ensure_one()

        line = self.with_company(self.company_id)
        price = line._get_display_price()
        product_taxes = line.product_id.taxes_id._filter_taxes_by_company(line.company_id)
        price_unit = line.product_id._get_tax_included_unit_price_from_price(
            price,
            product_taxes=product_taxes,
            fiscal_position=line.order_id.fiscal_position_id,
        )
        line.update({
            'price_unit': price_unit,
            'technical_price_unit': price_unit,
        })

    def _get_order_date(self):
        self.ensure_one()
        return self.order_id.date_order

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        if self.product_type == 'combo':
            return 0  # The display price of a combo line should always be 0.
        if self.combo_item_id:
            return self._get_combo_item_display_price()
        return self._get_display_price_ignore_combo()

    def _get_display_price_ignore_combo(self):
        """ This helper method allows to compute the display price of a SOL, while ignoring combo
        logic.

        I.e. this method returns the display price of a SOL as if it were neither a combo line nor a
        combo item line.
        """
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if not self.pricelist_item_id._show_discount():
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.pricelist_item_id._compute_price(
            product=self.product_id.with_context(**self._get_product_price_context()),
            **self._get_pricelist_kwargs(),
        )

    def _get_pricelist_kwargs(self):
        return {
            'quantity': self.product_uom_qty or 1.0,
            'uom': self.product_uom_id,
            'date': self._get_order_date(),
            'currency': self.currency_id,
        }

    def _get_product_price_context(self):
        """Gives the context for product price computation.

        :return: additional context to consider extra prices from attributes in the base product price.
        :rtype: dict
        """
        self.ensure_one()
        return self.product_id._get_product_price_context(
            self.product_no_variant_attribute_value_ids,
        )

    def _get_pricelist_price_context(self):
        """DO NOT USE in new code, this contextual logic should be dropped or heavily refactored soon"""
        self.ensure_one()
        return {
            'pricelist': self.order_id.pricelist_id.id,
            'uom': self.product_uom_id.id,
            'quantity': self.product_uom_qty,
            'date': self._get_order_date(),
        }

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.
        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.pricelist_item_id._compute_price_before_discount(
            product=self.product_id.with_context(**self._get_product_price_context()),
            **self._get_pricelist_kwargs()
        )

    def _get_combo_item_display_price(self):
        """ Compute the display price of this SOL's combo item.

        A combo item's price is a fraction of its combo product's price (i.e. the product of type
        `combo` which is referenced in this SOL's linked line). It is independent of the combo
        item's product (i.e. the product referenced in this SOL). The combo's `base_price` will be
        used to prorate the price of this combo with respect to the other combos in the combo
        product.

        Note: this method will throw if this SOL has no combo item or no linked combo product.
        """
        self.ensure_one()

        # Compute the combo product's price.
        combo_line = self._get_linked_line()
        combo_product_price = combo_line._get_display_price_ignore_combo()
        # Compute the combos' base prices.
        combo_base_prices = {
            combo_id: combo_id.currency_id._convert(
                from_amount=combo_id.base_price,
                to_currency=self.currency_id,
                company=self.company_id,
                date=self.order_id.date_order,
            ) for combo_id in combo_line.product_template_id.sudo().combo_ids
        }
        total_combo_base_price = sum(combo_base_prices.values())
        # Compute the prorated combo prices.
        combo_prices = {
            combo_id: self.currency_id.round(
                # Don't divide by total_combo_base_price if it's 0. This will make the prorating
                # wrong, but the delta will be fixed by combo_price_delta below.
                base_price * combo_product_price / (total_combo_base_price or 1)
            )
            for (combo_id, base_price) in combo_base_prices.items()
        }
        # Compute the delta between the combo product's price and the sum of its combo prices.
        # Ideally, this should be 0, but division in python isn't perfect, so we may need to adjust
        # the combo prices to make the delta 0.
        combo_price_delta = combo_product_price - sum(combo_prices.values())
        if combo_price_delta:
            combo_prices[combo_line.product_template_id.sudo().combo_ids[-1]] += combo_price_delta
        # Add the extra price of this combo item, as well as the extra prices of any `no_variant`
        # attributes to the combo price.
        return (
            combo_prices[self.combo_item_id.combo_id]
            + self.combo_item_id.extra_price
            + self.product_id._get_no_variant_attributes_price_extra(
                self.product_no_variant_attribute_value_ids
            )
        )

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_discount(self):
        discount_enabled = self.env['product.pricelist.item']._is_discount_feature_enabled()
        for line in self:
            if not line.product_id or line.display_type:
                line.discount = 0.0

            if not (line.order_id.pricelist_id and discount_enabled):
                continue

            if line.combo_item_id:
                line.discount = line._get_linked_line().discount
                continue

            line.discount = 0.0

            if not line.pricelist_item_id._show_discount():
                # No pricelist rule was found for the product
                # therefore, the pricelist didn't apply any discount/change
                # to the existing sales price.
                continue

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown to the customer
                    line.discount = discount

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        company = self.order_id.company_id or self.env.company
        base_values = {
            'tax_ids': self.tax_ids,
            'quantity': self.product_uom_qty,
            'partner_id': self.order_id.partner_id,
            'currency_id': self.order_id.currency_id or company.currency_id,
            'rate': self.order_id.currency_rate,
            'name': self.name,
        }
        if self._is_global_discount():
            base_values['special_type'] = 'global_discount'
        elif self.is_downpayment:
            base_values['special_type'] = 'down_payment'
        base_values.update(kwargs)
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(self, **base_values)

    def _is_global_discount(self):
        self.ensure_one()
        return self.extra_tax_data and self.extra_tax_data.get('computation_key', '').startswith('global_discount,')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
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

    @api.depends('price_subtotal', 'product_uom_qty')
    def _compute_price_reduce_taxexcl(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_total', 'product_uom_qty')
    def _compute_price_reduce_taxinc(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    # This computed default is necessary to have a clean computation inheritance
    # (cf sale_stock) instead of simply removing the default and specifying
    # the compute attribute & method in sale_stock.
    def _compute_customer_lead(self):
        self.customer_lead = 0.0

    @api.depends('is_expense')
    def _compute_qty_delivered_method(self):
        """ Sale module compute delivered qty for product [('type', 'in', ['consu']), ('service_type', '=', 'manual')]
                - consu + expense_policy : analytic (sum of analytic unit_amount)
                - consu + no expense_policy : manual (set manually on SOL)
                - service (+ service_type='manual', the only available option) : manual

            This is true when only sale is installed: sale_stock redifine the behavior for 'consu' type,
            and sale_timesheet implements the behavior of 'service' + service_type=timesheet.
        """
        for line in self:
            if line.is_expense:
                line.qty_delivered_method = 'analytic'
            else:  # service and consu
                line.qty_delivered_method = 'manual'

    @api.depends(
        'qty_delivered_method',
        'analytic_line_ids.so_line',
        'analytic_line_ids.unit_amount',
        'analytic_line_ids.product_uom_id')
    def _compute_qty_delivered(self):
        """ This method compute the delivered quantity of the SO lines: it covers the case provide by sale module, aka
            expense/vendor bills (sum of unit_amount of AAL), and manual case.
            This method should be overridden to provide other way to automatically compute delivered qty. Overrides should
            take their concerned so lines, compute and set the `qty_delivered` field, and call super with the remaining
            records.
        """
        delivered_qties = self._prepare_qty_delivered()
        for so_line in self:
            if not so_line.qty_delivered or so_line in delivered_qties:
                so_line.qty_delivered = delivered_qties[so_line]

    @api.depends('qty_delivered')
    @api.depends_context('accrual_entry_date')
    def _compute_qty_delivered_at_date(self):
        if not self._date_in_the_past():
            # Avoid useless compute if we don't look in the past.
            for line in self:
                line.qty_delivered_at_date = line.qty_delivered
            return
        delivered_qties = self._prepare_qty_delivered()
        for line in self:
            line.qty_delivered_at_date = delivered_qties[line]

    def _prepare_qty_delivered(self):
        # compute for analytic lines
        delivered_qties = defaultdict(float)
        lines_by_analytic = self.filtered(lambda sol: sol.qty_delivered_method == 'analytic')
        mapping = lines_by_analytic._get_delivered_quantity_by_analytic([('amount', '<=', 0.0)])
        for so_line in lines_by_analytic:
            delivered_qties[so_line] = mapping.get(so_line.id or so_line._origin.id, 0.0)
        return delivered_qties

    def _get_downpayment_state(self):
        self.ensure_one()

        if self.display_type:
            return ''

        invoice_lines = self._get_invoice_lines()
        if all(line.parent_state == 'draft' for line in invoice_lines):
            return 'draft'
        if all(line.parent_state == 'cancel' for line in invoice_lines):
            return 'cancel'

        return ''

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """ Compute and return the delivered quantity of current SO lines,
            based on their related analytic lines.
            :param additional_domain: domain to restrict AAL to include in computation (required since timesheet is an AAL with a project ...)
        """
        result = defaultdict(float)

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group analytic lines by product uom and so line
        domain = Domain.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line']._read_group(
            domain,
            ['product_uom_id', 'so_line'],
            ['unit_amount:sum', 'move_line_id:count_distinct', '__count'],
        )

        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        for uom, so_line, unit_amount_sum, move_line_id_count_distinct, count in data:
            if not uom:
                continue
            # avoid counting unit_amount twice when dealing with multiple analytic lines on the same move line
            if move_line_id_count_distinct == 1 and count > 1:
                qty = unit_amount_sum / count
            else:
                qty = unit_amount_sum
            qty = uom._compute_quantity(qty, so_line.product_uom_id, rounding_method='HALF-UP')
            result[so_line.id] += qty

        return result

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        invoiced_quantities = self._prepare_qty_invoiced()
        for line in self:
            line.qty_invoiced = invoiced_quantities[line]

    @api.depends('qty_invoiced')
    @api.depends_context('accrual_entry_date')
    def _compute_qty_invoiced_at_date(self):
        if not self._date_in_the_past():
            # Avoid useless compute if we don't look in the past.
            for line in self:
                line.qty_invoiced_at_date = line.qty_invoiced
            return
        invoiced_quantities = self._prepare_qty_invoiced()
        for line in self:
            line.qty_invoiced_at_date = invoiced_quantities[line]

    def _prepare_qty_invoiced(self):
        invoiced_qties = defaultdict(float)
        for line in self:
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    invoice_qty = invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom_id)
                    if invoice_line.move_id.move_type == 'out_invoice':
                        invoiced_qties[line] += invoice_qty
                    elif invoice_line.move_id.move_type == 'out_refund':
                        invoiced_qties[line] -= invoice_qty
        return invoiced_qties

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced_posted(self):
        """
        This method is almost identical to '_compute_qty_invoiced()'. The only difference lies in the fact that
        for accounting purposes, we only want the quantities of the posted invoices.
        We need a dedicated computation because the triggers are different and could lead to incorrect values for
        'qty_invoiced' when computed together.
        """
        for line in self:
            qty_invoiced_posted = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state == 'posted' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    qty_unsigned = invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom_id)
                    qty_signed = qty_unsigned * -invoice_line.move_id.direction_sign
                    qty_invoiced_posted += qty_signed
            line.qty_invoiced_posted = qty_invoiced_posted

    def _get_invoice_lines(self):
        self.ensure_one()
        if self.env.context.get('accrual_entry_date'):
            accrual_date = fields.Date.from_string(self.env.context['accrual_entry_date'])
            return self.invoice_lines.filtered(
                lambda l: l.move_id.invoice_date and l.move_id.invoice_date <= accrual_date
            )
        else:
            return self.invoice_lines

    # no trigger product_id.invoice_policy to avoid retroactively changing SO
    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'state')
    def _compute_qty_to_invoice(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        For combo product lines, compute the value if a linked combo item line gets recomputed,
        and set `qty_to_invoice` only if at least one of its combo item lines is invoiceable.
        """
        combo_lines = set()
        for line in self:
            if line.state == 'sale' and not line.display_type:
                if line.product_id.type == 'combo':
                    combo_lines.add(line)
                elif line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
                if line.combo_item_id and line.linked_line_id:
                    combo_lines.add(line.linked_line_id)
            else:
                line.qty_to_invoice = 0
        for combo_line in combo_lines:
            if any(
                line.combo_item_id and line.qty_to_invoice
                for line in combo_line.linked_line_ids
            ):
                combo_line.qty_to_invoice = combo_line.product_uom_qty - combo_line.qty_invoiced
            else:
                combo_line.qty_to_invoice = 0

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_compute_qty_to_invoice()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs only in state 'sale', the upselling opportunity is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        for line in self:
            if line.state != 'sale':
                line.invoice_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
                    line.product_uom_qty >= 0.0 and\
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    def _can_be_invoiced_alone(self):
        """ Whether a given line is meaningful to invoice alone.

        It is generally meaningless/confusing or even wrong to invoice some specific SOlines
        (delivery, discounts, rewards, ...) without others, unless they are the only left to invoice
        in the SO.
        """
        self.ensure_one()
        return self.product_id.id != self.company_id.sale_discount_product_id.id

    def _is_discount_line(self):
        self.ensure_one()
        return self.product_id in self.company_id.sale_discount_product_id

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state', 'invoice_lines.move_id.move_type')
    def _compute_untaxed_amount_invoiced(self):
        """ Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        for line in self:
            amount_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state == 'posted' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    invoice_date = invoice_line.move_id.invoice_date or fields.Date.today()
                    if invoice_line.move_id.move_type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
            line.untaxed_amount_invoiced = amount_invoiced

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state')
    def _compute_amount_invoiced(self):
        for line in self:
            amount_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                invoice = invoice_line.move_id
                if invoice.state == 'posted' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    invoice_date = invoice.invoice_date or fields.Date.context_today(self)
                    amount_invoiced_unsigned = invoice_line.currency_id._convert(invoice_line.price_total, line.currency_id, line.company_id, invoice_date)
                    amount_invoiced += amount_invoiced_unsigned * -invoice.direction_sign
            line.amount_invoiced = amount_invoiced

    @api.depends('state', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty', 'price_unit')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state == 'sale':
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                uom_qty_to_consider = line.qty_delivered if line.product_id.invoice_policy == 'delivery' else line.product_uom_qty
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                price_subtotal = price_reduce * uom_qty_to_consider
                if len(line.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
                    # As included taxes are not excluded from the computed subtotal, `compute_all()` method
                    # has to be called to retrieve the subtotal without them.
                    # `price_reduce_taxexcl` cannot be used as it is computed from `price_subtotal` field. (see upper Note)
                    price_subtotal = line.tax_ids.compute_all(
                        price_reduce,
                        currency=line.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id)['total_excluded']
                inv_lines = line._get_invoice_lines()
                if any(inv_lines.mapped(lambda l: l.discount != line.discount)):
                    # In case of re-invoicing with different discount we try to calculate manually the
                    # remaining amount to invoice
                    amount = 0
                    for l in inv_lines:
                        if len(l.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
                            amount += l.tax_ids.compute_all(l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity)['total_excluded']
                        else:
                            amount += l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity

                    amount_to_invoice = max(price_subtotal - amount, 0)
                else:
                    amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice = amount_to_invoice

    @api.depends('discount', 'price_total', 'product_uom_qty', 'qty_delivered', 'qty_invoiced_posted')
    def _compute_amount_to_invoice(self):
        for line in self:
            if line.product_uom_qty:
                uom_qty_to_consider = line.qty_delivered if line.product_id.invoice_policy == 'delivery' else line.product_uom_qty
                qty_to_invoice = uom_qty_to_consider - line.qty_invoiced_posted
                unit_price_total = line.price_total / line.product_uom_qty
                line.amount_to_invoice = unit_price_total * qty_to_invoice
            else:
                line.amount_to_invoice = 0.0

    @api.depends('price_unit', 'qty_invoiced_at_date', 'qty_delivered_at_date')
    @api.depends_context('accrual_entry_date')
    def _compute_amount_to_invoice_at_date(self):
        for line in self:
            line.amount_to_invoice_at_date = (line.qty_delivered_at_date - line.qty_invoiced_at_date) * line.price_unit

    @api.depends('order_id.partner_id', 'product_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = line.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution

    @api.depends('product_id', 'state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        self.product_updatable = True
        for line in self:
            if (
                line.is_downpayment
                or line.state == 'cancel'
                or line.state == 'sale' and (
                    line.order_id.locked
                    or line.qty_invoiced > 0
                    or line.qty_delivered > 0
                )
            ):
                line.product_updatable = False

    @api.depends('state')
    def _compute_product_uom_readonly(self):
        for line in self:
            # line.ids checks whether it's a new record not yet saved
            line.product_uom_readonly = line.ids and line.state in ['sale', 'cancel']

    def _compute_parent_id(self):
        sale_order_lines = set(self)
        for order, lines in self.grouped('order_id').items():
            if not order:
                lines.parent_id = False
                continue
            last_section = False
            last_sub = False
            for line in order.order_line.sorted('sequence'):
                if line.display_type == 'line_section':
                    last_section = line
                    if line in sale_order_lines:
                        line.parent_id = False
                    last_sub = False
                elif line.display_type == 'line_subsection':
                    if line in sale_order_lines:
                        line.parent_id = last_section
                    last_sub = line
                elif line in sale_order_lines:
                    line.parent_id = last_sub or last_section

    #=== CONSTRAINT METHODS ===#

    @api.constrains('combo_item_id')
    def _check_combo_item_id(self):
        """ `combo_item_id` should never be set manually. This constraint mainly serves to avoid
        programming errors.
        """
        for line in self:
            linked_line = line._get_linked_line()
            allowed_combo_items = linked_line.product_template_id.combo_ids.combo_item_ids
            if line.combo_item_id and line.combo_item_id not in allowed_combo_items:
                raise ValidationError(_(
                    "A sale order line's combo item must be among its linked line's available"
                    " combo items."
                ))
            if line.combo_item_id and line.combo_item_id.product_id != line.product_id:
                raise ValidationError(_(
                    "A sale order line's product must match its combo item's product."
                ))

    # === ONCHANGE METHODS ===#

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self._reset_price_unit()

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('display_type') or self.default_get(['display_type']).get('display_type'):
                vals['product_uom_qty'] = 0.0

            if 'technical_price_unit' in vals and 'price_unit' not in vals:
                # price_unit field was set as readonly in the view (but technical_price_unit not)
                # the field is not sent by the client and expected to be recomputed, but isn't
                # because technical_price_unit is set.
                vals.pop('technical_price_unit')

        lines = super().create(vals_list)
        for line in lines:
            linked_line = line._get_linked_line()
            if linked_line:
                line.linked_line_id = linked_line
        if self.env.context.get('sale_no_log_for_new_lines'):
            return lines

        for line in lines:
            if line.product_id and line.state == 'sale':
                msg = _("Extra line with %s", line.product_id.display_name)
                line.order_id.message_post(body=msg)

        return lines

    def _add_precomputed_values(self, vals_list):
        super()._add_precomputed_values(vals_list)
        for vals in vals_list:
            if 'price_unit' in vals and 'technical_price_unit' not in vals:
                vals['technical_price_unit'] = vals['price_unit']

    def write(self, vals):
        values = vals
        if 'display_type' in values:
            new_type = values.get('display_type')
            invalid_lines = self.filtered(
                lambda line:
                    line.display_type != new_type
                    and not (line.display_type == 'line_subsection' and new_type == 'line_section')
            )
            if invalid_lines:
                raise UserError(_(
                    "You cannot change the type of a sale order line. Instead you should "
                    "delete the current line and create a new line of the proper type."
                ))

        if 'product_id' in values and any(
            sol.product_id.id != values['product_id']
            and not sol.product_updatable
            for sol in self
        ):
            raise UserError(_("You cannot modify the product of this order line."))

        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) != 0)._update_line_quantity(values)

        if (
            'technical_price_unit' in values
            and 'price_unit' not in values
            and not self.env.context.get('sale_write_from_compute')
        ):
            # price_unit field was set as readonly in the view (but technical_price_unit not)
            # the field is not sent by the client and expected to be recomputed, but isn't
            # because technical_price_unit is set.
            values.pop('technical_price_unit')

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if any(self.order_id.mapped('locked')) and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))

            if 'name' in protected_fields_modified and all(self.mapped('is_downpayment')):
                protected_fields_modified.remove('name')

            fields = self.env['ir.model.fields'].sudo().search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            if fields:
                raise UserError(
                    _('It is forbidden to modify the following fields in a locked order:\n%s',
                      '\n'.join(fields.mapped('field_description')))
                )

        return super().write(values)

    def _get_protected_fields(self):
        """ Give the fields that should not be modified on a locked SO.

        :returns: list of field names
        :rtype: list
        """
        return [
            'product_id', 'name', 'price_unit', 'product_uom_id', 'product_uom_qty',
            'tax_ids', 'analytic_distribution', 'discount'
        ]

    def _update_line_quantity(self, values):
        orders = self.mapped('order_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.order_id == order)
            msg = Markup("<b>%s</b><ul>") % _("The ordered quantity has been updated.")
            for line in order_lines:
                if 'product_id' in values and values['product_id'] != line.product_id.id:
                    # tracking is meaningless if the product is changed as well.
                    continue
                msg += Markup("<li> %s: <br/>") % line.product_id.display_name
                msg += _(
                    "Ordered Quantity: %(old_qty)s -> %(new_qty)s",
                    old_qty=line.product_uom_qty,
                    new_qty=values["product_uom_qty"]
                ) + Markup("<br/>")
                if line.product_id.type == 'consu':
                    msg += _("Delivered Quantity: %s", line.qty_delivered) + Markup("<br/>")
                msg += _("Invoiced Quantity: %s", line.qty_invoiced) + Markup("<br/>")
            msg += Markup("</ul>")
            order.message_post(body=msg)

    def _check_line_unlink(self):
        """ Check whether given lines can be deleted or not.

        * Lines cannot be deleted if the order is confirmed.
        * Down payment lines who have not yet been invoiced bypass that exception.
        * Sections and Notes can always be deleted.

        :returns: Sales Order Lines that cannot be deleted
        :rtype: `sale.order.line` recordset
        """
        return self.filtered(
            lambda line:
                line.state == 'sale'
                and (line.invoice_lines or not line.is_downpayment)
                and not line.display_type
        )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_confirmed(self):
        if self._check_line_unlink():
            raise UserError(_("Once a sales order is confirmed, you can't remove one of its lines (we need to track if something gets invoiced or delivered).\n\
                Set the quantity to 0 instead."))

    #=== ACTION METHODS ===#

    @api.readonly
    def action_add_from_catalog(self):
        order = self.env['sale.order'].browse(self.env.context.get('order_id'))
        return order.with_context(child_field='order_line').action_add_from_catalog()

    #=== BUSINESS METHODS ===#

    def _expected_date(self):
        self.ensure_one()
        if self.state == 'sale' and self.order_id.date_order:
            order_date = self.order_id.date_order
        else:
            order_date = fields.Datetime.now()
        return order_date + timedelta(days=self.customer_lead or 0.0)

    def compute_uom_qty(self, new_qty, stock_move, rounding=True):
        return self.product_uom_id._compute_quantity(new_qty, stock_move.product_uom, rounding)

    def _get_invoice_line_sequence(self, new=0, old=0):
        """
        Method intended to be overridden in third-party module if we want to prevent the resequencing
        of invoice lines.

        :param int new:   the new line sequence
        :param int old:   the old line sequence

        :return:          the sequence of the SO line, by default the new one.
        """
        return new or old

    def _prepare_invoice_lines_vals_list(self, **optional_values):
        return [self._prepare_invoice_line(**optional_values)]

    def _prepare_invoice_line(self, **optional_values):
        """Prepare the values to create the new invoice line for a sales order line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        self.ensure_one()

        if self.product_id.type == 'combo':
            # If the quantity to invoice is a whole number, format it as an integer (with no decimal point)
            qty_to_invoice = int(self.qty_to_invoice) if self.qty_to_invoice == int(self.qty_to_invoice) else self.qty_to_invoice
            return {
                'display_type': 'line_section',
                'sequence': self.sequence,
                'name': f'{self.product_id.name} x {qty_to_invoice}',
                'product_uom_id': self.product_uom_id.id,
                'quantity': self.qty_to_invoice,
                'sale_line_ids': [Command.link(self.id)],
                'collapse_prices': self.collapse_prices,
                'collapse_composition': self.collapse_composition,
                **optional_values,
            }
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.env['account.move.line']._get_journal_items_full_name(self.name, self.product_id.display_name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_ids.ids)],
            'sale_line_ids': [Command.link(self.id)],
            'is_downpayment': self.is_downpayment,
            'extra_tax_data': self.extra_tax_data,
            'collapse_prices': self.collapse_prices,
            'collapse_composition': self.collapse_composition,
        }
        downpayment_lines = self.invoice_lines.filtered('is_downpayment')
        if self.is_downpayment and downpayment_lines:
            res['account_id'] = downpayment_lines.account_id[:1].id
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    def _set_analytic_distribution(self, inv_line_vals, **optional_values):
        if self.analytic_distribution and not self.display_type:
            inv_line_vals['analytic_distribution'] = self.analytic_distribution

    def _prepare_procurement_values(self):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        coming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        return {}

    def _validate_analytic_distribution(self):
        for line in self.filtered(lambda l: not l.display_type and l.state in ['draft', 'sent']):
            line._validate_distribution(**{
                'product': line.product_id.id,
                'business_domain': 'sale_order',
                'company_id': line.company_id.id,
            })

    def _get_downpayment_line_price_unit(self, invoices):
        return sum(
            l.price_unit if l.move_id.move_type == 'out_invoice' else -l.price_unit
            for l in self.invoice_lines
            if l.move_id.state == 'posted' and l.move_id not in invoices  # don't recompute with the final invoice
        )

    def _get_grouped_section_summary(self, display_taxes=True):
        """Return a tax-wise summary of sales order lines linked to section.

        Group lines by their tax IDs and computes subtotal and total for each group.
        """
        self.ensure_one()

        billable_lines = self.order_id.order_line.filtered(
            lambda line:
                line.product_type != 'combo'
                and self._is_line_in_section(line)
        )

        if display_taxes:
            res = [
                {
                    'tax_labels': [tax.tax_label for tax in taxes if tax.tax_label],
                    'price_subtotal': sum(lines.mapped('price_subtotal')),
                    'price_total': sum(lines.mapped('price_total')),
                }
                for taxes, lines in billable_lines.grouped('tax_ids').items()
            ]
        else:
            res = [{
                'tax_labels': [],
                'price_subtotal': sum(billable_lines.mapped('price_subtotal')),
                'price_total': sum(billable_lines.mapped('price_total')),
            }]
        return res or [{
            'tax_labels': [],
            'price_subtotal': 0.0,
            'price_total': 0.0,
        }]

    def get_parent_section_line(self):
        if not self.display_type and self.parent_id.display_type == 'line_subsection':
            return self.parent_id.parent_id

        return self.parent_id

    def _get_section_totals(self, totals_field):
        """Return the total/subtotal amount sale order lines linked to section."""
        self.ensure_one()
        section_lines = self._get_section_lines()
        return sum(section_lines.mapped(totals_field))

    def _get_combo_totals(self, totals_field):
        """Return the total/subtotal amount sale order lines linked to combo."""
        self.ensure_one()
        combo_item_lines = self.order_id.order_line.filtered(
            lambda line: line.linked_line_id == self and line.combo_item_id,
        )
        return sum(combo_item_lines.mapped(totals_field))

    def _has_taxes(self):
        """Check if a line has taxes or not. For (sub)sections, check if any child line has taxes."""
        self.ensure_one()
        return bool(
            self.tax_ids
            or (self.display_type and any(line._has_taxes() for line in self._get_section_lines())),
        )

    def _get_section_lines(self):
        self.ensure_one()
        return self.order_id.order_line.filtered(self._is_line_in_section)

    def _is_line_in_section(self, line):
        """Return whether the line is a direct or indirect child of the section."""
        self.ensure_one()
        is_direct_child = line.parent_id == self and not line.display_type
        is_indirect_child = (
            self.display_type == 'line_section'
            and line.parent_id
            and line.parent_id.display_type == 'line_subsection'
            and line.parent_id.parent_id == self
        )
        return is_direct_child or is_indirect_child

    #=== CORE METHODS OVERRIDES ===#

    def _get_partner_display(self):
        self.ensure_one()
        commercial_partner = self.sudo().order_partner_id.commercial_partner_id
        return f'({commercial_partner.ref or commercial_partner.name})'

    def _additional_name_per_id(self):
        return {
            so_line.id: so_line._get_partner_display()
            for so_line in self
        }

    #=== HOOKS ===#

    def _is_delivery(self):
        self.ensure_one()
        return False

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Return information about sale order lines in `self`.

        If `self` is empty, this method returns only the default value(s) needed for the product
        catalog. In this case, the quantity that equals 0.

        Otherwise, it returns a quantity and a price based on the product of the SOL(s) and whether
        the product is read-only or not.

        A product is considered read-only if the order is considered read-only (see
        ``SaleOrder._is_readonly`` for more details) or if `self` contains multiple records.

        Note: This method cannot be called with multiple records that have different products linked.

        :raise odoo.exceptions.ValueError: ``len(self.product_id) != 1``
        :rtype: dict
        :return: A dict with the following structure:
            {
                'quantity': float,
                'price': float,
                'readOnly': bool,
                'uomDisplayName': String,
            }
        """
        if len(self) == 1:
            return {
                'quantity': self.product_uom_qty,
                'price': self._get_discounted_price(),
                'readOnly': (
                    self.order_id._is_readonly()
                    or bool(self.combo_item_id)
                ),
                'uomDisplayName': self.product_uom_id.display_name,
            }
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            order = order_line.order_id
            return {
                'readOnly': True,
                'price': order.pricelist_id._get_product_price(
                    product=order_line.product_id,
                    quantity=1.0,
                    currency=order.currency_id,
                    date=order.date_order,
                    **kwargs,
                ),
                'quantity': sum(
                    self.mapped(
                        lambda line: line.product_uom_id._compute_quantity(
                            qty=line.product_uom_qty,
                            to_unit=line.product_id.uom_id,
                        )
                    )
                ),
                'uomDisplayName': self.product_id.uom_id.display_name,
            }
        else:
            return {
                'quantity': 0,
                # price will be computed in batch with pricelist utils so not given here
            }

    #=== TOOLING ===#

    def _convert_to_sol_currency(self, amount, currency):
        """Convert the given amount from the given currency to the SO(L) currency.

        :param float amount: the amount to convert
        :param currency: currency in which the given amount is expressed
        :type currency: `res.currency` record
        :returns: converted amount
        :rtype: float
        """
        self.ensure_one()
        to_currency = self.currency_id or self.order_id.currency_id
        if currency and to_currency and currency != to_currency:
            conversion_date = self.order_id.date_order or fields.Date.context_today(self)
            company = self.company_id or self.order_id.company_id or self.env.company
            return currency._convert(
                from_amount=amount,
                to_currency=to_currency,
                company=company,
                date=conversion_date,
                round=False,
            )
        return amount

    @api.model
    def _date_in_the_past(self):
        if not 'accrual_entry_date' in self.env.context:
            return False
        accrual_date = fields.Date.from_string(self.env.context['accrual_entry_date'])
        return accrual_date < fields.Date.today()

    def _get_discounted_price(self):
        self.ensure_one()
        return self.price_unit * (1 - (self.discount or 0.0) / 100.0)

    def has_valued_move_ids(self):
        return None  # TODO: remove in master

    def _get_linked_line(self):
        """ Return the linked line of this line, if any.

        This method relies on either `linked_line_id` or `linked_virtual_id` to retrieve the linked
        line, depending on whether the linked line is saved in the DB.
        """
        self.ensure_one()
        return self.linked_line_id or (
            self.linked_virtual_id and self.order_id.order_line.filtered(
                lambda line: line.virtual_id == self.linked_virtual_id
            ).ensure_one()
        ) or self.env['sale.order.line']

    def _get_linked_lines(self):
        """ Return the linked lines of this line, if any.

        This method relies on either `linked_line_id` or `linked_virtual_id` to retrieve the linked
        lines, depending on whether this line is saved in the DB.

        Note: we can't rely on `linked_line_ids` as it will only be populated when both this line
        and its linked lines are saved in the DB, which we can't ensure.
        """
        self.ensure_one()
        return (
            self._origin and self.order_id.order_line.filtered(
                lambda line: line.linked_line_id._origin == self._origin
            )
        ) or (
            self.virtual_id and self.order_id.order_line.filtered(
                lambda line: line.linked_virtual_id == self.virtual_id
            )
        ) or self.env['sale.order.line']

    def _sellable_lines_domain(self):
        discount_products_ids = self.env.companies.sale_discount_product_id.ids
        domain = Domain('is_downpayment', '=', False)
        if discount_products_ids:
            domain &= Domain('product_id', 'not in', discount_products_ids)
        return domain

    def _get_lines_with_price(self):
        """ A combo product line always has a zero price (by design). The actual price of the combo
        product can be computed by summing the prices of its combo items (i.e. its linked lines).
        """
        if self.product_type == 'combo':
            # Only consider combo item lines (not optional product lines)
            return self.linked_line_ids.filtered('combo_item_id')
        return self

    # For `sale_management`, to control optional products on portal
    def _can_be_edited_on_portal(self):
        self.ensure_one()
        return self.order_id._can_be_edited_on_portal() and not self.combo_item_id


# FILEPATH: odoo/addons/sale/models/utm_campaign.py
class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'
    _description = 'UTM Campaign'

    quotation_count = fields.Integer('Quotation Count',
        compute="_compute_quotation_count", compute_sudo=True, groups='sales_team.group_sale_salesman')
    invoiced_amount = fields.Integer(string="Revenues generated by the campaign",
        compute="_compute_sale_invoiced_amount", compute_sudo=True, groups='sales_team.group_sale_salesman')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')

    def _compute_quotation_count(self):
        quotation_data = self.env['sale.order']._read_group([
            ('campaign_id', 'in', self.ids)],
            ['campaign_id'], ['__count'])
        data_map = {campaign.id: count for campaign, count in quotation_data}
        for campaign in self:
            campaign.quotation_count = data_map.get(campaign.id, 0)

    def _compute_sale_invoiced_amount(self):
        if self.ids:
            self.env['account.move.line'].flush_model(['balance', 'move_id', 'account_id', 'display_type'])
            self.env['account.move'].flush_model(['state', 'campaign_id', 'move_type'])
            query_res = self.env.execute_query_dict(SQL(
                """ SELECT move.campaign_id, -SUM(line.balance) as price_subtotal
                    FROM account_move_line line
                    INNER JOIN account_move move ON line.move_id = move.id
                    WHERE move.state not in ('draft', 'cancel')
                        AND move.campaign_id IN %s
                        AND move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                        AND line.account_id IS NOT NULL
                        AND line.display_type = 'product'
                    GROUP BY move.campaign_id """,
                tuple(self.ids),
            ))
        else:
            query_res = []

        campaigns = self.browse()
        for datum in query_res:
            campaign = self.browse(datum['campaign_id'])
            campaign.invoiced_amount = datum['price_subtotal']
            campaigns |= campaign
        for campaign in (self - campaigns):
            campaign.invoiced_amount = 0

    def action_redirect_to_quotations(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('campaign_id', '=', self.id)]
        action['context'] = {'default_campaign_id': self.id}
        return action

    def action_redirect_to_invoiced(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        invoices = self.env['account.move'].search([('campaign_id', '=', self.id)])
        action['context'] = {
            'create': False,
            'edit': False,
            'view_no_maturity': True
        }
        action['domain'] = [
            ('id', 'in', invoices.ids),
            ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')),
            ('state', 'not in', ['draft', 'cancel'])
        ]
        return action


# FILEPATH: odoo/addons/sales_team/__manifest__.py
{   'data': [   'security/sales_team_security.xml',
                'security/ir.model.access.csv',
                'data/crm_team_data.xml',
                'views/crm_tag_views.xml',
                'views/crm_team_views.xml',
                'views/crm_team_member_views.xml',
                'views/mail_activity_views.xml'],
    'depends': ['base', 'mail'],
    'name': 'Sales Teams',
    'summary': 'Sales Teams'}

# FILEPATH: odoo/addons/sales_team/models/crm_tag.py
class CrmTag(models.Model):
    _name = 'crm.tag'


# FILEPATH: odoo/addons/sales_team/models/crm_team.py
class CrmTeam(models.Model):
    _name = 'crm.team'
    _inherit = ['mail.thread']
    _description = "Sales Team"
    _order = "sequence ASC, create_date DESC, id DESC"
    _check_company_auto = True
    user_id = fields.Many2one('res.users')
    member_ids = fields.Many2many('res.users', compute='_compute_member_ids')
    crm_team_member_ids = fields.One2many('crm.team.member', 'crm_team_id')
    crm_team_member_all_ids = fields.One2many('crm.team.member', 'crm_team_id')
    favorite_user_ids = fields.Many2many('res.users', 'team_favorite_user_rel', 'team_id', 'user_id')
    # Shrunk non computed fields: name, sequence, active, company_id, currency_id, user_id, crm_team_member_ids, crm_team_member_all_ids, color, favorite_user_ids
    # Shrunk computed_fields: is_membership_multi (_compute_is_membership_multi), member_ids (_compute_member_ids), member_company_ids (_compute_member_company_ids), member_warning (_compute_member_warning), is_favorite (_compute_is_favorite), dashboard_button_name (_compute_dashboard_button_name)


# FILEPATH: odoo/addons/sales_team/models/crm_team_member.py
class CrmTeamMember(models.Model):
    _name = 'crm.team.member'
    _inherit = ['mail.thread']
    _description = 'Sales Team Member'
    _rec_name = 'user_id'
    _order = 'create_date ASC, id'
    _check_company_auto = True
    crm_team_id = fields.Many2one('crm.team')
    user_id = fields.Many2one('res.users')
    user_in_teams_ids = fields.Many2many('res.users', compute='_compute_user_in_teams_ids')
    # Shrunk non computed fields: crm_team_id, user_id, active, image_1920, image_128, name, email, phone, company_id
    # Shrunk computed_fields: user_in_teams_ids (_compute_user_in_teams_ids), user_company_ids (_compute_user_company_ids), is_membership_multi (_compute_is_membership_multi), member_warning (_compute_member_warning)


# FILEPATH: odoo/addons/sales_team/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'
    crm_team_ids = fields.Many2many('crm.team', 'crm_team_member', 'user_id', 'crm_team_id', compute='_compute_crm_team_ids')
    crm_team_member_ids = fields.One2many('crm.team.member', 'user_id')
    sale_team_id = fields.Many2one('crm.team', compute='_compute_sale_team_id', store=True)
    # Shrunk non computed fields: crm_team_member_ids
    # Shrunk computed_fields: crm_team_ids (_compute_crm_team_ids), sale_team_id (_compute_sale_team_id)
