"""Print product feature audit summary inside an Odoo shell.

Usage:
    odoo shell -d <db> < product_feature_audit.py
"""

AuditLine = env[  # noqa: F821
    "object.request.product.feature.audit.line"
].sudo()
AuditLine.refresh_report()
groups = AuditLine.read_group(
    [],
    ["issue_type"],
    ["issue_type"],
    lazy=False,
)
print("Product feature audit")
for group in groups:
    count = group.get("__count") or group.get("issue_type_count") or 0
    print("%s: %s" % (group["issue_type"], count))
for line in AuditLine.search([], limit=100):
    print(
        "%s | %s | %s | %s"
        % (
            line.issue_type,
            line.product_id.display_name,
            line.feature_key or "-",
            line.note or "",
        )
    )
