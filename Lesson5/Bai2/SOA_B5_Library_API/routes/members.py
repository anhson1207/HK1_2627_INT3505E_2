from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Loan, Member
from routes.utils import body, fail, simple_page

bp = Blueprint("members", __name__)


@bp.get("/members")
def list_members():
    return simple_page(db.session.query(Member), Member)


@bp.post("/members")
def create_member():
    payload, err = body("create_member.schema.json")
    if err:
        return err
    m = Member(full_name=payload["fullName"], email=payload["email"])
    db.session.add(m)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fail("duplicate_email", "Email already exists", 409)
    return jsonify(m.to_dict()), 201


@bp.get("/members/<int:member_id>")
def get_member(member_id):
    m = db.session.get(Member, member_id)
    if not m:
        return fail("member_not_found", "Member not found", 404)
    return jsonify(m.to_dict())


@bp.get("/members/<int:member_id>/loans")
def member_loans(member_id):
    if not db.session.get(Member, member_id):
        return fail("member_not_found", "Member not found", 404)
    q = db.session.query(Loan).filter(Loan.member_id == member_id)
    return simple_page(q, Loan)
