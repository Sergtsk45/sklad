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
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS _legacy_object_request_warehouse (
            id SERIAL PRIMARY KEY,
            request_id INTEGER,
            warehouse_id INTEGER,
            check_warehouse_id INTEGER,
            migrated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
        )
        """
    )

    if _column_exists(cr, "object_request", "warehouse_id"):
        cr.execute(
            """
            INSERT INTO _legacy_object_request_warehouse
                (request_id, warehouse_id)
            SELECT id, warehouse_id
              FROM object_request
             WHERE warehouse_id IS NOT NULL
            """
        )

    rel_table = "object_request_check_warehouse_rel"
    if _table_exists(cr, rel_table):
        request_col = (
            "object_request_id"
            if _column_exists(cr, rel_table, "object_request_id")
            else "request_id"
        )
        warehouse_col = (
            "stock_warehouse_id"
            if _column_exists(cr, rel_table, "stock_warehouse_id")
            else "warehouse_id"
        )
        cr.execute(
            f"""
            INSERT INTO _legacy_object_request_warehouse
                (request_id, check_warehouse_id)
            SELECT {request_col}, {warehouse_col}
              FROM {rel_table}
             WHERE {request_col} IS NOT NULL
               AND {warehouse_col} IS NOT NULL
            """
        )
