"""
Test Suite for the Task Manager API
====================================
Run with:  pytest test_app.py -v
"""

import pytest
import json
from app_main import create_app


@pytest.fixture
def app():
    """Create a fresh app instance for every test."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """A test client lets us make requests without running the server."""
    return app.test_client()


@pytest.fixture
def sample_task(client):
    """Create and return a sample task for tests that need existing data."""
    response = client.post(
        "/tasks",
        data=json.dumps({"title": "Learn REST APIs", "description": "Build a project"}),
        content_type="application/json",
    )
    return json.loads(response.data)


# --- Health Check ---
class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status_field(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data


# --- Creating Tasks (POST) ---
class TestCreateTask:
    def test_create_task_success(self, client):
        response = client.post(
            "/tasks",
            data=json.dumps({"title": "Write tests"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["title"] == "Write tests"
        assert data["status"] == "todo"
        assert "id" in data

    def test_create_task_with_all_fields(self, client):
        payload = {"title": "Deploy app", "description": "Push to production", "status": "in_progress"}
        response = client.post("/tasks", data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["description"] == "Push to production"
        assert data["status"] == "in_progress"

    def test_create_task_missing_title(self, client):
        response = client.post(
            "/tasks", data=json.dumps({"description": "No title"}), content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_task_empty_title(self, client):
        response = client.post(
            "/tasks", data=json.dumps({"title": "   "}), content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_task_no_body(self, client):
        response = client.post("/tasks", content_type="application/json")
        assert response.status_code == 400


# --- Reading Tasks (GET) ---
class TestGetTasks:
    def test_get_empty_list(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["tasks"] == []
        assert data["count"] == 0

    def test_get_all_tasks(self, client, sample_task):
        response = client.get("/tasks")
        data = json.loads(response.data)
        assert data["count"] == 1

    def test_get_single_task(self, client, sample_task):
        response = client.get(f"/tasks/{sample_task['id']}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "Learn REST APIs"

    def test_get_nonexistent_task(self, client):
        response = client.get("/tasks/does-not-exist")
        assert response.status_code == 404

    def test_filter_by_status(self, client, sample_task):
        response = client.get("/tasks?status=todo")
        data = json.loads(response.data)
        assert data["count"] == 1
        response = client.get("/tasks?status=done")
        data = json.loads(response.data)
        assert data["count"] == 0


# --- Updating Tasks (PUT) ---
class TestUpdateTask:
    def test_update_title(self, client, sample_task):
        response = client.put(
            f"/tasks/{sample_task['id']}",
            data=json.dumps({"title": "Updated"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert json.loads(response.data)["title"] == "Updated"

    def test_update_status(self, client, sample_task):
        response = client.put(
            f"/tasks/{sample_task['id']}",
            data=json.dumps({"status": "done"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert json.loads(response.data)["status"] == "done"

    def test_update_invalid_status(self, client, sample_task):
        response = client.put(
            f"/tasks/{sample_task['id']}",
            data=json.dumps({"status": "invalid"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_update_nonexistent(self, client):
        response = client.put(
            "/tasks/nope", data=json.dumps({"title": "X"}), content_type="application/json"
        )
        assert response.status_code == 404


# --- Deleting Tasks (DELETE) ---
class TestDeleteTask:
    def test_delete_task(self, client, sample_task):
        response = client.delete(f"/tasks/{sample_task['id']}")
        assert response.status_code == 204
        response = client.get(f"/tasks/{sample_task['id']}")
        assert response.status_code == 404

    def test_delete_nonexistent(self, client):
        response = client.delete("/tasks/nope")
        assert response.status_code == 404