"""Route orders to v1 or v2 using cohort, allow-list, then a hash bucket."""
import hashlib
import logging
import os

from flask import request
from handlers import v1_create_order, v2_create_order

V2_PERCENT = int(os.getenv("V2_PERCENT", "5"))
if not 0 <= V2_PERCENT <= 100:
    raise ValueError("V2_PERCENT must be between 0 and 100")

V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}
log = logging.getLogger("gateway")


def route_to_v2(body):
    # 1. Explicit cohort has highest priority.
    cohort = request.headers.get("X-Cohort", "").lower()
    if cohort in V2_COHORTS:
        return True

    # 2. Allow-listed accounts always use v2.
    account = body.get("account_id", "")
    if account in V2_FORCE_ACCOUNTS:
        return True

    # 3. Stable percentage bucket by account_id.
    if V2_PERCENT == 0:
        return False
    bucket = int(hashlib.md5(account.encode()).hexdigest(), 16) % 100
    return bucket < V2_PERCENT


def dispatch(body):
    if route_to_v2(body):
        log.info("Order routed to v2: %s", body["account_id"])
        return "v2", v2_create_order(body)
    log.info("Order routed to v1: %s", body["account_id"])
    return "v1", v1_create_order(body)
