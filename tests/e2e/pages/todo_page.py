"""
Todo Application - Playwright Page Object Model.

This file is the baseline hand-written POM.
When the PlaywrightAgent runs, it overwrites this with an AI-generated version
based on the live HTML analysis.
"""
from typing import List
from playwright.sync_api import Page, Locator, expect


class TodoPage:
    """Page Object for the Todo application frontend."""

    def __init__(self, page: Page) -> None:
        self.page = page

    # ── Locators ──────────────────────────────────────────────────────────────

    @property
    def app_title(self) -> Locator:
        return self.page.get_by_test_id("app-title")

    @property
    def todo_input(self) -> Locator:
        return self.page.get_by_test_id("todo-input")

    @property
    def add_button(self) -> Locator:
        return self.page.get_by_test_id("add-todo-btn")

    @property
    def todo_list(self) -> Locator:
        return self.page.get_by_test_id("todo-list")

    @property
    def todo_items(self) -> Locator:
        return self.page.get_by_test_id("todo-item")

    @property
    def status_message(self) -> Locator:
        return self.page.get_by_test_id("status-message")

    @property
    def filter_all(self) -> Locator:
        return self.page.get_by_test_id("filter-all")

    @property
    def filter_active(self) -> Locator:
        return self.page.get_by_test_id("filter-active")

    @property
    def filter_completed(self) -> Locator:
        return self.page.get_by_test_id("filter-completed")

    # ── Actions ───────────────────────────────────────────────────────────────

    def navigate(self, base_url: str = "http://localhost:3000") -> None:
        """Navigate to the Todo application."""
        self.page.goto(base_url)
        self.page.wait_for_load_state("networkidle")

    def fill_input(self, title: str) -> None:
        """Type text into the todo input field without submitting."""
        self.todo_input.fill(title)

    def click_add(self) -> None:
        """Click the Add button to submit the form."""
        self.add_button.click()

    def add_todo(self, title: str) -> None:
        """Type a todo title and submit the form."""
        self.fill_input(title)
        self.click_add()
        # Wait for the item to appear
        self.page.get_by_test_id("todo-title").filter(has_text=title).wait_for()

    def delete_todo(self, title: str) -> None:
        """Click the Delete button for the todo with the given title."""
        item = self.page.locator('[data-testid="todo-item"]').filter(
            has=self.page.get_by_test_id("todo-title").filter(has_text=title)
        )
        item.get_by_test_id("delete-todo-btn").click()

    def toggle_todo(self, title: str, timeout_ms: int = 5000) -> None:
        """Toggle the completion checkbox and wait for the PUT to commit.

        The frontend's onchange handler does an async PUT and only then
        re-renders the <li> with the new data-completed value. Wait for
        that re-render so callers don't race the network round-trip.
        """
        item = self.page.locator('[data-testid="todo-item"]').filter(
            has=self.page.get_by_test_id("todo-title").filter(has_text=title)
        )
        was_completed = (item.get_attribute("data-completed") or "false") == "true"
        item.get_by_test_id("todo-checkbox").click()
        expected = "false" if was_completed else "true"
        expect(item).to_have_attribute("data-completed", expected, timeout=timeout_ms)

    def filter_todos(self, filter_name: str) -> None:
        """Click a filter button by name: 'All', 'Active', or 'Completed'."""
        filter_map = {
            "All": self.filter_all,
            "Active": self.filter_active,
            "Completed": self.filter_completed,
        }
        locator = filter_map.get(filter_name)
        if not locator:
            raise ValueError(f"Unknown filter: {filter_name!r}. Use 'All', 'Active', or 'Completed'.")
        locator.click()

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_todo_titles(self) -> List[str]:
        """Return a list of all visible todo titles."""
        return self.page.get_by_test_id("todo-title").all_inner_texts()

    def get_visible_count(self) -> int:
        """Return the number of visible todo items."""
        return self.todo_items.count()

    def is_todo_completed(self, title: str, timeout_ms: int = 5000) -> bool:
        """Return True if the todo with the given title is marked as completed.

        Toggling fires an async PUT and re-renders the <li>; wait for the
        post-render `data-completed="true"` attribute rather than reading
        class synchronously, otherwise we race the network round-trip.
        """
        completed_item = self.page.locator(
            '[data-testid="todo-item"][data-completed="true"]'
        ).filter(
            has=self.page.get_by_test_id("todo-title").filter(has_text=title)
        )
        try:
            completed_item.wait_for(state="attached", timeout=timeout_ms)
            return True
        except Exception:
            return False
