import re

from odoo.exceptions import ValidationError


OBJECT_WAREHOUSE_PREFIX = 'ОбМ-'
LEGACY_OBJECT_WAREHOUSE_ALIASES = {
    'обм-2': 'O001',
    'обм-4': 'O002',
}
METER_UOM_NAMES = {'m', 'meter', 'meters', 'метр', 'метры', 'м'}
COMPANY_PREFIXES = (
    'ООО',
    'АО',
    'ЗАО',
    'ПАО',
    'ОАО',
    'МУП',
    'ГУП',
)


def validate_picking_type_for_purchase(env, picking_type_id):
    """Проверить incoming picking type для черновика закупки (любой склад)."""
    picking_type = env['stock.picking.type'].browse(picking_type_id)
    if not picking_type.exists():
        raise ValidationError('Тип операции склада не найден.')
    if not picking_type.warehouse_id:
        raise ValidationError('У типа операции не указан склад.')


def validate_picking_type_is_object(env, picking_type_id):
    picking_type = env['stock.picking.type'].browse(picking_type_id)
    if not picking_type.exists():
        raise ValidationError('Тип операции склада не найден.')
    warehouse = picking_type.warehouse_id
    if not warehouse:
        raise ValidationError('У типа операции не указан склад.')
    validate_warehouse_code_pattern(env, warehouse.id)


def validate_product_is_storable(env, product_id):
    product = env['product.product'].browse(product_id)
    if not product.exists():
        raise ValidationError('Товар не найден.')
    if not product.is_storable:
        raise ValidationError(
            'Товар должен быть складируемым: включите признак "На складе".'
        )


def validate_state_in(record, allowed_states):
    if not record:
        raise ValidationError('Запись не найдена.')
    current_state = getattr(record, 'state', None)
    if current_state not in allowed_states:
        allowed = ', '.join(sorted(allowed_states))
        raise ValidationError(
            'Недопустимый статус записи: %s. Разрешены: %s.'
            % (current_state or 'не задан', allowed)
        )


def validate_warehouse_code_pattern(env, warehouse_id):
    warehouse = env['stock.warehouse'].browse(warehouse_id)
    if not warehouse.exists():
        raise ValidationError('Склад не найден.')
    project = env['object.request.project'].with_context(
        active_test=False
    ).search([('warehouse_id', '=', warehouse.id)], limit=1)
    if not project:
        raise ValidationError(
            'Склад должен быть связан с объектом комплектации; '
            'текущий код: %s.'
            % (warehouse.code or 'не задан')
        )


def validate_partner_is_supplier(env, partner_id):
    partner = env['res.partner'].browse(partner_id)
    if not partner.exists():
        raise ValidationError('Поставщик не найден.')
    if partner.supplier_rank <= 0:
        raise ValidationError(
            'Контрагент должен быть поставщиком (supplier_rank > 0).'
        )


def normalize_vat(inn):
    """Return only digits from Russian INN input."""
    return ''.join(re.findall(r'\d', inn or ''))


def validate_vat_unique(env, vat):
    """Return existing partner id for VAT duplicate, or None."""
    normalized = normalize_vat(vat)
    if not normalized:
        return None
    partner = env['res.partner'].search([('vat', '=', normalized)], limit=1)
    return partner.id if partner else None


def infer_is_company(name):
    """Infer res.partner.is_company from common Russian legal prefixes."""
    text = (name or '').strip().upper()
    if not text:
        return False
    if re.match(r'^ИП(?:\s|$|[.,])', text):
        return False
    return any(
        re.match(r'^%s(?:\s|$|[.,"])' % re.escape(prefix), text)
        for prefix in COMPANY_PREFIXES
    )


def validate_partner_create_args(args):
    """Validate create_partner_draft args and return a list of errors."""
    errors = []
    name = (args.get('name') or '').strip()
    vat = normalize_vat(args.get('vat'))
    if not name:
        errors.append('Укажите название поставщика.')
    if len(vat) not in (10, 12):
        errors.append('Укажите ИНН поставщика: 10 или 12 цифр.')
    email = (args.get('email') or '').strip()
    if email and '@' not in email:
        errors.append('Некорректный email поставщика.')
    return errors


def validate_uom_is_meter(env, product_id):
    product = env['product.product'].browse(product_id)
    if not product.exists():
        raise ValidationError('Товар не найден.')

    category_name = (product.categ_id.complete_name or '').lower()
    if 'труб' not in category_name:
        return ''

    uom_name = (product.uom_id.name or '').strip().lower()
    if uom_name in METER_UOM_NAMES:
        return ''

    return (
        'Для труб ожидается единица измерения "метр"; '
        'у товара "%s" сейчас "%s". '
        'До закрытия TD-002 пересчет должен подтвердить пользователь.'
        % (product.display_name, product.uom_id.display_name)
    )
