from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v2", __name__)


@bp.get("/users/<int:uid>")
def get(uid):
    user = get_user(uid)
    if not user:
        return {"error": "nf"}, 404

    return {
        "id": uid,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }
