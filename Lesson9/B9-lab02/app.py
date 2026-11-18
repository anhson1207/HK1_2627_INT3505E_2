from functools import wraps
from flask import Flask, jsonify, request

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}

USERS = {
    1: {"f": "Văn", "l": "Nguyễn", "e": "a@vnu.vn"},
    2: {"f": "Trang", "l": "Trần", "e": "b@vnu.vn"},
}

app = Flask(__name__)


def api_version(supported=SUPPORTED, default=LATEST):
    """Chọn phiên bản API từ X-API-Version, mặc định dùng v2."""
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                return jsonify(error="unsupported version"), 400

            result = fn(version, *args, **kwargs)
            if isinstance(result, tuple):
                payload, status = result
            else:
                payload, status = result, 200

            response = jsonify(payload)
            response.status_code = status
            response.headers["X-API-Version-Served"] = version
            return response

        return wrapper

    return decorate


@app.route("/users/<int:uid>", methods=["GET"])
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)
    if not user:
        return {"error": "not found"}, 404

    if version == "1":
        return {
            "id": uid,
            "full_name": f"{user['f']} {user['l']}",
        }

    # Version 2 va version theo ngay cung su dung schema moi.
    return {
        "id": uid,
        "first_name": user["f"],
        "last_name": user["l"],
        "email": user["e"],
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
