{
    'name': 'AI Assistant',
    'version': '19.0.1.0.0',
    'summary': 'Floating AI chat assistant for Odoo users',
    'description': """
        AI-консультант для Odoo 19.
        Плавающий чат-виджет с контекстно-зависимыми ответами
        на основе OpenRouter API.
    """,
    'category': 'Tools',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'base_setup',
        'mail',
        'stock',
        'purchase',
        'object_request',
        'custom_product_search',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/ai_assistant_assets.xml',
        'views/ai_assistant_settings_views.xml',
        'views/ai_assistant_audit_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_assistant/static/lib/html2canvas.min.js',
            'ai_assistant/static/src/scss/ai_chat_widget.scss',
            'ai_assistant/static/src/xml/ai_chat_widget.xml',
            'ai_assistant/static/src/js/screenshot_trigger.js',
            'ai_assistant/static/src/js/ai_chat_service.js',
            'ai_assistant/static/src/js/ai_chat_actions.js',
            'ai_assistant/static/src/js/ai_chat_boot.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
