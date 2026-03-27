"""
Pytest Agent.

Reads the OpenAPI specification and generates comprehensive pytest test
suites covering all API endpoints.
"""
from pathlib import Path
from typing import Optional

import yaml

from apps.agents.base_agent import BaseAgent
from apps.prompts.loader import load as load_prompt
from core.utilities.logging.custom_logger import logger as log


SYSTEM_PROMPT = load_prompt("pytest_api_tests.md")


class PytestAgent(BaseAgent):
    """
    Generates pytest API test files from an OpenAPI specification.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)

    def load_openapi_spec(self, spec_path: str) -> dict:
        """Load and parse the OpenAPI YAML spec."""
        log.info(f"[PytestAgent] Loading OpenAPI spec from {spec_path}")
        with open(spec_path, encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        return spec

    def generate_tests(self, spec: dict) -> str:
        """
        Generate pytest test code from the OpenAPI spec.

        Args:
            spec: Parsed OpenAPI specification as a dict.

        Returns:
            Python source code for the test file.
        """
        spec_json = yaml.dump(spec, default_flow_style=False)

        prompt = f"""Generate a comprehensive pytest test file for this OpenAPI specification.

OpenAPI Spec:
---
{spec_json}
---

Generate tests for ALL paths and methods. Include edge cases, validation errors, and happy paths.
The test file should be ready to run with: pytest tests/api/test_todo_api.py --alluredir=allure-results"""

        log.info("[PytestAgent] Generating pytest tests from OpenAPI spec")
        code = self._ask(prompt, system=SYSTEM_PROMPT)
        return self._extract_code_block(code, "python")

    def run(
        self,
        spec_path: str = "apps/example_app/openapi.yaml",
        output_path: str = "tests/api/test_todo_api_generated.py",
    ) -> str:
        """
        Load the OpenAPI spec, generate tests, and write to disk.

        Args:
            spec_path: Path to the OpenAPI YAML specification file.
            output_path: Path to write the generated test file.

        Returns:
            The generated Python test source code.
        """
        spec = self.load_openapi_spec(spec_path)
        test_code = self.generate_tests(spec)
        self.write_file(output_path, test_code)
        log.info(f"[PytestAgent] Generated API tests → {output_path}")
        return test_code
