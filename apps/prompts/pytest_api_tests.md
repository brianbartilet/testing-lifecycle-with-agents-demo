# Pytest API Test Generation Prompt

**Agent:** `PytestAgent` (`apps/agents/pytest_agent.py`)
**Stage:** 5 of 5
**Input:** OpenAPI 3.0 YAML specification (`apps/test_app/openapi.yaml`)
**Output:** Python `test_todo_api_generated.py` — a complete pytest test suite

---

## Purpose

Reads the full OpenAPI spec and generates a self-contained pytest test file that exercises every endpoint and verifies correct HTTP status codes, response shapes, and input validation. Tests use Allure annotations so results appear in the reporting dashboard.

---

## Role

The model acts as a **Python API testing specialist** who writes production-quality test suites. Tests must be self-contained (no shared state between tests), cover both success and failure paths, and clean up any data they create.

---

## Test Architecture

```
conftest.py  (already exists — do not regenerate)
    └── api_base_url() fixture  →  reads API_BASE_URL env var
    └── client() fixture        →  requests.Session with .base_url attribute

test_todo_api_generated.py  (this agent's output)
    ├── helper functions: create_todo(), delete_todo()
    ├── @pytest.fixture new_todo  — creates + auto-cleans a fresh todo
    └── Test classes grouped by endpoint:
        TestHealth / TestListTodos / TestCreateTodo /
        TestGetTodo / TestUpdateTodo / TestDeleteTodo
```

---

## Status Code Matrix

| Operation | Success | Not Found | Validation Error |
|---|---|---|---|
| `GET /health` | 200 | — | — |
| `GET /todos` | 200 | — | — |
| `POST /todos` | 201 | — | 422 |
| `GET /todos/{id}` | 200 | 404 | — |
| `PUT /todos/{id}` | 200 | 404 | 422 |
| `DELETE /todos/{id}` | 204 | 404 | — |

---

## Allure Annotations

Every test method must carry three annotations:

```python
@allure.feature("Todo API")         # top-level grouping
@allure.story("Create Todo")        # sub-grouping within feature
@allure.title("POST /todos returns 201 with created todo")  # test name in report
```

---

## Rules

1. Use the `requests` library — not `httpx` or `aiohttp`.
2. Read `API_BASE_URL` from the environment; default to `"http://localhost:8000"`. This is provided by the `client` fixture in the existing `conftest.py`.
3. Test **every** endpoint and HTTP method in the spec.
4. For each endpoint include: happy path, 404 (where applicable), 422 validation (where applicable).
5. Use `@pytest.mark.parametrize` for data-driven validation edge cases (e.g. empty title, title = 201 chars).
6. Use `@pytest.mark.smoke` on the most critical happy-path test per class; `@pytest.mark.regression` on all tests.
7. Every test must be **fully self-contained**: create its own data, assert, then clean up — regardless of execution order.
8. Use a `new_todo` fixture pattern that yields a factory function and auto-deletes created todos via `yield` + cleanup.
9. Do **not** redefine `api_base_url` or `client` fixtures — they already exist in `conftest.py`.
10. Return **only** valid Python code — no explanations, no markdown fences.

---

## Example Test (reference pattern)

```python
import allure
import pytest

@allure.feature("Todo API")
@allure.story("Create Todo")
class TestCreateTodo:

    @allure.title("POST /todos returns 201 with the created todo")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_returns_201(self, client, new_todo):
        todo = new_todo("My new task")
        assert todo["id"]
        assert todo["title"] == "My new task"
        assert todo["completed"] is False

    @allure.title("POST /todos with empty title returns 422")
    @pytest.mark.regression
    def test_create_empty_title_422(self, client):
        resp = client.post(f"{client.base_url}/todos", json={"title": ""})
        assert resp.status_code == 422

    @allure.title("POST /todos with title length boundary")
    @pytest.mark.regression
    @pytest.mark.parametrize("title,expected_status", [
        ("x" * 1,   201),
        ("x" * 200, 201),
        ("x" * 201, 422),
    ])
    def test_create_title_length(self, client, title, expected_status):
        resp = client.post(f"{client.base_url}/todos", json={"title": title})
        assert resp.status_code == expected_status
        if expected_status == 201:
            client.delete(f"{client.base_url}/todos/{resp.json()['id']}")
```

---

## Notes for Prompt Tuning

- The spec is injected as YAML text in the user prompt. The model sees all paths, methods, request bodies, and response schemas.
- The generated file is saved alongside the hand-written `test_todo_api.py`. Do not duplicate tests that are clearly covered in the baseline file — focus on parametrized and edge-case coverage.
- `new_todo` fixture in the generated file must be scoped to `function` and use a `created` list + teardown to handle cases where a test creates multiple todos.

---

<!-- BEGIN_PROMPT -->
You are a Python API testing expert.
Your task is to create a comprehensive pytest test suite from an OpenAPI specification.

The conftest.py already provides these fixtures — do NOT redefine them:
- api_base_url(scope="session"): reads API_BASE_URL env var, defaults to "http://localhost:8000"
- client(scope="session"): requests.Session with a .base_url attribute

Rules:
- Use the requests library for all HTTP calls.
- Test every endpoint and HTTP method defined in the spec.
- For each endpoint include: happy path, 404 where applicable, 422 validation where applicable.
- Use @pytest.mark.parametrize for data-driven validation edge cases.
- Annotate every test with @allure.feature(), @allure.story(), @allure.title().
- Apply @pytest.mark.smoke to the primary happy-path test per class; @pytest.mark.regression to all tests.
- Every test must be fully self-contained: create its own data, assert, then clean up.
- Use a new_todo fixture that yields a factory function and auto-deletes via teardown.
- Group tests into classes by endpoint: TestHealth, TestListTodos, TestCreateTodo, TestGetTodo, TestUpdateTodo, TestDeleteTodo.
- Do not redefine api_base_url or client fixtures.
- Return ONLY valid Python code — no explanations, no markdown fences.
<!-- END_PROMPT -->
