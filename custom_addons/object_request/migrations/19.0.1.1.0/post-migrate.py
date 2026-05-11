from odoo import api, SUPERUSER_ID


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = %s
           AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())


def _table_exists(cr, table):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.tables
         WHERE table_name = %s
        """,
        (table,),
    )
    return bool(cr.fetchone())


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    projects = env['object.request.project'].with_context(active_test=False).search([
        ('warehouse_id', '=', False),
    ])
    sequence = env['ir.sequence'].sudo()
    for project in projects:
        if not project.code:
            project.write({
                'code': sequence.next_by_code('object.request.project.code'),
            })
        project._ensure_project_warehouse()

    if (
        _column_exists(cr, 'object_request', 'warehouse_id')
        and _column_exists(cr, 'object_request_line', 'stock_qty_on_hand')
    ):
        cr.execute(
            """
            INSERT INTO object_request_line_stock
                (
                    line_id,
                    warehouse_id,
                    qty_on_hand,
                    qty_to_issue,
                    qty_reserved,
                    last_check_date,
                    company_id,
                    create_uid,
                    create_date,
                    write_uid,
                    write_date
                )
            SELECT
                line.id,
                req.warehouse_id,
                COALESCE(line.stock_qty_on_hand, 0.0),
                COALESCE(line.qty_to_issue, 0.0),
                COALESCE(line.qty_reserved, 0.0),
                line.stock_check_date,
                req.company_id,
                1,
                now(),
                1,
                now()
              FROM object_request_line line
              JOIN object_request req ON req.id = line.request_id
             WHERE req.warehouse_id IS NOT NULL
               AND COALESCE(line.stock_qty_on_hand, 0.0) > 0
               AND NOT EXISTS (
                   SELECT 1
                     FROM object_request_line_stock stock
                    WHERE stock.line_id = line.id
                      AND stock.warehouse_id = req.warehouse_id
               )
            """
        )

    if _column_exists(cr, 'object_request', 'warehouse_id'):
        cr.execute('ALTER TABLE object_request DROP COLUMN warehouse_id')
    if _column_exists(cr, 'object_request', 'stock_check_confirmed'):
        cr.execute('ALTER TABLE object_request DROP COLUMN stock_check_confirmed')
    if _table_exists(cr, 'object_request_check_warehouse_rel'):
        cr.execute('DROP TABLE object_request_check_warehouse_rel')
