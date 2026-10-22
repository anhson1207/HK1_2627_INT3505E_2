# Security Audit – Social Network API

**Phạm vi:** `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`.

| STT | Rủi ro bảo mật | Cách xử lý |
|---|---|---|
| 1 | **Brute force / dò tài khoản** ở `/auth/login`: thử mật khẩu liên tục hoặc phân biệt email tồn tại qua thông báo lỗi. | Giới hạn số lần đăng nhập; trả lỗi chung `invalid_credentials`. |
| 2 | **Lộ mật khẩu khi database bị truy cập trái phép** nếu lưu plaintext hoặc hash trực tiếp bằng MD5/SHA-256. | Hash mật khẩu bằng Argon2id hoặc bcrypt có salt và cost phù hợp. |
| 3 | **Lộ JWT secret** do hard-code hoặc commit file `.env` lên GitHub. | Đọc secret từ biến môi trường/secret manager; quét secret và thay khóa nếu bị lộ. |
| 4 | **Lộ password/token qua URL hoặc log** của `/auth/login`, `/auth/refresh`. | Truyền qua HTTPS; không đưa secret vào query string; che thông tin nhạy cảm trong log. |
| 5 | **Xác thực JWT sai**: chấp nhận `alg=none`, bỏ qua chữ ký hoặc không kiểm `exp`, `iss`, `aud` theo cấu hình. | Giới hạn thuật toán cho phép; kiểm chữ ký, loại token, thời hạn và các claims bắt buộc. |
| 6 | **Refresh token bị đánh cắp hoặc dùng lại** tại `/auth/refresh` để lấy access token mới. | Rotate refresh token sau mỗi lần dùng; phát hiện reuse và thu hồi phiên/token family liên quan. |
| 7 | **Access token bị lộ vẫn dùng được quá lâu**, kể cả sau logout nếu không có cơ chế thu hồi. | Đặt thời hạn ngắn (ví dụ 15 phút); kiểm trạng thái revoke/phiên khi cần. |
| 8 | **Thiếu kiểm tra scope** ở `GET /posts/{id}`: token hợp lệ nhưng không có `posts:read` vẫn đọc được bài. | Kiểm `posts:read` trước khi trả dữ liệu; thiếu quyền trả `403`. |
| 9 | **BOLA** ở `GET /posts/{id}`: đổi ID để đọc bài `private` của người khác. | Kiểm `visibility` và `author_id` so với user trong token; không đủ quyền trả `403`. |
| 10 | **Lộ thuộc tính nội bộ của bài viết** do trả nguyên bản ghi database. | Chỉ trả các field đã định nghĩa trong response schema; không trả dữ liệu nội bộ. |

**Quy ước phản hồi:** `401` khi thiếu/sai/hết hạn token; `403` khi thiếu scope hoặc không có quyền với bài viết; `404` khi bài viết không tồn tại; `429` khi vượt giới hạn request.

