
from locust import HttpUser, task, between
import random
import uuid


class BooksUser(HttpUser):
    wait_time = between(1, 3)

    # 1. Xem danh sách sách
    @task(3)
    def list_books(self):
        self.client.get(
            "/books",
            name="GET /books"
        )

    # 2. Tìm sách theo năm xuất bản
    def search_by_year(self, year):
        with self.client.get(
            "/books",
            params={"year": year},
            name="GET /books?year",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Unexpected HTTP {response.status_code}"
                )

            elif random.random() < 0.01:
                response.failure(
                    "SIMULATED_500: intentional 1% failure"
                )

            else:
                response.success()

    @task(2)
    def search_books(self):
        year = random.choice([2017, 2021, 2024])
        self.search_by_year(year)

    # 3. Tạo sách và xoá sau khi kiểm tra
    @task(1)
    def create_book(self):
        payload = {
            "title": f"Locust-{uuid.uuid4().hex}",
            "author": "Load Test",
            "year": 2024
        }

        with self.client.post(
            "/books",
            json=payload,
            name="POST /books",
            catch_response=True
        ) as response:

            if response.status_code != 201:
                response.failure(
                    f"Unexpected HTTP {response.status_code}"
                )
                return

            try:
                book_id = response.json()["id"]
            except (ValueError, KeyError, TypeError):
                response.failure("Missing book ID")
                return

        # Dọn dữ liệu thử nghiệm
        with self.client.delete(
            f"/books/{book_id}",
            name="DELETE /books/{id}",
            catch_response=True
        ) as response:
            if response.status_code != 204:
                response.failure(
                    f"Unexpected HTTP {response.status_code}"
                )
