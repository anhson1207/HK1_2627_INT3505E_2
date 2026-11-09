from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields


app = Flask(__name__)

app.config["API_TITLE"] = "Product API"
app.config["API_VERSION"] = "1.0.0"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_JSON_PATH"] = "openapi.json"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
)

api = Api(app)


products = [
    {"id": 1, "name": "Laptop Dell", "price": 1500},
    {"id": 2, "name": "iPhone 15", "price": 900}
]


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)



blp = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
    description="Product management API"
)



@blp.route("/")
class Products(MethodView):

    # GET /products
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return products

    # POST /products
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        new_product = {
            "id": max(
                (p["id"] for p in products),
                default=0
            ) + 1,
            "name": product_data["name"],
            "price": product_data["price"]
        }

        products.append(new_product)
        return new_product



api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
