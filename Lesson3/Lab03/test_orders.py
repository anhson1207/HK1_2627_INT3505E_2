import unittest
from app import app


class TestOrdersAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_filter_and_sort(self):
        # Filter
        r1 = self.client.get("/orders?status=paid")
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(all(o["status"] == "paid" for o in r1.json["data"]))

        # Sort
        r2 = self.client.get("/orders?sort=-total")
        totals = [o["total"] for o in r2.json["data"]]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_cursor_pagination(self):
        r1 = self.client.get("/orders?limit=3")
        cursor = r1.json["pagination"]["next_cursor"]
        self.assertIsNotNone(cursor)

        r2 = self.client.get(f"/orders?limit=3&cursor={cursor}")
        ids1 = {o["id"] for o in r1.json["data"]}
        ids2 = {o["id"] for o in r2.json["data"]}
        self.assertTrue(ids1.isdisjoint(ids2))

    def test_sparse_fieldsets(self):
        resp = self.client.get("/orders?fields=id,total")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(set(resp.json["data"][0].keys()), {"id", "total"})

    def test_errors_rfc7807(self):
        # Invalid cursor
        r1 = self.client.get("/orders?cursor=bad_cursor")
        self.assertEqual(r1.status_code, 400)
        self.assertEqual(r1.headers.get("Content-Type"), "application/problem+json")

        # Unknown field / sort
        self.assertEqual(self.client.get("/orders?fields=id,xyz").status_code, 400)
        self.assertEqual(self.client.get("/orders?sort=xyz").status_code, 400)
        self.assertEqual(self.client.get("/orders/9999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
