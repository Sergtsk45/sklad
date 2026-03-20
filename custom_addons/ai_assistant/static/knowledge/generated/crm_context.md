Role: Senior Odoo Architect enforcing OCA standards.
Context: The following is a codebase dump produced by the akaidoo CLI.
Command: /home/serg45/.local/bin/akaidoo addon crm -c akaidoo.conf --shrink=hard -B 30k -o custom_addons/ai_assistant/static/knowledge/generated/crm_context.md
Conventions:
1. Files start with `# FILEPATH: [path]`.
2. Some files were filtered out to save tokens; ask for them if you need.
3. `# shrunk` indicates code removed to save tokens; ask for full content if a specific logic flow is unclear.
4. Method definitions were eventually entirely skipped to save tokens and focus on the data model only.

# FILEPATH: odoo/addons/calendar/__manifest__.py
{   'data': [   'security/ir.model.access.csv',
                'security/calendar_security.xml',
                'data/calendar_cron.xml',
                'data/mail_template_data.xml',
                'data/calendar_data.xml',
                'data/mail_activity_type_data.xml',
                'data/mail_message_subtype_data.xml',
                'views/mail_activity_views.xml',
                'views/calendar_templates.xml',
                'views/calendar_views.xml',
                'views/res_config_settings_views.xml',
                'views/res_partner_views.xml',
                'views/res_users_views.xml',
                'wizard/calendar_provider_config.xml',
                'wizard/calendar_popover_delete_wizard.xml',
                'wizard/mail_activity_schedule_views.xml'],
    'depends': ['base', 'mail'],
    'name': 'Calendar',
    'summary': "Schedule employees' meetings"}

# FILEPATH: odoo/addons/calendar/models/calendar_alarm.py
class CalendarAlarm(models.Model):
    _name = 'calendar.alarm'
    _description = 'Event Alarm'
    _interval_selection = {'minutes': 'Minutes', 'hours': 'Hours', 'days': 'Days'}
    # Shrunk non computed fields: name, alarm_type, duration, interval, body, notify_responsible
    # Shrunk computed_fields: duration_minutes (_compute_duration_minutes), mail_template_id (_compute_mail_template_id)


# FILEPATH: odoo/addons/calendar/models/calendar_alarm_manager.py
class CalendarAlarm_Manager(models.AbstractModel):
    _name = 'calendar.alarm_manager'


# FILEPATH: odoo/addons/calendar/models/calendar_attendee.py
_logger = logging.getLogger(__name__)
class CalendarAttendee(models.Model):
    _name = 'calendar.attendee'
    _rec_name = 'common_name'
    _description = 'Calendar Attendee Information'
    _order = 'create_date ASC'
    STATE_SELECTION = [
        ('accepted', 'Yes'),
        ('declined', 'No'),
        ('tentative', 'Maybe'),
        ('needsAction', 'Needs Action'),
    ]
    event_id = fields.Many2one('calendar.event', 'Meeting linked')
    recurrence_id = fields.Many2one('calendar.recurrence', related='event_id.recurrence_id')
    # Shrunk non computed fields: event_id, recurrence_id, partner_id, email, phone, access_token, state, availability
    # Shrunk computed_fields: common_name (_compute_common_name), mail_tz (_compute_mail_tz)


# FILEPATH: odoo/addons/calendar/models/calendar_event.py
_logger = logging.getLogger(__name__)
SORT_ALIASES = {
    'start': 'sort_start',
    'start_date': 'sort_start',
}
RRULE_TYPE_SELECTION_UI = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
    ('custom', 'Custom')
]
class CalendarEvent(models.Model):
    _name = 'calendar.event'
    _description = "Calendar Event"
    _order = "start desc"
    _inherit = ["mail.thread"]
    _systray_view = 'calendar'
    DISCUSS_ROUTE = 'calendar/join_videocall'
    user_id = fields.Many2one('res.users', 'Organizer')
    videocall_channel_id = fields.Many2one('discuss.channel', 'Discuss Channel')
    categ_ids = fields.Many2many('calendar.event.type', 'meeting_category_rel', 'event_id', 'type_id', 'Tags')
    res_model_id = fields.Many2one('ir.model', 'Document Model')
    activity_ids = fields.One2many('mail.activity', 'calendar_event_id')
    attendee_ids = fields.One2many('calendar.attendee', 'event_id', 'Participant')
    current_attendee = fields.Many2one("calendar.attendee", compute="_compute_current_attendee")
    alarm_ids = fields.Many2many('calendar.alarm', 'calendar_alarm_calendar_event_rel')
    recurrence_id = fields.Many2one('calendar.recurrence')
    # Shrunk non computed fields: name, description, user_id, partner_id, location, notes, access_token, videocall_channel_id, privacy, show_as, active, categ_ids, start, allday, res_id, res_model_id, res_model, res_model_name, activity_ids, attendee_ids, current_status, partner_ids, alarm_ids, recurrency, recurrence_id, follow_recurrence, recurrence_update
    # Shrunk computed_fields: videocall_location (_compute_videocall_location), videocall_source (_compute_videocall_source), effective_privacy (_compute_effective_privacy), is_highlighted (_compute_is_highlighted), is_organizer_alone (_compute_is_organizer_alone), stop (_compute_stop), display_time (_compute_display_time), start_date (_compute_dates), stop_date (_compute_dates), duration (_compute_duration), current_attendee (_compute_current_attendee), should_show_status (_compute_should_show_status), invalid_email_partner_ids (_compute_invalid_email_partner_ids), unavailable_partner_ids (_compute_unavailable_partner_ids), rrule (_compute_recurrence), rrule_type_ui (_compute_rrule_type_ui), rrule_type (_compute_recurrence), event_tz (_compute_recurrence), end_type (_compute_recurrence), interval (_compute_recurrence), count (_compute_recurrence), mon (_compute_recurrence), tue (_compute_recurrence), wed (_compute_recurrence), thu (_compute_recurrence), fri (_compute_recurrence), sat (_compute_recurrence), sun (_compute_recurrence), month_by (_compute_recurrence), day (_compute_recurrence), weekday (_compute_recurrence), byday (_compute_recurrence), until (_compute_recurrence), display_description (_compute_display_description), attendees_count (_compute_attendees_count), accepted_count (_compute_attendees_count), declined_count (_compute_attendees_count), tentative_count (_compute_attendees_count), awaiting_count (_compute_attendees_count), user_can_edit (_compute_user_can_edit)


# FILEPATH: odoo/addons/calendar/models/calendar_event_type.py
class CalendarEventType(models.Model):
    _name = 'calendar.event.type'
    _description = 'Event Meeting Type'
    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!')
    # Shrunk non computed fields: name, color


# FILEPATH: odoo/addons/calendar/models/calendar_filter.py
class CalendarFilters(models.Model):
    _name = 'calendar.filters'


# FILEPATH: odoo/addons/calendar/models/calendar_recurrence.py
MAX_RECURRENT_EVENT = 720
SELECT_FREQ_TO_RRULE = {
    'daily': rrule.DAILY,
    'weekly': rrule.WEEKLY,
    'monthly': rrule.MONTHLY,
    'yearly': rrule.YEARLY,
}
RRULE_FREQ_TO_SELECT = {
    rrule.DAILY: 'daily',
    rrule.WEEKLY: 'weekly',
    rrule.MONTHLY: 'monthly',
    rrule.YEARLY: 'yearly',
}
RRULE_WEEKDAY_TO_FIELD = {
    rrule.MO.weekday: 'mon',
    rrule.TU.weekday: 'tue',
    rrule.WE.weekday: 'wed',
    rrule.TH.weekday: 'thu',
    rrule.FR.weekday: 'fri',
    rrule.SA.weekday: 'sat',
    rrule.SU.weekday: 'sun',
}
RRULE_WEEKDAYS = {'SUN': 'SU', 'MON': 'MO', 'TUE': 'TU', 'WED': 'WE', 'THU': 'TH', 'FRI': 'FR', 'SAT': 'SA'}
RRULE_TYPE_SELECTION = [
    ('daily', 'Days'),
    ('weekly', 'Weeks'),
    ('monthly', 'Months'),
    ('yearly', 'Years'),
]
END_TYPE_SELECTION = [
    ('count', 'Number of repetitions'),
    ('end_date', 'End date'),
    ('forever', 'Forever'),
]
MONTH_BY_SELECTION = [
    ('date', 'Date of month'),
    ('day', 'Day of month'),
]
WEEKDAY_SELECTION = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
]
BYDAY_SELECTION = [
    ('1', 'First'),
    ('2', 'Second'),
    ('3', 'Third'),
    ('4', 'Fourth'),
    ('-1', 'Last'),
]
class CalendarRecurrence(models.Model):
    _name = 'calendar.recurrence'
    _description = 'Event Recurrence Rule'
    base_event_id = fields.Many2one('calendar.event')
    calendar_event_ids = fields.One2many('calendar.event', 'recurrence_id')
    _month_day = models.Constraint("""CHECK (
        rrule_type != 'monthly'
        OR month_by != 'day'
        OR day >= 1 AND day <= 31
        OR weekday IN %s AND byday IN %s)""" % (
            tuple(wd[0] for wd in WEEKDAY_SELECTION),
            tuple(bd[0] for bd in BYDAY_SELECTION)),
        "The day must be between 1 and 31")
    # Shrunk non computed fields: base_event_id, calendar_event_ids, event_tz, rrule_type, end_type, interval, count, mon, tue, wed, thu, fri, sat, sun, month_by, day, weekday, byday, until, trigger_id
    # Shrunk computed_fields: name (_compute_name), rrule (_compute_rrule), dtstart (_compute_dtstart)


# FILEPATH: odoo/addons/calendar/models/discuss_channel.py
class DiscussChannel(models.Model):
    _inherit = "discuss.channel"
    calendar_event_ids = fields.One2many("calendar.event", "videocall_channel_id")
    # Shrunk non computed fields: calendar_event_ids


# FILEPATH: odoo/addons/calendar/models/ir_http.py
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'


# FILEPATH: odoo/addons/calendar/models/mail_activity.py
class MailActivity(models.Model):
    _inherit = "mail.activity"
    calendar_event_id = fields.Many2one('calendar.event')
    # Shrunk non computed fields: calendar_event_id


# FILEPATH: odoo/addons/calendar/models/mail_activity_mixin.py
class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'


# FILEPATH: odoo/addons/calendar/models/mail_activity_type.py
class MailActivityType(models.Model):
    _inherit = "mail.activity.type"


# FILEPATH: odoo/addons/calendar/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'


# FILEPATH: odoo/addons/calendar/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'
    # Shrunk computed_fields: calendar_default_privacy (_compute_calendar_default_privacy)


# FILEPATH: odoo/addons/calendar/models/res_users_settings.py
class ResUsersSettings(models.Model):
    _inherit = "res.users.settings"


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


# FILEPATH: odoo/addons/crm/__manifest__.py


{
    'name': 'CRM',
    'version': '1.9',
    'category': 'Sales/CRM',
    'sequence': 15,
    'summary': 'Track leads and close opportunities',
    'website': 'https://www.odoo.com/app/crm',
    'depends': [
        'base_setup',
        'sales_team',
        'mail',
        'calendar',
        'resource',
        'utm',
        'web_tour',
        'contacts',
        'digest',
        'phone_validation',
    ],
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',

        'data/crm_lead_merge_template.xml',
        'data/crm_lead_prediction_data.xml',
        'data/crm_lost_reason_data.xml',
        'data/crm_stage_data.xml',
        'data/crm_team_data.xml',
        'data/digest_data.xml',
        'data/ir_action_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/crm_recurring_plan_data.xml',
        'data/crm_tour.xml',

        'wizard/crm_lead_lost_views.xml',
        'wizard/crm_lead_to_opportunity_views.xml',
        'wizard/crm_lead_to_opportunity_mass_views.xml',
        'wizard/crm_merge_opportunities_views.xml',
        'wizard/crm_lead_pls_update_views.xml',

        'views/calendar_views.xml',
        'views/crm_recurring_plan_views.xml',
        'views/crm_lost_reason_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_member_views.xml',
        'views/digest_views.xml',
        'views/mail_activity_plan_views.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/utm_campaign_views.xml',
        'report/crm_activity_report_views.xml',
        'report/crm_opportunity_report_views.xml',
        'views/crm_team_views.xml',
        'views/crm_menu_views.xml',
        'views/crm_helper_templates.xml',
    ],
    'demo': [
        'data/crm_team_demo.xml',
        'data/crm_stage_demo.xml',
        'data/mail_template_demo.xml',
        'data/crm_team_member_demo.xml',
        'data/crm_lead_demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'crm/static/src/**',
            ('remove', 'crm/static/src/views/forecast_graph/**'),
            ('remove', 'crm/static/src/views/forecast_pivot/**'),
        ],
        'web.assets_backend_lazy': [
            'crm/static/src/views/forecast_graph/**',
            'crm/static/src/views/forecast_pivot/**',
        ],
        'web.assets_tests': [
            'crm/static/tests/tours/**/*',
        ],
        'web.assets_unit_tests': [
            'crm/static/tests/mock_server/**/*',
            'crm/static/tests/crm_test_helpers.js',
            'crm/static/tests/**/*.test.js',
            'crm/static/tests/crm_mock_server.js'
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}


# FILEPATH: odoo/addons/crm/models/calendar.py
class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_opportunity_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('crm.model_crm_lead').id,
                default_res_id=self.env.context['default_opportunity_id']
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to opportunity id (aka creating meeting from lead chatter)
        if 'opportunity_id' not in defaults:
            if self._is_crm_lead(defaults, self.env.context):
                defaults['opportunity_id'] = defaults.get('res_id', False) or self.env.context.get('default_res_id', False)

        return defaults

    opportunity_id = fields.Many2one(
        'crm.lead', 'Opportunity', domain="[('type', '=', 'opportunity')]",
        index=True, ondelete='set null')

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get('active_model') == 'crm.lead':
            opportunity_id = self.env.context.get('active_id')
            for event in self:
                if event.opportunity_id.id == opportunity_id:
                    event.is_highlighted = True

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events:
            if event.opportunity_id and not event.activity_ids:
                event.opportunity_id.log_meeting(event)
        return events

    def _is_crm_lead(self, defaults, ctx=None):
        """
            This method checks if the concerned model is a CRM lead.
            The information is not always in the defaults values,
            this is why it is necessary to check the context too.
        """
        res_model = defaults.get('res_model', False) or ctx and ctx.get('default_res_model')
        res_model_id = defaults.get('res_model_id', False) or ctx and ctx.get('default_res_model_id')

        return res_model and res_model == 'crm.lead' or res_model_id and self.env['ir.model'].sudo().browse(res_model_id).model == 'crm.lead'


