# Odoo Schema: `account_raw`

> Сгенерировано из `/tmp/akaidoo_raw/account_raw.md` скриптом `extract_schema.py`.  
> Модели: 41, полей всего: 511.

## `AccountAnalyticAccount` ← account.analytic.account
Файл: `odoo/addons/account/models/account_analytic_account.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `invoice_count` | Integer | — |  |
| `vendor_bill_count` | Integer | — |  |

## `AccountAnalyticApplicability` ← account.analytic.applicability
*Analytic Plan*  
Файл: `odoo/addons/account/models/account_analytic_plan.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `business_domain` | Selection | invoice,bill |  |
| `account_prefix` | Char | — | Financial Accounts Prefixes |
| `product_categ_id` | Many2one | product.category | Product Category |
| `display_account_prefix` | Boolean | — |  |
| `account_prefix_placeholder` | Char | — |  |

## `AccountAnalyticDistributionModel` ← account.analytic.distribution.model
Файл: `odoo/addons/account/models/account_analytic_distribution_model.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `account_prefix` | Char | — | Accounts Prefix |
| `product_id` | Many2one | product.product | Product |
| `product_categ_id` | Many2one | product.category | Product Category |
| `prefix_placeholder` | Char | — |  |

## `AccountAnalyticLine` ← account.analytic.line
*Analytic Line*  
Файл: `odoo/addons/account/models/account_analytic_line.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `product_id` | Many2one | product.product | Product |
| `general_account_id` | Many2one | account.account | Financial Account |
| `journal_id` | Many2one | account.journal | Financial Journal |
| `partner_id` | Many2one | ? |  |
| `move_line_id` | Many2one | account.move.line | Journal Item |
| `code` | Char | — |  |
| `ref` | Char | — | Ref. |
| `category` | Selection | invoice,vendor_bill |  |

## `DigestDigest` ← digest.digest
Файл: `odoo/addons/account/models/digest.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `kpi_account_total_revenue` | Boolean | — |  |
| `kpi_account_total_revenue_value` | Monetary | — |  |

## `IrActionsReport` ← ir.actions.report
Файл: `odoo/addons/account/models/ir_actions_report.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `is_invoice_report` | Boolean | — | Invoice report |

## `IrModuleModule` ← ir.module.module
Файл: `odoo/addons/account/models/ir_module.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `account_templates` | Binary | — |  |

## `ResCurrency` ← res.currency
Файл: `odoo/addons/account/models/res_currency.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `display_rounding_warning` | Boolean | — | Display Rounding Warning |
| `fiscal_country_codes` | Char | — |  |

## `UomUom` ← uom.uom
Файл: `odoo/addons/account/models/uom_uom.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `fiscal_country_codes` | Char | — |  |

## `account.account.tag`
*Account Tag*  
Файл: `odoo/addons/account/models/account_account_tag.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `applicability` | Selection | accounts,taxes,products |  |
| `color` | Integer | — |  |
| `active` | Boolean | — |  |
| `country_id` | Many2one | res.country | Country |
| `report_expression_id` | Many2one | account.report.expression |  |
| `balance_negate` | Boolean | — |  |

## `account.analytic.account` ← mail.thread
*Analytic Account*  
Файл: `odoo/addons/analytic/models/analytic_account.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `plan_id` | Many2one | account.analytic.plan |  |
| `root_plan_id` | Many2one | account.analytic.plan |  |
| `line_ids` | One2many | account.analytic.line |  |

## `account.analytic.distribution.model` ← analytic.mixin
*Analytic Distribution Model*  
Файл: `odoo/addons/analytic/models/analytic_distribution_model.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `partner_category_id` | Many2one | res.partner.category |  |

## `account.bank.statement`
*Bank Statement*  
Файл: `odoo/addons/account/models/account_bank_statement.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — | Reference |
| `reference` | Char | — | External Reference |
| `date` | Date | — |  |
| `first_line_index` | Char | — |  |
| `balance_start` | Monetary | — | Starting Balance |
| `balance_end` | Monetary | — | Computed Balance |
| `balance_end_real` | Monetary | — | Ending Balance |
| `company_id` | Many2one | res.company |  |
| `currency_id` | Many2one | res.currency |  |
| `journal_id` | Many2one | account.journal |  |
| `line_ids` | One2many | account.bank.statement.line | Statement lines |
| `is_complete` | Boolean | — |  |
| `is_valid` | Boolean | — |  |
| `journal_has_invalid_statements` | Boolean | — |  |
| `problem_description` | Text | — |  |
| `attachment_ids` | Many2many | ir.attachment | Attachments |
| `kanban_dashboard` | Text | — |  |
| `kanban_dashboard_graph` | Text | — |  |
| `json_activity_data` | Text | — |  |
| `show_on_dashboard` | Boolean | — | Show journal on dashboard |
| `color` | Integer | — |  |
| `current_statement_balance` | Monetary | — |  |
| `has_statement_lines` | Boolean | — |  |
| `entries_count` | Integer | — |  |
| `has_posted_entries` | Boolean | — |  |
| `has_entries` | Boolean | — |  |
| `has_sequence_holes` | Boolean | — |  |
| `has_unhashed_entries` | Boolean | — | Unhashed Entries |
| `last_statement_id` | Many2one | account.bank.statement |  |

## `account.cash.rounding`
*Account Cash Rounding*  
Файл: `odoo/addons/account/models/account_cash_rounding.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — | Name |
| `rounding` | Float | — | Rounding Precision |
| `strategy` | Selection | biggest_tax,add_invoice_line | Rounding Strategy |
| `profit_account_id` | Many2one | account.account | Profit Account |
| `loss_account_id` | Many2one | account.account | Loss Account |
| `rounding_method` | Selection | UP,DOWN,HALF-UP | Rounding Method |

