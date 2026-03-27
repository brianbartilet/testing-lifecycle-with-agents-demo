"""
Playwright E2E tests for the Todo application.

These are the hand-written baseline tests.
The PlaywrightAgent will augment/replace these with AI-generated versions.
"""
import allure
import pytest
from playwright.sync_api import Page, expect

from apps.testing.e2e.pages.todo_page import TodoPage


@allure.feature("Todo UI")
class TestTodoUI:

    @allure.story("Page Load")
    @allure.title("Todo app loads with correct title and form")
    @pytest.mark.smoke
    def test_page_loads(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        expect(todo.app_title).to_have_text("Todo App")
        expect(todo.todo_input).to_be_visible()
        expect(todo.add_button).to_be_visible()

    @allure.story("Add Todo")
    @allure.title("User can add a new todo item")
    @pytest.mark.smoke
    def test_add_todo(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("Buy groceries")
        titles = todo.get_todo_titles()
        assert "Buy groceries" in titles

    @allure.story("Add Todo")
    @allure.title("Input field is cleared after adding a todo")
    @pytest.mark.regression
    def test_input_clears_after_add(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("Temporary task")
        expect(todo.todo_input).to_have_value("")

    @allure.story("Complete Todo")
    @allure.title("User can mark a todo as complete")
    @pytest.mark.smoke
    def test_mark_complete(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("Write unit tests")
        todo.toggle_todo("Write unit tests")
        assert todo.is_todo_completed("Write unit tests")

    @allure.story("Delete Todo")
    @allure.title("User can delete a todo item")
    @pytest.mark.smoke
    def test_delete_todo(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("To be deleted")
        todo.delete_todo("To be deleted")
        assert "To be deleted" not in todo.get_todo_titles()

    @allure.story("Filter Todos")
    @allure.title("Active filter shows only incomplete todos")
    @pytest.mark.regression
    def test_filter_active(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("Active item")
        todo.add_todo("Completed item")
        todo.toggle_todo("Completed item")
        todo.filter_todos("Active")
        titles = todo.get_todo_titles()
        assert "Active item" in titles
        assert "Completed item" not in titles

    @allure.story("Filter Todos")
    @allure.title("Completed filter shows only completed todos")
    @pytest.mark.regression
    def test_filter_completed(self, page: Page, base_url: str):
        todo = TodoPage(page)
        todo.navigate(base_url)
        todo.add_todo("Still active")
        todo.add_todo("Already done")
        todo.toggle_todo("Already done")
        todo.filter_todos("Completed")
        titles = todo.get_todo_titles()
        assert "Already done" in titles
        assert "Still active" not in titles
