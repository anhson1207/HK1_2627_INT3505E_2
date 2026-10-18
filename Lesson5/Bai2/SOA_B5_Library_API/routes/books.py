"""Bai 2: offset AND signed composite-key cursor on the same list_books route."""
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request, url_for
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from extensions import db
from models import Author, Book, BookAuthor, BookCopy, Genre, Loan
from routes.utils import body, bounded_int, fail

bp = Blueprint("books", __name__)
SORT_FIELDS = {
    "id": Book.id,
    "title": Book.title,
    "publication_year": Book.publication_year,
    "created_at": Book.created_at,
}


def book_load():
    # Avoid N+1 while embedding authors, copies and their borrowing states.
    return (
        selectinload(Book.genre),
        selectinload(Book.author_links).selectinload(BookAuthor.author),
        selectinload(Book.copies).selectinload(BookCopy.loans),
    )


def parse_sort(raw):
    parts = raw.split(",")
    if not 1 <= len(parts) <= 3:
        return None, "sort must contain 1-3 keys"
    spec = []
    seen = set()
    for token in parts:
        token = token.strip()
        if not token or token in ("-", "+"):
            return None, "empty sort key"
        desc = token.startswith("-")
        name = token[1:] if desc else token
        if name not in SORT_FIELDS:
            return None, f"unknown sort key: {name}"
        if name in seen:
            return None, f"duplicate sort key: {name}"
        seen.add(name)
        spec.append((name, desc))
    if "id" not in seen:
        spec.append(("id", False))  # unique deterministic tie-breaker
    return spec, None


def signed_serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="library-books-cursor-v1")


def encode_cursor(item, raw_sort, genre_slug, spec):
    values = []
    for name, _ in spec:
        v = getattr(item, name)
        values.append(v.isoformat() if isinstance(v, datetime) else v)
    return signed_serializer().dumps({
        "version": 1, "sort": raw_sort, "genre": genre_slug, "values": values
    })


def apply_cursor(query, token, raw_sort, genre_slug, spec):
    try:
        c = signed_serializer().loads(token)
    except (BadSignature, ValueError, TypeError):
        return None, "invalid or tampered cursor"
    if not isinstance(c, dict) or c.get("version") != 1:
        return None, "unsupported cursor version"
    if c.get("sort") != raw_sort or c.get("genre") != genre_slug:
        return None, "cursor does not match current sort/genre"
    raw_values = c.get("values")
    if not isinstance(raw_values, list) or len(raw_values) != len(spec):
        return None, "invalid cursor shape"
    values = []
    try:
        for (name, _), value in zip(spec, raw_values):
            if name in ("id", "publication_year"):
                if type(value) is not int:
                    raise ValueError("bad number")
            elif name == "created_at":
                if not isinstance(value, str):
                    raise ValueError("bad timestamp")
                value = datetime.fromisoformat(value)
            elif not isinstance(value, str):
                raise ValueError("bad string")
            values.append(value)
    except (ValueError, TypeError, OverflowError):
        return None, "invalid cursor values"

    # Lexicographic keyset seek, including mixed ASC/DESC sort directions:
    # (a > va) OR (a = va AND b < vb) OR (... AND id > vid).
    branches = []
    for i, ((name, desc), value) in enumerate(zip(spec, values)):
        prefix = [SORT_FIELDS[n] == v for (n, _), v in zip(spec[:i], values[:i])]
        comparison = SORT_FIELDS[name] < value if desc else SORT_FIELDS[name] > value
        branches.append(and_(*prefix, comparison))
    return query.where(or_(*branches)), None


