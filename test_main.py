import pytest
from fastapi.testclient import TestClient
from main import app, todos_db, id_counter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database state before each test."""
    global id_counter
    todos_db.clear()
    import main
    main.id_counter = 1
    yield
    todos_db.clear()
    main.id_counter = 1


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome" in data["message"]
    assert data["docs_url"] == "/docs"


def test_create_todo():
    payload = {
        "title": "Buy groceries",
        "description": "Milk, Eggs, Bread",
        "completed": False,
        "priority": "high",
    }
    response = client.post("/todos/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, Eggs, Bread"
    assert data["completed"] is False
    assert data["priority"] == "high"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_todo_invalid():
    # Empty title should fail validation
    response = client.post("/todos/", json={"title": ""})
    assert response.status_code == 422


def test_get_todos_list():
    client.post("/todos/", json={"title": "Task 1", "priority": "low", "completed": True})
    client.post("/todos/", json={"title": "Task 2", "priority": "high", "completed": False})

    # Get all
    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filter completed
    response = client.get("/todos/?completed=true")
    assert response.status_code == 200
    completed_data = response.json()
    assert len(completed_data) == 1
    assert completed_data[0]["title"] == "Task 1"

    # Filter priority
    response = client.get("/todos/?priority=high")
    assert response.status_code == 200
    high_data = response.json()
    assert len(high_data) == 1
    assert high_data[0]["title"] == "Task 2"

    # Search
    response = client.get("/todos/?search=Task 1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_single_todo():
    client.post("/todos/", json={"title": "Single Task"})
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Task"

    # Non-existent ID
    response_404 = client.get("/todos/999")
    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Todo with ID 999 not found"


def test_put_todo():
    client.post("/todos/", json={"title": "Initial Title", "completed": False})
    put_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True,
        "priority": "low",
    }
    response = client.put("/todos/1", json=put_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True
    assert data["priority"] == "low"

    # PUT on non-existing todo
    response_404 = client.put("/todos/999", json=put_payload)
    assert response_404.status_code == 404


def test_patch_todo():
    client.post("/todos/", json={"title": "Test Patch", "completed": False})
    patch_payload = {"completed": True}
    response = client.patch("/todos/1", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Test Patch"

    # PATCH on non-existing todo
    response_404 = client.patch("/todos/999", json=patch_payload)
    assert response_404.status_code == 404


def test_delete_todo():
    client.post("/todos/", json={"title": "To be deleted"})
    response = client.delete("/todos/1")
    assert response.status_code == 204

    # Verify deleted
    get_res = client.get("/todos/1")
    assert get_res.status_code == 404

    # Delete non-existent
    delete_404 = client.delete("/todos/999")
    assert delete_404.status_code == 404
