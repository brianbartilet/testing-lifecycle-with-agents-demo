"""
Behave environment hooks for the testing lifecycle demo.

Sets up Playwright browser context before tests and tears it down after.
Reads configuration from environment variables so it works in Docker and CI.
"""
import os
from playwright.sync_api import sync_playwright


def before_all(context):
    context.base_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    context.api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )


def before_scenario(context, scenario):
    context.page = context.browser.new_page()
    context.page.set_default_timeout(10_000)


def after_scenario(context, scenario):
    if hasattr(context, "page"):
        context.page.close()


def after_all(context):
    if hasattr(context, "browser"):
        context.browser.close()
    if hasattr(context, "playwright"):
        context.playwright.stop()
