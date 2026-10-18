import pytest
from app import create_app
from extensions import db
from seed import seed


@pytest.fixture()
def app():
    application = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SECRET_KEY": "test-only-secret"})
    with application.app_context():
        seed()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def get_books(client, **params):
    return client.get("/api/v1/books", query_string=params)
