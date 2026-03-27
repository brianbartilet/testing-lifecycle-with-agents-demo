"""
BDD Agent.

Takes structured requirements produced by RequirementsAgent and generates
Gherkin feature files (.feature) compatible with Python behave.
"""
import json
from pathlib import Path
from typing import Optional

from apps.agents.base_agent import BaseAgent
from apps.prompts.loader import load as load_prompt
from core.utilities.logging.custom_logger import logger as log


SYSTEM_PROMPT = load_prompt("bdd_feature_generation.md")


class BDDAgent(BaseAgent):
    """
    Generates Gherkin feature files from structured requirements.

    For each set of requirements (grouped by component), produces one feature file.
    Output files are written to the specified features directory.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)

    def generate_feature(self, requirements: list[dict], component: str) -> str:
        """
        Generate a single .feature file for all requirements of a given component.

        Args:
            requirements: List of structured requirement dicts from RequirementsAgent.
            component: Component name (e.g. 'Frontend', 'Backend API').

        Returns:
            Gherkin feature file content as a string.
        """
        context = json.dumps(requirements, indent=2)
        prompt = f"""Generate a comprehensive Gherkin feature file for the {component} component.

Requirements:
{context}

Create a feature file that covers all the acceptance criteria and test scenarios listed above.
Include Background if there are shared preconditions.
Use Scenario Outline where multiple similar scenarios differ only by data."""

        log.info(f"[BDDAgent] Generating feature file for component: {component}")
        content = self._ask(prompt, system=SYSTEM_PROMPT)

        # Strip markdown code fences if present
        if "```" in content:
            content = self._extract_code_block(content, "gherkin")
            if not content:
                content = self._extract_code_block(content)

        return content

    def run(
        self,
        requirements: list[dict],
        output_dir: str = "apps/testing/features",
    ) -> dict[str, str]:
        """
        Generate feature files from requirements and write them to disk.

        Groups requirements by component and creates one feature file per component.

        Args:
            requirements: List of requirement dicts from RequirementsAgent.
            output_dir: Directory to write .feature files into.

        Returns:
            Dict mapping feature filename → generated content.
        """
        # Group by component
        by_component: dict[str, list[dict]] = {}
        for req in requirements:
            for component in req.get("components", ["General"]):
                by_component.setdefault(component, []).append(req)

        generated: dict[str, str] = {}
        output_path = Path(output_dir)

        for component, reqs in by_component.items():
            try:
                feature_content = self.generate_feature(reqs, component)
                filename = self._component_to_filename(component)
                file_path = output_path / filename
                self.write_file(str(file_path), feature_content)
                generated[filename] = feature_content
                log.info(f"[BDDAgent] Generated: {file_path}")
            except Exception as exc:
                log.error(f"[BDDAgent] Failed for component '{component}': {exc}")

        return generated

    @staticmethod
    def _component_to_filename(component: str) -> str:
        """Convert a component name to a safe .feature filename."""
        slug = component.lower().replace(" ", "_").replace("/", "_")
        # Remove non-alphanumeric except underscores
        slug = "".join(c if c.isalnum() or c == "_" else "" for c in slug)
        return f"{slug}.feature"
