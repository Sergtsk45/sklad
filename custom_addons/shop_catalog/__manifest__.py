{
    'name': 'Shop Catalog',
    'version': '19.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Каталог интернет-магазина по образцу santech.ru: дерево '
               'категорий, раскладка товаров, вид списком',
    'description': """
Дерево публичных категорий магазина (раздел → подраздел → группа) по образцу
каталога santech.ru, правила раскладки товаров по названию, вид «список» и
категории в левой колонке по умолчанию.
    """,
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'website_sale_stock'],
    'data': [
        'data/website_layout.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
}
