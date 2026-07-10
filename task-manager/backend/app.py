# =============================================================
#  app.py  --  Flask REST API  |  Task Manager
#  Endpoints:
#    GET    /api/tasks          list / search / filter tasks
#    GET    /api/tasks/<id>     get single task
#    POST   /api/tasks          create task
#    PUT    /api/tasks/<id>     update task
#    DELETE /api/tasks/<id>     delete task
#    GET    /api/stats          dashboard statistics
# =============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import models

app = Flask(__name__)
CORS(app)   # allow frontend (file://) to reach the API

# Auto-create SQLite DB and seed data on first run
models.init_db()


# ── Helpers ───────────────────────────────────────────────────

def serialize(task):
    """Convert a DB row dict to a JSON-safe dict."""
    if task is None:
        return None
    return {
        "task_id":       task["task_id"],
        "employee_name": task["employee_name"],
        "task_title":    task["task_title"],
        "completed":     bool(task["completed"]),
        "created_at":    str(task["created_at"]),
    }


def ok(data, code=200):
    return jsonify({"success": True,  "data": data}), code


def err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code


# ── Routes ────────────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({"message": "Task Manager API is running 🚀"})


# GET /api/tasks  →  list all tasks (optional: ?search=&completed=)
@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    search    = request.args.get("search", "").strip() or None
    comp_raw  = request.args.get("completed")
    completed = None
    if comp_raw is not None:
        completed = comp_raw.lower() == "true"

    tasks = models.get_all_tasks(search=search, completed=completed)
    return ok([serialize(t) for t in tasks])


# GET /api/tasks/<id>  →  single task
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = models.get_task(task_id)
    if task is None:
        return err("Task not found", 404)
    return ok(serialize(task))


# POST /api/tasks  →  create task
@app.route("/api/tasks", methods=["POST"])
def create_task():
    body          = request.get_json(silent=True) or {}
    employee_name = str(body.get("employee_name", "")).strip()
    task_title    = str(body.get("task_title",    "")).strip()
    completed     = bool(body.get("completed", False))

    if not employee_name:
        return err("employee_name is required")
    if not task_title:
        return err("task_title is required")

    new_id = models.create_task(employee_name, task_title, completed)
    task   = models.get_task(new_id)
    return ok(serialize(task), 201)


# PUT /api/tasks/<id>  →  update task
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    if models.get_task(task_id) is None:
        return err("Task not found", 404)

    body          = request.get_json(silent=True) or {}
    employee_name = body.get("employee_name")
    task_title    = body.get("task_title")
    completed     = body.get("completed")

    if employee_name is not None:
        employee_name = str(employee_name).strip()
        if not employee_name:
            return err("employee_name cannot be empty")

    if task_title is not None:
        task_title = str(task_title).strip()
        if not task_title:
            return err("task_title cannot be empty")

    if completed is not None:
        completed = bool(completed)

    models.update_task(task_id, employee_name, task_title, completed)
    return ok(serialize(models.get_task(task_id)))


# DELETE /api/tasks/<id>  →  delete task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if models.get_task(task_id) is None:
        return err("Task not found", 404)
    models.delete_task(task_id)
    return ok({"message": f"Task {task_id} deleted successfully"})


# GET /api/stats  →  dashboard statistics
@app.route("/api/stats", methods=["GET"])
def stats():
    data = models.get_stats()
    return ok({
        "total":     int(data["total"]     or 0),
        "completed": int(data["completed"] or 0),
        "pending":   int(data["pending"]   or 0),
        "employees": int(data["employees"] or 0),
    })


# ── Entry Point ───────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Task Manager API  -->  http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
