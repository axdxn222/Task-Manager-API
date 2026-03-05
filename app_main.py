"""
Task Manager REST API
=====================
A simple REST API built with Flask to teach core API concepts:
- CRUD operations (Create, Read, Update, Delete)
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes (200, 201, 400, 404)
- JSON request/response handling
- Input validation
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid


def create_app():
    """Application factory pattern — makes testing easier."""
    app = Flask(__name__)

    # ---------- In-memory "database" ----------
    # In production you'd use a real database (PostgreSQL, MongoDB, etc.)
    # We keep it simple so you can focus on the API concepts.
    tasks = {}
    VALID_PRIORITIES = ["low", "medium", "high"]

    # ========================================================
    # ROUTE 1 — Health check
    # ========================================================
    # PURPOSE: A simple endpoint that confirms the API is running.
    # CI/CD pipelines and load balancers hit this to verify deployments.
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200

    # ========================================================
    # ROUTE 2 — List all tasks  (GET /tasks)
    # ========================================================
    # HTTP GET = "give me data". No request body needed.
    # We return 200 OK with the full list.
    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        status_filter = request.args.get("status")
        priority_filter = request.args.get("priority")

        result = list(tasks.values())

        if status_filter:
            result = [t for t in result if t["status"] == status_filter]
        if priority_filter:
            result = [t for t in result if t["priority"] == priority_filter]

        # Pagination
        page = request.args.get("page", type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        if page:
            total_items = len(result)
            total_pages = max(1, -(-total_items // per_page))
            start = (page - 1) * per_page
            end = start + per_page
            result = result[start:end]

            return (
                jsonify(
                    {
                        "tasks": result,
                        "count": len(result),
                        "page": page,
                        "per_page": per_page,
                        "total_items": total_items,
                        "total_pages": total_pages,
                    }
                ),
                200,
            )

        return jsonify({"tasks": result, "count": len(result)}), 200

    # ========================================================
    # ROUTE — Search tasks  (GET /tasks/search)
    # ========================================================
    @app.route("/tasks/search", methods=["GET"])
    def search_tasks():
        query = request.args.get("q", "").strip().lower()

        if not query:
            return jsonify({"error": "Search query 'q' is required"}), 400

        results = []
        for task in tasks.values():
            if query in task["title"].lower() or query in task["description"].lower():
                results.append(task)

        return jsonify({"tasks": results, "count": len(results), "query": query}), 200

    # ========================================================
    # ROUTE 3 — Get a single task  (GET /tasks/<id>)
    # ========================================================
    # Path parameters let you identify a specific resource.
    @app.route("/tasks/<task_id>", methods=["GET"])
    def get_task(task_id):
        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task), 200

    # ========================================================
    # ROUTE 4 — Create a task  (POST /tasks)
    # ========================================================
    # HTTP POST = "create something new". Data comes in the request body.
    # We return 201 Created with the new resource.
    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json()

        # --- Input validation ---
        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400

        if not isinstance(data["title"], str) or len(data["title"].strip()) == 0:
            return jsonify({"error": "Title must be a non-empty string"}), 400

        if "priority" in data and data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"Priority must be one of: {VALID_PRIORITIES}"}), 400

        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": data["title"].strip(),
            "description": data.get("description", ""),
            "status": data.get("status", "todo"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "priority": data.get("priority", "medium"),
        }
        tasks[task_id] = task
        return jsonify(task), 201

    # ========================================================
    # ROUTE 5 — Update a task  (PUT /tasks/<id>)
    # ========================================================
    # HTTP PUT = "replace / update a resource".
    @app.route("/tasks/<task_id>", methods=["PUT"])
    def update_task(task_id):
        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        VALID_STATUSES = ["todo", "in_progress", "done"]
        if "status" in data and data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Status must be one of: {VALID_STATUSES}"}), 400

        if "priority" in data and data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"Priority must be one of: {VALID_PRIORITIES}"}), 400

        # Only update fields that were sent
        if "title" in data:
            task["title"] = data["title"]
        if "description" in data:
            task["description"] = data["description"]
        if "status" in data:
            task["status"] = data["status"]
        if "priority" in data:
            task["priority"] = data["priority"]
        task["updated_at"] = datetime.utcnow().isoformat()

        return jsonify(task), 200

    # ========================================================
    # ROUTE 6 — Delete a task  (DELETE /tasks/<id>)
    # ========================================================
    # HTTP DELETE = "remove this resource".
    # 204 No Content is the standard success response for deletions.
    @app.route("/tasks/<task_id>", methods=["DELETE"])
    def delete_task(task_id):
        if task_id not in tasks:
            return jsonify({"error": "Task not found"}), 404
        del tasks[task_id]
        return "", 204

    return app


# ---------- Run the server ----------
if __name__ == "__main__":
    app = create_app()
    print("\n🚀 Task Manager API running at http://localhost:5000")
    print("   Try: curl http://localhost:5000/health\n")
    app.run(debug=True, port=5000)
