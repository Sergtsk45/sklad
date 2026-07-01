{
    "name": "Object Request — Требование на комплектацию объекта",
    "version": "19.0.1.7.4",
    "category": "Inventory/Inventory",
    "summary": "Управление требованиями на комплектацию строительных объектов",
    "description": """
Модуль для управления требованиями на комплектацию объектов строительства.

Основные функции:
- Создание требований на комплектацию по объектам
- Импорт потребностей из Excel
- Ручное сопоставление строк с номенклатурой
- Создание складских документов выдачи
- Формирование черновиков закупок
- Печатные формы требования и расходной накладной
    """,
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "product",
        "stock",
        "purchase",
        "purchase_stock",
        "contacts",
        "custom_product_search",
    ],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "data/ir_sequence_data.xml",
        "security/object_request_security.xml",
        "security/ir.model.access.csv",
        "security/object_request_rules.xml",
        "reports/object_request_report.xml",
        "reports/issue_picking_report.xml",
        "reports/purchase_order_report.xml",
        "reports/purchase_compact_report_templates.xml",
        "wizards/import_excel_wizard_views.xml",
        "wizards/assign_lines_wizard_views.xml",
        "wizards/issue_wizard_views.xml",
        "wizards/issue_preview_wizard_views.xml",
        "wizards/auto_split_confirm_wizard_views.xml",
        "wizards/confirm_state_wizard_views.xml",
        "wizards/purchase_wizard_views.xml",
        "wizards/remember_matching_wizard_views.xml",
        "views/stock_picking_inherit_views.xml",
        "views/purchase_order_inherit_views.xml",
        "views/object_request_project_views.xml",
        "views/object_request_line_views.xml",
        "wizards/stock_check_wizard_views.xml",
        "views/object_request_views.xml",
        "views/object_request_analytics_views.xml",
        "views/object_request_menu.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "object_request/static/src/scss/object_request.scss",
            (
                "object_request/static/src/components/"
                "purchase_file_uploader/purchase_file_uploader.xml"
            ),
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