## `account.chart.template`
*Account Chart Template*  
Файл: `odoo/addons/account/models/chart_template.py`  

*Полей нет (абстрактная модель или наследование)*  

## `account.code.mapping`
*Mapping of account codes per company*  
Файл: `odoo/addons/account/models/account_code_mapping.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `account_id` | Many2one | account.account | Account |
| `company_id` | Many2one | res.company | Company |
| `code` | Char | — | Code |

## `account.document.import.mixin`
*Business document import mixin*  
Файл: `odoo/addons/account/models/account_document_import_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `account.full.reconcile`
*Full Reconcile*  
Файл: `odoo/addons/account/models/account_full_reconcile.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `partial_reconcile_ids` | One2many | account.partial.reconcile | Reconciliation Parts |
| `reconciled_line_ids` | One2many | account.move.line | Matched Journal Items |

## `account.incoterms`
*Incoterms*  
Файл: `odoo/addons/account/models/account_incoterms.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `code` | Char | — |  |
| `active` | Boolean | — |  |

## `account.journal` ← res.config.settings
Файл: `odoo/addons/account/models/res_config_settings.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `has_accounting_entries` | Boolean | — |  |
| `currency_id` | Many2one | res.currency | Currency |
| `currency_exchange_journal_id` | Many2one | account.journal | Currency Exchange Journal |
| `income_currency_exchange_account_id` | Many2one | account.account | Gain Exchange Rate Account |
| `expense_currency_exchange_account_id` | Many2one | account.account | Loss Exchange Rate Account |
| `has_chart_of_accounts` | Boolean | — | Company has a chart of accounts |
| `chart_template` | Selection | — |  |
| `sale_tax_id` | Many2one | account.tax | Default Sale Tax |
| `purchase_tax_id` | Many2one | account.tax | Default Purchase Tax |
| `account_price_include` | Selection | Default Sales Price Include,Default on whether the sales price used on the product and invoices with this Company includes its taxes. | Default Sales Price Include |
| `tax_calculation_rounding_method` | Selection | company_id.tax_calculation_rounding_method | Tax calculation rounding method |
| `account_journal_suspense_account_id` | Many2one | account.account | Bank Suspense |
| `transfer_account_id` | Many2one | account.account | Internal Transfer |
| `module_account_accountant` | Boolean | — | Accounting |
| `group_cash_rounding` | Boolean | — | Cash Rounding |
| `show_sale_receipts` | Boolean | — | Sale Receipt |
| `module_account_budget` | Boolean | — | Budget Management |
| `module_account_payment` | Boolean | — | Invoice Online Payment |
| `module_account_reports` | Boolean | — |  |
| `module_account_check_printing` | Boolean | — |  |
| `module_account_batch_payment` | Boolean | — | Use batch payments |
| `module_account_iso20022` | Boolean | — | SEPA Credit Transfer / ISO20022 |
| `module_account_sepa_direct_debit` | Boolean | — | Use SEPA Direct Debit |
| `module_account_bank_statement_import_qif` | Boolean | — |  |
| `module_currency_rate_live` | Boolean | — | Automatic Currency Rates |
| `module_account_intrastat` | Boolean | — | Intrastat |
| `module_product_margin` | Boolean | — | Allow Product Margin |
| `module_account_extract` | Boolean | — | Document Digitization |
| `module_account_invoice_extract` | Boolean | — |  |
| `module_account_bank_statement_extract` | Boolean | — |  |
| `module_snailmail_account` | Boolean | — | Snailmail |
| `module_account_peppol` | Boolean | — | PEPPOL Invoicing |
| `tax_exigibility` | Boolean | — | Cash Basis |
| `tax_cash_basis_journal_id` | Many2one | account.journal | Tax Cash Basis Journal |
| `account_cash_basis_base_account_id` | Many2one | account.account | Base Tax Received Account |
| `account_fiscal_country_id` | Many2one | ? | Fiscal Country Code |
| `qr_code` | Boolean | — | Display SEPA QR-code |
| `link_qr_code` | Boolean | — | Display Link QR-code |
| `incoterm_id` | Many2one | account.incoterms | Default incoterm |
| `invoice_terms` | Html | — | Terms & Conditions |
| `invoice_terms_html` | Html | — | Terms & Conditions as a Web page |
| `terms_type` | Selection | company_id.terms_type |  |
| `display_invoice_amount_total_words` | Boolean | — | Total amount of invoice in letters |
| `display_invoice_tax_company_currency` | Boolean | — | Taxes in company currency |
| `preview_ready` | Boolean | — | Display preview button |
| `use_invoice_terms` | Boolean | — | Default Terms & Conditions |
| `account_use_credit_limit` | Boolean | — | Sales Credit Limit |
| `account_default_credit_limit` | Monetary | — | Default Credit Limit |
| `country_code` | Char | — |  |
| `account_storno` | Boolean | — | Storno accounting |
| `display_account_storno` | Boolean | — |  |
| `group_sale_delivery_address` | Boolean | — |  |
| `quick_edit_mode` | Selection | Quick encoding | Quick encoding |
| `account_journal_early_pay_discount_loss_account_id` | Many2one | account.account | Early Discount Loss |
| `account_journal_early_pay_discount_gain_account_id` | Many2one | account.account | Early Discount Gain |
| `account_discount_income_allocation_id` | Many2one | account.account | Vendor Bills Discounts Account |
| `account_discount_expense_allocation_id` | Many2one | account.account | Customer Invoices Discounts Account |
| `is_account_peppol_eligible` | Boolean | — | PEPPOL eligible |
| `restrictive_audit_trail` | Boolean | — | Restricted Audit Trail |
| `force_restrictive_audit_trail` | Boolean | — | Forced Audit Trail |
| `autopost_bills` | Boolean | — |  |
| `income_account_id` | Many2one | ? |  |
| `expense_account_id` | Many2one | ? |  |

## `account.lock_exception`
*Account Lock Exception*  
Файл: `odoo/addons/account/models/account_lock_exception.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `active` | Boolean | — | Active |
| `state` | Selection | active,revoked,expired | State |
| `company_id` | Many2one | res.company | Company |
| `user_id` | Many2one | res.users | User |
| `reason` | Char | — | Reason |
| `end_datetime` | Datetime | — | End Date |
| `lock_date_field` | Selection | fiscalyear_lock_date,tax_lock_date,sale_lock_date,purchase_lock_date | Lock Date Field |
| `lock_date` | Date | — | Changed Lock Date |
| `company_lock_date` | Date | — | Original Lock Date |
| `fiscalyear_lock_date` | Date | — | Global Lock Date |
| `tax_lock_date` | Date | — | Tax Return Lock Date |
| `sale_lock_date` | Date | — | Sales Lock Date |
| `purchase_lock_date` | Date | — | Purchase Lock Date |

