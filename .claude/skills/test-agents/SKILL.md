---
name: test-agents
description: Run unit tests for the Anthropic API client module (apps/antropic/tests/). Requires ENV_APP_CONFIG_FILE pointing to a valid config YAML with an ANTHROPIC section.
disable-model-invocation: true
allowed-tools: Bash
---

Run the Anthropic client unit tests:

!`PYTHONPATH=. python -m pytest apps/antropic/tests/ -v --tb=short 2>&1`

Summarize:
- Total passed / failed / errored
- Any import errors (likely missing config or harqis-core not installed)
- Any test failures with the specific assertion that failed
