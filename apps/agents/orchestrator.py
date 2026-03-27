"""
Testing Lifecycle Orchestrator.

Runs all agents in sequence to produce a complete test suite:

  1. RequirementsAgent  — fetch JIRA tickets → structured requirements
  2. BDDAgent           — requirements → Gherkin .feature files
  3. StepDefinitionAgent— .feature files → behave step definitions
  4. PlaywrightAgent    — frontend HTML → Playwright page objects
  5. PytestAgent        — OpenAPI spec → pytest API tests

Can be triggered directly (python orchestrator.py) or via n8n webhook through
the command_runner Flask server.

Usage:
    python -m apps.agents.orchestrator [--skip-playwright] [--jql "..."]

Environment variables required:
    ANTHROPIC_API_KEY     Claude API key
    JIRA_BASE_URL         JIRA mock/real URL (default: http://localhost:8080)
    FRONTEND_URL          Frontend app URL (default: http://localhost:3000)
    API_BASE_URL          Backend API URL (default: http://localhost:8000)
"""
import argparse
import json
import os
import sys
import time

# Ensure the project root is on PYTHONPATH when running as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from apps.agents.requirements_agent import RequirementsAgent
from apps.agents.bdd_agent import BDDAgent
from apps.agents.step_definition_agent import StepDefinitionAgent
from apps.agents.playwright_agent import PlaywrightAgent
from apps.agents.pytest_agent import PytestAgent
from core.utilities.logging.custom_logger import logger as log


# ── Output paths ──────────────────────────────────────────────────────────────
REQUIREMENTS_OUTPUT = "tests/generated/requirements.json"
FEATURES_DIR        = "tests/features"
STEPS_DIR           = "tests/features/steps"
PAGE_OBJECTS_DIR    = "tests/e2e/pages"
API_TESTS_OUTPUT    = "tests/api/test_todo_api_generated.py"
OPENAPI_SPEC        = "apps/test_app/openapi.yaml"


def run_pipeline(
    jql: str = "status = 'Ready for Testing'",
    skip_playwright: bool = False,
) -> dict:
    """
    Execute the full testing lifecycle agent pipeline.

    Returns a summary dict with status and output paths for each stage.
    """
    jira_url = os.environ.get("JIRA_BASE_URL", "http://localhost:8080")
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    results = {}

    # ── Stage 1: Requirements Analysis ────────────────────────────────────────
    log.info("=" * 60)
    log.info("Stage 1: Requirements Analysis")
    log.info("=" * 60)
    t0 = time.time()
    try:
        req_agent = RequirementsAgent(jira_base_url=jira_url)
        requirements = req_agent.run(jql=jql, output_path=REQUIREMENTS_OUTPUT)
        results["requirements"] = {
            "status": "success",
            "count": len(requirements),
            "output": REQUIREMENTS_OUTPUT,
            "duration_s": round(time.time() - t0, 1),
        }
        log.info(f"Stage 1 complete: {len(requirements)} requirements extracted")
    except Exception as exc:
        results["requirements"] = {"status": "error", "error": str(exc)}
        log.error(f"Stage 1 failed: {exc}")
        return results  # Cannot continue without requirements

    # ── Stage 2: BDD Feature File Generation ──────────────────────────────────
    log.info("=" * 60)
    log.info("Stage 2: BDD Feature File Generation")
    log.info("=" * 60)
    t0 = time.time()
    try:
        bdd_agent = BDDAgent()
        features = bdd_agent.run(requirements=requirements, output_dir=FEATURES_DIR)
        results["bdd"] = {
            "status": "success",
            "files": list(features.keys()),
            "output_dir": FEATURES_DIR,
            "duration_s": round(time.time() - t0, 1),
        }
        log.info(f"Stage 2 complete: {len(features)} feature files generated")
    except Exception as exc:
        results["bdd"] = {"status": "error", "error": str(exc)}
        log.error(f"Stage 2 failed: {exc}")

    # ── Stage 3: Step Definition Generation ───────────────────────────────────
    log.info("=" * 60)
    log.info("Stage 3: Step Definition Generation")
    log.info("=" * 60)
    t0 = time.time()
    try:
        step_agent = StepDefinitionAgent()
        steps = step_agent.run(features_dir=FEATURES_DIR, steps_dir=STEPS_DIR)
        results["steps"] = {
            "status": "success",
            "files": list(steps.keys()),
            "output_dir": STEPS_DIR,
            "duration_s": round(time.time() - t0, 1),
        }
        log.info(f"Stage 3 complete: {len(steps)} step files generated")
    except Exception as exc:
        results["steps"] = {"status": "error", "error": str(exc)}
        log.error(f"Stage 3 failed: {exc}")

    # ── Stage 4: Playwright Page Object Generation ─────────────────────────────
    if not skip_playwright:
        log.info("=" * 60)
        log.info("Stage 4: Playwright Page Object Generation")
        log.info("=" * 60)
        t0 = time.time()
        try:
            pw_agent = PlaywrightAgent()
            page_obj_path = f"{PAGE_OBJECTS_DIR}/todo_page.py"
            pw_agent.run(frontend_url=frontend_url, output_path=page_obj_path)
            results["playwright"] = {
                "status": "success",
                "output": page_obj_path,
                "duration_s": round(time.time() - t0, 1),
            }
            log.info("Stage 4 complete: Playwright page object generated")
        except Exception as exc:
            results["playwright"] = {"status": "error", "error": str(exc)}
            log.warning(f"Stage 4 failed (non-fatal, using existing page object): {exc}")
    else:
        results["playwright"] = {"status": "skipped"}
        log.info("Stage 4: Skipped (--skip-playwright)")

    # ── Stage 5: Pytest API Test Generation ───────────────────────────────────
    log.info("=" * 60)
    log.info("Stage 5: Pytest API Test Generation")
    log.info("=" * 60)
    t0 = time.time()
    try:
        pytest_agent = PytestAgent()
        pytest_agent.run(spec_path=OPENAPI_SPEC, output_path=API_TESTS_OUTPUT)
        results["pytest"] = {
            "status": "success",
            "output": API_TESTS_OUTPUT,
            "duration_s": round(time.time() - t0, 1),
        }
        log.info("Stage 5 complete: Pytest API tests generated")
    except Exception as exc:
        results["pytest"] = {"status": "error", "error": str(exc)}
        log.error(f"Stage 5 failed: {exc}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run the AI-driven testing lifecycle agent pipeline"
    )
    parser.add_argument(
        "--jql",
        default="status = 'Ready for Testing'",
        help="JIRA Query Language string to select tickets (default: status = 'Ready for Testing')",
    )
    parser.add_argument(
        "--skip-playwright",
        action="store_true",
        help="Skip the Playwright page object generation stage (e.g. if frontend is not running)",
    )
    args = parser.parse_args()

    log.info("Starting AI-driven testing lifecycle pipeline")
    results = run_pipeline(jql=args.jql, skip_playwright=args.skip_playwright)

    log.info("\n" + "=" * 60)
    log.info("PIPELINE SUMMARY")
    log.info("=" * 60)
    print(json.dumps(results, indent=2))

    failed = [k for k, v in results.items() if v.get("status") == "error"]
    if failed:
        log.error(f"Failed stages: {', '.join(failed)}")
        sys.exit(1)
    else:
        log.info("All stages completed successfully.")


if __name__ == "__main__":
    main()
