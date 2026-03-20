# Odoo Schema: `crm_raw`

> Сгенерировано из `/tmp/akaidoo_raw/crm_raw.md` скриптом `extract_schema.py`.  
> Модели: 32, полей всего: 157.

## `CalendarEvent` ← calendar.event
Файл: `odoo/addons/crm/models/calendar.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `opportunity_id` | Many2one | crm.lead |  |

## `CrmTeamMember` ← crm.team.member
Файл: `odoo/addons/crm/models/crm_team_member.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `assignment_enabled` | Boolean | — |  |
| `assignment_domain` | Char | — |  |
| `assignment_domain_preferred` | Char | — |  |
| `assignment_optout` | Boolean | — |  |
| `assignment_max` | Integer | — |  |
| `lead_day_count` | Integer | — |  |
| `lead_month_count` | Integer | — |  |

## `DigestDigest` ← digest.digest
Файл: `odoo/addons/crm/models/digest.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `kpi_crm_lead_created` | Boolean | — |  |
| `kpi_crm_lead_created_value` | Integer | — |  |
| `kpi_crm_opportunities_won` | Boolean | — |  |
| `kpi_crm_opportunities_won_value` | Integer | — |  |

## `DiscussChannel` ← discuss.channel
Файл: `odoo/addons/calendar/models/discuss_channel.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `calendar_event_ids` | One2many | calendar.event |  |

## `MailActivity` ← mail.activity
Файл: `odoo/addons/calendar/models/mail_activity.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `calendar_event_id` | Many2one | calendar.event |  |

## `ResConfigSettings` ← res.config.settings
Файл: `odoo/addons/crm/models/res_config_settings.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `group_use_lead` | Boolean | — | Leads |
| `group_use_recurring_revenues` | Boolean | — | Recurring Revenues |
| `is_membership_multi` | Boolean | — | Multi Teams |
| `module_partnership` | Boolean | — |  |
| `crm_use_auto_assignment` | Boolean | — | Rule-Based Assignment |
| `crm_auto_assignment_action` | Selection | manual,auto | Auto Assignment Action |
| `crm_auto_assignment_interval_type` | Selection | minutes,hours,days,weeks | Auto Assignment Interval Unit |
| `crm_auto_assignment_interval_number` | Integer | — | Repeat every |
| `crm_auto_assignment_run_datetime` | Datetime | — | Auto Assignment Next Execution Date |
| `module_crm_iap_mine` | Boolean | — |  |
| `module_crm_iap_enrich` | Boolean | — |  |
| `module_website_crm_iap_reveal` | Boolean | — |  |
| `lead_enrich_auto` | Selection | manual,auto | Enrich lead automatically |
| `lead_mining_in_pipeline` | Boolean | — |  |
| `predictive_lead_scoring_start_date` | Date | — | Lead Scoring Starting Date |
| `predictive_lead_scoring_start_date_str` | Char | — | Lead Scoring Starting Date in String |
| `predictive_lead_scoring_fields` | Many2many | crm.lead.scoring.frequency.field | Lead Scoring Frequency Fields |
| `predictive_lead_scoring_fields_str` | Char | — | Lead Scoring Frequency Fields in String |
| `predictive_lead_scoring_field_labels` | Char | — |  |

## `ResPartner` ← res.partner
Файл: `odoo/addons/crm/models/res_partner.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `opportunity_ids` | One2many | crm.lead | Opportunities |
| `opportunity_count` | Integer | — | Opportunity Count |

## `ResUsers` ← res.users
Файл: `odoo/addons/sales_team/models/res_users.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `crm_team_ids` | Many2many | crm.team |  |
| `crm_team_member_ids` | One2many | crm.team.member |  |
| `sale_team_id` | Many2one | crm.team |  |

## `UtmCampaign` ← utm.campaign
Файл: `odoo/addons/crm/models/utm.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `use_leads` | Boolean | — |  |
| `crm_lead_count` | Integer | — |  |

## `calendar.alarm`
*Event Alarm*  
Файл: `odoo/addons/calendar/models/calendar_alarm.py`  

*Полей нет (абстрактная модель или наследование)*  

## `calendar.alarm_manager`
Файл: `odoo/addons/calendar/models/calendar_alarm_manager.py`  

*Полей нет (абстрактная модель или наследование)*  

## `calendar.attendee`
*Calendar Attendee Information*  
Файл: `odoo/addons/calendar/models/calendar_attendee.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `event_id` | Many2one | calendar.event |  |
| `recurrence_id` | Many2one | calendar.recurrence |  |

