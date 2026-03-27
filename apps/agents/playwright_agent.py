"""
Playwright Agent.

Analyzes the frontend HTML of the example application and generates
a Playwright Page Object Model (POM) class.
"""
from pathlib import Path
from typing import Optional

import requests

from apps.agents.base_agent import BaseAgent
from apps.prompts.loader import load as load_prompt
from core.utilities.logging.custom_logger import logger as log


SYSTEM_PROMPT = load_prompt("playwright_page_object.md")


class PlaywrightAgent(BaseAgent):
    """
    Generates a Playwright Page Object Model class from the live frontend HTML.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)

    def fetch_html(self, frontend_url: str) -> str:
        """Fetch the HTML source from the running frontend."""
        log.info(f"[PlaywrightAgent] Fetching HTML from {frontend_url}")
        response = requests.get(frontend_url, timeout=30)
        response.raise_for_status()
        return response.text

    def generate_page_object(self, html_source: str, class_name: str = "TodoPage") -> str:
        """
        Generate a Playwright POM class from the HTML source.

        Args:
            html_source: Raw HTML content of the frontend page.
            class_name: Name for the generated class.

        Returns:
            Python source code for the Page Object class.
        """
        # Truncate very long HTML to avoid token limits (keep first 8000 chars)
        html_excerpt = html_source[:8000] if len(html_source) > 8000 else html_source

        prompt = f"""Generate a Playwright Page Object Model class named `{class_name}` from this HTML.

HTML Source:
---
{html_excerpt}
---

Important data-testid attributes found (use these as primary selectors):
- app-title, add-todo-form, todo-input, add-todo-btn
- filter-bar, filter-all, filter-active, filter-completed
- status-message, todo-list, empty-state
- todo-item, todo-checkbox, todo-title, todo-description, delete-todo-btn

Generate a complete, production-ready Page Object class that covers all interactive elements."""

        log.info(f"[PlaywrightAgent] Generating page object class: {class_name}")
        code = self._ask(prompt, system=SYSTEM_PROMPT)
        return self._extract_code_block(code, "python")

    def run(
        self,
        frontend_url: str = "http://localhost:3000",
        output_path: str = "apps/testing/e2e/pages/todo_page.py",
        class_name: str = "TodoPage",
    ) -> str:
        """
        Fetch frontend HTML, generate a POM class, and write it to disk.

        Args:
            frontend_url: URL of the running frontend application.
            output_path: Path to write the generated page object file.
            class_name: Name for the generated page object class.

        Returns:
            The generated Python source code.
        """
        try:
            html_source = self.fetch_html(frontend_url)
        except Exception as exc:
            log.error(f"[PlaywrightAgent] Could not fetch HTML from {frontend_url}: {exc}")
            raise

        page_object_code = self.generate_page_object(html_source, class_name)
        self.write_file(output_path, page_object_code)
        log.info(f"[PlaywrightAgent] Generated page object → {output_path}")
        return page_object_code
