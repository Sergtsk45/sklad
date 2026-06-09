# flake8: noqa
import json
import re
from datetime import datetime


TARGETS = {
    10: {
        "code": "O001",
        "project_name": "Ломоносова 164",
        "warehouse_name": "Ломоносова 164 склад",
        "legacy_code": "ОбМ-2",
    },
    16: {
        "code": "O002",
        "project_name": "Б. Хмельницкого, 112",
        "warehouse_name": "Б. Хмельницкого, 112 склад",
        "legacy_code": "ОбМ-4",
    },
}

TEST_CODES = ("O001", "O002", "O003", "O004")


def _name(record):
    return record.display_name if record else False


def _read_module_versions(env):
    modules = env["ir.module.module"].sudo().search(
        [("name", "in", ["object_request", "ai_assistant", "stock", "purchase"])]
    )
    return [
        {
            "name": module.name,
            "state": module.state,
            "latest_version": module.latest_version,
            "installed_version": module.installed_version,
        }
        for module in modules
    ]


def _warehouse_snapshot(env, warehouse):
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
        "company_id": warehouse.company_id.id,
        "company": _name(warehouse.company_id),
        "view_location_id": warehouse.view_location_id.id,
        "lot_stock_id": warehouse.lot_stock_id.id,
        "in_type_id": warehouse.in_type_id.id,
        "int_type_id": warehouse.int_type_id.id,
        "picking_type_ids": picking_type_ids,
        "quant_count": Quant.search_count(quant_domain) if quant_domain else 0,
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


def _read_warehouses(env):
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    warehouses = Warehouse.search(
        ["|", ("code", "ilike", "ОбМ-"), ("code", "ilike", "O")]
    )
    return [_warehouse_snapshot(env, warehouse) for warehouse in warehouses]


def _read_quants(env, warehouse_ids):
    rows = []
    Quant = env["stock.quant"].sudo()
    for warehouse in env["stock.warehouse"].sudo().browse(warehouse_ids).exists():
        if not warehouse.view_location_id:
            continue
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


def _read_documents(env, warehouse_ids):
    rows = []
    Picking = env["stock.picking"].sudo()
    PickingType = env["stock.picking.type"].sudo()
    PurchaseOrder = env["purchase.order"].sudo()
    for warehouse in env["stock.warehouse"].sudo().browse(warehouse_ids).exists():
        picking_type_ids = PickingType.search(
            [("warehouse_id", "=", warehouse.id)]
        ).ids
        pickings = Picking.search([("picking_type_id", "in", picking_type_ids)])
        pos = PurchaseOrder.search([("picking_type_id", "in", picking_type_ids)])
        rows.append(
            {
                "warehouse_id": warehouse.id,
                "warehouse_code": warehouse.code,
                "picking_type_ids": picking_type_ids,
                "pickings": [
                    {
                        "id": picking.id,
                        "name": picking.name,
                        "state": picking.state,
                        "picking_type_id": picking.picking_type_id.id,
                        "origin": picking.origin,
                    }
                    for picking in pickings
                ],
                "purchase_orders": [
                    {
                        "id": po.id,
                        "name": po.name,
                        "state": po.state,
                        "picking_type_id": po.picking_type_id.id,
                        "partner_ref": po.partner_ref,
                    }
                    for po in pos
                ],
            }
        )
    return rows


def _read_projects(env):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    return [
        {
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "active": project.active,
            "warehouse_id": project.warehouse_id.id,
            "warehouse_code": project.warehouse_id.code,
            "request_count": len(project.request_ids),
            "request_ids": project.request_ids.ids,
        }
        for project in Project.search([])
    ]


def _read_sequence(env):
    seq = env["ir.sequence"].sudo().search(
        [("code", "=", "object.request.project.code")], limit=1
    )
    if not seq:
        return None
    return {
        "id": seq.id,
        "code": seq.code,
        "prefix": seq.prefix,
        "padding": seq.padding,
        "number_next_actual": seq.number_next_actual,
    }


def _audit(env):
    return {
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "database": env.cr.dbname,
        "modules": _read_module_versions(env),
        "sequence": _read_sequence(env),
        "warehouses": _read_warehouses(env),
        "target_quants": _read_quants(env, list(TARGETS)),
        "target_documents": _read_documents(env, list(TARGETS)),
        "projects": _read_projects(env),
    }


def _code_suffix(code):
    match = re.match(r"^O(\d{3})$", code or "")
    return int(match.group(1)) if match else 0


def _next_archive_code(env, prefix="X"):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    used_project_codes = set(Project.search([]).mapped("code"))
    used_warehouse_codes = set(Warehouse.search([]).mapped("code"))
    used = used_project_codes | used_warehouse_codes
    for number in range(1, 1000):
        code = f"{prefix}{number:03d}"
        if code not in used:
            return code
    raise RuntimeError("No free archive code found")


def _archive_project(project, actions):
    old_code = project.code
    new_code = _next_archive_code(project.env, "X")
    vals = {
        "active": False,
        "code": new_code,
        "name": f"{project.name} [архив {old_code}]",
    }
    project.write(vals)
    actions.append(
        {
            "action": "archive_project",
            "project_id": project.id,
            "old_code": old_code,
            "new_code": new_code,
        }
    )


def _archive_warehouse(warehouse, actions):
    old_code = warehouse.code
    vals = {"active": False}
    if old_code in TEST_CODES:
        vals["code"] = _next_archive_code(warehouse.env, "W")
    warehouse.write(vals)
    actions.append(
        {
            "action": "archive_warehouse",
            "warehouse_id": warehouse.id,
            "old_code": old_code,
            "new_code": warehouse.code,
        }
    )


