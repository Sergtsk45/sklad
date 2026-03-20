Role: Senior Odoo Architect enforcing OCA standards.
Context: The following is a codebase dump produced by the akaidoo CLI.
Command: /home/serg45/.local/bin/akaidoo addon stock -c akaidoo.conf --shrink=hard -B 30k -o custom_addons/ai_assistant/static/knowledge/generated/stock_context.md
Conventions:
1. Files start with `# FILEPATH: [path]`.
2. Some files were filtered out to save tokens; ask for them if you need.
3. `# shrunk` indicates code removed to save tokens; ask for full content if a specific logic flow is unclear.
4. Method definitions were eventually entirely skipped to save tokens and focus on the data model only.

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


# FILEPATH: odoo/addons/stock/__init__.py
def pre_init_hook(env):
    pass  # shrunk (lines 11-15)

def _assign_default_mail_template_picking_id(env):
    pass  # shrunk (lines 17-25)

def uninstall_hook(env):
    pass  # shrunk (lines 27-29)


# FILEPATH: odoo/addons/stock/__manifest__.py

{
    'name': 'Inventory',
    'version': '1.1',
    'summary': 'Manage your stock and logistics activities',
    'website': 'https://www.odoo.com/app/inventory',
    'depends': ['product', 'barcodes_gs1_nomenclature', 'digest'],
    'category': 'Supply Chain/Inventory',
    'sequence': 25,
    'demo': [
        'data/stock_demo_pre.xml',
        'data/stock_demo.xml',
        'data/stock_demo2.xml',
        'data/stock_orderpoint_demo.xml',
        'data/stock_storage_category_demo.xml',
    ],
    'data': [
        'security/stock_security.xml',
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
        'views/uom_uom_views.xml',
    ],
    'installable': True,
    'application': True,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': '_assign_default_mail_template_picking_id',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.report_assets_common': [
            'stock/static/src/scss/report_stock_reception.scss',
            'stock/static/src/scss/report_stock_rule.scss',
            'stock/static/src/scss/report_stockpicking_operations.scss',
        ],
        'web.assets_backend': [
            'stock/static/src/**/*.js',
            'stock/static/src/**/*.xml',
            'stock/static/src/**/*.scss',
            ('remove', 'stock/static/src/stock_forecasted/forecasted_graph.*'),
        ],
        'web.assets_backend_lazy': [
            'stock/static/src/stock_forecasted/forecasted_graph.*',
        ],
        'web.assets_frontend': [
            'stock/static/src/scss/stock_traceability_report.scss',
        ],
        'web.assets_tests': [
            'stock/static/tests/tours/*.js',
        ],
        'web.assets_unit_tests': [
            'stock/static/tests/*.test.js',
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}


# FILEPATH: odoo/addons/stock/models/barcode.py
class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'
    type = fields.Selection(selection_add=[
        ('weight', 'Weighted Product'),
        ('location', 'Location'),
        ('lot', 'Lot'),
        ('package', 'Package')
    ], ondelete={
        'weight': 'set default',
        'location': 'set default',
        'lot': 'set default',
        'package': 'set default',
    })


# FILEPATH: odoo/addons/stock/models/ir_actions_report.py
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'
    def _get_rendering_context(self, report, docids, data):
        pass  # shrunk (lines 7-16)


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

    stock_quant_ids = fields.One2many('stock.quant', 'product_id') # used to compute quantities
    stock_move_ids = fields.One2many('stock.move', 'product_id') # used to compute quantities
    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        inverse='_inverse_qty_available', digits='Product Unit', compute_sudo=False,
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    virtual_available = fields.Float(
        'Forecasted Quantity', compute='_compute_quantities', search='_search_virtual_available',
        digits='Product Unit', compute_sudo=False,
        help="Forecast quantity (computed as Quantity On Hand "
             "- Outgoing + Incoming)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    free_qty = fields.Float(
        'Free To Use Quantity ', compute='_compute_quantities', search='_search_free_qty',
        digits='Product Unit', compute_sudo=False,
        help="Available quantity (computed as Quantity On Hand "
             "- reserved quantity)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    incoming_qty = fields.Float(
        'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
        digits='Product Unit', compute_sudo=False,
        help="Quantity of planned incoming products.\n"
             "In a context with a single Stock Location, this includes "
             "goods arriving to this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods arriving to the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods arriving to any Stock "
             "Location with 'internal' type.")
    outgoing_qty = fields.Float(
        'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
        digits='Product Unit', compute_sudo=False,
        help="Quantity of planned outgoing products.\n"
             "In a context with a single Stock Location, this includes "
             "goods leaving this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods leaving the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods leaving any Stock "
             "Location with 'internal' type.")

    orderpoint_ids = fields.One2many('stock.warehouse.orderpoint', 'product_id', 'Minimum Stock Rules')
    nbr_moves_in = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False, help="Number of incoming stock moves in the past 12 months")
    nbr_moves_out = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False, help="Number of outgoing stock moves in the past 12 months")
    nbr_reordering_rules = fields.Integer('Reordering Rules',
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    reordering_min_qty = fields.Float(
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    reordering_max_qty = fields.Float(
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'product_id', 'Putaway Rules')
    storage_category_capacity_ids = fields.One2many('stock.storage.category.capacity', 'product_id', 'Storage Category Capacity')
    show_on_hand_qty_status_button = fields.Boolean(compute='_compute_show_qty_status_button')
    show_forecasted_qty_status_button = fields.Boolean(compute='_compute_show_qty_status_button')
    show_qty_update_button = fields.Boolean(compute='_compute_show_qty_update_button')
    valid_ean = fields.Boolean('Barcode is valid EAN', compute='_compute_valid_ean')
    lot_properties_definition = fields.PropertiesDefinition('Lot Properties')

    @api.depends('product_tmpl_id')
    def _compute_show_qty_status_button(self):
        for product in self:
            product.show_on_hand_qty_status_button = product.product_tmpl_id.show_on_hand_qty_status_button
            product.show_forecasted_qty_status_button = product.product_tmpl_id.show_forecasted_qty_status_button

    @api.depends('product_tmpl_id')
    def _compute_show_qty_update_button(self):
        for product in self:
            product.show_qty_update_button = product.product_tmpl_id._should_open_product_quants()

    @api.depends('barcode')
    def _compute_valid_ean(self):
        self.valid_ean = False
        for product in self:
            if product.barcode:
                product.valid_ean = check_barcode_encoding(product.barcode.rjust(14, '0'), 'gtin14')

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.quantity')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse_id', 'allowed_company_ids', 'is_storable'
    )
    def _compute_quantities(self):
        products = self.with_context(prefetch_fields=False).filtered(lambda p: p.type != 'service').with_context(prefetch_fields=True)
        res = products._compute_quantities_dict(self.env.context.get('lot_id'), self.env.context.get('owner_id'), self.env.context.get('package_id'), self.env.context.get('from_date'), self.env.context.get('to_date'))
        # Set qty fields to 0 for all products as services have 0 quantities. Also skips calling __setitem__ on products with 0 quantites in res.
        self.with_context(skip_qty_available_update=True).qty_available = 0.0
        self.incoming_qty = 0.0
        self.outgoing_qty = 0.0
        self.virtual_available = 0.0
        self.free_qty = 0.0
        for product in products:
            product.with_context(skip_qty_available_update=True).update({key: val for key, val in res[product.id].items() if val})

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        original_value = to_date
        to_date = fields.Datetime.to_datetime(to_date)
        if (isinstance(original_value, date) and not isinstance(original_value, datetime)) or \
            (isinstance(original_value, str) and len(original_value) == 10):
            to_date = datetime.combine(to_date.date(), time.max)

        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
            domain_move_in += [('move_line_ids.lot_id', '=', lot_id)]
            domain_move_out += [('move_line_ids.lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if 'owners' in self.env.context:
            owners = self.env.context['owners']
            if owners:
                domain_quant += [('owner_id', 'in', self.env.context['owners'])]
            else:
                domain_quant += [('owner_id', '=', False)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [('date', '>=', from_date)]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [('date', '<=', to_date)]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to
        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_in_todo, ['product_id'], ['product_qty:sum'])}
        moves_out_res = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_out_todo, ['product_id'], ['product_qty:sum'])}
        quants_res = {product.id: (quantity, reserved_quantity) for product, quantity, reserved_quantity in Quant._read_group(domain_quant, ['product_id'], ['quantity:sum', 'reserved_quantity:sum'])}
        expired_unreserved_quants_res = {}
        if self.env.context.get('with_expiration'):
            max_date = self.env.context['to_date'] if self.env.context.get('to_date') else self.env.context['with_expiration']
            domain_quant += [('removal_date', '<=', max_date)]
            expired_unreserved_quants_res = {product.id: quantity - reserved_quantity for product, quantity, reserved_quantity in Quant._read_group(domain_quant, ['product_id'], ['quantity:sum', 'reserved_quantity:sum'])}
        moves_in_res_past = defaultdict(float)
        moves_out_res_past = defaultdict(float)
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            groupby = ['product_id', 'product_uom']
            for product, uom, quantity in Move._read_group(domain_move_in_done, groupby, ['quantity:sum']):
                moves_in_res_past[product.id] += uom._compute_quantity(quantity, product.uom_id)

            for product, uom, quantity in Move._read_group(domain_move_out_done, groupby, ['quantity:sum']):
                moves_out_res_past[product.id] += uom._compute_quantity(quantity, product.uom_id)

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            origin_product_id = product._origin.id
            product_id = product.id
            if not origin_product_id or (
                origin_product_id not in quants_res
                and origin_product_id not in moves_in_res
                and origin_product_id not in moves_out_res
                and origin_product_id not in moves_in_res_past
                and origin_product_id not in moves_out_res_past
                and origin_product_id not in expired_unreserved_quants_res
            ):
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
                    0.0,
                )
                continue
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
            else:
                qty_available = quants_res.get(origin_product_id, [0.0])[0]
            reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
            expired_unreserved_qty = expired_unreserved_quants_res.get(origin_product_id, 0.0)
            res[product_id]['qty_available'] = product.uom_id.round(qty_available)
            res[product_id]['free_qty'] = product.uom_id.round(qty_available - reserved_quantity - expired_unreserved_qty)
            res[product_id]['incoming_qty'] = product.uom_id.round(moves_in_res.get(origin_product_id, 0.0))
            res[product_id]['outgoing_qty'] = product.uom_id.round(moves_out_res.get(origin_product_id, 0.0))
            res[product_id]['virtual_available'] = product.uom_id.round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'] - expired_unreserved_qty,
            )

        return res

    def _inverse_qty_available(self):
        """
        Inverse method for the 'qty_available' field, enabling manual adjustment of stock on hand quantity
        in the product form. To prevent the automatic creation of stock quants when the
        'compute_quantities' method is triggered, this method skips quant creation by custom context key.
        """
        if self.env.context.get('skip_qty_available_update', False):
            return
        for product in self:
            if (
                product.type == "consu" and product.is_storable and float_compare(product.qty_available,
                     0.0, precision_rounding=product.uom_id.rounding) >= 0
            ):
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', self.env.company.id)], limit=1
                )
                self.env['stock.quant'].with_context(inventory_mode=True, from_inverse_qty=True).create({
                    'product_id': product.id,
                    'location_id': warehouse.lot_stock_id.id,
                    'inventory_quantity': product.qty_available,
                })._apply_inventory()

    def _compute_nbr_moves(self):
        incoming_moves = self.env['stock.move.line']._read_group([
                ('product_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'incoming'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['__count'])
        outgoing_moves = self.env['stock.move.line']._read_group([
                ('product_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'outgoing'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['__count'])
        res_incoming = {product.id: count for product, count in incoming_moves}
        res_outgoing = {product.id: count for product, count in outgoing_moves}
        for product in self:
            product.nbr_moves_in = res_incoming.get(product.id, 0)
            product.nbr_moves_out = res_outgoing.get(product.id, 0)

    def get_components(self):
        self.ensure_one()
        return self.ids

    def get_total_routes(self):
        # Extend the total routes in other modules
        return self.env['stock.route']

    def _get_description(self, picking_type_id):
        """
            Return product description based on the picking type:
            * For outgoing pickings, we always use the product name.
            * For all other pickings, we try to use the product description (if one has been set),
              otherwise we fall back to the product name.
        """
        self.ensure_one()
        if picking_type_id.code == 'outgoing':
            return self.display_name
        return html2plaintext(self.description) if not is_html_empty(self.description) else self.display_name

    def _get_picking_description(self, picking_type_id):
        """
        Return product receipt/delivery/picking description depending on picking type passed as argument.
        """
        return {
            'incoming': self.description_pickingin,
            'outgoing': self.description_pickingout,
            'internal': self.description_picking
        }.get(picking_type_id.code, '')

    def _get_domain_locations(self):
        '''
        Parses the context and returns a list of location_ids based on it.
        It will return all stock locations when no parameters are given
        Possible parameters are shop, warehouse, location, compute_child
        '''
        Location = self.env['stock.location']
        Warehouse = self.env['stock.warehouse']

        def _search_ids(model, values):
            ids = set()
            domains = []
            for item in values:
                if isinstance(item, int):
                    ids.add(item)
                else:
                    domains.append(Domain(self.env[model]._rec_name, 'ilike', item))
            if domains:
                ids |= set(self.env[model].search(Domain.OR(domains)).ids)
            return ids

        # We may receive a location or warehouse from the context, either by explicit
        # python code or by the use of dummy fields in the search view.
        # Normalize them into a list.
        location = self.env.context.get('location') or self.env.context.get('search_location')
        if location and not isinstance(location, list):
            location = [location]
        warehouse = self.env.context.get('warehouse_id') or self.env.context.get('search_warehouse')
        if warehouse and not isinstance(warehouse, list):
            warehouse = [warehouse]
        # filter by location and/or warehouse
        if warehouse:
            w_ids = set(Warehouse.browse(_search_ids('stock.warehouse', warehouse)).mapped('view_location_id').ids)
            if location:
                l_ids = _search_ids('stock.location', location)
                parents = Location.browse(w_ids).mapped("parent_path")
                location_ids = {
                    loc.id
                    for loc in Location.browse(l_ids)
                    if any(loc.parent_path.startswith(parent) for parent in parents)
                }
            else:
                location_ids = w_ids
        else:
            if location:
                location_ids = _search_ids('stock.location', location)
            else:
                location_ids = set(Warehouse.search(
                    [('company_id', 'in', self.env.companies.ids)]
                ).mapped('view_location_id').ids)

        return self._get_domain_locations_new(location_ids)

    def _get_domain_locations_new(self, location_ids) -> tuple[Domain, Domain, Domain]:
        if not location_ids:
            return (Domain.FALSE,) * 3
        locations = self.env['stock.location'].browse(location_ids)
        # TDE FIXME: should move the support of child_of + bypass_search_access directly in expression
        # this optimizes [('location_id', 'child_of', locations.ids)]
        # by avoiding the ORM to search for children locations and injecting a
        # lot of location ids into the main query
        if self.env.context.get('strict'):
            loc_domain = Domain('location_id', 'in', locations.ids)
            dest_loc_domain = Domain('location_dest_id', 'in', locations.ids)
            dest_loc_domain_out = Domain('location_dest_id', 'not in', locations.ids)
        elif locations:
            alias = locations._table + '_inner'
            paths_query = Query(locations.env, alias, SQL.identifier(locations._table))
            paths_query.add_where(SQL(
                """EXISTS (
                    SELECT 1
                      FROM stock_location parent
                     WHERE parent.id IN %s
                       AND %s LIKE parent.parent_path || '%%'
                )""",
                tuple(locations.ids),
                SQL.identifier(alias, 'parent_path'),
            ))
            loc_domain = Domain('location_id', 'in', paths_query)
            # The condition should be split for done and not-done moves as the final_dest_id only make sense
            # for the part of the move chain that is not done yet.
            dest_loc_domain_done = Domain('location_dest_id', 'in', paths_query)
            dest_loc_domain_in_progress = Domain([
                '|',
                    '&', ('location_final_id', '!=', False), ('location_final_id', 'in', paths_query),
                    '&', ('location_final_id', '=', False), ('location_dest_id', 'in', paths_query),
            ])
            dest_loc_domain = Domain([
                '|',
                    '&', ('state', '=', 'done'), dest_loc_domain_done,
                    '&', ('state', '!=', 'done'), dest_loc_domain_in_progress,
            ])
            dest_loc_domain_out = Domain([
                '|',
                    '&', ('state', '=', 'done'), ~dest_loc_domain_done,
                    '&', ('state', '!=', 'done'), ~dest_loc_domain_in_progress,
            ])
            if self.env.context.get('skip_in_progress'):
                return (
                    loc_domain,
                    dest_loc_domain_done & ~loc_domain,
                    loc_domain & ~dest_loc_domain_done
                )

        # returns: (domain_quant_loc, domain_move_in_loc, domain_move_out_loc)
        return (
            loc_domain,
            dest_loc_domain & ~loc_domain,
            loc_domain & dest_loc_domain_out,
        )

    def _search_qty_available(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_search_qty_available_new' instead. This
        # allows better performances.
        if not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        return self._search_product_quantity(operator, value, 'qty_available')

    def _search_virtual_available(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'virtual_available')

    def _search_incoming_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'incoming_qty')

    def _search_outgoing_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'outgoing_qty')

    def _search_free_qty(self, operator, value):
        return self._search_product_quantity(operator, value, 'free_qty')

    def _search_product_quantity(self, operator, value, field):
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search.
        ids = self.with_context(prefetch_fields=False).search_fetch([], [field], order='id').filtered_domain([(field, operator, value)]).ids
        return [('id', 'in', ids)]

    def _search_qty_available_new(self, operator, value, lot_id=False, owner_id=False, package_id=False):
        ''' Optimized method which doesn't search on stock.moves, only on stock.quants. '''
        op = PY_OPERATORS.get(operator)
        if not op:
            return NotImplemented
        if isinstance(value, Iterable) and not isinstance(value, str):
            value = {float(v) for v in value}
        else:
            value = float(value)

        product_ids = set()
        domain_quant = self._get_domain_locations()[0]
        if lot_id:
            domain_quant.append(('lot_id', '=', lot_id))
        if owner_id:
            domain_quant.append(('owner_id', '=', owner_id))
        if package_id:
            domain_quant.append(('package_id', '=', package_id))
        quants_groupby = self.env['stock.quant']._read_group(domain_quant, ['product_id'], ['quantity:sum'])

        # check if we need include zero values in result
        include_zero = op(0.0, value)

        processed_product_ids = set()
        for product, quantity_sum in quants_groupby:
            product_id = product.id
            if include_zero:
                processed_product_ids.add(product_id)
            if op(quantity_sum, value):
                product_ids.add(product_id)

        if include_zero:
            products_without_quants_in_domain = self.env['product.product'].search([
                ('is_storable', '=', True),
                ('id', 'not in', list(processed_product_ids))],
                order='id'
            )
            product_ids |= set(products_without_quants_in_domain.ids)
        return list(product_ids)

    def _compute_nbr_reordering_rules(self):
        read_group_res = self.env['stock.warehouse.orderpoint']._read_group(
            [('product_id', 'in', self.ids)],
            ['product_id'],
            ['__count', 'product_min_qty:sum', 'product_max_qty:sum'])
        mapped_res = {product: aggregates for product, *aggregates in read_group_res}
        for product in self:
            count, product_min_qty_sum, product_max_qty_sum = mapped_res.get(product._origin, (0, 0, 0))
            product.nbr_reordering_rules = count
            product.reordering_min_qty = product_min_qty_sum
            product.reordering_max_qty = product_max_qty_sum

    @api.onchange('tracking')
    def _onchange_tracking(self):
        if any(product.tracking != 'none' and product.qty_available > 0 for product in self):
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _("You have product(s) in stock that have no lot/serial number. You can assign lot/serial numbers by doing an inventory adjustment.")}}

    @api.model
    def view_header_get(self, view_id, view_type):
        res = super().view_header_get(view_id, view_type)
        if not res and self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.location':
            return _(
                'Products: %(location)s',
                location=self.env['stock.location'].browse(self.env.context['active_id']).name,
            )
        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        context_location = self.env.context.get('location') or self.env.context.get('search_location')
        if context_location and isinstance(context_location, int):
            location = self.env['stock.location'].browse(context_location)
            if location.usage == 'supplier':
                if res.get('virtual_available'):
                    res['virtual_available']['string'] = _('Future Receipts')
                if res.get('qty_available'):
                    res['qty_available']['string'] = _('Received Qty')
            elif location.usage == 'internal':
                if res.get('virtual_available'):
                    res['virtual_available']['string'] = _('Forecasted Quantity')
            elif location.usage == 'customer':
                if res.get('virtual_available'):
                    res['virtual_available']['string'] = _('Future Deliveries')
                if res.get('qty_available'):
                    res['qty_available']['string'] = _('Delivered Qty')
            elif location.usage == 'inventory':
                if res.get('virtual_available'):
                    res['virtual_available']['string'] = _('Future P&L')
                if res.get('qty_available'):
                    res['qty_available']['string'] = _('P&L Qty')
            elif location.usage == 'production':
                if res.get('virtual_available'):
                    res['virtual_available']['string'] = _('Future Productions')
                if res.get('qty_available'):
                    res['qty_available']['string'] = _('Produced Qty')
        return res

    def action_view_orderpoints(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_orderpoint")
        action['context'] = literal_eval(action.get('context'))
        action['context'].pop('search_default_trigger', False)
        action['context'].update({
            'search_default_filter_not_snoozed': True,
        })
        if self and len(self) == 1:
            action['context'].update({
                'default_product_id': self.ids[0],
                'search_default_product_id': self.ids[0]
            })
        else:
            action['domain'] = Domain(action.get('domain') or Domain.TRUE) & Domain('product_id', 'in', self.ids)
        return action

    def action_view_routes(self):
        return self.mapped('product_tmpl_id').action_view_routes()

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [('product_id', '=', self.id)]
        return action

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            '|',
                ('product_id', '=', self.id),
                ('category_id', '=', self.product_tmpl_id.categ_id.id),
        ]
        return self.env['product.template']._get_action_view_related_putaway_rules(domain)

    def action_view_storage_category_capacity(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_storage_category_capacity")
        action['context'] = {
            'hide_package_type': True,
        }
        if len(self) == 1:
            action['context'].update({
                'default_product_id': self.id,
            })
        action['domain'] = [('product_id', 'in', self.ids)]
        return action

    def action_open_product_lot(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_product_production_lot_form")
        action['domain'] = [
            ('product_id', '=', self.id),
            '|', ('location_id', '=', False),
                 ('location_id', 'any', self.env['stock.location']._check_company_domain(self.env.context['allowed_company_ids']))
        ]
        action['context'] = {
            'default_product_id': self.id,
            'set_product_readonly': True,
            'search_default_group_by_location': True,
        }
        return action

    # Be aware that the exact same function exists in product.template
    def action_open_quants(self):
        hide_location = not self.env.user.has_group('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.env.user.has_group('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.env.user.has_group('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env['stock.quant'].action_view_quants()
        # note that this action is used by different views w/varying customizations
        if not self.env.context.get('is_stock_report'):
            action['domain'] = [('product_id', 'in', self.ids)]
            action["name"] = _('Update Quantity')
        return action

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_forecasted_product_product_action")
        return action

    def write(self, vals):
        if 'active' in vals:
            self.filtered(lambda p: p.active != vals['active']).with_context(active_test=False).orderpoint_ids.write({
                'active': vals['active']
            })
        return super().write(vals)

    def _get_quantity_in_progress(self, location_ids=False, warehouse_ids=False):
        return defaultdict(float), defaultdict(float)

    def _get_rules_from_location(self, location, route_ids=False, seen_rules=False):
        if not seen_rules:
            seen_rules = self.env['stock.rule']
        warehouse = location.warehouse_id
        rule = self.env['stock.rule'].with_context(active_test=True)._get_rule(self, location, {
            'route_ids': route_ids,
            'warehouse_id': warehouse,
        })
        if rule in seen_rules:
            raise UserError(_("Invalid rule's configuration, the following rule causes an endless loop: %s", rule.display_name))
        if not rule:
            return seen_rules
        if rule.procure_method == 'make_to_stock' or rule.action not in ('pull_push', 'pull'):
            return seen_rules | rule
        else:
            return self._get_rules_from_location(rule.location_src_id, seen_rules=seen_rules | rule)

    def _get_dates_info(self, date, location, route_ids=False):
        rules = self._get_rules_from_location(location, route_ids=route_ids)
        delays, _ = rules.with_context(bypass_delay_description=True)._get_lead_days(self)
        return {
            'date_planned': date,
            'date_order': date - relativedelta(days=delays['purchase_delay']),
        }

    def _get_only_qty_available(self):
        """ Get only quantities available, it is equivalent to read qty_available
        but avoid fetching other qty fields (avoid costly read group on moves)

        :rtype: defaultdict(float)
        """
        domain_quant = Domain.AND([self._get_domain_locations()[0], [('product_id', 'in', self.ids)]])
        quants_groupby = self.env['stock.quant']._read_group(domain_quant, ['product_id'], ['quantity:sum'])
        currents = defaultdict(float)
        currents.update({product.id: quantity for product, quantity in quants_groupby})
        return currents

    def _filter_to_unlink(self):
        domain = [('product_id', 'in', self.ids)]
        lines = self.env['stock.lot']._read_group(domain, ['product_id'])
        linked_product_ids = [product.id for [product] in lines]
        return super(ProductProduct, self - self.browse(linked_product_ids))._filter_to_unlink()

    @api.model
    def _count_returned_sn_products(self, sn_lot):
        domain = self._count_returned_sn_products_domain(sn_lot, or_domains=[])
        if not domain:
            return 0
        return self.env['stock.move.line'].search_count(domain)

    @api.model
    def _count_returned_sn_products_domain(self, sn_lot, or_domains):
        if not or_domains:
            return None
        return Domain([
            ('lot_id', '=', sn_lot.id),
            ('quantity', '=', 1),
            ('state', '=', 'done'),
        ]) & Domain.OR(or_domains)

    def _update_uom(self, to_uom_id):
        for uom, product, moves in self.env['stock.move']._read_group(
            [('product_id', 'in', self.ids)],
            ['product_uom', 'product_id'],
            ['id:recordset'],
        ):
            if uom != product.product_tmpl_id.uom_id:
                raise UserError(_('As other units of measure (ex : %(problem_uom)s) '
                'than %(uom)s have already been used for this product, the change of unit of measure can not be done.'
                'If you want to change it, please archive the product and create a new one.',
                problem_uom=uom.name, uom=product.product_tmpl_id.uom_id.name))
            moves.product_uom = to_uom_id

        for uom, product, move_lines in self.env['stock.move.line']._read_group(
            [('product_id', 'in', self.ids)],
            ['product_uom_id', 'product_id'],
            ['id:recordset'],
        ):
            if uom != product.product_tmpl_id.uom_id:
                raise UserError(_('As other units of measure (ex : %(problem_uom)s) '
                'than %(uom)s have already been used for this product, the change of unit of measure can not be done.'
                'If you want to change it, please archive the product and create a new one.',
                problem_uom=uom.name, uom=product.product_tmpl_id.uom_id.name))
            move_lines.product_uom_id = to_uom_id
        return super()._update_uom(to_uom_id)

    def filter_has_routes(self):
        """ Return products with route_ids
            or whose categ_id has total_route_ids.
        """
        products_with_routes = self.env['product.product']
        # retrieve products with route_ids
        products_with_routes += self.search([('id', 'in', self.ids), ('route_ids', '!=', False)])
        # retrive products with categ_ids having routes
        products_with_routes += self.search([('id', 'in', (self - products_with_routes).ids), ('categ_id.total_route_ids', '!=', False)])
        return products_with_routes

    def _trigger_uom_warning(self):
        res = super()._trigger_uom_warning()
        if res:
            return res
        moves = self.env['stock.move'].sudo().search_count(
            [('product_id', 'in', self.ids)], limit=1
        )
        return bool(moves)


# FILEPATH: odoo/addons/stock/models/product.py (lines 801-1224)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    def _default_responsible_id(self):
        # Return the current user unless it's OdooBot
        return not self.env.user._is_superuser() and self.env.uid

    is_storable = fields.Boolean(
        'Track Inventory', store=True, compute='compute_is_storable', readonly=False,
        default=False, precompute=True, tracking=True, help='A storable product is a product for which you manage stock.')
    responsible_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self._default_responsible_id(), company_dependent=True, check_company=True,
        help="This user will be responsible of the next activities related to logistic operations for this product.")
    property_stock_production = fields.Many2one(
        'stock.location', "Production Location",
        company_dependent=True, check_company=True, domain="[('usage', '=', 'production'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves generated by manufacturing orders.")
    property_stock_inventory = fields.Many2one(
        'stock.location', "Inventory Location",
        company_dependent=True, check_company=True, domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves generated when you do an inventory.")
    sale_delay = fields.Integer(
        'Customer Lead Time', default=0,
        help="Delivery lead time, in days. It's the number of days, promised to the customer, between the confirmation of the sales order and the delivery.")
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'By Quantity')],
        string="Tracking", required=True, default='none', # Not having a default value here causes issues when migrating.
        compute='_compute_tracking', store=True, readonly=False, precompute=True,
        help="Ensure the traceability of a storable product in your warehouse.")
    lot_sequence_id = fields.Many2one(
        'ir.sequence', 'Serial/Lot Numbers Sequence', default=lambda self: self.env.ref('stock.sequence_production_lots', raise_if_not_found=False),
        help='Technical Field: The Ir.Sequence record that is used to generate serial/lot numbers for this product')
    serial_prefix_format = fields.Char(
        'Custom Lot/Serial', compute='_compute_serial_prefix_format', inverse='_inverse_serial_prefix_format',
        help=SERIAL_PREFIX_FORMAT_HELP_TEXT)
    next_serial = fields.Char(compute='_compute_next_serial')
    description_picking = fields.Text('Description on Picking', translate=True)
    description_pickingout = fields.Text('Description on Delivery Orders', translate=True)
    description_pickingin = fields.Text('Description on Receptions', translate=True)
    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        inverse='_inverse_qty_available',compute_sudo=False, digits='Product Unit')
    virtual_available = fields.Float(
        'Forecasted Quantity', compute='_compute_quantities', search='_search_virtual_available',
        compute_sudo=False, digits='Product Unit')
    incoming_qty = fields.Float(
        'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
        compute_sudo=False, digits='Product Unit')
    outgoing_qty = fields.Float(
        'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
        compute_sudo=False, digits='Product Unit')
    # The goal of these fields is to be able to put some keys in context from search view in order
    # to influence computed field.
    location_id = fields.Many2one('stock.location', 'Location', store=False)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', store=False)
    has_available_route_ids = fields.Boolean(
        'Routes can be selected on this product', compute='_compute_has_available_route_ids',
        default=lambda self: self.env['stock.route'].search_count([('product_selectable', '=', True)]))
    route_ids = fields.Many2many(
        'stock.route', 'stock_route_product', 'product_id', 'route_id', 'Routes',
        domain=[('product_selectable', '=', True)], depends_context=['company', 'allowed_companies'],
        help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, replenished on order, etc.")
    nbr_moves_in = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False, help="Number of incoming stock moves in the past 12 months")
    nbr_moves_out = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False, help="Number of outgoing stock moves in the past 12 months")
    nbr_reordering_rules = fields.Integer('Reordering Rules',
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    reordering_min_qty = fields.Float(
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    reordering_max_qty = fields.Float(
        compute='_compute_nbr_reordering_rules', compute_sudo=False)
    # TDE FIXME: seems only visible in a view - remove me ?
    route_from_categ_ids = fields.Many2many(
        string="Category Routes", related='categ_id.total_route_ids', related_sudo=False)
    show_on_hand_qty_status_button = fields.Boolean(compute='_compute_show_qty_status_button')
    show_forecasted_qty_status_button = fields.Boolean(compute='_compute_show_qty_status_button')
    show_qty_update_button = fields.Boolean(compute='_compute_show_qty_update_button')

    @api.depends('type')
    def compute_is_storable(self):
        self.filtered(lambda t: t.type != 'consu' and t.is_storable).is_storable = False

    @api.depends('lot_sequence_id', 'lot_sequence_id.prefix')
    def _compute_serial_prefix_format(self):
        for template in self:
            template.serial_prefix_format = template.lot_sequence_id.prefix or ""

    def _inverse_serial_prefix_format(self):
        valid_sequences = self.env['ir.sequence'].search([('prefix', 'in', self.mapped('serial_prefix_format'))])
        sequences_by_prefix = {seq.prefix: seq for seq in valid_sequences}
        for template in self:
            if template.serial_prefix_format:
                if template.serial_prefix_format in sequences_by_prefix:
                    template.lot_sequence_id = sequences_by_prefix[template.serial_prefix_format]
                else:
                    new_sequence = self.env['ir.sequence'].create({
                        'name': f'{template.name} Serial Sequence',
                        'code': 'stock.lot.serial',
                        'prefix': template.serial_prefix_format,
                        'padding': 7,
                        'company_id': False,
                    })
                    template.lot_sequence_id = new_sequence
                    sequences_by_prefix[template.serial_prefix_format] = new_sequence
            else:
                template.lot_sequence_id = self.env.ref('stock.sequence_production_lots', raise_if_not_found=False)

    @api.depends('lot_sequence_id.number_next_actual')
    def _compute_next_serial(self):
        for template in self:
            if template.lot_sequence_id:
                template.next_serial = '{:0{}d}{}'.format(
                    template.lot_sequence_id.number_next_actual,
                    template.lot_sequence_id.padding,
                    template.lot_sequence_id.suffix or ""
                )
            else:
                template.next_serial = '0000001'

    @api.depends('is_storable')
    def _compute_show_qty_status_button(self):
        for template in self:
            template.show_on_hand_qty_status_button = template.is_storable
            template.show_forecasted_qty_status_button = template.is_storable

    @api.depends('is_storable')
    def _compute_has_available_route_ids(self):
        self.has_available_route_ids = self.env['stock.route'].search_count([('product_selectable', '=', True)])

    @api.depends('product_variant_count', 'tracking')
    def _compute_show_qty_update_button(self):
        for product in self:
            product.show_qty_update_button = (
                product._should_open_product_quants()
                or product.product_variant_count > 1
            )

    @api.depends(
        'product_variant_ids.qty_available',
        'product_variant_ids.virtual_available',
        'product_variant_ids.incoming_qty',
        'product_variant_ids.outgoing_qty',
        'tracking',
    )
    @api.depends_context('warehouse_id')
    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self.with_context(skip_qty_available_update=True):
            template.qty_available = res[template.id]['qty_available']
            template.virtual_available = res[template.id]['virtual_available']
            template.incoming_qty = res[template.id]['incoming_qty']
            template.outgoing_qty = res[template.id]['outgoing_qty']

    def _compute_quantities_dict(self):
        variants_available = {
            p['id']: p for p in self.product_variant_ids._origin.read(['qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'])
        }
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            for p in template.product_variant_ids._origin:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }
        return prod_available

    def _compute_nbr_moves(self):
        res = defaultdict(lambda: {'moves_in': 0, 'moves_out': 0})
        incoming_moves = self.env['stock.move.line']._read_group([
                ('product_id.product_tmpl_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'incoming'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['__count'])
        outgoing_moves = self.env['stock.move.line']._read_group([
                ('product_id.product_tmpl_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'outgoing'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['__count'])
        for product, count in incoming_moves:
            product_tmpl_id = product.product_tmpl_id.id
            res[product_tmpl_id]['moves_in'] += count
        for product, count in outgoing_moves:
            product_tmpl_id = product.product_tmpl_id.id
            res[product_tmpl_id]['moves_out'] += count
        for template in self:
            template.nbr_moves_in = res[template.id]['moves_in']
            template.nbr_moves_out = res[template.id]['moves_out']

    def _inverse_qty_available(self):
        if self.env.context.get('skip_qty_available_update', False):
            return
        for template in self:
            if template.qty_available and not template.product_variant_id:
                raise UserError(_("Save the product form before updating the Quantity On Hand."))
            else:
                template.product_variant_id.qty_available = template.qty_available

    @api.model
    def _get_action_view_related_putaway_rules(self, domain):
        return {
            'name': _('Putaway Rules'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.putaway.rule',
            'view_mode': 'list',
            'domain': domain,
        }

    def _search_qty_available(self, operator, value):
        domain = [('qty_available', operator, value)]
        product_variant_query = self.env['product.product']._search(domain)
        return [('product_variant_ids', 'in', product_variant_query)]

    def _search_virtual_available(self, operator, value):
        domain = [('virtual_available', operator, value)]
        product_variant_query = self.env['product.product']._search(domain)
        return [('product_variant_ids', 'in', product_variant_query)]

    def _search_incoming_qty(self, operator, value):
        domain = [('incoming_qty', operator, value)]
        product_variant_query = self.env['product.product']._search(domain)
        return [('product_variant_ids', 'in', product_variant_query)]

    def _search_outgoing_qty(self, operator, value):
        domain = [('outgoing_qty', operator, value)]
        product_variant_query = self.env['product.product']._search(domain)
        return [('product_variant_ids', 'in', product_variant_query)]

    def _compute_nbr_reordering_rules(self):
        res = {k: {'nbr_reordering_rules': 0, 'reordering_min_qty': 0, 'reordering_max_qty': 0} for k in self.ids}
        product_data = self.env['stock.warehouse.orderpoint']._read_group([('product_id.product_tmpl_id', 'in', self.ids)], ['product_id'], ['__count', 'product_min_qty:sum', 'product_max_qty:sum'])
        for product, count, product_min_qty, product_max_qty in product_data:
            product_tmpl_id = product.product_tmpl_id.id
            res[product_tmpl_id]['nbr_reordering_rules'] += count
            res[product_tmpl_id]['reordering_min_qty'] = product_min_qty
            res[product_tmpl_id]['reordering_max_qty'] = product_max_qty
        for template in self:
            if not template.id:
                template.nbr_reordering_rules = 0
                template.reordering_min_qty = 0
                template.reordering_max_qty = 0
                continue
            template.nbr_reordering_rules = res[template.id]['nbr_reordering_rules']
            template.reordering_min_qty = res[template.id]['reordering_min_qty']
            template.reordering_max_qty = res[template.id]['reordering_max_qty']

    @api.onchange('tracking')
    def _onchange_tracking(self):
        return self.mapped('product_variant_ids')._onchange_tracking()

    @api.depends('is_storable')
    def _compute_tracking(self):
        self.filtered(lambda t: not t.is_storable and t.tracking != 'none').tracking = 'none'

    @api.onchange('type')
    def _onchange_type(self):
        # Return a warning when trying to change the product type
        res = super()._onchange_type()
        if self.ids and self.product_variant_ids.ids and self.env['stock.move.line'].sudo().search_count([
            ('product_id', 'in', self.product_variant_ids.ids), ('state', '!=', 'cancel')
        ]):
            res['warning'] = {
                'title': _('Warning!'),
                'message': _(
                    'This product has been used in at least one inventory movement. '
                    'It is not advised to change the Product Type since it can lead to inconsistencies. '
                    'A better solution could be to archive the product and create a new one instead.'
                )
            }
        return res

    @api.model_create_multi
    def create(self, vals_list):
        product_tmpl_quantities = [
            vals.pop('qty_available', 0) for vals in vals_list
        ]

        product_templates = super().create(vals_list)

        if any(product_tmpl_quantities):
            for product_tmpl, qty in zip(product_templates, product_tmpl_quantities):
                if qty > 0 and product_tmpl.tracking == 'none':
                    product_tmpl.product_variant_id.qty_available = qty
        return product_templates

    def write(self, vals):
        if 'company_id' in vals and vals['company_id']:
            products_changing_company = self.filtered(lambda product: product.company_id.id != vals['company_id'])
            if products_changing_company:
                move = self.env['stock.move'].sudo().search([
                    ('product_id', 'in', products_changing_company.product_variant_ids.ids),
                    ('company_id', 'not in', [vals['company_id'], False]),
                ], order=None, limit=1)
                if move:
                    raise UserError(_("This product's company cannot be changed as long as there are stock moves of it belonging to another company."))

                # Forbid changing a product's company when quant(s) exist in another company.
                quant = self.env['stock.quant'].sudo().search([
                    ('product_id', 'in', products_changing_company.product_variant_ids.ids),
                    ('company_id', 'not in', [vals['company_id'], False]),
                    ('quantity', '!=', 0),
                ], order=None, limit=1)
                if quant:
                    raise UserError(_("This product's company cannot be changed as long as there are quantities of it belonging to another company."))

        clean_inventory = False
        if 'is_storable' in vals and any(vals['is_storable'] != prod_tmpl.is_storable and not prod_tmpl.is_storable for prod_tmpl in self):
            clean_inventory = True

        res = super().write(vals)
        if clean_inventory:
            self.env['stock.quant'].sudo()._clean_reservations()
        return res

    def copy(self, default=None):
        new_products = super().copy(default=default)
        # Since we don't copy product variants directly, we need to match the newly
        # created product variants with the old one, and copy the storage category
        # capacity from them.
        new_product_dict = {}
        for product in new_products.product_variant_ids:
            product_attribute_value = product.product_template_attribute_value_ids.product_attribute_value_id
            new_product_dict[product_attribute_value] = product.id
        storage_category_capacity_vals = []
        for storage_category_capacity in self.product_variant_ids.storage_category_capacity_ids:
            product_attribute_value = storage_category_capacity.product_id.product_template_attribute_value_ids.product_attribute_value_id
            storage_category_capacity_vals.append(storage_category_capacity.copy_data({'product_id': new_product_dict[product_attribute_value]})[0])
        self.env['stock.storage.category.capacity'].create(storage_category_capacity_vals)
        return new_products

    def _should_open_product_quants(self):
        self.ensure_one()
        advanced_option_groups = [
            'stock.group_stock_multi_locations',
            'stock.group_tracking_owner',
            'stock.group_tracking_lot',
        ]
        return (
            any(self.env.user.has_group(g) for g in advanced_option_groups)
            or self.tracking != "none"
        )

    # Be aware that the exact same function exists in product.product
    def action_open_quants(self):
        if 'product_variant' in self.env.context:
            return self.env['product.product'].browse(self.env.context['default_product_id']).action_open_quants()
        return self.product_variant_ids.filtered(lambda p: p.active or p.qty_available != 0).action_open_quants()

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            '|',
                ('product_id.product_tmpl_id', '=', self.id),
                ('category_id', '=', self.categ_id.id),
        ]
        return self._get_action_view_related_putaway_rules(domain)

    def action_view_storage_category_capacity(self):
        self.ensure_one()
        return self.product_variant_ids.action_view_storage_category_capacity()

    def action_view_orderpoints(self):
        return self.product_variant_ids.action_view_orderpoints()

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
        return action

    def action_open_product_lot(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_product_production_lot_form")
        action['domain'] = [
            ('product_id.product_tmpl_id', '=', self.id),
            '|', ('location_id', '=', False),
                 ('location_id', 'any', self.env['stock.location']._check_company_domain(self.env.context['allowed_company_ids']))
        ]
        action['context'] = {
            'default_product_tmpl_id': self.id,
            'search_default_group_by_location': True,
        }
        if self.product_variant_count == 1:
            action['context'].update({
                'default_product_id': self.product_variant_id.id,
            })
        return action

    def action_open_routes_diagram(self):
        products = False
        if self.env.context.get('default_product_id'):
            products = self.env['product.product'].browse(self.env.context['default_product_id'])
        if not products and self.env.context.get('default_product_tmpl_id'):
            products = self.env['product.template'].browse(self.env.context['default_product_tmpl_id']).product_variant_ids
        if not self.env.user.has_group('stock.group_stock_multi_warehouses') and len(products) == 1:
            company = products.company_id or self.env.company
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
            return self.env.ref('stock.action_report_stock_rule').report_action(None, data={
                'product_id': products.id,
                'warehouse_ids': warehouse.ids,
            }, config=False)
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_rules_report")
        action['context'] = self.env.context
        return action

    def action_product_tmpl_forecast_report(self):
        self.ensure_one()
        if not self.env.user._get_default_warehouse_id():
            self.env['stock.warehouse']._warehouse_redirect_warning()
        action = self.env["ir.actions.actions"]._for_xml_id('stock.stock_forecasted_product_template_action')
        return action


# FILEPATH: odoo/addons/stock/models/product.py (lines 1227-1288)
class ProductCategory(models.Model):
    _inherit = 'product.category'

    route_ids = fields.Many2many(
        'stock.route', 'stock_route_categ', 'categ_id', 'route_id', 'Routes',
        domain=[('product_categ_selectable', '=', True)])
    removal_strategy_id = fields.Many2one(
        'product.removal', 'Force Removal Strategy',
        help="Set a specific removal strategy that will be used regardless of the source location for this product category.\n\n"
             "FIFO: products/lots that were stocked first will be moved out first.\n"
             "LIFO: products/lots that were stocked last will be moved out first.\n"
             "Closest location: products/lots closest to the target location will be moved out first.\n"
             "FEFO: products/lots with the closest removal date will be moved out first "
             "(the availability of this method depends on the \"Expiration Dates\" setting).\n"
             "Least Packages: FIFO but with the least number of packages possible when there are several packages containing the same product.",
        tracking=True,
    )
    parent_route_ids = fields.Many2many(
        'stock.route', string='Parent Routes', compute='_compute_parent_route_ids')
    total_route_ids = fields.Many2many(
        'stock.route', string='Total routes', compute='_compute_total_route_ids', search='_search_total_route_ids',
        readonly=True)
    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'category_id', 'Putaway Rules')
    packaging_reserve_method = fields.Selection([
        ('full', 'Reserve Only Full Packagings'),
        ('partial', 'Reserve Partial Packagings'),], string="Reserve Packagings", default='partial',
        help="Reserve Only Full Packagings: will not reserve partial packagings. If customer orders 2 pallets of 1000 units each and you only have 1600 in stock, then only 1000 will be reserved\n"
             "Reserve Partial Packagings: allow reserving partial packagings. If customer orders 2 pallets of 1000 units each and you only have 1600 in stock, then 1600 will be reserved")
    filter_for_stock_putaway_rule = fields.Boolean('stock.putaway.rule', store=False, search='_search_filter_for_stock_putaway_rule')

    @api.depends('parent_id')
    def _compute_parent_route_ids(self):
        for category in self:
            base_cat = category
            routes = self.env['stock.route']
            while base_cat.parent_id:
                base_cat = base_cat.parent_id
                routes |= base_cat.route_ids
            category.parent_route_ids = routes - category.route_ids

    def _search_total_route_ids(self, operator, value):
        categories = self.with_context(active_test=False).search([])
        categ_ids = categories.filtered_domain([('total_route_ids', operator, value)]).ids
        return [('id', 'in', categ_ids)]

    @api.depends('route_ids', 'parent_route_ids')
    def _compute_total_route_ids(self):
        for category in self:
            category.total_route_ids = category.route_ids | category.parent_route_ids

    def _search_filter_for_stock_putaway_rule(self, operator, value):
        if operator != 'in':
            return NotImplemented

        domain = Domain.TRUE
        active_model = self.env.context.get('active_model')
        if active_model in ('product.template', 'product.product') and self.env.context.get('active_id'):
            product = self.env[active_model].browse(self.env.context.get('active_id'))
            product = product.exists()
            if product:
                domain = Domain('id', '=', product.categ_id.id)
        return domain


# FILEPATH: odoo/addons/stock/models/product.py (lines 1291-1342)
class UomUom(models.Model):
    _inherit = 'uom.uom'

    package_type_id = fields.Many2one('stock.package.type', string='Package Type')
    route_ids = fields.Many2many(related='package_type_id.route_ids', string='Routes', help='Routes propagated from the package type')

    def write(self, vals):
        # Users can not update the factor if open stock moves are based on it
        keys_to_protect = {'factor', 'relative_factor', 'relative_uom_id'}
        if any(key in vals for key in keys_to_protect):
            changed = self.filtered(
                lambda u: any(
                    f in vals and u[f] != vals[f]
                    for f in ('factor', 'relative_factor')
                ) or ('relative_uom_id' in vals and u.relative_uom_id.id != int(vals['relative_uom_id']))
            )
            if changed:
                error_msg = _(
                    "You cannot change the ratio of this unit of measure"
                    " as some products with this UoM have already been moved"
                    " or are currently reserved."
                )
                if self.env['stock.move'].sudo().search_count([
                    ('product_uom', 'in', changed.ids),
                    ('state', 'not in', ('cancel', 'done'))
                ]):
                    raise UserError(error_msg)
                if self.env['stock.move.line'].sudo().search_count([
                    ('product_uom_id', 'in', changed.ids),
                    ('state', 'not in', ('cancel', 'done')),
                ]):
                    raise UserError(error_msg)
                if self.env['stock.quant'].sudo().search_count([
                    ('product_id.product_tmpl_id.uom_id', 'in', changed.ids),
                    ('quantity', '!=', 0),
                ]):
                    raise UserError(error_msg)
        return super().write(vals)

    def _adjust_uom_quantities(self, qty, quant_uom):
        """ This method adjust the quantities of a procurement if its UoM isn't the same
        as the one of the quant and the parameter 'propagate_uom' is not set.
        """
        procurement_uom = self
        computed_qty = qty
        get_param = self.env['ir.config_parameter'].sudo().get_param
        if get_param('stock.propagate_uom') != '1':
            computed_qty = self._compute_quantity(qty, quant_uom, rounding_method='HALF-UP')
            procurement_uom = quant_uom
        else:
            computed_qty = self._compute_quantity(qty, procurement_uom, rounding_method='HALF-UP')
        return (computed_qty, procurement_uom)


# FILEPATH: odoo/addons/stock/models/product_catalog_mixin.py
class ProductCatalogMixin(models.AbstractModel):
    _inherit = "product.catalog.mixin"

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            'display_stock': self._is_display_stock_in_catalog(),
        }

    def _is_display_stock_in_catalog(self):
        return False


# FILEPATH: odoo/addons/stock/models/product_strategy.py (lines 8-13)
class ProductRemoval(models.Model):
    _name = 'product.removal'
    _description = 'Removal Strategy'
    name = fields.Char('Name', required=True, translate=True)
    method = fields.Char("Method", required=True, translate=True, help="FIFO, LIFO...")


# FILEPATH: odoo/addons/stock/models/product_strategy.py (lines 16-183)
class StockPutawayRule(models.Model):
    _name = 'stock.putaway.rule'
    _order = 'sequence,product_id'
    _description = 'Putaway Rule'
    _check_company_auto = True

    def _default_category_id(self):
        if self.env.context.get('active_model') == 'product.category':
            return self.env.context.get('active_id')

    def _default_location_id(self):
        if self.env.context.get('active_model') == 'stock.location':
            return self.env.context.get('active_id')
        if not self.env.user.has_group('stock.group_stock_multi_warehouses'):
            wh = self.env['stock.warehouse'].search(self.env['stock.warehouse']._check_company_domain(self.env.company), limit=1)
            input_loc, _ = wh._get_input_output_locations(wh.reception_steps, wh.delivery_steps)
            return input_loc

    def _default_product_id(self):
        if self.env.context.get('active_model') == 'product.template' and self.env.context.get('active_id'):
            product_template = self.env['product.template'].browse(self.env.context.get('active_id'))
            product_template = product_template.exists()
            if product_template.product_variant_count == 1:
                return product_template.product_variant_id
        elif self.env.context.get('active_model') == 'product.product':
            return self.env.context.get('active_id')

    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True,
        default=_default_product_id,
        index='btree_not_null',
        domain="[('product_tmpl_id', '=', context.get('active_id', False))] if context.get('active_model') == 'product.template' else [('type', '!=', 'service')]",
        ondelete='cascade')
    category_id = fields.Many2one('product.category', 'Product Category', index='btree_not_null',
        default=_default_category_id, domain=[('filter_for_stock_putaway_rule', '=', True)], ondelete='cascade')
    location_in_id = fields.Many2one(
        'stock.location', 'When product arrives in', check_company=True,
        domain="[('child_ids', '!=', False)]",
        default=_default_location_id, required=True, ondelete='cascade', index=True)
    location_out_id = fields.Many2one(
        'stock.location', 'Store to sublocation', check_company=True,
        domain="[('id', 'child_of', location_in_id)]",
        required=True, ondelete='cascade')
    sequence = fields.Integer('Priority', help="Give to the more specialized category, a higher priority to have them in top of the list.")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    package_type_ids = fields.Many2many('stock.package.type', string='Package Type', check_company=True)
    storage_category_id = fields.Many2one(
        'stock.storage.category', 'Storage Category',
        compute='_compute_storage_category', store=True, readonly=False,
        ondelete='cascade', check_company=True)
    active = fields.Boolean('Active', default=True)
    sublocation = fields.Selection([
        ('no', 'No'),
        ('last_used', 'Last Used'),
        ('closest_location', 'Closest Location')
    ], default='no')

    @api.depends('sublocation')
    def _compute_storage_category(self):
        for rule in self:
            if rule.sublocation != 'closest_location':
                rule.storage_category_id = False

    @api.onchange('sublocation', 'location_out_id', 'storage_category_id')
    def _onchange_sublocation(self):
        if self.sublocation == 'closest_location':
            child_location_ids = self.env['stock.location'].search([
                ('id', 'child_of', self.location_out_id.id),
                ('storage_category_id', '=', self.storage_category_id.id)
            ])
            if not child_location_ids:
                return {
                    'warning': {
                        'title': _("Warning"),
                        'message': _("Selected storage category does not exist in the 'store to' location or any of its sublocations"),
                    },
                }

    @api.onchange('location_in_id')
    def _onchange_location_in(self):
        loc_in, loc_out = self.location_in_id, self.location_out_id
        if not loc_out or (loc_in and not loc_out._child_of(loc_in)):
            self.location_out_id = self.location_in_id

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        return rules

    def write(self, vals):
        if 'company_id' in vals:
            for rule in self:
                if rule.company_id.id != vals['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))
        return super().write(vals)

    def _get_last_used_search_domain(self, product):
        self.ensure_one()
        domain = Domain([
            ('state', '=', 'done'),
            ('location_dest_id', 'child_of', self.location_out_id.id),
            ('product_id', '=', product.id),
        ])
        if self.package_type_ids:
            domain &= Domain('result_package_id.package_type_id', 'in', self.package_type_ids.ids)
        return domain

    def _get_last_used_location(self, product):
        self.ensure_one()
        return self.env['stock.move.line'].search(
            domain=self._get_last_used_search_domain(product),
            limit=1,
            order='date desc'
        ).location_dest_id

    def _get_putaway_location(self, product, quantity=0, package=None, packaging=None, qty_by_location=None):
        # find package type on package or packaging
        package_type = self.env['stock.package.type']
        if package:
            package_type = package.package_type_id
        elif packaging:
            package_type = packaging.package_type_id

        checked_locations = set()
        for putaway_rule in self:
            location_out = putaway_rule.location_out_id
            if putaway_rule.sublocation == 'last_used':
                location_dest_id = putaway_rule._get_last_used_location(product)
                location_out = location_dest_id or location_out

            child_locations = location_out.child_internal_location_ids

            if not putaway_rule.storage_category_id:
                if location_out in checked_locations:
                    continue
                if location_out._check_can_be_used(product, quantity, package, qty_by_location[location_out.id]):
                    return location_out
                continue
            else:
                child_locations = child_locations.filtered(lambda loc: loc.storage_category_id == putaway_rule.storage_category_id)

            # check if already have the product/package type stored
            for location in child_locations:
                if location in checked_locations:
                    continue
                if package_type:
                    if location.quant_ids.filtered(lambda q: q.package_id and q.package_id.package_type_id == package_type):
                        if location._check_can_be_used(product, quantity, package=package, location_qty=qty_by_location[location.id]):
                            return location
                        else:
                            checked_locations.add(location)
                elif product.uom_id.compare(qty_by_location[location.id], 0) > 0:
                    if location._check_can_be_used(product, quantity, location_qty=qty_by_location[location.id]):
                        return location
                    else:
                        checked_locations.add(location)

            # check locations with matched storage category
            for location in child_locations.filtered(lambda l: l.storage_category_id == putaway_rule.storage_category_id):
                if location in checked_locations:
                    continue
                if location._check_can_be_used(product, quantity, package, qty_by_location[location.id]):
                    return location
                checked_locations.add(location)

        return None


# FILEPATH: odoo/addons/stock/models/res_company.py
class ResCompany(models.Model):
    _inherit = "res.company"
    _check_company_auto = True
    def _default_confirmation_mail_template(self):
        pass  # shrunk (lines 10-14)
    internal_transit_location_id = fields.Many2one(
        'stock.location', 'Internal Transit Location', ondelete="restrict", check_company=True)
    stock_move_email_validation = fields.Boolean("Email Confirmation picking", default=False)
    stock_mail_confirmation_template_id = fields.Many2one('mail.template', string="Email Template confirmation picking",
        domain="[('model', '=', 'stock.picking')]",
        default=_default_confirmation_mail_template,
        help="Email sent to the customer once the order is done.")
    annual_inventory_month = fields.Selection([
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
    ], string='Annual Inventory Month',
        default='12',
        help="Annual inventory month for products not in a location with a cyclic inventory date. Set to no month if no automatic annual inventory.")
    annual_inventory_day = fields.Integer(
        string='Day of the month', default=31,
        help="""Day of the month when the annual inventory should occur. If zero or negative, then the first day of the month will be selected instead.
        If greater than the last day of a month, then the last day of the month will be selected instead.""")
    horizon_days = fields.Float(string="Replenishment Horizon", required=True, default=365,
                                help="""Configure your horizon to trigger reordering rules earlier to get
                                a head start on replenishment and avoid delays, or trigger it just-in-time
                                ('0 days') to avoid overstocking.""")
    stock_text_confirmation = fields.Boolean("Stock Text Confirmation")
    stock_confirmation_type = fields.Selection([('sms', 'SMS')], default='sms')
    def _create_transit_location(self):
        pass  # shrunk (lines 53-71)
    def _create_inventory_loss_location(self):
        pass  # shrunk (lines 73-80)
    def _create_production_location(self):
        pass  # shrunk (lines 82-89)
    def _create_scrap_location(self):
        pass  # shrunk (lines 91-97)
    def _create_scrap_sequence(self):
        pass  # shrunk (lines 99-112)
    @api.model
    def create_missing_warehouse(self):
        pass  # shrunk (lines 114-126)
    @api.model
    def create_missing_transit_location(self):
        pass  # shrunk (lines 128-131)
    @api.model
    def create_missing_inventory_loss_location(self):
        pass  # shrunk (lines 133-139)
    @api.model
    def create_missing_production_location(self):
        pass  # shrunk (lines 141-147)
    @api.model
    def create_missing_scrap_location(self):
        pass  # shrunk (lines 149-154)
    @api.model
    def create_missing_scrap_sequence(self):
        pass  # shrunk (lines 156-161)
    def _create_per_company_locations(self):
        pass  # shrunk (lines 163-168)
    def _create_per_company_sequences(self):
        pass  # shrunk (lines 170-172)
    def _create_per_company_picking_types(self):
        pass  # shrunk (lines 174-175)
    def _create_per_company_rules(self):
        pass  # shrunk (lines 177-178)
    @api.model_create_multi
    def create(self, vals_list):
        pass  # shrunk (lines 180-195)
    def _set_per_company_inter_company_locations(self, inter_company_location):
        pass  # shrunk (lines 197-211)
    def _get_text_validation(self, confirmation_type):
        pass  # shrunk (lines 213-215)


# FILEPATH: odoo/addons/stock/models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    module_product_expiry = fields.Boolean("Expiration Dates",
        help="Track following dates on lots & serial numbers: best before, removal, end of life, alert. \n Such dates are set automatically at lot/serial number creation based on values set on the product (in days).")
    group_stock_production_lot = fields.Boolean("Lots & Serial Numbers",
        implied_group='stock.group_production_lot', group="base.group_user,base.group_portal")
    group_stock_lot_print_gs1 = fields.Boolean("Print GS1 Barcodes for Lots & Serial Numbers",
        implied_group='stock.group_stock_lot_print_gs1')
    group_lot_on_delivery_slip = fields.Boolean("Display Lots & Serial Numbers on Delivery Slips",
        implied_group='stock.group_lot_on_delivery_slip', group="base.group_user,base.group_portal")
    group_stock_tracking_lot = fields.Boolean("Packages",
        implied_group='stock.group_tracking_lot')
    group_stock_tracking_owner = fields.Boolean("Consignment",
        implied_group='stock.group_tracking_owner')
    group_stock_adv_location = fields.Boolean("Multi-Step Routes",
        implied_group='stock.group_adv_location',
        help="Add and customize route operations to process product moves in your warehouse(s): e.g. unload > quality control > stock for incoming products, pick > pack > ship for outgoing products. \n You can also set putaway strategies on warehouse locations in order to send incoming products into specific child locations straight away (e.g. specific bins, racks).")
    group_warning_stock = fields.Boolean("Warnings for Stock", implied_group='stock.group_warning_stock')
    group_stock_sign_delivery = fields.Boolean("Signature", implied_group='stock.group_stock_sign_delivery')
    module_stock_picking_batch = fields.Boolean("Batch, Wave & Cluster Transfers")
    module_stock_barcode = fields.Boolean("Barcode Scanner")
    module_stock_barcode_barcodelookup = fields.Boolean("Stock Barcode Database")
    stock_move_email_validation = fields.Boolean(related='company_id.stock_move_email_validation', readonly=False)
    module_stock_sms = fields.Boolean("SMS Confirmation")
    module_delivery = fields.Boolean("Delivery Methods")
    module_delivery_dhl = fields.Boolean("DHL Express Connector")
    module_delivery_fedex_rest = fields.Boolean("FedEx Connector")
    module_delivery_ups_rest = fields.Boolean("UPS Connector")
    module_delivery_usps_rest = fields.Boolean("USPS Connector")
    module_delivery_bpost = fields.Boolean("bpost Connector")
    module_delivery_easypost = fields.Boolean("Easypost Connector")
    module_delivery_sendcloud = fields.Boolean("Sendcloud Connector")
    module_delivery_shiprocket = fields.Boolean("Shiprocket Connector")
    module_delivery_starshipit = fields.Boolean("Starshipit Connector")
    module_delivery_envia = fields.Boolean("Envia.com Connector")
    module_quality_control = fields.Boolean("Quality")
    module_quality_control_worksheet = fields.Boolean("Quality Worksheet")
    group_stock_multi_locations = fields.Boolean('Storage Locations', implied_group='stock.group_stock_multi_locations',
        help="Store products in specific locations of your warehouse (e.g. bins, racks) and to track inventory accordingly.")
    annual_inventory_month = fields.Selection(related='company_id.annual_inventory_month', readonly=False)
    annual_inventory_day = fields.Integer(related='company_id.annual_inventory_day', readonly=False)
    group_stock_reception_report = fields.Boolean("Reception Report", implied_group='stock.group_reception_report')
    module_stock_dropshipping = fields.Boolean("Dropshipping")
    barcode_separator = fields.Char(
        "Separator", config_parameter='stock.barcode_separator',
        help="Character(s) used to separate data contained within an aggregate barcode (i.e. a barcode containing multiple barcode encodings)")
    module_stock_fleet = fields.Boolean("Dispatch Management System")
    replenish_on_order = fields.Boolean("Replenish on Order (MTO)", compute='_compute_replenish_on_order', inverse='_inverse_replenish_on_order')
    stock_text_confirmation = fields.Boolean(related='company_id.stock_text_confirmation', string='Stock Text Validation with stock move', readonly=False)
    stock_confirmation_type = fields.Selection(related='company_id.stock_confirmation_type', string='Stock Text Validation type', readonly=False)
    horizon_days = fields.Float(related='company_id.horizon_days', readonly=False)
    def _compute_replenish_on_order(self):
        pass  # shrunk (lines 61-64)
    def _inverse_replenish_on_order(self):
        pass  # shrunk (lines 66-69)
    @api.onchange('group_stock_multi_locations')
    def _onchange_group_stock_multi_locations(self):
        pass  # shrunk (lines 71-74)
    @api.onchange('group_stock_production_lot')
    def _onchange_group_stock_production_lot(self):
        pass  # shrunk (lines 76-80)
    @api.onchange('stock_confirmation_type', 'stock_text_confirmation')
    def _onchange_stock_confirmation_fields(self):
        pass  # shrunk (lines 82-85)
    @api.onchange('group_stock_adv_location')
    def onchange_adv_location(self):
        pass  # shrunk (lines 87-90)
    def set_values(self):
        pass  # shrunk (lines 92-139)


# FILEPATH: odoo/addons/stock/models/res_partner.py
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _check_company_auto = True
    property_stock_customer = fields.Many2one(
        'stock.location', string="Customer Location", company_dependent=True, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="The stock location used as destination when sending goods to this contact.")
    property_stock_supplier = fields.Many2one(
        'stock.location', string="Vendor Location", company_dependent=True, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="The stock location used as source when receiving goods from this contact.")
    picking_warn_msg = fields.Text('Message for Stock Picking')
    def action_view_stock_serial(self):
        pass  # shrunk (lines 21-25)


# FILEPATH: odoo/addons/stock/models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'
    def _get_default_warehouse_id(self):
    # !!! Any change to the following search domain should probably
    # be also applied in sale_stock/models/sale_order.py/_init_column.
        pass  # shrunk (lines 9-12)


# FILEPATH: odoo/addons/stock/models/stock_location.py (lines 13-514)
class StockLocation(models.Model):
    _name = 'stock.location'
    _description = "Inventory Locations"
    _parent_name = "location_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_names_search = ['complete_name', 'barcode']
    _check_company_auto = True

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'barcode' in fields and 'barcode' not in res and res.get('complete_name'):
            res['barcode'] = res['complete_name']
        return res

    name = fields.Char('Location Name', required=True)
    complete_name = fields.Char("Full Location Name", compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a location without deleting it.")
    usage = fields.Selection([
        ('supplier', 'Vendor'),
        ('view', 'Virtual'),
        ('internal', 'Internal'),
        ('customer', 'Customer'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit')], string='Location Type',
        default='internal', index=True, required=True,
        help="* Vendor: Virtual location representing the source location for products coming from your vendors"
             "\n* Virtual: Virtual location used to create a hierarchical structure for your warehouse by aggregating its child locations. Can't directly contain products"
             "\n* Internal: Physical locations inside your warehouses,"
             "\n* Customer: Virtual location representing the destination location for products sent to your customers"
             "\n* Inventory Loss: Virtual location serving as the counterpart for inventory operations done to correct stock levels (Physical inventories)"
             "\n* Production: Virtual counterpart location for production operations. I.e. This location consumes components and produces finished products"
             "\n* Transit: Counterpart location that should be used for inter-company or inter-warehouses operations")
    location_id = fields.Many2one(
        'stock.location', 'Parent Location', index=True, check_company=True,
        help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")
    child_ids = fields.One2many('stock.location', 'location_id', 'Contains')
    child_internal_location_ids = fields.Many2many(
        'stock.location',
        string='Internal locations among descendants',
        compute='_compute_child_internal_location_ids',
        recursive=True,
        help='This location (if it\'s internal) and all its descendants filtered by type=Internal.'
    )
    parent_path = fields.Char(index=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this location is shared between companies')
    replenish_location = fields.Boolean('Replenishments', copy=False, compute="_compute_replenish_location", readonly=False, store=True,
                                        help='Trigger replenishment suggestions for this location when required')
    removal_strategy_id = fields.Many2one(
        'product.removal', 'Removal Strategy',
        help="Defines the default method used for suggesting the exact location (shelf) "
             "where to take the products from, which lot etc. for this location. "
             "This method can be enforced at the product category level, "
             "and a fallback is made on the parent locations if none is set here.\n\n"
             "FIFO: products/lots that were stocked first will be moved out first.\n"
             "LIFO: products/lots that were stocked last will be moved out first.\n"
             "Closest Location: products/lots closest to the target location will be moved out first.\n"
             "Least Packages: products/lots that were stocked in package with least amount of qty will be moved out first.\n"
             "FEFO: products/lots with the closest removal date will be moved out first "
             "(the availability of this method depends on the \"Expiration Dates\" setting).")
    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'location_in_id', 'Putaway Rules')
    barcode = fields.Char('Barcode', copy=False)
    quant_ids = fields.One2many('stock.quant', 'location_id')
    cyclic_inventory_frequency = fields.Integer("Inventory Frequency", default=0, help=" When different than 0, inventory count date for products stored at this location will be automatically set at the defined frequency.")
    last_inventory_date = fields.Date("Last Inventory", readonly=True, help="Date of the last inventory at this location.")
    next_inventory_date = fields.Date("Next Expected", compute="_compute_next_inventory_date", store=True, help="Date for next planned inventory based on cyclic schedule.")
    warehouse_view_ids = fields.One2many('stock.warehouse', 'view_location_id', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse_id', store=True)
    storage_category_id = fields.Many2one('stock.storage.category', string='Storage Category', check_company=True, index='btree_not_null')
    outgoing_move_line_ids = fields.One2many('stock.move.line', 'location_id') # used to compute weight
    incoming_move_line_ids = fields.One2many('stock.move.line', 'location_dest_id') # used to compute weight
    net_weight = fields.Float('Net Weight', compute="_compute_weight")
    forecast_weight = fields.Float('Forecasted Weight', compute="_compute_weight")
    is_empty = fields.Boolean('Is Empty', compute='_compute_is_empty', search='_search_is_empty')

    _barcode_company_uniq = models.Constraint(
        'unique (barcode,company_id)',
        'The barcode for a location must be unique per company!',
    )
    _inventory_freq_nonneg = models.Constraint(
        'check(cyclic_inventory_frequency >= 0)',
        'The inventory frequency (days) for a location must be non-negative',
    )
    _parent_path_id_idx = models.Index("(parent_path, id)")

    @api.depends('name', 'location_id.complete_name', 'usage')
    @api.depends_context('formatted_display_name')
    def _compute_display_name(self):
        super()._compute_display_name()
        for location in self:
            has_parent = location.location_id and location.usage != 'view'
            if location.env.context.get('formatted_display_name') and has_parent:
                location.display_name = f"--{location.location_id.complete_name}/--{location.name}"
            elif has_parent:
                location.display_name = f"{location.location_id.complete_name}/{location.name}"

    @api.depends('outgoing_move_line_ids.quantity_product_uom', 'incoming_move_line_ids.quantity_product_uom',
                 'outgoing_move_line_ids.state', 'incoming_move_line_ids.state',
                 'outgoing_move_line_ids.product_id.weight', 'outgoing_move_line_ids.product_id.weight',
                 'quant_ids.quantity', 'quant_ids.product_id.weight')
    def _compute_weight(self):
        weight_by_location = self._get_weight()
        for location in self:
            location.net_weight = weight_by_location[location]['net_weight']
            location.forecast_weight = weight_by_location[location]['forecast_weight']

    @api.depends('name', 'location_id.complete_name', 'usage')
    def _compute_complete_name(self):
        for location in self:
            if location.location_id and location.usage != 'view':
                location.complete_name = '%s/%s' % (location.location_id.complete_name, location.name)
            else:
                location.complete_name = location.name

    def _compute_is_empty(self):
        groups = self.env['stock.quant']._read_group(
            [('location_id.usage', 'in', ('internal', 'transit')),
             ('location_id', 'in', self.ids)],
            ['location_id'], ['quantity:sum'])
        groups = dict(groups)
        for location in self:
            location.is_empty = groups.get(location, 0) <= 0

    @api.depends('cyclic_inventory_frequency', 'last_inventory_date', 'usage', 'company_id')
    def _compute_next_inventory_date(self):
        for location in self:
            if location.company_id and location.usage in ['internal', 'transit'] and location.cyclic_inventory_frequency > 0:
                try:
                    if location.last_inventory_date:
                        days_until_next_inventory = location.cyclic_inventory_frequency - (fields.Date.today() - location.last_inventory_date).days
                        if days_until_next_inventory <= 0:
                            location.next_inventory_date = fields.Date.today() + timedelta(days=1)
                        else:
                            location.next_inventory_date = location.last_inventory_date + timedelta(days=location.cyclic_inventory_frequency)
                    else:
                        location.next_inventory_date = fields.Date.today() + timedelta(days=location.cyclic_inventory_frequency)
                except OverflowError:
                    raise UserError(_("The selected Inventory Frequency (Days) creates a date too far into the future."))
            else:
                location.next_inventory_date = False

    @api.depends('warehouse_view_ids', 'location_id')
    def _compute_warehouse_id(self):
        warehouses = self.env['stock.warehouse'].search([('view_location_id', 'parent_of', self.ids)])
        warehouses = warehouses.sorted(lambda w: w.view_location_id.parent_path, reverse=True)
        view_by_wh = OrderedDict((wh.view_location_id.id, wh.id) for wh in warehouses)
        self.warehouse_id = False
        for loc in self:
            if not loc.parent_path:
                continue
            path = set(int(loc_id) for loc_id in loc.parent_path.split('/')[:-1])
            for view_location_id in view_by_wh:
                if view_location_id in path:
                    loc.warehouse_id = view_by_wh[view_location_id]
                    break

    @api.depends('child_ids.usage', 'child_ids.child_internal_location_ids')
    def _compute_child_internal_location_ids(self):
        # batch reading optimization is not possible because the field has recursive=True
        for loc in self:
            loc.child_internal_location_ids = self.search([('id', 'child_of', loc.id), ('usage', '=', 'internal')])

    @api.depends('usage')
    def _compute_replenish_location(self):
        for loc in self:
            if loc.usage != 'internal':
                loc.replenish_location = False

    @api.constrains('replenish_location', 'location_id', 'usage')
    def _check_replenish_location(self):
        for loc in self:
            if loc.replenish_location:
                # cannot have parent/child location set as replenish as well
                replenish_wh_location = self.search([('id', '!=', loc.id), ('replenish_location', '=', True), '|', ('location_id', 'child_of', loc.id), ('location_id', 'parent_of', loc.id)], limit=1)
                if replenish_wh_location:
                    raise ValidationError(_('Another parent/sub replenish location %s exists, if you wish to change it, uncheck it first', replenish_wh_location.name))

    @api.constrains('usage')
    def _check_scrap_location(self):
        for record in self:
            if record.usage == 'inventory' and self.env['stock.picking.type'].search_count([('code', '=', 'mrp_operation'), ('default_location_dest_id', '=', record.id)], limit=1):
                raise ValidationError(_("You cannot set a location as a scrap location when it is assigned as a destination location for a manufacturing type operation."))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_master_data(self):
        inter_company_location = self.env.ref('stock.stock_location_inter_company')
        if inter_company_location in self:
            raise ValidationError(_('The %s location is required by the Inventory app and cannot be deleted, but you can archive it.', inter_company_location.name))

    def _search_is_empty(self, operator, value):
        if operator != 'in':
            return NotImplemented
        location_ids = [
            location.id
            for location, in self.env['stock.quant']._read_group(
                [('location_id.usage', 'in', ['internal', 'transit'])],
                ['location_id'],
                having=[('quantity:sum', '>', 0)]
            )
        ]
        return [('id', 'not in', location_ids)]

    def write(self, vals):
        values = vals
        if 'company_id' in values:
            for location in self:
                if location.company_id.id != values['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))
        if 'usage' in values and values['usage'] == 'view':
            if self.mapped('quant_ids'):
                raise UserError(_("This location's usage cannot be changed to view as it contains products."))
        if 'usage' in values:
            modified_locations = self.filtered(lambda l: l.usage != values['usage'])
            reserved_quantities = self.env['stock.quant'].search_count([
                ('location_id', 'in', modified_locations.ids),
                ('quantity', '>', 0),
                ],
                limit=1)
            if reserved_quantities:
                raise UserError(_(
                    "Internal locations having stock can't be converted"
                ))
        if 'active' in values:
            if not values['active']:
                for location in self:
                    warehouses = self.env['stock.warehouse'].search([('active', '=', True), '|', ('lot_stock_id', '=', location.id), ('view_location_id', '=', location.id)], limit=1)
                    if warehouses:
                        raise UserError(_(
                            "You cannot archive location %(location)s because it is used by warehouse %(warehouse)s",
                            location=location.display_name, warehouse=warehouses.display_name))

            if not self.env.context.get('do_not_check_quant'):
                children_location = self.env['stock.location'].with_context(active_test=False).search([('id', 'child_of', self.ids)])
                internal_children_locations = children_location.filtered(lambda l: l.usage == 'internal')
                children_quants = self.env['stock.quant'].search(['&', '|', ('quantity', '!=', 0), ('reserved_quantity', '!=', 0), ('location_id', 'in', internal_children_locations.ids)])
                if children_quants and not values['active']:
                    raise UserError(_(
                        "You can't disable locations %s because they still contain products.",
                        ', '.join(children_quants.mapped('location_id.display_name'))))
                else:
                    super(StockLocation, children_location - self).with_context(do_not_check_quant=True).write({
                        'active': values['active'],
                    })

        res = super().write(values)
        self.invalidate_model(['warehouse_id'])
        return res

    def unlink(self):
        return super(StockLocation, self.search([('id', 'child_of', self.ids)])).unlink()

    @api.model
    def name_create(self, name):
        if name:
            name_split = name.split('/')
            parent_location = self.env['stock.location'].search([
                ('complete_name', '=', '/'.join(name_split[:-1])),
            ], limit=1)
            new_location = self.create({
                'name': name.split('/')[-1],
                'location_id': parent_location.id if parent_location else False,
            })
            return new_location.id, new_location.display_name
        return super().name_create(name)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.invalidate_model(['warehouse_id'])
        return res

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'name' not in default:
            for location, vals in zip(self, vals_list):
                vals['name'] = _("%s (copy)", location.name)
        return vals_list

    def _get_putaway_strategy(self, product, quantity=0, package=None, packaging=None, additional_qty=None):
        """Returns the location where the product has to be put, if any compliant
        putaway strategy is found. Otherwise returns self.
        The quantity should be in the default UOM of the product, it is used when
        no package is specified.
        """
        self = self._check_access_putaway()
        products = self.env.context.get('products', self.env['product.product'])
        products |= product
        # find package type on package or packaging
        package_type = self.env['stock.package.type']
        if package:
            package_type = package.package_type_id
        elif packaging:
            package_type = packaging.package_type_id

        categ = products.categ_id if len(products.categ_id) == 1 else self.env['product.category']
        categs = categ
        while categ.parent_id:
            categ = categ.parent_id
            categs |= categ

        putaway_rules = self.putaway_rule_ids.filtered(lambda rule:
                                                       (not rule.product_id or rule.product_id in products) and
                                                       (not rule.category_id or rule.category_id in categs) and
                                                       (not rule.package_type_ids or package_type in rule.package_type_ids))

        putaway_rules = putaway_rules.sorted(lambda rule: (bool(rule.package_type_ids),
                                                           bool(rule.product_id),
                                                           bool(rule.category_id == categs[:1]),  # same categ, not a parent
                                                           bool(rule.category_id)),
                                             reverse=True)

        putaway_location = None
        locations = self.env.context.get("locations")
        if not locations:
            locations = self.child_internal_location_ids
        if putaway_rules:
            # get current product qty (qty in current quants and future qty on assigned ml) of all child locations
            qty_by_location = defaultdict(lambda: 0)
            if locations.storage_category_id:
                if package and package.package_type_id:
                    move_line_data = self.env['stock.move.line']._read_group([
                        ('id', 'not in', list(self.env.context.get('exclude_sml_ids', set()))),
                        ('result_package_id.package_type_id', '=', package_type.id),
                        ('state', 'not in', ['draft', 'cancel', 'done']),
                    ], ['location_dest_id'], ['result_package_id:count_distinct'])
                    quant_data = self.env['stock.quant']._read_group([
                        ('package_id.package_type_id', '=', package_type.id),
                        ('location_id', 'in', locations.ids),
                    ], ['location_id'], ['package_id:count_distinct'])
                    qty_by_location.update({location_dest.id: count for location_dest, count in move_line_data})
                    for location, count in quant_data:
                        qty_by_location[location.id] += count
                else:
                    move_line_data = self.env['stock.move.line']._read_group([
                        ('id', 'not in', list(self.env.context.get('exclude_sml_ids', set()))),
                        ('product_id', '=', product.id),
                        ('location_dest_id', 'in', locations.ids),
                        ('state', 'not in', ['draft', 'done', 'cancel'])
                    ], ['location_dest_id'], ['quantity:array_agg', 'product_uom_id:recordset'])
                    quant_data = self.env['stock.quant']._read_group([
                        ('product_id', '=', product.id),
                        ('location_id', 'in', locations.ids),
                    ], ['location_id'], ['quantity:sum'])

                    qty_by_location.update({location.id: quantity_sum for location, quantity_sum in quant_data})
                    for location_dest, quantity_list, uoms in move_line_data:
                        current_qty = sum(ml_uom._compute_quantity(float(qty), product.uom_id) for qty, ml_uom in zip(quantity_list, uoms))
                        qty_by_location[location_dest.id] += current_qty

            if additional_qty:
                for location_id, qty in additional_qty.items():
                    qty_by_location[location_id] += qty
            putaway_location = putaway_rules._get_putaway_location(product, quantity, package, packaging, qty_by_location)

        if not putaway_location:
            putaway_location = locations[0] if locations and self.usage == 'view' else self

        return putaway_location

    def _get_next_inventory_date(self):
        """ Used to get the next inventory date for a quant located in this location. It is
        based on:
        1. Does the location have a cyclic inventory set?
        2. If not 1, then is there an annual inventory date set (for its company)?
        3. If not 1 and 2, then quants have no next inventory date."""
        if self.usage not in ['internal', 'transit']:
            return False
        next_inventory_date = False
        company_inventory_date = False

        if self.company_id.annual_inventory_month:
            today = fields.Date.today()
            annual_inventory_month = int(self.company_id.annual_inventory_month)
            # Manage 0 and negative annual_inventory_day
            annual_inventory_day = max(self.company_id.annual_inventory_day, 1)
            max_day = calendar.monthrange(today.year, annual_inventory_month)[1]
            # Manage annual_inventory_day bigger than last_day
            annual_inventory_day = min(annual_inventory_day, max_day)
            company_inventory_date = today.replace(
                month=annual_inventory_month, day=annual_inventory_day)
            if company_inventory_date <= today:
                # Manage leap year with the february
                max_day = calendar.monthrange(today.year + 1, annual_inventory_month)[1]
                annual_inventory_day = min(annual_inventory_day, max_day)
                company_inventory_date = company_inventory_date.replace(
                    day=annual_inventory_day, year=today.year + 1)
        if self.next_inventory_date:
            next_inventory_date = min(self.next_inventory_date, company_inventory_date) if company_inventory_date else self.next_inventory_date
        elif self.company_id.annual_inventory_month:
            next_inventory_date = company_inventory_date
        return next_inventory_date

    def should_bypass_reservation(self):
        self.ensure_one()
        return self.usage in ('supplier', 'customer', 'inventory', 'production')

    def _check_access_putaway(self):
        return self

    def _check_can_be_used(self, product, quantity=0, package=None, location_qty=0):
        """Check if product/package can be stored in the location. Quantity
        should in the default uom of product, it's only used when no package is
        specified."""
        self.ensure_one()
        if self.storage_category_id:
            forecast_weight = self._get_weight(self.env.context.get('exclude_sml_ids', set()))[self]['forecast_weight']
            # check if enough space
            if package and package.package_type_id:
                # check weight
                package_smls = self.env['stock.move.line'].search([('result_package_id', '=', package.id), ('state', 'not in', ['done', 'cancel'])])
                if self.storage_category_id.max_weight < forecast_weight + sum(package_smls.mapped(lambda sml: sml.quantity_product_uom * sml.product_id.weight)):
                    return False
                # check if enough space
                package_capacity = self.storage_category_id.package_capacity_ids.filtered(lambda pc: pc.package_type_id == package.package_type_id)
                if package_capacity and location_qty >= package_capacity.quantity:
                    return False
            else:
                # check weight
                if self.storage_category_id.max_weight < forecast_weight + product.weight * quantity:
                    return False
                product_capacity = self.storage_category_id.product_capacity_ids.filtered(lambda pc: pc.product_id == product)
                # To handle new line without quantity in order to avoid suggesting a location already full
                if product_capacity and location_qty >= product_capacity.quantity:
                    return False
                if product_capacity and quantity + location_qty > product_capacity.quantity:
                    return False
            positive_quant = self.quant_ids.filtered(lambda q: q.product_id.uom_id.compare(q.quantity, 0) > 0)
            # check if only allow new product when empty
            if self.storage_category_id.allow_new_product == "empty" and positive_quant:
                return False
            # check if only allow same product
            if self.storage_category_id.allow_new_product == "same":
                # In case it's a package, `product` is not defined, so try to get
                # the package products from the context
                product = product or self.env.context.get('products')
                if (positive_quant and positive_quant.product_id != product) or len(product) > 1:
                    return False
                if self.env['stock.move.line'].search_count([
                    ('product_id', '!=', product.id),
                    ('state', 'not in', ('done', 'cancel')),
                    ('location_dest_id', '=', self.id),
                ], limit=1):
                    return False
        return True

    def _child_of(self, other_location):
        self.ensure_one()
        return self.parent_path.startswith(other_location.parent_path)

    def _is_outgoing(self):
        self.ensure_one()
        if self.usage == 'customer':
            return True
        # Can also be True if location is inter-company transit
        inter_comp_location = self.env.ref('stock.stock_location_inter_company', raise_if_not_found=False)
        return self._child_of(inter_comp_location)

    def _get_weight(self, excluded_sml_ids=False):
        """Returns a dictionary with the net and forecasted weight of the location.
        param excluded_sml_ids: set of stock.move.line ids to exclude from the computation
        """
        if not excluded_sml_ids:
            excluded_sml_ids = set()
        Product = self.env['product.product']
        StockMoveLine = self.env['stock.move.line']

        quants = self.env['stock.quant']._read_group(
            [('location_id', 'in', self.ids)],
            groupby=['location_id', 'product_id'], aggregates=['quantity:sum'],
        )
        base_domain = Domain('state', 'not in', ['draft', 'done', 'cancel']) & Domain('id', 'not in', tuple(excluded_sml_ids))
        outgoing_move_lines = StockMoveLine._read_group(
            Domain('location_id', 'in', self.ids) & base_domain,
            groupby=['location_id', 'product_id'], aggregates=['quantity_product_uom:sum'],
        )
        incoming_move_lines = StockMoveLine._read_group(
            Domain('location_dest_id', 'in', self.ids) & base_domain,
            groupby=['location_dest_id', 'product_id'], aggregates=['quantity_product_uom:sum']
        )

        products = Product.union(*(product for __, product, __ in quants + outgoing_move_lines + incoming_move_lines))
        products.fetch(['weight'])

        result = defaultdict(lambda: defaultdict(float))
        for loc, product, quantity_sum in quants:
            weight = quantity_sum * product.weight
            result[loc]['net_weight'] += weight
            result[loc]['forecast_weight'] += weight

        for loc, product, quantity_product_uom_sum in outgoing_move_lines:
            result[loc]['forecast_weight'] -= quantity_product_uom_sum * product.weight

        for dest_loc, product, quantity_product_uom_sum in incoming_move_lines:
            result[dest_loc]['forecast_weight'] += quantity_product_uom_sum * product.weight

        return result


# FILEPATH: odoo/addons/stock/models/stock_location.py (lines 517-595)
class StockRoute(models.Model):
    _name = 'stock.route'
    _description = "Inventory Routes"
    _order = 'sequence'
    _check_company_auto = True

    name = fields.Char('Route', required=True, translate=True)
    active = fields.Boolean('Active', default=True, help="If the active field is set to False, it will allow you to hide the route without removing it.")
    sequence = fields.Integer('Sequence', default=0)
    rule_ids = fields.One2many('stock.rule', 'route_id', 'Rules', copy=True)
    product_selectable = fields.Boolean('Applicable on Product', default=True, help="When checked, the route will be selectable in the Inventory tab of the Product form.")
    product_categ_selectable = fields.Boolean('Applicable on Product Category', help="When checked, the route will be selectable on the Product Category.")
    warehouse_selectable = fields.Boolean('Applicable on Warehouse', help="When a warehouse is selected for this route, this route should be seen as the default route when products pass through this warehouse.")
    package_type_selectable = fields.Boolean('Applicable on Package Type', help="When checked, the route will be selectable on package types")
    supplied_wh_id = fields.Many2one('stock.warehouse', 'Supplied Warehouse', index='btree_not_null')
    supplier_wh_id = fields.Many2one('stock.warehouse', 'Supplying Warehouse')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Leave this field empty if this route is shared between all companies')
    product_ids = fields.Many2many(
        'product.template', 'stock_route_product', 'route_id', 'product_id',
        'Products', copy=False, check_company=True)
    categ_ids = fields.Many2many('product.category', 'stock_route_categ', 'route_id', 'categ_id', 'Product Categories', copy=False)
    warehouse_domain_ids = fields.One2many('stock.warehouse', compute='_compute_warehouses')
    warehouse_ids = fields.Many2many(
        'stock.warehouse', 'stock_route_warehouse', 'route_id', 'warehouse_id',
        'Warehouses', copy=False, domain="[('id', 'in', warehouse_domain_ids)]")

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'name' not in default:
            for route, vals in zip(self, vals_list):
                vals['name'] = _("%s (copy)", route.name)
        return vals_list

    @api.depends('company_id')
    def _compute_warehouses(self):
        for loc in self:
            domain = [('company_id', '=', loc.company_id.id)] if loc.company_id else []
            loc.warehouse_domain_ids = self.env['stock.warehouse'].search(domain)

    @api.onchange('company_id')
    def _onchange_company(self):
        if self.company_id:
            self.warehouse_ids = self.warehouse_ids.filtered(lambda w: w.company_id == self.company_id)

    @api.onchange('warehouse_selectable')
    def _onchange_warehouse_selectable(self):
        if not self.warehouse_selectable:
            self.warehouse_ids = [(5, 0, 0)]

    def write(self, vals):
        if 'active' in vals:
            rules = self.with_context(active_test=False).rule_ids.sudo().filtered(lambda rule: rule.location_dest_id.active)
            if vals['active']:
                rules.action_unarchive()
            else:
                rules.action_archive()
        return super().write(vals)

    @api.constrains('company_id')
    def _check_company_consistency(self):
        for route in self:
            if not route.company_id:
                continue

            for rule in route.rule_ids:
                if route.company_id.id != rule.company_id.id:
                    raise ValidationError(_(
                        "Rule %(rule)s belongs to %(rule_company)s while the route belongs to %(route_company)s.",
                        rule=rule.display_name,
                        rule_company=rule.company_id.display_name,
                        route_company=route.company_id.display_name,
                    ))

    def _is_valid_resupply_route_for_product(self, product):
        return False


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

    @api.model
    def default_get(self, fields):
        context = dict(self.env.context)
        # We always want the company_id to be computed, regardless of where it's been created.
        context.pop('default_company_id', False)
        return super(StockLot, self.with_context(context)).default_get(fields)

    def _read_group_location_id(self, locations, domain):
        partner_locations = locations.search([('usage', 'in', ('customer', 'supplier'))])
        return partner_locations + locations.warehouse_id.search([]).lot_stock_id

    name = fields.Char('Lot/Serial Number', required=True, compute='_compute_name', store=True, readonly=False, help="Unique Lot/Serial Number", index='trigram', precompute=True)
    ref = fields.Char('Internal Reference', help="Internal reference number in case it differs from the manufacturer's lot/serial number")
    product_id = fields.Many2one(
        'product.product', 'Product', index=True,
        domain=("[('tracking', '!=', 'none'), ('is_storable', '=', True)] +"
            " ([('product_tmpl_id', '=', context['default_product_tmpl_id'])] if context.get('default_product_tmpl_id') else [])"),
        required=True, check_company=True, tracking=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit',
        related='product_id.uom_id')
    quant_ids = fields.One2many('stock.quant', 'lot_id', 'Quants', readonly=True)
    product_qty = fields.Float('On Hand Quantity', compute='_product_qty', search='_search_product_qty')
    note = fields.Html(string='Description')
    display_complete = fields.Boolean(compute='_compute_display_complete')
    company_id = fields.Many2one('res.company', 'Company', index=True, store=True, readonly=False, compute='_compute_company_id')
    delivery_ids = fields.Many2many('stock.picking', compute='_compute_delivery_ids', string='Transfers')
    delivery_count = fields.Integer('Delivery order count', compute='_compute_delivery_ids')
    partner_ids = fields.Many2many('res.partner', compute='_compute_partner_ids', search='_search_partner_ids')
    lot_properties = fields.Properties('Properties', definition='product_id.lot_properties_definition', copy=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', compute='_compute_single_location', store=True, readonly=False,
        inverse='_set_single_location', domain="[('usage', '!=', 'view')]", group_expand='_read_group_location_id')

    @api.depends('product_id')
    def _compute_name(self):
        for lot in self:
            if not lot.name:
                lot.name = lot.product_id.lot_sequence_id.next_by_id() if lot.product_id.lot_sequence_id else False

    @api.model
    def generate_lot_names(self, first_lot, count):
        """Generate `lot_names` from a string."""
        # We look if the first lot contains at least one digit.
        caught_initial_number = regex_findall(r"\d+", first_lot)
        if not caught_initial_number:
            return self.generate_lot_names(first_lot + "0", count)
        # We base the series on the last number found in the base lot.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the lot name to get the prefix and suffix.
        splitted = regex_split(initial_number, first_lot)
        # initial_number could appear several times, e.g. BAV023B00001S00001
        prefix = initial_number.join(splitted[:-1])
        suffix = splitted[-1]
        initial_number = int(initial_number)

        return [{
            'lot_name': '%s%s%s' % (prefix, str(initial_number + i).zfill(padding), suffix),
        } for i in range(0, count)]

    @api.model
    def _get_next_serial(self, company, product):
        """Return the next serial number to be attributed to the product."""
        if product.tracking != "none":
            last_serial = self.env['stock.lot'].search(
                ['|', ('company_id', '=', company.id), ('company_id', '=', False), ('product_id', '=', product.id)],
                limit=1, order='id DESC')
            if last_serial:
                return self.env['stock.lot'].generate_lot_names(last_serial.name, 2)[1]['lot_name']
        return False

    @api.constrains('name', 'product_id', 'company_id')
    def _check_unique_lot(self):
        domain = [('product_id', 'in', self.product_id.ids),
                  ('name', 'in', self.mapped('name'))]
        groupby = ['company_id', 'product_id', 'name']
        if any(not lot.company_id for lot in self):
            # We need to check across other companies to not have duplicates between 'no-company' and a company.
            self = self.sudo()
        records = self.with_context(skip_preprocess_gs1=True)._read_group(domain, groupby, ['__count'], order='company_id DESC')
        error_message_lines = set()
        cross_lots = {}
        for company, product, name, count in records:
            if not company:
                cross_lots[(product, name)] = count
            # For company-specific lots, we check that there is no duplicate with 'no-company' lots, but NOT between specific-company ones.
            if (company and (cross_lots.get((product, name), 0) + count) > 1) or count > 1:
                error_message_lines.add(_(" - Product: %(product)s, Lot/Serial Number: %(lot)s", product=product.display_name, lot=name))
        if error_message_lines:
            raise ValidationError(
                _(
                    "The combination of lot/serial number and product must be unique within a company including when no company is defined.\nThe following combinations contain duplicates:\n%(error_lines)s",
                    error_lines="\n".join(error_message_lines),
                ),
            )

    def _check_create(self):
        active_picking_id = self.env.context.get('active_picking_id', False)
        if active_picking_id:
            picking_id = self.env['stock.picking'].browse(active_picking_id)
            if picking_id and not picking_id.picking_type_id.use_create_lots:
                raise UserError(_('You are not allowed to create a lot or serial number with this operation type. To change this, go on the operation type and tick the box "Create New Lots/Serial Numbers".'))

    @api.depends('product_id.company_id')
    def _compute_company_id(self):
        for lot in self:
            if self.env.company in lot.product_id.company_id.all_child_ids and lot.product_id.company_id not in self.env.companies:
                lot.company_id = self.env.company
            else:
                lot.company_id = lot.product_id.company_id

    @api.depends('name')
    def _compute_display_complete(self):
        """ Defines if we want to display all fields in the stock.production.lot form view.
        It will if the record exists (`id` set) or if we precised it into the context.
        This compute depends on field `name` because as it has always a default value, it'll be
        always triggered.
        """
        for prod_lot in self:
            prod_lot.display_complete = prod_lot.id or self.env.context.get('display_complete')

    def _compute_delivery_ids(self):
        delivery_ids_by_lot = self._find_delivery_ids_by_lot_iterative()
        for lot in self:
            lot.delivery_ids = delivery_ids_by_lot.get(lot.id, [])
            lot.delivery_count = len(lot.delivery_ids)

    def _compute_partner_ids(self):
        delivery_ids_by_lot = self._find_delivery_ids_by_lot_iterative()
        for lot in self:
            if delivery_ids_by_lot.get(lot.id, []):
                lot.partner_ids = self.env['stock.picking'].browse(delivery_ids_by_lot[lot.id]).sorted(key='date_done', reverse=True).partner_id
            else:
                lot.partner_ids = False

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_single_location(self):
        for lot in self:
            quants = lot.quant_ids.filtered(lambda q: q.quantity > 0)
            lot.location_id = quants.location_id if len(quants.location_id) == 1 else False

    def _set_single_location(self):
        quants = self.quant_ids.filtered(lambda q: q.quantity > 0)
        if len(quants.location_id) == 1:
            unpack = len(quants.package_id.quant_ids) > 1
            quants.move_quants(location_dest_id=self.location_id, message=_("Lot/Serial Number Relocated"), unpack=unpack)
        elif len(quants.location_id) > 1:
            raise UserError(_('You can only move a lot/serial to a new location if it exists in a single location.'))

    @api.model_create_multi
    def create(self, vals_list):
        lot_product_ids =  {val.get('product_id') for val in vals_list} | {self.env.context.get('default_product_id')}
        self.with_context(lot_product_ids=lot_product_ids)._check_create()
        return super(StockLot, self.with_context(mail_create_nosubscribe=True)).create(vals_list)

    def write(self, vals):
        if 'company_id' in vals:
            for lot in self:
                if lot.location_id.company_id and vals['company_id'] and lot.location_id.company_id.id != vals['company_id']:
                    raise UserError(_("You cannot change the company of a lot/serial number currently in a location belonging to another company."))
        if 'product_id' in vals and any(vals['product_id'] != lot.product_id.id for lot in self):
            move_lines = self.env['stock.move.line'].search([('lot_id', 'in', self.ids), ('product_id', '!=', vals['product_id'])])
            if move_lines:
                raise UserError(_(
                    'You are not allowed to change the product linked to a serial or lot number '
                    'if some stock moves have already been created with that number. '
                    'This would lead to inconsistencies in your stock.'
                ))
        return super().write(vals)

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'name' not in default:
            for lot, vals in zip(self, vals_list):
                vals['name'] = _("(copy of) %s", lot.name)
        return vals_list

    @api.depends('quant_ids', 'quant_ids.quantity')
    @api.depends_context('owner_id', 'package_id', 'to_date', 'location', 'warehouse_id', 'allowed_company_ids')
    def _product_qty(self):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self.env['product.product'].with_context(skip_in_progress=True)._get_domain_locations()
        owner_id = self.env.context.get('owner_id')
        package_id = self.env.context.get('package_id')
        to_date = fields.Datetime.to_datetime(self.env.context.get('to_date'))
        dates_in_the_past = to_date and to_date < fields.Datetime.now()
        domain_quant = Domain([('lot_id', 'in', self.ids)]) & domain_quant_loc
        if owner_id is not None:
            domain_quant &= Domain([('owner_id', '=', owner_id)])
            domain_move_in_loc &= Domain([('owner_id', '=', owner_id)])
            domain_move_out_loc &= Domain([('owner_id', '=', owner_id)])
        if package_id is not None:
            domain_quant &= Domain([('package_id', '=', package_id)])
        quant_qty_by_lot = dict(self.env['stock.quant']._read_group(domain_quant, ['lot_id'], ['quantity:sum']))
        if not dates_in_the_past:
            for lot in self:
                lot.product_qty = quant_qty_by_lot.get(lot, 0.0)
        else:
            # If the date is in the past, we need to adjust the quantity on hand with the moves that happened after that date.
            domain_lot_done = Domain([('lot_id', 'in', self.ids), ('state', '=', 'done'), ('move_id.date', '>', to_date)])
            move_in_qty_by_lot = dict(self.env['stock.move.line']._read_group(domain_move_in_loc & domain_lot_done, ['lot_id'], ['quantity_product_uom:sum']))
            move_out_qty_by_lot = dict(self.env['stock.move.line']._read_group(domain_move_out_loc & domain_lot_done, ['lot_id'], ['quantity_product_uom:sum']))
            for lot in self:
                lot.product_qty = quant_qty_by_lot.get(lot, 0.0) - move_in_qty_by_lot.get(lot, 0.0) + move_out_qty_by_lot.get(lot, 0.0)

    def _search_product_qty(self, operator, value):
        op = PY_OPERATORS.get(operator)
        if not op:
            return NotImplemented
        if isinstance(value, Iterable) and not isinstance(value, str):
            value = {float(v) for v in value}
        else:
            value = float(value)
        domain = [
            ('lot_id', '!=', False),
            '|', ('location_id.usage', '=', 'internal'),
            '&', ('location_id.usage', '=', 'transit'), ('location_id.company_id', 'in', self.env.companies.ids)
        ]
        lots_w_qty = self.env['stock.quant']._read_group(domain=domain, groupby=['lot_id'], aggregates=['quantity:sum'], having=[('quantity:sum', '!=', 0)])
        ids = []
        lot_ids_w_qty = []
        for lot, quantity_sum in lots_w_qty:
            lot_id = lot.id
            lot_ids_w_qty.append(lot_id)
            if op(quantity_sum, value):
                ids.append(lot_id)

        # check if we need include zero values in result
        include_zero = op(0.0, value)
        if include_zero:
            return ['|', ('id', 'in', ids), ('id', 'not in', lot_ids_w_qty)]
        return [('id', 'in', ids)]

    def _search_partner_ids(self, operator, value):
        """ returns partner_ids that are directly delivered the product of the lot/SN, i.e. not
        lots/SNs that are consumed within a MO. This means this search is NOT symmetric with the
        partner_ids field within the form view since it uses different logic that isn't efficient
        enough for this search due to it being usable within the list view.
        """
        if operator in Domain.NEGATIVE_OPERATORS or not isinstance(value, (Iterable)):
            return NotImplemented
        is_no_partner = operator == 'in' and list(value) == [False]
        domain = Domain([
            ('lot_id', '!=', False),
            ('state', '=', 'done'),
        ])
        if is_no_partner:
            # reverse the search, get all lots sent to partner so we can return all lots NOT sent
            domain &= Domain('picking_partner_id', 'not in', value)
        else:
            domain &= Domain.OR([
                Domain('picking_partner_id', operator, value),
                Domain('move_partner_id', operator, value),
            ])
        domain &= Domain(self._get_outgoing_domain())
        move_lines = self.env['stock.move.line'].search(domain)

        if is_no_partner:
            return [('id', 'not in', move_lines.lot_id.ids)]
        return [('id', 'in', move_lines.lot_id.ids)]

    def action_lot_open_quants(self):
        self = self.with_context(search_default_lot_id=self.id, create=False)
        if self.env.user.has_group('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
        return self.env['stock.quant'].action_view_quants()

    def action_lot_open_transfers(self):
        self.ensure_one()

        action = {
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window'
        }
        if len(self.delivery_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.delivery_ids[0].id
            })
        else:
            action.update({
                'name': _("Delivery orders of %s", self.display_name),
                'domain': [('id', 'in', self.delivery_ids.ids)],
                'view_mode': 'list,form'
            })
        return action

    @api.model
    def _get_outgoing_domain(self):
        return [
            '|',
            '|', ('picking_code', '=', 'outgoing'), ('move_id.picking_code', '=', 'outgoing'),
            ('produce_line_ids', '!=', False),
        ]

    def _find_delivery_ids_by_lot(self, lot_path=None, delivery_by_lot=None):
        if lot_path is None:
            lot_path = set()
        domain = Domain([
            ('lot_id', 'in', self.ids),
            ('state', '=', 'done'),
        ]) & Domain(self._get_outgoing_domain())
        move_lines = self.env['stock.move.line'].search(domain)
        moves_by_lot = {
            lot_id: {'producing_lines': set(), 'barren_lines': set()}
            for lot_id in move_lines.lot_id.ids
        }
        for line in move_lines:
            if line.produce_line_ids:
                moves_by_lot[line.lot_id.id]['producing_lines'].add(line.id)
            else:
                moves_by_lot[line.lot_id.id]['barren_lines'].add(line.id)
        if delivery_by_lot is None:
            delivery_by_lot = dict()
        for lot in self:
            delivery_ids = set()

            if moves_by_lot.get(lot.id):
                producing_move_lines = self.env['stock.move.line'].browse(moves_by_lot[lot.id]['producing_lines'])
                barren_move_lines = self.env['stock.move.line'].browse(moves_by_lot[lot.id]['barren_lines'])

                if producing_move_lines:
                    lot_path.add(lot.id)
                    next_lots = producing_move_lines.produce_line_ids.lot_id.filtered(lambda l: l.id not in lot_path)
                    next_lots_ids = set(next_lots.ids)
                    # If some producing lots are in lot_path, it means that they have been previously processed.
                    # Their results are therefore already in delivery_by_lot and we add them to delivery_ids directly.
                    delivery_ids.update(*(delivery_by_lot.get(lot_id, []) for lot_id in (producing_move_lines.produce_line_ids.lot_id - next_lots).ids))

                    for lot_id, delivery_ids_set in next_lots._find_delivery_ids_by_lot(lot_path=lot_path, delivery_by_lot=delivery_by_lot).items():
                        if lot_id in next_lots_ids:
                            delivery_ids.update(delivery_ids_set)
                delivery_ids.update(barren_move_lines.picking_id.ids)

            delivery_by_lot[lot.id] = list(delivery_ids)
        return delivery_by_lot

    def _find_delivery_ids_by_lot_iterative(self):
        """ Retrieve all delivery IDs (outgoing picking) linked to the lots
            in self and all the lots found when parcouring the produce lines.
            :return: A dictionary where keys are the IDs of the original 'stock.lot'
                      records (self) and values are lists of associated 'stock.picking' IDs.
            :rtype: dict
        """

        all_lot_ids = set(self.ids)
        barren_lines = defaultdict(set)
        parent_map = defaultdict(set)

        # Prefetch the lines linked to lots and split them between producing lines
        # and barren lines (lines that have `produce_line_ids` and lines that don't
        # have them respectively) and build the map of the parents of each lot (so we
        # can browse the tree from the leaves to the root and propagate the pickings)
        queue = list(self.ids)
        while queue:
            domain = Domain([
                ('lot_id', 'in', queue),
                ('state', '=', 'done'),
            ]) & Domain(self._get_outgoing_domain())

            queue = []
            move_lines = self.env['stock.move.line'].search(domain)
            for line in move_lines:
                lot_id = line.lot_id.id

                produce_line_lot_ids = line.produce_line_ids.lot_id.ids
                if produce_line_lot_ids:
                    for child_lot_id in produce_line_lot_ids:
                        parent_map[child_lot_id].add(lot_id)
                else:
                    barren_lines[lot_id].add(line.id)

                next_lots = set(produce_line_lot_ids) - all_lot_ids
                all_lot_ids.update(next_lots)
                queue.extend(next_lots)

        # Initialize delivery_by_lot with barren lines (i.e. the leaves of the lot tree)
        lots_to_propagate = set()
        delivery_by_lot = {lot_id: set() for lot_id in all_lot_ids}
        for lot_id in barren_lines:
            barren_line_ids = barren_lines[lot_id]
            if barren_line_ids:
                barren_move_lines = self.env['stock.move.line'].browse(barren_line_ids)
                delivery_by_lot[lot_id].update(barren_move_lines.picking_id.ids)
                lots_to_propagate.add(lot_id)

        # Propagate the deliveries from the children to their parent lots.
        # This loop processes lots whose delivery sets have just been updated,
        # ensuring the new results are merged upward through the parent graph until
        # all deliveries are propagated
        while lots_to_propagate:
            lot_id = lots_to_propagate.pop()

            parent_ids = parent_map[lot_id]
            for parent_id in parent_ids:
                if not delivery_by_lot[lot_id].issubset(delivery_by_lot[parent_id]):
                    delivery_by_lot[parent_id].update(delivery_by_lot[lot_id])
                    lots_to_propagate.add(parent_id)

        return {lot_id: list(delivery_by_lot[lot_id]) for lot_id in delivery_by_lot}


# FILEPATH: odoo/addons/stock/models/stock_move.py
PROCUREMENT_PRIORITIES = [('0', 'Normal'), ('1', 'Urgent')]
class StockMove(models.Model):
    _name = 'stock.move'
    _description = "Stock Move"
    _order = 'sequence, id'
    _rec_name = 'reference'

    sequence = fields.Integer('Sequence', default=10)
    priority = fields.Selection(
        PROCUREMENT_PRIORITIES, 'Priority', default='0',
        compute="_compute_priority", store=True)
    date = fields.Datetime(
        'Date Scheduled', default=fields.Datetime.now, index=True, required=True,
        help="Scheduled date until move is done, then date of actual move processing")
    date_deadline = fields.Datetime(
        "Deadline", readonly=True, copy=False,
        help="In case of outgoing flow, validate the transfer before this date to allow to deliver at promised date to the customer.\n\
        In case of incoming flow, validate the transfer before this date in order to have these products in stock at the date promised by the supplier")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True, required=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        check_company=True,
        domain="[('type', '=', 'consu')]", index=True, required=True)
    product_category_id = fields.Many2one(
        'product.category', 'Product Category',
        related='product_id.categ_id')
    never_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value',
        'template_attribute_value_stock_move_rel',
        'move_id', 'template_attribute_value_id',
        string="Never attribute Values"
    )
    description_picking = fields.Text(string="Description Of Picking", compute='_compute_description_picking', inverse='_inverse_description_picking', compute_sudo=True)
    description_picking_manual = fields.Text(readonly=True)
    product_qty = fields.Float(
        'Real Quantity', compute='_compute_product_qty', inverse='_set_product_qty',
        digits=0, store=True, compute_sudo=True,
        help='Quantity in the default UoM of the product')
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit',
        default=0, required=True,
        help="This is the quantity of product that is planned to be moved."
             "Lowering this quantity does not generate a backorder."
             "Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    product_uom = fields.Many2one(
        'uom.uom', "Unit", required=True, domain="[('id', 'in', allowed_uom_ids)]",
        compute="_compute_product_uom", store=True, readonly=False, precompute=True,
    )
    # TDE FIXME: make it stored, otherwise group will not work
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        related='product_id.product_tmpl_id')
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        help='The operation takes and suggests products from this location.',
        bypass_search_access=True, index=True, required=True,
        compute='_compute_location_id', store=True, precompute=True, readonly=False,
        check_company=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Intermediate Location', required=True,
        help='The operations brings product to this location', readonly=False,
        index=True, store=True, compute='_compute_location_dest_id', precompute=True, inverse='_set_location_dest_id')
    location_final_id = fields.Many2one(
        'stock.location', 'Final Location',
        readonly=False, store=True,
        help="The operation brings the products to the intermediate location."
        "But this operation is part of a chain of operations targeting the final location.",
        bypass_search_access=True, index=True, check_company=True)
    location_usage = fields.Selection(string="Source Location Type", related='location_id.usage')
    location_dest_usage = fields.Selection(string="Destination Location Type", related='location_dest_id.usage')
    partner_id = fields.Many2one(
        'res.partner', 'Destination Address ',
        help="Optional address where goods are to be delivered, specifically used for allotment",
        compute='_compute_partner_id', store=True, readonly=False,
        index='btree_not_null')
    move_dest_ids = fields.Many2many(
        'stock.move', 'stock_move_move_rel', 'move_orig_id', 'move_dest_id', 'Destination Moves',
        copy=False,
        help="Optional: next stock move when chaining them")
    move_orig_ids = fields.Many2many(
        'stock.move', 'stock_move_move_rel', 'move_dest_id', 'move_orig_id', 'Original Move',
        copy=False,
        help="Optional: previous stock move when chaining them")
    picking_id = fields.Many2one('stock.picking', 'Transfer', index=True, check_company=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', index=True, readonly=True,
        help="* New: The stock move is created but not confirmed.\n"
             "* Waiting Another Move: A linked stock move should be done before this one.\n"
             "* Waiting: The stock move is confirmed but the product can't be reserved.\n"
             "* Available: The product of the stock move is reserved.\n"
             "* Done: The product has been transferred and the transfer has been confirmed.")
    picked = fields.Boolean(
        'Picked', compute='_compute_picked', inverse='_inverse_picked',
        store=True, readonly=False, copy=False, default=False,
        help="This checkbox is just indicative, it doesn't validate or generate any product moves.")

    # used to record the product cost set by the user during a picking confirmation (when costing
    # method used is 'average price' or 'real'). Value given in company currency and in product uom.
    # as it's a technical field, we intentionally don't provide the digits attribute
    price_unit = fields.Float('Unit Price', copy=False)
    origin = fields.Char("Source Document")
    procure_method = fields.Selection([
        ('make_to_stock', 'Default: Take From Stock'),
        ('make_to_order', 'Advanced: Apply Procurement Rules')], string='Supply Method',
        default='make_to_stock', required=True, copy=False,
        help="By default, the system will take from the stock in the source location and passively wait for availability. "
             "The other possibility allows you to directly create a procurement on the source location (and thus ignore "
             "its current stock) to gather products. If we want to chain moves and have this one to wait for the previous, "
             "this second option should be chosen.")
    scrap_id = fields.Many2one('stock.scrap', 'Scrap operation', readonly=True, check_company=True, index='btree_not_null')
    procurement_values = fields.Json(store=False, help="Dummy field to store procurement values to propagate them to later steps")
    reference_ids = fields.Many2many(
        'stock.reference', 'stock_reference_move_rel', 'move_id', 'reference_id', string='References')
    rule_id = fields.Many2one(
        'stock.rule', 'Stock Rule', ondelete='restrict', help='The stock rule that created this stock move',
        check_company=True)
    propagate_cancel = fields.Boolean(
        'Propagate cancel and split', default=True,
        help='If checked, when this move is cancelled, cancel the linked move too')
    delay_alert_date = fields.Datetime('Delay Alert Date', help='Process at this date to be on time', compute="_compute_delay_alert_date", store=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', compute='_compute_picking_type_id', store=True, readonly=False, check_company=True)
    is_inventory = fields.Boolean('Inventory')
    inventory_name = fields.Char(readonly=True)
    move_line_ids = fields.One2many('stock.move.line', 'move_id')
    package_ids = fields.One2many('stock.package', string='Packages', compute="_compute_package_ids")
    origin_returned_move_id = fields.Many2one(
        'stock.move', 'Origin return move', copy=False, index=True,
        help='Move that created the return move', check_company=True)
    returned_move_ids = fields.One2many('stock.move', 'origin_returned_move_id', 'All returned moves', help='Optional: all returned moves created from this move')
    availability = fields.Float(
        'Forecasted Quantity', compute='_compute_product_availability',
        readonly=True, help='Quantity in stock that can still be reserved for this move')
    # used to depict a restriction on the ownership of quants to consider when marking this move as 'done'
    restrict_partner_id = fields.Many2one(
        'res.partner', 'Owner ', check_company=True,
        index='btree_not_null')
    route_ids = fields.Many2many(
        'stock.route', 'stock_route_move', 'move_id', 'route_id', 'Destination route', help="Preferred route")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="the warehouse to consider for the route selection on the next procurement (if any).")
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking')
    has_lines_without_result_package = fields.Boolean(compute="_compute_has_lines_without_result_package")
    quantity = fields.Float(
        'Quantity', compute='_compute_quantity', digits='Product Unit', inverse='_set_quantity', store=True)
    # TODO: delete this field `show_operations`
    show_operations = fields.Boolean(related='picking_id.picking_type_id.show_operations')
    picking_code = fields.Selection(related='picking_id.picking_type_id.code', readonly=True)
    show_details_visible = fields.Boolean('Details Visible', compute='_compute_show_details_visible')
    is_storable = fields.Boolean(related='product_id.is_storable')
    additional = fields.Boolean("Whether the move was added after the picking's confirmation", default=False)
    is_locked = fields.Boolean(compute='_compute_is_locked', readonly=True)
    is_initial_demand_editable = fields.Boolean('Is initial demand editable', compute='_compute_is_initial_demand_editable')
    is_date_editable = fields.Boolean("Is Date Editable", compute="_compute_is_date_editable")
    is_quantity_done_editable = fields.Boolean('Is quantity done editable', compute='_compute_is_quantity_done_editable')
    reference = fields.Char(compute='_compute_reference', string="Reference", store=True)
    move_lines_count = fields.Integer(compute='_compute_move_lines_count')
    display_assign_serial = fields.Boolean(compute='_compute_display_assign_serial')
    display_import_lot = fields.Boolean(compute='_compute_display_assign_serial')
    next_serial = fields.Char('First SN/Lot')
    next_serial_count = fields.Integer('Number of SN/Lots')
    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'Original Reordering Rule', index=True)
    forecast_availability = fields.Float('Forecast Availability', compute='_compute_forecast_information', digits='Product Unit', compute_sudo=True)
    forecast_expected_date = fields.Datetime('Forecasted Expected date', compute='_compute_forecast_information', compute_sudo=True)
    lot_ids = fields.Many2many('stock.lot', compute='_compute_lot_ids', inverse='_set_lot_ids', string='Serial Numbers', readonly=False)
    reservation_date = fields.Date('Date to Reserve', compute='_compute_reservation_date', store=True, help="Computes when a move should be reserved")
    packaging_uom_id = fields.Many2one('uom.uom', 'Packaging', help="Packaging unit from sale or purchase orders", compute='_compute_packaging_uom_id', precompute=True, store=True)
    packaging_uom_qty = fields.Float('Packaging Quantity', help="Quantity in the packaging unit", compute='_compute_packaging_uom_qty', store=True)
    show_quant = fields.Boolean("Show Quant", compute="_compute_show_info")
    show_lots_m2o = fields.Boolean("Show lot_id", compute="_compute_show_info")
    show_lots_text = fields.Boolean("Show lot_name", compute="_compute_show_info")

    _product_location_index = models.Index("(product_id, location_id, location_dest_id, company_id, state)")

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids', 'product_id.seller_ids', 'product_id.seller_ids.product_uom_id')
    def _compute_allowed_uom_ids(self):
        for move in self:
            move.allowed_uom_ids = move.product_id.uom_id | move.product_id.uom_ids | move.sudo().product_id.seller_ids.product_uom_id

    @api.depends('product_id')
    def _compute_product_uom(self):
        for move in self:
            move.product_uom = move.product_id.uom_id.id

    @api.depends('picking_id.location_id')
    def _compute_location_id(self):
        for move in self:
            if move.picked:
                continue
            if not (location := move.location_id) or move.picking_id != move._origin.picking_id or move.picking_type_id != move._origin.picking_type_id:
                if move.picking_id:
                    location = move.picking_id.location_id
                elif move.picking_type_id:
                    location = move.picking_type_id.default_location_src_id
            move.location_id = location

    @api.depends('picking_id.location_dest_id')
    def _compute_location_dest_id(self):
        customer_loc, __ = self.env['stock.warehouse']._get_partner_locations()
        inter_comp_location = self.env.ref('stock.stock_location_inter_company', raise_if_not_found=False)
        for move in self:
            location_dest = False
            if move.picking_id:
                location_dest = move.picking_id.location_dest_id
            elif move.rule_id.location_dest_from_rule:
                location_dest = move.rule_id.location_dest_id
            elif move.picking_type_id:
                location_dest = move.picking_type_id.default_location_dest_id
            is_move_to_interco_transit = False
            if location_dest:
                is_move_to_interco_transit = location_dest._child_of(customer_loc) and move.location_final_id == inter_comp_location
            if location_dest and move.location_final_id and (move.location_final_id._child_of(location_dest) or is_move_to_interco_transit):
                # Force the location_final as dest in the following cases:
                # - The location_final is a sublocation of destination -> Means we reached the end
                # - The location dest is an out location (i.e. Customers) but the final dest is different (e.g. Inter-Company transfers)
                location_dest = move.location_final_id
            move.location_dest_id = location_dest

    def _set_location_dest_id(self):
        for ml in self.move_line_ids:
            parent_path = [int(loc_id) for loc_id in ml.location_dest_id.parent_path.split('/')[:-1]]
            if ml.move_id.location_dest_id.id in parent_path:
                continue
            loc_dest = ml.move_id.location_dest_id._get_putaway_strategy(ml.product_id, ml.quantity_product_uom)
            ml.location_dest_id = loc_dest

    @api.depends('has_tracking', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'product_id')
    def _compute_display_assign_serial(self):
        for move in self:
            move.display_import_lot = (
                move.has_tracking != 'none' and
                move.product_id and
                move.picking_type_id.use_create_lots and
                not move.origin_returned_move_id.id and
                move.state not in ('done', 'cancel')
            )
            move.display_assign_serial = move.display_import_lot

    @api.depends('move_line_ids.result_package_id')
    def _compute_has_lines_without_result_package(self):
        for move in self:
            move.has_lines_without_result_package = move.move_line_ids.result_package_id and any(not line.result_package_id for line in move.move_line_ids)

    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.result_package_id.outermost_package_id')
    def _compute_package_ids(self):
        for move in self:
            if move.state in ['done', 'cancel']:
                move.package_ids = move.move_line_ids.package_history_id.outermost_dest_id
            else:
                # Only display the top-level packages until the move is done.
                move.package_ids = move.move_line_ids.result_package_id.outermost_package_id

    @api.depends('move_line_ids.picked', 'state')
    def _compute_picked(self):
        for move in self:
            if move.state == 'done' or any(ml.picked for ml in move.move_line_ids):
                move.picked = True
            elif move.move_line_ids:
                move.picked = False

    def _inverse_picked(self):
        for move in self:
            move.move_line_ids.picked = move.picked

    @api.depends('picking_id.priority')
    def _compute_priority(self):
        for move in self:
            move.priority = move.picking_id.priority or '0'

    @api.depends('picking_id.picking_type_id')
    def _compute_picking_type_id(self):
        for move in self:
            if move.picking_id:
                move.picking_type_id = move.picking_id.picking_type_id

    @api.depends('picking_id.is_locked')
    def _compute_is_locked(self):
        for move in self:
            if move.picking_id:
                move.is_locked = move.picking_id.is_locked
            else:
                move.is_locked = False

    def _compute_is_date_editable(self):
        for move in self:
            if move.picking_id:
                move.is_date_editable = move.picking_id.is_date_editable
            else:
                move.is_date_editable = True

    @api.depends('product_id', 'has_tracking', 'move_line_ids')
    def _compute_show_details_visible(self):
        """ According to this field, the button that calls `action_show_details` will be displayed
        to work on a move from its picking form view, or not.
        """
        has_package = self.env.user.has_group('stock.group_tracking_lot')
        multi_locations_enabled = self.env.user.has_group('stock.group_stock_multi_locations')
        consignment_enabled = self.env.user.has_group('stock.group_tracking_owner')

        show_details_visible = multi_locations_enabled or has_package or consignment_enabled

        for move in self:
            if (
                not move.product_id
                or move.state == "draft"
                or (
                    not move.picking_type_id.use_create_lots
                    and not move.picking_type_id.use_existing_lots
                    and not self.env.user.has_group("stock.group_stock_tracking_lot")
                    and not self.env.user.has_group("stock.group_stock_multi_locations")
                )
            ):
                move.show_details_visible = False
            elif len(move.move_line_ids) > 1:
                move.show_details_visible = True
            else:
                move.show_details_visible = show_details_visible or move.has_tracking != 'none'

    @api.depends('state', 'picking_id.is_locked')
    def _compute_is_initial_demand_editable(self):
        for move in self:
            move.is_initial_demand_editable = not move.picking_id.is_locked or move.state == 'draft'

    @api.depends('product_id')
    def _compute_is_quantity_done_editable(self):
        for move in self:
            move.is_quantity_done_editable = move.product_id

    @api.depends('picking_id.name', 'scrap_id.name', 'location_dest_usage', 'is_inventory', 'inventory_name')
    def _compute_reference(self):
        for move in self:
            if move.scrap_id:
                move.reference = move.scrap_id.name
            elif move.is_inventory:
                if move.inventory_name:
                    move.reference = move.inventory_name
                else:
                    move.reference = _('Product Quantity Confirmed') if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) else _('Product Quantity Updated')
                    if move.create_uid and move.create_uid.id != SUPERUSER_ID:
                        move.reference += f' ({move.create_uid.display_name})'
            else:
                move.reference = move.picking_id.name

    @api.depends('move_line_ids')
    def _compute_move_lines_count(self):
        for move in self:
            move.move_lines_count = len(move.move_line_ids)

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'state')
    def _compute_product_qty(self):
        for move in self:
            move.product_qty = move.product_uom._compute_quantity(
                move.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')

    @api.depends('picking_id.partner_id')
    def _compute_partner_id(self):
        for move in self.filtered(lambda m: m.picking_id):
            move.partner_id = move.picking_id.partner_id

    @api.depends('move_orig_ids.date', 'move_orig_ids.state', 'state', 'date')
    def _compute_delay_alert_date(self):
        for move in self:
            if move.state in ('done', 'cancel'):
                move.delay_alert_date = False
                continue
            prev_moves = move.move_orig_ids.filtered(lambda m: m.state not in ('done', 'cancel') and m.date)
            prev_max_date = max(prev_moves.mapped("date"), default=False)
            if prev_max_date and prev_max_date > move.date:
                move.delay_alert_date = prev_max_date
            else:
                move.delay_alert_date = False

    def _quantity_sml(self):
        self.ensure_one()
        quantity = 0
        for move_line in self.move_line_ids:
            quantity += move_line.product_uom_id._compute_quantity(move_line.quantity, self.product_uom, round=False)
        return quantity

    @api.depends('move_line_ids.quantity', 'move_line_ids.product_uom_id')
    def _compute_quantity(self):
        """ This field represents the sum of the move lines `quantity`. It allows the user to know
        if there is still work to do.

        We take care of rounding this value at the general decimal precision and not the rounding
        of the move's UOM to make sure this value is really close to the real sum, because this
        field will be used in `_action_done` in order to know if the move will need a backorder or
        an extra move.
        """
        if not any(self._ids):
            # onchange
            for move in self:
                move.quantity = move._quantity_sml()
        else:
            # compute
            move_lines_ids = set()
            for move in self:
                move_lines_ids |= set(move.move_line_ids.ids)

            data = self.env['stock.move.line']._read_group(
                [('id', 'in', list(move_lines_ids))],
                ['move_id', 'product_uom_id'], ['quantity:sum']
            )
            sum_qty = defaultdict(float)
            for move, product_uom, qty_sum in data:
                uom = move.product_uom
                sum_qty[move.id] += product_uom._compute_quantity(qty_sum, uom, round=False)

            for move in self:
                move.quantity = sum_qty[move.id]

    def _set_quantity(self):
        def _process_decrease(move, quantity):
            mls_to_unlink = set()
            # Since the move lines might have been created in a certain order to respect
            # a removal strategy, they need to be unreserved in the opposite order
            for ml in reversed(move.move_line_ids.sorted('id')):
                if self.env.context.get('unreserve_unpicked_only') and ml.picked:
                    continue
                if move.product_uom.is_zero(quantity):
                    break
                qty_ml_dec = min(ml.quantity, ml.product_uom_id._compute_quantity(quantity, ml.product_uom_id, round=False))
                if ml.product_uom_id.is_zero(qty_ml_dec):
                    continue
                if ml.product_uom_id.compare(ml.quantity, qty_ml_dec) == 0 and ml.state not in ['done', 'cancel']:
                    mls_to_unlink.add(ml.id)
                else:
                    ml.quantity -= qty_ml_dec
                quantity -= move.product_uom._compute_quantity(qty_ml_dec, move.product_uom, round=False)
            self.env['stock.move.line'].browse(mls_to_unlink).unlink()

        def _process_increase(move, quantity):
            # move._action_assign(quantity)
            move._set_quantity_done(move.quantity)

        err = []
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit')
        for move in self:
            rounded_qty = float_round(move.quantity, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(rounded_qty, move.quantity, precision_digits=precision_digits) != 0:
                err.append(_("""
The quantity done for the product %(product)s doesn't respect the rounding precision defined on the system.
Please change the quantity done or the rounding precision in your settings.""",
                             product=move.product_id.display_name))
                continue
            delta_qty = move.quantity - move._quantity_sml()
            if move.product_uom.compare(delta_qty, 0) > 0:
                _process_increase(move, delta_qty)
            elif move.product_uom.compare(delta_qty, 0) < 0:
                _process_decrease(move, abs(delta_qty))
        if err:
            raise UserError('\n'.join(err))

    def _set_product_qty(self):
        """ The meaning of product_qty field changed lately and is now a functional field computing the quantity
        in the default product UoM. This code has been added to raise an error if a write is made given a value
        for `product_qty`, where the same write should set the `product_uom_qty` field instead, in order to
        detect errors. """
        raise UserError(_('The requested operation cannot be processed because of a programming error setting the `product_qty` field instead of the `product_uom_qty`.'))

    @api.depends('state', 'product_id', 'product_qty', 'location_id')
    def _compute_product_availability(self):
        """ Fill the `availability` field on a stock move, which is the quantity to potentially
        reserve. When the move is done, `availability` is set to the quantity the move did actually
        move.
        """
        for move in self:
            if move.state == 'done':
                move.availability = move.product_qty
            else:
                total_availability = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id) if move.product_id else 0.0
                move.availability = min(move.product_qty, total_availability)

    @api.depends('product_id', 'product_qty', 'picking_type_id', 'quantity', 'priority', 'state', 'product_uom_qty', 'location_id')
    def _compute_forecast_information(self):
        """ Compute forecasted information of the related product by warehouse."""
        self.forecast_availability = False
        self.forecast_expected_date = False

        # Prefetch product info to avoid fetching all product fields
        self.product_id.fetch(['type', 'uom_id'])

        not_product_moves = self.filtered(lambda move: not move.product_id.is_storable)
        for move in not_product_moves:
            move.forecast_availability = move.product_qty

        product_moves = (self - not_product_moves)

        outgoing_unreserved_moves_per_warehouse = defaultdict(set)
        now = fields.Datetime.now()

        def key_virtual_available(move, incoming=False):
            warehouse_id = move.location_dest_id.warehouse_id.id if incoming else move.location_id.warehouse_id.id
            return warehouse_id, max(move.date or now, now)

        # Prefetch efficiently virtual_available for _is_consuming draft move.
        prefetch_virtual_available = defaultdict(set)
        virtual_available_dict = {}
        for move in product_moves:
            if move._is_consuming() and move.state == 'draft' or move.picking_code == 'internal':
                prefetch_virtual_available[key_virtual_available(move)].add(move.product_id.id)
            elif move.picking_type_id.code == 'incoming':
                prefetch_virtual_available[key_virtual_available(move, incoming=True)].add(move.product_id.id)
        for key_context, product_ids in prefetch_virtual_available.items():
            read_res = self.env['product.product'].browse(product_ids).with_context(warehouse_id=key_context[0], to_date=key_context[1]).read([
                'virtual_available',
                'free_qty',
            ])
            virtual_available_dict[key_context] = {res['id']: (res['virtual_available'], res['free_qty']) for res in read_res}

        for move in product_moves:
            if key_virtual_available(move) in virtual_available_dict and move.product_id.id in virtual_available_dict[key_virtual_available(move)]:
                free_qty = virtual_available_dict[key_virtual_available(move)][move.product_id.id][1]
            else:
                free_qty = 0.0
            if move.state == 'assigned':
                move.forecast_availability = move.product_uom._compute_quantity(
                    move.quantity, move.product_id.uom_id, rounding_method='HALF-UP')
                continue
            elif move.state == 'draft' and float_compare(free_qty, move.product_qty, precision_rounding=move.product_id.uom_id.rounding) >= 0:
                move.forecast_availability = free_qty
                continue
            if move._is_consuming():
                if move.state == 'draft':
                    # for move _is_consuming and in draft -> the forecast_availability > 0 if in stock
                    move.forecast_availability = virtual_available_dict[key_virtual_available(move)][move.product_id.id][0] - move.product_qty
                elif move.state in ('waiting', 'confirmed', 'partially_available'):
                    outgoing_unreserved_moves_per_warehouse[move.location_id.warehouse_id].add(move.id)
            elif move.picking_type_id.code == 'internal':
                if float_compare(free_qty, move.product_qty, precision_rounding=move.product_id.uom_id.rounding) >= 0:
                    move.forecast_availability = free_qty
                    continue
            elif move.picking_type_id.code == 'incoming':
                forecast_availability = virtual_available_dict[key_virtual_available(move, incoming=True)][move.product_id.id][0]
                if move.state == 'draft':
                    forecast_availability += move.product_qty
                move.forecast_availability = forecast_availability

        for warehouse, moves_ids in outgoing_unreserved_moves_per_warehouse.items():
            if not warehouse:  # No prediction possible if no warehouse.
                continue
            moves_per_location = self.browse(moves_ids).grouped('location_id')
            for location, mvs in moves_per_location.items():
                forecast_info = mvs._get_forecast_availability_outgoing(warehouse, location)
                for move in mvs:
                    move.forecast_availability, move.forecast_expected_date = forecast_info[move]

    def _set_date_deadline(self, new_deadline):
        # Handle the propagation of `date_deadline` fields (up and down stream - only update by up/downstream documents)
        already_propagate_ids = self.env.context.get('date_deadline_propagate_ids', set())
        already_propagate_ids.update(self.ids)
        self = self.with_context(date_deadline_propagate_ids=already_propagate_ids)
        for move in self:
            moves_to_update = (move.move_dest_ids | move.move_orig_ids)
            if move.date_deadline:
                delta = move.date_deadline - fields.Datetime.to_datetime(new_deadline)
            else:
                delta = 0
            for move_update in moves_to_update:
                if move_update.state in ('done', 'cancel'):
                    continue
                if move_update.id in already_propagate_ids:
                    continue
                if move_update.date_deadline and delta:
                    move_update.date_deadline -= delta
                elif not move_update.date_deadline or move_update.date_deadline != new_deadline:
                    move_update.date_deadline = new_deadline

    @api.depends('move_line_ids.lot_id', 'move_line_ids.quantity')
    def _compute_lot_ids(self):
        domain = [('move_id', 'in', self.ids), ('lot_id', '!=', False), ('quantity', '!=', 0.0)]
        lots_by_move_id = self.env['stock.move.line']._read_group(
            domain,
            ['move_id'], ['lot_id:array_agg'],
        )
        lots_by_move_id = {move.id: lot_ids for move, lot_ids in lots_by_move_id}
        for move in self:
            move.lot_ids = lots_by_move_id.get(move._origin.id, [])

    def _set_lot_ids(self):
        for move in self:
            if move.state == 'assigned' and all(ml.lot_id in move.lot_ids for ml in move.move_line_ids):
                continue
            move_lines_commands = []
            mls = move.move_line_ids
            mls_with_lots = mls.filtered(lambda ml: ml.lot_id)
            mls_without_lots = (mls - mls_with_lots)
            for ml in mls_with_lots:
                if ml.quantity and ml.lot_id not in move.lot_ids:
                    move_lines_commands.append((2, ml.id))
            ls = move.move_line_ids.lot_id
            for lot in move.lot_ids:
                if lot not in ls:
                    if mls_without_lots[:1]:  # Updates an existing line without serial number.
                        move_line = mls_without_lots[:1]
                        move_lines_commands.append(Command.update(move_line.id, {
                            'lot_id': lot.id,
                            'product_uom_id': move.product_id.uom_id.id if move.product_id.tracking == 'serial' else move.product_uom.id,
                            'quantity': 1 if move.product_id.tracking == 'serial' else move.quantity,
                        }))
                        mls_without_lots -= move_line
                    else:  # No line without serial number, creates a new one.
                        reserved_quants = self.env['stock.quant'].with_context(packaging_uom_id=move.packaging_uom_id)._get_reserve_quantity(move.product_id, move.location_id, 1.0, lot_id=lot)
                        if reserved_quants and reserved_quants[0][0].lot_id:
                            move_line_vals = self._prepare_move_line_vals(quantity=0, reserved_quant=reserved_quants[0][0])
                        else:
                            move_line_vals = self._prepare_move_line_vals(quantity=0)
                            move_line_vals['lot_id'] = lot.id
                        move_line_vals['product_uom_id'] = move.product_id.uom_id.id
                        move_line_vals['quantity'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))
                else:
                    move_line = move.move_line_ids.filtered(lambda line: line.lot_id.id == lot.id)
                    move_line.quantity = 1
            move.write({'move_line_ids': move_lines_commands})

    @api.depends('picking_type_id', 'date', 'priority', 'state')
    def _compute_reservation_date(self):
        for move in self:
            if move.picking_type_id.reservation_method == 'by_date' and move.state in ['draft', 'confirmed', 'waiting', 'partially_available']:
                days = move.picking_type_id.reservation_days_before
                if move.priority == '1':
                    days = move.picking_type_id.reservation_days_before_priority
                move.reservation_date = fields.Date.to_date(move.date) - timedelta(days=days)
            elif move.picking_type_id.reservation_method == 'manual':
                move.reservation_date = False

    @api.depends('product_uom')
    def _compute_packaging_uom_id(self):
        for move in self:
            move.packaging_uom_id = move.product_uom

    @api.depends('product_uom_qty', 'packaging_uom_id')
    def _compute_packaging_uom_qty(self):
        for move in self:
            if move.packaging_uom_id:
                move.packaging_uom_qty = move.product_uom._compute_quantity(move.product_uom_qty, move.packaging_uom_id)

    @api.depends(
        'has_tracking',
        'picking_type_id.use_create_lots',
        'picking_type_id.use_existing_lots',
        'state',
        'origin_returned_move_id',
        'product_id.type',
        'picking_code',
    )
    def _compute_show_info(self):
        for move in self:
            move.show_quant = move.picking_code != 'incoming'\
                           and move.product_id.is_storable
            move.show_lots_text = move.has_tracking != 'none'\
                and move.picking_type_id.use_create_lots\
                and not move.picking_type_id.use_existing_lots\
                and move.state != 'done' \
                and not move.origin_returned_move_id.id
            move.show_lots_m2o = not move.show_quant\
                and not move.show_lots_text\
                and move.has_tracking != 'none'\
                and (move.picking_type_id.use_existing_lots or move.state == 'done' or move.origin_returned_move_id.id)

    @api.model
    def default_get(self, fields):
        # We override the default_get to make stock moves created after the picking was confirmed
        # directly as available in immediate transfer mode. This allows to create extra move lines
        # in the fp view. In planned transfer, the stock move are marked as `additional` and will be
        # auto-confirmed.
        defaults = super().default_get(fields)
        if self.env.context.get('default_picking_id'):
            picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
            if picking_id.state == 'done':
                defaults['state'] = 'done'
                defaults['additional'] = True
            elif picking_id.state not in ['cancel', 'draft', 'done']:
                defaults['additional'] = True  # to trigger `_autoconfirm_picking`
        return defaults

    @api.depends('picking_id', 'product_id', 'location_id', 'location_dest_id')
    def _compute_display_name(self):
        for move in self:
            move.display_name = '%s%s%s>%s' % (
                move.picking_id.origin and '%s/' % move.picking_id.origin or '',
                move.product_id.code and '%s: ' % move.product_id.code or '',
                move.location_id.name, move.location_dest_id.name)

    def _set_references(self):
        for move in self:
            if not move.reference_ids and move.picking_id:
                move.reference_ids = move.picking_id.reference_ids

    @api.depends('product_id', 'picking_type_id', 'description_picking_manual')
    def _compute_description_picking(self):
        for move in self:
            if move.description_picking_manual:
                move.description_picking = move.description_picking_manual
            elif move.product_id:
                product = move.product_id.with_context(lang=move._get_lang())
                move.description_picking = product._get_picking_description(move.picking_type_id) or move._get_description()
            else:
                move.description_picking = ""

    def _get_description(self):
        product = self.product_id.with_context(lang=self._get_lang())
        return product._get_description(self.picking_type_id)

    def _inverse_description_picking(self):
        for move in self:
            move.description_picking_manual = move.description_picking

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (vals.get('quantity') or vals.get('move_line_ids')) and 'lot_ids' in vals:
                vals.pop('lot_ids')
            picking_id = self.env['stock.picking'].browse(vals.get('picking_id'))
            if picking_id.state == 'done' and vals.get('state') != 'done':
                vals['state'] = 'done'
            if vals.get('state') == 'done':
                vals['picked'] = True
        res = super().create(vals_list)
        res._update_orderpoints()
        res._set_references()
        return res

    def write(self, vals):
        # Handle the write on the initial demand by updating the reserved quantity and logging
        # messages according to the state of the stock.move records.
        receipt_moves_to_reassign = self.env['stock.move']
        move_to_recompute_state = self.env['stock.move']
        move_to_check_location = self.env['stock.move']
        if 'quantity' in vals:
            if any(move.state == 'cancel' for move in self):
                raise UserError(_('You cannot change a cancelled stock move, create a new line instead.'))
        if 'product_uom' in vals and any(move.state == 'done' for move in self) and not self.env.context.get('skip_uom_conversion'):
            raise UserError(_('You cannot change the UoM for a stock move that has been set to \'Done\'.'))
        if 'product_uom_qty' in vals:
            for move in self.filtered(lambda m: m.state not in ('done', 'draft') and m.picking_id):
                if move.product_uom.compare(vals['product_uom_qty'], move.product_uom_qty):
                    self.env['stock.move.line']._log_message(move.picking_id, move, 'stock.track_move_template', vals)
            if self.env.context.get('do_not_unreserve') is None:
                move_to_unreserve = self.filtered(
                    lambda m: m.state not in ['draft', 'done', 'cancel'] and m.product_uom.compare(m.quantity, vals.get('product_uom_qty')) == 1
                )
                move_to_unreserve._do_unreserve()
                (self - move_to_unreserve).filtered(lambda m: m.state == 'assigned').write({'state': 'partially_available'})
                # When editing the initial demand, directly run again action assign on receipt moves.
                receipt_moves_to_reassign |= move_to_unreserve.filtered(lambda m: m.location_id.usage == 'supplier')
                receipt_moves_to_reassign |= (self - move_to_unreserve).filtered(
                    lambda m:
                        m.location_id.usage == 'supplier' and
                        m.state in ('partially_available', 'assigned')
                )
                move_to_recompute_state |= self - move_to_unreserve - receipt_moves_to_reassign
        if 'date_deadline' in vals:
            self._set_date_deadline(vals.get('date_deadline'))
        if 'move_orig_ids' in vals:
            move_to_recompute_state |= self.filtered(lambda m: m.state not in ['draft', 'cancel', 'done'])
        if 'location_id' in vals:
            move_to_check_location = self.filtered(lambda m: m.location_id.id != vals.get('location_id'))
        if 'product_id' in vals or 'location_id' in vals or 'location_dest_id' in vals:
            self._update_orderpoints()
        res = super().write(vals)
        moves_done = self.filtered(lambda m: m.state == 'done')
        if 'date' in vals and moves_done:
            moves_done.move_line_ids.date = vals['date']
        if move_to_recompute_state:
            move_to_recompute_state._recompute_state()
        if move_to_check_location:
            for ml in move_to_check_location.move_line_ids:
                parent_path = [int(loc_id) for loc_id in ml.location_id.parent_path.split('/')[:-1]]
                if move_to_check_location.location_id.id not in parent_path:
                    receipt_moves_to_reassign |= move_to_check_location
                    move_to_check_location.procure_method = 'make_to_stock'
                    move_to_check_location.move_orig_ids = [Command.clear()]
                    ml.unlink()
        if 'location_id' in vals or 'location_dest_id' in vals:
            wh_by_moves = defaultdict(self.env['stock.move'].browse)
            for move in self:
                move_warehouse = move.location_id.warehouse_id or move.location_dest_id.warehouse_id
                if move_warehouse == move.warehouse_id:
                    continue
                wh_by_moves[move_warehouse] |= move
            for warehouse, moves in wh_by_moves.items():
                moves.warehouse_id = warehouse.id
        if receipt_moves_to_reassign:
            receipt_moves_to_reassign._action_assign()
        if ('product_id' in vals or 'state' in vals or 'date' in vals or 'product_uom_qty' in vals or
                'location_id' in vals or 'location_dest_id' in vals):
            self._update_orderpoints()
        if 'picking_id' in vals:
            self._set_references()
        return res

    def _update_orderpoints(self):
        """ Manually mark the relevant orderpoints for re-computation.
        This allows us to only recompute the qty_to_order for the orderpoints in the relevant warehouse(s),
        instead of all the orderpoints linked to the product."""
        if not self:
            return
        domains = []
        for move in self:
            domain_for_move = Domain('product_id', '=', move.product_id.id)
            wh_ids = move.location_id.warehouse_id.ids + move.location_dest_id.warehouse_id.ids
            if wh_ids:
                domain_for_move &= Domain('warehouse_id', 'in', wh_ids)
            domains.append(domain_for_move)
        orderpoints = self.env['stock.warehouse.orderpoint'].sudo().search(Domain.OR(domains), order='id')
        orderpoints.invalidate_recordset(['qty_to_order', 'qty_forecast'])
        self.env.add_to_compute(self.env['stock.warehouse.orderpoint']._fields['qty_to_order_computed'], orderpoints)

    def _delay_alert_get_documents(self):
        """Returns a list of recordset of the documents linked to the stock.move in `self` in order
        to post the delay alert next activity. These documents are deduplicated. This method is meant
        to be overridden by other modules, each of them adding an element by type of recordset on
        this list.

        :return: a list of recordset of the documents linked to `self`
        :rtype: list
        """
        return list(self.mapped('picking_id'))

    def _propagate_date_log_note(self, move_orig):
        """Post a deadline change alert log note on the documents linked to `self`."""
        # TODO : get the end document (PO/SO/MO)
        doc_orig = move_orig._delay_alert_get_documents()
        documents = self._delay_alert_get_documents()
        if not documents or not doc_orig:
            return

        msg = _("The deadline has been automatically updated due to a delay on %s.", doc_orig[0]._get_html_link())
        msg_subject = _("Deadline updated due to delay on %s", doc_orig[0].name)
        # write the message on each document
        for doc in documents:
            last_message = doc.message_ids[:1]
            # Avoids to write the exact same message multiple times.
            if last_message and last_message.subject == msg_subject:
                continue
            odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
            doc.message_post(body=msg, author_id=odoobot_id, subject=msg_subject)

    def action_add_packages(self):
        """ Opens a list of suitable packages to add to a picking.
        """
        picking = self.env['stock.picking'].browse(self.env.context.get('picking_id'))
        if not picking:
            raise UserError(self.env._("You need a transfer to add these packages to."))
        return {
            'name': self.env._("Select Packages to Move"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.package',
            'view_mode': 'list',
            'views': [(self.env.ref('stock.stock_package_view_add_list').id, 'list')],
            'target': 'new',
            'domain': [('location_id', 'child_of', picking.location_id.id)],
            'context': {
                'picking_id': picking.id,
            },
        }

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()
        view = self.env.ref('stock.view_stock_move_operations')

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                allow_parent_move_picked_reset=True,
            ),
        }

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'move_to_match_ids': self.ids,
        }
        if self._is_consuming():
            warehouse = self.location_id.warehouse_id
        else:
            warehouse = self.location_dest_id.warehouse_id

        if warehouse:
            action['context']['warehouse_id'] = warehouse.id
        return action

    def _do_unreserve(self):
        moves_to_unreserve = OrderedSet()
        for move in self:
            if move.state == 'cancel' or (move.state == 'done' and move.location_dest_usage == 'inventory') or move.picked:
                # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
                # We may have done move in an open picking in a scrap scenario.
                continue
            elif move.state == 'done':
                raise UserError(_("You cannot unreserve a stock move that has been set to 'Done'."))
            moves_to_unreserve.add(move.id)
        moves_to_unreserve = self.env['stock.move'].browse(moves_to_unreserve)

        ml_to_unlink = OrderedSet()
        moves_not_to_recompute = OrderedSet()
        for ml in moves_to_unreserve.move_line_ids:
            if ml.picked:
                moves_not_to_recompute.add(ml.move_id.id)
                continue
            ml_to_unlink.add(ml.id)
        ml_to_unlink = self.env['stock.move.line'].browse(ml_to_unlink)
        moves_not_to_recompute = self.env['stock.move'].browse(moves_not_to_recompute)

        ml_to_unlink.unlink()
        # `write` on `stock.move.line` doesn't call `_recompute_state` (unlike to `unlink`),
        # so it must be called for each move where no move line has been deleted.
        (moves_to_unreserve - moves_not_to_recompute)._recompute_state()
        return True

    def _can_create_lot(self):
        return self.picking_type_id.use_existing_lots

    def _generate_serial_numbers(self, next_serial, next_serial_count=False, location_id=False):
        """ This method will generate `lot_name` from a string (field
        `next_serial`) and create a move line for each generated `lot_name`.
        """
        self.ensure_one()
        if not location_id:
            location_id = self.location_dest_id
        count = next_serial_count or self.next_serial_count
        if not count:
            raise ValidationError(_("The number of Serial Numbers to generate must be greater than zero."))
        lot_names = self.env['stock.lot'].generate_lot_names(next_serial, count)
        field_data = [{'lot_name': lot_name['lot_name'], 'quantity': 1} for lot_name in lot_names]
        if self._can_create_lot():
            self._create_lot_ids_from_move_line_vals(field_data, self.product_id.id, self.company_id.id)
        move_lines_commands = self._generate_serial_move_line_commands(field_data)
        self.move_line_ids = move_lines_commands
        return True

    def _create_lot_ids_from_move_line_vals(self, vals_list, product_id, company_id=False):
        """ This method will search or create the lot_id from the lot_name and set it in the vals_list
        """
        lot_names = [vals['lot_name'] for vals in vals_list if vals.get('lot_name')]
        lot_ids = self.env['stock.lot'].search([
            ('product_id', '=', product_id),
            '|', ('company_id', '=', company_id), ('company_id', '=', False),
            ('name', 'in', lot_names),
        ])
        lot_id_names = set(lot_ids.mapped('name'))
        lot_names = [lot_name for lot_name in lot_names if lot_name not in lot_id_names]  # lot_names not found to create
        lots_to_create_vals = [
            {'product_id': product_id, 'name': lot_name}
            for lot_name in lot_names
        ]
        lot_ids |= self.env['stock.lot'].create(lots_to_create_vals)

        lot_id_by_name = {lot.name: lot.id for lot in lot_ids}
        for vals in vals_list:
            lot_name = vals.get('lot_name', None)
            if not lot_name:
                continue
            vals['lot_id'] = lot_id_by_name[lot_name]
            vals['lot_name'] = False

    @api.model
    def split_lots(self, lots):
        breaking_char = '\n'
        separation_char = '\t'
        options = False

        if not lots:
            return []  # Skip if the `lot_name` doesn't contain multiple values.

        # Checks the lines and prepares the move lines' values.
        split_lines = lots.split(breaking_char)
        split_lines = list(filter(None, split_lines))
        move_lines_vals = []
        for lot_text in split_lines:
            move_line_vals = {
                'lot_name': lot_text,
                'quantity': 1,
            }
            # Semicolons are also used for separation but for convenience we
            # replace them to work only with tabs.
            lot_text_parts = lot_text.replace(';', separation_char).split(separation_char)
            options = options or self._get_formating_options(lot_text_parts[1:])
            for extra_string in lot_text_parts[1:]:
                field_data = self._convert_string_into_field_data(extra_string, options)
                if field_data:
                    lot_text = lot_text_parts[0]
                    if field_data == "ignore":
                        # Got an unusable data for this move, updates only the lot_name part.
                        move_line_vals.update(lot_name=lot_text)
                    else:
                        move_line_vals.update(**field_data, lot_name=lot_text)
                else:
                    # At least this part of the string is erronous and can't be converted,
                    # don't try to guess and simply use the full string as the lot name.
                    move_line_vals['lot_name'] = lot_text
                    break
            move_lines_vals.append(move_line_vals)
        return move_lines_vals

    @api.model
    def action_generate_lot_line_vals(self, context_data, mode, first_lot, count, lot_text):
        if not context_data.get('default_product_id'):
            raise UserError(_("No product found to generate Serials/Lots for."))
        assert mode in ('generate', 'import')
        default_vals = {}

        def generate_lot_qty(quantity, qty_per_lot):
            if qty_per_lot <= 0:
                raise UserError(_("The quantity per lot should always be a positive value."))
            line_count = int(quantity // qty_per_lot)
            leftover = quantity % qty_per_lot
            qty_array = [qty_per_lot] * line_count
            if leftover:
                qty_array.append(leftover)
            return qty_array

        # Get default values
        def remove_prefix(text, prefix):
            if text.startswith(prefix):
                return text[len(prefix):]
            return text
        for key in context_data:
            if key.startswith('default_'):
                default_vals[remove_prefix(key, 'default_')] = context_data[key]

        if default_vals['tracking'] == 'lot' and mode == 'generate':
            lot_qties = generate_lot_qty(default_vals['quantity'], count)
        else:
            lot_qties = [1] * count

        if mode == 'generate':
            lot_names = self.env['stock.lot'].generate_lot_names(first_lot, len(lot_qties))
        elif mode == 'import':
            lot_names = self.split_lots(lot_text)
            lot_qties = [1] * len(lot_names)

        vals_list = []
        loc_dest = self.env['stock.location'].browse(default_vals['location_dest_id'])
        product = self.env['product.product'].browse(default_vals['product_id'])
        for lot, qty in zip(lot_names, lot_qties):
            if not lot.get('quantity'):
                lot['quantity'] = qty
            putaway_loc_dest = loc_dest._get_putaway_strategy(product, lot['quantity'])
            vals_list.append({**default_vals,
                             **lot,
                             'location_dest_id': putaway_loc_dest.id,
                             'product_uom_id': product.uom_id.id,
                            })
        if default_vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(default_vals['picking_type_id'])
            if picking_type.use_existing_lots or context_data.get('force_lot_m2o'):
                self._create_lot_ids_from_move_line_vals(
                    vals_list, default_vals['product_id'], default_vals['company_id']
                )
        # format many2one values for webclient, id + display_name
        for values in vals_list:
            for key, value in values.items():
                if key in self.env['stock.move.line'] and isinstance(self.env['stock.move.line'][key], models.Model):
                    values[key] = {
                        'id': value,
                        'display_name': self.env['stock.move.line'][key].browse(value).display_name
                    }
        if product.lot_sequence_id and first_lot:
            current_sequence = product.lot_sequence_id._get_current_sequence()
            increment = product.lot_sequence_id.number_increment
            first_number = current_sequence.number_next_actual - increment
            final_number = first_number
            # Since the value might have been incremented by the "New" button of the "Generate Serial Numbers" wizard
            # we need to consider both the decremented and the current value of the sequence
            if first_lot == product.lot_sequence_id.get_next_char(first_number):
                final_number = first_number + len(lot_qties)
            elif first_lot == product.lot_sequence_id.get_next_char(first_number + increment):
                final_number = first_number + increment + len(lot_qties)
            if first_number != final_number:
                current_sequence.sudo().write({'number_next_actual': final_number})
        return vals_list

    def _push_apply(self):
        new_moves = []
        for move in self:
            new_move = self.env['stock.move']

            # if the move is a returned move, we don't want to check push rules, as returning a returned move is the only decent way
            # to receive goods without triggering the push rules again (which would duplicate chained operations)
            # first priority goes to the preferred routes defined on the move itself (e.g. coming from a SO line)
            warehouse_id = move.warehouse_id or move.picking_id.picking_type_id.warehouse_id

            StockRule = self.env['stock.rule']
            if move.location_dest_id.company_id not in self.env.companies:
                StockRule = self.env['stock.rule'].sudo()
                move = move.with_context(allowed_companies=self.env.user.company_ids.ids)
                warehouse_id = False

            related_packages = self.env['stock.package'].search_fetch([('id', 'parent_of', move.move_line_ids.result_package_id.ids)], ['package_type_id'])

            rule = StockRule._get_push_rule(move.product_id, move.location_dest_id, {
                'route_ids': move.route_ids | related_packages.package_type_id.route_ids, 'warehouse_id': warehouse_id, 'packaging_uom_id': move.packaging_uom_id,
            })

            excluded_rule_ids = []
            while (rule and rule.push_domain and not move.filtered_domain(literal_eval(rule.push_domain))):
                excluded_rule_ids.append(rule.id)
                rule = StockRule._get_push_rule(move.product_id, move.location_dest_id, {
                    'route_ids': move.route_ids | related_packages.package_type_id.route_ids, 'warehouse_id': warehouse_id, 'packaging_uom_id': move.packaging_uom_id,
                    'domain': [('id', 'not in', excluded_rule_ids)],
                })

            # Make sure it is not returning the return
            if rule and (not move.origin_returned_move_id or move.origin_returned_move_id.location_dest_id.id != rule.location_dest_id.id):
                new_move = rule._run_push(move) or new_move
                if new_move:
                    new_moves.append(new_move)

            move_to_propagate_ids = set()
            move_to_mts_ids = set()
            for m in move.move_dest_ids - new_move:
                if new_move and move.location_final_id and m.location_id == move.location_final_id:
                    move_to_propagate_ids.add(m.id)
                elif not m.location_id._child_of(move.location_dest_id):
                    move_to_mts_ids.add(m.id)
            self.env['stock.move'].browse(move_to_mts_ids)._break_mto_link(move)
            move.move_dest_ids = [Command.unlink(m_id) for m_id in move_to_propagate_ids]
            new_move.move_dest_ids = [Command.link(m_id) for m_id in move_to_propagate_ids]

        new_moves = self.env['stock.move'].concat(*new_moves)
        new_moves = new_moves.sudo()._action_confirm()

        return new_moves

    def _merge_moves_fields(self):
        """ This method will return a dict of stock move’s values that represent the values of all moves in `self` merged. """
        merge_extra = self.env.context.get('merge_extra')
        state = self._get_relevant_state_among_moves()
        origin = '/'.join(set(self.filtered(lambda m: m.origin).mapped('origin')))
        return {
            'product_uom_qty': sum(self.mapped('product_uom_qty')) if not merge_extra else self[0].product_uom_qty,
            'date': min(self.mapped('date')) if all(p.move_type == 'direct' for p in self.picking_id) else max(self.mapped('date')),
            'move_dest_ids': [(4, m.id) for m in self.mapped('move_dest_ids')],
            'move_orig_ids': [(4, m.id) for m in self.mapped('move_orig_ids')],
            'state': state,
            'origin': origin,
        }

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = [
            'product_id', 'price_unit', 'procure_method', 'location_id', 'location_dest_id', 'location_final_id',
            'product_uom', 'restrict_partner_id', 'origin_returned_move_id',
            'propagate_cancel', 'description_picking', 'never_product_template_attribute_value_ids',
        ]
        if self.env['ir.config_parameter'].sudo().get_param('stock.merge_only_same_date'):
            fields.append('date')
        if self.env.context.get('merge_extra'):
            fields.pop(fields.index('procure_method'))
        if not self.env['ir.config_parameter'].sudo().get_param('stock.merge_ignore_date_deadline'):
            fields.append('date_deadline')
        return fields

    @api.model
    def _prepare_merge_negative_moves_excluded_distinct_fields(self):
        return ['description_picking']

    def _clean_merged(self):
        """Cleanup hook used when merging moves"""
        self.write({'propagate_cancel': False})

    def _update_candidate_moves_list(self, candidate_moves_set):
        for picking in self.mapped('picking_id'):
            candidate_moves_set.add(picking.move_ids)

    def _merge_move_itemgetter(self, distinct_fields, excluded_fields=None):
        fields = set(distinct_fields or []) - set(excluded_fields or [])
        float_fields = {f_name for f_name in fields if self.env['stock.move']._fields[f_name].type == 'float'}
        base_getter = itemgetter(*fields - float_fields)

        if not float_fields:
            return base_getter

        float_precision = {f_name: (self.env['stock.move']._fields[f_name].get_digits(self.env) or (False, 2))[1] for f_name in float_fields}
        if 'price_unit' in float_fields:
            price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
            currency_precision = min(self.company_id.mapped('currency_id.decimal_places')) if self.company_id else False
            float_precision['price_unit'] = min(currency_precision, price_unit_prec) if currency_precision else price_unit_prec

        def _get_formatted_float_fields(move, f_name, precision):
            # Round and cast the value of move.f_name into a string so that rounding errors do not prevent the merge
            rounded_value = float_round(move[f_name], precision_digits=precision[f_name])
            return "{:.{precision}f}".format(rounded_value, precision=precision[f_name])

        return lambda move: base_getter(move) + tuple(_get_formatted_float_fields(move, f_name, float_precision) for f_name in float_fields)

    def _merge_moves(self, merge_into=False):
        """ This method will, for each move in `self`, go up in their linked picking and try to
        find in their existing moves a candidate into which we can merge the move.
        :return: Recordset of moves passed to this method. If some of the passed moves were merged
        into another existing one, return this one and not the (now unlinked) original.
        """

        candidate_moves_set = set()
        if not merge_into:
            self._update_candidate_moves_list(candidate_moves_set)
        else:
            candidate_moves_set.add(merge_into | self)

        distinct_fields = (self | self.env['stock.move'].concat(*candidate_moves_set))._prepare_merge_moves_distinct_fields()

        # Move removed after merge
        moves_to_unlink = self.env['stock.move']
        # Moves successfully merged
        merged_moves = self.env['stock.move']
        # Emptied moves
        moves_to_cancel = self.env['stock.move']

        moves_by_neg_key = defaultdict(lambda: self.env['stock.move'])
        # Need to check less fields for negative moves as some might not be set.
        neg_qty_moves = self.filtered(lambda m: m.product_uom.compare(m.product_qty, 0.0) < 0)
        # Detach their picking as they will either get absorbed or create a backorder, so no extra logs will be put in the chatter
        neg_qty_moves.picking_id = False
        excluded_fields = self._prepare_merge_negative_moves_excluded_distinct_fields()
        neg_key = self._merge_move_itemgetter(distinct_fields, excluded_fields)
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')

        for candidate_moves in candidate_moves_set:
            # First step find move to merge.
            candidate_moves = candidate_moves.filtered(lambda m: m.state not in ('done', 'cancel', 'draft')) - neg_qty_moves
            for __, g in groupby(candidate_moves, key=self._merge_move_itemgetter(distinct_fields)):
                moves = self.env['stock.move'].concat(*g)
                # Merge all positive moves together
                if len(moves) > 1:
                    # link all move lines to record 0 (the one we will keep).
                    moves.mapped('move_line_ids').write({'move_id': moves[0].id})
                    # merge move data
                    merge_extra = self.env.context.get('merge_extra') and bool(merge_into)
                    moves[0].write(moves.with_context(merge_extra=merge_extra)._merge_moves_fields())
                    # update merged moves dicts
                    moves_to_unlink |= moves[1:]
                    merged_moves |= moves[0]
                # Add the now single positive move to its limited key record
                moves_by_neg_key[neg_key(moves[0])] |= moves[0]

        for neg_move in neg_qty_moves:
            # Check all the candidates that matches the same limited key, and adjust their quantities to absorb negative moves
            for pos_move in moves_by_neg_key.get(neg_key(neg_move), []):
                new_total_value = pos_move.product_qty * pos_move.price_unit + neg_move.product_qty * neg_move.price_unit
                # If quantity can be fully absorbed by a single move, update its quantity and remove the negative move
                if pos_move.product_uom.compare(pos_move.product_uom_qty, abs(neg_move.product_uom_qty)) >= 0:
                    pos_move.product_uom_qty += neg_move.product_uom_qty
                    pos_move.write({
                        'price_unit': float_round(new_total_value / pos_move.product_qty, precision_digits=price_unit_prec) if pos_move.product_qty else 0,
                        'move_dest_ids': [Command.link(m.id) for m in neg_move.mapped('move_dest_ids') if m.location_id == pos_move.location_dest_id],
                        'move_orig_ids': [Command.link(m.id) for m in neg_move.mapped('move_orig_ids') if m.location_dest_id == pos_move.location_id],
                    })
                    merged_moves |= pos_move
                    moves_to_unlink |= neg_move
                    if pos_move.product_uom.is_zero(pos_move.product_uom_qty):
                        moves_to_cancel |= pos_move
                    break
                neg_move.product_uom_qty += pos_move.product_uom_qty
                neg_move.price_unit = float_round(new_total_value / neg_move.product_qty, precision_digits=price_unit_prec)
                pos_move.product_uom_qty = 0
                moves_to_cancel |= pos_move

        # We are using propagate to False in order to not cancel destination moves merged in moves[0]
        (moves_to_unlink | moves_to_cancel)._clean_merged()

        if moves_to_unlink:
            moves_to_unlink._action_cancel()
            moves_to_unlink.sudo().unlink()

        if moves_to_cancel:
            moves_to_cancel.filtered(lambda m: not m.picked)._action_cancel()

        return (self | merged_moves) - moves_to_unlink

    def _get_relevant_state_among_moves(self):
        # We sort our moves by importance of state:
        #     ------------- 0
        #     | Assigned  |
        #     -------------
        #     |  Waiting  |
        #     -------------
        #     |  Partial  |
        #     -------------
        #     |  Confirm  |
        #     ------------- len-1
        sort_map = {
            'assigned': 4,
            'waiting': 3,
            'partially_available': 2,
            'confirmed': 1,
        }
        moves_todo = self\
            .filtered(lambda move: move.state not in ['cancel', 'done'] and not (move.state == 'assigned' and not move.product_uom_qty))\
            .sorted(key=lambda move: (sort_map.get(move.state, 0), move.product_uom_qty))
        if not moves_todo:
            return 'assigned'
        # The picking should be the same for all moves.
        if moves_todo[:1].picking_id and moves_todo[:1].picking_id.move_type == 'one':
            if all(not m.product_uom_qty for m in moves_todo):
                return 'assigned'
            most_important_move = moves_todo[0]
            if most_important_move.state == 'confirmed':
                return 'confirmed'
            elif most_important_move.state == 'partially_available':
                return 'confirmed'
            else:
                return moves_todo[:1].state or 'draft'
        elif moves_todo[:1].state != 'assigned' and any(move.state in ['assigned', 'partially_available'] for move in moves_todo):
            return 'partially_available'
        else:
            least_important_move = moves_todo[-1:]
            if least_important_move.state == 'confirmed' and least_important_move.product_uom_qty == 0:
                return 'assigned'
            else:
                return moves_todo[-1:].state or 'draft'

    @api.onchange('lot_ids')
    def _onchange_lot_ids(self):
        quantity = sum(ml.quantity_product_uom for ml in self.move_line_ids.filtered(lambda ml: not ml.lot_id and ml.lot_name))
        quantity += self.product_id.uom_id._compute_quantity(len(self.lot_ids), self.product_uom)
        self.update({'quantity': quantity})

        base_location = self.picking_id.location_id or self.location_id
        quants = self.env['stock.quant'].sudo().search([
            ('product_id', '=', self.product_id.id),
            ('lot_id', 'in', self.lot_ids.ids),
            ('quantity', '!=', 0),
            ('location_id.usage', 'in', ('internal', 'transit', 'customer')),
            ('location_id', 'not any', [('location_id', 'child_of', base_location.id)])
        ])

        if quants:
            sn_to_location = ""
            for quant in quants:
                sn_to_location += _("\n(%(serial_number)s) exists in location %(location)s", serial_number=quant.lot_id.display_name, location=quant.location_id.display_name)
            return {
                'warning': {'title': _('Warning'), 'message': _('Unavailable Serial numbers. Please correct the serial numbers encoded: %(serial_numbers_to_locations)s', serial_numbers_to_locations=sn_to_location)}
            }

    def _key_assign_picking(self):
        self.ensure_one()
        keys = (self.reference_ids, self.location_id, self.location_dest_id, self.picking_type_id)
        if self.move_orig_ids.picking_id and not self.reference_ids:
            keys += (self.move_orig_ids.picking_id, )
        return keys

    def _search_picking_for_assignation_domain(self):
        domain = [
            ('reference_ids', '=', self.reference_ids.ids),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', (self.location_dest_id.id or self.picking_type_id.default_location_dest_id.id)),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])]
        return domain

    def _search_picking_for_assignation(self):
        self.ensure_one()
        if not self.reference_ids:
            return self.env['stock.picking']
        domain = self._search_picking_for_assignation_domain()
        picking = self.env['stock.picking'].search(domain, limit=1)
        return picking

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(self, key=lambda m: m._key_assign_picking())
        for _group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*moves)
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                # If a picking is found, we'll append `move` to its move list and thus its
                # `partner_id` and `ref` field will refer to multiple records. In this
                # case, we chose to wipe them.
                vals = moves._assign_picking_values(picking)
                if vals:
                    picking.write(vals)
            else:
                # Don't create picking for negative moves since they will be
                # reverse and assign to another picking
                moves = moves.filtered(lambda m: m.product_uom.compare(m.product_uom_qty, 0.0) >= 0)
                if not moves:
                    continue
                new_picking = True
                picking = Picking.create(moves._get_new_picking_values())

            moves.write({'picking_id': picking.id})
            moves._assign_picking_post_process(new=new_picking)
        return True

    def _assign_picking_values(self, picking):
        vals = {}
        if any(picking.partner_id != m.partner_id for m in self):
            vals['partner_id'] = False
        if any(picking.origin != m.origin for m in self):
            current_origins = picking.origin.split(',') if picking.origin else []
            new_moves_origins = [move.origin for move in self if move.origin]
            new_origin = ','.join(OrderedSet(current_origins + new_moves_origins))
            if picking.origin != new_origin:
                vals['origin'] = new_origin
        return vals

    def _assign_picking_post_process(self, new=False):
        pass

    def _generate_serial_move_line_commands(self, field_data, location_dest_id=False, origin_move_line=None):
        """Return a list of commands to update the move lines (write on
        existing ones or create new ones).
        Called when user want to create and assign multiple serial numbers in
        one time (using the button/wizard or copy-paste a list in the field).

        :param field_data: A list containing dict with at least `lot_name` and `quantity`
        :type field_data: list
        :param origin_move_line: A move line to duplicate the value from, empty record by default
        :type origin_move_line: record of :class:`stock.move.line`
        :return: A list of commands to create/update :class:`stock.move.line`
        :rtype: list
        """
        self.ensure_one()
        origin_move_line = origin_move_line or self.env['stock.move.line']
        loc_dest = origin_move_line.location_dest_id or location_dest_id
        move_line_vals = {
            'picking_id': self.picking_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
        }
        # Select the right move lines depending of the picking type's configuration.
        move_lines = self.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name)

        if origin_move_line:
            # Copies `owner_id` and `package_id` if new move lines are created from an existing one.
            move_line_vals.update({
                'owner_id': origin_move_line.owner_id.id,
                'package_id': origin_move_line.package_id.id,
            })

        move_lines_commands = []
        qty_by_location = defaultdict(float)
        for command_vals in field_data:
            quantity = command_vals['quantity']
            # We write the lot name on an existing move line (if we have still one)...
            if move_lines:
                move_lines_commands.append(Command.update(move_lines[0].id, command_vals))
                qty_by_location[move_lines[0].location_dest_id.id] += quantity
                move_lines = move_lines[1:]
            # ... or create a new move line with the serial name.
            else:
                loc = loc_dest or self.location_dest_id._get_putaway_strategy(self.product_id, quantity=quantity, additional_qty=qty_by_location)
                new_move_line_vals = {
                    **move_line_vals,
                    **command_vals,
                    'location_dest_id': loc.id
                }
                move_lines_commands.append(Command.create(new_move_line_vals))
                qty_by_location[loc.id] += quantity
        return move_lines_commands

    def _get_formating_options(self, strings):
        return {}

    def _get_new_picking_values(self):
        """ return create values for new picking that will be linked with group
        of moves in self.
        """
        origins = self.filtered(lambda m: m.origin).mapped('origin')
        origins = list(dict.fromkeys(origins)) # create a list of unique items
        # Will display source document if any, when multiple different origins
        # are found display a maximum of 5
        if len(origins) == 0:
            origin = False
        else:
            origin = ','.join(origins[:5])
            if len(origins) > 5:
                origin += "..."
        partners = self.mapped('partner_id')
        partner = len(partners) == 1 and partners.id or False
        vals = {
            'origin': origin,
            'company_id': self.mapped('company_id').id,
            'user_id': False,
            'partner_id': partner,
            'picking_type_id': self.mapped('picking_type_id').id,
            'location_id': self.mapped('location_id').id,
        }
        if self.location_dest_id.ids:
            vals['location_dest_id'] = self.location_dest_id.id
        return vals

    def _should_be_assigned(self):
        self.ensure_one()
        return bool(not self.picking_id and self.picking_type_id)

    def _action_confirm(self, merge=True, merge_into=False, create_proc=True):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        # Use OrderedSet of id (instead of recordset + |= ) for performance
        move_create_proc, move_to_confirm, move_waiting = OrderedSet(), OrderedSet(), OrderedSet()
        to_assign = defaultdict(OrderedSet)
        for move in self:
            if move.state != 'draft':
                continue
            # if the move is preceded, then it's waiting (if preceding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting.add(move.id)
            elif move.procure_method == 'make_to_order':
                move_waiting.add(move.id)
                if create_proc:
                    move_create_proc.add(move.id)
            elif move.rule_id and move.rule_id.procure_method == 'mts_else_mto':
                move_to_confirm.add(move.id)
                if create_proc:
                    move_create_proc.add(move.id)
            else:
                move_to_confirm.add(move.id)
            if move._should_be_assigned():
                key = (frozenset(move.reference_ids.ids), move.location_id.id, move.location_dest_id.id)
                to_assign[key].add(move.id)

        # create procurements for make to order moves
        procurement_requests = []
        move_create_proc = self.browse(move_create_proc)
        quantities = move_create_proc._prepare_procurement_qty()
        for move, quantity in zip(move_create_proc, quantities):
            values = move._prepare_procurement_values()
            origin = move._prepare_procurement_origin()
            procurement_requests.append(self.env['stock.rule'].Procurement(
                move.product_id, quantity, move.product_uom,
                move.location_id, move.rule_id and move.rule_id.name or "/",
                origin, move.company_id, values))
        self.env['stock.rule'].run(procurement_requests, raise_user_error=not self.env.context.get('from_orderpoint'))

        move_to_confirm, move_waiting = self.browse(move_to_confirm).filtered(lambda m: m.state != 'cancel'), self.browse(move_waiting).filtered(lambda m: m.state != 'cancel')
        move_to_confirm.write({'state': 'confirmed'})
        move_waiting.write({'state': 'waiting'})
        # procure_method sometimes changes with certain workflows so just in case, apply to all moves
        (move_to_confirm | move_waiting).filtered(lambda m: m.picking_type_id.reservation_method == 'at_confirm')\
            .write({'reservation_date': fields.Date.today()})

        # assign picking in batch for all confirmed move that share the same details
        for moves_ids in to_assign.values():
            self.browse(moves_ids).with_context(clean_context(self.env.context))._assign_picking()

        self._check_company()
        moves = self
        if merge:
            moves = self._merge_moves(merge_into=merge_into)

        neg_r_moves = moves.filtered(lambda move: move.product_uom.compare(move.product_uom_qty, 0) < 0)

        # Push remaining quantities to next step
        neg_to_push = neg_r_moves.filtered(lambda move: move.location_final_id and move.location_dest_id != move.location_final_id)
        new_push_moves = self.env['stock.move']
        if neg_to_push:
            new_push_moves = neg_to_push._push_apply()

        # Transform remaining move in returns in case of negative initial demand
        for move in neg_r_moves:
            move.location_id, move.location_dest_id, move.location_final_id = move.location_dest_id, move.location_id, move.location_id
            orig_move_ids, dest_move_ids = [], []
            for m in move.move_orig_ids | move.move_dest_ids:
                from_loc, to_loc = m.location_id, m.location_dest_id
                if m.product_uom.compare(m.product_uom_qty, 0) < 0:
                    from_loc, to_loc = to_loc, from_loc
                if to_loc == move.location_id:
                    orig_move_ids += m.ids
                elif move.location_dest_id == from_loc:
                    dest_move_ids += m.ids
            move.move_orig_ids, move.move_dest_ids = [Command.set(orig_move_ids)], [Command.set(dest_move_ids)]
            move.product_uom_qty *= -1
            if move.picking_type_id.return_picking_type_id:
                move.picking_type_id = move.picking_type_id.return_picking_type_id
            # We are returning some products, we must take them in the source location
            move.procure_method = 'make_to_stock'
        neg_r_moves._assign_picking()

        # call `_action_assign` on every confirmed move which location_id bypasses the reservation + those expected to be auto-assigned
        moves.filtered(lambda move: move.state in ('confirmed', 'partially_available')
                       and (move._should_bypass_reservation() or move._should_assign_at_confirm()))\
             ._action_assign()
        if new_push_moves:
            neg_push_moves = new_push_moves.filtered(lambda sm: sm.product_uom.compare(sm.product_uom_qty, 0) < 0)
            (new_push_moves - neg_push_moves).sudo()._action_confirm()
            # Negative moves do not have any picking, so we should try to merge it with their siblings
            neg_push_moves._action_confirm(merge_into=neg_push_moves.move_orig_ids.move_dest_ids)
        return moves

    def _prepare_procurement_origin(self):
        self.ensure_one()
        return (self.reference_ids and self.reference_ids[0].name) or self.origin or self.picking_id.display_name

    def _prepare_procurement_qty(self):
        quantities = []
        mtso_products_by_locations = defaultdict(list)
        mtso_moves = set()
        for move in self:
            if move.rule_id and move.rule_id.procure_method == 'mts_else_mto':
                mtso_moves.add(move.id)
                mtso_products_by_locations[move.location_id].append(move.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            if location.should_bypass_reservation():
                continue
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}
        for move in self:
            if move.id not in mtso_moves or move.product_id.uom_id.compare(move.product_qty, 0) <= 0:
                quantities.append(move.product_uom_qty)
                continue

            if move._should_bypass_reservation():
                quantities.append(move.product_uom_qty)
                continue

            free_qty = max(forecasted_qties_by_loc[move.location_id][move.product_id.id], 0)
            quantity = max(move.product_qty - free_qty, 0)
            product_uom_qty = move.product_id.uom_id._compute_quantity(quantity, move.product_uom, rounding_method='HALF-UP')
            quantities.append(product_uom_qty)
            forecasted_qties_by_loc[move.location_id][move.product_id.id] -= min(move.product_qty, free_qty)

        return quantities

    def _get_partner_id(self):
        if self.location_id == self.env.company.internal_transit_location_id:
            return False
        return self.partner_id.id

    def _prepare_procurement_values(self):
        """ Prepare specific key for moves or other componenets that will be created from a stock rule
        comming from a stock move. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        self.ensure_one()

        product_id = self.product_id.with_context(lang=self._get_lang())
        dates_info = {'date_planned': self._get_mto_procurement_date()}
        route = self.route_ids
        if not route:
            related_packages = self.env['stock.package'].search_fetch([('id', 'parent_of', self.move_line_ids.result_package_id.ids)], ['package_type_id'])
            route = related_packages.package_type_id.route_ids
        if self.location_id.warehouse_id and self.location_id.warehouse_id.lot_stock_id.parent_path in self.location_id.parent_path:
            dates_info = self.product_id._get_dates_info(self.date, self.location_id, route_ids=route)
        warehouse = self.warehouse_id or self.picking_type_id.warehouse_id
        if not self.location_id.warehouse_id:
            warehouse = self.rule_id.route_id.supplier_wh_id

        move_dest_ids = False
        if self.procure_method == "make_to_order":
            move_dest_ids = self
        return {
            # TODO CLPI: maybe make this a little cleaner
            'product_description_variants': self.description_picking and self.description_picking.replace(product_id._get_description(self.picking_type_id), '').replace(product_id._get_picking_description(self.picking_type_id) or '', ''),
            'never_product_template_attribute_value_ids': self.never_product_template_attribute_value_ids,
            'date_planned': dates_info.get('date_planned'),
            'date_order': dates_info.get('date_order'),
            'date_deadline': self.date_deadline,
            'move_dest_ids': move_dest_ids,
            'partner_id': self._get_partner_id() if self.rule_id.procure_method in ('make_to_order', 'mts_else_mto') else False,
            'route_ids': route,
            'warehouse_id': warehouse,
            'priority': self.priority,
            'reference_ids': self.reference_ids,
            'orderpoint_id': self.orderpoint_id,
            'packaging_uom_id': self.packaging_uom_id,
            'procurement_values': self.procurement_values,
        }

    def _get_mto_procurement_date(self):
        return self.date

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'picking_id': self.picking_id.id,
            'company_id': self.company_id.id,
        }
        if quantity:
            # TODO could be also move in create/write
            rounding = self.env['decimal.precision'].precision_get('Product Unit')
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            uom_quantity = float_round(uom_quantity, precision_digits=rounding)
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, quantity=uom_quantity)
            else:
                vals = dict(vals, quantity=quantity, product_uom_id=self.product_id.uom_id.id)
        package = None
        if reserved_quant:
            package = reserved_quant.package_id
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=package.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        return vals

    def _update_reserved_quantity(self, need, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        """ Create or update move lines and reserves quantity from quants
            Expects the need (qty to reserve) and location_id to reserve from.
            `quant_ids` can be passed as an optimization since no search on the database
            is performed and reservation is done on the passed quants set
        """
        self.ensure_one()
        move_line_vals, taken_quantity = self._update_reserved_quantity_vals(need, location_id, lot_id, package_id, owner_id, strict)
        if move_line_vals:
            self.env['stock.move.line'].create(move_line_vals)
        return taken_quantity

    def _update_reserved_quantity_vals(self, need, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        self.ensure_one()
        if not lot_id:
            lot_id = self.env['stock.lot']
        if not package_id:
            package_id = self.env['stock.package']
        if not owner_id:
            owner_id = self.env['res.partner']

        quants = self.env['stock.quant'].with_context(packaging_uom_id=self.packaging_uom_id)._get_reserve_quantity(
            self.product_id, location_id, need, uom_id=self.product_uom,
            lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)

        taken_quantity = 0
        rounding = self.env['decimal.precision'].precision_get('Product Unit')
        # Find a candidate move line to update or create a new one.
        candidate_lines = {}
        for line in self.move_line_ids:
            if line.result_package_id or line.product_id.tracking == 'serial':
                continue
            candidate_lines[line.location_id, line.lot_id, line.package_id, line.owner_id] = line
        move_line_vals = []
        grouped_quants = {}
        # Handle quants duplication
        for quant, quantity in quants:
            if (quant.location_id, quant.lot_id, quant.package_id, quant.owner_id) not in grouped_quants:
                grouped_quants[quant.location_id, quant.lot_id, quant.package_id, quant.owner_id] = [quant, quantity]
            else:
                grouped_quants[quant.location_id, quant.lot_id, quant.package_id, quant.owner_id][1] += quantity
        for reserved_quant, quantity in grouped_quants.values():
            taken_quantity += quantity
            to_update = candidate_lines.get((reserved_quant.location_id, reserved_quant.lot_id, reserved_quant.package_id, reserved_quant.owner_id))
            if to_update:
                uom_quantity = self.product_id.uom_id._compute_quantity(quantity, to_update.product_uom_id, rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                uom_quantity_back_to_product_uom = to_update.product_uom_id._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                to_update.with_context(reserved_quant=reserved_quant).quantity += uom_quantity
            else:
                if self.product_id.tracking == 'serial' and (self.picking_type_id.use_create_lots or self.picking_type_id.use_existing_lots):
                    vals_list = self._add_serial_move_line_to_vals_list(reserved_quant, quantity)
                    if vals_list:
                        move_line_vals += vals_list
                else:
                    move_line_vals.append(self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant))
        return move_line_vals, taken_quantity

    def _add_serial_move_line_to_vals_list(self, reserved_quant, quantity):
        return [self._prepare_move_line_vals(quantity=1, reserved_quant=reserved_quant) for i in range(int(quantity))]

    def _should_bypass_reservation(self, forced_location=False):
        self.ensure_one()
        location = forced_location or self.location_id
        return location.should_bypass_reservation() or not self.product_id.is_storable

    def _should_assign_at_confirm(self):
        return self._should_bypass_reservation() or self.picking_type_id.reservation_method == 'at_confirm' or (self.reservation_date and self.reservation_date <= fields.Date.today())

    def _get_picked_quantity(self):
        self.ensure_one()
        if self.picked and any(not ml.picked for ml in self.move_line_ids):
            picked_qty = 0
            for ml in self.move_line_ids:
                if not ml.picked:
                    continue
                picked_qty += ml.product_uom_id._compute_quantity(ml.quantity, self.product_uom, round=False)
            return picked_qty
        else:
            return self.quantity

    # necessary hook to be able to override move reservation to a restrict lot, owner, pack, location...
    def _get_available_quantity(self, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        self.ensure_one()
        if location_id.should_bypass_reservation():
            return self.product_qty
        return self.env['stock.quant']._get_available_quantity(self.product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict, allow_negative=allow_negative)

    def _get_available_move_lines_in(self):
        move_lines_in = self.move_orig_ids.move_dest_ids.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')

        def _keys_in_groupby(ml):
            return (ml.location_dest_id, ml.lot_id, ml.result_package_id, ml.owner_id)

        grouped_move_lines_in = {}
        for k, g in groupby(move_lines_in, key=_keys_in_groupby):
            quantity = 0
            for ml in g:
                quantity += ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id)
            grouped_move_lines_in[k] = quantity

        return grouped_move_lines_in

    def _get_available_move_lines_out(self, assigned_moves_ids, partially_available_moves_ids):
        move_lines_out_done = (self.move_orig_ids.mapped('move_dest_ids') - self)\
            .filtered(lambda m: m.state in ['done'])\
            .mapped('move_line_ids')
        # As we defer the write on the stock.move's state at the end of the loop, there
        # could be moves to consider in what our siblings already took.
        StockMove = self.env['stock.move']
        moves_out_siblings = self.move_orig_ids.mapped('move_dest_ids') - self
        moves_out_siblings_to_consider = moves_out_siblings & (StockMove.browse(assigned_moves_ids) + StockMove.browse(partially_available_moves_ids))
        reserved_moves_out_siblings = moves_out_siblings.filtered(lambda m: m.state in ['partially_available', 'assigned'])
        move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped('move_line_ids')

        def _keys_out_groupby(ml):
            return (ml.location_id, ml.lot_id, ml.package_id, ml.owner_id)

        grouped_move_lines_out = {}
        for k, g in groupby(move_lines_out_done, key=_keys_out_groupby):
            quantity = 0
            for ml in g:
                quantity += ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id)
            grouped_move_lines_out[k] = quantity
        for k, g in groupby(move_lines_out_reserved, key=_keys_out_groupby):
            grouped_move_lines_out[k] = sum(self.env['stock.move.line'].concat(*list(g)).mapped('quantity_product_uom'))

        return grouped_move_lines_out

    def _get_available_move_lines(self, assigned_moves_ids, partially_available_moves_ids):
        grouped_move_lines_in = self._get_available_move_lines_in()
        grouped_move_lines_out = self._get_available_move_lines_out(assigned_moves_ids, partially_available_moves_ids)
        available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key in grouped_move_lines_in}
        # pop key if the quantity available amount to 0
        rounding = self.product_id.uom_id.rounding
        return dict((k, v) for k, v in available_move_lines.items() if float_compare(v, 0, precision_rounding=rounding) > 0)

    def _action_assign(self, force_qty=False):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `reserved_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.quantity for move in self}

        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        # Once the quantities are assigned, we want to find a better destination location thanks
        # to the putaway rules. This redirection will be applied on moves of `moves_to_redirect`.
        moves_to_redirect = OrderedSet()
        moves_to_assign = self
        if not force_qty:
            moves_to_assign = moves_to_assign.filtered(
                lambda m: not m.picked and m.state in ['confirmed', 'waiting', 'partially_available']
            )
        moves_mto = moves_to_assign.filtered(lambda m: m.move_orig_ids and not m._should_bypass_reservation())
        quants_cache = self.env['stock.quant']._get_quants_by_products_locations(moves_mto.product_id, moves_mto.location_id)
        for move in moves_to_assign:
            move = move.with_company(move.company_id)
            rounding = roundings[move]
            if not force_qty:
                missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            else:
                missing_reserved_uom_quantity = force_qty
            if float_compare(missing_reserved_uom_quantity, 0, precision_rounding=rounding) <= 0:
                assigned_moves_ids.add(move.id)
                continue
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            if move._should_bypass_reservation():
                # create the move line(s) but do not impact quants
                if move.move_orig_ids:
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids, partially_available_moves_ids)
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        qty_added = min(missing_reserved_quantity, quantity)
                        move_line_vals = move._prepare_move_line_vals(qty_added)
                        move_line_vals.update({
                            'location_id': location_id.id,
                            'lot_id': lot_id.id,
                            'lot_name': lot_id.name,
                            'owner_id': owner_id.id,
                            'package_id': package_id.id,
                        })
                        move_line_vals_list.append(move_line_vals)
                        missing_reserved_quantity -= qty_added
                        if move.product_id.uom_id.is_zero(missing_reserved_quantity):
                            break

                if missing_reserved_quantity and move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for _i in range(int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                elif missing_reserved_quantity:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.picked and
                                                            not ml.lot_id and
                                                            not ml.result_package_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].quantity += move.product_id.uom_id._compute_quantity(
                            missing_reserved_quantity, move.product_uom, rounding_method='HALF-UP')
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves_ids.add(move.id)
                moves_to_redirect.add(move.id)
            else:
                if move.product_uom.is_zero(move.product_uom_qty) and not force_qty:
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    taken_quantity = move._update_reserved_quantity(need, move.location_id, strict=False)
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    moves_to_redirect.add(move.id)
                    if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `quantity` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids, partially_available_moves_ids)
                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.quantity_product_uom):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id, move_line.package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.package_id, move_line.owner_id)] -= move_line.quantity_product_uom

                    taken_quantities = {}
                    all_move_line_vals = []
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('quantity_product_uom')) - sum(taken_quantities.values())
                        move_line_vals, taken_quantity = move._update_reserved_quantity_vals(min(quantity, need), location_id, lot_id, package_id, owner_id, strict=True)
                        all_move_line_vals += move_line_vals
                        if move_line_vals:  # Only subtract for new lines (updates are already reflected in sum(move_line_ids))
                            taken_quantities[need, location_id, lot_id, package_id, owner_id] = taken_quantity
                    if all_move_line_vals:
                        self.env['stock.move.line'].create(all_move_line_vals)

                    for (need, location_id, lot_id, package_id, owner_id), taken_quantity in taken_quantities.items():
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        moves_to_redirect.add(move.id)
                        if float_is_zero(need - taken_quantity, precision_rounding=rounding):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty

        self.env['stock.move.line'].create(move_line_vals_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
        if not self.env.context.get('bypass_entire_pack'):
            self.picking_id._check_entire_pack()
        StockMove.browse(moves_to_redirect).move_line_ids._apply_putaway_strategy()

    def _action_cancel(self):
        if any(move.state == 'done' and move.location_dest_usage != 'inventory' for move in self):
            raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'. Create a return in order to reverse the moves which took place.'))
        moves_to_cancel = self.filtered(lambda m: m.state != 'cancel' and not (m.state == 'done' and m.location_dest_usage == 'inventory'))
        moves_to_cancel.picked = False
        # self cannot contain moves that are either cancelled or done, therefore we can safely
        # unlink all associated move_line_ids
        moves_to_cancel._do_unreserve()
        cancel_moves_origin = self.env['ir.config_parameter'].sudo().get_param('stock.cancel_moves_origin')

        moves_to_cancel.state = 'cancel'

        for move in moves_to_cancel:
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move_dest_to_cancel = move.move_dest_ids.filtered(lambda m: m.state != 'done' and move.location_dest_id == m.location_id)
                    move_dest_to_cancel._action_cancel()
                    # Unlink from dest if dest is not in the chain
                    (move.move_dest_ids - move_dest_to_cancel).write({
                        'procure_method': 'make_to_stock',
                        'move_orig_ids': [Command.unlink(move.id)]
                    })
                    if cancel_moves_origin:
                        move.move_orig_ids.sudo().filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move_dest_ids = move.move_dest_ids
                    move_dest_ids.write({
                        'procure_method': 'make_to_stock',
                        'move_orig_ids': [Command.unlink(move.id)]
                    })
        moves_to_cancel.write({
            'move_orig_ids': [(5, 0, 0)],
            'procure_method': 'make_to_stock',
        })
        return True

    def _skip_push(self):
        return self.is_inventory or (
            self.move_dest_ids and any(m.location_id._child_of(self.location_dest_id) for m in self.move_dest_ids)
        )

    def _check_quantity(self):
        return self.env['stock.quant'].sudo().search([
            ('product_id', 'in', self.product_id.ids),
            ('location_id', 'child_of', self.location_dest_id.ids),
            ('lot_id', 'in', self.sudo().lot_ids.ids)
        ]).check_quantity()

    def _action_done(self, cancel_backorder=False):
        moves = self.filtered(
            lambda move: move.state == 'draft')._action_confirm(merge=False)
        moves = (self | moves).exists().filtered(lambda x: x.state not in ('done', 'cancel'))

        # Cancel moves where necessary ; we should do it before creating the extra moves because
        # this operation could trigger a merge of moves.
        ml_ids_to_unlink = OrderedSet()
        for move in moves:
            if move.picked:
                # in theory, we should only have a mix of picked and non-picked mls in the barcode use case
                # where non-scanned mls = not picked => we definitely don't want to validate them
                ml_ids_to_unlink |= move.move_line_ids.filtered(lambda ml: not ml.picked).ids
            if (move.quantity <= 0 or not move.picked) and not move.is_inventory:
                if move.product_uom.compare(move.product_uom_qty, 0.0) == 0 or cancel_backorder:
                    move._action_cancel()
        self.env['stock.move.line'].browse(ml_ids_to_unlink).unlink()

        moves_todo = moves.filtered(lambda m:
            not (m.state == 'cancel' or (m.quantity <= 0 and not m.is_inventory) or not m.picked)
        )

        moves_todo._check_company()
        if not cancel_backorder:
            moves_todo._create_backorder()
        moves_todo.mapped('move_line_ids').sorted()._action_done()
        # Check the consistency of the result packages; there should be an unique location across
        # the contained quants.
        for result_package in moves_todo\
                .move_line_ids.filtered(lambda ml: ml.picked).mapped('result_package_id')\
                .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
            if len(result_package.quant_ids.filtered(lambda q: q.product_uom_id.compare(q.quantity, 0.0) > 0).mapped('location_id')) > 1:
                error_msg = _(
                    'You cannot move the same package content more than once in the same transfer'
                    ' or split the same package into two location.'
                )
                package_msg = _("\nPackage: %s", result_package.name)
                raise UserError(error_msg + package_msg)
        if any(ml.package_id and ml.package_id == ml.result_package_id for ml in moves_todo.move_line_ids):
            self.env['stock.quant']._unlink_zero_quants()
        picking = moves_todo.mapped('picking_id')
        moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})

        move_dests_per_company = defaultdict(lambda: self.env['stock.move'])

        # Break move dest link if move dest and move_dest source are not the same,
        # so that when move_dests._action_assign is called, the move lines are not created with
        # the new location, they should not be created at all.
        moves_to_push = moves_todo.filtered(lambda m: not m._skip_push())
        if moves_to_push:
            moves_to_push._push_apply()
        for move_dest in moves_todo.move_dest_ids:
            move_dests_per_company[move_dest.company_id.id] |= move_dest
        for company_id, move_dests in move_dests_per_company.items():
            move_dests.sudo().with_company(company_id)._action_assign()

        # We don't want to create back order for scrap moves
        # Replace by a kwarg in master
        if self.env.context.get('is_scrap'):
            return moves

        if picking and not cancel_backorder:
            backorder = picking._create_backorder()
            if any([m.state == 'assigned' for m in backorder.move_ids]):
                backorder._check_entire_pack()
        if moves_todo:
            moves_todo._check_quantity()
            moves_todo._action_synch_order()
        return moves_todo

    def _action_synch_order(self):
        return True

    def _create_backorder(self):
        # Split moves where necessary and move quants
        backorder_moves_vals = []
        for move in self:
            # To know whether we need to create a backorder or not, round to the general product's
            # decimal precision and not the product's UOM.
            rounding = self.env['decimal.precision'].precision_get('Product Unit')
            if float_compare(move.quantity, move.product_uom_qty, precision_digits=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity, move.product_id.uom_id, rounding_method='HALF-UP')
                new_move_vals = move._split(qty_split)
                backorder_moves_vals += new_move_vals
        backorder_moves = self.env['stock.move'].create(backorder_moves_vals)
        # The backorder moves are not yet in their own picking. We do not want to check entire packs for those
        # ones as it could messed up the result_package_id of the moves being currently validated
        backorder_moves.with_context(bypass_entire_pack=True)._action_confirm(merge=False, create_proc=False)
        return backorder_moves

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        if any(move.state not in ('draft', 'cancel') and (move.move_orig_ids or move.move_dest_ids) for move in self):
            raise UserError(_('You can not delete moves linked to another operation'))

    def unlink(self):
        # With the non plannified picking, draft moves could have some move lines.
        self.with_context(prefetch_fields=False).mapped('move_line_ids').unlink()
        return super(StockMove, self).unlink()

    def _prepare_move_split_vals(self, qty):
        vals = {
            'product_uom_qty': qty,
            'procure_method': self.procure_method,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids if x.state not in ('done', 'cancel')],
            'move_orig_ids': [(4, x.id) for x in self.move_orig_ids],
            'origin_returned_move_id': self.origin_returned_move_id.id,
            'price_unit': self.price_unit,
            'date_deadline': self.date_deadline,
        }
        if self.env.context.get('force_split_uom_id'):
            vals['product_uom'] = self.env.context['force_split_uom_id']
        return vals

    def _split(self, qty, restrict_partner_id=False):
        """ Splits `self` quantity and return values for a new moves to be created afterwards

        :param qty: float. quantity to split (given in product UoM)
        :param restrict_partner_id: optional partner that can be given in order to force the new move to restrict its choice of quants to the ones belonging to this partner.
        :returns: list of dict. stock move values """
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            raise UserError(_('You cannot split a stock move that has been set to \'Done\' or \'Cancel\'.'))
        elif self.state == 'draft':
            # we restrict the split of a draft move because if not confirmed yet, it may be replaced by several other moves in
            # case of phantom bom (with mrp module). And we don't want to deal with this complexity by copying the product that will explode.
            raise UserError(_('You cannot split a draft move. It needs to be confirmed first.'))

        if self.product_id.uom_id.is_zero(qty):
            return []

        decimal_precision = self.env['decimal.precision'].precision_get('Product Unit')

        # `qty` passed as argument is the quantity to backorder and is always expressed in the
        # quants UOM. If we're able to convert back and forth this quantity in the move's and the
        # quants UOM, the backordered move can keep the UOM of the move. Else, we'll create is in
        # the UOM of the quants.
        uom_qty = self.product_id.uom_id._compute_quantity(qty, self.product_uom, rounding_method='HALF-UP')
        if float_compare(qty, self.product_uom._compute_quantity(uom_qty, self.product_id.uom_id, rounding_method='HALF-UP'), precision_digits=decimal_precision) == 0:
            defaults = self._prepare_move_split_vals(uom_qty)
        else:
            defaults = self.with_context(force_split_uom_id=self.product_id.uom_id.id)._prepare_move_split_vals(qty)

        if restrict_partner_id:
            defaults['restrict_partner_id'] = restrict_partner_id

        # TDE CLEANME: remove context key + add as parameter
        if self.env.context.get('source_location_id'):
            defaults['location_id'] = self.env.context['source_location_id']
        new_move_vals = self.copy_data(defaults)

        # Update the original `product_qty` of the move. Use the general product's decimal
        # precision and not the move's UOM to handle case where the `quantity_done` is not
        # compatible with the move's UOM.
        new_product_qty = self.product_id.uom_id._compute_quantity(max(0, self.product_qty - qty), self.product_uom, round=False)
        new_product_qty = float_round(new_product_qty, precision_digits=self.env['decimal.precision'].precision_get('Product Unit'))
        self.with_context(do_not_unreserve=True).write({'product_uom_qty': new_product_qty})
        self._recompute_state()
        return new_move_vals

    def _post_process_created_moves(self):
        # This method is meant to be overriden in order to execute post
        # creation actions that would be bypassed since the move was
        # and will probably never be confirmed
        pass

    def _recompute_state(self):
        if self.env.context.get('preserve_state'):
            return
        moves_state_to_write = defaultdict(set)
        for move in self:
            rounding = move.product_uom.rounding
            if move.state in ('cancel', 'done') or (move.state == 'draft' and not move.quantity):
                continue
            elif float_compare(move.quantity, move.product_uom_qty, precision_rounding=rounding) >= 0:
                moves_state_to_write['assigned'].add(move.id)
            elif move.quantity and float_compare(move.quantity, move.product_uom_qty, precision_rounding=rounding) <= 0:
                moves_state_to_write['partially_available'].add(move.id)
            elif (move.procure_method == 'make_to_order' and not move.move_orig_ids) or\
                 (move.move_orig_ids and any(orig.product_uom.compare(orig.product_uom_qty, 0) > 0
                                             and orig.state not in ('done', 'cancel') for orig in move.move_orig_ids)):
                # In the process of merging a negative move, we may still have a negative move in the move_orig_ids at that point.
                moves_state_to_write['waiting'].add(move.id)
            else:
                moves_state_to_write['confirmed'].add(move.id)
        for state, moves_ids in moves_state_to_write.items():
            self.browse(moves_ids).filtered(lambda m: m.state != state).state = state

    def _is_consuming(self):
        self.ensure_one()
        from_wh = self.location_id.warehouse_id
        to_wh = self.location_dest_id.warehouse_id
        return self.picking_type_id.code in ('internal', 'outgoing') or (from_wh and to_wh and from_wh != to_wh)

    def _get_lang(self):
        """Determine language to use for translated description"""
        return self.picking_id.partner_id.lang or self.partner_id.lang or self.env.user.lang

    def _get_source_document(self):
        """ Return the move's document, used by `stock.forecasted_product_productt`
        and must be overrided to add more document type in the report.
        """
        self.ensure_one()
        return self.picking_id or False

    def _get_upstream_documents_and_responsibles(self, visited):
        if self not in visited and self.move_orig_ids and any(m.state not in ('done', 'cancel') for m in self.move_orig_ids):
            visited |= self
            return set(itertools.chain.from_iterable(
                move._get_upstream_documents_and_responsibles(visited)
                for move in self.move_orig_ids
                if move.state not in ('done', 'cancel')
            ))
        else:
            return []

    def _get_report_description_picking(self):
        self.ensure_one()
        description = self.description_picking or ""
        if description.startswith(self.product_id.display_name):
            description = description.removeprefix(self.product_id.display_name).strip()
        return description

    def _set_quantity_done_prepare_vals(self, qty):
        def _move_qty(qty):
            return self.product_id.uom_id._compute_quantity(qty, self.product_uom, round=False)

        self.ensure_one()
        res = []
        qty = self.product_uom._compute_quantity(qty, self.product_id.uom_id, round=False)
        total_qty = qty
        consumed_quant = set()
        for ml in self.move_line_ids:
            ml_qty = ml.quantity
            if ml.product_uom_id.compare(ml_qty, 0) < 0:
                continue

            if ml.product_uom_id != self.product_id.uom_id:
                ml_qty = ml.product_uom_id._compute_quantity(ml_qty, self.product_id.uom_id, round=False)

            if self.product_uom.is_zero(_move_qty(qty)):
                res.append(Command.delete(ml.id))
                continue

            if ml.product_id.uom_id.compare(ml_qty, qty) > 0:
                if ml.product_uom_id != self.product_id.uom_id:
                    qty = ml.product_id.uom_id._compute_quantity(qty, ml.product_uom_id, round=False)
                res.append(Command.update(ml.id, {'quantity': qty}))
                qty = 0
                continue

            if ml.result_package_id:
                qty -= ml_qty
                continue
            # remove what already on the line
            taken_qty = min(qty, ml_qty)
            qty -= taken_qty
            if self.product_uom.compare(_move_qty(qty), 0) <= 0:
                continue

            # find a quant similar to the move line on which we can reserve
            ml_quants = self.env['stock.quant']._get_reserve_quantity(self.product_id,
                                                                      ml.location_id,
                                                                      qty,
                                                                      lot_id=ml.lot_id,
                                                                      package_id=ml.package_id,
                                                                      owner_id=ml.owner_id,
                                                                      strict=True)
            avail_qty = sum(q[1] for q in ml_quants)
            # the quant did not add the quantity reserved on this specific move line
            consumed_quant |= {q[0].id for q in ml_quants}
            if self.product_uom.compare(avail_qty, qty) <= 0:
                qty -= avail_qty  # decrease the target quantity for the next move lines
                avail_qty += ml_qty  # add the actual move line quantity as we will update it and not `+=` it
                if ml.product_uom_id != self.product_id.uom_id:
                    avail_qty = ml.product_id.uom_id._compute_quantity(avail_qty, ml.product_uom_id, round=False)
                res.append(Command.update(ml.id, {'quantity': avail_qty}))

        # First reserve on quants
        if self.product_uom.compare(_move_qty(qty), 0.0) > 0:
            quants = self.env['stock.quant']._get_reserve_quantity(self.product_id, self.location_id, total_qty)
            for quant, avail_qty in quants:
                if quant.id in consumed_quant:
                    continue
                # compare the stock move quantity with the product free quantity
                taken_qty = min(qty, avail_qty)
                qty -= taken_qty
                res.append(Command.create(self._prepare_move_line_vals(quantity=taken_qty, reserved_quant=quant)))
                if self.product_id.uom_id.compare(_move_qty(qty), 0.0) <= 0:
                    break

        # If quant is not enough, create a(some) move lines from the move itself
        if self.product_uom.compare(_move_qty(qty), 0.0) > 0:
            if self.product_id.tracking != 'serial':
                qty = _move_qty(qty)
                vals = self._prepare_move_line_vals(quantity=0)
                vals['quantity'] = qty
                res.append((0, 0, vals))
            else:
                for _i in range(0, int(qty)):
                    vals = self._prepare_move_line_vals(quantity=0)
                    vals['quantity'] = 1
                    vals['product_uom_id'] = self.product_id.uom_id.id
                    res.append((0, 0, vals))
        return res

    def _set_quantity_done(self, qty):
        """
        Set the given quantity as quantity done on the move through the move lines. The method is
        able to handle move lines with a different UoM than the move (but honestly, this would be
        looking for trouble...).
        @param qty: quantity in the UoM of move.product_uom
        """
        existing_smls = self.move_line_ids
        self.move_line_ids = self._set_quantity_done_prepare_vals(qty)
        # `_set_quantity_done_prepare_vals` may return some commands to create new SMLs
        # These new SMLs need to be redirected thanks to putaway rules
        (self.move_line_ids - existing_smls)._apply_putaway_strategy()

    def _adjust_procure_method(self, picking_type_code=False):
        """ This method will try to apply the procure method MTO on some moves if
        a compatible MTO route is found. Else the procure method will be set to MTS
        picking_type_code (str, optional): Adjusts the procurement method based on
            the specified picking type code. The code to specify the picking type for
            the procurement group. Defaults to False.
        """
        # Prepare the MTSO variables. They are needed since MTSO moves are handled separately.
        # We need 2 dicts:
        # - needed quantity per location per product
        # - forecasted quantity per location per product

        for move in self:
            product_id = move.product_id
            location = move.location_id
            while location:
                domain = [
                    ('location_src_id', '=', location.id),
                    ('location_dest_id', '=', move.location_dest_id.id),
                    ('action', '!=', 'push')
                ]
                if picking_type_code:
                    domain.append(('picking_type_id.code', '=', picking_type_code))
                rule = self.env['stock.rule']._search_rule(False, move.packaging_uom_id, product_id, move.warehouse_id or move.picking_type_id.warehouse_id, domain)
                if rule:
                    break
                location = location.location_id
            if not rule:
                move.procure_method = 'make_to_stock'
                continue

            move.rule_id = rule.id
            if rule.procure_method in ['make_to_stock', 'make_to_order']:
                move.procure_method = rule.procure_method
            else:
                move.procure_method = 'make_to_stock'

    def _trigger_scheduler(self):
        """ Check for auto-triggered orderpoints and trigger them. """
        if not self or self.env['ir.config_parameter'].sudo().get_param('stock.no_auto_scheduler'):
            return

        orderpoints_by_company = defaultdict(lambda: self.env['stock.warehouse.orderpoint'])
        orderpoints_context_by_company = defaultdict(dict)
        for move in self:
            orderpoint = self.env['stock.warehouse.orderpoint'].search([
                ('product_id', '=', move.product_id.id),
                ('trigger', '=', 'auto'),
                ('location_id', 'parent_of', move.location_id.id),
                ('company_id', '=', move.company_id.id),
                '!', ('location_id', 'parent_of', move.location_dest_id.id),
            ], limit=1)
            if orderpoint:
                orderpoints_by_company[orderpoint.company_id] |= orderpoint
            if orderpoint and move.product_qty > orderpoint.product_min_qty and move.reference_ids:
                orderpoints_context_by_company[orderpoint.company_id].setdefault(orderpoint.id, set())
                orderpoints_context_by_company[orderpoint.company_id][orderpoint.id] |= set(move.reference_ids.ids)
        for company, orderpoints in orderpoints_by_company.items():
            orderpoints.with_context(origins=orderpoints_context_by_company[company])._procure_orderpoint_confirm(
                company_id=company, raise_user_error=False)

    def _trigger_assign(self):
        """ Check for and trigger action_assign for confirmed/partially_available moves related to done moves.
            Disable auto reservation if user configured to do so.
        """
        if not self or self.env['ir.config_parameter'].sudo().get_param('stock.picking_no_auto_reserve'):
            return

        product_domains = Domain.OR(
            [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id)]
            for move in self
        )
        static_domain = [('state', 'in', ['confirmed', 'partially_available']),
                         ('procure_method', '=', 'make_to_stock'),
                         '|',
                            ('reservation_date', '<=', fields.Date.today()),
                            ('picking_type_id.reservation_method', '=', 'at_confirm')
                        ]
        moves_to_reserve = self.env['stock.move'].search(
            Domain(static_domain) & product_domains,
            order='priority desc, date asc, id asc')
        moves_to_reserve = moves_to_reserve.sorted(key=lambda m: any(r in self.reference_ids.ids for r in m.reference_ids.ids), reverse=True)
        moves_to_reserve._action_assign()

    def _rollup_move_dests_fetch(self):
        seen = set(self.ids)
        self.fetch(['move_dest_ids'])
        move_dest_ids = set(self.move_dest_ids.ids)
        while not move_dest_ids.issubset(seen):
            seen |= move_dest_ids
            to_visit = self.browse(move_dest_ids)
            to_visit.fetch(['move_dest_ids'])
            move_dest_ids = set(to_visit.move_dest_ids.ids)

    def _rollup_move_origs_fetch(self):
        seen = set(self.ids)
        self.fetch(['move_orig_ids'])
        move_orig_ids = set(self.move_orig_ids.ids)
        while not move_orig_ids.issubset(seen):
            seen |= move_orig_ids
            to_visit = self.browse(move_orig_ids)
            to_visit.fetch(['move_orig_ids'])
            move_orig_ids = set(to_visit.move_orig_ids.ids)

    def _rollup_move_dests(self, seen=False) -> OrderedSet[int]:
        return self._rollup_moves(origin=False, seen=seen)

    def _rollup_move_origs(self, seen=False) -> OrderedSet[int]:
        return self._rollup_moves(seen=seen)

    def _rollup_moves(self, origin=True, seen=False) -> OrderedSet[int]:
        """
            Find all moves in chain depending the direction (origin)

            origin: if set (default), returns the origin moves, else return the destinations
        """
        target_field = "move_orig_ids" if origin else "move_dest_ids"
        if not seen:
            seen = OrderedSet()
        unseen = OrderedSet(self.ids) - seen
        if not unseen:
            return seen
        seen.update(unseen)
        self.filtered(lambda m: m.id in unseen)[target_field]._rollup_moves(origin, seen)
        return seen

    def _get_forecast_availability_outgoing(self, warehouse, location_id=False):
        """ Get forcasted information (sum_qty_expected, max_date_expected) of self for the warehouse's locations.
        :param warehouse: warehouse to search under
        :param  location_id: location source of outgoing moves
        :return: a defaultdict of outgoing moves from warehouse for product_id in self, values are tuple (sum_qty_expected, max_date_expected)
        :rtype: defaultdict
        """
        wh_location_query = self.env['stock.location']._search([('id', 'child_of', warehouse.view_location_id.id)])
        forecast_lines = self.env['stock.forecasted_product_product']._get_report_lines(False, self.product_id.ids, wh_location_query, location_id or warehouse.lot_stock_id, read=False)
        result = defaultdict(lambda: (0.0, False))
        for line in forecast_lines:
            move_out = line.get('move_out')
            if not move_out or not line['quantity']:
                continue
            move_in = line.get('move_in')
            qty_expected = line['quantity'] + result[move_out][0] if line['replenishment_filled'] else -line['quantity']
            date_expected = False
            if move_in:
                date_expected = max(move_in.date, result[move_out][1]) if result[move_out][1] else move_in.date
            result[move_out] = (qty_expected, date_expected)

        return result

    def action_open_reference(self):
        """ Open the form view of the move's reference document, if one exists, otherwise open form view of self
        """
        self.ensure_one()
        if not self.is_inventory and self.location_dest_usage == 'inventory':
            return {
                'res_model': 'stock.scrap',
                'type': 'ir.actions.act_window',
                'views': [[False, 'form']],
                'res_id': self.scrap_id.id,
            }
        source = self.picking_id
        if source and source.browse().has_access('read'):
            return {
                'res_model': source._name,
                'type': 'ir.actions.act_window',
                'views': [[False, "form"]],
                'res_id': source.id,
            }
        return {
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [[False, "form"]],
            'res_id': self.id,
        }

    def _convert_string_into_field_data(self, string, options):
        string = string.replace(',', '.')  # Parsing string as float works only with dot, not comma.
        if regex_findall(r'^([0-9]+\.?[0-9]*|\.[0-9]+)$', string):  # Number => Quantity.
            return {'quantity': float(string)}
        return False

    def _match_searched_availability(self, operator, value, get_comparison_date):
        def get_stock_moves(moves, state):
            if state == 'available':
                return moves.filtered(lambda m: m.forecast_availability == m.product_qty and not m.forecast_expected_date)
            elif state == 'expected':
                return moves.filtered(lambda m: m.forecast_availability == m.product_qty and m.forecast_expected_date and m.forecast_expected_date <= get_comparison_date(m))
            elif state == 'late':
                return moves.filtered(lambda m: m.forecast_availability == m.product_qty and m.forecast_expected_date and m.forecast_expected_date > get_comparison_date(m))
            elif state == 'unavailable':
                return moves if moves.filtered(lambda m: m.forecast_availability < m.product_qty) else self.env['stock.move']
            else:
                raise UserError(_('Selection not supported.'))

        if not value:
            raise UserError(_('Search not supported without a value.'))

        # We consider an operation without any moves as always available since there is no goods to wait.
        if len(self) == 0:
            is_selected_available = any(val == 'available' for val in value) if isinstance(value, list) else value == 'available'
            if is_selected_available == (operator in {'=', 'in'}):
                return True
            return False
        moves = self
        if operator == '=':
            moves = get_stock_moves(moves, value)
        elif operator == '!=':
            moves = moves - get_stock_moves(moves, value)
        elif operator == 'in':
            search_moves = self.env['stock.move']
            for state in value:
                search_moves |= get_stock_moves(moves, state)
            moves = search_moves
        elif operator == 'not in':
            search_moves = self.env['stock.move']
            for state in value:
                search_moves |= get_stock_moves(moves, state)
            moves = self - search_moves
        else:
            raise UserError(_('Operation not supported'))
        return bool(moves)

    def _break_mto_link(self, parent_move):
        self.move_orig_ids = [Command.unlink(parent_move.id)]
        self.procure_method = 'make_to_stock'
        self._recompute_state()

    def _get_product_catalog_lines_data(self, parent_record=False, **kwargs):
        if not (parent_record and self):
            return {
                'quantity': 0,
            }
        self.product_id.ensure_one()
        return {
            **parent_record._get_product_price_and_data(self.product_id),
            'quantity': sum(
                self.mapped(
                    lambda line: line.product_uom._compute_quantity(
                        qty=line.product_qty,
                        to_unit=line.product_uom,
                    ),
                ),
            ),
            'readOnly': len(self) > 1,
            'uomDisplayName': len(self) == 1 and self.product_uom.display_name or self.product_id.uom_id.display_name,
        }

    def _visible_quantity(self):
        self.ensure_one()
        return self.quantity

    def _is_incoming(self):
        self.ensure_one()
        return self.location_id.usage in ('customer', 'supplier') or (
            self.location_id.usage == 'transit' and not self.location_id.company_id
        )

    def _is_outgoing(self):
        self.ensure_one()
        return self.location_dest_id.usage in ('customer', 'supplier') or (
            self.location_dest_id.usage == 'transit' and not self.location_dest_id.company_id
        )


# FILEPATH: odoo/addons/stock/models/stock_move_line.py
class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _description = "Product Moves (Stock Move Line)"
    _rec_name = "product_id"
    _order = "result_package_id desc, id"

    picking_id = fields.Many2one(
        'stock.picking', 'Transfer', bypass_search_access=True,
        check_company=True,
        index=True,
        help='The stock operation where the packing has been made')
    move_id = fields.Many2one(
        'stock.move', 'Stock Operation',
        check_company=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=True, index=True)
    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade", check_company=True, domain="[('type', '!=', 'service')]", index=True)
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit', required=True, domain="[('id', 'in', allowed_uom_ids)]",
        compute="_compute_product_uom_id", store=True, readonly=False, precompute=True,
    )
    product_category_name = fields.Char(related="product_id.categ_id.complete_name", string="Product Category")
    quantity = fields.Float(
        'Quantity', digits='Product Unit', copy=False, store=True,
        compute='_compute_quantity', readonly=False)
    quantity_product_uom = fields.Float(
        'Quantity in Product UoM', digits='Product Unit',
        copy=False, compute='_compute_quantity_product_uom', store=True)
    picked = fields.Boolean('Picked', compute='_compute_picked', store=True, readonly=False, copy=False)
    package_id = fields.Many2one(
        'stock.package', 'Source Package', ondelete='restrict',
        check_company=True,
        domain="[('location_id', '=', location_id)]")
    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id)]", check_company=True)
    lot_name = fields.Char('Lot/Serial Number Name')
    result_package_id = fields.Many2one(
        'stock.package', 'Destination Package',
        ondelete='restrict', required=False, check_company=True,
        domain="['|', '|', ('location_id', '=', location_dest_id), ('id', '=', package_id), '&', ('location_id', '=', False), '|', ('move_line_ids', '=', False), ('move_line_ids.location_dest_id', '=', location_dest_id)]",
        help="If set, the operations are packed into this package")
    result_package_dest_name = fields.Char('Destination Package Name', related='result_package_id.dest_complete_name')
    package_history_id = fields.Many2one('stock.package.history', string="Package History", index='btree_not_null')
    is_entire_pack = fields.Boolean('Is added through entire package')
    date = fields.Datetime(
        'Date', default=fields.Datetime.now, required=True,
        help="Creation date of this move line until updated due to: quantity being increased, 'picked' status has updated, or move line is done.")
    scheduled_date = fields.Datetime('Scheduled Date', related='move_id.date')
    owner_id = fields.Many2one(
        'res.partner', 'From Owner',
        check_company=True, index='btree_not_null',
        help="When validating the transfer, the products will be taken from this owner.")
    location_id = fields.Many2one(
        'stock.location', 'From', domain="[('usage', '!=', 'view')]", check_company=True, required=True,
        compute="_compute_location_id", store=True, readonly=False, precompute=True, index=True,
    )
    location_dest_id = fields.Many2one('stock.location', 'To', domain="[('usage', '!=', 'view')]", check_company=True, required=True, compute="_compute_location_id", store=True, index=True, readonly=False, precompute=True)
    location_usage = fields.Selection(string="Source Location Type", related='location_id.usage')
    location_dest_usage = fields.Selection(string="Destination Location Type", related='location_dest_id.usage')
    lots_visible = fields.Boolean(compute='_compute_lots_visible')
    picking_partner_id = fields.Many2one(related='picking_id.partner_id', readonly=True)
    move_partner_id = fields.Many2one(related='move_id.partner_id', readonly=True)
    picking_code = fields.Selection(related='picking_type_id.code', readonly=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation type', compute='_compute_picking_type_id', search='_search_picking_type_id')
    picking_type_use_create_lots = fields.Boolean(related='picking_type_id.use_create_lots', readonly=True)
    picking_type_use_existing_lots = fields.Boolean(related='picking_type_id.use_existing_lots', readonly=True)
    state = fields.Selection(related='move_id.state', store=True)
    scrap_id = fields.Many2one(related='move_id.scrap_id')
    is_inventory = fields.Boolean(related='move_id.is_inventory')
    is_locked = fields.Boolean(related='move_id.is_locked', readonly=True)
    consume_line_ids = fields.Many2many('stock.move.line', 'stock_move_line_consume_rel', 'consume_line_id', 'produce_line_id')
    produce_line_ids = fields.Many2many('stock.move.line', 'stock_move_line_consume_rel', 'produce_line_id', 'consume_line_id')
    reference = fields.Char(related='move_id.reference', readonly=False)
    tracking = fields.Selection(related='product_id.tracking', readonly=True)
    origin = fields.Char(related='move_id.origin', string='Source')
    description_picking = fields.Text(related='move_id.description_picking')
    quant_id = fields.Many2one('stock.quant', "Pick From", store=False)  # Dummy field for the detailed operation view
    picking_location_id = fields.Many2one(related='picking_id.location_id')
    picking_location_dest_id = fields.Many2one(related='picking_id.location_dest_id')

    _free_reservation_index = models.Index("""(id, company_id, product_id, lot_id, location_id, owner_id, package_id)
        WHERE (state IS NULL OR state NOT IN ('cancel', 'done')) AND quantity_product_uom > 0 AND picked IS NOT TRUE""")

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids', 'product_id.seller_ids', 'product_id.seller_ids.product_uom_id')
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids | line.sudo().product_id.seller_ids.product_uom_id

    @api.depends('move_id.product_uom', 'product_id.uom_id')
    def _compute_product_uom_id(self):
        for line in self:
            if not line.product_uom_id:
                if line.move_id.product_uom:
                    line.product_uom_id = line.move_id.product_uom.id
                else:
                    line.product_uom_id = line.product_id.uom_id.id

    @api.depends('picking_id.picking_type_id', 'product_id.tracking')
    def _compute_lots_visible(self):
        for line in self:
            picking = line.picking_id
            if picking.picking_type_id and line.product_id.tracking != 'none':  # TDE FIXME: not sure correctly migrated
                line.lots_visible = picking.picking_type_id.use_existing_lots or picking.picking_type_id.use_create_lots
            else:
                line.lots_visible = line.product_id.tracking != 'none'

    @api.depends('state')
    def _compute_picked(self):
        for line in self:
            if line.move_id.state == 'done' or (self.env.context.get('allow_parent_move_picked_reset') and line.move_id.picked):
                line.picked = True

    @api.depends('picking_id')
    def _compute_picking_type_id(self):
        self.picking_type_id = False
        for line in self:
            if line.picking_id:
                line.picking_type_id = line.picking_id.picking_type_id

    @api.depends('move_id', 'move_id.location_id', 'move_id.location_dest_id', 'picking_id')
    def _compute_location_id(self):
        for line in self:
            if not line.location_id or line._origin.picking_id.location_id != line.picking_id.location_id:
                line.location_id = line.move_id.location_id or line.picking_id.location_id
            if not line.location_dest_id or line._origin.picking_id.location_dest_id != line.picking_id.location_dest_id:
                line.location_dest_id = line.move_id.location_dest_id or line.picking_id.location_dest_id

    def _search_picking_type_id(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS:
            return NotImplemented
        return Domain('picking_id.picking_type_id', operator, value)

    @api.depends('quant_id')
    def _compute_quantity(self):
        for record in self:
            if not record.quant_id or record.quantity:
                continue
            product_uom = record.product_id.uom_id
            sml_uom = record.product_uom_id
            move_visible_quantity = record.move_id and record.move_id._visible_quantity() or 0.0

            move_demand = record.move_id.product_uom._compute_quantity(record.move_id.product_uom_qty, sml_uom, rounding_method='HALF-UP')
            move_quantity = record.move_id.product_uom._compute_quantity(move_visible_quantity, sml_uom, rounding_method='HALF-UP')
            quant_qty = product_uom._compute_quantity(record.quant_id.available_quantity, sml_uom, rounding_method='HALF-UP')

            if sml_uom.compare(move_demand, move_quantity) > 0:
                record.quantity = max(0, min(quant_qty, move_demand - move_quantity))
            else:
                record.quantity = max(0, quant_qty)

    @api.depends('quantity', 'product_uom_id')
    def _compute_quantity_product_uom(self):
        for line in self:
            line.quantity_product_uom = line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id, rounding_method='HALF-UP')

    @api.constrains('lot_id', 'product_id')
    def _check_lot_product(self):
        for line in self:
            if line.lot_id and line.product_id != line.lot_id.sudo().product_id:
                raise ValidationError(_(
                    'This lot %(lot_name)s is incompatible with this product %(product_name)s',
                    lot_name=line.lot_id.name,
                    product_name=line.product_id.display_name
                ))

    @api.constrains('quantity')
    def _check_positive_quantity(self):
        if any(ml.quantity < 0 for ml in self):
            raise ValidationError(_('You can not enter negative quantities.'))

    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.lots_visible = self.product_id.tracking != 'none'

    @api.onchange('lot_name', 'lot_id')
    def _onchange_serial_number(self):
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This includes:
            - automatically switch `quantity` to 1.0
            - warn if he has already encoded `lot_name` in another move line
            - warn (and update if appropriate) if the SN is in a different source location than selected
        """
        res = {}
        if self.product_id.tracking == 'serial':
            if not self.quantity:
                self.quantity = 1

            message = None
            if self.lot_name or self.lot_id:
                move_lines_to_check = self._get_similar_move_lines() - self
                if self.lot_name:
                    counter = Counter([line.lot_name for line in move_lines_to_check])
                    if counter.get(self.lot_name) and counter[self.lot_name] > 1:
                        message = _('You cannot use the same serial number twice. Please correct the serial numbers encoded.')
                    elif not self.lot_id:
                        lots = self.env['stock.lot'].search([('product_id', '=', self.product_id.id),
                                                             ('name', '=', self.lot_name),
                                                             '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])
                        quants = lots.quant_ids.filtered(lambda q: q.quantity != 0 and q.location_id.usage in ['customer', 'internal', 'transit'])
                        if quants:
                            message = _(
                                'Serial number (%(serial_number)s) already exists in location(s): %(location_list)s. Please correct the serial number encoded.',
                                serial_number=self.lot_name,
                                location_list=quants.location_id.mapped('display_name')
                            )
                elif self.lot_id:
                    counter = Counter([line.lot_id.id for line in move_lines_to_check])
                    if counter.get(self.lot_id.id) and counter[self.lot_id.id] > 1:
                        message = _('You cannot use the same serial number twice. Please correct the serial numbers encoded.')
                    else:
                        # check if in correct source location
                        message, recommended_location = self.env['stock.quant'].sudo()._check_serial_number(
                            self.product_id, self.lot_id, self.company_id, self.location_id, self.picking_id.location_id)
                        if recommended_location:
                            self.location_id = recommended_location
            if message:
                res['warning'] = {'title': _('Warning'), 'message': message}
        return res

    @api.onchange('quantity', 'product_uom_id')
    def _onchange_quantity(self):
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This onchange will warn him if he set `quantity` to a non-supported value.
        """
        res = {}
        if self.quantity and self.product_id.tracking == 'serial':
            if self.product_id.uom_id.compare(self.quantity_product_uom, 1.0) != 0 and not self.product_id.uom_id.is_zero(self.quantity_product_uom):
                raise UserError(_('You can only process 1.0 %s of products with unique serial number.', self.product_id.uom_id.name))
        return res

    @api.onchange('result_package_id', 'product_id', 'product_uom_id', 'quantity')
    def _onchange_putaway_location(self):
        default_dest_location = self._get_default_dest_location()
        if not self.id and self.env.user.has_group('stock.group_stock_multi_locations') and self.product_id and self.quantity_product_uom \
                and self.location_dest_id == default_dest_location:
            quantity = self.quantity_product_uom
            self.location_dest_id = default_dest_location.with_context(exclude_sml_ids=self.ids)._get_putaway_strategy(
                self.product_id, quantity=quantity, package=self.result_package_id)

    def _apply_putaway_strategy(self):
        if self.env.context.get('avoid_putaway_rules'):
            return
        self = self.with_context(do_not_unreserve=True)
        for (package), smls in groupby(self, lambda sml: (sml.result_package_id.outermost_package_id)):
            smls = self.env['stock.move.line'].concat(*smls)
            locations = smls.move_id.location_dest_id.child_internal_location_ids
            excluded_smls = set(smls.ids)
            if package.package_type_id:
                best_loc = smls.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls, products=smls.product_id, locations=locations)._get_putaway_strategy(self.env['product.product'], package=package)
                smls.location_dest_id = best_loc
            elif package:
                used_locations = set()
                for sml in smls:
                    if len(used_locations) > 1:
                        break
                    sml.location_dest_id = sml.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls, locations=locations)._get_putaway_strategy(sml.product_id, quantity=sml.quantity)
                    excluded_smls.discard(sml.id)
                    used_locations.add(sml.location_dest_id)
                if len(used_locations) > 1:
                    for move, grouped_smls in smls.grouped('move_id').items():
                        grouped_smls.location_dest_id = move.location_dest_id
            else:
                for sml in smls:
                    putaway_loc_id = sml.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls)._get_putaway_strategy(
                        sml.product_id, quantity=sml.quantity, packaging=sml.move_id.packaging_uom_id,
                    )
                    if putaway_loc_id != sml.location_dest_id:
                        sml.location_dest_id = putaway_loc_id
                    excluded_smls.discard(sml.id)

    def _get_default_dest_location(self):
        if not self.env.user.has_group('stock.group_stock_multi_locations'):
            return self.location_dest_id[:1]
        if self.env.context.get('default_location_dest_id'):
            return self.env['stock.location'].browse([self.env.context.get('default_location_dest_id')])
        return (self.move_id.location_dest_id or self.picking_id.location_dest_id or self.location_dest_id)[:1]

    def _get_putaway_additional_qty(self):
        addtional_qty = {}
        for ml in self._origin:
            qty = ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id)
            addtional_qty[ml.location_dest_id.id] = addtional_qty.get(ml.location_dest_id.id, 0) - qty
        return addtional_qty

    def get_move_line_quant_match(self, move_id, dirty_move_line_ids, dirty_quant_ids):
        # Since the quant_id field is neither stored nor computed, this method is used to compute the match if it exists
        move = self.env['stock.move'].browse(move_id)
        deleted_move_lines = move.move_line_ids - self
        dirty_move_lines = self.env['stock.move.line'].browse(dirty_move_line_ids)
        quants_data = []
        move_lines_data = []
        domain = Domain("id", "in", dirty_quant_ids) | Domain.OR(
            Domain([
                ("product_id", "=", move_line.product_id.id),
                ("lot_id", "=", move_line.lot_id.id),
                ("location_id", "=", move_line.location_id.id),
                ("package_id", "=", move_line.package_id.id),
                ("owner_id", "=", move_line.owner_id.id),
            ])
            for move_line in dirty_move_lines | deleted_move_lines
        )
        if not domain.is_false():
            quants = self.env['stock.quant'].search(domain)
            for quant in quants:
                dirty_lines = dirty_move_lines.filtered(lambda ml: ml.product_id == quant.product_id
                    and ml.lot_id == quant.lot_id
                    and ml.location_id == quant.location_id
                    and ml.package_id == quant.package_id
                    and ml.owner_id == quant.owner_id
                )
                deleted_lines = deleted_move_lines.filtered(lambda ml: ml.product_id == quant.product_id
                    and ml.lot_id == quant.lot_id
                    and ml.location_id == quant.location_id
                    and ml.package_id == quant.package_id
                    and ml.owner_id == quant.owner_id
                )
                quants_data.append((quant.id, {"available_quantity": quant.available_quantity + sum(ml.quantity_product_uom for ml in deleted_lines), "move_line_ids": dirty_lines.ids}))
                move_lines_data += [(ml.id, {"quantity": ml.quantity, "quant_id": quant.id}) for ml in dirty_lines]
        return [quants_data, move_lines_data]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('move_id'):
                vals['company_id'] = self.env['stock.move'].browse(vals['move_id']).company_id.id
            elif vals.get('picking_id'):
                vals['company_id'] = self.env['stock.picking'].browse(vals['picking_id']).company_id.id
            if vals.get('move_id') and 'picked' not in vals:
                vals['picked'] = self.env['stock.move'].browse(vals['move_id']).picked
            if vals.get('quant_id'):
                vals.update(self._copy_quant_info(vals))

        mls = super().create(vals_list)

        created_moves = set()

        def create_move(move_line):
            new_move = self.env['stock.move'].create(move_line._prepare_stock_move_vals())
            move_line.move_id = new_move.id
            created_moves.add(new_move.id)

        # If the move line is directly create on the picking view.
        # If this picking is already done we should generate an
        # associated done move.
        for move_line in mls:
            if move_line.move_id or not move_line.picking_id:
                continue
            if move_line.picking_id.state != 'done':
                moves = move_line._get_linkable_moves()
                if moves:
                    vals = {
                        'move_id': moves[0].id,
                        'picking_id': moves[0].picking_id.id,
                    }
                    if moves[0].picked:
                        vals['picked'] = True
                    move_line.write(vals)
                else:
                    create_move(move_line)
            else:
                create_move(move_line)

        move_to_recompute_state = set()
        for move_line in mls:
            if move_line.state == 'done':
                continue
            location = move_line.location_id
            product = move_line.product_id
            move = move_line.move_id
            if move:
                reservation = not move._should_bypass_reservation()
            else:
                reservation = product.is_storable and not location.should_bypass_reservation()
            if move_line.quantity_product_uom and reservation:
                self.env.context.get('reserved_quant', self.env['stock.quant'])._update_reserved_quantity(
                    product, location, move_line.quantity_product_uom, lot_id=move_line.lot_id, package_id=move_line.package_id, owner_id=move_line.owner_id)

                if move:
                    move_to_recompute_state.add(move.id)
        self.env['stock.move'].browse(move_to_recompute_state)._recompute_state()
        self.env['stock.move'].browse(created_moves)._post_process_created_moves()

        for ml in mls:
            if ml.state == 'done':
                if ml.product_id.is_storable:
                    Quant = self.env['stock.quant']
                    quantity = ml.product_uom_id._compute_quantity(ml.quantity, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                    available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                    if available_qty < 0 and ml.lot_id:
                        # see if we can compensate the negative quants with some untracked quants
                        untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                        if untracked_qty:
                            taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                            Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                            Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                    Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
                next_moves = ml.move_id.move_dest_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
                next_moves._do_unreserve()
                next_moves._action_assign()
        move_done = mls.filtered(lambda m: m.state == "done").move_id
        if move_done:
            move_done._check_quantity()
        return mls

    def write(self, vals):
        if 'product_id' in vals and any(vals.get('state', ml.state) != 'draft' and vals['product_id'] != ml.product_id.id for ml in self):
            raise UserError(_("Changing the product is only allowed in 'Draft' state."))

        if ('lot_id' in vals or 'quant_id' in vals) and len(self.product_id) > 1:
            raise UserError(_("Changing the Lot/Serial number for move lines with different products is not allowed."))

        moves_to_recompute_state = self.env['stock.move']
        packages_to_check = self.env['stock.package']
        if 'result_package_id' in vals:
            # Either changed the result package or removed it
            packages_to_check = self.env['stock.package'].browse(self.result_package_id._get_all_package_dest_ids())
        triggers = [
            ('location_id', 'stock.location'),
            ('location_dest_id', 'stock.location'),
            ('lot_id', 'stock.lot'),
            ('package_id', 'stock.package'),
            ('result_package_id', 'stock.package'),
            ('owner_id', 'res.partner'),
            ('product_uom_id', 'uom.uom')
        ]
        if vals.get('quant_id'):
            vals.update(self._copy_quant_info(vals))
        updates = {}
        for key, model in triggers:
            if self.env.context.get('skip_uom_conversion'):
                continue
            if key in vals:
                updates[key] = vals[key] if isinstance(vals[key], models.BaseModel) else self.env[model].browse(vals[key])

        # When we try to write on a reserved move line any fields from `triggers`, result_package_id excepted,
        # or directly reserved_uom_qty` (the actual reserved quantity), we need to make sure the associated
        # quants are correctly updated in order to not make them out of sync (i.e. the sum of the
        # move lines `reserved_uom_qty` should always be equal to the sum of `reserved_quantity` on
        # the quants). If the new charateristics are not available on the quants, we chose to
        # reserve the maximum possible.
        if (updates and {'result_package_id'}.difference(updates.keys())) or 'quantity' in vals:
            for ml in self:
                if not ml.product_id.is_storable or ml.state == 'done':
                    continue
                if 'quantity' in vals or 'product_uom_id' in vals:
                    new_ml_uom = updates.get('product_uom_id', ml.product_uom_id)
                    new_reserved_qty = new_ml_uom._compute_quantity(
                        vals.get('quantity', ml.quantity), ml.product_id.uom_id, rounding_method='HALF-UP')
                    # Make sure `reserved_uom_qty` is not negative.
                    if ml.product_id.uom_id.compare(new_reserved_qty, 0) < 0:
                        raise UserError(_('Reserving a negative quantity is not allowed.'))
                else:
                    new_reserved_qty = ml.quantity_product_uom

                # Unreserve the old charateristics of the move line.
                if not ml.product_uom_id.is_zero(ml.quantity_product_uom):
                    ml._synchronize_quant(-ml.quantity_product_uom, ml.location_id, action="reserved")

                # Reserve the maximum available of the new charateristics of the move line.
                if not ml.move_id._should_bypass_reservation(updates.get('location_id', ml.location_id)):
                    ml._synchronize_quant(
                        new_reserved_qty, updates.get('location_id', ml.location_id), action="reserved",
                        lot=updates.get('lot_id', ml.lot_id), package=updates.get('package_id', ml.package_id),
                        owner=updates.get('owner_id', ml.owner_id))

                if ('quantity' in vals and vals['quantity'] != ml.quantity) or 'product_uom_id' in vals:
                    moves_to_recompute_state |= ml.move_id

        # When editing a done move line, the reserved availability of a potential chained move is impacted. Take care of running again `_action_assign` on the concerned moves.
        mls = self.env['stock.move.line']
        if updates or 'quantity' in vals:
            next_moves = self.env['stock.move']
            mls = self.filtered(lambda ml: ml.move_id.state == 'done' and ml.product_id.is_storable)
            if not updates:  # we can skip those where quantity is already good up to UoM rounding
                mls = mls.filtered(lambda ml: not ml.product_uom_id.is_zero(ml.quantity - vals['quantity']))
            for ml in mls:
                # undo the original move line
                in_date = ml._synchronize_quant(-ml.quantity_product_uom, ml.location_dest_id, package=ml.result_package_id)[1]
                ml._synchronize_quant(ml.quantity_product_uom, ml.location_id, in_date=in_date)

                # Unreserve and reserve following move in order to have the real reserved quantity on move_line.
                next_moves |= ml.move_id.move_dest_ids.filtered(lambda move: move.state not in ('done', 'cancel'))

                # Log a note
                if ml.picking_id:
                    ml._log_message(ml.picking_id, ml, 'stock.track_move_template', vals)
            move_done = mls.move_id
            if move_done:
                move_done._check_quantity()

        # update the date when it seems like (additional) quantities are "done" and the date hasn't been manually updated
        if 'date' not in vals and ('product_uom_id' in vals or 'quantity' in vals or vals.get('picked', False)):
            updated_ml_ids = set()
            for ml in self:
                if ml.state in ['draft', 'cancel', 'done']:
                    continue
                if vals.get('picked', False) and not ml.picked:
                    updated_ml_ids.add(ml.id)
                    continue
                if ('quantity' in vals or 'product_uom_id' in vals) and ml.picked:
                    new_qty = updates.get('product_uom_id', ml.product_uom_id)._compute_quantity(vals.get('quantity', ml.quantity), ml.product_id.uom_id, rounding_method='HALF-UP')
                    old_qty = ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id, rounding_method='HALF-UP')
                    if ml.product_uom_id.compare(old_qty, new_qty) < 0:
                        updated_ml_ids.add(ml.id)
            self.env['stock.move.line'].browse(updated_ml_ids).date = fields.Datetime.now()

        res = super(StockMoveLine, self).write(vals)

        for ml in mls:
            available_qty, dummy = ml._synchronize_quant(-ml.quantity_product_uom, ml.location_id)
            ml._synchronize_quant(ml.quantity_product_uom, ml.location_dest_id, package=ml.result_package_id)
            if available_qty < 0:
                ml._free_reservation(
                    ml.product_id, ml.location_id,
                    abs(available_qty), lot_id=ml.lot_id, package_id=ml.package_id,
                    owner_id=ml.owner_id)

        if packages_to_check:
            # Clear the dest from packages if not linked to any active picking
            packages_to_check.filtered(lambda p: p.package_dest_id and not p.picking_ids).package_dest_id = False
        if updates or 'quantity' in vals:
            # Updated fields could imply that entire packs are no longer entire.
            if mls_to_update := self._get_lines_not_entire_pack():
                mls_to_update.write({'is_entire_pack': False})

        # As stock_account values according to a move's `product_uom_qty`, we consider that any
        # done stock move should have its `quantity_done` equals to its `product_uom_qty`, and
        # this is what move's `action_done` will do. So, we replicate the behavior here.
        if updates or 'quantity' in vals:
            next_moves._do_unreserve()
            next_moves._action_assign()

        if moves_to_recompute_state:
            moves_to_recompute_state._recompute_state()

        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done_or_cancel(self):
        for ml in self:
            if ml.state in ('done', 'cancel'):
                raise UserError(_(
                    "Deleting product moves after the transfer is done?\n\n"
                    "That would be like going back in time to revert all operations triggered after this move. Who knows what the end result would be, So let's not do it.\n\n"
                    "Try changing the “done” quantity to 0 instead."
                ))

    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        for ml in self:
            # Unlinking a move line should unreserve.
            if not float_is_zero(ml.quantity_product_uom, precision_digits=precision) and ml.move_id and not ml.move_id._should_bypass_reservation(ml.location_id):
                self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.quantity_product_uom, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
        moves = self.mapped('move_id')
        packages = self.env['stock.package'].browse(self.result_package_id._get_all_package_dest_ids())
        res = super().unlink()
        if moves:
            # Add with_prefetch() to set the _prefecht_ids = _ids
            # because _prefecht_ids generator look lazily on the cache of move_id
            # which is clear by the unlink of move line
            moves.with_prefetch()._recompute_state()
        if packages:
            # Clear the dest from packages if not linked to any active picking
            packages.filtered(lambda p: p.package_dest_id and not p.picking_ids).package_dest_id = False
        return res

    def _exclude_requiring_lot(self):
        self.ensure_one()
        return self.move_id.picking_type_id or self.is_inventory or self.lot_id or self.move_id.scrap_id

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """

        # First, we loop over all the move lines to do a preliminary check: `quantity` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `quantity` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_ids_tracked_without_lot = OrderedSet()
        ml_ids_to_delete = OrderedSet()
        ml_ids_to_create_lot = OrderedSet()
        ml_ids_to_check = defaultdict(OrderedSet)

        for ml in self:
            # Check here if `ml.quantity` respects the rounding of `ml.product_uom_id`.
            uom_qty = ml.product_uom_id.round(ml.quantity, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit')
            quantity = float_round(ml.quantity, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, quantity, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%(product)s" doesn\'t respect the rounding precision '
                                  'defined on the unit of measure "%(unit)s". Please change the quantity done or the '
                                  'rounding precision of your unit of measure.',
                                  product=ml.product_id.display_name, unit=ml.product_uom_id.name))

            qty_done_float_compared = ml.product_uom_id.compare(ml.quantity, 0)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking == 'none':
                    continue
                picking_type_id = ml.move_id.picking_type_id
                if not ml._exclude_requiring_lot():
                    ml_ids_tracked_without_lot.add(ml.id)
                    continue
                if not picking_type_id or ml.lot_id or (not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots):
                    # If the user disabled both `use_create_lots` and `use_existing_lots`
                    # checkboxes on the picking type, he's allowed to enter tracked
                    # products without a `lot_id`.
                    continue
                if picking_type_id.use_create_lots:
                    ml_ids_to_check[(ml.product_id, ml.company_id)].add(ml.id)
                else:
                    ml_ids_tracked_without_lot.add(ml.id)

            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            elif not ml.is_inventory:
                ml_ids_to_delete.add(ml.id)

        for (product, _company), mls in ml_ids_to_check.items():
            mls = self.env['stock.move.line'].browse(mls)
            lots = self.env['stock.lot'].search([
                '|', ('company_id', '=', False), ('company_id', '=', ml.company_id.id),
                ('product_id', '=', product.id),
                ('name', 'in', mls.mapped('lot_name')),
            ])
            lots = {lot.name: lot for lot in lots}
            for ml in mls:
                lot = lots.get(ml.lot_name)
                if lot:
                    ml.lot_id = lot.id
                elif ml.lot_name:
                    ml_ids_to_create_lot.add(ml.id)
                else:
                    ml_ids_tracked_without_lot.add(ml.id)

        if ml_ids_tracked_without_lot:
            mls_tracked_without_lot = self.env['stock.move.line'].browse(ml_ids_tracked_without_lot)
            products_list = "\n".join(f"- {product_name}" for product_name in mls_tracked_without_lot.mapped("product_id.display_name"))
            raise UserError(
                _(
                    "You need to supply a Lot/Serial Number for product:\n%(products)s",
                    products=products_list,
                ),
            )
        if ml_ids_to_create_lot:
            self.env['stock.move.line'].browse(ml_ids_to_create_lot)._create_and_assign_production_lot()

        mls_to_delete = self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()

        mls_todo = (self - mls_to_delete)
        mls_todo._check_company()

        # Now, we can actually move the quant.
        ml_ids_to_ignore = OrderedSet()
        quants_cache = self.env['stock.quant']._get_quants_by_products_locations(
            mls_todo.product_id, mls_todo.location_id | mls_todo.location_dest_id,
            extra_domain=['|', ('lot_id', 'in', mls_todo.lot_id.ids), ('lot_id', '=', False)])

        # Prepare package history records before any actual move
        if not self.env.context.get('ignore_dest_packages'):
            package_history_vals = mls_todo._prepare_package_history_vals()
            if package_history_vals:
                self.env['stock.package.history'].create(package_history_vals)

        for ml in mls_todo.with_context(quants_cache=quants_cache):
            # if this move line is force assigned, unreserve elsewhere if needed
            ml._synchronize_quant(-ml.quantity_product_uom, ml.location_id, action="reserved")
            available_qty, in_date = ml._synchronize_quant(-ml.quantity_product_uom, ml.location_id)
            ml._synchronize_quant(ml.quantity_product_uom, ml.location_dest_id, package=ml.result_package_id, in_date=in_date)
            if available_qty < 0:
                ml.with_context(quants_cache=None)._free_reservation(
                    ml.product_id, ml.location_id,
                    abs(available_qty), lot_id=ml.lot_id, package_id=ml.package_id,
                    owner_id=ml.owner_id, ml_ids_to_ignore=ml_ids_to_ignore)
            ml_ids_to_ignore.add(ml.id)

        if not self.env.context.get('ignore_dest_packages'):
            mls_todo.result_package_id._apply_dest_to_package()

        # Reset the reserved quantity as we just moved it to the destination location.
        mls_todo.write({
            'date': fields.Datetime.now(),
        })

    def _synchronize_quant(self, quantity, location, action="available", in_date=False, **quants_value):
        """ quantity should be express in product's UoM"""
        lot = quants_value.get('lot', self.lot_id)
        package = quants_value.get('package', self.package_id)
        owner = quants_value.get('owner', self.owner_id)
        available_qty = 0
        if not self.product_id.is_storable or self.product_uom_id.is_zero(quantity):
            return 0, False
        if action == "available":
            available_qty, in_date = self.env['stock.quant']._update_available_quantity(self.product_id, location, quantity, lot_id=lot, package_id=package, owner_id=owner, in_date=in_date)
        elif action == "reserved" and not self.move_id._should_bypass_reservation(location):
            self.env['stock.quant']._update_reserved_quantity(self.product_id, location, quantity, lot_id=lot, package_id=package, owner_id=owner)
        if available_qty < 0 and lot:
            # see if we can compensate the negative quants with some untracked quants
            untracked_qty = self.env['stock.quant']._get_available_quantity(self.product_id, location, lot_id=False, package_id=package, owner_id=owner, strict=True)
            if not untracked_qty:
                return available_qty, in_date
            taken_from_untracked_qty = min(untracked_qty, abs(quantity))
            self.env['stock.quant']._update_available_quantity(self.product_id, location, -taken_from_untracked_qty, lot_id=False, package_id=package, owner_id=owner, in_date=in_date)
            self.env['stock.quant']._update_available_quantity(self.product_id, location, taken_from_untracked_qty, lot_id=lot, package_id=package, owner_id=owner, in_date=in_date)
        return available_qty, in_date

    def _get_similar_move_lines(self):
        self.ensure_one()
        lines = self.env['stock.move.line']
        picking_id = self.move_id.picking_id if self.move_id else self.picking_id
        if picking_id:
            lines |= picking_id.move_line_ids.filtered(lambda ml: ml.product_id == self.product_id and (ml.lot_id or ml.lot_name))
        return lines

    def _prepare_new_lot_vals(self):
        self.ensure_one()
        vals =  {
            'name': self.lot_name,
            'product_id': self.product_id.id,
        }
        if self.product_id.company_id and self.company_id in (self.product_id.company_id.all_child_ids | self.product_id.company_id):
            vals['company_id'] = self.company_id.id
        return vals

    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        # It is possible to have multiple time the same lot to create & assign,
        # so we handle the case with 2 dictionaries.
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
        for ml in self:
            key = (ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append(ml._prepare_new_lot_vals())

        lots = self.env['stock.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            lot = lots[key_to_index[key]].with_prefetch(lots._ids)   # With prefetch to reconstruct the ones broke by accessing by index
            mls.with_prefetch(self._prefetch_ids).write({'lot_id': lot.id})

    def _log_message(self, record, move, template, vals):
        data = vals.copy()
        if 'lot_id' in vals and vals['lot_id'] != move.lot_id.id:
            data['lot_name'] = self.env['stock.lot'].browse(vals.get('lot_id')).name
        if 'location_id' in vals:
            data['location_name'] = self.env['stock.location'].browse(vals.get('location_id')).name
        if 'location_dest_id' in vals:
            data['location_dest_name'] = self.env['stock.location'].browse(vals.get('location_dest_id')).name
        if 'package_id' in vals and vals['package_id'] != move.package_id.id:
            data['package_name'] = self.env['stock.package'].browse(vals.get('package_id')).name
        if 'package_result_id' in vals and vals['package_result_id'] != move.package_result_id.id:
            data['result_package_dest_name'] = self.env['stock.package'].browse(vals.get('result_package_id')).name
        if 'owner_id' in vals and vals['owner_id'] != move.owner_id.id:
            data['owner_name'] = self.env['res.partner'].browse(vals.get('owner_id')).name
        record.message_post_with_source(
            template,
            render_values={'move': move, 'vals': dict(vals, **data)},
            subtype_xmlid='mail.mt_note',
        )

    def _free_reservation(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, ml_ids_to_ignore=None):
        """ When editing a done move line or validating one with some forced quantities, it is
        possible to impact quants that were not reserved. It is therefore necessary to edit or
        unlink the move lines that reserved a quantity now unavailable.

        :param ml_ids_to_ignore: OrderedSet of `stock.move.line` ids that should NOT be unreserved
        """
        self.ensure_one()
        if ml_ids_to_ignore is None:
            ml_ids_to_ignore = OrderedSet()
        ml_ids_to_ignore |= self.ids

        if self.move_id._should_bypass_reservation(location_id):
            return

        # We now have to find the move lines that reserved our now unavailable quantity. We
        # take care to exclude ourselves and the move lines were work had already been done.
        outdated_move_lines_domain = [
            ('state', 'not in', ['done', 'cancel']),
            ('product_id', '=', product_id.id),
            ('lot_id', '=', lot_id.id if lot_id else False),
            ('location_id', '=', location_id.id),
            ('owner_id', '=', owner_id.id if owner_id else False),
            ('package_id', '=', package_id.id if package_id else False),
            ('quantity_product_uom', '>', 0.0),
            ('picked', '=', False),
            ('id', 'not in', tuple(ml_ids_to_ignore)),
        ]

        # We take the current picking first, then the pickings with the latest scheduled date
        def current_picking_first(cand):
            return (
                cand.picking_id != self.move_id.picking_id,
                -(cand.picking_id.scheduled_date or cand.move_id.date).timestamp()
                if cand.picking_id or cand.move_id else 0,
                -cand.id)

        outdated_candidates = self.env['stock.move.line'].search(outdated_move_lines_domain).sorted(current_picking_first)

        # As the move's state is not computed over the move lines, we'll have to manually
        # recompute the moves which we adapted their lines.
        move_to_reassign = self.env['stock.move']
        to_unlink_candidate_ids = set()

        for candidate in outdated_candidates:
            move_to_reassign |= candidate.move_id
            if self.product_uom_id.compare(candidate.quantity_product_uom, quantity) <= 0:
                quantity -= candidate.quantity_product_uom
                to_unlink_candidate_ids.add(candidate.id)
                if self.product_uom_id.is_zero(quantity):
                    break
            else:
                candidate.quantity -= candidate.product_id.uom_id._compute_quantity(quantity, candidate.product_uom_id, rounding_method='HALF-UP')
                break

        move_line_to_unlink = self.env['stock.move.line'].browse(to_unlink_candidate_ids)
        for m in (move_line_to_unlink.move_id | move_to_reassign):
            m.write({
                'procure_method': 'make_to_stock',
                'move_orig_ids': [Command.clear()]
            })
        move_line_to_unlink.unlink()
        move_to_reassign._action_assign()

    def _get_aggregated_properties(self, move_line=False, move=False):
        move = move or move_line.move_id
        uom = move.product_uom or move_line.product_uom_id
        packaging_uom = move.packaging_uom_id
        name = move.product_id.display_name
        description = move.description_picking or ""
        product = move.product_id
        if description.startswith(name):
            description = description.removeprefix(name).strip()
        elif description.startswith(product.name):
            description = description.removeprefix(product.name).strip()
        line_key = f'{product.id}_{product.display_name}_{description or ""}_{uom.id}_{packaging_uom.id}'
        properties = {
            'line_key': line_key,
            'name': name,
            'description': description,
            'product_uom': uom,
            'packaging_uom_id': packaging_uom,
            'move': move,
        }
        if move_line and move_line.result_package_id:
            properties['package'] = move_line.result_package_id
            properties['package_history'] = move_line.package_history_id
            properties['line_key'] += f'_{move_line.result_package_id.id}'
        return properties

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products (key = id+name+description+uom) and corresponding values of interest.

        Allows aggregation of data across separate move lines for the same product. This is expected to be useful
        in things such as delivery reports. Dict key is made as a combination of values we expect to want to group
        the products by (i.e. so data is not lost). This function purposely ignores lots/SNs because these are
        expected to already be properly grouped by line.

        returns: dictionary {product_id+name+description+uom: {product, name, description, quantity, product_uom}, ...}
        """
        aggregated_move_lines = {}

        # Loops to get backorders, backorders' backorders, and so and so...
        backorders = self.env['stock.picking']
        pickings = self.picking_id
        while pickings.backorder_ids:
            backorders |= pickings.backorder_ids
            pickings = pickings.backorder_ids

        for move_line in self:
            if kwargs.get('except_package') and move_line.result_package_id:
                continue
            aggregated_properties = self._get_aggregated_properties(move_line=move_line)
            line_key, uom = aggregated_properties['line_key'], aggregated_properties['product_uom']
            quantity = move_line.product_uom_id._compute_quantity(move_line.quantity, uom)
            packaging_quantity = move_line.product_uom_id._compute_quantity(quantity, move_line.move_id.packaging_uom_id)
            if line_key not in aggregated_move_lines:
                qty_ordered = None
                packaging_qty_ordered = None
                if backorders and not kwargs.get('strict'):
                    qty_ordered = move_line.move_id.product_uom_qty
                    # Filters on the aggregation key (product, description and uom) to add the
                    # quantities delayed to backorders to retrieve the original ordered qty.
                    following_move_lines = backorders.move_line_ids.filtered(
                        lambda ml: line_key.startswith(self._get_aggregated_properties(move=ml.move_id)['line_key'])
                    )
                    qty_ordered += sum(following_move_lines.move_id.mapped('product_uom_qty'))
                    # Remove the done quantities of the other move lines of the stock move
                    previous_move_lines = move_line.move_id.move_line_ids.filtered(
                        lambda ml: line_key.startswith(self._get_aggregated_properties(move=ml.move_id)['line_key']) and ml.id != move_line.id
                    )
                    qty_ordered -= sum([m.product_uom_id._compute_quantity(m.quantity, uom) for m in previous_move_lines])
                    packaging_qty_ordered = move_line.product_uom_id._compute_quantity(qty_ordered, move_line.move_id.packaging_uom_id)
                aggregated_move_lines[line_key] = {
                    **aggregated_properties,
                    'quantity': quantity,
                    'packaging_quantity': packaging_quantity,
                    'qty_ordered': qty_ordered or quantity,
                    'packaging_qty_ordered': packaging_qty_ordered or packaging_quantity,
                    'product': move_line.product_id,
                }
            else:
                aggregated_move_lines[line_key]['qty_ordered'] += quantity
                aggregated_move_lines[line_key]['packaging_qty_ordered'] += packaging_quantity
                aggregated_move_lines[line_key]['quantity'] += quantity
                aggregated_move_lines[line_key]['packaging_quantity'] += packaging_quantity

        # Does the same for empty move line to retrieve the ordered qty. for partially done moves
        # (as they are splitted when the transfer is done and empty moves don't have move lines).
        if kwargs.get('strict'):
            return aggregated_move_lines
        pickings = (self.picking_id | backorders)
        for empty_move in pickings.move_ids:
            to_bypass = False
            if not (empty_move.product_uom_qty and empty_move.product_uom.is_zero(empty_move.quantity)):
                continue
            if empty_move.state != "cancel":
                if empty_move.state != "confirmed" or empty_move.move_line_ids:
                    continue
                else:
                    to_bypass = True
            aggregated_properties = self._get_aggregated_properties(move=empty_move)
            line_key = aggregated_properties['line_key']

            if not any(aggregated_key.startswith(line_key) for aggregated_key in aggregated_move_lines) and not to_bypass:
                qty_ordered = empty_move.product_uom_qty
                aggregated_move_lines[line_key] = {
                    **aggregated_properties,
                    'quantity': False,
                    'packaging_quantity': 0,
                    'packaging_qty_ordered': 0,
                    'qty_ordered': qty_ordered,
                    'product': empty_move.product_id,
                }
            elif line_key in aggregated_move_lines:
                aggregated_move_lines[line_key]['qty_ordered'] += empty_move.product_uom_qty
            else:
                keys = list(filter(lambda key: key.startswith(line_key), aggregated_move_lines))
                if keys:
                    aggregated_move_lines[keys[0]]['qty_ordered'] += empty_move.product_uom_qty

        return aggregated_move_lines

    def _compute_sale_price(self):
        # To Override
        pass

    def _prepare_package_history_vals(self):
        history_vals = []
        packages = self.env['stock.package'].browse(self.result_package_id._get_all_package_dest_ids())
        for package in packages:
            history_vals.append({
                'location_id': package.location_id.id,
                'location_dest_id': package.location_dest_id.id,
                'move_line_ids': [Command.set(package.move_line_ids.filtered(lambda ml: ml.result_package_id == package).ids)],
                'picking_ids': [Command.set(package.picking_ids.ids)],
                'package_id': package.id,
                'package_name': package.complete_name,
                'parent_orig_id': package.parent_package_id.id,
                'parent_orig_name': package.parent_package_id.complete_name,
                'parent_dest_id': package.package_dest_id.id,
                'parent_dest_name': package.package_dest_id.dest_complete_name,
                'outermost_dest_id': package.outermost_package_id.id,
            })

        return history_vals

    @api.model
    def _prepare_stock_move_vals(self):
        self.ensure_one()
        return {
            'product_id': self.product_id.id,
            'product_uom_qty': 0 if self.picking_id and self.picking_id.state != 'done' else self.quantity,
            'product_uom': self.product_uom_id.id,
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': self.picking_id.location_dest_id.id,
            'picked': self.picked,
            'picking_id': self.picking_id.id,
            'state': self.picking_id.state,
            'picking_type_id': self.picking_id.picking_type_id.id,
            'restrict_partner_id': self.picking_id.owner_id.id,
            'company_id': self.picking_id.company_id.id,
            'partner_id': self.picking_id.partner_id.id,
        }

    def _copy_quant_info(self, vals):
        quant = self.env['stock.quant'].browse(vals.get('quant_id', 0))
        line_data = {
            'product_id': quant.product_id.id,
            'lot_id': quant.lot_id.id,
            'package_id': quant.package_id.id,
            'location_id': quant.location_id.id,
            'owner_id': quant.owner_id.id,
        }
        return line_data

    def action_open_reference(self):
        self.ensure_one()
        if self.move_id:
            action = self.move_id.action_open_reference()
            if action['res_model'] != 'stock.move':
                return action
        return {
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [[False, "form"]],
            'res_id': self.id,
        }

    def _pre_put_in_pack_hook(self, all_lines=False, package_id=False, package_type_id=False, package_name=False, from_package_wizard=False):
        move_lines = all_lines if self.env.context.get('force_move_lines') and all_lines else self
        action = move_lines._check_destinations()
        if action:
            return action
        if self._should_display_put_in_pack_wizard(package_id, package_type_id, package_name, from_package_wizard):
            action = self.env["ir.actions.actions"]._for_xml_id("stock.action_put_in_pack_wizard")
            action['context'] = {
                **literal_eval(action.get('context', '{}')),
                'all_move_line_ids': move_lines.ids,
                'default_move_line_ids': self.ids,
                'default_location_dest_id': self.location_dest_id.id,
                'picking_ids': move_lines.picking_id.ids,
            }
            return action

    def _check_destinations(self):
        if len(self.location_dest_id) > 1:
            view_id = self.env.ref('stock.stock_package_destination_form_view').id
            wiz = self.env['stock.package.destination'].create({
                'move_line_ids': self.ids,
                'location_dest_id': self[0].location_dest_id.id,
            })
            return {
                'name': _('Choose destination location'),
                'view_mode': 'form',
                'res_model': 'stock.package.destination',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'type': 'ir.actions.act_window',
                'res_id': wiz.id,
                'target': 'new'
            }

    def _get_lines_not_entire_pack(self):
        """ Checks within self for move lines that should no longer be considered as entire packs.
        """
        relevant_move_lines = self.filtered(lambda ml: ml.is_entire_pack)
        if not relevant_move_lines:
            return False

        # If `result_package_id` was either removed or changed, cannot be considered as an entire pack anymore.
        ids_to_update = set(relevant_move_lines.filtered(lambda ml: ml.package_id != ml.result_package_id).ids)
        for package, move_lines in relevant_move_lines.grouped('package_id').items():
            pickings = move_lines.picking_id
            if not pickings._is_single_transfer() or not pickings._check_move_lines_map_quant_package(package):
                ids_to_update.update(pickings.move_line_ids.filtered(lambda ml: ml.package_id == package).ids)

        return self.env['stock.move.line'].browse(ids_to_update)

    def _put_in_pack(self, package_id=False, package_type_id=False, package_name=False):
        if package_id:
            package = self.env['stock.package'].browse(package_id)
        elif package_type_id:
            package = self.env['stock.package'].create({
                'name': package_name,
                'package_type_id': package_type_id,
            })
        else:
            package_vals = {'name': package_name}
            package_type = self.move_id.packaging_uom_id.package_type_id
            if len(package_type) == 1:
                package_vals['package_type_id'] = package_type.id
            package = self.env['stock.package'].create(package_vals)
        if len(self) == 1:
            default_dest_location = self._get_default_dest_location()
            self.location_dest_id = default_dest_location._get_putaway_strategy(
                product=self.product_id,
                quantity=self.quantity,
                package=package
            )
        self.write({'result_package_id': package.id})
        return package

    def _post_put_in_pack_hook(self, package):
        if package and self.picking_type_id.auto_print_package_label:
            if self.picking_type_id.package_label_to_print == 'pdf':
                action = self.env.ref("stock.action_report_package_barcode_small").report_action(package.id, config=False)
            elif self.picking_type_id.package_label_to_print == 'zpl':
                action = self.env.ref("stock.label_package_template").report_action(package.id, config=False)
            if action:
                action.update({'close_on_report_download': True})
                clean_action(action, self.env)
                return action
        return package

    def action_put_in_pack(self, *, package_id=False, package_type_id=False, package_name=False):
        move_lines = self
        if self.env.context.get('all_move_line_ids'):
            move_lines = self.env['stock.move.line'].browse(self.env.context['all_move_line_ids'])
        # From the 'Moves' button, we want to take all move lines, without caring for picked or with/without packages.
        force_move_lines = bool(self.env.context.get('force_move_lines'))

        move_lines_to_pack, packages_to_pack = move_lines._get_lines_and_packages_to_pack(picked_first=not force_move_lines)
        done_pack = False
        if move_lines_to_pack:
            action = move_lines_to_pack._pre_put_in_pack_hook(move_lines, package_id, package_type_id, package_name, self.env.context.get('from_package_wizard'))
            if action:
                return action

            package = move_lines_to_pack._put_in_pack(package_id, package_type_id, package_name)
            done_pack = move_lines_to_pack._post_put_in_pack_hook(package)
        if done_pack and not force_move_lines:
            return done_pack
        elif packages_to_pack:
            if done_pack:
                packages_to_pack -= done_pack
                package_id = done_pack.id
            if packages_to_pack:
                return packages_to_pack.action_put_in_pack(package_id=package_id, package_type_id=package_type_id, package_name=package_name)

    def _get_lines_and_packages_to_pack(self, picked_first=True):
        """ Get all move lines & packages that need to be put in a pack.

            :param picked_first: If enabled, will prioritize picked move lines over other move lines.
            :return: move_lines_to_pack: All move lines without a pack that can be packed
            :return: packages_to_pack: All packages that can be packed
        """
        if len(self.picking_type_id) > 1:
            raise UserError(_('You cannot pack products into the same package when they are from different transfers with different operation types'))

        quantity_move_lines = self.filtered(lambda ml: ml.state not in ('done', 'cancel') and ml.product_uom_id.compare(ml.quantity, 0.0) > 0)
        if picked_first:
            picked_move_lines = quantity_move_lines.filtered(lambda ml: ml.picked)
            if picked_move_lines:
                # As long as at least a single move line is picked, we ignore the unpicked ones.
                quantity_move_lines = picked_move_lines

        move_lines_to_pack = quantity_move_lines.filtered(lambda ml: not ml.result_package_id)
        packages_to_pack = (quantity_move_lines - move_lines_to_pack).result_package_id.outermost_package_id

        return move_lines_to_pack, packages_to_pack

    def _get_revert_inventory_move_values(self):
        self.ensure_one()
        return {
            'inventory_name': _('%s [reverted]', self.reference),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.quantity,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': self.location_dest_id.id,
            'location_dest_id': self.location_id.id,
            'is_inventory': True,
            'picked': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'quantity': self.quantity,
                'location_id': self.location_dest_id.id,
                'location_dest_id': self.location_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.lot_id.id,
                'package_id': self.package_id.id,
                'result_package_id': self.package_id.id,
                'owner_id': self.owner_id.id,
            })]
        }

    def action_revert_inventory(self):
        move_vals = []
        # remove inventory mode
        self = self.with_context(inventory_mode=False)
        processed_move_line = self.env['stock.move.line']
        for move_line in self:
            if move_line.is_inventory and not move_line.product_uom_id.is_zero(move_line.quantity):
                processed_move_line += move_line
                move_vals.append(move_line._get_revert_inventory_move_values())
        if not processed_move_line:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'message': _("There are no inventory adjustments to revert."),
                }
            }
        moves = self.env['stock.move'].create(move_vals)
        moves._action_done()
        return {
            'name': _('Reverted Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line',
            'view_mode': 'list',
            'domain': [('id', 'in', moves.move_line_ids.ids + self.ids)]
        }

    def _get_linkable_moves(self):
        self.ensure_one()
        moves = self.picking_id.move_ids.filtered(lambda x: x.product_id == self.product_id)
        return sorted(moves, key=lambda m: m.quantity < m.product_qty, reverse=True)

    def _should_display_put_in_pack_wizard(self, package_id, package_type_id, package_name, from_package_wizard):
        define_package_type = self._should_set_package()
        return define_package_type and not from_package_wizard and (not package_id and not package_type_id and not package_name)

    def _should_set_package(self):
        package_type = self.picking_id.picking_type_id
        return len(package_type) == 1 and package_type.set_package_type


# FILEPATH: odoo/addons/stock/models/stock_orderpoint.py
_logger = logging.getLogger(__name__)
class StockWarehouseOrderpoint(models.Model):
    """ Defines Minimum stock rules. """
    _name = 'stock.warehouse.orderpoint'
    _description = "Minimum Inventory Rule"
    _check_company_auto = True
    _order = "location_id,company_id,id"

    name = fields.Char(
        'Name', copy=False, required=True, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.orderpoint'))
    trigger = fields.Selection([
        ('auto', 'Auto'), ('manual', 'Manual')], string='Trigger', default='auto', required=True)
    active = fields.Boolean(
        'Active', default=True,
        help="If the active field is set to False, it will allow you to hide the orderpoint without removing it.")
    snoozed_until = fields.Date('Snoozed', help="Hidden until next scheduler.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse',
        compute="_compute_warehouse_id", store=True, readonly=False, precompute=True,
        check_company=True, ondelete="cascade", required=True, index=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', index=True,
        compute="_compute_location_id", store=True, readonly=False, precompute=True,
        ondelete="cascade", required=True, check_company=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id')
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=("[('product_tmpl_id', '=', context.get('active_id', False))] if context.get('active_model') == 'product.template' else"
            " [('id', '=', context.get('default_product_id', False))] if context.get('default_product_id') else"
            " [('is_storable', '=', True)]"),
        ondelete='cascade', required=True, check_company=True, index=True)
    product_category_id = fields.Many2one('product.category', name='Product Category', related='product_id.categ_id')
    product_uom = fields.Many2one(
        'uom.uom', 'Unit', related='product_id.uom_id')
    product_uom_name = fields.Char(string='Product unit of measure label', related='product_uom.display_name', readonly=True)
    product_min_qty = fields.Float(
        'Min Quantity', digits='Product Unit', required=True, default=0.0,
        help="The minimum Stock level that will trigger a replenishment.")
    product_max_qty = fields.Float(
        'Max Quantity', digits='Product Unit', required=True, default=0.0,
        compute='_compute_product_max_qty', readonly=False, store=True,
        help="Stock level to reach when replenishing.")
    allowed_replenishment_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_replenishment_uom_ids')
    replenishment_uom_id = fields.Many2one(
        'uom.uom', 'Multiple',
        domain="[('id', 'in', allowed_replenishment_uom_ids)]", help="The procurement quantity will be rounded up to a multiple of this unit/packaging. If it is not set, it is not rounded.")
    replenishment_uom_id_placeholder = fields.Char(compute='_compute_replenishment_uom_id_placeholder')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True,
        default=lambda self: self.env.company)
    allowed_location_ids = fields.One2many(comodel_name='stock.location', compute='_compute_allowed_location_ids')

    rule_ids = fields.Many2many('stock.rule', string='Rules used', compute='_compute_rules')
    lead_horizon_date = fields.Date(compute='_compute_lead_days')
    lead_days = fields.Float(compute='_compute_lead_days')
    route_id = fields.Many2one(
        'stock.route', string='Route',
        domain="['|', ('product_selectable', '=', True), ('rule_ids.action', 'in', ['buy', 'manufacture'])]",
        inverse='_inverse_route_id')
    route_id_placeholder = fields.Char(compute='_compute_route_id_placeholder')
    effective_route_id = fields.Many2one(
        'stock.route', search='_search_effective_route_id', compute='_compute_effective_route_id',
        store=False, help='Either the route set directly or the one computed to be used by this replenishment'
    )
    qty_on_hand = fields.Float('On Hand', readonly=True, compute='_compute_qty', digits='Product Unit')
    qty_forecast = fields.Float('Forecast', readonly=True, compute='_compute_qty', digits='Product Unit')
    qty_to_order = fields.Float('To Order', compute='_compute_qty_to_order', inverse='_inverse_qty_to_order', search='_search_qty_to_order', digits='Product Unit')
    qty_to_order_computed = fields.Float('To Order Computed', store=True, compute='_compute_qty_to_order_computed', digits='Product Unit')
    qty_to_order_manual = fields.Float('To Order Manual', digits='Product Unit')

    days_to_order = fields.Float(compute='_compute_days_to_order', help="Numbers of days  in advance that replenishments demands are created.")

    unwanted_replenish = fields.Boolean('Unwanted Replenish', compute="_compute_unwanted_replenish")
    show_supply_warning = fields.Boolean(compute="_compute_show_supply_warning")
    deadline_date = fields.Date("Deadline", compute="_compute_deadline_date", store=True, readonly=True,
                                help="Date before which you should order to avoid falling below the minimum. If you "
                                     "have nothing to order while a deadline is found, it may be because a future "
                                     "arrival is expected after the minimum quantity is reached (potential stockout). "
                                     "Check the Forecast Report.")

    _product_location_check = models.Constraint(
        'unique (product_id, location_id, company_id)',
        'A replenishment rule already exists for this product on this location.',
    )

    @api.depends('warehouse_id')
    def _compute_allowed_location_ids(self):
        # We want to keep only the locations
        #  - strictly belonging to our warehouse
        #  - not belonging to any warehouses
        for orderpoint in self:
            loc_domain = Domain('usage', 'in', ('internal', 'view'))
            other_warehouses = self.env['stock.warehouse'].search([('id', '!=', orderpoint.warehouse_id.id)])
            for view_location_id in other_warehouses.mapped('view_location_id'):
                loc_domain &= ~Domain('id', 'child_of', view_location_id.id)
                loc_domain &= Domain('company_id', 'in', [False, orderpoint.company_id.id])
            orderpoint.allowed_location_ids = self.env['stock.location'].search(loc_domain)

    def _compute_show_supply_warning(self):
        for orderpoint in self:
            orderpoint.show_supply_warning = not orderpoint.rule_ids

    @api.depends('location_id', 'product_min_qty', 'route_id', 'product_id.route_ids', 'product_id.stock_move_ids.date',
                 'product_id.stock_move_ids.state', 'product_id.seller_ids', 'product_id.seller_ids.delay', 'company_id.horizon_days')
    def _compute_deadline_date(self):
        """ This function first checks if the qty_on_hand is less than the product_min_qty. If it is the case,
        the deadline_date is set to the current day. Afterwards if there are still orderpoints to compute,
        it retrieves all the outgoing and incoming moves until the lead_horizon_date and adds (or subtracts)
        them to the qty_on_hand. The first instance when the qty_on_hand dips below the product_min_qty is
        the deadline date. """
        self.fetch(['qty_on_hand'])
        critical_orderpoints = self.filtered(lambda o: o.qty_on_hand < o.product_min_qty)
        critical_orderpoints.deadline_date = fields.Date.today()
        orderpoints_to_compute = self - critical_orderpoints
        if not orderpoints_to_compute:
            return

        # We have to filter by company here in case of multi-company and because horizon_days is a company setting
        for company in orderpoints_to_compute.company_id:
            company_orderpoints = orderpoints_to_compute.filtered(lambda c: c.company_id == company)
            horizon_date = fields.Date.today() + relativedelta.relativedelta(days=company_orderpoints.get_horizon_days())
            _, domain_move_in, domain_move_out = company_orderpoints.product_id._get_domain_locations()
            domain_move_in = Domain.AND([
                [('product_id', 'in', company_orderpoints.product_id.ids)],
                [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))],
                domain_move_in,
                [('date', '<=', horizon_date)],
            ])
            domain_move_out = Domain.AND([
                [('product_id', '=', company_orderpoints.product_id.ids)],
                [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))],
                domain_move_out,
                [('date', '<=', horizon_date)],
            ])

            Move = self.env['stock.move'].with_context(active_test=False)
            incoming_moves_by_product_date = Move._read_group(domain_move_in, ['product_id', 'location_dest_id', 'date:day'], ['product_qty:sum'])
            outgoing_moves_by_product_date = Move._read_group(domain_move_out, ['product_id', 'location_id', 'date:day'], ['product_qty:sum'])

            moves_by_product_dict = {}
            for product, location, in_date, in_qty in incoming_moves_by_product_date:
                if not moves_by_product_dict.get((product.id, location.id)):
                    moves_by_product_dict[product.id, location.id] = defaultdict(float)
                moves_by_product_dict[product.id, location.id][in_date.date()] += in_qty
            for product, location, out_date, out_qty in outgoing_moves_by_product_date:
                if not moves_by_product_dict.get((product.id, location.id)):
                    moves_by_product_dict[product.id, location.id] = defaultdict(float)
                moves_by_product_dict[product.id, location.id][out_date.date()] -= out_qty

            for orderpoint in company_orderpoints:
                qty_on_hand_at_date = orderpoint.qty_on_hand
                tentative_deadline = horizon_date
                for move_date, move_qty in sorted(moves_by_product_dict.get((orderpoint.product_id.id, orderpoint.location_id.id), {}).items()):
                    qty_on_hand_at_date += move_qty
                    if qty_on_hand_at_date < orderpoint.product_min_qty:
                        tentative_deadline = move_date - relativedelta.relativedelta(days=orderpoint.lead_days)
                        break
                orderpoint.deadline_date = tentative_deadline if tentative_deadline < horizon_date else False

    @api.depends('rule_ids', 'product_id.seller_ids', 'product_id.seller_ids.delay', 'company_id.horizon_days')
    def _compute_lead_days(self):
        orderpoints_to_compute = self.filtered(lambda orderpoint: orderpoint.product_id and orderpoint.location_id)
        for orderpoint in orderpoints_to_compute.with_context(bypass_delay_description=True):
            values = orderpoint._get_lead_days_values()
            lead_days, dummy = orderpoint.rule_ids._get_lead_days(orderpoint.product_id, **values)
            orderpoint.lead_horizon_date = fields.Date.today() + relativedelta.relativedelta(days=lead_days['total_delay'] + lead_days['horizon_time'])
            orderpoint.lead_days = lead_days['total_delay']
        (self - orderpoints_to_compute).lead_horizon_date = False
        (self - orderpoints_to_compute).lead_days = 0

    @api.depends('route_id', 'product_id', 'location_id', 'company_id', 'warehouse_id', 'product_id.route_ids')
    def _compute_rules(self):
        orderpoints_to_compute = self.filtered(lambda orderpoint: orderpoint.product_id and orderpoint.location_id)
        # Small cache mapping (location_id, route_id, {all product routes}) -> stock.rule.
        # This reduces calls to _get_rules_from_location for products without routes and products with the same routes.
        rules_cache = {}
        for orderpoint in orderpoints_to_compute:
            all_product_routes = orderpoint.product_id.route_ids | orderpoint.product_id.categ_id.total_route_ids | orderpoint.product_id.get_total_routes()
            cache_key = (orderpoint.location_id, orderpoint.route_id, all_product_routes)
            rule_ids = rules_cache.get(cache_key) or orderpoint.product_id._get_rules_from_location(
                orderpoint.location_id, route_ids=orderpoint.route_id
            )
            orderpoint.rule_ids = rule_ids
            rules_cache[cache_key] = rule_ids
        (self - orderpoints_to_compute).rule_ids = False

    @api.depends('product_min_qty')
    def _compute_product_max_qty(self):
        for orderpoint in self:
            if orderpoint.product_max_qty < orderpoint.product_min_qty or not orderpoint.product_max_qty:
                orderpoint.product_max_qty = orderpoint.product_min_qty

    @api.depends('route_id', 'product_id', 'product_id.seller_ids', 'product_id.seller_ids.product_uom_id')
    def _compute_allowed_replenishment_uom_ids(self):
        for orderpoint in self:
            orderpoint.allowed_replenishment_uom_ids = orderpoint.product_id.uom_ids
            if 'buy' in orderpoint.rule_ids.mapped('action'):
                orderpoint.allowed_replenishment_uom_ids += orderpoint.product_id.seller_ids.product_uom_id

    @api.depends('allowed_replenishment_uom_ids')
    def _compute_replenishment_uom_id_placeholder(self):
        for orderpoint in self:
            replenishment_alternative = orderpoint._get_replenishment_multiple_alternative(orderpoint.qty_to_order)
            orderpoint.replenishment_uom_id_placeholder = replenishment_alternative.display_name if replenishment_alternative else ''

    def _inverse_route_id(self):
        # Override this method to add custom behavior when route is set
        pass

    @api.depends('product_id', 'product_id.categ_id', 'product_id.route_ids', 'product_id.categ_id.route_ids', 'location_id')
    def _compute_route_id_placeholder(self):
        for orderpoint in self:
            default_route = orderpoint._get_default_route()
            orderpoint.route_id_placeholder = default_route.display_name if default_route else ''

    @api.depends('route_id', 'product_id', 'product_id.categ_id', 'product_id.route_ids', 'product_id.categ_id.route_ids', 'location_id')
    def _compute_effective_route_id(self):
        for orderpoint in self:
            orderpoint.effective_route_id = orderpoint.route_id if orderpoint.route_id else orderpoint._get_default_route()

    def _search_effective_route_id(self, operator, value):
        routes = self.env['stock.route'].search([('id', operator, value)])
        orderpoints = self.env['stock.warehouse.orderpoint'].search([]).filtered(
            lambda orderpoint: orderpoint.effective_route_id in routes
        )
        return [('id', 'in', orderpoints.ids)]

    @api.depends('route_id', 'product_id')
    def _compute_days_to_order(self):
        self.days_to_order = 0

    @api.constrains('product_min_qty', 'product_max_qty')
    def _check_min_max_qty(self):
        if any(orderpoint.product_min_qty > orderpoint.product_max_qty for orderpoint in self):
            raise ValidationError(_('The minimum quantity must be less than or equal to the maximum quantity.'))

    @api.depends('location_id', 'company_id')
    def _compute_warehouse_id(self):
        for orderpoint in self:
            if orderpoint.location_id.warehouse_id:
                orderpoint.warehouse_id = orderpoint.location_id.warehouse_id
            elif orderpoint.company_id:
                orderpoint.warehouse_id = orderpoint.env['stock.warehouse'].search([
                    ('company_id', '=', orderpoint.company_id.id)
                ], limit=1)
            if not orderpoint.warehouse_id:
                self.env['stock.warehouse']._warehouse_redirect_warning()

    @api.depends('warehouse_id', 'company_id')
    def _compute_location_id(self):
        """ Finds location id for changed warehouse. """
        for orderpoint in self:
            warehouse = orderpoint.warehouse_id
            if not warehouse:
                warehouse = orderpoint.env['stock.warehouse'].search([
                    ('company_id', '=', orderpoint.company_id.id)
                ], limit=1)
            orderpoint.location_id = warehouse.lot_stock_id.id

    @api.depends('product_id', 'qty_to_order', 'product_max_qty')
    def _compute_unwanted_replenish(self):
        for orderpoint in self:
            if not orderpoint.product_id or orderpoint.product_uom.is_zero(orderpoint.qty_to_order) or orderpoint.product_uom.compare(orderpoint.product_max_qty, 0) == -1:
                orderpoint.unwanted_replenish = False
            else:
                after_replenish_qty = orderpoint.product_id.with_context(company_id=orderpoint.company_id.id, location=orderpoint.location_id.id).virtual_available + orderpoint.qty_to_order
                orderpoint.unwanted_replenish = orderpoint.product_uom.compare(after_replenish_qty, orderpoint.product_max_qty) > 0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id

    @api.model_create_multi
    def create(self, vals_list):
        if any(val.get('snoozed_until', False) and val.get('trigger', self.default_get(['trigger'])['trigger']) == 'auto' for val in vals_list):
            raise UserError(_("You can not create a snoozed orderpoint that is not manually triggered."))
        return super().create(vals_list)

    def write(self, vals):
        if 'company_id' in vals:
            for orderpoint in self:
                if orderpoint.company_id.id != vals['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))
        if 'snoozed_until' in vals:
            if any(orderpoint.trigger == 'auto' for orderpoint in self):
                raise UserError(_("You can only snooze manual orderpoints. You should rather archive 'auto-trigger' orderpoints if you do not want them to be triggered."))
        return super().write(vals)

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'lead_horizon_date': format_date(self.env, self.lead_horizon_date),
            'qty_to_order': self._get_qty_to_order(),
        }
        warehouse = self.warehouse_id
        if warehouse:
            action['context']['warehouse_id'] = warehouse.id
        return action

    @api.model
    def action_open_orderpoints(self):
        return self._get_orderpoint_action()

    def action_stock_replenishment_info(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_stock_replenishment_info')
        action['name'] = _(
            'Replenishment Information for %(product)s in %(warehouse)s',
            product=self.product_id.display_name,
            warehouse=self.warehouse_id.display_name,
        )
        res = self.env['stock.replenishment.info'].create({
            'orderpoint_id': self.id,
        })
        action['res_id'] = res.id
        return action

    def action_replenish(self, force_to_max=False):
        now = self.env.cr.now()
        if force_to_max:
            for orderpoint in self:
                orderpoint.qty_to_order = orderpoint._get_multiple_rounded_qty(orderpoint.product_max_qty - orderpoint.qty_forecast)
        try:
            self._procure_orderpoint_confirm(company_id=self.env.company)
        except UserError as e:
            if len(self) != 1:
                raise e
            raise RedirectWarning(e, {
                'name': self.product_id.display_name,
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'views': [(self.env.ref('product.product_normal_form_view').id, 'form')],
            }, _('Edit Product'))
        notification = False
        if len(self) == 1:
            notification = self.with_context(written_after=now)._get_replenishment_order_notification()
        # Forced to call compute quantity because we don't have a link.
        self.action_remove_manual_qty_to_order()
        self._compute_qty_to_order()
        self.filtered(lambda o: o.create_uid.id == SUPERUSER_ID and o.qty_to_order <= 0.0 and o.trigger == 'manual').unlink()
        return notification

    def action_replenish_auto(self):
        self.trigger = 'auto'
        return self.action_replenish()

    @api.depends('product_id', 'location_id', 'product_id.stock_move_ids', 'product_id.stock_move_ids.state',
                 'product_id.stock_move_ids.date', 'product_id.stock_move_ids.product_uom_qty', 'product_id.seller_ids.delay')
    def _compute_qty(self):
        orderpoints_contexts = defaultdict(lambda: self.env['stock.warehouse.orderpoint'])
        for orderpoint in self:
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.qty_on_hand = False
                orderpoint.qty_forecast = False
                continue
            orderpoint_context = orderpoint._get_product_context()
            product_context = frozendict({**orderpoint_context})
            orderpoints_contexts[product_context] |= orderpoint
        for orderpoint_context, orderpoints_by_context in orderpoints_contexts.items():
            products_qty = {
                p['id']: p for p in orderpoints_by_context.product_id.with_context(orderpoint_context).read(['qty_available', 'virtual_available'])
            }
            products_qty_in_progress = orderpoints_by_context._quantity_in_progress()
            for orderpoint in orderpoints_by_context:
                orderpoint.qty_on_hand = products_qty[orderpoint.product_id.id]['qty_available']
                orderpoint.qty_forecast = products_qty[orderpoint.product_id.id]['virtual_available'] + products_qty_in_progress[orderpoint.id]

    @api.depends('qty_to_order_manual', 'qty_to_order_computed')
    def _compute_qty_to_order(self):
        for orderpoint in self:
            orderpoint.qty_to_order = orderpoint.qty_to_order_manual if orderpoint.qty_to_order_manual else orderpoint.qty_to_order_computed

    def _inverse_qty_to_order(self):
        for orderpoint in self:
            if orderpoint.trigger == 'auto':
                orderpoint.qty_to_order_manual = 0
            elif not orderpoint.qty_to_order_manual and not orderpoint.qty_to_order:
                orderpoint.qty_to_order = orderpoint.qty_to_order_computed
            elif orderpoint.qty_to_order != orderpoint.qty_to_order_computed:
                orderpoint.qty_to_order_manual = orderpoint.qty_to_order

    def _search_qty_to_order(self, operator, value):
        records = self.search_fetch([('qty_to_order_manual', 'in', [0, False])], ['qty_to_order_computed'])
        matched_ids = records.filtered_domain([('qty_to_order_computed', operator, value)]).ids
        return ['|',
                    '&', ('qty_to_order_manual', operator, value), ('qty_to_order_manual', 'not in', [0, False]),
                    ('id', 'in', matched_ids)
                ]

    @api.depends('replenishment_uom_id', 'product_min_qty', 'product_max_qty',
    'product_id', 'location_id', 'product_id.seller_ids.delay', 'company_id.horizon_days')
    def _compute_qty_to_order_computed(self):
        def to_compute(orderpoint):
            rounding = orderpoint.product_uom.rounding
            # The check is on purpose. We only want to consider the horizon days if the forecast is negative and
            # there is already something to resupply base on lead times.
            return (
                orderpoint.id
                and float_compare(orderpoint.qty_forecast, orderpoint.product_min_qty, precision_rounding=rounding) < 0
            )

        orderpoints = self.filtered(to_compute)
        qty_in_progress_by_orderpoint = orderpoints._quantity_in_progress()
        for orderpoint in orderpoints:
            orderpoint.qty_to_order_computed = orderpoint._get_qty_to_order(qty_in_progress_by_orderpoint=qty_in_progress_by_orderpoint)
        (self - orderpoints).qty_to_order_computed = False

    def _get_default_rule(self):
        self.ensure_one()
        return self.env['stock.rule']._get_rule(self.product_id, self.location_id, {
            'route_ids': self.route_id,
            'warehouse_id': self.warehouse_id,
        })

    def _get_default_route(self):
        self.ensure_one()
        rules_groups = self.env['stock.rule']._read_group([
            '|', ('route_id.product_selectable', '!=', False),
            ('route_id.product_categ_selectable', '!=', False),
            ('location_dest_id', 'in', self.location_id.ids),
            ('action', 'in', ['pull_push', 'pull']),
            ('route_id.active', '!=', False)
        ], ['location_dest_id', 'route_id'])
        for location_dest, route in rules_groups:
            if route in (self.product_id.route_ids | self.product_id.categ_id.route_ids) and self.location_id == location_dest:
                return route
        return self.env['stock.route']

    def _get_replenishment_multiple_alternative(self, qty_to_order):
        """
        This method is used to get the alternative replenishment_uom_id for the orderpoint if not set manually.
        To be overridden in relevant modules.
        """
        return False

    def _get_qty_to_order(self, qty_in_progress_by_orderpoint=None):
        self.ensure_one()
        qty_to_order = 0.0
        qty_in_progress_by_orderpoint = qty_in_progress_by_orderpoint or {}
        qty_in_progress = qty_in_progress_by_orderpoint.get(self.id)
        if qty_in_progress is None:
            qty_in_progress = self._quantity_in_progress()[self.id]
        rounding = self.product_uom.rounding
        # The check is on purpose. We only want to consider the horizon days if the forecast is negative and
        # there is already something to resupply base on lead times.
        if float_compare(self.qty_forecast, self.product_min_qty, precision_rounding=rounding) < 0:
            product_context = self._get_product_context()
            qty_forecast_with_visibility = self.product_id.with_context(product_context).read(['virtual_available'])[0]['virtual_available'] + qty_in_progress
            qty_to_order = max(self.product_min_qty, self.product_max_qty) - qty_forecast_with_visibility
            qty_to_order = self._get_multiple_rounded_qty(qty_to_order)
        return qty_to_order

    def _get_lead_days_values(self):
        self.ensure_one()
        return {
            'days_to_order': self.days_to_order,
        }

    def _get_product_context(self):
        """Used to call `virtual_available` when running an orderpoint."""
        self.ensure_one()
        return {
            'location': self.location_id.id,
            'to_date': datetime.combine(self.lead_horizon_date, time.max)
        }

    def _get_orderpoint_action(self):
        """Create manual orderpoints for missing product in each warehouses. It also removes
        orderpoints that have been replenish. In order to do it:
        - It uses the report.stock.quantity to find missing quantity per product/warehouse
        - It checks if orderpoint already exist to refill this location.
        - It checks if it exists other sources (e.g RFQ) tha refill the warehouse.
        - It creates the orderpoints for missing quantity that were not refill by an upper option.

        return replenish report ir.actions.act_window
        """
        def is_parent_path_in(resupply_loc, path_dict, record_loc):
            return record_loc and resupply_loc.parent_path in path_dict.get(record_loc, '')

        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_orderpoint_replenish")
        action['context'] = self.env.context
        # Search also with archived ones to avoid to trigger product_location_check SQL constraints later
        # It means that when there will be a archived orderpoint on a location + product, the replenishment
        # report won't take in account this location + product and it won't create any manual orderpoint
        # In master: the active field should be remove
        orderpoints = self.env['stock.warehouse.orderpoint'].with_context(active_test=False).search([])
        # Remove previous automatically created orderpoint that has been refilled.
        orderpoints_removed = orderpoints._unlink_processed_orderpoints()
        orderpoints = orderpoints - orderpoints_removed
        if self.env.context.get('force_orderpoint_recompute', False):
            orderpoints._compute_qty_to_order_computed()
            orderpoints._compute_deadline_date()
        to_refill = defaultdict(float)
        all_product_ids = self._get_orderpoint_products()
        all_replenish_location_ids = self._get_orderpoint_locations()
        ploc_per_day = defaultdict(set)
        # For each replenish location get products with negative virtual_available aka forecast

        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)
        domain_quant, domain_move_in_loc, domain_move_out_loc = all_product_ids._get_domain_locations_new(all_replenish_location_ids.ids)
        domain_state = Domain('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))
        domain_product = Domain('product_id', 'in', all_product_ids.ids)

        domain_quant = Domain.AND((domain_product, domain_quant))
        domain_move_in = Domain.AND((domain_product, domain_state, domain_move_in_loc))
        domain_move_out = Domain.AND((domain_product, domain_state, domain_move_out_loc))

        moves_in = defaultdict(list)
        for item in Move._read_group(domain_move_in, ['product_id', 'location_dest_id', 'location_final_id'], ['product_qty:sum']):
            moves_in[item[0]].append((item[1], item[2], item[3]))

        moves_out = defaultdict(list)
        for item in Move._read_group(domain_move_out, ['product_id', 'location_id'], ['product_qty:sum']):
            moves_out[item[0]].append((item[1], item[2]))

        quants = defaultdict(list)
        for item in Quant._read_group(domain_quant, ['product_id', 'location_id'], ['quantity:sum']):
            quants[item[0]].append((item[1], item[2]))

        path = {loc: loc.parent_path for loc in self.env['stock.location'].with_context(active_test=False).search([('id', 'child_of', all_replenish_location_ids.ids)])}
        for loc in all_replenish_location_ids:
            for product in all_product_ids:
                qty_available = sum(q[1] for q in quants.get(product, [(0, 0)]) if is_parent_path_in(loc, path, q[0]))
                incoming_qty = sum(m[2] for m in moves_in.get(product, [(0, 0, 0)]) if is_parent_path_in(loc, path, m[0]) or is_parent_path_in(loc, path, m[1]))
                outgoing_qty = sum(m[1] for m in moves_out.get(product, [(0, 0)]) if is_parent_path_in(loc, path, m[0]))
                if product.uom_id.compare(qty_available + incoming_qty - outgoing_qty, 0) < 0:
                    # group product by lead_days and location in order to read virtual_available
                    # in batch
                    rules = product._get_rules_from_location(loc)
                    lead_days = rules.with_context(bypass_delay_description=True)._get_lead_days(product)[0]
                    ploc_per_day[lead_days['total_delay'] + lead_days['horizon_time'], loc].add(product.id)

        # recompute virtual_available with lead days
        today = fields.Datetime.now().replace(hour=23, minute=59, second=59)
        product_ids = set()
        location_ids = set()
        for (days, loc), prod_ids in ploc_per_day.items():
            products = self.env['product.product'].browse(prod_ids)
            qties = products.with_context(
                location=loc.id,
                to_date=today + relativedelta.relativedelta(days=days)
            ).read(['virtual_available'])
            for (product, qty) in zip(products, qties):
                if product.uom_id.compare(qty['virtual_available'], 0) < 0:
                    to_refill[(qty['id'], loc.id)] = qty['virtual_available']
                    product_ids.add(qty['id'])
                    location_ids.add(loc.id)
            products.invalidate_recordset()
        if not to_refill:
            return action

        # Remove incoming quantity from other origin than moves (e.g RFQ)
        product_ids = list(product_ids)
        location_ids = list(location_ids)
        qty_by_product_loc = self.env['product.product'].browse(product_ids)._get_quantity_in_progress(location_ids=location_ids)[0]
        rounding = self.env['decimal.precision'].precision_get('Product Unit')
        # Group orderpoint by product-location
        orderpoint_by_product_location = self.env['stock.warehouse.orderpoint']._read_group(
            [('id', 'in', orderpoints.ids), ('product_id', 'in', product_ids)],
            ['product_id', 'location_id'],
            ['id:recordset'])
        orderpoint_by_product_location = {
            (product.id, location.id): orderpoint.qty_to_order
            for product, location, orderpoint in orderpoint_by_product_location
        }
        for (product, location), product_qty in to_refill.items():
            qty_in_progress = qty_by_product_loc.get((product, location)) or 0.0
            qty_in_progress += orderpoint_by_product_location.get((product, location), 0.0)
            # Add qty to order for other orderpoint under this location.
            if not qty_in_progress:
                continue
            to_refill[(product, location)] = product_qty + qty_in_progress
        to_refill = {k: v for k, v in to_refill.items() if float_compare(
            v, 0.0, precision_digits=rounding) < 0.0}

        # With archived ones to avoid `product_location_check` SQL constraints
        orderpoint_by_product_location = self.env['stock.warehouse.orderpoint'].with_context(active_test=False)._read_group(
            [('id', 'in', orderpoints.ids), ('product_id', 'in', product_ids)],
            ['product_id', 'location_id'],
            ['id:recordset'])
        orderpoint_by_product_location = {
            (product.id, location.id): orderpoint
            for product, location, orderpoint in orderpoint_by_product_location
        }

        orderpoint_values_list = []
        for (product, location_id), product_qty in to_refill.items():
            orderpoint = orderpoint_by_product_location.get((product, location_id))
            if orderpoint:
                orderpoint.qty_forecast += product_qty
            else:
                orderpoint_values = self.env['stock.warehouse.orderpoint']._get_orderpoint_values(product, location_id)
                location = self.env['stock.location'].browse(location_id)
                orderpoint_values.update({
                    'name': _('Replenishment Report'),
                    'warehouse_id': location.warehouse_id.id or self.env['stock.warehouse'].search([('company_id', '=', location.company_id.id)], limit=1).id,
                    'company_id': location.company_id.id,
                })
                orderpoint_values_list.append(orderpoint_values)

        orderpoints = self.env['stock.warehouse.orderpoint'].with_user(SUPERUSER_ID).create(orderpoint_values_list)
        return action

    def action_remove_manual_qty_to_order(self):
        self.qty_to_order_manual = 0

    @api.model
    def _get_orderpoint_values(self, product, location):
        return {
            'product_id': product,
            'location_id': location,
            'product_max_qty': 0.0,
            'product_min_qty': 0.0,
            'trigger': 'manual',
        }

    def _get_replenishment_order_notification(self):
        self.ensure_one()
        domain = Domain('orderpoint_id', 'in', self.ids)
        if self.env.context.get('written_after'):
            domain &= Domain('write_date', '>=', self.env.context.get('written_after'))
        move = self.env['stock.move'].search(domain, limit=1)
        if ((move.location_id.warehouse_id and move.location_id.warehouse_id != self.warehouse_id)
            or move.location_id.usage == 'transit') and move.picking_id:
            action = self.env.ref('stock.stock_picking_action_picking_type')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('The inter-warehouse transfers have been generated'),
                    'message': '%s',
                    'links': [{
                        'label': move.picking_id.name,
                        'url': f'/odoo/action-stock.stock_picking_action_picking_type/{move.picking_id.id}'
                    }],
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        return False

    def _quantity_in_progress(self):
        """Return Quantities that are not yet in virtual stock but should be deduced from orderpoint rule
        (example: purchases created from orderpoints)"""
        return dict(self.mapped(lambda x: (x.id, 0.0)))

    @api.autovacuum
    def _unlink_processed_orderpoints(self):
        domain = Domain([
            ('create_uid', '=', SUPERUSER_ID),
            ('trigger', '=', 'manual'),
        ])
        if self.ids:
            domain &= Domain('id', 'in', self.ids)
        manual_orderpoints = self.env['stock.warehouse.orderpoint'].with_context(active_test=False).search(domain)
        orderpoints_to_remove = manual_orderpoints.filtered(lambda o: o.qty_to_order <= 0.0)
        # Remove previous automatically created orderpoint that has been refilled.
        orderpoints_to_remove.unlink()
        return orderpoints_to_remove

    def _prepare_procurement_values(self, date=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from an orderpoint. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        date_deadline = date or fields.Date.today()
        dates_info = self.product_id._get_dates_info(date_deadline, self.location_id, route_ids=self.route_id)
        values = {
            'route_ids': self.route_id,
            'date_planned': dates_info['date_planned'],
            'date_order': dates_info['date_order'],
            'date_deadline': date or False,
            'warehouse_id': self.warehouse_id,
            'orderpoint_id': self,
        }
        reference = self.env.context.get('origins')
        if reference:
            values['reference_ids'] = self.env['stock.reference'].browse(reference.get(self.id))
        return values

    def _procure_orderpoint_confirm(self, use_new_cursor=False, company_id=None, raise_user_error=True):
        """ Create procurements based on orderpoints.
        :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit after processing
            1000 orderpoints.
            This is appropriate for batch jobs only.
        """
        self = self.with_company(company_id)

        for orderpoints_batch_ids in split_every(1000, self.ids):
            if use_new_cursor:
                assert isinstance(self.env.cr, BaseCursor)
                cr = Registry(self.env.cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
            try:
                orderpoints_batch = self.env['stock.warehouse.orderpoint'].browse(orderpoints_batch_ids)
                all_orderpoints_exceptions = []
                while orderpoints_batch:
                    procurements = []
                    for orderpoint in orderpoints_batch:
                        origins = orderpoint.env.context.get('origins', {}).get(orderpoint.id, False)
                        if origins:
                            origins = self.env['stock.reference'].browse(origins)
                            origin = '%s - %s' % (orderpoint.display_name, ','.join(origins.mapped('name')))
                        else:
                            origin = orderpoint.name
                        if orderpoint.product_uom.compare(orderpoint.qty_to_order, 0.0) == 1:
                            date = orderpoint._get_orderpoint_procurement_date()
                            global_horizon_days = orderpoint.get_horizon_days()
                            if global_horizon_days:
                                date -= relativedelta.relativedelta(days=int(global_horizon_days))
                            values = orderpoint._prepare_procurement_values(date=date)
                            procurements.append(self.env['stock.rule'].Procurement(
                                orderpoint.product_id, orderpoint.qty_to_order, orderpoint.product_uom,
                                orderpoint.location_id, orderpoint.name, origin,
                                orderpoint.company_id, values))

                    try:
                        with self.env.cr.savepoint():
                            self.env['stock.rule'].with_context(from_orderpoint=True).run(procurements, raise_user_error=raise_user_error)
                    except ProcurementException as errors:
                        orderpoints_exceptions = []
                        for procurement, error_msg in errors.procurement_exceptions:
                            orderpoints_exceptions += [(procurement.values.get('orderpoint_id'), error_msg)]
                        all_orderpoints_exceptions += orderpoints_exceptions
                        failed_orderpoints = self.env['stock.warehouse.orderpoint'].concat(*[o[0] for o in orderpoints_exceptions])
                        if not failed_orderpoints:
                            _logger.error('Unable to process orderpoints')
                            break
                        orderpoints_batch -= failed_orderpoints

                    except OperationalError:
                        if use_new_cursor:
                            cr.rollback()
                            continue
                        else:
                            raise
                    else:
                        orderpoints_batch._post_process_scheduler()
                        break

                # Log an activity on product template for failed orderpoints.
                for orderpoint, error_msg in all_orderpoints_exceptions:
                    existing_activity = self.env['mail.activity'].search_count([
                        ('res_id', '=', orderpoint.product_id.product_tmpl_id.id),
                        ('res_model_id', '=', self.env.ref('product.model_product_template').id),
                        ('note', 'like', error_msg)], limit=1)
                    if not existing_activity:
                        orderpoint.product_id.product_tmpl_id.sudo().activity_schedule(
                            'mail.mail_activity_data_warning',
                            note=error_msg,
                            user_id=orderpoint.product_id.responsible_id.id or SUPERUSER_ID,
                        )

            finally:
                if use_new_cursor:
                    try:
                        cr.commit()
                    finally:
                        cr.close()
                    _logger.info("A batch of %d orderpoints is processed and committed", len(orderpoints_batch_ids))

        return {}

    def _post_process_scheduler(self):
        return True

    def _get_orderpoint_procurement_date(self):
        return timezone(self.company_id.partner_id.tz or 'UTC').localize(datetime.combine(self.lead_horizon_date, time(12))).astimezone(UTC).replace(tzinfo=None)

    def _get_orderpoint_products(self):
        return self.env['product.product'].search([('is_storable', '=', True), ('stock_move_ids', '!=', False)])

    def _get_orderpoint_locations(self):
        return self.env['stock.location'].search([('replenish_location', '=', True)])

    def _get_multiple_rounded_qty(self, qty_to_order):
        replenishment_multiple = self.replenishment_uom_id or self._get_replenishment_multiple_alternative(qty_to_order)
        if replenishment_multiple and replenishment_multiple != self.product_id.uom_id:
            # Replace the UP by DOWN if we don't want to order more quantity than product_max_qty
            qty_to_order = self.product_id.uom_id._compute_quantity(qty_to_order, replenishment_multiple)
            qty_to_order = fields.Float.round(qty_to_order, precision_digits=0, rounding_method="UP")
            qty_to_order = replenishment_multiple._compute_quantity(qty_to_order, self.product_id.uom_id)
        return qty_to_order

    def get_horizon_days(self):
        """ Return the value for Horizon. This can be (in order of priority):
        - the value set in context in the replenishment view
        - the value set on the company of the all the records in self. There should be at most 1 company_id on self.
        - the value set on the company of the user if all else fail.
        """
        return self.env.context.get('global_horizon_days', (self.company_id or self.env.company).horizon_days)


# FILEPATH: odoo/addons/stock/models/stock_package.py
class StockPackage(models.Model):
    """ Packages containing quants and/or other packages """
    _name = 'stock.package'
    _description = "Package"
    _order = 'name, id'
    _parent_name = 'parent_package_id'
    _parent_store = True
    _rec_name = 'complete_name'

    name = fields.Char('Package Reference', copy=False, index='trigram', required=True)
    complete_name = fields.Char("Full Package Name", compute='_compute_complete_name', recursive=True, store=True)
    dest_complete_name = fields.Char("Package Name At Destination", compute='_compute_dest_complete_name', recursive=True)
    quant_ids = fields.One2many('stock.quant', 'package_id', 'Bulk Content', readonly=True,
        domain=['|', ('quantity', '!=', 0), ('reserved_quantity', '!=', 0)])
    contained_quant_ids = fields.One2many('stock.quant', compute="_compute_contained_quant_ids", search="_search_contained_quant_ids")
    content_description = fields.Char('Contents', compute="_compute_content_description")
    package_type_id = fields.Many2one(
        'stock.package.type', 'Package Type', index=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', compute='_compute_package_info',
        index=True, readonly=False, store=True, recursive=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination location', compute='_compute_location_dest_id', search="_search_location_dest_id")
    company_id = fields.Many2one(
        'res.company', 'Company', compute='_compute_package_info',
        index=True, readonly=True, store=True, recursive=True)
    owner_id = fields.Many2one(
        'res.partner', 'Owner', compute='_compute_owner_id', search='_search_owner',
        readonly=True, compute_sudo=True)
    parent_package_id = fields.Many2one('stock.package', 'Container', index='btree_not_null')
    child_package_ids = fields.One2many('stock.package', 'parent_package_id', string='Contained Packages')
    all_children_package_ids = fields.One2many('stock.package', compute='_compute_all_children_package_ids', search="_search_all_children_package_ids")
    package_dest_id = fields.Many2one('stock.package', 'Destination Container', index='btree_not_null')
    outermost_package_id = fields.Many2one('stock.package', 'Outermost Destination Container', compute="_compute_outermost_package_id", search="_search_outermost_package_id", recursive=True)
    child_package_dest_ids = fields.One2many('stock.package', 'package_dest_id', 'Assigned Contained Packages')
    move_line_ids = fields.One2many('stock.move.line', compute="_compute_move_line_ids", search="_search_move_line_ids")
    picking_ids = fields.Many2many('stock.picking', string='Transfers', compute='_compute_picking_ids', search="_search_picking_ids", help="Transfers in which the Package is set as Destination Package")
    shipping_weight = fields.Float(string='Shipping Weight', help="Total weight of the package.")
    valid_sscc = fields.Boolean('Package name is valid SSCC', compute='_compute_valid_sscc')
    pack_date = fields.Date('Pack Date', default=fields.Date.today)
    parent_path = fields.Char(index=True)
    json_popover = fields.Char('JSON data for popover widget', compute='_compute_json_popover')

    @api.depends('child_package_ids', 'child_package_ids.parent_path')
    def _compute_all_children_package_ids(self):
        def fetch_all_children(parent_id, children_by_pack):
            children_ids = children_by_pack.get(parent_id, [])
            sub_children_ids = [cid for child_id in children_ids for cid in fetch_all_children(child_id, children_by_pack)]
            return children_ids + sub_children_ids

        groups = self.env['stock.package']._read_group([('id', 'child_of', self.ids)], ['parent_package_id'], ['id:array_agg'])
        children_by_pack = {package.id: children_ids for package, children_ids in groups}
        for package in self:
            package.all_children_package_ids = [Command.set(fetch_all_children(package.id, children_by_pack))]

    @api.depends('complete_name', 'package_type_id.packaging_length', 'package_type_id.width', 'package_type_id.height')
    @api.depends_context('formatted_display_name', 'show_dest_package', 'show_src_package', 'is_done')
    def _compute_display_name(self):
        show_dest_package = self.env.context.get('show_dest_package')
        show_src_package = self.env.context.get('show_src_package')
        is_done = self.env.context.get('is_done')
        for package in self:
            if is_done:
                display_name = package.name
            elif show_dest_package:
                display_name = package.dest_complete_name
            elif show_src_package:
                display_name = package.complete_name
            else:
                display_name = package.name

            if package.env.context.get('formatted_display_name') and package.package_type_id and package.package_type_id.packaging_length and package.package_type_id.width and package.package_type_id.height:
                package.display_name = f"{display_name}\t--{package.package_type_id.packaging_length} x {package.package_type_id.width} x {package.package_type_id.height}--"
            else:
                package.display_name = display_name

    @api.depends('name', 'parent_package_id.complete_name')
    def _compute_complete_name(self):
        for package in self:
            if package.parent_package_id:
                package.complete_name = '%s > %s' % (package.parent_package_id.complete_name, package.name)
            else:
                package.complete_name = package.name

    @api.depends('name', 'package_dest_id.dest_complete_name')
    def _compute_dest_complete_name(self):
        for package in self:
            if package.package_dest_id:
                package.dest_complete_name = '%s > %s' % (package.package_dest_id.dest_complete_name, package.name)
            else:
                package.dest_complete_name = package.name

    @api.depends('quant_ids', 'all_children_package_ids.quant_ids')
    def _compute_contained_quant_ids(self):
        for package in self:
            package.contained_quant_ids = package.quant_ids | package.all_children_package_ids.quant_ids

    @api.depends('contained_quant_ids')
    def _compute_content_description(self):
        def format_content(qty, uom_name, product_name, display_uom):
            quantity = str(int(qty) if qty == int(qty) else qty)
            return " ".join([quantity, uom_name, product_name] if display_uom else [quantity, product_name])

        display_uom = self.env.user.has_group('uom.group_uom')
        for package in self:
            package_content = package.contained_quant_ids.grouped(lambda q: (q.product_uom_id, q.product_id))
            package_content = [(uom.name, product.display_name, sum(quants.mapped('quantity'))) for ((uom, product), quants) in package_content.items()]
            package.content_description = format_list(self.env, [format_content(qty, uom_name, product_name, display_uom) for (uom_name, product_name, qty) in package_content])

    def _compute_json_popover(self):
        for package in self:
            if not package._has_issues():
                package.json_popover = False
                continue
            location_names = package.move_line_ids.location_dest_id.mapped('display_name')
            package.json_popover = json.dumps({
                'title': self.env._("Multiple destinations"),
                'msg': self.env._("This package is currently set to be sent in %(location_names_list)s.", location_names_list=location_names),
                'color': 'text-warning',
                'icon': 'fa-exclamation-triangle',
            })

    @api.depends('move_line_ids')
    def _compute_location_dest_id(self):
        for package in self:
            package.location_dest_id = package.move_line_ids.location_dest_id[:1] or False

    @api.depends('location_id', 'child_package_dest_ids')
    def _compute_move_line_ids(self):
        # location_id in depends to force the recompute of the move_line_ids if the package moves to another location.
        children_by_dest_pack, all_pack_ids = self._get_all_children_package_dest_ids()
        groups = self.env['stock.move.line']._read_group(
            domain=[('state', 'not in', ['done', 'cancel']), ('result_package_id', 'in', all_pack_ids)],
            groupby=['result_package_id'], aggregates=['id:array_agg'])
        move_lines_by_package = {package.id: move_line_ids for package, move_line_ids in groups}

        for package in self:
            move_line_ids = {line_id for child_id in children_by_dest_pack[package] for line_id in move_lines_by_package.get(child_id, [])}
            move_line_ids.update(move_lines_by_package.get(package.id, []))
            package.move_line_ids = [Command.set(list(move_line_ids))]

    @api.depends('child_package_ids', 'child_package_ids.location_id', 'quant_ids')
    def _compute_package_info(self):
        for package in self:
            package.location_id = False
            package.company_id = False
            quants = package.quant_ids.filtered(lambda q: q.product_uom_id.compare(q.quantity, 0) > 0)
            if quants:
                package.location_id = quants[0].location_id
                if all(q.company_id == quants[0].company_id for q in package.quant_ids):
                    package.company_id = quants[0].company_id
            elif package.child_package_ids:
                package.location_id = package.child_package_ids[0].location_id
                if all(p.company_id == package.child_package_ids[0].company_id for p in package.child_package_ids):
                    package.company_id = package.child_package_ids[0].company_id

    @api.depends('child_package_dest_ids')
    def _compute_picking_ids(self):
        children_by_dest_pack, all_pack_ids = self._get_all_children_package_dest_ids()
        groups = self.env['stock.move.line']._read_group(
            domain=[('state', 'not in', ['done', 'cancel']), ('result_package_id', 'in', all_pack_ids)],
            groupby=['result_package_id'], aggregates=['picking_id:array_agg'])
        pickings_by_package = {package.id: picking_ids for package, picking_ids in groups}

        for package in self:
            picking_ids = {picking_id for child_id in children_by_dest_pack[package] for picking_id in pickings_by_package.get(child_id, [])}
            picking_ids.update(pickings_by_package.get(package.id, []))
            package.picking_ids = [Command.set(list(picking_ids))]

    @api.depends('quant_ids.owner_id')
    def _compute_owner_id(self):
        for package in self:
            package.owner_id = False
            if package.quant_ids and all(
                q.owner_id == package.quant_ids[0].owner_id for q in package.quant_ids
            ):
                package.owner_id = package.quant_ids[0].owner_id

    @api.depends('package_dest_id', 'package_dest_id.outermost_package_id')
    def _compute_outermost_package_id(self):
        for package in self:
            if package.package_dest_id:
                package.outermost_package_id = package.package_dest_id.outermost_package_id
            else:
                package.outermost_package_id = package

    @api.depends('name')
    def _compute_valid_sscc(self):
        self.valid_sscc = False
        for package in self:
            if package.name:
                package.valid_sscc = check_barcode_encoding(package.name, 'sscc')

    def _search_all_children_package_ids(self, operator, value):
        packages = self.search_fetch(domain=[('id', operator, value)], field_names=['id'])
        return [('id', 'parent_of', packages.ids)]

    def _search_contained_quant_ids(self, operator, value):
        packages = self.search([('quant_ids', operator, value)])
        if packages:
            return [('id', 'parent_of', packages.ids)]
        else:
            return [('id', '=', False)]

    def _search_location_dest_id(self, operator, value):
        if operator not in ['in', 'not in']:
            return NotImplemented

        move_lines = self.env['stock.move.line'].search_fetch(
            domain=[('state', 'not in', ['done', 'cancel']), ('location_dest_id', operator, value)],
            field_names=['result_package_id'])
        all_package_ids = move_lines.result_package_id._get_all_package_dest_ids()

        return [('id', 'in', all_package_ids)]

    def _search_move_line_ids(self, operator, value):
        if operator not in ('in', 'any'):
            return NotImplemented
        if operator == 'any':
            operator = 'in'
            if isinstance(value, Domain):
                value = self.env['stock.move.line']._search(value)

        domain = Domain('state', 'not in', ['done', 'cancel'])
        pack_operator = 'in'
        if isinstance(value, Iterable) and tuple(value) == (False,):
            # Search for ('move_line_ids', '=', False), which means not assigned to any ongoing picking
            pack_operator = 'not in'
        else:
            domain &= Domain('id', operator, value)
        move_lines = self.env['stock.move.line'].search_fetch(domain=domain, field_names=['result_package_id'])
        all_package_ids = move_lines.result_package_id._get_all_package_dest_ids()

        return [('id', pack_operator, all_package_ids)]

    def _search_outermost_package_id(self, operator, value):
        if operator not in ['in', 'not in']:
            return NotImplemented

        packages = self.env['stock.package'].search_fetch(
            domain=[('package_dest_id', operator, value)],
            field_names=['child_package_dest_ids']
        )
        __, all_children_ids = packages._get_all_children_package_dest_ids()
        return [('id', 'in', all_children_ids)]

    def _search_owner(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS:
            return NotImplemented
        return Domain('quant_ids.owner_id', operator, value)

    def _search_picking_ids(self, operator, value):
        if operator not in ['in', 'not in']:
            return NotImplemented

        move_lines = self.env['stock.move.line'].search_fetch(
            domain=[('state', 'not in', ['done', 'cancel']), ('picking_id', operator, value)],
            field_names=['result_package_id'])
        all_package_ids = move_lines.result_package_id._get_all_package_dest_ids()

        return [('id', 'in', all_package_ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('complete_name'):
                vals['name'] = vals['complete_name']
                del vals['complete_name']
            if not vals.get('name'):
                package_type = self.env['stock.package.type'].browse(vals.get('package_type_id'))
                vals['name'] = package_type._get_next_name_by_sequence()

        return super().create(vals_list)

    def write(self, vals):
        if 'name' in vals and not vals.get('name'):
            # Recomputes the name according the sequence if the name was emptied.
            package_type = self.env['stock.package.type'].browse(vals.get('package_type_id'))
            for package in self:
                package_type = self.env['stock.package.type'].browse(vals.get('package_type_id', self.package_type_id.id))
                package.name = package_type._get_next_name_by_sequence()
            del vals['name']
        if 'location_id' in vals:
            is_pack_empty = any(not pack.contained_quant_ids for pack in self)
            if not vals['location_id'] and not is_pack_empty:
                raise UserError(self.env._('Cannot remove the location of a non empty package'))
            elif vals['location_id']:
                if is_pack_empty:
                    raise UserError(self.env._('Cannot move an empty package'))
                # create a move from the old location to new location
                location_dest_id = self.env['stock.location'].browse(vals['location_id'])
                quant_to_move = self.contained_quant_ids.filtered(lambda q: q.quantity > 0)
                quant_to_move.move_quants(location_dest_id, message=self.env._('Package manually relocated'), up_to_parent_packages=self)
        if vals.get('package_dest_id'):
            # Need to make sure we avoid a recursion within the package dests. Can't rely on the `parent_path` for destination packages.
            current_children_dest_ids = self._get_all_children_package_dest_ids()[1]
            if vals['package_dest_id'] in current_children_dest_ids:
                raise ValidationError(self.env._("A package can't have one of its contained packages as destination container."))

        return super().write(vals)

    def unpack(self):
        """ Unpacks quants directly inside the container, and remove contained packages from this package.
        """
        self.child_package_ids.parent_package_id = False
        if self.quant_ids:
            quants = self.quant_ids
            self.quant_ids.move_quants(message=self.env._("Quantities unpacked"), unpack=True)
            # Quant clean-up, mostly to avoid multiple quants of the same product. For example, unpack
            # 2 packages of 50, then reserve 100 => a quant of -50 is created at transfer validation.
            quants._quant_tasks()

    def action_add_to_picking(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('picking_id'))
        if picking and self:
            picking.action_add_entire_packs(self.ids)

    def _pre_put_in_pack_hook(self, package_id=False, package_type_id=False, package_name=False, from_package_wizard=False):
        if self.move_line_ids._should_display_put_in_pack_wizard(package_id, package_type_id, package_name, from_package_wizard):
            action = self.env["ir.actions.actions"]._for_xml_id("stock.action_put_in_pack_wizard")
            action['context'] = {
                **literal_eval(action.get('context', '{}')),
                'default_package_ids': self.ids,
                'default_location_dest_id': self.location_dest_id[:1].id,
            }
            return action
        return False

    def _post_put_in_pack_hook(self):
        self.ensure_one()
        return self

    def action_put_in_pack(self, *, package_id=False, package_type_id=False, package_name=False):
        action = self._pre_put_in_pack_hook(package_id, package_type_id, package_name, self.env.context.get('from_package_wizard'))
        if action:
            return action

        if package_id:
            package = self.env['stock.package'].browse(package_id)
        else:
            package = self.env['stock.package'].create({
                'package_type_id': package_type_id,
                'name': package_name,
            })
        previous_dest_packages = self.env['stock.package'].browse(self._get_all_package_dest_ids())
        self.package_dest_id = package
        if packs_to_clear := previous_dest_packages.filtered(lambda p: not p.move_line_ids):
            # If following the put in pack, we broke the existing chain somehow, we need to free all now irrelevant packages
            packs_to_clear.package_dest_id = False

        # Since the uppermost package changed, there might be some new putaway to apply.
        package.move_line_ids._apply_putaway_strategy()
        return package._post_put_in_pack_hook()

    def action_remove_package(self):
        """ Removes all packages in self from the destination container tree.
            For move lines directly linked to a package (through result_package_id)
            - If the entire package is moved, remove the move lines entirely from the picking
            - Otherwise, just unset the packages as destination package
        """
        all_package_dest_ids = self._get_all_package_dest_ids()
        all_move_line_ids = set(self.move_line_ids.ids)
        move_line_ids_to_unlink = set()
        related_move_ids = set()
        move_line_ids_to_update = set()
        for line in self.move_line_ids:
            picking_ids = self.env.context.get('picking_ids')
            if picking_ids and line.picking_id.id not in picking_ids:
                continue
            if line.result_package_id.id in self.ids:
                if line.is_entire_pack:
                    move_line_ids_to_unlink.add(line.id)
                    related_move_ids.add(line.move_id.id)
                else:
                    move_line_ids_to_update.add(line.id)

        self.env['stock.move.line'].browse(move_line_ids_to_unlink).unlink()
        self.env['stock.move.line'].browse(move_line_ids_to_update).write({'result_package_id': False})
        # Unlink moves that had no initial demand and don't have any more associated move lines
        self.env['stock.move'].search_fetch([('id', 'in', related_move_ids), ('product_uom_qty', '=', 0), ('move_line_ids', '=', False)], field_names=['id']).unlink()

        # If packages in self are dest containers of other packages, remove them as their dest as well
        self.child_package_dest_ids.package_dest_id = False
        self.package_dest_id = False

        # If parent packages are now isolated from bottom-level packages, clear their destination container as well
        self.env['stock.package'].search_fetch([('id', 'in', all_package_dest_ids), ('move_line_ids', '=', False)], field_names=['id']).write({'package_dest_id': False})

        # If outermost packages were changed, different putaway rules may apply.
        self.env['stock.move.line'].browse(all_move_line_ids - move_line_ids_to_unlink)._apply_putaway_strategy()
        return True

    def action_view_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        domain = ['|', ('result_package_id', 'in', self.ids), ('package_id', 'in', self.ids)]
        pickings = self.env['stock.move.line'].search(domain).mapped('picking_id')
        action['domain'] = [('id', 'in', pickings.ids)]
        return action

    def _check_move_lines_map_quant(self, move_lines):
        """ This method checks that all product (quants) of self (package) are well present in the `move_line_ids`. """
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        def _keys_groupby(record):
            return record.product_id, record.lot_id

        if not move_lines:
            return True

        grouped_quants = {}
        for k, g in groupby(self.contained_quant_ids, key=_keys_groupby):
            grouped_quants[k] = sum(self.env['stock.quant'].concat(*g).mapped('quantity'))

        grouped_ops = {}
        for k, g in groupby(move_lines, key=_keys_groupby):
            grouped_ops[k] = sum(self.env['stock.move.line'].concat(*g).mapped('quantity_product_uom'))

        return all(float_is_zero(grouped_quants.get(key, 0) - grouped_ops.get(key, 0), precision_digits=precision_digits) for key in grouped_quants) \
           and all(float_is_zero(grouped_ops.get(key, 0) - grouped_quants.get(key, 0), precision_digits=precision_digits) for key in grouped_ops)

    def _get_weight(self, picking_id=False):
        res = {}
        if picking_id:
            package_weights = defaultdict(float)
            # If we check the weight of an ongoing package, we may need to check its current child dest as well to known their own weight.
            children_by_dest_pack, all_pack_ids = self._get_all_children_package_dest_ids()
            base_weight_per_package_group = self.env['stock.package']._read_group(
                domain=[('id', 'in', all_pack_ids)],
                groupby=['id', 'package_type_id.base_weight']
            )
            base_weight_per_package = {pack.id: weight for pack, weight in base_weight_per_package_group}

            res_groups = self.env['stock.move.line']._read_group(
                [('result_package_id', 'in', all_pack_ids), ('product_id', '!=', False), ('picking_id', '=', picking_id)],
                ['result_package_id', 'product_id', 'product_uom_id', 'quantity'],
                ['__count'],
            )
            for result_package, product, product_uom, quantity, count in res_groups:
                package_weights[result_package.id] += (
                    count
                    * product_uom._compute_quantity(quantity, product.uom_id)
                    * product.weight
                )
        for package in self:
            weight = package.package_type_id.base_weight or 0.0
            if picking_id:
                res[package] = weight + package_weights[package.id]
                for child_id in children_by_dest_pack.get(package, []):
                    res[package] += base_weight_per_package.get(child_id, 0) + package_weights.get(child_id, 0)
            else:
                # Take the base_weight of every contained package, so we include package only containing packages
                weight += sum(package.all_children_package_ids.mapped(lambda p: p.package_type_id.base_weight))
                for quant in package.contained_quant_ids:
                    weight += quant.quantity * quant.product_id.weight
                res[package] = weight
        return res

    def _has_issues(self):
        self.ensure_one()
        return len(self.move_line_ids.location_dest_id) > 1

    def _apply_dest_to_package(self, processed_package_ids=None):
        """ Moves the packages to their new container and checks that no contained quants of the new container
            would be in different locations.
        """
        packages_todo = self
        if processed_package_ids:
            packages_todo = packages_todo.filtered(lambda p: p.id not in processed_package_ids)
        else:
            processed_package_ids = set()
        packs_by_container = packages_todo.grouped('package_dest_id')
        for container_package, packages in packs_by_container.items():
            if not container_package:
                # If package has no future container package, needs to be removed from its current one.
                packages.write({'parent_package_id': False})
                processed_package_ids.update(packages.ids)
                continue
            # At this point, the packages were already moved so we need to check their current position.
            new_location = packages.location_id
            if len(new_location) > 1:
                raise UserError(self.env._("Packages %(duplicate_names)s are moved to different locations while being in the same container %(container_name)s.",
                                            duplicate_names=packages.mapped('name'), container_name=container_package.name))
            contained_quants = container_package.contained_quant_ids.filtered(lambda q: not float_is_zero(q.quantity, precision_rounding=q.product_uom_id.rounding))
            if contained_quants and contained_quants.location_id != new_location:
                old_location = contained_quants.location_id - new_location
                raise UserError(self.env._("Can't move a container having packages in another location (%(old_location)s) to a different location (%(new_location)s).",
                                            old_location=old_location.display_name, new_location=new_location.display_name))
            packages.write({
                'parent_package_id': container_package.id,
                'package_dest_id': False,
            })
            processed_package_ids.update(packages.ids)
        # First level has been applied, need to check if next level needs to be applied as well.
        if packages_todo.parent_package_id.package_dest_id or packages_todo.parent_package_id.parent_package_id:
            packages_todo.parent_package_id._apply_dest_to_package(processed_package_ids)

    def _get_all_children_package_dest_ids(self):
        """ Gets all child packages that have the packages in self as their `package_dest_id` recursively.
            Since we can only have a single _parent field on the model, we need to do this manually.
            :returns: A dict for each record in self containing all packages that have it as `package_dest_id`, even remotely
            :returns: A list containing all children ids, regardless of their parents
        """
        def fetch_next_children(packages):
            if packages.child_package_dest_ids:
                return set(packages.ids) | fetch_next_children(packages.child_package_dest_ids)
            else:
                return set(packages.ids)

        all_children_ids = set(self.ids)
        all_children_by_pack = defaultdict(list)
        for package in self:
            if package.child_package_dest_ids:
                child_ids = list(fetch_next_children(package.child_package_dest_ids))
                all_children_ids.update(child_ids)
                all_children_by_pack[package] = child_ids

        return all_children_by_pack, all_children_ids

    def _get_all_package_dest_ids(self):
        """ Gets all parent destination packages recursively.
            Since we can only have a single _parent field on the model, we need to do this manually.
            :returns: A list containing all parent ids
        """
        def fetch_next_parents(packages):
            if packages.package_dest_id:
                return set(packages.ids) | fetch_next_parents(packages.package_dest_id)
            else:
                return set(packages.ids)

        return list(fetch_next_parents(self))

    def _apply_package_dest_for_entire_packs(self, allowed_package_ids=None):
        """ When a package is assigned to a picking, if all of its container is added,
            then we consider the container to be added itself, unless the container
            is a reusable package itself.
        """
        for container, packages in self.grouped('parent_package_id').items():
            if container.child_package_ids == packages and container.package_type_id.package_use != 'reusable':
                if allowed_package_ids and container.id not in allowed_package_ids:
                    continue
                packages.package_dest_id = container
        if self.package_dest_id:
            # If one level was added, need to check if the upper container is fully contained as well.
            self.package_dest_id._apply_package_dest_for_entire_packs(allowed_package_ids)


# FILEPATH: odoo/addons/stock/models/stock_package_history.py
class StockPackageHistory(models.Model):
    _name = 'stock.package.history'
    _description = "Stock Package History"
    _check_company_auto = True

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    location_id = fields.Many2one('stock.location', 'Origin Location')
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    move_line_ids = fields.One2many('stock.move.line', 'package_history_id', string='Move Lines', required=True)
    package_id = fields.Many2one('stock.package', 'Package', required=True, ondelete='cascade')
    package_name = fields.Char('Package Name', required=True)
    package_type_id = fields.Many2one('stock.package.type', related='package_id.package_type_id')
    parent_orig_id = fields.Many2one('stock.package', 'Origin Container')
    parent_orig_name = fields.Char('Origin Container Name')
    parent_dest_id = fields.Many2one('stock.package', 'Destination Container')
    parent_dest_name = fields.Char('Destination Container Name')
    outermost_dest_id = fields.Many2one('stock.package', 'Outermost Destination Container')
    picking_ids = fields.Many2many('stock.picking', string='Transfers')

    def _get_complete_dest_name_except_outermost(self):
        self.ensure_one()
        if not self.parent_dest_id:
            return ''
        elif self.parent_dest_id == self.outermost_dest_id:
            return self.package_id.name

        # Complete name without the first (outermost) package name
        return ' > '.join(self.package_name.split(' > ')[1:])

    def action_show_package(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.package',
            'res_id': self.package_id.id,
        }


# FILEPATH: odoo/addons/stock/models/stock_package_type.py
class StockPackageType(models.Model):
    _name = 'stock.package.type'
    _description = "Stock package type"
    _order = "sequence, id"

    def _get_default_length_uom(self):
        return self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    def _get_default_weight_uom(self):
        return self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    name = fields.Char('Package Type', required=True)
    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence', check_company=True, copy=False)
    sequence_code = fields.Char('Sequence Prefix', related="sequence_id.code", readonly=False)
    height = fields.Float('Height', help="Packaging Height")
    width = fields.Float('Width', help="Packaging Width")
    packaging_length = fields.Float('Length', help="Packaging Length")
    base_weight = fields.Float(string='Weight', help='Weight of the package type')
    max_weight = fields.Float('Max Weight', help='Maximum weight shippable in this packaging')
    barcode = fields.Char('Barcode', copy=False)
    weight_uom_name = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name', default=_get_default_weight_uom)
    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name', default=_get_default_length_uom)
    company_id = fields.Many2one('res.company', 'Company', index=True)
    package_use = fields.Selection([
        ('disposable', 'Disposable Box'),
        ('reusable', 'Reusable Box (totes)'),
        ], string='Package Use', default='disposable', required=True,
        help="""Reusable boxes are used for batch picking and emptied afterwards to be reused. In the barcode application, scanning a reusable box will add the products in this box.
        Disposable boxes aren't reused, when scanning a disposable box in the barcode application, the contained products are added to the transfer.""")
    has_quants = fields.Boolean('Has Contents', compute='_compute_has_quants')
    storage_category_capacity_ids = fields.One2many('stock.storage.category.capacity', 'package_type_id', 'Storage Category Capacity', copy=True)
    route_ids = fields.Many2many('stock.route', string='Routes', domain="[('package_type_selectable', '=', True)]")

    _barcode_uniq = models.Constraint(
        'unique(barcode)',
        'A barcode can only be assigned to one package type!',
    )
    _positive_height = models.Constraint(
        'CHECK(height>=0.0)',
        'Height must be positive',
    )
    _positive_width = models.Constraint(
        'CHECK(width>=0.0)',
        'Width must be positive',
    )
    _positive_length = models.Constraint(
        'CHECK(packaging_length>=0.0)',
        'Length must be positive',
    )
    _positive_max_weight = models.Constraint(
        'CHECK(max_weight>=0.0)',
        'Max Weight must be positive',
    )

    @api.depends('name', 'packaging_length', 'width', 'height')
    @api.depends_context('formatted_display_name')
    def _compute_display_name(self):
        packages_to_process_ids = []
        for package in self:
            if package.env.context.get('formatted_display_name') and package.packaging_length and package.width and package.height:
                package.display_name = f"{package.name}\t--{package.packaging_length} x {package.width} x {package.height}--"
            else:
                packages_to_process_ids.append(package.id)
        if packages_to_process_ids:
            super(StockPackageType, self.env['stock.package.type'].browse(packages_to_process_ids))._compute_display_name()

    def _compute_has_quants(self):
        pack_type_quants = dict(self.env['stock.package']._read_group(
            domain=[('quant_ids', '!=', False), ('package_type_id', 'in', self.ids)], groupby=['package_type_id'], aggregates=['__count']))

        for package_type in self:
            package_type.has_quants = pack_type_quants.get(package_type, 0) > 0

    def _compute_length_uom_name(self):
        for package_type in self:
            package_type.length_uom_name = self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    def _compute_weight_uom_name(self):
        for package_type in self:
            package_type.weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        return [dict(vals, name=self.env._("%s (copy)", package_type.name)) for package_type, vals in zip(self, vals_list)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence_id') and vals.get('sequence_code'):
                vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                    'name': self.env._('Package Type Sequence %(code)s', code=vals['sequence_code']),
                    'prefix': vals['sequence_code'],
                    'padding': 7,
                    'company_id': vals.get('company_id'),
                }).id
        return super().create(vals_list)

    def write(self, vals):
        seq_vals = {}
        if 'sequence_code' in vals:
            seq_vals['name'] = self.env._('Package Type Sequence %(code)s', code=vals['sequence_code'])
            seq_vals['prefix'] = vals['sequence_code']
        if 'company_id' in vals:
            seq_vals['company_id'] = vals['company_id']
        if seq_vals:
            seq_to_todo_ids = set()
            for package_type in self:
                if not package_type.sequence_id:
                    sequence = self.env['ir.sequence'].sudo().create({
                        **seq_vals,
                        'padding': 7,
                        'company_id': seq_vals.get('company_id', package_type.company_id.id),
                    })
                    package_type.sequence_id = sequence
                else:
                    seq_to_todo_ids.add(package_type.sequence_id.id)
            if seq_to_todo_ids:
                self.env['ir.sequence'].browse(list(seq_to_todo_ids)).sudo().write(seq_vals)
        return super().write(vals)

    def _get_next_name_by_sequence(self):
        if len(self) == 1 and self.sequence_id:
            return self.sequence_id.next_by_id()
        return self.env['ir.sequence'].next_by_code('stock.package')


# FILEPATH: odoo/addons/stock/models/stock_picking.py (lines 20-535)
class StockPickingType(models.Model):
    _name = 'stock.picking.type'
    _description = "Picking Type"
    _order = 'is_favorite desc, sequence, id'
    _rec_names_search = ['name', 'warehouse_id.name']
    _check_company_auto = True

    name = fields.Char('Operation Type', required=True, translate=True)
    color = fields.Integer('Color')
    sequence = fields.Integer('Sequence', help="Used to order the 'All Operations' kanban view")
    sequence_id = fields.Many2one(
        'ir.sequence', 'Reference Sequence',
        check_company=True, copy=False)
    sequence_code = fields.Char('Sequence Prefix', required=True)
    default_location_src_id = fields.Many2one(
        'stock.location', 'Source Location', compute='_compute_default_location_src_id',
        check_company=True, store=True, readonly=False, precompute=True, required=True,
        help="This is the default source location when this operation is manually created. However, it is possible to change it afterwards or that the routes use another one by default.")
    default_location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location', compute='_compute_default_location_dest_id',
        check_company=True, store=True, readonly=False, precompute=True, required=True,
        help="This is the default destination location when this operation is manually created. However, it is possible to change it afterwards or that the routes use another one by default.")
    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')], 'Type of Operation', default='incoming', required=True)
    return_picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type for Returns',
        index='btree_not_null',
        check_company=True)
    show_entire_packs = fields.Boolean('Move Entire Packages', default=False, help="If ticked, packages to move will be directly displayed in Barcode instead of the products they contain")
    set_package_type = fields.Boolean('Set Package Type', default=False, help="If ticked, you will be able to select which package or package type to use in a put in pack")
    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', compute='_compute_warehouse_id', store=True, readonly=False, ondelete='cascade',
        check_company=True)
    active = fields.Boolean('Active', default=True)
    use_create_lots = fields.Boolean(
        'Create New Lots/Serial Numbers', default=True,
        compute='_compute_use_create_lots', store=True, readonly=False,
        help="If this is checked only, it will suppose you want to create new Lots/Serial Numbers, so you can provide them in a text field. ")
    use_existing_lots = fields.Boolean(
        'Use Existing Lots/Serial Numbers', default=True,
        compute='_compute_use_existing_lots', store=True, readonly=False,
        help="If this is checked, you will be able to choose the Lots/Serial Numbers. You can also decide to not put lots in this operation type.  This means it will create stock with no lot or not put a restriction on the lot taken. ")
    print_label = fields.Boolean(
        'Generate Shipping Labels', compute="_compute_print_label", store=True, readonly=False,
        help="Check this box if you want to generate shipping label in this operation.")
    # TODO: delete this field `show_operations`
    show_operations = fields.Boolean(
        'Show Detailed Operations', default=False,
        help="If this checkbox is ticked, the pickings lines will represent detailed stock operations. If not, the picking lines will represent an aggregate of detailed stock operations.")
    reservation_method = fields.Selection(
        [('at_confirm', 'At Confirmation'), ('manual', 'Manually'), ('by_date', 'Before scheduled date')],
        'Reservation Method', required=True, default='at_confirm',
        help="How products in transfers of this operation type should be reserved.")
    reservation_days_before = fields.Integer('Days', help="Maximum number of days before scheduled date that products should be reserved.")
    reservation_days_before_priority = fields.Integer('Days when starred', help="Maximum number of days before scheduled date that priority picking products should be reserved.")
    auto_show_reception_report = fields.Boolean(
        "Show Reception Report at Validation",
        help="If this checkbox is ticked, Odoo will automatically show the reception report (if there are moves to allocate to) when validating.")
    auto_print_delivery_slip = fields.Boolean(
        "Auto Print Delivery Slip",
        help="If this checkbox is ticked, Odoo will automatically print the delivery slip of a picking when it is validated.")
    auto_print_return_slip = fields.Boolean(
        "Auto Print Return Slip",
        help="If this checkbox is ticked, Odoo will automatically print the return slip of a picking when it is validated.")

    auto_print_product_labels = fields.Boolean(
        "Auto Print Product Labels",
        help="If this checkbox is ticked, Odoo will automatically print the product labels of a picking when it is validated.")
    product_label_format = fields.Selection([
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price'),
        ('zpl', 'ZPL Labels'),
        ('zplxprice', 'ZPL Labels with price')], string="Product Label Format to auto-print", default='2x7xprice')
    auto_print_lot_labels = fields.Boolean(
        "Auto Print Lot/SN Labels",
        help="If this checkbox is ticked, Odoo will automatically print the lot/SN labels of a picking when it is validated.")
    lot_label_format = fields.Selection([
        ('4x12_lots', '4 x 12 - One per lot/SN'),
        ('4x12_units', '4 x 12 - One per unit'),
        ('zpl_lots', 'ZPL Labels - One per lot/SN'),
        ('zpl_units', 'ZPL Labels - One per unit')],
        string="Lot Label Format to auto-print", default='4x12_lots')
    auto_print_reception_report = fields.Boolean(
        "Auto Print Reception Report",
        help="If this checkbox is ticked, Odoo will automatically print the reception report of a picking when it is validated and has assigned moves.")
    auto_print_reception_report_labels = fields.Boolean(
        "Auto Print Reception Report Labels",
        help="If this checkbox is ticked, Odoo will automatically print the reception report labels of a picking when it is validated.")
    auto_print_packages = fields.Boolean(
        "Auto Print Packages",
        help="If this checkbox is ticked, Odoo will automatically print the packages and their contents of a picking when it is validated.")

    auto_print_package_label = fields.Boolean(
        "Auto Print Package Label",
        help="If this checkbox is ticked, Odoo will automatically print the package label when \"Put in Pack\" button is used.")
    package_label_to_print = fields.Selection(
        [('pdf', 'PDF'), ('zpl', 'ZPL')],
        "Package Label to Print", default='pdf')

    count_picking_draft = fields.Integer(compute='_compute_picking_count')
    count_picking_ready = fields.Integer(compute='_compute_picking_count')
    count_picking = fields.Integer(compute='_compute_picking_count')
    count_picking_waiting = fields.Integer(compute='_compute_picking_count')
    count_picking_late = fields.Integer(compute='_compute_picking_count')
    count_picking_backorders = fields.Integer(compute='_compute_picking_count')
    count_move_ready = fields.Integer(compute='_compute_move_count')
    hide_reservation_method = fields.Boolean(compute='_compute_hide_reservation_method')
    barcode = fields.Char('Barcode', copy=False)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    create_backorder = fields.Selection(
        [('ask', 'Ask'), ('always', 'Always'), ('never', 'Never')],
        'Create Backorder', required=True, default='ask',
        help="When validating a transfer:\n"
             " * Ask: users are asked to choose if they want to make a backorder for remaining products\n"
             " * Always: a backorder is automatically created for the remaining products\n"
             " * Never: remaining products are cancelled")
    show_picking_type = fields.Boolean(compute='_compute_show_picking_type')

    picking_properties_definition = fields.PropertiesDefinition("Picking Properties")
    favorite_user_ids = fields.Many2many(
        'res.users', 'picking_type_favorite_user_rel', 'picking_type_id', 'user_id',
    )
    is_favorite = fields.Boolean(
        compute='_compute_is_favorite', inverse='_inverse_is_favorite', search='_search_is_favorite',
        compute_sudo=True, string='Show Operation in Overview'
    )
    kanban_dashboard_graph = fields.Text(compute='_compute_kanban_dashboard_graph')
    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')],
        'Shipping Policy', default='direct', required=True,
        help="It specifies goods to be transferred partially or all at once")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence_id') and vals.get('sequence_code'):
                if vals.get('warehouse_id'):
                    wh = self.env['stock.warehouse'].browse(vals['warehouse_id'])
                    vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                        'name': _('%(warehouse)s Sequence %(code)s', warehouse=wh.name, code=vals['sequence_code']),
                        'prefix': wh.code + '/' + vals['sequence_code'] + '/', 'padding': 5,
                        'company_id': wh.company_id.id,
                    }).id
                else:
                    vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                        'name': _('Sequence %(code)s', code=vals['sequence_code']),
                        'prefix': vals['sequence_code'], 'padding': 5,
                        'company_id': vals.get('company_id') or self.env.company.id,
                    }).id
        return super().create(vals_list)

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for picking, vals in zip(self, vals_list):
            if 'name' not in default:
                vals['name'] = _("%s (copy)", picking.name)
            if 'sequence_code' not in default and 'sequence_id' not in default:
                vals['sequence_code'] = _("%s (copy)", picking.sequence_code)
        return vals_list

    def write(self, vals):
        if 'company_id' in vals:
            for picking_type in self:
                if picking_type.company_id.id != vals['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))
        if 'sequence_code' in vals:
            for picking_type in self:
                if picking_type.warehouse_id:
                    picking_type.sequence_id.sudo().write({
                        'name': _('%(warehouse)s Sequence %(code)s', warehouse=picking_type.warehouse_id.name, code=vals['sequence_code']),
                        'prefix': picking_type.warehouse_id.code + '/' + vals['sequence_code'] + '/', 'padding': 5,
                        'company_id': picking_type.warehouse_id.company_id.id,
                    })
                else:
                    picking_type.sequence_id.sudo().write({
                        'name': _('Sequence %(code)s', code=vals['sequence_code']),
                        'prefix': vals['sequence_code'], 'padding': 5,
                        'company_id': picking_type.env.company.id,
                    })
        if 'reservation_method' in vals:
            if vals['reservation_method'] == 'by_date':
                if picking_types := self.filtered(lambda p: p.reservation_method != 'by_date'):
                    domain = [('picking_type_id', 'in', picking_types.ids), ('state', 'in', ('draft', 'confirmed', 'waiting', 'partially_available'))]
                    group_by = ['picking_type_id']
                    aggregates = ['id:recordset']
                    for picking_type, moves in self.env['stock.move']._read_group(domain, group_by, aggregates):
                        common_days = vals.get('reservation_days_before') or picking_type.reservation_days_before
                        priority_days = vals.get('reservation_days_before_priority') or picking_type.reservation_days_before_priority
                        for move in moves:
                            move.reservation_date = fields.Date.to_date(move.date) - timedelta(days=priority_days if move.priority == '1' else common_days)
            else:
                if picking_types := self.filtered(lambda p: p.reservation_method == 'by_date'):
                    moves = self.env['stock.move'].search([('picking_type_id', 'in', picking_types.ids), ('state', 'not in', ('assigned', 'done', 'cancel'))])
                    moves.reservation_date = False

        return super().write(vals)

    @api.model
    def _search_is_favorite(self, operator, value):
        if operator != 'in':
            return NotImplemented
        return [('favorite_user_ids', 'in', [self.env.uid])]

    def _compute_is_favorite(self):
        for picking_type in self:
            picking_type.is_favorite = self.env.user in picking_type.favorite_user_ids

    def _inverse_is_favorite(self):
        sudoed_self = self.sudo()
        to_fav = sudoed_self.filtered(
            lambda picking_type: self.env.user not in picking_type.favorite_user_ids
        )
        to_fav.write({'favorite_user_ids': [(4, self.env.uid)]})
        (sudoed_self - to_fav).write({'favorite_user_ids': [(3, self.env.uid)]})

    def _order_field_to_sql(self, alias, field_name, direction, nulls, query):
        if field_name == 'is_favorite':
            sql_field = SQL(
                "%s IN (SELECT picking_type_id FROM picking_type_favorite_user_rel WHERE user_id = %s)",
                SQL.identifier(alias, 'id'), self.env.uid,
            )
            return SQL("%s %s %s", sql_field, direction, nulls)

        return super()._order_field_to_sql(alias, field_name, direction, nulls, query)

    @api.depends('code')
    def _compute_hide_reservation_method(self):
        for rec in self:
            rec.hide_reservation_method = rec.code == 'incoming'

    def _compute_picking_count(self):
        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', '=', 'assigned')],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('state', 'in', ('assigned', 'waiting', 'confirmed')), '|', ('scheduled_date', '<', fields.Date.today()), ('has_deadline_issue', '=', True)],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }
        for field_name, domain in domains.items():
            data = self.env['stock.picking']._read_group(domain +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['__count'])
            count = {picking_type.id: count for picking_type, count in data}
            for record in self:
                record[field_name] = count.get(record.id, 0)

    def _compute_move_count(self):
        data = self.env['stock.move']._read_group(
            [('state', '=', 'assigned'), ('picking_type_id', 'in', self.ids)],
            ['picking_type_id'], ['__count']
        )
        count = {picking_type.id: count for picking_type, count in data}
        for record in self:
            record['count_move_ready'] = count.get(record.id, 0)

    @api.depends('warehouse_id')
    def _compute_display_name(self):
        """ Display 'Warehouse_name: PickingType_name' """
        for picking_type in self:
            if picking_type.warehouse_id:
                picking_type.display_name = f"{picking_type.warehouse_id.name}: {picking_type.name}"
            else:
                picking_type.display_name = picking_type.name

    @api.depends('code')
    def _compute_use_create_lots(self):
        for picking_type in self:
            if picking_type.code == 'incoming':
                picking_type.use_create_lots = True

    @api.depends('code')
    def _compute_use_existing_lots(self):
        for picking_type in self:
            if picking_type.code == 'outgoing':
                picking_type.use_existing_lots = True

    @api.model
    def _search_display_name(self, operator, value):
        # Try to reverse the `display_name` structure
        if operator == 'in':
            return Domain.OR(self._search_display_name('=', v) for v in value)
        if operator == 'not in':
            return NotImplemented
        parts = isinstance(value, str) and value.split(': ')
        if parts and len(parts) == 2:
            return Domain('warehouse_id.name', operator, parts[0]) & Domain('name', operator, parts[1])
        if operator == '=':
            operator = 'in'
            value = [value]
        return super()._search_display_name(operator, value)

    @api.depends('code')
    def _compute_default_location_src_id(self):
        for picking_type in self:
            if not picking_type.warehouse_id:
                self.env['stock.warehouse']._warehouse_redirect_warning()
            stock_location = picking_type.warehouse_id.lot_stock_id
            if picking_type.code == 'incoming':
                picking_type.default_location_src_id = self.env.ref('stock.stock_location_suppliers').id
            else:
                picking_type.default_location_src_id = stock_location.id

    @api.depends('code')
    def _compute_default_location_dest_id(self):
        for picking_type in self:
            if not picking_type.warehouse_id:
                self.env['stock.warehouse']._warehouse_redirect_warning()
            stock_location = picking_type.warehouse_id.lot_stock_id
            if picking_type.code == 'outgoing':
                picking_type.default_location_dest_id = self.env.ref('stock.stock_location_customers').id
            else:
                picking_type.default_location_dest_id = stock_location.id

    @api.depends('code')
    def _compute_print_label(self):
        for picking_type in self:
            if picking_type.code in ('incoming', 'internal'):
                picking_type.print_label = False
            elif picking_type.code == 'outgoing':
                picking_type.print_label = True

    @api.onchange('code')
    def _onchange_picking_code(self):
        if self.code == 'internal' and not self.env.user.has_group('stock.group_stock_multi_locations'):
            return {
                'warning': {
                    'message': _('You need to activate storage locations to be able to do internal operation types.')
                }
            }

    @api.depends('company_id')
    def _compute_warehouse_id(self):
        for picking_type in self:
            if picking_type.warehouse_id:
                continue
            if picking_type.company_id:
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', picking_type.company_id.id)], limit=1)
                picking_type.warehouse_id = warehouse

    @api.depends('code')
    def _compute_show_picking_type(self):
        for record in self:
            record.show_picking_type = record.code in ['incoming', 'outgoing', 'internal']

    def _compute_kanban_dashboard_graph(self):
        grouped_records = self._get_aggregated_records_by_date()

        summaries = {}
        for picking_type_id, dates, data_series_name in grouped_records:
            summaries[picking_type_id] = {
                'data_series_name': data_series_name,
                'total_before': 0,
                'total_yesterday': 0,
                'total_today': 0,
                'total_day_1': 0,
                'total_day_2': 0,
                'total_after': 0,
            }
            for p_date in dates:
                date_category = self.env["stock.picking"].calculate_date_category(p_date)
                if date_category:
                    summaries[picking_type_id]['total_' + date_category] += 1

        self._prepare_graph_data(summaries)

    @api.onchange('sequence_code')
    def _onchange_sequence_code(self):
        if not self.sequence_code:
            return
        domain = [('sequence_code', '=', self.sequence_code), '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)]
        if self._origin.id:
            domain += [('id', '!=', self._origin.id)]
        picking_type = self.env['stock.picking.type'].search(domain, limit=1)
        if picking_type and picking_type.sequence_id != self.sequence_id:
            return {
                'warning': {
                    'message': _(
                        "This sequence prefix is already being used by another operation type. It is recommended that you select a unique prefix "
                        "to avoid issues and/or repeated reference values or assign the existing reference sequence to this operation type.")
                }
            }

    @api.model
    def action_redirect_to_barcode_installation(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("base.open_module_tree")
        action["context"] = dict(literal_eval(action["context"]), search_default_name="Barcode")
        return action

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        context = {}

        if self:
            action['display_name'] = self.display_name
            context.update({
                'default_picking_type_id': self.id,
                'default_company_id': self.company_id.id,
            })
        else:
            allowed_company_ids = self.env.context.get('allowed_company_ids', [])
            if allowed_company_ids:
                context.update({
                    'default_company_id': allowed_company_ids[0],
                })

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = [('picking_type_id', '=', self.id)]

        action['help'] = self.env['ir.ui.view']._render_template(
            'stock.help_message_template', {
                'picking_type_code': context.get('restricted_picking_type_code') or self.code,
            }
        )

        return action

    def get_action_picking_tree_late(self):
        return self._get_action('stock.action_picking_tree_late')

    def get_action_picking_tree_backorder(self):
        return self._get_action('stock.action_picking_tree_backorder')

    def get_action_picking_tree_waiting(self):
        return self._get_action('stock.action_picking_tree_waiting')

    def get_action_picking_tree_ready(self):
        return self._get_action('stock.action_picking_tree_ready')

    def get_action_picking_type_moves_analysis(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stock.stock_move_action')
        action['domain'] = Domain.AND([
            action['domain'] or [], [('picking_type_id', '=', self.id)]
        ])
        return action

    def get_stock_picking_action_picking_type(self):
        if self.code == 'incoming':
            return self._get_action('stock.action_picking_tree_incoming')
        if self.code == 'outgoing':
            return self._get_action('stock.action_picking_tree_outgoing')
        if self.code == 'internal':
            return self._get_action('stock.action_picking_tree_internal')
        return self._get_action('stock.stock_picking_action_picking_type')

    def get_action_picking_type_ready_moves(self):
        return self._get_action('stock.action_get_picking_type_ready_moves')

    def _get_aggregated_records_by_date(self):
        """
        Returns a list, each element containing 3 values:
        * picking type ID
        * list of date fields values of all pickings with that picking type
        * data series name, used to display it in the graph
        """
        records = self.env['stock.picking']._read_group(
            [
                ('picking_type_id', 'in', self.ids),
                ('state', 'in', ['assigned', 'waiting', 'confirmed'])
            ],
            ['picking_type_id'],
            ['scheduled_date' + ':array_agg'],
        )
        # Make sure that all picking type IDs are represented, even if empty
        picking_type_id_to_dates = {i: [] for i in self.ids}
        picking_type_id_to_dates.update({r[0].id: r[1] for r in records})
        return [(i, d, self.env._('Transfers')) for i, d in picking_type_id_to_dates.items()]

    def _prepare_graph_data(self, summaries):
        """
        Takes in summaries of picking types, each containing the name of the data
        series and categories to display with their corresponding stock picking counts.
        Converts each summary into data suitable for the dashboard graph and assigns
        that data to the corresponding picking type from `self`.

        If all values in a graph are 0, then they are assigned the "sample" type.
        """
        data_category_mapping = {
            'total_before': {'label': _('Before'), 'type': 'past'},
            'total_yesterday': {'label': _('Yesterday'), 'type': 'past'},
            'total_today': {'label': _('Today'), 'type': 'present'},
            'total_day_1': {'label': _('Tomorrow'), 'type': 'future'},
            'total_day_2': {'label': _('The day after tomorrow'), 'type': 'future'},
            'total_after': {'label': _('After'), 'type': 'future'},
        }

        for picking_type in self:
            picking_type_summary = summaries.get(picking_type.id)
            # Graph is empty if all its "total_*" values are 0
            empty = all(picking_type_summary[k] == 0 for k in data_category_mapping)
            graph_data = [{
                'key': _('Sample data') if empty else picking_type_summary['data_series_name'],
                # Passing the picking type ID allows for a redirection after clicking
                'picking_type_id': None if empty else picking_type.id,
                'values': [
                    dict(v, value=picking_type_summary[k], type='sample' if empty else v['type'])
                    for k, v in data_category_mapping.items()
                ],
            }]
            picking_type.kanban_dashboard_graph = json.dumps(graph_data)

    def _get_code_report_name(self):
        self.ensure_one()
        code_names = {
            'outgoing': _('Delivery Note'),
            'incoming': _('Goods Receipt Note'),
            'internal': _('Internal Move'),
        }
        return code_names.get(self.code)


# FILEPATH: odoo/addons/stock/models/stock_picking.py (lines 538-2142)
class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transfer"
    _order = "priority desc, scheduled_date asc, id desc"

    def _default_picking_type_id(self):
        picking_type_code = self.env.context.get('restricted_picking_type_code')
        if picking_type_code:
            picking_types = self.env['stock.picking.type'].search([
                ('code', '=', picking_type_code),
                ('company_id', '=', self.env.company.id),
            ])
            return picking_types[:1].id

    name = fields.Char(
        'Reference', default='/',
        copy=False, index='trigram', readonly=True)
    origin = fields.Char(
        'Source Document', index='trigram',
        help="Reference of the document")
    note = fields.Html('Notes')
    backorder_id = fields.Many2one(
        'stock.picking', 'Back Order of',
        copy=False, index='btree_not_null', readonly=True,
        check_company=True,
        help="If this shipment was split, then this field links to the shipment which contains the already processed part.")
    backorder_ids = fields.One2many('stock.picking', 'backorder_id', 'Back Orders')
    return_id = fields.Many2one('stock.picking', 'Return of', copy=False, index='btree_not_null', readonly=True, check_company=True,
        help="If this picking was created as a return of another picking, this field links to the original picking.")
    return_ids = fields.One2many('stock.picking', 'return_id', 'Returns')
    return_count = fields.Integer('# Returns', compute='_compute_return_count', compute_sudo=False)

    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',
        compute='_compute_move_type', store=True, required=True, readonly=False, precompute=True,
        help="It specifies goods to be deliver partially or all at once")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    reference_ids = fields.Many2many(
        'stock.reference', related="move_ids.reference_ids", string="References", readonly=True)
    priority = fields.Selection(
        PROCUREMENT_PRIORITIES, string='Priority', default='0',
        help="Products will be reserved first for the transfers with the highest priorities.")
    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, default=fields.Datetime.now, tracking=True,
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")
    date_deadline = fields.Datetime(
        "Deadline", compute='_compute_date_deadline', store=True,
        help="In case of outgoing flow, validate the transfer before this date to allow to deliver at promised date to the customer.\n\
        In case of incoming flow, validate the transfer before this date in order to have these products in stock at the date promised by the supplier")
    has_deadline_issue = fields.Boolean(
        "Is late", compute='_compute_has_deadline_issue', store=True, default=False,
        help="Is late or will be late depending on the deadline and scheduled date")
    date_done = fields.Datetime('Date of Transfer', copy=False, help="Date at which the transfer has been processed or cancelled.")
    delay_alert_date = fields.Datetime('Delay Alert Date', compute='_compute_delay_alert_date', search='_search_delay_alert_date')
    json_popover = fields.Char('JSON data for the popover widget', compute='_compute_json_popover')
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        compute="_compute_location_id", store=True, precompute=True, readonly=False,
        check_company=True, required=True)
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        compute="_compute_location_id", store=True, precompute=True, readonly=False,
        check_company=True, required=True)
    move_ids = fields.One2many('stock.move', 'picking_id', string="Stock Moves", copy=True)
    has_scrap_move = fields.Boolean(
        'Has Scrap Moves', compute='_has_scrap_move')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, index=True,
        default=_default_picking_type_id, tracking=True)
    warehouse_address_id = fields.Many2one('res.partner', related='picking_type_id.warehouse_id.partner_id')
    picking_type_code = fields.Selection(
        related='picking_type_id.code',
        readonly=True)
    picking_type_entire_packs = fields.Boolean(related='picking_type_id.show_entire_packs')
    use_create_lots = fields.Boolean(related='picking_type_id.use_create_lots')
    use_existing_lots = fields.Boolean(related='picking_type_id.use_existing_lots')
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        check_company=True, index='btree_not_null')
    company_id = fields.Many2one(
        'res.company', string='Company', related='picking_type_id.company_id',
        readonly=True, store=True, index=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible', tracking=True,
        domain=lambda self: [('all_group_ids', 'in', self.env.ref('stock.group_stock_user').id)],
        default=lambda self: self.env.user, copy=False
    )
    move_line_ids = fields.One2many('stock.move.line', 'picking_id', 'Operations')
    packages_count = fields.Integer('Packages Count', compute='_compute_packages_count')
    package_history_ids = fields.Many2many('stock.package.history', string='Transfered Packages', copy=False)
    show_check_availability = fields.Boolean(
        compute='_compute_show_check_availability',
        help='Technical field used to compute whether the button "Check Availability" should be displayed.')
    show_allocation = fields.Boolean(
        compute='_compute_show_allocation',
        help='Technical Field used to decide whether the button "Allocation" should be displayed.')
    owner_id = fields.Many2one(
        'res.partner', 'Assign Owner',
        check_company=True, index='btree_not_null',
        help="When validating the transfer, the products will be assigned to this owner.")
    printed = fields.Boolean('Printed', copy=False)
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed")
    is_locked = fields.Boolean(default=True, copy=False, help='When the picking is not done this allows changing the '
                               'initial demand. When the picking is done this allows '
                               'changing the done quantities.')
    is_date_editable = fields.Boolean(
        'Is Scheduled Date Editable', compute='_compute_is_date_editable')

    weight_bulk = fields.Float(
        'Bulk Weight', compute='_compute_bulk_weight', help="Total weight of products which are not in a package.")
    shipping_weight = fields.Float(
        "Weight for Shipping", digits="Stock Weight", compute='_compute_shipping_weight', readonly=False, store=True,
        help="Total weight of packages and products not in a package. "
        "Packages with no shipping weight specified will default to their products' total weight. "
        "This is the weight used to compute the cost of the shipping.")
    shipping_volume = fields.Float(
        "Volume for Shipping", compute="_compute_shipping_volume")

    # Used to search on pickings
    product_id = fields.Many2one('product.product', 'Product', related='move_ids.product_id', readonly=True)
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number', related='move_line_ids.lot_id', readonly=True)
    # TODO: delete this field `show_operations`
    show_operations = fields.Boolean(related='picking_type_id.show_operations')
    show_lots_text = fields.Boolean(compute='_compute_show_lots_text')
    has_tracking = fields.Boolean(compute='_compute_has_tracking')
    products_availability = fields.Char(
        string="Product Availability", compute='_compute_products_availability',
        help="Latest product availability status of the picking")
    products_availability_state = fields.Selection([
        ('available', 'Available'),
        ('expected', 'Expected'),
        ('late', 'Late')], compute='_compute_products_availability', search='_search_products_availability_state')

    picking_properties = fields.Properties(
        'Properties',
        definition='picking_type_id.picking_properties_definition',
        copy=True)
    show_next_pickings = fields.Boolean(compute='_compute_show_next_pickings')
    search_date_category = fields.Selection([
        ('before', 'Before'),
        ('yesterday', 'Yesterday'),
        ('today', 'Today'),
        ('day_1', 'Tomorrow'),
        ('day_2', 'The day after tomorrow'),
        ('after', 'After')],
        string='Date Category', store=False,
        search='_search_date_category', readonly=True
    )
    partner_country_id = fields.Many2one('res.country', related='partner_id.country_id')
    picking_warning_text = fields.Text(
        "Picking Instructions",
        help="Internal instructions for the partner or its parent company as set by the user.",
        compute='_compute_picking_warning_text')

    _name_uniq = models.Constraint(
        'unique(name, company_id)',
        'Reference must be unique per company!',
    )

    def _compute_has_tracking(self):
        for picking in self:
            picking.has_tracking = any(m.has_tracking != 'none' for m in picking.move_ids)

    @api.depends('picking_type_id')
    def _compute_move_type(self):
        for record in self:
            record.move_type = record.picking_type_id.move_type

    @api.depends('date_deadline', 'scheduled_date')
    def _compute_has_deadline_issue(self):
        for picking in self:
            picking.has_deadline_issue = picking.date_deadline and picking.date_deadline < picking.scheduled_date or False

    def _search_date_category(self, operator, value):
        if operator != 'in':
            return NotImplemented
        return Domain.OR(
            self.date_category_to_domain('scheduled_date', item)
            for item in value
        )

    @api.depends('move_ids.delay_alert_date')
    def _compute_delay_alert_date(self):
        delay_alert_date_data = self.env['stock.move']._read_group([('id', 'in', self.move_ids.ids), ('delay_alert_date', '!=', False)], ['picking_id'], ['delay_alert_date:max'])
        delay_alert_date_data = {picking.id: delay_alert_date for picking, delay_alert_date in delay_alert_date_data}
        for picking in self:
            picking.delay_alert_date = delay_alert_date_data.get(picking.id, False)

    @api.depends('signature')
    def _compute_is_signed(self):
        for picking in self:
            picking.is_signed = picking.signature

    def _compute_is_date_editable(self):
        for picking in self:
            if picking.state in ['done', 'cancel']:
                picking.is_date_editable = not picking.is_locked
            else:
                picking.is_date_editable = True

    @api.depends('state', 'picking_type_code', 'scheduled_date', 'move_ids', 'move_ids.forecast_availability', 'move_ids.forecast_expected_date')
    def _compute_products_availability(self):
        pickings = self.filtered(lambda picking:
            picking.state in ('waiting', 'confirmed', 'assigned') and
            picking.picking_type_code in ('outgoing', 'internal')
        )
        pickings.products_availability_state = 'available'
        pickings.products_availability = _('Available')
        other_pickings = self - pickings
        other_pickings.products_availability = False
        other_pickings.products_availability_state = False

        all_moves = pickings.move_ids
        # Force to prefetch more than 1000 by 1000
        all_moves._fields['forecast_availability'].compute_value(all_moves)
        for picking in pickings:
            # In case of draft the behavior of forecast_availability is different : if forecast_availability < 0 then there is a issue else not.
            if any(
                move.product_id
                and move.product_id.uom_id.compare(
                    move.forecast_availability, 0 if move.state == 'draft' else move.product_qty
                ) == -1
                for move in picking.move_ids
            ):
                picking.products_availability = _('Not Available')
                picking.products_availability_state = 'late'
            else:
                forecast_date = max(picking.move_ids.filtered('forecast_expected_date').mapped('forecast_expected_date'), default=False)
                if forecast_date:
                    picking.products_availability = _('Exp %s', format_date(self.env, forecast_date))
                    picking.products_availability_state = 'late' if picking.scheduled_date and picking.scheduled_date < forecast_date else 'expected'

    @api.depends('move_line_ids', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'state')
    def _compute_show_lots_text(self):
        group_production_lot_enabled = self.env.user.has_group('stock.group_production_lot')
        for picking in self:
            if not picking.move_line_ids and not picking.picking_type_id.use_create_lots:
                picking.show_lots_text = False
            elif group_production_lot_enabled and picking.picking_type_id.use_create_lots \
                    and not picking.picking_type_id.use_existing_lots and picking.state != 'done':
                picking.show_lots_text = True
            else:
                picking.show_lots_text = False

    def _compute_json_popover(self):
        picking_no_alert = self.filtered(lambda p: p.state in ('done', 'cancel') or not p.delay_alert_date)
        picking_no_alert.json_popover = False
        for picking in (self - picking_no_alert):
            picking.json_popover = json.dumps({
                'popoverTemplate': 'stock.PopoverStockRescheduling',
                'delay_alert_date': format_datetime(self.env, picking.delay_alert_date, dt_format=False),
                'late_elements': [{
                    'id': late_move.id,
                    'name': late_move.display_name,
                    'model': late_move._name,
                } for late_move in picking.move_ids.filtered(lambda m: m.delay_alert_date).move_orig_ids._delay_alert_get_documents()
                ]
            })

    @api.depends('move_type', 'move_ids.state', 'move_ids.picking_id')
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
          - (c) it's an incoming picking
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        picking_moves_state_map = defaultdict(dict)
        picking_move_lines = defaultdict(set)
        for move in self.env['stock.move'].search([('picking_id', 'in', self.ids)]):
            picking_id = move.picking_id
            move_state = move.state
            picking_moves_state_map[picking_id.id].update({
                'any_draft': picking_moves_state_map[picking_id.id].get('any_draft', False) or move_state == 'draft',
                'all_cancel': picking_moves_state_map[picking_id.id].get('all_cancel', True) and move_state == 'cancel',
                'all_cancel_done': picking_moves_state_map[picking_id.id].get('all_cancel_done', True) and move_state in ('cancel', 'done'),
                'all_done_are_scrapped': picking_moves_state_map[picking_id.id].get('all_done_are_scrapped', True) and (move.location_dest_usage == 'inventory' if move_state == 'done' else True),
                'any_cancel_and_not_scrapped': picking_moves_state_map[picking_id.id].get('any_cancel_and_not_scrapped', False) or (move_state == 'cancel' and move.location_dest_usage != 'inventory'),
            })
            picking_move_lines[picking_id.id].add(move.id)
        for picking in self:
            picking_id = (picking.ids and picking.ids[0]) or picking.id
            if not picking_moves_state_map[picking_id] or picking_moves_state_map[picking_id]['any_draft']:
                picking.state = 'draft'
            elif picking_moves_state_map[picking_id]['all_cancel']:
                picking.state = 'cancel'
            elif picking_moves_state_map[picking_id]['all_cancel_done']:
                if picking_moves_state_map[picking_id]['all_done_are_scrapped'] and picking_moves_state_map[picking_id]['any_cancel_and_not_scrapped']:
                    picking.state = 'cancel'
                else:
                    picking.state = 'done'
            else:
                if picking.location_id.should_bypass_reservation() and all(m.procure_method == 'make_to_stock' for m in picking.move_ids):
                    picking.state = 'assigned'
                else:
                    relevant_move_state = self.env['stock.move'].browse(picking_move_lines[picking_id])._get_relevant_state_among_moves()
                    if relevant_move_state == 'partially_available':
                        picking.state = 'assigned'
                    else:
                        picking.state = relevant_move_state

    @api.depends('move_ids.state', 'move_ids.date', 'move_type')
    def _compute_scheduled_date(self):
        for picking in self:
            if not picking.id:
                continue
            moves_dates = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel')).mapped('date')
            if picking.move_type == 'direct':
                picking.scheduled_date = min(moves_dates, default=picking.scheduled_date or fields.Datetime.now())
            else:
                picking.scheduled_date = max(moves_dates, default=picking.scheduled_date or fields.Datetime.now())

    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.product_uom_id', 'move_line_ids.quantity')
    def _compute_bulk_weight(self):
        picking_weights = defaultdict(float)
        res_groups = self.env['stock.move.line']._read_group(
            [('picking_id', 'in', self.ids), ('product_id', '!=', False), ('result_package_id', '=', False)],
            ['picking_id', 'product_id', 'product_uom_id', 'quantity'],
            ['__count'],
        )
        for picking, product, product_uom, quantity, count in res_groups:
            picking_weights[picking.id] += (
                count
                * product_uom._compute_quantity(quantity, product.uom_id)
                * product.weight
            )
        for picking in self:
            picking.weight_bulk = picking_weights[picking.id]

    @api.depends('move_line_ids.result_package_id', 'move_line_ids.result_package_id.shipping_weight', 'move_line_ids.result_package_id.outermost_package_id.shipping_weight', 'weight_bulk')
    def _compute_shipping_weight(self):
        for picking in self:
            # if shipping weight is not assigned => default to calculated product weight
            shipping_weight = picking.weight_bulk
            relevant_packages = picking.move_line_ids.result_package_id.outermost_package_id
            packages_weight = relevant_packages.sudo()._get_weight(picking.id)
            for package in relevant_packages:
                if package.shipping_weight:
                    shipping_weight += package.shipping_weight
                else:
                    shipping_weight += packages_weight.get(package, 0)
            picking.shipping_weight = shipping_weight

    def _compute_shipping_volume(self):
        for picking in self:
            volume = 0
            for move in picking.move_ids:
                volume += move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id) * move.product_id.volume
            picking.shipping_volume = volume

    @api.depends('move_ids.date_deadline', 'move_type')
    def _compute_date_deadline(self):
        for picking in self:
            if picking.move_type == 'direct':
                picking.date_deadline = min(picking.move_ids.filtered('date_deadline').mapped('date_deadline'), default=False)
            else:
                picking.date_deadline = max(picking.move_ids.filtered('date_deadline').mapped('date_deadline'), default=False)

    def _set_scheduled_date(self):
        for picking in self:
            if picking.state == 'cancel':
                raise UserError(_("You cannot change the Scheduled Date on a cancelled transfer."))
            if picking.state == 'done':
                continue
            picking.move_ids.write({'date': picking.scheduled_date})

    def _has_scrap_move(self):
        result = {
            picking
            for [picking] in self.env['stock.move']._read_group(
                [('picking_id', 'in', self.ids), ('location_dest_usage', '=', 'inventory')],
                ['picking_id'],
            )
        }
        for picking in self:
            picking.has_scrap_move = picking._origin in result

    def _compute_packages_count(self):
        done_pickings = self.filtered(lambda picking: picking.state == 'done')
        other_pickings = self - done_pickings

        packages_by_pick = defaultdict(int)
        # Cannot _read_group() as picking_ids isn't stored, nor grouped() because multiple pickings per package
        packages = self.env['stock.package'].search([('picking_ids', 'in', other_pickings.ids)])
        for pack in packages:
            for picking in pack.picking_ids:
                packages_by_pick[picking] += 1

        histories_by_pick = self.env['stock.package.history']._read_group([
            ('picking_ids', 'in', done_pickings.ids)], ['picking_ids'], ['__count'])
        histories_by_pick = dict(histories_by_pick)

        for picking in done_pickings:
            picking.packages_count = histories_by_pick.get(picking, 0)
        for picking in other_pickings:
            picking.packages_count = packages_by_pick.get(picking, 0)

    @api.depends('state', 'move_ids.product_uom_qty', 'picking_type_code')
    def _compute_show_check_availability(self):
        """ According to `picking.show_check_availability`, the "check availability" button will be
        displayed in the form view of a picking.
        """
        for picking in self:
            if picking.state not in ('confirmed', 'waiting', 'assigned'):
                picking.show_check_availability = False
                continue
            if all(m.picked or m.product_uom_qty == m.quantity for m in picking.move_ids):
                picking.show_check_availability = False
                continue
            picking.show_check_availability = any(
                move.state in ('waiting', 'confirmed', 'partially_available') and
                move.product_uom.compare(move.product_uom_qty, 0)
                for move in picking.move_ids
            )

    @api.depends('state', 'move_ids', 'picking_type_id')
    def _compute_show_allocation(self):
        self.show_allocation = False
        if not self.env.user.has_group('stock.group_reception_report'):
            return
        for picking in self:
            picking.show_allocation = picking._get_show_allocation(picking.picking_type_id)

    @api.depends('picking_type_id', 'partner_id')
    def _compute_location_id(self):
        for picking in self:
            if picking.state in ('cancel', 'done') or picking.return_id:
                continue
            picking = picking.with_company(picking.company_id)
            if picking.picking_type_id:
                location_src = picking.picking_type_id.default_location_src_id
                if location_src.usage == 'supplier' and picking.partner_id:
                    location_src = picking.partner_id.property_stock_supplier
                location_dest = picking.picking_type_id.default_location_dest_id
                if location_dest.usage == 'customer' and picking.partner_id:
                    location_dest = picking.partner_id.property_stock_customer
                picking.location_id = location_src.id
                picking.location_dest_id = location_dest.id

    @api.depends('return_ids')
    def _compute_return_count(self):
        for picking in self:
            picking.return_count = len(picking.return_ids)

    @api.depends('partner_id.name', 'partner_id.parent_id.name')
    def _compute_picking_warning_text(self):
        if not self.env.user.has_group('stock.group_warning_stock'):
            self.picking_warning_text = ''
            return
        for picking in self:
            text = ''
            if partner_msg := picking.partner_id.picking_warn_msg:
                text += partner_msg + '\n'
            if parent_msg := picking.partner_id.parent_id.picking_warn_msg:
                text += parent_msg + '\n'
            picking.picking_warning_text = text

    def _get_next_transfers(self):
        next_pickings = self.move_ids.move_dest_ids.picking_id
        return next_pickings.filtered(lambda p: p not in self.return_ids)

    @api.depends('move_ids.move_dest_ids')
    def _compute_show_next_pickings(self):
        self.show_next_pickings = len(self._get_next_transfers()) != 0

    def _search_products_availability_state(self, operator, value):
        if operator != 'in':
            return NotImplemented

        invalid_states = ('done', 'cancel', 'draft')
        if False in value:
            return ['|', ('state', 'in', invalid_states), *self._search_products_availability_state('in', value - {False})]
        value = set(self._fields['products_availability_state'].get_values(self.env)) & value
        if not value:
            return Domain.FALSE

        def _get_comparison_date(move):
            return move.picking_id.scheduled_date

        def _filter_picking_moves(picking):
            try:
                return picking.move_ids._match_searched_availability(operator, value, _get_comparison_date)
            except UserError:
                # invalid value for search
                return False

        pickings = self.env['stock.picking'].search([('state', 'not in', invalid_states)], order='id').filtered(_filter_picking_moves)
        return Domain('id', 'in', pickings.ids)

    def _get_show_allocation(self, picking_type_id):
        """ Helper method for computing "show_allocation" value.
        Separated out from _compute function so it can be reused in other models (e.g. batch).
        """
        if not picking_type_id or picking_type_id.code == 'outgoing':
            return False
        lines = self.move_ids.filtered(lambda m: m.product_id.is_storable and m.state != 'cancel')
        if lines:
            allowed_states = ['confirmed', 'partially_available', 'waiting']
            if self[0].state == 'done':
                allowed_states += ['assigned']
            wh_location_ids = self.env['stock.location']._search([('id', 'child_of', picking_type_id.warehouse_id.view_location_id.id), ('usage', '!=', 'supplier')])
            if self.env['stock.move'].search_count([
                ('state', 'in', allowed_states),
                ('product_qty', '>', 0),
                ('location_id', 'in', wh_location_ids),
                ('picking_id', 'not in', self.ids),
                ('product_id', 'in', lines.product_id.ids),
                '|', ('move_orig_ids', '=', False),
                     ('move_orig_ids', 'in', lines.ids)], limit=1):
                return True

    @api.model
    def get_empty_list_help(self, help_message):
        return self.env['ir.ui.view']._render_template(
            'stock.help_message_template', {
                'picking_type_code': self.env.context.get('restricted_picking_type_code') or self.picking_type_code,
            }
        )

    @api.model
    def _search_delay_alert_date(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS:
            return NotImplemented
        return [('move_ids.delay_alert_date', operator, value)]

    @api.onchange('picking_type_id', 'partner_id')
    def _onchange_picking_type(self):
        if self.picking_type_id and self.state == 'draft':
            self = self.with_company(self.company_id)
            self.move_ids.filtered(
                lambda m: m.picking_type_id != self.picking_type_id
            ).picking_type_id = self.picking_type_id
            self.move_ids.company_id = self.company_id

    @api.onchange('location_id')
    def _onchange_location_id(self):
        self.move_ids.location_id = self.location_id
        for move in self.move_ids.filtered(lambda m: m.move_orig_ids):
            for ml in move.move_line_ids:
                parent_path = [int(loc_id) for loc_id in ml.location_id.parent_path.split('/')[:-1]]
                if self.location_id.id not in parent_path:
                    return {'warning': {
                            'title': _("Warning: change source location"),
                            'message': _("Updating the location of this transfer will result in unreservation of the currently assigned items. "
                                         "An attempt to reserve items at the new location will be made and the link with preceding transfers will be discarded.\n\n"
                                         "To avoid this, please discard the source location change before saving.")
                        }
                    }

    @api.model_create_multi
    def create(self, vals_list):
        scheduled_dates = []
        for vals in vals_list:
            defaults = self.default_get(['name', 'picking_type_id'])
            picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id')))
            if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
                if picking_type.sequence_id:
                    vals['name'] = picking_type.sequence_id.next_by_id()

            # make sure to write `schedule_date` *after* the `stock.move` creation in
            # order to get a determinist execution of `_set_scheduled_date`
            scheduled_dates.append(vals.pop('scheduled_date', False))

        pickings = super().create(vals_list)

        for picking, scheduled_date in zip(pickings, scheduled_dates):
            if scheduled_date:
                picking.with_context(mail_notrack=True).write({'scheduled_date': scheduled_date})
        pickings._autoconfirm_picking()

        return pickings

    def write(self, vals):
        if vals.get('picking_type_id') and any(picking.state in ('done', 'cancel') for picking in self):
            raise UserError(_("Changing the operation type of this record is forbidden at this point."))
        if vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
            for picking in self:
                if picking.picking_type_id != picking_type:
                    picking.name = picking_type.sequence_id.next_by_id()
                    vals['location_id'] = picking_type.default_location_src_id.id
                    vals['location_dest_id'] = picking_type.default_location_dest_id.id
        res = super().write(vals)
        if vals.get('date_done'):
            self.filtered(lambda p: p.state == 'done').move_ids.date = vals['date_done']
        if vals.get('signature'):
            for picking in self:
                picking._attach_sign()
        # Change locations of moves if those of the picking change
        after_vals = {}
        if vals.get('location_id'):
            after_vals['location_id'] = vals['location_id']
        if vals.get('location_dest_id'):
            after_vals['location_dest_id'] = vals['location_dest_id']
        if 'partner_id' in vals:
            after_vals['partner_id'] = vals['partner_id']
        if after_vals:
            self.move_ids.filtered(lambda move: move.location_dest_usage != 'inventory').write(after_vals)
        if vals.get('move_ids'):
            self._autoconfirm_picking()

        return res

    def unlink(self):
        self.move_ids._action_cancel()
        self.with_context(prefetch_fields=False).move_ids.unlink()  # Checks if moves are not done
        return super().unlink()

    def do_print_picking(self):
        self.write({'printed': True})
        return self.env.ref('stock.action_report_picking').report_action(self)

    def should_print_delivery_address(self):
        self.ensure_one()
        return self.move_ids and (self.move_ids[0].partner_id or self.partner_id) and self._is_to_external_location()

    def _is_to_external_location(self):
        self.ensure_one()
        return self.picking_type_code == 'outgoing'

    def action_confirm(self):
        self._check_company()
        # call `_action_confirm` on every draft move
        self.move_ids.filtered(lambda move: move.state == 'draft')._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.move_ids.filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        return True

    def action_assign(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.move_ids.filtered(lambda move: move.state not in ('draft', 'cancel', 'done')).sorted(
            key=lambda move: (-int(move.priority), not bool(move.date_deadline), move.date_deadline, move.date, move.id)
        )
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        moves._action_assign()
        return True

    def action_cancel(self):
        self.move_ids._action_cancel()
        self.write({'is_locked': True})
        self.filtered(lambda x: not x.move_ids).state = 'cancel'
        return True

    def action_detailed_operations(self):
        view_id = self.env.ref('stock.view_stock_move_line_detailed_operation_tree').id
        return {
            'name': _('Detailed Operations'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line',
            'views': [(view_id, 'list')],
            'domain': [('id', 'in', self.move_line_ids.ids)],
            'context': {
                'sml_specific_default': True,
                'default_picking_id': self.id,
                'default_location_id': self.location_id.id,
                'default_location_dest_id': self.location_dest_id.id,
                'default_company_id': self.company_id.id,
                'show_lots_text': self.show_lots_text,
                'picking_code': self.picking_type_code,
                'create': self.state not in ('done', 'cancel'),
            }
        }

    def action_next_transfer(self):
        next_transfers = self._get_next_transfers()

        if len(next_transfers) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "views": [[False, "form"]],
                "res_id": next_transfers.id
            }
        return {
            'name': _('Next Transfers'),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "list"], [False, "form"]],
            "domain": [('id', 'in', next_transfers.ids)],
        }

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.move_ids.filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_ids.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

        # if incoming/internal moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code in ('incoming', 'internal')).move_ids.filtered(lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True

    def _send_confirmation_email(self):
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
        for stock_pick in self.filtered(lambda p: p.company_id.stock_move_email_validation and p.picking_type_id.code == 'outgoing'):
            delivery_template = stock_pick.company_id.stock_mail_confirmation_template_id
            stock_pick.with_context(force_send=True).message_post_with_source(
                delivery_template,
                email_layout_xmlid='mail.mail_notification_light',
                subtype_id=subtype_id,
            )

    def _check_move_lines_map_quant_package(self, package):
        return package._check_move_lines_map_quant(self.move_line_ids.filtered(lambda ml:
            ml.product_id.is_storable
            and (ml.package_id == package or ml.package_id in package.all_children_package_ids)))

    def _get_entire_pack_location_dest(self, move_line_ids):
        location_dest_ids = move_line_ids.mapped('location_dest_id')
        if len(location_dest_ids) > 1:
            return False
        return location_dest_ids.id

    def _is_single_transfer(self):
        # Overriden for batches.
        return len(self) == 1

    def _check_entire_pack(self):
        """ This function check if entire packs are moved in the picking"""
        for package in self.move_line_ids.package_id:
            pickings = self.move_line_ids.filtered(lambda ml: ml.package_id == package).picking_id
            if pickings._is_single_transfer() and pickings._check_move_lines_map_quant_package(package):
                move_lines_to_pack = pickings.move_line_ids.filtered(lambda ml: ml.package_id == package and not ml.result_package_id and ml.state not in ('done', 'cancel'))
                if package.package_type_id.package_use != 'reusable':
                    move_lines_to_pack.write({
                        'result_package_id': package.id,
                        'is_entire_pack': True,
                    })
        # If we move all packages within a package, we can consider that they keep their container as well
        self.move_line_ids.result_package_id._apply_package_dest_for_entire_packs()

    def _get_lot_move_lines_for_sanity_check(self, none_done_picking_ids, separate_pickings=True):
        """ Get all move_lines with tracked products that need to be checked over in the sanity check.
            :param none_done_picking_ids: Set of all pickings ids that have no quantity set on any move_line.
            :param separate_pickings: Indicates if pickings should be checked independently for lot/serial numbers or not.
        """
        def get_relevant_move_line_ids(none_done_picking_ids, picking):
            # Get all move_lines if picking has no quantity set, otherwise only get the move_lines with some quantity set.
            if picking.id in none_done_picking_ids:
                return picking.move_line_ids.filtered(lambda ml: ml.product_id and ml.product_id.tracking != 'none').ids
            else:
                return get_line_with_done_qty_ids(picking.move_line_ids)

        def get_line_with_done_qty_ids(move_lines):
            # Get only move_lines that has some quantity set.
            return move_lines.filtered(lambda ml: ml.product_id and ml.product_id.tracking != 'none' and ml.picked and ml.product_uom_id.compare(ml.quantity, 0)).ids

        if separate_pickings:
            # If pickings are checked independently, get full/partial move_lines depending if each picking has no quantity set.
            lines_to_check_ids = [line_id for picking in self for line_id in get_relevant_move_line_ids(none_done_picking_ids, picking)]
        else:
            # If pickings are checked as one (like in a batch), then get only the move_lines with quantity across all pickings if there is at least one.
            if any(picking.id not in none_done_picking_ids for picking in self):
                lines_to_check_ids = get_line_with_done_qty_ids(self.move_line_ids)
            else:
                lines_to_check_ids = self.move_line_ids.filtered(lambda ml: ml.product_id and ml.product_id.tracking != 'none').ids

        return self.env['stock.move.line'].browse(lines_to_check_ids)

    def _sanity_check(self, separate_pickings=True):
        """ Sanity check for `button_validate()`
            :param separate_pickings: Indicates if pickings should be checked independently for lot/serial numbers or not.
        """
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        pickings_without_moves = self.filtered(lambda p: not p.move_ids and not p.move_line_ids)
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit')

        no_quantities_done_ids = set()
        pickings_without_quantities = self.env['stock.picking']
        for picking in self:
            has_pick = any(move.picked and move.state not in ('done', 'cancel') for move in picking.move_ids)
            if all(float_is_zero(move.quantity, precision_digits=precision_digits) for move in picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel') and (not has_pick or m.picked))):
                pickings_without_quantities |= picking

        pickings_using_lots = self.filtered(lambda p: p.picking_type_id.use_create_lots or p.picking_type_id.use_existing_lots)
        if pickings_using_lots:
            lines_to_check = pickings_using_lots._get_lot_move_lines_for_sanity_check(no_quantities_done_ids, separate_pickings)
            for line in lines_to_check:
                if not line.lot_name and not line.lot_id:
                    pickings_without_lots |= line.picking_id
                    products_without_lots |= line.product_id

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_("You can’t validate an empty transfer. Please add some products to move before proceeding."))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.', ', '.join(products_without_lots.mapped('display_name'))))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.', ', '.join(pickings_without_moves.mapped('name')))
            if pickings_without_lots:
                message += _(
                    '\n\nTransfers %(transfer_list)s: You need to supply a Lot/Serial number for products %(product_list)s.',
                    transfer_list=pickings_without_lots.mapped('name'),
                    product_list=products_without_lots.mapped('display_name'),
                )
            if message:
                raise UserError(message.lstrip())

    def do_unreserve(self):
        self.move_ids._do_unreserve()

    def button_validate(self):
        self = self.filtered(lambda p: p.state != 'done')
        draft_picking = self.filtered(lambda p: p.state == 'draft')
        draft_picking.action_confirm()
        for move in draft_picking.move_ids:
            if move.product_uom.is_zero(move.quantity) and not move.product_uom.is_zero(move.product_uom_qty):
                move.quantity = move.product_uom_qty

        # Sanity checks.
        if not self.env.context.get('skip_sanity_check', False):
            self._sanity_check()

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                lambda p: p.picking_type_id.create_backorder != 'always'
            )
        pickings_to_backorder = self - pickings_not_to_backorder
        if pickings_not_to_backorder:
            pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        if pickings_to_backorder:
            pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        report_actions = self._get_autoprint_report_actions()
        another_action = False
        if self.env.user.has_group('stock.group_reception_report'):
            pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
            lines = pickings_show_report.move_ids.filtered(lambda m: m.product_id.is_storable and m.state != 'cancel' and m.quantity and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search([('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids), ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search_count([
                        ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                        ('product_qty', '>', 0),
                        ('location_id', 'in', wh_location_ids),
                        ('move_orig_ids', '=', False),
                        ('picking_id', 'not in', pickings_show_report.ids),
                        ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = pickings_show_report.action_view_reception_report()
                    action['context'] = {'default_picking_ids': pickings_show_report.ids}
                    if not report_actions:
                        return action
                    another_action = action
        if report_actions:
            return {
                'type': 'ir.actions.client',
                'tag': 'do_multi_print',
                'params': {
                    'reports': report_actions,
                    'anotherAction': another_action,
                }
            }
        return True

    def action_split_transfer(self):
        if all(m.product_uom.is_zero(m.quantity) for m in self.move_ids):
            raise UserError(_("%s: Nothing to split. Fill the quantities you want in a new transfer in the done quantities", self.display_name))
        if all(m.product_uom.compare(m.quantity, m.product_uom_qty) == 0 for m in self.move_ids):
            raise UserError(_("%s: Nothing to split, all demand is done. For split you need at least one line not fully fulfilled", self.display_name))
        if any(m.product_uom.compare(m.quantity, m.product_uom_qty) > 0 for m in self.move_ids):
            raise UserError(_("%s: Can't split: quantities done can't be above demand", self.display_name))

        moves = self.move_ids.filtered(lambda m: m.state not in ('done', 'cancel') and m.quantity != 0)
        backorder_moves = moves._create_backorder()
        backorder_moves += self.move_ids.filtered(lambda m: m.quantity == 0)
        self._create_backorder(backorder_moves=backorder_moves)

    def _pre_action_done_hook(self):
        for picking in self:
            has_quantity = False
            has_pick = False
            for move in picking.move_ids:
                if move.quantity:
                    has_quantity = True
                if move.location_dest_usage == 'inventory':
                    continue
                if move.picked:
                    has_pick = True
                if has_quantity and has_pick:
                    break
            if has_quantity and not has_pick:
                picking.move_ids.picked = True
        if not self.env.context.get('skip_backorder'):
            pickings_to_backorder = self._check_backorder()
            if pickings_to_backorder:
                return pickings_to_backorder._action_generate_backorder_wizard(show_transfers=self._should_show_transfers())
        return True

    def _should_show_transfers(self):
        """Whether the different transfers should be displayed on the pre action done wizards."""
        return len(self) > 1

    def _should_ignore_backorders(self):
        """ Checks if the `create_backorder` setting from the picking type should be ignored.
        """
        return bool(self.return_id)

    def _get_without_quantities_error_message(self):
        """ Returns the error message raised in validation if no quantities are reserved.
        The purpose of this method is to be overridden in case we want to adapt this message.

        :return: Translated error message
        :rtype: str
        """
        return _(
            "Transfer trouble alert! Validating a zero quantity transfer? You're not moving invisible goods around are you?\n"
            "Set some quantities and let's get moving!"
        )

    def _action_generate_backorder_wizard(self, show_transfers=False):
        view = self.env.ref('stock.view_backorder_confirmation')
        return {
            'name': _('Create Backorder?'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.backorder.confirmation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': dict(self.env.context, default_show_transfers=show_transfers, default_pick_ids=[(4, p.id) for p in self]),
        }

    def action_toggle_is_locked(self):
        self.ensure_one()
        self.is_locked = not self.is_locked
        return True

    def _check_backorder(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit")
        backorder_pickings = self.browse()
        for picking in self:
            if picking.picking_type_id.create_backorder != 'ask':
                continue
            if any(
                    (move.product_uom_qty and not move.picked) or
                    float_compare(move._get_picked_quantity(), move.product_uom_qty, precision_digits=prec) < 0
                    for move in picking.move_ids
                    if move.state != 'cancel'
            ):
                backorder_pickings |= picking
        return backorder_pickings

    def _autoconfirm_picking(self):
        """ Automatically run `action_confirm` on `self` if one of the
        picking's move was added after the initial
        call to `action_confirm`. Note that `action_confirm` will only work on draft moves.
        """
        for picking in self:
            if picking.state in ('done', 'cancel'):
                continue
            if not picking.move_ids:
                continue
            if any(move.additional for move in picking.move_ids):
                picking.action_confirm()
        to_confirm = self.move_ids.filtered(lambda m: m.state == 'draft' and m.quantity)
        to_confirm._action_confirm()

    def _get_moves_to_backorder(self):
        self.ensure_one()
        return self.move_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

    def _create_backorder_picking(self):
        self.ensure_one()
        return self.copy({
            'name': '/',
            'move_ids': [],
            'move_line_ids': [],
            'backorder_id': self.id,
        })

    def _create_backorder(self, backorder_moves=None):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']
        for picking in self:
            if backorder_moves:
                moves_to_backorder = backorder_moves.filtered(lambda m: m.picking_id == picking)
            else:
                moves_to_backorder = picking._get_moves_to_backorder()
            moves_to_backorder._recompute_state()
            if moves_to_backorder:
                backorder_picking = picking._create_backorder_picking()
                moves_to_backorder.write({'picking_id': backorder_picking.id, 'picked': False})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                backorders |= backorder_picking
                backorder_picking.user_id = False
                picking.message_post(
                    body=_('The backorder %s has been created.', backorder_picking._get_html_link())
                )
                if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                    bo_to_assign |= backorder_picking
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders

    def _log_activity_get_documents(self, orig_obj_changes, stream_field, stream, groupby_method=False):
        """ Generic method to log activity. To use with
        _log_activity method. It either log on uppermost
        ongoing documents or following documents. This method
        find all the documents and responsible for which a note
        has to be log. It also generate a rendering_context in
        order to render a specific note by documents containing
        only the information relative to the document it. For example
        we don't want to notify a picking on move that it doesn't
        contain.

        :param dict orig_obj_changes: contain a record as key and the
            change on this record as value.
            eg: {'move_id': (new product_uom_qty, old product_uom_qty)}
        :param str stream_field: It has to be a field of the
            records that are register in the key of 'orig_obj_changes'
            eg: 'move_dest_ids' if we use move as record (previous example)
                - 'UP' if we want to log on the upper most ongoing
                documents.
                - 'DOWN' if we want to log on following documents.
        :param str stream: ``'UP'`` or ``'DOWN'``
        :param groupby_method: Only need when
            stream is 'DOWN', it should group by tuple(object on
            which the activity is log, the responsible for this object)
        """
        if self.env.context.get('skip_activity'):
            return {}
        move_to_orig_object_rel = {co: ooc for ooc in orig_obj_changes.keys() for co in ooc[stream_field]}
        origin_objects = self.env[list(orig_obj_changes.keys())[0]._name].concat(*list(orig_obj_changes.keys()))
        # The purpose here is to group each destination object by
        # (document to log, responsible) no matter the stream direction.
        # example:
        # {'(delivery_picking_1, admin)': stock.move(1, 2)
        #  '(delivery_picking_2, admin)': stock.move(3)}
        visited_documents = {}
        if stream == 'DOWN':
            if groupby_method:
                grouped_moves = groupby(origin_objects.mapped(stream_field), key=groupby_method)
            else:
                raise AssertionError('You have to define a groupby method and pass them as arguments.')
        elif stream == 'UP':
            # When using upstream document it is required to define
            # _get_upstream_documents_and_responsibles on
            # destination objects in order to ascend documents.
            grouped_moves = {}
            for visited_move in origin_objects.mapped(stream_field):
                for document, responsible, visited in visited_move._get_upstream_documents_and_responsibles(self.env[visited_move._name]):
                    if grouped_moves.get((document, responsible)):
                        grouped_moves[(document, responsible)] |= visited_move
                        visited_documents[(document, responsible)] |= visited
                    else:
                        grouped_moves[(document, responsible)] = visited_move
                        visited_documents[(document, responsible)] = visited
            grouped_moves = grouped_moves.items()
        else:
            raise AssertionError('Unknown stream.')

        documents = {}
        for (parent, responsible), moves in grouped_moves:
            if not parent:
                continue
            moves = self.env[moves[0]._name].concat(*moves)
            # Get the note
            rendering_context = {move: (orig_object, orig_obj_changes[orig_object]) for move in moves for orig_object in move_to_orig_object_rel[move]}
            if visited_documents:
                documents[(parent, responsible)] = rendering_context, visited_documents.values()
            else:
                documents[(parent, responsible)] = rendering_context
        return documents

    def _log_activity(self, render_method, documents):
        """ Log a note for each documents, responsible pair in
        documents passed as argument. The render_method is then
        call in order to use a template and render it with a
        rendering_context.

        :param dict documents: A tuple (document, responsible) as key.
            An activity will be log by key. A rendering_context as value.
            If used with _log_activity_get_documents. In 'DOWN' stream
            cases the rendering_context will be a dict with format:
            {'stream_object': ('orig_object', new_qty, old_qty)}
            'UP' stream will add all the documents browsed in order to
            get the final/upstream document present in the key.
        :param callable render_method: a static function that will generate
            the html note to log on the activity. The render_method should
            use the args:
                - rendering_context dict: value of the documents argument
            the render_method should return a string with an html format
        """
        for (parent, responsible), rendering_context in documents.items():
            note = render_method(rendering_context)
            parent.sudo().activity_schedule(
                'mail.mail_activity_data_warning',
                date.today(),
                note=note,
                user_id=responsible.id,
            )

    def _log_less_quantities_than_expected(self, moves):
        """ Log an activity on picking that follow moves. The note
        contains the moves changes and all the impacted picking.

        :param dict moves: a dict with a move as key and tuple with
        new and old quantity as value. eg: {move_1 : (4, 5)}
        """
        def _keys_in_groupby(move):
            """ group by picking and the responsible for the product the
            move.
            """
            return (move.picking_id, move.product_id.responsible_id)

        def _render_note_exception_quantity(rendering_context):
            """ :param rendering_context:
            {'move_dest': (move_orig, (new_qty, old_qty))}
            """
            origin_moves = self.env['stock.move'].browse([move.id for move_orig in rendering_context.values() for move in move_orig[0]])
            origin_picking = origin_moves.mapped('picking_id')
            move_dest_ids = self.env['stock.move'].concat(*rendering_context.keys())
            impacted_pickings = origin_picking._get_impacted_pickings(move_dest_ids) - move_dest_ids.mapped('picking_id')
            values = {
                'origin_picking': origin_picking,
                'moves_information': rendering_context.values(),
                'impacted_pickings': impacted_pickings,
            }
            return self.env['ir.qweb']._render('stock.exception_on_picking', values)

        documents = self._log_activity_get_documents(moves, 'move_dest_ids', 'DOWN', _keys_in_groupby)
        documents = self._less_quantities_than_expected_add_documents(moves, documents)
        self._log_activity(_render_note_exception_quantity, documents)

    def _less_quantities_than_expected_add_documents(self, moves, documents):
        return documents

    def _get_impacted_pickings(self, moves):
        """ This function is used in _log_less_quantities_than_expected
        the purpose is to notify a user with all the pickings that are
        impacted by an action on a chained move.
        param: 'moves' contain moves that belong to a common picking.
        return: all the pickings that contain a destination moves
        (direct and indirect) from the moves given as arguments.
        """

        def _explore(impacted_pickings, explored_moves, moves_to_explore):
            for move in moves_to_explore:
                if move not in explored_moves:
                    impacted_pickings |= move.picking_id
                    explored_moves |= move
                    moves_to_explore |= move.move_dest_ids
            moves_to_explore = moves_to_explore - explored_moves
            if moves_to_explore:
                return _explore(impacted_pickings, explored_moves, moves_to_explore)
            else:
                return impacted_pickings

        return _explore(self.env['stock.picking'], self.env['stock.move'], moves)

    def action_put_in_pack(self, *, package_id=False, package_type_id=False, package_name=False):
        self.ensure_one()
        if self.env.context.get('sml_specific_default'):
            self = self.with_context(clean_context(self.env.context))
        if self.state not in ('done', 'cancel'):
            return self.move_line_ids.action_put_in_pack(package_id=package_id, package_type_id=package_type_id, package_name=package_name)

    @api.model
    def get_action_click_graph(self):
        return self._get_action("stock.action_picking_tree_graph")

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        context = dict(self.env.context)
        context.update(literal_eval(action['context']))
        action['context'] = context

        action['help'] = self.env['ir.ui.view']._render_template(
            'stock.help_message_template', {
                'picking_type_code': context.get('restricted_picking_type_code') or self.picking_type_code,
            }
        )

        return action

    @api.model
    def get_action_picking_tree_incoming(self):
        return self._get_action('stock.action_picking_tree_incoming')

    @api.model
    def get_action_picking_tree_outgoing(self):
        return self._get_action('stock.action_picking_tree_outgoing')

    @api.model
    def get_action_picking_tree_internal(self):
        return self._get_action('stock.action_picking_tree_internal')

    @api.model
    def calculate_date_category(self, datetime):
        """
        Assigns given datetime to one of the following categories:
        - "before"
        - "yesterday"
        - "today"
        - "day_1" (tomorrow)
        - "day_2" (the day after tomorrow)
        - "after"

        The categories are based on current user's timezone (e.g. "today" will last
        between 00:00 and 23:59 local time). The datetime itself is assumed to be
        in UTC. If the datetime is falsy, this function returns "".
        """
        start_today = fields.Datetime.context_timestamp(
            self.env.user, fields.Datetime.now()
        ).replace(hour=0, minute=0, second=0, microsecond=0)

        start_yesterday = start_today + timedelta(days=-1)
        start_day_1 = start_today + timedelta(days=1)
        start_day_2 = start_today + timedelta(days=2)
        start_day_3 = start_today + timedelta(days=3)

        date_category = ""

        if datetime:
            datetime = datetime.astimezone(pytz.UTC)
            if datetime < start_yesterday:
                date_category = "before"
            elif datetime >= start_yesterday and datetime < start_today:
                date_category = "yesterday"
            elif datetime >= start_today and datetime < start_day_1:
                date_category = "today"
            elif datetime >= start_day_1 and datetime < start_day_2:
                date_category = "day_1"
            elif datetime >= start_day_2 and datetime < start_day_3:
                date_category = "day_2"
            else:
                date_category = "after"

        return date_category

    @api.model
    def date_category_to_domain(self, field_name, date_category):
        """
        Given a date category, returns a list of tuples of operator and value
        that can be used in a domain to filter records based on their scheduled date.

        Args:
            date_category (str): The date category to use for the computation.
                Allowed values are:
                * "before"
                * "yesterday"
                * "today"
                * "day_1"
                * "day_2"
                * "after"

        Returns:
            a list of tuples:
                each tuple consists of an operator and a value that can be used in
                a domain to filter records based on their scheduled date.
                The operator can be "<" or ">=". The value is a datetime object.
                If an incorrect date category is passed, this method returns None.
        """
        start_today = fields.Datetime.context_timestamp(
            self.env.user, fields.Datetime.now()
        ).replace(hour=0, minute=0, second=0, microsecond=0)

        start_today = start_today.astimezone(pytz.UTC).replace(tzinfo=None)

        start_yesterday = start_today + timedelta(days=-1)
        start_day_1 = start_today + timedelta(days=1)
        start_day_2 = start_today + timedelta(days=2)
        start_day_3 = start_today + timedelta(days=3)

        date_category_to_search_domain = {
            "before": [(field_name, "<", start_yesterday)],
            "yesterday": [(field_name, ">=", start_yesterday), (field_name, "<", start_today)],
            "today": [(field_name, ">=", start_today), (field_name, "<", start_day_1)],
            "day_1": [(field_name, ">=", start_day_1), (field_name, "<", start_day_2)],
            "day_2": [(field_name, ">=", start_day_2), (field_name, "<", start_day_3)],
            "after": [(field_name, ">=", start_day_3)],
        }

        return date_category_to_search_domain.get(date_category)

    def button_scrap(self):
        self.ensure_one()
        view = self.env.ref('stock.stock_scrap_form_view2')
        products = self.env['product.product']
        for move in self.move_ids:
            if move.state not in ('draft', 'cancel') and move.product_id.type == 'consu':
                products |= move.product_id
        return {
            'name': _('Scrap Products'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {'default_picking_id': self.id, 'product_ids': products.ids, 'default_company_id': self.company_id.id},
            'target': 'new',
        }

    def action_add_entire_packs(self, package_ids):
        self.ensure_one()
        if self.state not in ('done', 'cancel'):
            all_packages = self.env['stock.package'].search([('id', 'child_of', package_ids)])
            all_package_ids = set(all_packages.ids)
            # Remove existing move lines that already pulled from these packages, as using them fully now.
            self.move_line_ids.filtered(lambda ml: ml.package_id.id in all_package_ids).unlink()
            move_line_vals = self._prepare_entire_pack_move_line_vals(all_packages)
            pack_move_lines = self.env['stock.move.line'].create(move_line_vals)
            pack_move_lines._apply_putaway_strategy()
            # Need to set the right package dest for now fully contained packages
            self.move_line_ids.result_package_id._apply_package_dest_for_entire_packs(allowed_package_ids=all_package_ids)
            return True
        return False

    def action_see_move_scrap(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        scraps = self.env['stock.scrap'].search([('picking_id', '=', self.id)])
        action['domain'] = [('id', 'in', scraps.ids)]
        action['context'] = dict(self.env.context, create=False)
        return action

    def action_see_packages(self):
        self.ensure_one()
        return {
            'name': self.env._("Packages"),
            'res_model': 'stock.package',
            'view_mode': 'list,kanban,form',
            'views': [(self.env.ref('stock.stock_package_view_list_editable').id, 'list'), (False, 'kanban'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('picking_ids', 'in', self.ids)],
            'context': {
                'picking_ids': self.ids,
                'location_id': self.location_id.id,
                'can_add_entire_packs': self.picking_type_code != 'incoming',
                'search_default_main_packages': True,
            },
        }

    def action_see_package_histories(self):
        self.ensure_one()
        return {
            'name': self.env._("Packages"),
            'res_model': 'stock.package.history',
            'view_mode': 'list',
            'views': [(False, 'list')],
            'type': 'ir.actions.act_window',
            'domain': [('picking_ids', '=', self.id)],
            'context': {
                'search_default_main_packages': 1,
            },
        }

    def action_picking_move_tree(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_action")
        action['views'] = [
            (self.env.ref('stock.view_picking_move_tree').id, 'list'),
        ]
        action['context'] = self.env.context
        action['domain'] = [('picking_id', 'in', self.ids)]
        return action

    def action_view_reception_report(self):
        return self.env["ir.actions.actions"]._for_xml_id("stock.stock_reception_action")

    def action_open_label_layout(self):
        view = self.env.ref('stock.product_label_layout_form_picking')
        return {
            'name': _('Choose Labels Layout'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.label.layout',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_product_ids': self.move_ids.product_id.ids,
                'default_move_ids': self.move_ids.ids,
                'default_move_quantity': 'move'},
        }

    def action_open_label_type(self):
        if self.env.user.has_group('stock.group_production_lot') and self.move_line_ids.lot_id:
            view = self.env.ref('stock.picking_label_type_form')
            return {
                'name': _('Choose Type of Labels To Print'),
                'type': 'ir.actions.act_window',
                'res_model': 'picking.label.type',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'default_picking_ids': self.ids},
            }
        return self.action_open_label_layout()

    def _attach_sign(self):
        """ Render the delivery report in pdf and attach it to the picking in `self`. """
        self.ensure_one()
        report = self.env['ir.actions.report']._render_qweb_pdf("stock.action_report_delivery", self.id)
        filename = "%s_signed_delivery_slip" % self.name
        if self.partner_id:
            message = _('Order signed by %s', self.partner_id.name)
        else:
            message = _('Order signed')
        self.message_post(
            attachments=[('%s.pdf' % filename, report[0])],
            body=message,
        )
        return True

    def action_see_returns(self):
        self.ensure_one()
        if len(self.return_ids) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "views": [[False, "form"]],
                "res_id": self.return_ids.id
            }
        return {
            'name': _('Returns'),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "list"], [False, "form"]],
            "domain": [('id', 'in', self.return_ids.ids)],
        }

    def _get_report_lang(self):
        return self.move_ids and self.move_ids[0].partner_id.lang or self.partner_id.lang or self.env.lang

    def _get_autoprint_report_actions(self):
        report_actions = []
        pickings_to_print = self.filtered(lambda p: p.picking_type_id.auto_print_delivery_slip)
        if pickings_to_print:
            action = self.env.ref("stock.action_report_delivery").report_action(pickings_to_print.ids, config=False)
            clean_action(action, self.env)
            report_actions.append(action)
        pickings_print_return_slip = self.filtered(lambda p: p.picking_type_id.auto_print_return_slip)
        if pickings_print_return_slip:
            action = self.env.ref("stock.return_label_report").report_action(pickings_print_return_slip.ids, config=False)
            clean_action(action, self.env)
            report_actions.append(action)

        if self.env.user.has_group('stock.group_reception_report'):
            reception_reports_to_print = self.filtered(
                lambda p: p.picking_type_id.auto_print_reception_report
                          and p.picking_type_id.code != 'outgoing'
                          and p.move_ids.move_dest_ids
            )
            if reception_reports_to_print:
                action = self.env.ref('stock.stock_reception_report_action').report_action(reception_reports_to_print, config=False)
                clean_action(action, self.env)
                report_actions.append(action)
            reception_labels_to_print = self.filtered(lambda p: p.picking_type_id.auto_print_reception_report_labels and p.picking_type_id.code != 'outgoing')
            if reception_labels_to_print:
                moves_to_print = reception_labels_to_print.move_ids.move_dest_ids
                if moves_to_print:
                    # needs to be string to support python + js calls to report
                    quantities = ','.join(str(qty) for qty in moves_to_print.mapped(lambda m: math.ceil(m.product_uom_qty)))
                    data = {
                        'docids': moves_to_print.ids,
                        'quantity': quantities,
                    }
                    action = self.env.ref('stock.label_picking').report_action(moves_to_print, data=data, config=False)
                    clean_action(action, self.env)
                    report_actions.append(action)
        pickings_print_product_label = self.filtered(lambda p: p.picking_type_id.auto_print_product_labels)
        pickings_by_print_formats = pickings_print_product_label.grouped(lambda p: p.picking_type_id.product_label_format)
        for print_format in pickings_print_product_label.picking_type_id.mapped("product_label_format"):
            pickings = pickings_by_print_formats.get(print_format)
            wizard = self.env['product.label.layout'].create({
                'product_ids': pickings.move_ids.product_id.ids,
                'move_ids': pickings.move_ids.ids,
                'move_quantity': 'move',
                'print_format': pickings.picking_type_id.product_label_format,
            })
            action = wizard.process()
            if action:
                clean_action(action, self.env)
                report_actions.append(action)
        if self.env.user.has_group('stock.group_production_lot'):
            pickings_print_lot_label = self.filtered(lambda p: p.picking_type_id.auto_print_lot_labels and p.move_line_ids.lot_id)
            pickings_by_print_formats = pickings_print_lot_label.grouped(lambda p: p.picking_type_id.lot_label_format)
            for print_format in pickings_print_lot_label.picking_type_id.mapped("lot_label_format"):
                pickings = pickings_by_print_formats.get(print_format)
                wizard = self.env['lot.label.layout'].create({
                    'move_line_ids': pickings.move_line_ids.ids,
                    'label_quantity': 'lots' if '_lots' in print_format else 'units',
                    'print_format': '4x12' if '4x12' in print_format else 'zpl',
                })
                action = wizard.process()
                if action:
                    clean_action(action, self.env)
                    report_actions.append(action)
        if self.env.user.has_group('stock.group_tracking_lot'):
            pickings_print_packages = self.filtered(lambda p: p.picking_type_id.auto_print_packages and p.move_line_ids.result_package_id)
            if pickings_print_packages:
                action = self.env.ref("stock.action_report_picking_packages").report_action(pickings_print_packages.ids, config=False)
                clean_action(action, self.env)
                report_actions.append(action)
        return report_actions

    def _get_packages_for_print(self):
        package_ids = OrderedSet()
        for picking in self:
            if picking.state == 'done':
                package_ids.update(picking.package_history_ids.package_id.ids)
            else:
                package_ids.update(picking.move_line_ids.result_package_id._get_all_package_dest_ids())
        return self.env['stock.package'].browse(package_ids)

    def _can_return(self):
        self.ensure_one()
        return self.state == 'done'

    # TODO: rename the parameter from reference to references in master for improved readability
    def _add_reference(self, reference=False):
        """ link the given references to the list of references. """
        self.ensure_one()
        self.move_ids.reference_ids = [Command.link(stock_reference.id) for stock_reference in reference]

    # TODO: rename the parameter from reference to references in master for improved readability
    def _remove_reference(self, reference):
        """ remove the given references from the list of references. """
        self.ensure_one()
        self.move_ids.reference_ids = [Command.unlink(stock_reference.id) for stock_reference in reference]

    def _prepare_entire_pack_move_line_vals(self, packages):
        """ Prepares the move line values for every packages within packages and their children that contain products.
        """
        self.ensure_one()
        move_line_vals = []
        for package_quant in packages.quant_ids:
            move_line_vals.append({
                'product_id': package_quant.product_id.id,
                'quantity': package_quant.quantity,
                'product_uom_id': package_quant.product_uom_id.id,
                'location_id': package_quant.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_id': self.id,
                'company_id': self.id,
                'package_id': package_quant.package_id.id,
                'result_package_id': package_quant.package_id.id,
                'lot_id': package_quant.lot_id.id,
                'owner_id': package_quant.owner_id.id,
                'is_entire_pack': True,
            })
        return move_line_vals


# FILEPATH: odoo/addons/stock/models/stock_quant.py
_logger = logging.getLogger(__name__)
class StockQuant(models.Model):
    _name = 'stock.quant'
    _description = 'Quants'
    _rec_name = 'product_id'
    _rec_names_search = ['location_id', 'lot_id', 'package_id', 'owner_id']

    def _domain_location_id(self):
        if self.env.user.has_group('stock.group_stock_user'):
            return "[('usage', 'in', ['internal', 'transit'])] if context.get('inventory_mode') else []"
        return "[]"

    def _domain_lot_id(self):
        if self.env.user.has_group('stock.group_stock_user'):
            return ("[] if not context.get('inventory_mode') else"
                " [('product_id', '=', context.get('active_id', False))] if context.get('active_model') == 'product.product' else"
                " [('product_id.product_tmpl_id', '=', context.get('active_id', False))] if context.get('active_model') == 'product.template' else"
                " [('product_id', '=', product_id)]")
        return "[]"

    def _domain_product_id(self):
        if self.env.user.has_group('stock.group_stock_user'):
            return ("[] if not context.get('inventory_mode') else"
                " [('is_storable', '=', True), ('product_tmpl_id', 'in', context.get('product_tmpl_ids', []) + [context.get('product_tmpl_id', 0)])] if context.get('product_tmpl_ids') or context.get('product_tmpl_id') else"
                " [('is_storable', '=', True)]")
        return "[]"

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=lambda self: self._domain_product_id(),
        ondelete='restrict', required=True, index=True, check_company=True)
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        related='product_id.product_tmpl_id')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit',
        readonly=True, related='product_id.uom_id')
    is_favorite = fields.Boolean(related='product_tmpl_id.is_favorite')
    company_id = fields.Many2one(related='location_id.company_id', string='Company', store=True, readonly=True)
    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=lambda self: self._domain_location_id(),
        bypass_search_access=True, ondelete='restrict', required=True, index=True)
    warehouse_id = fields.Many2one('stock.warehouse', related='location_id.warehouse_id')
    storage_category_id = fields.Many2one(related='location_id.storage_category_id')
    cyclic_inventory_frequency = fields.Integer(related='location_id.cyclic_inventory_frequency')
    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number', index=True,
        ondelete='restrict', check_company=True,
        domain=lambda self: self._domain_lot_id())
    lot_properties = fields.Properties(related='lot_id.lot_properties', definition='product_id.lot_properties_definition', readonly=True)
    sn_duplicated = fields.Boolean(string="Duplicated Serial Number", compute='_compute_sn_duplicated', help="If the same SN is in another Quant")
    package_id = fields.Many2one(
        'stock.package', 'Package',
        domain="['|', ('location_id', '=', location_id), '&', ('location_id', '=', False), ('quant_ids', '=', False)]",
        help='The package containing this quant', ondelete='restrict', check_company=True, index=True)
    owner_id = fields.Many2one(
        'res.partner', 'Owner',
        help='This is the owner of the quant', check_company=True,
        index='btree_not_null')
    quantity = fields.Float(
        'Quantity',
        help='Quantity of products in this quant, in the default unit of measure of the product',
        readonly=True, digits='Product Unit')
    reserved_quantity = fields.Float(
        'Reserved Quantity',
        default=0.0,
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True, required=True, digits='Product Unit')
    available_quantity = fields.Float(
        'Available Quantity',
        help="On hand quantity which hasn't been reserved on a transfer, in the default unit of measure of the product",
        compute='_compute_available_quantity', digits='Product Unit')
    in_date = fields.Datetime('Incoming Date', readonly=True, required=True, default=fields.Datetime.now)
    tracking = fields.Selection(related='product_id.tracking', readonly=True)
    on_hand = fields.Boolean('On Hand', store=False, search='_search_on_hand')
    product_categ_id = fields.Many2one(related='product_tmpl_id.categ_id')

    # Inventory Fields
    inventory_quantity = fields.Float(
        'Counted', digits='Product Unit',
        help="The product's counted quantity.")
    inventory_quantity_auto_apply = fields.Float(
        'Inventoried Quantity', digits='Product Unit',
        compute='_compute_inventory_quantity_auto_apply',
        inverse='_set_inventory_quantity', groups='stock.group_stock_manager'
    )
    inventory_diff_quantity = fields.Float(
        'Difference', compute='_compute_inventory_diff_quantity', store=True,
        help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
        readonly=True, digits='Product Unit')
    inventory_date = fields.Date(
        'Scheduled', compute='_compute_inventory_date', store=True, readonly=False,
        help="Next date the On Hand Quantity should be counted.")
    last_count_date = fields.Date(compute='_compute_last_count_date', help='Last time the Quantity was Updated')
    inventory_quantity_set = fields.Boolean(store=True, compute='_compute_inventory_quantity_set', readonly=False)
    is_outdated = fields.Boolean('Quantity has been moved since last count', compute='_compute_is_outdated', search='_search_is_outdated')
    user_id = fields.Many2one(
        'res.users', 'Assigned To', help="User assigned to do product count.",
        domain=lambda self: [('all_group_ids', 'in', self.env.ref('stock.group_stock_user').id)])

    @api.depends('quantity', 'reserved_quantity')
    def _compute_available_quantity(self):
        for quant in self:
            quant.available_quantity = quant.quantity - quant.reserved_quantity

    @api.depends('location_id')
    def _compute_inventory_date(self):
        quants = self.filtered(lambda q: not q.inventory_date and q.location_id.usage in ['internal', 'transit'])
        date_by_location = {loc: loc._get_next_inventory_date() for loc in quants.location_id}
        for quant in quants:
            quant.inventory_date = date_by_location[quant.location_id]

    def _compute_last_count_date(self):
        """ We look at the stock move lines associated with every quant to get the last count date.
        """
        self.last_count_date = False
        groups = self.env['stock.move.line']._read_group(
            [
                ('state', '=', 'done'),
                ('is_inventory', '=', True),
                ('product_id', 'in', self.product_id.ids),
                '|',
                    ('lot_id', 'in', self.lot_id.ids),
                    ('lot_id', '=', False),
                '|',
                    ('owner_id', 'in', self.owner_id.ids),
                    ('owner_id', '=', False),
                '|',
                    ('location_id', 'in', self.location_id.ids),
                    ('location_dest_id', 'in', self.location_id.ids),
                '|',
                    ('package_id', '=', False),
                    '|',
                        ('package_id', 'in', self.package_id.ids),
                        ('result_package_id', 'in', self.package_id.ids),
            ],
            ['product_id', 'lot_id', 'package_id', 'owner_id', 'result_package_id', 'location_id', 'location_dest_id'],
            ['date:max'])

        def _update_dict(date_by_quant, key, value):
            current_date = date_by_quant.get(key)
            if not current_date or value > current_date:
                date_by_quant[key] = value

        date_by_quant = {}
        for product, lot, package, owner, result_package, location, location_dest, move_line_date in groups:
            location_id = location.id
            location_dest_id = location_dest.id
            package_id = package.id
            result_package_id = result_package.id
            lot_id = lot.id
            owner_id = owner.id
            product_id = product.id
            _update_dict(date_by_quant, (location_id, package_id, product_id, lot_id, owner_id), move_line_date)
            _update_dict(date_by_quant, (location_dest_id, package_id, product_id, lot_id, owner_id), move_line_date)
            _update_dict(date_by_quant, (location_id, result_package_id, product_id, lot_id, owner_id), move_line_date)
            _update_dict(date_by_quant, (location_dest_id, result_package_id, product_id, lot_id, owner_id), move_line_date)
        for quant in self:
            quant.last_count_date = date_by_quant.get((quant.location_id.id, quant.package_id.id, quant.product_id.id, quant.lot_id.id, quant.owner_id.id))

    def _search(self, domain, *args, **kwargs):
        domain = Domain(domain).map_conditions(
            lambda condition: Domain('lot_id', 'any', [condition]) if condition.field_expr.startswith('lot_properties.') else condition
        )
        return super()._search(domain, *args, **kwargs)

    @api.depends('inventory_quantity', 'inventory_quantity_set')
    def _compute_inventory_diff_quantity(self):
        for quant in self:
            if quant.inventory_quantity_set:
                quant.inventory_diff_quantity = quant.inventory_quantity - quant.quantity
            else:
                quant.inventory_diff_quantity = 0

    @api.depends('inventory_quantity')
    def _compute_inventory_quantity_set(self):
        self.inventory_quantity_set = True

    @api.depends('inventory_quantity', 'quantity', 'product_id')
    def _compute_is_outdated(self):
        self.is_outdated = False
        for quant in self:
            if quant.product_id and quant.product_uom_id.compare(quant.inventory_quantity - quant.inventory_diff_quantity, quant.quantity) and quant.inventory_quantity_set:
                quant.is_outdated = True

    def _search_is_outdated(self, operator, value):
        if operator != 'in':
            return NotImplemented
        quant_ids = self.search([('inventory_quantity_set', '=', True)])
        quant_ids = quant_ids.filtered(lambda quant: quant.product_uom_id.compare(quant.inventory_quantity - quant.inventory_diff_quantity, quant.quantity)).ids
        return [('id', 'in', quant_ids)]

    @api.depends('quantity')
    def _compute_inventory_quantity_auto_apply(self):
        for quant in self:
            quant.inventory_quantity_auto_apply = quant.quantity

    @api.depends('lot_id')
    def _compute_sn_duplicated(self):
        self.sn_duplicated = False
        domain = [('tracking', '=', 'serial'), ('lot_id', 'in', self.lot_id.ids), ('quantity', '>', 0), ('location_id.usage', 'in', ['internal', 'transit'])]
        results = self._read_group(domain, ['lot_id'], having=[('__count', '>', 1)])
        duplicated_sn_ids = [lot.id for [lot] in results]
        quants_with_duplicated_sn = self.env['stock.quant'].search([('lot_id', 'in', duplicated_sn_ids)])
        quants_with_duplicated_sn.sn_duplicated = True

    def _set_inventory_quantity(self):
        """ Inverse method to create stock move when `inventory_quantity` is set
        (`inventory_quantity` is only accessible in inventory mode).
        """
        if not self._is_inventory_mode():
            return
        quant_to_inventory = self.env['stock.quant']
        for quant in self:
            if quant.quantity == quant.inventory_quantity_auto_apply:
                continue
            quant.inventory_quantity = quant.inventory_quantity_auto_apply
            quant_to_inventory |= quant
        quant_to_inventory.action_apply_inventory()

    def _search_on_hand(self, operator, value):
        """Handle the "on_hand" filter, indirectly calling `_get_domain_locations`."""
        if operator != 'in':
            return NotImplemented
        return self.env['product.product']._get_domain_locations()[0]

    def copy(self, default=None):
        raise UserError(_('You cannot duplicate stock quants.'))

    @api.model
    def name_create(self, name):
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """ Override to handle the "inventory mode" and create a quant as
        superuser the conditions are met.
        """
        def _add_to_cache(quant):
            if 'quants_cache' in self.env.context:
                self.env.context['quants_cache'][
                    quant.product_id.id, quant.location_id.id, quant.lot_id.id, quant.package_id.id, quant.owner_id.id
                ] |= quant

        quants = self.env['stock.quant']
        is_inventory_mode = self._is_inventory_mode()
        allowed_fields = self._get_inventory_fields_create()
        for vals in vals_list:
            if is_inventory_mode and any(f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
                if any(field for field in vals if not field.startswith('x_') and field not in allowed_fields):
                    raise UserError(_("Quant's creation is restricted, you can't do this operation."))
                auto_apply = 'inventory_quantity_auto_apply' in vals
                inventory_quantity = vals.pop('inventory_quantity_auto_apply', False) or vals.pop(
                    'inventory_quantity', False) or 0
                # Create an empty quant or write on a similar one.
                product = self.env['product.product'].browse(vals['product_id'])
                location = self.env['stock.location'].browse(vals['location_id'])
                lot_id = self.env['stock.lot'].browse(vals.get('lot_id'))
                package_id = self.env['stock.package'].browse(vals.get('package_id'))
                owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
                quant = self.env['stock.quant']
                if not self.env.context.get('import_file'):
                    # Merge quants later, to make sure one line = one record during batch import
                    quant = self._gather(product, location, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                if lot_id:
                    if self.env.context.get('import_file') and lot_id.product_id != product:
                        lot_name = lot_id.name
                        lot_id = self.env['stock.lot'].search([('product_id', '=', product.id), ('name', '=', lot_name)], limit=1)
                        if not lot_id:
                            company_id = location.company_id or self.env.company
                            lot_id = self.env['stock.lot'].create({'name': lot_name, 'product_id': product.id, 'company_id': company_id.id})
                        vals['lot_id'] = lot_id.id
                    quant = quant.filtered(lambda q: q.lot_id)
                if quant:
                    quant = quant[0].sudo()
                else:
                    quant = self.sudo().create(vals)
                    _add_to_cache(quant)
                if auto_apply:
                    quant.write({'inventory_quantity_auto_apply': inventory_quantity})
                else:
                    # Set the `inventory_quantity` field to create the necessary move.
                    quant.inventory_quantity = inventory_quantity
                    quant.user_id = vals.get('user_id', self.env.user.id)
                    quant.inventory_date = fields.Date.today()
                quants |= quant
            else:
                if 'inventory_quantity' not in vals:
                    vals['inventory_quantity_set'] = vals.get('inventory_quantity_set', False)
                quant = super().create(vals)
                _add_to_cache(quant)
                quants |= quant
                if self._is_inventory_mode() and quant.company_id:
                    quant._check_company()
        return quants

    def _load_records_create(self, values):
        """ Add default location if import file did not fill it"""
        company_user = self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        for value in values:
            if 'location_id' not in value:
                value['location_id'] = warehouse.lot_stock_id.id
        return super(StockQuant, self.with_context(inventory_mode=True))._load_records_create(values)

    def _load_records_write(self, values):
        """ Only allowed fields should be modified """
        return super(StockQuant, self.with_context(inventory_mode=True))._load_records_write(values)

    def _read_group_select(self, aggregate_spec, query):
        if aggregate_spec == 'inventory_quantity:sum' and self.env.context.get('inventory_report_mode'):
            return SQL("NULL")
        if aggregate_spec == 'available_quantity:sum':
            sql_quantity = self._read_group_select('quantity:sum', query)
            sql_reserved_quantity = self._read_group_select('reserved_quantity:sum', query)
            return SQL("%s - %s", sql_quantity, sql_reserved_quantity)
        if aggregate_spec == 'inventory_quantity_auto_apply:sum':
            return self._read_group_select('quantity:sum', query)
        return super()._read_group_select(aggregate_spec, query)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Inventory Adjustments'),
            'template': '/stock/static/xlsx/stock_quant.xlsx'
        }]

    @api.model
    def _get_forbidden_fields_write(self):
        """ Returns a list of fields user can't edit when he want to edit a quant in `inventory_mode`."""
        return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id']

    def write(self, vals):
        """ Override to handle the "inventory mode" and create the inventory move. """
        forbidden_fields = self._get_forbidden_fields_write()
        if self._is_inventory_mode() and any(field for field in forbidden_fields if field in vals.keys()):
            if any(quant.location_id.usage == 'inventory' for quant in self):
                # Do nothing when user tries to modify manually a inventory loss
                return
            self = self.sudo()
            raise UserError(_("Quant's editing is restricted, you can't do this operation."))
        return super(StockQuant, self).write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_wrong_permission(self):
        if not self.env.is_superuser():
            if not self.env.user.has_group('stock.group_stock_manager'):
                raise UserError(_("Quants are auto-deleted when appropriate. If you must manually delete them, please ask a stock manager to do it."))
            self = self.with_context(inventory_mode=True)
            self.inventory_quantity = 0
            self._apply_inventory()

    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [
            '|',
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
        ]
        if self.package_id:
            action['domain'] += [
                '|',
                    ('package_id', '=', self.package_id.id),
                    ('result_package_id', '=', self.package_id.id),
            ]
        action['context'] = literal_eval(action.get('context'))
        action['context']['search_default_product_id'] = self.product_id.id
        return action

    def action_view_orderpoints(self):
        action = self.env['product.product'].action_view_orderpoints()
        action['domain'] = [('product_id', '=', self.product_id.id)]
        return action

    @api.model
    def action_view_quants(self):
        self = self.with_context(search_default_internal_loc=1)
        self = self._set_view_context()
        return self._get_quants_action(extend=True)

    @api.model
    def action_view_inventory(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        self = self._set_view_context()
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx['no_at_date'] = True
        if self.env.user.has_group('stock.group_stock_user') and not self.env.user.has_group('stock.group_stock_manager'):
            ctx['search_default_my_count'] = True
        view_id = self.env.ref('stock.view_stock_quant_tree_inventory_editable').id
        action = {
            'name': _('Physical Inventory'),
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('location_id.usage', 'in', ['internal', 'transit'])],
            'views': [(view_id, 'list')],
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    {}
                </p>
                <p>
                    {} <span class="fa fa-cog"/>
                </p>
                """.format(escape(_('Your stock is currently empty')),
                           escape(_('Press the "New" button to define the quantity for a product in your stock or import quantities from a spreadsheet via the Actions menu'))),
        }
        return action

    def action_apply_inventory(self, date=None):
        # for some reason if multi-record, env.context doesn't pass to wizards...
        ctx = dict(self.env.context or {})
        ctx['default_quant_ids'] = self.ids
        quants_outdated = self.filtered(lambda quant: quant.is_outdated)
        if quants_outdated:
            ctx['default_quant_to_fix_ids'] = quants_outdated.ids
            return {
                'name': _('Conflict in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.inventory.conflict',
                'target': 'new',
                'context': ctx,
            }
        self._apply_inventory(date)
        self.inventory_quantity_set = False

    def action_stock_quant_relocate(self):
        if len(self.company_id) > 1 or any(not q.company_id.id for q in self) or any(q <= 0 for q in self.mapped('quantity')):
            raise UserError(_('You can only move positive quantities stored in locations used by a single company per relocation.'))
        context = {
            'default_quant_ids': self.ids,
            'default_lot_id': self.env.context.get("default_lot_id", False),
            'single_product': self.env.context.get("single_product", False)
        }
        return {
            'res_model': 'stock.quant.relocate',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def action_inventory_history(self):
        self.ensure_one()
        action = {
            'name': _('History'),
            'view_mode': 'list,form',
            'res_model': 'stock.move.line',
            'views': [(self.env.ref('stock.view_move_line_tree').id, 'list'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_inventory': 1,
                'search_default_done': 1,
                'search_default_product_id': self.product_id.id,
            },
            'domain': [
                ('company_id', '=', self.company_id.id),
                '|',
                    ('location_id', '=', self.location_id.id),
                    ('location_dest_id', '=', self.location_id.id),
            ],
        }
        if self.lot_id:
            action['context']['search_default_lot_id'] = self.lot_id.id
        if self.package_id:
            action['context']['search_default_package_id'] = self.package_id.id
            action['context']['search_default_result_package_id'] = self.package_id.id
        if self.owner_id:
            action['context']['search_default_owner_id'] = self.owner_id.id
        return action

    def action_set_inventory_quantity(self):
        quants_already_set = self.filtered(lambda quant: quant.inventory_quantity_set)
        if quants_already_set:
            ctx = dict(self.env.context or {}, default_quant_ids=self.ids)
            view = self.env.ref('stock.inventory_warning_set_view', False)
            return {
                'name': _('Quantities Already Set'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'res_model': 'stock.inventory.warning',
                'target': 'new',
                'context': ctx,
            }
        if not self.env.context.get('from_request_count'):
            for quant in self:
                quant.inventory_quantity = quant.quantity
        self.user_id = self.env.user.id
        self.inventory_quantity_set = True

    def action_apply_all(self):
        quant_ids = self.env['stock.quant'].search(self.env.context['active_domain']).ids
        ctx = dict(self.env.context or {}, default_quant_ids=quant_ids)
        view = self.env.ref('stock.stock_inventory_adjustment_name_form_view', False)
        return {
            'name': _('Inventory Adjustment'),
            'type': 'ir.actions.act_window',
            'views': [(view.id, 'form')],
            'res_model': 'stock.inventory.adjustment.name',
            'target': 'new',
            'context': ctx,
        }

    def action_reset(self):
        ctx = dict(self.env.context or {}, default_quant_ids=self.ids)
        view = self.env.ref('stock.inventory_warning_reset_view', False)
        return {
            'name': _('Quantities To Reset'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'stock.inventory.warning',
            'target': 'new',
            'context': ctx,
        }

    def action_clear_inventory_quantity(self):
        self.inventory_quantity = 0
        self.inventory_diff_quantity = 0
        self.inventory_quantity_set = False
        self.user_id = False

    def action_set_inventory_quantity_zero(self):
        self.inventory_quantity = 0
        if self.env.context.get('inventory_report_mode'):
            self._apply_inventory()
        else:
            self.user_id = self.env.user.id

    @api.depends('location_id', 'lot_id', 'package_id', 'owner_id')
    def _compute_display_name(self):
        """name that will be displayed in the detailed operation"""
        for record in self:
            if record.env.context.get('formatted_display_name'):
                name = f"{record.location_id.name}"
                if record.package_id:
                    name += f"\t--{record.package_id.display_name}--"
                if record.lot_id:
                    name += (' ' if record.package_id else '\t') + f"--{record.lot_id.name}--"
                record.display_name = name
            else:
                if not record.ids:
                    record.display_name = ''
                    continue
                name = [record.location_id.display_name]
                if record.lot_id:
                    name.append(record.lot_id.name)
                if record.package_id:
                    name.append(record.package_id.display_name)
                if record.owner_id:
                    name.append(record.owner_id.name)
                record.display_name = ' - '.join(name)

    @api.constrains('product_id')
    def check_product_id(self):
        if any(not elem.product_id.is_storable for elem in self):
            raise ValidationError(_('Quants cannot be created for consumables or services.'))

    def check_quantity(self):
        sn_quants = self.filtered(lambda q: q.product_id.tracking == 'serial' and q.location_id.usage != 'inventory' and q.lot_id)
        if not sn_quants:
            return
        domain = [
            ('product_id', 'in', sn_quants.product_id.ids),
            ('location_id', 'child_of', sn_quants.location_id.ids),
            ('lot_id', 'in', sn_quants.lot_id.ids)
        ]
        groups = self._read_group(
            domain,
            ['product_id', 'location_id', 'lot_id'],
            ['quantity:sum'],
        )
        for product, _location, lot, qty in groups:
            if product.uom_id.compare(abs(qty), 1) > 0:
                raise ValidationError(_('The serial number has already been assigned: \n Product: %(product)s, Serial Number: %(serial_number)s', product=product.display_name, serial_number=lot.name))

    @api.constrains('location_id')
    def check_location_id(self):
        for quant in self:
            if quant.location_id.usage == 'view':
                raise ValidationError(_('You cannot take products from or deliver products to a location of type "view" (%s).', quant.location_id.name))

    @api.constrains('lot_id')
    def check_lot_id(self):
        for quant in self:
            if quant.lot_id.product_id and quant.lot_id.product_id != quant.product_id:
                raise ValidationError(_('The Lot/Serial number (%s) is linked to another product.', quant.lot_id.name))

    @api.model
    def _get_removal_strategy(self, product_id, location_id):
        product_id = product_id.sudo()
        location_id = location_id.sudo()
        if product_id.categ_id.removal_strategy_id:
            return product_id.categ_id.removal_strategy_id.with_context(lang=None).method
        loc = location_id
        while loc:
            if loc.removal_strategy_id:
                return loc.removal_strategy_id.with_context(lang=None).method
            loc = loc.location_id
        return 'fifo'

    def _run_least_packages_removal_strategy_astar(self, domain, qty):
        # Fetch the available packages and contents
        domain = Domain(domain).optimize(self)
        query = self._search(domain, bypass_access=True)
        query.groupby = SQL("package_id")
        query.having = SQL("SUM(quantity - reserved_quantity) > 0")
        query.order = SQL("available_qty DESC")
        qty_by_package = self.env.execute_query(
            query.select('package_id', 'SUM(quantity - reserved_quantity) AS available_qty'))

        # Items that do not belong to a package are added individually to the list, any empty packages get removed.
        pkg_found = False
        new_qty_by_package = []
        none_elements = []

        for elem in qty_by_package:
            if elem[0] is None:
                none_elements.extend([(None, 1) for _ in range(int(elem[1]))])
            elif elem[1] != 0:
                new_qty_by_package.append(elem)
                pkg_found = True

        new_qty_by_package.extend(none_elements)
        qty_by_package = new_qty_by_package

        if not pkg_found:
            return domain
        size = len(qty_by_package)

        class PriorityQueue:
            def __init__(self):
                self.elements = []

            def empty(self) -> bool:
                return not self.elements

            def put(self, item, priority):
                heapq.heappush(self.elements, (priority, item))

            def get(self):
                return heapq.heappop(self.elements)[1]

        def heuristic(node):
            if node.next_index < size:
                return len(node.taken_packages) + node.count_remaining / qty_by_package[node.next_index][1]
            return len(node.taken_packages)

        def generate_domain(node):
            selected_single_items = []
            single_item_ids = False
            for pkg in node.taken_packages:
                if pkg[0] is None:
                    # Lazily retrieve ids for single items
                    if not single_item_ids:
                        single_item_ids = self.search(Domain('package_id', '=', None) & domain).ids
                    selected_single_items.append(single_item_ids.pop())

            return (
                Domain('package_id', 'in', [elem[0] for elem in node.taken_packages if elem[0] is not None])
                | Domain('id', 'in', selected_single_items)
            ) & domain

        Node = namedtuple("Node", "count_remaining taken_packages next_index")

        frontier = PriorityQueue()
        frontier.put(Node(qty, (), 0), 0)

        best_leaf = Node(qty, (), 0)

        try:
            while not frontier.empty():
                current = frontier.get()

                if current.count_remaining <= 0:
                    return generate_domain(current)

                # Keep track of processed package amounts to only generate one branch for the same amount
                last_count = None
                i = current.next_index
                while i < size:
                    pkg = qty_by_package[i]
                    i += 1
                    if pkg[1] == last_count:
                        continue
                    last_count = pkg[1]

                    count = current.count_remaining - pkg[1]
                    taken = current.taken_packages + (pkg,)
                    node = Node(count, taken, i)

                    if count < 0:
                        # Overselect case
                        if best_leaf.count_remaining > 0 or len(node.taken_packages) < len(best_leaf.taken_packages) or (len(node.taken_packages) == len(best_leaf.taken_packages) and node.count_remaining > best_leaf.count_remaining):
                            best_leaf = node
                        continue

                    if i >= size and count != 0:
                        # Not enough packages case
                        if node.count_remaining < best_leaf.count_remaining:
                            best_leaf = node
                        continue

                    frontier.put(node, heuristic(node))
        except MemoryError:
            _logger.info('Ran out of memory while trying to use the least_packages strategy to get quants. Domain: %s', domain)
            return domain

        # no exact matching possible, use best leaf
        return generate_domain(best_leaf)

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy in ['fifo', 'least_packages']:
            return 'in_date ASC, id'
        elif removal_strategy == 'lifo':
            return 'in_date DESC, id DESC'
        elif removal_strategy == 'closest':
            return False
        raise UserError(_('Removal strategy %s not implemented.', removal_strategy))

    def _get_gather_domain(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        domains = [Domain('product_id', '=', product_id.id)]
        if not strict:
            if lot_id:
                domains.append(Domain('lot_id', 'in', [lot_id.id, False]))
            if package_id:
                domains.append(Domain('package_id', '=', package_id.id))
            if owner_id:
                domains.append(Domain('owner_id', '=', owner_id.id))
            domains.append(Domain('location_id', 'child_of', location_id.id))
        else:
            domains.extend((
                Domain('lot_id', 'in', [False, lot_id.id if lot_id else False]),
                Domain('package_id', '=', package_id.id if package_id else False),
                Domain('owner_id', '=', owner_id.id if owner_id else False),
                Domain('location_id', '=', location_id.id),
            ))
        if self.env.context.get('with_expiration'):
            domains.append(Domain('removal_date', '>=', self.env.context['with_expiration']) | Domain('removal_date', '=', False))
        return Domain.AND(domains)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, qty=0):
        """ if records in self, the records are filtered based on the wanted characteristics passed to this function
            if not, a search is done with all the characteristics passed.
        """
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        domain = self._get_gather_domain(product_id, location_id, lot_id, package_id, owner_id, strict)
        if removal_strategy == 'least_packages' and qty:
            domain = self._run_least_packages_removal_strategy_astar(domain, qty)
        order = self._get_removal_strategy_order(removal_strategy)

        quants_cache = self.env.context.get('quants_cache')
        if quants_cache is not None and strict and removal_strategy != 'least_packages':
            res = self.env['stock.quant']
            if lot_id:
                res |= quants_cache[product_id.id, location_id.id, lot_id.id, package_id.id, owner_id.id]
            res |= quants_cache[product_id.id, location_id.id, False, package_id.id, owner_id.id]
        else:
            res = self.search(domain, order=order)
        if removal_strategy == "closest":
            res = res.sorted(lambda q: (q.location_id.complete_name, -q.id))
        return res.sorted(lambda q: not q.lot_id)

    def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        """ Return the available quantity, i.e. the sum of `quantity` minus the sum of
        `reserved_quantity`, for the set of quants sharing the combination of `product_id,
        location_id` if `strict` is set to False or sharing the *exact same characteristics*
        otherwise.
        The set of quants to filter from can be in `self`, if not a search will be done
        This method is called in the following usecases:
            - when a stock move checks its availability
            - when a stock move actually assign
            - when editing a move line, to check if the new value is forced or not
            - when validating a move line with some forced values and have to potentially unlink an
              equivalent move line in another picking
        In the two first usecases, `strict` should be set to `False`, as we don't know what exact
        quants we'll reserve, and the characteristics are meaningless in this context.
        In the last ones, `strict` should be set to `True`, as we work on a specific set of
        characteristics.

        :return: available quantity as a float
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        if product_id.tracking == 'none':
            available_quantity = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            if allow_negative:
                return available_quantity
            else:
                return available_quantity if product_id.uom_id.compare(available_quantity, 0.0) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}
            for quant in quants:
                if not quant.lot_id and strict and lot_id:
                    continue
                if not quant.lot_id:
                    availaible_quantities['untracked'] += quant.quantity - quant.reserved_quantity
                else:
                    availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
            if allow_negative:
                return sum(availaible_quantities.values())
            else:
                return sum(available_quantity for available_quantity in availaible_quantities.values() if product_id.uom_id.compare(available_quantity, 0) > 0)

    def _get_reserve_quantity(self, product_id, location_id, quantity, uom_id=None, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Get the quantity available to reserve for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. If no quants are in self, `_gather` will do a search to fetch the quants
        Typically, this method is called before the `stock.move.line` creation to know the reserved_qty that could be use.
        It's also called by `_update_reserve_quantity` to find the quant to reserve.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            could be done and how much the system is able to reserve on it
        """
        self = self.sudo()

        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict, qty=quantity)

        # avoid quants with negative qty to not lower available_qty
        available_quantity = quants._get_available_quantity(product_id, location_id, lot_id, package_id, owner_id, strict)

        # do full packaging reservation when it's needed
        if self.env.context.get('packaging_uom_id') and product_id.product_tmpl_id.categ_id.packaging_reserve_method == "full":
            available_quantity = self.env.context.get('packaging_uom_id')._check_qty(available_quantity, product_id.uom_id, "DOWN")

        quantity = min(quantity, available_quantity)

        # `quantity` is in the quants unit of measure. There's a possibility that the move's
        # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
        # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
        # to convert `quantity` to the move's unit of measure with a down rounding method and
        # then get it back in the quants unit of measure with an half-up rounding_method. This
        # way, we'll never reserve more than allowed. We do not apply this logic if
        # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
        # will take care of changing the UOM to the UOM of the product.
        if not strict and uom_id and product_id.uom_id != uom_id:
            quantity_move_uom = product_id.uom_id._compute_quantity(quantity, uom_id, rounding_method='DOWN')
            quantity = uom_id._compute_quantity(quantity_move_uom, product_id.uom_id, rounding_method='HALF-UP')

        if product_id.tracking == 'serial':
            if product_id.uom_id.compare(quantity, int(quantity)) != 0:
                quantity = 0

        reserved_quants = []

        if product_id.uom_id.compare(quantity, 0) > 0:
            # if we want to reserve
            available_quantity = sum(quants.filtered(lambda q: product_id.uom_id.compare(q.quantity, 0) > 0).mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
        elif product_id.uom_id.compare(quantity, 0) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            if product_id.uom_id.compare(abs(quantity), available_quantity) > 0:
                raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.', product_id.display_name))
        else:
            return reserved_quants

        negative_reserved_quantity = defaultdict(float)
        for quant in quants:
            if product_id.uom_id.compare(quant.quantity - quant.reserved_quantity, 0) < 0:
                negative_reserved_quantity[(quant.location_id, quant.lot_id, quant.package_id, quant.owner_id)] += quant.quantity - quant.reserved_quantity
        for quant in quants:
            if product_id.uom_id.compare(quantity, 0) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if product_id.uom_id.compare(max_quantity_on_quant, 0) <= 0:
                    continue
                negative_quantity = negative_reserved_quantity[(quant.location_id, quant.lot_id, quant.package_id, quant.owner_id)]
                if negative_quantity:
                    negative_qty_to_remove = min(abs(negative_quantity), max_quantity_on_quant)
                    negative_reserved_quantity[(quant.location_id, quant.lot_id, quant.package_id, quant.owner_id)] += negative_qty_to_remove
                    max_quantity_on_quant -= negative_qty_to_remove
                if product_id.uom_id.compare(max_quantity_on_quant, 0) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if product_id.uom_id.is_zero(quantity) or product_id.uom_id.is_zero(available_quantity):
                break
        return reserved_quants

    def _get_quants_by_products_locations(self, product_ids, location_ids, extra_domain=False):
        res = defaultdict(lambda: self.env['stock.quant'])
        if product_ids and location_ids:
            domain = Domain([
                ('product_id', 'in', product_ids.ids),
                ('location_id', 'child_of', location_ids.ids)
            ])
            if extra_domain:
                domain &= Domain(extra_domain)
            needed_quants = self.env['stock.quant']._read_group(
                domain,
                ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id'],
                ['id:recordset'], order="lot_id"
            )
            for product, loc, lot, package, owner, quants in needed_quants:
                res[product.id, loc.id, lot.id, package.id, owner.id] = quants
        return res

    @api.onchange('location_id', 'product_id', 'lot_id', 'package_id', 'owner_id')
    def _onchange_location_or_product_id(self):
        vals = {}

        # Once the new line is complete, fetch the new theoretical values.
        if self.product_id and self.location_id:
            # Sanity check if a lot has been set.
            if self.lot_id:
                if self.tracking == 'none' or self.product_id != self.lot_id.product_id:
                    vals['lot_id'] = None

            quant = self._gather(
                self.product_id, self.location_id, lot_id=self.lot_id,
                package_id=self.package_id, owner_id=self.owner_id, strict=True)
            self.quantity = sum(quant.filtered(lambda q: q.lot_id == self.lot_id).mapped('quantity'))

            # Special case: directly set the quantity to one for serial numbers,
            # it'll trigger `inventory_quantity` compute.
            if self.lot_id and self.tracking == 'serial':
                vals['inventory_quantity'] = 1
                vals['inventory_quantity_auto_apply'] = 1

        if vals:
            self.update(vals)

    @api.onchange('inventory_quantity')
    def _onchange_inventory_quantity(self):
        if self.location_id and self.location_id.usage == 'inventory':
            warning = {
                'title': _('You cannot modify inventory loss quantity'),
                'message': _(
                    'Editing quantities in an Inventory Adjustment location is forbidden,'
                    'those locations are used as counterpart when correcting the quantities.'
                )
            }
            return {'warning': warning}

    @api.onchange('lot_id')
    def _onchange_serial_number(self):
        if self.lot_id and self.product_id.tracking == 'serial':
            message, dummy = self.env['stock.quant'].sudo()._check_serial_number(self.product_id,
                                                                                 self.lot_id,
                                                                                 self.company_id)
            if message:
                return {'warning': {'title': _('Warning'), 'message': message}}

    @api.onchange('product_id', 'company_id')
    def _onchange_product_id(self):
        if self.location_id:
            return
        if self.product_id.tracking in ['lot', 'serial']:
            previous_quants = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id.usage', 'in', ['internal', 'transit'])], limit=1, order='create_date desc')
            if previous_quants:
                self.location_id = previous_quants.location_id
        if not self.location_id:
            company_id = self.company_id and self.company_id.id or self.env.company.id
            self.location_id = self.env['stock.warehouse'].search(
                [('company_id', '=', company_id)], limit=1
            ).lot_stock_id

    def _apply_inventory(self, date=None):
        # Consider the inventory_quantity as set => recompute the inventory_diff_quantity if needed
        self.inventory_quantity_set = True
        move_vals = []
        default_loss_locations = {}
        quants_with_missing_loss_locations = self.filtered(lambda quant: not quant.product_id.with_company(quant.company_id).property_stock_inventory)
        if quants_with_missing_loss_locations:
            for company in quants_with_missing_loss_locations.mapped('company_id'):
                loss_location_id = self.env['ir.default'].with_company(company)._get_model_defaults(
                    'product.template').get('property_stock_inventory')
                default_loss_locations[company.id] = self.env['stock.location'].browse(loss_location_id)
        for quant in self:
            # if inventory applied from product's inverse_qty and the inventory_diff_quantity is 0,
            # we skip creating a move with 0 quantity.
            if quant.env.context.get('from_inverse_qty') and quant.product_uom_id.compare(quant.inventory_diff_quantity, 0) == 0:
                continue
            inventory_location = quant.product_id.with_company(quant.company_id).property_stock_inventory or\
                default_loss_locations.get(quant.company_id.id)
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if quant.product_uom_id.compare(quant.inventory_diff_quantity, 0) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                     inventory_location,
                                                     quant.location_id, package_dest_id=quant.package_id))
            else:
                move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                     quant.location_id,
                                                     inventory_location,
                                                     package_id=quant.package_id))
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves.with_context(ignore_dest_packages=True)._action_done()
        if date:
            moves.date = date
        moves._trigger_assign()
        self.location_id.sudo().write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.action_clear_inventory_quantity()

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity=False, reserved_quantity=False, lot_id=None, package_id=None, owner_id=None, in_date=None):
        """ Increase or decrease `quantity` or 'reserved quantity' of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        if not (quantity or reserved_quantity):
            raise ValidationError(_('Quantity or Reserved Quantity should be set.'))
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
        if lot_id:
            if product_id.uom_id.compare(quantity, 0) > 0:
                quants = quants.filtered(lambda q: q.lot_id)
            else:
                # Don't remove quantity from a negative quant without lot
                quants = quants.filtered(lambda q: product_id.uom_id.compare(q.quantity, 0) > 0 or q.lot_id)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              quant.product_uom_id.compare(quant.quantity, 0) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # quants are already ordered in _gather
            # lock the first available
            quant = quants.try_lock_for_update(allow_referencing=True, limit=1)

        if quant:
            vals = {'in_date': in_date}
            if quantity:
                vals['quantity'] = quant.quantity + quantity
            if reserved_quantity:
                vals['reserved_quantity'] = max(0, quant.reserved_quantity + reserved_quantity)
            quant.write(vals)
        else:
            vals = {
                'product_id': product_id.id,
                'location_id': location_id.id,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
            }
            if quantity:
                vals['quantity'] = quantity
            if reserved_quantity:
                vals['reserved_quantity'] = reserved_quantity
            self.create(vals)
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True, allow_negative=True), in_date

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=True):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :return: available_quantity
        """
        self._update_available_quantity(product_id, location_id, reserved_quantity=quantity, lot_id=lot_id, package_id=package_id, owner_id=owner_id)

    @api.model
    def _unlink_zero_quants(self):
        """ _update_available_quantity may leave quants with no
        quantity and no reserved_quantity. It used to directly unlink
        these zero quants but this proved to hurt the performance as
        this method is often called in batch and each unlink invalidate
        the cache. We defer the calls to unlink in this method.
        """
        precision_digits = max(6, self.sudo().env.ref('uom.decimal_product_uom').digits * 2)
        # Use a select instead of ORM search for UoM robustness.
        query = """SELECT id FROM stock_quant WHERE (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
                                                     AND round(reserved_quantity::numeric, %s) = 0
                                                     AND (round(inventory_quantity::numeric, %s) = 0 OR inventory_quantity IS NULL)
                                                     AND user_id IS NULL;"""
        params = (precision_digits, precision_digits, precision_digits)
        self.env.cr.execute(query, params)
        quants = self.env['stock.quant'].browse([quant['id'] for quant in self.env.cr.dictfetchall()])
        quants.sudo().unlink()

    @api.model
    def _clean_reservations(self):
        reserved_quants = self.env['stock.quant']._read_group(
            [('reserved_quantity', '!=', 0)],
            ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id'],
            ['reserved_quantity:sum', 'id:recordset'],
        )
        reserved_move_lines = self.env['stock.move.line']._read_group(
            [
                ('state', 'in', ['assigned', 'partially_available', 'waiting', 'confirmed']),
                ('quantity_product_uom', '!=', 0),
                ('product_id.is_storable', '=', True),
            ],
            ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id'],
            ['quantity_product_uom:sum'],
        )
        reserved_move_lines = {
            (product, location, lot, package, owner): reserved_quantity
            for product, location, lot, package, owner, reserved_quantity in reserved_move_lines
        }
        for product, location, lot, package, owner, reserved_quantity, quants in reserved_quants:
            ml_reserved_qty = reserved_move_lines.get((product, location, lot, package, owner), 0)
            if location.should_bypass_reservation():
                quants._update_reserved_quantity(product, location, -reserved_quantity, lot_id=lot, package_id=package, owner_id=owner)
            elif product.uom_id.compare(reserved_quantity, ml_reserved_qty) != 0:
                quants._update_reserved_quantity(product, location, ml_reserved_qty - reserved_quantity, lot_id=lot, package_id=package, owner_id=owner)
            if ml_reserved_qty:
                del reserved_move_lines[(product, location, lot, package, owner)]

        for (product, location, lot, package, owner), reserved_quantity in reserved_move_lines.items():
            if location.should_bypass_reservation() or\
                self.env['stock.quant']._should_bypass_product(product, location, reserved_quantity, lot, package, owner):
                continue
            else:
                self.env['stock.quant']._update_reserved_quantity(product, location, reserved_quantity, lot_id=lot, package_id=package, owner_id=owner)

    @api.model
    def _merge_quants(self):
        """ In a situation where one transaction is updating a quant via
        `_update_available_quantity` and another concurrent one calls this function with the same
        argument, we’ll create a new quant in order for these transactions to not rollback. This
        method will find and deduplicate these quants.
        """
        params = []
        query = """WITH
                        dupes AS (
                            SELECT min(id) as to_update_quant_id,
                                (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)] as to_delete_quant_ids,
                                GREATEST(0, SUM(reserved_quantity)) as reserved_quantity,
                                SUM(inventory_quantity) as inventory_quantity,
                                SUM(quantity) as quantity,
                                MIN(in_date) as in_date
                            FROM stock_quant
        """
        if self._ids:
            query += """
                            WHERE
                                location_id in %s
                                AND product_id in %s
            """
            params = [tuple(self.location_id.ids), tuple(self.product_id.ids)]
        query += """
                            GROUP BY product_id, company_id, location_id, lot_id, package_id, owner_id
                            HAVING count(id) > 1
                        ),
                        _up AS (
                            UPDATE stock_quant q
                                SET quantity = d.quantity,
                                    reserved_quantity = d.reserved_quantity,
                                    inventory_quantity = d.inventory_quantity,
                                    in_date = d.in_date
                            FROM dupes d
                            WHERE d.to_update_quant_id = q.id
                        )
                   DELETE FROM stock_quant WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
        """
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(query, params)
                self.env.invalidate_all()
        except Error as e:
            _logger.info('an error occurred while merging quants: %s', e.pgerror)

    @api.model
    def _quant_tasks(self):
        self._merge_quants()
        self._clean_reservations()
        self._unlink_zero_quants()

    @api.model
    def _is_inventory_mode(self):
        """ Used to control whether a quant was written on or created during an
        "inventory session", meaning a mode where we need to create the stock.move
        record necessary to be consistent with the `inventory_quantity` field.
        """
        return self.env.context.get('inventory_mode') and self.env.user.has_group('stock.group_stock_user')

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        return ['product_id', 'owner_id'] + self._get_inventory_fields_write()

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        fields = ['inventory_quantity', 'inventory_quantity_auto_apply', 'inventory_diff_quantity',
                  'inventory_date', 'user_id', 'inventory_quantity_set', 'is_outdated', 'lot_id',
                  'location_id', 'package_id']
        return fields

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, package_id=False, package_dest_id=False):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param package_id: `stock.package`
        :param package_dest_id: `stock.package`
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()

        res = {
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'restrict_partner_id':  self.owner_id.id,
            'is_inventory': True,
            'picked': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'quantity': qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.lot_id.id,
                'package_id': package_id.id if package_id else False,
                'result_package_id': package_dest_id.id if package_dest_id else False,
                'owner_id': self.owner_id.id,
            })]
        }
        if self.env.context.get('inventory_name'):
            res['inventory_name'] = self.env.context.get('inventory_name')

        return res

    def _set_view_context(self):
        """ Adds context when opening quants related views. """
        if not self.env.user.has_group('stock.group_stock_multi_locations'):
            company_user = self.env.company
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
            if warehouse:
                self = self.with_context(default_location_id=warehouse.lot_stock_id.id, hide_location=not self.env.context.get('always_show_loc', False))

        # If user have rights to write on quant, we set quants in inventory mode.
        if self.env.user.has_group('stock.group_stock_user'):
            self = self.with_context(inventory_mode=True)
        return self

    @api.model
    def _get_quants_action(self, extend=False):
        """ Returns an action to open (non-inventory adjustment) quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx['inventory_report_mode'] = True
        ctx.pop('group_by', None)

        action = self.env['ir.actions.act_window']._for_xml_id('stock.stock_quant_action')

        form_view = self.env.ref('stock.view_stock_quant_form_editable').id
        if self.env.context.get('inventory_mode') and self.env.user.has_group('stock.group_stock_manager'):
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree_editable').id
        else:
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree').id
        action.update({
            'views': [
                (action['view_id'], 'list'),
                (form_view, 'form'),
            ],
            'context': ctx,
        })
        if extend:
            action.update({
                'view_mode': 'list,form,pivot,graph',
                'views': [
                    (action['view_id'], 'list'),
                    (form_view, 'form'),
                    (self.env.ref('stock.view_stock_quant_pivot').id, 'pivot'),
                    (self.env.ref('stock.stock_quant_view_graph').id, 'graph'),
                ],
            })
        # It's mainly define in the server action in order to call _get_quants_action when using the url
        action['path'] = "stock-locations"
        return action

    def _get_gs1_barcode(self, gs1_quantity_rules_ai_by_uom=False):
        """ Generates a GS1 barcode for the quant's properties (product, quantity and LN/SN.)

        :param gs1_quantity_rules_ai_by_uom: contains the products' GS1 AI paired with the UoM id
        :type gs1_quantity_rules_ai_by_uom: dict
        :return: str
        """
        self.ensure_one()
        gs1_quantity_rules_ai_by_uom = gs1_quantity_rules_ai_by_uom or {}
        barcode = ''

        # Product part.
        if self.product_id.valid_ean:
            barcode = self.product_id.barcode
            barcode = '01' + '0' * (14 - len(barcode)) + barcode
        elif self.tracking == 'none' or not self.lot_id:
            return ''  # Doesn't make sense to generate a GS1 barcode for qty with no other data.

        # Quantity part.
        if self.tracking != 'serial' or self.quantity > 1:
            quantity_ai = gs1_quantity_rules_ai_by_uom.get(self.product_uom_id.id)
            if quantity_ai:
                qty_str = str(int(self.quantity / self.product_uom_id.rounding))
                if len(qty_str) <= 6:
                    barcode += quantity_ai + '0' * (6 - len(qty_str)) + qty_str
            else:
                # No decimal indicator for GS1 Units, no better solution than rounding the qty.
                qty_str = str(int(round(self.quantity)))
                if len(qty_str) <= 8:
                    barcode += '30' + '0' * (8 - len(qty_str)) + qty_str

        # Tracking part (must be GS1 barcode's last part since we don't know SN/LN length.)
        if self.lot_id:
            if len(self.lot_id.name) > 20:
                # Cannot generate a valid GS1 barcode since the lot/serial number max length is
                # exceeded and this information is required if the LN/SN is present.
                return ''
            tracking_ai = '21' if self.tracking == 'serial' else '10'
            barcode += tracking_ai + self.lot_id.name
        return barcode

    def get_aggregate_barcodes(self):
        """ Generates and aggregates quants' barcodes. This method uses the config parameters
        `stock.agg_barcode_max_length` to determine the length limit of a single aggregate barcode
        (400 by default) and `stock.barcode_separator` to determine which character to use to
        separate individual encodings (this method can't work without this parameter and will return
        an empty list.) Depending on the number of quants, those parameters and the length of their
        barcode encodings, there can be one or more aggregate barcodes.

        :return: list
        """
        agg_barcode_max_length = int(self.env['ir.config_parameter'].sudo().get_param('stock.agg_barcode_max_length', 400))
        barcode_separator = self.env['ir.config_parameter'].sudo().get_param('stock.barcode_separator')
        if not barcode_separator:
            return []  # A barcode separator is mandatory to be able to aggregate barcodes.

        eol_char = '\t'  # Added at the end of aggregate barcodes to end `barcode_scanned` event.
        aggregate_barcodes = []
        aggregate_barcode = ""

        # Searches all GS1 rules linked to an UoM other than Unit and retrieves their AI.
        uom_unit_id = self.env.ref('uom.product_uom_unit').id
        gs1_quantity_rules = self.env['barcode.rule'].search([
            ('associated_uom_id', '!=', False),
            ('associated_uom_id', '!=', uom_unit_id),
            ('is_gs1_nomenclature', '=', True)]
        )
        gs1_quantity_rules_ai_by_uom = {}

        for rule in gs1_quantity_rules:
            decimal = str(len(f'{rule.associated_uom_id.rounding:.10f}'.rstrip('0').split('.')[1]))
            rule_ai = rule.pattern[1:4] + decimal
            gs1_quantity_rules_ai_by_uom[rule.associated_uom_id.id] = rule_ai

        previous_product = self.env['product.product']
        for quant in self:
            if not quant.product_id.barcode:
                continue
            barcode = ""
            # In case the quant product's barcode is not GS1 compliant, add it first,
            # so that the lots and qty barcodes that follow it will be used for this product.
            if previous_product != quant.product_id:
                previous_product = quant.product_id
                if not quant.product_id.valid_ean:
                    barcode += quant.product_id.barcode
            # Gets quant's barcode (either a GS1 barcode or only a serial number.)
            quant_gs1_barcode = quant._get_gs1_barcode(gs1_quantity_rules_ai_by_uom)
            if quant_gs1_barcode:
                barcode += (barcode_separator if barcode else '') + quant_gs1_barcode
            elif quant.tracking == 'serial':
                barcode += (barcode_separator if barcode else '') + quant.lot_id.name
            # If aggregate barcode will be too long, adds it to the result list and resets it.
            if aggregate_barcode and len(aggregate_barcode + barcode) > agg_barcode_max_length:
                aggregate_barcodes.append(aggregate_barcode + eol_char)
                aggregate_barcode = ""
            if barcode:
                if aggregate_barcode and aggregate_barcode[-1] != barcode_separator:
                    aggregate_barcode += barcode_separator
                aggregate_barcode += barcode

        if aggregate_barcode:
            aggregate_barcodes.append(aggregate_barcode + eol_char)

        return aggregate_barcodes

    @api.model
    def _check_serial_number(self, product_id, lot_id, company_id, source_location_id=None, ref_doc_location_id=None):
        """ Checks for duplicate serial numbers (SN) when assigning a SN (i.e. no source_location_id)
        and checks for potential incorrect location selection of a SN when using a SN (i.e.
        source_location_id). Returns warning message of all locations the SN is located at and
        (optionally) a recommended source location of the SN (when using SN from incorrect location).
        This function is designed to be used by onchange functions across differing situations including,
        but not limited to scrap, incoming picking SN encoding, and outgoing picking SN selection.

        :param product_id: `product.product` product to check SN for
        :param lot_id: `stock.production.lot` SN to check
        :param company_id: `res.company` company to check against (i.e. we ignore duplicate SNs across
            different companies for lots defined with a company)
        :param source_location_id: `stock.location` optional source location if using the SN rather
            than assigning it
        :param ref_doc_location_id: `stock.location` optional reference document location for
            determining recommended location. This is param expected to only be used when a
            `source_location_id` is provided.
        :return: tuple(message, recommended_location) If not None, message is a string expected to be
            used in warning message dict and recommended_location is a `location_id`
        """
        message = None
        recommended_location = None
        if product_id.tracking == 'serial':
            internal_domain = Domain('location_id.usage', 'in', ('internal', 'transit'))
            if lot_id.company_id:
                internal_domain &= Domain('company_id', '=', company_id.id)
            quants = self.env['stock.quant'].search(Domain.AND((
                Domain('product_id', '=', product_id.id),
                Domain('lot_id', 'in', lot_id.ids),
                Domain('quantity', '!=', 0),
                Domain('location_id.usage', '=', 'customer') | internal_domain,
            )))
            sn_locations = quants.mapped('location_id')
            if quants:
                if not source_location_id:
                    # trying to assign an already existing SN
                    message = _('The Serial Number (%(serial_number)s) is already used in location(s): %(location_list)s.\n\n'
                                'Is this expected? For example, this can occur if a delivery operation is validated '
                                'before its corresponding receipt operation is validated. In this case the issue will be solved '
                                'automatically once all steps are completed. Otherwise, the serial number should be corrected to '
                                'prevent inconsistent data.',
                                serial_number=lot_id.name, location_list=sn_locations.mapped('display_name'))

                elif source_location_id and source_location_id not in sn_locations:
                    # using an existing SN in the wrong location
                    recommended_location = self.env['stock.location']
                    if ref_doc_location_id:
                        for location in sn_locations:
                            if ref_doc_location_id.parent_path in location.parent_path:
                                recommended_location = location
                                break
                    else:
                        for location in sn_locations:
                            if location.usage != 'customer':
                                recommended_location = location
                                break
                    if recommended_location and recommended_location.company_id == company_id:
                        message = _('Serial number (%(serial_number)s) is not located in %(source_location)s, but is located in location(s): %(other_locations)s.\n\n'
                                    'Source location for this move will be changed to %(recommended_location)s',
                                    serial_number=lot_id.name,
                                    source_location=source_location_id.display_name,
                                    other_locations=sn_locations.mapped('display_name'),
                                    recommended_location=recommended_location.display_name)
                    else:
                        message = _('Serial number (%(serial_number)s) is not located in %(source_location)s, but is located in location(s): %(other_locations)s.\n\n'
                                    'Please correct this to prevent inconsistent data.',
                                    serial_number=lot_id.name,
                                    source_location=source_location_id.display_name,
                                    other_locations=sn_locations.mapped('display_name'))
                        recommended_location = None
        return message, recommended_location

    def move_quants(self, location_dest_id=False, package_dest_id=False, message=False, unpack=False, up_to_parent_packages=False):
        """ Directly move a stock.quant to another location and/or package by creating a stock.move.

        :param location_dest_id: `stock.location` destination location for the quants
        :param package_dest_id: `stock.package` destination package for the quants
        :param message: String to fill the reference field on the generated stock.move
        :param unpack: set to True when needing to unpack the quant
        :param up_to_parent_packages: `stock.package` that are the upper limit to keep the parents
        """
        def set_parent_package(all_quants, package, limit_ids):
            if not package.parent_package_id or (limit_ids and package.id in limit_ids):
                return
            if any(quant not in all_quants for quant in package.parent_package_id.contained_quant_ids):
                # Only move the container package as well if its whole content is moved as well
                return
            package.package_dest_id = package.parent_package_id
            return set_parent_package(all_quants, package.parent_package_id, limit_ids)

        message = message or _('Quantity Relocated')
        move_vals = []
        limit_ids = set(up_to_parent_packages.ids if up_to_parent_packages else [])
        for quant in self:
            result_package_id = package_dest_id  # temp variable to keep package_dest_id unchanged
            if not unpack and not package_dest_id:
                result_package_id = quant.package_id
                set_parent_package(self, result_package_id, limit_ids)
            move_vals.append(quant.with_context(inventory_name=message)._get_inventory_move_values(
                quant.quantity,
                quant.location_id,
                location_dest_id or quant.location_id,
                quant.package_id,
                result_package_id))
        moves = self.env['stock.move'].create(move_vals)
        moves._action_done()

    def _should_bypass_product(self, product=False, location=False, reserved_quantity=0, lot_id=False, package_id=False, owner_id=False):
        return False


# FILEPATH: odoo/addons/stock/models/stock_reference.py
class StockReference(models.Model):
    _name = 'stock.reference'
    _description = 'Reference between stock documents'

    name = fields.Char('Reference', required=True, readonly=True)
    move_ids = fields.Many2many(
        'stock.move', 'stock_reference_move_rel', 'reference_id', 'move_id', string="Stock Moves")
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking_ids', string="Transfers", readonly=True)

    def _compute_picking_ids(self):
        for reference in self:
            reference.picking_ids = reference.move_ids.picking_id


# FILEPATH: odoo/addons/stock/models/stock_replenish_mixin.py
class StockReplenishMixin(models.AbstractModel):
    _name = 'stock.replenish.mixin'
    _description = 'Product Replenish Mixin'

    route_id = fields.Many2one(
        'stock.route', string="Preferred Route",
        help="Apply specific route for the replenishment instead of product's default routes.",
        check_company=True)
    allowed_route_ids = fields.Many2many('stock.route', compute='_compute_allowed_route_ids')

    # INHERITS in 'Drop Shipping', 'Dropship and Subcontracting Management' and 'Dropship and Subcontracting Management'
    @api.depends('product_id', 'product_tmpl_id')
    def _compute_allowed_route_ids(self):
        domain = self._get_allowed_route_domain()
        route_ids = self.env['stock.route'].search(domain)
        self.allowed_route_ids = route_ids

    # TODO: remove dynamic domain
    # OVERWRITE in 'Drop Shipping', 'Dropship and Subcontracting Management' and 'Dropship and Subcontracting Management' to hide it
    def _get_allowed_route_domain(self):
        stock_location_inter_company_id = self.env.ref('stock.stock_location_inter_company').id

        base_domain = Domain('product_selectable', '=', True)
        if self.warehouse_id:
            wh_route_ids = self.warehouse_id.route_ids.filtered(lambda r: r._is_valid_resupply_route_for_product(self.product_id)).ids
            if wh_route_ids:
                base_domain |= Domain('id', 'in', wh_route_ids)

        return Domain.AND([
            base_domain,
            Domain('rule_ids.location_src_id', '!=', stock_location_inter_company_id),
            Domain('rule_ids.location_dest_id', '!=', stock_location_inter_company_id),
            Domain('rule_ids.location_dest_id.warehouse_id', '!=', False),
        ])


# FILEPATH: odoo/addons/stock/models/stock_rule.py
_logger = logging.getLogger(__name__)
class ProcurementException(Exception):
    """An exception raised by StockRule `run` containing all the faulty
    procurements.
    """
    def __init__(self, procurement_exceptions):
        """:param procurement_exceptions: a list of tuples containing the faulty
        procurement and their error messages
        :type procurement_exceptions: list
        """
        self.procurement_exceptions = procurement_exceptions

class Procurement(NamedTuple):
    product_id: fields.Many2one
    product_qty: fields.Float
    product_uom: fields.Many2one
    location_id: fields.Many2one
    name: fields.Char
    origin: fields.Char
    company_id: fields.Many2one
    values: dict

class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _name = 'stock.rule'
    _description = "Stock Rule"
    _order = "sequence, id"
    _check_company_auto = True

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'company_id' in fields and not res['company_id']:
            res['company_id'] = self.env.company.id
        return res

    Procurement = Procurement
    name = fields.Char(
        'Name', required=True, translate=True,
        help="This field will fill the packing origin and the name of its moves")
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the rule without removing it.")
    action = fields.Selection(
        selection=[('pull', 'Pull From'), ('push', 'Push To'), ('pull_push', 'Pull & Push')], string='Action',
        default='pull', required=True, index=True)
    sequence = fields.Integer('Sequence', default=20)
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company,
        domain="[('id', '=?', route_company_id)]", index=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location', required=True, check_company=True, index=True)
    location_src_id = fields.Many2one('stock.location', 'Source Location', check_company=True, index=True)
    location_dest_from_rule = fields.Boolean(
        "Destination location origin from rule", default=False,
        help="When set to True the destination location of the stock.move will be the rule."
        "Otherwise, it takes it from the picking type.")
    route_id = fields.Many2one('stock.route', 'Route', required=True, ondelete='cascade', index=True)
    route_company_id = fields.Many2one(related='route_id.company_id', string='Route Company')
    procure_method = fields.Selection([
        ('make_to_stock', 'Take From Stock'),
        ('make_to_order', 'Trigger Another Rule'),
        ('mts_else_mto', 'Take From Stock, if unavailable, Trigger Another Rule')], string='Supply Method', default='make_to_stock', required=True,
        help="Take From Stock: the products will be taken from the available stock of the source location.\n"
             "Trigger Another Rule: the system will try to find a stock rule to bring the products in the source location. The available stock will be ignored.\n"
             "Take From Stock, if Unavailable, Trigger Another Rule: the products will be taken from the available stock of the source location."
             "If there is no stock available, the system will try to find a  rule to bring the products in the source location.")
    route_sequence = fields.Integer('Route Sequence', related='route_id.sequence', store=True, compute_sudo=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, check_company=True,
        domain="[('code', 'in', picking_type_code_domain)] if picking_type_code_domain else []")
    picking_type_code_domain = fields.Json(compute='_compute_picking_type_code_domain')
    delay = fields.Integer('Lead Time', default=0, help="The expected date of the created transfer will be computed based on this lead time.")
    partner_address_id = fields.Many2one(
        'res.partner', 'Partner Address',
        check_company=True,
        help="Address where goods should be delivered. Optional.")
    propagate_cancel = fields.Boolean(
        'Cancel Next Move', default=False,
        help="When ticked, if the move created by this rule is cancelled, the next move will be cancelled too.")
    propagate_carrier = fields.Boolean(
        'Propagation of carrier', default=False,
        help="When ticked, carrier of shipment will be propagated.")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', check_company=True, index=True)
    auto = fields.Selection([
        ('manual', 'Manual Operation'),
        ('transparent', 'Automatic No Step Added')], string='Automatic Move',
        default='manual', required=True,
        help="The 'Manual Operation' value will create a stock move after the current one. "
             "With 'Automatic No Step Added', the location is replaced in the original move.")
    rule_message = fields.Html(compute='_compute_action_message')
    push_domain = fields.Char('Push Applicability')

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'name' not in default:
            for rule, vals in zip(self, vals_list):
                vals['name'] = _("%s (copy)", rule.name)
        return vals_list

    @api.constrains('company_id')
    def _check_company_consistency(self):
        for rule in self:
            route = rule.route_id
            if route.company_id and rule.company_id.id != route.company_id.id:
                raise ValidationError(_(
                    "Rule %(rule)s belongs to %(rule_company)s while the route belongs to %(route_company)s.",
                    rule=rule.display_name,
                    rule_company=rule.company_id.display_name,
                    route_company=route.company_id.display_name,
                ))

    @api.onchange('picking_type_id')
    def _onchange_picking_type(self):
        """ Modify locations to the default picking type's locations source and
        destination.
        Enable the delay alert if the picking type is a delivery
        """
        self.location_src_id = self.picking_type_id.default_location_src_id.id
        self.location_dest_id = self.picking_type_id.default_location_dest_id.id

    @api.onchange('route_id', 'company_id')
    def _onchange_route(self):
        """ Ensure that the rule's company is the same than the route's company. """
        if self.route_id.company_id:
            self.company_id = self.route_id.company_id
        if self.picking_type_id.warehouse_id.company_id != self.route_id.company_id:
            self.picking_type_id = False

    def _get_message_values(self):
        """ Return the source, destination and picking_type applied on a stock
        rule. The purpose of this function is to avoid code duplication in
        _get_message_dict functions since it often requires those data.
        """
        source = self.location_src_id and self.location_src_id.display_name or _('Source Location')
        destination = self.location_dest_id and self.location_dest_id.display_name or _('Destination Location')
        direct_destination = self.picking_type_id and self.picking_type_id.default_location_dest_id != self.location_dest_id and self.picking_type_id.default_location_dest_id.display_name
        operation = self.picking_type_id and self.picking_type_id.name or _('Operation Type')
        return source, destination, direct_destination, operation

    def _get_message_dict(self):
        """ Return a dict with the different possible message used for the
        rule message. It should return one message for each stock.rule action
        (except push and pull). This function is override in mrp and
        purchase_stock in order to complete the dictionary.
        """
        message_dict = {}
        source, destination, direct_destination, operation = self._get_message_values()
        if self.action in ('push', 'pull', 'pull_push'):
            suffix = ""
            if self.action in ('pull', 'pull_push') and direct_destination and not self.location_dest_from_rule:
                suffix = _("<br>The products will be moved towards <b>%(destination)s</b>, <br/> as specified from <b>%(operation)s</b> destination.", destination=direct_destination, operation=operation)
            if self.procure_method == 'make_to_order' and self.location_src_id:
                suffix += _("<br>A need is created in <b>%s</b> and a rule will be triggered to fulfill it.", source)
            if self.procure_method == 'mts_else_mto' and self.location_src_id:
                suffix += _("<br>If the products are not available in <b>%s</b>, a rule will be triggered to bring the missing quantity in this location.", source)
            message_dict = {
                'pull': _(
                    'When products are needed in <b>%(destination)s</b>, <br> <b>%(operation)s</b> are created from <b>%(source_location)s</b> to fulfill the need. %(suffix)s',
                    destination=destination,
                    operation=operation,
                    source_location=source,
                    suffix=suffix,
                ),
                'push': _(
                    'When products arrive in <b>%(source_location)s</b>, <br> <b>%(operation)s</b> are created to send them to <b>%(destination)s</b>.',
                    source_location=source,
                    operation=operation,
                    destination=destination,
                ),
            }
        return message_dict

    @api.depends('action', 'location_dest_id', 'location_src_id', 'picking_type_id', 'procure_method', 'location_dest_from_rule')
    def _compute_action_message(self):
        """ Generate dynamicaly a message that describe the rule purpose to the
        end user.
        """
        action_rules = self.filtered(lambda rule: rule.action)
        for rule in action_rules:
            message_dict = rule._get_message_dict()
            message = message_dict.get(rule.action) and message_dict[rule.action] or ""
            if rule.action == 'pull_push':
                message = message_dict['pull'] + "<br/><br/>" + message_dict['push']
            rule.rule_message = message
        (self - action_rules).rule_message = None

    @api.depends('action')
    def _compute_picking_type_code_domain(self):
        self.picking_type_code_domain = []

    def _get_push_new_date(self, move):
        """ Get the new date for a push rule.

        :param move: The stock move being processed
        :type move: stock.move
        :return: The new date as a string
        :rtype: str
        """
        return fields.Datetime.to_string(move.date + relativedelta(days=self.delay))

    def _run_push(self, move):
        """ Apply a push rule on a move.
        If the rule is 'no step added' it will modify the destination location
        on the move.
        If the rule is 'manual operation' it will generate a new move in order
        to complete the section define by the rule.
        Care this function is not call by method run. It is called explicitely
        in stock_move.py inside the method _push_apply
        """
        self.ensure_one()
        new_date = self._get_push_new_date(move)
        if self.auto == 'transparent':
            old_dest_location = move.location_dest_id
            move.write({'date': new_date, 'location_dest_id': self.location_dest_id.id})
            # make sure the location_dest_id is consistent with the move line location dest
            if move.move_line_ids:
                move.move_line_ids.location_dest_id = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id

            # avoid looping if a push rule is not well configured; otherwise call again push_apply to see if a next step is defined
            if self.location_dest_id != old_dest_location:
                # TDE FIXME: should probably be done in the move model IMO
                return move._push_apply()[:1]
        else:
            new_move_vals = self._push_prepare_move_copy_values(move, new_date)
            new_move = move.sudo().copy(new_move_vals)
            # when no more push we should reach final destination
            if new_move._skip_push():
                new_move.write({'location_dest_id': new_move.location_final_id.id})
            if new_move._should_bypass_reservation():
                new_move.write({'procure_method': 'make_to_stock'})
            if not new_move.location_id.should_bypass_reservation():
                move.sudo().write({'move_dest_ids': [(4, new_move.id)]})
            return new_move

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        company_id = self.company_id.id
        copied_quantity = move_to_copy.quantity
        final_location_id = False
        location_dest_id = self.location_dest_id.id
        if move_to_copy.location_final_id and not move_to_copy.location_dest_id._child_of(move_to_copy.location_final_id):
            final_location_id = move_to_copy.location_final_id.id
        if move_to_copy.location_final_id and move_to_copy.location_final_id._child_of(self.location_dest_id):
            location_dest_id = move_to_copy.location_final_id.id
        if move_to_copy.product_uom.compare(move_to_copy.product_uom_qty, 0) < 0:
            copied_quantity = move_to_copy.product_uom_qty
        if not company_id:
            company_id = self.sudo().warehouse_id and self.sudo().warehouse_id.company_id.id or self.sudo().picking_type_id.warehouse_id.company_id.id
        new_move_vals = {
            'product_uom_qty': copied_quantity,
            'origin': move_to_copy.origin or move_to_copy.picking_id.name or "/",
            'location_id': move_to_copy.location_dest_id.id,
            'location_dest_id': location_dest_id,
            'location_final_id': final_location_id,
            'rule_id': self.id,
            'date': new_date,
            'date_deadline': move_to_copy.date_deadline,
            'company_id': company_id,
            'picking_id': False,
            'picking_type_id': self.picking_type_id.id,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.warehouse_id.id or move_to_copy.location_dest_id.warehouse_id.id,
            'procure_method': 'make_to_order',
        }
        return new_move_vals

    @api.model
    def _run_pull(self, procurements):
        moves_values_by_company = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!', rule.name)
                raise ProcurementException([(procurement, msg)])

        # Prepare the move values, adapt the `procure_method` if needed.
        procurements = sorted(procurements, key=lambda proc: proc[0].product_uom.compare(proc[0].product_qty, 0.0) > 0)
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                procure_method = 'make_to_stock'

            move_values = rule._get_stock_move_values(*procurement)
            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].sudo().with_company(company_id).create(moves_values)
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()
        return True

    def _get_custom_move_fields(self):
        """ The purpose of this method is to be override in order to easily add
        fields from procurement 'values' argument to move data.
        """
        return []

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'pull' or 'pull_push') set on it.

        :rtype: dictionary
        '''

        date_scheduled = fields.Datetime.to_string(
            fields.Datetime.from_string(values['date_planned']) - relativedelta(days=self.delay or 0)
        )
        date_deadline = values.get('date_deadline') and (fields.Datetime.to_datetime(values['date_deadline']) - relativedelta(days=self.delay or 0)) or False
        partner = self.partner_address_id.id or values.get('partner_id', False)
        # it is possible that we've already got some move done, so check for the done qty and create
        # a new move with the correct qty
        qty_left = product_qty

        move_dest_ids = values.get('move_dest_ids') and [(4, x.id) for x in values['move_dest_ids']] or []

        # when create chained moves for inter-warehouse transfers, set the warehouses as partners
        if not partner and move_dest_ids:
            move_dest = values['move_dest_ids']
            if location_dest_id == company_id.internal_transit_location_id:
                partners = move_dest.location_dest_id.warehouse_id.partner_id
                if len(partners) == 1:
                    partner = partners.id
                move_dest.partner_id = self.location_src_id.warehouse_id.partner_id or self.company_id.partner_id

        # If the quantity is negative the move should be considered as a refund
        if product_uom.compare(product_qty, 0.0) < 0:
            values['to_refund'] = True

        move_values = {
            'company_id': self.company_id.id or self.location_src_id.company_id.id or self.location_dest_id.company_id.id or company_id.id,
            'product_id': product_id.id,
            'product_uom': product_uom.id,
            'product_uom_qty': qty_left,
            'partner_id': partner,
            'location_id': self.location_src_id.id,
            'location_final_id': location_dest_id.id,
            'move_dest_ids': move_dest_ids,
            'rule_id': self.id,
            'reference_ids': [Command.set(values.get('reference_ids', self.env['stock.reference']).ids)],
            'procure_method': self.procure_method,
            'origin': origin,
            'picking_type_id': self.picking_type_id.id,
            'procurement_values': self._serialize_procurement_values(values),
            'route_ids': [Command.clear()] + [Command.link(route.id) for route in values.get('route_ids', [])],
            'never_product_template_attribute_value_ids': values.get('never_product_template_attribute_value_ids'),
            'warehouse_id': self.warehouse_id.id,
            'date': date_scheduled,
            'date_deadline': date_deadline,
            'propagate_cancel': self.propagate_cancel,
            'priority': values.get('priority', "0"),
            'orderpoint_id': values.get('orderpoint_id') and values['orderpoint_id'].id,
        }
        if self.location_dest_from_rule:
            move_values['location_dest_id'] = self.location_dest_id.id
        for field in self._get_custom_move_fields():
            if field in values:
                move_values[field] = values.get(field)
        return move_values

    def _serialize_procurement_values(self, values):
        """Helper method to serialize procurement values for storage.

        This method handles the serialization of different types of values:
        - BaseModel instances are converted to their IDs
        - Datetime and Date fields are converted to strings
        - Other values are kept as is

        :param values: Dictionary of procurement values
        :return: Dictionary with serialized values
        """
        serialized = {}
        for key, value in values.items():
            if isinstance(value, models.BaseModel):
                serialized[key] = value.ids
            elif isinstance(value, (datetime.datetime, datetime.date)):
                serialized[key] = value.isoformat()
            elif isinstance(value, (fields.Datetime, fields.Date)):
                serialized[key] = fields.Datetime.to_string(value) if isinstance(value, fields.Datetime) else fields.Date.to_string(value)
            else:
                serialized[key] = value
        return serialized

    def _get_lead_days(self, product, **values):
        """Returns the cumulative delay and its description encountered by a
        procurement going through the rules in `self`.

        :param product: the product of the procurement
        :type product: :class:`~odoo.addons.product.models.product.ProductProduct`
        :return: the cumulative delay and cumulative delay's description
        :rtype: tuple[defaultdict(float), list[str, str]]
        """
        # FIXME : ensure one product or make the method work with multiple products
        _ = self.env._
        delays = defaultdict(float)
        delay_description = []
        bypass_delay_description = self.env.context.get('bypass_delay_description')
        # Check if the rules have lead time
        delaying_rules = self.filtered(lambda r: r.action in ['pull', 'pull_push'] and r.delay)
        if delaying_rules:
            delays['total_delay'] += sum(delaying_rules.mapped('delay'))
            if not bypass_delay_description:
                delay_description = [
                    (_('Delay on %s', rule.name), _('+ %d day(s)', rule.delay))
                    for rule in delaying_rules
                ]
        # Check if there's a horizon set
        bypass_global_horizon_days = self.env.context.get('bypass_global_horizon_days')
        if bypass_global_horizon_days:
            return delays, delay_description
        global_horizon_days = self.env['stock.warehouse.orderpoint'].get_horizon_days()
        if global_horizon_days:
            delays['horizon_time'] += global_horizon_days
            if not bypass_delay_description:
                delay_description.append((_('Time Horizon'), _('+ %d day(s)', global_horizon_days)))
        return delays, delay_description

    @api.model
    def _skip_procurement(self, procurement):
        return procurement.product_id.type != "consu" or float_is_zero(
            procurement.product_qty, precision_rounding=procurement.product_uom.rounding
        )

    @api.model
    def run(self, procurements, raise_user_error=True):
        """Fulfil `procurements` with the help of stock rules.

        Procurements are needs of products at a certain location. To fulfil
        these needs, we need to create some sort of documents (`stock.move`
        by default, but extensions of `_run_` methods allow to create every
        type of documents).

        :param procurements: the description of the procurement
        :type procurements: list of `~odoo.addons.stock.models.stock_rule.ProcurementGroup.Procurement`
        :param raise_user_error: will raise either an UserError or a ProcurementException
        :type raise_user_error: boolan, optional
        :raises UserError: if `raise_user_error` is True and a procurement isn't fulfillable
        :raises ProcurementException: if `raise_user_error` is False and a procurement isn't fulfillable
        """

        def raise_exception(procurement_errors):
            if raise_user_error:
                dummy, errors = zip(*procurement_errors)
                raise UserError('\n'.join(errors))
            else:
                raise ProcurementException(procurement_errors)
        actions_to_run = defaultdict(list)
        procurement_errors = []
        for procurement in procurements:
            procurement.values.setdefault('company_id', procurement.location_id.company_id)
            procurement.values.setdefault('priority', '0')
            procurement.values.setdefault('date_planned', procurement.values.get('date_planned', False) or fields.Datetime.now())
            if self._skip_procurement(procurement):
                continue
            rule = self._get_rule(procurement.product_id, procurement.location_id, procurement.values)
            if not rule:
                error = _('No rule has been found to replenish "%(product)s" in "%(location)s".\nVerify the routes configuration on the product.',
                    product=procurement.product_id.display_name, location=procurement.location_id.display_name)
                procurement_errors.append((procurement, error))
            else:
                action = 'pull' if rule.action == 'pull_push' else rule.action
                actions_to_run[action].append((procurement, rule))

        if procurement_errors:
            raise_exception(procurement_errors)

        for action, procurements in actions_to_run.items():
            if hasattr(self.env['stock.rule'], '_run_%s' % action):
                try:
                    getattr(self.env['stock.rule'], '_run_%s' % action)(procurements)
                except ProcurementException as e:
                    procurement_errors += e.procurement_exceptions
            else:
                _logger.error("The method _run_%s doesn't exist on the procurement rules" % action)

        if procurement_errors:
            raise_exception(procurement_errors)
        return True

    @api.model
    def _search_rule_for_warehouses(self, route_ids, packaging_uom_id, product_id, warehouse_ids, domain):
        domain = Domain(domain)
        if warehouse_ids:
            domain &= Domain('warehouse_id', 'in', [False, *warehouse_ids.ids])
        valid_route_ids = set()
        if route_ids:
            valid_route_ids |= set(route_ids.ids)
        if packaging_uom_id:
            packaging_routes = packaging_uom_id.package_type_id.route_ids
            valid_route_ids |= set(packaging_routes.ids)
        valid_route_ids |= set((product_id.route_ids | product_id.categ_id.total_route_ids).ids)
        if warehouse_ids:
            filter_function = partial(self._filter_warehouse_routes, product_id, warehouse_ids)
            valid_route_ids |= set(warehouse_ids.route_ids.filtered(filter_function).ids)
        if valid_route_ids:
            domain &= Domain('route_id', 'in', list(valid_route_ids))
        res = self.env["stock.rule"]._read_group(
            domain,
            groupby=["location_dest_id", "warehouse_id", "route_id"],
            aggregates=["id:recordset"],
            order="route_sequence:min, sequence:min",
        )
        rule_dict = defaultdict(OrderedDict)
        for group in res:
            rule_dict[group[0].id, group[2].id][group[1].id] = group[3].sorted(lambda rule: (rule.route_sequence, rule.sequence))[0]
        return rule_dict

    def _filter_warehouse_routes(self, product, warehouses, route):
        return route

    def _search_rule(self, route_ids, packaging_uom_id, product_id, warehouse_id, domain):
        """ First find a rule among the ones defined on the procurement
        group, then try on the routes defined for the product, finally fallback
        on the default behavior
        """
        Rule = self.env['stock.rule']
        res = self.env['stock.rule']
        domain = Domain(domain)
        if warehouse_id:
            domain &= Domain('warehouse_id', 'in', [False, warehouse_id.id])
        domain = domain.optimize(Rule)
        if route_ids:
            res = Rule.search(Domain('route_id', 'in', route_ids.ids) & domain, order='route_sequence, sequence', limit=1)
        if not res and packaging_uom_id:
            packaging_routes = packaging_uom_id.package_type_id.route_ids
            if packaging_routes:
                res = Rule.search(Domain('route_id', 'in', packaging_routes.ids) & domain, order='route_sequence, sequence', limit=1)
        if not res:
            product_routes = product_id.route_ids | product_id.categ_id.total_route_ids
            if product_routes:
                res = Rule.search(Domain('route_id', 'in', product_routes.ids) & domain, order='route_sequence, sequence', limit=1)
        if not res and warehouse_id:
            warehouse_routes = warehouse_id.route_ids
            if warehouse_routes:
                res = Rule.search(Domain('route_id', 'in', warehouse_routes.ids) & domain, order='route_sequence, sequence', limit=1)
        return res

    @api.model
    def _get_rule(self, product_id, location_id, values):
        """ Find a pull rule for the location_id, fallback on the parent
        locations if it could not be found.
        """
        result = self.env['stock.rule']
        if not location_id:
            return result
        locations = location_id
        # Get the location hierarchy, starting from location_id up to its root location.
        while locations[-1].location_id:
            locations |= locations[-1].location_id
        domain = self._get_rule_domain(locations, values)
        # Get a mapping (location_id, route_id) -> warehouse_id -> rule_id
        rule_dict = self._search_rule_for_warehouses(
            values.get("route_ids", False),
            values.get("packaging_uom_id", False),
            product_id,
            values.get("warehouse_id", locations.warehouse_id),
            domain,
        )

        def extract_rule(rule_dict, route_ids, warehouse_id, location_dest_id):
            rule = self.env['stock.rule']
            for route_id in sorted(route_ids, key=lambda r: (r not in product_id.route_ids, r.sequence)):
                sub_dict = rule_dict.get((location_dest_id.id, route_id.id))
                if not sub_dict:
                    continue
                if not warehouse_id:
                    rule = sub_dict[next(iter(sub_dict))]
                else:
                    rule = sub_dict.get(warehouse_id.id)
                    rule = rule or sub_dict[False]
                if rule:
                    break
            return rule

        def get_rule_for_routes(rule_dict, route_ids, packaging_uom_id, product_id, warehouse_id, location_dest_id):
            res = self.env['stock.rule']
            if route_ids:
                res = extract_rule(rule_dict, route_ids, warehouse_id, location_dest_id)
            if not res and packaging_uom_id:
                res = extract_rule(rule_dict, packaging_uom_id.package_type_id.route_ids, warehouse_id, location_dest_id)
            if not res:
                res = extract_rule(rule_dict, product_id.route_ids | product_id.categ_id.total_route_ids, warehouse_id, location_dest_id)
            if not res and warehouse_id:
                res = extract_rule(rule_dict, warehouse_id.route_ids, warehouse_id, location_dest_id)
            return res

        location = location_id
        # Go through the location hierarchy again, this time breaking at the first valid stock.rule found
        # in rules_by_location.
        inter_comp_location_checked = False
        while (not result) and location:
            candidate_locations = location
            if not inter_comp_location_checked and self._check_intercomp_location(location):
                # Add the intercomp location to candidate_locations as the intercomp domain was added
                # above in the call to _get_rule_domain.
                inter_comp_location = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
                candidate_locations |= inter_comp_location
                inter_comp_location_checked = True
            for candidate_location in candidate_locations:
                result = get_rule_for_routes(
                    rule_dict,
                    values.get("route_ids", self.env['stock.route']),
                    values.get("packaging_uom_id", self.env['uom.uom']),
                    product_id,
                    values.get("warehouse_id", candidate_location.warehouse_id),
                    candidate_location,
                )
                if result:
                    break
            else:
                location = location.location_id
        return result

    @api.model
    def _check_intercomp_location(self, locations):
        if locations.filtered(lambda location: location.usage == 'transit'):
            inter_comp_location = self.env.ref('stock.stock_location_inter_company', raise_if_not_found=False)
            return inter_comp_location and inter_comp_location.id in locations.ids

    @api.model
    def _get_rule_domain(self, locations, values):
        location_ids = locations.ids
        # If the method is called to find rules towards the Inter-company location, also add the 'Customer' location in the domain.
        # This is to avoid having to duplicate every rules that deliver to Customer to have the Inter-company part.
        if self._check_intercomp_location(locations):
            location_ids.append(self.env.ref('stock.stock_location_customers', raise_if_not_found=False).id)
        domain = Domain('location_dest_id', 'in', location_ids) & Domain('action', '!=', 'push')
        # In case the method is called by the superuser, we need to restrict the rules to the
        # ones of the company. This is not useful as a regular user since there is a record
        # rule to filter out the rules based on the company.
        if self.env.su and values.get('company_id'):
            company_ids = set(values.get('company_id').ids)
            if values.get('route_ids'):
                company_ids |= set(values['route_ids'].company_id.ids)
            domain_company = ['|', ('company_id', '=', False), ('company_id', 'child_of', list(company_ids))]
            domain &= Domain(domain_company)
        return domain

    @api.model
    def _get_push_rule(self, product_id, location_dest_id, values):
        """ Find a push rule for the location_dest_id, with a fallback to the parent locations if none could be found.
        """
        found_rule = self.env['stock.rule']
        location = location_dest_id
        while (not found_rule) and location:
            domain = Domain('location_src_id', '=', location.id) & Domain('action', 'in', ('push', 'pull_push'))
            if dom := values.get('domain'):
                domain &= Domain(dom)
            found_rule = self._search_rule(values.get('route_ids'), values.get('packaging_uom_id'), product_id, values.get('warehouse_id'), domain)
            location = location.location_id
        return found_rule

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        return Domain([
            ('company_id', '=?', company_id),
            ('state', 'in', ['confirmed', 'partially_available']),
            ('product_uom_qty', '!=', 0.0),
            '|',
                ('reservation_date', '<=', fields.Date.today()),
                ('picking_type_id.reservation_method', '=', 'at_confirm'),
        ])

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        if use_new_cursor:
            self.env['ir.cron']._commit_progress(remaining=self._get_scheduler_tasks_to_do())

        # Minimum stock rules
        domain = self._get_orderpoint_domain(company_id=company_id)
        orderpoints = self.env['stock.warehouse.orderpoint'].search(domain)
        orderpoints.sudo()._compute_qty_to_order_computed()
        orderpoints.sudo()._compute_deadline_date()
        orderpoints.sudo()._procure_orderpoint_confirm(use_new_cursor=use_new_cursor, company_id=company_id, raise_user_error=False)

        if use_new_cursor:
            self.env['ir.cron']._commit_progress(1)

        # Search all confirmed stock_moves and try to assign them
        domain = self._get_moves_to_assign_domain(company_id)
        moves_to_assign = self.env['stock.move'].search(domain, limit=None,
            order='reservation_date, priority desc, date asc, id asc')
        for moves_chunk in split_every(1000, moves_to_assign.ids):
            self.env['stock.move'].browse(moves_chunk).sudo()._action_assign()
            if use_new_cursor:
                self.env.cr.commit()
                _logger.info("A batch of %d moves are assigned and committed", len(moves_chunk))

        if use_new_cursor:
            self.env['ir.cron']._commit_progress(1)

        # Merge duplicated quants
        self.env['stock.quant']._quant_tasks()

        if use_new_cursor:
            self.env['ir.cron']._commit_progress(1)

    @api.model
    def _get_scheduler_tasks_to_do(self):
        """ Number of task to be executed by the stock scheduler. This number will be given in log
        message to know how many tasks succeeded."""
        return 3

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        """ Call the scheduler in order to check the running procurements (super method), to check the minimum stock rules
        and the availability of moves. This function is intended to be run for all the companies at the same time, so
        we run functions as SUPERUSER to avoid intercompanies and access rights issues. """
        try:
            self._run_scheduler_tasks(use_new_cursor=use_new_cursor, company_id=company_id)
        except Exception:
            _logger.error("Error during stock scheduler", exc_info=True)
            raise
        return {}

    @api.model
    def _get_orderpoint_domain(self, company_id=False):
        domain = [('trigger', '=', 'auto'), ('product_id.active', '=', True)]
        if company_id:
            domain += [('company_id', '=', company_id)]
        return domain


# FILEPATH: odoo/addons/stock/models/stock_scrap.py (lines 10-230)
class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'Scrap'

    name = fields.Char(
        'Reference',  default=lambda self: _('New'),
        copy=False, readonly=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    origin = fields.Char(string='Source Document')
    product_id = fields.Many2one(
        'product.product', 'Product', domain="[('type', '=', 'consu')]",
        required=True, check_company=True)
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit', domain="[('id', 'in', allowed_uom_ids)]",
        compute="_compute_product_uom_id", store=True, readonly=False, precompute=True,
        required=True)
    tracking = fields.Selection(string='Product Tracking', readonly=True, related="product_id.tracking")
    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial',
        domain="[('product_id', '=', product_id)]", check_company=True)
    package_id = fields.Many2one(
        'stock.package', 'Package',
        check_company=True)
    owner_id = fields.Many2one('res.partner', 'Owner', check_company=True)
    move_ids = fields.One2many('stock.move', 'scrap_id')
    picking_id = fields.Many2one('stock.picking', 'Picking', check_company=True)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        compute='_compute_location_id', store=True, required=True, precompute=True,
        domain="[('usage', '=', 'internal')]", check_company=True, readonly=False)
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location',
        compute='_compute_scrap_location_id', store=True, required=True, precompute=True,
        domain="[('usage', '=', 'inventory')]", check_company=True, readonly=False)
    scrap_qty = fields.Float(
        'Quantity', required=True, digits='Product Unit',
        compute='_compute_scrap_qty', default=1.0, readonly=False, store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status', default="draft", readonly=True, tracking=True)
    date_done = fields.Datetime('Date', readonly=True)
    should_replenish = fields.Boolean(string='Replenish Quantities', help="Trigger replenishment for scrapped products")
    scrap_reason_tag_ids = fields.Many2many(
        comodel_name='stock.scrap.reason.tag',
        string='Scrap Reason',
    )

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids', 'product_id.seller_ids', 'product_id.seller_ids.product_uom_id')
    def _compute_allowed_uom_ids(self):
        for scrap in self:
            scrap.allowed_uom_ids = scrap.product_id.uom_id | scrap.product_id.uom_ids | scrap.product_id.seller_ids.product_uom_id

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for scrap in self:
            scrap.product_uom_id = scrap.product_id.uom_id

    @api.depends('company_id', 'picking_id')
    def _compute_location_id(self):
        company_warehouses = self.env['stock.warehouse'].search([('company_id', 'in', self.company_id.ids)])
        if len(company_warehouses) == 0 and self.company_id:
            self.env['stock.warehouse']._warehouse_redirect_warning()
        groups = company_warehouses._read_group(
            [('company_id', 'in', self.company_id.ids)], ['company_id'], ['lot_stock_id:array_agg'])
        locations_per_company = {
            company.id: lot_stock_ids[0] if lot_stock_ids else False
            for company, lot_stock_ids in groups
        }
        for scrap in self:
            if scrap.picking_id:
                scrap.location_id = scrap.picking_id.location_dest_id if scrap.picking_id.state == 'done' else scrap.picking_id.location_id
            elif scrap.company_id:
                scrap.location_id = locations_per_company[scrap.company_id.id]

    @api.depends('company_id')
    def _compute_scrap_location_id(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.company_id.ids), ('usage', '=', 'inventory')], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        for scrap in self:
            if scrap.company_id:
                scrap.scrap_location_id = locations_per_company[scrap.company_id.id]

    @api.depends('move_ids', 'move_ids.move_line_ids.quantity', 'product_id')
    def _compute_scrap_qty(self):
        self.scrap_qty = 1
        for scrap in self:
            if scrap.move_ids:
                scrap.scrap_qty = scrap.move_ids[0].quantity

    @api.onchange('lot_id')
    def _onchange_serial_number(self):
        if self.product_id.tracking == 'serial' and self.lot_id:
            message, recommended_location = self.env['stock.quant'].sudo()._check_serial_number(self.product_id,
                                                                                                self.lot_id,
                                                                                                self.company_id,
                                                                                                self.location_id,
                                                                                                self.picking_id.location_dest_id)
            if message:
                if recommended_location:
                    self.location_id = recommended_location
                return {'warning': {'title': _('Warning'), 'message': message}}

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a scrap which is done.'))

    def _prepare_move_values(self):
        self.ensure_one()
        return {
            'origin': self.origin or self.picking_id.name or self.name,
            'company_id': self.company_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'state': 'draft',
            'product_uom_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrap_id': self.id,
            'location_dest_id': self.scrap_location_id.id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'quantity': self.scrap_qty,
                'location_id': self.location_id.id,
                'location_dest_id': self.scrap_location_id.id,
                'package_id': self.package_id.id,
                'owner_id': self.owner_id.id,
                'lot_id': self.lot_id.id,
            })],
            # 'restrict_partner_id': self.owner_id.id,
            'picked': True,
            'picking_id': self.picking_id.id
        }

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            scrap.write({'state': 'done'})
            scrap.date_done = fields.Datetime.now()
            if scrap.should_replenish:
                scrap.do_replenish()
        return True

    def do_replenish(self, values=False):
        self.ensure_one()
        values = values or {}
        self.with_context(clean_context(self.env.context)).env['stock.rule'].run([self.env['stock.rule'].Procurement(
            self.product_id,
            self.scrap_qty,
            self.product_uom_id,
            self.location_id,
            self.name,
            self.name,
            self.company_id,
            values
        )])

    def action_get_stock_picking(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    def action_get_stock_move_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.stock_move_line_action')
        action['domain'] = [('move_id', 'in', self.move_ids.ids)]
        return action

    def _should_check_available_qty(self):
        return self.product_id.is_storable

    def check_available_qty(self):
        if not self._should_check_available_qty():
            return True

        precision = self.env['decimal.precision'].precision_get('Product Unit')
        available_qty = self.with_context(
            location=self.location_id.id,
            lot_id=self.lot_id.id,
            package_id=self.package_id.id,
            owner_id=self.owner_id.id,
            strict=True,
        ).product_id.qty_available
        scrap_qty = self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id)
        return float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0

    def action_validate(self):
        self.ensure_one()
        if self.product_uom_id.is_zero(self.scrap_qty):
            raise UserError(_('You can only enter positive quantities.'))
        if self.check_available_qty():
            return self.do_scrap()
        else:
            ctx = dict(self.env.context)
            ctx.update({
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_scrap_id': self.id,
                'default_quantity': self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id),
                'default_product_uom_name': self.product_id.uom_name
            })
            return {
                'name': _('%(product)s: Insufficient Quantity To Scrap', product=self.product_id.display_name),
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }


# FILEPATH: odoo/addons/stock/models/stock_scrap.py (lines 233-245)
class StockScrapReasonTag(models.Model):
    _name = 'stock.scrap.reason.tag'
    _description = 'Scrap Reason Tag'
    _order = 'sequence, id'
    name = fields.Char(string="Name", required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Char(string="Color", default='#3C3C3C')
    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!',
    )


# FILEPATH: odoo/addons/stock/models/stock_storage_category.py (lines 7-45)
class StockStorageCategory(models.Model):
    _name = 'stock.storage.category'
    _description = "Storage Category"
    _order = "name"

    name = fields.Char('Storage Category', required=True)
    max_weight = fields.Float('Max Weight', digits='Stock Weight')
    capacity_ids = fields.One2many('stock.storage.category.capacity', 'storage_category_id', copy=True)
    product_capacity_ids = fields.One2many('stock.storage.category.capacity', compute="_compute_storage_capacity_ids", inverse="_set_storage_capacity_ids")
    package_capacity_ids = fields.One2many('stock.storage.category.capacity', compute="_compute_storage_capacity_ids", inverse="_set_storage_capacity_ids")
    allow_new_product = fields.Selection([
        ('empty', 'If the location is empty'),
        ('same', 'If all products are same'),
        ('mixed', 'Allow mixed products')], default='mixed', required=True)
    location_ids = fields.One2many('stock.location', 'storage_category_id')
    company_id = fields.Many2one('res.company', 'Company')
    weight_uom_name = fields.Char(string='Weight unit', compute='_compute_weight_uom_name')

    _positive_max_weight = models.Constraint(
        'CHECK(max_weight >= 0)',
        'Max weight should be a positive number.',
    )

    @api.depends('capacity_ids')
    def _compute_storage_capacity_ids(self):
        for storage_category in self:
            storage_category.product_capacity_ids = storage_category.capacity_ids.filtered(lambda c: c.product_id)
            storage_category.package_capacity_ids = storage_category.capacity_ids.filtered(lambda c: c.package_type_id)

    def _compute_weight_uom_name(self):
        self.weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def _set_storage_capacity_ids(self):
        for storage_category in self:
            storage_category.capacity_ids = storage_category.product_capacity_ids | storage_category.package_capacity_ids

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        return [dict(vals, name=self.env._("%s (copy)", category.name)) for category, vals in zip(self, vals_list)]


# FILEPATH: odoo/addons/stock/models/stock_storage_category.py (lines 48-75)
class StockStorageCategoryCapacity(models.Model):
    _name = 'stock.storage.category.capacity'
    _description = "Storage Category Capacity"
    _check_company_auto = True
    _order = "storage_category_id"

    storage_category_id = fields.Many2one('stock.storage.category', ondelete='cascade', required=True, index=True)
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', check_company=True, index='btree_not_null',
        domain=("[('product_tmpl_id', '=', context.get('active_id', False))] if context.get('active_model') == 'product.template' else"
            " [('id', '=', context.get('default_product_id', False))] if context.get('default_product_id') else"
            " [('is_storable', '=', True)]"))
    package_type_id = fields.Many2one('stock.package.type', 'Package Type', ondelete='cascade', check_company=True, index='btree_not_null')
    quantity = fields.Float('Quantity', required=True)
    product_uom_id = fields.Many2one(related='product_id.uom_id')
    company_id = fields.Many2one('res.company', 'Company', related="storage_category_id.company_id")

    _positive_quantity = models.Constraint(
        'CHECK(quantity > 0)',
        'Quantity should be a positive number.',
    )
    _unique_product = models.Constraint(
        'UNIQUE(product_id, storage_category_id)',
        'Multiple capacity rules for one product.',
    )
    _unique_package_type = models.Constraint(
        'UNIQUE(package_type_id, storage_category_id)',
        'Multiple capacity rules for one package type.',
    )


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
    # namedtuple used in helper methods generating values for routes
    Routing = namedtuple('Routing', ['from_loc', 'dest_loc', 'picking_type', 'action'])

    def _default_name(self):
        count = self.env['stock.warehouse'].with_context(active_test=False).search_count([('company_id', '=', self.env.company.id)])
        return "%s - warehouse # %s" % (self.env.company.name, count + 1) if count else self.env.company.name

    name = fields.Char('Warehouse', required=True, default=_default_name)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        readonly=True, required=True,
        help='The company is automatically set from your user preferences.')
    partner_id = fields.Many2one('res.partner', 'Address', default=lambda self: self.env.company.partner_id, check_company=True)
    view_location_id = fields.Many2one(
        'stock.location', 'View Location',
        domain="[('usage', '=', 'view'), ('company_id', '=', company_id)]",
        required=True, check_company=True, index=True)
    lot_stock_id = fields.Many2one(
        'stock.location', 'Location Stock',
        domain="[('usage', '=', 'internal'), ('company_id', '=', company_id)]",
        required=True, check_company=True)
    code = fields.Char('Short Name', required=True, size=5, help="Short name used to identify your warehouse")
    route_ids = fields.Many2many(
        'stock.route', 'stock_route_warehouse', 'warehouse_id', 'route_id',
        'Routes',
        domain="[('warehouse_selectable', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Defaults routes through the warehouse', check_company=True, copy=False)
    reception_steps = fields.Selection([
        ('one_step', 'Receive and Store (1 step)'),
        ('two_steps', 'Receive then Store (2 steps)'),
        ('three_steps', 'Receive, Quality Control, then Store (3 steps)')],
        'Incoming Shipments', default='one_step', required=True,
        help="Default incoming route to follow")
    delivery_steps = fields.Selection([
        ('ship_only', 'Deliver (1 step)'),
        ('pick_ship', 'Pick then Deliver (2 steps)'),
        ('pick_pack_ship', 'Pick, Pack, then Deliver (3 steps)')],
        'Outgoing Shipments', default='ship_only', required=True,
        help="Default outgoing route to follow")
    wh_input_stock_loc_id = fields.Many2one('stock.location', 'Input Location', check_company=True)
    wh_qc_stock_loc_id = fields.Many2one('stock.location', 'Quality Control Location', check_company=True)
    wh_output_stock_loc_id = fields.Many2one('stock.location', 'Output Location', check_company=True)
    wh_pack_stock_loc_id = fields.Many2one('stock.location', 'Packing Location', check_company=True)
    mto_pull_id = fields.Many2one('stock.rule', 'MTO rule', copy=False)
    pick_type_id = fields.Many2one('stock.picking.type', 'Pick Type', check_company=True, copy=False)
    pack_type_id = fields.Many2one('stock.picking.type', 'Pack Type', check_company=True, copy=False)
    out_type_id = fields.Many2one('stock.picking.type', 'Out Type', check_company=True, copy=False)
    in_type_id = fields.Many2one('stock.picking.type', 'In Type', check_company=True, copy=False)
    int_type_id = fields.Many2one('stock.picking.type', 'Internal Type', check_company=True, copy=False)
    qc_type_id = fields.Many2one('stock.picking.type', 'Quality Control Type', check_company=True, copy=False)
    store_type_id = fields.Many2one('stock.picking.type', 'Storage Type', check_company=True, copy=False)
    xdock_type_id = fields.Many2one('stock.picking.type', 'Cross Dock Type', check_company=True, copy=False)
    reception_route_id = fields.Many2one('stock.route', 'Receipt Route', ondelete='restrict', copy=False)
    delivery_route_id = fields.Many2one('stock.route', 'Delivery Route', ondelete='restrict', copy=False)
    resupply_wh_ids = fields.Many2many(
        'stock.warehouse', 'stock_wh_resupply_table', 'supplied_wh_id', 'supplier_wh_id',
        'Resupply From', help="Routes will be created automatically to resupply this warehouse from the warehouses ticked")
    resupply_route_ids = fields.One2many(
        'stock.route', 'supplied_wh_id', 'Resupply Routes',
        help="Routes will be created for these resupply warehouses and you can select them on products and product categories", copy=False)
    sequence = fields.Integer(default=10,
        help="Gives the sequence of this line when displaying the warehouses.")
    _warehouse_name_uniq = models.Constraint(
        'unique(name, company_id)',
        'The name of the warehouse must be unique per company!',
    )
    _warehouse_code_uniq = models.Constraint(
        'unique(code, company_id)',
        'The short name of the warehouse must be unique per company!',
    )

    @api.onchange('company_id')
    def _onchange_company_id(self):
        group_user = self.env.ref('base.group_user')
        group_stock_multi_warehouses = self.env.ref('stock.group_stock_multi_warehouses')
        group_stock_multi_location = self.env.ref('stock.group_stock_multi_locations')
        if group_stock_multi_warehouses not in group_user.implied_ids and group_stock_multi_location not in group_user.implied_ids:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Creating a new warehouse will automatically activate the Storage Locations setting')
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('company_id'):
                company = self.env['res.company'].browse(vals['company_id'])
                if 'name' not in vals:
                    vals['name'] = company.name
                if 'code' not in vals:
                    vals['code'] = company.name[:5]
                if 'partner_id' not in vals:
                    vals['partner_id'] = company.partner_id.id
            # create view location for warehouse then create all locations
            loc_vals = {'name': vals.get('code'), 'usage': 'view'}
            if vals.get('company_id'):
                loc_vals['company_id'] = vals.get('company_id')
            vals['view_location_id'] = self.env['stock.location'].create(loc_vals).id
            sub_locations = self._get_locations_values(vals)

            for field_name, values in sub_locations.items():
                values['location_id'] = vals['view_location_id']
                if vals.get('company_id'):
                    values['company_id'] = vals.get('company_id')
                vals[field_name] = self.env['stock.location'].with_context(active_test=False).create(values).id

        # actually create WH
        warehouses = super().create(vals_list)

        for warehouse, vals in zip(warehouses, vals_list):
            # create sequences and operation types
            new_vals = warehouse._create_or_update_sequences_and_picking_types()
            warehouse.write(new_vals)  # TDE FIXME: use super ?
            # create routes and push/stock rules
            route_vals = warehouse._create_or_update_route()
            warehouse.write(route_vals)

            # Update global route with specific warehouse rule.
            warehouse._create_or_update_global_routes_rules()

            # create route selectable on the product to resupply the warehouse from another one
            warehouse.create_resupply_routes(warehouse.resupply_wh_ids)

            # update partner data if partner assigned
            if vals.get('partner_id'):
                self._update_partner_data(vals['partner_id'], vals.get('company_id'))

            # manually update locations' warehouse since it didn't exist at their creation time
            view_location_id = self.env['stock.location'].browse(vals.get('view_location_id'))
            (view_location_id | view_location_id.with_context(active_test=False).child_ids).write({'warehouse_id': warehouse.id})

        self._check_multiwarehouse_group()

        return warehouses

    @api.model
    def _warehouse_redirect_warning(self):
        warehouse_action = self.env.ref('stock.action_warehouse_form')
        msg = _('Please create a warehouse for company %s.', self.env.company.display_name)
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise UserError(self.env._('Please contact your administrator to configure your warehouse.'))
        raise RedirectWarning(msg, warehouse_action.id, _('Go to Warehouses'))

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for warehouse, vals in zip(self, vals_list):
            if 'name' not in default:
                vals['name'] = _("%s (copy)", warehouse.name)
            if 'code' not in default:
                vals['code'] = _("COPY")
        return vals_list

    def write(self, vals):
        if 'company_id' in vals:
            for warehouse in self:
                if warehouse.company_id.id != vals['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))

        Route = self.env['stock.route']
        warehouses = self.with_context(active_test=False)
        warehouses._create_missing_locations(vals)

        if vals.get('reception_steps'):
            warehouses._update_location_reception(vals['reception_steps'])
        if vals.get('delivery_steps'):
            warehouses._update_location_delivery(vals['delivery_steps'])
        if vals.get('reception_steps') or vals.get('delivery_steps'):
            warehouses._update_reception_delivery_resupply(vals.get('reception_steps'), vals.get('delivery_steps'))

        if vals.get('resupply_wh_ids') and not vals.get('resupply_route_ids'):
            old_resupply_whs = {warehouse.id: warehouse.resupply_wh_ids for warehouse in warehouses}

        # If another partner assigned
        if vals.get('partner_id'):
            if vals.get('company_id'):
                warehouses._update_partner_data(vals['partner_id'], vals.get('company_id'))
            else:
                for warehouse in self:
                    warehouse._update_partner_data(vals['partner_id'], warehouse.company_id.id)

        if vals.get('code') or vals.get('name'):
            warehouses._update_name_and_code(vals.get('name'), vals.get('code'))

        res = super().write(vals)

        for warehouse in warehouses:
            # check if we need to delete and recreate route
            depends = [depend for depends in [value.get('depends', []) for value in warehouse._get_routes_values().values()] for depend in depends]
            if 'code' in vals or any(depend in vals for depend in depends):
                picking_type_vals = warehouse._create_or_update_sequences_and_picking_types()
                if picking_type_vals:
                    warehouse.write(picking_type_vals)
            if any(depend in vals for depend in depends):
                route_vals = warehouse._create_or_update_route()
                if route_vals:
                    warehouse.write(route_vals)
            # Check if a global rule(mto, buy, ...) need to be modify.
            # The field that impact those rules are listed in the
            # _get_global_route_rules_values method under the key named
            # 'depends'.
            global_rules = warehouse._get_global_route_rules_values()
            depends = [depend for depends in [value.get('depends', []) for value in global_rules.values()] for depend in depends]
            if any(rule in vals for rule in global_rules) or\
                    any(depend in vals for depend in depends):
                warehouse._create_or_update_global_routes_rules()

            if 'active' in vals:
                picking_type_ids = self.env['stock.picking.type'].with_context(active_test=False).search([('warehouse_id', '=', warehouse.id)])
                move_ids = self.env['stock.move'].search([
                    ('picking_type_id', 'in', picking_type_ids.ids),
                    ('state', 'not in', ('done', 'cancel')),
                ])
                if move_ids:
                    raise UserError(_(
                        'You still have ongoing operations for operation types %(operations)s in warehouse %(warehouse)s',
                        operations=move_ids.mapped('picking_type_id.name'),
                        warehouse=warehouse.name,
                    ))
                else:
                    picking_type_ids.write({'active': vals['active']})
                location_ids = self.env['stock.location'].with_context(active_test=False).search([('location_id', 'child_of', warehouse.view_location_id.id)])
                picking_type_using_locations = self.env['stock.picking.type'].search([
                    ('default_location_src_id', 'in', location_ids.ids),
                    ('default_location_dest_id', 'in', location_ids.ids),
                    ('id', 'not in', picking_type_ids.ids),
                ])
                if picking_type_using_locations:
                    raise UserError(_(
                        '%(operations)s have default source or destination locations within warehouse %(warehouse)s, therefore you cannot archive it.',
                        operations=picking_type_using_locations.mapped('name'),
                        warehouse=warehouse.name,
                    ))
                warehouse.view_location_id.write({'active': vals['active']})

                rule_ids = self.env['stock.rule'].with_context(active_test=False).search([('warehouse_id', '=', warehouse.id)])
                # Only modify route that apply on this warehouse.
                warehouse.route_ids.filtered(lambda r: len(r.warehouse_ids) == 1).write({'active': vals['active']})
                rule_ids.write({'active': vals['active']})

                if warehouse.active:
                    # Catch all warehouse fields that trigger a modfication on
                    # routes, rules, picking types and locations (e.g the reception
                    # steps). The purpose is to write on it in order to let the
                    # write method set the correct field to active or archive.
                    depends = set([])
                    for rule_item in warehouse._get_global_route_rules_values().values():
                        for depend in rule_item.get('depends', []):
                            depends.add(depend)
                    for rule_item in warehouse._get_routes_values().values():
                        for depend in rule_item.get('depends', []):
                            depends.add(depend)
                    values = {'resupply_route_ids': [(4, route.id) for route in warehouse.resupply_route_ids]}
                    for depend in depends:
                        values.update({depend: warehouse[depend]})
                    warehouse.write(values)

        if vals.get('resupply_wh_ids') and not vals.get('resupply_route_ids'):
            for warehouse in warehouses:
                new_resupply_whs = warehouse.resupply_wh_ids
                to_add = new_resupply_whs - old_resupply_whs[warehouse.id]
                to_remove = old_resupply_whs[warehouse.id] - new_resupply_whs
                if to_add:
                    existing_routes = Route.search([
                        ('supplied_wh_id', '=', warehouse.id),
                        ('supplier_wh_id', 'in', to_add.ids),
                        ('active', '=', False)
                    ])
                    existing_routes.action_unarchive()
                    remaining_to_add = to_add - existing_routes.supplier_wh_id
                    if remaining_to_add:
                        warehouse.create_resupply_routes(remaining_to_add)
                if to_remove:
                    to_disable_route_ids = Route.search([
                        ('supplied_wh_id', '=', warehouse.id),
                        ('supplier_wh_id', 'in', to_remove.ids),
                        ('active', '=', True)
                    ])
                    to_disable_route_ids.action_archive()

        if 'active' in vals:
            self._check_multiwarehouse_group()
        return res

    def unlink(self):
        res = super().unlink()
        self._check_multiwarehouse_group()
        return res

    def _check_multiwarehouse_group(self):
        cnt_by_company = self.env['stock.warehouse'].sudo()._read_group([('active', '=', True)], ['company_id'], aggregates=['__count'])
        if cnt_by_company:
            max_count = max(count for company, count in cnt_by_company)
            group_user = self.env.ref('base.group_user')
            group_stock_multi_warehouses = self.env.ref('stock.group_stock_multi_warehouses')
            group_stock_multi_locations = self.env.ref('stock.group_stock_multi_locations')
            if max_count <= 1 and group_stock_multi_warehouses in group_user.implied_ids:
                group_user.write({'implied_ids': [(3, group_stock_multi_warehouses.id)]})
                group_stock_multi_warehouses.write({'user_ids': [(3, user.id) for user in group_user.all_user_ids]})
            if max_count > 1 and group_stock_multi_warehouses not in group_user.implied_ids:
                if group_stock_multi_locations not in group_user.implied_ids:
                    self.env['res.config.settings'].create({
                        'group_stock_multi_locations': True,
                    }).execute()
                group_user.write({'implied_ids': [(4, group_stock_multi_warehouses.id), (4, group_stock_multi_locations.id)]})

    @api.model
    def _update_partner_data(self, partner_id, company_id):
        if not partner_id:
            return
        ResCompany = self.env['res.company']
        if company_id:
            transit_loc = ResCompany.browse(company_id).internal_transit_location_id.id
            self.env['res.partner'].browse(partner_id).with_company(company_id).write({'property_stock_customer': transit_loc, 'property_stock_supplier': transit_loc})
        else:
            transit_loc = self.env.company.internal_transit_location_id.id
            self.env['res.partner'].browse(partner_id).write({'property_stock_customer': transit_loc, 'property_stock_supplier': transit_loc})

    def _create_or_update_sequences_and_picking_types(self):
        """ Create or update existing picking types for a warehouse.
        Pikcing types are stored on the warehouse in a many2one. If the picking
        type exist this method will update it. The update values can be found in
        the method _get_picking_type_update_values. If the picking type does not
        exist it will be created with a new sequence associated to it.
        """
        self.ensure_one()
        IrSequenceSudo = self.env['ir.sequence'].sudo()
        PickingType = self.env['stock.picking.type']

        # choose the next available color for the operation types of this warehouse
        all_used_colors = [res['color'] for res in PickingType.search_read([('warehouse_id', '!=', False), ('color', '!=', False)], ['color'], order='color')]
        available_colors = [zef for zef in range(0, 12) if zef not in all_used_colors]
        color = available_colors[0] if available_colors else 0

        warehouse_data = {}
        sequence_data = self._get_sequence_values()

        # suit for each warehouse: reception, internal, pick, pack, ship
        max_sequence = self.env['stock.picking.type'].search_read([('sequence', '!=', False)], ['sequence'], limit=1, order='sequence desc')
        max_sequence = max_sequence and max_sequence[0]['sequence'] or 0

        data = self._get_picking_type_update_values()
        create_data, max_sequence = self._get_picking_type_create_values(max_sequence)

        for picking_type, values in data.items():
            if self[picking_type]:
                self[picking_type].sudo().sequence_id.write({'company_id': self.company_id.id})
                self[picking_type].write(values)
            else:
                data[picking_type].update(create_data[picking_type])
                existing_sequence = IrSequenceSudo.search_count([('company_id', '=', sequence_data[picking_type]['company_id']), ('name', '=', sequence_data[picking_type]['name'])], limit=1)
                sequence = IrSequenceSudo.create(sequence_data[picking_type])
                if existing_sequence:
                    sequence.name = _("%(name)s (copy)(%(id)s)", name=sequence.name, id=str(sequence.id))
                values.update(warehouse_id=self.id, color=color, sequence_id=sequence.id)
                warehouse_data[picking_type] = PickingType.create(values).id

        if 'out_type_id' in warehouse_data:
            PickingType.browse(warehouse_data['out_type_id']).write({'return_picking_type_id': warehouse_data.get('in_type_id', False)})
        if 'in_type_id' in warehouse_data:
            PickingType.browse(warehouse_data['in_type_id']).write({'return_picking_type_id': warehouse_data.get('out_type_id', False)})
        return warehouse_data

    def _create_or_update_global_routes_rules(self):
        """ Some rules are not specific to a warehouse(e.g MTO, Buy, ...)
        however they contain rule(s) for a specific warehouse. This method will
        update the rules contained in global routes in order to make them match
        with the wanted reception, delivery,... steps.
        """
        for rule_field, rule_details in self._get_global_route_rules_values().items():
            values = rule_details.get('update_values', {})
            if self[rule_field]:
                self[rule_field].write(values)
            else:
                values.update(rule_details['create_values'])
                values.update({'warehouse_id': self.id})
                self[rule_field] = self.env['stock.rule'].create(values)
        return True

    def _find_or_create_global_route(self, xml_id, route_name, create=True, raise_if_not_found=False):
        """ return a route record set from an xml_id or its name. """
        data_route = route = self.env.ref(xml_id, raise_if_not_found=False)
        company = self.company_id[:1] or self.env.company
        if not route or (route.sudo().company_id and route.sudo().company_id != company):
            route = self.env['stock.route'].with_context(active_test=False).search([
                ('name', 'like', route_name), ('company_id', 'in', [False, company.id])
            ], order='company_id', limit=1)
        if not route:
            if raise_if_not_found:
                raise UserError(_('Can\'t find any generic route %s.', route_name))
            elif data_route and create:
                route = data_route.copy({'name': route_name, 'company_id': company.id, 'rule_ids': False})
        return route

    def _get_global_route_rules_values(self):
        """ Method used by _create_or_update_global_routes_rules. It's
        purpose is to return a dict with this format.
        key: The rule contained in a global route that have to be create/update
        entry a dict with the following values:
            -depends: Field that impact the rule. When a field in depends is
            write on the warehouse the rule set as key have to be update.
            -create_values: values used in order to create the rule if it does
            not exist.
            -update_values: values used to update the route when a field in
            depends is modify on the warehouse.
        """
        vals = self._generate_global_route_rules_values()
        # `route_id` might be `False` if the user has deleted it, in such case we
        # should simply ignore the rule
        return {k: v for k, v in vals.items() if v.get('create_values', {}).get('route_id', True) and v.get('update_values', {}).get('route_id', True)}

    def _generate_global_route_rules_values(self):
        # We use 0 since routing are order from stock to cust. If the routing
        # order is modify, the mto rule will be wrong.
        rule = self.get_rules_dict()[self.id][self.delivery_steps]
        rule = [r for r in rule if r.from_loc == self.lot_stock_id][0]
        location_id = rule.from_loc
        location_dest_id = rule.dest_loc
        picking_type_id = rule.picking_type
        return {
            'mto_pull_id': {
                'depends': ['delivery_steps'],
                'create_values': {
                    'active': True,
                    'procure_method': 'make_to_order',
                    'company_id': self.company_id.id,
                    'action': 'pull',
                    'auto': 'manual',
                    'propagate_carrier': True,
                    'route_id': self._find_or_create_global_route('stock.route_warehouse0_mto', _('Replenish on Order (MTO)')).id
                },
                'update_values': {
                    'name': self._format_rulename(location_id, location_dest_id, 'MTO'),
                    'location_dest_id': location_dest_id.id,
                    'location_src_id': location_id.id,
                    'picking_type_id': picking_type_id.id,
                }
            }
        }

    def _create_or_update_route(self):
        """ Create or update the warehouse's routes.
        _get_routes_values method return a dict with:
            - route field name (e.g: delivery_route_id).
            - field that trigger an update on the route (key 'depends').
            - routing_key used in order to find rules contained in the route.
            - create values.
            - update values when a field in depends is modified.
            - rules default values.
        This method do an iteration on each route returned and update/create
        them. In order to update the rules contained in the route it will
        use the get_rules_dict that return a dict:
            - a receptions/delivery,... step value as key (e.g  'pick_ship')
            - a list of routing object that represents the rules needed to
            fullfil the pupose of the route.
        The routing_key from _get_routes_values is match with the get_rules_dict
        key in order to create/update the rules in the route
        (_find_existing_rule_or_create method is responsible for this part).
        """
        # Create routes and active/create their related rules.
        self.ensure_one()
        routes = []
        rules_dict = self.get_rules_dict()
        for route_field, route_data in self._get_routes_values().items():
            # If the route exists update it
            if self[route_field]:
                route = self[route_field]
                if 'route_update_values' in route_data:
                    route.write(route_data['route_update_values'])
                route.rule_ids.write({'active': False})
            # Create the route
            else:
                if 'route_update_values' in route_data:
                    route_data['route_create_values'].update(route_data['route_update_values'])
                route = self.env['stock.route'].create(route_data['route_create_values'])
                self[route_field] = route
            # Get rules needed for the route
            routing_key = route_data.get('routing_key')
            rules = rules_dict[self.id][routing_key]
            if 'rules_values' in route_data:
                route_data['rules_values'].update({'route_id': route.id})
            else:
                route_data['rules_values'] = {'route_id': route.id}
            rules_list = self._get_rule_values(
                rules, values=route_data['rules_values'])
            # Create/Active rules
            self._find_existing_rule_or_create(rules_list)
            if route_data['route_create_values'].get('warehouse_selectable', False) or route_data['route_update_values'].get('warehouse_selectable', False):
                routes.append(self[route_field])
        return {
            'route_ids': [(4, route.id) for route in routes],
        }

    def _get_routes_values(self):
        """ Return information in order to update warehouse routes.
        - The key is a route field sotred as a Many2one on the warehouse
        - This key contains a dict with route values:
            - routing_key: a key used in order to match rules from
            get_rules_dict function. It would be usefull in order to generate
            the route's rules.
            - route_create_values: When the Many2one does not exist the route
            is created based on values contained in this dict.
            - route_update_values: When a field contained in 'depends' key is
            modified and the Many2one exist on the warehouse, the route will be
            update with the values contained in this dict.
            - rules_values: values added to the routing in order to create the
            route's rules.
        """
        return {
            'reception_route_id': {
                'routing_key': self.reception_steps,
                'depends': ['reception_steps'],
                'route_update_values': {
                    'name': self._format_routename(route_type=self.reception_steps),
                    'active': self.active,
                },
                'route_create_values': {
                    'product_categ_selectable': True,
                    'warehouse_selectable': True,
                    'product_selectable': False,
                    'company_id': self.company_id.id,
                    'sequence': 50,
                },
                'rules_values': {
                    'active': True,
                    'propagate_cancel': True,
                }
            },
            'delivery_route_id': {
                'routing_key': self.delivery_steps,
                'depends': ['delivery_steps'],
                'route_update_values': {
                    'name': self._format_routename(route_type=self.delivery_steps),
                    'active': self.active,
                },
                'route_create_values': {
                    'product_categ_selectable': True,
                    'warehouse_selectable': True,
                    'product_selectable': False,
                    'company_id': self.company_id.id,
                    'sequence': 60,
                },
                'rules_values': {
                    'active': True,
                    'propagate_carrier': True
                }
            },
        }

    def _get_receive_routes_values(self, installed_depends):
        """ Return receive route values with 'procure_method': 'make_to_order'
        in order to update warehouse routes.

        This function has the same receive route values as _get_routes_values with the addition of
        'procure_method': 'make_to_order' to the 'rules_values'. This is expected to be used by
        modules that extend stock and add actions that can trigger receive 'make_to_order' rules (i.e.
        we don't want any of the generated rules by get_rules_dict to default to 'make_to_stock').
        Additionally this is expected to be used in conjunction with _get_receive_rules_dict().

        args:
        installed_depends - string value of installed (warehouse) boolean to trigger updating of reception route.
        """
        return {
            'reception_route_id': {
                'routing_key': self.reception_steps,
                'depends': ['reception_steps', installed_depends],
                'route_update_values': {
                    'name': self._format_routename(route_type=self.reception_steps),
                    'active': self.active,
                },
                'route_create_values': {
                    'product_categ_selectable': True,
                    'warehouse_selectable': True,
                    'product_selectable': False,
                    'company_id': self.company_id.id,
                    'sequence': 9,
                },
                'rules_values': {
                    'active': True,
                    'propagate_cancel': True,
                    'procure_method': 'make_to_order',
                }
            }
        }

    def _find_existing_rule_or_create(self, rules_list):
        """ This method will find existing rules or create new one. """
        for rule_vals in rules_list:
            existing_rule = self.env['stock.rule'].search([
                ('picking_type_id', '=', rule_vals['picking_type_id']),
                ('location_src_id', '=', rule_vals['location_src_id']),
                ('location_dest_id', '=', rule_vals['location_dest_id']),
                ('route_id', '=', rule_vals['route_id']),
                ('action', '=', rule_vals['action']),
                ('active', '=', False),
            ])
            if not existing_rule:
                self.env['stock.rule'].create(rule_vals)
            else:
                existing_rule.write({'active': True})

    def _get_locations_values(self, vals, code=False):
        """ Update the warehouse locations. """
        def_values = self.default_get(['reception_steps', 'delivery_steps'])
        reception_steps = vals.get('reception_steps', def_values['reception_steps'])
        delivery_steps = vals.get('delivery_steps', def_values['delivery_steps'])
        code = vals.get('code') or code or ''
        code = code.replace(' ', '').upper()
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        sub_locations = {
            'lot_stock_id': {
                'name': _('Stock'),
                'active': True,
                'usage': 'internal',
                'replenish_location': True,
                'barcode': self._valid_barcode(code + 'STOCK', company_id)
            },
            'wh_input_stock_loc_id': {
                'name': _('Input'),
                'active': reception_steps != 'one_step',
                'usage': 'internal',
                'barcode': self._valid_barcode(code + 'INPUT', company_id)
            },
            'wh_qc_stock_loc_id': {
                'name': _('Quality Control'),
                'active': reception_steps == 'three_steps',
                'usage': 'internal',
                'barcode': self._valid_barcode(code + 'QUALITY', company_id)
            },
            'wh_output_stock_loc_id': {
                'name': _('Output'),
                'active': delivery_steps != 'ship_only',
                'usage': 'internal',
                'barcode': self._valid_barcode(code + 'OUTPUT', company_id)
            },
            'wh_pack_stock_loc_id': {
                'name': _('Packing Zone'),
                'active': delivery_steps == 'pick_pack_ship',
                'usage': 'internal',
                'barcode': self._valid_barcode(code + 'PACKING', company_id)
            },
        }
        return sub_locations

    def _valid_barcode(self, barcode, company_id):
        location = self.env['stock.location'].with_context(active_test=False).search([
            ('barcode', '=', barcode),
            ('company_id', '=', company_id)
        ])
        return not location and barcode

    def _create_missing_locations(self, vals):
        """ It could happen that the user delete a mandatory location or a
        module with new locations was installed after some warehouses creation.
        In this case, this function will create missing locations in order to
        avoid mistakes during picking types and rules creation.
        """
        for warehouse in self:
            company_id = vals.get('company_id', warehouse.company_id.id)
            sub_locations = warehouse._get_locations_values(dict(vals, company_id=company_id), warehouse.code)
            missing_location = {}
            for location, location_values in sub_locations.items():
                if not warehouse[location] and location not in vals:
                    location_values['location_id'] = vals.get('view_location_id', warehouse.view_location_id.id)
                    location_values['company_id'] = company_id
                    missing_location[location] = self.env['stock.location'].create(location_values).id
            if missing_location:
                warehouse.write(missing_location)

    def create_resupply_routes(self, supplier_warehouses):
        Route = self.env['stock.route']
        Rule = self.env['stock.rule']

        dummy, output_location = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        internal_transit_location, external_transit_location = self._get_transit_locations()

        for supplier_wh in supplier_warehouses:
            transit_location = internal_transit_location if supplier_wh.company_id == self.company_id else external_transit_location
            if not transit_location:
                continue
            transit_location.active = True
            output_location = supplier_wh.lot_stock_id if supplier_wh.delivery_steps == 'ship_only' else supplier_wh.wh_output_stock_loc_id
            # Create extra MTO rule (only for 'ship only' because in the other cases MTO rules already exists)
            if supplier_wh.delivery_steps == 'ship_only':
                routing = [self.Routing(output_location, transit_location, supplier_wh.out_type_id, 'pull')]
                mto_vals = supplier_wh._get_global_route_rules_values().get('mto_pull_id')
                values = mto_vals['create_values']
                mto_rule_val = supplier_wh._get_rule_values(routing, values, name_suffix='MTO')
                Rule.create(mto_rule_val[0])

            inter_wh_route = Route.create(self._get_inter_warehouse_route_values(supplier_wh))

            pull_rules_list = supplier_wh._get_supply_pull_rules_values(
                [self.Routing(output_location, transit_location, supplier_wh.out_type_id, 'pull')],
                values={'route_id': inter_wh_route.id, 'location_dest_from_rule': True})
            if supplier_wh.delivery_steps != 'ship_only':
                # Replenish from Output location
                pull_rules_list += supplier_wh._get_supply_pull_rules_values(
                    [self.Routing(supplier_wh.lot_stock_id, output_location, supplier_wh.pick_type_id, 'pull')],
                    values={'route_id': inter_wh_route.id})
            pull_rules_list += self._get_supply_pull_rules_values(
                [self.Routing(transit_location, self.lot_stock_id, self.in_type_id, 'pull')],
                values={'route_id': inter_wh_route.id})
            for pull_rule_vals in pull_rules_list:
                Rule.create(pull_rule_vals)

    # Routing tools
    # ------------------------------------------------------------

    def _get_input_output_locations(self, reception_steps, delivery_steps):
        return (self.lot_stock_id if reception_steps == 'one_step' else self.wh_input_stock_loc_id,
                self.lot_stock_id if delivery_steps == 'ship_only' else self.wh_output_stock_loc_id)

    def _get_transit_locations(self):
        return self.company_id.internal_transit_location_id, self.env.ref('stock.stock_location_inter_company', raise_if_not_found=False) or self.env['stock.location']

    @api.model
    def _get_partner_locations(self):
        ''' returns a tuple made of the browse record of customer location and the browse record of supplier location'''
        Location = self.env['stock.location']
        customer_loc = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
        supplier_loc = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        if not customer_loc:
            customer_loc = Location.search([('usage', '=', 'customer')], limit=1)
        if not supplier_loc:
            supplier_loc = Location.search([('usage', '=', 'supplier')], limit=1)
        if not customer_loc and not supplier_loc:
            raise UserError(_('Can\'t find any customer or supplier location.'))
        return customer_loc, supplier_loc

    def _get_route_name(self, route_type):
        return self.env._(ROUTE_NAMES[route_type])  # pylint: disable=gettext-variable

    def get_rules_dict(self):
        """ Define the rules source/destination locations, picking_type and
        action needed for each warehouse route configuration.
        """
        customer_loc, supplier_loc = self._get_partner_locations()
        return {
            warehouse.id: {
                'one_step': [self.Routing(supplier_loc, warehouse.lot_stock_id, warehouse.in_type_id, 'pull')],
                'two_steps': [
                    self.Routing(supplier_loc, warehouse.lot_stock_id, warehouse.in_type_id, 'pull'),
                    self.Routing(warehouse.wh_input_stock_loc_id, warehouse.lot_stock_id, warehouse.store_type_id, 'push')],
                'three_steps': [
                    self.Routing(supplier_loc, warehouse.lot_stock_id, warehouse.in_type_id, 'pull'),
                    self.Routing(warehouse.wh_input_stock_loc_id, warehouse.wh_qc_stock_loc_id, warehouse.qc_type_id, 'push'),
                    self.Routing(warehouse.wh_qc_stock_loc_id, warehouse.lot_stock_id, warehouse.store_type_id, 'push')],
                'ship_only': [self.Routing(warehouse.lot_stock_id, customer_loc, warehouse.out_type_id, 'pull')],
                'pick_ship': [
                    self.Routing(warehouse.lot_stock_id, customer_loc, warehouse.pick_type_id, 'pull'),
                    self.Routing(warehouse.wh_output_stock_loc_id, customer_loc, warehouse.out_type_id, 'push')],
                'pick_pack_ship': [
                    self.Routing(warehouse.lot_stock_id, customer_loc, warehouse.pick_type_id, 'pull'),
                    self.Routing(warehouse.wh_pack_stock_loc_id, warehouse.wh_output_stock_loc_id, warehouse.pack_type_id, 'push'),
                    self.Routing(warehouse.wh_output_stock_loc_id, customer_loc, warehouse.out_type_id, 'push')],
                'company_id': warehouse.company_id.id,
            } for warehouse in self
        }

    def _get_receive_rules_dict(self):
        """ Return receive route rules without initial pull rule in order to update warehouse routes.

        This function has the same receive route rules as get_rules_dict without an initial pull rule.
        This is expected to be used by modules that extend stock and add actions that can trigger receive
        'make_to_order' rules (i.e. we don't expect the receive route to be able to pull on its own anymore).
        This is also expected to be used in conjuction with _get_receive_routes_values()
        """
        return {
            'one_step': [],
            'two_steps': [self.Routing(self.wh_input_stock_loc_id, self.lot_stock_id, self.store_type_id, 'push')],
            'three_steps': [
                self.Routing(self.wh_input_stock_loc_id, self.wh_qc_stock_loc_id, self.qc_type_id, 'push'),
                self.Routing(self.wh_qc_stock_loc_id, self.lot_stock_id, self.store_type_id, 'push')],
        }

    def _get_inter_warehouse_route_values(self, supplier_warehouse):
        return {
            'name': _('%(warehouse)s: Supply Product from %(supplier)s', warehouse=self.name, supplier=supplier_warehouse.name),
            'warehouse_selectable': True,
            'product_selectable': True,
            'product_categ_selectable': True,
            'supplied_wh_id': self.id,
            'supplier_wh_id': supplier_warehouse.id,
            'company_id': (self.company_id & supplier_warehouse.company_id).id,
        }

    # Pull / Push tools
    # ------------------------------------------------------------

    def _get_rule_values(self, route_values, values=None, name_suffix=''):
        first_rule = True
        rules_list = []
        for routing in route_values:
            route_rule_values = {
                'name': self._format_rulename(routing.from_loc, routing.dest_loc, name_suffix),
                'location_src_id': routing.from_loc.id,
                'location_dest_id': routing.dest_loc.id,
                'action': routing.action,
                'auto': 'manual',
                'picking_type_id': routing.picking_type.id,
                'procure_method': first_rule and 'make_to_stock' or 'make_to_order',
                'warehouse_id': self.id,
                'company_id': self.company_id.id,
            }
            route_rule_values.update(values or {})
            rules_list.append(route_rule_values)
            first_rule = False
        if values and values.get('propagate_cancel') and rules_list:
            # In case of rules chain with cancel propagation set, we need to stop
            # the cancellation for the last step in order to avoid cancelling
            # any other move after the chain.
            # Example: In the following flow:
            # Input -> Quality check -> Stock -> Customer
            # We want that cancelling I->GC cancel QC -> S but not S -> C
            # which means:
            # Input -> Quality check should have propagate_cancel = True
            # Quality check -> Stock should have propagate_cancel = False
            rules_list[-1]['propagate_cancel'] = False
        return rules_list

    def _get_supply_pull_rules_values(self, route_values, values=None):
        pull_values = {}
        pull_values.update(values)
        pull_values['active'] = True
        rules_list = self._get_rule_values(route_values, values=pull_values)
        for pull_rules in rules_list:
            pull_rules['procure_method'] = self.lot_stock_id.id != pull_rules['location_src_id'] and 'make_to_order' or 'make_to_stock'  # first part of the resuply route is MTS
        return rules_list

    def _update_reception_delivery_resupply(self, reception_new, delivery_new):
        """ Check if we need to change something to resupply warehouses and associated MTO rules """
        for warehouse in self:
            dummy, output_loc = warehouse._get_input_output_locations(reception_new, delivery_new)
            if delivery_new and warehouse.delivery_steps != delivery_new and (warehouse.delivery_steps == 'ship_only' or delivery_new == 'ship_only'):
                change_to_multiple = warehouse.delivery_steps == 'ship_only'
                warehouse._check_delivery_resupply(output_loc, change_to_multiple)

    def _check_delivery_resupply(self, new_location, change_to_multiple):
        """ Check if the resupply routes from this warehouse follow the changes of number of delivery steps
        Check routes being delivery bu this warehouse and change the rule going to transit location """
        Rule = self.env["stock.rule"]
        routes = self.env['stock.route'].search([('supplier_wh_id', '=', self.id)])
        rules = Rule.search(['&', '&', ('route_id', 'in', routes.ids), ('action', '!=', 'push'), ('location_dest_id.usage', '=', 'transit')])
        rules.write({
            'location_src_id': new_location.id,
            'procure_method': change_to_multiple and "make_to_order" or "make_to_stock"})
        if not change_to_multiple:
            # Remove the extra rule to resupply Output from Stock
            rules_to_archive = Rule.search([('route_id', 'in', routes.ids), ('action', '!=', 'push'),
                                           ('location_dest_id', '=', self.wh_output_stock_loc_id.id),
                                           ('picking_type_id', '=', self.pick_type_id.id)])
            rules_to_archive.active = False

            # If single delivery we should create the necessary MTO rules for the resupply
            routings = [self.Routing(self.lot_stock_id, location, self.out_type_id, 'pull') for location in rules.location_dest_id]
            mto_vals = self._get_global_route_rules_values().get('mto_pull_id')
            values = mto_vals['create_values']
            mto_rule_vals = self._get_rule_values(routings, values, name_suffix='MTO')

            for mto_rule_val in mto_rule_vals:
                Rule.create(mto_rule_val)
        else:
            # Add the missing rules to resupply Output from Stock
            rules_to_unarchive = Rule.with_context(active_test=False).search([
                ('route_id', 'in', routes.ids), ('action', '!=', 'push'),
                ('location_dest_id', '=', self.wh_output_stock_loc_id.id),
                ('picking_type_id', '=', self.pick_type_id.id)])
            rules_to_unarchive.active = True
            found_routes = rules_to_unarchive.route_id

            missing_rule_vals = []
            for route in (routes - found_routes):
                missing_rule_vals += self._get_supply_pull_rules_values(
                    [self.Routing(self.lot_stock_id, new_location, self.pick_type_id, 'pull')],
                    values={'route_id': route.id})
            Rule.create(missing_rule_vals)

            # We need to delete all the MTO stock rules, otherwise they risk to be used in the system
            Rule.search([
                '&', ('route_id', '=', self._find_or_create_global_route('stock.route_warehouse0_mto', _('Replenish on Order (MTO)'), create=False).id),
                ('location_dest_id.usage', '=', 'transit'),
                ('action', '!=', 'push'),
                ('location_src_id', '=', self.lot_stock_id.id)]).write({'active': False})

    def _update_name_and_code(self, new_name=False, new_code=False):
        if new_code:
            self.mapped('lot_stock_id').mapped('location_id').write({'name': new_code})
        if new_name:
            # TDE FIXME: replacing the route name ? not better to re-generate the route naming ?
            for warehouse in self:
                routes = warehouse.route_ids
                for route in routes:
                    route.write({'name': route.name.replace(warehouse.name, new_name, 1)})
                    for pull in route.rule_ids:
                        pull.write({'name': pull.name.replace(warehouse.name, new_name, 1)})
                if warehouse.mto_pull_id:
                    warehouse.mto_pull_id.write({'name': warehouse.mto_pull_id.name.replace(warehouse.name, new_name, 1)})
        for warehouse in self:
            sequence_data = warehouse._get_sequence_values(name=new_name, code=new_code)
            # `ir.sequence` write access is limited to system user
            if self.env.user.has_group('stock.group_stock_manager'):
                warehouse = warehouse.sudo()
            warehouse.in_type_id.sequence_id.write(sequence_data['in_type_id'])
            warehouse.qc_type_id.sequence_id.write(sequence_data['qc_type_id'])
            warehouse.store_type_id.sequence_id.write(sequence_data['store_type_id'])
            warehouse.out_type_id.sequence_id.write(sequence_data['out_type_id'])
            warehouse.pack_type_id.sequence_id.write(sequence_data['pack_type_id'])
            warehouse.pick_type_id.sequence_id.write(sequence_data['pick_type_id'])
            warehouse.int_type_id.sequence_id.write(sequence_data['int_type_id'])
            warehouse.xdock_type_id.sequence_id.write(sequence_data['xdock_type_id'])

    def _update_location_reception(self, new_reception_step):
        self.mapped('wh_qc_stock_loc_id').write({'active': new_reception_step == 'three_steps'})
        self.mapped('wh_input_stock_loc_id').write({'active': new_reception_step != 'one_step'})

    def _update_location_delivery(self, new_delivery_step):
        self.mapped('wh_pack_stock_loc_id').write({'active': new_delivery_step == 'pick_pack_ship'})
        self.mapped('wh_output_stock_loc_id').write({'active': new_delivery_step != 'ship_only'})

    # Misc
    # ------------------------------------------------------------

    def _get_picking_type_update_values(self):
        """ Return values in order to update the existing picking type when the
        warehouse's delivery_steps or reception_steps are modify.
        """
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        return {
            'in_type_id': {
                'default_location_dest_id': input_loc.id,
                'barcode': self.code.replace(" ", "").upper() + "IN",
            },
            'out_type_id': {
                'default_location_src_id': output_loc.id,
                'barcode': self.code.replace(" ", "").upper() + "OUT",
            },
            'pick_type_id': {
                'active': self.delivery_steps != 'ship_only' and self.active,
                'default_location_dest_id': output_loc.id if self.delivery_steps == 'pick_ship' else self.wh_pack_stock_loc_id.id,
                'barcode': self.code.replace(" ", "").upper() + "PICK",
            },
            'pack_type_id': {
                'active': self.delivery_steps == 'pick_pack_ship' and self.active,
                'default_location_dest_id': output_loc.id,
                'barcode': self.code.replace(" ", "").upper() + "PACK",
            },
            'qc_type_id': {
                'active': self.reception_steps == 'three_steps' and self.active,
                'barcode': self.code.replace(" ", "").upper() + "QC",
            },
            'store_type_id': {
                'active': self.reception_steps != 'one_step' and self.active,
                'default_location_src_id': input_loc.id if self.reception_steps == 'two_steps' else self.wh_qc_stock_loc_id.id,
                'barcode': self.code.replace(" ", "").upper() + "STOR",
            },
            'int_type_id': {
                'barcode': self.code.replace(" ", "").upper() + "INT",
            },
            'xdock_type_id': {
                'active': self.reception_steps != 'one_step' and self.delivery_steps != 'ship_only' and self.active,
                'barcode': self.code.replace(" ", "").upper() + "XD",
            }
        }

    def _get_picking_type_create_values(self, max_sequence):
        """ When a warehouse is created this method return the values needed in
        order to create the new picking types for this warehouse. Every picking
        type are created at the same time than the warehouse howver they are
        activated or archived depending the delivery_steps or reception_steps.
        """
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        return {
            'in_type_id': {
                'name': _('Receipts'),
                'code': 'incoming',
                'use_existing_lots': False,
                'sequence': max_sequence + 1,
                'sequence_code': 'IN',
                'company_id': self.company_id.id,
            }, 'out_type_id': {
                'name': _('Delivery Orders'),
                'code': 'outgoing',
                'use_create_lots': False,
                'sequence': max_sequence + 7,
                'sequence_code': 'OUT',
                'print_label': True,
                'company_id': self.company_id.id,
            }, 'pack_type_id': {
                'name': _('Pack'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.wh_pack_stock_loc_id.id,
                'default_location_dest_id': output_loc.id,
                'sequence': max_sequence + 6,
                'sequence_code': 'PACK',
                'company_id': self.company_id.id,
            }, 'pick_type_id': {
                'name': _('Pick'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.lot_stock_id.id,
                'sequence': max_sequence + 5,
                'sequence_code': 'PICK',
                'company_id': self.company_id.id,
            }, 'qc_type_id': {
                'name': _('Quality Control'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.wh_input_stock_loc_id.id,
                'default_location_dest_id': self.wh_qc_stock_loc_id.id,
                'sequence': max_sequence + 2,
                'sequence_code': 'QC',
                'company_id': self.company_id.id,
            }, 'store_type_id': {
                'name': _('Storage'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_dest_id': self.lot_stock_id.id,
                'sequence': max_sequence + 3,
                'sequence_code': 'STOR',
                'company_id': self.company_id.id,
            }, 'int_type_id': {
                'name': _('Internal Transfers'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.lot_stock_id.id,
                'default_location_dest_id': self.lot_stock_id.id,
                'active': self.env.user.has_group('stock.group_stock_multi_locations'),
                'sequence': max_sequence + 4,
                'sequence_code': 'INT',
                'company_id': self.company_id.id,
            }, 'xdock_type_id': {
                'name': _('Cross Dock'),
                'code': 'internal',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_src_id': self.wh_input_stock_loc_id.id,
                'default_location_dest_id': self.wh_output_stock_loc_id.id,
                'sequence': max_sequence + 8,
                'sequence_code': 'XD',
                'company_id': self.company_id.id,
            }
        }, max_sequence + 9

    def _get_sequence_values(self, name=False, code=False):
        """ Each picking type is created with a sequence. This method returns
        the sequence values associated to each picking type.
        """
        name = name if name else self.name
        code = code if code else self.code
        return {
            'in_type_id': {
                'name': _('%(name)s Sequence in', name=name),
                'prefix': code + '/' + (self.in_type_id.sequence_code or 'IN') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'out_type_id': {
                'name': _('%(name)s Sequence out', name=name),
                'prefix': code + '/' + (self.out_type_id.sequence_code or 'OUT') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'pack_type_id': {
                'name': _('%(name)s Sequence packing', name=name),
                'prefix': code + '/' + (self.pack_type_id.sequence_code or 'PACK') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'pick_type_id': {
                'name': _('%(name)s Sequence picking', name=name),
                'prefix': code + '/' + (self.pick_type_id.sequence_code or 'PICK') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'qc_type_id': {
                'name': _('%(name)s Sequence quality control', name=name),
                'prefix': code + '/' + (self.qc_type_id.sequence_code or 'QC') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'store_type_id': {
                'name': _('%(name)s Sequence storage', name=name),
                'prefix': code + '/' + (self.store_type_id.sequence_code or 'STOR') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'int_type_id': {
                'name': _('%(name)s Sequence internal', name=name),
                'prefix': code + '/' + (self.int_type_id.sequence_code or 'INT') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
            'xdock_type_id': {
                'name': _('%(name)s Sequence cross dock', name=name),
                'prefix': code + '/' + (self.xdock_type_id.sequence_code or 'XD') + '/', 'padding': 5,
                'company_id': self.company_id.id,
            },
        }

    def _format_rulename(self, from_loc, dest_loc, suffix):
        rulename = '%s: %s' % (self.code, from_loc.name)
        if dest_loc:
            rulename += ' → %s' % (dest_loc.name)
        if suffix:
            rulename += ' (' + suffix + ')'
        return rulename

    def _format_routename(self, name=None, route_type=None):
        if route_type:
            name = self._get_route_name(route_type)
        return '%s: %s' % (self.name, name)

    def _get_all_routes(self):
        routes = self.mapped('route_ids') | self.mapped('mto_pull_id').mapped('route_id')
        routes |= self.env["stock.route"].with_context(active_test=False).search([('supplied_wh_id', 'in', self.ids)])
        return routes

    def action_view_all_routes(self):
        routes = self._get_all_routes()
        return {
            'name': _('Warehouse\'s Routes'),
            'domain': [('id', 'in', routes.ids)],
            'res_model': 'stock.route',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'limit': 20,
            'context': dict(self.env.context, default_warehouse_selectable=True, default_warehouse_ids=self.ids)
        }

    def get_current_warehouses(self):
        return self.env['stock.warehouse'].search_read(fields=['id', 'name', 'code'])
