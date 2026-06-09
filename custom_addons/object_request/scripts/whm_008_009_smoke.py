import json
import traceback

from odoo import fields

from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindWarehouseTool,
)
from odoo.addons.ai_assistant.services.action_tools.validators import (
    validate_warehouse_code_pattern,
)


TARGET_CODES = ("O001", "O002")
LEGACY_QUERIES = {
    "ОбМ-2": "O001",
    "ОбМ-4": "O002",
}


def _jsonify(record):
    if not record:
        return False
    return {"id": record.id, "name": record.display_name}


def _target_projects(env):
    Project = (
        env["object.request.project"].sudo().with_context(active_test=False)
    )
    projects = Project.search([("code", "in", TARGET_CODES)])
    by_code = {project.code: project for project in projects}
    missing = [code for code in TARGET_CODES if code not in by_code]
    if missing:
        raise RuntimeError("Missing projects: %s" % ", ".join(missing))
    return by_code


def _warehouse_summary(env, project):
    warehouse = project.warehouse_id.with_context(active_test=False)
    Quant = env["stock.quant"].sudo()
    quants = Quant.search(
        [("location_id", "child_of", warehouse.view_location_id.id)]
    )
    qty_total = sum(quants.mapped("quantity"))
    return {
        "project_id": project.id,
        "project_name": project.name,
        "warehouse_id": warehouse.id,
        "warehouse_code": warehouse.code,
        "warehouse_name": warehouse.name,
        "warehouse_active": warehouse.active,
        "lot_stock_id": warehouse.lot_stock_id.id,
        "in_type_id": warehouse.in_type_id.id,
        "int_type_id": warehouse.int_type_id.id,
        "quant_rows": len(quants),
        "quantity_total": qty_total,
    }


def _ai_checks(env):
    tool = FindWarehouseTool()
    checks = {}
    queries = (
        "O001",
        "O002",
        "O",
        "Ломоносова",
        "Хмельницкого",
        *LEGACY_QUERIES,
    )
    for query in queries:
        warehouses = tool.execute(env, {"query": query})["warehouses"]
        checks[query] = [
            {
                "id": item["id"],
                "code": item["code"],
                "name": item["name"],
            }
            for item in warehouses
        ]
    for legacy_query, expected_code in LEGACY_QUERIES.items():
        actual_codes = [item["code"] for item in checks[legacy_query]]
        if expected_code not in actual_codes:
            raise RuntimeError(
                "%s did not resolve to %s: %s"
                % (legacy_query, expected_code, actual_codes)
            )
    projects = _target_projects(env)
    validators = {}
    for code, project in projects.items():
        validators[code] = validate_warehouse_code_pattern(
            env, project.warehouse_id.id
        )
    return {"find_warehouse": checks, "validators": validators}


def _find_smoke_product(env):
    Product = env["product.product"].sudo()
    product = Product.search(
        [
            ("type", "in", ["consu", "product"]),
            ("purchase_ok", "=", True),
            ("active", "=", True),
        ],
        limit=1,
    )
    if not product:
        product = Product.search(
            [("type", "in", ["consu", "product"]), ("active", "=", True)],
            limit=1,
        )
    if not product:
        raise RuntimeError("No active stock/consumable product found")
    return product


def _find_supplier(env):
    Partner = env["res.partner"].sudo()
    supplier = Partner.search([("supplier_rank", ">", 0)], limit=1)
    if not supplier:
        supplier = Partner.search([("is_company", "=", True)], limit=1)
    if not supplier:
        raise RuntimeError("No supplier/company partner found")
    return supplier


def _stock_move_vals(env, picking, product, qty, source, destination):
    Move = env["stock.move"]
    vals = {
        "product_id": product.id,
        "product_uom_qty": qty,
        "picking_id": picking.id,
        "location_id": source.id,
        "location_dest_id": destination.id,
    }
    if "description_picking" in Move._fields:
        vals["description_picking"] = product.display_name
    if "product_uom" in Move._fields:
        vals["product_uom"] = product.uom_id.id
    elif "product_uom_id" in Move._fields:
        vals["product_uom_id"] = product.uom_id.id
    return vals


def _draft_document_checks(env, projects):
    product = _find_smoke_product(env)
    supplier = _find_supplier(env)
    today = fields.Date.context_today(env["object.request"])
    PurchaseOrderLine = env["purchase.order.line"].sudo()
    PurchaseOrder = env["purchase.order"].sudo()
    Picking = env["stock.picking"].sudo()
    Move = env["stock.move"].sudo()
    Request = env["object.request"].sudo()

    checks = {}
    for code, project in projects.items():
        warehouse = project.warehouse_id
        request = Request.create(
            {
                "project_id": project.id,
                "foreman_user_id": env.user.id,
                "need_date": today,
                "comment": "WHM-008/009 rollback smoke",
            }
        )
        po_vals = {
            "partner_id": supplier.id,
            "origin": request.name,
            "is_object_request_purchase": True,
            "object_request_project_id": project.id,
        }
        if warehouse.in_type_id:
            po_vals["picking_type_id"] = warehouse.in_type_id.id
        po = PurchaseOrder.create(po_vals)
        line_vals = {
            "order_id": po.id,
            "product_id": product.id,
            "product_qty": 1.0,
            "name": product.display_name,
            "price_unit": 0.0,
            "date_planned": fields.Datetime.now(),
        }
        if "product_uom_id" in PurchaseOrderLine._fields:
            line_vals["product_uom_id"] = product.uom_id.id
        else:
            line_vals["product_uom"] = product.uom_id.id
        PurchaseOrderLine.create(line_vals)
        request.write({"purchase_order_ids": [(4, po.id)]})

        picking = Picking.create(
            {
                "picking_type_id": warehouse.int_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": warehouse.lot_stock_id.id,
                "origin": request.name,
                "is_object_request_issue": True,
                "object_request_project_id": project.id,
            }
        )
        Move.create(
            _stock_move_vals(
                env,
                picking,
                product,
                1.0,
                warehouse.lot_stock_id,
                warehouse.lot_stock_id,
            )
        )
        request.write({"issue_picking_ids": [(4, picking.id)]})
        checks[code] = {
            "request": _jsonify(request),
            "purchase_order": {
                "id": po.id,
                "picking_type_id": po.picking_type_id.id,
                "object_request_project_id": po.object_request_project_id.id,
            },
            "picking": {
                "id": picking.id,
                "picking_type_id": picking.picking_type_id.id,
                "object_request_project_id": (
                    picking.object_request_project_id.id
                ),
            },
        }
    return {
        "product": _jsonify(product),
        "supplier": _jsonify(supplier),
        "documents": checks,
    }


def main(env):
    report = {
        "status": "ok",
        "database": env.cr.dbname,
        "targets": {},
    }
    try:
        projects = _target_projects(env)
        report["targets"] = {
            code: _warehouse_summary(env, project)
            for code, project in projects.items()
        }
        report["ai_assistant"] = _ai_checks(env)
        report["draft_document_smoke"] = _draft_document_checks(
            env, projects
        )
    except Exception as exc:
        report["status"] = "error"
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()
    finally:
        env.cr.rollback()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    if report["status"] != "ok":
        raise SystemExit(1)


main(globals()["env"])
exit()
