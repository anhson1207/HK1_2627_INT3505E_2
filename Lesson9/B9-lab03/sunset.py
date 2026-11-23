"""Decorator cảnh báo và sunset API v1 (Practice 3, SOA B9)."""

from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps
import logging

from flask import jsonify, request

log = logging.getLogger("sunset")


def now_utc():
    """Tách riêng thời gian hiện tại để test được trước/sau sunset."""
    return datetime.now(timezone.utc)


def http_date(dt):
    """Chuyển UTC datetime thành HTTP-date, ví dụ 'Thu, 31 Dec 2026 ... GMT'."""
    return format_datetime(dt.astimezone(timezone.utc), usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    """Trước sunset: 200 + headers; từ sunset: 410 Gone."""
    if sunset_date.tzinfo is None or sunset_date.utcoffset() is None:
        raise ValueError("sunset_date must include timezone information")

    def decorate(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            # Ghi lại mọi lần client gọi endpoint đã deprecated.
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)

            if now_utc() >= sunset_date:
                return jsonify({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement,
                }), 410

            result = fn(*args, **kwargs)
            body, status = result if isinstance(result, tuple) else (result, 200)
            response = jsonify(body)
            response.status_code = status
            response.headers["Sunset"] = http_date(sunset_date)
            response.headers["Deprecation"] = "true"
            if replacement:
                response.headers["Link"] = (
                    f'<{replacement}>; rel="successor-version"'
                )
            return response

        return inner

    return decorate
