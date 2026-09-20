# Audit GitHub REST API

**1. Endpoint: Lấy thông tin một người dùng**
* **Method:** GET
* **URL:** `/users/{username}`
* **Status codes:** 200 OK (Thành công), 404 Not Found (Không tìm thấy user).
* **Headers:** `Accept: application/vnd.github+json`, `Authorization: Bearer <token>`
* **Đánh giá RESTful:** **Có.** Thỏa mãn tính chất Safe và Idempotent của GET. URI chứa danh từ số nhiều `/users/` định danh chính xác resource.

**2. Endpoint: Tạo Repository mới cho User xác thực**
* **Method:** POST
* **URL:** `/user/repos`
* **Status codes:** 201 Created (Tạo thành công), 401 Unauthorized, 422 Unprocessable Entity (Gửi thiếu field/sai validaton).
* **Headers:** `Content-Type: application/json`, `Location` (trả về URL của repo mới).
* **Đánh giá RESTful:** **Có.** Dùng POST để tạo mới resource. API trả về mã 201 Created kèm header Location chứa URL trỏ thẳng tới tài nguyên vừa tạo, tuân thủ chặt chẽ Uniform Interface.

**3. Endpoint: Cập nhật thông tin Repository**
* **Method:** PATCH
* **URL:** `/repos/{owner}/{repo}`
* **Status codes:** 200 OK, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity.
* **Headers:** `Content-Type: application/json`
* **Đánh giá RESTful:** **Có.** Dùng PATCH cho việc sửa đổi một phần dữ liệu (như đổi tên repo hoặc chỉnh sửa phần mô tả) mà không cần truyền toàn bộ payload như PUT.

**4. Endpoint: Xóa Repository**
* **Method:** DELETE
* **URL:** `/repos/{owner}/{repo}`
* **Status codes:** 204 No Content (Xóa thành công), 403 Forbidden, 404 Not Found.
* **Headers:** `Authorization: Bearer <token>`
* **Đánh giá RESTful:** **Có.** Đây là Idempotent method. Trả về đúng trạng thái 204 No Content do sau khi xóa thì không có body dữ liệu trả về.

**5. Endpoint: Khóa một Issue**
* **Method:** PUT
* **URL:** `/repos/{owner}/{repo}/issues/{issue_number}/lock`
* **Status codes:** 204 No Content, 403 Forbidden, 404 Not Found.
* **Headers:** `Content-Type: application/json`
* **Đánh giá RESTful:** **Có Vi Phạm (Dạng RESTful-ish).** Mặc dù vẫn quản lý state, việc chèn thêm động từ "lock" làm mất tính chất danh từ (chỉ resource) của URI. Tuy nhiên, cách thiết kế này khá phổ biến để quản lý sub-state trong hệ thống phức tạp.