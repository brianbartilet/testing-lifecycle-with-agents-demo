"""
Pytest conftest for Playwright E2E tests.

Provides browser, page, and base_url fixtures.
"""
import os
import pytest
from playwright.sync_api import sync_playwright, Browser, Page


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as pw:
        browser: Browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        yield browser
        browser.close()


@pytest.fixture
def page(browser_instance) -> Page:
    ctx = browser_instance.new_context()
    pg = ctx.new_page()
    pg.set_default_timeout(10_000)
    yield pg
    pg.close()
    ctx.close()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000")
