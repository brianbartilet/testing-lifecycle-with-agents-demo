---
name: run-pipeline
description: Run the full AI testing lifecycle agent pipeline (all 5 stages) against the mock JIRA. Requires ANTHROPIC_API_KEY and the jira-mock service to be running.
disable-model-invocation: true
allowed-tools: Bash, Read
---

Run the full agent pipeline. Pass an optional JQL string as `$ARGUMENTS` (default: `status = 'Ready for Testing'`).

!`PYTHONPATH=. python -m apps.agents.orchestrator --skip-playwright 2>&1`

After the run, summarize:
- Status of each stage (success / error / skipped)
- How many requirements were extracted in Stage 1
- Which feature files were generated in Stage 2
- Which step definition files were generated in Stage 3
- Which test files were generated in Stage 5
- Any errors and the likely cause
