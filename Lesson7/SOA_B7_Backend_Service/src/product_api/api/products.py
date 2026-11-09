from flask import Blueprint, jsonify
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from ..errors import Conflict, NotFound
from ..extensions import db
from ..models import Product
from ..schemas import ProductIn, ProductOut, ProductPatch, ReserveIn
from .common import pagination, require_json_object

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


def active_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        raise NotFound("Product not found")
    return product


@products_bp.get("")
def list_products():
    page, size = pagination()
    active = Product.archived.is_(False)
    rows = db.session.scalars(
        select(Product).where(active).order_by(Product.id)
        .offset((page - 1) * size).limit(size)
    ).all()
    total = db.session.scalar(select(func.count()).select_from(Product).where(active))
    return jsonify({
        "items": ProductOut(many=True).dump(rows),
        "page": page, "size": size, "total": total,
    }), 200


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    return jsonify(ProductOut().dump(active_product(product_id))), 200


@products_bp.post("")
def create_product():
    body = ProductIn().load(require_json_object())
    product = Product(**body)
    try:
        db.session.add(product)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("SKU already exists") from None
    return jsonify(ProductOut().dump(product)), 201


@products_bp.post("/<int:product_id>/reserve")
def reserve_product(product_id):
    body = ReserveIn().load(require_json_object())
    product = active_product(product_id)
    qty = body["qty"]
    updated = db.session.execute(
        update(Product).where(
            Product.id == product_id,
            Product.archived.is_(False),
            Product.qty_in_stock >= qty,
        ).values(qty_in_stock=Product.qty_in_stock - qty)
    )
    if updated.rowcount != 1:
        db.session.rollback()
        raise Conflict("Not enough stock")
    db.session.commit()
    db.session.refresh(product)
    return jsonify(ProductOut().dump(product)), 200


@products_bp.patch("/<int:product_id>")
def patch_product(product_id):
    body = ProductPatch().load(require_json_object())
    if not body:
        from marshmallow import ValidationError
        raise ValidationError({"_schema": ["At least one field is required"]})
    product = active_product(product_id)
    for key, value in body.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(ProductOut().dump(product)), 200


@products_bp.delete("/<int:product_id>")
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        raise NotFound("Product not found")
    if not product.archived:
        product.archived = True
        db.session.commit()
    return "", 204
