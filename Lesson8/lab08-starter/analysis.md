# Lab 04 – Phân tích kết quả Load Test

| Kịch bản | Users | p95 | RPS | Tỷ lệ lỗi |
|---|---:|---:|---:|---:|
| A | 10 | 10 ms | 5,82 | 1,73% |
| B | 50 | 9 ms | 27,37 | 0,31% |
| C | 200 | 28 ms | 113,82 | 0,38% |

### 1. Kịch bản nào có p95 cao nhất? Vì sao?

Kịch bản C có p95 cao nhất (28 ms). Khi 200 người dùng truy cập, nhiều request được xử lý cùng lúc nên thời gian phản hồi có xu hướng tăng. Tuy nhiên, độ trễ vẫn khá thấp.

### 2. Endpoint nào có tỷ lệ lỗi tăng?

Chỉ `GET /books?year` ghi nhận lỗi, lần lượt 3, 5 và 13 lỗi ở A, B, C. Số lỗi tăng nhưng tỷ lệ lỗi không tăng đều. Nguyên nhân là đoạn code giả lập xác suất lỗi 1% trong Locust, không phải lỗi HTTP 500 thực tế của API.

### 3. Kịch bản nào đạt SLO p95 dưới 300 ms?

Cả ba kịch bản đều đạt. Em đề xuất dùng kịch bản A (10 users, 30 giây) làm baseline cho CI vì chạy nhanh, ít tốn tài nguyên và đủ để phát hiện những thay đổi hiệu năng cơ bản.

### 4. Bonus – Nếu connection pool giới hạn 5 nhưng có 200 users?

Các request cần truy cập database có thể phải chờ kết nối, khiến p95 tăng hoặc xảy ra timeout. Để kiểm chứng, giới hạn pool còn 5 kết nối, chạy lại kịch bản C bằng Locust rồi so sánh p95, RPS, tỷ lệ lỗi và log backend với cấu hình ban đầu.