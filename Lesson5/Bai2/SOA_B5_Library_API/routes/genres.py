from flask import Blueprint, jsonify
from extensions import db
from models import Genre
bp = Blueprint("genres", __name__)


@bp.get("/genres")
def list_genres():
    return jsonify({"data": [g.to_dict() for g in db.session.query(Genre).order_by(Genre.id).limit(100).all()]})
