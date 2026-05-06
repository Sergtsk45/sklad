{
    'name': 'Custom Product Search',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Improved normalized product search for Odoo products',
    'description': """
Normalized product search for Odoo 19.

Adds stored normalized search fields on products and product templates,
extends backend product lookup, and provides a safe service method for
AI-assisted product search.
    """,
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'stock',
    ],
    'data': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
