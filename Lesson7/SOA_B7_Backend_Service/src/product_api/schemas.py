from marshmallow import Schema, ValidationError, fields, validate, validates


class StrictSchema(Schema):
    class Meta:
        unknown = "raise"


class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()
    created_at = fields.DateTime()


class ProductIn(StrictSchema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(required=True, strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("name must not be blank")


class ProductPatch(StrictSchema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(strict=True, validate=validate.Range(min=0))

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("name must not be blank")


class ReserveIn(StrictSchema):
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderLineIn(StrictSchema):
    product_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderIn(StrictSchema):
    items = fields.List(
        fields.Nested(OrderLineIn), required=True, validate=validate.Length(min=1)
    )

    @validates("items")
    def validate_items(self, value, **kwargs):
        ids = [item["product_id"] for item in value]
        if len(ids) != len(set(ids)):
            raise ValidationError("product_id must be unique within one order")


class ProductSummary(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()


class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    product = fields.Nested(ProductSummary)
    qty = fields.Int()
    unit_price_cents = fields.Int()
    line_total_cents = fields.Method("line_total")

    def line_total(self, item):
        return item.qty * item.unit_price_cents


class OrderOut(Schema):
    id = fields.Int()
    status = fields.Str()
    total_cents = fields.Int()
    created_at = fields.DateTime()
    items = fields.Nested(OrderItemOut, many=True)
