from datetime import date
from pathlib import Path
from uuid import uuid4

import yaml
from flask import Flask, Response, jsonify, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DEMO_TOKEN = "demo-token"

TASKS = {
    "11111111-1111-4111-8111-111111111111": {
        "id": "11111111-1111-4111-8111-111111111111",
        "title": "Hoàn thành bài OpenAPI",
        "status": "open",
        "priority": "high",
        "dueDate": "2026-10-12",
        "assigneeId": "22222222-2222-4222-8222-222222222222",
    }
}

STATUS_VALUES = {"open", "done"}
PRIORITY_VALUES = {"low", "normal", "high"}


def problem(status: int, title: str, detail: str):
    body = {
        "type": f"https://example.vn/errors/{title.lower().replace(' ', '-')}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    return jsonify(body), status, {"Content-Type": "application/problem+json"}


def require_bearer_token():
    if request.headers.get("Authorization") != f"Bearer {DEMO_TOKEN}":
        return problem(
            401,
            "Unauthorized",
            "Dùng Authorization header với Bearer demo-token.",
        )
    return None


def valid_iso_date(value):
    if value is None:
        return True
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_task_payload(payload, partial=False):
    if not isinstance(payload, dict):
        return "Request body phải là JSON object."

    allowed = {"title", "status", "priority", "dueDate", "assigneeId"}
    unknown = set(payload) - allowed
    if unknown:
        return f"Field không hợp lệ: {', '.join(sorted(unknown))}."

    if partial and not payload:
        return "PATCH phải có ít nhất một field cần cập nhật."

    if not partial and not str(payload.get("title", "")).strip():
        return "title là bắt buộc."

    if "title" in payload and not str(payload["title"]).strip():
        return "title không được để trống."

    if "status" in payload and payload["status"] not in STATUS_VALUES:
        return "status chỉ nhận open hoặc done."

    if "priority" in payload and payload["priority"] not in PRIORITY_VALUES:
        return "priority chỉ nhận low, normal hoặc high."

    if "dueDate" in payload and not valid_iso_date(payload["dueDate"]):
        return "dueDate phải theo định dạng YYYY-MM-DD."

    return None


@app.before_request
def protect_api_routes():
    if request.path.startswith("/v1/"):
        return require_bearer_token()
    return None


@app.get("/v1/tasks")
def list_tasks():
    status = request.args.get("status")
    if status is not None and status not in STATUS_VALUES:
        return problem(422, "Validation error", "status chỉ nhận open hoặc done.")

    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return problem(422, "Validation error", "limit phải là số nguyên.")

    if limit < 1 or limit > 100:
        return problem(422, "Validation error", "limit phải nằm trong khoảng 1..100.")

    tasks = list(TASKS.values())
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    return jsonify(tasks[:limit]), 200


@app.post("/v1/tasks")
def create_task():
    payload = request.get_json(silent=True)
    error = validate_task_payload(payload, partial=False)
    if error:
        return problem(422, "Validation error", error)

    task_id = str(uuid4())
    task = {
        "id": task_id,
        "title": payload["title"].strip(),
        "status": payload.get("status", "open"),
        "priority": payload.get("priority", "normal"),
        "dueDate": payload.get("dueDate"),
        "assigneeId": payload.get("assigneeId"),
    }
    TASKS[task_id] = task
    response = jsonify(task)
    response.status_code = 201
    response.headers["Location"] = f"/v1/tasks/{task_id}"
    return response


@app.get("/v1/tasks/<task_id>")
def get_task_by_id(task_id):
    task = TASKS.get(task_id)
    if task is None:
        return problem(404, "Task not found", "Task không tồn tại.")
    return jsonify(task), 200


@app.patch("/v1/tasks/<task_id>")
def patch_task(task_id):
    task = TASKS.get(task_id)
    if task is None:
        return problem(404, "Task not found", "Task không tồn tại.")

    payload = request.get_json(silent=True)
    error = validate_task_payload(payload, partial=True)
    if error:
        return problem(422, "Validation error", error)

    if "title" in payload:
        payload["title"] = payload["title"].strip()
    task.update(payload)
    return jsonify(task), 200


@app.delete("/v1/tasks/<task_id>")
def delete_task(task_id):
    if task_id not in TASKS:
        return problem(404, "Task not found", "Task không tồn tại.")
    del TASKS[task_id]
    return Response(status=204)


@app.get("/openapi.json")
def openapi_json():
    with (BASE_DIR / "openapi.yaml").open("r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)
    return jsonify(spec)


@app.get("/docs")
def swagger_docs():
    return """<!doctype html>
<html lang=\"vi\">
<head>
  <meta charset=\"utf-8\">
  <title>Tasks API - Swagger UI</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\">
</head>
<body>
  <div id=\"swagger-ui\"></div>
  <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        persistAuthorization: true
      });
    };
  </script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
