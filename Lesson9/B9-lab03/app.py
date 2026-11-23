"""Practice 3/5: Sunset middleware bằng Flask decorator."""

from datetime import datetime, timezone

from flask import Flask
from sunset import deprecate_at

app = Flask(__name__)

# Mốc trong slide Buổi 9, trang 22 (theo giờ UTC).
V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


# Endpoint v2 đơn giản, để liên kết thay thế thực sự truy cập được.
@app.route("/api/v2/users")
def list_v2():
    return [{"id": 1, "first_name": "Văn A", "last_name": "Nguyễn"}]


@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):
    return {"id": uid, "first_name": "Văn A", "last_name": "Nguyễn"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
