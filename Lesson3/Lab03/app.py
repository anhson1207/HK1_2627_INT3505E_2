import base64
import json
from flask import Flask, request, jsonify
from errors import ApiProblem, register_error_handlers

app = Flask(__name__)
register_error_handlers(app)

ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 350.0, "created_at": "2026-03-01T08:00:00Z"},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 45.5, "created_at": "2026-03-01T09:30:00Z"},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 120.0, "created_at": "2026-03-02T10:15:00Z"},
    {"id": 4, "customer_id": 103, "status": "shipped", "total": 520.0, "created_at": "2026-03-02T14:00:00Z"},
    {"id": 5, "customer_id": 104, "status": "cancelled", "total": 85.0, "created_at": "2026-03-03T11:20:00Z"},
    {"id": 6, "customer_id": 102, "status": "paid", "total": 210.0, "created_at": "2026-03-03T16:45:00Z"},
    {"id": 7, "customer_id": 105, "status": "pending", "total": 60.0, "created_at": "2026-03-04T07:10:00Z"},
    {"id": 8, "customer_id": 101, "status": "shipped", "total": 430.0, "created_at": "2026-03-04T12:30:00Z"},
]

ORDER_FIELDS = {"id", "customer_id", "status", "total", "created_at"}


def decode_cursor(cursor_str):
    try:
        raw = cursor_str.strip('"\'')
        raw += "=" * ((4 - len(raw) % 4) % 4)
        data = json.loads(base64.urlsafe_b64decode(raw).decode())
        if not isinstance(data, dict) or "id" not in data:
            raise ValueError
        return data
    except Exception:
        raise ApiProblem(400, "Bad Request", "Cursor không hợp lệ.", "invalid-cursor")


def encode_cursor(payload):
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


@app.get("/orders")
def get_orders():
    # 1. Limit
    try:
        limit = int(request.args.get("limit", 10))
        if not (1 <= limit <= 100):
            raise ValueError
    except ValueError:
        raise ApiProblem(400, "Bad Request", "limit phải là số từ 1 đến 100.", "invalid-limit")

    # 2. Filter
    data = list(ORDERS)
    if status := request.args.get("status"):
        data = [o for o in data if o["status"].lower() == status.lower()]
    if cid := request.args.get("customer_id"):
        data = [o for o in data if str(o["customer_id"]) == cid]

    # 3. Sort
    sort_field = request.args.get("sort", "created_at")
    desc = request.args.get("direction", "desc" if not request.args.get("sort") else "asc") == "desc"
    if sort_field.startswith("-"):
        sort_field, desc = sort_field[1:], True
    if sort_field not in ORDER_FIELDS:
        raise ApiProblem(400, "Bad Request", f"Trường sort '{sort_field}' không tồn tại.", "invalid-sort-field")
    data.sort(key=lambda o: (o[sort_field], o["id"]), reverse=desc)

    # 4. Cursor Pagination
    start = 0
    if cursor_raw := request.args.get("cursor"):
        c_id = decode_cursor(cursor_raw)["id"]
        found = [i for i, o in enumerate(data) if o["id"] == c_id]
        start = (found[0] + 1) if found else len(data)

    page = data[start:start + limit]
    has_more = (start + limit) < len(data)
    next_cursor = encode_cursor({"id": page[-1]["id"]}) if has_more and page else None

    # 5. Sparse fieldsets
    if fields_param := request.args.get("fields"):
        fields = [f.strip() for f in fields_param.split(",")]
        for f in fields:
            if f not in ORDER_FIELDS:
                raise ApiProblem(400, "Bad Request", f"Trường '{f}' không tồn tại.", "invalid-field")
        page = [{k: o[k] for k in fields if k in o} for o in page]

    return jsonify({
        "data": page,
        "pagination": {"limit": limit, "next_cursor": next_cursor, "has_more": has_more},
        "next": f"/orders?limit={limit}&cursor={next_cursor}" if next_cursor else None
    })


@app.get("/orders/<int:id>")
def get_order(id):
    order = next((o for o in ORDERS if o["id"] == id), None)
    if not order:
        raise ApiProblem(404, "Order not found", f"Không tìm thấy order {id}.", "order-not-found")
    return jsonify(order)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