def _cleanup_conflicts(env, actions):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    target_warehouse_ids = set(TARGETS)
    target_codes = {data["code"] for data in TARGETS.values()}

    projects = Project.search([("code", "in", TEST_CODES)])
    for project in projects:
        if project.warehouse_id.id in target_warehouse_ids:
            continue
        _archive_project(project, actions)

    warehouses = Warehouse.search([("code", "in", TEST_CODES)])
    for warehouse in warehouses:
        if warehouse.id in target_warehouse_ids:
            continue
        if warehouse.code in target_codes or warehouse.code in TEST_CODES:
            _archive_warehouse(warehouse, actions)


def _ensure_project(env, warehouse, target, actions):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    project = Project.search([("warehouse_id", "=", warehouse.id)], limit=1)
    if not project:
        project = Project.create(
            {
                "name": target["project_name"],
                "code": target["code"],
                "warehouse_id": warehouse.id,
                "company_id": warehouse.company_id.id,
                "active": True,
            }
        )
        actions.append(
            {
                "action": "create_project",
                "project_id": project.id,
                "code": target["code"],
                "warehouse_id": warehouse.id,
            }
        )
    else:
        before = {
            "name": project.name,
            "code": project.code,
            "active": project.active,
            "warehouse_id": project.warehouse_id.id,
        }
        project.write(
            {
                "name": target["project_name"],
                "code": target["code"],
                "active": True,
                "warehouse_id": warehouse.id,
                "company_id": warehouse.company_id.id,
            }
        )
        actions.append(
            {
                "action": "update_project",
                "project_id": project.id,
                "before": before,
                "after": {
                    "name": project.name,
                    "code": project.code,
                    "active": project.active,
                    "warehouse_id": project.warehouse_id.id,
                },
            }
        )
    return project


def _apply_targets(env, before_snapshots, actions):
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    for warehouse_id, target in TARGETS.items():
        warehouse = Warehouse.browse(warehouse_id).exists()
        if not warehouse:
            raise RuntimeError(f"Warehouse id {warehouse_id} not found")
        project = _ensure_project(env, warehouse, target, actions)
        warehouse.write(
            {
                "code": target["code"],
                "name": target["warehouse_name"],
                "active": True,
                "company_id": project.company_id.id,
            }
        )
        actions.append(
            {
                "action": "update_warehouse",
                "warehouse_id": warehouse.id,
                "legacy_code": target["legacy_code"],
                "code": warehouse.code,
                "name": warehouse.name,
            }
        )

        before = before_snapshots[warehouse_id]
        after = _warehouse_snapshot(env, warehouse)
        for field_name in (
            "view_location_id",
            "lot_stock_id",
            "in_type_id",
            "int_type_id",
        ):
            if before[field_name] != after[field_name]:
                raise RuntimeError(
                    f"Warehouse {warehouse_id} changed {field_name}: "
                    f"{before[field_name]} -> {after[field_name]}"
                )


def _update_sequence(env, actions):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    seq = env["ir.sequence"].sudo().search(
        [("code", "=", "object.request.project.code")], limit=1
    )
    if not seq:
        return
    max_code = max(
        (_code_suffix(code) for code in Project.search([]).mapped("code")),
        default=0,
    )
    next_number = max_code + 1
    if seq.number_next_actual < next_number:
        before = seq.number_next_actual
        seq.write({"number_next_actual": next_number})
        actions.append(
            {
                "action": "update_sequence",
                "sequence_id": seq.id,
                "before": before,
                "after": seq.number_next_actual,
            }
        )


def _validate(env):
    Project = env["object.request.project"].sudo().with_context(active_test=False)
    checks = []
    for warehouse_id, target in TARGETS.items():
        warehouse = env["stock.warehouse"].sudo().browse(warehouse_id)
        projects = Project.search(
            [("code", "=", target["code"]), ("warehouse_id", "=", warehouse_id)]
        )
        checks.append(
            {
                "warehouse_id": warehouse_id,
                "expected_code": target["code"],
                "warehouse_code": warehouse.code,
                "warehouse_name": warehouse.name,
                "project_ids": projects.ids,
                "project_count": len(projects),
                "ok": warehouse.code == target["code"] and len(projects) == 1,
            }
        )
    failed = [check for check in checks if not check["ok"]]
    if failed:
        raise RuntimeError(f"Validation failed: {failed}")
    return checks


def run(env):
    before = _audit(env)
    Warehouse = env["stock.warehouse"].sudo().with_context(active_test=False)
    missing_targets = [
        warehouse_id
        for warehouse_id in TARGETS
        if not Warehouse.browse(warehouse_id).exists()
    ]
    if missing_targets:
        env.cr.rollback()
        return {
            "status": "blocked_missing_target_warehouses",
            "missing_warehouse_ids": missing_targets,
            "before": before,
            "actions": [],
            "validations": [],
            "after": before,
        }
    before_target_snapshots = {
        warehouse_id: _warehouse_snapshot(
            env, Warehouse.browse(warehouse_id)
        )
        for warehouse_id in TARGETS
    }
    actions = []
    _cleanup_conflicts(env, actions)
    _apply_targets(env, before_target_snapshots, actions)
    _update_sequence(env, actions)
    validations = _validate(env)
    env.cr.commit()
    return {
        "before": before,
        "actions": actions,
        "validations": validations,
        "after": _audit(env),
    }


print(json.dumps(run(env), ensure_ascii=False, indent=2, default=str))