## `account.move` ← portal.mixin, mail.thread.main.attachment, mail.activity.mixin, sequence.mixin, product.catalog.mixin, account.document.import.mixin
*Journal Entry*  
Файл: `odoo/addons/account/models/account_move.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — | Number |
| `name_placeholder` | Char | — |  |
| `ref` | Char | — | Reference |
| `date` | Date | — | Date |
| `state` | Selection | draft,posted,cancel | Status |
| `move_type` | Selection | entry,out_invoice,out_refund,in_invoice,in_refund,out_receipt,in_receipt | Type |
| `is_storno` | Boolean | — |  |
| `journal_id` | Many2one | account.journal | Journal |
| `journal_group_id` | Many2one | account.journal.group | Ledger |
| `company_id` | Many2one | res.company | Company |
| `line_ids` | One2many | account.move.line | Journal Items |
| `journal_line_ids` | One2many | account.move.line | Journal Items (DEPRECATED) |
| `exchange_diff_partial_ids` | One2many | account.partial.reconcile | Related reconciliation |
| `origin_payment_id` | Many2one | account.payment | Payment |
| `matched_payment_ids` | Many2many | account.payment | Matched Payments |
| `reconciled_payment_ids` | Many2many | account.payment | Reconciled Payments |
| `payment_count` | Integer | — |  |
| `statement_line_id` | Many2one | account.bank.statement.line | Statement Line |
| `statement_id` | Many2one | ? |  |
| `adjusting_entry_origin_move_ids` | Many2many | account.move | Adjusting Entry Origin Moves |
| `adjusting_entry_origin_label` | Char | — |  |
| `adjusting_entry_origin_moves_count` | Integer | — | Adjusting Entry Origin Moves Count |
| `adjusting_entries_move_ids` | Many2many | account.move | Created Adjusting Entries |
| `adjusting_entries_count` | Integer | — | Adjusting Entries Count |
| `tax_cash_basis_rec_id` | Many2one | account.partial.reconcile | Tax Cash Basis Entry of |
| `tax_cash_basis_origin_move_id` | Many2one | account.move | Cash Basis Origin |
| `tax_cash_basis_created_move_ids` | One2many | account.move | Cash Basis Entries |
| `always_tax_exigible` | Boolean | — |  |
| `auto_post` | Selection | no,at_date,monthly,quarterly,yearly | Auto-post |
| `auto_post_until` | Date | — | Auto-post until |
| `auto_post_origin_id` | Many2one | account.move | First recurring entry |
| `hide_post_button` | Boolean | — |  |
| `checked` | Boolean | — | Reviewed |
| `posted_before` | Boolean | — |  |
| `suitable_journal_ids` | Many2many | account.journal |  |
| `highest_name` | Char | — |  |
| `made_sequence_gap` | Boolean | — |  |
| `show_name_warning` | Boolean | — |  |
| `type_name` | Char | — |  |
| `country_code` | Char | — |  |
| `account_fiscal_country_group_codes` | Json | — |  |
| `company_price_include` | Selection | company_id.account_price_include |  |
| `attachment_ids` | One2many | ir.attachment | Attachments |
| `audit_trail_message_ids` | One2many | mail.message | Audit Trail Messages |
| `no_followup` | Boolean | — | No Follow-Up |
| `restrict_mode_hash_table` | Boolean | — |  |
| `secure_sequence_number` | Integer | — | Inalterability No Gap Sequence # |
| `inalterable_hash` | Char | — | Inalterability Hash |
| `secured` | Boolean | — |  |
| `invoice_line_ids` | One2many | ? | Invoice lines |
| `invoice_date` | Date | — | Invoice/Bill Date |
| `invoice_date_due` | Date | — | Due Date |
| `delivery_date` | Date | — | Delivery Date |
| `show_delivery_date` | Boolean | — |  |
| `taxable_supply_date` | Date | — | Taxable Supply Date |
| `show_taxable_supply_date` | Boolean | — |  |
| `taxable_supply_date_placeholder` | Char | — |  |
| `invoice_payment_term_id` | Many2one | account.payment.term | Payment Terms |
| `needed_terms` | Binary | — |  |
| `needed_terms_dirty` | Boolean | — |  |
| `tax_calculation_rounding_method` | Selection | company_id.tax_calculation_rounding_method | Tax calculation rounding method |
| `show_journal` | Boolean | — |  |
| `partner_id` | Many2one | res.partner | Partner |
| `commercial_partner_id` | Many2one | res.partner | Commercial Entity |
| `partner_shipping_id` | Many2one | res.partner | Delivery Address |
| `partner_bank_id` | Many2one | res.partner.bank | Recipient Bank |
| `fiscal_position_id` | Many2one | account.fiscal.position | Fiscal Position |
| `payment_reference` | Char | — | Payment Reference |
| `display_qr_code` | Boolean | — | Display QR-code |
| `display_link_qr_code` | Boolean | — | Display Link QR-code |
| `qr_code_method` | Selection | res.partner.bank | Payment QR-code |
| `invoice_outstanding_credits_debits_widget` | Binary | — |  |
| `invoice_has_outstanding` | Boolean | — |  |
| `invoice_payments_widget` | Binary | — |  |
| `preferred_payment_method_line_id` | Many2one | account.payment.method.line | Preferred Payment Method Line |
| `company_currency_id` | Many2one | ? | Company Currency |
| `currency_id` | Many2one | res.currency | Currency |
| `expected_currency_rate` | Float | — |  |
| `invoice_currency_rate` | Float | — | Currency Rate |
| `direction_sign` | Integer | — |  |
| `amount_untaxed` | Monetary | — | Untaxed Amount |
| `amount_tax` | Monetary | — | Tax |
| `amount_total` | Monetary | — | Total |
| `amount_residual` | Monetary | — | Amount Due |
| `amount_untaxed_signed` | Monetary | — | Untaxed Amount Signed |
| `amount_untaxed_in_currency_signed` | Monetary | — | Untaxed Amount Signed Currency |
| `amount_tax_signed` | Monetary | — | Tax Signed |
| `amount_total_signed` | Monetary | — | Total Signed |
| `amount_total_in_currency_signed` | Monetary | — | Total in Currency Signed |
| `amount_residual_signed` | Monetary | — | Amount Due Signed |
| `tax_totals` | Binary | — | Invoice Totals |
| `payment_state` | Selection | Payment Status | Payment Status |
| `status_in_payment` | Selection | draft,posted,sent,cancel |  |
| `amount_total_words` | Char | — | Amount total in words |
| `reversed_entry_id` | Many2one | account.move | Reversal of |
| `reversal_move_ids` | One2many | account.move |  |
| `invoice_vendor_bill_id` | Many2one | account.move | Vendor Bill |
| `invoice_source_email` | Char | — | Source Email |
| `invoice_partner_display_name` | Char | — |  |
| `is_manually_modified` | Boolean | — |  |
| `quick_edit_mode` | Boolean | — |  |
| `quick_edit_total_amount` | Monetary | — | Total (Tax inc.) |
| `quick_encoding_vals` | Json | — |  |
| `narration` | Html | — | Terms and Conditions |
| `is_move_sent` | Boolean | — |  |
| `is_being_sent` | Boolean | — |  |
| `move_sent_values` | Selection | sent,not_sent | Sent |
| `invoice_user_id` | Many2one | res.users | Salesperson |
| `user_id` | Many2one | ? | User |
| `invoice_origin` | Char | — | Origin |
| `invoice_incoterm_id` | Many2one | account.incoterms | Incoterm |
| `incoterm_location` | Char | — | Incoterm Location |
| `invoice_cash_rounding_id` | Many2one | account.cash.rounding | Cash Rounding Method |
| `sending_data` | Json | — |  |
| `invoice_pdf_report_id` | Many2one | ir.attachment | PDF Attachment |
| `invoice_pdf_report_file` | Binary | — | PDF File |
| `invoice_incoterm_placeholder` | Char | — |  |
| `invoice_filter_type_domain` | Char | — |  |
| `bank_partner_id` | Many2one | res.partner |  |
| `tax_lock_date_message` | Char | — |  |
| `display_inactive_currency_warning` | Boolean | — |  |
| `tax_country_id` | Many2one | res.country |  |
| `tax_country_code` | Char | — |  |
| `has_reconciled_entries` | Boolean | — |  |
| `show_reset_to_draft_button` | Boolean | — |  |
| `partner_credit_warning` | Text | — |  |
| `duplicated_ref_ids` | Many2many | account.move |  |
| `is_draft_duplicated_ref_ids` | Boolean | — |  |
| `need_cancel_request` | Boolean | — |  |
| `show_update_fpos` | Boolean | — | Has Fiscal Position Changed |
| `payment_term_details` | Binary | — |  |
| `show_payment_term_details` | Boolean | — |  |
| `show_discount_details` | Boolean | — |  |
| `abnormal_amount_warning` | Text | — |  |
| `abnormal_date_warning` | Text | — |  |
| `alerts` | Json | — |  |
| `taxes_legal_notes` | Html | — | Taxes Legal Notes |
| `next_payment_date` | Date | — | Next Payment Date |
| `display_send_button` | Boolean | — |  |
| `highlight_send_button` | Boolean | — |  |
| `is_sale_installed` | Boolean | — |  |
| `account_audit_log_preview` | Text | — | Description |
| `account_audit_log_move_id` | Many2one | account.move | Journal Entry |
| `account_audit_log_partner_id` | Many2one | res.partner | Partner |
| `account_audit_log_account_id` | Many2one | account.account | Account |
| `account_audit_log_tax_id` | Many2one | account.tax | Tax |
| `account_audit_log_company_id` | Many2one | res.company | Company  |
| `account_audit_log_restricted` | Boolean | — | Protected by restricted Audit Logs |

## `account.move.line` ← analytic.mixin
*Journal Item*  
Файл: `odoo/addons/account/models/account_move_line.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `move_id` | Many2one | account.move | Journal Entry |
| `journal_id` | Many2one | ? |  |
| `journal_group_id` | Many2one | account.journal.group | Ledger |
| `company_id` | Many2one | ? |  |
| `company_currency_id` | Many2one | ? | Company Currency |
| `move_name` | Char | — | Number |
| `parent_state` | Selection | move_id.state |  |
| `date` | Date | — |  |
| `invoice_date` | Date | — |  |
| `ref` | Char | — |  |
| `is_storno` | Boolean | — | Company Storno Accounting |
| `sequence` | Integer | — |  |
| `move_type` | Selection | move_id.move_type |  |
| `account_id` | Many2one | account.account | Account |
| `account_name` | Char | — |  |
| `account_code` | Char | — |  |
| `search_account_id` | Many2one | account.account |  |
| `name` | Char | — | Label |
| `translated_product_name` | Text | — |  |
| `debit` | Monetary | — | Debit |
| `credit` | Monetary | — | Credit |
| `balance` | Monetary | — | Balance |
| `cumulated_balance` | Monetary | — | Cumulated Balance |
| `currency_rate` | Float | — |  |
| `amount_currency` | Monetary | — | Amount in Currency |
| `currency_id` | Many2one | res.currency | Currency |
| `is_same_currency` | Boolean | — |  |
| `partner_id` | Many2one | res.partner | Partner |
| `is_imported` | Boolean | — |  |
| `reconcile_model_id` | Many2one | account.reconcile.model | Reconciliation Model |
| `payment_id` | Many2one | account.payment | Originator Payment |
| `statement_line_id` | Many2one | account.bank.statement.line | Originator Statement Line |
| `statement_id` | Many2one | ? |  |
| `commercial_partner_country` | Many2one | ? | Commercial Partner Country |
| `tax_ids` | Many2many | account.tax | Taxes |
| `group_tax_id` | Many2one | account.tax | Originator Group of Taxes |
| `tax_line_id` | Many2one | account.tax | Originator Tax |
| `tax_group_id` | Many2one | ? | Originator tax group |
| `tax_base_amount` | Monetary | — | Base Amount |
| `tax_repartition_line_id` | Many2one | account.tax.repartition.line | Originator Tax Distribution Line |
| `tax_tag_ids` | Many2many | account.account.tag | Tags |
| `extra_tax_data` | Json | — |  |
| `amount_residual` | Monetary | — | Residual Amount |
| `amount_residual_currency` | Monetary | — | Residual Amount in Currency |
| `reconciled` | Boolean | — |  |
| `full_reconcile_id` | Many2one | account.full.reconcile | Matching |
| `matched_debit_ids` | One2many | account.partial.reconcile | Matched Debits |
| `matched_credit_ids` | One2many | account.partial.reconcile | Matched Credits |
| `reconciled_lines_ids` | Many2many | account.move.line |  |
| `reconciled_lines_excluding_exchange_diff_ids` | Many2many | account.move.line |  |
| `matching_number` | Char | — | Matching # |
| `is_account_reconcile` | Boolean | — | Account Reconcile |
| `account_type` | Selection | account_id.account_type | Internal Type |
| `account_internal_group` | Selection | account_id.internal_group |  |
| `account_root_id` | Many2one | ? | Account Root |
| `product_category_id` | Many2one | ? |  |
| `display_type` | Selection | product,cogs,tax,discount,rounding,payment_term,line_section,… |  |
| `collapse_composition` | Boolean | — | Hide Composition |
| `collapse_prices` | Boolean | — | Hide Prices |
| `parent_id` | Many2one | account.move.line | Parent Section Line |
| `product_id` | Many2one | product.product | Product |
| `allowed_uom_ids` | Many2many | uom.uom |  |
| `product_uom_id` | Many2one | uom.uom | Unit |
| `quantity` | Float | — | Quantity |
| `date_maturity` | Date | — | Due Date |
| `price_unit` | Float | — | Unit Price |
| `price_subtotal` | Monetary | — | Subtotal |
| `price_total` | Monetary | — | Total |
| `discount` | Float | — | Discount (%) |
| `tax_calculation_rounding_method` | Selection | company_id.tax_calculation_rounding_method | Tax calculation rounding method |
| `deductible_amount` | Float | — |  |
| `term_key` | Binary | — |  |
| `epd_key` | Binary | — |  |
| `epd_needed` | Binary | — |  |
| `epd_dirty` | Boolean | — |  |
| `discount_allocation_key` | Binary | — |  |
| `discount_allocation_needed` | Binary | — |  |
| `discount_allocation_dirty` | Boolean | — |  |
| `analytic_line_ids` | One2many | account.analytic.line | Analytic lines |
| `analytic_distribution` | Json | — |  |
| `has_invalid_analytics` | Boolean | — |  |
| `discount_date` | Date | — | Discount Date |
| `discount_amount_currency` | Monetary | — | Discount amount in Currency |
| `discount_balance` | Monetary | — | Discount Balance |
| `payment_date` | Date | — | Next Payment Date |
| `is_refund` | Boolean | — |  |
| `no_followup` | Boolean | — | No Follow-Up |

