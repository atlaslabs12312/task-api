from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
EDITOR = {"X-Role": "editor"}
ADMIN = {"X-Role": "admin"}
VIEWER = {"X-Role": "viewer"}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Build API"},
        headers=EDITOR,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Build API"
    assert data["completed"] is False


def test_viewer_can_list_tasks_and_filter():
    client.post("/tasks", json={"title": "Second task"}, headers=EDITOR)

    response = client.get("/tasks?q=Second", headers=VIEWER)

    assert response.status_code == 200
    assert any(task["title"] == "Second task" for task in response.json())


def test_missing_task():
    response = client.get("/tasks/999999", headers=VIEWER)

    assert response.status_code == 404


def test_complete_task():
    created = client.post(
        "/tasks",
        json={"title": "Complete me"},
        headers=EDITOR,
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/complete",
        headers=EDITOR,
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_viewer_cannot_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Forbidden"},
        headers=VIEWER,
    )

    assert response.status_code == 403


def test_viewer_cannot_read_audit_logs():
    response = client.get("/audit-logs", headers=VIEWER)

    assert response.status_code == 403


def test_admin_can_read_audit_logs():
    response = client.get("/audit-logs", headers=ADMIN)

    assert response.status_code == 200
    assert any(entry["action"] == "create" for entry in response.json())
