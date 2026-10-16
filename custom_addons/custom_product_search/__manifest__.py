{
    'name': 'Custom Product Search',
    'version': '19.0.2.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Improved normalized product search for Odoo products',
    'description': """
Normalized product search for Odoo 19.

Product search v2: search tokens with editable synonyms, ranked
autocomplete, token filter in product lists and a safe service method for
AI-assisted product search.
    """,
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_search_synonym_views.xml',
        'views/product_search_views.xml',
        'data/product_search_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
