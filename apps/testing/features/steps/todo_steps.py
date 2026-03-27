"""
Behave step definitions for the Todo application feature.

Uses Playwright (sync API) via context.page and the TodoPage page object.
context is populated by features/environment.py before each scenario.
"""
import requests
from behave import given, when, then
from playwright.sync_api import expect

from apps.testing.e2e.pages.todo_page import TodoPage


# ── Given ─────────────────────────────────────────────────────────────────────

@given("I open the Todo application")
def step_open_app(context):
    context.todo_page = TodoPage(context.page)
    context.todo_page.navigate(context.base_url)


@given('I have added a todo "{title}"')
def step_given_todo_added(context, title):
    context.todo_page.add_todo(title)


@given('the todo "{title}" is marked as completed')
def step_given_todo_completed(context, title):
    context.todo_page.toggle_todo(title)


# ── When ──────────────────────────────────────────────────────────────────────

@when('I type "{text}" in the todo input')
def step_type_todo(context, text):
    context.todo_page.fill_input(text)


@when("I click the Add button")
def step_click_add(context):
    context.todo_page.click_add()


@when('I add a todo "{title}"')
def step_add_todo(context, title):
    context.todo_page.add_todo(title)


@when('I check the checkbox for "{title}"')
def step_check_checkbox(context, title):
    context.todo_page.toggle_todo(title)


@when('I uncheck the checkbox for "{title}"')
def step_uncheck_checkbox(context, title):
    context.todo_page.toggle_todo(title)


@when('I click the Delete button for "{title}"')
def step_delete_todo(context, title):
    context.todo_page.delete_todo(title)


@when('I click the "{filter_name}" filter')
def step_click_filter(context, filter_name):
    context.todo_page.filter_todos(filter_name)


# ── Then ──────────────────────────────────────────────────────────────────────

@then('the page title should be "{expected_title}"')
def step_check_title(context, expected_title):
    expect(context.page.get_by_test_id("app-title")).to_have_text(expected_title)


@then("the add todo form should be visible")
def step_form_visible(context):
    expect(context.page.get_by_test_id("add-todo-form")).to_be_visible()


@then("the filter bar should be visible")
def step_filter_visible(context):
    expect(context.page.get_by_test_id("filter-bar")).to_be_visible()


@then('I should see "{title}" in the todo list')
def step_see_todo(context, title):
    locator = context.page.get_by_test_id("todo-title").filter(has_text=title)
    expect(locator).to_be_visible()


@then('I should not see "{title}" in the todo list')
def step_not_see_todo(context, title):
    locator = context.page.get_by_test_id("todo-title").filter(has_text=title)
    expect(locator).not_to_be_visible()


@then("the input field should be empty")
def step_input_empty(context):
    expect(context.page.get_by_test_id("todo-input")).to_have_value("")


@then("the todo list should contain {count:d} items")
def step_count_todos(context, count):
    items = context.page.get_by_test_id("todo-item")
    expect(items).to_have_count(count)


@then('"{title}" should be shown as completed')
def step_todo_completed(context, title):
    item = context.page.locator('[data-testid="todo-item"]').filter(
        has=context.page.get_by_test_id("todo-title").filter(has_text=title)
    )
    expect(item).to_have_class(lambda c: "completed" in c)


@then('"{title}" should be shown as active')
def step_todo_active(context, title):
    item = context.page.locator('[data-testid="todo-item"]').filter(
        has=context.page.get_by_test_id("todo-title").filter(has_text=title)
    )
    expect(item).not_to_have_class(lambda c: "completed" in c)


@then('"{title}" should not be in the todo list')
def step_todo_gone(context, title):
    titles = context.todo_page.get_todo_titles()
    assert title not in titles, f"Expected '{title}' to be deleted, but found it in: {titles}"


@then('the "{filter_name}" filter button should be active')
def step_filter_active(context, filter_name):
    testid_map = {"All": "filter-all", "Active": "filter-active", "Completed": "filter-completed"}
    testid = testid_map.get(filter_name, f"filter-{filter_name.lower()}")
    btn = context.page.get_by_test_id(testid)
    expect(btn).to_have_class(lambda c: "active" in c)
