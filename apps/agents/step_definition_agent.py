"""
Step Definition Agent.

Reads generated Gherkin feature files and produces Python behave step definitions
using Playwright for UI interactions.
"""
from pathlib import Path
from typing import Optional

from apps.agents.base_agent import BaseAgent
from apps.prompts.loader import load as load_prompt
from core.utilities.logging.custom_logger import logger as log


SYSTEM_PROMPT = load_prompt("step_definition_generation.md")


class StepDefinitionAgent(BaseAgent):
    """
    Generates behave step definition Python files from Gherkin feature files.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)

    def generate_steps(self, feature_content: str, feature_name: str) -> str:
        """
        Generate a Python step definitions file for a given feature file.

        Args:
            feature_content: The Gherkin .feature file content.
            feature_name: The feature filename (used for naming context).

        Returns:
            Python source code for the step definitions.
        """
        prompt = f"""Generate Python behave step definitions for this Gherkin feature file.

Feature file: {feature_name}
Content:
---
{feature_content}
---

Page objects available:
- apps.testing.e2e.pages.todo_page.TodoPage (for UI steps)
  Methods: navigate(), add_todo(title), get_todo_titles(), delete_todo(title),
           toggle_todo(title), filter_todos(filter_name), get_visible_count()

The behave context will have:
- context.page: Playwright Page object (for UI tests)
- context.api_base_url: Base URL for API calls (e.g. "http://localhost:8000")
- context.base_url: Frontend base URL (e.g. "http://localhost:3000")

Generate all step definitions needed to fully implement the scenarios in this feature file."""

        log.info(f"[StepDefinitionAgent] Generating steps for: {feature_name}")
        code = self._ask(prompt, system=SYSTEM_PROMPT)
        return self._extract_code_block(code, "python")

    def run(
        self,
        features_dir: str = "apps/testing/features",
        steps_dir: str = "apps/testing/features/steps",
    ) -> dict[str, str]:
        """
        Process all .feature files in features_dir and generate corresponding step files.

        Args:
            features_dir: Directory containing .feature files.
            steps_dir: Output directory for step definition Python files.

        Returns:
            Dict mapping step filename → generated content.
        """
        features_path = Path(features_dir)
        generated: dict[str, str] = {}

        feature_files = list(features_path.glob("*.feature"))
        if not feature_files:
            log.warning(f"[StepDefinitionAgent] No .feature files found in {features_dir}")
            return generated

        for feature_file in feature_files:
            try:
                feature_content = feature_file.read_text(encoding="utf-8")
                steps_code = self.generate_steps(feature_content, feature_file.name)

                stem = feature_file.stem
                out_path = Path(steps_dir) / f"{stem}_steps.py"
                self.write_file(str(out_path), steps_code)
                generated[out_path.name] = steps_code
                log.info(f"[StepDefinitionAgent] Generated: {out_path}")
            except Exception as exc:
                log.error(f"[StepDefinitionAgent] Failed for {feature_file.name}: {exc}")

        return generated
