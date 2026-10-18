from datetime import datetime, timezone
from flask import Blueprint, jsonify
from sqlalchemy import select
from extensions import db
from models import BookCopy, Loan, Member, utc_now
from routes.utils import body, fail

bp = Blueprint("loans", __name__)


def parse_utc(raw):
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timezone is required")
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


@bp.post("/loans")
def create_loan():
    payload, err = body("create_loan.schema.json")
    if err:
        return err
    member = db.session.get(Member, payload["memberId"])
    copy = db.session.get(BookCopy, payload["copyId"])
    if not member or not copy:
        return fail("not_found", "Member or copy not found", 404)
    if not copy.is_available():
        return fail("copy_unavailable", "This copy is on loan or in maintenance", 409)
    try:
        due = parse_utc(payload["dueAt"])
    except ValueError:
        return fail("bad_date", "dueAt must include timezone and be an ISO 8601 date-time")
    now = utc_now()
    if due <= now:
        return fail("bad_date", "dueAt must be in the future")
    loan = Loan(member_id=member.id, copy_id=copy.id, borrowed_at=now, due_at=due)
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201


@bp.patch("/loans/<int:loan_id>")
def return_loan(loan_id):
    loan = db.session.get(Loan, loan_id)
    if not loan:
        return fail("loan_not_found", "Loan not found", 404)
    payload, err = body("return_loan.schema.json")
    if err:
        return err
    if loan.returned_at:
        return fail("already_returned", "Loan has already been returned", 409)
    loan.returned_at = utc_now()
    db.session.commit()
    return jsonify(loan.to_dict())
