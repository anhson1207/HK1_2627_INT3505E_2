from flask import current_app, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, error, detail, status_code):
        super().__init__(detail)
        self.error = error
        self.detail = detail
        self.status_code = status_code


class NotFound(ApiError):
    def __init__(self, detail="Resource not found"):
        super().__init__("not_found", detail, 404)


class Conflict(ApiError):
    def __init__(self, detail="Resource conflict"):
        super().__init__("conflict", detail, 409)


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def api_error(err):
        return jsonify({"error": err.error, "detail": err.detail}), err.status_code

    @app.errorhandler(ValidationError)
    def validation_error(err):
        return jsonify({"error": "validation_error", "detail": err.messages}), 422

    @app.errorhandler(HTTPException)
    def http_error(err):
        # Invalid JSON / wrong Content-Type -> 400. Other HTTP errors retain their code.
        code = 400 if err.code == 415 else err.code
        error = "bad_request" if code == 400 else err.name.lower().replace(" ", "_")
        return jsonify({"error": error, "detail": err.description}), code

    @app.errorhandler(Exception)
    def unexpected_error(err):
        current_app.logger.exception("Unhandled request error")
        return jsonify({"error": "internal_error", "detail": "Internal server error"}), 500
