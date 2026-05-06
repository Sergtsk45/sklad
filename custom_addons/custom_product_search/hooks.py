"""Database hooks for custom_product_search."""


def post_init_hook(env):
    """Enable trigram support and normalized search indexes."""
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    env.cr.execute("""
        CREATE INDEX IF NOT EXISTS product_template_x_search_name_trgm_idx
        ON product_template
        USING gin (x_search_name gin_trgm_ops)
    """)
    env.cr.execute("""
        CREATE INDEX IF NOT EXISTS product_product_x_search_name_trgm_idx
        ON product_product
        USING gin (x_search_name gin_trgm_ops)
    """)
