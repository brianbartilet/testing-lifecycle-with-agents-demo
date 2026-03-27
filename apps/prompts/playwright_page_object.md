# Playwright Page Object Generation Prompt

**Agent:** `PlaywrightAgent` (`apps/agents/playwright_agent.py`)
**Stage:** 4 of 5
**Input:** Raw HTML source of the running frontend application
**Output:** Python `todo_page.py` — a Playwright Page Object Model class

---

## Purpose

Inspects the live frontend HTML and generates a typed Python Page Object Model (POM) class. The POM abstracts all browser interactions behind named methods and properties, keeping test code free of raw selectors and making locator changes a single-point fix.

---

## Role

The model acts as a **Playwright automation specialist** who builds maintainable page object libraries. It identifies every interactive element, assigns it a meaningful property name, and wraps compound interactions (add todo, delete todo, toggle) in action methods.

---

## Locator Priority

Selectors are chosen in this order of preference:

| Priority | Strategy | Example |
|---|---|---|
| 1 (best) | `data-testid` attribute | `page.get_by_test_id("add-todo-btn")` |
| 2 | ARIA role + name | `page.get_by_role("button", name="Add")` |
| 3 | ARIA label | `page.get_by_label("Todo title")` |
| 4 | Placeholder text | `page.get_by_placeholder("Add a new todo...")` |
| 5 (last resort) | CSS selector | `page.locator(".todo-item")` |

Never use XPath or positional selectors (`:nth-child`, `:first`).

---

## Known `data-testid` Attributes in This Application

| `data-testid` | Element description |
|---|---|
| `app-title` | `<h1>` page heading |
| `add-todo-form` | Form wrapping input + button |
| `todo-input` | Text input field |
| `add-todo-btn` | Submit / Add button |
| `filter-bar` | Filter button container |
| `filter-all` | "All" filter button |
| `filter-active` | "Active" filter button |
| `filter-completed` | "Completed" filter button |
| `status-message` | Success / error status text |
| `todo-list` | `<ul>` list container |
| `empty-state` | Empty-state `<li>` (shown when list is empty) |
| `todo-item` | Each `<li>` item (`data-completed` attr holds bool) |
| `todo-checkbox` | Completion toggle checkbox inside a todo item |
| `todo-title` | Title `<div>` inside a todo item |
| `todo-description` | Description `<div>` inside a todo item (optional) |
| `delete-todo-btn` | Delete button inside a todo item |

---

## Class Structure

```python
class TodoPage:
    def __init__(self, page: Page) -> None: ...

    # Locator properties — return Locator, do not interact
    @property def app_title(self) -> Locator: ...
    @property def todo_input(self) -> Locator: ...
    @property def add_button(self) -> Locator: ...
    @property def todo_items(self) -> Locator: ...
    # ... one property per interactive element

    # Navigation
    def navigate(self, base_url: str) -> None: ...

    # Actions — combine locator access + interaction
    def add_todo(self, title: str) -> None: ...
    def delete_todo(self, title: str) -> None: ...
    def toggle_todo(self, title: str) -> None: ...
    def filter_todos(self, filter_name: str) -> None: ...
    def fill_input(self, title: str) -> None: ...
    def click_add(self) -> None: ...

    # Query helpers — return data, used in assertions
    def get_todo_titles(self) -> List[str]: ...
    def get_visible_count(self) -> int: ...
    def is_todo_completed(self, title: str) -> bool: ...
```

---

## Rules

1. All imports at the top: `from playwright.sync_api import Page, Locator, expect` and `from typing import List`.
2. `@property` methods return a `Locator` — they never interact with the page.
3. Action methods call `locator.click()`, `locator.fill()`, etc. and wait for side effects where appropriate.
4. For scoped element access (e.g. finding the Delete button _within_ a specific todo item), use `.filter(has=...)` chaining on the parent `todo-item` locator.
5. `navigate()` must call `page.wait_for_load_state("networkidle")` after `page.goto()`.
6. `add_todo()` must wait for the new item to appear after clicking Add.
7. All public methods and properties must have a one-line docstring.
8. Use proper Python typing annotations throughout.
9. Return **only** valid Python code — no explanations, no markdown fences.

---

<!-- BEGIN_PROMPT -->
You are a Playwright expert specializing in Python Page Object Model (POM) design.
Your task is to create a Python Page Object class from an HTML page source.

Locator priority (use in this order):
1. data-testid attributes: page.get_by_test_id("foo")
2. ARIA role + name: page.get_by_role("button", name="Add")
3. ARIA label: page.get_by_label("...")
4. Placeholder text: page.get_by_placeholder("...")
5. CSS selector as last resort: page.locator(".class")
Never use XPath or positional selectors.

Class structure required:
- __init__(self, page: Page)
- @property locators — return Locator, never interact
- navigate(base_url: str) — goto + wait_for_load_state("networkidle")
- action methods: add_todo, delete_todo, toggle_todo, filter_todos, fill_input, click_add
- query helpers: get_todo_titles() -> List[str], get_visible_count() -> int, is_todo_completed(title) -> bool

Rules:
- Imports: from playwright.sync_api import Page, Locator, expect; from typing import List
- For scoped element access, use .filter(has=...) chaining on the parent todo-item locator.
- add_todo() must wait for the new title to appear after submitting.
- Every public method and property must have a one-line docstring.
- Use Python typing annotations throughout.
- Return ONLY valid Python code — no explanations, no markdown fences.
<!-- END_PROMPT -->
