from flask import Flask, jsonify, request

app = Flask(__name__)

POSTS = [
    {"id": 1, "title": "Bai viet 1", "content": "Noi dung 1"}
]


@app.get("/posts")
def get_posts():
    return jsonify(POSTS), 200


@app.post("/posts")
def create_post():
    data = request.json or {}
    new_post = {
        "id": len(POSTS) + 1,
        "title": data.get("title", ""),
        "content": data.get("content", "")
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.get("/posts/<int:pid>")
def get_post(pid):
    post = next((p for p in POSTS if p["id"] == pid), None)
    return (jsonify(post), 200) if post else ({"error": "not found"}, 404)

if __name__ == "__main__":
    app.run(debug=True)
