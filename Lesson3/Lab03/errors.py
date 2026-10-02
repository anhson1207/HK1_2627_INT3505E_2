import uuid
from flask import request, jsonify
from werkzeug.exceptions import HTTPException

ERROR_BASE = "https://api.example.com/probs"


class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__(detail or title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type_path = type_path
        self.extra = extra


def _problem(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4())[:8],
    }
    if detail:
        body["detail"] = detail
    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp


def register_error_handlers(app):
    @app.errorhandler(ApiProblem)
    def handle_problem(err):
        return _problem(err.status, err.title, err.detail, err.type_path, **err.extra)

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return _problem(err.code, err.name, err.description)

    @app.errorhandler(Exception)
    def handle_500(err):
        app.logger.error("Unhandled: %s", err)
        return _problem(500, "Internal Server Error", "Lỗi nội bộ máy chủ.")