## `calendar.event` ← mail.thread
*Calendar Event*  
Файл: `odoo/addons/calendar/models/calendar_event.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `user_id` | Many2one | res.users |  |
| `videocall_channel_id` | Many2one | discuss.channel |  |
| `categ_ids` | Many2many | calendar.event.type |  |
| `res_model_id` | Many2one | ir.model |  |
| `activity_ids` | One2many | mail.activity |  |
| `attendee_ids` | One2many | calendar.attendee |  |
| `current_attendee` | Many2one | calendar.attendee |  |
| `alarm_ids` | Many2many | calendar.alarm |  |
| `recurrence_id` | Many2one | calendar.recurrence |  |

## `calendar.event.type`
*Event Meeting Type*  
Файл: `odoo/addons/calendar/models/calendar_event_type.py`  

*Полей нет (абстрактная модель или наследование)*  

## `calendar.filters`
Файл: `odoo/addons/calendar/models/calendar_filter.py`  

*Полей нет (абстрактная модель или наследование)*  

## `calendar.recurrence`
*Event Recurrence Rule*  
Файл: `odoo/addons/calendar/models/calendar_recurrence.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `base_event_id` | Many2one | calendar.event |  |
| `calendar_event_ids` | One2many | calendar.event |  |

## `crm.lead` ← mail.thread.cc, mail.thread.blacklist, mail.thread.phone, mail.activity.mixin, utm.mixin, format.address.mixin, mail.tracking.duration.mixin
*Lead*  
Файл: `odoo/addons/crm/models/crm_lead.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `user_id` | Many2one | res.users | Salesperson |
| `user_company_ids` | Many2many | res.company |  |
| `team_id` | Many2one | crm.team | Sales Team |
| `company_id` | Many2one | res.company | Company |
| `referred` | Char | — |  |
| `description` | Html | — |  |
| `active` | Boolean | — |  |
| `type` | Selection | lead,opportunity |  |
| `priority` | Selection | — | Priority |
| `stage_id` | Many2one | crm.stage | Stage |
| `stage_id_color` | Integer | — | Stage Color |
| `tag_ids` | Many2many | crm.tag | Tags |
| `color` | Integer | — |  |
| `expected_revenue` | Monetary | — |  |
| `prorated_revenue` | Monetary | — |  |
| `recurring_revenue` | Monetary | — |  |
| `recurring_plan` | Many2one | crm.recurring.plan | Recurring Plan |
| `recurring_revenue_monthly` | Monetary | — |  |
| `recurring_revenue_monthly_prorated` | Monetary | — |  |
| `recurring_revenue_prorated` | Monetary | — |  |
| `company_currency` | Many2one | res.currency | Currency |
| `date_closed` | Datetime | — |  |
| `date_automation_last` | Datetime | — |  |
| `date_open` | Datetime | — |  |
| `day_open` | Float | — |  |
| `day_close` | Float | — |  |
| `date_last_stage_update` | Datetime | — |  |
| `date_conversion` | Datetime | — |  |
| `date_deadline` | Date | — |  |
| `commercial_partner_id` | Many2one | res.partner | Customer Company |
| `partner_id` | Many2one | res.partner | Contact |
| `partner_is_blacklisted` | Boolean | — |  |
| `contact_name` | Char | — |  |
| `partner_name` | Char | — |  |
| `function` | Char | — |  |
| `email_from` | Char | — |  |
| `email_normalized` | Char | — |  |
| `email_domain_criterion` | Char | — | Email Domain Criterion |
| `phone` | Char | — |  |
| `phone_sanitized` | Char | — |  |
| `phone_state` | Selection | correct,incorrect | Phone Quality |
| `email_state` | Selection | correct,incorrect | Email Quality |
| `website` | Char | — |  |
| `lang_id` | Many2one | res.lang | Language |
| `lang_code` | Char | — |  |
| `lang_active_count` | Integer | — |  |
| `street` | Char | — |  |
| `street2` | Char | — |  |
| `zip` | Char | — |  |
| `city` | Char | — |  |
| `state_id` | Many2one | res.country.state | State |
| `country_id` | Many2one | res.country | Country |
| `probability` | Float | — |  |
| `automated_probability` | Float | — |  |
| `is_automated_probability` | Boolean | — |  |
| `won_status` | Selection | won,lost,pending | Won/Lost |
| `lost_reason_id` | Many2one | crm.lost.reason | Lost Reason |
| `calendar_event_ids` | One2many | calendar.event | Meetings |
| `duplicate_lead_ids` | Many2many | crm.lead | Potential Duplicate Lead |
| `duplicate_lead_count` | Integer | — | Potential Duplicate Lead Count |
| `meeting_display_date` | Date | — |  |
| `meeting_display_label` | Char | — |  |
| `partner_email_update` | Boolean | — |  |
| `partner_phone_update` | Boolean | — |  |
| `is_partner_visible` | Boolean | — |  |
| `campaign_id` | Many2one | ? |  |
| `medium_id` | Many2one | ? |  |
| `source_id` | Many2one | ? |  |

## `crm.lost.reason`
*Opp. Lost Reason*  
Файл: `odoo/addons/crm/models/crm_lost_reason.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `active` | Boolean | — |  |
| `leads_count` | Integer | — |  |

