from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Build API"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Build API"
    assert data["completed"] is False


def test_missing_task():
    response = client.get("/tasks/999999")

    assert response.status_code == 404
