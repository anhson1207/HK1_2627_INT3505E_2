"""Kiểm thử trước và sau sunset không cần chỉnh giờ hệ thống."""

from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from app import app


class SunsetTests(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_before_sunset_returns_200_and_headers(self):
        before = datetime(2026, 11, 23, 12, 0, tzinfo=timezone.utc)
        with patch("sunset.now_utc", return_value=before):
            resp = self.client.get("/api/v1/users/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"id": 1, "full_name": "Nguyễn Văn A"})
        self.assertEqual(resp.headers["Sunset"], "Thu, 31 Dec 2026 23:59:59 GMT")
        self.assertEqual(resp.headers["Deprecation"], "true")
        self.assertEqual(
            resp.headers["Link"],
            '</api/v2/users>; rel="successor-version"',
        )

    def test_after_sunset_returns_410(self):
        after = datetime(2027, 1, 1, 0, 0, tzinfo=timezone.utc)
        with patch("sunset.now_utc", return_value=after):
            resp = self.client.get("/api/v1/users/1")
        self.assertEqual(resp.status_code, 410)
        self.assertEqual(resp.json["error"], "gone")
        self.assertEqual(resp.json["sunset"], "Thu, 31 Dec 2026 23:59:59 GMT")
        self.assertEqual(resp.json["use_instead"], "/api/v2/users")

    def test_request_logs_warning_before_sunset(self):
        before = datetime(2026, 11, 23, 12, 0, tzinfo=timezone.utc)
        with patch("sunset.now_utc", return_value=before):
            with self.assertLogs("sunset", level="WARNING") as logged:
                self.client.get("/api/v1/users/1")
        self.assertIn("deprecated_call /api/v1/users/1", logged.output[0])

    def test_request_logs_warning_after_sunset(self):
        after = datetime(2027, 1, 1, 0, 0, tzinfo=timezone.utc)
        with patch("sunset.now_utc", return_value=after):
            with self.assertLogs("sunset", level="WARNING") as logged:
                self.client.get("/api/v1/users/1")
        self.assertIn("deprecated_call /api/v1/users/1", logged.output[0])

    def test_v2_remains_available(self):
        resp = self.client.get("/api/v2/users/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["first_name"], "Văn A")
        self.assertEqual(resp.json["last_name"], "Nguyễn")

    def test_v2_link_target_exists(self):
        resp = self.client.get("/api/v2/users")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)
