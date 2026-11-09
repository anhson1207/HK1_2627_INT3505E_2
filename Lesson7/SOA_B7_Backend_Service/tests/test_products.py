def test_create_and_get_product(client):
    created = client.post("/api/v1/products", json={
        "sku": "PRD-001", "name": "Keyboard", "price_cents": 2999
    })
    assert created.status_code == 201
    product = created.get_json()
    assert product["qty_in_stock"] == 0
    assert client.get(f'/api/v1/products/{product["id"]}').get_json()["sku"] == "PRD-001"


def test_list_pagination(client, product_factory):
    product_factory("SKU-001")
    product_factory("SKU-002")
    product_factory("SKU-003")
    result = client.get("/api/v1/products?page=2&size=2")
    assert result.status_code == 200
    body = result.get_json()
    assert (body["page"], body["size"], body["total"]) == (2, 2, 3)
    assert [p["sku"] for p in body["items"]] == ["SKU-003"]


def test_duplicate_sku_is_conflict(client, product_factory):
    product_factory("SKU-001")
    result = client.post("/api/v1/products", json={
        "sku": "SKU-001", "name": "Duplicate", "price_cents": 0
    })
    assert result.status_code == 409
    assert result.get_json()["error"] == "conflict"


def test_invalid_input_returns_422(client):
    result = client.post("/api/v1/products", json={
        "sku": "S", "name": "", "price_cents": -3
    })
    assert result.status_code == 422
    assert result.get_json()["error"] == "validation_error"
    assert client.get("/api/v1/products?page=bad").status_code == 422


def test_patch_and_soft_delete(client, product_factory):
    product = product_factory()
    pid = product["id"]
    patch = client.patch(f"/api/v1/products/{pid}", json={"name": "Updated"})
    assert patch.status_code == 200
    assert patch.get_json()["name"] == "Updated"
    assert client.delete(f"/api/v1/products/{pid}").status_code == 204
    assert client.delete(f"/api/v1/products/{pid}").status_code == 204
    assert client.get(f"/api/v1/products/{pid}").status_code == 404
    assert client.get("/api/v1/products").get_json()["total"] == 0


def test_reserve_deducts_without_negative_stock(client, product_factory):
    pid = product_factory(qty=3)["id"]
    ok = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 2})
    assert ok.status_code == 200
    assert ok.get_json()["qty_in_stock"] == 1
    conflict = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 2})
    assert conflict.status_code == 409
    assert client.get(f"/api/v1/products/{pid}").get_json()["qty_in_stock"] == 1
    assert client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 0}).status_code == 422


def test_missing_and_bad_content_type(client):
    assert client.get("/api/v1/products/999").status_code == 404
    assert client.post("/api/v1/products", data="hello", content_type="text/plain").status_code == 400
