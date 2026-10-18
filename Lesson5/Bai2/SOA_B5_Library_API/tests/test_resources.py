import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
API = "/api/v1"


def validates(schema_name, data):
    doc = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    Draft202012Validator(doc, format_checker=FormatChecker()).validate(data)


def test_all_three_resource_schemas_match_real_api(client):
    book = client.get(API + "/books/1").json
    member = client.get(API + "/members/1").json
    loans = client.get(API + "/members/1/loans").json["data"]
    validates("book.schema.json", book)
    validates("member.schema.json", member)
    assert loans
    validates("loan.schema.json", loans[0])


def test_create_book_and_patch(client):
    r = client.post(API + "/books", json={
        "title": "REST API Design", "isbn": "9780000000100", "genreId": 1,
        "publicationYear": 2026, "description": "Lecture notes"
    })
    assert r.status_code == 201, r.json
    assert r.headers["Location"].endswith("/books/11")
    validates("book.schema.json", r.json)
    patch = client.patch(API + "/books/11", json={"title": "REST API Design Second"})
    assert patch.status_code == 200
    assert patch.json["title"] == "REST API Design Second"


def test_input_validation_and_duplicate_isbn(client):
    assert client.post(API + "/books", json={"title": "Broken"}).status_code == 400
    r = client.post(API + "/books", json={
        "title": "Duplicated", "isbn": "9780132350884", "genreId": 1, "publicationYear": 2026
    })
    assert r.status_code == 409
    assert client.patch(API + "/books/1", json={"weird": 3}).status_code == 400


def test_book_author_association_has_role(client):
    author = client.post(API + "/authors", json={"name": "A New Writer"})
    assert author.status_code == 201
    aid = author.json["id"]
    add = client.post(API + "/books/1/authors", json={"authorId": aid, "role": "editor"})
    assert add.status_code == 201
    assert any(x["id"] == aid and x["role"] == "editor"
               for x in client.get(API + "/books/1/authors").json["data"])
    assert client.post(API + "/books/1/authors", json={"authorId": aid}).status_code == 409
    assert client.delete(API + f"/books/1/authors/{aid}").status_code == 204


def test_member_and_copy_lifecycle(client):
    member = client.post(API + "/members", json={"fullName": "Sample Member", "email": "new@example.com"})
    assert member.status_code == 201
    assert client.get(API + f"/members/{member.json['id']}").status_code == 200
    copy = client.post(API + "/books/2/copies", json={"barcode": "FRESH-777"})
    assert copy.status_code == 201
    assert copy.json["isAvailable"] is True


def test_loan_does_not_allow_same_copy_twice_and_can_be_returned(client):
    member = client.post(API + "/members", json={"fullName": "Loan Tester", "email": "borrower@example.com"}).json
    copy = client.post(API + "/books/2/copies", json={"barcode": "NEW-LOAN-001"}).json
    due = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    data = {"memberId": member["id"], "copyId": copy["id"], "dueAt": due}
    first = client.post(API + "/loans", json=data)
    assert first.status_code == 201, first.json
    validates("loan.schema.json", first.json)
    assert first.json["status"] == "active"
    assert client.post(API + "/loans", json=data).status_code == 409
    returned = client.patch(API + f"/loans/{first.json['id']}", json={"action": "return"})
    assert returned.status_code == 200
    assert returned.json["status"] == "returned"
    assert client.post(API + "/loans", json=data).status_code == 201


def test_book_with_loan_history_cannot_be_deleted(client):
    assert client.delete(API + "/books/1").status_code == 409
    assert client.delete(API + "/books/10").status_code == 204
    assert client.get(API + "/books/10").status_code == 404


def test_genre_and_authors_queries(client):
    assert len(client.get(API + "/genres").json["data"]) == 4
    authors = client.get(API + "/authors", query_string={"limit": 2})
    assert authors.status_code == 200
    assert len(authors.json["data"]) == 2
    assert client.get(API + "/authors/1/books").status_code == 200
    assert client.get(API + "/books/1/copies").status_code == 200


def test_health(client):
    assert client.get("/health").json == {"status": "ok"}