## `account.move.send`
*Account Move Send*  
Файл: `odoo/addons/account/models/account_move_send.py`  

*Полей нет (абстрактная модель или наследование)*  

## `account.partial.reconcile`
*Partial Reconcile*  
Файл: `odoo/addons/account/models/account_partial_reconcile.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `debit_move_id` | Many2one | account.move.line |  |
| `credit_move_id` | Many2one | account.move.line |  |
| `full_reconcile_id` | Many2one | account.full.reconcile | Full Reconcile |
| `exchange_move_id` | Many2one | account.move |  |
| `draft_caba_move_vals` | Json | — | Values that created the draft cash-basis entry |
| `company_currency_id` | Many2one | res.currency | Company Currency |
| `debit_currency_id` | Many2one | res.currency | Currency of the debit journal item. |
| `credit_currency_id` | Many2one | res.currency | Currency of the credit journal item. |
| `amount` | Monetary | — |  |
| `debit_amount_currency` | Monetary | — |  |
| `credit_amount_currency` | Monetary | — |  |
| `company_id` | Many2one | res.company | Company |
| `max_date` | Date | — | Max Date of Matched Lines |

## `account.root`
*Account codes first 2 digits*  
Файл: `odoo/addons/account/models/account_root.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `parent_id` | Many2one | account.root |  |

