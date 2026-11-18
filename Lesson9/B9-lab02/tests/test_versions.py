import unittest

from app import app


class HeaderVersioningTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_default_is_v2(self):
        response = self.client.get("/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-API-Version-Served"], "2")
        self.assertEqual(response.json, {
            "id": 1,
            "first_name": "Văn",
            "last_name": "Nguyễn",
            "email": "a@vnu.vn",
        })

    def test_explicit_v1_uses_full_name(self):
        response = self.client.get("/users/1", headers={"X-API-Version": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-API-Version-Served"], "1")
        self.assertEqual(response.json, {"id": 1, "full_name": "Văn Nguyễn"})

    def test_explicit_v2(self):
        response = self.client.get("/users/2", headers={"X-API-Version": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-API-Version-Served"], "2")
        self.assertEqual(response.json["first_name"], "Trang")
        self.assertEqual(response.json["last_name"], "Trần")
        self.assertNotIn("full_name", response.json)

    def test_date_version(self):
        response = self.client.get("/users/1", headers={"X-API-Version": "2024-06-20"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-API-Version-Served"], "2024-06-20")
        self.assertEqual(response.json["first_name"], "Văn")

    def test_unsupported_version_returns_400(self):
        response = self.client.get("/users/1", headers={"X-API-Version": "99"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "unsupported version"})

    def test_unknown_user_returns_404(self):
        response = self.client.get("/users/9999", headers={"X-API-Version": "1"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "not found"})
        self.assertEqual(response.headers["X-API-Version-Served"], "1")

    def test_one_url_only(self):
        paths = {rule.rule for rule in app.url_map.iter_rules() if rule.endpoint != "static"}
        self.assertEqual(paths, {"/users/<int:uid>"})


if __name__ == "__main__":
    unittest.main()
