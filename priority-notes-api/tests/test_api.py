from fastapi.testclient import TestClient

from src.main import app
from src.storage import reset_storage

client = TestClient(app)


def setup_function():
    reset_storage()


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_note():
    response = client.post("/notes", json={
        "title": "Study CI/CD",
        "description": "Prepare pipeline",
        "important": True,
        "urgent": True
    })

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["quadrant"] == "do_now"


def test_get_notes():
    client.post("/notes", json={
        "title": "Read docs",
        "description": "",
        "important": True,
        "urgent": False
    })

    response = client.get("/notes")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_note_by_id():
    client.post("/notes", json={
        "title": "Test note",
        "description": "",
        "important": False,
        "urgent": True
    })

    response = client.get("/notes/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Test note"


def test_delete_note():
    client.post("/notes", json={
        "title": "Delete me",
        "description": "",
        "important": False,
        "urgent": False
    })

    response = client.delete("/notes/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted"
