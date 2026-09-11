import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

LOCATION_FIELDS = (
    ("zone", "capture_id", "object.request.project.capture"),
    ("floor", "floor_id", "object.request.project.floor"),
    ("section", "section_id", "object.request.project.section"),
)


def _normalize(value):
    return " ".join((value or "").split())


def _get_or_create_location(env, model_name, project, name):
    Location = env[model_name]
    location = Location.search(
        [
            ("project_id", "=", project.id),
            ("name", "=", name),
        ],
        limit=1,
    )
    if location:
        return location
    return Location.create(
        {
            "name": name,
            "project_id": project.id,
        }
    )


def _migrate_line_locations(env, line):
    vals = {}
    for legacy_field, target_field, model_name in LOCATION_FIELDS:
        if line[target_field]:
            continue
        name = _normalize(line[legacy_field])
        if not name:
            continue
        location = _get_or_create_location(
            env, model_name, line.request_id.project_id, name
        )
        vals[target_field] = location.id
    if vals:
        line.write(vals)
    return bool(vals)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env["object.request.line"].search(
        [
            ("request_id.project_id", "!=", False),
            "|",
            "|",
            ("zone", "!=", False),
            ("floor", "!=", False),
            ("section", "!=", False),
        ]
    )
    migrated = sum(1 for line in lines if _migrate_line_locations(env, line))
    _logger.info(
        "object_request 1.5.0: migrated %s line location values.",
        migrated,
    )
