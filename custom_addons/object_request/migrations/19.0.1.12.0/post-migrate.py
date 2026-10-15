import logging

from odoo import SUPERUSER_ID, api
from odoo.addons.object_request.models.fastener_mass import gost_table_mass_kg


_logger = logging.getLogger(__name__)

# TD-016: табличная масса 1 шт. по ГОСТ 7798-70 / ГОСТ 5915-70.
KG_PER_PIECE = {
    1298: ("Болт М16", gost_table_mass_kg("bolt", 16, 55)),
    1299: ("Гайка М16", gost_table_mass_kg("nut", 16)),
}
# Строки, перенесённые на кг-карточку 1299 с количеством в шт.
PIECE_LINES = (929, 362)


def _set_kg_per_piece(env):
    kg = env.ref("uom.product_uom_kgm")
    updated = env["product.template"]
    for template_id, (name_part, factor) in KG_PER_PIECE.items():
        template = env["product.template"].with_context(
            active_test=False
        ).browse(template_id).exists()
        if (
            not template
            or name_part.lower() not in (template.name or "").lower()
            or template.uom_id != kg
            or template.kg_per_piece
        ):
            _logger.warning(
                "object_request 1.12.0: skip kg_per_piece for template %s",
                template_id,
            )
            continue
        template.kg_per_piece = factor
        updated |= template
    return updated


def _convert_piece_line(env, line):
    product = line.product_id
    if (
        not product.kg_per_piece
        or line.qty_requested_pcs
        or line.stock_ids._issue_moves()
        or line.purchase_order_line_id
        or line.qty_issued
    ):
        _logger.warning(
            "object_request 1.12.0: line %s not converted (no factor, "
            "already in pcs or has issue/purchase)",
            line.id,
        )
        return False
    pieces = line.qty_requested
    line.stock_ids.with_context(
        auto_stock_distribution=True,
        skip_qty_to_issue_limit=True,
        skip_stock_total_sync=True,
    ).write({"qty_to_issue": 0.0, "qty_planned_to_issue": 0.0})
    line.with_context(or_skip_qty_lock=True).write(
        {
            "qty_to_issue": 0.0,
            "qty_to_buy": 0.0,
            "procurement_mode": "manual",
            "manual_plan_override": False,
            "qty_requested_pcs": pieces,
        }
    )
    _logger.info(
        "object_request 1.12.0: line %s: %s pcs -> %s %s",
        line.id,
        pieces,
        line.qty_requested,
        line.uom_id.name,
    )
    return True


def migrate(cr, version):
    """TD-016: масса 1 шт. метизов, карточки ГОСТ, пересчёт шт. → кг."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    templates = _set_kg_per_piece(env)
    created = env["product.template"]._create_gost_fastener_templates()
    _logger.info(
        "object_request 1.12.0: created %s GOST fastener templates",
        len(created),
    )
    lines = env["object.request.line"].browse(PIECE_LINES).exists()
    converted = lines.filtered(lambda line: _convert_piece_line(env, line))
    _logger.info(
        "object_request 1.12.0: kg_per_piece on %s templates, "
        "converted lines %s",
        len(templates),
        converted.ids,
    )