@bp.get("/books")
def list_books():
    """GET ?strategy=offset|cursor&genre=technology&sort=-publication_year,title."""
    strategy = request.args.get("strategy", "cursor")
    if strategy not in ("offset", "cursor"):
        return fail("bad_strategy", "strategy must be offset or cursor")
    limit, err = bounded_int(request.args.get("limit"), "limit")
    if err:
        return err
    raw_sort = request.args.get("sort", "-id")
    spec, why = parse_sort(raw_sort)
    if why:
        return fail("bad_sort", why)
    genre_slug = request.args.get("genre") or None
    query = select(Book).options(*book_load())
    if genre_slug:
        query = query.join(Genre, Book.genre_id == Genre.id).where(Genre.slug == genre_slug)
    query = query.order_by(*[
        SORT_FIELDS[name].desc() if desc else SORT_FIELDS[name].asc()
        for name, desc in spec
    ])

    if strategy == "offset":
        if "cursor" in request.args:
            return fail("bad_parameter", "cursor only applies to cursor strategy")
        offset, err = bounded_int(request.args.get("offset"), "offset", default=0, minimum=0, maximum=10**8)
        if err:
            return err
        count_q = select(db.func.count(Book.id))
        if genre_slug:
            count_q = count_q.join(Genre, Book.genre_id == Genre.id).where(Genre.slug == genre_slug)
        total = db.session.scalar(count_q)
        rows = db.session.scalars(query.offset(offset).limit(limit)).all()
        return jsonify({"data": [b.to_dict() for b in rows], "pagination": {
            "strategy": "offset", "offset": offset, "limit": limit, "total": total,
            "hasMore": offset + len(rows) < total,
        }})

    if "offset" in request.args:
        return fail("bad_parameter", "offset only applies to offset strategy")
    token = request.args.get("cursor")
    if token:
        query, why = apply_cursor(query, token, raw_sort, genre_slug, spec)
        if why:
            return fail("bad_cursor", why)
    rows = db.session.scalars(query.limit(limit + 1)).all()
    more = len(rows) > limit
    page = rows[:limit]
    next_cursor = encode_cursor(page[-1], raw_sort, genre_slug, spec) if more and page else None
    return jsonify({"data": [b.to_dict() for b in page], "pagination": {
        "strategy": "cursor", "limit": limit, "hasMore": more, "nextCursor": next_cursor,
    }})


@bp.post("/books")
def create_book():
    payload, err = body("create_book.schema.json")
    if err:
        return err
    genre = db.session.get(Genre, payload["genreId"])
    if not genre:
        return fail("genre_not_found", "genreId does not exist", 404)
    b = Book(title=payload["title"], isbn=payload["isbn"],
             publication_year=payload["publicationYear"],
             description=payload.get("description"), genre_id=genre.id)
    db.session.add(b)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("duplicate_isbn", "ISBN is already registered", 409)
    response = jsonify(b.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("books.get_book", book_id=b.id)
    return response


@bp.get("/books/<int:book_id>")
def get_book(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    return jsonify(b.to_dict())


@bp.patch("/books/<int:book_id>")
def patch_book(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    payload, err = body("patch_book.schema.json")
    if err:
        return err
    if "genreId" in payload:
        if not db.session.get(Genre, payload["genreId"]):
            return fail("genre_not_found", "genreId does not exist", 404)
        b.genre_id = payload["genreId"]
    for key, attr in (("title", "title"), ("isbn", "isbn"),
                      ("publicationYear", "publication_year"), ("description", "description")):
        if key in payload:
            setattr(b, attr, payload[key])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("duplicate_isbn", "ISBN already registered", 409)
    return jsonify(b.to_dict())


@bp.delete("/books/<int:book_id>")
def delete_book(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    if db.session.scalar(select(db.func.count(Loan.id)).join(BookCopy).where(BookCopy.book_id == book_id)):
        return fail("has_loan_history", "Cannot delete books with loan history", 409)
    db.session.delete(b)
    db.session.commit()
    return "", 204


@bp.get("/books/<int:book_id>/authors")
def book_authors(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    return jsonify({"data": [{"id": link.author.id, "name": link.author.name, "role": link.role}
                             for link in b.author_links]})


@bp.post("/books/<int:book_id>/authors")
def attach_author(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    payload, err = body("attach_author.schema.json")
    if err:
        return err
    if not db.session.get(Author, payload["authorId"]):
        return fail("author_not_found", "Author not found", 404)
    if db.session.get(BookAuthor, (book_id, payload["authorId"])):
        return fail("duplicate_link", "Author already linked to book", 409)
    link = BookAuthor(book_id=book_id, author_id=payload["authorId"], role=payload.get("role", "co"))
    db.session.add(link)
    db.session.commit()
    return jsonify({"bookId": book_id, "authorId": link.author_id, "role": link.role}), 201


@bp.delete("/books/<int:book_id>/authors/<int:author_id>")
def detach_author(book_id, author_id):
    link = db.session.get(BookAuthor, (book_id, author_id))
    if not link:
        return fail("link_not_found", "Author/book relation not found", 404)
    db.session.delete(link)
    db.session.commit()
    return "", 204


@bp.get("/books/<int:book_id>/copies")
def book_copies(book_id):
    b = db.session.get(Book, book_id)
    if not b:
        return fail("book_not_found", "Book not found", 404)
    return jsonify({"data": [c.to_dict() for c in b.copies]})


@bp.post("/books/<int:book_id>/copies")
def create_copy(book_id):
    if not db.session.get(Book, book_id):
        return fail("book_not_found", "Book not found", 404)
    payload, err = body("create_copy.schema.json")
    if err:
        return err
    c = BookCopy(book_id=book_id, barcode=payload["barcode"], condition=payload.get("condition", "available"))
    db.session.add(c)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("duplicate_barcode", "Barcode already registered", 409)
    return jsonify(c.to_dict()), 201
