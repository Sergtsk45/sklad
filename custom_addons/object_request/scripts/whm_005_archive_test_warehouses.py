# flake8: noqa
import json
from datetime import datetime

from odoo.exceptions import UserError


TEST_WAREHOUSE_CODES = ("ОбМ-1", "ОбМ-3", "ОбМ-5")
ARCHIVED_DUPLICATE_CODES = ("X001", "X002", "X003", "X004")


def _name(record):
    return record.display_name if record else False


def _warehouse_stats(env, warehouse):
    Quant = env["stock.quant"].sudo()
    Picking = env["stock.picking"].sudo()
    PickingType = env["stock.picking.type"].sudo()
    PurchaseOrder = env["purchase.order"].sudo()
    quant_domain = []
    if warehouse.view_location_id:
        quant_domain = [
            ("location_id", "child_of", warehouse.view_location_id.id),
            ("quantity", "!=", 0),
        ]
    picking_type_ids = PickingType.search(
        [("warehouse_id", "=", warehouse.id)]
    ).ids
    return {
        "id": warehouse.id,
        "code": warehouse.code,
        "name": warehouse.name,
        "active": warehouse.active,
        "view_location_id": warehouse.view_location_id.id,
        "lot_stock_id": warehouse.lot_stock_id.id,
        "in_type_id": warehouse.in_type_id.id,
        "int_type_id": warehouse.int_type_id.id,
        "quant_count": Quant.search_count(quant_domain) if quant_domain else 0,
        "quant_total": sum(Quant.search(quant_domain).mapped("quantity"))
        if quant_domain
        else 0.0,
        "picking_type_ids": picking_type_ids,
        "picking_count": Picking.search_count(
            [("picking_type_id", "in", picking_type_ids)]
        )
        if picking_type_ids
        else 0,
        "purchase_order_count": PurchaseOrder.search_count(
            [("picking_type_id", "in", picking_type_ids)]
        )
        if picking_type_ids
        else 0,
    }


def _project_snapshot(env):
    Project = env["object.request.project"].sudo().with_context(
        active_test=False
    )
    return [
        {
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "active": project.active,
            "warehouse_id": project.warehouse_id.id,
            "request_count": len(project.request_ids),
        }
        for project in Project.search([])
    ]


def _warehouse_snapshot(env):
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    warehouses = Warehouse.search(
        [
            "|",
            ("code", "in", TEST_WAREHOUSE_CODES),
            ("code", "in", ARCHIVED_DUPLICATE_CODES),
        ]
    )
    return [_warehouse_stats(env, warehouse) for warehouse in warehouses]


def _quant_details(env, warehouse):
    Quant = env["stock.quant"].sudo()
    rows = []
    if not warehouse.view_location_id:
        return rows
    quants = Quant.search(
        [
            ("location_id", "child_of", warehouse.view_location_id.id),
            ("quantity", "!=", 0),
        ]
    )
    for quant in quants:
        rows.append(
            {
                "warehouse_id": warehouse.id,
                "warehouse_code": warehouse.code,
                "location_id": quant.location_id.id,
                "location": _name(quant.location_id),
                "product_id": quant.product_id.id,
                "product": _name(quant.product_id),
                "quantity": quant.quantity,
                "reserved_quantity": quant.reserved_quantity,
            }
        )
    return rows


def _audit(env):
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    details = []
    for warehouse in Warehouse.search([("code", "in", TEST_WAREHOUSE_CODES)]):
        details.extend(_quant_details(env, warehouse))
    return {
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "database": env.cr.dbname,
        "warehouses": _warehouse_snapshot(env),
        "test_warehouse_quant_details": details,
        "projects": _project_snapshot(env),
    }


def run(env):
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    before = _audit(env)
    actions = []
    for warehouse in Warehouse.search([("code", "in", TEST_WAREHOUSE_CODES)]):
        if not warehouse.active:
            actions.append(
                {
                    "action": "skip_already_archived",
                    "warehouse_id": warehouse.id,
                    "code": warehouse.code,
                }
            )
            continue
        stats = _warehouse_stats(env, warehouse)
        try:
            warehouse.write({"active": False})
        except UserError as error:
            env.cr.rollback()
            actions.append(
                {
                    "action": "blocked_archive_warehouse",
                    "warehouse_id": warehouse.id,
                    "code": warehouse.code,
                    "reason": str(error),
                    "quant_count_preserved": stats["quant_count"],
                    "quant_total_preserved": stats["quant_total"],
                    "picking_count_preserved": stats["picking_count"],
                    "purchase_order_count_preserved": stats[
                        "purchase_order_count"
                    ],
                }
            )
            continue
        actions.append(
            {
                "action": "archive_warehouse",
                "warehouse_id": warehouse.id,
                "code": warehouse.code,
                "quant_count_preserved": stats["quant_count"],
                "quant_total_preserved": stats["quant_total"],
                "picking_count_preserved": stats["picking_count"],
                "purchase_order_count_preserved": stats[
                    "purchase_order_count"
                ],
            }
        )
    env.cr.commit()
    after = _audit(env)
    validations = []
    for code in TEST_WAREHOUSE_CODES:
        warehouse = Warehouse.search([("code", "=", code)], limit=1)
        validations.append(
            {
                "code": code,
                "warehouse_id": warehouse.id,
                "active": warehouse.active,
                "ok": bool(warehouse) and not warehouse.active,
            }
        )
    return {
        "before": before,
        "actions": actions,
        "validations": validations,
        "after": after,
    }


print(json.dumps(run(env), ensure_ascii=False, indent=2, default=str))
