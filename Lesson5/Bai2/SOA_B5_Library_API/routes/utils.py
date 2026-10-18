import json
from pathlib import Path
from flask import jsonify, request
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def fail(code, message, status=400, **extra):
    return jsonify({"error": code, "message": message, **extra}), status


def body(schema_name=None):
    """Return (payload, error response). Enforce JSON objects and optional schema."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, fail("invalid_json", "A JSON object is required")
    if schema_name:
        schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        issues = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload), key=lambda e: str(e.path))
        if issues:
            err = issues[0]
            return None, fail("validation_failed", err.message, field=list(err.path))
    return payload, None


def bounded_int(raw, name, default=20, maximum=100, minimum=1):
    if raw is None:
        return default, None
    try:
        value = int(raw)
    except (ValueError, TypeError):
        return None, fail("bad_parameter", f"{name} must be an integer")
    if value < minimum:
        return None, fail("bad_parameter", f"{name} must be >= {minimum}")
    return min(value, maximum), None


def simple_page(q, model):
    limit, err = bounded_int(request.args.get("limit"), "limit")
    if err:
        return err
    offset, err = bounded_int(request.args.get("offset"), "offset", default=0, minimum=0, maximum=10**8)
    if err:
        return err
    total = q.count()
    rows = q.order_by(model.id).offset(offset).limit(limit).all()
    return jsonify({"data": [r.to_dict() for r in rows],
                    "pagination": {"strategy": "offset", "offset": offset,
                                   "limit": limit, "total": total, "hasMore": offset + len(rows) < total}})
