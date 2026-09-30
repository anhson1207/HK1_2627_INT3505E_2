import uuid
import logging
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
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
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
    def handle_api_problem(err):
        return _problem(
            status=err.status,
            title=err.title,
            detail=err.detail,
            type_path=err.type_path,
            **err.extra
        )


    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return _problem(
            status=err.code,
            title=err.name,
            detail=err.description
        )


    @app.errorhandler(Exception)
    def handle_exception(err):
        app.logger.error("Unhandled Exception: %s", err, exc_info=True)
        return _problem(
            status=500,
            title="Internal Server Error",
            detail="Đã xảy ra lỗi nội bộ máy chủ."
        )
