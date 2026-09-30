from flask import Flask, jsonify
from errors import ApiProblem, register_error_handlers

app = Flask(__name__)
register_error_handlers(app)


USERS = {
    42: {"id": 42, "name": "Nguyen Van A"}
}


@app.get("/users/<int:id>")
def get_user(id):
    user = USERS.get(id)
    if not user:
        raise ApiProblem(
            status=404,
            title="User not found",
            type_path="user-not-found",
            resource_id=id,
        )
    return jsonify(user)


if __name__ == "__main__":
    app.run(debug=True)
