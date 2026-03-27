"""
Baseline pytest API tests for the Todo REST API.

Tests all CRUD endpoints, status codes, and validation rules from the OpenAPI spec.
These are the hand-written baseline tests.
The PytestAgent will generate additional tests in test_todo_api_generated.py.
"""
import allure
import pytest
import requests


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_base_url(api_base_url):
    return api_base_url


@pytest.fixture
def new_todo(client):
    """Create a fresh todo and clean it up after each test."""
    todo = None
    created = []

    def _create(title="Test Todo", description=None):
        nonlocal todo
        payload = {"title": title}
        if description:
            payload["description"] = description
        resp = client.post(f"{client.base_url}/todos", json=payload)
        assert resp.status_code == 201
        todo = resp.json()
        created.append(todo["id"])
        return todo

    yield _create

    for tid in created:
        client.delete(f"{client.base_url}/todos/{tid}")


# ── Health ─────────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("Health")
class TestHealth:

    @allure.title("Health endpoint returns 200 ok")
    @pytest.mark.smoke
    def test_health(self, client):
        resp = client.get(f"{client.base_url}/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["service"] == "todo-api"


# ── List Todos ─────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("List Todos")
class TestListTodos:

    @allure.title("GET /todos returns 200 with array")
    @pytest.mark.smoke
    def test_list_returns_array(self, client):
        resp = client.get(f"{client.base_url}/todos")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @allure.title("GET /todos?completed=false filters by incomplete")
    @pytest.mark.regression
    def test_list_filter_active(self, client, new_todo):
        todo = new_todo("Active filter test")
        resp = client.get(f"{client.base_url}/todos", params={"completed": "false"})
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()]
        assert todo["id"] in ids

    @allure.title("GET /todos?completed=true filters by completed")
    @pytest.mark.regression
    def test_list_filter_completed(self, client, new_todo):
        todo = new_todo("Complete filter test")
        client.put(f"{client.base_url}/todos/{todo['id']}", json={"completed": True})
        resp = client.get(f"{client.base_url}/todos", params={"completed": "true"})
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()]
        assert todo["id"] in ids


# ── Create Todo ────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("Create Todo")
class TestCreateTodo:

    @allure.title("POST /todos returns 201 with created todo")
    @pytest.mark.smoke
    def test_create_returns_201(self, client, new_todo):
        todo = new_todo("My new task")
        assert todo["id"]
        assert todo["title"] == "My new task"
        assert todo["completed"] is False

    @allure.title("Created todo has timestamps")
    @pytest.mark.regression
    def test_create_has_timestamps(self, client, new_todo):
        todo = new_todo("Timestamp test")
        assert todo["created_at"]
        assert todo["updated_at"]

    @allure.title("POST /todos with description persists it")
    @pytest.mark.regression
    def test_create_with_description(self, client, new_todo):
        todo = new_todo("Task with desc", description="Some details")
        assert todo["description"] == "Some details"

    @allure.title("POST /todos with empty title returns 422")
    @pytest.mark.regression
    def test_create_empty_title_422(self, client):
        resp = client.post(f"{client.base_url}/todos", json={"title": ""})
        assert resp.status_code == 422

    @allure.title("POST /todos with missing title returns 422")
    @pytest.mark.regression
    def test_create_missing_title_422(self, client):
        resp = client.post(f"{client.base_url}/todos", json={})
        assert resp.status_code == 422

    @allure.title("POST /todos with title > 200 chars returns 422")
    @pytest.mark.regression
    def test_create_title_too_long_422(self, client):
        resp = client.post(f"{client.base_url}/todos", json={"title": "x" * 201})
        assert resp.status_code == 422


# ── Get Todo ───────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("Get Todo")
class TestGetTodo:

    @allure.title("GET /todos/{id} returns the correct todo")
    @pytest.mark.smoke
    def test_get_todo(self, client, new_todo):
        created = new_todo("Get me")
        resp = client.get(f"{client.base_url}/todos/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]
        assert resp.json()["title"] == "Get me"

    @allure.title("GET /todos/{id} returns 404 for unknown id")
    @pytest.mark.regression
    def test_get_nonexistent_404(self, client):
        resp = client.get(f"{client.base_url}/todos/nonexistent-id")
        assert resp.status_code == 404


# ── Update Todo ────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("Update Todo")
class TestUpdateTodo:

    @allure.title("PUT /todos/{id} updates the title")
    @pytest.mark.smoke
    def test_update_title(self, client, new_todo):
        todo = new_todo("Old title")
        resp = client.put(f"{client.base_url}/todos/{todo['id']}", json={"title": "New title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New title"

    @allure.title("PUT /todos/{id} marks todo as complete")
    @pytest.mark.smoke
    def test_mark_complete(self, client, new_todo):
        todo = new_todo("Complete me")
        resp = client.put(f"{client.base_url}/todos/{todo['id']}", json={"completed": True})
        assert resp.status_code == 200
        assert resp.json()["completed"] is True

    @allure.title("PUT /todos/{id} returns 404 for unknown id")
    @pytest.mark.regression
    def test_update_nonexistent_404(self, client):
        resp = client.put(f"{client.base_url}/todos/no-such-id", json={"title": "X"})
        assert resp.status_code == 404

    @allure.title("PUT /todos/{id} updates updated_at timestamp")
    @pytest.mark.regression
    def test_update_timestamp(self, client, new_todo):
        todo = new_todo("Timestamp update")
        original_ts = todo["updated_at"]
        import time; time.sleep(0.01)
        updated = client.put(
            f"{client.base_url}/todos/{todo['id']}", json={"title": "New"}
        ).json()
        assert updated["updated_at"] >= original_ts


# ── Delete Todo ────────────────────────────────────────────────────────────────

@allure.feature("Todo API")
@allure.story("Delete Todo")
class TestDeleteTodo:

    @allure.title("DELETE /todos/{id} returns 204")
    @pytest.mark.smoke
    def test_delete_returns_204(self, client, new_todo):
        todo = new_todo("Delete me")
        resp = client.delete(f"{client.base_url}/todos/{todo['id']}")
        assert resp.status_code == 204

    @allure.title("Deleted todo cannot be retrieved")
    @pytest.mark.regression
    def test_deleted_todo_not_found(self, client, new_todo):
        todo = new_todo("Gone soon")
        client.delete(f"{client.base_url}/todos/{todo['id']}")
        resp = client.get(f"{client.base_url}/todos/{todo['id']}")
        assert resp.status_code == 404

    @allure.title("DELETE /todos/{id} returns 404 for unknown id")
    @pytest.mark.regression
    def test_delete_nonexistent_404(self, client):
        resp = client.delete(f"{client.base_url}/todos/no-such-id")
        assert resp.status_code == 404