# FILEPATH: odoo/addons/crm/models/crm_lead.py
_logger = logging.getLogger(__name__)
CRM_LEAD_FIELDS_TO_MERGE = [
    # UTM mixin
    'campaign_id',
    'medium_id',
    'source_id',
    # Mail mixin
    'email_cc',
    # description
    'name',
    'user_id',
    'color',
    'company_id',
    'lang_id',
    'team_id',
    'referred',
    # pipeline
    'stage_id',
    # revenues
    'expected_revenue',
    'recurring_plan',
    'recurring_revenue',
    # dates
    'create_date',
    'date_automation_last',
    'date_deadline',
    # partner / contact
    'partner_id',
    'title',
    'partner_name',
    'contact_name',
    'email_from',
    'function',
    'phone',
    'website',
]
PARTNER_FIELDS_TO_SYNC = [
    'lang',
    'phone',
    'function',
    'website',
]
PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]
PLS_COMPUTE_BATCH_STEP = 50000
PLS_UPDATE_BATCH_STEP = 5000
class CrmLead(models.Model):
    _name = 'crm.lead'
    _description = "Lead"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.thread.phone',
                'mail.activity.mixin',
                'utm.mixin',
                'format.address.mixin',
                'mail.tracking.duration.mixin',
               ]
    _primary_email = 'email_from'
    _check_company_auto = True
    _track_duration_field = 'stage_id'

    # Description
    name = fields.Char(
        'Opportunity', index='trigram', required=True,
        compute='_compute_name', readonly=False, store=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="[('share', '=', False)]",
        check_company=True, index=True, tracking=True)
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to lead company or all if no company')
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', check_company=True, index=True, tracking=True,
        compute='_compute_team_id', ondelete="set null", readonly=False, store=True, precompute=True)
    lead_properties = fields.Properties(
        'Properties', definition='team_id.lead_properties_definition',
        copy=True)
    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        compute='_compute_company_id', readonly=False, store=True)
    referred = fields.Char('Referred By')
    description = fields.Html('Notes')
    active = fields.Boolean('Active', default=True, tracking=72)
    type = fields.Selection([
        ('lead', 'Lead'), ('opportunity', 'Opportunity')], required=True, tracking=15, index=True,
        default=lambda self: 'lead' if self.env.user.has_group('crm.group_use_lead') else 'opportunity')
    # Pipeline management
    priority = fields.Selection(
        crm_stage.AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=crm_stage.AVAILABLE_PRIORITIES[0][0])
    stage_id = fields.Many2one(
        'crm.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
        domain="['|', ('team_ids', '=', False), ('team_ids', 'in', team_id)]")
    stage_id_color = fields.Integer(string='Stage Color', related="stage_id.color", export_string_translation=False)
    tag_ids = fields.Many2many(
        'crm.tag', 'crm_tag_rel', 'lead_id', 'tag_id', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    # Revenues
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True, default=0.0)
    prorated_revenue = fields.Monetary('Prorated Revenue', currency_field='company_currency', store=True, compute="_compute_prorated_revenue")
    recurring_revenue = fields.Monetary('Recurring Revenues', currency_field='company_currency', tracking=True, default=0.0)
    recurring_plan = fields.Many2one('crm.recurring.plan', string="Recurring Plan")
    recurring_revenue_monthly = fields.Monetary('Expected MRR', currency_field='company_currency', store=True,
                                                compute="_compute_recurring_revenue_monthly")
    recurring_revenue_monthly_prorated = fields.Monetary('Prorated MRR', currency_field='company_currency', store=True,
                                                         compute="_compute_recurring_revenue_monthly_prorated")
    recurring_revenue_prorated = fields.Monetary('Prorated Recurring Revenues', currency_field='company_currency',
                                                 compute="_compute_recurring_revenue_prorated", store=True)
    company_currency = fields.Many2one("res.currency", string='Currency', compute="_compute_company_currency", compute_sudo=True)
    # Dates
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False)
    date_automation_last = fields.Datetime('Last Action', readonly=True)
    date_open = fields.Datetime(
        'Assignment Date', compute='_compute_date_open', readonly=True, store=True)
    day_open = fields.Float('Days to Assign', compute='_compute_day_open', store=True)
    day_close = fields.Float('Days to Close', compute='_compute_day_close', store=True)
    date_last_stage_update = fields.Datetime(
        'Last Stage Update', compute='_compute_date_last_stage_update', index=True, readonly=True, store=True)
    date_conversion = fields.Datetime('Conversion Date', readonly=True)
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.")
    # Customer / contact

    # UX field to ease partner creation
    # Not to be relied on for business logic
    commercial_partner_id = fields.Many2one(
        'res.partner', string='Customer Company', domain="[('is_company', '=', True)]",
        compute='_compute_commercial_partner_id', readonly=False, store=False,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Contact', check_company=True, index=True, tracking=10,
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    partner_is_blacklisted = fields.Boolean('Partner is blacklisted', related='partner_id.is_blacklisted', readonly=True)
    contact_name = fields.Char(
        'Contact Name', index='trigram', tracking=30,
        compute='_compute_contact_name', readonly=False, store=True)
    partner_name = fields.Char(
        'Company Name', index='trigram', tracking=20,
        compute='_compute_partner_name', readonly=False, store=True,
        help='The name of the future partner company that will be created while converting the lead into opportunity')
    function = fields.Char('Job Position', compute='_compute_function', readonly=False, store=True)
    email_from = fields.Char(
        'Email', tracking=40, index='trigram',
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True)
    email_normalized = fields.Char(index='trigram')  # inherited via mail.thread.blacklist
    email_domain_criterion = fields.Char(
        string='Email Domain Criterion',
        compute="_compute_email_domain_criterion",
        index='btree_not_null',  # used for exact match, void value do not matter
        store=True,
    )
    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', readonly=False, store=True)
    phone_sanitized = fields.Char(index='btree_not_null')  # inherited via mail.thread.phone
    phone_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Phone Quality', compute="_compute_phone_state", store=True)
    email_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Email Quality', compute="_compute_email_state", store=True)
    website = fields.Char('Website', help="Website of the contact", compute="_compute_website", readonly=False, store=True)
    lang_id = fields.Many2one(
        'res.lang', string='Language',
        compute='_compute_lang_id', readonly=False, store=True)
    lang_code = fields.Char(related='lang_id.code')
    lang_active_count = fields.Integer(compute='_compute_lang_active_count')
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)
    # Probability (Opportunity only)
    probability = fields.Float(
        'Probability', aggregator="avg", copy=False,
        compute='_compute_probabilities', readonly=False, store=True)
    automated_probability = fields.Float('Automated Probability', compute='_compute_probabilities', readonly=True, store=True)
    is_automated_probability = fields.Boolean('Is automated probability?', compute="_compute_is_automated_probability")
    # Won/Lost
    won_status = fields.Selection(
        [
            ('won', 'Won'),
            ('lost', 'Lost'),
            ('pending', 'Pending'),
        ], string='Won/Lost', compute='_compute_won_status', store=True, tracking=70)
    lost_reason_id = fields.Many2one(
        'crm.lost.reason', string='Lost Reason',
        index=True, ondelete='restrict', tracking=71)
    # Statistics
    calendar_event_ids = fields.One2many('calendar.event', 'opportunity_id', string='Meetings')
    duplicate_lead_ids = fields.Many2many("crm.lead", compute="_compute_potential_lead_duplicates", string="Potential Duplicate Lead",
        context={"active_test": False}, compute_sudo=True)
    duplicate_lead_count = fields.Integer(compute="_compute_potential_lead_duplicates", string="Potential Duplicate Lead Count",
        compute_sudo=True)
    meeting_display_date = fields.Date(compute="_compute_meeting_display")
    meeting_display_label = fields.Char(compute="_compute_meeting_display")
    # UX
    partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_partner_email_update')
    partner_phone_update = fields.Boolean('Partner Phone will Update', compute='_compute_partner_phone_update')
    is_partner_visible = fields.Boolean('Is Partner Visible', compute='_compute_is_partner_visible')
    # UTMs - enforcing the fact that we want to 'set null' when relation is unlinked
    campaign_id = fields.Many2one(ondelete='set null')
    medium_id = fields.Many2one(ondelete='set null')
    source_id = fields.Many2one(ondelete='set null')

    _check_probability = models.Constraint(
        'check(probability >= 0 and probability <= 100)',
        'The probability of closing the deal should be between 0% and 100%!',
    )
    _user_id_team_id_type_index = models.Index("(user_id, team_id, type)")
    _create_date_team_id_idx = models.Index("(create_date, team_id)")
    _default_order_idx = models.Index('(priority DESC, id DESC) WHERE active IS TRUE')

    @api.constrains('probability', 'stage_id')
    def _check_won_validity(self):
        for lead in self:
            if lead.stage_id.is_won and lead.probability != 100:
                raise ValidationError(_("A lead in a Won stage cannot be lost. Move it to another stage first."))

    @api.depends('company_id')
    def _compute_user_company_ids(self):
        all_companies = self.env['res.company'].search([])
        for lead in self:
            if not lead.company_id:
                lead.user_company_ids = all_companies
            else:
                lead.user_company_ids = lead.company_id

    @api.depends('company_id')
    def _compute_company_currency(self):
        for lead in self:
            if not lead.company_id:
                lead.company_currency = self.env.company.currency_id
            else:
                lead.company_currency = lead.company_id.currency_id

    # ORM Override to manage company_currency to aggregates monetary field
    def _field_to_sql(self, alias, field_expr, query=None) -> SQL:
        if field_expr == 'company_currency':
            alias_company = query.make_alias(self._table, 'company_id')
            company_field_sql = self._field_to_sql(self._table, 'company_id', query)
            query.add_join('LEFT JOIN', alias_company, 'res_company', SQL(
                "%s = %s", company_field_sql, SQL.identifier(alias_company, 'id'),
            ))
            company_currency_expr = self.env['res.company']._field_to_sql(alias_company, 'currency_id', query)
            return SQL(
                '(CASE WHEN %s IS NOT NULL THEN %s ELSE %s END)',
                company_field_sql, company_currency_expr, self.env.company.currency_id.id
            )
        return super()._field_to_sql(alias, field_expr, query)

    @api.depends('user_id', 'type')
    def _compute_team_id(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for lead in self:
            # setting user as void should not trigger a new team computation
            if not lead.user_id:
                continue
            user = lead.user_id
            if lead.team_id and user in (lead.team_id.member_ids | lead.team_id.user_id):
                continue
            team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
            team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            if lead.team_id != team:
                lead.team_id = team.id

    @api.depends('user_id', 'team_id', 'partner_id')
    def _compute_company_id(self):
        """ Compute company_id coherency. """
        for lead in self:
            proposal = lead.company_id

            # invalidate wrong configuration
            if proposal:
                # company not in responsible companies
                if lead.user_id and proposal not in lead.user_id.company_ids:
                    proposal = False
                # inconsistent
                elif lead.team_id.company_id and proposal != lead.team_id.company_id:
                    proposal = False
                # void company on team and no assignee
                elif lead.team_id and not lead.team_id.company_id and not lead.user_id:
                    proposal = False
                # no user and no team -> void company and let assignment do its job
                # unless customer has a company
                elif not lead.team_id and not lead.user_id and \
                        (not lead.partner_id or lead.partner_id.company_id != proposal):
                    proposal = False

            # propose a new company based on team > user (respecting context) > partner
            if not proposal:
                if lead.team_id.company_id:
                    lead.company_id = lead.team_id.company_id
                elif lead.user_id:
                    if self.env.company in lead.user_id.company_ids:
                        lead.company_id = self.env.company
                    else:
                        lead.company_id = lead.user_id.company_id & self.env.companies
                elif lead.partner_id:
                    lead.company_id = lead.partner_id.company_id
                else:
                    lead.company_id = False

    @api.depends('team_id', 'type')
    def _compute_stage_id(self):
        for lead in self:
            if not lead.stage_id or (lead.team_id and lead.stage_id.team_ids and lead.team_id not in lead.stage_id.team_ids):
                lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id

    @api.depends('user_id')
    def _compute_date_open(self):
        for lead in self:
            if not lead.date_open and lead.user_id:
                lead.date_open = self.env.cr.now()

    @api.depends('stage_id')
    def _compute_date_last_stage_update(self):
        for lead in self:
            if not lead.date_last_stage_update:
                lead.date_last_stage_update = self.env.cr.now()

    @api.depends('create_date', 'date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        leads = self.filtered(lambda l: l.date_open and l.create_date)
        others = self - leads
        others.day_open = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date).replace(microsecond=0)
            date_open = fields.Datetime.from_string(lead.date_open)
            lead.day_open = abs((date_open - date_create).days)

    @api.depends('create_date', 'date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        leads = self.filtered(lambda l: l.date_closed and l.create_date)
        others = self - leads
        others.day_close = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_closed)
            lead.day_close = abs((date_close - date_create).days)

    def _get_rotting_depends_fields(self):
        return super()._get_rotting_depends_fields() + ['won_status', 'type']

    def _get_rotting_domain(self):
        return super()._get_rotting_domain() & Domain([
            ('won_status', '=', 'pending'),
            ('type', '=', 'opportunity'),
        ])

    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name:
                lead.name = _("%s's opportunity") % lead.partner_id.name

    @api.depends('partner_id', 'partner_name')
    def _compute_commercial_partner_id(self):
        leads_w_partners = self.filtered('partner_id')
        for lead in leads_w_partners:
            commercial_partner = lead.partner_id.commercial_partner_id
            lead.commercial_partner_id = commercial_partner.is_company and commercial_partner != lead.partner_id and commercial_partner
        # match by name if exists
        remaining_leads_w_pname = (self - leads_w_partners).filtered('partner_name')
        commercial_partner_by_name = self.env['res.partner']._read_group(
            [('is_company', '=', True), ('name', 'in', remaining_leads_w_pname.mapped('partner_name'))],
            ['name'], ['id:array_agg'],
        )
        remaining_leads_by_name = remaining_leads_w_pname.grouped('partner_name')
        for commercial_partner_name, commercial_partner_ids in commercial_partner_by_name:
            remaining_leads_by_name[commercial_partner_name].commercial_partner_id = commercial_partner_ids[0]

    @api.onchange('commercial_partner_id')
    def _onchange_commercial_partner_id(self):
        for lead in self:
            if lead.partner_id and lead.commercial_partner_id and lead.commercial_partner_id != lead.partner_id.commercial_partner_id:
                # writing to partner will invalidate and recompute
                # re-write the original value to keep user selection
                commercial_partner = lead.commercial_partner_id
                lead.update({
                    'partner_id': False,
                    'email_from': False,
                    'phone': False,
                })
                lead.commercial_partner_id = commercial_partner
            if not lead.name and lead.commercial_partner_id:
                lead.name = _("%s's opportunity", lead.commercial_partner_id.name)

    @api.depends('partner_id')
    def _compute_contact_name(self):
        """ compute the new values when partner_id has changed """
        to_reset = self.filtered(lambda l: not l.partner_id)
        to_reset.contact_name = False
        for lead in (self - to_reset):
            lead.update(lead._prepare_contact_name_from_partner(lead.partner_id))

    @api.depends('partner_id')
    def _compute_partner_name(self):
        """ compute the new values when partner_id has changed """
        to_reset = self.filtered(lambda l: not l.partner_id)
        to_reset.partner_name = False
        for lead in (self - to_reset):
            lead.update(lead._prepare_partner_name_from_partner(lead.partner_id))

    @api.depends('partner_id')
    def _compute_function(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.function or lead.partner_id.function:
                lead.function = lead.partner_id.function

    @api.depends('partner_id')
    def _compute_website(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.website or lead.partner_id.website:
                lead.website = lead.partner_id.website

    @api.depends('partner_id')
    def _compute_lang_id(self):
        """ compute the lang based on partner, erase any value to force the partner
        one if set. """
        # prepare cache
        lang_codes = [code for code in self.mapped('partner_id.lang') if code]
        if lang_codes:
            lang_id_by_code = dict(
                (code, self.env['res.lang']._get_data(code=code).id)
                for code in lang_codes
            )
        else:
            lang_id_by_code = {}
        for lead in self.filtered('partner_id'):
            lead.lang_id = lang_id_by_code.get(lead.partner_id.lang, False)

    @api.depends('lang_id')
    def _compute_lang_active_count(self):
        self.lang_active_count = len(self.env['res.lang'].get_installed())

    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for lead in self:
            lead.update(lead._prepare_address_values_from_partner(lead.partner_id))

    @api.depends('partner_id.email')
    def _compute_email_from(self):
        for lead in self:
            if lead.partner_id.email and lead._get_partner_email_update():
                lead.email_from = lead.partner_id.email

    def _inverse_email_from(self):
        for lead in self:
            if lead._get_partner_email_update(force_void=False):
                lead.partner_id.email = lead.email_from

    @api.depends('email_normalized')
    def _compute_email_domain_criterion(self):
        self.email_domain_criterion = False
        for lead in self.filtered('email_normalized'):
            lead.email_domain_criterion = iap_tools.mail_prepare_for_domain_search(
                lead.email_normalized
            )

    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id.phone and lead._get_partner_phone_update():
                lead.phone = lead.partner_id.phone

    def _inverse_phone(self):
        for lead in self:
            if lead._get_partner_phone_update(force_void=False):
                lead.partner_id.phone = lead.phone

    @api.depends('phone', 'country_id.code')
    def _compute_phone_state(self):
        for lead in self:
            phone_status = False
            if lead.phone:
                country_code = lead.country_id.code if lead.country_id and lead.country_id.code else None
                try:
                    if phone_validation.phone_parse(lead.phone, country_code):  # otherwise library not installed
                        phone_status = 'correct'
                except UserError:
                    phone_status = 'incorrect'
            lead.phone_state = phone_status

    @api.depends('email_from')
    def _compute_email_state(self):
        for lead in self:
            email_state = False
            if lead.email_from:
                email_state = 'incorrect'
                for email in email_normalize_all(lead.email_from):
                    if mail_validation.mail_validate(email):
                        email_state = 'correct'
                        break
            lead.email_state = email_state

    @api.depends('probability', 'automated_probability')
    def _compute_is_automated_probability(self):
        """ If probability and automated_probability are equal probability computation
        is considered as automatic, aka probability is sync with automated_probability """
        for lead in self:
            lead.is_automated_probability = tools.float_compare(lead.probability, lead.automated_probability, 2) == 0

    @api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())
    def _compute_probabilities(self):
        lead_probabilities, _unused = self._pls_get_naive_bayes_probabilities()
        for lead in self:
            if lead.id in lead_probabilities:
                was_automated = lead.active and lead.is_automated_probability
                lead.automated_probability = lead_probabilities[lead.id]
                if was_automated:
                    lead.probability = lead.automated_probability

    @api.depends('expected_revenue', 'probability')
    def _compute_prorated_revenue(self):
        for lead in self:
            lead.prorated_revenue = round((lead.expected_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)

    @api.depends('recurring_revenue', 'recurring_plan.number_of_months')
    def _compute_recurring_revenue_monthly(self):
        for lead in self:
            lead.recurring_revenue_monthly = (lead.recurring_revenue or 0.0) / (lead.recurring_plan.number_of_months or 1)

    @api.depends('recurring_revenue_monthly', 'probability')
    def _compute_recurring_revenue_monthly_prorated(self):
        for lead in self:
            lead.recurring_revenue_monthly_prorated = (lead.recurring_revenue_monthly or 0.0) * (lead.probability or 0) / 100.0

    @api.depends('recurring_revenue', 'probability')
    def _compute_recurring_revenue_prorated(self):
        for lead in self:
            lead.recurring_revenue_prorated = (lead.recurring_revenue or 0.0) * (lead.probability or 0) / 100.0

    @api.depends('calendar_event_ids', 'calendar_event_ids.start')
    def _compute_meeting_display(self):
        now = fields.Datetime.now()
        meeting_data = self.env['calendar.event'].sudo()._read_group([
            ('opportunity_id', 'in', self.ids),
        ], ['opportunity_id'], ['start:array_agg', 'start:max'])
        mapped_data = {
            lead: {
                'last_meeting_date': last_meeting_date,
                'next_meeting_date': min([dt for dt in meeting_start_dates if dt > now] or [False]),
            } for lead, meeting_start_dates, last_meeting_date in meeting_data
        }
        for lead in self:
            lead_meeting_info = mapped_data.get(lead)
            if not lead_meeting_info:
                lead.meeting_display_date = False
                lead.meeting_display_label = _('No Meeting')
            elif lead_meeting_info['next_meeting_date']:
                lead.meeting_display_date = fields.Datetime.context_timestamp(lead, lead_meeting_info['next_meeting_date'])
                lead.meeting_display_label = _('Next Meeting')
            else:
                lead.meeting_display_date = fields.Datetime.context_timestamp(lead, lead_meeting_info['last_meeting_date'])
                lead.meeting_display_label = _('Last Meeting')

    @api.depends('active', 'probability', 'stage_id')
    def _compute_won_status(self):
        for lead in self:
            if lead.probability == 100 and lead.stage_id.is_won:
                lead.won_status = 'won'
            elif not lead.active and lead.probability == 0:
                lead.won_status = 'lost'
            else:
                lead.won_status = 'pending'

    @api.depends('email_domain_criterion', 'email_normalized', 'partner_id',
                 'phone_sanitized')
    def _compute_potential_lead_duplicates(self):
        """ Override potential lead duplicates computation to be more efficient
        with high lead volume.
        Criterions:
          * email domain exact match;
          * phone_sanitized exact match;
          * same commercial entity;
        """
        SEARCH_RESULT_LIMIT = 21

        def return_if_relevant(model_name, domain):
            """ Returns the recordset obtained by performing a search on the provided
            model with the provided domain if the cardinality of that recordset is
            below a given threshold (i.e: `SEARCH_RESULT_LIMIT`). Otherwise, returns
            an empty recordset of the provided model as it indicates search term
            was not relevant.
            Note: The function will use the administrator privileges to guarantee
            that a maximum amount of leads will be included in the search results
            and transcend multi-company record rules. It also includes archived
            records. Idea is that counter indicates duplicates are present and
            the lead could be escalated to managers.
            """
            model = self.env[model_name].with_context(active_test=False)
            res = model.search(domain, limit=SEARCH_RESULT_LIMIT)
            return res if len(res) < SEARCH_RESULT_LIMIT else model

        for lead in self:
            lead_id = lead._origin.id
            common_lead_domain = [
                ('id', '!=', lead_id)
            ]

            duplicate_lead_ids = self.env['crm.lead']

            # check the "company" email domain duplicates
            if lead.email_domain_criterion:
                duplicate_lead_ids |= return_if_relevant('crm.lead', common_lead_domain + [
                    ('email_domain_criterion', '=', lead.email_domain_criterion)
                ])
            # check for "same commercial entity" duplicates
            if lead.partner_id and lead.partner_id.commercial_partner_id:
                duplicate_lead_ids |= lead.with_context(active_test=False).search(common_lead_domain + [
                    ("partner_id", "child_of", lead.partner_id.commercial_partner_id.ids)
                ])
            # check the phone number duplicates, based on phone_sanitized. Only
            # exact matches are found, and the single one stored in phone_sanitized
            # in case phone is set.
            if lead.phone_sanitized:
                duplicate_lead_ids |= return_if_relevant('crm.lead', common_lead_domain + [
                    ('phone_sanitized', '=', lead.phone_sanitized)
                ])

            lead.duplicate_lead_ids = duplicate_lead_ids + lead
            lead.duplicate_lead_count = len(duplicate_lead_ids)

    @api.depends('email_from', 'partner_id')
    def _compute_partner_email_update(self):
        for lead in self:
            lead.partner_email_update = lead._get_partner_email_update(force_void=False)

    @api.depends('phone', 'partner_id')
    def _compute_partner_phone_update(self):
        for lead in self:
            lead.partner_phone_update = lead._get_partner_phone_update(force_void=False)

    @api.depends_context('uid')
    @api.depends('partner_id', 'type')
    def _compute_is_partner_visible(self):
        """ When the crm.lead is of type 'lead', we don't want to display the "Customer" field on the form view
        unless it's set (or debug mode).

        Indeed, most of the times leads will not have this information set, since when we assign a Customer we
        usually convert the lead to an opportunity as well.

        This means that on the lead form, we don't want to display this field since it may be misleading for the
        end user.
        When it's set however, we want to display it, mainly because there are a few automatic synchronizations between
        the lead and its partner (phone and email for examples), and this needs to be clear that modifying
        one of those fields will in turn modify the linked partner."""
        is_debug_mode = self.env.user.has_group('base.group_no_one')
        for lead in self:
            lead.is_partner_visible = bool(lead.type == 'opportunity' or lead.partner_id or is_debug_mode)

    @api.onchange('phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.phone:
            self.phone = self._phone_format(fname='phone', force_format='INTERNATIONAL') or self.phone

    def _prepare_values_from_partner(self, partner):
        """ Get a dictionary with values coming from partner information to
        copy on a lead. Non-address fields get the current lead
        values to avoid being reset if partner has no value for them. """

        # Sync all address fields from partner, or none, to avoid mixing them.
        values = self._prepare_address_values_from_partner(partner)

        # For other fields, get the info from the partner, but only if set
        values.update({f: partner[f] or self[f] for f in PARTNER_FIELDS_TO_SYNC if f != 'lang'})
        if partner.lang:
            values['lang_id'] = self.env['res.lang']._get_data(code=partner.lang).id

        # Fields with specific logic
        values.update(self._prepare_contact_name_from_partner(partner))
        values.update(self._prepare_partner_name_from_partner(partner))

        return self._convert_to_write(values)

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    def _prepare_contact_name_from_partner(self, partner):
        contact_name = False if partner.is_company else partner.name
        return {'contact_name': contact_name or self.contact_name}

    def _prepare_partner_name_from_partner(self, partner):
        """ Company name: name of partner parent (if set) or name of partner
        (if company) or company_name of partner (if not a company). """
        partner_name = partner.parent_id.name
        if not partner_name and partner.is_company:
            partner_name = partner.name
        elif not partner_name and partner.company_name:
            partner_name = partner.company_name
        return {'partner_name': partner_name or self.partner_name}

    def _get_partner_email_update(self, force_void=True):
        """Calculate if we should write the email on the related partner. When
        the email of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of email update methods.

        :param bool force_void: if False, skip when lead has a void email value.
          This is used notably to avoid propagating void lead value to a valid
          partner value.
        """
        self.ensure_one()
        if self.partner_id and (force_void or self.email_from) and self.email_from != self.partner_id.email:
            lead_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.partner_id.email) or self.partner_id.email or False
            return lead_email_normalized != partner_email_normalized
        return False

    def _get_partner_phone_update(self, force_void=True):
        """Calculate if we should write the phone on the related partner. When
        the phone of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of phone update methods.

        :param bool force_void: if False, skip when lead has a void phone value.
          This is used notably to avoid propagating void lead value to a valid
          partner value.
        """
        self.ensure_one()
        if self.partner_id and (force_void or self.phone) and self.phone != self.partner_id.phone:
            lead_phone_formatted = self._phone_format(fname='phone') or self.phone or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website'):
                vals['website'] = self.env['res.partner']._clean_website(vals['website'])
        leads = super().create(vals_list)

        # handling a date_closed value if the lead is directly created in the won stage
        won_to_set = leads.filtered(lambda l: not l.date_closed and l.stage_id.is_won)
        won_to_set.write({'date_closed': fields.Datetime.now()})

        if self.default_get(['partner_id']).get('partner_id') is None:
            commercial_partner_ids = [vals['commercial_partner_id'] for vals in vals_list if vals.get('commercial_partner_id')]
            CommercialPartners = self.env['res.partner'].with_prefetch(commercial_partner_ids)
            for lead, lead_vals in zip(leads, vals_list, strict=True):
                if not lead_vals.get('partner_id') and lead_vals.get('commercial_partner_id'):
                    commercial_partner = CommercialPartners.browse(lead_vals['commercial_partner_id'])
                    if (lead.phone or lead.email_from) and (
                        lead.phone_sanitized != commercial_partner.phone_sanitized or
                        lead.email_normalized != commercial_partner.email_normalized
                    ):
                        lead.partner_name = lead.partner_name or commercial_partner.name
                        continue
                    lead.partner_id = commercial_partner

        leads._handle_won_lost({}, {
            lead.id: {
                'is_lost': lead.won_status == 'lost',
                'is_won': lead.won_status == 'won',
            } for lead in leads
        })

        return leads

    def write(self, vals):
        if vals.get('website'):
            vals['website'] = self.env['res.partner']._clean_website(vals['website'])

        now = self.env.cr.now()
        stage_updated, stage_is_won = False, False
        # stage change (or reset): update date_last_stage_update if at least one
        # lead does not have the same stage
        if 'stage_id' in vals:
            stage_updated = any(lead.stage_id.id != vals['stage_id'] for lead in self)
            if stage_updated:
                vals['date_last_stage_update'] = now
            if stage_updated and vals.get('stage_id'):
                stage = self.env['crm.stage'].browse(vals['stage_id'])
                if stage.is_won:
                    vals.update({'active': True, 'probability': 100, 'automated_probability': 100})
                    stage_is_won = True
        # user change; update date_open if at least one lead does not
        # have the same user
        if 'user_id' in vals and not vals.get('user_id'):
            vals['date_open'] = False
        elif vals.get('user_id'):
            user_updated = any(lead.user_id.id != vals['user_id'] for lead in self)
            if user_updated:
                vals['date_open'] = now

        # stage change with new stage: update probability and date_closed
        if vals.get('probability', 0) >= 100 or not vals.get('active', True):
            vals['date_closed'] = fields.Datetime.now()
        elif vals.get('probability', 0) > 0:
            vals['date_closed'] = False
        elif stage_updated and not stage_is_won and not 'probability' in vals:
            vals['date_closed'] = False

        update_frequencies = any(field in ['active', 'stage_id', 'probability'] for field in vals)
        old_status_by_lead = {
            lead.id: {
                'is_lost': lead.won_status == 'lost',
                'is_won': lead.won_status == 'won',
            } for lead in self
        } if update_frequencies else {}

        if not stage_is_won:
            result = super().write(vals)
        else:
            # stage change between two won stages: does not change the date_closed
            leads_already_won = self.filtered(lambda lead: lead.stage_id.is_won)
            remaining = self - leads_already_won
            if remaining:
                result = super(CrmLead, remaining).write(vals)
            if leads_already_won:
                vals.pop('date_closed', False)
                result = super(CrmLead, leads_already_won).write(vals)

        if update_frequencies:
            self._handle_won_lost(old_status_by_lead, {
                lead.id: {
                    'is_lost': lead.won_status == 'lost',
                    'is_won': lead.won_status == 'won',
                } for lead in self
            })

        return result

    @api.model
    def search_fetch(self, domain, field_names=None, offset=0, limit=None, order=None):
        """ Override to support ordering on my_activity_date_deadline.

        Ordering through web client calls search_read() with an order parameter
        set. Method search_read() then calls search_fetch(). Here we override
        search_fetch() to intercept a search with an order on field
        my_activity_date_deadline. In that case we do the search in two steps.

        First step: fill with deadline-based results

          * Perform a read_group on my activities to get a mapping lead_id / deadline
            Remember date_deadline is required, we always have a value for it. Only
            the earliest deadline per lead is kept.
          * Search leads linked to those activities that also match the asked domain
            and order from the original search request.
          * Results of that search will be at the top of returned results. Use limit
            None because we have to search all leads linked to activities as ordering
            on deadline is done in post processing.
          * Reorder them according to deadline asc or desc depending on original
            search ordering. Finally take only a subset of those leads to fill with
            results matching asked offset / limit.

        Second step: fill with other results. If first step does not gives results
        enough to match offset and limit parameters we fill with a search on other
        leads. We keep the asked domain and ordering while filtering out already
        scanned leads to keep a coherent results.

        All other search and search_read are left untouched by this override to avoid
        side effects. Search_count is not affected by this override.
        """
        if not order or 'my_activity_date_deadline' not in order:
            return super().search_fetch(domain, field_names, offset, limit, order)
        order_items = [order_item.strip().lower() for order_item in (order or self._order).split(',')]
        domain = Domain(domain)

        # Perform a read_group on my activities to get a mapping lead_id / deadline
        # Remember date_deadline is required, we always have a value for it. Only
        # the earliest deadline per lead is kept.
        activity_asc = any('my_activity_date_deadline asc' in item for item in order_items)
        my_lead_activities = self.env['mail.activity']._read_group(
            [('res_model', '=', self._name), ('user_id', '=', self.env.uid)],
            ['res_id'],
            ['date_deadline:min'],
            order='date_deadline:min ASC, res_id',
        )
        my_lead_mapping = dict(my_lead_activities)
        my_lead_ids = list(my_lead_mapping.keys())
        my_lead_domain = Domain('id', 'in', my_lead_ids) & domain
        my_lead_order = ', '.join(item for item in order_items if 'my_activity_date_deadline' not in item)

        # Search leads linked to those activities and order them. See docstring
        # of this method for more details.
        search_res = super().search_fetch(my_lead_domain, field_names, order=my_lead_order)
        my_lead_ids_ordered = sorted(search_res.ids, key=lambda lead_id: my_lead_mapping[lead_id], reverse=not activity_asc)
        # keep only requested window (offset + limit, or offset+)
        my_lead_ids_keep = my_lead_ids_ordered[offset:(offset + limit)] if limit else my_lead_ids_ordered[offset:]
        # keep list of already skipped lead ids to exclude them from future search
        my_lead_ids_skip = my_lead_ids_ordered[:(offset + limit)] if limit else my_lead_ids_ordered

        # do not go further if limit is achieved
        if limit and len(my_lead_ids_keep) >= limit:
            return self.browse(my_lead_ids_keep)

        # Fill with remaining leads. If a limit is given, simply remove count of
        # already fetched. Otherwise keep none. If an offset is set we have to
        # reduce it by already fetch results hereabove. Order is updated to exclude
        # my_activity_date_deadline when calling super() .
        lead_limit = (limit - len(my_lead_ids_keep)) if limit else None
        if offset:
            lead_offset = max((offset - len(search_res), 0))
        else:
            lead_offset = 0
        lead_order = ', '.join(item for item in order_items if 'my_activity_date_deadline' not in item)

        other_lead_res = super().search_fetch(
            Domain('id', 'not in', my_lead_ids_skip) & domain,
            field_names, lead_offset, lead_limit, lead_order,
        )
        return self.browse(my_lead_ids_keep) + other_lead_res

    def _handle_won_lost(self, old_status_by_lead, new_status_by_lead):
        """ This method handles all changes of won / lost status of leads on creation / writing,
        and update the scoring frequency table accordingly:
        - To lost : Increment corresponding lost count
        - To won : Increment corresponding won count
        - Leaving lost : Decrement corresponding lost count
        - Leaving won : Decrement corresponding won count
        More than one operation can happen simultaneously, for instance, going from lost to won:
        Decrement corresponding lost count + increment corresponding won count.

        A lead is WON when in won stage (and probability = 100% but that is implied and constrained)
        A lead is LOST when active = False AND probability = 0
        In every other case, the lead is not won nor lost.

        :param old_status_by_lead: dict of old status by lead: {lead.id: {'is_lost': ..., 'is_won': ...}}
        :param new_status_by_lead: dict of new status by lead: {lead.id: {'is_lost': ..., 'is_won': ...}}
        """
        leads_reach_won_ids = self.env['crm.lead']
        leads_leave_won_ids = self.env['crm.lead']
        leads_reach_lost_ids = self.env['crm.lead']
        leads_leave_lost_ids = self.env['crm.lead']

        for lead in self:
            new_status = new_status_by_lead.get(
                lead.id, {'is_lost': False, 'is_won': False}
            )
            old_status = old_status_by_lead.get(
                lead.id, {'is_lost': False, 'is_won': False}
            )
            if new_status['is_lost'] and new_status['is_won']:
                raise ValidationError(_("The lead %s cannot be won and lost at the same time.", lead))

            if new_status['is_lost'] and not old_status['is_lost']:
                leads_reach_lost_ids += lead
            elif not new_status['is_lost'] and old_status['is_lost']:
                leads_leave_lost_ids += lead

            if new_status['is_won'] and not old_status['is_won']:
                leads_reach_won_ids += lead
            elif not new_status['is_won'] and old_status['is_won']:
                leads_leave_won_ids += lead

        leads_reach_won_ids._pls_increment_frequencies(to_state='won')
        leads_leave_won_ids._pls_increment_frequencies(from_state='won')
        leads_reach_lost_ids._pls_increment_frequencies(to_state='lost')
        leads_leave_lost_ids._pls_increment_frequencies(from_state='lost')

        return True

    def copy_data(self, default=None):
        # set default value in context, if not already set (Put stage to 'new' stage)
        # Set date_open to today if it is an opp
        default = dict(default or {})
        if not self.env.user.has_group('crm.group_use_recurring_revenues'):
            default['recurring_revenue'] = 0
            default['recurring_plan'] = False
        vals_list = super().copy_data(default=default)
        now = self.env.cr.now()
        for lead, vals in zip(self, vals_list):
            vals.setdefault('type', lead.type)
            vals.setdefault('team_id', lead.team_id.id)
            vals['date_open'] = now if lead.type == 'opportunity' and lead.user_id.active else False
            if not lead.user_id.active:
                vals['user_id'] = False
        return vals_list

    def unlink(self):
        """ Update meetings when removing opportunities, otherwise you have
        a link to a record that does not lead anywhere. """
        meetings = self.env['calendar.event'].search([
            ('res_id', 'in', self.ids),
            ('res_model', '=', self._name),
        ])
        if meetings:
            meetings.write({
                'res_id': False,
                'res_model_id': False,
            })
        return super().unlink()

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self.env.context.get('default_team_id')
        team_ids = self.env.user.crm_team_ids._ids if self.env.context.get('show_user_team_stages') else ()
        team_ids += (team_id,) if team_id else ()
        search_domain = ['|', ('id', 'in', stages.ids), ('team_ids', '=', False)]
        if team_ids:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_ids', '=', False), ('team_ids', 'in', team_ids)]

        # perform search
        stage_ids = stages.sudo()._search(search_domain, order=stages._order)
        return stages.browse(stage_ids)

    def _stage_find(self, team_id=False, domain=None, order='sequence, id', limit=1):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :param order : base search order for stage
            :param limit : base search limit for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for lead in self:
            if lead.team_id:
                team_ids.add(lead.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_ids', '=', False), ('team_ids', 'in', list(team_ids))]
        else:
            search_domain = [('team_ids', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['crm.stage'].search(search_domain, order=order, limit=limit)

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def action_unarchive(self):
        """ When re-activating, force update probability for both leads and
        opportunities. Note that archiving triggers nothing more, as a lead
        can be archived and not lost. """
        activated = self.filtered(lambda rec: not rec.active)
        res = super().action_unarchive()
        if activated:
            activated.write({'lost_reason_id': False})
            activated._compute_probabilities()
        return res

    def action_restore(self):
        """ Restoring a lost lead means that it should go back to its normal life cycle.
        This should reactivate the lead but also force the recompute of its probability, for the stage where the lead
        is currently at. During toggle_active, when reactivating a lost lead,only the automated probability will be
        recomputed, because the probability is not automated anymore. Restore will reset this automation."""
        self.action_unarchive()
        for lead in self:
            lead.probability = lead.automated_probability

    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 AND active = False """
        res = self.action_archive()
        self.write({**additional_values, 'probability': 0, 'automated_probability': 0})
        return res

    def action_set_won(self):
        """ Won semantic: stage.is_won (AND probability = 100 but implied) """
        self.action_unarchive()
        # group the leads by team_id, in order to write once by values couple (each write leads to frequency increment)
        leads_by_won_stage = {}
        for lead in self:
            won_stages = self._stage_find(domain=[('is_won', '=', True)], limit=None)
            # ABD : We could have a mixed pipeline, with "won" stages being separated by "standard"
            # stages. In the future, we may want to prevent any "standard" stage to have a higher
            # sequence than any "won" stage. But while this is not the case, searching
            # for the "won" stage while alterning the sequence order (see below) will correctly
            # handle such a case :
            #       stage sequence : [x] [x (won)] [y] [y (won)] [z] [z (won)]
            #       when in stage [y] and marked as "won", should go to the stage [y (won)],
            #       not in [x (won)] nor [z (won)]
            stage_id = next((stage for stage in won_stages if stage.sequence > lead.stage_id.sequence), None)
            if not stage_id:
                stage_id = next((stage for stage in reversed(won_stages) if stage.sequence <= lead.stage_id.sequence), won_stages)
            if stage_id in leads_by_won_stage:
                leads_by_won_stage[stage_id] += lead
            else:
                leads_by_won_stage[stage_id] = lead
        for won_stage_id, leads in leads_by_won_stage.items():
            leads.write({'stage_id': won_stage_id.id, 'probability': 100})
        return True

    def action_set_automated_probability(self):
        """ Update the automated probability and align probability to that value """
        self.ensure_one()
        self._compute_probabilities()
        self.write({'probability': self.automated_probability})

    def action_set_won_rainbowman(self):
        self.ensure_one()
        self.action_set_won()

        message = self._get_rainbowman_message()
        if message:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/image/%s/%s/image_1024' % (self.team_id.user_id._name, self.team_id.user_id.id) if self.team_id.user_id.image_1024 else '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        return True

    def get_rainbowman_message(self):
        self.ensure_one()
        if self.stage_id.is_won:
            return self._get_rainbowman_message()
        return False

    def _get_rainbowman_message(self):
        self.ensure_one()
        if not self.user_id:
            return False
        self.flush_model()  # flush fields to make sure DB is up to date

        # checked here as it is its position in the priority order
        if len(self.message_ids) >= 25:
            return _('Phew, that took some effort — but you nailed it. Good job!')

        team_condition = f'team_id = {self.team_id.id}' if self.team_id else 'team_id IS NULL'
        source_case = f'source_id = {self.source_id.id} AND {team_condition}' if self.source_id else 'false'
        country_case = f'country_id = {self.country_id.id} AND {team_condition}' if self.country_id else 'false'
        tz_midnight = fields.Datetime.now().astimezone(pytz.timezone(self.env.user.tz or self.user_id.tz or 'UTC')).replace(hour=0, minute=0, second=0)
        tz_midnight_in_utc = tz_midnight.astimezone(pytz.UTC).replace(tzinfo=None)
        query = f"""
        SELECT
            MAX(CASE WHEN team_id = %(team_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '31 days' AND id <> %(lead_id)s THEN expected_revenue ELSE 0 END) AS max_team_31,
            MAX(CASE WHEN team_id = %(team_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '7 days'  AND id <> %(lead_id)s THEN expected_revenue ELSE 0 END) AS max_team_7,
            MAX(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '31 days' AND id <> %(lead_id)s THEN expected_revenue ELSE 0 END) AS max_user_31,
            MAX(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '7 days'  AND id <> %(lead_id)s THEN expected_revenue ELSE 0 END) AS max_user_7,
            MIN(CASE WHEN COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '31 days' THEN day_close ELSE 31 END) AS min_day_close_31,
            COUNT(CASE WHEN user_id = %(user_id)s THEN 1 ELSE NULL END) AS count_user_closed_year,
            COUNT(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '3 days' AND COALESCE(date_closed, create_date) < %(tz_midnight)s - INTERVAL '2 days' THEN 1 ELSE NULL END) AS count_user_closed_minus3day,
            COUNT(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '2 days' AND COALESCE(date_closed, create_date) < %(tz_midnight)s - INTERVAL '1 days' THEN 1 ELSE NULL END) AS count_user_closed_minus2day,
            COUNT(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s - INTERVAL '1 days' AND COALESCE(date_closed, create_date) < %(tz_midnight)s THEN 1 ELSE NULL END) AS count_user_closed_yesterday,
            COUNT(CASE WHEN user_id = %(user_id)s AND COALESCE(date_closed, create_date) >= %(tz_midnight)s THEN 1 ELSE NULL END) AS count_user_closed_today,
            COUNT(CASE WHEN {source_case} THEN 1 ELSE NULL END) AS count_source_closed_year,
            COUNT(CASE WHEN {country_case} THEN 1 ELSE NULL END) AS count_country_closed_year
            FROM crm_lead
            WHERE
                type = 'opportunity'
            AND
                active = True
            AND
                probability = 100
            AND
                DATE_TRUNC('year', COALESCE(date_closed, create_date)) = DATE_TRUNC('year', %(tz_midnight)s)
            AND
                (user_id = %(user_id)s OR team_id = %(team_id)s)
        """
        self.env.cr.execute(query, {
            'user_id': self.env.user.id,
            'team_id': self.team_id.id or -1,
            'lead_id': self.id,
            'tz_midnight': tz_midnight_in_utc,
        })
        query_result = self.env.cr.dictfetchone()

        def _is_lower_than_expected_revenue(value):
            return self.expected_revenue and value is not None and value < self.expected_revenue

        if query_result['count_user_closed_year'] == 1:
            return _('Go, go, go! Congrats for your first deal.')
        elif _is_lower_than_expected_revenue(query_result['max_team_31']):
            return _('Boom! Team record for the past 30 days.')
        elif _is_lower_than_expected_revenue(query_result['max_team_7']):
            return _('Yeah! Best deal out of the last 7 days for the team.')
        elif _is_lower_than_expected_revenue(query_result['max_user_31']):
            return _('You just beat your personal record for the past 30 days.')
        elif _is_lower_than_expected_revenue(query_result['max_user_7']):
            return _('You just beat your personal record for the past 7 days.')
        elif query_result['count_user_closed_today'] == 5:
            return _('You\'re on fire! Fifth deal won today 🔥')
        elif query_result['count_user_closed_today'] == 1 and query_result['count_user_closed_yesterday'] and query_result['count_user_closed_minus2day'] and not query_result['count_user_closed_minus3day']:
            return _('You\'re on a winning streak. 3 deals in 3 days, congrats!')
        # check that at least one minute has elapsed since record creation to only account for 'real' leads
        elif query_result['min_day_close_31'] == self.day_close and self.day_close < 31 \
            and self.date_closed and (self.date_closed - self.create_date).total_seconds() > 60:
            return _('Wow, that was fast. That deal didn’t stand a chance!')
        # use duration tracking field to determine if the task jumped from first to last stage
        # only takes into accounts stages on which the lead has spent at least a minute,
        # to only account for valid stage movements
        elif len(stage_ids := [int(stage_id) for stage_id, duration in self.duration_tracking.items() if duration >= 60]) == 1:
            first_stage = self.env['crm.stage'].search([
                '|', ('team_ids', 'in', False), ('team_ids', 'in', self.team_id.id),
            ], order='sequence ASC', limit=1)
            if first_stage.id == stage_ids[0]:
                return _('No detours, no delays - from %(stage_name)s straight to the win! 🚀', stage_name=first_stage.name)
        if query_result['count_country_closed_year'] == 1 and self.country_id:
            return _('You just expanded the map! First win in %(country)s.', country=self.country_id.name)
        elif query_result['count_source_closed_year'] == 1 and self.source_id:
            return _('Yay, your first win from %(utm_source_name)s!', utm_source_name=self.source_id.name)
        return False

    def action_schedule_meeting(self, smart_calendar=True):
        """ Open meeting's calendar view to schedule meeting on current opportunity.

            :param bool smart_calendar: to set to False if the view should not try to choose relevant
              mode and initial date for calendar view, see ``_get_opportunity_meeting_view_parameters``
            :returns: dictionary value for created Meeting view
            :rtype: dict
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        current_opportunity_id = self.id if self.type == 'opportunity' else False
        action['context'] = {
            'search_default_opportunity_id': current_opportunity_id,
            'default_opportunity_id': current_opportunity_id,
            'default_partner_id': self.partner_id.id,
            'default_partner_ids': partner_ids,
            'default_team_id': self.team_id.id,
            'default_name': self.name,
        }

        # 'Smart' calendar view : get the most relevant time period to display to the user.
        if current_opportunity_id and smart_calendar:
            mode, initial_date = self._get_opportunity_meeting_view_parameters()
            action['context'].update({'default_mode': mode, 'initial_date': initial_date})

        return action

    def _get_opportunity_meeting_view_parameters(self):
        """ Return the most relevant parameters for calendar view when viewing meetings linked to an opportunity.
            If there are any meetings that are not finished yet, only consider those meetings,
            since the user would prefer no to see past meetings. Otherwise, consider all meetings.
            Allday events datetimes are used without taking tz into account.
            -If there is no event, return week mode and false (The calendar will target 'now' by default)
            -If there is only one, return week mode and date of the start of the event.
            -If there are several events entirely on the same week, return week mode and start of first event.
            -Else, return month mode and the date of the start of first event as initial date. (If they are
            on the same month, this will display that month and therefore show all of them, which is expected)

            :return tuple(mode, initial_date)
                - mode: selected mode of the calendar view, 'week' or 'month'
                - initial_date: date of the start of the first relevant meeting. The calendar will target that date.
        """
        self.ensure_one()
        meeting_results = self.env["calendar.event"].search_read([('opportunity_id', '=', self.id)], ['start', 'stop', 'allday'])
        if not meeting_results:
            return "week", False

        user_pytz = self.env.tz

        # meeting_dts will contain one tuple of datetimes per meeting : (Start, Stop)
        # meetings_dts and now_dt are as per user time zone.
        meeting_dts = []
        now_dt = datetime.now().astimezone(user_pytz).replace(tzinfo=None)

        # When creating an allday meeting, whatever the TZ, it will be stored the same e.g. 00.00.00->23.59.59 in utc or
        # 08.00.00->18.00.00. Therefore we must not put it back in the user tz but take it raw.
        for meeting in meeting_results:
            if meeting.get('allday'):
                meeting_dts.append((meeting.get('start'), meeting.get('stop')))
            else:
                meeting_dts.append((meeting.get('start').astimezone(user_pytz).replace(tzinfo=None),
                                   meeting.get('stop').astimezone(user_pytz).replace(tzinfo=None)))

        # If there are meetings that are still ongoing or to come, only take those.
        unfinished_meeting_dts = [meeting_dt for meeting_dt in meeting_dts if meeting_dt[1] >= now_dt]
        relevant_meeting_dts = unfinished_meeting_dts if unfinished_meeting_dts else meeting_dts
        relevant_meeting_count = len(relevant_meeting_dts)

        if relevant_meeting_count == 1:
            return "week", relevant_meeting_dts[0][0].date()
        else:
            # Range of meetings
            earliest_start_dt = min(relevant_meeting_dt[0] for relevant_meeting_dt in relevant_meeting_dts)
            latest_stop_dt = max(relevant_meeting_dt[1] for relevant_meeting_dt in relevant_meeting_dts)

            # The week start day depends on language. We fetch the week_start of user's language. 1 is monday.
            lang_week_start = self.env["res.lang"].search_read([('code', '=', self.env.user.lang)], ['week_start'])
            # We substract one to make week_start_index range 0-6 instead of 1-7
            week_start_index = int(lang_week_start[0].get('week_start', '1')) - 1

            # We compute the weekday of earliest_start_dt according to week_start_index. earliest_start_dt_index will be 0 if we are on the
            # first day of the week and 6 on the last. weekday() returns 0 for monday and 6 for sunday. For instance, Tuesday in UK is the
            # third day of the week, so earliest_start_dt_index is 2, and remaining_days_in_week includes tuesday, so it will be 5.
            # The first term 7 is there to avoid negative left side on the modulo, improving readability.
            earliest_start_dt_weekday = (7 + earliest_start_dt.weekday() - week_start_index) % 7
            remaining_days_in_week = 7 - earliest_start_dt_weekday

            # We compute the start of the week following the one containing the start of the first meeting.
            next_week_start_date = earliest_start_dt.date() + timedelta(days=remaining_days_in_week)

            # Latest_stop_dt must be before the start of following week. Limit is therefore set at midnight of first day, included.
            meetings_in_same_week = latest_stop_dt <= datetime(next_week_start_date.year, next_week_start_date.month, next_week_start_date.day, 0, 0, 0)

            if meetings_in_same_week:
                return "week", earliest_start_dt.date()
            else:
                return "month", earliest_start_dt.date()

    def action_reschedule_meeting(self):
        self.ensure_one()
        action = self.action_schedule_meeting(smart_calendar=False)
        next_activity = self.activity_ids.filtered(lambda activity: activity.user_id == self.env.user)[:1]
        if next_activity.calendar_event_id:
            action['context']['initial_date'] = next_activity.calendar_event_id.start
        return action

    def action_show_potential_duplicates(self):
        """ Open kanban view to display duplicate leads or opportunity.
            :return dict: dictionary value for created kanban view
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_opportunities")
        action['domain'] = [('id', 'in', self.duplicate_lead_ids.ids)]
        action['context'] = {
            'active_test': False,
            'create': False
        }
        return action

    # ------------------------------------------------------------
    # VIEWS
    # ------------------------------------------------------------

    def redirect_lead_opportunity_view(self):
        self.ensure_one()
        return {
            'name': _('Lead or Opportunity'),
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'domain': [('type', '=', self.type)],
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'default_type': self.type}
        }

    @api.model
    def get_empty_list_help(self, help_message):
        """ This method returns the action helpers for the leads. If help is already provided
            on the action, the same is returned. Otherwise, we build the help message which
            contains the alias responsible for creating the lead (if available) and return it.
        """
        if not is_html_empty(help_message):
            return help_message

        help_title, sub_title = "", ""
        if self.env.context.get('default_type') == 'lead':
            help_title = _('Create a new lead')
        else:
            help_title = _('Create an opportunity to start playing with your pipeline.')
        alias_domain = [
            ('company_id', 'in', [self.env.company.id, False]),
            ('alias_id.alias_name', '!=', False),
            ('alias_id.alias_name', '!=', ''),
            ('alias_id.alias_model_id.model', '=', 'crm.lead'),
        ]
        # sort by use_leads, then by our membership of the team
        alias_records = self.env['crm.team'].search(alias_domain).sorted(
            lambda r: (r.use_leads, self.env.user in r.member_ids), reverse=True
        )
        alias_record = alias_records[0] if alias_records else None
        if alias_record and alias_record.alias_domain and alias_record.alias_name:
            sub_title = Markup(_('Use the <i>New</i> button, or send an email to %(email_link)s to test the email gateway.')) % {
                'email_link': Markup("<b><a href='mailto:%s'>%s</a></b>") % (alias_record.alias_email, alias_record.alias_email),
            }
        return super().get_empty_list_help(
            f'<p class="o_view_nocontent_smiling_face">{help_title}</p><p class="oe_view_nocontent_alias">{sub_title}</p>'
        )

    # ------------------------------------------------------------
    # BUSINESS
    # ------------------------------------------------------------

    def _assign_userless_lead_in_team(self, creation_source: str):
        """ Assign userless leads to their team's leader. """
        if not self._is_rule_based_assignment_activated() and self.team_id:
            for team_id, leads in self.filtered(lambda lead: not lead.user_id).grouped('team_id').items():
                if team_id.user_id:
                    leads.user_id = team_id.user_id
                    message = _('This new lead created by %(creation_source)s was automatically assigned to team leader %(user_name)s',
                        user_name=team_id.user_id.name,
                        creation_source=creation_source,
                    )
                    leads._message_log_batch(bodies={lead.id: message for lead in leads})

    def log_meeting(self, meeting):
        """ Log the meeting info with a link to it in the chatter
        :param record meeting: the meeting we want to log
        """
        if not meeting.duration:
            duration = _('unknown')
        else:
            duration = self.env['ir.qweb.field.duration'].value_to_html(meeting.duration, {'unit': 'hour'})
        meeting_usertime = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, meeting.start))
        meeting_time = Markup("<time datetime='%(meeting_start)s+00:00'>%(meeting_user_time)s</time>") % {
            'meeting_start': meeting.start,
            'meeting_user_time': meeting_usertime,
        }
        message = Markup("<p>%(meeting)s<br/>%(subject_string)s %(subject_link)s<br/>%(duration)s<p>") % {
            'meeting': _("Meeting scheduled at %s", meeting_time),
            'subject_string': _("Subject: "),
            'subject_link': meeting._get_html_link(),
            'duration': _("Duration: %s", duration),
        }
        return self.message_post(body=message)

    # ------------------------------------------------------------
    # MERGE AND CONVERT LEADS / OPPORTUNITIES
    # ------------------------------------------------------------

    def _merge_data(self, fnames=None):
        """ Prepare lead/opp data into a dictionary for merging. Different types
            of fields are processed in different ways:
                - text: all the values are concatenated
                - m2m and o2m: those fields aren't processed
                - m2o: the first not null value prevails (the other are dropped)
                - any other type of field: same as m2o

            :param fnames: list of fields to process
            :returns: contains the merged values of the new opportunity
            :rtype: dict
        """
        if fnames is None:
            fnames = self._merge_get_fields()
        fcallables = self._merge_get_fields_specific()
        address_values = self._merge_get_fields_address()

        # helpers
        def _get_first_not_null(attr, opportunities):
            value = False
            for opp in opportunities:
                if opp[attr]:
                    value = opp[attr].id if isinstance(opp[attr], models.BaseModel) else opp[attr]
                    break
            return value

        # process the field's values
        data = {}
        for field_name in fnames:
            field = self._fields.get(field_name)
            if field is None:
                continue

            fcallable = fcallables.get(field_name)
            if fcallable and callable(fcallable):
                data[field_name] = fcallable(field_name, self)
            elif field_name in address_values:
                data[field_name] = address_values[field_name]
            elif not fcallable and field.type in ('many2many', 'one2many'):
                continue
            else:
                data[field_name] = _get_first_not_null(field_name, self)  # take the first not null

        return data

    def merge_opportunity(self, user_id=False, team_id=False, auto_unlink=True):
        """
        Merge opportunities in one. Different cases of merge:

        - merge leads together = 1 new lead
        - merge at least 1 opp with anything else (lead or opp) = 1 new opp

        The resulting lead/opportunity will be the most important one (based on its confidence level)
        updated with values from other opportunities to merge.

        :param user_id: the id of the saleperson. If not given, will be determined by :meth:`_merge_data`.
        :param team_id: the id of the Sales Team. If not given, will be determined by :meth:`_merge_data`.
        :returns: crm.lead record resulting of th merge
        """
        return self._merge_opportunity(user_id=user_id, team_id=team_id, auto_unlink=auto_unlink)

    def _merge_opportunity(self, user_id=False, team_id=False, auto_unlink=True, max_length=5):
        """ Private merging method. This one allows to relax rules on record set
        length allowing to merge more than 5 opportunities at once if requested.
        This should not be called by action buttons.

        See ``merge_opportunity`` for more details. """
        if len(self.ids) <= 1:
            raise UserError(_('Select at least two Leads/Opportunities from the list to merge them.'))

        if max_length and len(self.ids) > max_length and not self.env.is_superuser():
            raise UserError(_("To prevent data loss, Leads and Opportunities can only be merged by groups of %(max_length)s.", max_length=max_length))

        opportunities = self._sort_by_confidence_level(reverse=True)

        # get SORTED recordset of head and tail, and complete list
        opportunities_head = opportunities[0]
        opportunities_tail = opportunities[1:]

        # merge all the sorted opportunity. This means the value of
        # the first (head opp) will be a priority.
        merged_data = opportunities._merge_data(self._merge_get_fields())

        # force value for saleperson and Sales Team
        if user_id:
            merged_data['user_id'] = user_id
        if team_id:
            merged_data['team_id'] = team_id

        merged_followers = opportunities_head._merge_followers(opportunities_tail)

        # log merge message
        opportunities_head._merge_log_summary(merged_followers, opportunities_tail)
        # merge other data (mail.message, attachments, ...) from tail into head
        opportunities_head._merge_dependences(opportunities_tail)

        # check if the stage is in the stages of the Sales Team. If not, assign the stage with the lowest sequence
        if merged_data.get('team_id'):
            team_stage_ids = self.env['crm.stage'].search(['|', ('team_ids', 'in', merged_data['team_id']), ('team_ids', '=', False)], order='sequence, id')
            if merged_data.get('stage_id') not in team_stage_ids.ids:
                merged_data['stage_id'] = team_stage_ids[0].id if team_stage_ids else False

        # write merged data into first opportunity; remove some keys if already
        # set on opp to avoid useless recomputes
        if 'user_id' in merged_data and opportunities_head.user_id.id == merged_data['user_id']:
            merged_data.pop('user_id')
        if 'team_id' in merged_data and opportunities_head.team_id.id == merged_data['team_id']:
            merged_data.pop('team_id')
        opportunities_head.write(merged_data)

        # delete tail opportunities
        # we use the SUPERUSER to avoid access rights issues because as the user had the rights to see the records it should be safe to do so
        if auto_unlink:
            opportunities_tail.sudo().unlink()

        return opportunities_head

    def _merge_get_fields_address(self):
        """The address fields are propagated as a whole.

        The address is taken from the lead with the most non-empty address field
        (sorted by highest rank if multiple lead have the same amount of non-empty
        fields).
        """
        source_lead = max(self, key=lambda lead: len(list(
            lead[field] for field in PARTNER_ADDRESS_FIELDS_TO_SYNC
            if lead[field]
        )))
        return {fname: source_lead[fname] for fname in PARTNER_ADDRESS_FIELDS_TO_SYNC}

    def _merge_get_fields_specific(self):
        return {
            'description': lambda fname, leads: '<br/><br/>'.join(desc for desc in leads.mapped('description') if not is_html_empty(desc)),
            'type': lambda fname, leads: 'opportunity' if any(lead.type == 'opportunity' for lead in leads) else 'lead',
            'priority': lambda fname, leads: max(priorities) if (priorities := leads.filtered('priority').mapped('priority')) else False,
            'tag_ids': lambda fname, leads: leads.mapped('tag_ids'),
            'lost_reason_id': lambda fname, leads:
                False if leads and leads[0].probability
                else next((lead.lost_reason_id for lead in leads if lead.lost_reason_id), False),
        }

    def _merge_get_fields(self):
        return (
            CRM_LEAD_FIELDS_TO_MERGE
            + list(self._merge_get_fields_specific().keys())
            + PARTNER_ADDRESS_FIELDS_TO_SYNC
        )

    def _merge_dependences(self, opportunities):
        """ Merge dependences (messages, attachments,activities, calendar events,
        ...). These dependences will be transfered to `self` considered as the
        master lead.

        :param opportunities : recordset of opportunities to transfer. Does not
          include `self` which is the target crm.lead being the result of the
          merge;
        """
        self.ensure_one()
        self._merge_dependences_history(opportunities)
        self._merge_dependences_attachments(opportunities)
        self._merge_dependences_calendar_events(opportunities)

    def _merge_dependences_history(self, opportunities):
        """ Move history from the given opportunities to the current one. `self`
        is the crm.lead record destination for message of `opportunities`.

        This method moves
          * messages
          * activities

        :param opportunities: see ``_merge_dependences``
        """
        self.ensure_one()
        # sudo usage: because we want to go through all messages, whatever the real ACLs
        # current user has on them
        for opportunity_su in opportunities.sudo():
            for message_su in opportunity_su.message_ids:
                if message_su.subject:
                    subject = _("From %(source_name)s: %(source_subject)s", source_name=opportunity_su.name, source_subject=message_su.subject)
                else:
                    subject = _("From %(source_name)s", source_name=opportunity_su.name)
                message_su.write({
                    'res_id': self.id,
                    'subject': subject,
                })
        opportunities.activity_ids.write({
            'res_id': self.id,
        })

        return True

    def _merge_dependences_attachments(self, opportunities):
        """ Move attachments of given opportunities to the current one `self`, and rename
            the attachments having same name than native ones.

        :param opportunities: see ``_merge_dependences``
        """
        self.ensure_one()

        all_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', 'in', opportunities.ids)
        ])

        for opportunity in opportunities:
            attachments = all_attachments.filtered(lambda attach: attach.res_id == opportunity.id)
            for attachment in attachments:
                attachment.write({
                    'res_id': self.id,
                    'name': _("%(attach_name)s (from %(lead_name)s)",
                              attach_name=attachment.name,
                              lead_name=opportunity.name[:20]
                             )
                })
        return True

    def _merge_dependences_calendar_events(self, opportunities):
        """ Move calender.event from the given opportunities to the current one. `self` is the
            crm.lead record destination for event of `opportunities`.
        :param opportunities: see ``merge_dependences``
        """
        self.ensure_one()
        meetings = self.env['calendar.event'].search([('opportunity_id', 'in', opportunities.ids)])
        return meetings.write({
            'res_id': self.id,
            'opportunity_id': self.id,
        })

    def _merge_followers(self, opportunities):
        """Add the followers into the destination lead if they post a message in the last 30 days.

        :param opportunities : Record<crm.lead> of opportunities to transfer
        :return: {old_lead_id: Record<mail.followers>} Followers which have been added in
            the destination lead grouped by source lead ID.
        """
        self.ensure_one()

        self.env['mail.message'].flush_model()
        self.env['mail.followers'].flush_model()

        # Get the active followers (followers whose partner post a message on the
        # leads in the last 30 days) which should be moved on the destination lead
        self.env.cr.execute(
            '''
            SELECT MAX(mf.id) AS id
              FROM mail_followers AS mf
              JOIN mail_message AS mm
                ON mm.author_id = mf.partner_id
               AND mm.res_id = mf.res_id
               AND mm.model = 'crm.lead'
               AND mm.date > NOW() - INTERVAL '30 DAY'
                   /* Check if the partner is already
                      following the destination lead */
         LEFT JOIN mail_followers AS destf
                ON destf.res_model = 'crm.lead'
               AND destf.res_id = %(lead_id)s
               AND destf.partner_id = mf.partner_id
                   /* Select only once each partner
                      to not create duplicated followers */
             WHERE mf.res_model = 'crm.lead'
               AND mf.res_id IN %(lead_ids)s
               AND destf IS NULL
          GROUP BY mf.partner_id
            ''',
            {'lead_ids': tuple(opportunities.ids), 'lead_id': self.id},
        )
        followers_to_update = [r[0] for r in self.env.cr.fetchall()]
        followers_to_update = self.env['mail.followers'].browse(followers_to_update).sudo()
        followers_by_old_lead = dict(groupby(followers_to_update, lambda f: f.res_id))
        followers_to_update.write({'res_id': self.id})
        return followers_by_old_lead

    def _merge_log_summary(self, merged_followers, opportunities_tail):
        """Log the merge message on the lead."""
        self.ensure_one()
        self.message_post_with_source(
            "crm.crm_lead_merge_summary",
            render_values={
                "merged_followers": merged_followers,
                "opportunities": opportunities_tail,
                "is_html_empty": is_html_empty,
            },
            subtype_xmlid='mail.mt_note',
        )

    def _format_properties(self):
        """Format the properties to build the merge message.

        Return a list of dict containing the label, and a value key if there's only
        one value, or a "values" key if we have multiple values (e.g. many2many, tags).

        E.G.
            [{
                'label': 'My Partner',
                'value': 'Alice',
            }, {
                'label': 'My Partners',
                'values': [
                    {'name': 'Alice'},
                    {'name': 'Bob'},
                ],
            }, {
                'label': 'My Tags',
                'values': [
                    {'name': 'A', 'color': 1},
                    {'name': 'C', 'color': 3},
                ],
            }]
        """
        self.ensure_one()
        # read to have the display names already in the value
        properties = self.read(['lead_properties'])[0]['lead_properties']

        formatted = []
        for definition in properties:
            label = definition.get('string')
            value = definition.get('value')
            property_type = definition['type']
            if not value and property_type != 'boolean':
                continue

            property_dict = {'label': label}
            if property_type == 'boolean':
                property_dict['value'] = _('Yes') if value else _('No')
            elif value and property_type == 'many2one':
                property_dict['value'] = value[1]
            elif value and property_type == 'many2many':
                # show many2many in badge
                property_dict['values'] = [{'name': rec[1]} for rec in value]
            elif value and property_type in ['selection', 'tags']:
                # retrieve the option label from the value
                options = {
                    option[0]: option[1:]
                    for option in (definition.get(property_type) or [])
                }
                if property_type == 'selection':
                    value = options.get(value)
                    property_dict['value'] = value[0] if value else None
                else:
                    property_dict['values'] = [{
                        'name': options[tag][0],
                        'color': options[tag][1],
                        } for tag in value if tag in options
                    ]
            else:
                property_dict['value'] = value

            formatted.append(property_dict)

        return formatted

    # CONVERT
    # ----------------------------------------------------------------------

    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        new_team_id = team_id if team_id else self.team_id.id
        upd_values = {
            'type': 'opportunity',
            'date_conversion': self.env.cr.now(),
        }
        if customer != self.partner_id:
            upd_values['partner_id'] = customer.id if customer else False
        if not self.stage_id:
            stage = self._stage_find(team_id=new_team_id)
            upd_values['stage_id'] = stage.id
        return upd_values

    def convert_opportunity(self, partner, user_ids=False, team_id=False):
        customer = partner if partner else self.env['res.partner']
        for lead in self:
            if not lead.active or lead.won_status == 'won':
                continue
            vals = lead._convert_opportunity_data(customer, team_id)
            lead.write(vals)

        if user_ids or team_id:
            self._handle_salesmen_assignment(user_ids=user_ids, team_id=team_id)

        return True

    def _handle_partner_assignment(self, force_partner_id=False, create_missing=True, with_parent=None):
        """ Update customer (partner_id) of leads. Purpose is to set the same
        partner on most leads; either through a newly created partner either
        through a given partner_id.

        :param int force_partner_id: if set, update all leads to that customer;
        :param create_missing: for leads without customer, create a new one
          based on lead information;
        :param with_parent: if set, create the new partner with the given parent
        """
        for lead in self:
            if force_partner_id:
                lead.partner_id = force_partner_id
            if not lead.partner_id and create_missing:
                partner = lead._create_customer(with_parent=with_parent)
                lead.partner_id = partner.id

    def _handle_salesmen_assignment(self, user_ids=False, team_id=False):
        """ Assign salesmen and salesteam to a batch of leads.  If there are more
        leads than salesmen, these salesmen will be assigned in round-robin. E.g.
        4 salesmen (S1, S2, S3, S4) for 6 leads (L1, L2, ... L6) will assigned as
        following: L1 - S1, L2 - S2, L3 - S3, L4 - S4, L5 - S1, L6 - S2.

        :param list user_ids: salesmen to assign
        :param int team_id: salesteam to assign
        """
        update_vals = {'team_id': team_id} if team_id else {}
        if not user_ids and team_id:
            self.write(update_vals)
        else:
            lead_ids = self.ids
            steps = len(user_ids)
            # pass 1 : lead_ids[0:6:3] = [L1,L4]
            # pass 2 : lead_ids[1:6:3] = [L2,L5]
            # pass 3 : lead_ids[2:6:3] = [L3,L6]
            # ...
            for idx in range(0, steps):
                subset_ids = lead_ids[idx:len(lead_ids):steps]
                update_vals['user_id'] = user_ids[idx]
                self.env['crm.lead'].browse(subset_ids).write(update_vals)

    # ------------------------------------------------------------
    # MERGE / CONVERT TOOLS
    # ---------------------------------------------------------

    # CLASSIFICATION TOOLS
    # --------------------------------------------------

    def _get_lead_duplicates(self, partner=None, email=None, include_lost=False):
        """ Search for leads that seem duplicated based on partner / email.

        :param partner : optional customer when searching duplicated
        :param email: email (possibly formatted) to search
        :param boolean include_lost: if True, search includes archived opportunities
          (still only active leads are considered). If False, search for active
          and not won leads and opportunities;
        """
        if not email and not partner:
            return self.env['crm.lead']

        domain = []
        normalized_emails = email_normalize_all(email)
        if normalized_emails:
            domain.append(('email_normalized', 'in', normalized_emails))
        if partner:
            domain.append(('partner_id', '=', partner.id))

        if not domain:
            return self.env['crm.lead']

        domain = ['|'] * (len(domain) - 1) + domain
        if include_lost:
            # include lost means archived opportunities are allowed, if lost
            domain += [('won_status', '!=', 'won'), '|', ('type', '=', 'opportunity'), ('active', '=', True)]
        else:
            # always filter out archived, those are not actionable anymore
            domain += [('won_status', '=', 'pending'), ('active', '=', True)]

        return self.with_context(active_test=False).search(domain)

    def _sort_by_confidence_level(self, reverse=False):
        """ Sorting the leads/opps according to the confidence level to it
        being won. It is sorted following this incremental heuristics :

          * "not lost" first (inactive leads are lost); normally all leads
            should be active but in case lost one, they are always last.
            Inactive opportunities are considered as valid;
          * opportunity is more reliable than a lead which is a pre-stage
            used mainly for first classification;
          * stage sequence: the higher the better as it indicates we are moving
            towards won stage;
          * probability: the higher the better as it is more likely to be won;
          * ID: the higher the better when all other parameters are equal. We
            consider newer leads to be more reliable;
        """
        def opps_key(opportunity):
            return opportunity.type == 'opportunity' or opportunity.active,  \
                opportunity.type == 'opportunity', \
                opportunity.stage_id.sequence, \
                opportunity.probability, \
                -opportunity._origin.id

        return self.sorted(key=opps_key, reverse=reverse)

    # CUSTOMER TOOLS
    # --------------------------------------------------

    def _find_matching_partner(self):
        """ Try to find a matching partner with available information on the
        lead, using currently customer's email

        :return: partner browse record
        """
        self.ensure_one()
        partner = self.partner_id
        if not partner and (self.email_normalized or self.email_from):
            partner = self._partner_find_from_emails_single(
                [self.email_normalized or self.email_from],
                no_create=True,
            )
        return partner

    def _create_customer(self, with_parent=None):
        """ Create a partner from lead data and link it to the lead.

        :param with_parent: if set, create the new partner with the given parent
        :return: newly-created partner browse record
        """
        Partner = self.env['res.partner']
        contact_name = self.contact_name
        if not contact_name:
            contact_name = parse_contact_from_email(self.email_from)[0] if self.email_from else False

        if with_parent:
            partner_company = with_parent
        elif self.partner_name:
            partner_company = Partner.create(self._prepare_customer_values(self.partner_name, is_company=True))
        elif self.partner_id:
            partner_company = self.partner_id
        else:
            partner_company = self.env['res.partner']

        if contact_name:
            return Partner.create(self._prepare_customer_values(contact_name, is_company=False, parent_id=partner_company.id))

        if partner_company:
            return partner_company
        return Partner.create(self._prepare_customer_values(self.name, is_company=False))

    def _get_customer_information(self):
        email_keys_to_values = super()._get_customer_information()

        for lead in self:
            email_key = lead.email_normalized or lead.email_from
            # do not fill Falsy with random data, unless monorecord (= always correct)
            if not email_key and len(self) > 1:
                continue
            values = email_keys_to_values.setdefault(email_key, {})
            contact_name = lead.contact_name or parse_contact_from_email(lead.email_from)[0] or lead.email_from
            is_company = bool(lead.partner_name) and contact_name == lead.partner_name
            # Note that we don't attempt to create the parent company even if partner name is set
            values.update({
                key: val for key, val in lead._prepare_customer_values(
                    contact_name, is_company=is_company, parent_id=False
                ).items() if val and key != 'email'  # don't force email used as criterion
            })
            values['is_company'] = is_company
            if not is_company and lead.commercial_partner_id:
                values['parent_id'] = lead.commercial_partner_id.id
                values.pop('company_name', None)
        return email_keys_to_values

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        """ Extract data from lead to create a partner.

        :param partner_name : future name of the partner
        :param is_company : True if the partner is a company
        :param parent_id : id of the parent partner (False if no parent)

        :return: dictionary of values to give at res_partner.create()
        """
        email_parts = tools.email_split(self.email_from)
        res = {
            'name': partner_name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'phone': self.phone,
            'email': email_parts[0] if email_parts else False,
            'function': self.function,
            # address
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            # company / hierarchy
            'parent_id': parent_id,
            'is_company': is_company,
            'company_name': not is_company and not parent_id and self.partner_name,
            'type': 'contact'
        }
        if self.lang_id.active:
            res['lang'] = self.lang_id.code
        return res

    def _is_rule_based_assignment_activated(self):
        """ Returns whether a rule-based assignment method is activated (cron-enabled or manually-ran).
        """
        return self.env['ir.config_parameter'].sudo().get_param('crm.lead.auto.assignment', False)

    # ------------------------------------------------------------
    # MAILING
    # ------------------------------------------------------------

    def _creation_subtype(self):
        return self.env.ref('crm.mt_lead_create')

    def _creation_message(self):
        self.ensure_one()
        if self.team_id:
            return _('A new lead has been created for the team "%(team_name)s".', team_name=self.team_id.display_name)
        return _('A new lead has been created and is not assigned to any team.')

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values and self.won_status == 'won':
            return self.env.ref('crm.mt_lead_won')
        elif 'lost_reason_id' in init_values and self.lost_reason_id:
            return self.env.ref('crm.mt_lead_lost')
        elif 'stage_id' in init_values:
            return self.env.ref('crm.mt_lead_stage')
        elif 'won_status' in init_values and self.won_status != 'lost':
            return self.env.ref('crm.mt_lead_restored')
        elif 'won_status' in init_values and self.won_status == 'lost':
            return self.env.ref('crm.mt_lead_lost')
        return super()._track_subtype(init_values)

    def _notify_by_email_prepare_rendering_context(self, message, msg_vals=False, model_description=False,
                                                   force_email_company=False, force_email_lang=False,
                                                   force_record_name=False):
        render_context = super()._notify_by_email_prepare_rendering_context(
            message, msg_vals=msg_vals, model_description=model_description,
            force_email_company=force_email_company, force_email_lang=force_email_lang,
            force_record_name=force_record_name,
        )
        if self.date_deadline:
            render_context['subtitles'].append(
                _('Deadline: %s', self.date_deadline.strftime(get_lang(self.env).date_format)))
        return render_context

    def _notify_get_reply_to(self, default=None, author_id=False):
        # Override to set alias of lead and opportunities to their sales team if any
        aliases = self.mapped('team_id').sudo()._notify_get_reply_to(default=default, author_id=author_id)
        res = {lead.id: aliases.get(lead.team_id.id) for lead in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(super(CrmLead, leftover)._notify_get_reply_to(default=default, author_id=author_id))
        return res

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set an user as responsible. We prefer that
        # assignment is done automatically (scoring) or manually. Otherwise it
        # would always be root (gateway user). It also allows to exclude portal
        # and public users.
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('priority') in dict(crm_stage.AVAILABLE_PRIORITIES):
            defaults['priority'] = msg_dict.get('priority')
        defaults.update(custom_values)

        new_lead = super().message_new(msg_dict, custom_values=defaults)
        new_lead._assign_userless_lead_in_team(_('incoming email'))
        return new_lead

    def _message_post_after_hook(self, message, msg_vals):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(
                lambda partner: partner.email == self.email_from or (self.email_normalized and partner.email_normalized == self.email_normalized)
            )
            if new_partner:
                if new_partner[0].email_normalized:
                    email_domain = ('email_normalized', '=', new_partner[0].email_normalized)
                else:
                    email_domain = ('email_from', '=', new_partner[0].email)
                self.search([
                    ('partner_id', '=', False), email_domain, ('stage_id.fold', '=', False)
                ]).write({'partner_id': new_partner[0].id})
        return super()._message_post_after_hook(message, msg_vals)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Leads & Opportunities'),
            'template': '/crm/static/xls/crm_lead.xls'
        }]

    # ------------------------------------------------------------
    # PLS
    # ------------------------------------------------------------
    # Predictive lead scoring is computing the lead probability, based on won and lost leads from the past
    # Each won/lost lead increments a frequency table, where we store, for each field/value couple, the number of
    # won and lost leads.
    #   E.g. : A won lead from Belgium will increase the won count of the frequency country_id='Belgium' by 1.
    # The frequencies are split by team_id, so each team has its own frequencies environment. (Team A doesn't impact B)
    # There are two main ways to build the frequency table:
    #   - Live Increment: At each Won/lost, we increment directly the frequencies based on the lead values.
    #       Done right BEFORE writing the lead as won or lost.
    #       We consider a lead that will be marked as won or lost.
    #       Used each time a lead is won or lost, to ensure frequency table is always up to date
    #   - One shot Rebuild: empty the frequency table and rebuild it from scratch, based on every already won/lost leads
    #       Done during cron process.
    #       We consider all the leads that have been already won or lost.
    #       Used in one shot, when modifying the criteria to take into account (fields or reference date)

    # ---------------------------------
    # PLS: Probability Computation
    # ---------------------------------
    def _pls_get_naive_bayes_probabilities(self, batch_mode=False, is_tooltip=False):
        """
        In machine learning, naive Bayes classifiers (NBC) are a family of simple "probabilistic classifiers" based on
        applying Bayes theorem with strong (naive) independence assumptions between the variables taken into account.
        E.g: will TDE eat m&m's depending on his sleep status, the amount of work he has and the fullness of his stomach?
        As we use experience to compute the statistics, every day, we will register the variables state + the result.
        As the days pass, we will be able to determine, with more and more precision, if TDE will eat m&m's
        for a specific combination :
            - did sleep very well, a lot of work and stomach full > Will never happen !
            - didn't sleep at all, no work at all and empty stomach > for sure !
        Following Bayes' Theorem: the probability that an event occurs (to win) under certain conditions is proportional
        to the probability to win under each condition separately and the probability to win. We compute a 'Win score'
        -> P(Won | A∩B) ∝ P(A∩B | Won)*P(Won) OR S(Won | A∩B) = P(A∩B | Won)*P(Won)
        To compute a percentage of probability to win, we also compute the 'Lost score' that is proportional to the
        probability to lose under each condition separately and the probability to lose.
        -> Probability =  S(Won | A∩B) / ( S(Won | A∩B) + S(Lost | A∩B) )
        See https://www.youtube.com/watch?v=CPqOCI0ahss can help to get a quick and simple example.
        One issue about NBC is when a event occurence is never observed.
        E.g: if when TDE has an empty stomach, he always eat m&m's, than the "not eating m&m's when empty stomach' event
        will never be observed.
        This is called 'zero frequency' and that leads to division (or at least multiplication) by zero.
        To avoid this, we add 0.1 in each frequency. With few data, the computation is than not really realistic.
        The more we have records to analyse, the more the estimation will be precise.

        :param bool is_tooltip: If true, method recomputes the probability of self, that should be a singleton, and
            also returns a dict containing probability, and a list of all (score, field, value) triplets for all value of
            PLS fields that impact the computation of the probability. Score is a simple value that indicates whether the
            impact is positive (>.5) or negative (<.5). See method prepare_pls_tooltip_data, or test_pls_tooltip_data for
            more details

        :return: probability in percent (and rounded at 2 decimals) that the lead will be won at the current stage.
        """
        lead_probabilities = {}
        if not self:
            return lead_probabilities

        # Initialize tooltip data. A returned 0.00 probability means computation was not possible.
        tooltip_data = {}
        if is_tooltip:
            self.ensure_one()
            tooltip_data = {
                'probability': 0.0,
                'scores': [],
            }

        # Get all leads values, no matter the team_id
        domain = []
        if batch_mode:
            domain = [
                ('active', '=', True),
                ('id', 'in', self.ids),
                ('won_status', '=', 'pending'),
            ]
        leads_values_dict = self._pls_get_lead_pls_values(domain=domain)

        if not leads_values_dict:
            return lead_probabilities

        # Get unique couples to search in frequency table and won leads.
        leads_fields = set()  # keep unique fields, as a lead can have multiple tag_ids
        won_leads = set()
        won_stage_ids = self.env['crm.stage'].search([('is_won', '=', True)]).ids
        for lead_id, values in leads_values_dict.items():
            for field, value in values['values']:
                if field == 'stage_id' and value in won_stage_ids:
                    won_leads.add(lead_id)
                leads_fields.add(field)
        leads_fields = sorted(leads_fields)
        # get all variable related records from frequency table, no matter the team_id
        frequencies = self.env['crm.lead.scoring.frequency'].search([('variable', 'in', list(leads_fields))], order="team_id asc, id")

        # get all team_ids from frequencies
        frequency_teams = frequencies.mapped('team_id')
        frequency_team_ids = [team.id for team in frequency_teams]

        # restrict to frequencies of lead team if any exist.
        if is_tooltip and self.team_id & frequency_teams:
            frequency_team_ids = [self.team_id.id]
            frequencies = frequencies.filtered(
                lambda frequency: frequency.team_id & self.team_id
            )

        # 1. Compute each variable value count individually
        # regroup each variable to be able to compute their own probabilities
        # As all the variable does not enter into account (as we reject unset values in the process)
        # each value probability must be computed only with their own variable related total count
        # special case: for lead for which team_id is not in frequency table or lead with no team_id,
        # we consider all the records, independently from team_id (this is why we add a result[-1])
        result = dict((team_id, dict((field, dict(won_total=0, lost_total=0)) for field in leads_fields)) for team_id in frequency_team_ids)
        result[-1] = dict((field, dict(won_total=0, lost_total=0)) for field in leads_fields)
        for frequency in frequencies:
            field = frequency['variable']
            value = frequency['value']  # This is always a string

            # To avoid that a tag take too much importance if its subset is too small,
            # we ignore the tag frequencies if we have less than 50 won or lost for this tag.
            if field == 'tag_id' and (frequency['won_count'] + frequency['lost_count']) < 50:
                continue

            if frequency.team_id:
                team_result = result[frequency.team_id.id]
                team_result[field][value] = {'won': frequency['won_count'], 'lost': frequency['lost_count']}
                team_result[field]['won_total'] += frequency['won_count']
                team_result[field]['lost_total'] += frequency['lost_count']

            if value not in result[-1][field]:
                result[-1][field][value] = {'won': 0, 'lost': 0}
            result[-1][field][value]['won'] += frequency['won_count']
            result[-1][field][value]['lost'] += frequency['lost_count']
            result[-1][field]['won_total'] += frequency['won_count']
            result[-1][field]['lost_total'] += frequency['lost_count']

        # Get all won, lost and total count for all records in frequencies per team_id
        for team_id in result:
            result[team_id]['team_won'], \
            result[team_id]['team_lost'], \
            result[team_id]['team_total'] = self._pls_get_won_lost_total_count(result[team_id])

        save_team_id = None
        p_won, p_lost = 1, 1
        for lead_id, lead_values in leads_values_dict.items():
            # if stage_id is null, return 0 and bypass computation
            lead_fields = [value[0] for value in lead_values.get('values', [])]
            if not 'stage_id' in lead_fields:
                lead_probabilities[lead_id] = 0
                continue
            # if lead stage is won, return 100
            elif lead_id in won_leads:
                lead_probabilities[lead_id] = 100
                continue

            # team_id not in frequency Table -> convert to -1
            lead_team_id = lead_values['team_id'] if lead_values['team_id'] in result else -1
            if lead_team_id != save_team_id:
                save_team_id = lead_team_id
                team_won = result[save_team_id]['team_won']
                team_lost = result[save_team_id]['team_lost']
                team_total = result[save_team_id]['team_total']
                # if one count = 0, we cannot compute lead probability
                if not team_won or not team_lost:
                    continue
                p_won = team_won / team_total
                p_lost = team_lost / team_total

            # 2. Compute won and lost score using each variable's individual probability
            s_lead_won, s_lead_lost = p_won, p_lost
            for field, value in lead_values['values']:
                field_result = result.get(save_team_id, {}).get(field)
                value = value.origin if hasattr(value, 'origin') else value
                value_result = field_result.get(str(value)) if field_result else False
                if value_result:
                    total_won = team_won if field == 'stage_id' else field_result['won_total']
                    total_lost = team_lost if field == 'stage_id' else field_result['lost_total']
                    # if one count = 0, we cannot compute lead probability
                    if not total_won or not total_lost:
                        continue
                    p_field_value_won = value_result['won'] / total_won
                    p_field_value_lost = value_result['lost'] / total_lost
                    s_lead_won *= p_field_value_won
                    s_lead_lost *= p_field_value_lost

                    if is_tooltip:
                        score = (
                            1 - p_field_value_lost if field == 'stage_id'
                            else p_field_value_won / (p_field_value_won + p_field_value_lost)
                        )
                        tooltip_data['scores'].append((score, field, value))
            # 3. Compute Probability to win
            probability = s_lead_won / (s_lead_won + s_lead_lost)
            lead_probabilities[lead_id] = min(max(round(100 * probability, 2), 0.01), 99.99)

        if tooltip_data and self.id in lead_probabilities:
            tooltip_data['probability'] = lead_probabilities[self.id]

        return lead_probabilities, tooltip_data

    # ---------------------------------
    # PLS: Live Increment
    # ---------------------------------
    def _pls_increment_frequencies(self, from_state=None, to_state=None):
        """
        When losing or winning a lead, this method is called to increment each PLS parameter related to the lead
        in won_count (if won) or in lost_count (if lost).

        This method is also used when reactivating a mistakenly lost lead (using the decrement argument).
        In this case, the lost count should be de-increment by 1 for each PLS parameter linked to the lead.

        Live increment must be done before writing the new values because we need to know the state change (from and to).
        This would not be an issue for the reach won or reach lost as we just need to increment the frequencies with the
        final state of the lead.
        This issue is when the lead leaves a closed state because once the new values have been writen, we do not know
        what was the previous state that we need to decrement.
        This is why 'is_won' and 'decrement' parameters are used to describe the from / to change of its state.
        """
        new_frequencies_by_team, existing_frequencies_by_team = self._pls_prepare_update_frequency_table(target_state=from_state or to_state)

        # update frequency table
        self._pls_update_frequency_table(new_frequencies_by_team, 1 if to_state else -1,
                                         existing_frequencies_by_team=existing_frequencies_by_team)

    # ---------------------------------
    # PLS: One shot rebuild
    # ---------------------------------
    def _cron_update_automated_probabilities(self):
        """ This cron will :
          - rebuild the lead scoring frequency table
          - recompute all the automated_probability and align probability if both were aligned
        """
        cron_start_date = datetime.now()
        self._rebuild_pls_frequency_table()
        self._update_automated_probabilities()
        _logger.info("Predictive Lead Scoring : Cron duration = %d seconds" % ((datetime.now() - cron_start_date).total_seconds()))

    def _rebuild_pls_frequency_table(self):
        # Clear the frequencies table (in sql to speed up the cron)
        try:
            self.browse().check_access('unlink')
        except AccessError:
            raise UserError(_("You don't have the access needed to run this cron."))
        else:
            self.env.cr.execute('TRUNCATE TABLE crm_lead_scoring_frequency')

        new_frequencies_by_team, unused = self._pls_prepare_update_frequency_table(rebuild=True)
        # update frequency table
        self._pls_update_frequency_table(new_frequencies_by_team, 1)

        _logger.info("Predictive Lead Scoring : crm.lead.scoring.frequency table rebuilt")

    def _update_automated_probabilities(self):
        """ Recompute all the automated_probability (and align probability if both were aligned) for all the leads
        that are active (not won, nor lost).

        For performance matter, as there can be a huge amount of leads to recompute, this cron proceed by batch.
        Each batch is performed into its own transaction, in order to minimise the lock time on the lead table
        (and to avoid complete lock if there was only 1 transaction that would last for too long -> several minutes).
        If a concurrent update occurs, it will simply be put in the queue to get the lock.
        """
        pls_start_date = self._pls_get_safe_start_date()
        if not pls_start_date:
            return

        # 1. Get all the leads to recompute created after pls_start_date that are nor won nor lost
        pending_lead_domain = [
            ('stage_id', '!=', False),
            ('create_date', '>=', pls_start_date),
            ('won_status', '=', 'pending'),
        ]
        leads_to_update = self.env['crm.lead'].search(pending_lead_domain)
        leads_to_update_count = len(leads_to_update)

        # 2. Compute by batch to avoid memory error
        lead_probabilities = {}
        for i in range(0, leads_to_update_count, PLS_COMPUTE_BATCH_STEP):
            leads_to_update_part = leads_to_update[i:i + PLS_COMPUTE_BATCH_STEP]
            batch_probabilites, _unused = leads_to_update_part._pls_get_naive_bayes_probabilities(batch_mode=True)
            lead_probabilities.update(batch_probabilites)
        _logger.info("Predictive Lead Scoring : New automated probabilities computed")

        # 3. Group by new probability to reduce server roundtrips when executing the update
        probability_leads = defaultdict(list)
        for lead_id, probability in sorted(lead_probabilities.items()):
            probability_leads[probability].append(lead_id)

        # 4. Update automated_probability (+ probability if both were equal)
        update_sql = """UPDATE crm_lead
                        SET automated_probability = %s,
                            probability = CASE WHEN (probability = automated_probability OR probability is null)
                                               THEN (%s)
                                               ELSE (probability)
                                          END
                        WHERE id in %s"""

        # Update by a maximum number of leads at the same time, one batch by transaction :
        # - avoid memory errors
        # - avoid blocking the table for too long with a too big transaction
        transactions_count, transactions_failed_count = 0, 0
        cron_update_lead_start_date = datetime.now()
        auto_commit = not modules.module.current_test
        self.flush_model()
        for probability, probability_lead_ids in probability_leads.items():
            for lead_ids_current in tools.split_every(PLS_UPDATE_BATCH_STEP, probability_lead_ids):
                transactions_count += 1
                try:
                    self.env.cr.execute(update_sql, (probability, probability, tuple(lead_ids_current)))
                    # auto-commit except in testing mode
                    if auto_commit:
                        self.env.cr.commit()
                except Exception as e:
                    _logger.warning("Predictive Lead Scoring : update transaction failed. Error: %s" % e)
                    transactions_failed_count += 1
        self.invalidate_model()

        _logger.info(
            "Predictive Lead Scoring : All automated probabilities updated (%d leads / %d transactions (%d failed) / %d seconds)" % (
                leads_to_update_count,
                transactions_count,
                transactions_failed_count,
                (datetime.now() - cron_update_lead_start_date).total_seconds(),
            )
        )

    # ---------------------------------
    # PLS: Common parts for both mode
    # ---------------------------------
    def _pls_prepare_update_frequency_table(self, rebuild=False, target_state=False):
        """
        This method is common to Live Increment or Full Rebuild mode, as it shares the main steps.
        This method will prepare the frequency dict needed to update the frequency table:
            - New frequencies: frequencies that we need to add in the frequency table.
            - Existing frequencies: frequencies that are already in the frequency table.
        In rebuild mode, only the new frequencies are needed as existing frequencies are truncated.
        For each team, each dict contains the frequency in won and lost for each field/value couple
        of the target leads.
        Target leads are :
            - in Live increment mode : given ongoing leads (self)
            - in Full rebuild mode : all the closed (won and lost) leads in the DB.
        During the frequencies update, with both new and existing frequencies, we can split frequencies to update
        and frequencies to add. If a field/value couple already exists in the frequency table, we just update it.
        Otherwise, we need to insert a new one.
        """
        # Keep eligible leads
        pls_start_date = self._pls_get_safe_start_date()
        if not pls_start_date:
            return {}, {}

        if rebuild:  # rebuild will treat every closed lead in DB, increment will treat current ongoing leads
            pls_leads = self
        else:
            # Only treat leads created after the PLS start Date
            pls_leads = self.filtered(
                lambda lead: fields.Date.to_date(pls_start_date) <= fields.Date.to_date(lead.create_date))
            if not pls_leads:
                return {}, {}

        # Extract target leads values
        if rebuild:  # rebuild is ok
            domain = [
                ('create_date', '>=', pls_start_date),
                ('won_status', 'in', ['lost', 'won']),
              ]
            team_ids = self.env['crm.team'].with_context(active_test=False).search([]).ids + [0]  # If team_id is unset, consider it as team 0
        else:  # increment
            domain = [('id', 'in', pls_leads.ids)]
            team_ids = pls_leads.mapped('team_id').ids + [0]

        leads_values_dict = pls_leads._pls_get_lead_pls_values(domain=domain)

        # split leads values by team_id
        # get current frequencies related to the target leads
        leads_frequency_values_by_team = dict((team_id, []) for team_id in team_ids)
        leads_pls_fields = set()  # ensure to keep each field unique (can have multiple tag_id leads_values_dict)
        for values in leads_values_dict.values():
            team_id = values.get('team_id', 0)  # If team_id is unset, consider it as team 0
            lead_frequency_values = {'count': 1}
            for field, value in values['values']:
                if field != "probability":  # was added to lead values in batch mode to know won/lost state, but is not a pls fields.
                    leads_pls_fields.add(field)
                else:  # extract lead probability - needed to increment tag_id frequency. (proba always before tag_id)
                    lead_probability = value
                if field == 'tag_id':  # handle tag_id separatelly (as in One Shot rebuild mode)
                    leads_frequency_values_by_team[team_id].append({field: value, 'count': 1, 'probability': lead_probability})
                else:
                    lead_frequency_values[field] = value
            leads_frequency_values_by_team[team_id].append(lead_frequency_values)
        leads_pls_fields = sorted(leads_pls_fields)

        # get new frequencies
        new_frequencies_by_team = {}
        for team_id in team_ids:
            # prepare fields and tag values for leads by team
            new_frequencies_by_team[team_id] = self._pls_prepare_frequencies(
                leads_frequency_values_by_team[team_id], leads_pls_fields, target_state=target_state)

        # get existing frequencies
        existing_frequencies_by_team = {}
        if not rebuild:  # there is no existing frequency in rebuild mode as they were all deleted.
            # read all fields to get everything in memory in one query (instead of having query + prefetch)
            existing_frequencies = self.env['crm.lead.scoring.frequency'].search_read(
                ['&', ('variable', 'in', leads_pls_fields),
                      '|', ('team_id', 'in', pls_leads.mapped('team_id').ids), ('team_id', '=', False)])
            for frequency in existing_frequencies:
                team_id = frequency['team_id'][0] if frequency.get('team_id') else 0
                if team_id not in existing_frequencies_by_team:
                    existing_frequencies_by_team[team_id] = dict((field, {}) for field in leads_pls_fields)

                existing_frequencies_by_team[team_id][frequency['variable']][frequency['value']] = {
                    'frequency_id': frequency['id'],
                    'won': frequency['won_count'],
                    'lost': frequency['lost_count']
                }

        return new_frequencies_by_team, existing_frequencies_by_team

    def _pls_update_frequency_table(self, new_frequencies_by_team, step, existing_frequencies_by_team=None):
        """ Create / update the frequency table in a cross company way, per team_id"""
        values_to_update = {}
        values_to_create = []
        if not existing_frequencies_by_team:
            existing_frequencies_by_team = {}
        # build the create multi + frequencies to update
        for team_id, new_frequencies in new_frequencies_by_team.items():
            for field, value in new_frequencies.items():
                # frequency already present ?
                current_frequencies = existing_frequencies_by_team.get(team_id, {})
                for param, result in value.items():
                    current_frequency_for_couple = current_frequencies.get(field, {}).get(param, {})
                    # If frequency already present : UPDATE IT
                    if current_frequency_for_couple:
                        new_won = current_frequency_for_couple['won'] + (result['won'] * step)
                        new_lost = current_frequency_for_couple['lost'] + (result['lost'] * step)
                        # ensure to have always positive frequencies
                        values_to_update[current_frequency_for_couple['frequency_id']] = {
                            'won_count': new_won if new_won > 0 else 0.1,
                            'lost_count': new_lost if new_lost > 0 else 0.1
                        }
                        continue

                    # Else, CREATE a new frequency record.
                    # We add + 0.1 in won and lost counts to avoid zero frequency issues
                    # should be +1 but it weights too much on small recordset.
                    values_to_create.append({
                        'variable': field,
                        'value': param,
                        'won_count': result['won'] + 0.1,
                        'lost_count': result['lost'] + 0.1,
                        'team_id': team_id if team_id else None  # team_id = 0 means no team_id
                    })

        LeadScoringFrequency = self.env['crm.lead.scoring.frequency'].sudo()
        for frequency_id, values in values_to_update.items():
            LeadScoringFrequency.browse(frequency_id).write(values)

        if values_to_create:
            LeadScoringFrequency.create(values_to_create)

    # ---------------------------------
    # Utility Tools for PLS
    # ---------------------------------

    # PLS:  Config Parameters
    # ---------------------
    def _pls_get_safe_start_date(self):
        """ As config_parameters does not accept Date field,
            we get directly the date formated string stored into the Char config field,
            as we directly use this string in the sql queries.
            To avoid sql injections when using this config param,
            we ensure the date string can be effectively a date."""
        str_date = self.env['ir.config_parameter'].sudo().get_param('crm.pls_start_date')
        if not fields.Date.to_date(str_date):
            return False
        return str_date

    def _pls_get_safe_fields(self):
        """ As config_parameters does not accept M2M field,
            we the fields from the formated string stored into the Char config field.
            To avoid sql injections when using that list, we return only the fields
            that are defined on the model. """
        pls_fields_config = self.env['ir.config_parameter'].sudo().get_param('crm.pls_fields')
        pls_fields = pls_fields_config.split(',') if pls_fields_config else []
        pls_safe_fields = [field for field in pls_fields if field in self._fields.keys()]
        return pls_safe_fields

    # Compute Automated Probability Tools
    # -----------------------------------
    def _pls_get_won_lost_total_count(self, team_results):
        """ Get all won and all lost + total :
               first stage can be used to know how many lost and won there is
               as won count are equals for all stage
               and first stage is always incremented in lost_count
        :param team_results:
        :return: won count, lost count and total count for all records in frequencies
        """
        # TODO : check if we need to handle specific team_id stages [for lost count] (if first stage in sequence is team_specific)
        first_stage_id = self.env['crm.stage'].search([('team_ids', '=', False)], order='sequence, id', limit=1)
        if str(first_stage_id.id) not in team_results.get('stage_id', []):
            return 0, 0, 0
        stage_result = team_results['stage_id'][str(first_stage_id.id)]
        return stage_result['won'], stage_result['lost'], stage_result['won'] + stage_result['lost']

    # PLS: Rebuild Frequency Table Tools
    # ----------------------------------
    def _pls_prepare_frequencies(self, lead_values, leads_pls_fields, target_state=None):
        """new state is used when getting frequencies for leads that are changing to lost or won.
        Stays none if we are checking frequencies for leads already won or lost."""
        pls_fields = leads_pls_fields.copy()
        frequencies = dict((field, {}) for field in pls_fields)

        stage_ids = self.env['crm.stage'].search_read([], ['sequence', 'name', 'id'], order='sequence, id')
        stage_sequences = {stage['id']: stage['sequence'] for stage in stage_ids}

        # Increment won / lost frequencies by criteria (field / value couple)
        for values in lead_values:
            if target_state:  # ignore probability values if target state (as probability is the old value)
                won_count = values['count'] if target_state == 'won' else 0
                lost_count = values['count'] if target_state == 'lost' else 0
            else:
                won_count = values['count'] if values.get('probability', 0) == 100 else 0
                lost_count = values['count'] if values.get('probability', 1) == 0  else 0

            if 'tag_id' in values:
                frequencies = self._pls_increment_frequency_dict(frequencies, 'tag_id', values['tag_id'], won_count, lost_count)
                continue

            # Else, treat other fields
            if 'tag_id' in pls_fields:  # tag_id already treated here above.
                pls_fields.remove('tag_id')
            for field in pls_fields:
                if field not in values:
                    continue
                value = values[field]
                if value or field in ('email_state', 'phone_state'):
                    if field == 'stage_id':
                        if won_count:  # increment all stages if won
                            stages_to_increment = [stage['id'] for stage in stage_ids]
                        else:  # increment only current + previous stages if lost
                            current_stage_sequence = stage_sequences[value]
                            stages_to_increment = [stage['id'] for stage in stage_ids if stage['sequence'] <= current_stage_sequence]
                        for stage_id in stages_to_increment:
                            frequencies = self._pls_increment_frequency_dict(frequencies, field, stage_id, won_count, lost_count)
                    else:
                        frequencies = self._pls_increment_frequency_dict(frequencies, field, value, won_count, lost_count)

        return frequencies

    def _pls_increment_frequency_dict(self, frequencies, field, value, won, lost):
        value = str(value)  # Ensure we will always compare strings.
        if value not in frequencies[field]:
            frequencies[field][value] = {'won': won, 'lost': lost}
        else:
            frequencies[field][value]['won'] += won
            frequencies[field][value]['lost'] += lost
        return frequencies

    # Common PLS Tools
    # ----------------
    def _pls_get_lead_pls_values(self, domain=None):
        """
        This methods builds a dict where, for each lead in self or matching the given domain,
        we will get a list of field/value couple.
        Due to onchange and create, we don't always have the id of the lead to recompute.
        When we update few records (one, typically) with onchanges, we build the lead_values (= couple field/value)
        using the ORM.
        To speed up the computation and avoid making too much DB read inside loops,
        we can give a domain to make sql queries to bypass the ORM.
        This domain will be used in sql queries to get the values for every lead matching the domain.
        :param domain: If set, we get all the leads values via unique sql queries (one for tags, one for other fields),
                            using the given domain on leads.
                       If not set, get lead values lead by lead using the ORM.
        :return: {lead_id: [(field1: value1), (field2: value2), ...], ...}
        """
        leads_values_dict = OrderedDict()
        pls_fields = ["stage_id", "team_id"] + self._pls_get_safe_fields()

        # Check if tag_ids is in the pls_fields and removed it from the list. The tags will be managed separately.
        use_tags = 'tag_ids' in pls_fields
        if use_tags:
            pls_fields.remove('tag_ids')

        if domain:
            # Get leads values
            self.flush_model()
            # active_test = False as domain should take active into 'active' field it self
            query = self.env['crm.lead'].with_context(active_test=False)._search(domain, bypass_access=True)
            table = query.table
            query.order = SQL("%(table)s.team_id asc, %(table)s.id desc", table=SQL.identifier(table))
            sql_fields = [SQL.identifier(field) for field in pls_fields]
            self.env.cr.execute(query.select(
                SQL("id"),
                SQL("probability"),
                *sql_fields,
            ))
            lead_results = self.env.cr.dictfetchall()

            if use_tags:
                # Get tags values
                tag_rel_alias = query.left_join(table, 'id', 'crm_tag_rel', 'lead_id', 'crm_tag_rel')
                tag_alias = query.left_join(tag_rel_alias, 'tag_id', 'crm_tag', 'id', 'crm_tag')
                self.env.cr.execute(query.select(
                    SQL("%s AS lead_id", SQL.identifier(table, "id")),
                    SQL("%s AS tag_id", SQL.identifier(tag_alias, "id")),
                ))
                tag_results = self.env.cr.dictfetchall()
            else:
                tag_results = []

            # get all (variable, value) couple for all in self
            for lead in lead_results:
                lead_values = []
                for field in pls_fields + ['probability']:  # add probability as used in _pls_prepare_frequencies (needed in rebuild mode)
                    value = lead[field]
                    if field == 'team_id':  # ignore team_id as stored separately in leads_values_dict[lead_id][team_id]
                        continue
                    if value or field == 'probability':  # 0 is a correct value for probability
                        lead_values.append((field, value))
                    elif field in ('email_state', 'phone_state'):  # As ORM reads 'None' as 'False', do the same here
                        lead_values.append((field, False))
                    leads_values_dict[lead['id']] = {'values': lead_values, 'team_id': lead['team_id'] or 0}

            for tag in tag_results:
                if tag['tag_id']:
                    leads_values_dict[tag['lead_id']]['values'].append(('tag_id', tag['tag_id']))
            return leads_values_dict
        else:
            for lead in self:
                lead_values = []
                for field in pls_fields:
                    if field == 'team_id':  # ignore team_id as stored separately in leads_values_dict[lead_id][team_id]
                        continue
                    value = lead[field].id if isinstance(lead[field], models.BaseModel) else lead[field]
                    if value or field in ('email_state', 'phone_state'):
                        lead_values.append((field, value))
                if use_tags:
                    for tag in lead.tag_ids:
                        lead_values.append(('tag_id', tag.id))
                leads_values_dict[lead.id] = {'values': lead_values, 'team_id': lead['team_id'].id}
            return leads_values_dict

    # PLS Backend Tooltip
    # -------------------
    def prepare_pls_tooltip_data(self):
        """
        Compute and return all necessary information to render CrmPlsTooltip, displayed when
        pressing the small AI button, located next to the label of probability when automated,
        in the crm.lead form view. This method first replaces ids with display names of relational
        fields before returning data, then also recomputes probabilities and writes them on self.

        :returns:

            ::
                {
                    low_3_data: list of field-value couples for lowest 3 criterions, lowest first
                    probability: numerical value, used for display on tooltip
                    team_name: string, name of lead team if any
                    top_3_data: list of field-value couples for top 3 criterions, highest first
                }

        :rtype: dict
        """
        self.ensure_one()
        _unused, tooltip_data = self._pls_get_naive_bayes_probabilities(is_tooltip=True)
        sorted_scores_with_name = []

        # We want to display names in the tooltip, not ids.
        # The last element in tuple is only used for tags to ensure same color in tooltip.
        for score, field, value in sorted(tooltip_data['scores']):
            # Skip nonsense results for phone and email states. May happen in a db having a few leads.
            if field in ['phone_state', 'email_state']:
                if value in [False, 'incorrect'] and tools.float_compare(score, 0.50, 2) > 0:
                    continue
                if value == 'correct' and tools.float_compare(score, 0.50, 2) < 0:
                    continue
            if field == 'tag_id':
                tag = self.tag_ids.filtered(lambda tag: tag.id == value)
                sorted_scores_with_name.append((score, field, tag.display_name, tag.color))
            elif isinstance(self[field], models.BaseModel):
                sorted_scores_with_name.append((score, field, self[field].display_name, False))
            else:
                sorted_scores_with_name.append((score, field, str(value), False))

        # Update automated probability, as it may have changed since last computation
        # -> avoids differences in display between tooltip and record. A 0.00 probability implies
        # that the computation was not possible. Sample data will be used instead.
        probability_values = {'automated_probability': tooltip_data['probability']}
        if self.is_automated_probability:
            probability_values['probability'] = tooltip_data['probability']
        self.write(probability_values)

        # Sample values if probability could not be computed. If it was, but if all scores
        # were excluded above, a placeholder will be used instead in the tooltip.
        if tools.float_is_zero(tooltip_data['probability'], 2):
            sorted_scores_with_name = [
                (.1, 'email_state', False, False),
                (.2, 'tag_id', _('Exploration'), 4),
                (.3, 'stage_id', _('New'), False),
                (.7, 'phone_state', 'correct', False),
                (.8, 'country_id', _('Belgium'), False),
                (.9, 'tag_id', _('Consulting'), 3),
            ]

        return {
            'low_3_data': [
                {
                    'field': element[1],
                    'value': element[2],
                    'color': element[3]
                } for element in sorted_scores_with_name[:3] if tools.float_compare(element[0], 0.50, 2) < 0
            ],
            'probability': tooltip_data['probability'],
            'team_name': self.team_id.display_name,
            'top_3_data': [
                {
                    'field': element[1],
                    'value': element[2],
                    'color': element[3]
                } for element in sorted_scores_with_name[::-1][:3] if tools.float_compare(element[0], 0.50, 2) > 0
            ],
        }


# FILEPATH: odoo/addons/crm/models/crm_lead_scoring_frequency.py (lines 7-15)
class CrmLeadScoringFrequency(models.Model):
    _name = 'crm.lead.scoring.frequency'
    _description = 'Lead Scoring Frequency'
    variable = fields.Char('Variable', index=True)
    value = fields.Char('Value')
    won_count = fields.Float('Won Count', digits=(16, 1))
    lost_count = fields.Float('Lost Count', digits=(16, 1))
    team_id = fields.Many2one('crm.team', 'Sales Team', ondelete="cascade")


# FILEPATH: odoo/addons/crm/models/crm_lead_scoring_frequency.py (lines 18-30)
class CrmLeadScoringFrequencyField(models.Model):
    _name = 'crm.lead.scoring.frequency.field'
    _description = 'Fields that can be used for predictive lead scoring computation'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(related="field_id.field_description")
    field_id = fields.Many2one(
        'ir.model.fields', domain=[('model_id.model', '=', 'crm.lead')], required=True,
        ondelete='cascade',
    )
    color = fields.Integer('Color', default=_get_default_color)


# FILEPATH: odoo/addons/crm/models/crm_lost_reason.py
class CrmLostReason(models.Model):
    _name = 'crm.lost.reason'
    _description = 'Opp. Lost Reason'

    name = fields.Char('Description', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    leads_count = fields.Integer('Leads Count', compute='_compute_leads_count')

    def _compute_leads_count(self):
        lead_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            [('lost_reason_id', 'in', self.ids)],
            ['lost_reason_id'],
            ['__count'],
        )
        mapped_data = {lost_reason.id: count for lost_reason, count in lead_data}
        for reason in self:
            reason.leads_count = mapped_data.get(reason.id, 0)

    def action_lost_leads(self):
        return {
            'name': _('Leads'),
            'view_mode': 'list,form',
            'domain': [('lost_reason_id', 'in', self.ids)],
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }


# FILEPATH: odoo/addons/crm/models/crm_recurring_plan.py
class CrmRecurringPlan(models.Model):
    _name = 'crm.recurring.plan'
    _description = "CRM Recurring revenue plans"
    _order = "sequence"
    name = fields.Char('Plan Name', required=True, translate=True)
    number_of_months = fields.Integer('# Months', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    _check_number_of_months = models.Constraint(
        'CHECK(number_of_months >= 0)',
        "The number of month can't be negative.",
    )


# FILEPATH: odoo/addons/crm/models/crm_stage.py
AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]
class CrmStage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = 'crm.stage'
    _description = "CRM Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    is_won = fields.Boolean('Is Won Stage?')
    rotting_threshold_days = fields.Integer('Days to rot', default=0, help='Highlight opportunities that haven\'t been updated for this many days. \
        Set to 0 to disable. Changing this parameter will not affect the rotting status/date of resources last updated before this change.')
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    team_ids = fields.Many2many('crm.team', string='Sales Teams', ondelete='restrict')
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    # This field for interface only
    team_count = fields.Integer('team_count', compute='_compute_team_count')
    color = fields.Integer(string='Color', export_string_translation=False)

    @api.depends('team_ids')
    def _compute_team_count(self):
        self.team_count = self.env['crm.team'].search_count([])

    @api.onchange('is_won')
    def _onchange_is_won(self):
        return {
            'warning': {
                'title': _("Do you really want to update this stage?"),
                'message': _("Changing the value of 'Is Won Stage' may induce a large number of operations, "
                            "as the probabilities of opportunities in this stage will be recomputed on saving."),
            }
        }

    def write(self, vals):
        """ Since leads that are in a won stage must have their
        probability = 100%, this override ensures that setting a stage as won
        will set all the leads in that stage to probability = 100%.
        Inversely, if a won stage is not marked as won anymore, the lead
        probability should be recomputed based on automated probability.
        Note: If a user sets a stage as won and changes his mind right after,
        the manual probability will be lost in the process."""
        res = super().write(vals)
        if 'is_won' in vals:
            won_leads = self.env['crm.lead'].search([('stage_id', 'in', self.ids)])
            if won_leads and vals.get('is_won'):
                won_leads.write({'probability': 100, 'automated_probability': 100})
            elif won_leads and not vals.get('is_won'):
                won_leads._compute_probabilities()
        return res


# FILEPATH: odoo/addons/crm/models/crm_team.py
_logger = logging.getLogger(__name__)
class CrmTeam(models.Model):
    _name = 'crm.team'
    _inherit = ['mail.alias.mixin', 'crm.team']
    _description = 'Sales Team'

    use_leads = fields.Boolean('Leads', help="Check this box to filter and qualify incoming requests as leads before converting them into opportunities and assigning them to a salesperson.")
    use_opportunities = fields.Boolean('Pipeline', default=True, help="Check this box to manage a presales process with opportunities.")
    alias_id = fields.Many2one(help="The email address associated with this channel. New emails received will automatically create new leads assigned to the channel.")
    # assignment
    assignment_enabled = fields.Boolean('Lead Assign', compute='_compute_assignment_enabled')
    assignment_auto_enabled = fields.Boolean('Auto Assignment', compute='_compute_assignment_enabled')
    assignment_optout = fields.Boolean('Skip auto assignment')
    assignment_max = fields.Integer(
        'Lead Average Capacity', compute='_compute_assignment_max',
        help='Monthly average leads capacity for all salesmen belonging to the team')
    assignment_domain = fields.Char(
        'Assignment Domain', tracking=True,
        help='Additional filter domain when fetching unassigned leads to allocate to the team.')
    # statistics about leads / opportunities / both
    lead_unassigned_count = fields.Integer(
        string='# Unassigned Leads', compute='_compute_lead_unassigned_count')
    lead_all_assigned_month_count = fields.Integer(
        string='# Leads/Opps assigned this month', compute='_compute_lead_all_assigned_month_count',
        help="Number of leads and opportunities assigned this last month.")
    lead_all_assigned_month_exceeded = fields.Boolean('Exceed monthly lead assignement', compute="_compute_lead_all_assigned_month_count",
        help="True if the monthly lead assignment count is greater than the maximum assignment limit, false otherwise."
    )
    # properties
    lead_properties_definition = fields.PropertiesDefinition('Lead Properties')

    @api.depends('crm_team_member_ids.assignment_max')
    def _compute_assignment_max(self):
        for team in self:
            team.assignment_max = sum(member.assignment_max for member in team.crm_team_member_ids)

    def _compute_assignment_enabled(self):
        assign_enabled = self.env['crm.lead']._is_rule_based_assignment_activated()
        auto_assign_enabled = False
        if assign_enabled:
            assign_cron = self.sudo().env.ref('crm.ir_cron_crm_lead_assign', raise_if_not_found=False)
            auto_assign_enabled = assign_cron.active if assign_cron else False
        self.assignment_enabled = assign_enabled
        self.assignment_auto_enabled = auto_assign_enabled

    def _compute_lead_unassigned_count(self):
        leads_data = self.env['crm.lead']._read_group([
            ('team_id', 'in', self.ids),
            ('user_id', '=', False),
        ], ['team_id'], ['__count'])
        counts = {team.id: count for team, count in leads_data}
        for team in self:
            team.lead_unassigned_count = counts.get(team.id, 0)

    @api.depends('crm_team_member_ids.lead_month_count', 'assignment_max')
    def _compute_lead_all_assigned_month_count(self):
        for team in self:
            team.lead_all_assigned_month_count = sum(member.lead_month_count for member in team.crm_team_member_ids)
            team.lead_all_assigned_month_exceeded = team.lead_all_assigned_month_count > team.assignment_max

    @api.onchange('use_leads', 'use_opportunities')
    def _onchange_use_leads_opportunities(self):
        if not self.use_leads and not self.use_opportunities:
            self.alias_name = False

    @api.constrains('assignment_domain')
    def _constrains_assignment_domain(self):
        for team in self:
            try:
                domain = literal_eval(team.assignment_domain or '[]')
                if domain:
                    self.env['crm.lead'].search(domain, limit=1)
            except Exception:
                raise exceptions.ValidationError(_('Assignment domain for team %(team)s is incorrectly formatted', team=team.name))

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    def write(self, vals):
        result = super().write(vals)
        if 'use_leads' in vals or 'use_opportunities' in vals:
            for team in self:
                alias_vals = team._alias_get_creation_values()
                team.write({
                    'alias_name': alias_vals.get('alias_name', team.alias_name),
                    'alias_defaults': alias_vals.get('alias_defaults'),
                })
        return result

    def unlink(self):
        """ When unlinking, concatenate ``crm.lead.scoring.frequency`` linked to
        the team into "no team" statistics. """
        frequencies = self.env['crm.lead.scoring.frequency'].search([('team_id', 'in', self.ids)])
        if frequencies:
            existing_noteam = self.env['crm.lead.scoring.frequency'].sudo().search([
                ('team_id', '=', False),
                ('variable', 'in', frequencies.mapped('variable'))
            ])
            for frequency in frequencies:
                # skip void-like values
                if float_compare(frequency.won_count, 0.1, 2) != 1 and float_compare(frequency.lost_count, 0.1, 2) != 1:
                    continue

                match = existing_noteam.filtered(lambda frequ_nt: frequ_nt.variable == frequency.variable and frequ_nt.value == frequency.value)
                if match:
                    # remove extra .1 that may exist in db as those are artifacts of initializing
                    # frequency table. Final value of 0 will be set to 0.1.
                    exist_won_count = float_round(match.won_count, precision_digits=0, rounding_method='HALF-UP')
                    exist_lost_count = float_round(match.lost_count, precision_digits=0, rounding_method='HALF-UP')
                    add_won_count = float_round(frequency.won_count, precision_digits=0, rounding_method='HALF-UP')
                    add_lost_count = float_round(frequency.lost_count, precision_digits=0, rounding_method='HALF-UP')
                    new_won_count = exist_won_count + add_won_count
                    new_lost_count = exist_lost_count + add_lost_count
                    match.won_count = new_won_count if float_compare(new_won_count, 0.1, 2) == 1 else 0.1
                    match.lost_count = new_lost_count if float_compare(new_lost_count, 0.1, 2) == 1 else 0.1
                else:
                    existing_noteam += self.env['crm.lead.scoring.frequency'].sudo().create({
                        'lost_count': frequency.lost_count if float_compare(frequency.lost_count, 0.1, 2) == 1 else 0.1,
                        'team_id': False,
                        'value': frequency.value,
                        'variable': frequency.variable,
                        'won_count': frequency.won_count if float_compare(frequency.won_count, 0.1, 2) == 1 else 0.1,
                    })
        return super().unlink()

    # ------------------------------------------------------------
    # MESSAGING
    # ------------------------------------------------------------

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('crm.lead').id
        if self.id:
            if not self.use_leads and not self.use_opportunities:
                values['alias_name'] = False
            values['alias_defaults'] = defaults = literal_eval(self.alias_defaults or "{}")
            has_group_use_lead = self.env.user.has_group('crm.group_use_lead')
            defaults['type'] = 'lead' if has_group_use_lead and self.use_leads else 'opportunity'
            defaults['team_id'] = self.id
        return values

    # ------------------------------------------------------------
    # LEAD ASSIGNMENT
    # ------------------------------------------------------------

    @api.model
    def _cron_assign_leads(self, force_quota=False, creation_delta_days=7):
        """ Cron method assigning leads. Leads are allocated to all teams and
        assigned to their members.

        The cron is designed to run at least once a day or more.
        A number of leads will be assigned each time depending on the daily leads
        already assigned.
        This allows the assignment process based on the cron to work on a daily basis
        without allocating too much leads on members if the cron is executed multiple
        times a day.
        The daily quota of leads can be forcefully assigned with force_quota
        (ignoring the daily leads already assigned).

        See ``CrmTeam.action_assign_leads()`` and its sub methods for more
        details about assign process.

        """
        self.env['crm.team'].search([
            '&', '|', ('use_leads', '=', True), ('use_opportunities', '=', True),
            ('assignment_optout', '=', False)
        ])._action_assign_leads(force_quota=force_quota, creation_delta_days=creation_delta_days)
        return True

    def action_assign_leads(self):
        """ Manual (direct) leads assignment. This method both

          * assigns leads to teams given by self;
          * assigns leads to salespersons belonging to self;

        See sub methods for more details about assign process.

        :returns: action, a client notification giving some insights on assign
          process;
        """
        teams_data, members_data = self._action_assign_leads(force_quota=True, creation_delta_days=0)

        # format result messages
        logs = self._action_assign_leads_logs(teams_data, members_data)
        html_message = Markup('<br />').join(logs)
        notif_message = ' '.join(logs)

        # log a note in case of manual assign (as this method will mainly be called
        # on singleton record set, do not bother doing a specific message per team)
        log_action = _("Lead Assignment requested by %(user_name)s", user_name=self.env.user.name)
        log_message = Markup("<p>%s<br /><br />%s</p>") % (log_action, html_message)
        self._message_log_batch(bodies=dict((team.id, log_message) for team in self))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Leads Assigned"),
                'message': notif_message,
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            }
        }

    def _action_assign_leads(self, force_quota=False, creation_delta_days=7):
        """ Private method for lead assignment. This method both

          * assigns leads to teams given by self;
          * assigns leads to salespersons belonging to self;

        See sub methods for more details about assign process.

        :param bool force_quota: Assign the full daily quota without taking into account
                                 the leads already assigned today
        :param int creation_delta_days: Take into account all leads created in the last nb days (by default 7).
                                        If set to zero we take all the past leads.

        :returns: 2-elements tuple (teams_data, members_data) as a
          structure-based result of assignment process. For more details
          about data see :meth:`CrmTeam._allocate_leads` and
          :meth:`CrmTeam._assign_and_convert_leads`;
        """
        if not (self.env.user.has_group('sales_team.group_sale_manager') or self.env.is_system()):
            raise exceptions.UserError(_('Lead/Opportunities automatic assignment is limited to managers or administrators'))

        _logger.info(
            '### START Lead Assignment (%d teams, %d sales persons, force daily quota: %s)',
            len(self),
            len(self.crm_team_member_ids),
            "ON" if force_quota else "OFF")
        teams_data = self._allocate_leads(creation_delta_days=creation_delta_days)
        _logger.info('### Team repartition done. Starting salesmen assignment.')
        members_data = self._assign_and_convert_leads(force_quota=force_quota)
        _logger.info('### END Lead Assignment')
        return teams_data, members_data

    def _action_assign_leads_logs(self, teams_data, members_data):
        """ Tool method to prepare notification about assignment process result.

        :param teams_data: see ``CrmTeam._allocate_leads()``;
        :param members_data: see ``CrmTeam._assign_and_convert_leads()``;

        :returns: list of formatted logs, ready to be formatted into a nice
        plaintext or html message at caller's will
        :rtype: list[str]
        """
        # extract some statistics
        assigned = sum(len(teams_data[team]['assigned']) + len(teams_data[team]['merged']) for team in teams_data)
        duplicates = sum(len(teams_data[team]['duplicates']) for team in teams_data)
        members = len(members_data)
        members_assigned = sum(len(member_data['assigned']) for member_data in members_data.values())

        # format user notification
        message_parts = []
        # 1- duplicates removal
        if duplicates:
            message_parts.append(_("%(duplicates)s duplicates leads have been merged.",
                                   duplicates=duplicates))

        # 2- nothing assigned at all
        if not assigned and not members_assigned:
            if len(self) == 1:
                if not self.assignment_max:
                    message_parts.append(
                        _("No allocated leads to %(team_name)s team because it has no capacity. Add capacity to its salespersons.",
                          team_name=self.name))
                else:
                    message_parts.append(
                        _("No allocated leads to %(team_name)s team and its salespersons because no unassigned lead matches its domain.",
                          team_name=self.name))
            else:
                message_parts.append(
                    _("No allocated leads to any team or salesperson. Check your Sales Teams and Salespersons configuration as well as unassigned leads."))

        # 3- team allocation
        if not assigned and members_assigned:
            if len(self) == 1:
                message_parts.append(
                    _("No new lead allocated to %(team_name)s team because no unassigned lead matches its domain.",
                      team_name=self.name))
            else:
                message_parts.append(_("No new lead allocated to the teams because no lead match their domains."))
        elif assigned:
            if len(self) == 1:
                message_parts.append(
                    _("%(assigned)s leads allocated to %(team_name)s team.",
                      assigned=assigned, team_name=self.name))
            else:
                message_parts.append(
                    _("%(assigned)s leads allocated among %(team_count)s teams.",
                      assigned=assigned, team_count=len(self)))

        # 4- salespersons assignment
        if not members_assigned and assigned:
            message_parts.append(
                _("No lead assigned to salespersons because no unassigned lead matches their domains."))
        elif members_assigned:
            message_parts.append(
                _("%(members_assigned)s leads assigned among %(member_count)s salespersons.",
                  members_assigned=members_assigned, member_count=members))

        return message_parts

    def _allocate_leads(self, creation_delta_days=7):
        """ Allocate leads to teams given by self. This method sets ``team_id``
        field on lead records that are unassigned (no team and no responsible).
        No salesperson is assigned in this process. Its purpose is simply to
        allocate leads within teams.

        This process allocates all available leads on teams weighted by their
        maximum assignment by month that indicates their relative workload.

        Heuristic of this method is the following:
          * find unassigned leads for each team, aka leads being
            * without team, without user -> not assigned;
            * not won nor inactive -> live leads;
            * created in the last creation_delta_days (in the last week by default)
              This avoid to take into account old leads in the allocation.
            * if set, a delay after creation can be applied (see BUNDLE_HOURS_DELAY)
              parameter explanations here below;
            * matching the team's assignment domain (empty means
              everything);

          * assign a weight to each team based on their assignment_max that
            indicates their relative workload;

          * pick a random team using a weighted random choice and find a lead
            to assign:

            * remove already assigned leads from the available leads. If there
              is not any lead spare to assign, remove team from active teams;
            * pick the first lead and set the current team;
            * when setting a team on leads, leads are also merged with their
              duplicates. Purpose is to clean database and avoid assigning
              duplicates to same or different teams;
            * add lead and its duplicates to already assigned leads;

          * pick another random team until their is no more leads to assign
            to any team;

        This process ensure that teams having overlapping domains will all
        receive leads as lead allocation is done one lead at a time. This
        allocation will be proportional to their size (assignment of their
        members).

        Supported ``ir.config_parameter`` settings.

        ``crm.assignment.bundle``
            deprecated

        ``crm.assignment.commit.bundle`` (``int``)
            Allow to set size of lead batch to be committed together. By
            default 100 which is a good trade-off between transaction time and
            speed.

        ``crm.assignment.delay`` (``float``)
            Give a delay before taking a lead into assignment process
            (BUNDLE_HOURS_DELAY) given in hours. Purpose if to allow other
            crons or automation rules to make their job. This option is mainly
            historic as its purpose was to let automation rules prepare leads
            and score before PLS was added into CRM. This is now not required
            anymore but still supported;

        :param int creation_delta_days: see ``CrmTeam._action_assign_leads()``;

        :rtype: dict[str, Any]
        :return: dictionary mapping each team with assignment result:

            ``assigned`` (``set[int]``)
                Lead IDs directly assigned to the team
                (no duplicate or merged found)

            ``merged`` (``set[int]``)
                Lead IDs merged and assigned to the team
                (main leads being results of merge process)

            ``duplicates`` (``set[int]``)
                Lead IDs found as duplicates and merged into other leads.
                Those leads are unlinked during assign process and are already
                removed at return of this method

        """

        BUNDLE_HOURS_DELAY = float(self.env['ir.config_parameter'].sudo().get_param('crm.assignment.delay', default=0))
        BUNDLE_COMMIT_SIZE = int(self.env['ir.config_parameter'].sudo().get_param('crm.assignment.commit.bundle', 100))
        auto_commit = not modules.module.current_test

        # leads
        max_create_dt = self.env.cr.now() - datetime.timedelta(hours=BUNDLE_HOURS_DELAY)
        duplicates_lead_cache = dict()

        # teams data
        teams_data, population, weights = dict(), list(), list()
        for team in self:
            if not team.assignment_max:
                continue

            lead_domain = Domain.AND([
                literal_eval(team.assignment_domain or '[]'),
                [('create_date', '<=', max_create_dt)],
                ['&', ('team_id', '=', False), ('user_id', '=', False)],
                [('won_status', '!=', 'won')]
            ])
            if creation_delta_days > 0:
                lead_domain &= Domain('create_date', '>', self.env.cr.now() - datetime.timedelta(days=creation_delta_days))

            leads = self.env["crm.lead"].search(lead_domain)
            # Fill duplicate cache: search for duplicate lead before the assignment
            # avoid to flush during the search at every assignment
            for lead in leads:
                if lead not in duplicates_lead_cache:
                    duplicates_lead_cache[lead] = lead._get_lead_duplicates(email=lead.email_from)

            teams_data[team] = {
                "team": team,
                "leads": leads,
                "assigned": set(),
                "merged": set(),
                "duplicates": set(),
            }
            population.append(team)
            weights.append(team.assignment_max)

        # Start a new transaction, since data fetching take times
        # and the first commit occur at the end of the bundle,
        # the first transaction can be long which we want to avoid
        if auto_commit:
            self.env.cr.commit()

        # assignment process data
        global_data = dict(assigned=set(), merged=set(), duplicates=set())
        leads_done_ids, lead_unlink_ids, counter = set(), set(), 0
        while population:
            counter += 1
            team = random.choices(population, weights=weights, k=1)[0]

            # filter remaining leads, remove team if no more leads for it
            teams_data[team]["leads"] = teams_data[team]["leads"].filtered(lambda l: l.id not in leads_done_ids).exists()
            if not teams_data[team]["leads"]:
                population_index = population.index(team)
                population.pop(population_index)
                weights.pop(population_index)
                continue

            # assign + deduplicate and concatenate results in teams_data to keep some history
            candidate_lead = teams_data[team]["leads"][0]
            assign_res = team._allocate_leads_deduplicate(candidate_lead, duplicates_cache=duplicates_lead_cache)
            for key in ('assigned', 'merged', 'duplicates'):
                teams_data[team][key].update(assign_res[key])
                leads_done_ids.update(assign_res[key])
                global_data[key].update(assign_res[key])
            lead_unlink_ids.update(assign_res['duplicates'])

            # auto-commit except in testing mode. As this process may be time consuming or we
            # may encounter errors, already commit what is allocated to avoid endless cron loops.
            if auto_commit and counter % BUNDLE_COMMIT_SIZE == 0:
                # unlink duplicates once
                self.env['crm.lead'].browse(lead_unlink_ids).unlink()
                lead_unlink_ids = set()
                self.env.cr.commit()

        # unlink duplicates once
        self.env['crm.lead'].browse(lead_unlink_ids).unlink()

        if auto_commit:
            self.env.cr.commit()

        # some final log
        _logger.info('## Assigned %s leads', (len(global_data['assigned']) + len(global_data['merged'])))
        for team, team_data in teams_data.items():
            _logger.info(
                '## Assigned %s leads to team %s',
                len(team_data['assigned']) + len(team_data['merged']), team.id)
            _logger.info(
                '\tLeads: direct assign %s / merge result %s / duplicates merged: %s',
                team_data['assigned'], team_data['merged'], team_data['duplicates'])
        return teams_data

    def _allocate_leads_deduplicate(self, leads, duplicates_cache=None):
        """ Assign leads to sales team given by self by calling lead tool
        method _handle_salesmen_assignment. In this method we deduplicate leads
        allowing to reduce number of resulting leads before assigning them
        to salesmen.

        :param leads: recordset of leads to assign to current team;
        :param duplicates_cache: if given, avoid to perform a duplicate search
          and fetch information in it instead;
        """
        self.ensure_one()
        duplicates_cache = duplicates_cache if duplicates_cache is not None else dict()

        # classify leads
        leads_assigned = self.env['crm.lead']  # direct team assign
        leads_done_ids, leads_merged_ids, leads_dup_ids = set(), set(), set()  # classification
        leads_dups_dict = dict()  # lead -> its duplicate
        for lead in leads:
            if lead.id not in leads_done_ids:

                # fill cache if not already done
                if lead not in duplicates_cache:
                    duplicates_cache[lead] = lead._get_lead_duplicates(email=lead.email_from)
                lead_duplicates = duplicates_cache[lead].exists()

                if len(lead_duplicates) > 1:
                    leads_dups_dict[lead] = lead_duplicates
                    leads_done_ids.update((lead + lead_duplicates).ids)
                else:
                    leads_assigned += lead
                    leads_done_ids.add(lead.id)

        # assign team to direct assign (leads_assigned) + dups keys (to ensure their team
        # if they are elected master of merge process)
        dups_to_assign = [lead for lead in leads_dups_dict]
        leads_assigned.union(*dups_to_assign)._handle_salesmen_assignment(user_ids=None, team_id=self.id)

        for lead in leads.filtered(lambda lead: lead in leads_dups_dict):
            lead_duplicates = leads_dups_dict[lead]
            merged = lead_duplicates._merge_opportunity(user_id=False, team_id=False, auto_unlink=False, max_length=0)
            leads_dup_ids.update((lead_duplicates - merged).ids)
            leads_merged_ids.add(merged.id)

        return {
            'assigned': set(leads_assigned.ids),
            'merged': leads_merged_ids,
            'duplicates': leads_dup_ids,
        }

    def _get_lead_to_assign_domain(self):
        return [
            ('user_id', '=', False),
            ('date_open', '=', False),
            ('team_id', 'in', self.ids),
        ]

    def _assign_and_convert_leads(self, force_quota=False):
        """ Main processing method to assign leads to sales team members. It also
        converts them into opportunities. This method should be called after
        ``_allocate_leads`` as this method assigns leads already allocated to
        the member's team. Its main purpose is therefore to distribute team
        workload on its members based on their capacity.

        This method follows the following heuristic
            * Get quota per member
            * Find all leads to be assigned per team
            * Sort list of members per number of leads received in the last 24h
            * Assign the lead using round robin
                * Find the first member with a compatible domain
                * Assign the lead
                * Move the member at the end of the list if quota is not reached
                * Remove it otherwise
                * Move to the next lead

        :param bool force_quota: see ``CrmTeam._action_assign_leads()``;

        :returns: dict() with each member assignment result:
          membership: {
            'assigned': set of lead IDs directly assigned to the member;
          }, ...

        """
        auto_commit = not modules.module.current_test
        result_data = {}
        commit_bundle_size = int(self.env['ir.config_parameter'].sudo().get_param('crm.assignment.commit.bundle', 100))
        teams_with_members = self.filtered(lambda team: team.crm_team_member_ids)
        quota_per_member = {member: member._get_assignment_quota(force_quota=force_quota) for member in self.crm_team_member_ids}
        counter = 0
        leads_per_team = dict(self.env['crm.lead']._read_group(
            teams_with_members._get_lead_to_assign_domain(),
            ['team_id'],
            # Do not use recordset aggregation to avoid fetching all the leads at once in memory
            # We want to have in memory only leads for the current team
            # and make sure we need them before fetching them
            ['id:array_agg'],
        ))

        def _assign_lead(lead, members, member_leads, members_quota, assign_lst, optional_lst=None):
            """ Find relevant member whose domain(s) accept the lead. If found convert
            and update internal structures accordingly. """
            member_found = next((member for member in members if lead in member_leads[member]), False)
            if not member_found:
                return
            lead.with_context(mail_auto_subscribe_no_notify=True).convert_opportunity(
                lead.partner_id,
                user_ids=member_found.user_id.ids
            )
            result_data[member_found]['assigned'] += lead

            # if member still has quota, move at end of list; otherwise just remove
            assign_lst.remove(member_found)
            if optional_lst is not None:
                optional_lst.remove(member_found)
            members_quota[member_found] -= 1
            if members_quota[member_found] > 0:
                assign_lst.append(member_found)
                if optional_lst is not None:
                    optional_lst.append(member_found)
            return member_found

        for team, leads_to_assign_ids in leads_per_team.items():
            members_to_assign = list(team.crm_team_member_ids.filtered(lambda member:
                not member.assignment_optout and quota_per_member.get(member, 0) > 0
            ).sorted(key=lambda member: quota_per_member.get(member, 0), reverse=True))
            if not members_to_assign:
                continue
            result_data.update({
                member: {"assigned": self.env["crm.lead"], "quota": quota_per_member[member]}
                for member in members_to_assign
            })
            # Need to check that record still exists since the ids have been fetched at the beginning of the process
            # Previous iteration has committed the change, records may have been deleted in the meanwhile
            to_assign = self.env['crm.lead'].browse(leads_to_assign_ids).exists()

            members_to_assign_wpref = [
                m for m in members_to_assign
                if m.assignment_domain_preferred and literal_eval(m.assignment_domain_preferred or '')
            ]
            preferred_leads_per_member = {
                member: to_assign.filtered_domain(
                    Domain.AND([
                        literal_eval(member.assignment_domain or '[]'),
                        literal_eval(member.assignment_domain_preferred)
                    ])
                ) for member in members_to_assign_wpref
            }
            preferred_leads = self.env['crm.lead'].concat(*[lead for lead in preferred_leads_per_member.values()])
            assigned_preferred_leads = self.env['crm.lead']

            # first assign loop: preferred leads, always priority
            for lead in preferred_leads.sorted(lambda lead: (-lead.probability, id)):
                counter += 1
                member_found = _assign_lead(lead, members_to_assign_wpref, preferred_leads_per_member, quota_per_member, members_to_assign, members_to_assign_wpref)
                if not member_found:
                    continue
                assigned_preferred_leads += lead
                if auto_commit and counter % commit_bundle_size == 0:
                    self.env.cr.commit()

            # second assign loop: fill up with other leads
            to_assign = to_assign - assigned_preferred_leads
            leads_per_member = {
                member: to_assign.filtered_domain(literal_eval(member.assignment_domain or '[]'))
                for member in members_to_assign
            }
            for lead in to_assign.sorted(lambda lead: (-lead.probability, id)):
                counter += 1
                member_found = _assign_lead(lead, members_to_assign, leads_per_member, quota_per_member, members_to_assign)
                if not member_found:
                    continue
                if auto_commit and counter % commit_bundle_size == 0:
                    self.env.cr.commit()

            # Make sure we commit at least at the end of the team
            if auto_commit:
                self.env.cr.commit()
            # Once we are done with a team we don't need to keep the leads in memory
            # Try to avoid to explode memory usage
            self.env.invalidate_all()
            _logger.info(
                'Team %s: Assigned %s leads based on preference, on a potential of %s (limited by quota)',
                team.name, len(assigned_preferred_leads), len(preferred_leads)
            )
        _logger.info(
            'Assigned %s leads to %s salesmen',
            sum(len(r['assigned']) for r in result_data.values()), len(result_data)
        )
        for member, member_info in result_data.items():
            _logger.info(
                '-> member %s of team %s: assigned %d/%d leads (%s)',
                member.id, member.crm_team_id.id, len(member_info["assigned"]), member_info["quota"], member_info["assigned"]
            )
        return result_data

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_your_pipeline(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        return self._action_update_to_pipeline(action)

    @api.model
    def action_opportunity_forecast(self):
        action = self.env['ir.actions.actions']._for_xml_id('crm.crm_lead_action_forecast')
        return self._action_update_to_pipeline(action)

    def action_open_leads(self):
        action = self.env['ir.actions.actions']._for_xml_id('crm.crm_case_form_view_salesteams_opportunity')
        rcontext = {
            'team': self,
        }
        action['help'] = self.env['ir.ui.view']._render_template('crm.crm_action_helper', values=rcontext)
        return action

    def action_open_unassigned_leads(self):
        action = self.action_open_leads()
        context_str = action.get('context', '{}')
        if context_str:
            try:
                context = safe_eval(action['context'], {'active_id': self.id, 'uid': self.env.uid})
            except (NameError, ValueError):
                context = {}
        else:
            context = {}
        action['context'] = context | {'search_default_unassigned': True}
        return action

    @api.model
    def _action_update_to_pipeline(self, action):
        self.check_access("read")
        user_team_id = self.env.user.sale_team_id.id
        if not user_team_id:
            user_team_id = self.search([], limit=1).id
            action['help'] = "<p class='o_view_nocontent_smiling_face'>%s</p><p>" % _("Create an Opportunity")
            if user_team_id:
                if self.env.user.has_group('sales_team.group_sale_manager'):
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should <a name="%d" type="action" tabindex="-1">join a team.</a>""",
                                        self.env.ref('sales_team.crm_team_action_config').id)
                else:
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should join a team.""")
        try:
            action_context = safe_eval(action['context'], {'uid': self.env.uid})
        except (NameError, ValueError):
            action_context = {}
        action['context'] = action_context
        return action

    def _compute_dashboard_button_name(self):
        super()._compute_dashboard_button_name()
        team_with_pipelines = self.filtered(lambda el: el.use_opportunities)
        team_with_pipelines.update({'dashboard_button_name': _("Pipeline")})

    def action_primary_channel_button(self):
        self.ensure_one()
        if self.use_opportunities:
            return self.action_open_leads()
        return super().action_primary_channel_button()


# FILEPATH: odoo/addons/crm/models/crm_team_member.py
_logger = logging.getLogger(__name__)
class CrmTeamMember(models.Model):
    _inherit = 'crm.team.member'

    # assignment
    assignment_enabled = fields.Boolean(related="crm_team_id.assignment_enabled")
    assignment_domain = fields.Char('Assignment Domain', tracking=True)
    assignment_domain_preferred = fields.Char('Preference assignment Domain', tracking=True)
    assignment_optout = fields.Boolean('Pause assignment')
    assignment_max = fields.Integer('Average Leads Capacity (on 30 days)', default=30)
    lead_day_count = fields.Integer(
        'Leads (last 24h)', compute='_compute_lead_day_count',
        help='Number of leads assigned to this member in the last 24 hours (lost leads excluded)')
    lead_month_count = fields.Integer(
        'Leads (30 days)', compute='_compute_lead_month_count',
        help='Number of leads assigned to this member in the last 30 days')

    @api.depends('user_id', 'crm_team_id')
    def _compute_lead_day_count(self):
        day_date = fields.Datetime.now() - datetime.timedelta(hours=24)
        daily_leads_counts = self._get_lead_from_date(day_date)

        for member in self:
            member.lead_day_count = daily_leads_counts.get((member.user_id.id, member.crm_team_id.id), 0)

    @api.depends('user_id', 'crm_team_id')
    def _compute_lead_month_count(self):
        month_date = fields.Datetime.now() - datetime.timedelta(days=30)
        monthly_leads_counts = self._get_lead_from_date(month_date)

        for member in self:
            member.lead_month_count = monthly_leads_counts.get((member.user_id.id, member.crm_team_id.id), 0)

    def _get_lead_from_date(self, date_from, active_test=False):
        return {
            (user.id, team.id): count for user, team, count in self.env['crm.lead'].with_context(active_test=active_test)._read_group(
                [
                    ('date_open', '>=', date_from),
                    ('team_id', 'in', self.crm_team_id.ids),
                    ('user_id', 'in', self.user_id.ids),
                ],
                ['user_id', 'team_id'],
                ['__count'],
            )
        }

    @api.constrains('assignment_domain')
    def _constrains_assignment_domain(self):
        for member in self:
            try:
                domain = literal_eval(member.assignment_domain or '[]')
                if domain:
                    self.env['crm.lead'].search(domain, limit=1)
            except Exception:
                raise exceptions.ValidationError(_(
                    'Member assignment domain for user %(user)s and team %(team)s is incorrectly formatted',
                    user=member.user_id.name, team=member.crm_team_id.name
                ))

    @api.constrains('assignment_domain_preferred')
    def _constrains_assignment_domain_preferred(self):
        for member in self:
            try:
                domain = literal_eval(member.assignment_domain_preferred or '[]')
                if domain:
                    self.env['crm.lead'].search(domain, limit=1)
            except Exception:
                raise exceptions.ValidationError(_(
                    'Member preferred assignment domain for user %(user)s and team %(team)s is incorrectly formatted',
                    user=member.user_id.name, team=member.crm_team_id.name
                ))

    # ------------------------------------------------------------
    # LEAD ASSIGNMENT
    # ------------------------------------------------------------

    def _get_assignment_quota(self, force_quota=False):
        """ Return the remaining daily quota based
        on the assignment_max and the lead already assigned in the past 24h

        :param bool force_quota: see ``CrmTeam._action_assign_leads()``;
        """
        quota = float_round(self.assignment_max / 30.0, precision_digits=0, rounding_method='HALF-UP')
        if force_quota:
            return quota
        return quota - self.lead_day_count


# FILEPATH: odoo/addons/crm/models/digest.py
class DigestDigest(models.Model):
    _inherit = 'digest.digest'

    kpi_crm_lead_created = fields.Boolean('New Leads')
    kpi_crm_lead_created_value = fields.Integer(compute='_compute_kpi_crm_lead_created_value')
    kpi_crm_opportunities_won = fields.Boolean('Opportunities Won')
    kpi_crm_opportunities_won_value = fields.Integer(compute='_compute_kpi_crm_opportunities_won_value')

    def _compute_kpi_crm_lead_created_value(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

        self._calculate_company_based_kpi('crm.lead', 'kpi_crm_lead_created_value')

    def _compute_kpi_crm_opportunities_won_value(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

        self._calculate_company_based_kpi(
            'crm.lead',
            'kpi_crm_opportunities_won_value',
            date_field='date_closed',
            additional_domain=[('type', '=', 'opportunity'), ('probability', '=', '100')],
        )

    def _compute_kpis_actions(self, company, user):
        res = super()._compute_kpis_actions(company, user)
        res['kpi_crm_lead_created'] = 'crm.crm_lead_action_pipeline?menu_id=%s' % self.env.ref('crm.crm_menu_root').id
        res['kpi_crm_opportunities_won'] = 'crm.crm_lead_action_pipeline?menu_id=%s' % self.env.ref('crm.crm_menu_root').id
        if user.has_group('crm.group_use_lead'):
            res['kpi_crm_lead_created'] = 'crm.crm_lead_all_leads?menu_id=%s' % self.env.ref('crm.crm_menu_root').id
        return res


# FILEPATH: odoo/addons/crm/models/ir_config_parameter.py
class IrConfig_Parameter(models.Model):
    _inherit = 'ir.config_parameter'

    def write(self, vals):
        result = super().write(vals)
        if any(record.key == "crm.pls_fields" for record in self):
            self.env.flush_all()
            self.env.registry._setup_models__(self.env.cr, ['crm.lead'])
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any(record.key == "crm.pls_fields" for record in records):
            self.env.flush_all()
            self.env.registry._setup_models__(self.env.cr, ['crm.lead'])
        return records

    def unlink(self):
        pls_emptied = any(record.key == "crm.pls_fields" for record in self)
        result = super().unlink()
        if pls_emptied and not self.env.context.get(MODULE_UNINSTALL_FLAG):
            self.env.flush_all()
            self.env.registry._setup_models__(self.env.cr, ['crm.lead'])
        return result


# FILEPATH: odoo/addons/crm/models/mail_activity.py
class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_create_calendar_event(self):
        """ Small override of the action that creates a calendar.

        If the activity is linked to a crm.lead through the "opportunity_id" field, we include in
        the action context the default values used when scheduling a meeting from the crm.lead form
        view.
        e.g: It will set the partner_id of the crm.lead as default attendee of the meeting. """

        action = super(MailActivity, self).action_create_calendar_event()
        opportunity = self.calendar_event_id.opportunity_id
        if opportunity:
            opportunity_action_context = opportunity.action_schedule_meeting(smart_calendar=False).get('context', {})
            opportunity_action_context['initial_date'] = self.calendar_event_id.start

            action['context'].update(opportunity_action_context)

        return action


# FILEPATH: odoo/addons/crm/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    group_use_lead = fields.Boolean(string="Leads", implied_group='crm.group_use_lead')
    group_use_recurring_revenues = fields.Boolean(string="Recurring Revenues", implied_group='crm.group_use_recurring_revenues')
    is_membership_multi = fields.Boolean(string='Multi Teams', config_parameter='sales_team.membership_multi')
    module_partnership = fields.Boolean("Membership / Partnership")
    crm_use_auto_assignment = fields.Boolean(
        string='Rule-Based Assignment', config_parameter='crm.lead.auto.assignment')
    crm_auto_assignment_action = fields.Selection([
        ('manual', 'Manually'), ('auto', 'Repeatedly')],
        string='Auto Assignment Action', compute='_compute_crm_auto_assignment_data',
        readonly=False, store=True,
        help='Manual assign allow to trigger assignment from team form view using an action button. Automatic configures a cron running repeatedly assignment in all teams.')
    crm_auto_assignment_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'),
        ('days', 'Days'), ('weeks', 'Weeks')],
        string='Auto Assignment Interval Unit', compute='_compute_crm_auto_assignment_data',
        readonly=False, store=True,
        help='Interval type between each cron run (e.g. each 2 days or each 2 hours)')
    crm_auto_assignment_interval_number = fields.Integer(
        string="Repeat every", compute='_compute_crm_auto_assignment_data',
        readonly=False, store=True,
        help='Number of interval type between each cron run (e.g. each 2 days or each 4 days)')
    crm_auto_assignment_run_datetime = fields.Datetime(
        string="Auto Assignment Next Execution Date", compute='_compute_crm_auto_assignment_data',
        readonly=False, store=True)
    module_crm_iap_mine = fields.Boolean("Generate new leads based on their country, industries, size, etc.")
    module_crm_iap_enrich = fields.Boolean("Enrich your leads automatically with company data based on their email address.")
    module_website_crm_iap_reveal = fields.Boolean("Create Leads/Opportunities from your website's traffic")
    lead_enrich_auto = fields.Selection([
        ('manual', 'Enrich leads on demand only'),
        ('auto', 'Enrich all leads automatically'),
    ], string='Enrich lead automatically', default='auto', config_parameter='crm.iap.lead.enrich.setting')
    lead_mining_in_pipeline = fields.Boolean("Create a lead mining request directly from the opportunity pipeline.", config_parameter='crm.lead_mining_in_pipeline')
    predictive_lead_scoring_start_date = fields.Date(string='Lead Scoring Starting Date', compute="_compute_pls_start_date", inverse="_inverse_pls_start_date_str")
    predictive_lead_scoring_start_date_str = fields.Char(string='Lead Scoring Starting Date in String', config_parameter='crm.pls_start_date')
    predictive_lead_scoring_fields = fields.Many2many('crm.lead.scoring.frequency.field', string='Lead Scoring Frequency Fields', compute="_compute_pls_fields", inverse="_inverse_pls_fields_str")
    predictive_lead_scoring_fields_str = fields.Char(string='Lead Scoring Frequency Fields in String', config_parameter='crm.pls_fields')
    predictive_lead_scoring_field_labels = fields.Char(compute='_compute_predictive_lead_scoring_field_labels')
    @api.depends('crm_use_auto_assignment')
    def _compute_crm_auto_assignment_data(self):
        pass  # shrunk (lines 55-68)
    @api.onchange('crm_auto_assignment_interval_type', 'crm_auto_assignment_interval_number')
    def _onchange_crm_auto_assignment_run_datetime(self):
        pass  # shrunk (lines 70-80)
    @api.depends('predictive_lead_scoring_fields_str')
    def _compute_pls_fields(self):
        pass  # shrunk (lines 82-92)
    def _inverse_pls_fields_str(self):
        pass  # shrunk (lines 94-101)
    @api.depends('predictive_lead_scoring_start_date_str')
    def _compute_pls_start_date(self):
        pass  # shrunk (lines 103-117)
    def _inverse_pls_start_date_str(self):
        pass  # shrunk (lines 119-124)
    @api.depends('predictive_lead_scoring_fields')
    def _compute_predictive_lead_scoring_field_labels(self):
        pass  # shrunk (lines 126-133)
    def set_values(self):
        pass  # shrunk (lines 135-162)
    def _get_crm_auto_assignmment_run_datetime(self, run_datetime, run_interval, run_interval_number):
        pass  # shrunk (lines 164-169)
    def action_crm_assign_leads(self):
        pass  # shrunk (lines 171-173)


# FILEPATH: odoo/addons/crm/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'
    opportunity_ids = fields.One2many('crm.lead', 'partner_id', string='Opportunities', domain=[('type', '=', 'opportunity')])
    opportunity_count = fields.Integer(
        string="Opportunity Count",
        groups='sales_team.group_sale_salesman',
        compute='_compute_opportunity_count',
    )
    def _fetch_children_partners_for_hierarchy(self):
    # retrieve all children partners and prefetch 'parent_id' on them, saving
    # queries for recursive parent_id browse
        pass  # shrunk (lines 16-21)
    def _get_contact_opportunities_domain(self):
        pass  # shrunk (lines 23-24)
    def _compute_opportunity_count(self):
        pass  # shrunk (lines 26-39)
    def _compute_application_statistics_hook(self):
        pass  # shrunk (lines 41-49)
    def action_view_opportunity(self):
        pass  # shrunk (lines 51-62)


# FILEPATH: odoo/addons/crm/models/res_users.py
class ResUsers(models.Model):
    _inherit = "res.users"
    @api.depends_context(
    'crm_formatted_display_name_team',
    'formatted_display_name')
    def _compute_display_name(self):
        pass  # shrunk (lines 7-17)


# FILEPATH: odoo/addons/crm/models/utm.py
class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    use_leads = fields.Boolean('Use Leads', compute='_compute_use_leads')
    crm_lead_count = fields.Integer('Leads/Opportunities count', groups='sales_team.group_sale_salesman', compute="_compute_crm_lead_count")

    def _compute_use_leads(self):
        self.use_leads = self.env.user.has_group('crm.group_use_lead')

    def _compute_crm_lead_count(self):
        lead_data = self.env['crm.lead'].with_context(active_test=False)._read_group([
            ('campaign_id', 'in', self.ids)],
            ['campaign_id'], ['__count'])
        mapped_data = {campaign.id: count for campaign, count in lead_data}
        for campaign in self:
            campaign.crm_lead_count = mapped_data.get(campaign.id, 0)

    def action_redirect_to_leads_opportunities(self):
        view = 'crm.crm_lead_all_leads' if self.use_leads else 'crm.crm_lead_opportunities'
        action = self.env['ir.actions.act_window']._for_xml_id(view)
        action['view_mode'] = 'list,kanban,graph,pivot,form,calendar'
        action['domain'] = [('campaign_id', 'in', self.ids)]
        action['context'] = {'active_test': False, 'create': False}
        return action


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


# FILEPATH: odoo/addons/phone_validation/__manifest__.py
{   'data': [   'security/ir.model.access.csv',
                'views/phone_blacklist_views.xml',
                'views/res_partner_views.xml',
                'wizard/phone_blacklist_remove_view.xml'],
    'depends': ['base', 'mail'],
    'name': 'Phone Numbers Validation',
    'summary': 'Validate and format phone numbers'}

# FILEPATH: odoo/addons/phone_validation/models/mail_thread_phone.py
PHONE_REGEX_PATTERN = r'[\s\\./\(\)\-]'
class MailThreadPhone(models.AbstractModel):
    _name = 'mail.thread.phone'
    _description = 'Phone Blacklist Mixin'
    _inherit = ['mail.thread']
    _phone_search_min_length = 3
    # Shrunk non computed fields: phone_mobile_search
    # Shrunk computed_fields: phone_sanitized (_compute_phone_sanitized), phone_sanitized_blacklisted (_compute_blacklisted), phone_blacklisted (_compute_blacklisted)


# FILEPATH: odoo/addons/phone_validation/models/models.py
class Base(models.AbstractModel):
    _inherit = 'base'


# FILEPATH: odoo/addons/phone_validation/models/phone_blacklist.py
class PhoneBlacklist(models.Model):
    _name = 'phone.blacklist'
    _inherit = ['mail.thread']


# FILEPATH: odoo/addons/phone_validation/models/res_partner.py
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['mail.thread.phone', 'res.partner']


# FILEPATH: odoo/addons/phone_validation/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'


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
    _description = "CRM Tag"
    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!')
    # Shrunk non computed fields: name, color


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
