"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
def test_get_books_empty(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []



def test_get_book_not_found(client):
    response = client.get("/books/999999")

    assert response.status_code == 404

    data = response.get_json()

    assert data is not None
    assert data["code"] == "NOT_FOUND"



def test_post_book_missing_title(client):
    payload = {
        "author": "Nguyen Van A"
    }

    response = client.post(
        "/books",
        json=payload
    )

    assert response.status_code == 400

    data = response.get_json()
    errors = data.get("errors", [])

    assert any(
        error.get("field") == "title"
        for error in errors
    )



def test_delete_then_get_returns_404(
    client, sample_book
):
    book_id = sample_book

    delete_response = client.delete(
        f"/books/{book_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/books/{book_id}"
    )

    assert get_response.status_code == 404