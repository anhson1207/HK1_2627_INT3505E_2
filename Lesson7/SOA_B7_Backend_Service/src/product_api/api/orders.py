from flask import Blueprint, jsonify
from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from ..errors import Conflict, NotFound
from ..extensions import db
from ..models import Order, OrderItem, Product
from ..schemas import OrderIn, OrderOut, OrderItemOut
from .common import pagination, require_json_object

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def with_items():
    return selectinload(Order.items).selectinload(OrderItem.product)


@orders_bp.get("")
def list_orders():
    page, size = pagination()
    orders = db.session.scalars(
        select(Order).options(with_items()).order_by(Order.id)
        .offset((page - 1) * size).limit(size)
    ).all()
    total = db.session.scalar(select(func.count()).select_from(Order))
    return jsonify({
        "items": OrderOut(many=True).dump(orders),
        "page": page, "size": size, "total": total,
    }), 200


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = db.session.scalar(
        select(Order).where(Order.id == order_id).options(with_items())
    )
    if order is None:
        raise NotFound("Order not found")
    return jsonify(OrderOut().dump(order)), 200


@orders_bp.get("/<int:order_id>/items")
def list_order_items(order_id):
    order = db.session.scalar(
        select(Order).where(Order.id == order_id).options(with_items())
    )
    if order is None:
        raise NotFound("Order not found")
    return jsonify({"items": OrderItemOut(many=True).dump(order.items)}), 200


@orders_bp.post("")
def create_order():
    lines = OrderIn().load(require_json_object())["items"]
    ids = [line["product_id"] for line in lines]
    found = db.session.scalars(select(Product).where(Product.id.in_(ids))).all()
    product_map = {product.id: product for product in found if not product.archived}
    if any(product_id not in product_map for product_id in ids):
        raise NotFound("One or more products do not exist or are archived")

    order = Order(status="placed", total_cents=0)
    total = 0
    try:
        for line in sorted(lines, key=lambda item: item["product_id"]):
            product = product_map[line["product_id"]]
            qty = line["qty"]
            result = db.session.execute(
                update(Product).where(
                    Product.id == product.id,
                    Product.archived.is_(False),
                    Product.qty_in_stock >= qty,
                ).values(qty_in_stock=Product.qty_in_stock - qty)
            )
            if result.rowcount != 1:
                raise Conflict(f"Not enough stock for product {product.id}")
            order.items.append(OrderItem(
                product=product, qty=qty, unit_price_cents=product.price_cents
            ))
            total += qty * product.price_cents
        order.total_cents = total
        db.session.add(order)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    created = db.session.scalar(
        select(Order).where(Order.id == order.id).options(with_items())
        .execution_options(populate_existing=True)
    )
    return jsonify(OrderOut().dump(created)), 201