## `crm.recurring.plan`
*CRM Recurring revenue plans*  
Файл: `odoo/addons/crm/models/crm_recurring_plan.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `number_of_months` | Integer | — |  |
| `active` | Boolean | — |  |
| `sequence` | Integer | — |  |

## `crm.stage`
*CRM Stages*  
Файл: `odoo/addons/crm/models/crm_stage.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `sequence` | Integer | — |  |
| `is_won` | Boolean | — |  |
| `rotting_threshold_days` | Integer | — |  |
| `requirements` | Text | — |  |
| `team_ids` | Many2many | crm.team | Sales Teams |
| `fold` | Boolean | — |  |
| `team_count` | Integer | — |  |
| `color` | Integer | — | Color |

## `crm.tag`
*CRM Tag*  
Файл: `odoo/addons/sales_team/models/crm_tag.py`  

*Полей нет (абстрактная модель или наследование)*  

## `crm.team` ← mail.alias.mixin, crm.team
*Sales Team*  
Файл: `odoo/addons/crm/models/crm_team.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `use_leads` | Boolean | — |  |
| `use_opportunities` | Boolean | — |  |
| `alias_id` | Many2one | ? |  |
| `assignment_enabled` | Boolean | — |  |
| `assignment_auto_enabled` | Boolean | — |  |
| `assignment_optout` | Boolean | — |  |
| `assignment_max` | Integer | — |  |
| `assignment_domain` | Char | — |  |
| `lead_unassigned_count` | Integer | — | # Unassigned Leads |
| `lead_all_assigned_month_count` | Integer | — | # Leads/Opps assigned this month |
| `lead_all_assigned_month_exceeded` | Boolean | — |  |
| `user_id` | Many2one | res.users |  |
| `member_ids` | Many2many | res.users |  |
| `crm_team_member_ids` | One2many | crm.team.member |  |
| `crm_team_member_all_ids` | One2many | crm.team.member |  |
| `favorite_user_ids` | Many2many | res.users |  |

## `crm.team.member` ← mail.thread
*Sales Team Member*  
Файл: `odoo/addons/sales_team/models/crm_team_member.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `crm_team_id` | Many2one | crm.team |  |
| `user_id` | Many2one | res.users |  |
| `user_in_teams_ids` | Many2many | res.users |  |

## `html.field.history.mixin`
Файл: `odoo/addons/html_editor/models/html_field_history_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `mail.thread.phone` ← mail.thread
*Phone Blacklist Mixin*  
Файл: `odoo/addons/phone_validation/models/mail_thread_phone.py`  

*Полей нет (абстрактная модель или наследование)*  

## `phone.blacklist` ← mail.thread
Файл: `odoo/addons/phone_validation/models/phone_blacklist.py`  

*Полей нет (абстрактная модель или наследование)*  

## `res.partner` ← mail.thread.phone, res.partner
Файл: `odoo/addons/phone_validation/models/res_partner.py`  

*Полей нет (абстрактная модель или наследование)*  

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
