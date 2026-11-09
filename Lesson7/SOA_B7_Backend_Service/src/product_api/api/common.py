from flask import request
from marshmallow import ValidationError


def require_json_object():
    if not request.is_json:
        from werkzeug.exceptions import BadRequest

        raise BadRequest("Content-Type must be application/json")
    from werkzeug.exceptions import BadRequest

    payload = request.get_json()
    if not isinstance(payload, dict):
        raise ValidationError({"_schema": ["Expected a JSON object"]})
    return payload


def pagination():
    values = {}
    for name, default in (("page", 1), ("size", 20)):
        raw = request.args.get(name, str(default))
        try:
            values[name] = int(raw)
        except (ValueError, TypeError):
            raise ValidationError({name: ["Must be a positive integer"]}) from None
        if values[name] < 1:
            raise ValidationError({name: ["Must be at least 1"]})
    values["size"] = min(values["size"], 100)
    return values["page"], values["size"]
