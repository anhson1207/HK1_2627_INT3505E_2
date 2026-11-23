"""Minimal in-memory order handlers for the routing exercise (no database)."""
from uuid import uuid4


def v1_create_order(body):
    return {
        "order_id": str(uuid4()),
        "account_id": body["account_id"],
        "status": "created",
    }


def v2_create_order(body):
    return {
        "id": str(uuid4()),
        "account_id": body["account_id"],
        "status": "created",
        "currency": "VND",
        "schema_version": "2",
    }
