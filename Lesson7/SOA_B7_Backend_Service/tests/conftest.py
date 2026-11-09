import pytest

from product_api import create_app
from product_api.extensions import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def product_factory(client):
    def create(sku="SKU-001", name="USB-C Adapter", price_cents=1200, qty=10):
        response = client.post("/api/v1/products", json={
            "sku": sku, "name": name, "price_cents": price_cents,
            "qty_in_stock": qty,
        })
        assert response.status_code == 201, response.get_json()
        return response.get_json()
    return create
