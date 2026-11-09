
products = [
    {"id": 1, "name": "Laptop Dell", "price": 1500},
    {"id": 2, "name": "iPhone 15", "price": 900}
]


# GET /products
def get_products():
    return products, 200


# POST /products
def add_product(body):
    new_product = {
        "id": len(products) + 1,
        "name": body["name"],
        "price": body["price"]
    }

    products.append(new_product)
    return new_product, 201
