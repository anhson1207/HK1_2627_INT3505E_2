# SOA Buổi 7 – Backend Service

API quản lý sản phẩm và đơn hàng sử dụng Flask,
SQLAlchemy và PostgreSQL.

## Chức năng
- Product: CRUD, reserve, soft delete.
- Order: Quản lý đơn hàng và OrderItem.
- Database: SQLAlchemy, Flask-Migrate.
- Docker: PostgreSQL, Gunicorn, health checks.

## Chạy Docker
docker compose up --build -d

## Kiểm thử
pip install -e '.[test]'
python -m pytest -v

## API
- /api/v1/products
- /api/v1/products/{id}
- /api/v1/products/{id}/reserve
- /api/v1/orders
- /api/v1/orders/{id}
- /api/v1/orders/{id}/items
- /healthz
- /ready
