from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Author
from routes.utils import body, fail, simple_page

bp = Blueprint("authors", __name__)


@bp.get("/authors")
def list_authors():
    return simple_page(db.session.query(Author), Author)


@bp.post("/authors")
def create_author():
    payload, err = body("create_author.schema.json")
    if err:
        return err
    author = Author(name=payload["name"], bio=payload.get("bio"))
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201


@bp.get("/authors/<int:author_id>/books")
def author_books(author_id):
    author = db.session.get(Author, author_id)
    if not author:
        return fail("author_not_found", "Author not found", 404)
    return jsonify({"data": [{"id": link.book.id, "title": link.book.title, "role": link.role}
                             for link in author.book_links]})
