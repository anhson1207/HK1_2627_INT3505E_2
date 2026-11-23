import unittest
from unittest.mock import patch

import gateway
from app import app


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post(self, account_id, cohort=None):
        headers = {"X-Cohort": cohort} if cohort else None
        return self.client.post("/orders", json={"account_id": account_id}, headers=headers)

    def test_beta_cohort_uses_v2(self):
        response = self.post("acct_01", "beta")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["X-Order-Handler"], "v2")
        self.assertEqual(response.json["schema_version"], "2")

    def test_internal_cohort_uses_v2(self):
        response = self.post("acct_01", "INTERNAL")
        self.assertEqual(response.headers["X-Order-Handler"], "v2")

    def test_allowlist_account_42_uses_v2(self):
        response = self.post("acct_42")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["X-Order-Handler"], "v2")

    def test_allowlist_account_99_uses_v2(self):
        response = self.post("acct_99")
        self.assertEqual(response.headers["X-Order-Handler"], "v2")

    def test_ordinary_account_uses_v1_with_5_percent(self):
        # md5('acct_01') % 100 == 46, so it is outside the first 5 buckets.
        with patch.object(gateway, "V2_PERCENT", 5):
            response = self.post("acct_01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Order-Handler"], "v1")
        self.assertIn("order_id", response.json)

    def test_ordinary_account_inside_5_percent_uses_v2(self):
        # md5('acct_03') % 100 == 2, so it belongs to the v2 canary.
        with patch.object(gateway, "V2_PERCENT", 5):
            response = self.post("acct_03")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["X-Order-Handler"], "v2")

    def test_rollout_100_percent_moves_ordinary_accounts_to_v2(self):
        with patch.object(gateway, "V2_PERCENT", 100):
            response = self.post("acct_01")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["X-Order-Handler"], "v2")

    def test_rollout_zero_still_preserves_priority_overrides(self):
        with patch.object(gateway, "V2_PERCENT", 0):
            self.assertEqual(self.post("acct_01").headers["X-Order-Handler"], "v1")
            self.assertEqual(self.post("acct_42").headers["X-Order-Handler"], "v2")
            self.assertEqual(self.post("acct_01", "beta").headers["X-Order-Handler"], "v2")

    def test_invalid_body_returns_400(self):
        response = self.client.post("/orders", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
