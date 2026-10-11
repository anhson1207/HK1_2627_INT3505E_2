# Hai quyết định thiết kế khó nhất

## 1. Sử dụng PATCH thay vì PUT để cập nhật Task

API sử dụng `PATCH /v1/tasks/{taskId}` vì yêu cầu cập nhật chỉ một phần dữ liệu của Task, ví dụ chỉ đổi `status` hoặc `dueDate`.

Nếu dùng `PUT`, client thường phải gửi lại toàn bộ representation của Task. Điều này không cần thiết khi chỉ muốn sửa một vài field và có thể làm tăng nguy cơ ghi đè dữ liệu không mong muốn.

Vì vậy, `PATCH` phù hợp hơn với bài toán cập nhật từng phần của Task

## 2. Lựa chọn status code phù hợp cho từng trường hợp

API không trả `200 OK` cho mọi tình huống mà sử dụng status code theo đúng ý nghĩa của từng thao tác:

- `200 OK`: lấy dữ liệu hoặc cập nhật Task thành công.
- `201 Created`: tạo Task mới thành công.
- `204 No Content`: xóa Task thành công và không cần response body.
- `404 Not Found`: không tìm thấy Task theo `taskId`.
- `422 Unprocessable Entity`: dữ liệu gửi lên đúng định dạng nhưng không hợp lệ theo validation.

Cách thiết kế này giúp client hiểu kết quả request ngay từ HTTP status code, đồng thời làm API rõ ràng và dễ kiểm thử hơn.
