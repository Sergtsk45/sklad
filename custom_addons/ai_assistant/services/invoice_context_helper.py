# @file: invoice_context_helper.py
# @description: Сопоставление счёта с Odoo, инъекция INVOICE_CONTEXT (AIA-057).
# @dependencies: invoice_extraction_store, action_tools.read_tools
# @created: 2026-05-30

import json

from odoo.addons.ai_assistant.services.action_tools.validators import (
    infer_is_company,
    normalize_vat,
)
from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindPartnerTool,
    SearchProductsTool,
)
from odoo.addons.ai_assistant.services.invoice_parsing.address_utils import (
    parse_supplier_address,
)


class InvoiceContextHelper:
    """Сопоставляет счёт с partner/product и формирует system-блок для LLM."""

    _CONTEXT_HEADER = 'INVOICE_CONTEXT (используй для плана PO):'

    def __init__(self, env, invoice_store):
        self.env = env
        self._store = invoice_store
        self._find_partner = FindPartnerTool()
        self._search_products = SearchProductsTool()

    def fetch_context(self, uid, extraction_token):
        """Загрузить счёт из store и собрать контекст сопоставления."""
        if not extraction_token:
            return None
        invoice_data = self._store.get(uid, extraction_token)
        if not invoice_data:
            return None
        return self._build_context(invoice_data)

    def _build_context(self, invoice_data):
        supplier = invoice_data.get('supplier') or {}
        partner = self._match_supplier(supplier)
        partner_id = (
            partner.get('partner_id')
            if partner.get('status') == 'matched'
            else None
        )
        return {
            'invoice_number': invoice_data.get('invoice_number'),
            'invoice_date': invoice_data.get('invoice_date'),
            'supplier_extracted': {
                'name': supplier.get('name'),
                'inn': supplier.get('inn'),
                'kpp': supplier.get('kpp'),
                'address': supplier.get('address'),
            },
            'partner': partner,
            'items': [
                self._match_item(item, partner_id=partner_id)
                for item in (invoice_data.get('items') or [])
            ],
            'totals': invoice_data.get('totals') or {},
            'warehouse_required': True,
        }

    def _match_supplier(self, supplier):
        inn = (supplier.get('inn') or '').strip()
        if inn:
            result = self._match_partners_by_query(inn)
            if result:
                return result

        name = (supplier.get('name') or '').strip()
        if name:
            result = self._match_partners_by_query(name)
            if result:
                return result

        return {
            'status': 'not_found',
            'extracted_name': supplier.get('name'),
            'extracted_inn': inn or None,
            'needs_create_partner_draft': bool(inn),
            'partner_error': None if inn else 'inn_required',
            'partner_draft_args': (
                self.build_partner_draft_args({'supplier': supplier})
                if inn else {}
            ),
        }

    def build_partner_draft_args(self, invoice_data):
        supplier = (invoice_data or {}).get('supplier') or {}
        name = (supplier.get('name') or '').strip()
        vat = normalize_vat(supplier.get('inn'))
        args = {
            'name': name,
            'vat': vat,
            'category': 'Поставщик',
            'is_company': infer_is_company(name),
        }
        address = (supplier.get('address') or '').strip()
        if address:
            args.update(parse_supplier_address(address))
        kpp = (supplier.get('kpp') or '').strip()
        if kpp:
            args['comment'] = 'КПП: %s' % kpp
        return args

    def _match_partners_by_query(self, query):
        partners = self._find_partner.execute(
            self.env,
            {'query': query, 'is_supplier': True},
        ).get('partners') or []
        if len(partners) == 1:
            partner = partners[0]
            return {
                'status': 'matched',
                'partner_id': partner['id'],
                'name': partner.get('display_name') or partner.get('name'),
                'vat': partner.get('vat'),
            }
        if len(partners) > 1:
            return {
                'status': 'ambiguous',
                'candidates': [
                    {
                        'partner_id': partner['id'],
                        'name': (
                            partner.get('display_name') or partner.get('name')
                        ),
                        'vat': partner.get('vat'),
                    }
                    for partner in partners
                ],
            }
        return None

    def _match_item(self, item, partner_id=None):
        name = (item.get('name') or '').strip()
        article = (item.get('article') or '').strip()
        line = {
            'line_no': item.get('line_no'),
            'name': name,
            'unit': item.get('unit'),
            'qty': item.get('qty'),
            'price': item.get('price'),
            'amount_w_vat': item.get('amount_w_vat'),
            'article': article,
        }
        if len(name) < 2 and not article:
            line['product'] = {
                'status': 'not_found',
                'candidates': [],
                'needs_create_product_draft': True,
            }
            return line

        by_article = self._match_product_by_article(
            article,
            partner_id=partner_id,
        )
        if by_article:
            candidate = self._format_product_record(by_article)
            line['product'] = {
                'status': 'matched',
                'product_id': by_article.id,
                'display_name': by_article.display_name,
                'match_by': 'article',
                'candidates': [candidate],
                'needs_create_product_draft': False,
            }
            return line

        if len(name) < 2:
            line['product'] = {
                'status': 'not_found',
                'candidates': [],
                'needs_create_product_draft': True,
            }
            return line

        products = self._search_products.execute(
            self.env,
            {'query': name, 'limit': 5},
        ).get('products') or []
        candidates = [
            self._format_product_candidate(product)
            for product in products
        ]

        if len(products) == 1:
            product = products[0]
            line['product'] = {
                'status': 'matched',
                'product_id': product['id'],
                'display_name': product.get('display_name'),
                'match_by': 'name',
                'candidates': candidates,
                'needs_create_product_draft': False,
            }
        elif len(products) > 1:
            line['product'] = {
                'status': 'candidates',
                'candidates': candidates,
                'needs_create_product_draft': False,
            }
        else:
            line['product'] = {
                'status': 'not_found',
                'candidates': [],
                'needs_create_product_draft': True,
            }
        return line

    def _match_product_by_article(self, article, partner_id=None):
        """Найти product.product по артикулу поставщика или default_code."""
        code = (article or '').strip()
        if not code:
            return self.env['product.product'].browse()

        SupplierInfo = self.env['product.supplierinfo']
        domains = []
        if partner_id:
            domains.append([
                ('product_code', '=ilike', code),
                ('partner_id', '=', partner_id),
            ])
        domains.append([('product_code', '=ilike', code)])

        for domain in domains:
            infos = SupplierInfo.search(domain, limit=5)
            if not infos:
                continue
            products = self.env['product.product']
            for info in infos:
                product = info.product_id
                if not product and info.product_tmpl_id:
                    product = info.product_tmpl_id.product_variant_id
                if product:
                    products |= product
            products = products.filtered('active')
            if len(products) == 1:
                return products
            if len(products) > 1:
                # Несколько разных карточек с одним кодом — не матчим.
                return self.env['product.product'].browse()
            # infos найдены, но без product — пробуем следующий domain

        product = self.env['product.product'].search(
            [('default_code', '=ilike', code), ('active', '=', True)],
            limit=1,
        )
        return product

    def _format_product_record(self, product):
        return {
            'product_id': product.id,
            'display_name': product.display_name,
            'default_code': product.default_code or False,
            'uom_id': product.uom_id.id if product.uom_id else False,
            'list_price': product.list_price,
        }

    def _format_product_candidate(self, product):
        return {
            'product_id': product['id'],
            'display_name': product.get('display_name'),
            'default_code': product.get('default_code'),
            'uom_id': product.get('uom_id'),
            'list_price': product.get('list_price'),
        }

    def build_context_message(self, invoice_context):
        if not invoice_context:
            return None
        payload = json.dumps(invoice_context, ensure_ascii=False, default=str)
        return (
            '%s\n%s\n'
            'Правила: сначала поставщик, потом товары, потом PO; '
            'если partner.needs_create_partner_draft=true — предложи '
            'create_partner_draft и не создавай PO; '
            'не подставляй склад/объект по умолчанию (D3) — '
            'уточни у пользователя склад приёмки (код или название, '
            'find_warehouse) перед PO; '
            'позиции с needs_create_product_draft=true — create_product_draft '
            'по одной строке с list_price из счёта; далее кнопки workflow '
            '(следующий товар / закупка на склад).'
        ) % (self._CONTEXT_HEADER, payload)
