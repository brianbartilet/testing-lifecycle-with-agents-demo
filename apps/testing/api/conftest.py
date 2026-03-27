"""
Pytest conftest for API tests.

Provides a requests Session fixture pointed at the running Todo API.
"""
import os
import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client(api_base_url: str) -> requests.Session:
    """Requests session with the API base URL set."""
    session = requests.Session()
    session.base_url = api_base_url
    yield session
    session.close()


def create_todo(client: requests.Session, title: str, description: str = None) -> dict:
    """Helper: create a todo and return the response body."""
    payload = {"title": title}
    if description:
        payload["description"] = description
    resp = client.post(f"{client.base_url}/todos", json=payload)
    resp.raise_for_status()
    return resp.json()


def delete_todo(client: requests.Session, todo_id: str) -> None:
    """Helper: delete a todo by ID, ignoring 404."""
    client.delete(f"{client.base_url}/todos/{todo_id}")
