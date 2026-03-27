---
name: run-bdd-tests
description: Run the behave BDD test suite (Gherkin feature files with Playwright). Requires todo-backend on port 8000 and todo-frontend on port 3000.
disable-model-invocation: true
allowed-tools: Bash
---

Run BDD tests with optional tag filter. Pass a behave tag as `$ARGUMENTS` (e.g. `smoke`, `regression`) or leave blank to run all tagged scenarios.

!`PYTHONPATH=. API_BASE_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3000 behave tests/features/ --no-capture ${ARGUMENTS:+--tags="@$ARGUMENTS"} 2>&1`

Summarize:
- Scenarios passed / failed / skipped
- Any step failures: scenario name + failing step + error
- If browser launch fails, check that Playwright browsers are installed: `python -m playwright install chromium`
- If connection errors appear, remind that both services must be running (run `/services-up`)
