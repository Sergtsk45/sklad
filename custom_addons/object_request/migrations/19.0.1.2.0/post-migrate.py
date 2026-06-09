from odoo import api, SUPERUSER_ID


TARGETS = {
    10: {
        "code": "O001",
        "project_name": "Ломоносова 164",
        "warehouse_name": "Ломоносова 164 склад",
    },
    16: {
        "code": "O002",
        "project_name": "Б. Хмельницкого, 112",
        "warehouse_name": "Б. Хмельницкого, 112 склад",
    },
}

CONFLICT_CODES = ("O001", "O002", "O003", "O004")


def _next_archive_code(env, prefix):
    Project = env["object.request.project"].with_context(active_test=False)
    Warehouse = env["stock.warehouse"].with_context(active_test=False)
    used = set(Project.search([]).mapped("code"))
    used |= set(Warehouse.search([]).mapped("code"))
    for number in range(1, 1000):
        code = f"{prefix}{number:03d}"
        if code not in used:
            return code
    raise RuntimeError("No free archive code found")


def _archive_conflicting_projects(env):
    Project = env["object.request.project"].with_context(active_test=False)
    target_warehouse_ids = set(TARGETS)
    projects = Project.search([("code", "in", CONFLICT_CODES)])
    for project in projects:
        if project.warehouse_id.id in target_warehouse_ids:
            continue
        old_code = project.code
        project.write(
            {
                "active": False,
                "code": _next_archive_code(env, "X"),
                "name": f"{project.name} [архив {old_code}]",
            }
        )


def _archive_conflicting_warehouses(env):
    Warehouse = env["stock.warehouse"].with_context(active_test=False)
    target_warehouse_ids = set(TARGETS)
    warehouses = Warehouse.search([("code", "in", CONFLICT_CODES)])
    for warehouse in warehouses:
        if warehouse.id in target_warehouse_ids:
            continue
        vals = {"active": False}
        if warehouse.code in CONFLICT_CODES:
            vals["code"] = _next_archive_code(env, "W")
        warehouse.write(vals)


def _ensure_target_project(env, warehouse, target):
    Project = env["object.request.project"].with_context(active_test=False)
    project = Project.search([("warehouse_id", "=", warehouse.id)], limit=1)
    vals = {
        "name": target["project_name"],
        "code": target["code"],
        "active": True,
        "warehouse_id": warehouse.id,
        "company_id": warehouse.company_id.id,
    }
    if project:
        project.write(vals)
    else:
        project = Project.create(vals)
    return project


def _apply_targets(env):
    Warehouse = env["stock.warehouse"].with_context(active_test=False)
    for warehouse_id, target in TARGETS.items():
        warehouse = Warehouse.browse(warehouse_id).exists()
        if not warehouse:
            continue
        before = {
            "view_location_id": warehouse.view_location_id.id,
            "lot_stock_id": warehouse.lot_stock_id.id,
            "in_type_id": warehouse.in_type_id.id,
            "int_type_id": warehouse.int_type_id.id,
        }
        project = _ensure_target_project(env, warehouse, target)
        warehouse.write(
            {
                "code": target["code"],
                "name": target["warehouse_name"],
                "active": True,
                "company_id": project.company_id.id,
            }
        )
        after = {
            "view_location_id": warehouse.view_location_id.id,
            "lot_stock_id": warehouse.lot_stock_id.id,
            "in_type_id": warehouse.in_type_id.id,
            "int_type_id": warehouse.int_type_id.id,
        }
        if before != after:
            raise RuntimeError(
                "WHM migration changed warehouse links for id %s"
                % warehouse_id
            )


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _archive_conflicting_projects(env)
    _archive_conflicting_warehouses(env)
    _apply_targets(env)
