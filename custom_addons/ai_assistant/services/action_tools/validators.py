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
PARTNER_CATEGORIES = {
    'Поставщик': {'supplier_rank': 1},
    'Заказчик': {'customer_rank': 1},
    'Покупатель': {'customer_rank': 1},
    'Подрядчик': {'supplier_rank': 1},
}

# OpenAI/Gemini-compatible JSON Schema (без union type string|array).
PARTNER_CATEGORY_SCHEMA = {
    'type': 'string',
    'enum': list(PARTNER_CATEGORIES),
}


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


def validate_partner_category(value):
    category = (value or '').strip()
    if category not in PARTNER_CATEGORIES:
        raise ValidationError(
            'Категория контрагента должна быть одной из: %s.'
            % ', '.join(PARTNER_CATEGORIES)
        )
    return category


def normalize_partner_categories(value):
    if isinstance(value, list):
        categories = value
    else:
        categories = [value]
    normalized = []
    for category in categories:
        valid_category = validate_partner_category(category)
        if valid_category not in normalized:
            normalized.append(valid_category)
    if not normalized:
        raise ValidationError('Укажите категорию контрагента.')
    return normalized


def get_or_create_partner_tag(env, category):
    category = validate_partner_category(category)
    tag = env['res.partner.category'].search(
        [('name', '=', category)],
        limit=1,
    )
    if tag:
        return tag
    return env['res.partner.category'].create({'name': category})


def validate_bic(value):
    bic = ''.join(re.findall(r'\d', value or ''))
    if len(bic) != 9:
        raise ValidationError('БИК должен содержать 9 цифр.')
    return bic


def validate_acc_number(value):
    acc_number = ''.join(re.findall(r'\d', value or ''))
    if len(acc_number) != 20:
        raise ValidationError('Расчётный счёт должен содержать 20 цифр.')
    return acc_number


def normalize_phone(value):
    phone = (value or '').strip()
    digits = ''.join(re.findall(r'\d', phone))
    if len(digits) == 11 and digits.startswith('8'):
        return '+7 (%s) %s-%s-%s' % (
            digits[1:4],
            digits[4:7],
            digits[7:9],
            digits[9:11],
        )
    return phone


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
        errors.append('Укажите название контрагента.')
    if len(vat) not in (10, 12):
        errors.append('Укажите ИНН контрагента: 10 или 12 цифр.')
    email = (args.get('email') or '').strip()
    if email and '@' not in email:
        errors.append('Некорректный email контрагента.')
    try:
        normalize_partner_categories(args.get('category') or [])
    except ValidationError as err:
        errors.append(str(err))
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
        'Пересчитайте количество в метры перед подтверждением закупки.'
        % (product.display_name, product.uom_id.display_name)
    )