## `analytic.mixin`
*Analytic Mixin*  
Файл: `odoo/addons/analytic/models/analytic_mixin.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `distribution_analytic_account_ids` | Many2many | account.analytic.account |  |

## `html.field.history.mixin`
Файл: `odoo/addons/html_editor/models/html_field_history_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.onboarding`
*Onboarding*  
Файл: `odoo/addons/onboarding/models/onboarding_onboarding.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `step_ids` | Many2many | onboarding.onboarding.step |  |
| `current_progress_id` | Many2one | onboarding.progress |  |
| `progress_ids` | One2many | onboarding.progress |  |

## `onboarding.onboarding.step`
*Onboarding Step*  
Файл: `odoo/addons/onboarding/models/onboarding_onboarding_step.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `onboarding_ids` | Many2many | onboarding.onboarding |  |
| `current_progress_step_id` | Many2one | onboarding.progress.step |  |
| `progress_ids` | One2many | onboarding.progress.step |  |

## `onboarding.progress`
*Onboarding Progress Tracker*  
Файл: `odoo/addons/onboarding/models/onboarding_progress.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `onboarding_id` | Many2one | onboarding.onboarding |  |
| `progress_step_ids` | Many2many | onboarding.progress.step |  |

## `onboarding.progress.step`
*Onboarding Progress Step Tracker*  
Файл: `odoo/addons/onboarding/models/onboarding_progress_step.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `progress_ids` | Many2many | onboarding.progress |  |
| `step_id` | Many2one | onboarding.onboarding.step |  |

## `res.company` ← res.company, mail.thread
Файл: `odoo/addons/account/models/company.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `fiscalyear_last_day` | Integer | — |  |
| `fiscalyear_last_month` | Selection | 12 |  |
| `fiscalyear_lock_date` | Date | — | Global Lock Date |
| `tax_lock_date` | Date | — | Tax Return Lock Date |
| `sale_lock_date` | Date | — | Sales Lock Date |
| `purchase_lock_date` | Date | — | Purchase Lock date |
| `hard_lock_date` | Date | — | Hard Lock Date |
| `user_fiscalyear_lock_date` | Date | — |  |
| `user_tax_lock_date` | Date | — |  |
| `user_sale_lock_date` | Date | — |  |
| `user_purchase_lock_date` | Date | — |  |
| `user_hard_lock_date` | Date | — |  |
| `transfer_account_id` | Many2one | account.account | Inter-Banks Transfer Account |
| `expects_chart_of_accounts` | Boolean | — | Expects a Chart of Accounts |
| `chart_template` | Selection | _chart_template_selection |  |
| `bank_account_code_prefix` | Char | — | Prefix of the bank accounts |
| `cash_account_code_prefix` | Char | — | Prefix of the cash accounts |
| `default_cash_difference_income_account_id` | Many2one | account.account | Cash Difference Income |
| `default_cash_difference_expense_account_id` | Many2one | account.account | Cash Difference Expense |
| `account_journal_suspense_account_id` | Many2one | account.account | Journal Suspense Account |
| `account_journal_early_pay_discount_gain_account_id` | Many2one | account.account | Cash Discount Write-Off Gain Account |
| `account_journal_early_pay_discount_loss_account_id` | Many2one | account.account | Cash Discount Write-Off Loss Account |
| `transfer_account_code_prefix` | Char | — | Prefix of the transfer accounts |
| `account_sale_tax_id` | Many2one | account.tax | Default Sale Tax |
| `account_purchase_tax_id` | Many2one | account.tax | Default Purchase Tax |
| `account_purchase_receipt_fiscal_position_id` | Many2one | account.fiscal.position | Default Purchase Receipt Fiscal Position |
| `tax_calculation_rounding_method` | Selection | round_globally,round_per_line | Tax Calculation Rounding Method |
| `currency_exchange_journal_id` | Many2one | account.journal | Exchange Gain or Loss Journal |
| `income_currency_exchange_account_id` | Many2one | account.account | Gain Exchange Rate Account |
| `expense_currency_exchange_account_id` | Many2one | account.account | Loss Exchange Rate Account |
| `anglo_saxon_accounting` | Boolean | — | Use anglo-saxon accounting |
| `bank_journal_ids` | One2many | account.journal | Bank Journals |
| `incoterm_id` | Many2one | account.incoterms | Default incoterm |
| `qr_code` | Boolean | — | Display QR-code on invoices |
| `link_qr_code` | Boolean | — | Display Link QR-code |
| `display_invoice_amount_total_words` | Boolean | — | Total amount of invoice in letters |
| `display_invoice_tax_company_currency` | Boolean | — | Taxes in company currency |
| `account_use_credit_limit` | Boolean | — | Sales Credit Limit |
| `batch_payment_sequence_id` | Many2one | ir.sequence |  |
| `account_opening_move_id` | Many2one | account.move | Opening Journal Entry |
| `account_opening_journal_id` | Many2one | account.journal | Opening Journal |
| `account_opening_date` | Date | — | Opening Entry |
| `invoice_terms` | Html | — | Default Terms and Conditions |
| `terms_type` | Selection | plain,html | Terms & Conditions format |
| `invoice_terms_html` | Html | — | Default Terms and Conditions as a Web page |
| `account_default_pos_receivable_account_id` | Many2one | account.account | Default PoS Receivable Account |
| `expense_accrual_account_id` | Many2one | account.account |  |
| `revenue_accrual_account_id` | Many2one | account.account |  |
| `automatic_entry_default_journal_id` | Many2one | account.journal |  |
| `domestic_fiscal_position_id` | Many2one | account.fiscal.position |  |
| `account_fiscal_country_id` | Many2one | res.country | Fiscal Country |
| `account_fiscal_country_group_codes` | Json | — |  |
| `account_enabled_tax_country_ids` | Many2many | res.country | l10n-used countries |
| `tax_exigibility` | Boolean | — | Use Cash Basis |
| `tax_cash_basis_journal_id` | Many2one | account.journal | Cash Basis Journal |
| `account_cash_basis_base_account_id` | Many2one | account.account | Base Tax Received Account |
| `account_storno` | Boolean | — | Storno accounting |
| `display_account_storno` | Boolean | — |  |
| `fiscal_position_ids` | One2many | account.fiscal.position |  |
| `multi_vat_foreign_country_ids` | Many2many | res.country | Foreign VAT countries |
| `quick_edit_mode` | Selection | out_invoices,in_invoices,out_and_in_invoices | Quick encoding |
| `account_discount_income_allocation_id` | Many2one | account.account | Separate account for income discount |
| `account_discount_expense_allocation_id` | Many2one | account.account | Separate account for expense discount |
| `restrictive_audit_trail` | Boolean | — | Restrictive Audit Trail |
| `force_restrictive_audit_trail` | Boolean | — | Force Audit Trail |
| `autopost_bills` | Boolean | — | Auto-validate bills |
| `account_price_include` | Selection | tax_included,tax_excluded | Default Sales Price Include |
| `company_vat_placeholder` | Char | — |  |
| `company_registry_placeholder` | Char | — |  |
| `income_account_id` | Many2one | account.account | Income Account |
| `expense_account_id` | Many2one | account.account | Expense Account |
| `price_difference_account_id` | Many2one | account.account | Price Difference Account |

