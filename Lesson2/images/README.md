# Images

## Bài 1

<p align="center">
  <img src="./1_1.png" alt="Bài 1 - Kiểm thử GET và POST cho API sách">
  <br>
  <em>Kiểm thử <code>GET /books</code> để lấy danh sách sách, <code>POST /books</code> để tạo sách mới và trường hợp thiếu dữ liệu trả về mã 422.</em>
</p>

<p align="center">
  <img src="./1_2.png" alt="Bài 1 - Kiểm tra các mã trạng thái khi tạo sách">
  <br>
  <em>Kiểm tra các phản hồi của <code>POST /books</code>: tạo thành công với mã 201, thiếu trường bắt buộc với mã 422 và thiếu Content-Type JSON với mã 415.</em>
</p>

## Bài 2

<p align="center">
  <img src="./2.png" alt="Bài 2 - Tạo và xóa sách">
  <br>
  <em>Tạo dữ liệu sách để kiểm thử và gửi <code>DELETE /books/1</code>, nhận mã 204 No Content khi xóa thành công.</em>
</p>

## Bài 3

<p align="center">
  <img src="./3_1.png" alt="Bài 3 - Kiểm thử phân trang danh sách sách">
  <br>
  <em>Tạo dữ liệu mẫu và gọi <code>GET /books</code> để kiểm tra kết quả phân trang cùng các liên kết HATEOAS.</em>
</p>

<p align="center">
  <img src="./3_2.png" alt="Bài 3 - Lọc sách theo tác giả">
  <br>
  <em>Gọi <code>GET /books?author=Orwell</code> để lọc danh sách sách theo tên tác giả.</em>
</p>

<p align="center">
  <img src="./3_3.png" alt="Bài 3 - Kiểm tra phản hồi JSON nâng cao">
  <br>
  <em>Yêu cầu phản hồi JSON và kiểm tra cấu trúc kết quả gồm dữ liệu sách, thông tin phân trang và các liên kết HATEOAS.</em>
</p>
