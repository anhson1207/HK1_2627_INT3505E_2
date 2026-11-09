from sqlalchemy import event

from product_api.extensions import db


def create_two_products(product_factory):
    p1 = product_factory("BOOK-001", "Book A", 1000, 5)
    p2 = product_factory("BOOK-002", "Book B", 2000, 8)
    return p1, p2


def create_order(client, p1, p2):
    return client.post("/api/v1/orders", json={"items": [
        {"product_id": p1["id"], "qty": 2},
        {"product_id": p2["id"], "qty": 3},
    ]})


def test_create_order_with_multiple_order_items(client, product_factory):
    p1, p2 = create_two_products(product_factory)
    response = create_order(client, p1, p2)
    assert response.status_code == 201, response.get_json()
    data = response.get_json()
    assert data["total_cents"] == 2 * 1000 + 3 * 2000
    assert len(data["items"]) == 2
    assert [line["product"]["name"] for line in data["items"]] == ["Book A", "Book B"]
    assert client.get(f'/api/v1/products/{p1["id"]}').get_json()["qty_in_stock"] == 3
    assert client.get(f'/api/v1/products/{p2["id"]}').get_json()["qty_in_stock"] == 5
    assert client.get(f'/api/v1/orders/{data["id"]}').status_code == 200
    items_response = client.get(f'/api/v1/orders/{data["id"]}/items')
    assert items_response.status_code == 200
    assert len(items_response.get_json()["items"]) == 2


def test_order_stock_failure_is_atomic(client, product_factory):
    p1, p2 = create_two_products(product_factory)
    response = client.post("/api/v1/orders", json={"items": [
        {"product_id": p1["id"], "qty": 2},
        {"product_id": p2["id"], "qty": 999},
    ]})
    assert response.status_code == 409
    assert client.get(f'/api/v1/products/{p1["id"]}').get_json()["qty_in_stock"] == 5
    assert client.get("/api/v1/orders").get_json()["total"] == 0


def test_order_rejects_invalid_items(client, product_factory):
    product = product_factory()
    duplicate = client.post("/api/v1/orders", json={"items": [
        {"product_id": product["id"], "qty": 1},
        {"product_id": product["id"], "qty": 2},
    ]})
    assert duplicate.status_code == 422
    unknown = client.post("/api/v1/orders", json={"items": [
        {"product_id": 999, "qty": 1},
    ]})
    assert unknown.status_code == 404


def test_order_keeps_unit_price_snapshot(client, product_factory):
    p1, p2 = create_two_products(product_factory)
    data = create_order(client, p1, p2).get_json()
    client.patch(f'/api/v1/products/{p1["id"]}', json={"price_cents": 9000})
    old = client.get(f'/api/v1/orders/{data["id"]}').get_json()
    assert old["total_cents"] == 8000
    assert old["items"][0]["unit_price_cents"] == 1000


def test_order_get_eager_loading_no_n_plus_one(client, product_factory, app):
    # Two orders, two products, stable SQL count with selectinload.
    p1, p2 = create_two_products(product_factory)
    first = create_order(client, p1, p2)
    assert first.status_code == 201
    second = client.post("/api/v1/orders", json={"items": [
        {"product_id": p1["id"], "qty": 1},
    ]})
    assert second.status_code == 201

    statements = []

    def count_select(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", count_select)
        try:
            response = client.get("/api/v1/orders?page=1&size=20")
        finally:
            event.remove(db.engine, "before_cursor_execute", count_select)

    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["total"] == 2
    assert len(body["items"][0]["items"]) == 2
    # Orders + OrderItems + Products + COUNT: at most 4 SELECTs, not 1 + N.
    assert len(statements) <= 4, "Potential N+1 queries: " + repr(statements)


def test_missing_order(client):
    assert client.get("/api/v1/orders/42").status_code == 404