## `res.country.state` ← res.country.group
Файл: `odoo/addons/account/models/res_country_group.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `exclude_state_ids` | Many2many | res.country.state | Fiscal Exceptions |

## `res.partner.bank` ← res.partner.bank, mail.thread, mail.activity.mixin
Файл: `odoo/addons/account/models/res_partner_bank.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `journal_id` | One2many | account.journal | Account Journal |
| `has_iban_warning` | Boolean | — |  |
| `partner_country_name` | Char | — |  |
| `has_money_transfer_warning` | Boolean | — |  |
| `money_transfer_service` | Char | — |  |
| `partner_supplier_rank` | Integer | — |  |
| `partner_customer_rank` | Integer | — |  |
| `related_moves` | One2many | account.move |  |
| `bank_id` | Many2one | ? |  |
| `active` | Boolean | — |  |
| `acc_number` | Char | — |  |
| `acc_holder_name` | Char | — |  |
| `clearing_number` | Char | — |  |
| `partner_id` | Many2one | ? |  |
| `user_has_group_validate_bank_account` | Boolean | — |  |
| `allow_out_payment` | Boolean | — |  |
| `currency_id` | Many2one | ? |  |
| `lock_trust_fields` | Boolean | — |  |
| `duplicate_bank_partner_ids` | Many2many | res.partner |  |

## `resource.calendar`
Файл: `odoo/addons/resource/models/resource_calendar.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.attendance`
Файл: `odoo/addons/resource/models/resource_calendar_attendance.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.leaves`
Файл: `odoo/addons/resource/models/resource_calendar_leaves.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.mixin`
Файл: `odoo/addons/resource/models/resource_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.resource`
Файл: `odoo/addons/resource/models/resource_resource.py`  

*Полей нет (абстрактная модель или наследование)*  

## `sequence.mixin`
*Automatic sequence*  
Файл: `odoo/addons/account/models/sequence_mixin.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `sequence_prefix` | Char | — |  |
| `sequence_number` | Integer | — |  |
