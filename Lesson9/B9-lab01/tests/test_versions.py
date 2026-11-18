import unittest
from app import app


class UserVersioningTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_v1_full_name(self):
        response = self.client.get("/api/v1/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "id": 1, "full_name": "Văn Nguyễn", "email": "a@vnu.vn"
        })

    def test_v2_first_and_last_name(self):
        response = self.client.get("/api/v2/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "id": 1, "first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"
        })

    def test_v1_user_2(self):
        response = self.client.get("/api/v1/users/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["full_name"], "Trang Trần")

    def test_v2_user_2(self):
        response = self.client.get("/api/v2/users/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["first_name"], "Trang")

    def test_v1_not_found(self):
        response = self.client.get("/api/v1/users/9999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "nf"})

    def test_v2_not_found(self):
        response = self.client.get("/api/v2/users/9999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "nf"})


if __name__ == "__main__":
    unittest.main()
