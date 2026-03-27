---
name: run-e2e-tests
description: Run the Playwright E2E pytest test suite against the full stack. Requires todo-backend on port 8000 and todo-frontend on port 3000.
disable-model-invocation: true
allowed-tools: Bash
---

Run E2E tests with optional marker filter. Pass a pytest marker as `$ARGUMENTS` (e.g. `smoke`, `regression`) or leave blank to run all.

!`PYTHONPATH=. API_BASE_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3000 python -m pytest tests/e2e/ ${ARGUMENTS:+-m "$ARGUMENTS"} --tb=short -v 2>&1`

Summarize:
- Total passed / failed / skipped
- Any failures: test name + assertion or Playwright error
- If browser launch fails, check that Playwright browsers are installed: `python -m playwright install chromium`
- If connection errors appear, remind that both services must be running (run `/services-up`)
