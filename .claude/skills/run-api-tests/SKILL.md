---
name: run-api-tests
description: Run the pytest API test suite against the todo-backend. Requires the backend service running on port 8000.
disable-model-invocation: true
allowed-tools: Bash
---

Run API tests with optional marker filter. Pass a pytest marker as `$ARGUMENTS` (e.g. `smoke`, `regression`) or leave blank to run all.

!`PYTHONPATH=. python -m pytest tests/api/ ${ARGUMENTS:+-m "$ARGUMENTS"} --tb=short -v 2>&1`

Summarize:
- Total passed / failed / skipped
- Any failures: test name + assertion error
- If connection errors appear, remind that `docker compose up -d todo-backend` is needed (run `/services-up`)
