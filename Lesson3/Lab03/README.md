# Orders API với Cursor Pagination (Lab 3)

## 1. Cấu trúc Endpoint

- `GET /orders`: Lấy danh sách đơn hàng
  - `cursor`: Token phân trang base64
  - `limit`: Số bản ghi mỗi trang (mặc định 10, tối đa 100)
  - `status`: Lọc theo trạng thái (`paid`, `pending`, `shipped`, `cancelled`)
  - `customer_id`: Lọc theo ID khách hàng
  - `sort`: Sắp xếp (`total`, `-total`, `created_at`, ...)
  - `fields`: Chọn trường trả về (`id,total`)
- `GET /orders/<id>`: Chi tiết đơn hàng

## 2. Kiểm thử cURL

```bash
# 1. Filter theo status
curl 'localhost:5000/orders?status=paid'

# 2. Phân trang cursor
curl 'localhost:5000/orders?limit=5'
curl 'localhost:5000/orders?limit=5&cursor=<NEXT_CURSOR>'

# 3. Sparse fieldsets
curl 'localhost:5000/orders?fields=id,total'

# 4. Cursor hỏng trả 400 (RFC 7807 problem+json)
curl 'localhost:5000/orders?cursor=invalid_cursor'
```

## 3. Chạy Server & Test

```bash
# Chạy app
python app.py

# Chạy unit test
python test_orders.py
```
