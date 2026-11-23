from flask import Flask, jsonify, request
from gateway import dispatch

app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("account_id"), str) or not body["account_id"].strip():
        return jsonify(error="account_id is required"), 400

    which, result = dispatch(body)
    response = jsonify(result)
    response.headers["X-Order-Handler"] = which
    return response, (201 if which == "v2" else 200)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
