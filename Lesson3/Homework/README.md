# Bài tập Buổi 3 - API Design Principles & Best Practices

## 1. Refactor API giỏ hàng

### 1.1. API sau khi refactor

| API cũ | API đề xuất |
|---|---|
| `POST /addItemToCart?userId=42&productId=99&qty=2` | `POST /api/v1/users/42/cart/items` |
| `GET /getCartItems` | `GET /api/v1/users/42/cart/items` |
| `POST /removeItemFromCart` | `DELETE /api/v1/users/42/cart/items/99` |
| `GET /checkOut?userId=42` | `POST /api/v1/users/42/cart/checkout` |
| `POST /makeOrder?userId=42` | `POST /api/v1/users/42/orders` |
| `GET /getOrder?orderId=1001` | `GET /api/v1/orders/1001` |
| `GET /listUserOrders?userId=42` | `GET /api/v1/users/42/orders` |
| `GET /productsList.json?cat=phones` | `GET /api/v1/products?category=phones` |
| `POST /login?username=u&password=p` | `POST /api/v1/sessions` |
| `POST /signup` | `POST /api/v1/users` |

### 1.2. Refactor response lỗi

API cũ:

```json
{
  "status": "FAIL",
  "error_code": 5,
  "msg": "out of stock"
}
```

HTTP status:

```http
200 OK
```

API sau khi refactor:

```http
409 Conflict
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/problems/out-of-stock",
  "title": "Product out of stock",
  "detail": "Product 99 is currently out of stock.",
  "status": 409,
  "instance": "/api/v1/users/42/cart/items"
}
```
### 1.3. Nhận xét

- URL sử dụng danh từ thay vì động từ.
- HTTP method được sử dụng đúng mục đích.
- Path dùng lowercase, collection dùng số nhiều.
- ID được đưa vào path khi dùng để định danh resource.
- Bỏ đuôi `.json`.
- Không truyền username/password trong query string.
- Bổ sung version prefix `/api/v1`.
- Không trả `200 OK` khi response thực tế là lỗi.

---

## 2. Review Spotify Web API

### 2.1. Tiêu chí 1 - Tài nguyên là danh từ

Một số endpoint:

```http
GET /v1/tracks/{id}
GET /v1/artists/{id}
GET /v1/artists/{id}/albums
GET /v1/playlists/{playlist_id}/items
POST /v1/me/playlists
```

Nhận xét:

- Các resource được biểu diễn bằng danh từ như `tracks`, `artists`, `albums`, `playlists`, `items`.
- Hành động được thể hiện bằng HTTP method như `GET`, `POST`.
- Không sử dụng endpoint dạng `/getTrack`, `/createPlaylist`.
- Quan hệ giữa các resource được thể hiện bằng nested path như:

```text
/artists/{id}/albums
/playlists/{playlist_id}/items
```

**Kết luận:** Spotify Web API tuân thủ tốt nguyên tắc sử dụng danh từ để biểu diễn resource.

### 2.2. Tiêu chí 2 - Naming nhất quán

Ví dụ:

```http
GET /v1/tracks/{id}
GET /v1/artists/{id}
GET /v1/artists/{id}/albums
GET /v1/playlists/{playlist_id}/items
GET /v1/me/top/{type}?time_range=short_term&limit=10&offset=0
```

Nhận xét:

- Path sử dụng lowercase nhất quán.
- Collection sử dụng dạng số nhiều: `tracks`, `artists`, `albums`, `playlists`, `items`.
- Query parameter nhiều từ sử dụng snake_case, ví dụ `time_range`.
- API sử dụng version prefix `/v1`.
- Tên endpoint ngắn, dễ đọc và dễ dự đoán.

**Kết luận:** Naming của Spotify Web API nhất quán và dễ hiểu.
