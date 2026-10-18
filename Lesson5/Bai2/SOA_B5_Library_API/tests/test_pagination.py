"""Tests for both pagination strategies, multi-key ties, and cursor security."""
from tests.conftest import get_books


def test_offset_page_metadata(client):
    r = get_books(client, strategy="offset", limit=3, offset=2, sort="title")
    assert r.status_code == 200
    assert len(r.json["data"]) == 3
    assert r.json["pagination"] == {
        "strategy": "offset", "offset": 2, "limit": 3, "total": 10, "hasMore": True
    }


def test_offset_results_are_ordered(client):
    r = get_books(client, strategy="offset", limit=10, sort="title")
    titles = [row["title"] for row in r.json["data"]]
    assert titles == sorted(titles)


def test_cursor_walks_all_books_without_duplicates_even_on_ties(client):
    cursor = None
    got = []
    for _ in range(10):
        args = {"strategy": "cursor", "limit": 2, "sort": "-publication_year,title", "genre": "technology"}
        if cursor:
            args["cursor"] = cursor
        r = get_books(client, **args)
        assert r.status_code == 200, r.json
        got.extend((v["publicationYear"], v["title"], v["id"]) for v in r.json["data"])
        cursor = r.json["pagination"]["nextCursor"]
        if not r.json["pagination"]["hasMore"]:
            break
    assert len(got) == 7
    assert len(set(got)) == 7
    assert got == sorted(got, key=lambda x: (-x[0], x[1], x[2]))


def test_both_pagination_strategies_yield_same_first_page(client):
    q = {"limit": 4, "genre": "technology", "sort": "title,-publication_year"}
    offset = get_books(client, strategy="offset", **q).json
    cursor = get_books(client, strategy="cursor", **q).json
    assert [x["id"] for x in offset["data"]] == [x["id"] for x in cursor["data"]]


def test_cursor_rejects_modified_token(client):
    first = get_books(client, strategy="cursor", limit=1)
    token = first.json["pagination"]["nextCursor"]
    assert token
    bad = token[:-2] + ("xx" if token[-2:] != "xx" else "yy")
    r = get_books(client, strategy="cursor", limit=1, cursor=bad)
    assert r.status_code == 400
    assert r.json["error"] == "bad_cursor"


def test_cursor_binds_sort(client):
    token = get_books(client, limit=1, sort="title").json["pagination"]["nextCursor"]
    r = get_books(client, limit=1, sort="-title", cursor=token)
    assert r.status_code == 400
    assert "sort/genre" in r.json["message"]


def test_cursor_binds_genre(client):
    token = get_books(client, limit=1, genre="technology").json["pagination"]["nextCursor"]
    r = get_books(client, limit=1, genre="literature", cursor=token)
    assert r.status_code == 400


def test_invalid_strategy(client):
    assert get_books(client, strategy="page").status_code == 400


def test_invalid_sort_and_duplicate_keys(client):
    for invalid in ("price", "id,id", "title,-title", "", "title,,id", "title,id,created_at,-publication_year"):
        r = get_books(client, sort=invalid)
        assert r.status_code == 400, (invalid, r.json)


def test_invalid_limit_and_offset(client):
    for bad in (0, -1, "xyz"):
        assert get_books(client, limit=bad).status_code == 400
    for bad in (-1, "xyz"):
        assert get_books(client, strategy="offset", offset=bad).status_code == 400


def test_limit_capped_at_100(client):
    assert get_books(client, limit=99999).json["pagination"]["limit"] == 100


def test_offset_and_cursor_cannot_be_mixed(client):
    assert get_books(client, strategy="cursor", offset=0).status_code == 400
    assert get_books(client, strategy="offset", cursor="test").status_code == 400


def test_nonexistent_genre_empty_result(client):
    for strategy in ("offset", "cursor"):
        result = get_books(client, genre="unknown", strategy=strategy)
        assert result.status_code == 200
        assert result.json["data"] == []
        assert result.json["pagination"]["hasMore"] is False
